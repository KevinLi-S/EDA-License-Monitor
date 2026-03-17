export const mockDashboard = {
  vendor_count: 4,
  server_count: 9,
  open_alerts: 3,
  top_busy_features: [
    { feature: 'VCS', vendor: 'synopsys', server: 'snps-lic-01', total: 100, used: 83, free: 17, collected_at: '2026-03-05T12:00:00+08:00' },
    { feature: 'DC', vendor: 'synopsys', server: 'snps-lic-01', total: 40, used: 36, free: 4, collected_at: '2026-03-05T12:00:00+08:00' },
    { feature: 'Virtuoso', vendor: 'cadence', server: 'cdns-lic-01', total: 60, used: 41, free: 19, collected_at: '2026-03-05T12:00:00+08:00' }
  ],
  risk_summary: {
    critical: 1,
    high: 2,
    medium: 1,
    findings: [
      { vendor: 'ansys', severity: 'critical', issue: 'License integrity warning detected', detail: 'CVD License file has been Tampered' },
      { vendor: 'ansys', severity: 'high', issue: 'Ecomms disabled', detail: 'Encrypted Communication disabled' },
      { vendor: 'ansys', severity: 'high', issue: 'External filters disabled', detail: 'EXTERNAL FILTERS are OFF' },
      { vendor: 'synopsys', severity: 'medium', issue: 'No options file', detail: 'Options file used: None' }
    ]
  }
}

export const mockServers = [
  { id: 1, name: 'snps-lic-01', vendor: 'synopsys', host: '10.0.0.11', port: 27000, status: 'online', last_seen_at: '2026-03-05 12:00:00' },
  { id: 2, name: 'cdns-lic-01', vendor: 'cadence', host: '10.0.0.12', port: 5280, status: 'online', last_seen_at: '2026-03-05 12:00:00' },
  { id: 3, name: 'mnt-lic-01', vendor: 'mentor', host: '10.0.0.13', port: 1717, status: 'degraded', last_seen_at: '2026-03-05 11:59:00' }
]

export const mockServerActions = [
  { id: 1, server: 'snps-lic-01', action: 'restart', status_after: 'restarting', message: 'service restarting', created_at: '2026-03-05 12:08:00' },
  { id: 2, server: 'cdns-lic-01', action: 'start', status_after: 'online', message: 'service started', created_at: '2026-03-05 11:58:00' }
]

export const mockFeatures = [
  { feature: 'VCS', vendor: 'synopsys', server: 'snps-lic-01', total: 100, used: 83, free: 17, collected_at: '2026-03-05 12:00:00' },
  { feature: 'DC', vendor: 'synopsys', server: 'snps-lic-01', total: 40, used: 36, free: 4, collected_at: '2026-03-05 12:00:00' },
  { feature: 'Virtuoso', vendor: 'cadence', server: 'cdns-lic-01', total: 60, used: 41, free: 19, collected_at: '2026-03-05 12:00:00' }
]

export const mockAlerts = [
  { id: 1, type: 'low_free', severity: 'high', message: 'DC free licenses < 10', status: 'open', created_at: '2026-03-05 11:58:00' },
  { id: 2, type: 'server_down', severity: 'high', message: 'ansys-lic-02 heartbeat missing', status: 'open', created_at: '2026-03-05 11:30:00' }
]

export const mockLicenseKeys = [
  { id: 1, vendor: 'synopsys', feature: 'VCSCompiler_Net', version: '2023.09', total: 100, used: 83, expiry: '2026-12-31', server: 'snps-lic-01' },
  { id: 2, vendor: 'synopsys', feature: 'Verdi', version: '2023.09', total: 30, used: 12, expiry: '2026-10-31', server: 'snps-lic-01' },
  { id: 3, vendor: 'ansys', feature: 'redhawk', version: '2024R1', total: 50, used: 44, expiry: '2026-08-15', server: 'ansys-lic-01' },
  { id: 4, vendor: 'cadence', feature: 'Virtuoso', version: 'ICADVM20.1', total: 60, used: 41, expiry: '2027-01-30', server: 'cdns-lic-01' }
]
