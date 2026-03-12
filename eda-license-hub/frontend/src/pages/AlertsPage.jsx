import { Card, Col, Row, Select, Space, Statistic, Table, Tag } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockAlerts } from '../mockData'

const colorMap = { critical: 'red', high: 'volcano', medium: 'gold', low: 'blue' }

export default function AlertsPage() {
  const [rows, setRows] = useState([])
  const [severity, setSeverity] = useState('all')
  const [status, setStatus] = useState('all')

  useEffect(() => {
    if (useMock) {
      setRows(mockAlerts)
      return
    }
    api.get('/alerts').then((r) => setRows(r.data))
  }, [])

  const filtered = useMemo(() => rows.filter((x) => (severity === 'all' || x.severity === severity) && (status === 'all' || x.status === status)), [rows, severity, status])

  const stats = useMemo(() => ({
    total: rows.length,
    critical: rows.filter((x) => x.severity === 'critical').length,
    high: rows.filter((x) => x.severity === 'high').length,
    open: rows.filter((x) => x.status === 'open').length,
  }), [rows])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Row gutter={14}>
        <Col span={6}><Card><Statistic title="Alerts 总数" value={stats.total} /></Card></Col>
        <Col span={6}><Card><Statistic title="Critical" value={stats.critical} /></Card></Col>
        <Col span={6}><Card><Statistic title="High" value={stats.high} /></Card></Col>
        <Col span={6}><Card><Statistic title="Open" value={stats.open} /></Card></Col>
      </Row>

      <Card title="告警中心 Alerts">
        <Space style={{ marginBottom: 12 }} wrap>
          <Select value={severity} onChange={setSeverity} style={{ width: 180 }} options={[{ label: 'All Severity', value: 'all' }, { label: 'Critical', value: 'critical' }, { label: 'High', value: 'high' }, { label: 'Medium', value: 'medium' }, { label: 'Low', value: 'low' }]} />
          <Select value={status} onChange={setStatus} style={{ width: 180 }} options={[{ label: 'All Status', value: 'all' }, { label: 'Open', value: 'open' }, { label: 'Closed', value: 'closed' }]} />
        </Space>
        <Table
          rowKey="id"
          dataSource={filtered}
          columns={[
            { title: 'Type', dataIndex: 'type', width: 160 },
            { title: 'Severity', dataIndex: 'severity', width: 120, render: (v) => <Tag color={colorMap[v] || 'default'}>{v}</Tag> },
            { title: 'Status', dataIndex: 'status', width: 100, render: (v) => <Tag color={v === 'open' ? 'red' : 'green'}>{v}</Tag> },
            { title: 'Message', dataIndex: 'message' },
            { title: 'Created At', dataIndex: 'created_at', width: 180 },
          ]}
        />
      </Card>
    </Space>
  )
}
