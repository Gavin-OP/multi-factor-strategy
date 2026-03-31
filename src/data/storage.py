"""
Data Storage - SQLAlchemy ORM for data persistence
"""

import pandas as pd
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, String, Float, DateTime, BigInteger,
    Index, UniqueConstraint, inspect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from loguru import logger
import configparser

Base = declarative_base()


class DailyPrice(Base):
    """Daily price data table"""
    __tablename__ = "daily_price"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    date = Column(DateTime, nullable=False, comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(BigInteger, comment="成交量")
    amount = Column(Float, comment="成交额")
    pct_change = Column(Float, comment="涨跌幅")
    turnover = Column(Float, comment="换手率")
    
    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_symbol_date"),
        Index("idx_date", "date"),
        Index("idx_symbol", "symbol"),
    )


class FactorValue(Base):
    """Factor value table"""
    __tablename__ = "factor_value"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment="股票代码")
    date = Column(DateTime, nullable=False, comment="交易日期")
    factor_name = Column(String(50), nullable=False, comment="因子名称")
    factor_value = Column(Float, comment="因子值")
    
    __table_args__ = (
        UniqueConstraint("symbol", "date", "factor_name", name="uq_symbol_date_factor"),
        Index("idx_factor_date", "date", "factor_name"),
    )


class FactorMetadata(Base):
    """Factor metadata table"""
    __tablename__ = "factor_metadata"
    
    factor_name = Column(String(50), primary_key=True, comment="因子名称")
    factor_category = Column(String(50), comment="因子分类")
    description = Column(String(500), comment="因子描述")
    ic_mean = Column(Float, comment="IC均值")
    ic_std = Column(Float, comment="IC标准差")
    icir = Column(Float, comment="ICIR")
    is_active = Column(String(1), default="Y", comment="是否启用")
    created_at = Column(DateTime, comment="创建时间")
    updated_at = Column(DateTime, comment="更新时间")


class DataStorage:
    """
    Data storage using SQLAlchemy
    
    Features:
    - ORM-based data persistence
    - Support for SQLite and PostgreSQL
    - Transaction management
    - Efficient batch operations
    """
    
    def __init__(self, config_path: str = "config/config.ini"):
        """
        Initialize data storage
        
        Args:
            config_path: Path to config file
        """
        self.config = self._load_config(config_path)
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
        logger.info("DataStorage initialized successfully")
    
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """Load configuration"""
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        return config
    
    def _create_engine(self):
        """Create SQLAlchemy engine"""
        driver = self.config.get("database", "driver", fallback="sqlite")
        
        if driver == "sqlite":
            db_path = self.config.get("database", "database", fallback="outputs/quant_factor.db")
            url = f"sqlite:///{db_path}"
        else:
            host = self.config.get("database", "host", fallback="localhost")
            port = self.config.get("database", "port", fallback="5432")
            database = self.config.get("database", "database")
            username = self.config.get("database", "username")
            password = self.config.get("database", "password")
            url = f"{driver}://{username}:{password}@{host}:{port}/{database}"
        
        return create_engine(url, echo=False, pool_pre_ping=True)
    
    def _create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def save_daily_data(self, df: pd.DataFrame, if_exists: str = "append"):
        """
        Save daily price data
        
        Args:
            df: DataFrame with daily price data
            if_exists: How to handle existing data ("append", "replace", "fail")
        """
        if df.empty:
            logger.warning("Empty DataFrame, skipping save")
            return
        
        # Ensure date is datetime
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        
        # Save to database
        df.to_sql(
            DailyPrice.__tablename__,
            self.engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=10000
        )
        
        logger.info(f"Saved {len(df)} rows to daily_price table")
    
    def load_daily_data(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load daily price data
        
        Args:
            symbol: Stock symbol (optional, loads all if None)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with daily price data
        """
        query = "SELECT * FROM daily_price WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY symbol, date"
        
        df = pd.read_sql(query, self.engine, params=params)
        
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        
        logger.info(f"Loaded {len(df)} rows from daily_price table")
        return df
    
    def save_factor_data(
        self,
        df: pd.DataFrame,
        factor_name: str,
        if_exists: str = "append"
    ):
        """
        Save factor values
        
        Args:
            df: DataFrame with columns [symbol, date, factor_value]
            factor_name: Name of the factor
            if_exists: How to handle existing data
        """
        df = df.copy()
        df["factor_name"] = factor_name
        df["date"] = pd.to_datetime(df["date"])
        
        df.to_sql(
            FactorValue.__tablename__,
            self.engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=10000
        )
        
        logger.info(f"Saved {len(df)} factor values for {factor_name}")
    
    def load_factor_data(
        self,
        factor_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load factor values
        
        Args:
            factor_name: Name of the factor
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with factor values
        """
        query = "SELECT * FROM factor_value WHERE factor_name = ?"
        params = [factor_name]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY symbol, date"
        
        df = pd.read_sql(query, self.engine, params=params)
        
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        
        return df
    
    def save_factor_metadata(
        self,
        factor_name: str,
        factor_category: str,
        description: str,
        ic_stats: dict
    ):
        """Save factor metadata"""
        with self.get_session() as session:
            from datetime import datetime
            
            metadata = session.query(FactorMetadata).filter_by(
                factor_name=factor_name
            ).first()
            
            if metadata:
                metadata.ic_mean = ic_stats.get("ic_mean")
                metadata.ic_std = ic_stats.get("ic_std")
                metadata.icir = ic_stats.get("icir")
                metadata.updated_at = datetime.now()
            else:
                metadata = FactorMetadata(
                    factor_name=factor_name,
                    factor_category=factor_category,
                    description=description,
                    ic_mean=ic_stats.get("ic_mean"),
                    ic_std=ic_stats.get("ic_std"),
                    icir=ic_stats.get("icir"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(metadata)
        
        logger.info(f"Saved metadata for factor: {factor_name}")
    
    def get_active_factors(self) -> List[str]:
        """Get list of active factors"""
        with self.get_session() as session:
            factors = session.query(FactorMetadata.factor_name).filter_by(
                is_active="Y"
            ).all()
            return [f[0] for f in factors]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
