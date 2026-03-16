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
            <h1 className='brand-title'>EDA License Hub</h1>
            <p className='brand-subtitle'>Light operations dashboard</p>
          </div>
        </div>

        <div className='sidebar-status'>
          <span className='status-dot' />
          <div>
            <strong>System healthy</strong>
            <span>Phase-2 frontend shell on live route entry</span>
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
          <strong>API contract unchanged</strong>
          <span>
            Dashboard and server views keep the same phase-2 fetch paths while adopting the new admin-style UI.
          </span>
        </div>
      </aside>

      <main className='main-panel'>
        <header className='topbar'>
          <div>
            <p className='eyebrow'>Monitoring workspace</p>
            <h2>{activeItem.label}</h2>
            <p className='topbar-copy'>{activeItem.description}</p>
          </div>
          <div className='topbar-actions'>
            <button type='button' className='header-button secondary'>Export</button>
            <button type='button' className='header-button secondary'>Share</button>
            <button type='button' className='header-button primary'>Refresh View</button>
          </div>
        </header>

        <section className='content-shell'>
          <Outlet />
        </section>
      </main>
    </div>
  )
}
