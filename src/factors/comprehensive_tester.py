"""
Comprehensive Factor Validation - Complete factor effectiveness testing

This module implements professional factor validation methods used by
top quantitative hedge funds:

1. IC Analysis (Information Coefficient)
2. Regression Method (Factor Return, t-statistics)
3. Group Testing (Quintile/Decile Analysis)
4. IC Decay Analysis (Half-life)
5. Turnover Analysis
6. Neutralization (Industry/Market Cap)
7. Statistical Tests (t-test, Wilcoxon)
8. Factor Correlation & Orthogonalization
9. Monotonicity Testing
10. Factor Periodicity Analysis
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from loguru import logger
from scipy import stats
from scipy.optimize import minimize
from dataclasses import dataclass, field
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


@dataclass
class ComprehensiveFactorStats:
    """Complete factor statistics for professional validation"""
    # Basic Info
    name: str
    category: str
    
    # IC Analysis
    ic_mean: float = 0.0
    ic_std: float = 0.0
    icir: float = 0.0
    ic_t_stat: float = 0.0
    ic_positive_ratio: float = 0.0
    ic_significant_ratio: float = 0.0
    ic_abs_mean: float = 0.0
    
    # Regression Method
    factor_return_mean: float = 0.0
    factor_return_t_stat: float = 0.0
    t_value_mean: float = 0.0
    t_value_significant_ratio: float = 0.0
    
    # Group Testing
    group_returns: List[float] = field(default_factory=list)
    group_sharpe: List[float] = field(default_factory=list)
    spread_return: float = 0.0
    spread_sharpe: float = 0.0
    spread_t_stat: float = 0.0
    spread_p_value: float = 0.0
    monotonicity: float = 0.0
    monotonicity_score: float = 0.0
    
    # IC Decay
    ic_half_life: float = 0.0
    ic_decay_curve: List[float] = field(default_factory=list)
    
    # Turnover
    turnover_mean: float = 0.0
    turnover_std: float = 0.0
    autocorrelation: float = 0.0
    
    # Statistical Tests
    wilcoxon_stat: float = 0.0
    wilcoxon_pvalue: float = 0.0
    ks_stat: float = 0.0
    ks_pvalue: float = 0.0
    
    # Risk-Adjusted
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # Effectiveness
    is_effective: bool = False
    effectiveness_score: float = 0.0
    failure_reasons: List[str] = field(default_factory=list)


class FactorPreprocessor:
    """
    Factor data preprocessing
    
    Methods:
    - Winsorization (remove outliers)
    - Standardization (z-score)
    - Industry Neutralization
    - Market Cap Neutralization
    """
    
    @staticmethod
    def winsorize(
        df: pd.DataFrame,
        column: str = "factor_value",
        method: str = "mad",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Winsorize factor values to remove outliers
        
        Methods:
        - mad: Median Absolute Deviation (robust)
        - std: Standard Deviation
        - quantile: Quantile-based
        """
        df = df.copy()
        
        if method == "mad":
            # MAD method (most robust)
            median = df[column].median()
            mad = np.median(np.abs(df[column] - median))
            upper = median + threshold * mad * 1.4826
            lower = median - threshold * mad * 1.4826
        
        elif method == "std":
            mean = df[column].mean()
            std = df[column].std()
            upper = mean + threshold * std
            lower = mean - threshold * std
        
        elif method == "quantile":
            lower = df[column].quantile(0.01)
            upper = df[column].quantile(0.99)
        
        else:
            raise ValueError(f"Unknown winsorize method: {method}")
        
        df[column] = df[column].clip(lower, upper)
        return df
    
    @staticmethod
    def standardize(
        df: pd.DataFrame,
        column: str = "factor_value",
        method: str = "zscore"
    ) -> pd.DataFrame:
        """
        Standardize factor values (cross-sectionally)
        
        Methods:
        - zscore: Standard normal
        - rank: Rank transformation
        - quantile: Quantile normalization
        """
        df = df.copy()
        
        if method == "zscore":
            df[column] = df.groupby("date")[column].transform(
                lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x - x.mean()
            )
        
        elif method == "rank":
            df[column] = df.groupby("date")[column].transform(
                lambda x: x.rank(pct=True)
            )
        
        elif method == "quantile":
            df[column] = df.groupby("date")[column].transform(
                lambda x: pd.qcut(x, 10, labels=False, duplicates="drop") / 10
            )
        
        return df
    
    @staticmethod
    def neutralize_industry(
        df: pd.DataFrame,
        industry_mapping: Dict[str, str],
        column: str = "factor_value"
    ) -> pd.DataFrame:
        """
        Industry neutralization using regression residuals
        
        Args:
            df: DataFrame with factor values
            industry_mapping: Dict mapping symbol to industry
            column: Factor column to neutralize
        """
        df = df.copy()
        df["industry"] = df["symbol"].map(industry_mapping)
        
        # Create industry dummies
        industries = df["industry"].dropna().unique()
        
        def neutralize_group(group):
            if len(group) < 5:
                return group[column]
            
            # Create dummy variables
            for ind in industries:
                group[f"ind_{ind}"] = (group["industry"] == ind).astype(float)
            
            # Regression on industry dummies
            X = group[[f"ind_{ind}" for ind in industries]].values
            y = group[column].values
            
            try:
                # OLS regression
                coef = np.linalg.lstsq(X, y, rcond=None)[0]
                residual = y - X @ coef
                return pd.Series(residual, index=group.index)
            except:
                return group[column]
        
        df[column] = df.groupby("date").apply(neutralize_group).reset_index(level=0, drop=True)
        
        return df.drop(columns=["industry"] + [f"ind_{ind}" for ind in industries], errors="ignore")
    
    @staticmethod
    def neutralize_market_cap(
        df: pd.DataFrame,
        market_cap_df: pd.DataFrame,
        column: str = "factor_value"
    ) -> pd.DataFrame:
        """
        Market cap neutralization
        
        Args:
            df: DataFrame with factor values
            market_cap_df: DataFrame with columns [symbol, date, market_cap]
            column: Factor column to neutralize
        """
        df = df.copy()
        
        # Merge market cap
        df = df.merge(market_cap_df[["symbol", "date", "market_cap"]], 
                      on=["symbol", "date"], how="left")
        
        # Log market cap
        df["log_mcap"] = np.log(df["market_cap"])
        
        def neutralize_group(group):
            if len(group) < 5 or group["log_mcap"].isna().all():
                return group[column]
            
            # Regression on log market cap
            valid = group.dropna(subset=["log_mcap", column])
            if len(valid) < 5:
                return group[column]
            
            X = valid["log_mcap"].values.reshape(-1, 1)
            y = valid[column].values
            
            try:
                coef = np.linalg.lstsq(X, y, rcond=None)[0]
                residual = y - X @ coef
                
                result = group[column].copy()
                result[valid.index] = residual
                return result
            except:
                return group[column]
        
        df[column] = df.groupby("date").apply(neutralize_group).reset_index(level=0, drop=True)
        
        return df.drop(columns=["market_cap", "log_mcap"], errors="ignore")


class ComprehensiveFactorTester:
    """
    Complete Factor Testing Framework
    
    Implements all professional factor validation methods:
    
    1. IC Analysis
       - IC mean, std, ICIR
       - IC t-statistics
       - IC cumulative curve
       - IC significance ratio
    
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
    
    def __init__(
        self,
        ic_threshold: float = 0.02,
        icir_threshold: float = 0.5,
        n_groups: int = 5,
        max_decay_periods: int = 20,
        significance_level: float = 0.05
    ):
        self.ic_threshold = ic_threshold
        self.icir_threshold = icir_threshold
        self.n_groups = n_groups
        self.max_decay_periods = max_decay_periods
        self.significance_level = significance_level
        
        self.preprocessor = FactorPreprocessor()
    
    def calculate_ic_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        method: str = "spearman"
    ) -> Dict[str, Any]:
        """
        Comprehensive IC Analysis
        """
        # Merge data
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Calculate IC series
        ic_list = []
        
        for date, group in merged.groupby("date"):
            if len(group) < 10:
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
        
        ic_df = pd.DataFrame(ic_list)
        
        if ic_df.empty:
            return {}
        
        ic_series = ic_df["ic"].dropna()
        
        # Calculate statistics
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        icir = ic_mean / ic_std if ic_std > 0 else 0
        
        # t-statistics
        n = len(ic_series)
        ic_t_stat = ic_mean / (ic_std / np.sqrt(n)) if ic_std > 0 else 0
        
        # Ratios
        ic_positive_ratio = (ic_series > 0).mean()
        ic_significant_ratio = (ic_df["pvalue"] < self.significance_level).mean()
        ic_abs_mean = ic_series.abs().mean()
        
        return {
            "ic_df": ic_df,
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "icir": icir,
            "ic_t_stat": ic_t_stat,
            "ic_positive_ratio": ic_positive_ratio,
            "ic_significant_ratio": ic_significant_ratio,
            "ic_abs_mean": ic_abs_mean,
            "n_periods": n
        }
    
    def calculate_regression_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Regression Method for Factor Testing
        
        Factor Return = coefficient from regressing returns on factor values
        """
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        results = []
        
        for date, group in merged.groupby("date"):
            if len(group) < 10:
                continue
            
            X = group["factor_value"].values.reshape(-1, 1)
            y = group["forward_return"].values
            
            # Add constant
            X_with_const = np.column_stack([np.ones(len(X)), X])
            
            try:
                # OLS regression
                coef = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                
                # Calculate residuals and statistics
                y_pred = X_with_const @ coef
                residuals = y - y_pred
                
                # Standard error
                n = len(y)
                k = 2  # intercept + slope
                mse = np.sum(residuals**2) / (n - k)
                var_coef = mse * np.linalg.inv(X_with_const.T @ X_with_const)
                se = np.sqrt(np.diag(var_coef))
                
                # t-statistics
                t_stats = coef / se
                
                results.append({
                    "date": date,
                    "factor_return": coef[1],
                    "t_value": t_stats[1],
                    "intercept": coef[0]
                })
                
            except Exception as e:
                continue
        
        if not results:
            return {}
        
        reg_df = pd.DataFrame(results)
        
        # Statistics
        factor_return_mean = reg_df["factor_return"].mean()
        factor_return_std = reg_df["factor_return"].std()
        factor_return_t_stat = factor_return_mean / (factor_return_std / np.sqrt(len(reg_df))) if factor_return_std > 0 else 0
        
        t_value_mean = reg_df["t_value"].abs().mean()
        t_value_significant_ratio = (reg_df["t_value"].abs() > 1.96).mean()
        
        return {
            "reg_df": reg_df,
            "factor_return_mean": factor_return_mean,
            "factor_return_std": factor_return_std,
            "factor_return_t_stat": factor_return_t_stat,
            "t_value_mean": t_value_mean,
            "t_value_significant_ratio": t_value_significant_ratio
        }
    
    def calculate_group_testing(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        n_groups: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Group Testing (Quintile/Decile Analysis)
        """
        n_groups = n_groups or self.n_groups
        
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Assign groups
        merged["group"] = merged.groupby("date")["factor_value"].transform(
            lambda x: pd.qcut(x, n_groups, labels=False, duplicates="drop") + 1
        )
        
        # Calculate group returns
        group_returns = merged.groupby(["date", "group"])["forward_return"].mean().unstack()
        
        if group_returns.empty:
            return {}
        
        # Group statistics
        group_stats = []
        for g in range(1, n_groups + 1):
            if g in group_returns.columns:
                col = group_returns[g].dropna()
                group_stats.append({
                    "group": g,
                    "mean_return": col.mean(),
                    "std_return": col.std(),
                    "sharpe": col.mean() / col.std() * np.sqrt(252) if col.std() > 0 else 0,
                    "hit_rate": (col > 0).mean()
                })
        
        group_stats_df = pd.DataFrame(group_stats)
        
        # Spread analysis (top - bottom)
        if len(group_stats_df) >= 2:
            spread = group_returns.iloc[:, -1] - group_returns.iloc[:, 0]
            spread_mean = spread.mean()
            spread_std = spread.std()
            spread_sharpe = spread_mean / spread_std * np.sqrt(252) if spread_std > 0 else 0
            spread_t_stat = spread_mean / (spread_std / np.sqrt(len(spread))) if spread_std > 0 else 0
            spread_p_value = stats.ttest_1samp(spread.dropna(), 0)[1]
        else:
            spread_mean = spread_std = spread_sharpe = spread_t_stat = spread_p_value = 0
        
        # Monotonicity
        monotonicity = self._calculate_monotonicity(group_stats_df)
        monotonicity_score = self._calculate_monotonicity_score(group_stats_df)
        
        return {
            "group_returns": group_returns,
            "group_stats": group_stats_df,
            "spread_mean": spread_mean,
            "spread_std": spread_std,
            "spread_sharpe": spread_sharpe,
            "spread_t_stat": spread_t_stat,
            "spread_p_value": spread_p_value,
            "monotonicity": monotonicity,
            "monotonicity_score": monotonicity_score
        }
    
    def _calculate_monotonicity(self, group_stats: pd.DataFrame) -> float:
        """Calculate monotonicity (proportion of correct orderings)"""
        returns = group_stats["mean_return"].values
        n = len(returns)
        
        if n < 2:
            return 0
        
        correct = 0
        total = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                total += 1
                if returns[i] < returns[j]:
                    correct += 1
        
        return correct / total if total > 0 else 0
    
    def _calculate_monotonicity_score(self, group_stats: pd.DataFrame) -> float:
        """Calculate monotonicity score using Spearman correlation"""
        if len(group_stats) < 2:
            return 0
        
        groups = group_stats["group"].values
        returns = group_stats["mean_return"].values
        
        corr, _ = stats.spearmanr(groups, returns)
        return corr
    
    def calculate_ic_decay(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        max_periods: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        IC Decay Analysis and Half-life Calculation
        """
        max_periods = max_periods or self.max_decay_periods
        
        # Get unique dates sorted
        dates = sorted(factor_df["date"].unique())
        
        decay_curve = []
        
        for lag in range(max_periods + 1):
            if lag >= len(dates) - 1:
                break
            
            # Calculate IC with lagged returns
            lagged_returns = returns_df.copy()
            lagged_returns["date"] = lagged_returns.groupby("symbol")["date"].transform(
                lambda x: x.shift(-lag)
            )
            
            merged = pd.merge(
                factor_df,
                lagged_returns[["symbol", "date", "forward_return"]].dropna(),
                on=["symbol", "date"],
                how="inner"
            )
            
            if merged.empty:
                continue
            
            # Calculate IC
            ic_list = []
            for date, group in merged.groupby("date"):
                if len(group) >= 10:
                    ic, _ = stats.spearmanr(group["factor_value"], group["forward_return"])
                    ic_list.append(ic)
            
            mean_ic = np.mean(ic_list) if ic_list else 0
            decay_curve.append({"lag": lag, "ic": mean_ic})
        
        if not decay_curve:
            return {}
        
        decay_df = pd.DataFrame(decay_curve)
        
        # Calculate half-life
        half_life = self._calculate_half_life(decay_df)
        
        return {
            "decay_df": decay_df,
            "decay_curve": decay_df["ic"].tolist(),
            "half_life": half_life
        }
    
    def _calculate_half_life(self, decay_df: pd.DataFrame) -> float:
        """Calculate IC half-life"""
        if len(decay_df) < 2:
            return 0
        
        ic_values = decay_df["ic"].values
        initial_ic = abs(ic_values[0])
        
        if initial_ic == 0:
            return 0
        
        half_ic = initial_ic / 2
        
        # Find first point where IC drops below half
        for i, ic in enumerate(ic_values):
            if abs(ic) <= half_ic:
                return float(i)
        
        # If never drops below half, return max periods
        return float(len(ic_values))
    
    def calculate_turnover_analysis(
        self,
        factor_df: pd.DataFrame,
        top_pct: float = 0.2
    ) -> Dict[str, Any]:
        """
        Turnover and Autocorrelation Analysis
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
        
        if not turnovers:
            return {}
        
        turnover_mean = np.mean(turnovers)
        turnover_std = np.std(turnovers)
        
        # Calculate autocorrelation of factor values
        factor_pivot = factor_df.pivot(index="date", columns="symbol", values="factor_value")
        autocorr_list = []
        
        for col in factor_pivot.columns:
            series = factor_pivot[col].dropna()
            if len(series) > 1:
                autocorr_list.append(series.autocorr(lag=1))
        
        autocorrelation = np.mean([x for x in autocorr_list if not np.isnan(x)]) if autocorr_list else 0
        
        return {
            "turnover_mean": turnover_mean,
            "turnover_std": turnover_std,
            "autocorrelation": autocorrelation
        }
    
    def calculate_statistical_tests(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Statistical Tests for Factor Effectiveness
        """
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Split by median
        median_factor = merged.groupby("date")["factor_value"].transform("median")
        high_group = merged[merged["factor_value"] >= median_factor]["forward_return"]
        low_group = merged[merged["factor_value"] < median_factor]["forward_return"]
        
        results = {}
        
        # Wilcoxon rank-sum test
        try:
            stat, pvalue = stats.ranksums(high_group.dropna(), low_group.dropna())
            results["wilcoxon_stat"] = stat
            results["wilcoxon_pvalue"] = pvalue
        except:
            results["wilcoxon_stat"] = 0
            results["wilcoxon_pvalue"] = 1
        
        # KS test
        try:
            stat, pvalue = stats.ks_2samp(high_group.dropna(), low_group.dropna())
            results["ks_stat"] = stat
            results["ks_pvalue"] = pvalue
        except:
            results["ks_stat"] = 0
            results["ks_pvalue"] = 1
        
        return results
    
    def calculate_risk_metrics(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Risk-Adjusted Metrics for Factor
        """
        # Calculate group returns for spread
        group_result = self.calculate_group_testing(factor_df, returns_df)
        
        if not group_result or "group_returns" not in group_result:
            return {}
        
        group_returns = group_result["group_returns"]
        
        if group_returns.empty or len(group_returns.columns) < 2:
            return {}
        
        # Spread returns
        spread = group_returns.iloc[:, -1] - group_returns.iloc[:, 0]
        
        # Sortino ratio (downside deviation)
        downside_returns = spread[spread < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino = spread.mean() * 252 / downside_std if downside_std > 0 else 0
        
        # Max drawdown
        cumulative = (1 + spread).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Calmar ratio
        calmar = spread.mean() * 252 / max_drawdown if max_drawdown > 0 else 0
        
        return {
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "max_drawdown": max_drawdown
        }
    
    def test_factor_comprehensive(
        self,
        factor: Any,  # FactorBase
        df: pd.DataFrame,
        forward_periods: List[int] = [1, 5, 10, 20],
        preprocess: bool = True,
        neutralize: bool = False
    ) -> ComprehensiveFactorStats:
        """
        Comprehensive Factor Testing
        
        Args:
            factor: Factor instance
            df: DataFrame with OHLCV data
            forward_periods: Forward return periods to test
            preprocess: Apply preprocessing (winsorize, standardize)
            neutralize: Apply industry/market cap neutralization
        
        Returns:
            ComprehensiveFactorStats object
        """
        logger.info(f"Comprehensive testing for factor: {factor.name}")
        
        # Calculate factor values
        factor_df = factor.calculate(df)
        
        if factor_df.empty:
            return ComprehensiveFactorStats(name=factor.name, category="unknown")
        
        # Preprocessing
        if preprocess:
            factor_df = self.preprocessor.winsorize(factor_df)
            factor_df = self.preprocessor.standardize(factor_df)
        
        # Calculate forward returns for main period
        df_copy = df.copy()
        main_period = forward_periods[0] if forward_periods else 5
        df_copy["forward_return"] = df_copy.groupby("symbol")["close"].transform(
            lambda x: x.shift(-main_period) / x - 1
        )
        
        # Run all tests
        ic_result = self.calculate_ic_analysis(factor_df, df_copy)
        reg_result = self.calculate_regression_analysis(factor_df, df_copy)
        group_result = self.calculate_group_testing(factor_df, df_copy)
        decay_result = self.calculate_ic_decay(factor_df, df_copy)
        turnover_result = self.calculate_turnover_analysis(factor_df)
        stat_result = self.calculate_statistical_tests(factor_df, df_copy)
        risk_result = self.calculate_risk_metrics(factor_df, df_copy)
        
        # Determine effectiveness
        is_effective, score, reasons = self._determine_effectiveness(
            ic_result, reg_result, group_result, turnover_result
        )
        
        return ComprehensiveFactorStats(
            name=factor.name,
            category=factor.get_metadata().get("category", "unknown"),
            
            # IC Analysis
            ic_mean=ic_result.get("ic_mean", 0),
            ic_std=ic_result.get("ic_std", 0),
            icir=ic_result.get("icir", 0),
            ic_t_stat=ic_result.get("ic_t_stat", 0),
            ic_positive_ratio=ic_result.get("ic_positive_ratio", 0),
            ic_significant_ratio=ic_result.get("ic_significant_ratio", 0),
            ic_abs_mean=ic_result.get("ic_abs_mean", 0),
            
            # Regression
            factor_return_mean=reg_result.get("factor_return_mean", 0),
            factor_return_t_stat=reg_result.get("factor_return_t_stat", 0),
            t_value_mean=reg_result.get("t_value_mean", 0),
            t_value_significant_ratio=reg_result.get("t_value_significant_ratio", 0),
            
            # Group Testing
            group_returns=group_result.get("group_stats", pd.DataFrame())["mean_return"].tolist() if not group_result.get("group_stats", pd.DataFrame()).empty else [],
            group_sharpe=group_result.get("group_stats", pd.DataFrame())["sharpe"].tolist() if not group_result.get("group_stats", pd.DataFrame()).empty else [],
            spread_return=group_result.get("spread_mean", 0),
            spread_sharpe=group_result.get("spread_sharpe", 0),
            spread_t_stat=group_result.get("spread_t_stat", 0),
            spread_p_value=group_result.get("spread_p_value", 1),
            monotonicity=group_result.get("monotonicity", 0),
            monotonicity_score=group_result.get("monotonicity_score", 0),
            
            # IC Decay
            ic_half_life=decay_result.get("half_life", 0),
            ic_decay_curve=decay_result.get("decay_curve", []),
            
            # Turnover
            turnover_mean=turnover_result.get("turnover_mean", 0),
            turnover_std=turnover_result.get("turnover_std", 0),
            autocorrelation=turnover_result.get("autocorrelation", 0),
            
            # Statistical Tests
            wilcoxon_stat=stat_result.get("wilcoxon_stat", 0),
            wilcoxon_pvalue=stat_result.get("wilcoxon_pvalue", 1),
            ks_stat=stat_result.get("ks_stat", 0),
            ks_pvalue=stat_result.get("ks_pvalue", 1),
            
            # Risk
            sortino_ratio=risk_result.get("sortino_ratio", 0),
            calmar_ratio=risk_result.get("calmar_ratio", 0),
            max_drawdown=risk_result.get("max_drawdown", 0),
            
            # Effectiveness
            is_effective=is_effective,
            effectiveness_score=score,
            failure_reasons=reasons
        )
    
    def _determine_effectiveness(
        self,
        ic_result: Dict,
        reg_result: Dict,
        group_result: Dict,
        turnover_result: Dict
    ) -> Tuple[bool, float, List[str]]:
        """
        Determine if factor is effective based on multiple criteria
        """
        reasons = []
        score = 0
        max_score = 10
        
        # Criteria 1: IC mean (weight: 2)
        ic_mean = abs(ic_result.get("ic_mean", 0))
        if ic_mean >= 0.03:
            score += 2
        elif ic_mean >= 0.02:
            score += 1
        else:
            reasons.append(f"IC mean too low ({ic_mean:.4f})")
        
        # Criteria 2: ICIR (weight: 2)
        icir = abs(ic_result.get("icir", 0))
        if icir >= 0.5:
            score += 2
        elif icir >= 0.3:
            score += 1
        else:
            reasons.append(f"ICIR too low ({icir:.4f})")
        
        # Criteria 3: IC t-stat (weight: 1)
        ic_t = abs(ic_result.get("ic_t_stat", 0))
        if ic_t >= 2:
            score += 1
        else:
            reasons.append(f"IC t-stat not significant ({ic_t:.2f})")
        
        # Criteria 4: Regression t-value ratio (weight: 1)
        t_ratio = reg_result.get("t_value_significant_ratio", 0)
        if t_ratio >= 0.5:
            score += 1
        else:
            reasons.append(f"Regression significance ratio low ({t_ratio:.2%})")
        
        # Criteria 5: Monotonicity (weight: 2)
        mono = group_result.get("monotonicity_score", 0)
        if mono >= 0.7:
            score += 2
        elif mono >= 0.5:
            score += 1
        else:
            reasons.append(f"Poor monotonicity ({mono:.2f})")
        
        # Criteria 6: Spread significance (weight: 1)
        spread_t = abs(group_result.get("spread_t_stat", 0))
        if spread_t >= 2:
            score += 1
        else:
            reasons.append(f"Spread not significant (t={spread_t:.2f})")
        
        # Criteria 7: Turnover (weight: 1)
        turnover = turnover_result.get("turnover_mean", 1)
        if turnover <= 0.3:
            score += 1
        elif turnover > 0.5:
            reasons.append(f"High turnover ({turnover:.2%})")
        
        normalized_score = score / max_score
        is_effective = normalized_score >= 0.5 and len(reasons) <= 3
        
        return is_effective, normalized_score, reasons


class FactorCorrelationAnalyzer:
    """
    Factor Correlation and Orthogonalization Analysis
    """
    
    @staticmethod
    def calculate_correlation_matrix(
        factor_df: pd.DataFrame,
        method: str = "spearman"
    ) -> pd.DataFrame:
        """
        Calculate cross-sectional correlation between factors
        """
        factor_cols = [col for col in factor_df.columns 
                       if col not in ["symbol", "date"]]
        
        correlations = []
        
        for col1 in factor_cols:
            row = []
            for col2 in factor_cols:
                # Calculate cross-sectional correlation
                corr = factor_df.groupby("date").apply(
                    lambda g: g[col1].corr(g[col2], method=method)
                ).mean()
                row.append(corr)
            correlations.append(row)
        
        return pd.DataFrame(
            correlations,
            index=factor_cols,
            columns=factor_cols
        )
    
    @staticmethod
    def orthogonalize_factors(
        factor_df: pd.DataFrame,
        base_factor: str,
        method: str = "residual"
    ) -> pd.DataFrame:
        """
        Orthogonalize factors against a base factor
        
        Methods:
        - residual: Use regression residuals
        - gram_schmidt: Gram-Schmidt orthogonalization
        """
        factor_cols = [col for col in factor_df.columns 
                       if col not in ["symbol", "date"]]
        
        result = factor_df.copy()
        
        for col in factor_cols:
            if col == base_factor:
                continue
            
            if method == "residual":
                # Regress on base factor
                def orthogonalize_group(g):
                    if len(g) < 5:
                        return g[col]
                    
                    X = g[base_factor].values.reshape(-1, 1)
                    y = g[col].values
                    
                    try:
                        coef = np.linalg.lstsq(X, y, rcond=None)[0]
                        residual = y - X @ coef
                        return pd.Series(residual, index=g.index)
                    except:
                        return g[col]
                
                result[col] = factor_df.groupby("date").apply(orthogonalize_group).reset_index(level=0, drop=True)
        
        return result
    
    @staticmethod
    def calculate_vif(
        factor_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate Variance Inflation Factor for multicollinearity detection
        """
        from sklearn.linear_model import LinearRegression
        
        factor_cols = [col for col in factor_df.columns 
                       if col not in ["symbol", "date"]]
        
        vif_dict = {}
        
        for col in factor_cols:
            other_cols = [c for c in factor_cols if c != col]
            
            # Get data (drop NaN)
            data = factor_df[[col] + other_cols].dropna()
            
            if len(data) < 10:
                vif_dict[col] = np.inf
                continue
            
            X = data[other_cols].values
            y = data[col].values
            
            try:
                model = LinearRegression()
                model.fit(X, y)
                r2 = model.score(X, y)
                
                if r2 < 1:
                    vif = 1 / (1 - r2)
                else:
                    vif = np.inf
                
                vif_dict[col] = vif
            except:
                vif_dict[col] = np.inf
        
        return vif_dict
