<template>
  <div class="history-page">
    <h1>生成历史</h1>

    <!-- =========================
         账号状态提示（WS 实时）
    ========================= -->
    <div
      v-if="accountStatus !== 'normal'"
      class="status-banner"
      :class="accountStatus"
    >
      <span v-if="accountStatus === 'restricted'">
        当前账号为受限状态：仅可查看历史记录。
      </span>
      <span v-else-if="accountStatus === 'banned'">
        当前账号已被封禁。
      </span>
    </div>

    <!-- =========================
         加载 / 错误
    ========================= -->
    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- =========================
         历史列表
    ========================= -->
    <div
      v-for="item in list"
      :key="item.id"
      class="card"
    >
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

    <!-- =========================
         分页
    ========================= -->
    <div class="pager">
      <button
        @click="prevPage"
        :disabled="offset === 0 || accountStatus !== 'normal'"
      >
        上一页
      </button>
      <button
        @click="nextPage"
        :disabled="list.length < limit || accountStatus !== 'normal'"
      >
        下一页
      </button>
    </div>

    <!-- =========================
         大图预览
    ========================= -->
    <div
      v-if="preview"
      class="preview"
      @click="preview = ''"
    >
      <img :src="preview" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useAccountStatusStore } from '@/stores/accountStatus'
import { fetchHistory } from '@/api'

/**
 * =========================
 * account_status（WS 唯一事实源）
 * =========================
 */
const accountStatusStore = useAccountStatusStore()

const accountStatus = computed(() => {
  return accountStatusStore.status
})

/**
 * =========================
 * 页面状态
 * =========================
 */
const list = ref([])
const loading = ref(false)
const error = ref('')

const limit = 10
const offset = ref(0)

const preview = ref('')
let timer = null

/**
 * =========================
 * 获取历史记录
 * =========================
 */
const loadHistory = async () => {
  // ⭐ 唯一禁止条件：banned
  if (accountStatus.value === 'banned') return

  loading.value = true
  error.value = ''

  try {
    const data = await fetchHistory({
      limit,
      offset: offset.value,
    })

    list.value = data

    const hasPending = data.some(
      (item) => item.status === 'pending'
    )

    hasPending ? startPolling() : stopPolling()
  } catch {
    error.value = '获取历史失败'
  } finally {
    loading.value = false
  }
}

/**
 * =========================
 * 轮询（仅基于任务状态）
 * =========================
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
 * =========================
 * account_status 变化联动
 * =========================
 */
watch(
  () => accountStatus.value,
  (val) => {
    if (val === 'banned') {
      stopPolling()
      list.value = []
      return
    }

    // normal / restricted / unknown
    loadHistory()
  }
)

/**
 * =========================
 * 分页
 * =========================
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
 * =========================
 * 工具函数
 * =========================
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

/**
 * =========================
 * 初始化
 * =========================
 */
onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  stopPolling()
})
</script>


<style scoped>
/* 样式保持不变 */
.history-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px;
}

.status-banner {
  padding: 10px 14px;
  margin-bottom: 12px;
  font-size: 13px;
  border-radius: 6px;
}

.status-banner.restricted {
  background: #fff7ed;
  color: #9a3412;
}

.status-banner.banned {
  background: #fef2f2;
  color: #991b1b;
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
