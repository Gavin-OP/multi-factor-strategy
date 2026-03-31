#!/usr/bin/env python3
"""
Main Pipeline Script - Run the complete quantitative strategy pipeline

This script demonstrates the full workflow:
1. Data loading
2. Factor calculation and testing
3. Signal generation
4. Portfolio construction
5. Backtesting
6. Risk analysis and reporting

Usage:
    python scripts/run_pipeline.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from src.data import DataManager
from src.factors import FactorEngine, get_all_factors
from src.signals import SignalGenerator
from src.portfolio import PortfolioConstructor, WeightAllocator, Rebalancer
from src.backtest import BacktestEngine
from src.risk import RiskManager, RiskAnalytics, PerformanceReporter

# Initialize console
console = Console()


def setup():
    """Setup logging and environment"""
    # Configure logger
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    logger.add(
        "outputs/logs/pipeline_{time:YYYYMMDD}.log",
        level="DEBUG",
        rotation="1 day"
    )


def load_data(start_date: str, end_date: str, n_stocks: int = 50) -> pd.DataFrame:
    """Load market data"""
    console.print("\n[bold blue]Step 1: Loading Market Data[/bold blue]")
    
    # Initialize data manager with mock source for demo
    dm = DataManager(data_source="mock")
    
    # Generate mock stock list
    symbols = [f"{i:06d}" for i in range(1, n_stocks + 1)]
    
    # Fetch data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("Fetching price data...", total=None)
        df = dm.get_daily_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            show_progress=False
        )
    
    # Display summary
    table = Table(title="Data Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Symbols", str(df["symbol"].nunique()))
    table.add_row("Date Range", f"{df['date'].min().date()} to {df['date'].max().date()}")
    table.add_row("Total Rows", f"{len(df):,}")
    table.add_row("Memory (MB)", f"{df.memory_usage(deep=True).sum() / 1e6:.2f}")
    console.print(table)
    
    return df


def test_factors(df: pd.DataFrame) -> dict:
    """Calculate and test factors"""
    console.print("\n[bold blue]Step 2: Factor Calculation and Testing[/bold blue]")
    
    engine = FactorEngine()
    
    # Test all factors
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("Testing factors...", total=None)
        results = engine.test_all_factors(df, forward_periods=[1, 5, 20], show_progress=False)
    
    # Create summary table
    table = Table(title="Factor Test Results (20-day Forward Returns)")
    table.add_column("Factor", style="cyan")
    table.add_column("IC Mean", style="white")
    table.add_column("ICIR", style="white")
    table.add_column("Monotonicity", style="white")
    table.add_column("Status", style="bold")
    
    effective_count = 0
    for name, result in results.items():
        test_20d = result.get("tests", {}).get("20d", {})
        ic_stats = test_20d.get("ic_stats", {})
        is_effective = test_20d.get("is_effective", False)
        
        ic_mean = ic_stats.get("ic_mean", 0)
        icir = ic_stats.get("icir", 0)
        mono = test_20d.get("monotonicity", 0)
        
        status = "[green]✓ Effective[/green]" if is_effective else "[yellow]○ Ineffective[/yellow]"
        if is_effective:
            effective_count += 1
        
        table.add_row(
            name,
            f"{ic_mean:.4f}",
            f"{icir:.4f}",
            f"{mono:.4f}",
            status
        )
    
    console.print(table)
    console.print(f"\n[bold]Effective Factors: {effective_count}/{len(results)}[/bold]")
    
    return results


def generate_signals(df: pd.DataFrame, test_results: dict) -> pd.DataFrame:
    """Generate trading signals"""
    console.print("\n[bold blue]Step 3: Signal Generation[/bold blue]")
    
    # Initialize signal generator
    signal_gen = SignalGenerator()
    
    # Get effective factors
    effective_factors = [
        name for name, result in test_results.items()
        if any(
            test.get("is_effective", False)
            for test in result.get("tests", {}).values()
        )
    ]
    
    console.print(f"Using {len(effective_factors)} effective factors for signal generation")
    
    # Calculate factors for signal generation
    from src.factors import FactorEngine
    engine = FactorEngine()
    factor_df = engine.calculate_factors(df, factor_names=effective_factors, show_progress=False)
    
    # Calculate forward returns for fitting
    df_copy = df.copy()
    df_copy["forward_return"] = df_copy.groupby("symbol")["close"].transform(
        lambda x: x.shift(-5) / x - 1
    )
    
    # Generate signals
    signals = signal_gen.generate(factor_df, df_copy, fit=True)
    
    # Display signal summary
    table = Table(title="Signal Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total Signals", str(len(signals)))
    table.add_row("Dates", str(signals["date"].nunique()))
    table.add_row("Avg Selected/Date", f"{signals[signals['selected']].groupby('date').size().mean():.1f}")
    console.print(table)
    
    return signals


def construct_portfolio(
    df: pd.DataFrame,
    signals: pd.DataFrame
) -> pd.DataFrame:
    """Construct portfolio"""
    console.print("\n[bold blue]Step 4: Portfolio Construction[/bold blue]")
    
    # Initialize components
    weight_allocator = WeightAllocator(
        scheme="signal",
        max_position=0.05,
        min_position=0.01
    )
    
    # Get latest signal date
    latest_date = signals["date"].max()
    latest_signals = signals[signals["date"] == latest_date]
    
    # Allocate weights
    selected = latest_signals[latest_signals["selected"]].copy()
    positions = weight_allocator.allocate(selected)
    
    # Display portfolio
    table = Table(title=f"Portfolio Positions ({latest_date.date()})")
    table.add_column("Symbol", style="cyan")
    table.add_column("Signal", style="white")
    table.add_column("Weight", style="green")
    
    for _, row in positions.nlargest(20, "weight").iterrows():
        symbol = row["symbol"]
        signal = selected[selected["symbol"] == symbol]["signal"].iloc[0]
        weight = row["weight"]
        table.add_row(symbol, f"{signal:.4f}", f"{weight:.2%}")
    
    console.print(table)
    
    # Summary
    summary = weight_allocator.get_weight_summary(positions)
    console.print(f"\n[bold]Positions: {summary['n_positions']}, Effective N: {summary['effective_n']:.1f}[/bold]")
    
    return positions


def run_backtest(
    df: pd.DataFrame,
    signals: pd.DataFrame
) -> dict:
    """Run backtest"""
    console.print("\n[bold blue]Step 5: Backtesting[/bold blue]")
    
    # Initialize backtest engine
    engine = BacktestEngine(
        initial_capital=10_000_000,
        commission=0.0003,
        slippage=0.0001
    )
    
    # Run backtest
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("Running backtest...", total=None)
        result = engine.run(
            price_df=df,
            signal_df=signals,
            rebalance_freq=5,
            n_positions=30,
            weighting="equal"
        )
    
    # Display results
    table = Table(title="Backtest Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    metrics = result.metrics
    table.add_row("Initial Capital", f"${metrics['initial_capital']:,.0f}")
    table.add_row("Final Capital", f"${metrics['final_capital']:,.0f}")
    table.add_row("Total Return", f"{metrics['total_return']:.2%}")
    table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    table.add_row("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
    table.add_row("Total Trades", str(metrics['n_trades']))
    table.add_row("Win Rate", f"{metrics['win_rate']:.2%}")
    
    console.print(table)
    
    return result


def analyze_risk(
    returns: pd.Series,
    output_path: str = "outputs/reports"
) -> dict:
    """Analyze risk and generate report"""
    console.print("\n[bold blue]Step 6: Risk Analysis and Reporting[/bold blue]")
    
    # Initialize components
    risk_manager = RiskManager()
    analytics = RiskAnalytics()
    reporter = PerformanceReporter(risk_manager, analytics, output_path)
    
    # Calculate metrics
    risk_metrics = risk_manager.calculate_risk_metrics(returns)
    
    # Display risk metrics
    table = Table(title="Risk Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("VaR (95%)", f"{risk_metrics.var_95:.2%}")
    table.add_row("CVaR (95%)", f"{risk_metrics.cvar_95:.2%}")
    table.add_row("Max Drawdown", f"{risk_metrics.max_drawdown:.2%}")
    table.add_row("Annual Volatility", f"{risk_metrics.volatility:.2%}")
    table.add_row("Sortino Ratio", f"{risk_metrics.sortino_ratio:.2f}")
    table.add_row("Calmar Ratio", f"{risk_metrics.calmar_ratio:.2f}")
    
    console.print(table)
    
    # Generate tearsheet
    try:
        analytics.generate_tearsheet(
            returns,
            output_path=f"{output_path}/tearsheet.html"
        )
        console.print(f"\n[green]Report saved to {output_path}/tearsheet.html[/green]")
    except Exception as e:
        console.print(f"\n[yellow]Could not generate tearsheet: {e}[/yellow]")
    
    return {
        "risk_metrics": risk_metrics,
        "performance_metrics": analytics.calculate_performance_metrics(returns)
    }


def main():
    """Main pipeline execution"""
    console.print(Panel.fit(
        "[bold blue]Quantitative Factor Strategy Pipeline[/bold blue]\n"
        "[dim]Professional Factor Research and Backtesting Framework[/dim]",
        border_style="blue"
    ))
    
    # Setup
    setup()
    
    # Configuration
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365*2)).strftime("%Y-%m-%d")
    
    console.print(f"\n[dim]Period: {start_date} to {end_date}[/dim]")
    
    # Step 1: Load Data
    df = load_data(start_date, end_date, n_stocks=50)
    
    # Step 2: Factor Testing
    test_results = test_factors(df)
    
    # Step 3: Signal Generation
    signals = generate_signals(df, test_results)
    
    # Step 4: Portfolio Construction
    positions = construct_portfolio(df, signals)
    
    # Step 5: Backtest
    backtest_result = run_backtest(df, signals)
    
    # Step 6: Risk Analysis
    equity_curve = backtest_result.equity_curve
    returns = equity_curve.set_index("date")["return"].dropna()
    risk_analysis = analyze_risk(returns)
    
    # Final summary
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]Pipeline Complete![/bold green]\n\n"
        f"• Tested {len(test_results)} factors\n"
        f"• Generated signals for {signals['date'].nunique()} dates\n"
        f"• Constructed portfolio with {len(positions)} positions\n"
        f"• Backtest return: {backtest_result.metrics['total_return']:.2%}\n"
        f"• Sharpe Ratio: {backtest_result.metrics['sharpe_ratio']:.2f}\n\n"
        f"[dim]Reports saved to outputs/reports/[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
