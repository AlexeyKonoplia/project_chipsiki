import axios from 'axios'

// Same-origin in production (nginx proxies /api); dev uses Vite proxy.
const api = axios.create({
  baseURL: '/',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token invalid/expired — drop it.
      localStorage.removeItem('token')
    }
    return Promise.reject(error)
  }
)

export default api
