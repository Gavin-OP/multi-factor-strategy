"""
Factor Engine - Factor calculation, testing, and evaluation

Professional factor testing framework:
- IC (Information Coefficient) analysis
- IR (Information Ratio) calculation
- Group testing (quintile analysis)
- Factor turnover analysis
- Factor correlation analysis
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from loguru import logger
from scipy import stats
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns

from src.factors.base import FactorBase, FactorRegistry


@dataclass
class FactorStats:
    """Factor statistics"""
    name: str
    ic_mean: float
    ic_std: float
    icir: float
    ic_t_stat: float
    ic_positive_ratio: float
    group_spread: float
    monotonicity: float
    turnover: float
    is_effective: bool


class FactorTester:
    """
    Factor testing and evaluation
    
    Professional factor testing following industry standards:
    - IC/IR analysis
    - Group testing (quintile analysis)
    - Monotonicity test
    - Turnover analysis
    """
    
    def __init__(
        self,
        ic_threshold: float = 0.02,
        icir_threshold: float = 0.5,
        n_groups: int = 5
    ):
        """
        Initialize factor tester
        
        Args:
            ic_threshold: Minimum IC mean threshold
            icir_threshold: Minimum ICIR threshold
            n_groups: Number of groups for group testing
        """
        self.ic_threshold = ic_threshold
        self.icir_threshold = icir_threshold
        self.n_groups = n_groups
    
    def calculate_ic(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        method: str = "spearman"
    ) -> pd.DataFrame:
        """
        Calculate Information Coefficient
        
        Args:
            factor_df: DataFrame with columns [symbol, date, factor_value]
            returns_df: DataFrame with columns [symbol, date, forward_return]
            method: Correlation method ("spearman" or "pearson")
            
        Returns:
            DataFrame with IC time series
        """
        # Merge factor and returns
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Calculate IC for each date
        ic_list = []
        
        for date, group in merged.groupby("date"):
            if len(group) < 10:  # Minimum sample size
                continue
            
            if method == "spearman":
                ic, pvalue = stats.spearmanr(
                    group["factor_value"],
                    group["forward_return"],
                    nan_policy="omit"
                )
            else:
                ic, pvalue = stats.pearsonr(
                    group["factor_value"].dropna(),
                    group["forward_return"].dropna()
                )
            
            ic_list.append({
                "date": date,
                "ic": ic,
                "pvalue": pvalue,
                "n_stocks": len(group)
            })
        
        return pd.DataFrame(ic_list)
    
    def calculate_ic_stats(self, ic_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate IC statistics"""
        ic_series = ic_df["ic"].dropna()
        
        if len(ic_series) == 0:
            return {}
        
        stats_dict = {
            "ic_mean": ic_series.mean(),
            "ic_std": ic_series.std(),
            "icir": ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            "ic_t_stat": ic_series.mean() / (ic_series.std() / np.sqrt(len(ic_series))),
            "ic_positive_ratio": (ic_series > 0).mean(),
            "ic_significant_ratio": (ic_df["pvalue"] < 0.05).mean()
        }
        
        return stats_dict
    
    def group_test(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Group testing (quintile analysis)
        
        Args:
            factor_df: DataFrame with factor values
            returns_df: DataFrame with forward returns
            
        Returns:
            Tuple of (group_returns, group_statistics)
        """
        # Merge data
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Assign groups
        merged["group"] = merged.groupby("date")["factor_value"].transform(
            lambda x: pd.qcut(x, self.n_groups, labels=False, duplicates="drop") + 1
        )
        
        # Calculate group returns
        group_returns = merged.groupby(["date", "group"])["forward_return"].mean().unstack()
        group_returns.columns = [f"Group_{i}" for i in group_returns.columns]
        
        # Calculate statistics
        group_stats = []
        for g in range(1, self.n_groups + 1):
            col = f"Group_{g}"
            if col in group_returns.columns:
                group_stats.append({
                    "group": g,
                    "mean_return": group_returns[col].mean(),
                    "std_return": group_returns[col].std(),
                    "sharpe": group_returns[col].mean() / group_returns[col].std() * np.sqrt(252),
                    "hit_rate": (group_returns[col] > 0).mean()
                })
        
        group_stats_df = pd.DataFrame(group_stats)
        
        # Calculate spread (top - bottom)
        if len(group_stats_df) >= 2:
            spread = group_returns.iloc[:, -1] - group_returns.iloc[:, 0]
            spread_stats = {
                "spread_mean": spread.mean(),
                "spread_std": spread.std(),
                "spread_sharpe": spread.mean() / spread.std() * np.sqrt(252),
                "spread_t_stat": spread.mean() / (spread.std() / np.sqrt(len(spread)))
            }
        else:
            spread_stats = {}
        
        return group_returns, group_stats_df, spread_stats
    
    def calculate_monotonicity(
        self,
        group_stats: pd.DataFrame
    ) -> float:
        """
        Calculate monotonicity score
        
        Higher score indicates better monotonic relationship
        between factor values and returns
        """
        returns = group_stats["mean_return"].values
        n = len(returns)
        
        if n < 2:
            return 0
        
        # Count pairs that are correctly ordered
        correct = 0
        total = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                total += 1
                if returns[i] < returns[j]:
                    correct += 1
        
        return correct / total if total > 0 else 0
    
    def calculate_turnover(
        self,
        factor_df: pd.DataFrame,
        top_pct: float = 0.2
    ) -> float:
        """
        Calculate factor turnover
        
        Measures how much the top/bottom stocks change over time
        """
        # Get top stocks for each date
        top_stocks = factor_df.groupby("date").apply(
            lambda g: set(g.nlargest(int(len(g) * top_pct), "factor_value")["symbol"])
        )
        
        # Calculate turnover
        turnovers = []
        dates = sorted(top_stocks.index)
        
        for i in range(1, len(dates)):
            prev_stocks = top_stocks[dates[i-1]]
            curr_stocks = top_stocks[dates[i]]
            
            if len(prev_stocks) > 0 and len(curr_stocks) > 0:
                turnover = 1 - len(prev_stocks & curr_stocks) / len(curr_stocks)
                turnovers.append(turnover)
        
        return np.mean(turnovers) if turnovers else 0
    
    def test_factor(
        self,
        factor: FactorBase,
        df: pd.DataFrame,
        forward_periods: List[int] = [1, 5, 20]
    ) -> Dict[str, Any]:
        """
        Comprehensive factor test
        
        Args:
            factor: Factor instance
            df: DataFrame with OHLCV data
            forward_periods: Forward return periods to test
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"Testing factor: {factor.name}")
        
        results = {
            "factor_name": factor.name,
            "metadata": factor.get_metadata(),
            "tests": {}
        }
        
        # Calculate factor values
        factor_df = factor.calculate(df)
        
        if factor_df.empty:
            logger.warning(f"Factor {factor.name} returned empty data")
            return results
        
        # Calculate forward returns
        for period in forward_periods:
            df_copy = df.copy()
            df_copy["forward_return"] = df_copy.groupby("symbol")["close"].transform(
                lambda x: x.shift(-period) / x - 1
            )
            
            # IC test
            ic_df = self.calculate_ic(factor_df, df_copy)
            if ic_df.empty:
                continue
            
            ic_stats = self.calculate_ic_stats(ic_df)
            
            # Group test
            group_returns, group_stats, spread_stats = self.group_test(factor_df, df_copy)
            
            # Monotonicity
            monotonicity = self.calculate_monotonicity(group_stats)
            
            # Turnover
            turnover = self.calculate_turnover(factor_df)
            
            # Determine effectiveness
            is_effective = (
                abs(ic_stats.get("ic_mean", 0)) >= self.ic_threshold and
                abs(ic_stats.get("icir", 0)) >= self.icir_threshold
            )
            
            results["tests"][f"{period}d"] = {
                "ic_stats": ic_stats,
                "group_stats": group_stats.to_dict("records"),
                "spread_stats": spread_stats,
                "monotonicity": monotonicity,
                "turnover": turnover,
                "is_effective": is_effective
            }
        
        return results


class FactorEngine:
    """
    Factor Engine - Main interface for factor operations
    
    Features:
    - Factor calculation
    - Factor testing
    - Factor storage
    - Factor combination
    - Factor analysis visualization
    """
    
    def __init__(self, storage=None, config: Optional[Dict] = None):
        """
        Initialize factor engine
        
        Args:
            storage: DataStorage instance
            config: Configuration dictionary
        """
        self.storage = storage
        self.config = config or {}
        self.tester = FactorTester(
            ic_threshold=self.config.get("ic_threshold", 0.02),
            icir_threshold=self.config.get("icir_threshold", 0.5)
        )
        
        # Cache for calculated factors
        self._factor_cache: Dict[str, pd.DataFrame] = {}
        
        logger.info("FactorEngine initialized")
    
    def calculate_factors(
        self,
        df: pd.DataFrame,
        factor_names: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Calculate multiple factors
        
        Args:
            df: DataFrame with OHLCV data
            factor_names: List of factor names (None for all)
            show_progress: Show progress bar
            
        Returns:
            DataFrame with all factor values
        """
        if factor_names is None:
            factors = FactorRegistry.get_all()
            factor_names = list(factors.keys())
            factors = list(factors.values())
        else:
            factors = [FactorRegistry.get(name) for name in factor_names]
            factors = [f for f in factors if f is not None]
        
        all_factors = []
        
        iterator = factors
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(factors, desc="Calculating factors")
        
        for factor in iterator:
            try:
                factor_df = factor.calculate(df)
                if not factor_df.empty:
                    factor_df = factor_df.rename(
                        columns={"factor_value": factor.name}
                    )
                    all_factors.append(factor_df)
            except Exception as e:
                logger.error(f"Error calculating {factor.name}: {e}")
        
        if not all_factors:
            return pd.DataFrame()
        
        # Merge all factors
        result = all_factors[0]
        for factor_df in all_factors[1:]:
            result = result.merge(
                factor_df[["symbol", "date", factor_df.columns[-1]]],
                on=["symbol", "date"],
                how="outer"
            )
        
        logger.info(f"Calculated {len(factor_names)} factors")
        
        return result
    
    def test_all_factors(
        self,
        df: pd.DataFrame,
        forward_periods: List[int] = [1, 5, 20],
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Test all registered factors
        
        Args:
            df: DataFrame with OHLCV data
            forward_periods: Forward return periods
            show_progress: Show progress bar
            
        Returns:
            Dictionary with test results for all factors
        """
        factors = FactorRegistry.get_all()
        results = {}
        
        iterator = list(factors.values())
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc="Testing factors")
        
        for factor in iterator:
            result = self.tester.test_factor(factor, df, forward_periods)
            results[factor.name] = result
        
        # Summary
        effective_factors = [
            name for name, result in results.items()
            if any(
                test.get("is_effective", False)
                for test in result.get("tests", {}).values()
            )
        ]
        
        logger.info(
            f"Tested {len(results)} factors, "
            f"{len(effective_factors)} effective"
        )
        
        return results
    
    def get_factor_correlation(
        self,
        factor_df: pd.DataFrame,
        method: str = "spearman"
    ) -> pd.DataFrame:
        """
        Calculate factor correlation matrix
        
        Args:
            factor_df: DataFrame with factor values
            method: Correlation method
            
        Returns:
            Correlation matrix
        """
        # Pivot to wide format
        factor_cols = [col for col in factor_df.columns 
                       if col not in ["symbol", "date"]]
        
        # Calculate cross-sectional correlation
        correlations = []
        
        for col1 in factor_cols:
            row = []
            for col2 in factor_cols:
                corr = factor_df.groupby("date").apply(
                    lambda g: g[col1].corr(g[col2], method=method)
                ).mean()
                row.append(corr)
            correlations.append(row)
        
        corr_df = pd.DataFrame(
            correlations,
            index=factor_cols,
            columns=factor_cols
        )
        
        return corr_df
    
    def visualize_factor_test(
        self,
        test_results: Dict[str, Any],
        output_path: Optional[str] = None
    ):
        """
        Visualize factor test results
        
        Args:
            test_results: Test results dictionary
            output_path: Path to save the figure
        """
        factor_name = test_results["factor_name"]
        tests = test_results["tests"]
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Factor Analysis: {factor_name}", fontsize=14, fontweight="bold")
        
        # 1. IC time series
        ax1 = axes[0, 0]
        for period, test in tests.items():
            if "ic_stats" in test:
                # We need to regenerate IC data for visualization
                pass
        ax1.set_title("IC Time Series")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("IC")
        ax1.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        
        # 2. IC statistics
        ax2 = axes[0, 1]
        ic_means = []
        icirs = []
        labels = []
        for period, test in tests.items():
            ic_stats = test.get("ic_stats", {})
            ic_means.append(ic_stats.get("ic_mean", 0))
            icirs.append(ic_stats.get("icir", 0))
            labels.append(period)
        
        x = np.arange(len(labels))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, ic_means, width, label="IC Mean")
        ax2_twin = ax2.twinx()
        bars2 = ax2_twin.bar(x + width/2, icirs, width, label="ICIR", color="orange")
        
        ax2.set_xlabel("Forward Period")
        ax2.set_ylabel("IC Mean")
        ax2_twin.set_ylabel("ICIR")
        ax2.set_title("IC Statistics by Period")
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)
        ax2.legend(loc="upper left")
        ax2_twin.legend(loc="upper right")
        
        # 3. Group returns
        ax3 = axes[1, 0]
        for period, test in tests.items():
            group_stats = test.get("group_stats", [])
            if group_stats:
                groups = [g["group"] for g in group_stats]
                returns = [g["mean_return"] * 100 for g in group_stats]
                ax3.bar(groups, returns, alpha=0.5, label=period)
        
        ax3.set_xlabel("Group")
        ax3.set_ylabel("Mean Return (%)")
        ax3.set_title("Group Returns")
        ax3.legend()
        ax3.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        
        # 4. Summary statistics
        ax4 = axes[1, 1]
        ax4.axis("off")
        
        summary_text = f"""
Factor: {factor_name}
Category: {test_results["metadata"].get("category", "N/A")}

Test Results:
"""
        for period, test in tests.items():
            ic_stats = test.get("ic_stats", {})
            summary_text += f"""
{period} Forward Return:
  IC Mean: {ic_stats.get("ic_mean", 0):.4f}
  IC Std:  {ic_stats.get("ic_std", 0):.4f}
  ICIR:    {ic_stats.get("icir", 0):.4f}
  T-Stat:  {ic_stats.get("ic_t_stat", 0):.4f}
  Monotonicity: {test.get("monotonicity", 0):.4f}
  Turnover: {test.get("turnover", 0):.4f}
  Effective: {"Yes" if test.get("is_effective") else "No"}
"""
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, 
                 fontsize=10, verticalalignment="center", fontfamily="monospace")
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            logger.info(f"Saved visualization to {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def save_effective_factors(
        self,
        test_results: Dict[str, Any],
        min_icir: float = 0.5
    ):
        """
        Save effective factors to database
        
        Args:
            test_results: Test results dictionary
            min_icir: Minimum ICIR threshold
        """
        if not self.storage:
            logger.warning("No storage configured, cannot save factors")
            return
        
        for factor_name, result in test_results.items():
            tests = result.get("tests", {})
            
            # Check if any period meets threshold
            for period, test in tests.items():
                icir = test.get("ic_stats", {}).get("icir", 0)
                
                if abs(icir) >= min_icir:
                    self.storage.save_factor_metadata(
                        factor_name=factor_name,
                        factor_category=result["metadata"].get("category", "unknown"),
                        description=result["metadata"].get("description", ""),
                        ic_stats=test.get("ic_stats", {})
                    )
                    logger.info(f"Saved effective factor: {factor_name}")
                    break
