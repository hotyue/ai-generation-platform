<template>
  <div class="history-page">
    <h1>生成历史</h1>

    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-for="item in list" :key="item.id" class="card">
      <div class="info">
        <div class="prompt">{{ item.prompt }}</div>

        <div class="meta">
          <span :class="['status', item.status]">
            状态：{{ statusText(item.status) }}
          </span>
          <span>{{ formatTime(item.created_at) }}</span>
        </div>
      </div>

      <div class="thumb" v-if="item.image_url">
        <img
          :src="item.image_url"
          @click="openPreview(item.image_url)"
        />
      </div>

      <div v-if="item.status === 'pending'" class="pending">
        ⏳ 生成中…
      </div>

      <div v-if="item.status === 'failed'" class="failed">
        ❌ 生成失败
      </div>
    </div>

    <!-- 分页 -->
    <div class="pager">
      <button @click="prevPage" :disabled="offset === 0">
        上一页
      </button>
      <button @click="nextPage" :disabled="list.length < limit">
        下一页
      </button>
    </div>

    <!-- 大图预览 -->
    <div v-if="preview" class="preview" @click="preview = ''">
      <img :src="preview" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchHistory } from '@/api'

const list = ref([])
const loading = ref(false)
const error = ref('')

const limit = 10
const offset = ref(0)

const preview = ref('')
let timer = null

/**
 * 获取历史记录
 */
const loadHistory = async () => {
  loading.value = true
  error.value = ''

  try {
    const data = await fetchHistory({
      limit,
      offset: offset.value,
    })

    list.value = data

    const hasPending = data.some(item => item.status === 'pending')
    hasPending ? startPolling() : stopPolling()
  } catch (e) {
    error.value = '获取历史失败'
  } finally {
    loading.value = false
  }
}

/**
 * 轮询（仅存在 pending 时）
 */
const startPolling = () => {
  if (timer) return
  timer = setInterval(loadHistory, 3000)
}

const stopPolling = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

/**
 * 分页
 */
const prevPage = () => {
  if (offset.value === 0) return
  offset.value -= limit
  loadHistory()
}

const nextPage = () => {
  offset.value += limit
  loadHistory()
}

/**
 * 工具函数
 */
const openPreview = (url) => {
  preview.value = url
}

const statusText = (s) => {
  if (s === 'pending') return '生成中'
  if (s === 'success') return '已完成'
  if (s === 'failed') return '失败'
  return s
}

const formatTime = (t) => {
  return new Date(t).toLocaleString()
}

onMounted(loadHistory)
onUnmounted(stopPolling)
</script>


<style scoped>
.history-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px;
}

.card {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.prompt {
  font-weight: bold;
  margin-bottom: 6px;
}

.meta {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 12px;
}

.status.pending {
  color: #f59e0b;
}

.status.success {
  color: #16a34a;
}

.status.failed {
  color: #dc2626;
}

.thumb img {
  width: 120px;
  cursor: pointer;
  border-radius: 4px;
}

.pending {
  font-size: 12px;
  color: #f59e0b;
}

.failed {
  font-size: 12px;
  color: #dc2626;
}

.pager {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 16px 0;
}

.error {
  color: red;
}

.preview {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview img {
  max-width: 90%;
  max-height: 90%;
}
</style>
