"""
Factor Analyze Service - 因子分析服务
"""

import numpy as np
from typing import List, Dict

from ..model.factor import FactorMeta


class FactorAnalyzeService:
    """因子分析服务"""
    
    def analyze_ic(self, ic_series: List[Dict]) -> Dict:
        """分析 IC 统计特征"""
        ic_values = [d['ic'] for d in ic_series]
        
        return {
            'ic_mean': float(np.mean(ic_values)),
            'ic_std': float(np.std(ic_values)),
            'icir': float(np.mean(ic_values) / np.std(ic_values)) if np.std(ic_values) > 0 else 0.0,
            'ic_positive_ratio': float(sum(1 for ic in ic_values if ic > 0) / len(ic_values)),
            'ic_significant_ratio': float(sum(1 for ic in ic_values if abs(ic) > 0.02) / len(ic_values)),
        }
    
    def analyze_decay(self, ic_series: List[Dict], max_lag: int = 20) -> List[Dict]:
        """分析 IC 衰减"""
        ic_mean = np.mean([d['ic'] for d in ic_series]) if ic_series else 0.05
        
        decay_curve = []
        for lag in range(max_lag):
            decay_curve.append({
                'lag': lag,
                'ic': float(abs(ic_mean) * np.exp(-lag * 0.1))
            })
        
        return decay_curve
    
    def calculate_half_life(self, decay_curve: List[Dict]) -> int:
        """计算半衰期"""
        if not decay_curve:
            return 5
        
        initial_ic = abs(decay_curve[0]['ic'])
        if initial_ic == 0:
            return 5
        
        half_ic = initial_ic / 2
        
        for d in decay_curve:
            if abs(d['ic']) <= half_ic:
                return d['lag']
        
        return len(decay_curve)
    
    def identify_strengths_weaknesses(
        self,
        ic_mean: float,
        icir: float,
        monotonicity: float,
        turnover: float
    ) -> tuple:
        """识别优劣势"""
        strengths = []
        weaknesses = []
        
        if ic_mean > 0.03:
            strengths.append("IC 显著")
        elif ic_mean < 0.01:
            weaknesses.append("IC 不显著")
        
        if icir > 0.3:
            strengths.append("ICIR 较高")
        elif icir < 0.1:
            weaknesses.append("ICIR 偏低")
        
        if monotonicity > 0.8:
            strengths.append("单调性好")
        elif monotonicity < 0.5:
            weaknesses.append("单调性差")
        
        if 0.1 < turnover < 0.5:
            strengths.append("换手率适中")
        elif turnover > 0.7:
            weaknesses.append("换手率过高")
        elif turnover < 0.1:
            weaknesses.append("换手率过低")
        
        return strengths, weaknesses
