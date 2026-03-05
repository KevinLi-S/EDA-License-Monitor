import { Button, Card, Input, Select, Space, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'

const mockLogs = [
  { id: 'synopsys-1', vendor: 'synopsys', line: 1, content: '1:41:10 (lmgrd) FlexNet Licensing started ...' },
  { id: 'synopsys-900', vendor: 'synopsys', line: 900, content: '1:42:17 (snpslmd) Galaxy-Unsupported Galaxy-Zroute Galil_Solver' },
]

export default function LogsPage() {
  const [rows, setRows] = useState([])
  const [vendor, setVendor] = useState('synopsys')
  const [mode, setMode] = useState('full')
  const [keyword, setKeyword] = useState('')
  const [input, setInput] = useState('')

  const load = async (v = vendor, k = keyword, m = mode) => {
    if (useMock) {
      const out = mockLogs.filter(
        (x) => (v === 'all' || x.vendor === v) && (!k || x.content.toLowerCase().includes(k.toLowerCase())),
      )
      setRows(out)
      return
    }
    const r = await api.get('/license-logs', { params: { vendor: v, keyword: k, mode: m, limit: 5000 } })
    setRows(Array.isArray(r.data) ? r.data : [])
  }

  useEffect(() => {
    load('synopsys', '', 'full')
  }, [])

  return (
    <Card title="License Logs (Real)">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          value={vendor}
          onChange={(v) => {
            setVendor(v)
            load(v, keyword, mode)
          }}
          style={{ width: 180 }}
          options={[
            { label: 'Synopsys', value: 'synopsys' },
            { label: 'Ansys', value: 'ansys' },
            { label: 'All Vendors', value: 'all' },
          ]}
        />
        <Select
          value={mode}
          onChange={(m) => {
            setMode(m)
            load(vendor, keyword, m)
          }}
          style={{ width: 160 }}
          options={[
            { label: 'Full Log', value: 'full' },
            { label: 'Errors Only', value: 'error' },
          ]}
        />
        <Input
          placeholder="Keyword (optional)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={() => {
            setKeyword(input)
            load(vendor, input, mode)
          }}
          style={{ width: 360 }}
        />
        <Button
          type="primary"
          onClick={() => {
            setKeyword(input)
            load(vendor, input, mode)
          }}
        >
          Search Logs
        </Button>
        <Button
          onClick={() => {
            setInput('')
            setKeyword('')
            setVendor('synopsys')
            setMode('full')
            load('synopsys', '', 'full')
          }}
        >
          Reset
        </Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={rows}
        pagination={{ pageSize: 50 }}
        columns={[
          { title: 'Vendor', dataIndex: 'vendor', width: 120, render: (v) => <Tag>{v}</Tag> },
          { title: 'Line', dataIndex: 'line', width: 90 },
          { title: 'Log Content', dataIndex: 'content' },
        ]}
      />
    </Card>
  )
}
