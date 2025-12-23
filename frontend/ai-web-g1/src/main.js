import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

import App from './App.vue'
import './style.css'

// ⭐ Auth Store
import { useAuthStore } from '@/stores/auth'

// ⭐ Account Status WS
import { startAccountStatusWS } from '@/utils/ws'

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
 * 设计原则（非常重要）：
 *
 * - ❗ App 必须能在「被封禁态」下正常启动
 * - ❗ main.js 不负责裁决账号权限
 * - ❗ main.js 只负责：
 *     - 尝试恢复登录态
 *     - 失败就清 token
 *     - 永远不阻断 mount
 *
 * ❌ main.js 里禁止：
 *   - alert
 *   - router.replace
 *   - 强制退出逻辑
 */
const bootstrap = async () => {
  /**
   * ⭐ 若存在 token：
   * - 尝试 fetchMe
   * - fetchMe 失败（401 / 403 / 网络异常）
   *   → 清 token
   *   → 不抛异常
   *   → 继续启动
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
   * ⭐ v1.0.11：启动账号状态 WS
   * =========================
   *
   * 设计裁决：
   * - 只在“用户态已稳定”后启动
   * - 不关心 account_status
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
   * 4️⃣ 用户态已“稳定”，再启用 router
   * =========================
   *
   * ⚠️ 顺序非常重要：
   * - router.beforeEach 里通常依赖 authStore
   * - 必须等 fetchMe 结束
   */
  app.use(router)

  /**
   * =========================
   * 5️⃣ 挂载应用（永远要执行）
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
