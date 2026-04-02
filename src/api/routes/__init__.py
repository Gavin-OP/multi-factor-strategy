"""
Routes __init__
"""

from .data import router as data_router
from .factors import router as factors_router
from .backtest import router as backtest_router

__all__ = ['data_router', 'factors_router', 'backtest_router']
