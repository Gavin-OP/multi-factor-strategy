"""
API Routers v1
"""

from fastapi import APIRouter
from .factor_router import router as factor_router
from .backtest_router import router as backtest_router
from .data_router import router as data_router

api_router = APIRouter()
api_router.include_router(factor_router)
api_router.include_router(backtest_router)
api_router.include_router(data_router)

__all__ = ['api_router']
