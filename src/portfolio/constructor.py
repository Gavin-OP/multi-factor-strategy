"""
Portfolio Constructor - Build and manage portfolio
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from dataclasses import dataclass
from datetime import datetime

from src.portfolio.weighting import WeightAllocator


@dataclass
class PortfolioState:
    """Portfolio state at a point in time"""
    date: datetime
    positions: pd.DataFrame
    total_value: float
    cash: float
    weights: pd.Series
    returns: Optional[float] = None


class PortfolioConstructor:
    """
    Portfolio Construction Manager
    
    Features:
    - Build portfolio from signals
    - Track portfolio state
    - Handle corporate actions
    - Support multiple asset classes
    
    Workflow:
    1. Receive stock selection
    2. Apply weighting scheme
    3. Apply constraints
    4. Track positions
    """
    
    def __init__(
        self,
        weight_allocator: Optional[WeightAllocator] = None,
        initial_capital: float = 10000000,
        transaction_cost: float = 0.0003,
        slippage: float = 0.0001,
        allow_short: bool = False
    ):
        """
        Initialize portfolio constructor
        
        Args:
            weight_allocator: Weight allocator instance
            initial_capital: Initial portfolio value
            transaction_cost: Transaction cost as fraction
            slippage: Slippage as fraction
            allow_short: Allow short positions
        """
        self.weight_allocator = weight_allocator or WeightAllocator()
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.allow_short = allow_short
        
        # Portfolio state
        self.cash = initial_capital
        self.positions: Dict[str, float] = {}  # symbol -> quantity
        self.position_values: Dict[str, float] = {}  # symbol -> value
        self._portfolio_history: List[PortfolioState] = []
        
        logger.info(
            f"PortfolioConstructor initialized: "
            f"capital={initial_capital:,.0f}, "
            f"cost={transaction_cost:.4f}"
        )
    
    def construct(
        self,
        selected_stocks: pd.DataFrame,
        price_df: pd.DataFrame,
        date: datetime,
        **kwargs
    ) -> PortfolioState:
        """
        Construct portfolio for a given date
        
        Args:
            selected_stocks: DataFrame with selected stocks and signals
            price_df: DataFrame with current prices
            date: Current date
            **kwargs: Additional arguments for weight allocation
            
        Returns:
            Portfolio state
        """
        # Get prices for selected stocks
        prices = price_df[price_df["date"] == date].set_index("symbol")["close"]
        
        # Calculate target weights
        weights_df = self.weight_allocator.allocate(
            selected_stocks,
            previous_weights=self._get_previous_weights(),
            **kwargs
        )
        
        # Merge with prices
        weights_df = weights_df.merge(
            prices.reset_index()[["symbol", "close"]],
            on="symbol",
            how="left"
        )
        
        # Calculate position sizes
        total_value = self._get_total_value(prices)
        
        weights_df["target_value"] = weights_df["weight"] * total_value
        weights_df["target_quantity"] = weights_df["target_value"] / weights_df["close"]
        weights_df["target_quantity"] = weights_df["target_quantity"].fillna(0)
        
        # Calculate trades
        trades = self._calculate_trades(weights_df, prices)
        
        # Apply transaction costs
        trade_value = trades["trade_value"].abs().sum()
        costs = trade_value * (self.transaction_cost + self.slippage)
        self.cash -= costs
        
        # Update positions
        self._update_positions(trades, prices)
        
        # Create portfolio state
        state = PortfolioState(
            date=date,
            positions=weights_df.copy(),
            total_value=self._get_total_value(prices),
            cash=self.cash,
            weights=weights_df.set_index("symbol")["weight"]
        )
        
        self._portfolio_history.append(state)
        
        logger.info(
            f"Portfolio constructed for {date.date()}: "
            f"{len(weights_df)} positions, "
            f"value={state.total_value:,.0f}"
        )
        
        return state
    
    def _get_previous_weights(self) -> Optional[pd.Series]:
        """Get previous period weights"""
        if not self.position_values:
            return None
        
        total = sum(self.position_values.values())
        if total == 0:
            return None
        
        return pd.Series({
            symbol: value / total
            for symbol, value in self.position_values.items()
        })
    
    def _get_total_value(self, prices: pd.Series) -> float:
        """Calculate total portfolio value"""
        position_value = sum(
            self.positions.get(symbol, 0) * prices.get(symbol, 0)
            for symbol in self.positions
        )
        return position_value + self.cash
    
    def _calculate_trades(
        self,
        target_df: pd.DataFrame,
        prices: pd.Series
    ) -> pd.DataFrame:
        """Calculate required trades"""
        trades = []
        
        for _, row in target_df.iterrows():
            symbol = row["symbol"]
            target_qty = row["target_quantity"]
            current_qty = self.positions.get(symbol, 0)
            trade_qty = target_qty - current_qty
            
            price = prices.get(symbol, row["close"])
            trade_value = trade_qty * price
            
            trades.append({
                "symbol": symbol,
                "current_quantity": current_qty,
                "target_quantity": target_qty,
                "trade_quantity": trade_qty,
                "price": price,
                "trade_value": trade_value
            })
        
        return pd.DataFrame(trades)
    
    def _update_positions(
        self,
        trades: pd.DataFrame,
        prices: pd.Series
    ):
        """Update positions after trades"""
        for _, trade in trades.iterrows():
            symbol = trade["symbol"]
            trade_qty = trade["trade_quantity"]
            trade_value = trade["trade_value"]
            
            # Update position
            old_qty = self.positions.get(symbol, 0)
            new_qty = old_qty + trade_qty
            
            if new_qty == 0:
                if symbol in self.positions:
                    del self.positions[symbol]
                if symbol in self.position_values:
                    del self.position_values[symbol]
            else:
                self.positions[symbol] = new_qty
                self.position_values[symbol] = new_qty * prices.get(symbol, trade["price"])
            
            # Update cash
            self.cash -= trade_value
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        total_value = sum(self.position_values.values()) + self.cash
        
        return {
            "total_value": total_value,
            "cash": self.cash,
            "cash_pct": self.cash / total_value if total_value > 0 else 0,
            "n_positions": len(self.positions),
            "largest_position_pct": max(self.position_values.values()) / total_value if self.position_values else 0,
            "positions": list(self.positions.keys())
        }
    
    def get_position_weights(self) -> pd.Series:
        """Get current position weights"""
        total = sum(self.position_values.values())
        if total == 0:
            return pd.Series()
        
        return pd.Series({
            symbol: value / total
            for symbol, value in self.position_values.items()
        })
    
    def get_portfolio_history(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame"""
        if not self._portfolio_history:
            return pd.DataFrame()
        
        records = []
        for state in self._portfolio_history:
            records.append({
                "date": state.date,
                "total_value": state.total_value,
                "cash": state.cash,
                "n_positions": len(state.weights[state.weights > 0]),
                "largest_weight": state.weights.max() if len(state.weights) > 0 else 0
            })
        
        return pd.DataFrame(records)
    
    def reset(self):
        """Reset portfolio to initial state"""
        self.cash = self.initial_capital
        self.positions = {}
        self.position_values = {}
        self._portfolio_history = []
        logger.info("Portfolio reset to initial state")
