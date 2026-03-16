import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type Server = {
  id: number
  name: string
  vendor: string
  host: string
  port: number
  status: string
  feature_count: number
  usage_percent: number
}

function getUsageTone(usagePercent: number) {
  if (usagePercent >= 90) return 'danger'
  if (usagePercent >= 75) return 'warning'
  return 'ok'
}

export default function Dashboard() {
  const [servers, setServers] = useState<Server[]>([])

  useEffect(() => {
    apiGet<Server[]>('/servers').then(setServers).catch(console.error)
  }, [])

  const vendorOverview = useMemo(() => {
    const grouped = servers.reduce<Record<string, { serviceCount: number; featureCount: number; maxUsage: number; onlineCount: number }>>((acc, server) => {
      const key = server.vendor || 'unknown'
      if (!acc[key]) acc[key] = { serviceCount: 0, featureCount: 0, maxUsage: 0, onlineCount: 0 }
      acc[key].serviceCount += 1
      acc[key].featureCount += server.feature_count
      acc[key].maxUsage = Math.max(acc[key].maxUsage, server.usage_percent)
      if (['up', 'online'].includes(server.status.toLowerCase())) acc[key].onlineCount += 1
      return acc
    }, {})

    return Object.entries(grouped)
      .map(([vendor, value]) => ({
        vendor,
        ...value,
      }))
      .sort((a, b) => b.maxUsage - a.maxUsage)
  }, [servers])

  const stats = useMemo(() => {
    const vendorCount = vendorOverview.length
    const serviceCount = servers.length
    const highRisk = servers.filter((server) => server.usage_percent >= 90).length
    const avgUsage = servers.length
      ? servers.reduce((sum, server) => sum + server.usage_percent, 0) / servers.length
      : 0
    return { vendorCount, serviceCount, highRisk, avgUsage }
  }, [servers, vendorOverview])

  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>控制中心</p>
          <h3>各厂家 License 服务概览</h3>
          <p>Dashboard 不再强调趋势图，而是集中展示各家 license 服务运行情况、容量压力和服务分布。</p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill'>{stats.vendorCount} 个厂家</span>
          <span className='status-pill online'>{stats.serviceCount} 个服务</span>
          <span className={`status-pill ${stats.highRisk ? 'danger' : 'online'}`}>{stats.highRisk} 个高风险服务</span>
        </div>
      </section>

      <section className='kpi-grid compact'>
        <article className='metric-card'>
          <p>厂家数量</p>
          <h3>{stats.vendorCount}</h3>
          <span>当前纳入监控的 vendor 数</span>
        </article>
        <article className='metric-card'>
          <p>服务数量</p>
          <h3>{stats.serviceCount}</h3>
          <span>当前 license service 总数</span>
        </article>
        <article className='metric-card'>
          <p>平均峰值使用率</p>
          <h3>{stats.avgUsage.toFixed(1)}%</h3>
          <span>基于所有服务的 usage_percent</span>
        </article>
      </section>

      <section className='vendor-overview-grid'>
        {vendorOverview.map((vendor) => (
          <article key={vendor.vendor} className={`vendor-card ${getUsageTone(vendor.maxUsage)}`}>
            <div className='vendor-card-head'>
              <div>
                <p className='eyebrow'>Vendor</p>
                <h4>{vendor.vendor}</h4>
              </div>
              <span className={`status-pill ${getUsageTone(vendor.maxUsage) === 'danger' ? 'danger' : getUsageTone(vendor.maxUsage) === 'warning' ? 'warning' : 'online'}`}>
                峰值 {vendor.maxUsage.toFixed(1)}%
              </span>
            </div>
            <div className='vendor-card-body'>
              <div>
                <strong>{vendor.serviceCount}</strong>
                <span>服务数</span>
              </div>
              <div>
                <strong>{vendor.onlineCount}</strong>
                <span>在线数</span>
              </div>
              <div>
                <strong>{vendor.featureCount}</strong>
                <span>Feature 数</span>
              </div>
            </div>
            <div className='bar-track'>
              <div className={`bar-fill ${getUsageTone(vendor.maxUsage)}`} style={{ width: `${Math.min(vendor.maxUsage, 100)}%` }} />
            </div>
          </article>
        ))}
        {!vendorOverview.length && <div className='empty-state padded'>当前还没有可展示的厂家服务概览数据。</div>}
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>服务明细</p>
            <h3>各厂家 License 服务列表</h3>
          </div>
          <span className='status-pill'>{servers.length} 行</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table'>
            <thead>
              <tr>
                <th>服务名称</th>
                <th>厂家</th>
                <th>端点</th>
                <th>状态</th>
                <th>Features</th>
                <th>峰值使用率</th>
              </tr>
            </thead>
            <tbody>
              {servers.map((server) => (
                <tr key={server.id}>
                  <td>
                    <div className='table-primary'>
                      <strong>{server.name}</strong>
                      <span>服务 #{server.id}</span>
                    </div>
                  </td>
                  <td>{server.vendor}</td>
                  <td>{server.host}:{server.port}</td>
                  <td>
                    <span className={`status-pill ${['up', 'online'].includes(server.status.toLowerCase()) ? 'online' : 'warning'}`}>
                      {server.status}
                    </span>
                  </td>
                  <td>{server.feature_count}</td>
                  <td>
                    <div className='usage-cell'>
                      <div className='bar-track slim'>
                        <div className={`bar-fill ${getUsageTone(server.usage_percent)}`} style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                      </div>
                      <span>{server.usage_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!servers.length && <div className='empty-state padded'>当前还没有返回服务列表数据。</div>}
        </div>
      </section>
    </div>
  )
}
