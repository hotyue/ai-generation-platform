import { defineStore } from 'pinia'
import http from '@/utils/http'
import {
  setToken as persistToken,
  getToken,
  clearToken as clearPersistToken
} from '@/utils/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken() || null,
    user: null,
    quota: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    // =========================
    // Token 管理
    // =========================
    setToken(token) {
      this.token = token
      persistToken(token)
    },

    clearToken() {
      this.token = null
      this.user = null
      this.quota = null
      clearPersistToken()
    },

    // =========================
    // 用户数据
    // =========================
    setUser(user) {
      this.user = user
      this.quota = user?.quota ?? null
    },

    setQuota(quota) {
      this.quota = quota
    },

    // ⭐ =========================
    // ⭐ User State Event（v1）
    // ⭐ =========================
    applyUserEvent(event) {
      if (!event || !event.event_type) return

      switch (event.event_type) {
        case 'USER_QUOTA_UPDATED':
          // 权威覆盖，不做计算
          if (typeof event.payload?.balance === 'number') {
            this.quota = event.payload.balance
          }
          break

        // v1 只处理 quota，其他事件后续再扩展
        default:
          break
      }
    },

    // =========================
    // 获取当前用户
    // =========================
    async fetchMe() {
      if (!this.token) return

      const user = await http.get('/auth/me')
      this.setUser(user)
    },
  },
})
