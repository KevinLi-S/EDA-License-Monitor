class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private listeners: Map<string, Array<(data: any) => void>> = new Map()
  private url: string

  constructor() {
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  }

  connect(token?: string) {
    const wsUrl = token ? `${this.url}?token=${token}` : this.url

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected')
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected')
      this.scheduleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private handleMessage(message: any) {
    const { type, data } = message

    // Call all registered listeners for this message type
    const callbacks = this.listeners.get(type) || []
    callbacks.forEach((cb) => cb(data))

    // Also call wildcard listeners
    const wildcardCallbacks = this.listeners.get('*') || []
    wildcardCallbacks.forEach((cb) => cb(message))
  }

  on(messageType: string, callback: (data: any) => void) {
    if (!this.listeners.has(messageType)) {
      this.listeners.set(messageType, [])
    }
    this.listeners.get(messageType)!.push(callback)
  }

  off(messageType: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(messageType)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  private startHeartbeat() {
    setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, 30000) // 30 seconds
  }

  private scheduleReconnect() {
    this.reconnectTimer = window.setTimeout(() => {
      const token = localStorage.getItem('auth_token')
      this.connect(token || undefined)
    }, 5000) // Reconnect after 5 seconds
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }
}

export default new WebSocketService()
