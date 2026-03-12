import { Layout, Menu, Space, Tag, Typography } from 'antd'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ServersPage from './pages/ServersPage'
import AlertsPage from './pages/AlertsPage'
import LicenseKeysPage from './pages/LicenseKeysPage'
import LogsPage from './pages/LogsPage'
import UploadPage from './pages/UploadPage'

const { Header, Content, Sider } = Layout

export default function App() {
  const location = useLocation()
  const selected = location.pathname === '/' ? '/dashboard' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={236} theme="dark" style={{ boxShadow: '2px 0 14px rgba(0,0,0,.12)' }}>
        <div style={{ height: 72, padding: '14px 18px', color: '#fff' }}>
          <div style={{ fontWeight: 800, fontSize: 18 }}>EDA License Hub</div>
          <div style={{ opacity: 0.72, fontSize: 12, marginTop: 4 }}>Monitor · Operate · Audit</div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selected]}
          items={[
            { key: '/dashboard', label: <Link to="/dashboard">📊 总览 Dashboard</Link> },
            { key: '/servers', label: <Link to="/servers">🖥️ 服务管理 Servers</Link> },
            { key: '/license-keys', label: <Link to="/license-keys">🔑 Feature 使用情况</Link> },
            { key: '/alerts', label: <Link to="/alerts">🚨 告警中心 Alerts</Link> },
            { key: '/logs', label: <Link to="/logs">📜 日志中心 Logs</Link> },
            { key: '/upload', label: <Link to="/upload">📤 数据接入 Upload</Link> },
          ]}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: 'linear-gradient(90deg, #0f172a 0%, #1e3a8a 40%, #0f766e 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            color: '#fff',
            paddingInline: 24,
          }}
        >
          <div>
            <Typography.Title level={4} style={{ margin: 0, color: '#fff' }}>
              License Monitoring & Management Console
            </Typography.Title>
            <Typography.Text style={{ color: 'rgba(255,255,255,.78)' }}>
              面向模拟生产环境的 EDA License 运维控制台
            </Typography.Text>
          </div>
          <Space>
            <Tag color="cyan">v1.3.2</Tag>
            <Tag color="geekblue">test env: 192.168.110.128</Tag>
          </Space>
        </Header>
        <Content style={{ padding: 20, background: '#f5f7fb' }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/servers" element={<ServersPage />} />
            <Route path="/license-keys" element={<LicenseKeysPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/upload" element={<UploadPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
