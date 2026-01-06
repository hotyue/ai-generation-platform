/**
 * 系统级裁决状态（X / Y / Z）
 * - 来源：WS state-based 消息
 * - 语义：系统事实快照
 * - 不参与任何计算
 */

const STORAGE_KEY = 'ws_decision_xyz'

/**
 * 判断是否为 WS 裁决消息
 */
export function isWsDecisionMessage(msg) {
  return (
    msg &&
    typeof msg === 'object' &&
    typeof msg.X === 'number' &&
    typeof msg.Y === 'number' &&
    typeof msg.Z === 'number'
  )
}

/**
 * 处理 WS 裁决消息
 * - 覆盖式写入
 */
export function handleWsDecisionMessage(msg) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(msg))

    // ⭐ 同 tab 实时通知（系统级事实变更）
    window.dispatchEvent(
      new CustomEvent('WS_DECISION_UPDATED', {
        detail: msg,
      })
    )
  } catch {
    // localStorage 不可用时忽略
  }
}

/**
 * 读取最近一次裁决（给页面 / 组件用）
 */
export function getCachedWsDecision() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}
