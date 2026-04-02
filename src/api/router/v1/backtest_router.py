"""
Backtest Router - 回测路由
"""

from fastapi import APIRouter, Depends
from ..schema import BacktestRequest
from ..controller import BacktestController

router = APIRouter(prefix="/backtest", tags=["backtest"])


def get_backtest_controller():
    return BacktestController()


@router.post("/run")
async def run_backtest(
    request: BacktestRequest,
    controller: BacktestController = Depends(get_backtest_controller)
):
    """运行策略回测"""
    return await controller.run_backtest(request)
