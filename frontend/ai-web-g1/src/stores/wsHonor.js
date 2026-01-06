/**
 * WS event-handler：HONOR_LEVEL_UP
 * - 荣誉等级实时更新
 * - 冗余余额同步
 * - 全局一次性祝贺事件
 */

import { useHonorStore } from '@/stores/honor'
import { useAuthStore } from '@/stores/auth'

export function handleHonorLevelUp(payload) {
  if (!payload || typeof payload !== 'object') return

  const honorStore = useHonorStore()
  const authStore = useAuthStore()

  /**
   * 1️⃣ 荣誉等级更新
   */
  const after = payload.after
  if (after && typeof after === 'object') {
    honorStore.setHonor({
      star: Number(after.star ?? 0),
      moon: Number(after.moon ?? 0),
      sun: Number(after.sun ?? 0),
      diamond: Number(after.diamond ?? 0),
      crown: Number(after.crown ?? 0),
      total_success_tasks: Number(
        payload.after_total_success_tasks ?? 0
      ),
    })
  }

  /**
   * 2️⃣ 冗余余额同步（等价 USER_QUOTA_UPDATED）
   */
  const balance = payload.balance
  if (typeof balance === 'number') {
    authStore.setQuota(balance)
  }

  /**
   * 3️⃣ 全局一次性祝贺事件
   * - 不进 store
   * - 不持久
   */
  try {
    window.dispatchEvent(
      new CustomEvent('HONOR_LEVEL_UP', {
        detail: payload,
      })
    )
  } catch {
    // 非浏览器环境或异常时忽略
  }
}
