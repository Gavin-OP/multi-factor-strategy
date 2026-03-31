# 量化因子策略数据库架构设计

## 📐 系统架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           应用层 (Application Layer)                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  数据服务     │  │  因子服务     │  │  回测服务     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
├─────────────────────────────────────────────────────────────────────────┤
│                           数据访问层 (Data Access Layer)                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SQLAlchemy ORM / Repository Pattern            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           数据库层 (Database Layer)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ stock_db     │  │ factor_db    │  │ backtest_db  │                  │
│  │ 股票数据     │  │ 因子数据     │  │ 回测数据     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ 三库分离架构

### 设计原则
1. **Separation of Concerns**: 股票数据、因子数据、回测数据独立存储
2. **可扩展性**: 每个数据库可独立扩容
3. **性能优化**: 针对不同数据特征优化存储
4. **数据隔离**: 避免相互影响，便于维护

---

## 1️⃣ stock_db (股票数据库)

### ER Diagram

```
┌─────────────────┐       ┌─────────────────┐
│    stocks       │       │   stock_daily   │
├─────────────────┤       ├─────────────────┤
│ PK symbol       │───┐   │ PK id           │
│    name         │   │   │ FK symbol       │───┐
│    exchange     │   │   │ FK stock_id     │◄──┘
│    industry     │   │   │    trade_date   │
│    list_date    │   │   │    open         │
│    market_cap   │   │   │    high         │
│    status       │   │   │    low          │
└─────────────────┘   │   │    close        │
        │             │   │    volume       │
        │             │   │    amount       │
        │             │   │    pct_change   │
        │             │   │    turnover     │
        │             │   └─────────────────┘
        │             │
        │             │   ┌─────────────────┐
        │             └──►│  stock_info     │
        │                 ├─────────────────┤
        │                 │ PK symbol       │
        │                 │    sector       │
        │                 │    industry     │
        │                 │    is_hs300     │
        │                 │    is_zz500     │
        │                 └─────────────────┘
        │
        │             ┌─────────────────┐
        └────────────►│  financial_data │
                      ├─────────────────┤
                      │ PK id           │
                      │ FK symbol       │
                      │    report_date  │
                      │    revenue      │
                      │    net_profit   │
                      │    roe          │
                      │    pe_ratio     │
                      │    pb_ratio     │
                      └─────────────────┘
```

### 表结构

```sql
-- 股票基础信息
CREATE TABLE stocks (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(20),           -- 交易所: SH, SZ, BJ
    industry VARCHAR(50),           -- 行业
    sector VARCHAR(50),             -- 板块
    list_date DATE,                 -- 上市日期
    market_cap DECIMAL(20,2),       -- 总市值
    status VARCHAR(10) DEFAULT 'L', -- 状态: L-上市, D-退市, P-暂停
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 日线行情数据 (分区表)
CREATE TABLE stock_daily (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    amount DECIMAL(20,2),
    pct_change DECIMAL(8,4),
    turnover DECIMAL(8,4),
    vwap DECIMAL(12,4),
    adj_factor DECIMAL(12,6),
    PRIMARY KEY (id),
    UNIQUE (symbol, trade_date)
);
CREATE INDEX idx_stock_daily_symbol ON stock_daily(symbol);
CREATE INDEX idx_stock_daily_date ON stock_daily(trade_date);

-- 财务数据
CREATE TABLE financial_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    report_date DATE NOT NULL,
    report_type VARCHAR(20),        -- 报告类型
    revenue DECIMAL(20,2),          -- 营业收入
    net_profit DECIMAL(20,2),       -- 净利润
    total_assets DECIMAL(20,2),     -- 总资产
    total_equity DECIMAL(20,2),     -- 股东权益
    roe DECIMAL(8,4),               -- ROE
    pe_ratio DECIMAL(8,4),          -- 市盈率
    pb_ratio DECIMAL(8,4),          -- 市净率
    UNIQUE (symbol, report_date, report_type)
);

-- 股票标签/分类
CREATE TABLE stock_tags (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    tag_value VARCHAR(100),
    UNIQUE (symbol, tag_name)
);
```

---

## 2️⃣ factor_db (因子数据库)

### ER Diagram

```
┌─────────────────┐       ┌─────────────────┐
│ factor_metadata │       │  factor_values  │
├─────────────────┤       ├─────────────────┤
│ PK factor_name  │───┐   │ PK id           │
│    category     │   │   │ FK factor_name  │◄──┐
│    description  │   │   │    symbol       │   │
│    formula      │   │   │    trade_date   │   │
│    lookback     │   │   │    factor_value │   │
│    ic_mean      │   │   │    rank_value   │   │
│    icir         │   │   │    zscore_value │   │
│    is_active    │   │   └─────────────────┘   │
│    created_at   │   │                         │
└─────────────────┘   │   ┌─────────────────┐   │
                      └──►│  factor_stats   │   │
                          ├─────────────────┤   │
                          │ PK id           │   │
                          │ FK factor_name  │◄──┘
                          │    calc_date    │
                          │    ic           │
                          │    icir         │
                          │    turnover     │
                          │    monotonicity │
                          └─────────────────┘
                                │
                                │   ┌─────────────────┐
                                └──►│ ic_time_series  │
                                    ├─────────────────┤
                                    │ PK id           │
                                    │ FK factor_name  │
                                    │    trade_date   │
                                    │    ic           │
                                    │    pvalue       │
                                    │    n_stocks     │
                                    └─────────────────┘
```

### 表结构

```sql
-- 因子元数据
CREATE TABLE factor_metadata (
    factor_name VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50),              -- 因子分类: momentum, value, quality, etc.
    description TEXT,
    formula TEXT,                       -- 因子公式/计算逻辑
    lookback_period INT,               -- 回看周期
    update_freq VARCHAR(20),           -- 更新频率: daily, weekly, monthly
    ic_mean DECIMAL(8,6),              -- IC均值
    ic_std DECIMAL(8,6),               -- IC标准差
    icir DECIMAL(8,4),                 -- ICIR
    half_life INT,                     -- 半衰期
    turnover DECIMAL(8,4),             -- 平均换手率
    monotonicity DECIMAL(8,4),         -- 单调性得分
    is_active BOOLEAN DEFAULT TRUE,    -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 因子值表 (分区表，按日期分区)
CREATE TABLE factor_values (
    id BIGSERIAL,
    factor_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    factor_value DECIMAL(16,8),
    rank_value INT,                    -- 截面排名
    zscore_value DECIMAL(8,4),         -- 标准化值
    group_id INT,                      -- 分组ID (1-5 或 1-10)
    PRIMARY KEY (id),
    UNIQUE (factor_name, symbol, trade_date)
);
CREATE INDEX idx_factor_values_name ON factor_values(factor_name);
CREATE INDEX idx_factor_values_date ON factor_values(trade_date);
CREATE INDEX idx_factor_values_symbol ON factor_values(symbol);

-- 因子统计表 (每日统计)
CREATE TABLE factor_daily_stats (
    id BIGSERIAL PRIMARY KEY,
    factor_name VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,
    ic DECIMAL(8,6),                   -- 当日IC
    ic_pvalue DECIMAL(8,6),            -- IC p值
    ic_significant BOOLEAN,            -- IC是否显著
    factor_return DECIMAL(12,8),       -- 因子收益率
    t_value DECIMAL(8,4),              -- t值
    turnover DECIMAL(8,4),             -- 当日换手率
    n_stocks INT,                      -- 股票数量
    UNIQUE (factor_name, trade_date)
);

-- IC时间序列
CREATE TABLE ic_time_series (
    id BIGSERIAL PRIMARY KEY,
    factor_name VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,
    ic DECIMAL(8,6),
    ic_method VARCHAR(20),             -- spearman / pearson
    forward_period INT,                -- 预测期: 1, 5, 20
    pvalue DECIMAL(8,6),
    n_stocks INT,
    UNIQUE (factor_name, trade_date, forward_period, ic_method)
);

-- IC衰减曲线
CREATE TABLE ic_decay (
    id BIGSERIAL PRIMARY KEY,
    factor_name VARCHAR(50) NOT NULL,
    calc_date DATE NOT NULL,           -- 计算日期
    lag_period INT NOT NULL,           -- 滞后期数
    ic DECIMAL(8,6),
    UNIQUE (factor_name, calc_date, lag_period)
);

-- 分组收益统计
CREATE TABLE group_returns (
    id BIGSERIAL PRIMARY KEY,
    factor_name VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,
    group_id INT NOT NULL,             -- 组别 1-5
    mean_return DECIMAL(12,8),         -- 平均收益
    median_return DECIMAL(12,8),       -- 中位数收益
    std_return DECIMAL(12,8),          -- 收益标准差
    sharpe DECIMAL(8,4),               -- 夏普比率
    n_stocks INT,
    UNIQUE (factor_name, trade_date, group_id)
);

-- 因子相关性矩阵
CREATE TABLE factor_correlation (
    id BIGSERIAL PRIMARY KEY,
    factor1 VARCHAR(50) NOT NULL,
    factor2 VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,
    correlation DECIMAL(8,6),
    method VARCHAR(20),                -- spearman / pearson
    UNIQUE (factor1, factor2, trade_date, method)
);
```

---

## 3️⃣ backtest_db (回测数据库)

### ER Diagram

```
┌─────────────────┐       ┌─────────────────┐
│  backtest_run   │       │ portfolio_state │
├─────────────────┤       ├─────────────────┤
│ PK run_id       │───┐   │ PK id           │
│    strategy_name│   │   │ FK run_id       │◄──┐
│    start_date   │   │   │    date         │   │
│    end_date     │   │   │    total_value  │   │
│    initial_cap  │   │   │    cash         │   │
│    final_value  │   │   │    n_positions │   │
│    total_return │   │   │    turnover     │   │
│    sharpe       │   │   └─────────────────┘   │
│    max_dd       │   │                         │
│    win_rate     │   │   ┌─────────────────┐   │
│    status       │   └──►│   positions     │   │
└─────────────────┘       ├─────────────────┤   │
                          │ PK id           │   │
                          │ FK run_id       │◄──┘
                          │    date         │
                          │    symbol       │
                          │    weight       │
                          │    shares       │
                          │    entry_price  │
                          │    exit_price   │
                          └─────────────────┘
                                │
                                │   ┌─────────────────┐
                                └──►│    trades       │
                                    ├─────────────────┤
                                    │ PK id           │
                                    │ FK run_id       │
                                    │    symbol       │
                                    │    trade_date   │
                                    │    direction    │
                                    │    quantity     │
                                    │    price        │
                                    │    commission   │
                                    │    pnl          │
                                    └─────────────────┘
```

### 表结构

```sql
-- 回测运行记录
CREATE TABLE backtest_run (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- 参数配置
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20,2),
    commission_rate DECIMAL(8,6),
    slippage_rate DECIMAL(8,6),
    rebalance_freq INT,                -- 调仓频率(天)
    n_positions INT,                   -- 持仓数量
    weighting_method VARCHAR(50),      -- 加权方法
    
    -- 性能指标
    final_value DECIMAL(20,2),
    total_return DECIMAL(12,6),
    annual_return DECIMAL(12,6),
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,6),
    win_rate DECIMAL(8,4),
    profit_factor DECIMAL(8,4),
    
    -- 风险指标
    volatility DECIMAL(8,6),
    var_95 DECIMAL(8,6),
    cvar_95 DECIMAL(8,6),
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 组合状态快照
CREATE TABLE portfolio_state (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES backtest_run(run_id),
    date DATE NOT NULL,
    total_value DECIMAL(20,2),
    cash DECIMAL(20,2),
    equity DECIMAL(20,2),
    n_positions INT,
    daily_return DECIMAL(12,8),
    cumulative_return DECIMAL(12,8),
    turnover DECIMAL(8,6),
    UNIQUE (run_id, date)
);
CREATE INDEX idx_portfolio_state_run ON portfolio_state(run_id);
CREATE INDEX idx_portfolio_state_date ON portfolio_state(date);

-- 持仓记录
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES backtest_run(run_id),
    date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    weight DECIMAL(8,6),
    shares DECIMAL(16,4),
    entry_price DECIMAL(12,4),
    current_price DECIMAL(12,4),
    market_value DECIMAL(20,2),
    unrealized_pnl DECIMAL(20,2),
    daily_pnl DECIMAL(20,2),
    UNIQUE (run_id, date, symbol)
);
CREATE INDEX idx_positions_run ON positions(run_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);

-- 交易记录
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES backtest_run(run_id),
    trade_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10),             -- buy / sell / short / cover
    quantity DECIMAL(16,4),
    price DECIMAL(12,4),
    amount DECIMAL(20,2),
    commission DECIMAL(20,2),
    slippage DECIMAL(20,2),
    pnl DECIMAL(20,2),
    execution_time TIMESTAMP
);
CREATE INDEX idx_trades_run ON trades(run_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_date ON trades(trade_date);

-- 回测因子配置
CREATE TABLE backtest_factors (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES backtest_run(run_id),
    factor_name VARCHAR(50) NOT NULL,
    factor_weight DECIMAL(8,6),
    UNIQUE (run_id, factor_name)
);

-- 回测指标序列
CREATE TABLE backtest_metrics_series (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES backtest_run(run_id),
    date DATE NOT NULL,
    equity DECIMAL(20,2),
    benchmark_equity DECIMAL(20,2),
    daily_return DECIMAL(12,8),
    cumulative_return DECIMAL(12,8),
    rolling_sharpe DECIMAL(8,4),
    rolling_volatility DECIMAL(8,6),
    drawdown DECIMAL(8,6),
    UNIQUE (run_id, date)
);
```

---

## 🔗 数据库连接配置

### 推荐免费方案

| 数据库 | 推荐平台 | 免费额度 | 推荐理由 |
|--------|---------|---------|---------|
| **stock_db** | Supabase | 500MB | 专业稳定，自动API |
| **factor_db** | Neon | 500MB | 弹性扩展，边缘计算 |
| **backtest_db** | Xata | **15GB** | 空间最大，适合回测 |

---

## 📦 完整SQL初始化脚本

见 `scripts/init_databases.sql`
