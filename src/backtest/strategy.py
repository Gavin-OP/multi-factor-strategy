"""
Backtest Strategy - Factor-based strategy implementation
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from abc import ABC, abstractmethod


class StrategyBase(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        pass
    
    @abstractmethod
    def get_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """Get target positions from signals"""
        pass


class FactorStrategy(StrategyBase):
    """
    Factor-based trading strategy
    
    Workflow:
    1. Calculate factors
    2. Combine factors into signal
    3. Select stocks
    4. Allocate weights
    """
    
    def __init__(
        self,
        factor_engine,
        signal_generator,
        stock_selector,
        weight_allocator,
        n_positions: int = 50,
        rebalance_freq: int = 5
    ):
        """
        Initialize factor strategy
        
        Args:
            factor_engine: FactorEngine instance
            signal_generator: SignalGenerator instance
            stock_selector: StockSelector instance
            weight_allocator: WeightAllocator instance
            n_positions: Number of positions
            rebalance_freq: Rebalance frequency in days
        """
        self.factor_engine = factor_engine
        self.signal_generator = signal_generator
        self.stock_selector = stock_selector
        self.weight_allocator = weight_allocator
        self.n_positions = n_positions
        self.rebalance_freq = rebalance_freq
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals from data"""
        # Calculate factors
        factor_df = self.factor_engine.calculate_factors(data)
        
        # Generate signals
        signal_df = self.signal_generator.generate(factor_df)
        
        return signal_df
    
    def get_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """Get target positions from signals"""
        # Select stocks
        selected = self.stock_selector.select(signals)
        
        # Allocate weights
        positions = self.weight_allocator.allocate(selected)
        
        return positions
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000000
    ) -> Dict[str, Any]:
        """
        Run simple backtest
        
        Args:
            data: DataFrame with OHLCV data
            initial_capital: Initial capital
            
        Returns:
            Dictionary with backtest results
        """
        logger.info("Running factor strategy backtest...")
        
        # Generate signals
        signals = self.generate_signals(data)
        
        # Get unique dates
        dates = sorted(signals["date"].unique())
        
        # Initialize portfolio
        portfolio_value = initial_capital
        positions = {}
        equity_curve = []
        
        for i, date in enumerate(dates):
            # Check if rebalance date
            if i % self.rebalance_freq == 0:
                # Get signals for date
                date_signals = signals[signals["date"] == date]
                
                # Get target positions
                target_positions = self.get_positions(date_signals)
                
                # Update positions
                positions = target_positions.set_index("symbol")["weight"].to_dict()
            
            # Calculate portfolio value
            date_data = data[data["date"] == date]
            daily_value = 0
            
            for symbol, weight in positions.items():
                stock_data = date_data[date_data["symbol"] == symbol]
                if not stock_data.empty:
                    price = stock_data["close"].iloc[0]
                    # Simplified: use weight * total_value as position value
                    daily_value += weight * portfolio_value
            
            # Add cash
            daily_value += portfolio_value * (1 - sum(positions.values()))
            
            equity_curve.append({
                "date": date,
                "equity": daily_value,
                "portfolio_value": portfolio_value
            })
            
            # Update portfolio value (simplified)
            # In practice, you'd calculate actual returns
            if i > 0:
                returns = date_data.groupby("symbol")["close"].pct_change()
                portfolio_return = sum(
                    positions.get(s, 0) * returns.get(s, 0)
                    for s in positions
                )
                portfolio_value *= (1 + portfolio_return)
        
        equity_df = pd.DataFrame(equity_curve)
        
        # Calculate metrics
        equity_df["return"] = equity_df["equity"].pct_change()
        
        total_return = (equity_df["equity"].iloc[-1] / initial_capital) - 1
        sharpe = (
            equity_df["return"].mean() / equity_df["return"].std() * np.sqrt(252)
            if equity_df["return"].std() > 0 else 0
        )
        
        # Max drawdown
        cumulative = equity_df["equity"]
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            "equity_curve": equity_df,
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "final_value": equity_df["equity"].iloc[-1]
        }
