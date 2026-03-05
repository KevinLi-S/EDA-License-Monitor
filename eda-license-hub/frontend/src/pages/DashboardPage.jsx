import { Card, Col, Progress, Row, Statistic, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'
import { mockDashboard } from '../mockData'

export default function DashboardPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (useMock) {
      setData(mockDashboard)
      return
    }
    api.get('/dashboard').then((r) => setData(r.data))
  }, [])

  return (
    <>
      <Row gutter={16} style={{ marginBottom: 12 }}>
        <Col span={24}>{useMock ? <Tag color="blue">Mock Mode</Tag> : <Tag color="green">Live API</Tag>}</Col>
      </Row>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="Vendors" value={data?.vendor_count ?? 0} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Servers" value={data?.server_count ?? 0} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Open Alerts" value={data?.open_alerts ?? 0} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
      </Row>
      <Card title="Top Busy Features" style={{ marginTop: 16 }}>
        <Table
          rowKey={(r) => `${r.feature}-${r.server}-${r.collected_at}`}
          dataSource={data?.top_busy_features || []}
          columns={[
            { title: 'Feature', dataIndex: 'feature' },
            { title: 'Vendor', dataIndex: 'vendor' },
            { title: 'Server', dataIndex: 'server' },
            { title: 'Total', dataIndex: 'total' },
            { title: 'Used', dataIndex: 'used' },
            { title: 'Free', dataIndex: 'free' },
            {
              title: 'Utilization',
              render: (_, r) => <Progress size="small" percent={Math.round((r.used / Math.max(r.total, 1)) * 100)} />,
            },
          ]}
          pagination={false}
        />
      </Card>
    </>
  )
}
