"""
Factor Controller - 因子控制器
"""

from ..schema import FactorTestRequest, FactorTestResponse
from ...application.orchestrator import FactorResearchOrchestrator
from ...repository.tushare_repository import TushareRepository
from ...model.factor_definitions import get_factor_definition, list_factor_definitions
from ...model.alpha101_definitions import get_alpha101_definition, list_alpha101_definitions


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
        # 基础因子
        basic_factors = list_factor_definitions()
        # Alpha101 因子
        alpha101_factors = list_alpha101_definitions()
        
        all_factors = []
        
        # 添加基础因子
        for d in basic_factors:
            all_factors.append({
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "description": d.description,
                "type": "basic"
            })
        
        # 添加 Alpha101 因子
        for d in alpha101_factors:
            all_factors.append({
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "description": d.description,
                "type": "alpha101",
                "formula": d.formula
            })
        
        return {"factors": all_factors}
    
    async def get_factor_code(self, factor_id: str) -> dict:
        """获取因子代码"""
        # 先查找基础因子
        definition = get_factor_definition(factor_id)
        factor_type = "basic"
        
        # 如果没找到，查找 Alpha101 因子
        if definition is None:
            definition = get_alpha101_definition(factor_id)
            factor_type = "alpha101"
        
        if definition is None:
            return {
                "error": f"Factor {factor_id} not found",
                "code": None
            }
        
        result = {
            "id": definition.id,
            "name": definition.name,
            "category": definition.category,
            "description": definition.description,
            "code": definition.code,
            "parameters": definition.parameters,
            "references": definition.references,
            "type": factor_type
        }
        
        # Alpha101 特有字段
        if factor_type == "alpha101" and hasattr(definition, 'formula'):
            result["formula"] = definition.formula
        
        return result
