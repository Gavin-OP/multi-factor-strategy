"""
Signals - 信号模块

信号 = 多因子组合，是更高层次的投资策略
"""

from typing import Dict, List, Optional
import pandas as pd

from ..model.signal import Signal


class SignalStorage:
    """
    信号存储
    
    管理信号的注册、存储、查询
    """
    
    def __init__(self):
        self._signals: Dict[str, Signal] = {}
        self._values: Dict[str, pd.DataFrame] = {}
    
    def register(self, signal: Signal) -> None:
        """注册信号"""
        self._signals[signal.code] = signal
    
    def unregister(self, code: str) -> None:
        """注销信号"""
        self._signals.pop(code, None)
        self._values.pop(code, None)
    
    def get(self, code: str) -> Optional[Signal]:
        """获取信号"""
        return self._signals.get(code)
    
    def list_all(self) -> List[Signal]:
        """列出所有信号"""
        return list(self._signals.values())
    
    def save_values(self, code: str, values: pd.DataFrame) -> None:
        """保存信号值"""
        self._values[code] = values
    
    def get_values(self, code: str) -> Optional[pd.DataFrame]:
        """获取信号值"""
        return self._values.get(code)


# 全局单例
_storage: Optional[SignalStorage] = None


def get_storage() -> SignalStorage:
    """获取信号存储单例"""
    global _storage
    if _storage is None:
        _storage = SignalStorage()
    return _storage
