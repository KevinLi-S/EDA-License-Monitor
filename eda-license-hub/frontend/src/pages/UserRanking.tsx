import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type UserRankingRow = {
  username: string
  server_names: string[]
  feature_names: string[]
  unique_feature_count: number
  current_checkout_count: number
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

export default function UserRanking() {
  const [items, setItems] = useState<UserRankingRow[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    apiGet<UserRankingRow[]>('/licenses/user-ranking?limit=200').then(setItems).catch(console.error)
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return items
    return items.filter((item) =>
      [item.username, ...item.server_names, ...item.feature_names].some((value) => value.toLowerCase().includes(q)),
    )
  }, [items, query])

  return (
    <div className='page-stack'>
      <section className='section-header-card synopsys-like'>
        <div>
          <p className='eyebrow'>用户排行</p>
          <h3>User Ranking</h3>
          <p>基于当前 checkout 与历史日志事件统计用户活跃度、涉及 feature 数以及 denied 情况。</p>
        </div>
        <div className='search-strip'>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索用户 / Feature / Service' className='table-search' />
        </div>
      </section>

      <section className='panel table-panel synopsys-table-panel'>
        <div className='table-wrap'>
          <table className='data-table synopsys-table'>
            <thead>
              <tr>
                <th>Username</th>
                <th>Current Checkouts</th>
                <th>Feature Count</th>
                <th>Total Log Events</th>
                <th>OUT / IN / DENIED</th>
                <th>Services</th>
                <th>Feature Preview</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.username}>
                  <td>{item.username}</td>
                  <td>{item.current_checkout_count}</td>
                  <td>{item.unique_feature_count}</td>
                  <td>{item.total_log_events}</td>
                  <td>{item.checkout_events} / {item.checkin_events} / {item.denied_events}</td>
                  <td>{item.server_names.join(', ') || '-'}</td>
                  <td>{item.feature_names.slice(0, 5).join(', ')}{item.feature_names.length > 5 ? ' …' : ''}</td>
                  <td>{formatDateTime(item.last_seen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && <div className='empty-state padded'>当前没有可展示的用户排行数据。</div>}
        </div>
      </section>
    </div>
  )
}
