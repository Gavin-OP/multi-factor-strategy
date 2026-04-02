"""
Strategy Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Position:
    """持仓"""
    stock_code: str
    shares: float
    weight: float
    entry_price: float
    current_price: float = 0.0
    pnl: float = 0.0


@dataclass
class Portfolio:
    """组合"""
    name: str
    positions: List[Position] = field(default_factory=list)
    total_value: float = 0.0
    cash: float = 0.0
    
    def get_weights(self) -> Dict[str, float]:
        return {p.stock_code: p.weight for p in self.positions}


@dataclass
class RebalancePlan:
    """再平衡计划"""
    date: str
    trades: List[Dict] = field(default_factory=list)
    turnover: float = 0.0
    commission: float = 0.0


@dataclass
class Strategy:
    """策略"""
    code: str
    name: str
    factors: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    
    # 配置
    rebalance_freq: str = "monthly"
    top_n: int = 50
    weight_method: str = "equal"
    
    # 状态
    portfolio: Optional[Portfolio] = None
    created_at: datetime = field(default_factory=datetime.now)
