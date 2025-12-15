<template>
  <div class="quota-page">
    <h1>额度变动记录</h1>

    <!-- 加载 / 错误 -->
    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- 列表 -->
    <div v-for="item in list" :key="item.id" class="row">
      <div class="left">
        <div
          class="change"
          :class="item.change > 0 ? 'plus' : 'minus'"
        >
          {{ item.change > 0 ? '+' : '' }}{{ item.change }}
        </div>

        <div class="reason">
          {{ reasonText(item.reason) }}
        </div>
      </div>

      <div class="time">
        {{ formatTime(item.created_at) }}
      </div>
    </div>

    <!-- 空态 -->
    <div v-if="!loading && list.length === 0" class="empty">
      暂无额度变动记录
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchQuotaLogs } from '@/api'

const list = ref([])
const loading = ref(false)
const error = ref('')

const limit = 10
const offset = ref(0)

/**
 * reason → 中文说明
 */
const reasonText = (reason) => {
  if (!reason) return '未知变动'

  if (reason === 'manual_grant') return '管理员手动充值'
  if (reason.startsWith('plan:')) {
    return `套餐充值（${reason.replace('plan:', '')}）`
  }
  if (reason === 'generate') return '生成图片消耗'

  return reason
}

const formatTime = (t) => {
  return new Date(t).toLocaleString()
}

/**
 * 获取额度日志
 */
const fetchLogs = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await fetchQuotaLogs({
      limit,
      offset: offset.value,
    })

    list.value = res
  } catch (e) {
    console.error(e)
    error.value = '获取额度记录失败'
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (offset.value === 0) return
  offset.value -= limit
  fetchLogs()
}

const nextPage = () => {
  offset.value += limit
  fetchLogs()
}

onMounted(fetchLogs)
</script>

<style scoped>
.quota-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 8px;
  border-bottom: 1px solid #eee;
}

.left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.change {
  font-size: 18px;
  font-weight: bold;
}

.change.plus {
  color: #16a34a;
}

.change.minus {
  color: #dc2626;
}

.reason {
  font-size: 14px;
  color: #555;
}

.time {
  font-size: 12px;
  color: #888;
}

.pager {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.error {
  color: red;
}

.empty {
  text-align: center;
  color: #888;
  margin-top: 24px;
}
</style>
