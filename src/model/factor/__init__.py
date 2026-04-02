"""
Factor Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any


@dataclass
class FactorMeta:
    """因子元信息"""
    code: str                           # 因子代码
    name: str                           # 因子名称
    category: str                       # 类别：momentum/value/quality...
    formula: str = ""                   # 计算公式
    parameters: Dict = field(default_factory=dict)
    
    # 验证结果
    ic_mean: float = 0.0
    ic_std: float = 0.0
    icir: float = 0.0
    ic_t_stat: float = 0.0
    ic_positive_ratio: float = 0.0
    spread_return: float = 0.0
    spread_sharpe: float = 0.0
    monotonicity: float = 0.0
    half_life: int = 0
    turnover: float = 0.0
    
    # 评分
    grade: str = "F"
    score: float = 0.0
    is_effective: bool = False
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    tags: List[str] = field(default_factory=list)
    status: str = "active"              # active/deprecated/testing
    
    # 优劣势
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class FactorValue:
    """因子值"""
    factor_code: str
    date: str
    values: Dict[str, float]            # {stock_code: factor_value}


@dataclass
class FactorResult:
    """因子验证结果"""
    factor: FactorMeta
    
    # 时间序列数据
    ic_series: List[Dict] = field(default_factory=list)
    quantile_returns: List[Dict] = field(default_factory=list)
    decay_curve: List[Dict] = field(default_factory=list)
    
    # 数据来源
    data_source: str = "tushare"
