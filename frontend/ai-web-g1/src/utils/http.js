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
let isLoggingOut = false   // ⭐ 退出进行中熔断

/**
 * =========================
 * ⭐ v1.0.11 关键补丁
 * 新会话必须显式清理 HTTP 退出态
 * =========================
 */
export function resetHttpLogoutState() {
  hasForcedLogout = false
  isLoggingOut = false
}

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

/**
 * =========================
 * 请求拦截（v1.0.11 修正版）
 * =========================
 */
http.interceptors.request.use((config) => {
  /**
   * ⭐ 已进入退出流程，直接中断
   */
  if (isLoggingOut) {
    return Promise.reject(new axios.Cancel('Logging out'))
  }

  /**
   * ⭐ 正常注入 token
   * ❗ v1.0.11：HTTP 层不再裁决 account_status
   */
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

/**
 * =========================
 * 响应拦截（v1.0.11 稳定裁剪版）
 * =========================
 */
http.interceptors.response.use(
  (res) => res.data,

  async (err) => {
    const authStore = useAuthStore()

    /**
     * =========================
     * 已在退出流程中，直接放行错误
     * =========================
     */
    if (isLoggingOut || hasForcedLogout) {
      return Promise.reject(err)
    }

    /**
     * 无 response（被中断 / Cancel / 网络异常）
     */
    if (!err.response) {
      return Promise.reject(err)
    }

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
     * ⚠️ v1.0.11 裁决重点（保持不动）
     *
     * HTTP 层：
     * - 不基于 401 / 403 推断 account_status
     * - 不执行 logout / 跳转
     *
     * 所有账号状态裁决：
     * → 由 WS + Router 统一完成
     * =========================
     */

    return Promise.reject(err)
  }
)

/**
 * =========================
 * 强制退出（保留，仅供 WS / 显式调用）
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
