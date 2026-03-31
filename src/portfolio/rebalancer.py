"""
Rebalancer - Portfolio rebalancing logic
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Callable
from loguru import logger
from datetime import datetime, timedelta
from enum import Enum


class RebalanceFrequency(Enum):
    """Rebalance frequency options"""
    DAILY = 1
    WEEKLY = 5
    BI_WEEKLY = 10
    MONTHLY = 20
    QUARTERLY = 60


class RebalanceTrigger:
    """
    Rebalance trigger conditions
    
    Triggers rebalancing when:
    - Time-based: Fixed interval
    - Drift-based: Portfolio weights drift from target
    - Signal-based: Signal changes significantly
    """
    
    def __init__(
        self,
        frequency: RebalanceFrequency = RebalanceFrequency.WEEKLY,
        drift_threshold: Optional[float] = None,
        signal_change_threshold: Optional[float] = None
    ):
        """
        Initialize rebalance trigger
        
        Args:
            frequency: Rebalance frequency
            drift_threshold: Maximum allowed weight drift
            signal_change_threshold: Maximum allowed signal change
        """
        self.frequency = frequency
        self.drift_threshold = drift_threshold
        self.signal_change_threshold = signal_change_threshold
        
        self._last_rebalance: Optional[datetime] = None
        self._days_since_rebalance = 0
    
    def should_rebalance(
        self,
        current_date: datetime,
        current_weights: Optional[pd.Series] = None,
        target_weights: Optional[pd.Series] = None,
        current_signals: Optional[pd.Series] = None,
        previous_signals: Optional[pd.Series] = None
    ) -> bool:
        """
        Check if rebalancing is needed
        
        Args:
            current_date: Current date
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            current_signals: Current signals
            previous_signals: Previous period signals
            
        Returns:
            True if rebalancing is needed
        """
        # Time-based trigger
        if self._last_rebalance is None:
            self._last_rebalance = current_date
            return True
        
        self._days_since_rebalance += 1
        
        if self._days_since_rebalance >= self.frequency.value:
            self._days_since_rebalance = 0
            self._last_rebalance = current_date
            return True
        
        # Drift-based trigger
        if self.drift_threshold is not None:
            if current_weights is not None and target_weights is not None:
                drift = self._calculate_drift(current_weights, target_weights)
                if drift > self.drift_threshold:
                    self._days_since_rebalance = 0
                    self._last_rebalance = current_date
                    return True
        
        # Signal-based trigger
        if self.signal_change_threshold is not None:
            if current_signals is not None and previous_signals is not None:
                signal_change = self._calculate_signal_change(
                    current_signals, previous_signals
                )
                if signal_change > self.signal_change_threshold:
                    self._days_since_rebalance = 0
                    self._last_rebalance = current_date
                    return True
        
        return False
    
    def _calculate_drift(
        self,
        current: pd.Series,
        target: pd.Series
    ) -> float:
        """Calculate portfolio drift"""
        # Align indices
        all_symbols = current.index.union(target.index)
        current = current.reindex(all_symbols, fill_value=0)
        target = target.reindex(all_symbols, fill_value=0)
        
        # Calculate absolute drift
        drift = (current - target).abs().sum() / 2
        return drift
    
    def _calculate_signal_change(
        self,
        current: pd.Series,
        previous: pd.Series
    ) -> float:
        """Calculate signal change"""
        # Align indices
        common_symbols = current.index.intersection(previous.index)
        
        if len(common_symbols) == 0:
            return 1.0
        
        # Calculate correlation
        corr = current[common_symbols].corr(previous[common_symbols])
        return 1 - corr


class Rebalancer:
    """
    Portfolio Rebalancer
    
    Features:
    - Multiple rebalance triggers
    - Trade optimization
    - Turnover control
    - Cost-aware rebalancing
    
    Workflow:
    1. Check rebalance trigger
    2. Calculate target portfolio
    3. Optimize trades
    4. Execute rebalance
    """
    
    def __init__(
        self,
        trigger: Optional[RebalanceTrigger] = None,
        max_turnover: float = 0.3,
        min_trade_size: float = 0.001,
        trade_buffer: float = 0.0
    ):
        """
        Initialize rebalancer
        
        Args:
            trigger: Rebalance trigger instance
            max_turnover: Maximum turnover per rebalance
            min_trade_size: Minimum trade size as fraction of portfolio
            trade_buffer: No-trade buffer around target weights
        """
        self.trigger = trigger or RebalanceTrigger()
        self.max_turnover = max_turnover
        self.min_trade_size = min_trade_size
        self.trade_buffer = trade_buffer
        
        self._rebalance_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"Rebalancer initialized: "
            f"frequency={trigger.frequency if trigger else 'weekly'}, "
            f"max_turnover={max_turnover}"
        )
    
    def check_and_rebalance(
        self,
        current_date: datetime,
        current_weights: pd.Series,
        target_weights: pd.Series,
        current_signals: Optional[pd.Series] = None,
        previous_signals: Optional[pd.Series] = None
    ) -> Optional[pd.Series]:
        """
        Check if rebalancing is needed and return adjusted weights
        
        Args:
            current_date: Current date
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            current_signals: Current signals
            previous_signals: Previous signals
            
        Returns:
            Adjusted weights if rebalancing, None otherwise
        """
        should_rebalance = self.trigger.should_rebalance(
            current_date=current_date,
            current_weights=current_weights,
            target_weights=target_weights,
            current_signals=current_signals,
            previous_signals=previous_signals
        )
        
        if not should_rebalance:
            return None
        
        # Calculate adjusted weights
        adjusted_weights = self._optimize_trades(
            current_weights,
            target_weights
        )
        
        # Record rebalance
        self._record_rebalance(
            current_date,
            current_weights,
            adjusted_weights
        )
        
        return adjusted_weights
    
    def _optimize_trades(
        self,
        current: pd.Series,
        target: pd.Series
    ) -> pd.Series:
        """
        Optimize trades considering constraints
        
        Args:
            current: Current weights
            target: Target weights
            
        Returns:
            Adjusted target weights
        """
        # Align indices
        all_symbols = current.index.union(target.index)
        current = current.reindex(all_symbols, fill_value=0)
        target = target.reindex(all_symbols, fill_value=0)
        
        # Apply trade buffer
        if self.trade_buffer > 0:
            # Only trade if deviation exceeds buffer
            deviation = target - current
            adjusted = current.copy()
            
            for symbol in all_symbols:
                if abs(deviation[symbol]) > self.trade_buffer:
                    adjusted[symbol] = target[symbol]
            
            target = adjusted
        
        # Apply turnover constraint
        turnover = (target - current).abs().sum() / 2
        
        if turnover > self.max_turnover:
            # Scale down trades
            scale = self.max_turnover / turnover
            target = current + scale * (target - current)
        
        # Apply minimum trade size
        trades = target - current
        small_trades = trades.abs() < self.min_trade_size
        target[small_trades] = current[small_trades]
        
        # Normalize
        target = target / target.sum()
        
        return target
    
    def _record_rebalance(
        self,
        date: datetime,
        old_weights: pd.Series,
        new_weights: pd.Series
    ):
        """Record rebalance event"""
        turnover = (new_weights - old_weights).abs().sum() / 2
        
        self._rebalance_history.append({
            "date": date,
            "turnover": turnover,
            "n_positions_before": (old_weights > 0).sum(),
            "n_positions_after": (new_weights > 0).sum(),
            "positions_added": ((old_weights == 0) & (new_weights > 0)).sum(),
            "positions_removed": ((old_weights > 0) & (new_weights == 0)).sum()
        })
    
    def get_rebalance_schedule(
        self,
        start_date: str,
        end_date: str,
        custom_dates: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generate rebalance schedule
        
        Args:
            start_date: Start date
            end_date: End date
            custom_dates: Custom rebalance dates
            
        Returns:
            DataFrame with rebalance dates
        """
        dates = pd.date_range(start_date, end_date, freq="B")
        
        if custom_dates:
            custom_dates = pd.to_datetime(custom_dates)
            rebalance = [d in custom_dates for d in dates]
        else:
            rebalance = [i % self.trigger.frequency.value == 0 
                        for i in range(len(dates))]
        
        schedule = pd.DataFrame({
            "date": dates,
            "rebalance": rebalance
        })
        
        return schedule
    
    def get_rebalance_history(self) -> pd.DataFrame:
        """Get rebalance history"""
        if not self._rebalance_history:
            return pd.DataFrame()
        
        return pd.DataFrame(self._rebalance_history)
    
    def get_rebalance_summary(self) -> Dict[str, Any]:
        """Get rebalance summary statistics"""
        if not self._rebalance_history:
            return {}
        
        history = self.get_rebalance_history()
        
        return {
            "n_rebalances": len(history),
            "avg_turnover": history["turnover"].mean(),
            "max_turnover": history["turnover"].max(),
            "avg_positions": history["n_positions_after"].mean(),
            "avg_positions_added": history["positions_added"].mean(),
            "avg_positions_removed": history["positions_removed"].mean()
        }
