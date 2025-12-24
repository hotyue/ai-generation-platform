<template>
  <!--
    v1.0.24 · Viewport Responsive Layout Governance
    App 仅承担最小布局壳职责：
    - 占满浏览器 viewport
    - 内容在 viewport 内居中
    - 不做任何主题 / 业务 / 交互判断
  -->
  <div class="app-viewport">
    <div class="app-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
// App 只负责承载路由与最小 viewport 布局壳
// 不做任何 Layout 策略判断
</script>

<style>
/* --------------------------------------------------
 * v1.0.24 · 全局高度链闭合（viewport 基础）
 * -------------------------------------------------- */
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}

/* --------------------------------------------------
 * Viewport 壳：以浏览器 viewport 为唯一基准
 * -------------------------------------------------- */
.app-viewport {
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh; /* 动态 viewport，适配移动端地址栏 */
  display: flex;
  justify-content: center;
}

/* --------------------------------------------------
 * 内容壳：只负责居中与结构承载
 * -------------------------------------------------- */
.app-content {
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
