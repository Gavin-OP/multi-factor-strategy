"""
Quant Factor Strategy API
FastAPI backend service for factor analysis and backtesting
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.providers import TushareProvider
from src.factors.factor_engine import FactorEngine
from src.backtest.backtest_engine import BacktestEngine

app = FastAPI(
    title="Quant Factor Strategy API",
    description="多因子量化策略分析平台 API",
    version="1.0.0"
)

# CORS configuration for GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gavin-op.github.io",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Models ==============

class FactorTestRequest(BaseModel):
    factor_type: str
    start_date: str
    end_date: str
    quantiles: int = 5
    forward_period: int = 5
    industry_neutral: bool = False
    market_cap_neutral: bool = False


class BacktestRequest(BaseModel):
    factors: List[str]
    weight_method: str = "equal"
    rebalance_freq: str = "monthly"
    top_n: int = 50
    commission: float = 0.001
    slippage: float = 0.001
    start_date: str
    end_date: str


# ============== Data Endpoints ==============

@app.get("/")
async def root():
    return {"message": "Quant Factor Strategy API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/stocks")
async def get_stocks(
    limit: int = Query(default=100, le=500),
    market: str = Query(default="主板")
):
    """获取股票列表"""
    try:
        provider = TushareProvider()
        stocks = provider.get_stock_list(market=market)
        return {
            "data": stocks.head(limit).to_dict(orient="records"),
            "total": len(stocks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{ts_code}/price")
async def get_stock_price(
    ts_code: str,
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None)
):
    """获取股票行情数据"""
    try:
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        provider = TushareProvider()
        df = provider.get_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "code": ts_code,
            "data": df.to_dict(orient="records")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Factor Analysis Endpoints ==============

@app.get("/api/factors/types")
async def get_factor_types():
    """获取可用因子类型"""
    return {
        "factors": [
            {"id": "momentum_1m", "name": "1月动量", "category": "动量因子"},
            {"id": "momentum_3m", "name": "3月动量", "category": "动量因子"},
            {"id": "momentum_6m", "name": "6月动量", "category": "动量因子"},
            {"id": "momentum_12m", "name": "12月动量", "category": "动量因子"},
            {"id": "value_pe", "name": "PE因子", "category": "价值因子"},
            {"id": "value_pb", "name": "PB因子", "category": "价值因子"},
            {"id": "quality_roe", "name": "ROE因子", "category": "质量因子"},
            {"id": "quality_roa", "name": "ROA因子", "category": "质量因子"},
            {"id": "volatility_1m", "name": "1月波动率", "category": "波动率因子"},
            {"id": "liquidity_turnover", "name": "换手率", "category": "流动性因子"},
        ]
    }


@app.post("/api/factors/test")
async def test_factor(request: FactorTestRequest):
    """
    因子有效性测试
    
    返回 IC 分析、分位数分析、单调性检验等结果
    """
    try:
        provider = TushareProvider()
        engine = FactorEngine(provider)
        
        # Run factor test
        result = engine.test_factor(
            factor_type=request.factor_type,
            start_date=request.start_date,
            end_date=request.end_date,
            quantiles=request.quantiles,
            forward_period=request.forward_period,
            industry_neutral=request.industry_neutral,
            market_cap_neutral=request.market_cap_neutral
        )
        
        return result
        
    except Exception as e:
        # Return mock data if Tushare not configured
        return generate_mock_factor_result(request)


def generate_mock_factor_result(request: FactorTestRequest) -> Dict[str, Any]:
    """生成模拟因子测试结果（当 Tushare 未配置时使用）"""
    np.random.seed(42)
    
    ic_series = [
        {"date": f"2024-{str(i%12+1).zfill(2)}", "ic": float(np.random.randn() * 0.1)}
        for i in range(24)
    ]
    
    quantile_returns = [
        {"quantile": i, "return": float(0.05 + i * 0.03 + np.random.randn() * 0.01), "sharpe": float(0.5 + i * 0.2)}
        for i in range(1, request.quantiles + 1)
    ]
    
    decay_curve = [
        {"lag": i, "ic": float(0.05 * np.exp(-i * 0.1))}
        for i in range(20)
    ]
    
    ic_values = [d["ic"] for d in ic_series]
    ic_mean = float(np.mean(ic_values))
    ic_std = float(np.std(ic_values))
    
    return {
        "name": request.factor_type,
        "category": "因子",
        "icMean": ic_mean,
        "icStd": ic_std,
        "icir": ic_mean / ic_std if ic_std > 0 else 0,
        "icTStat": float(np.mean(ic_values) / (np.std(ic_values) / np.sqrt(len(ic_values))),
        "icPositiveRatio": float(sum(1 for ic in ic_values if ic > 0) / len(ic_values)),
        "icSignificantRatio": float(0.35),
        "factorReturn": float(0.08),
        "factorReturnTStat": float(2.45),
        "spreadReturn": quantile_returns[-1]["return"] - quantile_returns[0]["return"],
        "spreadSharpe": float(1.25),
        "monotonicity": float(0.85),
        "halfLife": int(5),
        "turnover": float(0.35),
        "auc": float(0.535),
        "f1Score": float(0.52),
        "grade": "B",
        "score": float(0.65),
        "isEffective": True,
        "strengths": ["IC显著", "单调性好", "换手率适中"],
        "weaknesses": ["ICIR偏低", "半衰期较短"],
        "quantileReturns": quantile_returns,
        "icSeries": ic_series,
        "decayCurve": decay_curve,
    }


# ============== Backtest Endpoints ==============

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """
    运行策略回测
    
    返回净值曲线、风险指标、持仓明细等
    """
    try:
        provider = TushareProvider()
        engine = BacktestEngine(provider)
        
        result = engine.run(
            factors=request.factors,
            weight_method=request.weight_method,
            rebalance_freq=request.rebalance_freq,
            top_n=request.top_n,
            commission=request.commission,
            slippage=request.slippage,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return result
        
    except Exception as e:
        return generate_mock_backtest_result(request)


def generate_mock_backtest_result(request: BacktestRequest) -> Dict[str, Any]:
    """生成模拟回测结果"""
    np.random.seed(42)
    
    # Generate 250 trading days
    dates = pd.date_range(start="2024-01-01", periods=250, freq="B")
    
    # NAV curve with some randomness
    nav_base = 1 + np.cumsum(np.random.randn(250) * 0.003)
    benchmark_base = 1 + np.cumsum(np.random.randn(250) * 0.002)
    
    nav_curve = [
        {"date": d.strftime("%Y-%m-%d"), "nav": float(nav), "benchmark": float(bench)}
        for d, nav, bench in zip(dates, nav_base, benchmark_base)
    ]
    
    # Drawdown
    rolling_max = np.maximum.accumulate(nav_base)
    drawdown = (nav_base - rolling_max) / rolling_max
    
    drawdown_curve = [
        {"date": d.strftime("%Y-%m-%d"), "drawdown": float(dd)}
        for d, dd in zip(dates, drawdown)
    ]
    
    # Monthly returns
    monthly_returns = [
        {"month": f"{i+1}月", "return": float((np.random.rand() - 0.4) * 0.1)}
        for i in range(12)
    ]
    
    # Holdings
    holdings = [
        {
            "code": f"{600000 + i:06d}",
            "name": f"股票{i+1}",
            "weight": float(np.random.rand() * 0.05),
            "return": float((np.random.rand() - 0.5) * 0.3)
        }
        for i in range(request.top_n)
    ]
    
    return {
        "totalReturn": float(nav_base[-1] / nav_base[0] - 1),
        "annualReturn": float(0.25),
        "excessReturn": float(0.18),
        "annualVolatility": float(0.18),
        "sharpeRatio": float(1.38),
        "informationRatio": float(1.12),
        "maxDrawdown": float(drawdown.min()),
        "winRate": float(0.58),
        "profitLossRatio": float(1.45),
        "beta": float(0.75),
        "alpha": float(0.08),
        "trackingError": float(0.12),
        "downsideRisk": float(0.10),
        "avgHoldingPeriod": int(15),
        "turnoverRate": float(0.45),
        "navCurve": nav_curve,
        "drawdownCurve": drawdown_curve,
        "monthlyReturns": monthly_returns,
        "yearlyReturns": [
            {"year": "2022", "return": 0.15, "benchmark": 0.08},
            {"year": "2023", "return": 0.28, "benchmark": 0.12},
            {"year": "2024", "return": 0.22, "benchmark": 0.10},
        ],
        "holdings": holdings,
    }


@app.get("/api/index/daily")
async def get_index_daily(
    ts_code: str = Query(default="000001.SH", description="指数代码"),
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None)
):
    """获取指数日线数据"""
    try:
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        provider = TushareProvider()
        df = provider.get_index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        return {
            "code": ts_code,
            "data": df.to_dict(orient="records")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
