<template>
  <div class="plans-page">
    <h1>套餐中心</h1>

    <!-- =========================
         账号状态提示
    ========================= -->
    <div
      v-if="accountStatus !== 'normal'"
      class="status-banner"
      :class="accountStatus"
    >
      <span v-if="accountStatus === 'restricted'">
        当前账号为受限状态：可查看套餐，但暂不可购买。
      </span>
      <span v-else-if="accountStatus === 'banned'">
        当前账号已被封禁，无法进行任何购买操作。
      </span>
    </div>

    <!-- =========================
         加载 / 错误
    ========================= -->
    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- =========================
         套餐列表
    ========================= -->
    <div class="grid">
      <div
        v-for="p in plans"
        :key="p.id"
        class="plan-wrapper"
      >
        <!-- 套餐卡片 -->
        <PlanCard
          :plan="p"
          :disabled="accountStatus !== 'normal'"
        />

        <!-- 覆盖层（非 normal） -->
        <div
          v-if="accountStatus !== 'normal'"
          class="overlay"
        >
          <span v-if="accountStatus === 'restricted'">
            账号受限，暂不可购买
          </span>
          <span v-else-if="accountStatus === 'banned'">
            账号已封禁
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchPlans } from '@/api'
import PlanCard from '@/components/PlanCard.vue'

const router = useRouter()
const authStore = useAuthStore()

/**
 * account_status（唯一来源）
 */
const accountStatus = computed(() => authStore.accountStatus)

/**
 * 页面状态
 */
const plans = ref([])
const loading = ref(false)
const error = ref('')

/**
 * 拉取套餐
 */
const loadPlans = async () => {
  loading.value = true
  error.value = ''
  try {
    plans.value = await fetchPlans()
  } catch (e) {
    console.error(e)
    error.value = '获取套餐失败'
  } finally {
    loading.value = false
  }
}

/**
 * 初始化
 */
onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      router.replace('/login')
      return
    }
  }

  // banned 用户不允许进入
  if (accountStatus.value === 'banned') {
    router.replace('/login')
    return
  }

  loadPlans()
})
</script>

<style scoped>
.plans-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 16px;
}

/* 状态提示条 */
.status-banner {
  padding: 10px 14px;
  margin-bottom: 16px;
  font-size: 14px;
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

/* 套餐网格 */
.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.plan-wrapper {
  position: relative;
}

/* 覆盖层 */
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #444;
  border-radius: 8px;
}

.error {
  color: red;
}
</style>
