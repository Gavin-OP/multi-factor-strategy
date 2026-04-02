import { useState, useEffect } from 'react';
import {
  Card, Row, Col, Select, Input, Space, Typography, Tag,
  Spin, message, Tabs, Table, Button, Modal, Descriptions,
  DatePicker, Segmented
} from 'antd';
import {
  SearchOutlined, LineChartOutlined, DatabaseOutlined,
  CodeOutlined, CopyOutlined, CheckOutlined, CalendarOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useTheme } from '../theme';
import type { EChartsOption } from 'echarts';
import dayjs, { type Dayjs } from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface IndexData {
  ts_code: string;
  trade_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  vol: number;
}

interface Stock {
  ts_code: string;
  symbol: string;
  name: string;
  market: string;
}

interface FactorCode {
  id: string;
  name: string;
  category: string;
  description: string;
  code: string;
  parameters: Record<string, number>;
  references: string[];
}

// 主要指数列表
const mainIndices = [
  { ts_code: '000001.SH', name: '上证指数' },
  { ts_code: '399006.SZ', name: '创业板指' },
  { ts_code: '000688.SH', name: '科创50' },
  { ts_code: '000300.SH', name: '沪深300' },
  { ts_code: '000016.SH', name: '上证50' },
  { ts_code: '000905.SH', name: '中证500' },
];

// 周期类型
type PeriodType = 'daily' | 'weekly' | 'monthly';

// 预设时间范围
const datePresets: { label: string; value: [Dayjs, Dayjs] }[] = [
  { label: '近1月', value: [dayjs().subtract(1, 'month'), dayjs()] },
  { label: '近3月', value: [dayjs().subtract(3, 'month'), dayjs()] },
  { label: '近6月', value: [dayjs().subtract(6, 'month'), dayjs()] },
  { label: '近1年', value: [dayjs().subtract(1, 'year'), dayjs()] },
  { label: '近3年', value: [dayjs().subtract(3, 'year'), dayjs()] },
];

export default function MarketDataPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // 指数状态
  const [selectedIndex, setSelectedIndex] = useState('000001.SH');
  const [indexData, setIndexData] = useState<IndexData[]>([]);
  const [indexLoading, setIndexLoading] = useState(false);
  const [indexSource, setIndexSource] = useState('mock');
  const [indexDateRange, setIndexDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(3, 'month'),
    dayjs()
  ]);
  const [indexPeriod, setIndexPeriod] = useState<PeriodType>('daily');

  // 股票搜索状态
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState<Stock[]>([]);
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [stockData, setStockData] = useState<IndexData[]>([]);
  const [stockLoading, setStockLoading] = useState(false);
  const [stockSource, setStockSource] = useState('mock');
  const [stockDateRange, setStockDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(3, 'month'),
    dayjs()
  ]);
  const [stockPeriod, setStockPeriod] = useState<PeriodType>('daily');

  // 因子代码状态
  const [factorCode, setFactorCode] = useState<FactorCode | null>(null);
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [copied, setCopied] = useState(false);

  // 格式化日期为 API 格式
  const formatDate = (date: dayjs.Dayjs) => date.format('YYYYMMDD');

  // 获取指数数据
  const fetchIndexData = async () => {
    setIndexLoading(true);
    try {
      const startDate = formatDate(indexDateRange[0]);
      const endDate = formatDate(indexDateRange[1]);
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/index/daily?ts_code=${selectedIndex}&start_date=${startDate}&end_date=${endDate}`
      );
      if (response.ok) {
        const data = await response.json();
        setIndexData(data.data || []);
        setIndexSource(data.source || 'mock');
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('Error fetching index data:', error);
      const mockData = generateMockIndexData(selectedIndex, indexDateRange[0], indexDateRange[1]);
      setIndexData(mockData);
      setIndexSource('mock');
      message.warning('后端服务未连接，使用模拟数据');
    }
    setIndexLoading(false);
  };

  // 搜索股票
  const searchStocks = async (keyword: string) => {
    if (!keyword.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/stocks/search?keyword=${encodeURIComponent(keyword)}&limit=20`
      );
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.data || []);
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('Error searching stocks:', error);
      const mockResults = generateMockStocks(keyword);
      setSearchResults(mockResults);
    }
  };

  // 获取股票K线
  const fetchStockData = async (tsCode: string) => {
    setStockLoading(true);
    try {
      const startDate = formatDate(stockDateRange[0]);
      const endDate = formatDate(stockDateRange[1]);
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/stocks/${tsCode}/price?start_date=${startDate}&end_date=${endDate}`
      );
      if (response.ok) {
        const data = await response.json();
        setStockData(data.data || []);
        setStockSource(data.source || 'mock');
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('Error fetching stock data:', error);
      const mockData = generateMockIndexData(tsCode, stockDateRange[0], stockDateRange[1]);
      setStockData(mockData);
      setStockSource('mock');
      message.warning('使用模拟数据');
    }
    setStockLoading(false);
  };

  // 获取因子代码
  const fetchFactorCode = async (factorId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/factors/${factorId}/code`);
      if (response.ok) {
        const data = await response.json();
        setFactorCode(data);
        setCodeModalVisible(true);
      }
    } catch (error) {
      console.error('Error fetching factor code:', error);
    }
  };

  // 生成模拟指数数据
  const generateMockIndexData = (code: string, startDate: dayjs.Dayjs, endDate: dayjs.Dayjs): IndexData[] => {
    const data: IndexData[] = [];
    let price = code.includes('399') ? 2000 : 3000;
    const days = endDate.diff(startDate, 'day');
    const dataPoints = Math.min(days, 250);
    
    for (let i = 0; i < dataPoints; i++) {
      const date = startDate.add(i, 'day');
      if (date.day() === 0 || date.day() === 6) continue; // 跳过周末
      
      const change = (Math.random() - 0.5) * 0.03;
      price = price * (1 + change);
      
      data.push({
        ts_code: code,
        trade_date: date.format('YYYYMMDD'),
        open: price * (1 + (Math.random() - 0.5) * 0.01),
        high: price * 1.015,
        low: price * 0.985,
        close: price,
        vol: Math.random() * 1e8 + 5e7
      });
    }
    return data;
  };

  // 生成模拟股票
  const generateMockStocks = (keyword: string): Stock[] => {
    const stocks: Stock[] = [];
    for (let i = 0; i < 10; i++) {
      const code = `60000${i}.SH`;
      stocks.push({
        ts_code: code,
        symbol: code.split('.')[0],
        name: `股票${keyword}${i}`,
        market: '上海'
      });
    }
    return stocks;
  };

  // 复制代码
  const copyCode = () => {
    if (factorCode?.code) {
      navigator.clipboard.writeText(factorCode.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // 指数数据加载
  useEffect(() => {
    fetchIndexData();
  }, [selectedIndex, indexDateRange, indexPeriod]);

  // 股票数据加载
  useEffect(() => {
    if (selectedStock) {
      fetchStockData(selectedStock.ts_code);
    }
  }, [selectedStock, stockDateRange, stockPeriod]);

  // K线图配置
  const getKlineOption = (data: IndexData[], title: string, period: PeriodType): EChartsOption => ({
    title: {
      text: title,
      left: 'center',
      textStyle: { color: isDark ? '#fff' : '#333', fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const klineData = params[0];
        const volData = params[1];
        if (!klineData) return '';
        const [open, close, low, high] = klineData.data;
        const change = ((close - open) / open * 100).toFixed(2);
        const changeColor = close >= open ? '#ef5350' : '#26a69a';
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${klineData.name}</div>
            <div>开盘: ${open.toFixed(2)}</div>
            <div>收盘: <span style="color: ${changeColor}">${close.toFixed(2)} (${change}%)</span></div>
            <div>最高: ${high.toFixed(2)}</div>
            <div>最低: ${low.toFixed(2)}</div>
            ${volData ? `<div>成交量: ${(volData.data / 1e8).toFixed(2)}亿</div>` : ''}
          </div>
        `;
      }
    },
    legend: {
      data: ['K线', '成交量'],
      bottom: 10,
      textStyle: { color: isDark ? '#aaa' : '#666' }
    },
    grid: [
      { left: '8%', right: '8%', top: '12%', height: '52%' },
      { left: '8%', right: '8%', top: '68%', height: '16%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: data.map(d => d.trade_date),
        axisLabel: {
          color: isDark ? '#aaa' : '#666',
          rotate: 45,
          fontSize: 10
        },
        axisLine: { lineStyle: { color: isDark ? '#444' : '#ddd' } }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: data.map(d => d.trade_date),
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        type: 'value',
        scale: true,
        axisLabel: { color: isDark ? '#aaa' : '#666' },
        splitLine: { lineStyle: { color: isDark ? '#333' : '#eee' } }
      },
      {
        type: 'value',
        gridIndex: 1,
        axisLabel: { 
          color: isDark ? '#aaa' : '#666',
          formatter: (value: number) => value >= 1e8 ? `${(value/1e8).toFixed(0)}亿` : `${(value/1e4).toFixed(0)}万`
        },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 60, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], bottom: 5, start: 60, end: 100, height: 20 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: data.map(d => [d.open, d.close, d.low, d.high]),
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: data.map((d, i) => ({
          value: d.vol,
          itemStyle: {
            color: data[i]?.close >= data[i]?.open ? '#ef5350' : '#26a69a'
          }
        }))
      }
    ],
    backgroundColor: 'transparent'
  });

  // 指数列表项
  const IndexCard = ({ code, name }: { code: string; name: string }) => {
    const isSelected = selectedIndex === code;
    return (
      <Card
        hoverable
        size="small"
        style={{
          marginBottom: 8,
          borderColor: isSelected ? '#1890ff' : undefined,
          background: isDark ? '#1f1f1f' : '#fff',
          cursor: 'pointer'
        }}
        onClick={() => setSelectedIndex(code)}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: isSelected ? 'bold' : 'normal' }}>{name}</span>
          <Tag color={isSelected ? 'blue' : 'default'} style={{ margin: 0 }}>{code}</Tag>
        </div>
      </Card>
    );
  };

  // 日期范围选择器配置
  const rangePickerStyle = { 
    width: 280,
    background: isDark ? '#1f1f1f' : '#fff'
  };

  return (
    <div style={{ padding: 24, background: isDark ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ color: isDark ? '#fff' : '#333', marginBottom: 24 }}>
        <LineChartOutlined /> 行情数据
      </Title>

      <Row gutter={24}>
        {/* 左侧：指数列表 */}
        <Col xs={24} lg={5}>
          <Card
            title={<><DatabaseOutlined /> 指数列表</>}
            size="small"
            style={{ marginBottom: 16, background: isDark ? '#1f1f1f' : '#fff' }}
          >
            {mainIndices.map(index => (
              <IndexCard key={index.ts_code} code={index.ts_code} name={index.name} />
            ))}
          </Card>
        </Col>

        {/* 右侧：K线图和股票搜索 */}
        <Col xs={24} lg={19}>
          <Tabs
            defaultActiveKey="index"
            items={[
              {
                key: 'index',
                label: '指数K线',
                children: (
                  <Card style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
                    {/* 控制栏 */}
                    <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                      <Col xs={24} sm={12} md={10}>
                        <Space>
                          <CalendarOutlined style={{ color: isDark ? '#aaa' : '#666' }} />
                          <RangePicker
                            value={indexDateRange}
                            onChange={(dates) => {
                              if (dates && dates[0] && dates[1]) {
                                setIndexDateRange([dates[0], dates[1]]);
                              }
                            }}
                            presets={datePresets}
                            style={rangePickerStyle}
                            allowClear={false}
                          />
                        </Space>
                      </Col>
                      <Col xs={24} sm={12} md={6}>
                        <Segmented
                          value={indexPeriod}
                          onChange={(value) => setIndexPeriod(value as PeriodType)}
                          options={[
                            { label: '日线', value: 'daily' },
                            { label: '周线', value: 'weekly' },
                            { label: '月线', value: 'monthly' },
                          ]}
                          block
                        />
                      </Col>
                      <Col xs={24} md={8}>
                        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                          <Title level={4} style={{ margin: 0 }}>
                            {mainIndices.find(i => i.ts_code === selectedIndex)?.name || '指数'}
                          </Title>
                          <Tag color={indexSource === 'tushare' ? 'green' : 'orange'}>
                            数据来源: {indexSource === 'tushare' ? 'Tushare' : '模拟数据'}
                          </Tag>
                        </Space>
                      </Col>
                    </Row>

                    <Spin spinning={indexLoading}>
                      <div style={{ height: 480 }}>
                        <ReactECharts
                          option={getKlineOption(indexData, '', indexPeriod)}
                          style={{ height: '100%' }}
                        />
                      </div>
                    </Spin>
                  </Card>
                )
              },
              {
                key: 'stock',
                label: '股票K线',
                children: (
                  <Card style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
                    {/* 控制栏 */}
                    <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                      <Col xs={24} sm={12} md={8}>
                        <Input.Search
                          placeholder="输入股票代码或名称搜索"
                          value={searchKeyword}
                          onChange={e => setSearchKeyword(e.target.value)}
                          onSearch={searchStocks}
                          enterButton={<SearchOutlined />}
                          allowClear
                        />
                      </Col>
                      {searchResults.length > 0 && (
                        <Col xs={24} sm={12} md={6}>
                          <Select
                            placeholder="选择股票"
                            style={{ width: '100%' }}
                            onChange={(value) => {
                              const stock = searchResults.find(s => s.ts_code === value);
                              setSelectedStock(stock || null);
                            }}
                            value={selectedStock?.ts_code}
                            options={searchResults.map(s => ({
                              value: s.ts_code,
                              label: `${s.name} (${s.ts_code})`
                            }))}
                            showSearch
                            filterOption={(input, option) =>
                              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                          />
                        </Col>
                      )}
                      <Col xs={24} sm={12} md={6}>
                        <Segmented
                          value={stockPeriod}
                          onChange={(value) => setStockPeriod(value as PeriodType)}
                          options={[
                            { label: '日线', value: 'daily' },
                            { label: '周线', value: 'weekly' },
                            { label: '月线', value: 'monthly' },
                          ]}
                          block
                        />
                      </Col>
                      <Col xs={24} sm={12} md={6}>
                        <Space>
                          <CalendarOutlined style={{ color: isDark ? '#aaa' : '#666' }} />
                          <RangePicker
                            value={stockDateRange}
                            onChange={(dates) => {
                              if (dates && dates[0] && dates[1]) {
                                setStockDateRange([dates[0], dates[1]]);
                              }
                            }}
                            presets={datePresets}
                            style={{ width: 240 }}
                            allowClear={false}
                          />
                        </Space>
                      </Col>
                    </Row>

                    {selectedStock && (
                      <>
                        <div style={{ marginBottom: 16 }}>
                          <Space>
                            <Title level={4} style={{ margin: 0 }}>
                              {selectedStock.name} ({selectedStock.ts_code})
                            </Title>
                            <Tag color={stockSource === 'tushare' ? 'green' : 'orange'}>
                              数据来源: {stockSource === 'tushare' ? 'Tushare' : '模拟数据'}
                            </Tag>
                          </Space>
                        </div>
                        <Spin spinning={stockLoading}>
                          <div style={{ height: 480 }}>
                            <ReactECharts
                              option={getKlineOption(stockData, '', stockPeriod)}
                              style={{ height: '100%' }}
                            />
                          </div>
                        </Spin>
                      </>
                    )}

                    {!selectedStock && (
                      <div style={{ textAlign: 'center', padding: 80, color: isDark ? '#666' : '#999' }}>
                        <SearchOutlined style={{ fontSize: 48, marginBottom: 16, opacity: 0.5 }} />
                        <div>请输入股票代码或名称搜索，选择后查看K线图</div>
                      </div>
                    )}
                  </Card>
                )
              },
              {
                key: 'factor-code',
                label: '因子代码',
                children: (
                  <Card style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
                    <Table
                      dataSource={[
                        { id: 'momentum_1m', name: '1月动量', category: '动量因子' },
                        { id: 'momentum_3m', name: '3月动量', category: '动量因子' },
                        { id: 'momentum_6m', name: '6月动量', category: '动量因子' },
                        { id: 'momentum_12m', name: '12月动量', category: '动量因子' },
                        { id: 'value_pe', name: 'PE因子', category: '价值因子' },
                        { id: 'value_pb', name: 'PB因子', category: '价值因子' },
                        { id: 'quality_roe', name: 'ROE因子', category: '质量因子' },
                        { id: 'quality_roa', name: 'ROA因子', category: '质量因子' },
                        { id: 'volatility_1m', name: '1月波动率', category: '波动率因子' },
                        { id: 'liquidity_turnover', name: '换手率', category: '流动性因子' },
                      ]}
                      rowKey="id"
                      pagination={false}
                      columns={[
                        { title: '因子ID', dataIndex: 'id', key: 'id', width: 150 },
                        { title: '因子名称', dataIndex: 'name', key: 'name', width: 120 },
                        { title: '类别', dataIndex: 'category', key: 'category', width: 120 },
                        {
                          title: '操作',
                          key: 'action',
                          render: (_, record) => (
                            <Button
                              type="link"
                              icon={<CodeOutlined />}
                              onClick={() => fetchFactorCode(record.id)}
                            >
                              查看代码
                            </Button>
                          )
                        }
                      ]}
                    />
                  </Card>
                )
              }
            ]}
          />
        </Col>
      </Row>

      {/* 因子代码弹窗 */}
      <Modal
        title={factorCode?.name || '因子代码'}
        open={codeModalVisible}
        onCancel={() => setCodeModalVisible(false)}
        width={800}
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
            <Descriptions column={1} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="描述">{factorCode.description}</Descriptions.Item>
              <Descriptions.Item label="参数">
                {Object.entries(factorCode.parameters || {}).map(([k, v]) => `${k}=${v}`).join(', ') || '无'}
              </Descriptions.Item>
              <Descriptions.Item label="参考文献">
                {factorCode.references?.join('; ') || '无'}
              </Descriptions.Item>
            </Descriptions>
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
