import {
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockServerActions, mockServers } from '../mockData'

const statusColor = (v) => {
  if (v === 'online') return 'green'
  if (v === 'degraded' || v === 'restarting') return 'gold'
  return 'red'
}

export default function ServersPage() {
  const [rows, setRows] = useState([])
  const [actionRows, setActionRows] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()

  const vendorOptions = useMemo(() => ['synopsys', 'cadence', 'mentor', 'ansys'], [])

  const load = async () => {
    if (useMock) {
      setRows(mockServers)
      setActionRows(mockServerActions)
      return
    }
    const [serversRes, actionsRes] = await Promise.all([api.get('/servers'), api.get('/server-actions')])
    setRows(serversRes.data)
    setActionRows(actionsRes.data)
  }

  useEffect(() => {
    load()
  }, [])

  const addActionLogLocal = (serverName, action, statusAfter) => {
    setActionRows((prev) => [
      {
        id: Date.now(),
        server: serverName,
        action,
        status_after: statusAfter,
        message: `service ${action === 'restart' ? 'restarting' : action + 'ed'}`,
        created_at: new Date().toISOString(),
      },
      ...prev,
    ])
  }

  const applyActionLocal = (id, action) => {
    const found = rows.find((x) => x.id === id)
    let status = 'degraded'
    if (action === 'start') status = 'online'
    if (action === 'stop') status = 'offline'
    if (action === 'restart') status = 'restarting'

    setRows((prev) => prev.map((s) => (s.id === id ? { ...s, status } : s)))
    addActionLogLocal(found?.name || 'unknown', action, status)
    message.success(`Mock action executed: ${action}`)
  }

  const runAction = async (row, action) => {
    if (useMock) {
      applyActionLocal(row.id, action)
      return
    }
    await api.post(`/servers/${row.id}/action`, { action })
    message.success(`${action} command sent`)
    load()
  }

  const onCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ vendor: 'synopsys', port: 27000 })
    setOpen(true)
  }

  const onEdit = (row) => {
    setEditing(row)
    form.setFieldsValue({
      name: row.name,
      vendor: row.vendor,
      host: row.host,
      port: row.port,
    })
    setOpen(true)
  }

  const onDelete = async (row) => {
    if (useMock) {
      setRows((prev) => prev.filter((x) => x.id !== row.id))
      message.success('Mock delete done')
      return
    }
    await api.delete(`/servers/${row.id}`)
    message.success('Server deleted')
    load()
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    if (useMock) {
      if (editing) {
        setRows((prev) => prev.map((x) => (x.id === editing.id ? { ...x, ...values } : x)))
      } else {
        setRows((prev) => [
          {
            id: Date.now(),
            ...values,
            status: 'offline',
            last_seen_at: new Date().toISOString(),
          },
          ...prev,
        ])
      }
      setOpen(false)
      message.success('Mock save complete')
      return
    }

    if (editing) {
      await api.put(`/servers/${editing.id}`, values)
      message.success('Server updated')
    } else {
      await api.post('/servers', values)
      message.success('Server added')
    }
    setOpen(false)
    load()
  }

  return (
    <Row gutter={16}>
      <Col span={16}>
        <Card
          title="License Servers"
          extra={<Button type="primary" onClick={onCreate}>Add Server</Button>}
        >
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
                render: (v) => <Tag color={statusColor(v)}>{v}</Tag>,
              },
              {
                title: 'Actions',
                render: (_, row) => (
                  <Space wrap>
                    <Popconfirm title={`Start ${row.name}?`} onConfirm={() => runAction(row, 'start')}>
                      <Button size="small" type="primary">Start</Button>
                    </Popconfirm>
                    <Popconfirm title={`Stop ${row.name}?`} onConfirm={() => runAction(row, 'stop')}>
                      <Button size="small" danger>Stop</Button>
                    </Popconfirm>
                    <Popconfirm title={`Restart ${row.name}?`} onConfirm={() => runAction(row, 'restart')}>
                      <Button size="small">Restart</Button>
                    </Popconfirm>
                    <Button size="small" onClick={() => onEdit(row)}>Edit</Button>
                    <Popconfirm title={`Delete ${row.name}?`} onConfirm={() => onDelete(row)}>
                      <Button size="small" danger type="dashed">Delete</Button>
                    </Popconfirm>
                  </Space>
                ),
              },
            ]}
          />
        </Card>
      </Col>
      <Col span={8}>
        <Card title="Operation Logs" style={{ height: '100%' }}>
          <Table
            size="small"
            rowKey="id"
            dataSource={actionRows}
            pagination={{ pageSize: 6 }}
            columns={[
              { title: 'Server', dataIndex: 'server' },
              { title: 'Action', dataIndex: 'action' },
              { title: 'After', dataIndex: 'status_after', render: (v) => <Tag color={statusColor(v)}>{v}</Tag> },
              { title: 'Time', dataIndex: 'created_at' },
            ]}
          />
          <Typography.Text type="secondary">Initial version: command records only. Next we can add operator + result details.</Typography.Text>
        </Card>
      </Col>

      <Modal
        title={editing ? 'Edit Server' : 'Add Server'}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={onSubmit}
        okText="Save"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input placeholder="snps-lic-01" />
          </Form.Item>
          <Form.Item name="vendor" label="Vendor" rules={[{ required: true }]}>
            <Input placeholder={`e.g. ${vendorOptions.join('/')}`} />
          </Form.Item>
          <Form.Item name="host" label="Host" rules={[{ required: true }]}>
            <Input placeholder="10.0.0.11" />
          </Form.Item>
          <Form.Item name="port" label="Port" rules={[{ required: true }]}>
            <InputNumber min={1} max={65535} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Row>
  )
}
