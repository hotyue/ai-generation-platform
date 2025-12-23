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
  } catch (err: any) {
    // v1.0.13：显式展示后端返回的注册错误信息
    const msg =
      err?.response?.data?.detail || '注册失败，请重试'
    alert(msg)
    throw err
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* =========================
 * 页面容器
 * ========================= */

.auth-container {
  max-width: 360px;
  margin: 100px auto;
  padding: 24px;

  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: 8px;

  color: var(--text-primary);
}

/* =========================
 * 表单项
 * ========================= */

.form-item {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* =========================
 * 输入框
 * ========================= */

input {
  width: 100%;
  padding: 8px;

  background: var(--bg-card);
  color: var(--text-primary);

  border: 1px solid var(--border-base);
  border-radius: 4px;
}

input::placeholder {
  color: var(--text-muted);
}

input:focus {
  outline: none;
  border-color: var(--state-success);
}

/* =========================
 * 按钮
 * ========================= */

button {
  width: 100%;
  padding: 10px;

  border-radius: 6px;
  border: 1px solid var(--border-base);

  background: var(--bg-card);
  color: var(--text-primary);

  font-size: 15px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* =========================
 * 底部链接
 * ========================= */

.link {
  margin-top: 12px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.link a {
  color: var(--state-success);
  text-decoration: none;
}

.link a:hover {
  text-decoration: underline;
}
</style>
