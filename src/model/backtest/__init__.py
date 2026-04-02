"""
Backtest Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TradeRecord:
    """交易记录"""
    date: str
    stock_code: str
    direction: str              # buy/sell
    shares: float
    price: float
    amount: float
    commission: float


@dataclass
class PerformanceMetric:
    """绩效指标"""
    total_return: float = 0.0
    annual_return: float = 0.0
    excess_return: float = 0.0
    annual_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    information_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_loss_ratio: float = 0.0
    beta: float = 0.0
    alpha: float = 0.0
    tracking_error: float = 0.0
    downside_risk: float = 0.0
    avg_holding_period: int = 0
    turnover_rate: float = 0.0


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_code: str
    start_date: str
    end_date: str
    
    # 绩效
    metrics: PerformanceMetric = field(default_factory=PerformanceMetric)
    
    # 时间序列
    nav_curve: List[Dict] = field(default_factory=list)
    drawdown_curve: List[Dict] = field(default_factory=list)
    monthly_returns: List[Dict] = field(default_factory=list)
    yearly_returns: List[Dict] = field(default_factory=list)
    
    # 交易
    trades: List[TradeRecord] = field(default_factory=list)
    holdings: List[Dict] = field(default_factory=list)
    
    # 元数据
    data_source: str = "tushare"
    created_at: datetime = field(default_factory=datetime.now)
