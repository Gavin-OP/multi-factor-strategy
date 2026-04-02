"""
Signal Library - 信号库
统一管理信号的注册、存储、查询
"""

from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

from ..model.signal import Signal


class SignalLibrary:
    """
    信号库
    
    职责：
    1. 信号注册管理
    2. 信号值存储
    3. 信号查询
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
_signal_library: Optional[SignalLibrary] = None


def get_signal_library() -> SignalLibrary:
    """获取信号库单例"""
    global _signal_library
    if _signal_library is None:
        _signal_library = SignalLibrary()
    return _signal_library
