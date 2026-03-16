import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '../services/api'

type Server = {
  id: number
  name: string
  vendor: string
  host: string
  port: number
  status: string
  feature_count: number
  usage_percent: number
}

export default function Servers() {
  const [servers, setServers] = useState<Server[]>([])
  const [refreshing, setRefreshing] = useState(false)

  const load = () => apiGet<Server[]>('/servers').then(setServers)

  useEffect(() => {
    load().catch(console.error)
  }, [])

  async function refresh() {
    setRefreshing(true)
    try {
      await apiPost('/servers/refresh')
      await load()
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Servers</h1>
        <button onClick={refresh} disabled={refreshing} style={{ padding: '8px 16px' }}>
          {refreshing ? 'Refreshing...' : 'Run Collector'}
        </button>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {['Name', 'Vendor', 'Endpoint', 'Status', 'Features', 'Peak Usage'].map((head) => (
              <th key={head} style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: 12 }}>{head}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {servers.map((server) => (
            <tr key={server.id}>
              <td style={{ padding: 12 }}>{server.name}</td>
              <td style={{ padding: 12 }}>{server.vendor}</td>
              <td style={{ padding: 12 }}>{server.host}:{server.port}</td>
              <td style={{ padding: 12 }}>{server.status}</td>
              <td style={{ padding: 12 }}>{server.feature_count}</td>
              <td style={{ padding: 12 }}>{server.usage_percent.toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
