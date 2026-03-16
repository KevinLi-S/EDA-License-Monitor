import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type Overview = {
  kpis: Array<{ label: string; value: string; trend: string }>
  servers: Array<{ id: number; name: string; vendor: string; usage_percent: number; status: string }>
  alerts: Array<{ id: number; severity: string; message: string }>
}

const severityRank: Record<string, number> = {
  critical: 4,
  high: 3,
  warning: 2,
  medium: 2,
  info: 1,
  low: 1,
}

export default function Dashboard() {
  const [data, setData] = useState<Overview>({ kpis: [], servers: [], alerts: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiGet<Overview>('/overview')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const computed = useMemo(() => {
    const onlineServers = data.servers.filter((server) => server.status.toLowerCase() === 'online').length
    const avgUsage = data.servers.length
      ? data.servers.reduce((sum, server) => sum + server.usage_percent, 0) / data.servers.length
      : 0
    const topAlert = [...data.alerts].sort(
      (a, b) => (severityRank[b.severity.toLowerCase()] ?? 0) - (severityRank[a.severity.toLowerCase()] ?? 0),
    )[0]

    return {
      onlineServers,
      avgUsage,
      topAlert,
    }
  }, [data])

  return (
    <div className='page-stack'>
      <section className='hero-banner'>
        <div>
          <p className='eyebrow'>Executive snapshot</p>
          <h2>License operations at a glance</h2>
          <p>
            A presentation-friendly overview of server posture, collector alerts, and capacity pressure.
            Existing phase-2 APIs stay untouched.
          </p>
        </div>
        <div className='hero-metrics'>
          <div>
            <strong>{computed.onlineServers}/{data.servers.length || 0}</strong>
            <span>servers online</span>
          </div>
          <div>
            <strong>{computed.avgUsage.toFixed(1)}%</strong>
            <span>average peak usage</span>
          </div>
        </div>
      </section>

      <section className='kpi-grid'>
        {data.kpis.map((kpi) => (
          <article key={kpi.label} className='kpi-card'>
            <p>{kpi.label}</p>
            <h3>{kpi.value}</h3>
            <span>{kpi.trend}</span>
          </article>
        ))}
        {data.kpis.length === 0 && (
          <article className='kpi-card muted'>
            <p>Overview feed</p>
            <h3>{loading ? 'Loading…' : 'No data'}</h3>
            <span>Waiting for /overview response</span>
          </article>
        )}
      </section>

      <section className='dashboard-grid'>
        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Fleet health</p>
              <h3>Server snapshot</h3>
            </div>
            <span className='status-pill online'>{computed.onlineServers} healthy</span>
          </div>
          <div className='server-list'>
            {data.servers.map((server) => (
              <div key={server.id} className='server-list-item'>
                <div>
                  <strong>{server.name}</strong>
                  <span>{server.vendor}</span>
                </div>
                <div className='server-list-stats'>
                  <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                    {server.status}
                  </span>
                  <span>{server.usage_percent.toFixed(1)}% peak</span>
                </div>
              </div>
            ))}
            {!data.servers.length && <div className='empty-state'>No servers have been returned yet.</div>}
          </div>
        </article>

        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Escalations</p>
              <h3>Collector alerts</h3>
            </div>
            {computed.topAlert ? (
              <span className='status-pill danger'>{computed.topAlert.severity.toUpperCase()}</span>
            ) : (
              <span className='status-pill online'>Quiet</span>
            )}
          </div>
          <div className='alert-list'>
            {data.alerts.map((alert) => (
              <div key={alert.id} className='alert-item'>
                <span className={`alert-dot severity-${alert.severity.toLowerCase()}`} />
                <div>
                  <strong>{alert.severity.toUpperCase()}</strong>
                  <p>{alert.message}</p>
                </div>
              </div>
            ))}
            {!data.alerts.length && <div className='empty-state'>No active alerts from the collector loop.</div>}
          </div>
        </article>
      </section>

      <section className='dashboard-grid secondary'>
        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Capacity outlook</p>
              <h3>Utilization bands</h3>
            </div>
            <span className='status-pill'>Placeholder</span>
          </div>
          <div className='bar-stack'>
            {data.servers.slice(0, 5).map((server) => (
              <div key={server.id} className='bar-row'>
                <label>{server.name}</label>
                <div className='bar-track'>
                  <div className='bar-fill' style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                </div>
                <span>{server.usage_percent.toFixed(1)}%</span>
              </div>
            ))}
            {!data.servers.length && <div className='empty-state'>Usage bands will appear once server data is available.</div>}
          </div>
        </article>

        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Presentation notes</p>
              <h3>Talking points</h3>
            </div>
          </div>
          <ul className='bullet-list'>
            <li>Dashboard, Servers, Alerts, and Analytics now share a cohesive operations-shell layout.</li>
            <li>KPI cards and fleet summaries are API-driven and safe for live demos.</li>
            <li>Analytics visuals remain placeholder-grade, making phase-3 scope obvious without looking unfinished.</li>
          </ul>
        </article>
      </section>
    </div>
  )
}
