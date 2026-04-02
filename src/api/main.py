"""
Quant Factor Strategy API
FastAPI backend service for factor analysis and backtesting
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from .routes import data_router, factors_router, backtest_router

# Create FastAPI app
app = FastAPI(
    title="Quant Factor Strategy API",
    description="多因子量化策略分析平台 API - 支持 Tushare 真实数据",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Include routers
app.include_router(data_router)
app.include_router(factors_router)
app.include_router(backtest_router)


@app.get("/")
async def root():
    """API 根路径"""
    tushare_configured = bool(os.environ.get("TUSHARE_TOKEN"))
    return {
        "message": "Quant Factor Strategy API",
        "version": "1.0.0",
        "tushare_configured": tushare_configured,
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    tushare_configured = bool(os.environ.get("TUSHARE_TOKEN"))
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tushare": "configured" if tushare_configured else "not_configured"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
