// src/api/history.js
import http from '@/utils/http'

/**
 * 获取生成历史
 * @param {Object} params
 * @param {number} params.limit
 * @param {number} params.offset
 */
export function fetchHistory(params = { limit: 20, offset: 0 }) {
  return http.get('/history', {
    params,
  })
}
