<template>
  <div class="profile-page">
    <h1>账户信息</h1>

    <!-- ========================= 用户信息 ========================= -->
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

      <!-- ===== 荣誉等级（v1.0.30） ===== -->
      <div class="row">
        <span class="label">荣誉等级</span>
        <span class="honor-level">
          <span :class="['honor-item', `level-${honorStore.crown}`]">👑</span>
          <span :class="['honor-item', `level-${honorStore.diamond}`]">💎</span>
          <span :class="['honor-item', `level-${honorStore.sun}`]">☀️</span>
          <span :class="['honor-item', `level-${honorStore.moon}`]">🌙</span>
          <span :class="['honor-item', `level-${honorStore.star}`]">⭐</span>
        </span>
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

    <!-- ========================= 封禁提示 ========================= -->
    <section
      v-if="accountStatus === 'banned'"
      class="card banned-hint"
    >
      当前账号已被封禁，所有生成、额度、套餐相关功能均不可用。
      <br />
      如有疑问，请联系管理员。
    </section>

    <!-- ========================= 配额信息 ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card"
    >
      <h2>🎯 当前配额</h2>

      <div class="quota-box">
        <div class="quota-number">
          {{ authStore.quota ?? '--' }}
        </div>
        <div class="quota-desc">
          剩余生成次数
        </div>
      </div>

      <p class="hint">
        每次生成图片将消耗 1 次额度
      </p>
    </section>

    <!-- ========================= 最近额度变动 ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card quota-card"
    >
      <h2>📊 最近额度变动</h2>

      <div v-if="quotaLogs.length === 0" class="empty">
        暂无额度记录
      </div>

      <div
        v-for="log in quotaLogs"
        :key="log.id"
        class="info-row"
      >
        <!-- 左列：原因 -->
        <div class="cell-main ellipsis">
          {{ reasonText(log.reason) }}
        </div>

        <!-- 中列：变动值（6ch） -->
        <div
          class="cell-mid mono"
          :class="log.change > 0 ? 'plus' : 'minus'"
        >
          {{ log.change > 0 ? '+' : '' }}{{ log.change }}
        </div>

        <!-- 右列：时间（14ch） -->
        <div class="cell-end muted">
          {{ formatTime(log.created_at) }}
        </div>
      </div>

      <p class="hint">
        仅展示最近 5 条记录
      </p>
    </section>

    <!-- ========================= 可用套餐 ========================= -->
    <section
      v-if="accountStatus !== 'banned'"
      class="card plan-card"
    >
      <h2>📦 可用套餐</h2>

      <div v-if="plans.length === 0" class="empty">
        暂无套餐
      </div>

      <div
        v-for="plan in plans"
        :key="plan.id"
        class="info-row"
      >
        <!-- 左列：套餐名 -->
        <div class="cell-main ellipsis">
          {{ plan.name }}
        </div>

        <!-- 中列：次数 + 价格（按内容宽度） -->
        <div class="cell-mid mono">
          {{ plan.quota }} 次 · ¥{{ plan.price }}
        </div>

        <!-- 右列：状态（8ch） -->
        <div class="cell-end active">
          可用
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
import { useHonorStore } from '@/stores/honor'
import { fetchPlans, fetchQuotaLogs } from '@/api'

const authStore = useAuthStore()
const accountStatusStore = useAccountStatusStore()
const honorStore = useHonorStore()

const me = computed(() => authStore.user)
const accountStatus = computed(() => accountStatusStore.status)

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

const plans = ref([])
const quotaLogs = ref([])

const loadPlans = async () => {
  plans.value = await fetchPlans()
}

const loadQuotaLogs = async () => {
  quotaLogs.value = await fetchQuotaLogs({
    limit: 5,
    offset: 0,
  })
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

  const d = new Date(t)
  const MM = String(d.getMonth() + 1).padStart(2, '0')
  const DD = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')

  return `${MM}/${DD} ${hh}:${mm}:${ss}`
}

onMounted(async () => {
  if (accountStatus.value !== 'banned') {
    await Promise.all([
      loadPlans(),
      loadQuotaLogs(),
    ])
  }
})

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

/* ===== 卡片 ===== */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: 8px;
  padding: 16px;
  color: var(--text-primary);
}

.card h2 {
  margin-bottom: 12px;
}

/* ===== 基本行 ===== */
.row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}

.label {
  color: var(--text-secondary);
}

/* ===== 荣誉等级 ===== */
.honor-level {
  display: inline-flex;
  gap: 6px;
}

.honor-item {
  font-size: 16px;
  line-height: 1;
}

/* 等级强度映射（示例） */
.level-1 { opacity: 0.3; }
.level-2 { opacity: 0.45; }
.level-3 { opacity: 0.6; }
.level-4 { opacity: 0.8; }
.level-5 { opacity: 1; }

/* ===== 配额 ===== */
.quota-box {
  text-align: center;
  margin: 16px 0;
}

.quota-number {
  font-size: 36px;
  font-weight: bold;
}

.hint {
  color: var(--text-secondary);
}

/* ===== 三段式信息行（最终稳定版） ===== */
.info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-base);
}

/* 左列：吃剩余空间 */
.cell-main {
  flex: 1 1 auto;
  min-width: 0;
  text-align: left;
}

/* 中列：默认按内容宽度 */
.cell-mid {
  flex: 0 0 auto;
  text-align: right;
  white-space: nowrap;
}

/* 右列：固定宽度 */
.cell-end {
  flex: 0 0 auto;
  text-align: right;
  white-space: nowrap;
}

/* ===== 业务语义宽度裁决 ===== */
.quota-card .cell-mid {
  flex-basis: 6ch;
}

.quota-card .cell-end {
  flex-basis: 14ch;
}

.plan-card .cell-mid {
  flex-basis: auto;
}

.plan-card .cell-end {
  flex-basis: 6ch;
}

/* ===== 辅助 ===== */
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mono {
  font-variant-numeric: tabular-nums;
}

.muted {
  color: var(--text-secondary);
}

.plus {
  color: var(--state-success);
}

.minus {
  color: var(--state-danger);
}

.active {
  color: var(--state-success);
}
</style>
