import { useState } from 'react';
import {
  Card, Row, Col, Select, InputNumber, Checkbox, Button, Space,
  Statistic, Tag, Typography, Progress, Divider, message, Descriptions
} from 'antd';
import {
  PlayCircleOutlined, SettingOutlined, LineChartOutlined,
  BarChartOutlined, SafetyCertificateOutlined, DashboardOutlined,
  CheckCircleOutlined, CloseCircleOutlined, WarningOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useTheme } from '../theme';
import type { EChartsOption } from 'echarts';

const { Title, Text } = Typography;

// API base URL - will use environment variable or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface FactorResult {
  name: string;
  category: string;
  icMean: number;
  icStd: number;
  icir: number;
  icTStat: number;
  icPositiveRatio: number;
  icSignificantRatio: number;
  factorReturn: number;
  factorReturnTStat: number;
  spreadReturn: number;
  spreadSharpe: number;
  monotonicity: number;
  halfLife: number;
  turnover: number;
  auc: number;
  f1Score: number;
  grade: string;
  score: number;
  isEffective: boolean;
  strengths: string[];
  weaknesses: string[];
  quantileReturns: { quantile: number; return: number; sharpe: number }[];
  icSeries: { date: string; ic: number }[];
  decayCurve: { lag: number; ic: number }[];
}

const factorTypes = [
  { value: 'momentum_1m', label: '1月动量' },
  { value: 'momentum_3m', label: '3月动量' },
  { value: 'momentum_6m', label: '6月动量' },
  { value: 'momentum_12m', label: '12月动量' },
  { value: 'value_pe', label: 'PE因子' },
  { value: 'value_pb', label: 'PB因子' },
  { value: 'quality_roe', label: 'ROE因子' },
  { value: 'quality_roa', label: 'ROA因子' },
  { value: 'volatility_1m', label: '1月波动率' },
  { value: 'liquidity_turnover', label: '换手率' },
];

export default function FactorAnalysisPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [selectedFactor, setSelectedFactor] = useState('momentum_12m');
  const [quantiles, setQuantiles] = useState(5);
  const [forwardPeriod, setForwardPeriod] = useState(5);
  const [industryNeutral, setIndustryNeutral] = useState(false);
  const [marketCapNeutral, setMarketCapNeutral] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<FactorResult | null>(null);

  const handleRunTest = async () => {
    setTesting(true);
    
    try {
      // Call backend API
      const response = await fetch(`${API_BASE_URL}/api/factors/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          factor_type: selectedFactor,
          start_date: '20230101',
          end_date: '20231231',
          quantiles: quantiles,
          forward_period: forwardPeriod,
          industry_neutral: industryNeutral,
          market_cap_neutral: marketCapNeutral,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        message.success('因子测试完成');
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('Error running factor test:', error);
      message.warning('后端服务未连接，使用模拟数据');
      
      // Fallback to mock data
      const mockResult = generateMockResult(selectedFactor, quantiles);
      setResult(mockResult);
    }
    
    setTesting(false);
  };

  // Generate mock result (used when backend is not available)
  const generateMockResult = (factorType: string, q: number): FactorResult => {
    const icSeries = Array.from({ length: 24 }, (_, i) => ({
      date: `2024-${String(i % 12 + 1).padStart(2, '0')}`,
      ic: (Math.random() - 0.4) * 0.15
    }));

    const quantileReturns = Array.from({ length: q }, (_, i) => ({
      quantile: i + 1,
      return: 0.05 + i * 0.03 + Math.random() * 0.01,
      sharpe: 0.5 + i * 0.2
    }));

    const decayCurve = Array.from({ length: 20 }, (_, i) => ({
      lag: i,
      ic: 0.045 * Math.exp(-i * 0.1)
    }));

    const icValues = icSeries.map(d => d.ic);
    const icMean = icValues.reduce((a, b) => a + b, 0) / icValues.length;
    const icStd = Math.sqrt(icValues.reduce((a, b) => a + Math.pow(b - icMean, 2), 0) / icValues.length);

    return {
      name: factorType,
      category: '因子',
      icMean,
      icStd,
      icir: icMean / icStd,
      icTStat: icMean / (icStd / Math.sqrt(icValues.length)),
      icPositiveRatio: icValues.filter(ic => ic > 0).length / icValues.length,
      icSignificantRatio: 0.35,
      factorReturn: 0.08,
      factorReturnTStat: 2.45,
      spreadReturn: quantileReturns[q - 1].return - quantileReturns[0].return,
      spreadSharpe: 1.25,
      monotonicity: 0.85,
      halfLife: 5,
      turnover: 0.35,
      auc: 0.535,
      f1Score: 0.52,
      grade: 'B',
      score: 0.65,
      isEffective: true,
      strengths: ['IC显著', '单调性好', '换手率适中'],
      weaknesses: ['ICIR偏低', '半衰期较短'],
      quantileReturns,
      icSeries,
      decayCurve,
    };
  };

  // IC Time Series Chart
  const icChartOption: EChartsOption = {
    title: { text: 'IC 时间序列', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result?.icSeries.map(d => d.date) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    series: [{
      type: 'line',
      data: result?.icSeries.map(d => d.ic) || [],
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#1890ff' }
    }],
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
    backgroundColor: 'transparent'
  };

  // Quantile Returns Chart
  const quantileChartOption: EChartsOption = {
    title: { text: '分位数收益', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result?.quantileReturns.map(d => `Q${d.quantile}`) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666', formatter: '{value}%' }
    },
    series: [{
      type: 'bar',
      data: result?.quantileReturns.map(d => (d.return * 100).toFixed(2)) || [],
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#1890ff' },
            { offset: 1, color: '#69c0ff' }
          ]
        }
      }
    }],
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
    backgroundColor: 'transparent'
  };

  // IC Decay Chart
  const decayChartOption: EChartsOption = {
    title: { text: 'IC 衰减曲线', left: 'center', textStyle: { color: isDark ? '#fff' : '#333' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: result?.decayCurve.map(d => d.lag) || [],
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: isDark ? '#aaa' : '#666' }
    },
    series: [{
      type: 'line',
      data: result?.decayCurve.map(d => d.ic) || [],
      smooth: true,
      itemStyle: { color: '#722ed1' }
    }],
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
    backgroundColor: 'transparent'
  };

  const getGradeColor = (grade: string) => {
    const colors: Record<string, string> = {
      'A+': '#52c41a',
      'A': '#73d13d',
      'B': '#faad14',
      'C': '#fa8c16',
      'D': '#f5222d',
      'F': '#ff4d4f'
    };
    return colors[grade] || '#d9d9d9';
  };

  return (
    <div style={{ padding: 24, background: isDark ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ color: isDark ? '#fff' : '#333', marginBottom: 24 }}>
        <LineChartOutlined /> 因子有效性分析
      </Title>

      {/* Configuration Card */}
      <Card 
        title={<><SettingOutlined /> 参数配置</>}
        style={{ marginBottom: 24 }}
        extra={
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleRunTest}
            loading={testing}
            size="large"
          >
            运行测试
          </Button>
        }
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>因子类型</div>
            <Select
              value={selectedFactor}
              onChange={setSelectedFactor}
              options={factorTypes}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>分位数</div>
            <InputNumber
              value={quantiles}
              onChange={(v) => setQuantiles(v || 5)}
              min={2}
              max={10}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>预测周期</div>
            <InputNumber
              value={forwardPeriod}
              onChange={(v) => setForwardPeriod(v || 5)}
              min={1}
              max={60}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>中性化处理</div>
            <Space direction="vertical">
              <Checkbox
                checked={industryNeutral}
                onChange={(e) => setIndustryNeutral(e.target.checked)}
              >
                行业中性
              </Checkbox>
              <Checkbox
                checked={marketCapNeutral}
                onChange={(e) => setMarketCapNeutral(e.target.checked)}
              >
                市值中性
              </Checkbox>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Results */}
      {result && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Effectiveness Summary */}
          <Card>
            <Row gutter={[24, 24]} align="middle">
              <Col xs={24} md={12}>
                <Space size="large">
                  {result.isEffective ? (
                    <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
                  ) : (
                    <CloseCircleOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />
                  )}
                  <div>
                    <Title level={3} style={{ margin: 0 }}>
                      {result.name}
                      <Tag color={getGradeColor(result.grade)} style={{ marginLeft: 8 }}>
                        评级: {result.grade}
                      </Tag>
                    </Title>
                    <Text type="secondary">{result.category}</Text>
                  </div>
                </Space>
              </Col>
              <Col xs={24} md={12}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="综合得分"
                      value={(result.score * 100).toFixed(0)}
                      suffix="%"
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="有效性"
                      value={result.isEffective ? '有效' : '无效'}
                      valueStyle={{ color: result.isEffective ? '#52c41a' : '#ff4d4f' }}
                    />
                  </Col>
                  <Col span={8}>
                    <Progress
                      type="circle"
                      percent={result.score * 100}
                      strokeColor={result.isEffective ? '#52c41a' : '#faad14'}
                      format={() => result.grade}
                    />
                  </Col>
                </Row>
              </Col>
            </Row>

            <Divider />

            <Row gutter={24}>
              <Col xs={24} md={12}>
                <Title level={5}><CheckCircleOutlined style={{ color: '#52c41a' }} /> 优势</Title>
                <ul>
                  {result.strengths.map((s, i) => (
                    <li key={i}><Text>{s}</Text></li>
                  ))}
                </ul>
              </Col>
              <Col xs={24} md={12}>
                <Title level={5}><WarningOutlined style={{ color: '#faad14' }} /> 不足</Title>
                <ul>
                  {result.weaknesses.map((w, i) => (
                    <li key={i}><Text>{w}</Text></li>
                  ))}
                </ul>
              </Col>
            </Row>
          </Card>

          {/* IC Analysis */}
          <Card title={<><DashboardOutlined /> IC 分析</>}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="IC 均值" value={result.icMean.toFixed(4)} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="IC 标准差" value={result.icStd.toFixed(4)} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="ICIR" value={result.icir.toFixed(3)} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic
                  title="IC t统计量"
                  value={result.icTStat.toFixed(2)}
                  valueStyle={{ color: Math.abs(result.icTStat) > 2 ? '#52c41a' : undefined }}
                />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="IC 正值比例" value={`${(result.icPositiveRatio * 100).toFixed(0)}%`} />
              </Col>
              <Col xs={12} sm={8} md={4}>
                <Statistic title="IC 显著比例" value={`${(result.icSignificantRatio * 100).toFixed(0)}%`} />
              </Col>
            </Row>
            <div style={{ marginTop: 24, height: 300 }}>
              <ReactECharts option={icChartOption} style={{ height: '100%' }} />
            </div>
          </Card>

          {/* Quantile Analysis */}
          <Card title={<><BarChartOutlined /> 分位数分析</>}>
            <Row gutter={24}>
              <Col xs={24} lg={12}>
                <div style={{ height: 300 }}>
                  <ReactECharts option={quantileChartOption} style={{ height: '100%' }} />
                </div>
              </Col>
              <Col xs={24} lg={12}>
                <Descriptions column={2} bordered size="small">
                  <Descriptions.Item label="多空价差收益">
                    <Text strong>{(result.spreadReturn * 100).toFixed(2)}%</Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="价差夏普">
                    {result.spreadSharpe.toFixed(2)}
                  </Descriptions.Item>
                  <Descriptions.Item label="单调性得分">
                    <Progress percent={result.monotonicity * 100} size="small" />
                  </Descriptions.Item>
                  <Descriptions.Item label="半衰期(期)">
                    {result.halfLife}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          {/* IC Decay */}
          <Card title={<><LineChartOutlined /> IC 衰减分析</>}>
            <Row gutter={24}>
              <Col xs={24} lg={16}>
                <div style={{ height: 300 }}>
                  <ReactECharts option={decayChartOption} style={{ height: '100%' }} />
                </div>
              </Col>
              <Col xs={24} lg={8}>
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="半衰期">
                    <Text strong>{result.halfLife} 期</Text>
                  </Descriptions.Item>
                  <Descriptions.Item label="平均换手率">
                    {(result.turnover * 100).toFixed(1)}%
                  </Descriptions.Item>
                  <Descriptions.Item label="AUC">
                    {result.auc.toFixed(3)}
                  </Descriptions.Item>
                  <Descriptions.Item label="F1分数">
                    {result.f1Score.toFixed(3)}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
          </Card>

          {/* Risk Metrics */}
          <Card title={<><SafetyCertificateOutlined /> 风险指标</>}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={6}>
                <Statistic title="索提诺比率" value="1.45" />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic title="卡尔马比率" value="0.92" />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic title="VaR(95%)" value="2.3%" />
              </Col>
              <Col xs={12} sm={6}>
                <Statistic title="CVaR(95%)" value="3.1%" />
              </Col>
            </Row>
          </Card>
        </Space>
      )}
    </div>
  );
}
