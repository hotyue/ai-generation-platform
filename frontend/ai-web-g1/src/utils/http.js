import axios from 'axios'
import { getToken, clearToken } from './auth'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

/**
 * =========================
 * 全局状态锁
 * =========================
 * 用于防止 Token 失效时引发的无限重定向和并发注销报错
 */
let hasForcedLogout = false
let isLoggingOut = false   // ⭐ 退出进行中熔断

/**
 * =========================
 * HTTP 退出态重置 (继承自并发控制补丁)
 * =========================
 * 新会话（如重新登录后）必须显式清理此状态，否则新用户的请求会被前一次的退出态错误拦截
 */
export function resetHttpLogoutState() {
  hasForcedLogout = false
  isLoggingOut = false
}

/**
 * =========================
 * ⭐ 核心修缮：开源环境通用部署适配 (动态 API 寻址)
 * =========================
 * 彻底告别 Vite 构建期死板绑定的 VITE_API_BASE_URL！
 * 采用“三级降级策略”实现“一次构建，到处运行”的通用 Docker 镜像：
 * * 1. window.__ENV__?.API_BASE_URL : 生产环境 Docker 运行时注入的最优先配置 (由 env.js 提供)
 * 2. import.meta.env.VITE_API_BASE_URL : 本地开发环境的兜底配置 (由 .env 提供)
 * 3. '/api' : 极限情况下的相对路径降级 (配合 Nginx 反向代理完美运行)
 */
const BASE_URL = window.__ENV__?.API_BASE_URL || 
                 import.meta.env.VITE_API_BASE_URL || 
                 '/api';

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

/**
 * =========================
 * 请求拦截器
 * =========================
 */
http.interceptors.request.use((config) => {
  /**
   * 1. 退出熔断机制：若系统已进入退出流程，直接中断多余的请求，防止因旧请求超时报错导致前端弹窗乱飞
   */
  if (isLoggingOut) {
    return Promise.reject(new axios.Cancel('Logging out'))
  }

  /**
   * 2. 身份注入：携带 JWT Token
   * 注：HTTP 层纯粹做数据搬运，不再越权裁决用户的 account_status
   */
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

/**
 * =========================
 * 响应拦截器 (稳定裁剪版)
 * =========================
 * 核心哲学：HTTP 只管网络层错误，账号业务状态的裁决全部交由 WebSocket 统一仲裁
 */
http.interceptors.response.use(
  (res) => res.data,

  async (err) => {
    const authStore = useAuthStore()

    // 1. 若已在退出流程中，拦截所有新产生的报错，避免对用户造成视觉干扰
    if (isLoggingOut || hasForcedLogout) {
      return Promise.reject(err)
    }

    // 2. 无 response（通常是因为被代码主动 Cancel、或是由于网络断连导致没有收到服务端任何响应）
    if (!err.response) {
      return Promise.reject(err)
    }

    // 3. 未登录态隔离：如果本地没有 token，或者正处于登录页，直接放行错误让对应组件自行处理
    if (!authStore.token || router.currentRoute.value.path === '/login') {
      return Promise.reject(err)
    }

    /**
     * =========================
     * ⚠️ 状态裁决分离说明 (历史架构升级记录)
     * =========================
     * 过去：一旦 HTTP 收到 401/403，会立刻判定为 Token 失效并强行踢回登录页。
     * 现在：彻底剥离！HTTP 层不再基于 401/403 推断账号是否被封禁或余额不足。
     * 所有的状态裁决权已全盘移交至 WebSocket 长连接实时下发的消息。
     * 这样从根本上杜绝了页面并发请求接口时，导致的“多重踢出”与路由冲突死循环。
     * =========================
     */

    return Promise.reject(err)
  }
)

/**
 * =========================
 * 会话级强制退出 (底层清理)
 * =========================
 * 仅供 WebSocket 收到后端明确踢出指令，或用户主动点击“退出账号”时显式调用
 */
export function forceLogout(authStore) {
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