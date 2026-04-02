"""
Signal Generation Service - 信号生成服务
"""

import numpy as np
import pandas as pd
from typing import Dict, List

from ...model.signal import Signal, TradingSignal


class SignalGenerationService:
    """信号生成服务"""
    
    def generate_from_factors(
        self,
        factor_values: Dict[str, Dict[str, float]],
        method: str = "equal_weight"
    ) -> Dict[str, float]:
        """
        从因子生成信号
        
        Args:
            factor_values: {factor_code: {stock_code: value}}
            method: 组合方法
        
        Returns:
            {stock_code: signal_value}
        """
        if not factor_values:
            return {}
        
        # 获取所有股票
        all_stocks = set()
        for fv in factor_values.values():
            all_stocks.update(fv.keys())
        
        signals = {}
        
        for stock in all_stocks:
            values = []
            for fv in factor_values.values():
                if stock in fv:
                    values.append(fv[stock])
            
            if values:
                if method == "equal_weight":
                    signals[stock] = float(np.mean(values))
                elif method == "ic_weight":
                    # TODO: 实现 IC 加权
                    signals[stock] = float(np.mean(values))
                else:
                    signals[stock] = float(np.mean(values))
        
        return signals
    
    def normalize_signals(self, signals: Dict[str, float]) -> Dict[str, float]:
        """标准化信号"""
        if not signals:
            return {}
        
        values = np.array(list(signals.values()))
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return {k: 0.0 for k in signals}
        
        return {k: float((v - mean) / std) for k, v in signals.items()}
    
    def filter_signals(
        self,
        signals: Dict[str, float],
        top_n: int = 50,
        threshold: float = None
    ) -> Dict[str, float]:
        """筛选信号"""
        if threshold:
            signals = {k: v for k, v in signals.items() if abs(v) > threshold}
        
        sorted_signals = sorted(signals.items(), key=lambda x: abs(x[1]), reverse=True)
        return dict(sorted_signals[:top_n])
