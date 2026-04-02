"""
Signal Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Signal:
    """信号模型"""
    code: str                           # 信号代码
    name: str                           # 信号名称
    factors: List[str] = field(default_factory=list)  # 组成因子
    method: str = ""                    # 组合方法
    
    # 信号值
    values: Dict[str, float] = field(default_factory=dict)  # {stock_code: signal_value}
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    date: str = ""


@dataclass
class TradingSignal:
    """交易信号"""
    date: str
    stock_code: str
    signal_value: float
    direction: int                      # 1: 买入, -1: 卖出, 0: 持有
    confidence: float = 0.0
