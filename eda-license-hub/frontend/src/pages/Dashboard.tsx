import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type Overview = {
  kpis: Array<{ label: string; value: string; trend: string }>
  servers: Array<{ id: number; name: string; vendor: string; usage_percent: number; status: string }>
  alerts: Array<{ id: number; severity: string; message: string }>
}

const severityRank: Record<string, number> = {
  critical: 4,
  high: 3,
  warning: 2,
  medium: 2,
  info: 1,
  low: 1,
}

function getUsageTone(usagePercent: number) {
  if (usagePercent >= 90) return 'danger'
  if (usagePercent >= 75) return 'warning'
  return 'ok'
}

export default function Dashboard() {
  const [data, setData] = useState<Overview>({ kpis: [], servers: [], alerts: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiGet<Overview>('/overview')
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const computed = useMemo(() => {
    const onlineServers = data.servers.filter((server) => server.status.toLowerCase() === 'online').length
    const avgUsage = data.servers.length
      ? data.servers.reduce((sum, server) => sum + server.usage_percent, 0) / data.servers.length
      : 0
    const topAlert = [...data.alerts].sort(
      (a, b) => (severityRank[b.severity.toLowerCase()] ?? 0) - (severityRank[a.severity.toLowerCase()] ?? 0),
    )[0]
    const highestUsage = [...data.servers].sort((a, b) => b.usage_percent - a.usage_percent).slice(0, 6)

    return {
      onlineServers,
      avgUsage,
      topAlert,
      highestUsage,
    }
  }, [data])

  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>控制中心</p>
          <h3>许可证运行总览</h3>
          <p>
            参考 layout-B 的后台布局风格，重点展示运行状态、容量压力与风险概览；底层仍沿用现有 phase-2 接口。
          </p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill online'>{computed.onlineServers}/{data.servers.length || 0} 台在线</span>
          <span className='status-pill'>平均峰值 {computed.avgUsage.toFixed(1)}%</span>
          <span className={`status-pill ${computed.topAlert ? 'danger' : 'online'}`}>
            {computed.topAlert ? `最高告警 ${computed.topAlert.severity.toUpperCase()}` : '当前无活动告警'}
          </span>
        </div>
      </section>

      <section className='charts-row'>
        <article className='panel trend-panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>趋势区域</p>
              <h3>使用趋势快照</h3>
            </div>
            <span className='status-pill'>近 24 小时</span>
          </div>
          <div className='trend-chart'>
            <div className='trend-fill' />
            <div className='trend-grid' />
            <div className='trend-legend'>
              <strong>{computed.avgUsage.toFixed(1)}%</strong>
              <span>全局平均使用率</span>
            </div>
          </div>
        </article>

        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>状态面板</p>
              <h3>服务器姿态</h3>
            </div>
          </div>
          <div className='status-list'>
            {data.servers.map((server) => (
              <div key={server.id} className='status-item'>
                <div className='status-item-main'>
                  <span className={`status-indicator ${server.status.toLowerCase() === 'online' ? 'ok' : 'down'}`} />
                  <div>
                    <strong>{server.name}</strong>
                    <span>{server.vendor}</span>
                  </div>
                </div>
                <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                  {server.status}
                </span>
              </div>
            ))}
            {!data.servers.length && <div className='empty-state'>/overview 暂时还没有返回服务器数据。</div>}
          </div>
        </article>
      </section>

      <section className='kpi-grid dashboard-kpis'>
        {data.kpis.map((kpi) => (
          <article key={kpi.label} className='metric-card'>
            <p>{kpi.label}</p>
            <h3>{kpi.value}</h3>
            <span>{kpi.trend}</span>
          </article>
        ))}
        {data.kpis.length === 0 && (
          <article className='metric-card muted'>
            <p>总览数据流</p>
            <h3>{loading ? '加载中…' : '暂无数据'}</h3>
            <span>等待 /overview 返回结果</span>
          </article>
        )}
      </section>

      <section className='license-grid'>
        {computed.highestUsage.map((server) => {
          const tone = getUsageTone(server.usage_percent)
          return (
            <article key={server.id} className={`license-card ${tone}`}>
              <div className='license-name'>{server.vendor}</div>
              <div className='license-usage'>{server.usage_percent.toFixed(1)}%</div>
              <div className='usage-bar'>
                <div className={`usage-fill ${tone}`} style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
              </div>
              <div className='license-detail'>
                {server.name} • {server.status}
              </div>
            </article>
          )
        })}
        {!computed.highestUsage.length && <div className='empty-state'>有服务器数据后，这里会显示高使用率卡片。</div>}
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>运行明细</p>
            <h3>服务器使用详情</h3>
          </div>
          <span className='status-pill'>{data.servers.length} 行</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table'>
            <thead>
              <tr>
                <th>服务器</th>
                <th>厂商</th>
                <th>状态</th>
                <th>峰值使用率</th>
                <th>风险</th>
              </tr>
            </thead>
            <tbody>
              {data.servers.map((server) => (
                <tr key={server.id}>
                  <td>
                    <div className='table-primary'>
                      <strong>{server.name}</strong>
                      <span>服务器 #{server.id}</span>
                    </div>
                  </td>
                  <td>{server.vendor}</td>
                  <td>
                    <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
                      {server.status}
                    </span>
                  </td>
                  <td>
                    <div className='usage-cell'>
                      <div className='bar-track slim'>
                        <div className={`bar-fill ${getUsageTone(server.usage_percent)}`} style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                      </div>
                      <span>{server.usage_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-pill ${getUsageTone(server.usage_percent) === 'danger' ? 'danger' : getUsageTone(server.usage_percent) === 'warning' ? 'warning' : 'online'}`}>
                      {getUsageTone(server.usage_percent) === 'danger'
                        ? '高风险'
                        : getUsageTone(server.usage_percent) === 'warning'
                          ? '关注'
                          : '稳定'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data.servers.length && <div className='empty-state padded'>/overview 暂时还没有返回明细行。</div>}
        </div>
      </section>
    </div>
  )
}
