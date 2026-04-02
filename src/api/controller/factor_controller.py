"""
Factor Controller - 因子控制器
"""

from ..schema import FactorTestRequest, FactorTestResponse
from ...application.orchestrator import FactorResearchOrchestrator
from ...repository.tushare_repository import TushareRepository


class FactorController:
    """因子控制器"""
    
    def __init__(self):
        tushare_repo = TushareRepository()
        self.orchestrator = FactorResearchOrchestrator(tushare_repo)
    
    async def test_factor(self, request: FactorTestRequest) -> dict:
        """测试因子"""
        result = self.orchestrator.research_factor(
            factor_type=request.factor_type,
            start_date=request.start_date,
            end_date=request.end_date,
            quantiles=request.quantiles,
            forward_period=request.forward_period
        )
        
        factor = result.factor
        
        return {
            "name": factor.name,
            "category": factor.category,
            "icMean": factor.ic_mean,
            "icStd": factor.ic_std,
            "icir": factor.icir,
            "icTStat": factor.ic_t_stat,
            "icPositiveRatio": factor.ic_positive_ratio,
            "icSignificantRatio": 0.35,
            "spreadReturn": factor.spread_return,
            "spreadSharpe": factor.spread_sharpe,
            "monotonicity": factor.monotonicity,
            "halfLife": factor.half_life,
            "turnover": factor.turnover,
            "grade": factor.grade,
            "score": factor.score,
            "isEffective": factor.is_effective,
            "strengths": factor.strengths,
            "weaknesses": factor.weaknesses,
            "quantileReturns": result.quantile_returns,
            "icSeries": result.ic_series,
            "decayCurve": result.decay_curve,
            "dataSource": result.data_source
        }
    
    async def get_factor_types(self) -> dict:
        """获取因子类型列表"""
        return {
            "factors": [
                {"id": "momentum_1m", "name": "1月动量", "category": "动量因子"},
                {"id": "momentum_3m", "name": "3月动量", "category": "动量因子"},
                {"id": "momentum_6m", "name": "6月动量", "category": "动量因子"},
                {"id": "momentum_12m", "name": "12月动量", "category": "动量因子"},
                {"id": "value_pe", "name": "PE因子", "category": "价值因子"},
                {"id": "value_pb", "name": "PB因子", "category": "价值因子"},
                {"id": "quality_roe", "name": "ROE因子", "category": "质量因子"},
                {"id": "quality_roa", "name": "ROA因子", "category": "质量因子"},
                {"id": "volatility_1m", "name": "1月波动率", "category": "波动率因子"},
                {"id": "liquidity_turnover", "name": "换手率", "category": "流动性因子"},
            ]
        }
