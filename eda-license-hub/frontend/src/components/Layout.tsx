import { Link, Outlet, useLocation } from 'react-router-dom'

const items = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/servers', label: 'Servers' },
  { path: '/alerts', label: 'Alerts' },
  { path: '/analytics', label: 'Analytics' },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', minHeight: '100vh', fontFamily: 'Arial, sans-serif' }}>
      <aside style={{ background: '#111827', color: '#fff', padding: '24px 16px' }}>
        <h2 style={{ marginTop: 0 }}>EDA License</h2>
        <nav style={{ display: 'grid', gap: 8 }}>
          {items.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                color: '#fff',
                textDecoration: 'none',
                padding: '10px 12px',
                borderRadius: 8,
                background: location.pathname === item.path ? '#2563eb' : 'transparent',
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main style={{ background: '#f3f4f6', padding: 24 }}>
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, minHeight: 'calc(100vh - 48px)' }}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}
