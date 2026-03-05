import { Table } from 'antd'
import { useEffect, useState } from 'react'
import api from '../api'

export default function ServersPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/servers').then((r) => setRows(r.data))
  }, [])

  return (
    <Table
      rowKey="id"
      dataSource={rows}
      columns={[
        { title: 'Name', dataIndex: 'name' },
        { title: 'Vendor', dataIndex: 'vendor' },
        { title: 'Host', dataIndex: 'host' },
        { title: 'Port', dataIndex: 'port' },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Last Seen', dataIndex: 'last_seen_at' },
      ]}
    />
  )
}
