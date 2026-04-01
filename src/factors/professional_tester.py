"""
Professional Factor Effectiveness Testing Module
百亿量化级因子有效性检测框架

This module implements ALL professional factor validation methods used by
top quantitative hedge funds worldwide, based on comprehensive research of
Alphalens, WorldQuant, and other professional frameworks.

Categories:
1. IC Analysis (Information Coefficient)
2. Regression Method (Factor Return, t-statistics)
3. Group Testing (Quantile Analysis)
4. Market Cap Stratification Analysis
5. Industry Stratification Analysis
6. IC Decay & Half-life Analysis
7. Turnover Analysis
8. Predictive Power Analysis (Hit Rate, F1, ROC, AUC)
9. Statistical Tests
10. Factor Stability Analysis
11. Risk-Adjusted Metrics
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple, Union
from loguru import logger
from scipy import stats
from scipy.optimize import minimize
from dataclasses import dataclass, field
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Machine Learning imports
from sklearn.metrics import (
    roc_curve, auc, roc_auc_score,
    precision_score, recall_score, f1_score, accuracy_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit


@dataclass
class MarketCapStratificationStats:
    """Market Cap Stratification Analysis Results"""
    large_cap_ic: float = 0.0
    large_cap_icir: float = 0.0
    large_cap_return: float = 0.0
    large_cap_sharpe: float = 0.0
    
    mid_cap_ic: float = 0.0
    mid_cap_icir: float = 0.0
    mid_cap_return: float = 0.0
    mid_cap_sharpe: float = 0.0
    
    small_cap_ic: float = 0.0
    small_cap_icir: float = 0.0
    small_cap_return: float = 0.0
    small_cap_sharpe: float = 0.0
    
    size_effect_ratio: float = 0.0  # Small cap vs Large cap effectiveness


@dataclass
class IndustryStratificationStats:
    """Industry Stratification Analysis Results"""
    industry_ic_dict: Dict[str, float] = field(default_factory=dict)
    industry_icir_dict: Dict[str, float] = field(default_factory=dict)
    industry_return_dict: Dict[str, float] = field(default_factory=dict)
    industry_consistency: float = 0.0  # Proportion of industries with positive IC
    industry_dispersion: float = 0.0  # IC dispersion across industries


@dataclass
class QuantileAnalysisStats:
    """Detailed Quantile Analysis Results"""
    quantile_returns: Dict[int, float] = field(default_factory=dict)
    quantile_sharpe: Dict[int, float] = field(default_factory=dict)
    quantile_volatility: Dict[int, float] = field(default_factory=dict)
    quantile_max_drawdown: Dict[int, float] = field(default_factory=dict)
    quantile_hit_rate: Dict[int, float] = field(default_factory=dict)
    quantile_count: Dict[int, int] = field(default_factory=dict)
    
    # Spread analysis
    spread_return: float = 0.0
    spread_sharpe: float = 0.0
    spread_t_stat: float = 0.0
    spread_p_value: float = 0.0
    
    # Monotonicity
    monotonicity_score: float = 0.0
    monotonicity_p_value: float = 0.0


@dataclass
class PredictivePowerStats:
    """Machine Learning based predictive power analysis"""
    # Classification metrics
    hit_rate: float = 0.0  # Overall accuracy
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # ROC/AUC
    auc_score: float = 0.0
    roc_curve_data: Optional[np.ndarray] = None
    
    # Direction prediction
    up_precision: float = 0.0  # Precision for predicting up moves
    down_precision: float = 0.0  # Precision for predicting down moves
    
    # Confusion matrix
    true_positive: int = 0
    true_negative: int = 0
    false_positive: int = 0
    false_negative: int = 0
    
    # Information coefficient
    spearman_ic: float = 0.0
    pearson_ic: float = 0.0


@dataclass
class FactorStabilityStats:
    """Factor Stability Analysis Results"""
    # Rolling IC statistics
    rolling_ic_mean: float = 0.0
    rolling_ic_std: float = 0.0
    rolling_ic_trend: float = 0.0  # Slope of IC over time
    rolling_ic_autocorr: float = 0.0
    
    # Regime sensitivity
    bull_market_ic: float = 0.0
    bear_market_ic: float = 0.0
    regime_sensitivity: float = 0.0
    
    # Out-of-sample performance
    in_sample_ic: float = 0.0
    out_sample_ic: float = 0.0
    oos_degradation: float = 0.0  # How much IC degrades out-of-sample
    
    # Stability metrics
    ic_cv: float = 0.0  # Coefficient of variation
    stability_score: float = 0.0


@dataclass
class AdvancedStatisticalTests:
    """Advanced Statistical Tests Results"""
    # Normality tests
    jarque_bera_stat: float = 0.0
    jarque_bera_pvalue: float = 0.0
    shapiro_stat: float = 0.0
    shapiro_pvalue: float = 0.0
    
    # Significance tests
    t_test_stat: float = 0.0
    t_test_pvalue: float = 0.0
    wilcoxon_stat: float = 0.0
    wilcoxon_pvalue: float = 0.0
    
    # Multiple comparison correction
    bonferroni_adjusted_pvalue: float = 0.0
    
    # Factor decay analysis
    decay_rate: float = 0.0
    autocorr_lag1: float = 0.0
    autocorr_lag5: float = 0.0
    autocorr_lag10: float = 0.0


@dataclass
class ProfessionalFactorStats:
    """
    Complete factor statistics for professional validation
    百亿量化级因子评估指标全集
    """
    # Basic Info
    name: str
    category: str
    
    # ==================== 1. IC Analysis ====================
    ic_mean: float = 0.0
    ic_std: float = 0.0
    icir: float = 0.0
    ic_t_stat: float = 0.0
    ic_positive_ratio: float = 0.0
    ic_significant_ratio: float = 0.0
    ic_abs_mean: float = 0.0
    ic_skewness: float = 0.0
    ic_kurtosis: float = 0.0
    
    # ==================== 2. Regression Method ====================
    factor_return_mean: float = 0.0
    factor_return_std: float = 0.0
    factor_return_t_stat: float = 0.0
    factor_return_p_value: float = 0.0
    t_value_mean: float = 0.0
    t_value_significant_ratio: float = 0.0
    
    # ==================== 3. Group Testing ====================
    quantile_stats: Optional[QuantileAnalysisStats] = None
    
    # ==================== 4. Market Cap Stratification ====================
    market_cap_stats: Optional[MarketCapStratificationStats] = None
    
    # ==================== 5. Industry Stratification ====================
    industry_stats: Optional[IndustryStratificationStats] = None
    
    # ==================== 6. IC Decay ====================
    ic_half_life: float = 0.0
    ic_decay_curve: List[float] = field(default_factory=list)
    ic_decay_r_squared: float = 0.0
    
    # ==================== 7. Turnover ====================
    turnover_mean: float = 0.0
    turnover_std: float = 0.0
    autocorrelation: float = 0.0
    factor_rank_autocorr: float = 0.0
    
    # ==================== 8. Predictive Power ====================
    predictive_stats: Optional[PredictivePowerStats] = None
    
    # ==================== 9. Statistical Tests ====================
    stat_tests: Optional[AdvancedStatisticalTests] = None
    
    # ==================== 10. Stability Analysis ====================
    stability_stats: Optional[FactorStabilityStats] = None
    
    # ==================== 11. Risk-Adjusted ====================
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    var_95: float = 0.0
    cvar_95: float = 0.0
    
    # ==================== Effectiveness Summary ====================
    is_effective: bool = False
    effectiveness_score: float = 0.0
    effectiveness_grade: str = "F"  # A+, A, B, C, D, F
    failure_reasons: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


class ProfessionalFactorTester:
    """
    Professional Factor Testing Framework
    百亿量化级因子测试框架
    
    Implements ALL professional factor validation methods:
    
    1. IC Analysis
       - IC mean, std, ICIR
       - IC t-statistics, significance
       - IC distribution (skewness, kurtosis)
    
    2. Regression Method
       - Factor return series
       - t-value series, significance
    
    3. Quantile Analysis (Detailed)
       - Per-quantile statistics
       - Monotonicity testing
       - Spread analysis
    
    4. Market Cap Stratification
       - Large/Mid/Small cap effectiveness
       - Size effect analysis
    
    5. Industry Stratification
       - Industry-specific IC
       - Cross-industry consistency
    
    6. IC Decay Analysis
       - Half-life calculation
       - Decay curve fitting
    
    7. Turnover Analysis
       - Group turnover
       - Factor rank autocorrelation
    
    8. Predictive Power (ML-based)
       - Hit Rate, Precision, Recall, F1
       - ROC/AUC analysis
    
    9. Statistical Tests
       - Normality tests
       - Significance tests
       - Multiple comparison correction
    
    10. Stability Analysis
        - Rolling IC
        - Regime sensitivity
        - Out-of-sample testing
    
    11. Risk-Adjusted Metrics
        - Sortino, Calmar
        - VaR, CVaR
    """
    
    def __init__(
        self,
        ic_threshold: float = 0.02,
        icir_threshold: float = 0.5,
        n_quantiles: int = 5,
        max_decay_periods: int = 20,
        significance_level: float = 0.05,
        market_cap_percentiles: Tuple[float, float] = (0.3, 0.7),  # 30%, 70%
        rolling_window: int = 252,  # 1 year
        train_test_split: float = 0.7
    ):
        self.ic_threshold = ic_threshold
        self.icir_threshold = icir_threshold
        self.n_quantiles = n_quantiles
        self.max_decay_periods = max_decay_periods
        self.significance_level = significance_level
        self.market_cap_percentiles = market_cap_percentiles
        self.rolling_window = rolling_window
        self.train_test_split = train_test_split
        
        self.preprocessor = FactorPreprocessor()
    
    # ==================== 1. IC Analysis ====================
    
    def calculate_ic_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        method: str = "spearman"
    ) -> Dict[str, Any]:
        """
        Comprehensive IC Analysis with distribution statistics
        """
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        ic_list = []
        
        for date, group in merged.groupby("date"):
            if len(group) < 10:
                continue
            
            valid_data = group.dropna(subset=["factor_value", "forward_return"])
            if len(valid_data) < 10:
                continue
            
            if method == "spearman":
                ic, pvalue = stats.spearmanr(
                    valid_data["factor_value"],
                    valid_data["forward_return"]
                )
            else:
                ic, pvalue = stats.pearsonr(
                    valid_data["factor_value"],
                    valid_data["forward_return"]
                )
            
            ic_list.append({
                "date": date,
                "ic": ic,
                "pvalue": pvalue,
                "n_stocks": len(valid_data)
            })
        
        ic_df = pd.DataFrame(ic_list)
        
        if ic_df.empty:
            return {}
        
        ic_series = ic_df["ic"].dropna()
        
        # Basic statistics
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
        
        # Distribution statistics
        ic_skewness = stats.skew(ic_series)
        ic_kurtosis = stats.kurtosis(ic_series)
        
        return {
            "ic_df": ic_df,
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "icir": icir,
            "ic_t_stat": ic_t_stat,
            "ic_positive_ratio": ic_positive_ratio,
            "ic_significant_ratio": ic_significant_ratio,
            "ic_abs_mean": ic_abs_mean,
            "ic_skewness": ic_skewness,
            "ic_kurtosis": ic_kurtosis,
            "n_periods": n
        }
    
    # ==================== 2. Regression Method ====================
    
    def calculate_regression_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Regression Method for Factor Testing
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
            
            valid = group.dropna(subset=["factor_value", "forward_return"])
            if len(valid) < 10:
                continue
            
            X = valid["factor_value"].values.reshape(-1, 1)
            y = valid["forward_return"].values
            
            X_with_const = np.column_stack([np.ones(len(X)), X])
            
            try:
                coef = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                y_pred = X_with_const @ coef
                residuals = y - y_pred
                
                n = len(y)
                k = 2
                mse = np.sum(residuals**2) / (n - k)
                var_coef = mse * np.linalg.inv(X_with_const.T @ X_with_const)
                se = np.sqrt(np.diag(var_coef))
                t_stats = coef / se
                p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), n - k))
                
                r_squared = 1 - np.sum(residuals**2) / np.sum((y - y.mean())**2)
                
                results.append({
                    "date": date,
                    "factor_return": coef[1],
                    "t_value": t_stats[1],
                    "p_value": p_values[1],
                    "r_squared": r_squared,
                    "intercept": coef[0]
                })
                
            except Exception as e:
                continue
        
        if not results:
            return {}
        
        reg_df = pd.DataFrame(results)
        
        factor_return_mean = reg_df["factor_return"].mean()
        factor_return_std = reg_df["factor_return"].std()
        factor_return_t_stat = factor_return_mean / (factor_return_std / np.sqrt(len(reg_df))) if factor_return_std > 0 else 0
        factor_return_p_value = 2 * (1 - stats.norm.cdf(abs(factor_return_t_stat)))
        
        t_value_mean = reg_df["t_value"].abs().mean()
        t_value_significant_ratio = (reg_df["p_value"] < self.significance_level).mean()
        
        return {
            "reg_df": reg_df,
            "factor_return_mean": factor_return_mean,
            "factor_return_std": factor_return_std,
            "factor_return_t_stat": factor_return_t_stat,
            "factor_return_p_value": factor_return_p_value,
            "t_value_mean": t_value_mean,
            "t_value_significant_ratio": t_value_significant_ratio,
            "r_squared_mean": reg_df["r_squared"].mean()
        }
    
    # ==================== 3. Quantile Analysis (Detailed) ====================
    
    def calculate_quantile_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        n_quantiles: Optional[int] = None
    ) -> QuantileAnalysisStats:
        """
        Detailed Quantile Analysis with comprehensive statistics
        """
        n_quantiles = n_quantiles or self.n_quantiles
        
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        # Assign quantiles
        merged["quantile"] = merged.groupby("date")["factor_value"].transform(
            lambda x: pd.qcut(x, n_quantiles, labels=False, duplicates="drop") + 1
        )
        
        # Calculate quantile returns time series
        quantile_returns_ts = merged.groupby(["date", "quantile"])["forward_return"].mean().unstack()
        
        stats_obj = QuantileAnalysisStats()
        
        # Per-quantile statistics
        for q in range(1, n_quantiles + 1):
            if q in quantile_returns_ts.columns:
                returns = quantile_returns_ts[q].dropna()
                
                stats_obj.quantile_returns[q] = returns.mean() * 252  # Annualized
                stats_obj.quantile_volatility[q] = returns.std() * np.sqrt(252)
                stats_obj.quantile_sharpe[q] = (
                    stats_obj.quantile_returns[q] / stats_obj.quantile_volatility[q]
                    if stats_obj.quantile_volatility[q] > 0 else 0
                )
                stats_obj.quantile_hit_rate[q] = (returns > 0).mean()
                stats_obj.quantile_count[q] = len(returns)
                
                # Max drawdown
                cum_returns = (1 + returns).cumprod()
                running_max = cum_returns.cummax()
                drawdown = (cum_returns - running_max) / running_max
                stats_obj.quantile_max_drawdown[q] = abs(drawdown.min())
        
        # Spread analysis (top - bottom)
        if n_quantiles in quantile_returns_ts.columns and 1 in quantile_returns_ts.columns:
            spread = quantile_returns_ts[n_quantiles] - quantile_returns_ts[1]
            spread = spread.dropna()
            
            stats_obj.spread_return = spread.mean() * 252
            spread_std = spread.std() * np.sqrt(252)
            stats_obj.spread_sharpe = stats_obj.spread_return / spread_std if spread_std > 0 else 0
            stats_obj.spread_t_stat = spread.mean() / (spread.std() / np.sqrt(len(spread))) if spread.std() > 0 else 0
            stats_obj.spread_p_value = stats.ttest_1samp(spread, 0)[1]
        
        # Monotonicity test
        stats_obj.monotonicity_score = self._calculate_monotonicity_score(stats_obj.quantile_returns)
        stats_obj.monotonicity_p_value = self._test_monotonicity(quantile_returns_ts)
        
        return stats_obj
    
    def _calculate_monotonicity_score(self, quantile_returns: Dict[int, float]) -> float:
        """Calculate monotonicity using Spearman correlation"""
        if len(quantile_returns) < 2:
            return 0
        
        quantiles = list(quantile_returns.keys())
        returns = list(quantile_returns.values())
        
        corr, _ = stats.spearmanr(quantiles, returns)
        return corr
    
    def _test_monotonicity(self, quantile_returns_ts: pd.DataFrame) -> float:
        """Test monotonicity using Cochran-Armitage trend test"""
        if quantile_returns_ts.empty or len(quantile_returns_ts.columns) < 2:
            return 1.0
        
        mean_returns = quantile_returns_ts.mean()
        quantiles = np.arange(len(mean_returns))
        
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(quantiles, mean_returns)
        
        return p_value
    
    # ==================== 4. Market Cap Stratification ====================
    
    def calculate_market_cap_stratification(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        market_cap_df: pd.DataFrame
    ) -> MarketCapStratificationStats:
        """
        Analyze factor effectiveness across different market cap groups
        
        Args:
            factor_df: DataFrame with columns [symbol, date, factor_value]
            returns_df: DataFrame with columns [symbol, date, forward_return]
            market_cap_df: DataFrame with columns [symbol, date, market_cap]
        """
        # Merge all data
        merged = factor_df.merge(
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        ).merge(
            market_cap_df[["symbol", "date", "market_cap"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        stats_obj = MarketCapStratificationStats()
        
        # For each date, classify stocks into large/mid/small cap
        merged["market_cap_group"] = merged.groupby("date")["market_cap"].transform(
            lambda x: pd.qcut(x, [0, 0.3, 0.7, 1.0], labels=["small", "mid", "large"], duplicates="drop")
        )
        
        # Calculate IC for each group
        for group, group_name in [("large", "large_cap"), ("mid", "mid_cap"), ("small", "small_cap")]:
            group_data = merged[merged["market_cap_group"] == group]
            
            if len(group_data) < 100:
                continue
            
            # Calculate IC
            ic_list = []
            returns_list = []
            
            for date, daily_data in group_data.groupby("date"):
                if len(daily_data) < 10:
                    continue
                
                valid = daily_data.dropna(subset=["factor_value", "forward_return"])
                if len(valid) < 10:
                    continue
                
                ic, _ = stats.spearmanr(valid["factor_value"], valid["forward_return"])
                ic_list.append(ic)
                returns_list.append(valid["forward_return"].mean())
            
            if ic_list:
                ic_mean = np.mean(ic_list)
                ic_std = np.std(ic_list)
                icir = ic_mean / ic_std if ic_std > 0 else 0
                ann_return = np.mean(returns_list) * 252
                ann_vol = np.std(returns_list) * np.sqrt(252)
                sharpe = ann_return / ann_vol if ann_vol > 0 else 0
                
                setattr(stats_obj, f"{group_name}_ic", ic_mean)
                setattr(stats_obj, f"{group_name}_icir", icir)
                setattr(stats_obj, f"{group_name}_return", ann_return)
                setattr(stats_obj, f"{group_name}_sharpe", sharpe)
        
        # Calculate size effect ratio
        if stats_obj.small_cap_ic != 0 and stats_obj.large_cap_ic != 0:
            stats_obj.size_effect_ratio = stats_obj.small_cap_ic / stats_obj.large_cap_ic
        
        return stats_obj
    
    # ==================== 5. Industry Stratification ====================
    
    def calculate_industry_stratification(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        industry_mapping: Dict[str, str]
    ) -> IndustryStratificationStats:
        """
        Analyze factor effectiveness across industries
        
        Args:
            factor_df: DataFrame with columns [symbol, date, factor_value]
            returns_df: DataFrame with columns [symbol, date, forward_return]
            industry_mapping: Dict mapping symbol to industry
        """
        merged = factor_df.merge(
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        merged["industry"] = merged["symbol"].map(industry_mapping)
        
        stats_obj = IndustryStratificationStats()
        
        # Calculate IC for each industry
        for industry, industry_data in merged.groupby("industry"):
            if len(industry_data) < 100:
                continue
            
            ic_list = []
            returns_list = []
            
            for date, daily_data in industry_data.groupby("date"):
                if len(daily_data) < 5:
                    continue
                
                valid = daily_data.dropna(subset=["factor_value", "forward_return"])
                if len(valid) < 5:
                    continue
                
                ic, _ = stats.spearmanr(valid["factor_value"], valid["forward_return"])
                ic_list.append(ic)
                returns_list.append(valid["forward_return"].mean())
            
            if ic_list:
                ic_mean = np.mean(ic_list)
                ic_std = np.std(ic_list)
                icir = ic_mean / ic_std if ic_std > 0 else 0
                ann_return = np.mean(returns_list) * 252
                
                stats_obj.industry_ic_dict[industry] = ic_mean
                stats_obj.industry_icir_dict[industry] = icir
                stats_obj.industry_return_dict[industry] = ann_return
        
        # Calculate consistency and dispersion
        ics = list(stats_obj.industry_ic_dict.values())
        if ics:
            stats_obj.industry_consistency = sum(1 for ic in ics if ic > 0) / len(ics)
            stats_obj.industry_dispersion = np.std(ics)
        
        return stats_obj
    
    # ==================== 6. IC Decay Analysis ====================
    
    def calculate_ic_decay(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        max_periods: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        IC Decay Analysis with exponential decay fitting
        """
        max_periods = max_periods or self.max_decay_periods
        
        dates = sorted(factor_df["date"].unique())
        decay_curve = []
        
        for lag in range(max_periods + 1):
            if lag >= len(dates) - 1:
                break
            
            # Create lagged returns
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
                valid = group.dropna(subset=["factor_value", "forward_return"])
                if len(valid) >= 10:
                    ic, _ = stats.spearmanr(valid["factor_value"], valid["forward_return"])
                    ic_list.append(ic)
            
            mean_ic = np.mean(ic_list) if ic_list else 0
            decay_curve.append({"lag": lag, "ic": mean_ic})
        
        if not decay_curve:
            return {}
        
        decay_df = pd.DataFrame(decay_curve)
        
        # Calculate half-life
        half_life = self._calculate_half_life(decay_df)
        
        # Fit exponential decay
        r_squared = self._fit_decay_curve(decay_df)
        
        return {
            "decay_df": decay_df,
            "decay_curve": decay_df["ic"].tolist(),
            "half_life": half_life,
            "r_squared": r_squared
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
        
        for i, ic in enumerate(ic_values):
            if abs(ic) <= half_ic:
                return float(i)
        
        return float(len(ic_values))
    
    def _fit_decay_curve(self, decay_df: pd.DataFrame) -> float:
        """Fit exponential decay curve and return R-squared"""
        if len(decay_df) < 3:
            return 0
        
        lags = decay_df["lag"].values
        ics = np.abs(decay_df["ic"].values)
        
        try:
            # Fit exponential decay: IC = a * exp(-b * lag)
            def exp_decay(x, a, b):
                return a * np.exp(-b * x)
            
            from scipy.optimize import curve_fit
            popt, _ = curve_fit(exp_decay, lags, ics, p0=[ics[0], 0.1], maxfev=1000)
            
            # Calculate R-squared
            y_pred = exp_decay(lags, *popt)
            ss_res = np.sum((ics - y_pred) ** 2)
            ss_tot = np.sum((ics - np.mean(ics)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return r_squared
        except:
            return 0
    
    # ==================== 7. Turnover Analysis ====================
    
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
        
        # Factor rank autocorrelation
        factor_pivot = factor_df.pivot(index="date", columns="symbol", values="factor_value")
        
        # Calculate factor rank
        factor_rank = factor_pivot.rank(axis=1)
        
        # Autocorrelation of ranks
        rank_autocorr_list = []
        for col in factor_rank.columns:
            series = factor_rank[col].dropna()
            if len(series) > 1:
                autocorr = series.autocorr(lag=1)
                if not np.isnan(autocorr):
                    rank_autocorr_list.append(autocorr)
        
        factor_rank_autocorr = np.mean(rank_autocorr_list) if rank_autocorr_list else 0
        
        # Simple autocorrelation
        autocorr_list = []
        for col in factor_pivot.columns:
            series = factor_pivot[col].dropna()
            if len(series) > 1:
                autocorr = series.autocorr(lag=1)
                if not np.isnan(autocorr):
                    autocorr_list.append(autocorr)
        
        autocorrelation = np.mean(autocorr_list) if autocorr_list else 0
        
        return {
            "turnover_mean": turnover_mean,
            "turnover_std": turnover_std,
            "autocorrelation": autocorrelation,
            "factor_rank_autocorr": factor_rank_autocorr
        }
    
    # ==================== 8. Predictive Power Analysis ====================
    
    def calculate_predictive_power(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        return_threshold: float = 0.0  # Positive/negative threshold
    ) -> PredictivePowerStats:
        """
        Calculate machine learning based predictive power metrics
        
        This treats factor as a binary classifier:
        - Factor > median → Predict positive return
        - Factor < median → Predict negative return
        """
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        stats_obj = PredictivePowerStats()
        
        # Create binary labels
        merged["actual_direction"] = (merged["forward_return"] > return_threshold).astype(int)
        
        # Use factor median as threshold for prediction
        merged["predicted_direction"] = merged.groupby("date")["factor_value"].transform(
            lambda x: (x > x.median()).astype(int)
        )
        
        # Drop NaN
        valid = merged.dropna(subset=["factor_value", "forward_return"])
        
        if len(valid) < 100:
            return stats_obj
        
        y_true = valid["actual_direction"].values
        y_pred = valid["predicted_direction"].values
        y_score = valid["factor_value"].values  # Raw factor values for ROC
        
        # Classification metrics
        stats_obj.hit_rate = accuracy_score(y_true, y_pred)
        stats_obj.precision = precision_score(y_true, y_pred, zero_division=0)
        stats_obj.recall = recall_score(y_true, y_pred, zero_division=0)
        stats_obj.f1_score = f1_score(y_true, y_pred, zero_division=0)
        
        # ROC/AUC
        try:
            stats_obj.auc_score = roc_auc_score(y_true, y_score)
            fpr, tpr, thresholds = roc_curve(y_true, y_score)
            stats_obj.roc_curve_data = np.column_stack([fpr, tpr])
        except:
            stats_obj.auc_score = 0.5
        
        # Direction-specific precision
        up_mask = valid["actual_direction"] == 1
        down_mask = valid["actual_direction"] == 0
        
        if up_mask.sum() > 0:
            stats_obj.up_precision = valid[up_mask]["predicted_direction"].mean()
        if down_mask.sum() > 0:
            stats_obj.down_precision = 1 - valid[down_mask]["predicted_direction"].mean()
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        stats_obj.true_negative = int(tn)
        stats_obj.false_positive = int(fp)
        stats_obj.false_negative = int(fn)
        stats_obj.true_positive = int(tp)
        
        # Information coefficient
        stats_obj.spearman_ic, _ = stats.spearmanr(valid["factor_value"], valid["forward_return"])
        stats_obj.pearson_ic, _ = stats.pearsonr(valid["factor_value"], valid["forward_return"])
        
        return stats_obj
    
    # ==================== 9. Statistical Tests ====================
    
    def calculate_statistical_tests(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> AdvancedStatisticalTests:
        """
        Advanced Statistical Tests
        """
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        stats_obj = AdvancedStatisticalTests()
        
        # Split by median
        median_factor = merged.groupby("date")["factor_value"].transform("median")
        high_group = merged[merged["factor_value"] >= median_factor]["forward_return"].dropna()
        low_group = merged[merged["factor_value"] < median_factor]["forward_return"].dropna()
        
        # Normality tests on IC
        ic_result = self.calculate_ic_analysis(factor_df, returns_df)
        if ic_result and "ic_df" in ic_result:
            ic_series = ic_result["ic_df"]["ic"].dropna()
            
            if len(ic_series) >= 8:
                # Jarque-Bera test
                jb_stat, jb_pvalue = stats.jarque_bera(ic_series)
                stats_obj.jarque_bera_stat = jb_stat
                stats_obj.jarque_bera_pvalue = jb_pvalue
            
            if len(ic_series) >= 3:
                # Shapiro-Wilk test
                shapiro_stat, shapiro_pvalue = stats.shapiro(ic_series)
                stats_obj.shapiro_stat = shapiro_stat
                stats_obj.shapiro_pvalue = shapiro_pvalue
        
        # Significance tests
        if len(high_group) > 0 and len(low_group) > 0:
            # t-test
            t_stat, t_pvalue = stats.ttest_ind(high_group, low_group)
            stats_obj.t_test_stat = t_stat
            stats_obj.t_test_pvalue = t_pvalue
            
            # Wilcoxon test
            try:
                stat, pvalue = stats.ranksums(high_group, low_group)
                stats_obj.wilcoxon_stat = stat
                stats_obj.wilcoxon_pvalue = pvalue
            except:
                pass
        
        # Bonferroni correction
        if stats_obj.t_test_pvalue > 0:
            stats_obj.bonferroni_adjusted_pvalue = min(1.0, stats_obj.t_test_pvalue * 3)
        
        # Autocorrelation analysis
        factor_pivot = factor_df.pivot(index="date", columns="symbol", values="factor_value")
        autocorr_results = []
        
        for col in factor_pivot.columns:
            series = factor_pivot[col].dropna()
            if len(series) > 10:
                for lag in [1, 5, 10]:
                    ac = series.autocorr(lag=lag)
                    if not np.isnan(ac):
                        autocorr_results.append((lag, ac))
        
        if autocorr_results:
            stats_obj.autocorr_lag1 = np.mean([ac for lag, ac in autocorr_results if lag == 1])
            stats_obj.autocorr_lag5 = np.mean([ac for lag, ac in autocorr_results if lag == 5])
            stats_obj.autocorr_lag10 = np.mean([ac for lag, ac in autocorr_results if lag == 10])
        
        # Decay rate
        decay_result = self.calculate_ic_decay(factor_df, returns_df, max_periods=10)
        if decay_result and "decay_curve" in decay_result:
            decay_curve = decay_result["decay_curve"]
            if len(decay_curve) >= 2:
                stats_obj.decay_rate = 1 - (abs(decay_curve[-1]) / abs(decay_curve[0])) if decay_curve[0] != 0 else 0
        
        return stats_obj
    
    # ==================== 10. Stability Analysis ====================
    
    def calculate_stability_analysis(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        market_returns_df: Optional[pd.DataFrame] = None
    ) -> FactorStabilityStats:
        """
        Factor Stability Analysis
        
        Includes:
        - Rolling IC analysis
        - Regime sensitivity (bull/bear)
        - Out-of-sample testing
        """
        stats_obj = FactorStabilityStats()
        
        # Calculate IC series
        ic_result = self.calculate_ic_analysis(factor_df, returns_df)
        
        if not ic_result or "ic_df" not in ic_result:
            return stats_obj
        
        ic_df = ic_result["ic_df"]
        ic_series = ic_df.set_index("date")["ic"]
        
        # Rolling IC statistics
        if len(ic_series) >= self.rolling_window:
            rolling_ic = ic_series.rolling(window=self.rolling_window)
            stats_obj.rolling_ic_mean = rolling_ic.mean().dropna().mean()
            stats_obj.rolling_ic_std = rolling_ic.std().dropna().mean()
            
            # IC trend (linear regression on rolling mean)
            rolling_mean = rolling_ic.mean().dropna()
            if len(rolling_mean) > 2:
                x = np.arange(len(rolling_mean))
                slope, _, _, _, _ = stats.linregress(x, rolling_mean.values)
                stats_obj.rolling_ic_trend = slope
        else:
            stats_obj.rolling_ic_mean = ic_series.mean()
            stats_obj.rolling_ic_std = ic_series.std()
        
        # IC autocorrelation
        if len(ic_series) > 1:
            stats_obj.rolling_ic_autocorr = ic_series.autocorr(lag=1)
        
        # CV (Coefficient of Variation)
        if stats_obj.rolling_ic_mean != 0:
            stats_obj.ic_cv = abs(stats_obj.rolling_ic_std / stats_obj.rolling_ic_mean)
        
        # Regime sensitivity (if market returns provided)
        if market_returns_df is not None and len(market_returns_df) > 0:
            merged_dates = ic_df["date"].values
            
            # Align dates
            market_returns = market_returns_df.set_index("date")
            ic_df_temp = ic_df.set_index("date")
            
            common_dates = ic_df_temp.index.intersection(market_returns.index)
            
            if len(common_dates) > 0:
                aligned_ic = ic_df_temp.loc[common_dates, "ic"]
                aligned_market = market_returns.loc[common_dates, "market_return"]
                
                # Bull/Bear classification
                bull_mask = aligned_market > 0
                bear_mask = aligned_market <= 0
                
                if bull_mask.sum() > 5 and bear_mask.sum() > 5:
                    stats_obj.bull_market_ic = aligned_ic[bull_mask].mean()
                    stats_obj.bear_market_ic = aligned_ic[bear_mask].mean()
                    stats_obj.regime_sensitivity = abs(stats_obj.bull_market_ic - stats_obj.bear_market_ic)
        
        # Out-of-sample analysis
        n_total = len(ic_series)
        n_train = int(n_total * self.train_test_split)
        
        if n_train >= 10 and (n_total - n_train) >= 10:
            in_sample_ic = ic_series.iloc[:n_train].mean()
            out_sample_ic = ic_series.iloc[n_train:].mean()
            
            stats_obj.in_sample_ic = in_sample_ic
            stats_obj.out_sample_ic = out_sample_ic
            
            if abs(in_sample_ic) > 0:
                stats_obj.oos_degradation = (in_sample_ic - out_sample_ic) / abs(in_sample_ic)
        
        # Calculate stability score
        score = 0
        if abs(stats_obj.rolling_ic_mean) > 0.02:
            score += 1
        if stats_obj.ic_cv < 2.0:
            score += 1
        if abs(stats_obj.rolling_ic_trend) < 0.001:
            score += 1
        if abs(stats_obj.regime_sensitivity) < 0.02:
            score += 1
        if stats_obj.oos_degradation < 0.3:
            score += 1
        
        stats_obj.stability_score = score / 5.0
        
        return stats_obj
    
    # ==================== 11. Risk-Adjusted Metrics ====================
    
    def calculate_risk_metrics(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Enhanced Risk-Adjusted Metrics
        """
        group_result = self.calculate_quantile_analysis(factor_df, returns_df)
        
        if not group_result or group_result.quantile_returns is None:
            return {}
        
        quantile_returns = group_result.quantile_returns
        
        # Get spread returns
        n_quantiles = max(quantile_returns.keys()) if quantile_returns else 0
        if n_quantiles < 2:
            return {}
        
        # Need to recalculate with daily returns for drawdown
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        merged["quantile"] = merged.groupby("date")["factor_value"].transform(
            lambda x: pd.qcut(x, n_quantiles, labels=False, duplicates="drop") + 1
        )
        
        quantile_returns_ts = merged.groupby(["date", "quantile"])["forward_return"].mean().unstack()
        
        if quantile_returns_ts.empty or len(quantile_returns_ts.columns) < 2:
            return {}
        
        # Spread returns
        spread = quantile_returns_ts.iloc[:, -1] - quantile_returns_ts.iloc[:, 0]
        
        # Sortino ratio
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
        
        # VaR and CVaR
        var_95 = np.percentile(spread.dropna(), 5)
        cvar_95 = spread[spread <= var_95].mean() if len(spread[spread <= var_95]) > 0 else var_95
        
        return {
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "max_drawdown": max_drawdown,
            "var_95": abs(var_95),
            "cvar_95": abs(cvar_95)
        }
    
    # ==================== Main Testing Function ====================
    
    def test_factor_comprehensive(
        self,
        factor: Any,  # FactorBase
        df: pd.DataFrame,
        market_cap_df: Optional[pd.DataFrame] = None,
        industry_mapping: Optional[Dict[str, str]] = None,
        market_returns_df: Optional[pd.DataFrame] = None,
        forward_periods: List[int] = [1, 5, 10, 20],
        preprocess: bool = True,
        neutralize: bool = False
    ) -> ProfessionalFactorStats:
        """
        Comprehensive Professional Factor Testing
        
        Args:
            factor: Factor instance
            df: DataFrame with OHLCV data
            market_cap_df: DataFrame with market cap data
            industry_mapping: Dict mapping symbol to industry
            market_returns_df: DataFrame with market returns
            forward_periods: Forward return periods to test
            preprocess: Apply preprocessing
            neutralize: Apply neutralization
        
        Returns:
            ProfessionalFactorStats object with all metrics
        """
        logger.info(f"Professional comprehensive testing for factor: {factor.name}")
        
        # Calculate factor values
        factor_df = factor.calculate(df)
        
        if factor_df.empty:
            return ProfessionalFactorStats(name=factor.name, category="unknown")
        
        # Preprocessing
        if preprocess:
            factor_df = self.preprocessor.winsorize(factor_df)
            factor_df = self.preprocessor.standardize(factor_df)
        
        # Calculate forward returns
        df_copy = df.copy()
        main_period = forward_periods[0] if forward_periods else 5
        df_copy["forward_return"] = df_copy.groupby("symbol")["close"].transform(
            lambda x: x.shift(-main_period) / x - 1
        )
        
        # Run all tests
        logger.info("  Running IC analysis...")
        ic_result = self.calculate_ic_analysis(factor_df, df_copy)
        
        logger.info("  Running regression analysis...")
        reg_result = self.calculate_regression_analysis(factor_df, df_copy)
        
        logger.info("  Running quantile analysis...")
        quantile_stats = self.calculate_quantile_analysis(factor_df, df_copy)
        
        logger.info("  Running IC decay analysis...")
        decay_result = self.calculate_ic_decay(factor_df, df_copy)
        
        logger.info("  Running turnover analysis...")
        turnover_result = self.calculate_turnover_analysis(factor_df)
        
        logger.info("  Running predictive power analysis...")
        predictive_stats = self.calculate_predictive_power(factor_df, df_copy)
        
        logger.info("  Running statistical tests...")
        stat_tests = self.calculate_statistical_tests(factor_df, df_copy)
        
        logger.info("  Running stability analysis...")
        stability_stats = self.calculate_stability_analysis(factor_df, df_copy, market_returns_df)
        
        logger.info("  Running risk metrics analysis...")
        risk_result = self.calculate_risk_metrics(factor_df, df_copy)
        
        # Optional: Market Cap Stratification
        market_cap_stats = None
        if market_cap_df is not None and not market_cap_df.empty:
            logger.info("  Running market cap stratification...")
            market_cap_stats = self.calculate_market_cap_stratification(
                factor_df, df_copy, market_cap_df
            )
        
        # Optional: Industry Stratification
        industry_stats = None
        if industry_mapping is not None:
            logger.info("  Running industry stratification...")
            industry_stats = self.calculate_industry_stratification(
                factor_df, df_copy, industry_mapping
            )
        
        # Determine effectiveness
        is_effective, score, grade, reasons, strengths = self._determine_effectiveness(
            ic_result, reg_result, quantile_stats, turnover_result, 
            predictive_stats, stability_stats
        )
        
        return ProfessionalFactorStats(
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
            ic_skewness=ic_result.get("ic_skewness", 0),
            ic_kurtosis=ic_result.get("ic_kurtosis", 0),
            
            # Regression
            factor_return_mean=reg_result.get("factor_return_mean", 0),
            factor_return_t_stat=reg_result.get("factor_return_t_stat", 0),
            factor_return_p_value=reg_result.get("factor_return_p_value", 0),
            t_value_mean=reg_result.get("t_value_mean", 0),
            t_value_significant_ratio=reg_result.get("t_value_significant_ratio", 0),
            
            # Group Testing
            quantile_stats=quantile_stats,
            
            # Market Cap Stratification
            market_cap_stats=market_cap_stats,
            
            # Industry Stratification
            industry_stats=industry_stats,
            
            # IC Decay
            ic_half_life=decay_result.get("half_life", 0),
            ic_decay_curve=decay_result.get("decay_curve", []),
            ic_decay_r_squared=decay_result.get("r_squared", 0),
            
            # Turnover
            turnover_mean=turnover_result.get("turnover_mean", 0),
            turnover_std=turnover_result.get("turnover_std", 0),
            autocorrelation=turnover_result.get("autocorrelation", 0),
            factor_rank_autocorr=turnover_result.get("factor_rank_autocorr", 0),
            
            # Predictive Power
            predictive_stats=predictive_stats,
            
            # Statistical Tests
            stat_tests=stat_tests,
            
            # Stability
            stability_stats=stability_stats,
            
            # Risk
            sortino_ratio=risk_result.get("sortino_ratio", 0),
            calmar_ratio=risk_result.get("calmar_ratio", 0),
            max_drawdown=risk_result.get("max_drawdown", 0),
            var_95=risk_result.get("var_95", 0),
            cvar_95=risk_result.get("cvar_95", 0),
            
            # Effectiveness
            is_effective=is_effective,
            effectiveness_score=score,
            effectiveness_grade=grade,
            failure_reasons=reasons,
            strengths=strengths
        )
    
    def _determine_effectiveness(
        self,
        ic_result: Dict,
        reg_result: Dict,
        quantile_stats: QuantileAnalysisStats,
        turnover_result: Dict,
        predictive_stats: PredictivePowerStats,
        stability_stats: FactorStabilityStats
    ) -> Tuple[bool, float, str, List[str], List[str]]:
        """
        Determine factor effectiveness with professional grading
        """
        reasons = []
        strengths = []
        score = 0
        max_score = 15
        
        # 1. IC mean (weight: 2)
        ic_mean = abs(ic_result.get("ic_mean", 0))
        if ic_mean >= 0.05:
            score += 2
            strengths.append(f"Strong IC ({ic_mean:.4f})")
        elif ic_mean >= 0.03:
            score += 1.5
            strengths.append(f"Good IC ({ic_mean:.4f})")
        elif ic_mean >= 0.02:
            score += 1
        else:
            reasons.append(f"IC too low ({ic_mean:.4f})")
        
        # 2. ICIR (weight: 2)
        icir = abs(ic_result.get("icir", 0))
        if icir >= 1.0:
            score += 2
            strengths.append(f"Excellent ICIR ({icir:.2f})")
        elif icir >= 0.5:
            score += 1.5
            strengths.append(f"Good ICIR ({icir:.2f})")
        elif icir >= 0.3:
            score += 1
        else:
            reasons.append(f"ICIR too low ({icir:.2f})")
        
        # 3. IC t-stat (weight: 1)
        ic_t = abs(ic_result.get("ic_t_stat", 0))
        if ic_t >= 3:
            score += 1
            strengths.append("Highly significant IC")
        elif ic_t >= 2:
            score += 0.5
        else:
            reasons.append(f"IC not significant (t={ic_t:.2f})")
        
        # 4. Monotonicity (weight: 2)
        mono = quantile_stats.monotonicity_score if quantile_stats else 0
        if mono >= 0.8:
            score += 2
            strengths.append(f"Excellent monotonicity ({mono:.2f})")
        elif mono >= 0.6:
            score += 1.5
        elif mono >= 0.4:
            score += 1
        else:
            reasons.append(f"Poor monotonicity ({mono:.2f})")
        
        # 5. Spread significance (weight: 1)
        spread_t = abs(quantile_stats.spread_t_stat) if quantile_stats else 0
        if spread_t >= 2:
            score += 1
        else:
            reasons.append(f"Spread not significant (t={spread_t:.2f})")
        
        # 6. Predictive power (weight: 2)
        auc = predictive_stats.auc_score if predictive_stats else 0.5
        if auc >= 0.55:
            score += 2
            strengths.append(f"Good AUC ({auc:.3f})")
        elif auc >= 0.52:
            score += 1
        else:
            reasons.append(f"Low AUC ({auc:.3f})")
        
        # 7. F1 Score (weight: 1)
        f1 = predictive_stats.f1_score if predictive_stats else 0
        if f1 >= 0.5:
            score += 1
        else:
            reasons.append(f"Low F1 score ({f1:.3f})")
        
        # 8. Stability (weight: 2)
        stability = stability_stats.stability_score if stability_stats else 0
        if stability >= 0.8:
            score += 2
            strengths.append(f"Highly stable ({stability:.2f})")
        elif stability >= 0.6:
            score += 1.5
        elif stability >= 0.4:
            score += 1
        else:
            reasons.append(f"Unstable factor ({stability:.2f})")
        
        # 9. Turnover (weight: 1)
        turnover = turnover_result.get("turnover_mean", 1)
        if turnover <= 0.2:
            score += 1
            strengths.append("Low turnover")
        elif turnover <= 0.3:
            score += 0.5
        elif turnover > 0.5:
            reasons.append(f"High turnover ({turnover:.2%})")
        
        # 10. IC half-life (weight: 1)
        half_life = decay_result.get("half_life", 0) if (decay_result := {}) else 0
        if 3 <= half_life <= 20:
            score += 1
        elif half_life < 2:
            reasons.append(f"IC decays too fast (half-life={half_life})")
        
        normalized_score = score / max_score
        
        # Determine grade
        if normalized_score >= 0.85:
            grade = "A+"
        elif normalized_score >= 0.75:
            grade = "A"
        elif normalized_score >= 0.65:
            grade = "B"
        elif normalized_score >= 0.50:
            grade = "C"
        elif normalized_score >= 0.35:
            grade = "D"
        else:
            grade = "F"
        
        is_effective = normalized_score >= 0.5 and len(reasons) <= 3
        
        return is_effective, normalized_score, grade, reasons, strengths


class FactorPreprocessor:
    """
    Factor data preprocessing
    """
    
    @staticmethod
    def winsorize(
        df: pd.DataFrame,
        column: str = "factor_value",
        method: str = "mad",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """Winsorize factor values"""
        df = df.copy()
        
        if method == "mad":
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
            raise ValueError(f"Unknown method: {method}")
        
        df[column] = df[column].clip(lower, upper)
        return df
    
    @staticmethod
    def standardize(
        df: pd.DataFrame,
        column: str = "factor_value",
        method: str = "zscore"
    ) -> pd.DataFrame:
        """Standardize factor values"""
        df = df.copy()
        
        if method == "zscore":
            df[column] = df.groupby("date")[column].transform(
                lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x - x.mean()
            )
        elif method == "rank":
            df[column] = df.groupby("date")[column].transform(
                lambda x: x.rank(pct=True)
            )
        
        return df


# Convenience function
def test_factor(
    factor: Any,
    df: pd.DataFrame,
    **kwargs
) -> ProfessionalFactorStats:
    """
    Convenience function to test a factor
    """
    tester = ProfessionalFactorTester()
    return tester.test_factor_comprehensive(factor, df, **kwargs)
