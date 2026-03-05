import { Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'
import { mockServers } from '../mockData'

export default function ServersPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    if (useMock) {
      setRows(mockServers)
      return
    }
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
        {
          title: 'Status',
          dataIndex: 'status',
          render: (v) => <Tag color={v === 'online' ? 'green' : v === 'degraded' ? 'gold' : 'red'}>{v}</Tag>,
        },
        { title: 'Last Seen', dataIndex: 'last_seen_at' },
      ]}
    />
  )
}
