import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type FeatureUsageRow = {
  feature_name: string
  vendor: string
  server_names: string[]
  current_users: string[]
  current_checkout_count: number
  log_users: string[]
  unique_user_count: number
  total_log_events: number
  checkout_events: number
  checkin_events: number
  denied_events: number
  last_seen: string | null
}

function formatDateTime(value: string | null) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export default function FeatureUsage() {
  const [items, setItems] = useState<FeatureUsageRow[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    apiGet<FeatureUsageRow[]>('/licenses/feature-usage?limit=200').then(setItems).catch(console.error)
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return items
    return items.filter((item) =>
      [item.feature_name, item.vendor, ...item.server_names, ...item.current_users, ...item.log_users].some((value) =>
        value.toLowerCase().includes(q),
      ),
    )
  }, [items, query])

  return (
    <div className='page-stack'>
      <section className='section-header-card synopsys-like'>
        <div>
          <p className='eyebrow'>Feature 分析</p>
          <h3>Feature Usage</h3>
          <p>聚合当前 checkout 与历史日志事件，回答“谁在使用哪个 feature、哪个 feature 最热”。</p>
        </div>
        <div className='search-strip'>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索 Feature / Vendor / User / Service' className='table-search' />
        </div>
      </section>

      <section className='panel table-panel synopsys-table-panel'>
        <div className='table-wrap'>
          <table className='data-table synopsys-table'>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Vendor</th>
                <th>Current Users</th>
                <th>当前占用</th>
                <th>历史用户数</th>
                <th>OUT / IN / DENIED</th>
                <th>Service</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={`${item.vendor}-${item.feature_name}`}>
                  <td>{item.feature_name}</td>
                  <td>{item.vendor}</td>
                  <td>{item.current_users.length ? item.current_users.join(', ') : '-'}</td>
                  <td>{item.current_checkout_count}</td>
                  <td>{item.unique_user_count}</td>
                  <td>{item.checkout_events} / {item.checkin_events} / {item.denied_events}</td>
                  <td>{item.server_names.join(', ') || '-'}</td>
                  <td>{formatDateTime(item.last_seen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && <div className='empty-state padded'>当前没有可展示的 feature usage 数据。</div>}
        </div>
      </section>
    </div>
  )
}
