<template>
  <div class="login-page">
    <h1>登录</h1>

    <input
      v-model="username"
      placeholder="用户名"
      class="input"
      :disabled="loading"
    />

    <input
      v-model="password"
      type="password"
      placeholder="密码"
      class="input"
      :disabled="loading"
    />

    <!-- 注册 / 登录 按钮行 -->
    <div class="btn-row">
      <button
        class="btn btn-secondary"
        @click="goRegister"
        :disabled="loading"
      >
        注册
      </button>

      <button
        class="btn btn-primary"
        @click="handleLogin"
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''

  // =========================
  // 1️⃣ 基础校验
  // =========================
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true

  try {
    // =========================
    // 2️⃣ 请求登录接口
    // =========================
    const res = await login({
      username: username.value,
      password: password.value,
    })

    const token = res?.access_token
    if (!token) {
      throw new Error('未获取到登录凭证')
    }

    // =========================
    // 3️⃣ 写入 token（Pinia + localStorage）
    // =========================
    authStore.setToken(token)

    // =========================
    // 4️⃣ 拉取用户信息（可选但推荐）
    // 确保 account_status / quota 就绪
    // =========================
    try {
      await authStore.fetchMe(true)
    } catch {
      // fetchMe 内部已做语义处理
    }

    // =========================
    // 5️⃣ 跳转业务页
    // =========================
    router.push('/generate')

  } catch (e) {
    // =========================
    // 6️⃣ 登录失败语义化处理（关键）
    // =========================
    const status = e?.response?.status
    const detail = e?.response?.data?.detail

    if (status === 403) {
      // 封禁账号（合法失败）
      error.value = detail || '账号已被封禁'
      return
    }

    if (status === 401) {
      // 用户名 / 密码错误
      error.value = detail || '用户名或密码错误'
      return
    }

    // 其他异常
    error.value = '登录失败，请稍后重试'

  } finally {
    loading.value = false
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

.btn-primary {
  background: #2563eb;
  color: #fff;
  border: none;
}

.btn-secondary {
  background: #f5f5f5;
  border: 1px solid #ddd;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 8px;
}
</style>
