const alertFeed = [
  {
    severity: 'critical',
    title: 'Collector failure escalation',
    detail: 'Wire backend collector exceptions into this feed when phase-3 notification workflows land.',
  },
  {
    severity: 'warning',
    title: 'License saturation watch',
    detail: 'Use this view to highlight vendors or features that remain close to denial thresholds.',
  },
  {
    severity: 'info',
    title: 'Operator acknowledgement trail',
    detail: 'Reserved for mute / acknowledge / assign actions without changing the current phase-2 API surface.',
  },
]

export default function Alerts() {
  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>告警中心</p>
          <h3>告警升级与响应流程</h3>
          <p>当前仍是完善过的占位模块，用来保持整体外观完整，同时不额外虚构新的后端接口。</p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill danger'>2 个待处理项</span>
          <span className='status-pill'>预览模块</span>
        </div>
      </section>

      <section className='dashboard-grid secondary'>
        {alertFeed.map((item) => (
          <article key={item.title} className='panel'>
            <div className='panel-header'>
              <div>
                <p className='eyebrow'>{item.severity.toUpperCase()}</p>
                <h3>{item.title}</h3>
              </div>
              <span className={`status-pill ${item.severity === 'critical' ? 'danger' : item.severity === 'warning' ? 'warning' : ''}`}>
                {item.severity}
              </span>
            </div>
            <p className='panel-copy'>{item.detail}</p>
          </article>
        ))}
      </section>

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>建议模块</p>
            <h3>下一步可扩展项</h3>
          </div>
        </div>
        <ul className='bullet-list'>
          <li>按严重级别筛选的队列，补充负责人、确认时间与来源服务器。</li>
          <li>为高严重级别采集失败接入 webhook 或邮件通知。</li>
          <li>从告警直接下钻到分析页，方便演示或排障时快速解释原因。</li>
        </ul>
      </section>
    </div>
  )
}
