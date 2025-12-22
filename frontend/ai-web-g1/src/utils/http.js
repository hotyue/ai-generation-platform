import axios from 'axios'
import { getToken, clearToken } from './auth'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  // ⬇️ 使用 Vite 环境变量
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

/**
 * =========================
 * 请求拦截：自动加 token
 * =========================
 */
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * =========================
 * 响应拦截（关键治理点）
 * =========================
 */
http.interceptors.response.use(
  (res) => {
    return res.data
  },
  (err) => {
    const authStore = useAuthStore()

    // ⚠️ 网络级错误（例如服务器不可达）
    if (!err.response) {
      console.error('Network Error:', err)
      alert('网络异常，请稍后重试')
      return Promise.reject(err)
    }

    const status = err.response.status
    const detail = err.response.data?.detail

    /**
     * =========================
     * 🚨 401 / 403：账号失效统一收敛
     * =========================
     *
     * 场景覆盖：
     * - token 过期
     * - 管理员运行期封禁账号
     * - account_status = banned
     *
     * 行为：
     * - 清 token
     * - 清 Pinia user
     * - 跳转登录页
     * - ❗ 只执行一次，避免多次跳转
     */
    if (status === 401 || status === 403) {
      if (authStore.token) {
        console.warn('Auth invalid, force logout:', detail)

        authStore.clearToken()
        clearToken()

        // 使用 replace，防止回退
        router.replace('/login')
      }

      return Promise.reject(err)
    }

    /**
     * =========================
     * 其他业务错误（422 / 400 / 500）
     * =========================
     */
    alert(detail || '请求失败')
    return Promise.reject(err)
  }
)

export default http
