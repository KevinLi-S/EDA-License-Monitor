import { Button, Card, Input, Modal, Progress, Select, Space, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'
import { mockLicenseKeys } from '../mockData'

export default function LicenseKeysPage() {
  const [rows, setRows] = useState([])
  const [keyword, setKeyword] = useState('')
  const [vendorFilter, setVendorFilter] = useState('all')
  const [selectedUsers, setSelectedUsers] = useState([])
  const [userOpen, setUserOpen] = useState(false)

  const load = async (v = vendorFilter, k = keyword) => {
    try {
      if (useMock) {
        const base = mockLicenseKeys.filter((x) => v === 'all' || String(x.vendor).toLowerCase() === v)
        const out = k.trim()
          ? base.filter((r) => [r.feature, r.vendor, r.version, r.server].join(' ').toLowerCase().includes(k.toLowerCase()))
          : base
        setRows(out)
        return
      }
      const r = await api.get('/license-keys', { params: { vendor: v, keyword: k, limit: 2000 } })
      setRows(Array.isArray(r.data) ? r.data : [])
    } catch (e) {
      console.error(e)
      setRows([])
      window?.alert?.('License Keys loading failed. Please refresh backend and try again.')
    }
  }

  useEffect(() => {
    load('all', '')
  }, [])

  const onSearch = () => load(vendorFilter, keyword)

  return (
    <Card title="License Keys (Real)">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          value={vendorFilter}
          onChange={(v) => {
            setVendorFilter(v)
            load(v, keyword)
          }}
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
          onPressEnter={onSearch}
        />
        <Button type="primary" onClick={onSearch}>Search Feature</Button>
        <Button onClick={() => { setKeyword(''); setVendorFilter('all'); load('all', '') }}>Reset</Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={rows}
        pagination={{ pageSize: 50 }}
        columns={[
          { title: 'Feature', dataIndex: 'feature' },
          { title: 'Vendor', dataIndex: 'vendor', render: (v) => <Tag>{v}</Tag> },
          { title: 'Version', dataIndex: 'version' },
          { title: 'Total', dataIndex: 'total', width: 90 },
          { title: 'Used', dataIndex: 'used', width: 90 },
          {
            title: 'Usage',
            render: (_, r) => <Progress size="small" percent={Math.round((r.used / Math.max(r.total, 1)) * 100)} />,
          },
          {
            title: 'Users',
            width: 160,
            render: (_, r) => (
              <Space>
                <Tag color={r.active_user_count > 0 ? 'blue' : 'default'}>{r.active_user_count || 0}</Tag>
                <Button
                  size="small"
                  disabled={!r.active_user_count}
                  onClick={() => {
                    setSelectedUsers(r.active_users || [])
                    setUserOpen(true)
                  }}
                >
                  View
                </Button>
              </Space>
            ),
          },
          { title: 'Expiry Date', dataIndex: 'expiry' },
          { title: 'Server', dataIndex: 'server' },
        ]}
      />

      <Modal title="Active Users" open={userOpen} onCancel={() => setUserOpen(false)} footer={<Button onClick={() => setUserOpen(false)}>Close</Button>}>
        {selectedUsers.length ? (
          <ul>
            {selectedUsers.map((u) => (
              <li key={u}>{u}</li>
            ))}
          </ul>
        ) : (
          'No active users'
        )}
      </Modal>
    </Card>
  )
}
