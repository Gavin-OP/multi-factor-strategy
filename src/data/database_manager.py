"""
Database Manager - 统一数据库管理

支持三种部署方式:
1. 本地 SQLite (开发/测试)
2. 本地 PostgreSQL (生产)
3. 云数据库 Supabase/Neon/Xata

三个数据库:
- stock_db: 股票数据
- factor_db: 因子数据  
- backtest_db: 回测数据
"""

import os
from typing import Optional, Dict, Any
from loguru import logger
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, Boolean, DECIMAL, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import uuid

# ============================================
# 数据库配置
# ============================================

DATABASE_CONFIGS = {
    # 本地开发 SQLite
    "local_sqlite": {
        "stock_db": "sqlite:///./outputs/db/stock.db",
        "factor_db": "sqlite:///./outputs/db/factor.db",
        "backtest_db": "sqlite:///./outputs/db/backtest.db"
    },
    
    # 本地 PostgreSQL
    "local_postgres": {
        "stock_db": "postgresql://quant:quant123@localhost:5432/stock_db",
        "factor_db": "postgresql://quant:quant123@localhost:5432/factor_db",
        "backtest_db": "postgresql://quant:quant123@localhost:5432/backtest_db"
    },
    
    # Supabase (推荐用于 stock_db)
    "supabase": {
        "stock_db": os.environ.get("SUPABASE_STOCK_DB_URL", ""),
        "factor_db": os.environ.get("SUPABASE_FACTOR_DB_URL", ""),
        "backtest_db": os.environ.get("SUPABASE_BACKTEST_DB_URL", "")
    },
    
    # Neon (推荐用于 factor_db)
    "neon": {
        "factor_db": os.environ.get("NEON_DB_URL", "")
    },
    
    # Xata (推荐用于 backtest_db)
    "xata": {
        "backtest_db": os.environ.get("XATA_DB_URL", "")
    }
}


class DatabaseManager:
    """
    统一数据库管理器
    
    Features:
    - 多数据库支持 (stock_db, factor_db, backtest_db)
    - 多部署方式 (SQLite, PostgreSQL, Supabase, Neon, Xata)
    - 自动建表
    - 连接池管理
    """
    
    def __init__(
        self,
        mode: str = "local_sqlite",
        custom_urls: Optional[Dict[str, str]] = None
    ):
        """
        初始化数据库管理器
        
        Args:
            mode: 部署模式
            custom_urls: 自定义数据库URL
        """
        self.mode = mode
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
        
        # 获取数据库URL
        if custom_urls:
            self.db_urls = custom_urls
        else:
            self.db_urls = DATABASE_CONFIGS.get(mode, DATABASE_CONFIGS["local_sqlite"])
        
        # 初始化数据库
        self._init_databases()
        
        logger.info(f"DatabaseManager initialized: mode={mode}, dbs={list(self.db_urls.keys())}")
    
    def _init_databases(self):
        """初始化所有数据库"""
        for db_name, db_url in self.db_urls.items():
            if not db_url:
                continue
            
            try:
                # 创建引擎
                engine = create_engine(
                    db_url,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,
                    echo=False
                )
                
                # 创建会话工厂
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                
                self.engines[db_name] = engine
                self.sessions[db_name] = SessionLocal
                
                logger.info(f"✓ {db_name} initialized")
                
            except Exception as e:
                logger.error(f"✗ {db_name} failed: {e}")
    
    def create_tables(self):
        """创建所有表"""
        # Stock DB tables
        self._create_stock_tables()
        
        # Factor DB tables
        self._create_factor_tables()
        
        # Backtest DB tables
        self._create_backtest_tables()
        
        logger.info("All tables created")
    
    def _create_stock_tables(self):
        """创建股票数据库表"""
        if "stock_db" not in self.engines:
            return
        
        engine = self.engines["stock_db"]
        Base = declarative_base()
        
        class Stock(Base):
            __tablename__ = "stocks"
            
            symbol = Column(String(20), primary_key=True)
            name = Column(String(100))
            exchange = Column(String(20))
            industry = Column(String(50))
            sector = Column(String(50))
            list_date = Column(DateTime)
            market_cap = Column(DECIMAL(20, 2))
            status = Column(String(10), default="L")
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        class StockDaily(Base):
            __tablename__ = "stock_daily"
            __table_args__ = (
                UniqueConstraint("symbol", "trade_date", name="uq_symbol_date"),
                Index("idx_stock_daily_symbol", "symbol"),
                Index("idx_stock_daily_date", "trade_date"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            symbol = Column(String(20), nullable=False)
            trade_date = Column(DateTime, nullable=False)
            open = Column(DECIMAL(12, 4))
            high = Column(DECIMAL(12, 4))
            low = Column(DECIMAL(12, 4))
            close = Column(DECIMAL(12, 4))
            volume = Column(BigInteger)
            amount = Column(DECIMAL(20, 2))
            pct_change = Column(DECIMAL(8, 4))
            turnover = Column(DECIMAL(8, 4))
            vwap = Column(DECIMAL(12, 4))
            adj_factor = Column(DECIMAL(12, 6))
        
        class FinancialData(Base):
            __tablename__ = "financial_data"
            __table_args__ = (
                UniqueConstraint("symbol", "report_date", "report_type", name="uq_financial"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            symbol = Column(String(20), nullable=False)
            report_date = Column(DateTime, nullable=False)
            report_type = Column(String(20))
            revenue = Column(DECIMAL(20, 2))
            net_profit = Column(DECIMAL(20, 2))
            total_assets = Column(DECIMAL(20, 2))
            total_equity = Column(DECIMAL(20, 2))
            roe = Column(DECIMAL(8, 4))
            pe_ratio = Column(DECIMAL(8, 4))
            pb_ratio = Column(DECIMAL(8, 4))
        
        Base.metadata.create_all(engine)
        logger.info("Stock DB tables created")
    
    def _create_factor_tables(self):
        """创建因子数据库表"""
        if "factor_db" not in self.engines:
            return
        
        engine = self.engines["factor_db"]
        Base = declarative_base()
        
        class FactorMetadata(Base):
            __tablename__ = "factor_metadata"
            
            factor_name = Column(String(50), primary_key=True)
            category = Column(String(50))
            description = Column(Text)
            formula = Column(Text)
            lookback_period = Column(Integer)
            update_freq = Column(String(20))
            ic_mean = Column(DECIMAL(8, 6))
            ic_std = Column(DECIMAL(8, 6))
            icir = Column(DECIMAL(8, 4))
            half_life = Column(Integer)
            turnover = Column(DECIMAL(8, 4))
            monotonicity = Column(DECIMAL(8, 4))
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        class FactorValue(Base):
            __tablename__ = "factor_values"
            __table_args__ = (
                UniqueConstraint("factor_name", "symbol", "trade_date", name="uq_factor_symbol_date"),
                Index("idx_factor_values_name", "factor_name"),
                Index("idx_factor_values_date", "trade_date"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            factor_name = Column(String(50), nullable=False)
            symbol = Column(String(20), nullable=False)
            trade_date = Column(DateTime, nullable=False)
            factor_value = Column(DECIMAL(16, 8))
            rank_value = Column(Integer)
            zscore_value = Column(DECIMAL(8, 4))
            group_id = Column(Integer)
        
        class ICTimeSeries(Base):
            __tablename__ = "ic_time_series"
            __table_args__ = (
                UniqueConstraint("factor_name", "trade_date", "forward_period", "ic_method", name="uq_ic_ts"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            factor_name = Column(String(50), nullable=False)
            trade_date = Column(DateTime, nullable=False)
            ic = Column(DECIMAL(8, 6))
            ic_method = Column(String(20))
            forward_period = Column(Integer)
            pvalue = Column(DECIMAL(8, 6))
            n_stocks = Column(Integer)
        
        class GroupReturns(Base):
            __tablename__ = "group_returns"
            __table_args__ = (
                UniqueConstraint("factor_name", "trade_date", "group_id", name="uq_group_returns"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            factor_name = Column(String(50), nullable=False)
            trade_date = Column(DateTime, nullable=False)
            group_id = Column(Integer, nullable=False)
            mean_return = Column(DECIMAL(12, 8))
            median_return = Column(DECIMAL(12, 8))
            std_return = Column(DECIMAL(12, 8))
            sharpe = Column(DECIMAL(8, 4))
            n_stocks = Column(Integer)
        
        Base.metadata.create_all(engine)
        logger.info("Factor DB tables created")
    
    def _create_backtest_tables(self):
        """创建回测数据库表"""
        if "backtest_db" not in self.engines:
            return
        
        engine = self.engines["backtest_db"]
        Base = declarative_base()
        
        class BacktestRun(Base):
            __tablename__ = "backtest_run"
            
            run_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
            strategy_name = Column(String(100), nullable=False)
            description = Column(Text)
            start_date = Column(DateTime, nullable=False)
            end_date = Column(DateTime, nullable=False)
            initial_capital = Column(DECIMAL(20, 2))
            commission_rate = Column(DECIMAL(8, 6))
            slippage_rate = Column(DECIMAL(8, 6))
            rebalance_freq = Column(Integer)
            n_positions = Column(Integer)
            weighting_method = Column(String(50))
            final_value = Column(DECIMAL(20, 2))
            total_return = Column(DECIMAL(12, 6))
            annual_return = Column(DECIMAL(12, 6))
            sharpe_ratio = Column(DECIMAL(8, 4))
            sortino_ratio = Column(DECIMAL(8, 4))
            calmar_ratio = Column(DECIMAL(8, 4))
            max_drawdown = Column(DECIMAL(8, 6))
            win_rate = Column(DECIMAL(8, 4))
            profit_factor = Column(DECIMAL(8, 4))
            volatility = Column(DECIMAL(8, 6))
            var_95 = Column(DECIMAL(8, 6))
            cvar_95 = Column(DECIMAL(8, 6))
            status = Column(String(20), default="pending")
            created_at = Column(DateTime, default=datetime.utcnow)
            completed_at = Column(DateTime)
        
        class PortfolioState(Base):
            __tablename__ = "portfolio_state"
            __table_args__ = (
                UniqueConstraint("run_id", "date", name="uq_portfolio_date"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            run_id = Column(String(36), ForeignKey("backtest_run.run_id"), nullable=False)
            date = Column(DateTime, nullable=False)
            total_value = Column(DECIMAL(20, 2))
            cash = Column(DECIMAL(20, 2))
            equity = Column(DECIMAL(20, 2))
            n_positions = Column(Integer)
            daily_return = Column(DECIMAL(12, 8))
            cumulative_return = Column(DECIMAL(12, 8))
            turnover = Column(DECIMAL(8, 6))
        
        class Position(Base):
            __tablename__ = "positions"
            __table_args__ = (
                UniqueConstraint("run_id", "date", "symbol", name="uq_position"),
            )
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            run_id = Column(String(36), ForeignKey("backtest_run.run_id"), nullable=False)
            date = Column(DateTime, nullable=False)
            symbol = Column(String(20), nullable=False)
            weight = Column(DECIMAL(8, 6))
            shares = Column(DECIMAL(16, 4))
            entry_price = Column(DECIMAL(12, 4))
            current_price = Column(DECIMAL(12, 4))
            market_value = Column(DECIMAL(20, 2))
            unrealized_pnl = Column(DECIMAL(20, 2))
            daily_pnl = Column(DECIMAL(20, 2))
        
        class Trade(Base):
            __tablename__ = "trades"
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            run_id = Column(String(36), ForeignKey("backtest_run.run_id"), nullable=False)
            trade_date = Column(DateTime, nullable=False)
            symbol = Column(String(20), nullable=False)
            direction = Column(String(10))
            quantity = Column(DECIMAL(16, 4))
            price = Column(DECIMAL(12, 4))
            amount = Column(DECIMAL(20, 2))
            commission = Column(DECIMAL(20, 2))
            slippage = Column(DECIMAL(20, 2))
            pnl = Column(DECIMAL(20, 2))
            execution_time = Column(DateTime)
        
        Base.metadata.create_all(engine)
        logger.info("Backtest DB tables created")
    
    def get_session(self, db_name: str) -> Session:
        """获取数据库会话"""
        if db_name not in self.sessions:
            raise ValueError(f"Database {db_name} not initialized")
        return self.sessions[db_name]()
    
    def get_engine(self, db_name: str):
        """获取数据库引擎"""
        if db_name not in self.engines:
            raise ValueError(f"Database {db_name} not initialized")
        return self.engines[db_name]
    
    def close(self):
        """关闭所有数据库连接"""
        for engine in self.engines.values():
            engine.dispose()
        logger.info("All database connections closed")


# 需要导入 BigInteger
from sqlalchemy import BigInteger


def get_database_manager(
    mode: str = "local_sqlite",
    create_tables: bool = True
) -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Args:
        mode: 部署模式
        create_tables: 是否自动创建表
        
    Returns:
        DatabaseManager 实例
    """
    manager = DatabaseManager(mode=mode)
    
    if create_tables:
        manager.create_tables()
    
    return manager
