import { Progress, Table } from 'antd'
import { useEffect, useState } from 'react'
import api, { useMock } from '../api'
import { mockFeatures } from '../mockData'

export default function FeaturesPage() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    if (useMock) {
      setRows(mockFeatures)
      return
    }
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
        {
          title: 'Utilization',
          render: (_, r) => <Progress size="small" percent={Math.round((r.used / Math.max(r.total, 1)) * 100)} />,
        },
        { title: 'Collected At', dataIndex: 'collected_at' },
      ]}
    />
  )
}
