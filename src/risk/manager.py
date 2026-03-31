"""
Risk Manager - Risk monitoring and control
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetrics:
    """Risk metrics container"""
    var_95: float
    var_99: float
    cvar_95: float
    max_drawdown: float
    volatility: float
    beta: float
    tracking_error: float
    information_ratio: float
    sortino_ratio: float
    calmar_ratio: float


class RiskManager:
    """
    Risk Management System
    
    Features:
    - Value at Risk (VaR) calculation
    - Drawdown monitoring
    - Position limits
    - Risk budgeting
    - Risk alerts
    
    This follows professional risk management standards
    used by large quantitative hedge funds.
    """
    
    def __init__(
        self,
        max_position_size: float = 0.05,
        max_sector_weight: float = 0.30,
        max_drawdown_limit: float = 0.15,
        var_confidence: float = 0.95,
        risk_free_rate: float = 0.03
    ):
        """
        Initialize risk manager
        
        Args:
            max_position_size: Maximum single position size
            max_sector_weight: Maximum sector weight
            max_drawdown_limit: Maximum drawdown before risk reduction
            var_confidence: VaR confidence level
            risk_free_rate: Risk-free rate for calculations
        """
        self.max_position_size = max_position_size
        self.max_sector_weight = max_sector_weight
        self.max_drawdown_limit = max_drawdown_limit
        self.var_confidence = var_confidence
        self.risk_free_rate = risk_free_rate
        
        self._current_drawdown = 0
        self._risk_level = RiskLevel.LOW
        
        logger.info(
            f"RiskManager initialized: "
            f"max_position={max_position_size:.2%}, "
            f"max_dd={max_drawdown_limit:.2%}"
        )
    
    def calculate_var(
        self,
        returns: pd.Series,
        confidence: Optional[float] = None,
        method: str = "historical"
    ) -> float:
        """
        Calculate Value at Risk
        
        Args:
            returns: Returns series
            confidence: Confidence level
            method: VaR method ("historical", "parametric", "cornish_fisher")
            
        Returns:
            VaR value
        """
        confidence = confidence or self.var_confidence
        
        if method == "historical":
            # Historical VaR
            var = -np.percentile(returns, (1 - confidence) * 100)
        
        elif method == "parametric":
            # Parametric VaR (assumes normal distribution)
            mean = returns.mean()
            std = returns.std()
            var = -(mean + std * np.percentile(np.random.normal(0, 1, 100000), 
                                                (1 - confidence) * 100))
        
        elif method == "cornish_fisher":
            # Cornish-Fisher expansion (accounts for skewness and kurtosis)
            mean = returns.mean()
            std = returns.std()
            skew = returns.skew()
            kurt = returns.kurtosis()
            
            z = np.percentile(np.random.normal(0, 1, 100000), (1 - confidence) * 100)
            
            # Cornish-Fisher adjustment
            z_cf = (z + 
                    (z**2 - 1) * skew / 6 +
                    (z**3 - 3*z) * (kurt - 3) / 24 -
                    (2*z**3 - 5*z) * skew**2 / 36)
            
            var = -(mean + std * z_cf)
        
        else:
            raise ValueError(f"Unknown VaR method: {method}")
        
        return var
    
    def calculate_cvar(
        self,
        returns: pd.Series,
        confidence: Optional[float] = None
    ) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall)
        
        Args:
            returns: Returns series
            confidence: Confidence level
            
        Returns:
            CVaR value
        """
        confidence = confidence or self.var_confidence
        var = self.calculate_var(returns, confidence)
        
        # Average of losses beyond VaR
        cvar = -returns[returns < -var].mean()
        
        return cvar
    
    def calculate_max_drawdown(
        self,
        equity_curve: pd.Series
    ) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            equity_curve: Equity curve series
            
        Returns:
            Maximum drawdown
        """
        cumulative = equity_curve
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        
        return abs(drawdown.min())
    
    def calculate_risk_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics
        
        Args:
            returns: Portfolio returns
            benchmark_returns: Benchmark returns (optional)
            
        Returns:
            RiskMetrics object
        """
        # VaR
        var_95 = self.calculate_var(returns, 0.95)
        var_99 = self.calculate_var(returns, 0.99)
        cvar_95 = self.calculate_cvar(returns, 0.95)
        
        # Drawdown
        equity = (1 + returns).cumprod()
        max_drawdown = self.calculate_max_drawdown(equity)
        
        # Volatility
        volatility = returns.std() * np.sqrt(252)
        
        # Beta (if benchmark provided)
        if benchmark_returns is not None:
            cov = returns.cov(benchmark_returns)
            var_bench = benchmark_returns.var()
            beta = cov / var_bench if var_bench > 0 else 0
            
            # Tracking error
            tracking_error = (returns - benchmark_returns).std() * np.sqrt(252)
            
            # Information ratio
            excess_return = (returns.mean() - benchmark_returns.mean()) * 252
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
        else:
            beta = 0
            tracking_error = volatility
            information_ratio = 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        excess_return = returns.mean() * 252 - self.risk_free_rate
        sortino_ratio = excess_return / downside_std if downside_std > 0 else 0
        
        # Calmar ratio
        calmar_ratio = excess_return / max_drawdown if max_drawdown > 0 else 0
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            max_drawdown=max_drawdown,
            volatility=volatility,
            beta=beta,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio
        )
    
    def check_position_limits(
        self,
        positions: pd.DataFrame,
        sector_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Check position limits
        
        Args:
            positions: DataFrame with positions and weights
            sector_mapping: Dictionary mapping symbols to sectors
            
        Returns:
            Dictionary with limit check results
        """
        violations = []
        
        # Check individual position limits
        max_weight = positions["weight"].max()
        if max_weight > self.max_position_size:
            violations.append({
                "type": "position_limit",
                "message": f"Max position weight {max_weight:.2%} exceeds limit {self.max_position_size:.2%}",
                "symbols": positions[positions["weight"] > self.max_position_size]["symbol"].tolist()
            })
        
        # Check sector limits
        if sector_mapping:
            positions["sector"] = positions["symbol"].map(sector_mapping)
            sector_weights = positions.groupby("sector")["weight"].sum()
            
            for sector, weight in sector_weights.items():
                if weight > self.max_sector_weight:
                    violations.append({
                        "type": "sector_limit",
                        "message": f"Sector {sector} weight {weight:.2%} exceeds limit {self.max_sector_weight:.2%}",
                        "sector": sector,
                        "weight": weight
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    def update_risk_level(
        self,
        current_drawdown: float
    ) -> RiskLevel:
        """
        Update risk level based on current drawdown
        
        Args:
            current_drawdown: Current drawdown
            
        Returns:
            RiskLevel enum
        """
        self._current_drawdown = current_drawdown
        
        if current_drawdown < self.max_drawdown_limit * 0.3:
            self._risk_level = RiskLevel.LOW
        elif current_drawdown < self.max_drawdown_limit * 0.6:
            self._risk_level = RiskLevel.MEDIUM
        elif current_drawdown < self.max_drawdown_limit:
            self._risk_level = RiskLevel.HIGH
        else:
            self._risk_level = RiskLevel.CRITICAL
        
        return self._risk_level
    
    def get_risk_budget(
        self,
        risk_level: Optional[RiskLevel] = None
    ) -> Dict[str, float]:
        """
        Get risk budget based on risk level
        
        Args:
            risk_level: Risk level (uses current if None)
            
        Returns:
            Dictionary with risk budget parameters
        """
        risk_level = risk_level or self._risk_level
        
        budgets = {
            RiskLevel.LOW: {
                "position_multiplier": 1.0,
                "leverage_limit": 1.0,
                "new_position_limit": self.max_position_size
            },
            RiskLevel.MEDIUM: {
                "position_multiplier": 0.8,
                "leverage_limit": 0.8,
                "new_position_limit": self.max_position_size * 0.8
            },
            RiskLevel.HIGH: {
                "position_multiplier": 0.5,
                "leverage_limit": 0.5,
                "new_position_limit": self.max_position_size * 0.5
            },
            RiskLevel.CRITICAL: {
                "position_multiplier": 0.2,
                "leverage_limit": 0.2,
                "new_position_limit": self.max_position_size * 0.2
            }
        }
        
        return budgets.get(risk_level, budgets[RiskLevel.LOW])
    
    def generate_risk_report(
        self,
        returns: pd.Series,
        positions: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk report
        
        Args:
            returns: Portfolio returns
            positions: Current positions
            
        Returns:
            Risk report dictionary
        """
        metrics = self.calculate_risk_metrics(returns)
        
        report = {
            "risk_level": self._risk_level.value,
            "current_drawdown": self._current_drawdown,
            "drawdown_limit": self.max_drawdown_limit,
            "risk_metrics": {
                "var_95": metrics.var_95,
                "var_99": metrics.var_99,
                "cvar_95": metrics.cvar_95,
                "max_drawdown": metrics.max_drawdown,
                "volatility": metrics.volatility,
                "beta": metrics.beta,
                "sortino_ratio": metrics.sortino_ratio,
                "calmar_ratio": metrics.calmar_ratio
            },
            "risk_budget": self.get_risk_budget()
        }
        
        if positions is not None:
            report["position_check"] = self.check_position_limits(positions)
        
        return report
