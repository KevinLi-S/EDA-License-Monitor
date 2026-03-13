import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Space,
  Statistic,
  Switch,
  Table,
  Tag,
  Typography,
  Upload,
  message,
} from 'antd'
import { InboxOutlined, UploadOutlined } from '@ant-design/icons'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockServerActions, mockServers } from '../mockData'

const { Dragger } = Upload

const statusColor = (v) => {
  if (v === 'online') return 'green'
  if (v === 'degraded' || v === 'restarting' || v === 'stale') return 'gold'
  if (v === 'unknown') return 'default'
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
  const [detail, setDetail] = useState(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [fileList, setFileList] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [uploadHistory, setUploadHistory] = useState([])
  const [form] = Form.useForm()

  const vendorOptions = useMemo(() => ['synopsys', 'cadence', 'mentor', 'ansys'], [])

  const enrichRows = (items) => items.map((x, idx) => ({
    ...x,
    feature_count: x.feature_count ?? (idx + 2) * 3,
    total_licenses: x.total_licenses ?? (idx + 1) * 80,
    used_licenses: x.used_licenses ?? (idx + 1) * 42,
    risk_level: x.risk_level ?? (x.status === 'offline' ? 'high' : x.status === 'online' ? 'low' : 'medium'),
  }))

  const load = async () => {
    if (useMock) {
      setRows(enrichRows(mockServers))
      setActionRows(mockServerActions)
      return
    }
    const [serversRes, actionsRes] = await Promise.all([api.get('/servers'), api.get('/server-actions')])
    setRows(enrichRows(serversRes.data || []))
    setActionRows(actionsRes.data || [])
  }

  useEffect(() => {
    load()
  }, [])

  const stats = useMemo(() => ({
    total: rows.length,
    online: rows.filter((x) => x.status === 'online').length,
    offline: rows.filter((x) => x.status === 'offline').length,
    unstable: rows.filter((x) => x.status === 'degraded' || x.status === 'restarting' || x.status === 'stale').length,
  }), [rows])

  const addActionLogLocal = (serverName, action, statusAfter) => {
    setActionRows((prev) => [{ id: Date.now(), server: serverName, action, status_after: statusAfter, message: `service ${action === 'restart' ? 'restarting' : action + 'ed'}`, created_at: new Date().toISOString() }, ...prev])
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

  const onUpload = async () => {
    const fobj = fileList[0]?.originFileObj
    if (!fobj) {
      message.warning('Please select a license file first')
      return
    }

    if (useMock) {
      const mockResult = { ok: true, filename: fobj.name, parsed_features: 12, server: 'snps-lic-01', port: 27000 }
      setUploadResult(mockResult)
      setUploadHistory((prev) => [{ key: Date.now(), filename: fobj.name, parsed: 12, server: 'snps-lic-01', time: new Date().toLocaleString() }, ...prev])
      message.success('Mock upload completed')
      return
    }

    const fd = new FormData()
    fd.append('file', fobj)
    setUploading(true)
    try {
      const { data } = await api.post('/license/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setUploadResult(data)
      setUploadHistory((prev) => [{ key: Date.now(), filename: data.filename, parsed: data.parsed_features, server: data.server, time: new Date().toLocaleString() }, ...prev])
      message.success(`Uploaded successfully, parsed ${data?.parsed_features ?? 0} features`)
      load()
    } finally {
      setUploading(false)
    }
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
      else setRows((prev) => [{ id: Date.now(), ...values, status: 'offline', last_seen_at: new Date().toISOString(), feature_count: 0, total_licenses: 0, used_licenses: 0, risk_level: 'low' }, ...prev])
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
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Alert type="info" showIcon message="Operations" description="Dry Run is enabled by default. Preview commands before real Start / Stop / Restart actions." />

      <Row gutter={14}>
        <Col span={6}><Card><Statistic title="Total Servers" value={stats.total} /></Card></Col>
        <Col span={6}><Card><Statistic title="Online" value={stats.online} /></Card></Col>
        <Col span={6}><Card><Statistic title="Offline" value={stats.offline} /></Card></Col>
        <Col span={6}><Card><Statistic title="Unstable / In Progress" value={stats.unstable} /></Card></Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="License Upload">
            <Typography.Text type="secondary">
              Upload a license file here to refresh license data and verify the end-to-end linkage.
            </Typography.Text>
            <Divider />
            <Dragger
              beforeUpload={() => false}
              maxCount={1}
              fileList={fileList}
              onChange={({ fileList: next }) => setFileList(next.slice(-1))}
              style={{ padding: 16 }}
            >
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p className="ant-upload-text">Click or drag a .lic / .dat / .txt file here</p>
              <p className="ant-upload-hint">Use a real license file when validating live data.</p>
            </Dragger>
            <Space style={{ marginTop: 16 }}>
              <Button type="primary" icon={<UploadOutlined />} onClick={onUpload} loading={uploading}>Upload and Parse</Button>
              <Button onClick={() => { setFileList([]); setUploadResult(null) }}>Clear</Button>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Upload Result" style={{ height: '100%' }}>
            {uploadResult ? (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="File">{uploadResult.filename}</Descriptions.Item>
                <Descriptions.Item label="Server">{uploadResult.server}</Descriptions.Item>
                <Descriptions.Item label="Port">{uploadResult.port}</Descriptions.Item>
                <Descriptions.Item label="Parsed Features">{uploadResult.parsed_features}</Descriptions.Item>
                <Descriptions.Item label="Status">{uploadResult.ok ? 'Success' : 'Failed'}</Descriptions.Item>
              </Descriptions>
            ) : (
              <Typography.Text type="secondary">Upload a file to see the parse result here.</Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={16}>
          <Card
            title="License Servers"
            extra={(
              <Space>
                <span>Dry Run</span>
                <Switch checked={dryRun} onChange={setDryRun} />
                <Button type="primary" onClick={onCreate}>Add Server</Button>
              </Space>
            )}
          >
            <Table
              rowKey="id"
              dataSource={rows}
              pagination={{ pageSize: 10 }}
              columns={[
                {
                  title: 'Name',
                  dataIndex: 'name',
                  render: (v, row) => <Button type="link" onClick={() => { setDetail(row); setDetailOpen(true) }}>{v}</Button>,
                },
                { title: 'Vendor', dataIndex: 'vendor' },
                { title: 'Host', dataIndex: 'host' },
                { title: 'Port', dataIndex: 'port', width: 80 },
                { title: 'Status', dataIndex: 'status', width: 110, render: (v) => <Tag color={statusColor(v)}>{v}</Tag> },
                { title: 'Features', dataIndex: 'feature_count', width: 90 },
                { title: 'Used / Total', width: 130, render: (_, r) => `${r.used_licenses}/${r.total_licenses}` },
                { title: 'Risk', dataIndex: 'risk_level', width: 90, render: (v) => <Tag color={v === 'high' ? 'red' : v === 'medium' ? 'gold' : 'green'}>{v}</Tag> },
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
                { title: 'Action', dataIndex: 'action', width: 80 },
                { title: 'After', dataIndex: 'status_after', width: 100, render: (v) => <Tag color={statusColor(v)}>{v}</Tag> },
                { title: 'Time', dataIndex: 'created_at' },
              ]}
            />
            <Typography.Text type="secondary">Click a server name to view details.</Typography.Text>
          </Card>
        </Col>
      </Row>

      <Modal title="Execution Preview" open={previewOpen} onCancel={() => setPreviewOpen(false)} footer={<Button onClick={() => setPreviewOpen(false)}>Close</Button>}>
        {preview && (
          <Descriptions column={1} size="small" bordered>
            <Descriptions.Item label="Vendor">{preview.vendor}</Descriptions.Item>
            <Descriptions.Item label="Action">{preview.action}</Descriptions.Item>
            <Descriptions.Item label="Command"><code>{preview.command}</code></Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      <Modal title={editing ? 'Edit Server' : 'Add Server'} open={open} onCancel={() => setOpen(false)} onOk={onSubmit} okText="Save">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}><Input placeholder="snps-lic-01" /></Form.Item>
          <Form.Item name="vendor" label="Vendor" rules={[{ required: true }]}><Input placeholder={`e.g. ${vendorOptions.join('/')}`} /></Form.Item>
          <Form.Item name="host" label="Host" rules={[{ required: true }]}><Input placeholder="10.0.0.11" /></Form.Item>
          <Form.Item name="port" label="Port" rules={[{ required: true }]}><InputNumber min={1} max={65535} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>

      <Modal title="Server Detail" open={detailOpen} onCancel={() => setDetailOpen(false)} footer={<Button onClick={() => setDetailOpen(false)}>Close</Button>} width={720}>
        {detail && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="Name">{detail.name}</Descriptions.Item>
            <Descriptions.Item label="Vendor">{detail.vendor}</Descriptions.Item>
            <Descriptions.Item label="Host">{detail.host}</Descriptions.Item>
            <Descriptions.Item label="Port">{detail.port}</Descriptions.Item>
            <Descriptions.Item label="Status"><Tag color={statusColor(detail.status)}>{detail.status}</Tag></Descriptions.Item>
            <Descriptions.Item label="Last Seen">{detail.last_seen_at || '-'}</Descriptions.Item>
            <Descriptions.Item label="Feature Count">{detail.feature_count}</Descriptions.Item>
            <Descriptions.Item label="Used / Total">{detail.used_licenses}/{detail.total_licenses}</Descriptions.Item>
            <Descriptions.Item label="Risk Level"><Tag color={detail.risk_level === 'high' ? 'red' : detail.risk_level === 'medium' ? 'gold' : 'green'}>{detail.risk_level}</Tag></Descriptions.Item>
            <Descriptions.Item label="Notes">This is the first aggregated detail view and can be extended with related alerts, logs, and trends.</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </Space>
  )
}
