<template>
  <transition name="toast-slide">
    <div v-if="visible" class="honor-toast">
      <span class="text">
        🎉 恭喜您荣誉升到 {{ levelAfter }} 级，
        系统奖励 {{ rewardQuota }} 点额度！
      </span>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * =========================
 * 展示状态
 * =========================
 */
const visible = ref(false)
const levelAfter = ref(0)
const rewardQuota = ref(0)

let hideTimer = null

/**
 * =========================
 * 显示 Toast（统一入口）
 * =========================
 */
function showToast(payload) {
  // 防御性裁决
  const level = Number(payload?.task_level_after ?? payload?.level_after ?? 0)
  const reward = Number(payload?.reward_quota ?? 0)

  if (level <= 0) return

  levelAfter.value = level
  rewardQuota.value = reward

  visible.value = true

  // 重置计时器
  if (hideTimer) {
    clearTimeout(hideTimer)
  }

  hideTimer = setTimeout(() => {
    visible.value = false
    hideTimer = null
  }, 5000)
}

/**
 * =========================
 * 监听全局 WS 事件
 * =========================
 *
 * 说明：
 * - WS 消息已经在 ws 管理器中被 parse
 * - 这里通过 window 事件桥接，避免组件直接耦合 WS
 * - 保证组件“纯展示”
 */
function onHonorLevelUp(event) {
  const payload = event.detail
  if (!payload) return
  showToast(payload)
}

onMounted(() => {
  window.addEventListener('HONOR_LEVEL_UP', onHonorLevelUp)
})

onUnmounted(() => {
  window.removeEventListener('HONOR_LEVEL_UP', onHonorLevelUp)
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
})
</script>

<style scoped>
/* =========================
   Toast 容器
========================= */
.honor-toast {
  position: fixed;
  top: 56px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;

  background: linear-gradient(
    90deg,
    #facc15,
    #f59e0b,
    #facc15
  );
  color: #3f2d00;

  padding: 10px 18px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 500;

  box-shadow:
    0 6px 20px rgba(0, 0, 0, 0.18);

  white-space: nowrap;
}

/* =========================
   进入 / 离开动画
========================= */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.35s ease;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, -20px);
}

.toast-slide-enter-to {
  opacity: 1;
  transform: translate(-50%, 0);
}

.toast-slide-leave-from {
  opacity: 1;
  transform: translate(-50%, 0);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>
