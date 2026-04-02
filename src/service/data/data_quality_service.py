"""
Data Quality Service - 数据质量服务
"""

import pandas as pd
from typing import List, Dict


class DataQualityService:
    """数据质量服务"""
    
    def check_missing(self, df: pd.DataFrame) -> Dict:
        """检查缺失值"""
        return {
            'missing_count': int(df.isnull().sum().sum()),
            'missing_ratio': float(df.isnull().sum().sum() / df.size),
            'columns_with_missing': df.columns[df.isnull().any()].tolist()
        }
    
    def check_outliers(self, df: pd.DataFrame, columns: List[str] = None) -> Dict:
        """检查异常值"""
        if columns is None:
            columns = df.select_dtypes(include=['float64', 'int64']).columns
        
        outliers = {}
        for col in columns:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                
                outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()
                outliers[col] = int(outlier_count)
        
        return outliers
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据"""
        df = df.copy()
        
        # 填充缺失值
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
