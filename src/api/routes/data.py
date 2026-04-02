"""
Data Routes - 数据接口
"""

from fastapi import APIRouter, Query
import pandas as pd
import numpy as np
import os

router = APIRouter(prefix="/api", tags=["data"])

# Tushare token
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")


@router.get("/stocks")
async def get_stocks(
    limit: int = Query(default=100, le=500),
    market: str = Query(default="主板")
):
    """获取股票列表 - 使用 Tushare 真实数据"""
    if TUSHARE_TOKEN:
        try:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()
            
            # 获取真实股票列表
            df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
            
            if market and 'market' in df.columns:
                df = df[df['market'] == market]
            
            return {
                "data": df.head(limit).to_dict(orient="records"),
                "total": len(df),
                "source": "tushare"
            }
        except Exception as e:
            return {
                "data": [],
                "total": 0,
                "source": "error",
                "error": str(e)
            }
    
    # Mock data fallback
    stocks = [
        {"ts_code": f"{600000+i:06d}.SH", "symbol": f"{600000+i:06d}", "name": f"股票{i+1}", "market": market}
        for i in range(limit)
    ]
    return {"data": stocks, "total": limit, "source": "mock"}


@router.get("/stocks/{ts_code}/price")
async def get_stock_price(
    ts_code: str,
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None)
):
    """获取股票行情 - 使用 Tushare 真实数据"""
    from datetime import datetime
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    if TUSHARE_TOKEN:
        try:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()
            
            # 获取真实日线数据
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df.empty:
                return {"code": ts_code, "data": [], "source": "tushare", "message": "No data found"}
            
            df = df.sort_values('trade_date')
            
            return {
                "code": ts_code,
                "data": df.to_dict(orient="records"),
                "source": "tushare"
            }
        except Exception as e:
            return {"code": ts_code, "data": [], "source": "error", "error": str(e)}
    
    # Mock data
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n = min(len(dates), 100)
    
    base_price = 10.0
    returns = np.random.randn(n) * 0.02
    close = base_price * np.exp(np.cumsum(returns))
    
    data = [{
        'ts_code': ts_code,
        'trade_date': dates[i].strftime('%Y%m%d'),
        'open': float(close[i] * (1 + np.random.randn() * 0.01)),
        'high': float(close[i] * 1.02),
        'low': float(close[i] * 0.98),
        'close': float(close[i]),
        'vol': int(np.random.randint(1000000, 10000000)),
    } for i in range(n)]
    
    return {"code": ts_code, "data": data, "source": "mock"}


@router.get("/index/daily")
async def get_index_daily(
    ts_code: str = Query(default="000001.SH", description="指数代码，默认上证指数"),
    start_date: str = Query(default="20230101"),
    end_date: str = Query(default=None)
):
    """获取指数日线 - 使用 Tushare 真实数据"""
    from datetime import datetime
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    if TUSHARE_TOKEN:
        try:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()
            
            # 获取真实指数数据
            df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df.empty:
                return {"code": ts_code, "data": [], "source": "tushare", "message": "No data found"}
            
            df = df.sort_values('trade_date')
            
            return {
                "code": ts_code,
                "data": df.to_dict(orient="records"),
                "source": "tushare"
            }
        except Exception as e:
            return {"code": ts_code, "data": [], "source": "error", "error": str(e)}
    
    # Mock data
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n = min(len(dates), 100)
    
    base = 3000.0
    close = base * np.exp(np.cumsum(np.random.randn(n) * 0.01))
    
    data = [{
        'trade_date': dates[i].strftime('%Y%m%d'),
        'close': float(close[i]),
    } for i in range(n)]
    
    return {"code": ts_code, "data": data, "source": "mock"}
