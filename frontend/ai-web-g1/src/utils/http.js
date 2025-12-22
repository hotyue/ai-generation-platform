import axios from 'axios'
import { getToken, clearToken } from './auth'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

/**
 * =========================
 * 全局状态锁
 * =========================
 */
let hasForcedLogout = false
let isLoggingOut = false   // ⭐ 新增：退出进行中熔断

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

/**
 * =========================
 * 请求拦截
 * =========================
 */
http.interceptors.request.use((config) => {
  if (isLoggingOut) {
    // ⭐ 退出中，直接中断请求
    return Promise.reject(new axios.Cancel('Logging out'))
  }

  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * =========================
 * 响应拦截（最终稳定版）
 * =========================
 */
http.interceptors.response.use(
  (res) => res.data,

  async (err) => {
    const authStore = useAuthStore()

    /**
     * =========================
     * ⭐ 第一熔断：已在退出流程中
     * =========================
     */
    if (isLoggingOut || hasForcedLogout) {
      return Promise.reject(err)
    }

    /**
     * =========================
     * 无 response（被中断的并发请求）
     * =========================
     */
    if (!err.response) {
      return Promise.reject(err)
    }

    const status = err.response.status

    /**
     * =========================
     * 未登录态隔离
     * =========================
     */
    if (!authStore.token || router.currentRoute.value.path === '/login') {
      return Promise.reject(err)
    }

    /**
     * =========================
     * 401 / 403：账号治理入口（只允许一个）
     * =========================
     */
    if ((status === 401 || status === 403) && !isLoggingOut) {
      isLoggingOut = true

      try {
        await authStore.fetchMe()
        // fetchMe 成功，说明只是普通 403
        isLoggingOut = false
        return Promise.reject(err)
      } catch {
        forceLogout(authStore)
        return Promise.reject(err)
      }
    }

    return Promise.reject(err)
  }
)

/**
 * =========================
 * 强制退出（原子操作）
 * =========================
 */
function forceLogout(authStore) {
  if (hasForcedLogout) return

  hasForcedLogout = true
  isLoggingOut = true

  authStore.clearToken()
  clearToken()

  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }
}

export default http
