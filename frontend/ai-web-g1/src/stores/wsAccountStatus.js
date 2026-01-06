/**
 * WS event-handler：ACCOUNT_STATUS_UPDATED
 * - v1.0.11 起的唯一事实源
 * - 仅做状态覆盖，不做任何裁决
 */

import { useAccountStatusStore } from '@/stores/accountStatus'

export function handleAccountStatusUpdated(payload) {
  const status = payload?.account_status
  if (typeof status !== 'string') return

  const accountStatusStore = useAccountStatusStore()
  accountStatusStore.setStatus(status)
}
