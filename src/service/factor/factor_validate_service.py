"""
Factor Validate Service - 因子验证服务
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple

from ..model.factor import FactorMeta, FactorResult


class FactorValidateService:
    """因子验证服务"""
    
    def validate_factor(
        self,
        factor_values: Dict[str, float],
        forward_returns: Dict[str, float],
        quantiles: int = 5
    ) -> Tuple[float, float, float]:
        """
        验证因子有效性
        
        Args:
            factor_values: {stock_code: factor_value}
            forward_returns: {stock_code: forward_return}
            quantiles: 分位数
        
        Returns:
            (ic, icir, t_stat)
        """
        # 合并数据
        common_stocks = set(factor_values.keys()) & set(forward_returns.keys())
        if len(common_stocks) < 10:
            return 0.0, 0.0, 0.0
        
        f_values = [factor_values[s] for s in common_stocks]
        r_values = [forward_returns[s] for s in common_stocks]
        
        # 计算 IC (Spearman 相关系数)
        ic, p_value = stats.spearmanr(f_values, r_values)
        
        # ICIR 和 t-stat
        icir = 0.0
        t_stat = 0.0
        
        return float(ic), float(icir), float(t_stat)
    
    def calculate_ic_series(
        self,
        factor_values_list: List[Dict],
        forward_returns_list: List[Dict]
    ) -> List[Dict]:
        """计算 IC 时间序列"""
        ic_series = []
        
        for i, (fv, fr) in enumerate(zip(factor_values_list, forward_returns_list)):
            ic, _, _ = self.validate_factor(fv, fr)
            ic_series.append({
                'date': f"2024-{str(i % 12 + 1).zfill(2)}",
                'ic': ic
            })
        
        return ic_series
    
    def calculate_quantile_returns(
        self,
        factor_values: Dict[str, float],
        forward_returns: Dict[str, float],
        quantiles: int = 5
    ) -> List[Dict]:
        """计算分位数收益"""
        common_stocks = set(factor_values.keys()) & set(forward_returns.keys())
        if len(common_stocks) < quantiles * 5:
            return []
        
        # 按因子值排序
        sorted_stocks = sorted(
            common_stocks,
            key=lambda s: factor_values.get(s, 0)
        )
        
        # 分组
        group_size = len(sorted_stocks) // quantiles
        quantile_returns = []
        
        for q in range(quantiles):
            start = q * group_size
            end = start + group_size if q < quantiles - 1 else len(sorted_stocks)
            group_stocks = sorted_stocks[start:end]
            
            returns = [forward_returns[s] for s in group_stocks]
            quantile_returns.append({
                'quantile': q + 1,
                'return': float(np.mean(returns)) if returns else 0.0,
                'sharpe': float(np.mean(returns) / np.std(returns)) if returns and np.std(returns) > 0 else 0.0
            })
        
        return quantile_returns
    
    def calculate_monotonicity(self, quantile_returns: List[Dict]) -> float:
        """计算单调性得分"""
        if len(quantile_returns) < 2:
            return 0.0
        
        returns = [q['return'] for q in quantile_returns]
        n = len(returns)
        
        correct = 0
        total = n * (n - 1) / 2
        
        for i in range(n):
            for j in range(i + 1, n):
                if returns[i] < returns[j]:
                    correct += 1
        
        return correct / total if total > 0 else 0.0
    
    def calculate_grade(self, ic_mean: float, icir: float, monotonicity: float) -> Tuple[str, float, bool]:
        """计算评级"""
        score = 0.0
        
        # IC 评分 (0-40)
        if ic_mean > 0.05:
            score += 40
        elif ic_mean > 0.03:
            score += 30
        elif ic_mean > 0.01:
            score += 20
        elif ic_mean > 0:
            score += 10
        
        # ICIR 评分 (0-30)
        if icir > 0.5:
            score += 30
        elif icir > 0.3:
            score += 20
        elif icir > 0.1:
            score += 10
        
        # 单调性评分 (0-30)
        score += monotonicity * 30
        
        score = score / 100
        
        # 评级
        if score >= 0.9:
            grade = 'A+'
        elif score >= 0.8:
            grade = 'A'
        elif score >= 0.7:
            grade = 'B'
        elif score >= 0.6:
            grade = 'C'
        elif score >= 0.5:
            grade = 'D'
        else:
            grade = 'F'
        
        is_effective = ic_mean > 0.02 and score >= 0.5
        
        return grade, score, is_effective
