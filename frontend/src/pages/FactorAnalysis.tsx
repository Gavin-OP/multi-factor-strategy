import { useState, useEffect } from 'react';
import {
  Card, Row, Col, Select, InputNumber, Checkbox, Button, Space,
  Statistic, Tag, Typography, Progress, Divider, message, Descriptions,
  DatePicker, Modal, Spin
} from 'antd';
import {
  PlayCircleOutlined, SettingOutlined, LineChartOutlined,
  BarChartOutlined, SafetyCertificateOutlined, DashboardOutlined,
  CheckCircleOutlined, CloseCircleOutlined, WarningOutlined,
  CodeOutlined, CopyOutlined, CheckOutlined, CalendarOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useTheme } from '../theme';
import type { EChartsOption } from 'echarts';
import dayjs, { type Dayjs } from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

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
  dataSource: string;
}

interface FactorType {
  id: string;
  name: string;
  category: string;
  description: string;
  type: string;
  formula?: string;
}

interface FactorCode {
  id: string;
  name: string;
  category: string;
  description: string;
  code: string;
  parameters: Record<string, number>;
  references: string[];
  formula?: string;
  type?: string;
}

const datePresets: { label: string; value: [Dayjs, Dayjs] }[] = [
  { label: '近1月', value: [dayjs().subtract(1, 'month'), dayjs()] },
  { label: '近3月', value: [dayjs().subtract(3, 'month'), dayjs()] },
  { label: '近6月', value: [dayjs().subtract(6, 'month'), dayjs()] },
  { label: '近1年', value: [dayjs().subtract(1, 'year'), dayjs()] },
];

export default function FactorAnalysisPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // 日期范围
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(3, 'month'),
    dayjs()
  ]);
  
  // 因子配置
  const [selectedFactor, setSelectedFactor] = useState('momentum_12m');
  const [quantiles, setQuantiles] = useState(5);
  const [forwardPeriod, setForwardPeriod] = useState(5);
  const [industryNeutral, setIndustryNeutral] = useState(false);
  const [marketCapNeutral, setMarketCapNeutral] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<FactorResult | null>(null);
  
  // 因子列表
  const [factorTypes, setFactorTypes] = useState<FactorType[]>([]);
  const [loadingFactors, setLoadingFactors] = useState(true);
  
  // 因子代码弹窗
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [factorCode, setFactorCode] = useState<FactorCode | null>(null);
  const [loadingCode, setLoadingCode] = useState(false);
  const [copied, setCopied] = useState(false);

  // 获取因子列表
  useEffect(() => {
    const fetchFactorTypes = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/factors/types`);
        if (response.ok) {
          const data = await response.json();
          setFactorTypes(data.factors || []);
        }
      } catch (error) {
        console.error('Failed to fetch factor types:', error);
      }
      setLoadingFactors(false);
    };
    fetchFactorTypes();
  }, []);

  // 获取因子代码
  const fetchFactorCode = async (factorId: string) => {
    setLoadingCode(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/factors/${factorId}/code`);
      if (response.ok) {
        const data = await response.json();
        setFactorCode(data);
        setCodeModalVisible(true);
      }
    } catch (error) {
      console.error('Failed to fetch factor code:', error);
      message.error('获取因子代码失败');
    }
    setLoadingCode(false);
  };

  // 复制代码
  const copyCode = () => {
    if (factorCode?.code) {
      navigator.clipboard.writeText(factorCode.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      message.success('代码已复制');
    }
  };

  // 运行测试
  const handleRunTest = async () => {
    setTesting(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/factors/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          factor_type: selectedFactor,
          start_date: dateRange[0].format('YYYYMMDD'),
          end_date: dateRange[1].format('YYYYMMDD'),
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

  // Generate mock result
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
      dataSource: 'mock'
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

  // 按类别分组因子
  const groupedFactors = factorTypes.reduce((acc, factor) => {
    const category = factor.category || '其他';
    if (!acc[category]) acc[category] = [];
    acc[category].push(factor);
    return acc;
  }, {} as Record<string, FactorType[]>);

  return (
    <div style={{ padding: 24, background: isDark ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ color: isDark ? '#fff' : '#333', marginBottom: 24 }}>
        <LineChartOutlined /> 因子有效性分析
      </Title>

      {/* Configuration Card */}
      <Card 
        title={<><SettingOutlined /> 参数配置</>}
        style={{ marginBottom: 24, background: isDark ? '#1f1f1f' : '#fff' }}
        extra={
          <Space>
            <Button
              icon={<CodeOutlined />}
              onClick={() => fetchFactorCode(selectedFactor)}
              loading={loadingCode}
            >
              查看代码
            </Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleRunTest}
              loading={testing}
              size="large"
            >
              运行测试
            </Button>
          </Space>
        }
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>日期范围</div>
            <RangePicker
              value={dateRange}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                }
              }}
              presets={datePresets}
              style={{ width: '100%' }}
              allowClear={false}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ marginBottom: 8 }}>因子类型</div>
            <Select
              value={selectedFactor}
              onChange={setSelectedFactor}
              style={{ width: '100%' }}
              loading={loadingFactors}
              showSearch
              optionFilterProp="label"
            >
              {Object.entries(groupedFactors).map(([category, factors]) => (
                <Select.OptGroup key={category} label={category}>
                  {factors.map(f => (
                    <Select.Option key={f.id} value={f.id} label={f.name}>
                      <Space>
                        <span>{f.name}</span>
                        {f.type === 'alpha101' && <Tag color="purple" style={{ fontSize: 10 }}>α101</Tag>}
                      </Space>
                    </Select.Option>
                  ))}
                </Select.OptGroup>
              ))}
            </Select>
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
          <Col xs={24}>
            <Space>
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
          <Card style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
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
                      <Tag color={result.dataSource === 'tushare' ? 'green' : 'orange'} style={{ marginLeft: 4 }}>
                        {result.dataSource === 'tushare' ? 'Tushare数据' : '模拟数据'}
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
          <Card title={<><DashboardOutlined /> IC 分析</>} style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
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
          <Card title={<><BarChartOutlined /> 分位数分析</>} style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
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
          <Card title={<><LineChartOutlined /> IC 衰减分析</>} style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
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
          <Card title={<><SafetyCertificateOutlined /> 风险指标</>} style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
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

      {/* Factor Code Modal */}
      <Modal
        title={factorCode?.name || '因子代码'}
        open={codeModalVisible}
        onCancel={() => setCodeModalVisible(false)}
        width={900}
        footer={[
          <Button key="close" onClick={() => setCodeModalVisible(false)}>
            关闭
          </Button>,
          <Button
            key="copy"
            type="primary"
            icon={copied ? <CheckOutlined /> : <CopyOutlined />}
            onClick={copyCode}
          >
            {copied ? '已复制' : '复制代码'}
          </Button>
        ]}
      >
        {factorCode && (
          <>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="类别">{factorCode.category}</Descriptions.Item>
              <Descriptions.Item label="类型">
                <Tag color={factorCode.type === 'alpha101' ? 'purple' : 'blue'}>
                  {factorCode.type === 'alpha101' ? 'Alpha101' : '基础因子'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>{factorCode.description}</Descriptions.Item>
              {factorCode.formula && (
                <Descriptions.Item label="公式" span={2}>
                  <code style={{ background: isDark ? '#333' : '#f5f5f5', padding: '4px 8px', borderRadius: 4 }}>
                    {factorCode.formula}
                  </code>
                </Descriptions.Item>
              )}
              <Descriptions.Item label="参数">
                {Object.entries(factorCode.parameters || {}).map(([k, v]) => `${k}=${v}`).join(', ') || '无'}
              </Descriptions.Item>
              <Descriptions.Item label="参考文献">
                {factorCode.references?.slice(0, 1).join('; ') || '无'}
              </Descriptions.Item>
            </Descriptions>
            <Title level={5}>Python 实现</Title>
            <pre style={{
              background: isDark ? '#0d1117' : '#f6f8fa',
              padding: 16,
              borderRadius: 6,
              overflow: 'auto',
              maxHeight: 400,
              fontSize: 13
            }}>
              {factorCode.code}
            </pre>
          </>
        )}
      </Modal>
    </div>
  );
}
