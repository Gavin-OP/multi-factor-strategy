"""
Data Controller - 数据控制器
"""

from ...repository.tushare_repository import TushareRepository


class DataController:
    """数据控制器"""
    
    def __init__(self):
        self.tushare_repo = TushareRepository()
    
    async def get_stock_list(self, limit: int = 100, market: str = None) -> dict:
        """获取股票列表"""
        stocks = self.tushare_repo.get_stock_list(market=market, limit=limit)
        
        return {
            "data": [
                {
                    "ts_code": s.ts_code,
                    "symbol": s.symbol,
                    "name": s.name,
                    "market": s.market
                }
                for s in stocks
            ],
            "total": len(stocks),
            "source": "tushare" if self.tushare_repo.is_available() else "mock"
        }
    
    async def get_stock_price(self, ts_code: str, start_date: str, end_date: str) -> dict:
        """获取股票行情"""
        prices = self.tushare_repo.get_daily_prices(ts_code, start_date, end_date)
        
        return {
            "code": ts_code,
            "data": [
                {
                    "trade_date": p.trade_date,
                    "open": p.open,
                    "high": p.high,
                    "low": p.low,
                    "close": p.close,
                    "vol": p.vol
                }
                for p in prices
            ],
            "source": "tushare" if self.tushare_repo.is_available() else "mock"
        }
    
    async def get_index_daily(self, ts_code: str, start_date: str, end_date: str) -> dict:
        """获取指数日线"""
        df = self.tushare_repo.get_index_daily(ts_code, start_date, end_date)
        
        return {
            "code": ts_code,
            "data": df.to_dict('records') if not df.empty else [],
            "source": "tushare" if self.tushare_repo.is_available() else "mock"
        }
    
    async def get_index_list(self) -> dict:
        """获取指数列表"""
        indices = self.tushare_repo.get_index_list()
        return {
            "data": indices,
            "source": "tushare" if self.tushare_repo.is_available() else "mock"
        }
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> dict:
        """搜索股票"""
        stocks = self.tushare_repo.search_stocks(keyword, limit)
        return {
            "data": [
                {
                    "ts_code": s.ts_code,
                    "symbol": s.symbol,
                    "name": s.name,
                    "market": s.market
                }
                for s in stocks
            ],
            "total": len(stocks),
            "source": "tushare" if self.tushare_repo.is_available() else "mock"
        }
