import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Додаємо JWT до кожного запиту автоматично
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Якщо токен протермінований — редиректимо на /login
apiClient.interceptors.response.use(
  (response) => {
    // Якщо бекенд повернув новий токен — перезаписуємо
    const freshToken = response.headers['x-new-token']
    if (freshToken) {
      localStorage.setItem('accessToken', freshToken)
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default apiClient
