import axios from 'axios'

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

// Обробляє 401 глобально — чистить сесію і кидає на логін
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthEndpoint =
      error.config?.url?.includes('/auth/login') || error.config?.url?.includes('/auth/register')

    // 401 на auth ендпоінтах — НЕ редіректимо
    // 401 на захищених ендпоінтах — редіректимо на /login
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('currentUser')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  },
)

export default apiClient
