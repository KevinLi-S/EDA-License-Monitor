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

function getUsageTone(usagePercent: number) {
  if (usagePercent >= 90) return 'danger'
  if (usagePercent >= 75) return 'warning'
  return 'ok'
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
    const highestUsage = [...data.servers].sort((a, b) => b.usage_percent - a.usage_percent).slice(0, 6)

    return {
      onlineServers,
      avgUsage,
      topAlert,
      highestUsage,
    }
  }, [data])

  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>Control center</p>
          <h3>License operations overview</h3>
          <p>
            Styled after the reference admin layout: light shell, grouped cards, status summary, usage focus.
            Existing phase-2 API responses remain untouched.
          </p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill online'>{computed.onlineServers}/{data.servers.length || 0} online</span>
          <span className='status-pill'>{computed.avgUsage.toFixed(1)}% avg peak</span>
          <span className={`status-pill ${computed.topAlert ? 'danger' : 'online'}`}>
            {computed.topAlert ? computed.topAlert.severity.toUpperCase() : 'No active alerts'}
          </span>
        </div>
      </section>

      <section className='charts-row'>
        <article className='panel trend-panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Trend area</p>
              <h3>Usage trend snapshot</h3>
            </div>
            <span className='status-pill'>24h view</span>
          </div>
          <div className='trend-chart'>
            <div className='trend-fill' />
            <div className='trend-grid' />
            <div className='trend-legend'>
              <strong>{computed.avgUsage.toFixed(1)}%</strong>
              <span>Average fleet usage</span>
            </div>
          </div>
        </article>

        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>Status</p>
              <h3>Server posture</h3>
            </div>
          </div>
          <div className='status-list'>
            {data.servers.map((server) => (
              <div key={server.id} className='status-item'>
                <div className='status-item-main'>
                  <span className={`status-indicator ${server.status.toLowerCase() === 'online' ? 'ok' : 'down'}`} />
                  <div>
                    <strong>{server.name}</strong>
                    <span>{server.vendor}</span>
                  </div>
                </div>
                <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                  {server.status}
                </span>
              </div>
            ))}
            {!data.servers.length && <div className='empty-state'>No servers returned from /overview yet.</div>}
          </div>
        </article>
      </section>

      <section className='kpi-grid dashboard-kpis'>
        {data.kpis.map((kpi) => (
          <article key={kpi.label} className='metric-card'>
            <p>{kpi.label}</p>
            <h3>{kpi.value}</h3>
            <span>{kpi.trend}</span>
          </article>
        ))}
        {data.kpis.length === 0 && (
          <article className='metric-card muted'>
            <p>Overview feed</p>
            <h3>{loading ? 'Loading…' : 'No data'}</h3>
            <span>Waiting for /overview response</span>
          </article>
        )}
      </section>

      <section className='license-grid'>
        {computed.highestUsage.map((server) => {
          const tone = getUsageTone(server.usage_percent)
          return (
            <article key={server.id} className={`license-card ${tone}`}>
              <div className='license-name'>{server.vendor}</div>
              <div className='license-usage'>{server.usage_percent.toFixed(1)}%</div>
              <div className='usage-bar'>
                <div className={`usage-fill ${tone}`} style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
              </div>
              <div className='license-detail'>
                {server.name} • {server.status}
              </div>
            </article>
          )
        })}
        {!computed.highestUsage.length && <div className='empty-state'>Usage cards will appear once server data is available.</div>}
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>Operations table</p>
            <h3>Server usage detail</h3>
          </div>
          <span className='status-pill'>{data.servers.length} rows</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table'>
            <thead>
              <tr>
                <th>Server</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Peak usage</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {data.servers.map((server) => (
                <tr key={server.id}>
                  <td>
                    <div className='table-primary'>
                      <strong>{server.name}</strong>
                      <span>Server #{server.id}</span>
                    </div>
                  </td>
                  <td>{server.vendor}</td>
                  <td>
                    <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                      {server.status}
                    </span>
                  </td>
                  <td>
                    <div className='usage-cell'>
                      <div className='bar-track slim'>
                        <div className={`bar-fill ${getUsageTone(server.usage_percent)}`} style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                      </div>
                      <span>{server.usage_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-pill ${getUsageTone(server.usage_percent) === 'danger' ? 'danger' : getUsageTone(server.usage_percent) === 'warning' ? 'warning' : 'online'}`}>
                      {getUsageTone(server.usage_percent) === 'danger'
                        ? 'High'
                        : getUsageTone(server.usage_percent) === 'warning'
                          ? 'Watch'
                          : 'Stable'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data.servers.length && <div className='empty-state padded'>No server rows returned from /overview yet.</div>}
        </div>
      </section>
    </div>
  )
}
