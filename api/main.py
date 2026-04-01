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
import os

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

# Tushare token
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")

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
        if TUSHARE_TOKEN:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()
            df = pro.stock_basic(exchange='', list_status='L')
            return {
                "data": df.head(limit).to_dict(orient="records"),
                "total": len(df)
            }
    except Exception as e:
        pass
    
    # Mock data
    stocks = [
        {"ts_code": f"{600000+i:06d}.SH", "symbol": f"{600000+i:06d}", "name": f"股票{i+1}"}
        for i in range(limit)
    ]
    return {"data": stocks, "total": limit}


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
    """因子有效性测试"""
    return generate_mock_factor_result(request)


def generate_mock_factor_result(request: FactorTestRequest) -> Dict[str, Any]:
    """生成模拟因子测试结果"""
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
        "icTStat": float(np.mean(ic_values) / (np.std(ic_values) / np.sqrt(len(ic_values)))),
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
    """运行策略回测"""
    return generate_mock_backtest_result(request)


def generate_mock_backtest_result(request: BacktestRequest) -> Dict[str, Any]:
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
