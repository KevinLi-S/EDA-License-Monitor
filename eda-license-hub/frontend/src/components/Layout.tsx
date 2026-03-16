import { Link, Outlet, useLocation } from 'react-router-dom'

const sections = [
  {
    title: 'Monitoring',
    items: [
      { path: '/dashboard', label: 'Dashboard', icon: '▣', description: 'Overview, trends, and server posture' },
      { path: '/analytics', label: 'Analytics', icon: '◔', description: 'Capacity outlook and trend modules' },
    ],
  },
  {
    title: 'Operations',
    items: [
      { path: '/servers', label: 'Servers', icon: '◫', description: 'Collector endpoints and refresh control' },
      { path: '/alerts', label: 'Alerts', icon: '△', description: 'Escalations and response workflow' },
    ],
  },
]

const flatItems = sections.flatMap((section) => section.items)

export default function Layout() {
  const location = useLocation()
  const activeItem = flatItems.find((item) => location.pathname.startsWith(item.path)) ?? flatItems[0]

  return (
    <div className='app-shell'>
      <aside className='sidebar'>
        <div className='sidebar-header'>
          <div className='brand-mark'>EL</div>
          <div>
            <h1 className='brand-title'>EDA License Monitor</h1>
            <p className='brand-subtitle'>轻量运维看板</p>
          </div>
        </div>

        <nav className='sidebar-nav'>
          {sections.map((section) => (
            <div key={section.title} className='nav-section'>
              <p className='nav-section-title'>{section.title}</p>
              <div className='nav-group'>
                {section.items.map((item) => {
                  const active = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`nav-item${active ? ' active' : ''}`}
                    >
                      <div className='nav-item-main'>
                        <span className='nav-icon'>{item.icon}</span>
                        <div>
                          <span className='nav-label'>{item.label}</span>
                          <small>{item.description}</small>
                        </div>
                      </div>
                      {active && <span className='nav-badge'>Live</span>}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className='sidebar-panel'>
          <p className='nav-section-title'>Workspace note</p>
          <strong>接口保持不变</strong>
          <span>
            Dashboard 与 Servers 仍沿用 phase-2 原有接口路径，仅更新展示层样式与布局。
          </span>
        </div>
      </aside>

      <main className='main-panel'>
        <header className='topbar'>
          <div>
            <p className='eyebrow'>监控工作台</p>
            <h2>{activeItem.label}</h2>
            <p className='topbar-copy'>{activeItem.description}</p>
          </div>
          <div className='topbar-actions'>
            <button type='button' className='header-button secondary'>导出</button>
            <button type='button' className='header-button secondary'>分享</button>
            <button type='button' className='header-button primary'>刷新视图</button>
          </div>
        </header>

        <section className='content-shell'>
          <Outlet />
        </section>
      </main>
    </div>
  )
}
