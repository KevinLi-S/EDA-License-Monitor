import { useEffect, useMemo, useState } from 'react'
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

  const summary = useMemo(() => {
    const online = servers.filter((server) => server.status.toLowerCase() === 'online').length
    const highUsage = servers.filter((server) => server.usage_percent >= 80).length
    const avgFeatures = servers.length
      ? servers.reduce((sum, server) => sum + server.feature_count, 0) / servers.length
      : 0

    return { online, highUsage, avgFeatures }
  }, [servers])

  return (
    <div className='page-stack'>
      <section className='section-header'>
        <div>
          <p className='eyebrow'>Infrastructure inventory</p>
          <h2>Server fleet</h2>
          <p>Run the collector, inspect endpoints, and walk through license-capacity hotspots in one table.</p>
        </div>
        <button className='primary-button' onClick={refresh} disabled={refreshing}>
          {refreshing ? 'Refreshing…' : 'Run Collector'}
        </button>
      </section>

      <section className='kpi-grid compact'>
        <article className='kpi-card'>
          <p>Online servers</p>
          <h3>{summary.online}</h3>
          <span>of {servers.length || 0} registered endpoints</span>
        </article>
        <article className='kpi-card'>
          <p>High pressure nodes</p>
          <h3>{summary.highUsage}</h3>
          <span>≥ 80% peak utilization</span>
        </article>
        <article className='kpi-card'>
          <p>Average feature count</p>
          <h3>{summary.avgFeatures.toFixed(1)}</h3>
          <span>tracked features per server</span>
        </article>
      </section>

      <section className='panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>Operational table</p>
            <h3>Collector endpoints</h3>
          </div>
          <span className='status-pill'>{servers.length} rows</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table'>
            <thead>
              <tr>
                <th>Name</th>
                <th>Vendor</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Features</th>
                <th>Peak usage</th>
              </tr>
            </thead>
            <tbody>
              {servers.map((server) => (
                <tr key={server.id}>
                  <td>
                    <div className='table-primary'>
                      <strong>{server.name}</strong>
                      <span>Server #{server.id}</span>
                    </div>
                  </td>
                  <td>{server.vendor}</td>
                  <td>
                    <span className='mono'>{server.host}:{server.port}</span>
                  </td>
                  <td>
                    <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                      {server.status}
                    </span>
                  </td>
                  <td>{server.feature_count}</td>
                  <td>
                    <div className='usage-cell'>
                      <div className='bar-track slim'>
                        <div className='bar-fill' style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                      </div>
                      <span>{server.usage_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!servers.length && <div className='empty-state padded'>No server rows returned from /servers yet.</div>}
        </div>
      </section>
    </div>
  )
}
