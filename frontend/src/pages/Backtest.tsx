import React, { useState, useMemo } from 'react';
import {
  Card, Row, Col, Select, InputNumber, Button, Space,
  Statistic, Table, Tag, Tabs, Typography, Progress, Tooltip,
  Collapse, Divider, message, Spin, Alert, Descriptions, Badge,
  Checkbox, DatePicker, Form, Input, Switch
} from 'antd';
import {
  PlayCircleOutlined, SettingOutlined, LineChartOutlined,
  BarChartOutlined, PieChartOutlined, ThunderboltOutlined,
  SafetyCertificateOutlined, DashboardOutlined, WarningOutlined,
  CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined,
  CalendarOutlined, DatabaseOutlined, StockOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useTheme } from '../theme';
import type { EChartsOption } from 'echarts';
import type { RowNode } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const { Title, Text } = Typography;
const { Panel } = Collapse;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

interface BacktestResult {
  totalReturn: number;
  annualReturn: number;
  excessReturn: number;
  annualVolatility: number;
  sharpeRatio: number;
  informationRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitLossRatio: number;
  beta: number;
  alpha: number;
  trackingError: number;
  downsideRisk: number;
  avgHoldingPeriod: number;
  turnoverRate: number;
  navCurve: { date: string; nav: number; benchmark: number }[];
  drawdownCurve: { date: string; drawdown: number }[];
  monthlyReturns: { month: string; return: number }[];
  yearlyReturns: { year: string; return: number; benchmark: number }[];
  holdings: { code: string; name: string; weight: number; return: number }[];
}

// Mock data
const mockBacktestResult: BacktestResult = {
  totalReturn: 0.85,
  annualReturn: 0.25,
  excessReturn: 0.18,
  annualVolatility: 0.18,
  sharpeRatio: 1.38,
  informationRatio: 1.12,
  maxDrawdown: -0.15,
  winRate: 0.58,
  profitLossRatio: 1.45,
  beta: 0.75,
  alpha: 0.08,
  trackingError: 0.12,
  downsideRisk: 0.10,
  avgHoldingPeriod: 15,
  turnoverRate: 0.45,
  navCurve: Array.from({ length: 250 }, (_, i) => ({
    date: `2024-${String(Math.floor(i / 20) + 1).padStart(2, '0')}-${String((i % 20) + 1).padStart(2, '0')}`,
    nav: 1 + i * 0.003 + Math.sin(i / 10) * 0.05 + Math.random() * 0.02,
    benchmark: 1 + i * 0.002 + Math.sin(i / 15) * 0.03 + Math.random() * 0.01
  })),
  drawdownCurve: Array.from({ length: 250 }, (_, i) => ({
    date: `2024-${String(Math.floor(i / 20) + 1).padStart(2, '0')}-${String((i % 20) + 1).padStart(2, '0')}`,
    drawdown: -Math.abs(Math.sin(i / 20)) * 0.15 - Math.random() * 0.02
  })),
  monthlyReturns: Array.from({ length: 12 }, (_, i) => ({
    month: `${i + 1}月`,
    return: (Math.random() - 0.4) * 0.1
  })),
  yearlyReturns: [
    { year: '2022', return: 0.15, benchmark: 0.08 },
    { year: '2023', return: 0.28, benchmark: 0.12 },
    { year: '2024', return: 0.22, benchmark: 0.10 },
  ],
  holdings: Array.from({ length: 50 }, (_, i) => ({
    code: `00000${i + 1}`.slice(-6),
    name: `股票${i + 1}`,
    weight: Math.random() * 0.05,
    return: (Math.random() - 0.5) * 0.5
  }))
};

const availableFactors = [
  { id: 'momentum_12m', name: 'Momentum 12M', category: 'Momentum' },
  { id: 'momentum_1m', name: 'Momentum 1M Reversal', category: 'Momentum' },
  { id: 'value_pe', name: 'P/E Ratio', category: 'Value' },
  { id: 'value_pb', name: 'P/B Ratio', category: 'Value' },
  { id: 'quality_roe', name: 'ROE', category: 'Quality' },
  { id: 'quality_roa', name: 'ROA', category: 'Quality' },
  { id: 'growth_sales', name: 'Sales Growth', category: 'Growth' },
  { id: 'volatility_1m', name: 'Volatility 1M', category: 'Volatility' },
];

const weightMethods = [
  { value: 'equal', label: '等权' },
  { value: 'ic', label: 'IC 加权' },
  { value: 'icir', label: 'ICIR 加权' },
  { value: 'max_sharpe', label: '最大夏普' },
  { value: 'min_variance', label: '最小方差' },
];

const rebalanceFreqs = [
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' },
  { value: 'quarterly', label: '每季' },
];

export default function BacktestPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [selectedFactors, setSelectedFactors] = useState<string[]>(['momentum_12m', 'value_pe']);
  const [weightMethod, setWeightMethod] = useState('equal');
  const [rebalanceFreq, setRebalanceFreq] = useState('monthly');
  const [topN, setTopN] = useState(50);
  const [maxWeight, setMaxWeight] = useState(0.05);
  const [commission, setCommission] = useState(0.001);
  const [slippage, setSlippage] = useState(0.001);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const handleRunBacktest = async () => {
    if (selectedFactors.length === 0) {
      message.warning('请至少选择一个因子');
      return;
    }
    setRunning(true);
    await new Promise(resolve => setTimeout(resolve, 3000));
    setResult(mockBacktestResult);
    setRunning(false);
    message.success('回测完成');
  };

  // NAV Chart
  const navChartOption: EChartsOption = useMemo(() => ({
    title: { text: '净值曲线', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['策略', '基准'], top: 30 },
    xAxis: {
      type: 'category',
      data: result?.navCurve.map(d => d.date) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    series: [
      {
        name: '策略',
        type: 'line',
        data: result?.navCurve.map(d => d.nav) || [],
        smooth: true,
        itemStyle: { color: '#1890ff' },
        areaStyle: { opacity: 0.1 }
      },
      {
        name: '基准',
        type: 'line',
        data: result?.navCurve.map(d => d.benchmark) || [],
        smooth: true,
        itemStyle: { color: '#faad14' },
        lineStyle: { type: 'dashed' }
      }
    ],
    grid: { left: '10%', right: '10%', bottom: '20%', top: '20%' },
    backgroundColor: 'transparent'
  }), [result?.navCurve, isDark]);

  // Drawdown Chart
  const drawdownChartOption: EChartsOption = useMemo(() => ({
    title: { text: '回撤曲线', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result?.drawdownCurve.map(d => d.date) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666', formatter: '{value}%' }
    },
    series: [{
      type: 'line',
      data: result?.drawdownCurve.map(d => (d.drawdown * 100).toFixed(2)) || [],
      itemStyle: { color: '#ff4d4f' },
      areaStyle: { color: '#ff4d4f', opacity: 0.3 }
    }],
    grid: { left: '10%', right: '10%', bottom: '20%', top: '15%' },
    backgroundColor: 'transparent'
  }), [result?.drawdownCurve, isDark]);

  // Monthly Returns Chart
  const monthlyChartOption: EChartsOption = useMemo(() => ({
    title: { text: '月度收益', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result?.monthlyReturns.map(d => d.month) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666', formatter: '{value}%' }
    },
    series: [{
      type: 'bar',
      data: result?.monthlyReturns.map(d => ({
        value: (d.return * 100).toFixed(2),
        itemStyle: { color: d.return >= 0 ? '#52c41a' : '#ff4d4f' }
      })) || []
    }],
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
    backgroundColor: 'transparent'
  }), [result?.monthlyReturns, isDark]);

  // Monthly Heatmap
  const heatmapOption: EChartsOption = useMemo(() => {
    const years = ['2022', '2023', '2024'];
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
    const data: [number, number, number][] = [];
    
    years.forEach((year, yIndex) => {
      months.forEach((month, mIndex) => {
        const value = (Math.random() - 0.45) * 0.15;
        data.push([mIndex, yIndex, value]);
      });
    });

    return {
      title: { text: '月度收益热力图', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
      tooltip: {
        formatter: (params: any) => {
          return `${years[params.data[1]]} ${months[params.data[0]]}: ${(params.data[2] * 100).toFixed(2)}%`;
        }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLabel: { color: isDark ? '#aaa' : '#666' }
      },
      yAxis: {
        type: 'category',
        data: years,
        axisLabel: { color: isDark ? '#aaa' : '#666' }
      },
      visualMap: {
        min: -0.15,
        max: 0.15,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: ['#ff4d4f', '#fff', '#52c41a']
        }
      },
      series: [{
        type: 'heatmap',
        data: data.map(d => [d[0], d[1], d[2]]),
        label: {
          show: true,
          formatter: (params: any) => `${(params.data[2] * 100).toFixed(1)}%`
        }
      }],
      grid: { left: '15%', right: '10%', bottom: '20%', top: '15%' },
      backgroundColor: 'transparent'
    };
  }, [isDark]);

  // AG Grid Column Definitions
  const holdingColumns = useMemo(() => [
    { field: 'code', headerName: '代码', width: 100, pinned: 'left' },
    { field: 'name', headerName: '名称', width: 120 },
    { field: 'weight', headerName: '权重', width: 100, valueFormatter: (p: any) => `${(p.value * 100).toFixed(2)}%` },
    { field: 'return', headerName: '收益', width: 100, 
      valueFormatter: (p: any) => `${(p.value * 100).toFixed(2)}%`,
      cellStyle: (p: any) => ({ color: p.value >= 0 ? '#52c41a' : '#ff4d4f' })
    }
  ], []);

  return (
    <div style={{ padding: 24, background: isDark ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ color: isDark ? '#fff' : '#333', marginBottom: 24 }}>
        <StockOutlined /> 策略回测
      </Title>

      {/* Configuration */}
      <Card 
        title={<><SettingOutlined /> 策略配置</>}
        style={{ marginBottom: 24 }}
        extra={
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleRunBacktest}
            loading={running}
            size="large"
          >
            运行回测
          </Button>
        }
      >
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={12}>
            <div style={{ marginBottom: 8 }}>选择因子</div>
            <Checkbox.Group
              value={selectedFactors}
              onChange={(v) => setSelectedFactors(v as string[])}
              style={{ width: '100%' }}
            >
              <Row>
                {availableFactors.map(factor => (
                  <Col span={12} key={factor.id}>
                    <Checkbox value={factor.id}>{factor.name}</Checkbox>
                  </Col>
                ))}
              </Row>
            </Checkbox.Group>
          </Col>
          <Col xs={24} lg={12}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <div style={{ marginBottom: 8 }}>权重方法</div>
                <Select
                  value={weightMethod}
                  onChange={setWeightMethod}
                  options={weightMethods}
                  style={{ width: '100%' }}
                />
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 8 }}>调仓频率</div>
                <Select
                  value={rebalanceFreq}
                  onChange={setRebalanceFreq}
                  options={rebalanceFreqs}
                  style={{ width: '100%' }}
                />
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>持仓数量</div>
                <InputNumber
                  value={topN}
                  onChange={(v) => setTopN(v || 50)}
                  min={10}
                  max={500}
                  style={{ width: '100%' }}
                />
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>手续费</div>
                <InputNumber
                  value={commission}
                  onChange={(v) => setCommission(v || 0.001)}
                  step={0.0001}
                  min={0}
                  max={0.01}
                  style={{ width: '100%' }}
                  formatter={v => `${(Number(v) * 100).toFixed(2)}%`}
                  parser={v => Number(v?.replace('%', '')) / 100}
                />
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>滑点</div>
                <InputNumber
                  value={slippage}
                  onChange={(v) => setSlippage(v || 0.001)}
                  step={0.0001}
                  min={0}
                  max={0.01}
                  style={{ width: '100%' }}
                  formatter={v => `${(Number(v) * 100).toFixed(2)}%`}
                  parser={v => Number(v?.replace('%', '')) / 100}
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </Card>

      {/* Results */}
      {result && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Performance Summary */}
          <Card>
            <Row gutter={[24, 16]}>
              <Col xs={12} sm={8} md={4}>
                <Statistic
                  title="总收益"
                  value={(result.totalReturn * 100).toFixed(1)}
                  suffix="%"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic
                  title="年化收益"
                  value={(result.annualReturn * 100).toFixed(1)}
                  suffix="%"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic
                  title="夏普比率"
                  value={result.sharpeRatio.toFixed(2)}
                  valueStyle={{ color: result.sharpeRatio > 1 ? '#52c41a' : '#faad14' }}
                />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic
                  title="最大回撤"
                  value={(result.maxDrawdown * 100).toFixed(1)}
                  suffix="%"
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="胜率" value={(result.winRate * 100).toFixed(0)} suffix="%" />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="盈亏比" value={result.profitLossRatio.toFixed(2)} />
              </Col>
            </Row>
          </Card>

          {/* Charts */}
          <Tabs defaultActiveKey="nav">
            <TabPane tab="净值曲线" key="nav">
              <Card>
                <div style={{ height: 400 }}>
                  <ReactECharts option={navChartOption} style={{ height: '100%' }} />
                </div>
              </Card>
            </TabPane>
            <TabPane tab="回撤曲线" key="drawdown">
              <Card>
                <div style={{ height: 300 }}>
                  <ReactECharts option={drawdownChartOption} style={{ height: '100%' }} />
                </div>
              </Card>
            </TabPane>
            <TabPane tab="月度收益" key="monthly">
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Card>
                    <div style={{ height: 300 }}>
                      <ReactECharts option={monthlyChartOption} style={{ height: '100%' }} />
                    </div>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card>
                    <div style={{ height: 300 }}>
                      <ReactECharts option={heatmapOption} style={{ height: '100%' }} />
                    </div>
                  </Card>
                </Col>
              </Row>
            </TabPane>
            <TabPane tab="持仓明细" key="holdings">
              <Card>
                <div className={isDark ? 'ag-theme-alpine-dark' : 'ag-theme-alpine'} style={{ height: 400 }}>
                  <AgGridReact
                    rowData={result.holdings}
                    columnDefs={holdingColumns}
                    animateRows={true}
                    pagination={true}
                    paginationPageSize={20}
                  />
                </div>
              </Card>
            </TabPane>
          </Tabs>

          {/* Risk Analysis */}
          <Card title={<><SafetyCertificateOutlined /> 风险分析</>}>
            <Row gutter={[24, 24]}>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="Beta" value={result.beta.toFixed(2)} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="Alpha" value={`${(result.alpha * 100).toFixed(1)}%`} valueStyle={{ color: '#52c41a' }} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="信息比率" value={result.informationRatio.toFixed(2)} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="跟踪误差" value={`${(result.trackingError * 100).toFixed(1)}%`} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="下行风险" value={`${(result.downsideRisk * 100).toFixed(1)}%`} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="年化波动率" value={`${(result.annualVolatility * 100).toFixed(1)}%`} />
              </Col>
            </Row>
          </Card>

          {/* Position Analysis */}
          <Card title={<><DatabaseOutlined /> 持仓分析</>}>
            <Descriptions bordered column={{ xs: 1, sm: 2, md: 4 }}>
              <Descriptions.Item label="平均持仓周期">{result.avgHoldingPeriod} 天</Descriptions.Item>
              <Descriptions.Item label="换手率">{(result.turnoverRate * 100).toFixed(0)}%</Descriptions.Item>
              <Descriptions.Item label="超额收益">{(result.excessReturn * 100).toFixed(1)}%</Descriptions.Item>
              <Descriptions.Item label="持仓数量">{result.holdings.length}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Space>
      )}
    </div>
  );
}
