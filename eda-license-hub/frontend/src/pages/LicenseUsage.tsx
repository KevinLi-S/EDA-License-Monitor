import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

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

export default function LicenseUsage() {
  const [items, setItems] = useState<LicenseUsageRow[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    apiGet<LicenseUsageRow[]>('/licenses/usage').then(setItems).catch(console.error)
  }, [])

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
          <h3>License Key Usage</h3>
          <p>展示当前活跃 checkout 用户、客户端主机以及最后使用时间，风格参考 Synopsys Web Portal。</p>
        </div>
        <div className='search-strip'>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索用户名 / License Key / Host' className='table-search' />
        </div>
      </section>

      <section className='panel table-panel synopsys-table-panel'>
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
          {!filtered.length && <div className='empty-state padded'>当前没有活跃的 license usage 记录。</div>}
        </div>
      </section>
    </div>
  )
}
