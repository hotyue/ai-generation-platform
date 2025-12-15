// src/api/plan.js
import http from '@/utils/http'

export function fetchPlans() {
  return http.get('/plans')
}
