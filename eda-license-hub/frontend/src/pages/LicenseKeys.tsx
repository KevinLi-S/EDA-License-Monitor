import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type LicenseKey = {
  id: number
  key_name: string
  vendor: string
  version: string | null
  server_name: string
  issued: number
  used: number
  available: number
  usage_percent: number
}

export default function LicenseKeys() {
  const [items, setItems] = useState<LicenseKey[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    apiGet<LicenseKey[]>('/licenses/keys').then(setItems).catch(console.error)
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return items
    return items.filter((item) =>
      [item.key_name, item.vendor, item.server_name, item.version || ''].some((value) => value.toLowerCase().includes(q)),
    )
  }, [items, query])

  return (
    <div className='page-stack'>
      <section className='section-header-card synopsys-like'>
        <div>
          <p className='eyebrow'>许可证页面</p>
          <h3>License Keys</h3>
          <p>参考 Synopsys Web License 管理界面的信息布局，展示各个 key 的发放量、使用量与剩余量。</p>
        </div>
        <div className='search-strip'>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索 License Keys' className='table-search' />
        </div>
      </section>

      <section className='panel table-panel synopsys-table-panel'>
        <div className='table-wrap'>
          <table className='data-table synopsys-table'>
            <thead>
              <tr>
                <th>Key Name</th>
                <th>Vendor</th>
                <th>Version</th>
                <th>No. of License Issued</th>
                <th>No. Used</th>
                <th>No. Available</th>
                <th>Usage</th>
                <th>Service</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td>{item.key_name}</td>
                  <td>{item.vendor}</td>
                  <td>{item.version || '-'}</td>
                  <td>{item.issued}</td>
                  <td>{item.used}</td>
                  <td>{item.available}</td>
                  <td>
                    <div className='usage-cell'>
                      <div className='bar-track slim'>
                        <div className={`bar-fill ${item.usage_percent >= 90 ? 'danger' : item.usage_percent >= 75 ? 'warning' : 'ok'}`} style={{ width: `${Math.min(item.usage_percent, 100)}%` }} />
                      </div>
                      <span>{item.usage_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td>{item.server_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filtered.length && <div className='empty-state padded'>当前没有符合条件的 license keys。</div>}
        </div>
      </section>
    </div>
  )
}
