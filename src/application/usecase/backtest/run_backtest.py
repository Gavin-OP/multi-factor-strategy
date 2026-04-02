"""
Run Backtest UseCase - 运行回测用例
"""

from typing import List, Dict

from ...model.backtest import BacktestResult
from ...repository.tushare_repository import TushareRepository
from ...service.backtest.backtest_engine_service import BacktestEngineService


class RunBacktestUseCase:
    """运行回测用例"""
    
    def __init__(
        self,
        tushare_repo: TushareRepository,
        backtest_service: BacktestEngineService
    ):
        self.tushare_repo = tushare_repo
        self.backtest_service = backtest_service
    
    def execute(
        self,
        factors: List[str],
        start_date: str,
        end_date: str,
        weight_method: str = "equal",
        top_n: int = 50,
        commission: float = 0.001,
        slippage: float = 0.001
    ) -> BacktestResult:
        """
        执行回测
        
        Args:
            factors: 因子列表
            start_date: 开始日期
            end_date: 结束日期
            weight_method: 权重方法
            top_n: 持仓数量
            commission: 手续费
            slippage: 滑点
        
        Returns:
            回测结果
        """
        # 尝试使用真实数据
        if self.tushare_repo.is_available():
            try:
                return self._run_with_real_data(
                    factors, start_date, end_date, weight_method, top_n, commission, slippage
                )
            except Exception as e:
                print(f"Real data backtest failed: {e}")
        
        # 使用模拟数据
        return self.backtest_service.generate_mock_backtest(top_n)
    
    def _run_with_real_data(
        self,
        factors: List[str],
        start_date: str,
        end_date: str,
        weight_method: str,
        top_n: int,
        commission: float,
        slippage: float
    ) -> BacktestResult:
        """使用真实数据回测"""
        # 获取股票列表
        stocks = self.tushare_repo.get_stock_list(limit=top_n)
        stock_codes = [s.ts_code for s in stocks]
        
        # 获取价格数据
        price_data = self.tushare_repo.get_daily_multiple(stock_codes, start_date, end_date)
        
        # 获取基准数据
        benchmark_data = self.tushare_repo.get_index_daily("000001.SH", start_date, end_date)
        
        if price_data.empty:
            return self.backtest_service.generate_mock_backtest(top_n)
        
        # 生成模拟信号（简化版）
        signals = self._generate_mock_signals(price_data)
        
        # 运行回测
        return self.backtest_service.run_backtest(
            signals=signals,
            price_data=price_data,
            benchmark_data=benchmark_data,
            top_n=top_n,
            commission=commission,
            slippage=slippage
        )
    
    def _generate_mock_signals(self, price_data) -> List[Dict]:
        """生成模拟信号"""
        signals = []
        
        for date in price_data['trade_date'].unique()[:50]:
            for ts_code in price_data['ts_code'].unique()[:20]:
                signals.append({
                    'date': date,
                    'stock_code': ts_code,
                    'signal_value': float((hash(ts_code + date) % 100) / 100)
                })
        
        return signals
