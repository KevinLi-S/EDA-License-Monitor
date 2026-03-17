import { useEffect, useMemo, useState } from 'react'
import { apiGet, apiPost } from '../services/api'

type LicenseUsageRow = {
  id: number
  key_name: string
  vendor: string
  version: string | null
  username: string
  client_hostname: string
  last_used: string
  server_name: string
}

function formatDateTime(value: string) {
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

function toApiDateTime(value: string) {
  if (!value) return ''
  return `${value}:00`
}

export default function LicenseUsage() {
  const [items, setItems] = useState<LicenseUsageRow[]>([])
  const [query, setQuery] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [refreshMessage, setRefreshMessage] = useState('')

  const load = async () => {
    const params = new URLSearchParams()
    if (startTime) params.set('start_time', toApiDateTime(startTime))
    if (endTime) params.set('end_time', toApiDateTime(endTime))
    const queryString = params.toString()

    const rows = await apiGet<LicenseUsageRow[]>(`/licenses/usage${queryString ? `?${queryString}` : ''}`)
    setItems(rows)
  }

  useEffect(() => {
    let cancelled = false

    const poll = () => {
      setLoading(true)
      load()
        .catch(console.error)
        .finally(() => {
          if (!cancelled) setLoading(false)
        })
    }

    poll()
    const timer = window.setInterval(poll, 30000)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [startTime, endTime])

  async function refreshNow() {
    setRefreshing(true)
    setRefreshMessage('正在立即采集当前 license 使用状态…')
    try {
      await apiPost('/servers/refresh')
      await load()
      setRefreshMessage('立即刷新完成。')
    } catch (error) {
      console.error(error)
      setRefreshMessage('立即刷新失败，请稍后再试。')
    } finally {
      setRefreshing(false)
      window.setTimeout(() => setRefreshMessage(''), 4000)
    }
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return items
    return items.filter((item) =>
      [item.key_name, item.vendor, item.username, item.client_hostname, item.server_name, item.version || ''].some((value) => value.toLowerCase().includes(q)),
    )
  }, [items, query])

  return (
    <div className='page-stack'>
      <section className='section-header-card synopsys-like'>
        <div>
          <p className='eyebrow'>使用页面</p>
          <h3>License Usage</h3>
          <p>只展示当前有使用中的 license，支持按时间范围筛选活跃 checkout 记录。</p>
        </div>
        <div className='search-strip stacked-filters'>
          <button type='button' className='header-button primary' onClick={refreshNow} disabled={refreshing}>
            {refreshing ? '立即刷新中…' : '立即刷新'}
          </button>
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
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索用户名 / License Key / Host' className='table-search' />
        </div>
        {refreshMessage && <p className='eyebrow'>{refreshMessage}</p>}
      </section>

      <section className='panel table-panel synopsys-table-panel'>
        <div className='panel-header grouped-table-header'>
          <div>
            <p className='eyebrow'>活跃记录</p>
            <h3>{filtered.length}</h3>
          </div>
          <span className='status-pill'>{loading ? 'Loading…' : 'Filtered'}</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table synopsys-table'>
            <thead>
              <tr>
                <th>License key Name</th>
                <th>Vendor</th>
                <th>Version</th>
                <th>Username</th>
                <th>Last Used</th>
                <th>Client Hostname</th>
                <th>Service</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td>{item.key_name}</td>
                  <td>{item.vendor}</td>
                  <td>{item.version || '-'}</td>
                  <td>{item.username}</td>
                  <td>{formatDateTime(item.last_used)}</td>
                  <td>{item.client_hostname}</td>
                  <td>{item.server_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && <div className='empty-state padded'>当前筛选条件下没有活跃的 license usage 记录。</div>}
        </div>
      </section>
    </div>
  )
}
