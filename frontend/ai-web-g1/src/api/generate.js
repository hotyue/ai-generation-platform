// src/api/generate.js
import http from '@/utils/http'

// 提交生成任务
export function createGenerateTask(prompt) {
  return http.post('/generate', { prompt })
}
