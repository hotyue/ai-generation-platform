import { useAccountStatusStore } from '@/stores/accountStatus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

let ws = null
let currentToken = null
let pendingTimer = null

// ⭐ 新增：登录页调用 start 时先挂起，等路由离开登录页再真正启动
let pendingToken = null
let hasRouteHook = false

/**
 * 从 API_BASE_URL 派生 WS Base
 * 规则：
 *   http  -> ws
 *   https -> wss
 *   去掉 /api
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

  // 只注册一次：离开登录/注册页时，如果有挂起 token，就启动
  router.afterEach(() => {
    if (!pendingToken) return
    const path = router.currentRoute.value.path
    if (isGuestPath(path)) return

    const token = pendingToken
    pendingToken = null
    // 这里会走正常启动逻辑（含 token 变化清理）
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

  /**
   * ⭐ 关键修复点 A（替代“硬拦截”）
   * 在登录/注册页被调用时，不丢弃，而是挂起等待路由切走后再启动
   */
  if (isGuestPath(path)) {
    pendingToken = token
    ensureRouteHook()
    return
  }

  /**
   * ⭐ 关键修复点 1
   * token 未变化且 ws 存在 → 不重复建立
   */
  if (ws && currentToken === token) {
    return
  }

  /**
   * ⭐ 关键修复点 2
   * token 变化 / 旧 ws 残留 → 强制清理
   */
  stopAccountStatusWS()

  currentToken = token

  /**
   * ⭐ 防抖：避免刚切页时反复建连（可保留）
   */
  if (pendingTimer) {
    clearTimeout(pendingTimer)
    pendingTimer = null
  }

  pendingTimer = setTimeout(() => {
    pendingTimer = null

    // 再次确认：如果又回到登录/注册页，就不启动，继续挂起
    const curPath = router.currentRoute.value.path
    if (isGuestPath(curPath)) {
      pendingToken = token
      ensureRouteHook()
      return
    }

    const accountStatusStore = useAccountStatusStore()

    const wsBaseUrl = getWsBaseUrl()
    const url = `${wsBaseUrl}/ws/account-status?token=${token}`

    const localWs = new WebSocket(url)
    ws = localWs

    localWs.onmessage = (event) => {
      // 防止旧 ws 回调污染新会话
      if (localWs !== ws) return

      try {
        const data = JSON.parse(event.data)
        if (data.type === 'account_status') {
          // ⭐ WS 只同步事实，不做退出裁决
          accountStatusStore.setStatus(data.account_status)
        }
      } catch (e) {
        // 非法消息忽略
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

  // ⭐ 停止时也清掉挂起 token，避免退出后又被 afterEach 拉起
  pendingToken = null

  if (ws) {
    ws.close()
    ws = null
    currentToken = null
  }
}

/**
 * =========================
 * 明确的“会话级退出”
 * =========================
 */
export function forceLogout() {
  const authStore = useAuthStore()
  const accountStatusStore = useAccountStatusStore()

  // 1️⃣ 清理鉴权
  authStore.logout()

  // 2️⃣ 清理账号态
  accountStatusStore.reset()

  // 3️⃣ 关闭 WS（也会清 pendingToken）
  stopAccountStatusWS()

  // 4️⃣ 跳转登录页
  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }
}
