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
      <section className='section-header'>
        <div>
          <p className='eyebrow'>Alert center</p>
          <h2>Escalations and response workflow</h2>
          <p>This screen is intentionally presentation-ready placeholder UI: polished enough for demos, honest about phase-3 depth.</p>
        </div>
        <span className='status-pill danger'>Preview</span>
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

      <section className='panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>Suggested widgets</p>
            <h3>Next-step modules</h3>
          </div>
        </div>
        <ul className='bullet-list'>
          <li>Severity-filtered queue with assignee, acknowledged timestamp, and source server.</li>
          <li>Webhook/email bridge for high-severity collector failures.</li>
          <li>Alert-to-analytics drilldown for fast explanation during demos or incident review.</li>
        </ul>
      </section>
    </div>
  )
}
