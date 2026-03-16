import { useEffect, useState } from 'react'
import { apiGet } from '../services/api'

export function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  useEffect(() => {
    apiGet('/alerts').then(setAlerts).catch(() => {})
  }, [])

  return (
    <section className="panel">
      <h2>Alerts</h2>
      <p>Phase-1 先展示告警骨架，后续补规则配置、恢复流转、通知通道。</p>
      <ul className="list">
        {alerts.map((alert) => (
          <li key={alert.id}>{alert.triggered_at} · {alert.severity.toUpperCase()} · {alert.message}</li>
        ))}
      </ul>
    </section>
  )
}
