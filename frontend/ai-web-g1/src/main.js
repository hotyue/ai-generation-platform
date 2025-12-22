import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

import App from './App.vue'
import './style.css'

// ⭐ Auth Store
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)

// 1️⃣ Pinia 必须最先初始化
const pinia = createPinia()
app.use(pinia)

// 2️⃣ 先拿到 authStore（此时 Pinia 已就绪）
const authStore = useAuthStore(pinia)

// 3️⃣ 启动引导流程
const bootstrap = async () => {
  /**
   * ⭐ 核心原则：
   * - 有 token → 必须先 fetchMe()
   * - fetchMe 失败 → 立即清空 token
   * - 用户态确定之后，再挂 router / mount
   */

  if (authStore.token) {
    try {
      await authStore.fetchMe()
    } catch (err) {
      console.warn('bootstrap: fetchMe failed, clear token', err)
      authStore.clearToken()
    }
  }

  // 4️⃣ 用户态确定后，再启用路由
  app.use(router)

  // 5️⃣ 最后再 mount
  app.mount('#app')
}

// 🚀 启动
bootstrap()
