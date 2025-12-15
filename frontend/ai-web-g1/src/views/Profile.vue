<template>
  <div class="profile-page">
    <h1>账户信息</h1>

    <!-- =========================
         用户信息
    ========================= -->
    <section class="card">
      <h2>👤 用户信息</h2>

      <div class="row">
        <span class="label">用户名</span>
        <span>{{ me?.username || '--' }}</span>
      </div>

      <div class="row">
        <span class="label">角色</span>
        <span>{{ me?.role || '--' }}</span>
      </div>

      <div class="row">
        <span class="label">注册时间</span>
        <span>{{ formatTime(me?.created_at) }}</span>
      </div>
    </section>

    <!-- =========================
         配额信息
    ========================= -->
    <section class="card">
      <h2>🎯 当前配额</h2>

      <div class="quota-box">
        <div class="quota-number">
          {{ me?.quota ?? '--' }}
        </div>
        <div class="quota-desc">
          剩余生成次数
        </div>
      </div>

      <p class="hint">
        每次生成图片将消耗 1 次额度
      </p>
    </section>

    <!-- =========================
         最近额度变动
    ========================= -->
    <section class="card">
      <h2>📊 最近额度变动</h2>

      <div v-if="quotaLogs.length === 0" class="empty">
        暂无额度记录
      </div>

      <div
        v-for="log in quotaLogs"
        :key="log.id"
        class="quota-log-row"
      >
        <div
          class="change"
          :class="log.change > 0 ? 'plus' : 'minus'"
        >
          {{ log.change > 0 ? '+' : '' }}{{ log.change }}
        </div>

        <div class="log-info">
          <div class="reason">
            {{ reasonText(log.reason) }}
          </div>
          <div class="time">
            {{ formatTime(log.created_at) }}
          </div>
        </div>
      </div>

      <p class="hint">
        仅展示最近 5 条记录，完整记录请前往额度明细页
      </p>
    </section>

    <!-- =========================
         套餐列表（只读）
    ========================= -->
    <section class="card">
      <h2>📦 可用套餐</h2>

      <div v-if="plans.length === 0" class="empty">
        暂无套餐
      </div>

      <div v-for="plan in plans" :key="plan.id" class="plan">
        <div class="plan-info">
          <div class="plan-name">{{ plan.name }}</div>
          <div class="plan-meta">
            <span>{{ plan.quota }} 次</span>
            <span>￥{{ plan.price }}</span>
          </div>
        </div>

        <div class="plan-status">
          <span v-if="plan.is_active" class="active">可用</span>
          <span v-else class="inactive">已停用</span>
        </div>
      </div>

      <p class="hint">
        套餐购买功能即将上线
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getMe,
  fetchPlans,
  fetchQuotaLogs,
} from '@/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const me = ref(null)
const plans = ref([])
const quotaLogs = ref([])

// =========================
// 当前用户
// =========================
const fetchMe = async () => {
  try {
    me.value = await getMe()
    authStore.setUser(me.value)
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
}

// =========================
// 套餐（只读）
// =========================
const loadPlans = async () => {
  try {
    plans.value = await fetchPlans()
  } catch (e) {
    console.error('获取套餐失败', e)
  }
}

// =========================
// 最近额度记录
// =========================
const loadQuotaLogs = async () => {
  try {
    quotaLogs.value = await fetchQuotaLogs({
      limit: 5,
      offset: 0,
    })
  } catch (e) {
    console.error('获取额度记录失败', e)
  }
}

const reasonText = (reason) => {
  if (!reason) return '未知变动'
  if (reason === 'manual_grant') return '管理员充值'
  if (reason === 'generate') return '生成图片消耗'
  if (reason.startsWith('plan:')) {
    return `套餐充值（${reason.replace('plan:', '')}）`
  }
  return reason
}

const formatTime = (t) => {
  if (!t) return '--'
  return new Date(t).toLocaleString()
}

onMounted(() => {
  fetchMe()
  loadPlans()
  loadQuotaLogs()
})
</script>

<style scoped>
/* —— 样式保持你原来的，不动 —— */
.profile-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #ffffff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
}

.card h2 {
  margin-bottom: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}

.label {
  color: #666;
}

.quota-box {
  text-align: center;
  margin: 16px 0;
}

.quota-number {
  font-size: 36px;
  font-weight: bold;
}

.quota-desc {
  color: #666;
}
</style>
