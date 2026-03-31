import React, { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart,
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  PieChart as PieChartIcon,
  RefreshCw,
  Play,
  CheckSquare,
  Square
} from 'lucide-react'

// ============================================
// Mock Data - 实际项目中会从后端 API 获取
// ============================================

const FACTORS = [
  { id: 'Factor001', name: 'Factor001 - 价量相关性', category: 'volume_price', ic: 0.042, icir: 0.65, halfLife: 8, effective: true },
  { id: 'Factor002', name: 'Factor002 - 日内动量', category: 'momentum', ic: 0.038, icir: 0.58, halfLife: 5, effective: true },
  { id: 'Factor003', name: 'Factor003 - 成交量排名', category: 'volume_price', ic: 0.035, icir: 0.52, halfLife: 6, effective: true },
  { id: 'Factor004', name: 'Factor004 - 成交量振荡', category: 'volume_price', ic: 0.028, icir: 0.42, halfLife: 4, effective: false },
  { id: 'Factor005', name: 'Factor005 - VWAP动量', category: 'momentum', ic: 0.045, icir: 0.72, halfLife: 10, effective: true },
  { id: 'Factor006', name: 'Factor006 - 开盘量相关', category: 'volume_price', ic: 0.032, icir: 0.48, halfLife: 7, effective: true },
  { id: 'Factor007', name: 'Factor007 - 成交量突破', category: 'volume_price', ic: 0.029, icir: 0.44, halfLife: 3, effective: false },
  { id: 'Factor008', name: 'Factor008 - 收盘价动量', category: 'momentum', ic: 0.033, icir: 0.51, halfLife: 9, effective: true },
  { id: 'Factor009', name: 'Factor009 - 成交量比率', category: 'volume_price', ic: 0.036, icir: 0.55, halfLife: 6, effective: true },
  { id: 'Factor010', name: 'Factor010 - 收益相关', category: 'volume_price', ic: 0.031, icir: 0.47, halfLife: 5, effective: false },
  { id: 'Momentum', name: 'Momentum - 动量因子', category: 'momentum', ic: 0.044, icir: 0.68, halfLife: 12, effective: true },
  { id: 'Volatility', name: 'Volatility - 波动率', category: 'risk', ic: -0.038, icir: -0.62, halfLife: 15, effective: true },
  { id: 'Liquidity', name: 'Liquidity - 流动性', category: 'liquidity', ic: -0.035, icir: -0.55, halfLife: 8, effective: true },
]

const generateEquityCurve = (factors: string[], period: number = 252) => {
  // 根据选择的因子生成模拟净值曲线
  const baseReturn = factors.length > 0 
    ? factors.reduce((sum, f) => {
        const factor = FACTORS.find(fa => fa.id === f)
        return sum + (factor?.ic || 0) * 0.5
      }, 0) / factors.length
    : 0.0003

  const dates = Array.from({ length: period }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (period - i))
    return d.toISOString().split('T')[0]
  })

  let equity = 10000000
  const data = dates.map((date, i) => {
    const dailyReturn = baseReturn + (Math.random() - 0.5) * 0.02
    equity *= (1 + dailyReturn)
    return {
      date,
      equity,
      return: dailyReturn,
      benchmark: 10000000 * Math.exp(0.0002 * i),
    }
  })
  return data
}

const generateFactorDetail = (factorId: string) => {
  const factor = FACTORS.find(f => f.id === factorId)
  if (!factor) return null

  // IC 时间序列
  const icSeries = Array.from({ length: 52 }, (_, i) => ({
    week: i + 1,
    ic: factor.ic + (Math.random() - 0.5) * 0.03,
  }))

  // IC 衰减曲线
  const icDecay = Array.from({ length: 20 }, (_, i) => ({
    lag: i,
    ic: factor.ic * Math.exp(-i / factor.halfLife),
  }))

  // 分组收益
  const groupReturns = Array.from({ length: 5 }, (_, i) => ({
    group: `Q${i + 1}`,
    return: (i - 2) * factor.ic * 0.3 + (Math.random() - 0.5) * 0.02,
    sharpe: (i - 2) * factor.icir * 0.5 + Math.random(),
  }))

  // 换手率
  const turnover = Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
    turnover: 0.2 + Math.random() * 0.3,
  }))

  return {
    ...factor,
    icSeries,
    icDecay,
    groupReturns,
    turnover,
    stats: {
      icMean: factor.ic,
      icStd: factor.ic / factor.icir,
      icir: factor.icir,
      halfLife: factor.halfLife,
      monotonicity: 0.7 + Math.random() * 0.25,
      turnover: 0.25 + Math.random() * 0.15,
      sortino: factor.icir * 1.2,
      maxDrawdown: 0.08 + Math.random() * 0.1,
    }
  }
}

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

// ============================================
// Main App Component
// ============================================

function App() {
  const [activeTab, setActiveTab] = useState<'factors' | 'backtest'>('factors')
  const [selectedFactor, setSelectedFactor] = useState<string | null>(null)
  const [factorDetail, setFactorDetail] = useState<any>(null)
  const [selectedFactors, setSelectedFactors] = useState<string[]>([])
  const [backtestLoading, setBacktestLoading] = useState(false)
  const [backtestResult, setBacktestResult] = useState<any>(null)

  // 当选择因子时加载详情
  useEffect(() => {
    if (selectedFactor) {
      const detail = generateFactorDetail(selectedFactor)
      setFactorDetail(detail)
    }
  }, [selectedFactor])

  // 运行回测
  const runBacktest = () => {
    if (selectedFactors.length === 0) return
    
    setBacktestLoading(true)
    
    // 模拟回测
    setTimeout(() => {
      const equityCurve = generateEquityCurve(selectedFactors)
      const finalEquity = equityCurve[equityCurve.length - 1].equity
      const totalReturn = finalEquity / 10000000 - 1
      
      setBacktestResult({
        equityCurve,
        totalReturn,
        sharpe: selectedFactors.reduce((sum, f) => {
          const factor = FACTORS.find(fa => fa.id === f)
          return sum + (factor?.icir || 0)
        }, 0) / selectedFactors.length * 2,
        maxDrawdown: 0.1 + Math.random() * 0.1,
        winRate: 0.55 + Math.random() * 0.1,
        selectedFactors: selectedFactors.map(f => FACTORS.find(fa => fa.id === f)?.name),
      })
      
      setBacktestLoading(false)
    }, 1500)
  }

  // 切换因子选择
  const toggleFactor = (factorId: string) => {
    setSelectedFactors(prev => 
      prev.includes(factorId)
        ? prev.filter(f => f !== factorId)
        : [...prev, factorId]
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Quant Factor Strategy</h1>
            <p className="text-slate-400 text-sm">量化因子策略分析与回测平台</p>
          </div>
          
          {/* Tab Switcher */}
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('factors')}
              className={`px-4 py-2 rounded-lg transition ${
                activeTab === 'factors' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              因子分析
            </button>
            <button
              onClick={() => setActiveTab('backtest')}
              className={`px-4 py-2 rounded-lg transition ${
                activeTab === 'backtest' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              策略回测
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {activeTab === 'factors' ? (
          <FactorAnalysisTab
            factors={FACTORS}
            selectedFactor={selectedFactor}
            setSelectedFactor={setSelectedFactor}
            factorDetail={factorDetail}
          />
        ) : (
          <BacktestTab
            factors={FACTORS}
            selectedFactors={selectedFactors}
            toggleFactor={toggleFactor}
            runBacktest={runBacktest}
            backtestLoading={backtestLoading}
            backtestResult={backtestResult}
          />
        )}
      </main>

      <footer className="border-t border-slate-700 p-4 text-center text-slate-500 text-sm">
        <p>Quant Factor Strategy Framework • 数据源: Akshare / Tushare / yfinance / Mock</p>
      </footer>
    </div>
  )
}

// ============================================
// Factor Analysis Tab
// ============================================

function FactorAnalysisTab({ 
  factors, 
  selectedFactor, 
  setSelectedFactor,
  factorDetail
}: any) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Factor List */}
      <div className="lg:col-span-1">
        <div className="bg-slate-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">因子列表 ({factors.length})</h2>
          
          <div className="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto">
            {factors.map((factor: any) => (
              <div
                key={factor.id}
                onClick={() => setSelectedFactor(factor.id)}
                className={`p-3 rounded-lg cursor-pointer transition ${
                  selectedFactor === factor.id
                    ? 'bg-blue-600'
                    : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{factor.name}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    factor.effective 
                      ? 'bg-green-900 text-green-300' 
                      : 'bg-yellow-900 text-yellow-300'
                  }`}>
                    {factor.effective ? '有效' : '无效'}
                  </span>
                </div>
                <div className="mt-2 text-sm text-slate-300 flex gap-4">
                  <span>IC: {factor.ic.toFixed(3)}</span>
                  <span>ICIR: {factor.icir.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Factor Detail */}
      <div className="lg:col-span-2">
        {factorDetail ? (
          <div className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard 
                title="IC Mean" 
                value={factorDetail.stats.icMean.toFixed(4)} 
                positive={factorDetail.stats.icMean > 0}
              />
              <MetricCard 
                title="ICIR" 
                value={factorDetail.stats.icir.toFixed(2)} 
                positive={Math.abs(factorDetail.stats.icir) > 0.5}
              />
              <MetricCard 
                title="Half-Life" 
                value={`${factorDetail.stats.halfLife}d`} 
                positive={factorDetail.stats.halfLife > 5}
              />
              <MetricCard 
                title="Monotonicity" 
                value={factorDetail.stats.monotonicity.toFixed(2)} 
                positive={factorDetail.stats.monotonicity > 0.7}
              />
            </div>

            {/* IC Time Series */}
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">IC 时间序列</h3>
              <ResponsiveContainer width="100%" height={250}>
                <ComposedChart data={factorDetail.icSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="week" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                  <Area type="monotone" dataKey="ic" fill="#3b82f6" fillOpacity={0.3} stroke="#3b82f6" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Two Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* IC Decay */}
              <div className="bg-slate-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">IC 衰减曲线</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={factorDetail.icDecay}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="lag" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                    <Line type="monotone" dataKey="ic" stroke="#10b981" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Group Returns */}
              <div className="bg-slate-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">分组收益</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={factorDetail.groupReturns}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="group" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(v) => `${(v * 100).toFixed(1)}%`} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                    <Bar dataKey="return" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Detailed Stats Table */}
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">详细统计</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-slate-400">IC Mean</p>
                  <p className="text-lg font-bold">{factorDetail.stats.icMean.toFixed(4)}</p>
                </div>
                <div>
                  <p className="text-slate-400">IC Std</p>
                  <p className="text-lg font-bold">{factorDetail.stats.icStd.toFixed(4)}</p>
                </div>
                <div>
                  <p className="text-slate-400">Sortino Ratio</p>
                  <p className="text-lg font-bold">{factorDetail.stats.sortino.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-slate-400">Max Drawdown</p>
                  <p className="text-lg font-bold text-red-400">{(factorDetail.stats.maxDrawdown * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg p-8 text-center">
            <p className="text-slate-400">请从左侧选择一个因子查看详细分析</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ============================================
// Backtest Tab
// ============================================

function BacktestTab({
  factors,
  selectedFactors,
  toggleFactor,
  runBacktest,
  backtestLoading,
  backtestResult
}: any) {
  return (
    <div className="space-y-6">
      {/* Factor Selection */}
      <div className="bg-slate-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">选择因子组合 ({selectedFactors.length} 已选)</h2>
          <button
            onClick={runBacktest}
            disabled={selectedFactors.length === 0 || backtestLoading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {backtestLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                回测中...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                运行回测
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-2">
          {factors.map((factor: any) => (
            <div
              key={factor.id}
              onClick={() => toggleFactor(factor.id)}
              className={`p-3 rounded-lg cursor-pointer transition border-2 ${
                selectedFactors.includes(factor.id)
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-transparent bg-slate-700 hover:bg-slate-600'
              }`}
            >
              <div className="flex items-center gap-2">
                {selectedFactors.includes(factor.id) ? (
                  <CheckSquare className="w-4 h-4 text-blue-400" />
                ) : (
                  <Square className="w-4 h-4 text-slate-400" />
                )}
                <span className="text-sm font-medium">{factor.id}</span>
              </div>
              <div className="mt-1 text-xs text-slate-400">
                IC: {factor.ic.toFixed(3)} | ICIR: {factor.icir.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Backtest Results */}
      {backtestResult && (
        <div className="space-y-6">
          {/* Summary Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              title="Total Return"
              value={`${(backtestResult.totalReturn * 100).toFixed(1)}%`}
              positive={backtestResult.totalReturn > 0}
            />
            <MetricCard
              title="Sharpe Ratio"
              value={backtestResult.sharpe.toFixed(2)}
              positive={backtestResult.sharpe > 1}
            />
            <MetricCard
              title="Max Drawdown"
              value={`${(backtestResult.maxDrawdown * 100).toFixed(1)}%`}
              positive={backtestResult.maxDrawdown < 0.15}
            />
            <MetricCard
              title="Win Rate"
              value={`${(backtestResult.winRate * 100).toFixed(1)}%`}
              positive={backtestResult.winRate > 0.5}
            />
          </div>

          {/* Equity Curve */}
          <div className="bg-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">净值曲线</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={backtestResult.equityCurve}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#64748b" tick={false} />
                <YAxis stroke="#64748b" tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                <Legend />
                <Area type="monotone" dataKey="equity" name="策略" fill="#3b82f6" fillOpacity={0.3} stroke="#3b82f6" />
                <Line type="monotone" dataKey="benchmark" name="基准" stroke="#64748b" strokeDasharray="5 5" dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Selected Factors Info */}
          <div className="bg-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">已选因子</h3>
            <div className="flex flex-wrap gap-2">
              {backtestResult.selectedFactors.map((name: string, i: number) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-blue-900 text-blue-300 rounded-full text-sm"
                >
                  {name}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!backtestResult && !backtestLoading && (
        <div className="bg-slate-800 rounded-lg p-8 text-center">
          <p className="text-slate-400">选择因子后点击"运行回测"查看结果</p>
        </div>
      )}
    </div>
  )
}

// ============================================
// Reusable Components
// ============================================

function MetricCard({ title, value, positive }: { title: string; value: string; positive: boolean }) {
  return (
    <div className="bg-slate-800 rounded-lg p-4">
      <p className="text-slate-400 text-sm">{title}</p>
      <p className={`text-2xl font-bold mt-1 ${positive ? 'text-green-400' : 'text-red-400'}`}>
        {value}
      </p>
    </div>
  )
}

export default App
