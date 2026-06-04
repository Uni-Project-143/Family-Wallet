import axios from 'axios'
import { getApiErrorMessage } from '../utils/apiError'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Додає Bearer token до кожного запиту
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обробляє помилки глобально:
// - прикріплює готове повідомлення error.userMessage (для всіх викликів)
// - на 401 поза auth-ендпоінтами чистить сесію і кидає на /login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Єдине змістовне повідомлення — доступне будь-якому caller через err.userMessage
    error.userMessage = getApiErrorMessage(error)

    const url = error.config?.url || ''
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/register')

    // 401 на захищених ендпоінтах — сесія недійсна → на логін
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('currentUser')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
