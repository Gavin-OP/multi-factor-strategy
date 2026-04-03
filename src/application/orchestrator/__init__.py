"""
Application Orchestrators
"""

from typing import Optional
from ..usecase.factor import ValidateFactorUseCase
from ..usecase.backtest import RunBacktestUseCase
from ...repository.tushare_repository import TushareRepository
from ...service.factor.factor_compute_service import FactorComputeService
from ...service.factor.factor_validate_service import FactorValidateService
from ...service.factor.factor_analyze_service import FactorAnalyzeService
from ...service.backtest.backtest_engine_service import BacktestEngineService
from ...factors import get_storage
from ...model.factor import FactorResult
from ...model.backtest import BacktestResult


class FactorResearchOrchestrator:
    """
    因子研究编排器
    
    协调因子计算、验证、分析的完整流程
    """
    
    def __init__(self, tushare_repo: Optional[TushareRepository] = None):
        self.tushare_repo = tushare_repo or TushareRepository()
        
        # 初始化服务
        self.compute_service = FactorComputeService()
        self.validate_service = FactorValidateService()
        self.analyze_service = FactorAnalyzeService()
        self.backtest_service = BacktestEngineService()
        
        # 初始化用例
        self.validate_factor_usecase = ValidateFactorUseCase(
            self.tushare_repo,
            self.compute_service,
            self.validate_service,
            self.analyze_service
        )
        
        # 因子存储
        self.factor_storage = get_storage()
    
    def research_factor(
        self,
        factor_type: str,
        start_date: str,
        end_date: str,
        quantiles: int = 5,
        forward_period: int = 5,
        register: bool = True
    ) -> FactorResult:
        """
        完整的因子研究流程
        
        1. 验证因子
        2. 注册到因子库
        """
        # 验证因子
        result = self.validate_factor_usecase.execute(
            factor_type=factor_type,
            start_date=start_date,
            end_date=end_date,
            quantiles=quantiles,
            forward_period=forward_period
        )
        
        # 注册到因子存储
        if register and result.factor.is_effective:
            self.factor_storage.register_meta(result.factor)
        
        return result


class StrategyBacktestOrchestrator:
    """
    策略回测编排器
    
    协调信号生成、回测的完整流程
    """
    
    def __init__(self, tushare_repo: Optional[TushareRepository] = None):
        self.tushare_repo = tushare_repo or TushareRepository()
        self.backtest_service = BacktestEngineService()
        
        self.run_backtest_usecase = RunBacktestUseCase(
            self.tushare_repo,
            self.backtest_service
        )
    
    def run_backtest(
        self,
        factors: list,
        start_date: str,
        end_date: str,
        weight_method: str = "equal",
        top_n: int = 50,
        commission: float = 0.001,
        slippage: float = 0.001
    ) -> BacktestResult:
        """运行策略回测"""
        return self.run_backtest_usecase.execute(
            factors=factors,
            start_date=start_date,
            end_date=end_date,
            weight_method=weight_method,
            top_n=top_n,
            commission=commission,
            slippage=slippage
        )
