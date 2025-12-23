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
  border: 1px solid var(--border-base);
  border-radius: 8px;
  padding: 16px;

  background: var(--bg-card);
  color: var(--text-primary);

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
  color: var(--text-primary);
}

.quota {
  font-size: 14px;
  color: var(--text-secondary);
}

.price {
  font-size: 22px;
  font-weight: bold;
  color: var(--state-success);
}

.btn {
  margin-top: auto;
  padding: 8px;

  background: var(--bg-muted);
  color: var(--text-primary);

  border: 1px solid var(--border-base);
  border-radius: 4px;

  cursor: not-allowed;
}
</style>
