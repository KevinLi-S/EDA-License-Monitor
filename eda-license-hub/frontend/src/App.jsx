import { NavLink, Route, Routes } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage'
import { ServersPage } from './pages/ServersPage'
import { AlertsPage } from './pages/AlertsPage'
import { AnalyticsPage } from './pages/AnalyticsPage'

const navItems = [
  ['/', 'Dashboard'],
  ['/servers', 'Servers'],
  ['/alerts', 'Alerts'],
  ['/analytics', 'Analytics'],
]

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">EDA License Dashboard</div>
        <nav>
          {navItems.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === '/'} className="nav-link">
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <header className="topbar">
          <div>
            <h1>Phase-1 Skeleton</h1>
            <p>FastAPI + React + Celery + PostgreSQL/Redis compose scaffold</p>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/servers" element={<ServersPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </main>
    </div>
  )
}
