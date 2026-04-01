import { useState, useEffect } from 'react'
import { 
  ConfigProvider, Layout, Menu, Button, Dropdown, Space, theme as antdTheme,
  Typography, Tooltip, Badge, Tag
} from 'antd'
import {
  DatabaseOutlined, LineChartOutlined, BranchesOutlined,
  SunOutlined, MoonOutlined, GlobalOutlined, MenuOutlined,
  ApiOutlined, CheckCircleOutlined, CloseCircleOutlined
} from '@ant-design/icons'
import { I18nProvider, useI18n } from './i18n'
import { ThemeProvider, useTheme } from './theme'
import DatabaseArchitecture from './components/DatabaseArchitecture'
import FactorAnalysisPage from './pages/FactorAnalysis'
import BacktestPage from './pages/Backtest'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

const { Header, Content, Footer, Sider } = Layout
const { Title } = Typography

// API URL from environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Hook to check API status
function useApiStatus() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  
  const checkApi = async () => {
    try {
      const response = await fetch(`${API_URL}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      if (response.ok) {
        setStatus('online')
      } else {
        setStatus('offline')
      }
    } catch {
      setStatus('offline')
    }
  }
  
  useEffect(() => {
    checkApi()
    // Check every 30 seconds
    const interval = setInterval(checkApi, 30000)
    return () => clearInterval(interval)
  }, [])
  
  return { status, checkApi }
}

function AppContent() {
  const { t, language, setLanguage } = useI18n()
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'
  const { status, checkApi } = useApiStatus()
  
  const [currentPage, setCurrentPage] = useState('architecture')
  const [collapsed, setCollapsed] = useState(false)

  // Menu items
  const menuItems = [
    { key: 'architecture', icon: <DatabaseOutlined />, label: t.nav.database },
    { key: 'factors', icon: <LineChartOutlined />, label: t.nav.factors },
    { key: 'backtest', icon: <BranchesOutlined />, label: t.nav.backtest },
  ]

  // Language menu
  const langMenu = {
    items: [
      { key: 'zh', label: '中文', onClick: () => { setLanguage('zh'); dayjs.locale('zh-cn') } },
      { key: 'en', label: 'English', onClick: () => { setLanguage('en'); dayjs.locale('en') } },
    ]
  }

  // API status indicator
  const statusConfig = {
    checking: { color: '#faad14', text: '检查中...', icon: <ApiOutlined spin /> },
    online: { color: '#52c41a', text: '后端已连接', icon: <CheckCircleOutlined /> },
    offline: { color: '#ff4d4f', text: '后端离线', icon: <CloseCircleOutlined /> },
  }

  // Render page
  const renderPage = () => {
    switch (currentPage) {
      case 'architecture':
        return <DatabaseArchitecture />
      case 'factors':
        return <FactorAnalysisPage />
      case 'backtest':
        return <BacktestPage />
      default:
        return <DatabaseArchitecture />
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Sider - visible on md and up */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        breakpoint="md"
        style={{
          background: isDark ? '#141414' : '#fff',
        }}
        theme={isDark ? 'dark' : 'light'}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`
        }}>
          <Title level={4} style={{ margin: 0, color: isDark ? '#fff' : '#1890ff' }}>
            {collapsed ? 'QFS' : t.nav.title}
          </Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentPage]}
          onClick={(e) => setCurrentPage(e.key)}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        {/* Header */}
        <Header style={{
          padding: '0 16px',
          background: isDark ? '#141414' : '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`,
          position: 'sticky',
          top: 0,
          zIndex: 100
        }}>
          {/* Mobile menu button */}
          <div className="md:hidden">
            <Dropdown
              menu={{ items: menuItems.map(item => ({ ...item, onClick: () => setCurrentPage(item.key) })) }}
              trigger={['click']}
            >
              <Button type="text" icon={<MenuOutlined />} />
            </Dropdown>
          </div>

          {/* Desktop nav - hidden on mobile */}
          <Menu
            mode="horizontal"
            selectedKeys={[currentPage]}
            onClick={(e) => setCurrentPage(e.key)}
            items={menuItems}
            style={{ flex: 1, border: 0, background: 'transparent' }}
            className="hidden md:flex"
          />

          {/* Right controls */}
          <Space>
            {/* API Status Indicator */}
            <Tooltip title={
              <div>
                <div>{statusConfig[status].text}</div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>{API_URL}</div>
                <div style={{ fontSize: 11, marginTop: 4 }}>点击重新检查</div>
              </div>
            }>
              <Tag 
                color={statusConfig[status].color}
                style={{ cursor: 'pointer', margin: 0 }}
                onClick={checkApi}
              >
                {statusConfig[status].icon}
                <span style={{ marginLeft: 4 }} className="hidden sm:inline">
                  API {status === 'online' ? '在线' : status === 'offline' ? '离线' : '...'}
                </span>
              </Tag>
            </Tooltip>

            {/* Language */}
            <Dropdown menu={langMenu} trigger={['click']}>
              <Button type="text" icon={<GlobalOutlined />}>
                <span className="hidden sm:inline">{language === 'zh' ? '中文' : 'EN'}</span>
              </Button>
            </Dropdown>

            {/* Theme toggle */}
            <Tooltip title={t.theme.toggle}>
              <Button 
                type="text" 
                icon={isDark ? <SunOutlined /> : <MoonOutlined />}
                onClick={toggleTheme}
              />
            </Tooltip>
          </Space>
        </Header>

        {/* Content */}
        <Content style={{ 
          margin: 0,
          background: isDark ? '#000' : '#f5f5f5',
        }}>
          {renderPage()}
        </Content>

        {/* Footer */}
        <Footer style={{
          textAlign: 'center',
          background: isDark ? '#141414' : '#fff',
          borderTop: `1px solid ${isDark ? '#303030' : '#f0f0f0'}`,
          padding: '16px 24px'
        }}>
          <Typography.Text type="secondary">
            {t.footer.text} • {t.footer.freeDb}: Supabase + Neon + Xata • {t.footer.freeData}: AkShare + Tushare + BaoStock
          </Typography.Text>
        </Footer>
      </Layout>
    </Layout>
  )
}

function App() {
  const { theme } = useTheme()
  const { language } = useI18n()
  const isDark = theme === 'dark'

  return (
    <ConfigProvider
      locale={language === 'zh' ? zhCN : enUS}
      theme={{
        algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <AppContent />
    </ConfigProvider>
  )
}

// Wrap with providers
function AppWrapper() {
  return (
    <ThemeProvider>
      <I18nProvider>
        <App />
      </I18nProvider>
    </ThemeProvider>
  )
}

export default AppWrapper
