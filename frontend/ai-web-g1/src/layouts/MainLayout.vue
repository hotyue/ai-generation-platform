<template>
  <div class="layout">
    <!-- 顶部导航 -->
    <header class="navbar">
      <div class="logo">AI Web</div>

      <nav class="nav">
        <router-link
          to="/generate"
          class="nav-item"
          :class="{ active: isActive('/generate') }"
        >
          生成
        </router-link>

        <router-link
          to="/history"
          class="nav-item"
          :class="{ active: isActive('/history') }"
        >
          历史
        </router-link>

        <router-link
          to="/plans"
          class="nav-item"
          :class="{ active: isActive('/plans') }"
        >
          套餐
        </router-link>

        <router-link
          to="/profile"
          class="nav-item"
          :class="{ active: isActive('/profile') }"
        >
          账户
        </router-link>

        <router-link
          to="/quota"
          class="nav-item"
          :class="{ active: isActive('/quota') }"
        >
          额度
        </router-link>
      </nav>

      <div class="right">
        <span class="quota">
          剩余：{{ quota ?? '--' }}
        </span>

        <button class="logout" @click="logout">
          退出
        </button>
      </div>
    </header>

    <!-- 页面内容 -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import http from '@/utils/http'   // ✅ 正确：统一使用 http

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

/**
 * =========================
 * 导航高亮
 * =========================
 */
const isActive = (path) => {
  return route.path.startsWith(path)
}

/**
 * =========================
 * quota（来自 Pinia）
 * =========================
 */
const quota = computed(() => authStore.quota)

/**
 * =========================
 * 初始化拉取用户信息（关键）
 * =========================
 */
const fetchMe = async () => {
  // 已登录但还没有用户信息
  if (!authStore.token || authStore.user) return

  try {
    const user = await http.get('/auth/me')
    authStore.setUser(user)
  } catch (e) {
    console.error('获取用户信息失败', e)

    // token 失效，强制登出
    authStore.clearToken()
    router.replace('/login')
  }
}

onMounted(fetchMe)

/**
 * =========================
 * 退出登录
 * =========================
 */
const logout = () => {
  authStore.clearToken()
  router.push('/login')
}
</script>

<style scoped>
/* —— 样式保持不变 —— */
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #1f2937;
  color: #fff;
}

.logo {
  font-size: 18px;
  font-weight: bold;
}

.nav {
  display: flex;
  gap: 12px;
}

.nav-item {
  color: #cbd5e1;
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 4px;
}

.nav-item.active {
  background: #374151;
  color: #fff;
}

.right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quota {
  font-size: 14px;
}

.logout {
  background: #ef4444;
  color: #fff;
  border: none;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.content {
  flex: 1;
  padding: 16px;
}
</style>
