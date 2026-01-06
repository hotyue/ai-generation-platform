import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

import App from './App.vue'
import './style.css'
import './assets/styles/theme.css' // ⭐ v1.0.14：全局主题语义层入口

// ⭐ Auth Store
import { useAuthStore } from '@/stores/auth'

// ⭐ Account Status WS（WS 会话层）
import { startAccountStatusWS } from '@/utils/ws'

// ⭐ WS 路由层注册
import {
  registerStateHandler,
  registerEventHandler,
} from '@/utils/ws_router'

// ⭐ 系统裁决状态（X / Y / Z）
import {
  isWsDecisionMessage,
  handleWsDecisionMessage,
} from '@/stores/systemDecision'

// ⭐ account_status WS handler（v1.0.11 起唯一事实源）
import { handleAccountStatusUpdated } from '@/stores/wsAccountStatus'

import { handleUserQuotaUpdated } from '@/stores/wsQuota'
import { handleHonorLevelUp } from '@/stores/wsHonor'


/**
 * =========================
 * ⭐ v1.0.14：主题语义锚点
 * =========================
 *
 * 执行级事实：
 * - 非主题切换
 * - 非业务逻辑
 * - 仅用于建立全站统一主题语义入口
 */
document.documentElement.setAttribute('data-theme', 'system')

/**
 * =========================
 * ⭐ WS 系统级能力注册（必须最早）
 * =========================
 *
 * 设计裁决：
 * - main.js 只做“注册”，不做处理
 * - 注册即全局生效
 * - 与页面 / store 解耦
 */

// 1️⃣ 系统裁决状态（state-based）
registerStateHandler(isWsDecisionMessage, handleWsDecisionMessage)

// 2️⃣ account_status（event-based · WS 唯一事实源）
registerEventHandler(
  'ACCOUNT_STATUS_UPDATED',
  handleAccountStatusUpdated
)

// quota
registerEventHandler(
  'USER_QUOTA_UPDATED',
  handleUserQuotaUpdated
)

// honor
registerEventHandler(
  'HONOR_LEVEL_UP',
  handleHonorLevelUp
)

const app = createApp(App)

/**
 * =========================
 * 1️⃣ 初始化 Pinia（必须最先）
 * =========================
 */
const pinia = createPinia()
app.use(pinia)

/**
 * =========================
 * 2️⃣ 获取 authStore（Pinia 已就绪）
 * =========================
 */
const authStore = useAuthStore(pinia)

/**
 * =========================
 * 3️⃣ 启动引导流程（bootstrap）
 * =========================
 *
 * 设计原则（保持不变）：
 * - App 必须能在「被封禁态 / 未登录态」下正常启动
 * - main.js 不负责账号裁决
 * - main.js 永远不阻断 mount
 */
const bootstrap = async () => {
  /**
   * ⭐ 若存在 token：
   * - 尝试 fetchMe
   * - 失败 → 清 token → 继续启动
   */
  if (authStore.token) {
    try {
      await authStore.fetchMe()
    } catch (err) {
      console.warn('[bootstrap] fetchMe failed, clear token', err)
      authStore.clearToken()
    }
  }

  /**
   * =========================
   * ⭐ v1.0.11：启动 WS 会话
   * =========================
   *
   * 裁决保持不变：
   * - 只在 token 存在时启动
   * - WS 失败不影响启动
   */
  if (authStore.token) {
    try {
      startAccountStatusWS(authStore.token)
    } catch (err) {
      console.warn('[bootstrap] startAccountStatusWS failed', err)
    }
  }

  /**
   * =========================
   * 4️⃣ 用户态“稳定”后再启用 router
   * =========================
   */
  app.use(router)

  /**
   * =========================
   * 5️⃣ 挂载应用（永远执行）
   * =========================
   */
  app.mount('#app')
}

/**
 * =========================
 * 🚀 启动
 * =========================
 */
bootstrap()
