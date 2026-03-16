import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'
import { connectDashboardSocket } from '../services/websocket'

export function DashboardPage() {
  const [data, setData] = useState({ kpis: [], servers: [], alerts: [] })
  const [socketState, setSocketState] = useState('disconnected')

  useEffect(() => {
    apiGet('/overview').then(setData).catch(() => {})
    const socket = connectDashboardSocket((message) => {
      if (message.type === 'initial') setSocketState('connected')
    })
    socket.onopen = () => {
      setSocketState('connected')
      socket.send('ping')
    }
    socket.onclose = () => setSocketState('disconnected')
    return () => socket.close()
  }, [])

  const cards = useMemo(() => data.kpis || [], [data])

  return (
    <div className="page-grid">
      <section className="hero-card">
        <div>
          <h2>Operations overview</h2>
          <p>WebSocket: {socketState}</p>
        </div>
      </section>
      <section className="kpi-grid">
        {cards.map((item) => (
          <article className="panel" key={item.label}>
            <span className="muted">{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.trend}</small>
          </article>
        ))}
      </section>
      <section className="panel">
        <h3>Server snapshot</h3>
        <ul className="list">
          {data.servers.map((server) => (
            <li key={server.id}>{server.name} · {server.vendor} · {server.usage_percent}%</li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3>Recent alerts</h3>
        <ul className="list">
          {data.alerts.map((alert) => (
            <li key={alert.id}>{alert.severity.toUpperCase()} · {alert.message}</li>
          ))}
        </ul>
      </section>
    </div>
  )
}
