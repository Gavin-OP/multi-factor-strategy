"""
Factor Registry - 因子注册中心

管理所有因子的注册、查询、实例化
"""

from typing import Dict, List, Type, Optional
from .base import Factor, FactorMeta


class FactorRegistry:
    """
    因子注册中心
    
    使用方式：
        # 注册因子
        @FactorRegistry.register
        class MyFactor(Factor):
            ...
        
        # 获取因子
        factor = FactorRegistry.get("my_factor")
        values = factor.compute(data)
        
        # 列出所有因子
        all_factors = FactorRegistry.list_all()
    """
    
    _factors: Dict[str, Type[Factor]] = {}
    _categories: Dict[str, List[str]] = {}
    
    @classmethod
    def register(cls, factor_class: Type[Factor]) -> Type[Factor]:
        """
        注册因子
        
        用作装饰器：
            @FactorRegistry.register
            class MyFactor(Factor):
                ...
        """
        if not factor_class.id:
            raise ValueError(f"Factor {factor_class.__name__} must define 'id'")
        
        cls._factors[factor_class.id] = factor_class
        
        # 按类别索引
        category = factor_class.category or "other"
        if category not in cls._categories:
            cls._categories[category] = []
        cls._categories[category].append(factor_class.id)
        
        return factor_class
    
    @classmethod
    def get(cls, factor_id: str) -> Optional[Factor]:
        """获取因子实例"""
        factor_class = cls._factors.get(factor_id)
        if factor_class:
            return factor_class()
        return None
    
    @classmethod
    def get_meta(cls, factor_id: str) -> Optional[FactorMeta]:
        """获取因子元信息"""
        factor_class = cls._factors.get(factor_id)
        if factor_class:
            return factor_class.get_meta()
        return None
    
    @classmethod
    def list_all(cls) -> List[FactorMeta]:
        """列出所有因子元信息"""
        return [f.get_meta() for f in cls._factors.values()]
    
    @classmethod
    def list_by_category(cls, category: str) -> List[FactorMeta]:
        """按类别列出因子"""
        factor_ids = cls._categories.get(category, [])
        return [cls._factors[fid].get_meta() for fid in factor_ids]
    
    @classmethod
    def list_categories(cls) -> List[str]:
        """列出所有类别"""
        return list(cls._categories.keys())
    
    @classmethod
    def count(cls) -> int:
        """返回已注册因子数量"""
        return len(cls._factors)


# 便捷函数
def register_factor(factor_class: Type[Factor]) -> Type[Factor]:
    """注册因子的便捷函数"""
    return FactorRegistry.register(factor_class)


def get_factor(factor_id: str) -> Optional[Factor]:
    """获取因子实例"""
    return FactorRegistry.get(factor_id)


def list_factors() -> List[FactorMeta]:
    """列出所有因子"""
    return FactorRegistry.list_all()
