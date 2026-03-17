import { useEffect, useMemo, useState } from 'react'
import { apiGet, apiPost } from '../services/api'

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

export default function Servers() {
  const [servers, setServers] = useState<Server[]>([])
  const [refreshing, setRefreshing] = useState(false)
  const [refreshMessage, setRefreshMessage] = useState('')

  const load = () => apiGet<Server[]>('/servers').then(setServers)

  useEffect(() => {
    load().catch(console.error)
    const timer = window.setInterval(() => {
      load().catch(console.error)
    }, 30000)
    return () => window.clearInterval(timer)
  }, [])

  async function refresh() {
    setRefreshing(true)
    setRefreshMessage('正在采集最新 lmstat / log 数据…')
    try {
      await apiPost('/servers/refresh')
      await load()
      setRefreshMessage('刷新完成，页面已更新。')
    } catch (error) {
      console.error(error)
      setRefreshMessage('刷新失败，请稍后再试。')
    } finally {
      setRefreshing(false)
      window.setTimeout(() => setRefreshMessage(''), 4000)
    }
  }

  const summary = useMemo(() => {
    const online = servers.filter((server) => server.status.toLowerCase() === 'online').length
    const highUsage = servers.filter((server) => server.usage_percent >= 80).length
    const avgFeatures = servers.length
      ? servers.reduce((sum, server) => sum + server.feature_count, 0) / servers.length
      : 0

    return { online, highUsage, avgFeatures }
  }, [servers])

  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>基础设施清单</p>
          <h3>服务器列表与采集控制</h3>
          <p>以白卡片后台视图展示端点状态、采集刷新能力以及当前容量压力。</p>
        </div>
        <div className='topbar-actions'>
          <button type='button' className='header-button secondary'>上传配置</button>
          <button type='button' className='header-button primary' onClick={refresh} disabled={refreshing}>
            {refreshing ? '刷新中…' : '运行采集'}
          </button>
        </div>
        {refreshMessage && <p className='eyebrow'>{refreshMessage}</p>}
      </section>

      <section className='kpi-grid compact'>
        <article className='metric-card'>
          <p>在线服务器</p>
          <h3>{summary.online}</h3>
          <span>共 {servers.length || 0} 个已登记端点</span>
        </article>
        <article className='metric-card'>
          <p>高压力节点</p>
          <h3>{summary.highUsage}</h3>
          <span>峰值使用率 ≥ 80%</span>
        </article>
        <article className='metric-card'>
          <p>平均特征数</p>
          <h3>{summary.avgFeatures.toFixed(1)}</h3>
          <span>每台服务器跟踪的 feature 数</span>
        </article>
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>采集端点</p>
            <h3>服务器明细表</h3>
          </div>
          <span className='status-pill'>{servers.length} 行</span>
        </div>
        <div className='table-wrap'>
          <table className='data-table'>
            <thead>
              <tr>
                <th>名称</th>
                <th>厂商</th>
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
                      <span>服务器 #{server.id}</span>
                    </div>
                  </td>
                  <td>{server.vendor}</td>
                  <td>
                    <span className='mono'>{server.host}:{server.port}</span>
                  </td>
                  <td>
                    <span className={`status-pill ${server.status.toLowerCase() === 'online' ? 'online' : 'warning'}`}>
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
          {!servers.length && <div className='empty-state padded'>/servers 暂时还没有返回服务器数据。</div>}
        </div>
      </section>
    </div>
  )
}
