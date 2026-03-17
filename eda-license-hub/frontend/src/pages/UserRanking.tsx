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

function toApiDateTime(value: string) {
  if (!value) return ''
  return `${value}:00`
}

export default function UserRanking() {
  const [items, setItems] = useState<UserRankingRow[]>([])
  const [query, setQuery] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams({ limit: '200' })
    if (startTime) params.set('start_time', toApiDateTime(startTime))
    if (endTime) params.set('end_time', toApiDateTime(endTime))

    setLoading(true)
    apiGet<UserRankingRow[]>(`/licenses/user-ranking?${params.toString()}`)
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [startTime, endTime])

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
          <p>基于当前 checkout 与历史日志事件统计用户活跃度，支持按时间范围筛选排行结果。</p>
        </div>
        <div className='search-strip stacked-filters'>
          <input
            type='datetime-local'
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className='table-search'
            aria-label='开始时间'
          />
          <input
            type='datetime-local'
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            className='table-search'
            aria-label='结束时间'
          />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索用户 / Feature / Service' className='table-search' />
        </div>
      </section>

      <section className='panel table-panel synopsys-table-panel'>
        <div className='panel-header grouped-table-header'>
          <div>
            <p className='eyebrow'>排行记录</p>
            <h3>{filtered.length}</h3>
          </div>
          <span className='status-pill'>{loading ? 'Loading…' : 'Filtered'}</span>
        </div>
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
          {!filtered.length && <div className='empty-state padded'>当前筛选条件下没有可展示的用户排行数据。</div>}
        </div>
      </section>
    </div>
  )
}
