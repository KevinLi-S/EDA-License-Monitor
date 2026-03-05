import { Card, Col, Row, Table, Tag } from 'antd'
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
        <Col span={8}><Card title="Vendors">{data?.vendor_count ?? '-'}</Card></Col>
        <Col span={8}><Card title="Servers">{data?.server_count ?? '-'}</Card></Col>
        <Col span={8}><Card title="Open Alerts">{data?.open_alerts ?? '-'}</Card></Col>
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
          ]}
          pagination={false}
        />
      </Card>
    </>
  )
}
