"""
Data Router - 数据路由
"""

from fastapi import APIRouter, Depends, Query
from ..controller import DataController

router = APIRouter(prefix="/data", tags=["data"])


def get_data_controller():
    return DataController()


@router.get("/stocks")
async def get_stocks(
    limit: int = Query(default=100, le=500),
    market: str = Query(default=None),
    controller: DataController = Depends(get_data_controller)
):
    """获取股票列表"""
    return await controller.get_stock_list(limit=limit, market=market)


@router.get("/stocks/{ts_code}/price")
async def get_stock_price(
    ts_code: str,
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None),
    controller: DataController = Depends(get_data_controller)
):
    """获取股票行情"""
    return await controller.get_stock_price(ts_code, start_date, end_date)


@router.get("/index/daily")
async def get_index_daily(
    ts_code: str = Query(default="000001.SH"),
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None),
    controller: DataController = Depends(get_data_controller)
):
    """获取指数日线数据"""
    return await controller.get_index_daily(ts_code, start_date, end_date)
