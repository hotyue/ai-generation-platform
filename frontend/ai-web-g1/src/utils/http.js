import axios from 'axios'
import { getToken } from './auth'

const http = axios.create({
  // ⬇️ 关键改动：使用 Vite 环境变量
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

// 请求拦截：自动加 token
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误提示
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    alert(err.response?.data?.detail || '请求失败')
    return Promise.reject(err)
  }
)

export default http
