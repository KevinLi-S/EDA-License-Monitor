import { useEffect, useState } from 'react'
import { apiGet } from '../services/api'

export function ServersPage() {
  const [servers, setServers] = useState([])
  useEffect(() => {
    apiGet('/servers').then(setServers).catch(() => {})
  }, [])

  return (
    <section className="panel">
      <h2>Servers</h2>
      <p>Phase-1 页面骨架：后续补服务器详情、控制动作、日志与 checkout 视图。</p>
      <table className="table">
        <thead><tr><th>Name</th><th>Vendor</th><th>Endpoint</th><th>Status</th><th>Usage</th></tr></thead>
        <tbody>
          {servers.map((server) => (
            <tr key={server.id}>
              <td>{server.name}</td><td>{server.vendor}</td><td>{server.host}:{server.port}</td><td>{server.status}</td><td>{server.usage_percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
