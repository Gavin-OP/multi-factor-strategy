"""
Factors - 因子模块

包含所有因子的定义、注册和存储
"""

from .base import Factor, FactorMeta, FactorGroup
from .registry import FactorRegistry, register_factor, get_factor, list_factors
from .storage import FactorStorage, get_storage


# 导入所有因子模块，触发注册
from . import momentum
from . import value
from . import quality
from . import volatility
from . import liquidity
from . import alpha101


__all__ = [
    # 基类
    'Factor',
    'FactorMeta', 
    'FactorGroup',
    # 注册中心
    'FactorRegistry',
    'register_factor',
    'get_factor',
    'list_factors',
    # 存储
    'FactorStorage',
    'get_storage',
]
