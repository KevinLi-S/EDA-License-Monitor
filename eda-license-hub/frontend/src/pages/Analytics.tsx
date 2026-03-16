import { useEffect, useMemo, useState } from 'react'
import { apiGet } from '../services/api'

type TrendPoint = {
  timestamp: string
  usage_percent: number
}

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

function formatTimeLabel(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function buildLinePath(points: number[], width: number, height: number) {
  if (!points.length) return ''
  const max = Math.max(...points, 1)
  const min = Math.min(...points, 0)
  const range = Math.max(max - min, 1)
  return points
    .map((point, index) => {
      const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width
      const y = height - ((point - min) / range) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

function buildAreaPath(points: number[], width: number, height: number) {
  if (!points.length) return ''
  const line = buildLinePath(points, width, height)
  return `${line} L ${width} ${height} L 0 ${height} Z`
}

function polarToCartesian(cx: number, cy: number, radius: number, angle: number) {
  return {
    x: cx + radius * Math.cos(angle),
    y: cy + radius * Math.sin(angle),
  }
}

function buildDonutSegment(startAngle: number, endAngle: number, outerRadius: number, innerRadius: number) {
  const cx = 80
  const cy = 80
  const startOuter = polarToCartesian(cx, cy, outerRadius, startAngle)
  const endOuter = polarToCartesian(cx, cy, outerRadius, endAngle)
  const startInner = polarToCartesian(cx, cy, innerRadius, startAngle)
  const endInner = polarToCartesian(cx, cy, innerRadius, endAngle)
  const largeArc = endAngle - startAngle > Math.PI ? 1 : 0

  return [
    `M ${startOuter.x} ${startOuter.y}`,
    `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${endOuter.x} ${endOuter.y}`,
    `L ${endInner.x} ${endInner.y}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${startInner.x} ${startInner.y}`,
    'Z',
  ].join(' ')
}

export default function Analytics() {
  const [trend, setTrend] = useState<TrendPoint[]>([])
  const [servers, setServers] = useState<Server[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      apiGet<TrendPoint[]>('/analytics/usage-trend'),
      apiGet<Server[]>('/servers'),
    ])
      .then(([trendData, serverData]) => {
        setTrend(trendData)
        setServers(serverData)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const trendChart = useMemo(() => {
    const values = trend.map((item) => item.usage_percent)
    return {
      linePath: buildLinePath(values, 520, 180),
      areaPath: buildAreaPath(values, 520, 180),
      max: values.length ? Math.max(...values) : 0,
      avg: values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0,
      latest: values.length ? values[values.length - 1] : 0,
    }
  }, [trend])

  const vendorMix = useMemo(() => {
    const grouped = servers.reduce<Record<string, { count: number; peak: number }>>((acc, server) => {
      const key = server.vendor || 'unknown'
      if (!acc[key]) acc[key] = { count: 0, peak: 0 }
      acc[key].count += 1
      acc[key].peak = Math.max(acc[key].peak, server.usage_percent)
      return acc
    }, {})

    const palette = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#e74c3c', '#1abc9c']
    const entries = Object.entries(grouped).map(([vendor, value], index) => ({
      vendor,
      count: value.count,
      peak: value.peak,
      color: palette[index % palette.length],
    }))
    const total = entries.reduce((sum, item) => sum + item.count, 0) || 1

    let angle = -Math.PI / 2
    return entries.map((item) => {
      const slice = (item.count / total) * Math.PI * 2
      const path = buildDonutSegment(angle, angle + slice, 66, 38)
      angle += slice
      return {
        ...item,
        ratio: (item.count / total) * 100,
        path,
      }
    })
  }, [servers])

  const rankedServers = useMemo(() => [...servers].sort((a, b) => b.usage_percent - a.usage_percent).slice(0, 6), [servers])

  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>分析工作区</p>
          <h3>真实趋势与容量图表</h3>
          <p>本页直接使用现有 phase-2 接口数据生成图表，不再展示占位示意图。</p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill'>{trend.length} 个趋势点</span>
          <span className='status-pill online'>{servers.length} 台服务器</span>
        </div>
      </section>

      <section className='kpi-grid compact'>
        <article className='metric-card'>
          <p>最新平均使用率</p>
          <h3>{trendChart.latest.toFixed(1)}%</h3>
          <span>来自 usage-trend 最后一个采样点</span>
        </article>
        <article className='metric-card'>
          <p>趋势均值</p>
          <h3>{trendChart.avg.toFixed(1)}%</h3>
          <span>基于当前返回的全部趋势点</span>
        </article>
        <article className='metric-card'>
          <p>峰值记录</p>
          <h3>{trendChart.max.toFixed(1)}%</h3>
          <span>趋势序列中的最高平均使用率</span>
        </article>
      </section>

      <section className='dashboard-grid secondary'>
        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>真实趋势</p>
              <h3>平均使用率变化</h3>
            </div>
            <span className='status-pill'>/analytics/usage-trend</span>
          </div>
          {trend.length ? (
            <div className='svg-chart-card'>
              <svg viewBox='0 0 560 240' className='svg-chart'>
                <g transform='translate(20,20)'>
                  {[0, 1, 2, 3, 4].map((line) => (
                    <line
                      key={line}
                      x1='0'
                      y1={line * 45}
                      x2='520'
                      y2={line * 45}
                      className='chart-grid-line'
                    />
                  ))}
                  <path d={trendChart.areaPath} className='chart-area' />
                  <path d={trendChart.linePath} className='chart-line' />
                  {trend.map((point, index) => {
                    const x = trend.length === 1 ? 260 : (index / (trend.length - 1)) * 520
                    const max = Math.max(...trend.map((item) => item.usage_percent), 1)
                    const min = Math.min(...trend.map((item) => item.usage_percent), 0)
                    const range = Math.max(max - min, 1)
                    const y = 180 - ((point.usage_percent - min) / range) * 180
                    return <circle key={`${point.timestamp}-${index}`} cx={x} cy={y} r='4' className='chart-point' />
                  })}
                </g>
              </svg>
              <div className='chart-axis-labels'>
                {trend.map((point) => (
                  <span key={point.timestamp}>{formatTimeLabel(point.timestamp)}</span>
                ))}
              </div>
            </div>
          ) : (
            <div className='empty-state padded'>{loading ? '趋势数据加载中…' : '暂无趋势数据。'}</div>
          )}
        </article>

        <article className='panel'>
          <div className='panel-header'>
            <div>
              <p className='eyebrow'>厂商分布</p>
              <h3>服务器来源占比</h3>
            </div>
            <span className='status-pill'>/servers</span>
          </div>
          {vendorMix.length ? (
            <div className='donut-layout'>
              <svg viewBox='0 0 160 160' className='donut-chart'>
                {vendorMix.map((item) => (
                  <path key={item.vendor} d={item.path} fill={item.color} />
                ))}
                <text x='80' y='76' textAnchor='middle' className='donut-center-label'>厂商数</text>
                <text x='80' y='98' textAnchor='middle' className='donut-center-value'>{vendorMix.length}</text>
              </svg>
              <div className='chart-legend'>
                {vendorMix.map((item) => (
                  <div key={item.vendor} className='legend-item'>
                    <span className='legend-dot' style={{ background: item.color }} />
                    <div>
                      <strong>{item.vendor}</strong>
                      <span>{item.count} 台 · 占比 {item.ratio.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className='empty-state padded'>{loading ? '厂商分布加载中…' : '暂无厂商分布数据。'}</div>
          )}
        </article>
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>热点列表</p>
            <h3>服务器峰值使用率排名</h3>
          </div>
          <span className='status-pill'>Top {rankedServers.length}</span>
        </div>
        {rankedServers.length ? (
          <div className='bar-rank-list'>
            {rankedServers.map((server) => (
              <div key={server.id} className='bar-rank-item'>
                <div className='bar-rank-head'>
                  <strong>{server.name}</strong>
                  <span>{server.vendor} · {server.usage_percent.toFixed(1)}%</span>
                </div>
                <div className='bar-track'>
                  <div className='bar-fill' style={{ width: `${Math.min(server.usage_percent, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className='empty-state padded'>{loading ? '排名数据加载中…' : '暂无服务器排名数据。'}</div>
        )}
      </section>
    </div>
  )
}
