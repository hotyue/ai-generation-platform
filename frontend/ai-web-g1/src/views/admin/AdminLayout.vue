<template>
  <div class="admin-layout">
    <!-- 顶部 -->
    <header class="admin-header">
      <div class="title">Admin Console</div>
      <button class="exit" @click="goBack">
        返回用户端
      </button>
    </header>

    <!-- 内容区 -->
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/generate')
}
</script>

<style scoped>
/* =========================
 * 后台整体布局
 * ========================= */

.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  color: var(--text-primary);
}

/* =========================
 * 顶部 Header
 * ========================= */

.admin-header {
  height: 56px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;

  background: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
  color: var(--text-primary);
}

.title {
  font-weight: bold;
}

/* =========================
 * 返回按钮
 * ========================= */

.exit {
  padding: 6px 10px;
  cursor: pointer;

  background: var(--bg-card);
  color: var(--text-primary);

  border: 1px solid var(--border-base);
  border-radius: 4px;
}

.exit:hover {
  opacity: 0.85;
}

/* =========================
 * 内容区
 * ========================= */

.admin-content {
  flex: 1;
  padding: 16px;

  background: var(--bg-base);
  color: var(--text-primary);
}
</style>
