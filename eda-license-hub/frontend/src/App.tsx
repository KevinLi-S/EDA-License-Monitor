import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Servers from './pages/Servers'
import Alerts from './pages/Alerts'
import Analytics from './pages/Analytics'
import LicenseKeys from './pages/LicenseKeys'
import LicenseUsage from './pages/LicenseUsage'
import FeatureUsage from './pages/FeatureUsage'
import UserRanking from './pages/UserRanking'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout />}>
          <Route index element={<Navigate to='/dashboard' replace />} />
          <Route path='dashboard' element={<Dashboard />} />
          <Route path='servers' element={<Servers />} />
          <Route path='license-keys' element={<LicenseKeys />} />
          <Route path='license-usage' element={<LicenseUsage />} />
          <Route path='feature-usage' element={<FeatureUsage />} />
          <Route path='user-ranking' element={<UserRanking />} />
          <Route path='alerts' element={<Alerts />} />
          <Route path='analytics' element={<Analytics />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
