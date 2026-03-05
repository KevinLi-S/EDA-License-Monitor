import {
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  Upload,
  message,
} from 'antd'
import { UploadOutlined } from '@ant-design/icons'
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
  const [dryRun, setDryRun] = useState(true)
  const [preview, setPreview] = useState(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [uploadFileList, setUploadFileList] = useState([])
  const [uploading, setUploading] = useState(false)
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

  const openPreview = async (row, action) => {
    if (useMock) {
      setPreview({ server_id: row.id, vendor: row.vendor, action, command: `mockctl ${action} --server ${row.host}:${row.port}` })
      setPreviewOpen(true)
      return
    }
    const r = await api.get(`/servers/${row.id}/action-preview`, { params: { action } })
    setPreview(r.data)
    setPreviewOpen(true)
  }

  const runAction = async (row, action) => {
    if (useMock) {
      applyActionLocal(row.id, action)
      return
    }
    const res = await api.post(`/servers/${row.id}/action`, { action, dry_run: dryRun })
    if (res.data?.dry_run) message.info(`Dry run: ${action} previewed, no execution`)
    else if (res.data?.ok) message.success(`${action} command executed`)
    else message.error(`Real execution failed: ${res.data?.stderr || 'command not available in runtime'}`)
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
    form.setFieldsValue({ name: row.name, vendor: row.vendor, host: row.host, port: row.port })
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
      if (editing) setRows((prev) => prev.map((x) => (x.id === editing.id ? { ...x, ...values } : x)))
      else {
        setRows((prev) => [{ id: Date.now(), ...values, status: 'offline', last_seen_at: new Date().toISOString() }, ...prev])
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

  const doUploadLicense = async () => {
    const f = uploadFileList[0]?.originFileObj
    if (!f) {
      message.warning('Please select a license file first')
      return
    }

    if (useMock) {
      message.success('Mock upload done. Go to License Keys page to view updates.')
      setUploadOpen(false)
      setUploadFileList([])
      return
    }

    const fd = new FormData()
    fd.append('file', f)
    setUploading(true)
    try {
      const r = await api.post('/license/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      message.success(`Upload success: parsed ${r.data?.parsed_features ?? 0} features`)
      setUploadOpen(false)
      setUploadFileList([])
      load()
    } finally {
      setUploading(false)
    }
  }

  return (
    <Row gutter={16}>
      <Col span={16}>
        <Card
          title="License Servers"
          extra={(
            <Space>
              <span>Dry Run</span>
              <Switch checked={dryRun} onChange={setDryRun} />
              <Button onClick={() => setUploadOpen(true)} icon={<UploadOutlined />}>Upload License</Button>
              <Button type="primary" onClick={onCreate}>Add Server</Button>
            </Space>
          )}
        >
          <Table
            rowKey="id"
            dataSource={rows}
            columns={[
              { title: 'Name', dataIndex: 'name' },
              { title: 'Vendor', dataIndex: 'vendor' },
              { title: 'Host', dataIndex: 'host' },
              { title: 'Port', dataIndex: 'port' },
              { title: 'Status', dataIndex: 'status', render: (v) => <Tag color={statusColor(v)}>{v}</Tag> },
              {
                title: 'Actions',
                render: (_, row) => (
                  <Space wrap>
                    <Popconfirm title={`Start ${row.name}?`} onConfirm={() => runAction(row, 'start')}><Button size="small" type="primary">Start</Button></Popconfirm>
                    <Popconfirm title={`Stop ${row.name}?`} onConfirm={() => runAction(row, 'stop')}><Button size="small" danger>Stop</Button></Popconfirm>
                    <Popconfirm title={`Restart ${row.name}?`} onConfirm={() => runAction(row, 'restart')}><Button size="small">Restart</Button></Popconfirm>
                    <Button size="small" onClick={() => openPreview(row, 'restart')}>Preview Cmd</Button>
                    <Button size="small" onClick={() => onEdit(row)}>Edit</Button>
                    <Popconfirm title={`Delete ${row.name}?`} onConfirm={() => onDelete(row)}><Button size="small" danger type="dashed">Delete</Button></Popconfirm>
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
          <Typography.Text type="secondary">Now supports license file upload for real-time key refresh.</Typography.Text>
        </Card>
      </Col>

      <Modal title="Execution Preview" open={previewOpen} onCancel={() => setPreviewOpen(false)} footer={<Button onClick={() => setPreviewOpen(false)}>Close</Button>}>
        {preview && (
          <Descriptions column={1} size="small" bordered>
            <Descriptions.Item label="Vendor">{preview.vendor}</Descriptions.Item>
            <Descriptions.Item label="Action">{preview.action}</Descriptions.Item>
            <Descriptions.Item label="Command"><code>{preview.command}</code></Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      <Modal title="Upload License File" open={uploadOpen} onCancel={() => setUploadOpen(false)} onOk={doUploadLicense} confirmLoading={uploading} okText="Upload & Refresh">
        <Upload
          beforeUpload={() => false}
          fileList={uploadFileList}
          onChange={({ fileList }) => setUploadFileList(fileList.slice(-1))}
          maxCount={1}
        >
          <Button icon={<UploadOutlined />}>Select license file (.lic / .dat / .txt)</Button>
        </Upload>
      </Modal>

      <Modal title={editing ? 'Edit Server' : 'Add Server'} open={open} onCancel={() => setOpen(false)} onOk={onSubmit} okText="Save">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input placeholder="snps-lic-01" /></Form.Item>
          <Form.Item name="vendor" label="Vendor" rules={[{ required: true }]}><Input placeholder={`e.g. ${vendorOptions.join('/')}`} /></Form.Item>
          <Form.Item name="host" label="Host" rules={[{ required: true }]}><Input placeholder="10.0.0.11" /></Form.Item>
          <Form.Item name="port" label="Port" rules={[{ required: true }]}><InputNumber min={1} max={65535} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </Row>
  )
}
