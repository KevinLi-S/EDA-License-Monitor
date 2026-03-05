import { Button, Card, Space, Table, Tag, message } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'
import { mockServers } from '../mockData'

export default function ServersPage() {
  const [rows, setRows] = useState([])

  const load = () => {
    if (useMock) {
      setRows(mockServers)
      return
    }
    api.get('/servers').then((r) => setRows(r.data))
  }

  useEffect(() => {
    load()
  }, [])

  const applyActionLocal = (id, action) => {
    setRows((prev) =>
      prev.map((s) => {
        if (s.id !== id) return s
        if (action === 'start') return { ...s, status: 'online' }
        if (action === 'stop') return { ...s, status: 'offline' }
        return { ...s, status: 'degraded' }
      }),
    )
    message.success(`Mock action executed: ${action}`)
  }

  const runAction = async (id, action) => {
    if (useMock) {
      applyActionLocal(id, action)
      return
    }
    await api.post(`/servers/${id}/action`, { action })
    message.success(`${action} command sent`)
    load()
  }

  return (
    <Card title="License Servers">
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
          {
            title: 'Actions',
            render: (_, row) => (
              <Space>
                <Button size="small" type="primary" onClick={() => runAction(row.id, 'start')}>Start</Button>
                <Button size="small" danger onClick={() => runAction(row.id, 'stop')}>Stop</Button>
                <Button size="small" onClick={() => runAction(row.id, 'restart')}>Restart</Button>
              </Space>
            ),
          },
        ]}
      />
    </Card>
  )
}
