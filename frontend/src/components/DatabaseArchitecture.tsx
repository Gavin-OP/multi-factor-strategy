import React, { useState } from 'react'
import { Database, Server, Table, Key, Link, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'

// ============================================
// ER Diagram Data
// ============================================

const DATABASE_SCHEMA = {
  stock_db: {
    name: "Stock Database",
    description: "存储股票基础信息、行情数据、财务数据",
    tables: {
      stocks: {
        name: "stocks",
        description: "股票基础信息表",
        columns: [
          { name: "symbol", type: "VARCHAR(20)", pk: true, fk: null, comment: "股票代码" },
          { name: "name", type: "VARCHAR(100)", pk: false, fk: null, comment: "股票名称" },
          { name: "exchange", type: "VARCHAR(20)", pk: false, fk: null, comment: "交易所" },
          { name: "industry", type: "VARCHAR(50)", pk: false, fk: null, comment: "行业" },
          { name: "sector", type: "VARCHAR(50)", pk: false, fk: null, comment: "板块" },
          { name: "list_date", type: "DATE", pk: false, fk: null, comment: "上市日期" },
          { name: "market_cap", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "总市值" },
          { name: "status", type: "VARCHAR(10)", pk: false, fk: null, comment: "状态" },
        ]
      },
      stock_daily: {
        name: "stock_daily",
        description: "日线行情数据表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "symbol", type: "VARCHAR(20)", pk: false, fk: "stocks.symbol", comment: "股票代码" },
          { name: "trade_date", type: "DATE", pk: false, fk: null, comment: "交易日期" },
          { name: "open", type: "DECIMAL(12,4)", pk: false, fk: null, comment: "开盘价" },
          { name: "high", type: "DECIMAL(12,4)", pk: false, fk: null, comment: "最高价" },
          { name: "low", type: "DECIMAL(12,4)", pk: false, fk: null, comment: "最低价" },
          { name: "close", type: "DECIMAL(12,4)", pk: false, fk: null, comment: "收盘价" },
          { name: "volume", type: "BIGINT", pk: false, fk: null, comment: "成交量" },
          { name: "amount", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "成交额" },
          { name: "pct_change", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "涨跌幅" },
        ]
      },
      financial_data: {
        name: "financial_data",
        description: "财务数据表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "symbol", type: "VARCHAR(20)", pk: false, fk: "stocks.symbol", comment: "股票代码" },
          { name: "report_date", type: "DATE", pk: false, fk: null, comment: "报告日期" },
          { name: "revenue", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "营业收入" },
          { name: "net_profit", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "净利润" },
          { name: "roe", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "ROE" },
          { name: "pe_ratio", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "市盈率" },
          { name: "pb_ratio", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "市净率" },
        ]
      }
    },
    relations: [
      { from: "stocks", to: "stock_daily", type: "1:N", label: "has daily data" },
      { from: "stocks", to: "financial_data", type: "1:N", label: "has financials" },
    ]
  },
  
  factor_db: {
    name: "Factor Database",
    description: "存储因子元数据、因子值、因子统计",
    tables: {
      factor_metadata: {
        name: "factor_metadata",
        description: "因子元数据表",
        columns: [
          { name: "factor_name", type: "VARCHAR(50)", pk: true, fk: null, comment: "因子名称" },
          { name: "category", type: "VARCHAR(50)", pk: false, fk: null, comment: "因子分类" },
          { name: "description", type: "TEXT", pk: false, fk: null, comment: "因子描述" },
          { name: "formula", type: "TEXT", pk: false, fk: null, comment: "因子公式" },
          { name: "lookback_period", type: "INT", pk: false, fk: null, comment: "回看周期" },
          { name: "ic_mean", type: "DECIMAL(8,6)", pk: false, fk: null, comment: "IC均值" },
          { name: "icir", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "ICIR" },
          { name: "half_life", type: "INT", pk: false, fk: null, comment: "半衰期" },
          { name: "is_active", type: "BOOLEAN", pk: false, fk: null, comment: "是否启用" },
        ]
      },
      factor_values: {
        name: "factor_values",
        description: "因子值表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "factor_name", type: "VARCHAR(50)", pk: false, fk: "factor_metadata.factor_name", comment: "因子名称" },
          { name: "symbol", type: "VARCHAR(20)", pk: false, fk: null, comment: "股票代码" },
          { name: "trade_date", type: "DATE", pk: false, fk: null, comment: "交易日期" },
          { name: "factor_value", type: "DECIMAL(16,8)", pk: false, fk: null, comment: "因子值" },
          { name: "rank_value", type: "INT", pk: false, fk: null, comment: "排名" },
          { name: "zscore_value", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "标准化值" },
          { name: "group_id", type: "INT", pk: false, fk: null, comment: "分组ID" },
        ]
      },
      ic_time_series: {
        name: "ic_time_series",
        description: "IC时间序列表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "factor_name", type: "VARCHAR(50)", pk: false, fk: "factor_metadata.factor_name", comment: "因子名称" },
          { name: "trade_date", type: "DATE", pk: false, fk: null, comment: "交易日期" },
          { name: "ic", type: "DECIMAL(8,6)", pk: false, fk: null, comment: "IC值" },
          { name: "forward_period", type: "INT", pk: false, fk: null, comment: "预测期" },
          { name: "pvalue", type: "DECIMAL(8,6)", pk: false, fk: null, comment: "p值" },
        ]
      },
      group_returns: {
        name: "group_returns",
        description: "分组收益表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "factor_name", type: "VARCHAR(50)", pk: false, fk: "factor_metadata.factor_name", comment: "因子名称" },
          { name: "trade_date", type: "DATE", pk: false, fk: null, comment: "交易日期" },
          { name: "group_id", type: "INT", pk: false, fk: null, comment: "组别" },
          { name: "mean_return", type: "DECIMAL(12,8)", pk: false, fk: null, comment: "平均收益" },
          { name: "sharpe", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "夏普比率" },
        ]
      }
    },
    relations: [
      { from: "factor_metadata", to: "factor_values", type: "1:N", label: "has values" },
      { from: "factor_metadata", to: "ic_time_series", type: "1:N", label: "has IC" },
      { from: "factor_metadata", to: "group_returns", type: "1:N", label: "has groups" },
    ]
  },
  
  backtest_db: {
    name: "Backtest Database",
    description: "存储回测运行、组合状态、交易记录",
    tables: {
      backtest_run: {
        name: "backtest_run",
        description: "回测运行记录表",
        columns: [
          { name: "run_id", type: "UUID", pk: true, fk: null, comment: "运行ID" },
          { name: "strategy_name", type: "VARCHAR(100)", pk: false, fk: null, comment: "策略名称" },
          { name: "start_date", type: "DATE", pk: false, fk: null, comment: "开始日期" },
          { name: "end_date", type: "DATE", pk: false, fk: null, comment: "结束日期" },
          { name: "initial_capital", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "初始资金" },
          { name: "total_return", type: "DECIMAL(12,6)", pk: false, fk: null, comment: "总收益" },
          { name: "sharpe_ratio", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "夏普比率" },
          { name: "max_drawdown", type: "DECIMAL(8,6)", pk: false, fk: null, comment: "最大回撤" },
          { name: "win_rate", type: "DECIMAL(8,4)", pk: false, fk: null, comment: "胜率" },
          { name: "status", type: "VARCHAR(20)", pk: false, fk: null, comment: "状态" },
        ]
      },
      portfolio_state: {
        name: "portfolio_state",
        description: "组合状态表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "run_id", type: "UUID", pk: false, fk: "backtest_run.run_id", comment: "运行ID" },
          { name: "date", type: "DATE", pk: false, fk: null, comment: "日期" },
          { name: "total_value", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "总价值" },
          { name: "cash", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "现金" },
          { name: "daily_return", type: "DECIMAL(12,8)", pk: false, fk: null, comment: "日收益" },
        ]
      },
      positions: {
        name: "positions",
        description: "持仓记录表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "run_id", type: "UUID", pk: false, fk: "backtest_run.run_id", comment: "运行ID" },
          { name: "date", type: "DATE", pk: false, fk: null, comment: "日期" },
          { name: "symbol", type: "VARCHAR(20)", pk: false, fk: null, comment: "股票代码" },
          { name: "weight", type: "DECIMAL(8,6)", pk: false, fk: null, comment: "权重" },
          { name: "shares", type: "DECIMAL(16,4)", pk: false, fk: null, comment: "股数" },
          { name: "unrealized_pnl", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "未实现盈亏" },
        ]
      },
      trades: {
        name: "trades",
        description: "交易记录表",
        columns: [
          { name: "id", type: "BIGSERIAL", pk: true, fk: null, comment: "主键" },
          { name: "run_id", type: "UUID", pk: false, fk: "backtest_run.run_id", comment: "运行ID" },
          { name: "trade_date", type: "DATE", pk: false, fk: null, comment: "交易日期" },
          { name: "symbol", type: "VARCHAR(20)", pk: false, fk: null, comment: "股票代码" },
          { name: "direction", type: "VARCHAR(10)", pk: false, fk: null, comment: "方向" },
          { name: "quantity", type: "DECIMAL(16,4)", pk: false, fk: null, comment: "数量" },
          { name: "price", type: "DECIMAL(12,4)", pk: false, fk: null, comment: "价格" },
          { name: "pnl", type: "DECIMAL(20,2)", pk: false, fk: null, comment: "盈亏" },
        ]
      }
    },
    relations: [
      { from: "backtest_run", to: "portfolio_state", type: "1:N", label: "has states" },
      { from: "backtest_run", to: "positions", type: "1:N", label: "has positions" },
      { from: "backtest_run", to: "trades", type: "1:N", label: "has trades" },
    ]
  }
}

const FREE_DATABASE_PROVIDERS = [
  {
    name: "Supabase",
    url: "https://supabase.com",
    freeQuota: "500 MB",
    features: ["PostgreSQL", "自动 API", "实时订阅", "认证系统"],
    recommended: "推荐用于 stock_db",
    rating: 5
  },
  {
    name: "Neon",
    url: "https://neon.tech",
    freeQuota: "500 MB",
    features: ["PostgreSQL", "弹性配置", "边缘计算", "分支功能"],
    recommended: "推荐用于 factor_db",
    rating: 4
  },
  {
    name: "Xata",
    url: "https://xata.io",
    freeQuota: "15 GB",
    features: ["PostgreSQL", "空间最大", "自动 API", "搜索功能"],
    recommended: "推荐用于 backtest_db",
    rating: 4
  },
  {
    name: "MemFire Cloud",
    url: "https://memfiredb.com",
    freeQuota: "512 MB",
    features: ["PostgreSQL", "国内服务", "Supabase 技术", "小程序支持"],
    recommended: "国内替代方案",
    rating: 4
  }
]

const FREE_DATA_SOURCES = [
  {
    name: "AkShare",
    type: "Python库",
    coverage: "A股、港股、美股、期货、基金",
    price: "完全免费",
    features: ["无需注册", "无限制", "数据丰富", "自动更新"],
    limitations: ["频率限制", "稳定性一般"],
    rating: 5,
    url: "https://akshare.akfamily.xyz"
  },
  {
    name: "Tushare",
    type: "API服务",
    coverage: "A股、港股、美股",
    price: "需Token，有免费额度",
    features: ["数据质量高", "接口稳定", "财务完整"],
    limitations: ["需要积分", "频率限制"],
    rating: 5,
    url: "https://tushare.pro"
  },
  {
    name: "BaoStock",
    type: "Python库",
    coverage: "A股历史数据",
    price: "完全免费",
    features: ["历史数据准确", "无限制", "开源免费"],
    limitations: ["无实时行情", "更新慢"],
    rating: 4,
    url: "http://baostock.com"
  },
  {
    name: "yfinance",
    type: "Python库",
    coverage: "美股、港股、部分A股ETF",
    price: "完全免费",
    features: ["全球市场", "简单易用", "无限制"],
    limitations: ["A股支持有限", "延迟较高"],
    rating: 4,
    url: "https://pypi.org/project/yfinance"
  },
  {
    name: "东方财富",
    type: "网页/API",
    coverage: "A股",
    price: "免费",
    features: ["实时行情", "资金流向", "财务数据"],
    limitations: ["需要爬虫", "不稳定"],
    rating: 3,
    url: "https://data.eastmoney.com"
  }
]

// ============================================
// Components
// ============================================

export default function DatabaseArchitecture() {
  const [selectedDb, setSelectedDb] = useState<string>('stock_db')
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set())

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables)
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName)
    } else {
      newExpanded.add(tableName)
    }
    setExpandedTables(newExpanded)
  }

  const currentDb = DATABASE_SCHEMA[selectedDb as keyof typeof DATABASE_SCHEMA]

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">数据库架构设计</h1>
          <p className="text-slate-400">三库分离架构 - Stock DB · Factor DB · Backtest DB</p>
        </div>

        {/* Database Selector */}
        <div className="flex gap-2 mb-6">
          {Object.keys(DATABASE_SCHEMA).map((dbKey) => (
            <button
              key={dbKey}
              onClick={() => setSelectedDb(dbKey)}
              className={`px-4 py-2 rounded-lg transition ${
                selectedDb === dbKey
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                {DATABASE_SCHEMA[dbKey as keyof typeof DATABASE_SCHEMA].name}
              </div>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ER Diagram */}
          <div className="lg:col-span-2 bg-slate-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">{currentDb.name}</h2>
            <p className="text-slate-400 mb-6">{currentDb.description}</p>

            {/* Tables */}
            <div className="space-y-4">
              {Object.values(currentDb.tables).map((table) => (
                <div key={table.name} className="border border-slate-700 rounded-lg overflow-hidden">
                  {/* Table Header */}
                  <div
                    onClick={() => toggleTable(table.name)}
                    className="flex items-center justify-between p-3 bg-slate-700 cursor-pointer hover:bg-slate-600 transition"
                  >
                    <div className="flex items-center gap-2">
                      <Table className="w-4 h-4 text-blue-400" />
                      <span className="font-mono font-semibold">{table.name}</span>
                      <span className="text-xs text-slate-400 ml-2">{table.description}</span>
                    </div>
                    {expandedTables.has(table.name) ? (
                      <ChevronDown className="w-4 h-4" />
                    ) : (
                      <ChevronRight className="w-4 h-4" />
                    )}
                  </div>

                  {/* Table Columns */}
                  {expandedTables.has(table.name) && (
                    <div className="p-3">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-slate-400 border-b border-slate-700">
                            <th className="text-left py-1">Column</th>
                            <th className="text-left py-1">Type</th>
                            <th className="text-left py-1">Key</th>
                            <th className="text-left py-1">Comment</th>
                          </tr>
                        </thead>
                        <tbody>
                          {table.columns.map((col) => (
                            <tr key={col.name} className="border-b border-slate-700/50">
                              <td className="py-2 font-mono">
                                <span className={col.pk ? "text-yellow-400 font-semibold" : ""}>
                                  {col.name}
                                </span>
                              </td>
                              <td className="py-2 text-slate-300">{col.type}</td>
                              <td className="py-2">
                                {col.pk && (
                                  <span className="flex items-center gap-1 text-yellow-400">
                                    <Key className="w-3 h-3" /> PK
                                  </span>
                                )}
                                {col.fk && (
                                  <span className="flex items-center gap-1 text-green-400">
                                    <Link className="w-3 h-3" /> FK
                                  </span>
                                )}
                              </td>
                              <td className="py-2 text-slate-400">{col.comment}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Relations */}
            <div className="mt-6">
              <h3 className="font-semibold mb-3">表关系</h3>
              <div className="space-y-2">
                {currentDb.relations.map((rel, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm bg-slate-700/50 p-2 rounded">
                    <span className="font-mono text-blue-400">{rel.from}</span>
                    <span className="text-slate-400">--[{rel.type}]--&gt;</span>
                    <span className="font-mono text-blue-400">{rel.to}</span>
                    <span className="text-slate-500 text-xs ml-2">({rel.label})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Free Database Providers */}
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Server className="w-4 h-4" />
                免费数据库服务
              </h3>
              <div className="space-y-3">
                {FREE_DATABASE_PROVIDERS.map((provider) => (
                  <div key={provider.name} className="border border-slate-700 rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{provider.name}</span>
                      <a 
                        href={provider.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                    <div className="text-sm text-green-400 mb-1">
                      免费额度: {provider.freeQuota}
                    </div>
                    <div className="text-xs text-slate-400 mb-2">
                      {provider.recommended}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {provider.features.slice(0, 3).map((f) => (
                        <span key={f} className="text-xs bg-slate-700 px-2 py-0.5 rounded">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Free Data Sources */}
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Database className="w-4 h-4" />
                免费数据源
              </h3>
              <div className="space-y-3">
                {FREE_DATA_SOURCES.map((source) => (
                  <div key={source.name} className="border border-slate-700 rounded p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">{source.name}</span>
                      <span className="text-xs text-green-400">{source.price}</span>
                    </div>
                    <div className="text-xs text-slate-400 mb-2">
                      {source.coverage}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {source.features.slice(0, 3).map((f) => (
                        <span key={f} className="text-xs bg-slate-700 px-2 py-0.5 rounded">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
