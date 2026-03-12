import { Button, Card, Input, Select, Space, Table, Tag } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'

const mockLogs = [
  { id: 'synopsys-1', vendor: 'synopsys', line: 1, content: '1:41:10 (lmgrd) FlexNet Licensing started ...' },
  { id: 'synopsys-900', vendor: 'synopsys', line: 900, content: '1:42:17 (snpslmd) Galaxy-Unsupported Galaxy-Zroute Galil_Solver' },
  { id: 'ansys-901', vendor: 'ansys', line: 901, content: 'ERROR: Encrypted Communication disabled' },
]

function inferSeverity(content) {
  const text = String(content || '').toLowerCase()
  if (text.includes('tampered') || text.includes('refused')) return 'critical'
  if (text.includes('error') || text.includes('failed') || text.includes('denied')) return 'high'
  if (text.includes('expired') || text.includes('unsupported')) return 'medium'
  return 'info'
}

export default function LogsPage() {
  const [rows, setRows] = useState([])
  const [vendor, setVendor] = useState('all')
  const [mode, setMode] = useState('full')
  const [keyword, setKeyword] = useState('')
  const [input, setInput] = useState('')

  const load = async (v = vendor, k = keyword, m = mode) => {
    if (useMock) {
      const out = mockLogs.filter((x) => (v === 'all' || x.vendor === v) && (!k || x.content.toLowerCase().includes(k.toLowerCase())))
      setRows(out)
      return
    }
    const r = await api.get('/license-logs', { params: { vendor: v, keyword: k, mode: m, limit: 5000 } })
    setRows(Array.isArray(r.data) ? r.data : [])
  }

  useEffect(() => {
    load('all', '', 'full')
  }, [])

  const enhancedRows = useMemo(() => rows.map((r) => ({ ...r, severity: inferSeverity(r.content) })), [rows])

  return (
    <Card title="日志中心 Logs">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select value={vendor} onChange={(v) => { setVendor(v); load(v, keyword, mode) }} style={{ width: 180 }} options={[{ label: 'All Vendors', value: 'all' }, { label: 'Synopsys', value: 'synopsys' }, { label: 'Cadence', value: 'cadence' }, { label: 'Mentor', value: 'mentor' }, { label: 'Ansys', value: 'ansys' }]} />
        <Select value={mode} onChange={(m) => { setMode(m); load(vendor, keyword, m) }} style={{ width: 160 }} options={[{ label: 'Full Log', value: 'full' }, { label: 'Errors Only', value: 'error' }]} />
        <Input placeholder="Keyword (optional)" value={input} onChange={(e) => setInput(e.target.value)} onPressEnter={() => { setKeyword(input); load(vendor, input, mode) }} style={{ width: 360 }} />
        <Button type="primary" onClick={() => { setKeyword(input); load(vendor, input, mode) }}>Search Logs</Button>
        <Button onClick={() => { setInput(''); setKeyword(''); setVendor('all'); setMode('full'); load('all', '', 'full') }}>Reset</Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={enhancedRows}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: 'Vendor', dataIndex: 'vendor', width: 120, render: (v) => <Tag>{v}</Tag> },
          { title: 'Line', dataIndex: 'line', width: 90 },
          { title: 'Severity', dataIndex: 'severity', width: 110, render: (v) => <Tag color={v === 'critical' ? 'red' : v === 'high' ? 'volcano' : v === 'medium' ? 'gold' : 'blue'}>{v}</Tag> },
          { title: 'Log Content', dataIndex: 'content' },
        ]}
      />
    </Card>
  )
}
