const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost/ws'

export function connectDashboardSocket(onMessage) {
  const socket = new WebSocket(WS_BASE_URL)
  socket.onmessage = (event) => {
    const payload = event.data === 'pong' ? { type: 'pong' } : JSON.parse(event.data)
    onMessage(payload)
  }
  return socket
}
