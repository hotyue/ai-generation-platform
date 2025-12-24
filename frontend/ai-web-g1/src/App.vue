<template>
  <div class="app-fixed">
    <div class="app-scroll">
      <router-view />
    </div>
  </div>
</template>

<script setup>
// v1.0.24 · iOS Safari 视觉 viewport 固定 + 容器滚动
</script>

<style>
/* ---------------------------------------
 * 基础重置
 * --------------------------------------- */
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}

/* ---------------------------------------
 * 固定到“真实可视区域”（iOS Safari 关键）
 * --------------------------------------- */
.app-fixed {
  position: fixed;
  top: env(safe-area-inset-top);
  right: env(safe-area-inset-right);
  bottom: env(safe-area-inset-bottom);
  left: env(safe-area-inset-left);

  display: flex;
  justify-content: center;

  /* 固定容器本身不滚动，滚动交给内部 */
  overflow: hidden;
}

/* ---------------------------------------
 * 滚动容器：承载 router-view
 * 关键点：
 * - overflow-y: auto 开启滚动
 * - -webkit-overflow-scrolling: touch 启用 iOS 惯性滚动
 * - min-height: 0 避免 flex 子项高度挤压导致无法滚动
 * --------------------------------------- */
.app-scroll {
  width: 100%;
  max-width: 100%;

  flex: 1;
  min-height: 0;

  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
</style>
