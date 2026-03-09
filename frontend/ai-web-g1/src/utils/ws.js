import router from '@/router'
import { routeWsMessage } from '@/utils/ws_router'

/**
 * =========================
 * WebSocket 会话生命周期状态
 * =========================
 */
let ws = null
let currentToken = null
let pendingTimer = null

// 登录页挂起机制：防止在未经身份验证的路由建立连接
let pendingToken = null
let hasRouteHook = false

/**
 * =========================
 * ⭐ 核心修缮：动态协议与地址推导引擎 (Docker 通用镜像适配)
 * =========================
 * 过去：高度依赖构建期硬编码的 VITE_API_BASE_URL，缺失直接 throw Error 导致白屏。
 * 现在：引入“三级降级与动态感知”策略。
 * 1. 优先读取 docker-entrypoint 注入的 window.__ENV__.API_BASE_URL
 * 2. 自动根据 API 地址的协议 (http/https) 智能推导 WS 协议 (ws/wss)
 * 3. 剥离多余的路径（如 /api），精准提取主机名 (host) 以匹配后端的 /ws 挂载点
 */
function getWsBaseUrl() {
  const apiBaseUrl = window.__ENV__?.API_BASE_URL || 
                     import.meta.env.VITE_API_BASE_URL || 
                     window.location.origin;

  try {
    // 鲁棒性解析：即使传入的是 '/api' 这样的相对路径，也能结合当前域名算出绝对地址
    const url = new URL(apiBaseUrl, window.location.origin);
    // 自动适配协议：安全环境使用 wss，普通环境使用 ws
    const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    // 仅返回协议和主机部分，与后端的 ws 挂载点保持一致
    return `${wsProtocol}//${url.host}`;
  } catch (e) {
    // 极限异常兜底：若 URL 解析彻底失败，基于当前浏览器访问的协议和域名直接硬推导
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}`;
  }
}

/**
 * =========================
 * 访客路径识别 (导出以解决作用域闭包问题)
 * =========================
 */
export function isGuestPath(path) {
  return path === '/login' || path === '/register'
}

/**
 * =========================
 * 路由守卫：延迟建立连接
 * =========================
 * 确保用户在离开登录/注册页、正式进入应用主体后再发起 WS 握手
 */
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
 * 启动 WebSocket 核心引擎
 * =========================
 * 负责建立底层长连接，并将收到的业务数据转交给 WS Router 路由分发
 */
export function startAccountStatusWS(token) {
  if (!token) return

  const path = router.currentRoute.value.path

  // 1. 登录 / 注册页 → 挂起连接行为，等待离开这些页面后再启动
  if (isGuestPath(path)) {
    pendingToken = token
    ensureRouteHook()
    return
  }

  // 2. 幂等性检查：如果 token 未变化且长连接存活，则不重复浪费资源建立握手
  if (ws && currentToken === token) {
    return
  }

  // 3. 上下文切换清理：账号变更或存在僵尸连接时，强制回收旧连接
  stopAccountStatusWS()
  currentToken = token

  // 4. 抖动防护：避免前端路由频繁切页导致的瞬间大批量 WS 握手轰炸服务器
  if (pendingTimer) {
    clearTimeout(pendingTimer)
    pendingTimer = null
  }

  pendingTimer = setTimeout(() => {
    pendingTimer = null

    // 二次确认：防抖结束后，确保当前用户仍不在访客页面
    const curPath = router.currentRoute.value.path
    if (isGuestPath(curPath)) {
      pendingToken = token
      ensureRouteHook()
      return
    }

    // ⭐ 使用重构后的动态地址引擎获取准确的 WS 地址
    const wsBaseUrl = getWsBaseUrl()
    const url = `${wsBaseUrl}/ws?token=${token}`

    const localWs = new WebSocket(url)
    ws = localWs

    /**
     * =========================
     * WebSocket 消息入口总线
     * =========================
     * 网络层只做连接维护，收到数据后剥离底层外壳，直接投递给 ws_router 业务层处理
     */
    localWs.onmessage = (event) => {
      // 竞态条件防护：防止快速切换账号时，旧连接的残留消息污染新账号的状态池
      if (localWs !== ws) return

      try {
        const msg = JSON.parse(event.data)
        routeWsMessage(msg)
      } catch {
        // 非法或无法解析的消息直接丢弃，保证前端不因此崩溃
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
 * 停止 WebSocket (资源回收)
 * =========================
 * 退出账号或强行切换环境时调用，确保释放网络连接和闭包定时器
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
 * 统一强制退出出口
 * =========================
 */
export function forceLogout() {
  stopAccountStatusWS()

  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }
}