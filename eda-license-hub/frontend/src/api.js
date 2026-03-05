import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
})

export const useMock = String(import.meta.env.VITE_USE_MOCK || 'false').toLowerCase() === 'true'

export default api
