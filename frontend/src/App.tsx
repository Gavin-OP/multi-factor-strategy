import React, { useState } from 'react'
import { Database, LineChart, Settings, GitBranch } from 'lucide-react'
import DatabaseArchitecture from './components/DatabaseArchitecture'
import FactorAnalysisPage from './pages/FactorAnalysis'
import BacktestPage from './pages/Backtest'

// Main App with Navigation
function App() {
  const [currentPage, setCurrentPage] = useState<'architecture' | 'factors' | 'backtest'>('architecture')

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-800">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-6">
              <h1 className="text-lg font-bold">Quant Factor Strategy</h1>
              
              <div className="flex gap-1">
                <NavButton 
                  active={currentPage === 'architecture'}
                  onClick={() => setCurrentPage('architecture')}
                  icon={<Database className="w-4 h-4" />}
                  label="数据库架构"
                />
                <NavButton 
                  active={currentPage === 'factors'}
                  onClick={() => setCurrentPage('factors')}
                  icon={<LineChart className="w-4 h-4" />}
                  label="因子分析"
                />
                <NavButton 
                  active={currentPage === 'backtest'}
                  onClick={() => setCurrentPage('backtest')}
                  icon={<GitBranch className="w-4 h-4" />}
                  label="策略回测"
                />
              </div>
            </div>
            
            <div className="text-sm text-slate-400">
              数据源: AkShare / Tushare / yfinance
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentPage === 'architecture' && <DatabaseArchitecture />}
        {currentPage === 'factors' && <FactorAnalysisPage />}
        {currentPage === 'backtest' && <BacktestPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 p-4 text-center text-slate-500 text-sm">
        <p>Quant Factor Strategy Framework • 免费数据库: Supabase + Neon + Xata • 免费数据: AkShare + Tushare + BaoStock</p>
      </footer>
    </div>
  )
}

function NavButton({ active, onClick, icon, label }: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  label: string
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition ${
        active 
          ? 'bg-blue-600 text-white' 
          : 'text-slate-400 hover:text-white hover:bg-slate-700'
      }`}
    >
      {icon}
      {label}
    </button>
  )
}

export default App
