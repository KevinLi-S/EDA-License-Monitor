import { Table } from 'antd'
import { useEffect, useState } from 'react'
import api from '../api'

export default function FeaturesPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/features').then((r) => setRows(r.data))
  }, [])

  return (
    <Table
      rowKey={(r) => `${r.feature}-${r.server}-${r.collected_at}`}
      dataSource={rows}
      columns={[
        { title: 'Feature', dataIndex: 'feature' },
        { title: 'Vendor', dataIndex: 'vendor' },
        { title: 'Server', dataIndex: 'server' },
        { title: 'Total', dataIndex: 'total' },
        { title: 'Used', dataIndex: 'used' },
        { title: 'Free', dataIndex: 'free' },
        { title: 'Collected At', dataIndex: 'collected_at' },
      ]}
    />
  )
}
