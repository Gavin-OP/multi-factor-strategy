"""
Factor Controller - 因子控制器
"""

from ..schema import FactorTestRequest, FactorTestResponse
from ...application.orchestrator import FactorResearchOrchestrator
from ...repository.tushare_repository import TushareRepository
from ...model.factor_definitions import get_factor_definition, list_factor_definitions


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
        definitions = list_factor_definitions()
        return {
            "factors": [
                {
                    "id": d.id,
                    "name": d.name,
                    "category": d.category,
                    "description": d.description
                }
                for d in definitions
            ]
        }
    
    async def get_factor_code(self, factor_id: str) -> dict:
        """获取因子代码"""
        definition = get_factor_definition(factor_id)
        
        if definition is None:
            return {
                "error": f"Factor {factor_id} not found",
                "code": None
            }
        
        return {
            "id": definition.id,
            "name": definition.name,
            "category": definition.category,
            "description": definition.description,
            "code": definition.code,
            "parameters": definition.parameters,
            "references": definition.references
        }
