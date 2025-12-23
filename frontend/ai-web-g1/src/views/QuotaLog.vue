<template>
  <div class="quota-page">
    <h1>额度变动记录</h1>

    <!-- =========================
         账号状态提示（WS 实时）
    ========================= -->
    <div
      v-if="accountStatus !== 'normal'"
      class="status-banner"
      :class="accountStatus"
    >
      <span v-if="accountStatus === 'restricted'">
        当前账号为受限状态：仅可查看额度变动记录。
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
         列表
    ========================= -->
    <div
      v-for="item in list"
      :key="item.id"
      class="row"
    >
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
    <div
      v-if="!loading && list.length === 0"
      class="empty"
    >
      暂无额度变动记录
    </div>

    <!-- 分页 -->
    <div class="pager">
      <button
        @click="prevPage"
        :disabled="offset === 0"
      >
        上一页
      </button>
      <button
        @click="nextPage"
        :disabled="list.length < limit"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAccountStatusStore } from '@/stores/accountStatus'
import { fetchQuotaLogs } from '@/api'

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

/**
 * =========================
 * 工具函数
 * =========================
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
 * =========================
 * 获取额度日志
 * =========================
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

/**
 * =========================
 * 分页
 * =========================
 */
const prevPage = () => {
  if (offset.value === 0) return
  offset.value -= limit
  fetchLogs()
}

const nextPage = () => {
  offset.value += limit
  fetchLogs()
}

/**
 * =========================
 * account_status 变化联动（v1.0.11）
 * =========================
 *
 * - 仅驱动 UI
 * - 不 fetch
 * - 不跳转
 */
watch(
  () => accountStatus.value,
  () => {
    // UI 自动响应即可
  }
)

/**
 * =========================
 * 初始化
 * =========================
 */
onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.quota-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
  color: var(--text-primary);
}

/* =========================
 * 状态提示条
 * ========================= */

.status-banner {
  padding: 10px 14px;
  margin-bottom: 12px;
  font-size: 13px;
  border-radius: 6px;
  border: 1px solid var(--border-base);
  background: var(--bg-muted);
  color: var(--text-primary);
}

.status-banner.restricted {
  border-color: var(--state-warning);
  color: var(--state-warning);
  background: var(--bg-muted);
}

.status-banner.banned {
  border-color: var(--state-danger);
  color: var(--state-danger);
  background: var(--bg-muted);
}

/* =========================
 * 列表行
 * ========================= */

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 8px;
  border-bottom: 1px solid var(--border-base);
}

.left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* =========================
 * 额度变动
 * ========================= */

.change {
  font-size: 18px;
  font-weight: bold;
}

.change.plus {
  color: var(--state-success);
}

.change.minus {
  color: var(--state-danger);
}

.reason {
  font-size: 14px;
  color: var(--text-secondary);
}

.time {
  font-size: 12px;
  color: var(--text-muted);
}

/* =========================
 * 分页
 * ========================= */

.pager {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.pager button {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid var(--border-base);
  background: var(--bg-card);
  color: var(--text-primary);
}

.pager button:disabled {
  opacity: 0.5;
}

/* =========================
 * 错误 / 空态
 * ========================= */

.error {
  color: var(--state-danger);
}

.empty {
  text-align: center;
  color: var(--text-muted);
  margin-top: 24px;
}
</style>
