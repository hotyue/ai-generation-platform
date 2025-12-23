<template>
  <div class="layout">
    <!-- =========================
         顶部导航
    ========================= -->
    <header class="navbar">
      <div class="logo">AI Web</div>

      <!-- =========================
           主导航（受 account_status 影响）
      ========================= -->
      <nav class="nav">
        <!-- 🚫 restricted / banned 不显示生成 -->
        <router-link
          v-if="canAccessGenerate"
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
          to="/quota"
          class="nav-item"
          :class="{ active: isActive('/quota') }"
        >
          额度
        </router-link>

        <router-link
          to="/profile"
          class="nav-item"
          :class="{ active: isActive('/profile') }"
        >
          账户
        </router-link>
      </nav>

      <!-- =========================
           右侧状态区
      ========================= -->
      <div class="right">
        <span
          v-if="authStore.token"
          class="status-pill"
          :class="statusClass"
          :title="statusTitle"
        >
          {{ statusText }}
        </span>

        <span class="quota">
          剩余：{{ quota ?? '--' }}
        </span>

        <button class="logout" @click="logout">
          退出
        </button>
      </div>
    </header>

    <!-- =========================
         全局账号状态提示条
    ========================= -->
    <div
      v-if="authStore.token && accountStatus !== 'normal'"
      class="top-banner"
      :class="statusClass"
    >
      <span v-if="accountStatus === 'restricted'">
        当前账号为受限状态：生成等部分功能不可用。
      </span>
      <span v-else-if="accountStatus === 'banned'">
        当前账号已封禁，请联系管理员处理。
      </span>
    </div>

    <!-- =========================
         页面内容
    ========================= -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAccountStatusStore } from '@/stores/accountStatus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const accountStatusStore = useAccountStatusStore()

/**
 * =========================
 * 导航高亮
 * =========================
 */
const isActive = (path) => route.path.startsWith(path)

/**
 * =========================
 * quota
 * =========================
 */
const quota = computed(() => authStore.quota)

/**
 * =========================
 * account_status（v1.0.11 唯一事实源）
 * =========================
 */
const accountStatus = computed(() => {
  return accountStatusStore.status
})

/**
 * =========================
 * 生成权限（展示级）
 * =========================
 */
const canAccessGenerate = computed(() => {
  return accountStatus.value === 'normal'
})

/**
 * =========================
 * 状态展示
 * =========================
 */
const statusText = computed(() => {
  if (accountStatus.value === 'restricted') return '受限'
  if (accountStatus.value === 'banned') return '封禁'
  return '正常'
})

const statusTitle = computed(() => {
  if (accountStatus.value === 'restricted') return '账号受限：部分功能不可用'
  if (accountStatus.value === 'banned') return '账号封禁：禁止使用'
  return '账号正常'
})

const statusClass = computed(() => {
  if (accountStatus.value === 'restricted') return 'restricted'
  if (accountStatus.value === 'banned') return 'banned'
  return 'normal'
})

/**
 * =========================
 * 退出登录（显式行为）
 * =========================
 */
const logout = () => {
  authStore.clearToken()
  accountStatusStore.reset()
  router.push('/login')
}
</script>

<style scoped>
/* 保留你原有样式，未做破坏性修改 */

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

/* ===== 账号状态展示 ===== */
.status-pill {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.status-pill.normal {
  background: rgba(34, 197, 94, 0.18);
}

.status-pill.restricted {
  background: rgba(245, 158, 11, 0.18);
}

.status-pill.banned {
  background: rgba(239, 68, 68, 0.20);
}

.top-banner {
  padding: 10px 16px;
  font-size: 13px;
  border-bottom: 1px solid #eee;
}

.top-banner.restricted {
  background: #fff7ed;
  color: #9a3412;
}

.top-banner.banned {
  background: #fef2f2;
  color: #991b1b;
}
</style>
