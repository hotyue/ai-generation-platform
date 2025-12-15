<template>
  <div class="plan-card" :class="{ inactive: !plan.is_active }">
    <h3 class="name">{{ plan.name }}</h3>

    <div class="quota">
      {{ plan.quota }} 次
    </div>

    <div class="price">
      ¥ {{ plan.price }}
    </div>

    <button class="btn" disabled>
      暂不支持购买
    </button>
  </div>
</template>

<script setup>
defineProps({
  plan: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.plan-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-card.inactive {
  opacity: 0.5;
}

.name {
  font-size: 18px;
  font-weight: bold;
}

.quota {
  font-size: 14px;
  color: #374151;
}

.price {
  font-size: 22px;
  font-weight: bold;
  color: #2563eb;
}

.btn {
  margin-top: auto;
  padding: 8px;
  background: #9ca3af;
  color: #fff;
  border: none;
  border-radius: 4px;
}
</style>
