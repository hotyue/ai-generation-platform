<template>
  <div class="generate-page">
    <h1>文生图</h1>

    <!-- =========================
         用户状态加载中
    ========================= -->
    <p v-if="userLoading" class="loading">
      用户信息加载中...
    </p>

    <template v-else>
      <!-- =========================
           WS 任务调度信息（裁决展示）
      ========================= -->
      <div
        v-if="wsDecision.X !== null"
        class="schedule-box"
      >
        <p>前方排队任务数：<strong>{{ wsDecision.X }}</strong></p>
        <p>平均执行耗时：<strong>{{ wsDecision.Y }} 秒</strong></p>
        <p>预计完成时间：<strong>{{ wsDecision.Z }} 秒</strong></p>
      </div>

      <!-- =========================
           输入框
      ========================= -->
      <textarea
        v-model="prompt"
        class="textarea"
        placeholder="请输入生成提示词"
        :disabled="textareaDisabled"
      />

      <!-- =========================
           操作按钮（结构性硬闸）
      ========================= -->
      <button
        v-if="canGenerate"
        class="btn"
        @click="handleGenerate"
      >
        <span v-if="isGenerating">生成中...</span>
        <span v-else>开始生成</span>
      </button>

      <!-- 不可生成态：无 click -->
      <button
        v-else
        class="btn"
        disabled
      >
        <span v-if="accountStatus === 'restricted'">不可生成（账号受限）</span>
        <span v-else-if="accountStatus === 'banned'">账号已封禁</span>
        <span v-else-if="authStore.quota <= 0">次数不足</span>
        <span v-else>不可用</span>
      </button>

      <!-- =========================
           状态提示
      ========================= -->
      <p v-if="accountStatus === 'restricted'" class="warn">
        当前账号为受限状态，部分功能不可用
      </p>

      <p v-if="accountStatus === 'banned'" class="error">
        当前账号已被封禁
      </p>

      <p v-if="error" class="error">
        {{ error }}
      </p>

      <!-- =========================
           任务状态
      ========================= -->
      <div v-if="taskId" class="task-box">
        <p><strong>任务 ID：</strong>{{ taskId }}</p>
        <p><strong>状态：</strong>{{ statusText }}</p>
        <p v-if="quotaLeft !== null">
          <strong>剩余次数：</strong>{{ quotaLeft }}
        </p>
      </div>

      <!-- =========================
           图片展示
      ========================= -->
      <div v-if="imageUrl" class="image-box">
        <img :src="imageUrl" alt="生成结果" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAccountStatusStore } from '@/stores/accountStatus'
import { createGenerateTask, fetchHistory } from '@/api'

/**
 * =========================
 * Store
 * =========================
 */
const authStore = useAuthStore()
const accountStatusStore = useAccountStatusStore()

/**
 * =========================
 * 用户加载态
 * =========================
 */
const userLoading = computed(() => {
  return authStore.token && !authStore.user
})

/**
 * =========================
 * account_status（v1.0.11 修正版）
 * =========================
 */
const accountStatus = computed(() => {
  return accountStatusStore.status !== 'unknown'
    ? accountStatusStore.status
    : (authStore.user?.account_status ?? 'normal')
})

/**
 * =========================
 * WS 系统裁决状态（X / Y / Z）
 * - 唯一来源：localStorage
 * - 只读、不裁决
 * =========================
 */
const wsDecision = ref({
  X: null,
  Y: null,
  Z: null,
})

const loadWsDecisionFromCache = () => {
  try {
    const raw = localStorage.getItem('ws_decision_xyz')
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (
      typeof parsed?.X === 'number' &&
      typeof parsed?.Y === 'number' &&
      typeof parsed?.Z === 'number'
    ) {
      wsDecision.value = parsed
    }
  } catch {
    // 忽略非法缓存
  }
}

const onStorage = (e) => {
  if (e.key !== 'ws_decision_xyz') return
  loadWsDecisionFromCache()
}

const onWsDecisionUpdated = () => {
  loadWsDecisionFromCache()
}


// 首次加载
loadWsDecisionFromCache()

window.addEventListener('storage', onStorage)
window.addEventListener('WS_DECISION_UPDATED', onWsDecisionUpdated)

/**
 * =========================
 * 本地状态
 * =========================
 */
const prompt = ref('')
const loading = ref(false)
const error = ref('')

const taskId = ref('')
const quotaLeft = ref(null)
const status = ref('')
const imageUrl = ref('')

let timer = null

/**
 * =========================
 * 派生状态
 * =========================
 */
const isGenerating = computed(() => {
  return loading.value || status.value === 'pending'
})

const textareaDisabled = computed(() => {
  return (
    isGenerating.value ||
    authStore.quota <= 0 ||
    accountStatus.value !== 'normal'
  )
})

const canGenerate = computed(() => {
  return (
    !userLoading.value &&
    !isGenerating.value &&
    authStore.quota > 0 &&
    accountStatus.value === 'normal'
  )
})

const statusText = computed(() => {
  if (status.value === 'pending') return '生成中'
  if (status.value === 'success') return '已完成'
  if (status.value === 'failed') return '生成失败'
  return status.value
})

/**
 * =========================
 * account_status 变化联动
 * =========================
 */
watch(
  () => accountStatus.value,
  (val) => {
    if (val !== 'normal') {
      stopPolling()
      if (status.value === 'pending') {
        status.value = ''
      }
    }
  }
)

/**
 * =========================
 * 提交生成任务
 * =========================
 */
const handleGenerate = async () => {
  if (!canGenerate.value) return

  if (!prompt.value) {
    error.value = '请输入提示词'
    return
  }

  error.value = ''
  loading.value = true
  imageUrl.value = ''
  taskId.value = ''
  status.value = ''

  try {
    const res = await createGenerateTask(prompt.value)

    taskId.value = res.task_id
    quotaLeft.value = res.quota_left
    authStore.setQuota(res.quota_left)

    status.value = 'pending'
    prompt.value = ''

    startPolling()
  } finally {
    loading.value = false
  }
}

/**
 * =========================
 * 轮询
 * =========================
 */
const startPolling = () => {
  stopPolling()

  timer = setInterval(async () => {
    if (accountStatus.value !== 'normal') {
      stopPolling()
      return
    }

    try {
      const list = await fetchHistory()
      const record = list.find(
        (item) => item.task_id === taskId.value
      )

      if (!record) return

      status.value = record.status

      if (record.status === 'success') {
        imageUrl.value = record.image_url
        stopPolling()
      }

      if (record.status === 'failed') {
        stopPolling()
      }
    } catch {
      stopPolling()
    }
  }, 3000)
}

const stopPolling = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('storage', onStorage)
  window.removeEventListener('WS_DECISION_UPDATED', onWsDecisionUpdated)
})
</script>

<style scoped>
.generate-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: var(--text-primary);
}

.loading {
  color: var(--text-secondary);
}

.schedule-box {
  padding: 12px;
  border-radius: 6px;
  background: var(--bg-muted);
  border: 1px dashed var(--border-base);
  color: var(--text-secondary);
  font-size: 14px;
}

.textarea {
  min-height: 120px;
  padding: 12px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-base);
  border-radius: 6px;
}

.textarea::placeholder {
  color: var(--text-muted);
}

.textarea:disabled {
  opacity: 0.6;
}

.btn {
  padding: 10px;
  font-size: 16px;
  border-radius: 6px;
  border: 1px solid var(--border-base);
  background: var(--bg-card);
  color: var(--text-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.warn {
  color: var(--state-warning);
}

.error {
  color: var(--state-danger);
}

.task-box {
  padding: 12px;
  border-radius: 6px;
  background: var(--bg-muted);
  border: 1px solid var(--border-base);
  color: var(--text-primary);
}

.image-box img {
  max-width: 100%;
  border-radius: 4px;
  border: 1px solid var(--border-base);
}
</style>
