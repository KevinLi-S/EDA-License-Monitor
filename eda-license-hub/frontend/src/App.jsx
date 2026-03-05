import { Layout, Menu } from 'antd'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ServersPage from './pages/ServersPage'
import FeaturesPage from './pages/FeaturesPage'
import AlertsPage from './pages/AlertsPage'

const { Header, Content } = Layout

export default function App() {
  const location = useLocation()
  const selected = location.pathname === '/' ? '/dashboard' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ color: '#fff', fontWeight: 700 }}>EDA License Hub</Header>
      <Menu
        mode="horizontal"
        selectedKeys={[selected]}
        items={[
          { key: '/dashboard', label: <Link to="/dashboard">Dashboard</Link> },
          { key: '/servers', label: <Link to="/servers">Servers</Link> },
          { key: '/features', label: <Link to="/features">Features</Link> },
          { key: '/alerts', label: <Link to="/alerts">Alerts</Link> },
        ]}
      />
      <Content style={{ padding: 20 }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/servers" element={<ServersPage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>
      </Content>
    </Layout>
  )
}
