"""
Backtest Engine Service - 回测引擎服务
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

from ..model.backtest import BacktestResult, PerformanceMetric, TradeRecord
from ..model.strategy import Portfolio, Position
from ..model.market import Price


class BacktestEngineService:
    """回测引擎服务"""
    
    def run_backtest(
        self,
        signals: List[Dict],
        price_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        initial_capital: float = 1000000.0,
        commission: float = 0.001,
        slippage: float = 0.001,
        top_n: int = 50,
    ) -> BacktestResult:
        """
        运行回测
        
        Args:
            signals: 信号列表 [{date, stock_code, signal_value}]
            price_data: 价格数据
            benchmark_data: 基准数据
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点
            top_n: 持仓数量
        
        Returns:
            回测结果
        """
        # 初始化
        capital = initial_capital
        portfolio = Portfolio(name="backtest", total_value=capital)
        
        trades = []
        nav_curve = []
        
        # 获取所有日期
        dates = sorted(price_data['trade_date'].unique())
        
        for i, date in enumerate(dates):
            # 获取当日信号
            day_signals = [s for s in signals if s.get('date') == date]
            
            if day_signals:
                # 按信号值排序，选取 top_n
                sorted_signals = sorted(day_signals, key=lambda x: x['signal_value'], reverse=True)
                selected_stocks = [s['stock_code'] for s in sorted_signals[:top_n]]
                
                # 调仓
                trades.extend(self._rebalance(
                    portfolio, selected_stocks, date, price_data, capital, commission, slippage
                ))
            
            # 计算净值
            nav = self._calculate_nav(portfolio, date, price_data, capital)
            benchmark_nav = self._get_benchmark_nav(benchmark_data, date)
            
            nav_curve.append({
                'date': date,
                'nav': nav,
                'benchmark': benchmark_nav
            })
            
            capital = nav
        
        # 计算绩效
        metrics = self._calculate_metrics(nav_curve, benchmark_data)
        
        return BacktestResult(
            strategy_code="backtest",
            start_date=dates[0] if dates else "",
            end_date=dates[-1] if dates else "",
            metrics=metrics,
            nav_curve=nav_curve,
            trades=trades,
            data_source="tushare"
        )
    
    def _rebalance(
        self,
        portfolio: Portfolio,
        selected_stocks: List[str],
        date: str,
        price_data: pd.DataFrame,
        capital: float,
        commission: float,
        slippage: float
    ) -> List[TradeRecord]:
        """调仓"""
        trades = []
        
        # 等权分配
        weight = 1.0 / len(selected_stocks) if selected_stocks else 0
        
        # 清仓
        for pos in portfolio.positions:
            trades.append(TradeRecord(
                date=date,
                stock_code=pos.stock_code,
                direction="sell",
                shares=pos.shares,
                price=pos.current_price,
                amount=pos.shares * pos.current_price,
                commission=pos.shares * pos.current_price * commission
            ))
        
        # 开仓
        portfolio.positions = []
        for stock_code in selected_stocks:
            day_price = price_data[
                (price_data['ts_code'] == stock_code) & 
                (price_data['trade_date'] == date)
            ]
            
            if not day_price.empty:
                price = float(day_price['close'].iloc[0]) * (1 + slippage)
                shares = (capital * weight) / price
                
                portfolio.positions.append(Position(
                    stock_code=stock_code,
                    shares=shares,
                    weight=weight,
                    entry_price=price,
                    current_price=price
                ))
                
                trades.append(TradeRecord(
                    date=date,
                    stock_code=stock_code,
                    direction="buy",
                    shares=shares,
                    price=price,
                    amount=shares * price,
                    commission=shares * price * commission
                ))
        
        return trades
    
    def _calculate_nav(
        self,
        portfolio: Portfolio,
        date: str,
        price_data: pd.DataFrame,
        capital: float
    ) -> float:
        """计算净值"""
        total_value = 0
        
        for pos in portfolio.positions:
            day_price = price_data[
                (price_data['ts_code'] == pos.stock_code) & 
                (price_data['trade_date'] == date)
            ]
            if not day_price.empty:
                pos.current_price = float(day_price['close'].iloc[0])
                total_value += pos.shares * pos.current_price
        
        return total_value
    
    def _get_benchmark_nav(self, benchmark_data: pd.DataFrame, date: str) -> float:
        """获取基准净值"""
        day_data = benchmark_data[benchmark_data['trade_date'] == date]
        if not day_data.empty:
            return float(day_data['close'].iloc[0])
        return 1.0
    
    def _calculate_metrics(
        self,
        nav_curve: List[Dict],
        benchmark_data: pd.DataFrame
    ) -> PerformanceMetric:
        """计算绩效指标"""
        if not nav_curve:
            return PerformanceMetric()
        
        navs = [d['nav'] for d in nav_curve]
        benchmarks = [d['benchmark'] for d in nav_curve]
        
        # 总收益
        total_return = navs[-1] / navs[0] - 1
        
        # 年化收益
        days = len(navs)
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
        
        # 收益率序列
        returns = pd.Series(navs).pct_change().dropna()
        
        # 波动率
        annual_volatility = float(returns.std() * np.sqrt(252)) if len(returns) > 0 else 0
        
        # 夏普比率
        sharpe_ratio = float(annual_return / annual_volatility) if annual_volatility > 0 else 0
        
        # 最大回撤
        nav_series = pd.Series(navs)
        rolling_max = nav_series.expanding().max()
        drawdown = (nav_series - rolling_max) / rolling_max
        max_drawdown = float(drawdown.min())
        
        # 胜率
        positive_days = sum(1 for r in returns if r > 0)
        win_rate = positive_days / len(returns) if len(returns) > 0 else 0
        
        return PerformanceMetric(
            total_return=total_return,
            annual_return=annual_return,
            annual_volatility=annual_volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
        )
    
    def generate_mock_backtest(self, top_n: int = 50) -> BacktestResult:
        """生成模拟回测结果"""
        np.random.seed(42)
        
        dates = pd.date_range(start="2024-01-01", periods=250, freq="B")
        nav_base = 1 + np.cumsum(np.random.randn(250) * 0.003)
        benchmark_base = 1 + np.cumsum(np.random.randn(250) * 0.002)
        
        nav_curve = [
            {"date": d.strftime("%Y-%m-%d"), "nav": float(nav), "benchmark": float(bench)}
            for d, nav, bench in zip(dates, nav_base, benchmark_base)
        ]
        
        rolling_max = np.maximum.accumulate(nav_base)
        drawdown = (nav_base - rolling_max) / rolling_max
        
        drawdown_curve = [
            {"date": d.strftime("%Y-%m-%d"), "drawdown": float(dd)}
            for d, dd in zip(dates, drawdown)
        ]
        
        monthly_returns = [
            {"month": f"{i+1}月", "return": float((np.random.rand() - 0.4) * 0.1)}
            for i in range(12)
        ]
        
        holdings = [
            {
                "code": f"{600000 + i:06d}",
                "name": f"股票{i+1}",
                "weight": float(np.random.rand() * 0.05),
                "return": float((np.random.rand() - 0.5) * 0.3)
            }
            for i in range(top_n)
        ]
        
        return BacktestResult(
            strategy_code="mock",
            start_date="2024-01-01",
            end_date="2024-12-31",
            metrics=PerformanceMetric(
                total_return=float(nav_base[-1] / nav_base[0] - 1),
                annual_return=0.25,
                excess_return=0.18,
                annual_volatility=0.18,
                sharpe_ratio=1.38,
                information_ratio=1.12,
                max_drawdown=float(drawdown.min()),
                win_rate=0.58,
                profit_loss_ratio=1.45,
                beta=0.75,
                alpha=0.08,
                tracking_error=0.12,
                downside_risk=0.10,
                avg_holding_period=15,
                turnover_rate=0.45,
            ),
            nav_curve=nav_curve,
            drawdown_curve=drawdown_curve,
            monthly_returns=monthly_returns,
            yearly_returns=[
                {"year": "2023", "return": 0.28, "benchmark": 0.12},
                {"year": "2024", "return": 0.22, "benchmark": 0.10},
            ],
            holdings=holdings,
            data_source="mock"
        )
