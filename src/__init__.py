"""
Quant Factor Strategy Package

A professional quantitative factor strategy framework.
"""

__version__ = "1.0.0"
__author__ = "Quant Research Team"

from src.data import DataManager, DataFetcher, DataCache
from src.factors import FactorEngine, FactorBase
from src.signals import SignalGenerator
from src.portfolio import PortfolioConstructor
from src.backtest import BacktestEngine
from src.risk import RiskManager
