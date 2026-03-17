import { Button, Card, Col, Input, Modal, Progress, Row, Select, Space, Statistic, Table, Tag, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import api, { useMock } from '../api'
import { mockLicenseKeys } from '../mockData'

function usageColor(percent) {
  if (percent >= 90) return 'exception'
  if (percent >= 75) return 'active'
  return 'normal'
}

export default function LicenseKeysPage() {
  const [rows, setRows] = useState([])
  const [keyword, setKeyword] = useState('')
  const [vendorFilter, setVendorFilter] = useState('all')
  const [selectedUsers, setSelectedUsers] = useState([])
  const [userOpen, setUserOpen] = useState(false)
  const [totalCount, setTotalCount] = useState(0)

  const load = async (v = vendorFilter, k = keyword) => {
    try {
      if (useMock) {
        const base = mockLicenseKeys.filter((x) => v === 'all' || String(x.vendor).toLowerCase() === v)
        const out = k.trim() ? base.filter((r) => [r.feature, r.vendor, r.version, r.server].join(' ').toLowerCase().includes(k.toLowerCase())) : base
        setRows(out.map((r) => ({ ...r, free: Math.max((r.total || 0) - (r.used || 0), 0), active_user_count: r.active_user_count || 0, active_users: r.active_users || [] })))
        setTotalCount(out.length)
        return
      }
      const [countRes, listRes] = await Promise.all([
        api.get('/license-keys-count', { params: { vendor: v, keyword: k } }),
        api.get('/license-keys', { params: { vendor: v, keyword: k, limit: 500 } }),
      ])
      setTotalCount(Number(countRes?.data?.count || 0))
      setRows((Array.isArray(listRes.data) ? listRes.data : []).map((x) => ({ ...x, free: Math.max((x.total || 0) - (x.used || 0), 0) })))
    } catch (e) {
      console.error(e)
      setRows([])
      setTotalCount(0)
      message.error('License Keys 加载失败，请检查后端服务或刷新重试')
    }
  }

  useEffect(() => {
    load('all', '')
  }, [])

  const onSearch = () => load(vendorFilter, keyword)

  const summary = useMemo(() => {
    const total = totalCount
    const hot = rows.filter((r) => (r.used / Math.max(r.total, 1)) >= 0.85).length
    const active = rows.filter((r) => (r.active_user_count || 0) > 0).length
    const expiring = rows.filter((r) => String(r.expiry || '').startsWith('2026')).length
    return { total, hot, active, expiring }
  }, [rows, totalCount])

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Row gutter={14}>
        <Col span={6}><Card><Statistic title="Feature 总数" value={summary.total} /></Card></Col>
        <Col span={6}><Card><Statistic title="高利用率 Feature" value={summary.hot} /></Card></Col>
        <Col span={6}><Card><Statistic title="存在活跃用户" value={summary.active} /></Card></Col>
        <Col span={6}><Card><Statistic title="可能临近到期" value={summary.expiring} /></Card></Col>
      </Row>

      <Card title="Feature 使用情况 / License Keys">
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
              { label: 'Mentor', value: 'mentor' },
              { label: 'Ansys', value: 'ansys' },
            ]}
          />
          <Input placeholder="Search feature/vendor/version/server" value={keyword} onChange={(e) => setKeyword(e.target.value)} style={{ width: 320 }} onPressEnter={onSearch} />
          <Button type="primary" onClick={onSearch}>Search Feature</Button>
          <Button onClick={() => { setKeyword(''); setVendorFilter('all'); load('all', '') }}>Reset</Button>
        </Space>

        <Table
          rowKey="id"
          dataSource={rows}
          pagination={{ pageSize: 20 }}
          rowClassName={(r) => ((r.used / Math.max(r.total, 1)) >= 0.9 ? 'hot-row' : '')}
          columns={[
            { title: 'Feature', dataIndex: 'feature' },
            { title: 'Vendor', dataIndex: 'vendor', render: (v) => <Tag>{v}</Tag> },
            { title: 'Version', dataIndex: 'version' },
            { title: 'Server', dataIndex: 'server' },
            { title: 'Total', dataIndex: 'total', width: 90 },
            { title: 'Used', dataIndex: 'used', width: 90 },
            { title: 'Free', dataIndex: 'free', width: 90 },
            {
              title: 'Usage',
              render: (_, r) => {
                const p = Math.round((r.used / Math.max(r.total, 1)) * 100)
                return <Progress size="small" percent={p} status={usageColor(p)} />
              },
            },
            {
              title: 'Users',
              width: 160,
              render: (_, r) => (
                <Space>
                  <Tag color={r.active_user_count > 0 ? 'blue' : 'default'}>{r.active_user_count || 0}</Tag>
                  <Button size="small" disabled={!r.active_user_count} onClick={() => { setSelectedUsers(r.active_users || []); setUserOpen(true) }}>View</Button>
                </Space>
              ),
            },
            {
              title: 'Expiry Date',
              dataIndex: 'expiry',
              render: (v) => <Tag color={String(v || '').startsWith('2026') ? 'orange' : 'default'}>{v}</Tag>,
            },
          ]}
        />
      </Card>

      <Modal title="Active Users" open={userOpen} onCancel={() => setUserOpen(false)} footer={<Button onClick={() => setUserOpen(false)}>Close</Button>}>
        {selectedUsers.length ? <ul>{selectedUsers.map((u) => <li key={u}>{u}</li>)}</ul> : 'No active users'}
      </Modal>
    </Space>
  )
}
