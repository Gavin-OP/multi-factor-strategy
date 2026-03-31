"""
Performance Reporter - Generate comprehensive performance reports
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from loguru import logger
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

from src.risk.manager import RiskManager
from src.risk.analytics import RiskAnalytics


class PerformanceReporter:
    """
    Performance Report Generator
    
    Features:
    - Strategy performance summary
    - Risk metrics visualization
    - Factor attribution
    - Comparison reports
    
    Generates professional-grade reports similar to
    what billion-dollar quantitative funds use.
    """
    
    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        analytics: Optional[RiskAnalytics] = None,
        output_dir: str = "outputs/reports"
    ):
        """
        Initialize performance reporter
        
        Args:
            risk_manager: RiskManager instance
            analytics: RiskAnalytics instance
            output_dir: Output directory for reports
        """
        self.risk_manager = risk_manager or RiskManager()
        self.analytics = analytics or RiskAnalytics()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_full_report(
        self,
        returns: pd.Series,
        positions: Optional[pd.DataFrame] = None,
        benchmark_returns: Optional[pd.Series] = None,
        factor_returns: Optional[pd.DataFrame] = None,
        report_name: str = "performance_report"
    ) -> str:
        """
        Generate comprehensive performance report
        
        Args:
            returns: Portfolio returns
            positions: Position history
            benchmark_returns: Benchmark returns
            factor_returns: Factor returns for attribution
            report_name: Report name
            
        Returns:
            Path to generated report
        """
        logger.info("Generating comprehensive performance report...")
        
        # Calculate metrics
        metrics = self.analytics.calculate_performance_metrics(
            returns, benchmark_returns
        )
        
        risk_metrics = self.risk_manager.calculate_risk_metrics(
            returns, benchmark_returns
        )
        
        # Create figure
        fig = plt.figure(figsize=(16, 20))
        
        # 1. Performance summary
        ax1 = plt.subplot(4, 2, 1)
        ax1.axis("off")
        summary_text = self._format_summary(metrics, risk_metrics)
        ax1.text(0, 0.5, summary_text, fontsize=10, family="monospace",
                 verticalalignment="center")
        
        # 2. Equity curve
        ax2 = plt.subplot(4, 2, 2)
        self._plot_equity_curve(ax2, returns, benchmark_returns)
        
        # 3. Drawdown
        ax3 = plt.subplot(4, 2, 3)
        self._plot_drawdown(ax3, returns)
        
        # 4. Rolling Sharpe
        ax4 = plt.subplot(4, 2, 4)
        self._plot_rolling_sharpe(ax4, returns)
        
        # 5. Monthly returns heatmap
        ax5 = plt.subplot(4, 2, 5)
        self._plot_monthly_returns(ax5, returns)
        
        # 6. Return distribution
        ax6 = plt.subplot(4, 2, 6)
        self._plot_return_distribution(ax6, returns)
        
        # 7. Rolling volatility
        ax7 = plt.subplot(4, 2, 7)
        self._plot_rolling_volatility(ax7, returns)
        
        # 8. Risk contribution
        ax8 = plt.subplot(4, 2, 8)
        if positions is not None:
            self._plot_position_contribution(ax8, positions, returns)
        else:
            self._plot_risk_decomposition(ax8, risk_metrics)
        
        plt.tight_layout()
        
        # Save report
        report_path = self.output_dir / f"{report_name}_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(report_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        # Generate HTML report
        html_path = self._generate_html_report(
            metrics, risk_metrics, returns, benchmark_returns, report_name
        )
        
        logger.info(f"Report saved to {report_path}")
        
        return str(report_path)
    
    def _format_summary(
        self,
        metrics: Dict[str, float],
        risk_metrics: Any
    ) -> str:
        """Format performance summary text"""
        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    STRATEGY PERFORMANCE SUMMARY                ║
╠═══════════════════════════════════════════════════════════════╣
║ RETURN METRICS                                                 ║
║   Total Return:         {metrics.get('total_return', 0):>10.2%}                       ║
║   Annual Return:        {metrics.get('annual_return', 0):>10.2%}                       ║
║   Annual Volatility:    {metrics.get('annual_volatility', 0):>10.2%}                       ║
║                                                               ║
║ RISK-ADJUSTED METRICS                                          ║
║   Sharpe Ratio:         {metrics.get('sharpe_ratio', 0):>10.2f}                       ║
║   Sortino Ratio:        {metrics.get('sortino_ratio', 0):>10.2f}                       ║
║   Calmar Ratio:         {metrics.get('calmar_ratio', 0):>10.2f}                       ║
║   Information Ratio:    {metrics.get('information_ratio', 0):>10.2f}                       ║
║                                                               ║
║ RISK METRICS                                                   ║
║   Max Drawdown:         {risk_metrics.max_drawdown:>10.2%}                       ║
║   VaR (95%):            {risk_metrics.var_95:>10.2%}                       ║
║   CVaR (95%):           {risk_metrics.cvar_95:>10.2%}                       ║
║   Beta:                 {risk_metrics.beta:>10.2f}                       ║
║   Tracking Error:       {risk_metrics.tracking_error:>10.2%}                       ║
║                                                               ║
║ TRADE METRICS                                                  ║
║   Win Rate:             {metrics.get('win_rate', 0):>10.2%}                       ║
║   Profit Factor:        {metrics.get('profit_factor', 0):>10.2f}                       ║
║   Avg Win:              {metrics.get('avg_win', 0):>10.2%}                       ║
║   Avg Loss:             {metrics.get('avg_loss', 0):>10.2%}                       ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return summary
    
    def _plot_equity_curve(self, ax, returns, benchmark_returns):
        """Plot equity curve"""
        equity = (1 + returns).cumprod()
        equity.plot(ax=ax, label="Strategy", linewidth=2)
        
        if benchmark_returns is not None:
            bench_equity = (1 + benchmark_returns).cumprod()
            bench_equity.plot(ax=ax, label="Benchmark", linewidth=1, alpha=0.7)
        
        ax.set_title("Cumulative Returns", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("")
    
    def _plot_drawdown(self, ax, returns):
        """Plot drawdown"""
        equity = (1 + returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        
        ax.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color="red")
        ax.plot(drawdown, color="red", linewidth=1)
        ax.set_title("Drawdown", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("")
    
    def _plot_rolling_sharpe(self, ax, returns, window=126):
        """Plot rolling Sharpe ratio"""
        rolling_sharpe = returns.rolling(window).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        
        rolling_sharpe.plot(ax=ax, linewidth=1.5)
        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        ax.axhline(y=1, color="green", linestyle="--", alpha=0.5, label="Target Sharpe")
        ax.set_title(f"Rolling Sharpe Ratio ({window}d)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("")
        ax.legend()
    
    def _plot_monthly_returns(self, ax, returns):
        """Plot monthly returns heatmap"""
        monthly = returns.resample("M").apply(lambda x: (1 + x).prod() - 1)
        monthly_table = monthly.to_frame("return")
        monthly_table["year"] = monthly_table.index.year
        monthly_table["month"] = monthly_table.index.month
        
        pivot = monthly_table.pivot_table(
            values="return",
            index="year",
            columns="month",
            aggfunc="first"
        )
        
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".1%",
            cmap="RdYlGn",
            center=0,
            ax=ax,
            cbar_kws={"label": "Return"}
        )
        ax.set_title("Monthly Returns", fontsize=12)
        ax.set_xlabel("Month")
        ax.set_ylabel("Year")
    
    def _plot_return_distribution(self, ax, returns):
        """Plot return distribution"""
        returns.hist(ax=ax, bins=50, alpha=0.7, density=True)
        
        # Fit normal distribution
        mean, std = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        normal_dist = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
        ax.plot(x, normal_dist, "r--", label="Normal")
        
        ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
        ax.set_title("Return Distribution", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_rolling_volatility(self, ax, returns, window=63):
        """Plot rolling volatility"""
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)
        
        rolling_vol.plot(ax=ax, linewidth=1.5)
        ax.set_title(f"Rolling Volatility ({window}d)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("")
    
    def _plot_risk_decomposition(self, ax, risk_metrics):
        """Plot risk decomposition"""
        metrics = {
            "VaR": risk_metrics.var_95,
            "CVaR": risk_metrics.cvar_95,
            "Max DD": risk_metrics.max_drawdown,
            "Volatility": risk_metrics.volatility
        }
        
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        ax.bar(metrics.keys(), [abs(v) for v in metrics.values()], color=colors)
        ax.set_title("Risk Metrics Summary", fontsize=12)
        ax.set_ylabel("Value")
    
    def _plot_position_contribution(self, ax, positions, returns):
        """Plot position contribution"""
        # Simplified - in practice, calculate actual contribution
        ax.text(0.5, 0.5, "Position Contribution\n(Requires detailed position data)",
                ha="center", va="center", fontsize=12)
        ax.set_title("Position Contribution", fontsize=12)
    
    def _generate_html_report(
        self,
        metrics,
        risk_metrics,
        returns,
        benchmark_returns,
        report_name
    ) -> str:
        """Generate HTML report"""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Report - {report_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
    </style>
</head>
<body>
    <h1>Strategy Performance Report</h1>
    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <h2>Performance Summary</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total Return</td><td class="{'positive' if metrics.get('total_return', 0) > 0 else 'negative'}">{metrics.get('total_return', 0):.2%}</td></tr>
        <tr><td>Annual Return</td><td class="{'positive' if metrics.get('annual_return', 0) > 0 else 'negative'}">{metrics.get('annual_return', 0):.2%}</td></tr>
        <tr><td>Sharpe Ratio</td><td>{metrics.get('sharpe_ratio', 0):.2f}</td></tr>
        <tr><td>Max Drawdown</td><td class="negative">{risk_metrics.max_drawdown:.2%}</td></tr>
        <tr><td>Win Rate</td><td>{metrics.get('win_rate', 0):.2%}</td></tr>
    </table>
    
    <h2>Risk Metrics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>VaR (95%)</td><td>{risk_metrics.var_95:.2%}</td></tr>
        <tr><td>CVaR (95%)</td><td>{risk_metrics.cvar_95:.2%}</td></tr>
        <tr><td>Volatility</td><td>{risk_metrics.volatility:.2%}</td></tr>
        <tr><td>Beta</td><td>{risk_metrics.beta:.2f}</td></tr>
        <tr><td>Sortino Ratio</td><td>{risk_metrics.sortino_ratio:.2f}</td></tr>
    </table>
</body>
</html>
"""
        
        html_path = self.output_dir / f"{report_name}_{datetime.now().strftime('%Y%m%d')}.html"
        with open(html_path, "w") as f:
            f.write(html_template)
        
        return str(html_path)
