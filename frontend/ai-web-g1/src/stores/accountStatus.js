import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/auth'

export const useAccountStatusStore = defineStore('accountStatus', {
  state: () => ({
    // unknown | normal | restricted | banned
    status: 'unknown',
    initialized: false, // ⭐ 是否已完成一次事实注入
  }),

  actions: {
    /**
     * =========================
     * WS / 外部统一入口
     * =========================
     */
    setStatus(status) {
      this.status = status
      this.initialized = true
    },

    /**
     * =========================
     * v1.0.11 新增：
     * 登录完成后的一次性初始化
     * =========================
     *
     * 事实来源：authStore.user.account_status
     * 只执行一次
     */
    initFromAuth() {
      if (this.initialized) return

      const authStore = useAuthStore()
      if (authStore.user && authStore.user.account_status) {
        this.status = authStore.user.account_status
        this.initialized = true
      }
    },

    /**
     * =========================
     * 退出 / 切换账号
     * =========================
     */
    reset() {
      this.status = 'unknown'
      this.initialized = false
    },
  },
})
