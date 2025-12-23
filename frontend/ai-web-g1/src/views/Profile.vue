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
        <span class="label">账户状态</span>
        <span class="status" :class="accountStatus">
          {{ accountStatusText }}
        </span>
      </div>

      <div class="row">
        <span class="label">注册时间</span>
        <span>{{ formatTime(me?.created_at) }}</span>
      </div>
    </section>

    <!-- =========================
         封禁提示（展示级）
    ========================= -->
    <section
      v-if="accountStatus === 'banned'"
      class="card banned-hint"
    >
      当前账号已被封禁，所有生成、额度、套餐相关功能均不可用。
      <br />
      如有疑问，请联系管理员。
    </section>

    <!-- =========================
         配额信息（仅 normal / restricted）
    ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card"
    >
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
         最近额度变动（仅 normal / restricted）
    ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card"
    >
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
        仅展示最近 5 条记录
      </p>
    </section>

    <!-- =========================
         套餐列表（仅 normal / restricted）
    ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card"
    >
      <h2>📦 可用套餐</h2>

      <div v-if="plans.length === 0" class="empty">
        暂无套餐
      </div>

      <div
        v-for="plan in plans"
        :key="plan.id"
        class="plan"
      >
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
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAccountStatusStore } from '@/stores/accountStatus'
import { fetchPlans, fetchQuotaLogs } from '@/api'

const authStore = useAuthStore()
const accountStatusStore = useAccountStatusStore()

/**
 * =========================
 * 用户信息（来自 authStore）
 * =========================
 */
const me = computed(() => authStore.user)

/**
 * =========================
 * account_status（WS 唯一事实源）
 * =========================
 */
const accountStatus = computed(() => {
  return accountStatusStore.status
})

const accountStatusText = computed(() => {
  switch (accountStatus.value) {
    case 'restricted':
      return '受限（部分功能不可用）'
    case 'banned':
      return '已封禁（禁止使用）'
    default:
      return '正常'
  }
})

/**
 * =========================
 * 页面数据
 * =========================
 */
const plans = ref([])
const quotaLogs = ref([])

/**
 * =========================
 * 数据加载（展示级）
 * =========================
 */
const loadPlans = async () => {
  plans.value = await fetchPlans()
}

const loadQuotaLogs = async () => {
  quotaLogs.value = await fetchQuotaLogs({
    limit: 5,
    offset: 0,
  })
}

/**
 * =========================
 * 工具函数
 * =========================
 */
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

/**
 * =========================
 * 初始化
 * =========================
 */
onMounted(async () => {
  // 页面展示级初始化
  if (accountStatus.value !== 'banned') {
    await Promise.all([
      loadPlans(),
      loadQuotaLogs(),
    ])
  }
})

/**
 * =========================
 * account_status 实时联动（v1.0.11 核心）
 * =========================
 */
watch(
  () => accountStatus.value,
  async (status) => {
    if (status === 'banned') {
      plans.value = []
      quotaLogs.value = []
      return
    }

    await Promise.all([
      loadPlans(),
      loadQuotaLogs(),
    ])
  }
)
</script>

<style scoped>
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

/* ===== 账户状态 ===== */
.status.normal {
  color: #16a34a;
}

.status.restricted {
  color: #f59e0b;
}

.status.banned {
  color: #dc2626;
  font-weight: 600;
}

/* ===== 封禁提示 ===== */
.banned-hint {
  border: 1px solid #fecaca;
  background: #fff1f2;
  color: #b91c1c;
  font-weight: 500;
}

/* ===== 配额 ===== */
.quota-box {
  text-align: center;
  margin: 16px 0;
}

.quota-number {
  font-size: 36px;
  font-weight: bold;
}
</style>
