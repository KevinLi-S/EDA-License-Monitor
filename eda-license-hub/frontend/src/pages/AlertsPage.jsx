import { Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api from '../api'

export default function AlertsPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/alerts').then((r) => setRows(r.data))
  }, [])

  return (
    <Table
      rowKey="id"
      dataSource={rows}
      columns={[
        { title: 'Type', dataIndex: 'type' },
        { title: 'Severity', dataIndex: 'severity', render: (v) => <Tag color={v === 'high' ? 'red' : 'gold'}>{v}</Tag> },
        { title: 'Message', dataIndex: 'message' },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Created At', dataIndex: 'created_at' },
      ]}
    />
  )
}
