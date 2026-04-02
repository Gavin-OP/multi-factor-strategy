"""
Market Data Models
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Stock:
    """股票模型"""
    ts_code: str              # 股票代码
    symbol: str               # 代码
    name: str                 # 名称
    area: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    list_date: Optional[str] = None


@dataclass
class Price:
    """价格模型"""
    ts_code: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    pre_close: float
    change: float
    pct_chg: float
    vol: float
    amount: float


@dataclass
class Index:
    """指数模型"""
    ts_code: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    vol: float
    amount: float
