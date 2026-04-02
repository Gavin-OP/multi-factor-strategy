import { useState, useEffect } from 'react';
import {
  Card, Row, Col, Select, Input, Radio, Space, Typography, Tag,
  Spin, message, Tabs, Table, Button, Modal, Descriptions
} from 'antd';
import {
  SearchOutlined, LineChartOutlined, DatabaseOutlined,
  CodeOutlined, CopyOutlined, CheckOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useTheme } from '../theme';
import type { EChartsOption } from 'echarts';

const { Title, Text, Paragraph } = Typography;

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

export default function MarketDataPage() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // 指数状态
  const [selectedIndex, setSelectedIndex] = useState('000001.SH');
  const [indexData, setIndexData] = useState<IndexData[]>([]);
  const [indexLoading, setIndexLoading] = useState(false);
  const [indexSource, setIndexSource] = useState('mock');

  // 股票搜索状态
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState<Stock[]>([]);
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [stockData, setStockData] = useState<IndexData[]>([]);
  const [stockLoading, setStockLoading] = useState(false);
  const [stockPeriod, setStockPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [stockSource, setStockSource] = useState('mock');

  // 因子代码状态
  const [factorCode, setFactorCode] = useState<FactorCode | null>(null);
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [copied, setCopied] = useState(false);

  // 获取指数数据
  const fetchIndexData = async () => {
    setIndexLoading(true);
    try {
      const endDate = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/index/daily?ts_code=${selectedIndex}&start_date=20230101&end_date=${endDate}`
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
      // 使用模拟数据
      const mockData = generateMockIndexData(selectedIndex);
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
      // 模拟搜索结果
      const mockResults = generateMockStocks(keyword);
      setSearchResults(mockResults);
    }
  };

  // 获取股票K线
  const fetchStockData = async (tsCode: string) => {
    setStockLoading(true);
    try {
      const endDate = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const response = await fetch(
        `${API_BASE_URL}/api/v1/data/stocks/${tsCode}/price?start_date=20230101&end_date=${endDate}`
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
      const mockData = generateMockIndexData(tsCode);
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
  const generateMockIndexData = (code: string): IndexData[] => {
    const data: IndexData[] = [];
    let price = code.includes('399') ? 2000 : 3000;
    const startDate = new Date('2023-01-01');
    
    for (let i = 0; i < 100; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i * 3);
      const change = (Math.random() - 0.5) * 0.03;
      price = price * (1 + change);
      
      data.push({
        ts_code: code,
        trade_date: date.toISOString().slice(0, 10).replace(/-/g, ''),
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

  useEffect(() => {
    fetchIndexData();
  }, [selectedIndex]);

  useEffect(() => {
    if (selectedStock) {
      fetchStockData(selectedStock.ts_code);
    }
  }, [selectedStock, stockPeriod]);

  // K线图配置
  const getKlineOption = (data: IndexData[], title: string): EChartsOption => ({
    title: {
      text: title,
      left: 'center',
      textStyle: { color: isDark ? '#fff' : '#333' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['K线', '成交量'],
      bottom: 10,
      textStyle: { color: isDark ? '#aaa' : '#666' }
    },
    grid: [
      { left: '10%', right: '8%', top: '15%', height: '50%' },
      { left: '10%', right: '8%', top: '70%', height: '15%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: data.map(d => d.trade_date),
        axisLabel: {
          color: isDark ? '#aaa' : '#666',
          rotate: 45
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
        axisLabel: { color: isDark ? '#aaa' : '#666' },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], bottom: 5, start: 50, end: 100 }
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
        data: data.map(d => d.vol),
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
        style={{
          marginBottom: 8,
          borderColor: isSelected ? '#1890ff' : undefined,
          background: isDark ? '#1f1f1f' : '#fff'
        }}
        onClick={() => setSelectedIndex(code)}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: isSelected ? 'bold' : 'normal' }}>{name}</span>
          <Tag color={isSelected ? 'blue' : 'default'}>{code}</Tag>
        </div>
      </Card>
    );
  };

  return (
    <div style={{ padding: 24, background: isDark ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
      <Title level={2} style={{ color: isDark ? '#fff' : '#333', marginBottom: 24 }}>
        <LineChartOutlined /> 行情数据
      </Title>

      <Row gutter={24}>
        {/* 左侧：指数列表 */}
        <Col xs={24} lg={6}>
          <Card
            title={<><DatabaseOutlined /> 指数列表</>}
            style={{ marginBottom: 16, background: isDark ? '#1f1f1f' : '#fff' }}
          >
            {mainIndices.map(index => (
              <IndexCard key={index.ts_code} code={index.ts_code} name={index.name} />
            ))}
          </Card>
        </Col>

        {/* 右侧：K线图和股票搜索 */}
        <Col xs={24} lg={18}>
          <Tabs
            defaultActiveKey="index"
            items={[
              {
                key: 'index',
                label: '指数K线',
                children: (
                  <Card style={{ background: isDark ? '#1f1f1f' : '#fff' }}>
                    <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                      <Title level={4}>
                        {mainIndices.find(i => i.ts_code === selectedIndex)?.name || '指数'}
                        <Tag color={indexSource === 'tushare' ? 'green' : 'orange'} style={{ marginLeft: 8 }}>
                          数据来源: {indexSource === 'tushare' ? 'Tushare' : '模拟数据'}
                        </Tag>
                      </Title>
                    </div>
                    <Spin spinning={indexLoading}>
                      <div style={{ height: 500 }}>
                        <ReactECharts
                          option={getKlineOption(indexData, '')}
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
                    <Space style={{ marginBottom: 16 }} size="middle">
                      <Input.Search
                        placeholder="输入股票代码或名称"
                        style={{ width: 250 }}
                        value={searchKeyword}
                        onChange={e => setSearchKeyword(e.target.value)}
                        onSearch={searchStocks}
                        enterButton={<SearchOutlined />}
                      />
                      {searchResults.length > 0 && (
                        <Select
                          placeholder="选择股票"
                          style={{ width: 200 }}
                          onChange={(value) => {
                            const stock = searchResults.find(s => s.ts_code === value);
                            setSelectedStock(stock || null);
                          }}
                          value={selectedStock?.ts_code}
                          options={searchResults.map(s => ({
                            value: s.ts_code,
                            label: `${s.name} (${s.ts_code})`
                          }))}
                        />
                      )}
                      <Radio.Group value={stockPeriod} onChange={e => setStockPeriod(e.target.value)}>
                        <Radio.Button value="daily">日线</Radio.Button>
                        <Radio.Button value="weekly">周线</Radio.Button>
                        <Radio.Button value="monthly">月线</Radio.Button>
                      </Radio.Group>
                    </Space>

                    {selectedStock && (
                      <>
                        <div style={{ marginBottom: 16 }}>
                          <Title level={4}>
                            {selectedStock.name} ({selectedStock.ts_code})
                            <Tag color={stockSource === 'tushare' ? 'green' : 'orange'} style={{ marginLeft: 8 }}>
                              数据来源: {stockSource === 'tushare' ? 'Tushare' : '模拟数据'}
                            </Tag>
                          </Title>
                        </div>
                        <Spin spinning={stockLoading}>
                          <div style={{ height: 500 }}>
                            <ReactECharts
                              option={getKlineOption(stockData, '')}
                              style={{ height: '100%' }}
                            />
                          </div>
                        </Spin>
                      </>
                    )}

                    {!selectedStock && (
                      <div style={{ textAlign: 'center', padding: 60, color: isDark ? '#666' : '#999' }}>
                        请搜索并选择股票查看K线图
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
                      columns={[
                        { title: '因子ID', dataIndex: 'id', key: 'id' },
                        { title: '因子名称', dataIndex: 'name', key: 'name' },
                        { title: '类别', dataIndex: 'category', key: 'category' },
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
