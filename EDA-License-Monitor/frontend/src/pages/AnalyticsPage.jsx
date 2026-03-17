import { useEffect, useState } from 'react'
import { apiGet } from '../services/api'

export function AnalyticsPage() {
  const [points, setPoints] = useState([])
  useEffect(() => {
    apiGet('/analytics/usage-trend').then(setPoints).catch(() => {})
  }, [])

  return (
    <section className="panel">
      <h2>Analytics</h2>
      <p>Phase-1 仅放趋势数据骨架，后续接真实历史表和多时间范围聚合。</p>
      <div className="chart-placeholder">
        {points.map((point) => (
          <div key={point.timestamp} className="bar" style={{ height: `${Math.max(point.usage_percent, 8)}%` }} title={`${point.usage_percent}%`} />
        ))}
      </div>
    </section>
  )
}
