#!/usr/bin/env python3
"""
Comprehensive Factor Testing Script

This script demonstrates professional factor validation methods used by
top quantitative hedge funds (百亿量化标准):

1. IC Analysis (Information Coefficient)
   - IC mean, std, ICIR
   - IC t-statistics
   - IC significance ratio
   - IC cumulative curve

2. Regression Method
   - Factor return series
   - t-value series
   - Significance analysis

3. Group Testing (Quintile/Decile)
   - Group returns
   - Spread analysis
   - Monotonicity
   - Statistical tests

4. IC Decay Analysis
   - Half-life calculation
   - Decay curve
   - Periodicity

5. Turnover Analysis
   - Group turnover
   - Autocorrelation

6. Statistical Tests
   - t-test
   - Wilcoxon test
   - KS test

7. Risk-Adjusted Metrics
   - Sortino ratio
   - Calmar ratio
   - Max drawdown
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from src.data import DataManager
from src.factors import get_all_factors, ComprehensiveFactorTester, ComprehensiveFactorStats
from src.factors.comprehensive_tester import FactorPreprocessor, FactorCorrelationAnalyzer

console = Console()


def setup():
    """Setup logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def load_data(start_date: str, end_date: str, n_stocks: int = 50) -> pd.DataFrame:
    """Load market data"""
    console.print("\n[bold blue]Step 1: Loading Market Data[/bold blue]")
    
    from src.data import DataFetcher
    fetcher = DataFetcher(source="mock")
    symbols = [f"{i:06d}" for i in range(1, n_stocks + 1)]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("Fetching price data...", total=None)
        df = fetcher.fetch_daily(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            show_progress=False
        )
    
    console.print(f"[green]✓[/green] Loaded {len(df):,} rows for {df['symbol'].nunique()} stocks")
    return df


def run_comprehensive_tests(df: pd.DataFrame) -> dict:
    """Run comprehensive factor tests"""
    console.print("\n[bold blue]Step 2: Comprehensive Factor Testing[/bold blue]")
    
    factors = get_all_factors()
    tester = ComprehensiveFactorTester(
        ic_threshold=0.02,
        icir_threshold=0.5,
        n_groups=5,
        max_decay_periods=10
    )
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Testing factors...", total=None)
        
        for factor in factors:
            try:
                stats = tester.test_factor_comprehensive(
                    factor=factor,
                    df=df,
                    forward_periods=[1, 5, 10, 20],
                    preprocess=True
                )
                results[factor.name] = stats
            except Exception as e:
                logger.error(f"Error testing {factor.name}: {e}")
    
    return results


def display_results(results: dict):
    """Display comprehensive test results"""
    console.print("\n[bold blue]Step 3: Results Summary[/bold blue]")
    
    # Main results table
    table = Table(title="Comprehensive Factor Test Results", show_lines=True)
    table.add_column("Factor", style="cyan", width=20)
    table.add_column("IC Mean", justify="right")
    table.add_column("ICIR", justify="right")
    table.add_column("IC t-Stat", justify="right")
    table.add_column("Half-Life", justify="right")
    table.add_column("Mono.", justify="right")
    table.add_column("Turnover", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Status", style="bold")
    
    for name, stats in sorted(results.items(), key=lambda x: x[1].effectiveness_score, reverse=True):
        ic_mean = f"{stats.ic_mean:.4f}"
        icir = f"{stats.icir:.2f}"
        ic_t = f"{stats.ic_t_stat:.2f}"
        half_life = f"{stats.ic_half_life:.0f}" if stats.ic_half_life > 0 else "N/A"
        mono = f"{stats.monotonicity_score:.2f}"
        turnover = f"{stats.turnover_mean:.1%}"
        score = f"{stats.effectiveness_score:.2f}"
        status = "[green]✓ Effective[/green]" if stats.is_effective else "[yellow]✗ Ineffective[/yellow]"
        
        table.add_row(name, ic_mean, icir, ic_t, half_life, mono, turnover, score, status)
    
    console.print(table)
    
    # Summary statistics
    effective_count = sum(1 for s in results.values() if s.is_effective)
    console.print(f"\n[bold]Effective Factors: {effective_count}/{len(results)}[/bold]")
    
    # Detailed view for top factor
    top_factor = max(results.items(), key=lambda x: x[1].effectiveness_score)
    display_detailed_results(top_factor[0], top_factor[1])


def display_detailed_results(name: str, stats: ComprehensiveFactorStats):
    """Display detailed results for a single factor"""
    console.print(f"\n[bold blue]Detailed Analysis: {name}[/bold blue]")
    
    # IC Analysis
    ic_table = Table(title="IC Analysis")
    ic_table.add_column("Metric", style="cyan")
    ic_table.add_column("Value", style="green")
    ic_table.add_row("IC Mean", f"{stats.ic_mean:.4f}")
    ic_table.add_row("IC Std", f"{stats.ic_std:.4f}")
    ic_table.add_row("ICIR", f"{stats.icir:.4f}")
    ic_table.add_row("IC t-Statistic", f"{stats.ic_t_stat:.2f}")
    ic_table.add_row("IC > 0 Ratio", f"{stats.ic_positive_ratio:.2%}")
    ic_table.add_row("IC Significant Ratio", f"{stats.ic_significant_ratio:.2%}")
    console.print(ic_table)
    
    # Regression Analysis
    reg_table = Table(title="Regression Analysis")
    reg_table.add_column("Metric", style="cyan")
    reg_table.add_column("Value", style="green")
    reg_table.add_row("Factor Return Mean", f"{stats.factor_return_mean:.6f}")
    reg_table.add_row("Factor Return t-Stat", f"{stats.factor_return_t_stat:.2f}")
    reg_table.add_row("Mean |t-value|", f"{stats.t_value_mean:.2f}")
    reg_table.add_row("|t| > 1.96 Ratio", f"{stats.t_value_significant_ratio:.2%}")
    console.print(reg_table)
    
    # Group Testing
    if stats.group_returns:
        group_table = Table(title="Group Testing (Quintile Analysis)")
        group_table.add_column("Group", style="cyan")
        group_table.add_column("Mean Return", style="green")
        group_table.add_column("Sharpe", style="yellow")
        for i, (ret, sr) in enumerate(zip(stats.group_returns, stats.group_sharpe), 1):
            group_table.add_row(f"Q{i}", f"{ret:.4%}", f"{sr:.2f}")
        group_table.add_row("Spread (Q5-Q1)", f"{stats.spread_return:.4%}", f"{stats.spread_sharpe:.2f}")
        console.print(group_table)
    
    # Additional Metrics
    other_table = Table(title="Additional Metrics")
    other_table.add_column("Metric", style="cyan")
    other_table.add_column("Value", style="green")
    other_table.add_row("IC Half-Life (periods)", f"{stats.ic_half_life:.0f}")
    other_table.add_row("Monotonicity Score", f"{stats.monotonicity_score:.2f}")
    other_table.add_row("Avg Turnover", f"{stats.turnover_mean:.2%}")
    other_table.add_row("Factor Autocorrelation", f"{stats.autocorrelation:.2f}")
    other_table.add_row("Sortino Ratio", f"{stats.sortino_ratio:.2f}")
    other_table.add_row("Calmar Ratio", f"{stats.calmar_ratio:.2f}")
    other_table.add_row("Max Drawdown", f"{stats.max_drawdown:.2%}")
    other_table.add_row("Wilcoxon p-value", f"{stats.wilcoxon_pvalue:.4f}")
    console.print(other_table)
    
    # Failure Reasons
    if stats.failure_reasons:
        console.print(f"\n[yellow]Failure Reasons:[/yellow]")
        for reason in stats.failure_reasons:
            console.print(f"  • {reason}")


def generate_visualization(results: dict, output_dir: str = "outputs"):
    """Generate visualization of factor tests"""
    console.print("\n[bold blue]Step 4: Generating Visualizations[/bold blue]")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Factor Comparison Chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    names = list(results.keys())
    
    # IC Mean comparison
    ax1 = axes[0, 0]
    ic_means = [results[n].ic_mean for n in names]
    colors = ['green' if v > 0 else 'red' for v in ic_means]
    ax1.barh(names, ic_means, color=colors, alpha=0.7)
    ax1.axvline(x=0.02, color='blue', linestyle='--', label='Threshold')
    ax1.axvline(x=-0.02, color='blue', linestyle='--')
    ax1.set_xlabel('IC Mean')
    ax1.set_title('IC Mean by Factor')
    ax1.legend()
    
    # ICIR comparison
    ax2 = axes[0, 1]
    icirs = [results[n].icir for n in names]
    colors = ['green' if v > 0.5 else 'orange' if v > 0.3 else 'red' for v in icirs]
    ax2.barh(names, icirs, color=colors, alpha=0.7)
    ax2.axvline(x=0.5, color='blue', linestyle='--', label='Threshold')
    ax2.set_xlabel('ICIR')
    ax2.set_title('ICIR by Factor')
    ax2.legend()
    
    # Monotonicity comparison
    ax3 = axes[1, 0]
    monos = [results[n].monotonicity_score for n in names]
    colors = ['green' if v > 0.7 else 'orange' if v > 0.5 else 'red' for v in monos]
    ax3.barh(names, monos, color=colors, alpha=0.7)
    ax3.axvline(x=0.7, color='blue', linestyle='--', label='Threshold')
    ax3.set_xlabel('Monotonicity Score')
    ax3.set_title('Monotonicity by Factor')
    ax3.legend()
    
    # Effectiveness Score
    ax4 = axes[1, 1]
    scores = [results[n].effectiveness_score for n in names]
    colors = ['green' if results[n].is_effective else 'red' for n in names]
    ax4.barh(names, scores, color=colors, alpha=0.7)
    ax4.axvline(x=0.5, color='blue', linestyle='--', label='Threshold')
    ax4.set_xlabel('Effectiveness Score')
    ax4.set_title('Overall Effectiveness Score')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/factor_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. IC Decay Curves
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for name, stats in list(results.items())[:5]:  # Top 5 factors
        if stats.ic_decay_curve:
            ax.plot(stats.ic_decay_curve, label=name, marker='o', markersize=3)
    
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Lag Period')
    ax.set_ylabel('IC')
    ax.set_title('IC Decay Curves')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/ic_decay.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Group Returns Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    
    group_data = []
    for name, stats in results.items():
        if stats.group_returns:
            group_data.append(stats.group_returns)
    
    if group_data:
        group_df = pd.DataFrame(group_data, index=list(results.keys())[:len(group_data)])
        group_df.columns = [f'Q{i+1}' for i in range(len(group_df.columns))]
        
        import seaborn as sns
        sns.heatmap(group_df * 100, annot=True, fmt='.2f', cmap='RdYlGn', center=0, ax=ax)
        ax.set_title('Group Returns (%) by Factor')
        ax.set_xlabel('Quintile')
        ax.set_ylabel('Factor')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/group_returns.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    console.print(f"[green]✓[/green] Visualizations saved to {output_dir}/")


def main():
    """Main execution"""
    console.print(Panel.fit(
        "[bold blue]Comprehensive Factor Testing Framework[/bold blue]\n"
        "[dim]Professional Factor Validation (百亿量化标准)[/dim]",
        border_style="blue"
    ))
    
    setup()
    
    # Configuration
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365*2)).strftime("%Y-%m-%d")
    
    # Load data
    df = load_data(start_date, end_date, n_stocks=50)
    
    # Run comprehensive tests
    results = run_comprehensive_tests(df)
    
    # Display results
    display_results(results)
    
    # Generate visualizations
    generate_visualization(results)
    
    # Final summary
    effective = [n for n, s in results.items() if s.is_effective]
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold green]Testing Complete![/bold green]\n\n"
        f"• Tested {len(results)} factors comprehensively\n"
        f"• {len(effective)} factors passed all criteria\n"
        f"• Visualizations saved to outputs/\n\n"
        f"[dim]Factors: {', '.join(effective[:5])}{'...' if len(effective) > 5 else ''}[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
