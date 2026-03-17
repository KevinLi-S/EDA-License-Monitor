import axios from 'axios'

const defaultBaseUrl = `${window.location.protocol}//${window.location.hostname}:8000/api`

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || defaultBaseUrl,
})

export const useMock = String(import.meta.env.VITE_USE_MOCK || 'false').toLowerCase() === 'true'

export default api
