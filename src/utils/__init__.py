"""
Utilities
"""

from datetime import datetime, timedelta
from typing import List


def date_range(start_date: str, end_date: str) -> List[str]:
    """生成日期范围"""
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    
    return dates


def format_return(value: float) -> str:
    """格式化收益率"""
    return f"{value * 100:.2f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """格式化数字"""
    return f"{value:.{decimals}f}"
