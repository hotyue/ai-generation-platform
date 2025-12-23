// src/api/admin.js
import http from '@/utils/http'

export function fetchAdminPlans() {
  return http.get('/admin/plans')
}

export function createAdminPlan(data) {
  return http.post('/admin/plans', data)
}

// 新增：管理员修改套餐
export function updateAdminPlan(id, data) {
  return http.put(`/admin/plans/${id}`, data)
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

// ================================
// account_status 管理（v1.0.15）
// ================================

export function restrictUser(userId) {
  return http.post(`/admin/users/${userId}/restrict`)
}

export function unrestrictUser(userId) {
  return http.post(`/admin/users/${userId}/unrestrict`)
}

export function banUser(userId) {
  return http.post(`/admin/users/${userId}/ban`)
}

export function unbanUser(userId) {
  return http.post(`/admin/users/${userId}/unban`)
}
