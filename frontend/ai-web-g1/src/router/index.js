import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAccountStatusStore } from '@/stores/accountStatus'

import Login from '../views/Login.vue'
import Generate from '../views/Generate.vue'
import History from '../views/History.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Plans from '../views/Plans.vue'
import QuotaLog from '../views/QuotaLog.vue'

import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminHome from '@/views/admin/AdminHome.vue'

const routes = [
  // =========================
  // 登录 / 注册（未登录）
  // =========================
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    component: () => import('@/views/Register.vue'),
    meta: { guestOnly: true },
  },

  // =========================
  // 用户端（登录后）
  // =========================
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/generate' },
      { path: 'generate', name: 'Generate', component: Generate },
      { path: 'history', name: 'History', component: History },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
      },
      { path: 'plans', name: 'Plans', component: Plans },
      { path: 'quota', name: 'Quota', component: QuotaLog },
    ],
  },

  // =========================
  // Admin 后台
  // =========================
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
    children: [
      { path: '', name: 'AdminHome', component: AdminHome },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/AdminUsers.vue'),
      },
      {
        path: 'plans',
        name: 'AdminPlans',
        component: () => import('@/views/admin/AdminPlans.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * =========================
 * 全局路由守卫（v1.0.11 · 最终裁决版）
 * =========================
 *
 * 裁决分层原则（已冻结）：
 *
 * - authStore：会话状态（token / user）
 * - accountStatusStore：账号状态事实（WS）
 * - router：最终裁决者（允许终结会话）
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const accountStatusStore = useAccountStatusStore()

  const isLoggedIn = authStore.isLoggedIn

  // =========================
  // 1️⃣ 未登录 → 访问受保护页面
  // =========================
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  // =========================
  // 2️⃣ 已登录 → 访问登录 / 注册
  // =========================
  if (to.meta.guestOnly && isLoggedIn) {
    next('/generate')
    return
  }

  // =========================
  // 3️⃣ Admin 权限裁决（保持原逻辑）
  // =========================
  if (to.meta.requiresAdmin) {
    try {
      if (!authStore.user) {
        await authStore.fetchMe()
      }

      if (!authStore.user || authStore.user.role !== 'admin') {
        next('/generate')
        return
      }
    } catch {
      authStore.clearToken()
      next('/login')
      return
    }
  }

  // =========================
  // 4️⃣ account_status 强裁决（v1.0.11 核心）
  // =========================
  /**
   * 设计结论（已确认）：
   *
   * - banned 是“会话级终止状态”
   * - 一旦进入 banned
   * - 任意路由行为 == 用户继续使用意图
   * - 必须立即、不可逆地终结会话
   */
  if (isLoggedIn && accountStatusStore.status === 'banned') {
    // ⭐ 核心修复点：先终结会话
    authStore.clearToken()

    // 再跳转登录页（避免 SPA 半死亡态）
    if (to.path !== '/login') {
      next('/login')
      return
    }
  }

  next()
})

export default router
