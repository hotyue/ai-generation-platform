/**
 * WS 消息路由层
 * - 不关心 WebSocket 生命周期
 * - 不关心业务含义
 * - 只负责：按消息形态分发
 */

/**
 * event-based handlers
 * key: event_type
 * value: handler(payload, rawMsg)
 */
const eventHandlers = new Map()

/**
 * state-based handlers
 * matcher: (msg) => boolean
 * handler: (msg) => void
 */
const stateHandlers = []

export function registerEventHandler(eventType, handler) {
  if (typeof eventType !== 'string' || typeof handler !== 'function') {
    return
  }
  eventHandlers.set(eventType, handler)
}

export function registerStateHandler(matcher, handler) {
  if (typeof matcher !== 'function' || typeof handler !== 'function') {
    return
  }
  stateHandlers.push({ matcher, handler })
}

/**
 * WS 消息统一入口
 * @param {any} msg - 已 JSON.parse 的消息
 * @returns {boolean} 是否被处理
 */
export function routeWsMessage(msg) {
  if (!msg || typeof msg !== 'object') {
    return false
  }

  /**
   * 1️⃣ event-based（显式 event_type）
   */
  if (typeof msg.event_type === 'string') {
    const handler = eventHandlers.get(msg.event_type)
    if (handler) {
      handler(msg.payload, msg)
      return true
    }
    return false
  }

  /**
   * 2️⃣ state-based（无 event_type）
   */
  for (const { matcher, handler } of stateHandlers) {
    try {
      if (matcher(msg)) {
        handler(msg)
        return true
      }
    } catch {
      // 单个 handler 出错不得影响其他
    }
  }

  return false
}
