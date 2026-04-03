"""
Factor Base - 因子基类

所有因子的抽象基类，定义统一接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np


@dataclass
class FactorMeta:
    """因子元信息"""
    id: str                              # 因子唯一标识
    name: str                            # 因子名称
    category: str                        # 类别：momentum/value/quality...
    description: str = ""                # 描述
    formula: str = ""                    # 计算公式（文本描述）
    parameters: Dict[str, Any] = field(default_factory=dict)  # 参数
    references: List[str] = field(default_factory=list)       # 参考文献
    author: str = ""                     # 作者
    tags: List[str] = field(default_factory=list)             # 标签


class Factor(ABC):
    """
    因子抽象基类
    
    所有因子必须继承此类并实现 compute 方法
    """
    
    # 子类必须定义的类属性
    id: str = ""
    name: str = ""
    category: str = ""
    description: str = ""
    formula: str = ""
    parameters: Dict[str, Any] = {}
    references: List[str] = []
    
    @classmethod
    def get_meta(cls) -> FactorMeta:
        """获取因子元信息"""
        return FactorMeta(
            id=cls.id,
            name=cls.name,
            category=cls.category,
            description=cls.description,
            formula=cls.formula,
            parameters=cls.parameters,
            references=cls.references,
        )
    
    @abstractmethod
    def compute(self, data: pd.DataFrame) -> pd.Series:
        """
        计算因子值
        
        Args:
            data: 包含 OHLCV 等列的 DataFrame，按股票分组
            
        Returns:
            因子值 Series，index 为股票代码
        """
        pass
    
    def __repr__(self):
        return f"<Factor {self.id}: {self.name}>"


class FactorGroup:
    """
    因子族基类
    
    用于组织一类因子，如 Alpha101
    """
    
    group_name: str = ""
    group_description: str = ""
    
    @classmethod
    @abstractmethod
    def get_factors(cls) -> List[type]:
        """返回该族所有因子类"""
        pass
