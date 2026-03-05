import { Button, Card, Input, Progress, Select, Space, Table, Tag } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockLicenseKeys } from '../mockData'

export default function LicenseKeysPage() {
  const [rows, setRows] = useState([])
  const [keyword, setKeyword] = useState('')
  const [searchText, setSearchText] = useState('')
  const [vendorFilter, setVendorFilter] = useState('all')

  const load = async () => {
    try {
      if (useMock) {
        setRows(mockLicenseKeys)
        return
      }
      const r = await api.get('/license-keys')
      setRows(Array.isArray(r.data) ? r.data : [])
    } catch (e) {
      console.error(e)
      setRows([])
      window?.alert?.('License Keys loading failed. Please refresh backend and try again.')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = useMemo(() => {
    const k = searchText.trim().toLowerCase()
    let base = rows
    if (vendorFilter !== 'all') {
      base = base.filter((r) => String(r.vendor).toLowerCase() === vendorFilter)
    }
    if (!k) return base
    return base.filter((r) =>
      [r.feature, r.vendor, r.version, r.server].join(' ').toLowerCase().includes(k),
    )
  }, [rows, searchText, vendorFilter])

  return (
    <Card title="License Keys">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          value={vendorFilter}
          onChange={setVendorFilter}
          style={{ width: 200 }}
          options={[
            { label: 'All Vendors', value: 'all' },
            { label: 'Synopsys', value: 'synopsys' },
            { label: 'Cadence', value: 'cadence' },
          ]}
        />
        <Input
          placeholder="Search feature/vendor/version/server"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          style={{ width: 320 }}
          onPressEnter={() => setSearchText(keyword)}
        />
        <Button type="primary" onClick={() => setSearchText(keyword)}>Search Feature</Button>
        <Button onClick={() => { setKeyword(''); setSearchText('') }}>Reset</Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={filtered}
        columns={[
          { title: 'Feature', dataIndex: 'feature' },
          { title: 'Vendor', dataIndex: 'vendor', render: (v) => <Tag>{v}</Tag> },
          { title: 'Version', dataIndex: 'version' },
          { title: 'Total', dataIndex: 'total', width: 80 },
          { title: 'Used', dataIndex: 'used', width: 80 },
          {
            title: 'Usage',
            render: (_, r) => <Progress size="small" percent={Math.round((r.used / Math.max(r.total, 1)) * 100)} />,
          },
          { title: 'Expiry Date', dataIndex: 'expiry' },
          { title: 'Server', dataIndex: 'server' },
        ]}
      />
    </Card>
  )
}
