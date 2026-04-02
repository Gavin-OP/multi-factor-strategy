"""
Configuration
"""

import os
from typing import Optional


class Settings:
    """全局配置"""
    
    # Tushare
    TUSHARE_TOKEN: str = os.environ.get("TUSHARE_TOKEN", "")
    
    # API
    API_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "https://gavin-op.github.io",
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    # 因子配置
    DEFAULT_QUANTILES: int = 5
    DEFAULT_FORWARD_PERIOD: int = 5
    
    # 回测配置
    DEFAULT_TOP_N: int = 50
    DEFAULT_COMMISSION: float = 0.001
    DEFAULT_SLIPPAGE: float = 0.001


settings = Settings()
