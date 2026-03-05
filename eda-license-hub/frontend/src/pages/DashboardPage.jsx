import { Card, Col, Progress, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockDashboard } from '../mockData'

const sevColor = { critical: 'red', high: 'volcano', medium: 'gold' }
const { Text } = Typography

const glass = {
  borderRadius: 14,
  border: '1px solid #eef2ff',
  boxShadow: '0 8px 24px rgba(20, 30, 55, 0.06)',
}

function ScoreCard({ title, value, color = '#1677ff', suffix, hint }) {
  return (
    <Card
      style={{
        ...glass,
        background: `linear-gradient(135deg, ${color}12 0%, #ffffff 70%)`,
      }}
      bodyStyle={{ padding: 18 }}
    >
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Text type="secondary">{title}</Text>
        <Statistic value={value ?? 0} suffix={suffix} valueStyle={{ color }} />
        {hint ? <Text type="secondary">{hint}</Text> : null}
      </Space>
    </Card>
  )
}

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [vendorFilter, setVendorFilter] = useState('all')

  useEffect(() => {
    if (useMock) {
      setData(mockDashboard)
      return
    }
    api.get('/dashboard').then((r) => setData(r.data))
  }, [])

  const filteredTopFeatures = useMemo(() => {
    const list = data?.top_busy_features || []
    if (vendorFilter === 'all') return list
    return list.filter((x) => String(x.vendor).toLowerCase() === vendorFilter)
  }, [data, vendorFilter])

  const riskCounts = useMemo(() => {
    const list = data?.risk_summary?.findings || []
    return {
      critical: list.filter((x) => x.severity === 'critical').length,
      high: list.filter((x) => x.severity === 'high').length,
      medium: list.filter((x) => x.severity === 'medium').length,
    }
  }, [data])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card
        style={{
          ...glass,
          background: 'linear-gradient(100deg, #0f172a 0%, #1d4ed8 45%, #0ea5e9 100%)',
          color: '#fff',
        }}
        bodyStyle={{ padding: 18 }}
      >
        <Row align="middle" justify="space-between">
          <Col>
            <Typography.Title level={4} style={{ margin: 0, color: '#fff' }}>
              EDA License Operations Dashboard
            </Typography.Title>
            <Text style={{ color: 'rgba(255,255,255,.88)' }}>
              Unified view of capacity, usage pressure and log-derived risks
            </Text>
          </Col>
          <Col>
            {useMock ? <Tag color="blue">Mock Mode</Tag> : <Tag color="green">Live API</Tag>}
          </Col>
        </Row>
      </Card>

      <Row gutter={14}>
        <Col span={6}><ScoreCard title="Vendors" value={data?.vendor_count} color="#2563eb" hint="Connected ecosystems" /></Col>
        <Col span={6}><ScoreCard title="Servers" value={data?.server_count} color="#0891b2" hint="License managers online/offline" /></Col>
        <Col span={6}><ScoreCard title="Open Alerts" value={data?.open_alerts} color="#dc2626" hint="Operational alerts pending" /></Col>
        <Col span={6}><ScoreCard title="Critical Risks" value={data?.risk_summary?.critical} color="#b91c1c" hint="Need immediate attention" /></Col>
      </Row>

      <Row gutter={14}>
        <Col span={16}>
          <Card
            title="Top Busy Features"
            style={glass}
            extra={
              <Select
                value={vendorFilter}
                onChange={setVendorFilter}
                style={{ width: 180 }}
                options={[
                  { label: 'All Vendors', value: 'all' },
                  { label: 'Synopsys', value: 'synopsys' },
                  { label: 'Cadence', value: 'cadence' },
                ]}
              />
            }
          >
            <Table
              rowKey={(r) => `${r.feature}-${r.server}-${r.collected_at}`}
              dataSource={filteredTopFeatures}
              pagination={false}
              columns={[
                { title: 'Feature', dataIndex: 'feature' },
                { title: 'Vendor', dataIndex: 'vendor' },
                { title: 'Server', dataIndex: 'server' },
                { title: 'Total', dataIndex: 'total', width: 80 },
                { title: 'Used', dataIndex: 'used', width: 80 },
                { title: 'Free', dataIndex: 'free', width: 80 },
                {
                  title: 'Utilization',
                  render: (_, r) => {
                    const p = Math.round((r.used / Math.max(r.total, 1)) * 100)
                    const status = p >= 90 ? 'exception' : p >= 75 ? 'active' : 'normal'
                    return <Progress size="small" percent={p} status={status} />
                  },
                },
              ]}
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card title="Risk Overview" style={{ ...glass, marginBottom: 14 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Row justify="space-between"><Text>Critical</Text><Tag color="red">{riskCounts.critical}</Tag></Row>
              <Row justify="space-between"><Text>High</Text><Tag color="volcano">{riskCounts.high}</Tag></Row>
              <Row justify="space-between"><Text>Medium</Text><Tag color="gold">{riskCounts.medium}</Tag></Row>
            </Space>
          </Card>

          <Card title="Risk Findings" style={glass}>
            <Table
              size="small"
              rowKey={(r) => `${r.vendor}-${r.issue}`}
              dataSource={data?.risk_summary?.findings || []}
              pagination={{ pageSize: 5 }}
              columns={[
                { title: 'Vendor', dataIndex: 'vendor', width: 90 },
                {
                  title: 'Issue',
                  dataIndex: 'issue',
                  render: (v, row) => (
                    <Space direction="vertical" size={0}>
                      <Text>{v}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>{row.detail}</Text>
                    </Space>
                  ),
                },
                { title: 'S', dataIndex: 'severity', width: 66, render: (v) => <Tag color={sevColor[v] || 'default'}>{v}</Tag> },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  )
}
