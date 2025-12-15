import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Generate from '../views/Generate.vue'
import History from '../views/History.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Plans from '../views/Plans.vue'
import QuotaLog from '../views/QuotaLog.vue'

import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminHome from '@/views/admin/AdminHome.vue'

import { useAuthStore } from '@/stores/auth'

const routes = [
  // =========================
  // 登录页（未登录可访问）
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
    meta: { guest: true }
  },

  // =========================
  // 用户端（登录后，MainLayout）
  // =========================
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/generate',
      },
      {
        path: 'generate',
        name: 'Generate',
        component: Generate,
      },
      {
        path: 'history',
        name: 'History',
        component: History,
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
      },
      {
        path: 'plans',
        name: 'Plans',
        component: Plans,
      },
      {
        path: 'quota',
        name: 'Quota',
        component: QuotaLog,
      },
    ],
  },

  // =========================
  // Admin 后台（G6-1）
  // =========================
  {
    path: '/admin',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      requiresAdmin: true, // ⭐ 关键标识
    },
    children: [
      {
        path: '',
        name: 'AdminHome',
        component: AdminHome,
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/AdminUsers.vue'),
        meta: { requiresAdmin: true },
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
 * 全局路由守卫（含 Admin 权限）
 * =========================
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const isLoggedIn = authStore.isLoggedIn

  // 1️⃣ 未登录 → 访问需要登录的页面
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  // 2️⃣ 已登录 → 再访问登录页
  if (to.meta.guestOnly && isLoggedIn) {
    next('/generate')
    return
  }

  // 3️⃣ Admin 权限校验（关键修复点）
  if (to.meta.requiresAdmin) {
    try {
      // ⭐ 如果 user 还没加载，先拉一次
      if (!authStore.user) {
        await authStore.fetchMe()
      }

      if (!authStore.user || authStore.user.role !== 'admin') {
        next('/generate')
        return
      }
    } catch (e) {
      next('/generate')
      return
    }
  }

  next()
})

export default router
