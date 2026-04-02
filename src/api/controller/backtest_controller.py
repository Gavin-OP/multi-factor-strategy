"""
Backtest Controller - 回测控制器
"""

from ..schema import BacktestRequest, BacktestResponse
from ...application.orchestrator import StrategyBacktestOrchestrator
from ...repository.tushare_repository import TushareRepository


class BacktestController:
    """回测控制器"""
    
    def __init__(self):
        tushare_repo = TushareRepository()
        self.orchestrator = StrategyBacktestOrchestrator(tushare_repo)
    
    async def run_backtest(self, request: BacktestRequest) -> dict:
        """运行回测"""
        result = self.orchestrator.run_backtest(
            factors=request.factors,
            start_date=request.start_date,
            end_date=request.end_date,
            weight_method=request.weight_method,
            top_n=request.top_n,
            commission=request.commission,
            slippage=request.slippage
        )
        
        metrics = result.metrics
        
        return {
            "totalReturn": metrics.total_return,
            "annualReturn": metrics.annual_return,
            "excessReturn": metrics.excess_return,
            "annualVolatility": metrics.annual_volatility,
            "sharpeRatio": metrics.sharpe_ratio,
            "informationRatio": metrics.information_ratio,
            "maxDrawdown": metrics.max_drawdown,
            "winRate": metrics.win_rate,
            "profitLossRatio": metrics.profit_loss_ratio,
            "beta": metrics.beta,
            "alpha": metrics.alpha,
            "trackingError": metrics.tracking_error,
            "downsideRisk": metrics.downside_risk,
            "avgHoldingPeriod": metrics.avg_holding_period,
            "turnoverRate": metrics.turnover_rate,
            "navCurve": result.nav_curve,
            "drawdownCurve": result.drawdown_curve,
            "monthlyReturns": result.monthly_returns,
            "yearlyReturns": result.yearly_returns,
            "holdings": result.holdings,
            "dataSource": result.data_source
        }
