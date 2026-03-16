import { Link, Outlet, useLocation } from 'react-router-dom'

const items = [
  { path: '/dashboard', label: 'Control Center', description: 'KPIs, fleet health, today summary' },
  { path: '/servers', label: 'Server Fleet', description: 'Collector refresh and endpoint status' },
  { path: '/alerts', label: 'Alerts', description: 'Risk feed and escalation queue' },
  { path: '/analytics', label: 'Analytics', description: 'Utilization patterns and capacity' },
]

export default function Layout() {
  const location = useLocation()
  const activeItem = items.find((item) => location.pathname.startsWith(item.path)) ?? items[0]

  return (
    <div className='app-shell'>
      <aside className='sidebar'>
        <div>
          <div className='brand-mark'>EL</div>
          <div className='brand-title'>EDA License Hub</div>
          <div className='brand-subtitle'>Phase-2 operations cockpit</div>
        </div>

        <nav className='nav-list'>
          {items.map((item) => {
            const active = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item${active ? ' active' : ''}`}
              >
                <span>{item.label}</span>
                <small>{item.description}</small>
              </Link>
            )
          })}
        </nav>

        <div className='sidebar-panel'>
          <p className='eyebrow'>Live posture</p>
          <strong>Collector loop online</strong>
          <span>Keep this screen open for demos, standups, and lightweight ops review.</span>
        </div>
      </aside>

      <main className='main-panel'>
        <header className='topbar'>
          <div>
            <p className='eyebrow'>Monitoring workspace</p>
            <h1>{activeItem.label}</h1>
            <p className='topbar-copy'>{activeItem.description}</p>
          </div>
          <div className='topbar-badges'>
            <span className='status-pill online'>Phase 2 Demo</span>
            <span className='status-pill'>API contract preserved</span>
          </div>
        </header>

        <section className='content-card'>
          <Outlet />
        </section>
      </main>
    </div>
  )
}
