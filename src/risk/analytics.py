"""
Risk Analytics - Performance and risk analytics using QuantStats
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from loguru import logger
import matplotlib.pyplot as plt


class RiskAnalytics:
    """
    Risk and Performance Analytics
    
    Features:
    - Performance metrics calculation
    - Risk decomposition
    - Factor exposure analysis
    - Attribution analysis
    
    Uses QuantStats for professional-grade analytics.
    """
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        Initialize risk analytics
        
        Args:
            risk_free_rate: Annual risk-free rate
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_performance_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Dictionary of metrics
        """
        # Basic metrics
        total_return = (1 + returns).prod() - 1
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        
        # Risk-adjusted metrics
        sharpe = (annual_return - self.risk_free_rate) / annual_vol if annual_vol > 0 else 0
        
        # Downside metrics
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino = (annual_return - self.risk_free_rate) / downside_std if downside_std > 0 else 0
        
        # Drawdown metrics
        equity = (1 + returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        max_dd = abs(drawdown.min())
        avg_dd = abs(drawdown.mean())
        
        # Recovery metrics
        dd_periods = self._calculate_drawdown_periods(drawdown)
        avg_recovery = np.mean(dd_periods) if dd_periods else 0
        
        # Win/Loss metrics
        win_rate = (returns > 0).sum() / len(returns)
        avg_win = returns[returns > 0].mean() if (returns > 0).any() else 0
        avg_loss = returns[returns < 0].mean() if (returns < 0).any() else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        metrics = {
            "total_return": total_return,
            "annual_return": annual_return,
            "annual_volatility": annual_vol,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": max_dd,
            "avg_drawdown": avg_dd,
            "avg_recovery_days": avg_recovery,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "skewness": returns.skew(),
            "kurtosis": returns.kurtosis(),
            "calmar_ratio": annual_return / max_dd if max_dd > 0 else 0
        }
        
        # Benchmark-relative metrics
        if benchmark_returns is not None:
            metrics.update(
                self._calculate_relative_metrics(returns, benchmark_returns)
            )
        
        return metrics
    
    def _calculate_relative_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[str, float]:
        """Calculate benchmark-relative metrics"""
        # Align indices
        common_idx = returns.index.intersection(benchmark_returns.index)
        returns = returns[common_idx]
        benchmark_returns = benchmark_returns[common_idx]
        
        # Excess returns
        excess = returns - benchmark_returns
        
        # Beta
        cov = returns.cov(benchmark_returns)
        var_bench = benchmark_returns.var()
        beta = cov / var_bench if var_bench > 0 else 0
        
        # Alpha (annualized)
        alpha = (excess.mean() * 252)
        
        # Tracking error
        tracking_error = excess.std() * np.sqrt(252)
        
        # Information ratio
        ir = alpha / tracking_error if tracking_error > 0 else 0
        
        # Correlation
        correlation = returns.corr(benchmark_returns)
        
        # R-squared
        r_squared = correlation ** 2
        
        # Treynor ratio
        treynor = (returns.mean() * 252 - self.risk_free_rate) / beta if beta != 0 else 0
        
        return {
            "alpha": alpha,
            "beta": beta,
            "tracking_error": tracking_error,
            "information_ratio": ir,
            "correlation": correlation,
            "r_squared": r_squared,
            "treynor_ratio": treynor
        }
    
    def _calculate_drawdown_periods(
        self,
        drawdown: pd.Series
    ) -> list:
        """Calculate drawdown periods"""
        periods = []
        in_drawdown = False
        start = None
        
        for i, dd in enumerate(drawdown):
            if dd < 0 and not in_drawdown:
                in_drawdown = True
                start = i
            elif dd >= 0 and in_drawdown:
                in_drawdown = False
                periods.append(i - start)
        
        if in_drawdown:
            periods.append(len(drawdown) - start)
        
        return periods
    
    def generate_tearsheet(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        output_path: Optional[str] = None
    ):
        """
        Generate performance tearsheet
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns
            output_path: Path to save the report
        """
        try:
            import quantstats as qs
            
            # Generate quantstats report
            if benchmark_returns is not None:
                qs.reports.html(
                    returns,
                    benchmark=benchmark_returns,
                    output=output_path or "outputs/tearsheet.html",
                    title="Strategy Performance Report"
                )
            else:
                qs.reports.html(
                    returns,
                    output=output_path or "outputs/tearsheet.html",
                    title="Strategy Performance Report"
                )
            
            logger.info(f"Tearsheet saved to {output_path or 'outputs/tearsheet.html'}")
            
        except ImportError:
            logger.warning("quantstats not installed, using basic plotting")
            self._generate_basic_report(returns, benchmark_returns, output_path)
    
    def _generate_basic_report(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series],
        output_path: Optional[str]
    ):
        """Generate basic performance report without quantstats"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Equity curve
        ax1 = axes[0, 0]
        equity = (1 + returns).cumprod()
        equity.plot(ax=ax1, label="Strategy")
        
        if benchmark_returns is not None:
            bench_equity = (1 + benchmark_returns).cumprod()
            bench_equity.plot(ax=ax1, label="Benchmark")
        
        ax1.set_title("Cumulative Returns")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        ax2 = axes[0, 1]
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        drawdown.plot(ax=ax2, kind="area", alpha=0.3, color="red")
        ax2.set_title("Drawdown")
        ax2.grid(True, alpha=0.3)
        
        # Monthly returns
        ax3 = axes[1, 0]
        monthly_returns = returns.resample("M").apply(lambda x: (1 + x).prod() - 1)
        colors = ["green" if x > 0 else "red" for x in monthly_returns]
        monthly_returns.plot(kind="bar", ax=ax3, color=colors, alpha=0.7)
        ax3.set_title("Monthly Returns")
        ax3.set_xticklabels([])
        ax3.grid(True, alpha=0.3)
        
        # Return distribution
        ax4 = axes[1, 1]
        returns.hist(ax=ax4, bins=50, alpha=0.7)
        ax4.axvline(x=0, color="red", linestyle="--")
        ax4.set_title("Return Distribution")
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            logger.info(f"Report saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def calculate_rolling_metrics(
        self,
        returns: pd.Series,
        window: int = 252,
        metrics: list = ["sharpe", "volatility", "max_drawdown"]
    ) -> pd.DataFrame:
        """
        Calculate rolling metrics
        
        Args:
            returns: Returns series
            window: Rolling window
            metrics: List of metrics to calculate
            
        Returns:
            DataFrame with rolling metrics
        """
        results = {}
        
        if "sharpe" in metrics:
            rolling_sharpe = returns.rolling(window).apply(
                lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
            )
            results["rolling_sharpe"] = rolling_sharpe
        
        if "volatility" in metrics:
            rolling_vol = returns.rolling(window).std() * np.sqrt(252)
            results["rolling_volatility"] = rolling_vol
        
        if "max_drawdown" in metrics:
            rolling_dd = returns.rolling(window).apply(
                lambda x: self._rolling_max_dd(x)
            )
            results["rolling_max_drawdown"] = rolling_dd
        
        if "return" in metrics:
            rolling_ret = returns.rolling(window).apply(
                lambda x: (1 + x).prod() - 1
            )
            results["rolling_return"] = rolling_ret
        
        return pd.DataFrame(results)
    
    def _rolling_max_dd(self, returns: pd.Series) -> float:
        """Calculate max drawdown for a series"""
        equity = (1 + returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        return abs(drawdown.min())
