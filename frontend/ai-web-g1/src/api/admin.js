// src/api/admin.js
import http from '@/utils/http'

export function fetchAdminPlans() {
  return http.get('/admin/plans')
}

export function createAdminPlan(data) {
  return http.post('/admin/plans', data)
}

export function disableAdminPlan(id) {
  return http.post(`/admin/plans/${id}/disable`)
}

export function enableAdminPlan(id) {
  return http.post(`/admin/plans/${id}/enable`)
}

export function fetchAdminUsers() {
  return http.get('/admin/users')
}

export function grantUserQuota(userId, quota) {
  return http.post(
    `/admin/users/${userId}/grant`,
    { quota }
  )
}

export function applyUserPlan(userId, planId) {
  return http.post(
    `/admin/users/${userId}/apply-plan/${planId}`
  )
}
