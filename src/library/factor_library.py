"""
Factor Library - 因子库
统一管理因子的注册、存储、查询
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

from ..model.factor import FactorMeta, FactorValue


class FactorLibrary:
    """
    因子库
    
    职责：
    1. 因子注册管理
    2. 因子值存储
    3. 因子元信息管理
    4. 因子查询和筛选
    """
    
    def __init__(self):
        self._meta: Dict[str, FactorMeta] = {}
        self._values: Dict[str, pd.DataFrame] = {}
    
    # ========== 注册管理 ==========
    
    def register(self, factor: FactorMeta) -> None:
        """注册因子"""
        factor.updated_at = datetime.now()
        self._meta[factor.code] = factor
    
    def unregister(self, code: str) -> None:
        """注销因子"""
        self._meta.pop(code, None)
        self._values.pop(code, None)
    
    def get(self, code: str) -> Optional[FactorMeta]:
        """获取因子元信息"""
        return self._meta.get(code)
    
    def exists(self, code: str) -> bool:
        """检查因子是否存在"""
        return code in self._meta
    
    # ========== 列表查询 ==========
    
    def list_all(self) -> List[FactorMeta]:
        """列出所有因子"""
        return list(self._meta.values())
    
    def list_effective(self) -> List[FactorMeta]:
        """列出有效因子"""
        return [f for f in self._meta.values() if f.is_effective]
    
    def list_by_category(self, category: str) -> List[FactorMeta]:
        """按类别列出"""
        return [f for f in self._meta.values() if f.category == category]
    
    def list_by_grade(self, grade: str) -> List[FactorMeta]:
        """按评级列出"""
        return [f for f in self._meta.values() if f.grade == grade]
    
    def list_active(self) -> List[FactorMeta]:
        """列出活跃因子"""
        return [f for f in self._meta.values() if f.status == "active"]
    
    # ========== 值存储 ==========
    
    def save_values(self, code: str, values: pd.DataFrame) -> None:
        """保存因子值"""
        self._values[code] = values
    
    def get_values(self, code: str) -> Optional[pd.DataFrame]:
        """获取因子值"""
        return self._values.get(code)
    
    def get_values_on_date(self, code: str, date: str) -> Optional[pd.Series]:
        """获取某日的因子值"""
        df = self._values.get(code)
        if df is not None and date in df.index:
            return df.loc[date]
        return None
    
    # ========== 状态管理 ==========
    
    def activate(self, code: str) -> None:
        """激活因子"""
        if code in self._meta:
            self._meta[code].status = "active"
    
    def deprecate(self, code: str) -> None:
        """废弃因子"""
        if code in self._meta:
            self._meta[code].status = "deprecated"
    
    def update_score(self, code: str, score: float, grade: str, is_effective: bool) -> None:
        """更新评分"""
        if code in self._meta:
            factor = self._meta[code]
            factor.score = score
            factor.grade = grade
            factor.is_effective = is_effective
            factor.updated_at = datetime.now()
    
    # ========== 统计 ==========
    
    def stats(self) -> dict:
        """统计信息"""
        factors = list(self._meta.values())
        categories = set(f.category for f in factors)
        
        return {
            "total": len(factors),
            "effective": sum(1 for f in factors if f.is_effective),
            "active": sum(1 for f in factors if f.status == "active"),
            "deprecated": sum(1 for f in factors if f.status == "deprecated"),
            "by_grade": {
                grade: sum(1 for f in factors if f.grade == grade)
                for grade in set(f.grade for f in factors)
            },
            "by_category": {
                cat: sum(1 for f in factors if f.category == cat)
                for cat in categories
            }
        }


# 全局单例
_factor_library: Optional[FactorLibrary] = None


def get_factor_library() -> FactorLibrary:
    """获取因子库单例"""
    global _factor_library
    if _factor_library is None:
        _factor_library = FactorLibrary()
    return _factor_library
