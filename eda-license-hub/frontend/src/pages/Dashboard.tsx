import { useEffect, useState } from 'react'
import { apiGet } from '../services/api'

type Overview = {
  kpis: Array<{ label: string; value: string; trend: string }>
  servers: Array<{ id: number; name: string; vendor: string; usage_percent: number; status: string }>
  alerts: Array<{ id: number; severity: string; message: string }>
}

export default function Dashboard() {
  const [data, setData] = useState<Overview>({ kpis: [], servers: [], alerts: [] })

  useEffect(() => {
    apiGet<Overview>('/overview').then(setData).catch(console.error)
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 16 }}>
        {data.kpis.map((kpi) => (
          <div key={kpi.label} style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>
            <div style={{ color: '#6b7280', fontSize: 14 }}>{kpi.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{kpi.value}</div>
            <div style={{ color: '#2563eb', fontSize: 13 }}>{kpi.trend}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 24 }}>
        <section style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>
          <h2>Server snapshot</h2>
          <ul>
            {data.servers.map((server) => (
              <li key={server.id}>{server.name} · {server.vendor} · {server.status} · {server.usage_percent.toFixed(1)}%</li>
            ))}
          </ul>
        </section>
        <section style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: 16 }}>
          <h2>Collector alerts</h2>
          <ul>
            {data.alerts.map((alert) => (
              <li key={alert.id}>{alert.severity.toUpperCase()} · {alert.message}</li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
