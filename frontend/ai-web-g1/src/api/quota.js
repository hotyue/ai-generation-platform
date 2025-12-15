// src/api/quota.js
import http from '@/utils/http'

export function fetchQuotaLogs(params) {
  return http.get('/quota/logs', { params })
}
