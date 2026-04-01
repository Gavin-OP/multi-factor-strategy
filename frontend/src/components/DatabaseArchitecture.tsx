import React from 'react'
import { Card, Typography, Row, Col, Tag, Table, Divider, Progress, Statistic, Badge, Space } from 'antd'
import {
  DatabaseOutlined,   CloudOutlined, ApiOutlined, SafetyOutlined,
  ClockCircleOutlined, BarChartOutlined, CodeOutlined
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography

interface DataProvider {
  name: string
  type: 'free' | 'freemium' | 'paid'
  markets: string[]
  dataTypes: string[]
  rateLimit: string
  status: 'active' | 'planned' | 'beta'
}

interface Database {
  name: string
  type: string
  freeTier: string
  features: string[]
  status: 'active' | 'planned'
}

const dataProviders: DataProvider[] = [
  { name: 'AkShare', type: 'free', markets: ['A股', '港股', '美股', '期货'], dataTypes: ['行情', '财务', '宏观'], rateLimit: '无限制', status: 'active' },
  { name: 'Tushare', type: 'freemium', markets: ['A股', '港股', '美股'], dataTypes: ['行情', '财务', '指数'], rateLimit: '500次/分', status: 'active' },
  { name: 'BaoStock', type: 'free', markets: ['A股'], dataTypes: ['行情', '财务'], rateLimit: '无限制', status: 'active' },
  { name: 'yfinance', type: 'free', markets: ['美股', '港股', 'A股'], dataTypes: ['行情', '基本面'], rateLimit: '2000次/时', status: 'active' },
  { name: 'Alpha Vantage', type: 'freemium', markets: ['美股', '外汇', '加密货币'], dataTypes: ['行情', '技术指标'], rateLimit: '5次/分', status: 'planned' },
]

const databases: Database[] = [
  { name: 'Supabase', type: 'PostgreSQL', freeTier: '500MB', features: ['实时订阅', 'REST API', '认证'], status: 'active' },
  { name: 'Neon', type: 'PostgreSQL', freeTier: '3GB', features: ['Serverless', '分支', '自动扩展'], status: 'active' },
  { name: 'Xata', type: 'PostgreSQL', freeTier: '1GB', features: ['搜索', '分支', 'TypeScript'], status: 'planned' },
  { name: 'PlanetScale', type: 'MySQL', freeTier: '5GB', features: ['分支', '无服务器', '扩展'], status: 'planned' },
]

const providerColumns = [
  { title: '数据源', dataIndex: 'name', key: 'name', render: (name: string, record: DataProvider) => (
    <Space>
      {name}
      {record.type === 'free' && <Tag color="green">免费</Tag>}
      {record.type === 'freemium' && <Tag color="blue">免费版</Tag>}
    </Space>
  )},
  { title: '市场', dataIndex: 'markets', key: 'markets', render: (markets: string[]) => markets.join(', ') },
  { title: '数据类型', dataIndex: 'dataTypes', key: 'dataTypes', render: (types: string[]) => types.join(', ') },
  { title: '频率限制', dataIndex: 'rateLimit', key: 'rateLimit' },
  { title: '状态', dataIndex: 'status', key: 'status', render: (status: string) => (
    status === 'active' ? <Badge status="success" text="已集成" /> : <Badge status="processing" text="计划中" />
  )},
]

const dbColumns = [
  { title: '数据库', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '免费额度', dataIndex: 'freeTier', key: 'freeTier' },
  { title: '特性', dataIndex: 'features', key: 'features', render: (features: string[]) => features.join(', ') },
  { title: '状态', dataIndex: 'status', key: 'status', render: (status: string) => (
    status === 'active' ? <Badge status="success" text="已配置" /> : <Badge status="processing" text="计划中" />
  )},
]

export default function DatabaseArchitecture() {
  return (
    <div style={{ padding: 24 }}>
      <Title level={2}><DatabaseOutlined /> 数据库架构设计</Title>
      <Paragraph type="secondary">
        完全免费的多数据源量化平台架构，支持 A股、港股、美股市场数据
      </Paragraph>

      <Row gutter={[16, 16]}>
        {/* 架构概览 */}
        <Col xs={24} lg={12}>
          <Card title={<><CodeOutlined /> 架构概览</>} extra={<Tag color="green">开源</Tag>}>
            <div style={{ padding: 16 }}>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Statistic title="数据源" value={5} suffix="个" />
                  <Progress percent={80} size="small" format={() => '已集成'} />
                </Col>
                <Col span={12}>
                  <Statistic title="数据库" value={4} suffix="个" />
                  <Progress percent={50} size="small" format={() => '已配置'} />
                </Col>
              </Row>
            </div>
            <Divider />
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Statistic title="支持市场" value={4} />
              </Col>
              <Col span={8}>
                <Statistic title="数据类型" value={10} />
              </Col>
              <Col span={8}>
                <Statistic title="月成本" value={0} prefix="¥" />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 核心特性 */}
        <Col xs={24} lg={12}>
          <Card title={<><SafetyOutlined /> 核心特性</>}>
            <Row gutter={[16, 16]}>
              {[
                { icon: <CloudOutlined />, title: '多云部署', desc: '支持 AWS/GCP/Azure' },
                { icon: <ApiOutlined />, title: 'API 优先', desc: 'RESTful + GraphQL' },
                { icon: <ClockCircleOutlined />, title: '实时同步', desc: '增量数据更新' },
                { icon: <BarChartOutlined />, title: '高性能', desc: '百万级数据秒查' },
              ].map((item, i) => (
                <Col xs={12} key={i}>
                  <Card size="small">
                    <Space>
                      {item.icon}
                      <div>
                        <Text strong>{item.title}</Text>
                        <br />
                        <Text type="secondary">{item.desc}</Text>
                      </div>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 数据源表格 */}
        <Col span={24}>
          <Card title="数据源配置">
            <Table 
              dataSource={dataProviders} 
              columns={providerColumns} 
              rowKey="name"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 数据库表格 */}
        <Col span={24}>
          <Card title="数据库配置">
            <Table 
              dataSource={databases} 
              columns={dbColumns} 
              rowKey="name"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* 数据流程 */}
        <Col span={24}>
          <Card title="数据流程">
            <Row gutter={[16, 16]} align="middle">
              {[
                { name: '数据采集', icon: <ApiOutlined /> },
                { name: '数据清洗', icon: <SafetyOutlined /> },
                { name: '因子计算', icon: <BarChartOutlined /> },
                { name: '信号生成', icon: <CodeOutlined /> },
              ].map((item, i, arr) => (
                <React.Fragment key={i}>
                  <Col xs={12} sm={6}>
                    <Card size="small" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 24 }}>{item.icon}</div>
                      <Text>{item.name}</Text>
                    </Card>
                  </Col>
                  {i < arr.length - 1 && (
                    <Col xs={12} sm={6} key={`arrow-${i}`}>
                      <Text style={{ fontSize: 20 }}>→</Text>
                    </Col>
                  )}
                </React.Fragment>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
