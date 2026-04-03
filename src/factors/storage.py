"""
Factor Storage - 因子存储

管理因子值的存储、查询、持久化
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

from .base import FactorMeta


class FactorStorage:
    """
    因子存储
    
    职责：
    1. 因子值存储（内存/文件/数据库）
    2. 因子值查询
    3. 因子值持久化
    """
    
    def __init__(self):
        self._values: Dict[str, pd.DataFrame] = {}  # {factor_id: DataFrame}
        self._meta: Dict[str, FactorMeta] = {}       # {factor_id: FactorMeta}
    
    # ========== 元信息管理 ==========
    
    def register_meta(self, meta: FactorMeta) -> None:
        """注册因子元信息"""
        self._meta[meta.id] = meta
    
    def get_meta(self, factor_id: str) -> Optional[FactorMeta]:
        """获取因子元信息"""
        return self._meta.get(factor_id)
    
    def list_metas(self) -> List[FactorMeta]:
        """列出所有因子元信息"""
        return list(self._meta.values())
    
    def update_score(self, factor_id: str, score: float, grade: str, is_effective: bool) -> None:
        """更新因子评分"""
        if factor_id in self._meta:
            meta = self._meta[factor_id]
            meta.score = score
            meta.grade = grade
            meta.is_effective = is_effective
    
    # ========== 值存储 ==========
    
    def save(self, factor_id: str, values: pd.DataFrame) -> None:
        """保存因子值"""
        self._values[factor_id] = values
    
    def get(self, factor_id: str) -> Optional[pd.DataFrame]:
        """获取因子值"""
        return self._values.get(factor_id)
    
    def get_on_date(self, factor_id: str, date: str) -> Optional[pd.Series]:
        """获取某日的因子值"""
        df = self._values.get(factor_id)
        if df is not None and date in df.index:
            return df.loc[date]
        return None
    
    def exists(self, factor_id: str) -> bool:
        """检查因子值是否存在"""
        return factor_id in self._values
    
    def delete(self, factor_id: str) -> None:
        """删除因子值"""
        self._values.pop(factor_id, None)
    
    # ========== 查询 ==========
    
    def list_effective(self) -> List[FactorMeta]:
        """列出有效因子"""
        return [m for m in self._meta.values() if m.is_effective]
    
    def list_by_category(self, category: str) -> List[FactorMeta]:
        """按类别列出"""
        return [m for m in self._meta.values() if m.category == category]
    
    def list_by_grade(self, grade: str) -> List[FactorMeta]:
        """按评级列出"""
        return [m for m in self._meta.values() if m.grade == grade]
    
    # ========== 统计 ==========
    
    def stats(self) -> dict:
        """统计信息"""
        metas = list(self._meta.values())
        return {
            "total": len(metas),
            "effective": sum(1 for m in metas if m.is_effective),
            "stored": len(self._values),
            "by_grade": {
                grade: sum(1 for m in metas if m.grade == grade)
                for grade in set(m.grade for m in metas)
            },
            "by_category": {
                cat: sum(1 for m in metas if m.category == cat)
                for cat in set(m.category for m in metas)
            }
        }


# 全局单例
_storage: Optional[FactorStorage] = None


def get_storage() -> FactorStorage:
    """获取因子存储单例"""
    global _storage
    if _storage is None:
        _storage = FactorStorage()
    return _storage
