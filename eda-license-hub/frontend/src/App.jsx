import { Layout, Menu, Typography } from 'antd'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ServersPage from './pages/ServersPage'
import FeaturesPage from './pages/FeaturesPage'
import AlertsPage from './pages/AlertsPage'

const { Header, Content, Sider } = Layout

export default function App() {
  const location = useLocation()
  const selected = location.pathname === '/' ? '/dashboard' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark">
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700 }}>
          EDA License Hub
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selected]}
          items={[
            { key: '/dashboard', label: <Link to="/dashboard">📊 Dashboard</Link> },
            { key: '/servers', label: <Link to="/servers">🖥️ Servers</Link> },
            { key: '/features', label: <Link to="/features">🧩 Features</Link> },
            { key: '/alerts', label: <Link to="/alerts">🚨 Alerts</Link> },
          ]}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: 'linear-gradient(90deg, #141e30 0%, #243b55 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            color: '#fff',
          }}
        >
          <Typography.Title level={4} style={{ margin: 0, color: '#fff' }}>
            License Service Management Console
          </Typography.Title>
          <span style={{ opacity: 0.9 }}>MVP</span>
        </Header>
        <Content style={{ padding: 20, background: '#f5f7fb' }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/servers" element={<ServersPage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
