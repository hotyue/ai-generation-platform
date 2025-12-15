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
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  height: 56px;
  background: #111827;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
}

.title {
  font-weight: bold;
}

.exit {
  background: #374151;
  color: #fff;
  border: none;
  padding: 6px 10px;
  cursor: pointer;
}

.admin-content {
  flex: 1;
  background: #f9fafb;
}
</style>
