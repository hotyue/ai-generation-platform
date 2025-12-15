<template>
  <div class="auth-container">
    <h2>注册账号</h2>

    <form @submit.prevent="handleRegister">
      <div class="form-item">
        <label>用户名</label>
        <input
          v-model="form.username"
          type="text"
          placeholder="请输入用户名"
          required
        />
      </div>

      <div class="form-item">
        <label>密码</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          required
        />
      </div>

      <div class="form-item">
        <label>确认密码</label>
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          required
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>

    <p class="link">
      已有账号？
      <router-link to="/login">去登录</router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api'

const router = useRouter()
const loading = ref(false)
const confirmPassword = ref('')

const form = reactive({
  username: '',
  password: ''
})

const handleRegister = async () => {
  if (form.password !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }

  try {
    loading.value = true
    await register({
      username: form.username,
      password: form.password
    })

    alert('注册成功，请登录')
    router.push('/login')
  } catch {
    // ❗错误提示已在 http.js 中统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 360px;
  margin: 100px auto;
}

.form-item {
  margin-bottom: 16px;
}

input {
  width: 100%;
  padding: 8px;
}

button {
  width: 100%;
  padding: 10px;
}

.link {
  margin-top: 12px;
  text-align: center;
}
</style>
