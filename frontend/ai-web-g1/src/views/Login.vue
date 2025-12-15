<template>
  <div class="login-page">
    <h1>登录</h1>

    <input
      v-model="username"
      placeholder="用户名"
      class="input"
    />

    <input
      v-model="password"
      type="password"
      placeholder="密码"
      class="input"
    />

    <!-- 注册 / 登录 按钮行 -->
    <div class="btn-row">
      <button class="btn btn-secondary" @click="goRegister">
        注册
      </button>

      <button class="btn btn-primary" @click="handleLogin">
        登录
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api'   // ✅ 关键改动

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  error.value = ''

  // 1️⃣ 基础校验
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  try {
    // 2️⃣ 使用统一 API（走 http.js + VITE_API_BASE）
    const res = await login({
      username: username.value,
      password: password.value,
    })

    const token = res.access_token
    if (!token) {
      throw new Error('未获取到 token')
    }

    // 3️⃣ 写入 Pinia + localStorage
    authStore.setToken(token)

    // 4️⃣ 跳转业务页
    router.push('/generate')

  } catch (e) {
    console.error('login error:', e)
    error.value = '登录失败，请检查用户名或密码'
  }
}

// 跳转注册页
const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.input {
  width: 240px;
  padding: 8px;
}

.btn-row {
  display: flex;
  gap: 12px;
}

.btn {
  width: 114px;
  padding: 8px;
  cursor: pointer;
}

.btn-secondary {
  background: #f5f5f5;
  border: 1px solid #ddd;
}

.error {
  color: red;
}
</style>
