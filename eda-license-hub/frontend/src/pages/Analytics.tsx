const chartCards = [
  {
    title: 'Utilization trend',
    caption: 'Reserved for time-series API output and vendor filtering.',
  },
  {
    title: 'Feature demand mix',
    caption: 'Pie or stacked-bar treatment can land later without restructuring the shell.',
  },
  {
    title: 'Capacity forecast',
    caption: 'Ideal place for breach prediction and expansion recommendations.',
  },
]

export default function Analytics() {
  return (
    <div className='page-stack'>
      <section className='section-header-card'>
        <div>
          <p className='eyebrow'>分析工作区</p>
          <h3>容量趋势与叙事模块</h3>
          <p>沿用同一套浅色后台风格，同时如实表达当前 phase-2 的能力边界。</p>
        </div>
        <div className='header-chip-row'>
          <span className='status-pill'>可扩展到 Phase-3</span>
          <span className='status-pill online'>界面已对齐</span>
        </div>
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

      <section className='panel table-panel'>
        <div className='panel-header'>
          <div>
            <p className='eyebrow'>分析目标</p>
            <h3>这个页面未来应回答的问题</h3>
          </div>
        </div>
        <ul className='bullet-list'>
          <li>哪些厂商正在逐步接近容量风险？</li>
          <li>哪些 feature 池最值得优先采购或清理？</li>
          <li>采集新鲜度会如何影响大家对当前总览数据的信任度？</li>
        </ul>
      </section>
    </div>
  )
}
