import { defineStore } from 'pinia'
import http from '@/utils/http'
import {
  setToken as persistToken,
  getToken,
  clearToken as clearPersistToken
} from '@/utils/auth'

/**
 * ⭐ v1.0.11：WS 生命周期由 authStore 统一接管
 */
import {
  startAccountStatusWS,
  stopAccountStatusWS,
} from '@/utils/ws'

/**
 * ⭐ v1.0.30：荣誉状态派生 Store
 */
import { useHonorStore } from '@/stores/honor'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken() || null,

    /**
     * 用户完整对象（来自 /auth/me）
     * 必须包含：
     * - role
     * - quota
     * - account_status
     * - level_* / total_success_tasks
     */
    user: null,

    /**
     * quota 单独拆出来
     * 用于 Header / Generate 页高频读取
     */
    quota: null,

    /**
     * 是否已经拉取过 me
     */
    meLoaded: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,

    isAdmin: (state) => state.user?.role === 'admin',

    /**
     * ⭐ 账户状态（唯一权威出口）
     */
    accountStatus: (state) => {
      return state.user?.account_status || 'normal'
    },
  },

  actions: {
    // =========================
    // Token 管理
    // =========================
    setToken(token) {
      this.token = token
      persistToken(token)

      // 切换账号时，强制重新拉 me
      this.meLoaded = false

      /**
       * ⭐ v1.0.11
       * token 成立 = 会话建立
       * → 立刻启动 WS
       */
      try {
        startAccountStatusWS(token)
      } catch {
        // WS 启动失败不影响登录主流程
      }
    },

    clearToken() {
      /**
       * ⭐ v1.0.11
       * 会话终止 → 先停 WS
       */
      try {
        stopAccountStatusWS()
      } catch {
        // ignore
      }

      this.token = null
      this.user = null
      this.quota = null
      this.meLoaded = false
      clearPersistToken()
    },

    // =========================
    // 用户数据（唯一初始化入口）
    // =========================
    setUser(user) {
      this.user = user
      this.quota = user?.quota ?? null
      this.meLoaded = true

      /**
       * ⭐ v1.0.30
       * 初始化荣誉状态（派生状态）
       * 数据源：/auth/me
       */
      try {
        const honorStore = useHonorStore()

        honorStore.setHonor({
          star: user?.level_star ?? 0,
          moon: user?.level_moon ?? 0,
          sun: user?.level_sun ?? 0,
          diamond: user?.level_diamond ?? 0,
          crown: user?.level_crown ?? 0,
          total_success_tasks: user?.total_success_tasks ?? 0,
        })
      } catch {
        // honor store 未就绪时，不阻断登录流程
      }
    },

    setQuota(quota) {
      this.quota = quota
    },

    // =========================
    // User State Event（WS）
    // =========================
    applyUserEvent(event) {
      if (!event || !event.event_type) return

      switch (event.event_type) {
        case 'USER_QUOTA_UPDATED':
          if (typeof event.payload?.balance === 'number') {
            this.quota = event.payload.balance
          }
          break

        // 未来可扩展：
        // USER_STATUS_UPDATED
        default:
          break
      }
    },

    // =========================
    // 获取当前用户（/auth/me）
    // =========================
    async fetchMe(force = false) {
      if (!this.token) return

      // 已加载且不强制刷新 → 直接返回
      if (this.meLoaded && !force) return

      try {
        const user = await http.get('/auth/me')
        this.setUser(user)
      } catch (e) {
        const status = e?.response?.status

        // 401：token 无效 / 过期 → 直接清理
        if (status === 401) {
          this.clearToken()
        }

        // 403：账号被封禁 / 受限（合法状态）
        // ❗️不清 token，不清 user
        // 由页面根据 accountStatus 决定行为
        if (status === 403) {
          this.meLoaded = true
        }

        throw e
      }
    },
  },
})
