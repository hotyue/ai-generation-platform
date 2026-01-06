import router from '@/router'
import { routeWsMessage } from '@/utils/ws_router'

let ws = null
let currentToken = null
let pendingTimer = null

// 登录页挂起机制
let pendingToken = null
let hasRouteHook = false

/**
 * 从 API_BASE_URL 派生 WS Base
 * http  -> ws
 * https -> wss
 * 去掉 /api
 */
function getWsBaseUrl() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL is not defined')
  }

  const url = new URL(apiBaseUrl)
  const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${wsProtocol}//${url.host}`
}

function isGuestPath(path) {
  return path === '/login' || path === '/register'
}

function ensureRouteHook() {
  if (hasRouteHook) return
  hasRouteHook = true

  router.afterEach(() => {
    if (!pendingToken) return
    const path = router.currentRoute.value.path
    if (isGuestPath(path)) return

    const token = pendingToken
    pendingToken = null
    startAccountStatusWS(token)
  })
}

/**
 * =========================
 * 启动 WS（登录后调用）
 * =========================
 */
export function startAccountStatusWS(token) {
  if (!token) return

  const path = router.currentRoute.value.path

  // 登录 / 注册页 → 挂起，等待离开再启动
  if (isGuestPath(path)) {
    pendingToken = token
    ensureRouteHook()
    return
  }

  // token 未变化且 ws 已存在 → 不重复建立
  if (ws && currentToken === token) {
    return
  }

  // token 变化 / 残留 ws → 强制清理
  stopAccountStatusWS()
  currentToken = token

  // 防抖：避免切页抖动
  if (pendingTimer) {
    clearTimeout(pendingTimer)
    pendingTimer = null
  }

  pendingTimer = setTimeout(() => {
    pendingTimer = null

    const curPath = router.currentRoute.value.path
    if (isGuestPath(curPath)) {
      pendingToken = token
      ensureRouteHook()
      return
    }

    const wsBaseUrl = getWsBaseUrl()
    const url = `${wsBaseUrl}/ws?token=${token}`

    const localWs = new WebSocket(url)
    ws = localWs

    /**
     * =========================
     * WS 消息入口（只做路由转发）
     * =========================
     */
    localWs.onmessage = (event) => {
      // 防止旧 ws 污染
      if (localWs !== ws) return

      try {
        const msg = JSON.parse(event.data)
        routeWsMessage(msg)
      } catch {
        // 非法消息直接忽略
      }
    }

    localWs.onclose = () => {
      if (localWs === ws) {
        ws = null
        currentToken = null
      }
    }

    localWs.onerror = () => {
      if (localWs === ws) {
        ws = null
        currentToken = null
      }
    }
  }, 50)
}

/**
 * =========================
 * 停止 WS（退出 / 切换账号）
 * =========================
 */
export function stopAccountStatusWS() {
  if (pendingTimer) {
    clearTimeout(pendingTimer)
    pendingTimer = null
  }

  pendingToken = null

  if (ws) {
    ws.close()
    ws = null
    currentToken = null
  }
}

/**
 * =========================
 * 会话级强制退出
 * =========================
 */
export function forceLogout() {
  stopAccountStatusWS()

  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }
}
