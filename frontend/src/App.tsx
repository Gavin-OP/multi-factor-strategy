import React from 'react'
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
} from 'recharts'
import { TrendingUp, TrendingDown, Activity, DollarSign, PieChart as PieChartIcon } from 'lucide-react'

// Mock data
const equityCurveData = Array.from({ length: 100 }, (_, i) => ({
  date: `2023-${String(Math.floor(i / 30) + 1).padStart(2, '0')}-${String((i % 30) + 1).padStart(2, '0')}`,
  equity: 10000000 * Math.exp(0.0003 * i + 0.01 * Math.sin(i / 10)),
  benchmark: 10000000 * Math.exp(0.0002 * i + 0.008 * Math.sin(i / 12)),
}))

const monthlyReturns = [
  { month: 'Jan', return: 2.3 },
  { month: 'Feb', return: -1.2 },
  { month: 'Mar', return: 3.5 },
  { month: 'Apr', return: 1.8 },
  { month: 'May', return: -0.5 },
  { month: 'Jun', return: 2.1 },
  { month: 'Jul', return: 4.2 },
  { month: 'Aug', return: -2.1 },
  { month: 'Sep', return: 1.5 },
  { month: 'Oct', return: 3.8 },
  { month: 'Nov', return: 2.2 },
  { month: 'Dec', return: 1.9 },
]

const factorPerformance = [
  { name: 'Factor001', ic: 0.04, icir: 0.65, effective: true },
  { name: 'Factor002', ic: 0.03, icir: 0.52, effective: true },
  { name: 'Factor003', ic: 0.02, icir: 0.45, effective: true },
  { name: 'Factor004', ic: 0.01, icir: 0.32, effective: false },
  { name: 'Factor005', ic: 0.05, icir: 0.72, effective: true },
  { name: 'Factor006', ic: 0.02, icir: 0.48, effective: true },
  { name: 'Momentum', ic: 0.04, icir: 0.58, effective: true },
  { name: 'Volatility', ic: 0.03, icir: 0.55, effective: true },
]

const positions = [
  { symbol: '000001', weight: 5.2, signal: 1.23, return: 2.5 },
  { symbol: '000002', weight: 4.8, signal: 1.15, return: 1.8 },
  { symbol: '000003', weight: 4.5, signal: 1.08, return: -0.5 },
  { symbol: '000004', weight: 4.2, signal: 1.02, return: 3.2 },
  { symbol: '000005', weight: 3.9, signal: 0.98, return: 0.8 },
  { symbol: '000006', weight: 3.7, signal: 0.95, return: 1.2 },
  { symbol: '000007', weight: 3.5, signal: 0.92, return: -1.1 },
  { symbol: '000008', weight: 3.3, signal: 0.88, return: 2.1 },
  { symbol: '000009', weight: 3.1, signal: 0.85, return: 0.5 },
  { symbol: '000010', weight: 2.9, signal: 0.82, return: 1.5 },
]

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

const pieData = [
  { name: 'Technology', value: 35 },
  { name: 'Finance', value: 20 },
  { name: 'Healthcare', value: 15 },
  { name: 'Consumer', value: 12 },
  { name: 'Industrial', value: 10 },
  { name: 'Other', value: 8 },
]

function App() {
  const metrics = {
    totalReturn: 24.5,
    annualReturn: 12.3,
    sharpeRatio: 1.85,
    maxDrawdown: -8.2,
    winRate: 58.5,
    profitFactor: 1.65,
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Quant Factor Strategy Dashboard
        </h1>
        <p className="text-slate-400">
          Real-time performance monitoring and analysis
        </p>
      </header>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Total Return"
          value={`${metrics.totalReturn}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          positive={metrics.totalReturn > 0}
        />
        <MetricCard
          title="Sharpe Ratio"
          value={metrics.sharpeRatio.toFixed(2)}
          icon={<Activity className="w-6 h-6" />}
          positive={metrics.sharpeRatio > 1}
        />
        <MetricCard
          title="Max Drawdown"
          value={`${metrics.maxDrawdown}%`}
          icon={<TrendingDown className="w-6 h-6" />}
          positive={metrics.maxDrawdown > -10}
        />
        <MetricCard
          title="Win Rate"
          value={`${metrics.winRate}%`}
          icon={<DollarSign className="w-6 h-6" />}
          positive={metrics.winRate > 50}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Equity Curve */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Equity Curve</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={equityCurveData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#64748b" tick={false} />
              <YAxis stroke="#64748b" tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                labelStyle={{ color: '#f1f5f9' }}
                formatter={(value: number) => [`$${(value / 1e6).toFixed(2)}M`, '']}
              />
              <Area
                type="monotone"
                dataKey="equity"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                name="Strategy"
              />
              <Area
                type="monotone"
                dataKey="benchmark"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.1}
                name="Benchmark"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Returns */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Monthly Returns</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyReturns}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="month" stroke="#64748b" />
              <YAxis stroke="#64748b" tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                formatter={(value: number) => [`${value}%`, 'Return']}
              />
              <Bar
                dataKey="return"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
              >
                {monthlyReturns.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.return >= 0 ? '#10b981' : '#ef4444'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Factor Performance */}
        <div className="card lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4">Factor Performance</h2>
          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Factor</th>
                  <th>IC</th>
                  <th>ICIR</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {factorPerformance.map((factor, i) => (
                  <tr key={i}>
                    <td className="font-medium">{factor.name}</td>
                    <td className={factor.ic > 0.02 ? 'positive' : ''}>
                      {factor.ic.toFixed(3)}
                    </td>
                    <td className={factor.icir > 0.5 ? 'positive' : ''}>
                      {factor.icir.toFixed(2)}
                    </td>
                    <td>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          factor.effective
                            ? 'bg-green-900 text-green-300'
                            : 'bg-yellow-900 text-yellow-300'
                        }`}
                      >
                        {factor.effective ? 'Effective' : 'Ineffective'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sector Allocation */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Sector Allocation</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                formatter={(value: number) => [`${value}%`, '']}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-2 mt-4">
            {pieData.map((item, index) => (
              <div key={item.name} className="flex items-center gap-1">
                <div
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-xs text-slate-400">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Top Positions</h2>
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Weight</th>
                <th>Signal</th>
                <th>Return</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos, i) => (
                <tr key={i}>
                  <td className="font-medium">{pos.symbol}</td>
                  <td>{pos.weight.toFixed(1)}%</td>
                  <td>{pos.signal.toFixed(2)}</td>
                  <td className={pos.return >= 0 ? 'positive' : 'negative'}>
                    {pos.return >= 0 ? '+' : ''}{pos.return.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-slate-500 text-sm">
        <p>Quant Factor Strategy Framework • Built with React + Python</p>
      </footer>
    </div>
  )
}

function MetricCard({
  title,
  value,
  icon,
  positive,
}: {
  title: string
  value: string
  icon: React.ReactNode
  positive: boolean
}) {
  return (
    <div className="card flex items-center gap-4">
      <div
        className={`p-3 rounded-lg ${
          positive ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
        }`}
      >
        {icon}
      </div>
      <div>
        <p className="text-slate-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

export default App
