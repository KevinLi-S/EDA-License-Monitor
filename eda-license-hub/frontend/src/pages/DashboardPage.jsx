import { Card, Col, Row, Table } from 'antd'
import { useEffect, useState } from 'react'
import api from '../api'

export default function DashboardPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/dashboard').then((r) => setData(r.data))
  }, [])

  return (
    <>
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
