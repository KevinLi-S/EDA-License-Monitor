const chartCards = [
  {
    title: 'Utilization trend',
    caption: 'Reserved for time-series API output and vendor filtering.',
  },
  {
    title: 'Feature demand mix',
    caption: 'Pie / stacked-bar treatment can land later without restructuring the shell.',
  },
  {
    title: 'Capacity forecast',
    caption: 'Ideal place for breach prediction and expansion recommendations.',
  },
]

export default function Analytics() {
  return (
    <div className='page-stack'>
      <section className='section-header'>
        <div>
          <p className='eyebrow'>Analytics workspace</p>
          <h2>Capacity narrative and trend placeholders</h2>
          <p>The backend can grow richer reporting later; for now this page frames the story cleanly for stakeholders.</p>
        </div>
        <span className='status-pill'>Phase-3 ready</span>
      </section>

      <section className='dashboard-grid secondary'>
        {chartCards.map((card, index) => (
          <article key={card.title} className='panel'>
            <div className='panel-header'>
              <div>
                <p className='eyebrow'>Module {index + 1}</p>
                <h3>{card.title}</h3>
              </div>
            </div>
            <div className='chart-placeholder'>
              <div className='chart-lines' />
              <p>{card.caption}</p>
            </div>
          </article>
        ))}
      </section>

      <section className='panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>Narrative helpers</p>
            <h3>What this page should eventually answer</h3>
          </div>
        </div>
        <ul className='bullet-list'>
          <li>Which vendors are trending toward capacity risk?</li>
          <li>Which feature pools justify procurement or cleanup action first?</li>
          <li>How does collector freshness affect trust in the dashboard snapshot?</li>
        </ul>
      </section>
    </div>
  )
}
