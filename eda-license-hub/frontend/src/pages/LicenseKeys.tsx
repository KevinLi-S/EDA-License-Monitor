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
  const [vendor, setVendor] = useState('all')

  useEffect(() => {
    apiGet<LicenseKey[]>('/licenses/keys').then(setItems).catch(console.error)
  }, [])

  const vendors = useMemo(() => ['all', ...Array.from(new Set(items.map((item) => item.vendor))).sort()], [items])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return items.filter((item) => {
      const matchesVendor = vendor === 'all' || item.vendor === vendor
      const matchesQuery =
        !q || [item.key_name, item.vendor, item.server_name, item.version || ''].some((value) => value.toLowerCase().includes(q))
      return matchesVendor && matchesQuery
    })
  }, [items, query, vendor])

  const grouped = useMemo(() => {
    return filtered.reduce<Record<string, LicenseKey[]>>((acc, item) => {
      if (!acc[item.vendor]) acc[item.vendor] = []
      acc[item.vendor].push(item)
      return acc
    }, {})
  }, [filtered])

  const orderedGroups = useMemo(
    () => Object.entries(grouped).sort((a, b) => a[0].localeCompare(b[0])),
    [grouped],
  )

  return (
    <div className='page-stack'>
      <section className='section-header-card synopsys-like'>
        <div>
          <p className='eyebrow'>许可证页面</p>
          <h3>License Keys</h3>
          <p>参考 Synopsys Web License 管理界面的信息布局，按厂商分组展示各个 feature 的发放量、使用量与剩余量。</p>
        </div>
        <div className='search-strip stacked-filters'>
          <select value={vendor} onChange={(e) => setVendor(e.target.value)} className='table-search'>
            {vendors.map((item) => (
              <option key={item} value={item}>
                {item === 'all' ? '全部 Vendor' : item}
              </option>
            ))}
          </select>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='搜索 License Keys / Service' className='table-search' />
        </div>
      </section>

      {orderedGroups.map(([groupName, groupItems]) => (
        <section key={groupName} className='panel table-panel synopsys-table-panel'>
          <div className='panel-header grouped-table-header'>
            <div>
              <p className='eyebrow'>Vendor</p>
              <h3>{groupName}</h3>
            </div>
            <span className='status-pill'>{groupItems.length} 个 feature</span>
          </div>
          <div className='table-wrap'>
            <table className='data-table synopsys-table'>
              <thead>
                <tr>
                  <th>Feature Name</th>
                  <th>Version</th>
                  <th>No. of License Issued</th>
                  <th>No. Used</th>
                  <th>No. Available</th>
                  <th>Usage</th>
                  <th>Service</th>
                </tr>
              </thead>
              <tbody>
                {groupItems.map((item) => (
                  <tr key={item.id}>
                    <td>{item.key_name}</td>
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
          </div>
        </section>
      ))}

      {!orderedGroups.length && <div className='empty-state padded'>当前没有符合条件的 license keys。</div>}
    </div>
  )
}
