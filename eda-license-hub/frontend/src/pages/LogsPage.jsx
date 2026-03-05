import { Button, Card, Input, Select, Space, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'

const mockLogs = [
  { id: 'ansys-55', vendor: 'ansys', line: 55, content: 'CVD License file has been Tampered.So no.of license Restricted to Original count' },
  { id: 'synopsys-900', vendor: 'synopsys', line: 900, content: 'Galaxy-Unsupported Galaxy-Zroute Galil_Solver' },
]

export default function LogsPage() {
  const [rows, setRows] = useState([])
  const [vendor, setVendor] = useState('all')
  const [keyword, setKeyword] = useState('')
  const [input, setInput] = useState('')

  const load = async (v = vendor, k = keyword) => {
    if (useMock) {
      setRows(mockLogs.filter((x) => (v === 'all' || x.vendor === v) && (!k || x.content.toLowerCase().includes(k.toLowerCase()))))
      return
    }
    const r = await api.get('/license-logs', { params: { vendor: v, keyword: k } })
    setRows(Array.isArray(r.data) ? r.data : [])
  }

  useEffect(() => {
    load('all', '')
  }, [])

  return (
    <Card title="License Error Logs">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          value={vendor}
          onChange={(v) => { setVendor(v); load(v, keyword) }}
          style={{ width: 180 }}
          options={[
            { label: 'All Vendors', value: 'all' },
            { label: 'Synopsys', value: 'synopsys' },
            { label: 'Ansys', value: 'ansys' },
          ]}
        />
        <Input
          placeholder="Keyword (e.g. tampered/denied/error)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={() => { setKeyword(input); load(vendor, input) }}
          style={{ width: 360 }}
        />
        <Button type="primary" onClick={() => { setKeyword(input); load(vendor, input) }}>Search Logs</Button>
        <Button onClick={() => { setInput(''); setKeyword(''); setVendor('all'); load('all', '') }}>Reset</Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={rows}
        columns={[
          { title: 'Vendor', dataIndex: 'vendor', width: 120, render: (v) => <Tag>{v}</Tag> },
          { title: 'Line', dataIndex: 'line', width: 90 },
          { title: 'Log Content', dataIndex: 'content' },
        ]}
      />
    </Card>
  )
}
