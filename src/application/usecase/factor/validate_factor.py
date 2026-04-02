"""
Validate Factor UseCase - 验证因子用例
"""

import numpy as np
import pandas as pd
from typing import Dict, List

from ....model.factor import FactorMeta, FactorResult
from ....repository.tushare_repository import TushareRepository
from ....service.factor.factor_compute_service import FactorComputeService
from ....service.factor.factor_validate_service import FactorValidateService
from ....service.factor.factor_analyze_service import FactorAnalyzeService


class ValidateFactorUseCase:
    """验证因子用例"""
    
    def __init__(
        self,
        tushare_repo: TushareRepository,
        compute_service: FactorComputeService,
        validate_service: FactorValidateService,
        analyze_service: FactorAnalyzeService
    ):
        self.tushare_repo = tushare_repo
        self.compute_service = compute_service
        self.validate_service = validate_service
        self.analyze_service = analyze_service
    
    def execute(
        self,
        factor_type: str,
        start_date: str,
        end_date: str,
        quantiles: int = 5,
        forward_period: int = 5
    ) -> FactorResult:
        """
        执行因子验证
        
        Returns:
            因子验证结果
        """
        # 尝试使用真实数据
        if self.tushare_repo.is_available():
            try:
                return self._validate_with_real_data(
                    factor_type, start_date, end_date, quantiles, forward_period
                )
            except Exception as e:
                print(f"Real data validation failed: {e}")
        
        # 使用模拟数据
        return self._validate_with_mock_data(factor_type, quantiles)
    
    def _validate_with_real_data(
        self,
        factor_type: str,
        start_date: str,
        end_date: str,
        quantiles: int,
        forward_period: int
    ) -> FactorResult:
        """使用真实数据验证"""
        # 获取股票列表
        stocks = self.tushare_repo.get_stock_list(limit=50)
        stock_codes = [s.ts_code for s in stocks]
        
        # 获取价格数据
        price_data = self.tushare_repo.get_daily_multiple(stock_codes, start_date, end_date)
        
        if price_data.empty:
            return self._validate_with_mock_data(factor_type, quantiles)
        
        # 计算因子值
        factor_values = self.compute_service.compute_factor_values(price_data, factor_type)
        
        # 计算未来收益
        forward_returns = self._calculate_forward_returns(price_data, forward_period)
        
        # 验证因子
        ic, icir, t_stat = self.validate_service.validate_factor(
            factor_values, forward_returns, quantiles
        )
        
        # 计算分位数收益
        quantile_returns = self.validate_service.calculate_quantile_returns(
            factor_values, forward_returns, quantiles
        )
        
        # 计算单调性
        monotonicity = self.validate_service.calculate_monotonicity(quantile_returns)
        
        # 计算评级
        grade, score, is_effective = self.validate_service.calculate_grade(
            ic, icir, monotonicity
        )
        
        # 识别优劣势
        strengths, weaknesses = self.analyze_service.identify_strengths_weaknesses(
            ic, icir, monotonicity, 0.35
        )
        
        # 创建因子元信息
        factor = FactorMeta(
            code=factor_type,
            name=factor_type,
            category=self._get_category(factor_type),
            ic_mean=ic,
            icir=icir,
            grade=grade,
            score=score,
            is_effective=is_effective,
            strengths=strengths,
            weaknesses=weaknesses
        )
        
        return FactorResult(
            factor=factor,
            quantile_returns=quantile_returns,
            data_source="tushare"
        )
    
    def _calculate_forward_returns(
        self,
        price_data: pd.DataFrame,
        forward_period: int
    ) -> Dict[str, float]:
        """计算未来收益"""
        forward_returns = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            
            if len(stock_data) >= forward_period:
                try:
                    start_price = stock_data['close'].iloc[0]
                    end_price = stock_data['close'].iloc[forward_period]
                    forward_returns[ts_code] = float(end_price / start_price - 1)
                except:
                    pass
        
        return forward_returns
    
    def _validate_with_mock_data(self, factor_type: str, quantiles: int) -> FactorResult:
        """使用模拟数据验证"""
        np.random.seed(42)
        
        # 模拟 IC 序列
        ic_series = [
            {"date": f"2024-{str(i%12+1).zfill(2)}", "ic": float(np.random.randn() * 0.1)}
            for i in range(24)
        ]
        
        # 模拟分位数收益
        quantile_returns = [
            {"quantile": i, "return": float(0.05 + i * 0.03 + np.random.randn() * 0.01), "sharpe": float(0.5 + i * 0.2)}
            for i in range(1, quantiles + 1)
        ]
        
        # 模拟衰减曲线
        decay_curve = [{"lag": i, "ic": float(0.05 * np.exp(-i * 0.1))} for i in range(20)]
        
        # 分析 IC
        ic_stats = self.analyze_service.analyze_ic(ic_series)
        
        # 计算单调性
        monotonicity = self.validate_service.calculate_monotonicity(quantile_returns)
        
        # 计算评级
        grade, score, is_effective = self.validate_service.calculate_grade(
            ic_stats['ic_mean'], ic_stats['icir'], monotonicity
        )
        
        # 识别优劣势
        strengths, weaknesses = self.analyze_service.identify_strengths_weaknesses(
            ic_stats['ic_mean'], ic_stats['icir'], monotonicity, 0.35
        )
        
        factor = FactorMeta(
            code=factor_type,
            name=factor_type,
            category=self._get_category(factor_type),
            ic_mean=ic_stats['ic_mean'],
            ic_std=ic_stats['ic_std'],
            icir=ic_stats['icir'],
            ic_positive_ratio=ic_stats['ic_positive_ratio'],
            spread_return=quantile_returns[-1]['return'] - quantile_returns[0]['return'] if quantile_returns else 0,
            monotonicity=monotonicity,
            grade=grade,
            score=score,
            is_effective=is_effective,
            strengths=strengths,
            weaknesses=weaknesses
        )
        
        return FactorResult(
            factor=factor,
            ic_series=ic_series,
            quantile_returns=quantile_returns,
            decay_curve=decay_curve,
            data_source="mock"
        )
    
    def _get_category(self, factor_type: str) -> str:
        """获取因子类别"""
        if factor_type.startswith('momentum'):
            return '动量因子'
        elif factor_type.startswith('value'):
            return '价值因子'
        elif factor_type.startswith('quality'):
            return '质量因子'
        elif factor_type.startswith('volatility'):
            return '波动率因子'
        elif factor_type.startswith('liquidity'):
            return '流动性因子'
        else:
            return '其他因子'
