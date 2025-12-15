<template>
  <div class="plans-page">
    <h1>套餐中心</h1>

    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="grid">
      <PlanCard
        v-for="p in plans"
        :key="p.id"
        :plan="p"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchPlans } from '@/api'
import PlanCard from '@/components/PlanCard.vue'

const plans = ref([])
const loading = ref(false)
const error = ref('')

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

onMounted(loadPlans)
</script>

<style scoped>
.plans-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 16px;
}

.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.error {
  color: red;
}
</style>
