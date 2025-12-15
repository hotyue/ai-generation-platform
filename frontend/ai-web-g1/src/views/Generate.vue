<template>
  <div class="generate-page">
    <h1>文生图</h1>

    <!-- 输入 -->
    <textarea
      v-model="prompt"
      placeholder="请输入生成提示词"
      class="textarea"
      :disabled="isGenerating || authStore.quota <= 0"
    ></textarea>

    <!-- ⭐ 按钮态升级 -->
    <button
      class="btn"
      :disabled="!canGenerate"
      @click="handleGenerate"
    >
      <span v-if="isGenerating">生成中...</span>
      <span v-else-if="authStore.quota <= 0">次数不足</span>
      <span v-else>开始生成</span>
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- 任务状态 -->
    <div v-if="taskId" class="task-box">
      <p><strong>任务 ID：</strong>{{ taskId }}</p>
      <p><strong>状态：</strong>{{ statusText }}</p>
      <p v-if="quotaLeft !== null">
        <strong>剩余次数：</strong>{{ quotaLeft }}
      </p>
    </div>

    <!-- 图片展示 -->
    <div v-if="imageUrl" class="image-box">
      <img :src="imageUrl" alt="生成结果" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { createGenerateTask, fetchHistory } from '@/api'

const authStore = useAuthStore()

const prompt = ref('')
const loading = ref(false)
const error = ref('')

const taskId = ref('')
const quotaLeft = ref(null)
const status = ref('')
const imageUrl = ref('')

let timer = null

const isGenerating = computed(() => {
  return loading.value || status.value === 'pending'
})

const canGenerate = computed(() => {
  return authStore.quota > 0 && !isGenerating.value
})

const statusText = computed(() => {
  if (status.value === 'pending') return '生成中'
  if (status.value === 'success') return '已完成'
  if (status.value === 'failed') return '生成失败'
  return status.value
})

/**
 * 提交生成任务
 */
const handleGenerate = async () => {
  if (!canGenerate.value) return

  error.value = ''
  imageUrl.value = ''
  taskId.value = ''
  status.value = ''

  if (!prompt.value) {
    error.value = '请输入提示词'
    return
  }

  if (authStore.quota <= 0) {
    error.value = '生成次数不足，请充值'
    return
  }

  loading.value = true

  try {
    const res = await createGenerateTask(prompt.value)

    taskId.value = res.task_id
    quotaLeft.value = res.quota_left

    authStore.setQuota(res.quota_left)

    status.value = 'pending'
    prompt.value = ''

    startPolling()
  } catch {
    // 错误提示已由 http.js 统一处理
  } finally {
    loading.value = false
  }
}

/**
 * 轮询任务状态
 */
const startPolling = () => {
  stopPolling()

  timer = setInterval(async () => {
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
}

.textarea {
  min-height: 120px;
  padding: 12px;
  font-size: 14px;
}

.btn {
  padding: 10px;
  font-size: 16px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: red;
}

.task-box {
  padding: 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
}

.image-box img {
  max-width: 100%;
  border-radius: 4px;
}
</style>
