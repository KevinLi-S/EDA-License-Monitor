import { Alert, Card, Col, Progress, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockDashboard, mockServers, mockAlerts, mockServerActions } from '../mockData'

const sevColor = { critical: 'red', high: 'volcano', medium: 'gold' }
const { Text } = Typography

const glass = {
  borderRadius: 14,
  border: '1px solid #eef2ff',
  boxShadow: '0 8px 24px rgba(20, 30, 55, 0.06)',
}

function ScoreCard({ title, value, color = '#1677ff', suffix, hint }) {
  return (
    <Card style={{ ...glass, background: `linear-gradient(135deg, ${color}12 0%, #ffffff 70%)` }} bodyStyle={{ padding: 18 }}>
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
  const [servers, setServers] = useState([])
  const [alerts, setAlerts] = useState([])
  const [actions, setActions] = useState([])
  const [vendorFilter, setVendorFilter] = useState('all')

  useEffect(() => {
    if (useMock) {
      setData(mockDashboard)
      setServers(mockServers)
      setAlerts(mockAlerts)
      setActions(mockServerActions)
      return
    }
    Promise.all([
      api.get('/dashboard'),
      api.get('/servers').catch(() => ({ data: [] })),
      api.get('/alerts').catch(() => ({ data: [] })),
      api.get('/server-actions').catch(() => ({ data: [] })),
    ]).then(([dashboardRes, serversRes, alertsRes, actionsRes]) => {
      setData(dashboardRes.data)
      setServers(serversRes.data || [])
      setAlerts(alertsRes.data || [])
      setActions(actionsRes.data || [])
    })
  }, [])

  const filteredTopFeatures = useMemo(() => {
    const list = data?.top_busy_features || []
    if (vendorFilter === 'all') return list
    return list.filter((x) => String(x.vendor).toLowerCase() === vendorFilter)
  }, [data, vendorFilter])

  const serverStats = useMemo(() => {
    const rows = servers || []
    const online = rows.filter((x) => x.status === 'online').length
    const offline = rows.filter((x) => x.status === 'offline').length
    const restarting = rows.filter((x) => x.status === 'restarting' || x.status === 'degraded').length
    return { online, offline, restarting }
  }, [servers])

  const hotFeatureCount = useMemo(() => filteredTopFeatures.filter((x) => (x.used / Math.max(x.total, 1)) >= 0.85).length, [filteredTopFeatures])

  const riskCounts = useMemo(() => {
    const list = data?.risk_summary?.findings || []
    return {
      critical: list.filter((x) => x.severity === 'critical').length,
      high: list.filter((x) => x.severity === 'high').length,
      medium: list.filter((x) => x.severity === 'medium').length,
    }
  }, [data])

  const recentEvents = useMemo(() => {
    const a = (alerts || []).slice(0, 3).map((x) => ({ type: 'alert', title: x.type, detail: x.message, time: x.created_at }))
    const b = (actions || []).slice(0, 3).map((x) => ({ type: 'action', title: `${x.server} ${x.action}`, detail: x.message, time: x.created_at }))
    return [...a, ...b].sort((x, y) => String(y.time).localeCompare(String(x.time))).slice(0, 6)
  }, [alerts, actions])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card style={{ ...glass, background: 'linear-gradient(100deg, #0f172a 0%, #1d4ed8 45%, #0ea5e9 100%)', color: '#fff' }} bodyStyle={{ padding: 18 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Typography.Title level={4} style={{ margin: 0, color: '#fff' }}>EDA License Operations Dashboard</Typography.Title>
            <Text style={{ color: 'rgba(255,255,255,.88)' }}>面向测试环境 192.168.110.128 的统一监控视图：容量、健康、告警、风险一屏总览</Text>
          </Col>
          <Col>
            {useMock ? <Tag color="blue">Mock Mode</Tag> : <Tag color="green">Live API</Tag>}
          </Col>
        </Row>
      </Card>

      <Alert
        type="info"
        showIcon
        message="当前演示重点"
        description="当前页面已切到真实数据展示。由于暂未接入实时 checkout/in-use 采集链路，Usage/Used 暂按保守值 0 展示；此页重点看容量、服务状态、风险摘要和最近事件。"
      />

      <Row gutter={14}>
        <Col span={6}><ScoreCard title="Vendors" value={data?.vendor_count} color="#2563eb" hint="Connected ecosystems" /></Col>
        <Col span={6}><ScoreCard title="Servers" value={data?.server_count} color="#0891b2" hint={`online ${serverStats.online} / offline ${serverStats.offline}`} /></Col>
        <Col span={6}><ScoreCard title="Open Alerts" value={data?.open_alerts} color="#dc2626" hint="Operational alerts pending" /></Col>
        <Col span={6}><ScoreCard title="Critical Risks" value={data?.risk_summary?.critical} color="#b91c1c" hint="Need immediate attention" /></Col>
      </Row>

      <Row gutter={14}>
        <Col span={6}><ScoreCard title="Online Servers" value={serverStats.online} color="#16a34a" hint="Healthy nodes" /></Col>
        <Col span={6}><ScoreCard title="Offline Servers" value={serverStats.offline} color="#ef4444" hint="Need inspection" /></Col>
        <Col span={6}><ScoreCard title="Restarting / Degraded" value={serverStats.restarting} color="#f59e0b" hint="Action in progress or unstable" /></Col>
        <Col span={6}><ScoreCard title="Hot Features" value={hotFeatureCount} color="#7c3aed" hint="需要实时使用采集后才有意义" /></Col>
      </Row>

      <Row gutter={14}>
        <Col span={16}>
          <Card
            title="Feature Capacity Samples"
            style={glass}
            extra={<Select value={vendorFilter} onChange={setVendorFilter} style={{ width: 180 }} options={[{ label: 'All Vendors', value: 'all' }, { label: 'Synopsys', value: 'synopsys' }, { label: 'Cadence', value: 'cadence' }, { label: 'Mentor', value: 'mentor' }, { label: 'Ansys', value: 'ansys' }]} />}
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
                    return <Progress size="small" percent={p} status={status} format={(percent) => `${percent}% (实时占用未接入)`} />
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
              pagination={{ pageSize: 4 }}
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

      <Card title="Recent Events" style={glass}>
        <Table
          rowKey={(r, idx) => `${r.type}-${idx}`}
          dataSource={recentEvents}
          pagination={false}
          columns={[
            { title: 'Type', dataIndex: 'type', width: 100, render: (v) => <Tag color={v === 'alert' ? 'red' : 'blue'}>{v}</Tag> },
            { title: 'Title', dataIndex: 'title', width: 220 },
            { title: 'Detail', dataIndex: 'detail' },
            { title: 'Time', dataIndex: 'time', width: 180 },
          ]}
        />
      </Card>
    </Space>
  )
}
