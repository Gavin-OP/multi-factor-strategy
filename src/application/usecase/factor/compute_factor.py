"""
Compute Factor UseCase - 计算因子用例
"""

from typing import Dict, Optional
import pandas as pd

from ....model.factor import FactorMeta, FactorValue
from ....repository.tushare_repository import TushareRepository
from ....service.factor.factor_compute_service import FactorComputeService


class ComputeFactorUseCase:
    """计算因子用例"""
    
    def __init__(
        self,
        tushare_repo: TushareRepository,
        compute_service: FactorComputeService
    ):
        self.tushare_repo = tushare_repo
        self.compute_service = compute_service
    
    def execute(
        self,
        factor_type: str,
        start_date: str,
        end_date: str,
        stock_codes: Optional[list] = None
    ) -> Dict[str, float]:
        """
        执行因子计算
        
        Args:
            factor_type: 因子类型 (momentum_1m, volatility_1m 等)
            start_date: 开始日期
            end_date: 结束日期
            stock_codes: 股票代码列表（可选）
        
        Returns:
            {stock_code: factor_value}
        """
        # 获取股票列表
        if stock_codes is None:
            stocks = self.tushare_repo.get_stock_list(limit=50)
            stock_codes = [s.ts_code for s in stocks]
        
        # 获取价格数据
        price_data = self.tushare_repo.get_daily_multiple(stock_codes, start_date, end_date)
        
        if price_data.empty:
            return {}
        
        # 计算因子值
        factor_values = self.compute_service.compute_factor_values(
            price_data,
            factor_type
        )
        
        return factor_values
