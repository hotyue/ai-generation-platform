/**
 * WS event-handler：USER_QUOTA_UPDATED
 * - 用户余额 / 配额的实时同步
 * - 不裁决、不跳转
 */

import { useAuthStore } from '@/stores/auth'

export function handleUserQuotaUpdated(payload) {
  const balance = payload?.balance
  if (typeof balance !== 'number') return

  const authStore = useAuthStore()
  authStore.setQuota(balance)
}
