<template>
  <div class="admin-plans">
    <h1 class="title">套餐管理</h1>

    <!-- 顶部操作 -->
    <div class="toolbar">
      <button class="btn primary" @click="showCreate = true">
        新增套餐
      </button>
    </div>

    <!-- 加载 / 错误 -->
    <div v-if="loading" class="hint">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- 套餐列表 -->
    <div class="plan-list">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="plan-card"
      >
        <div class="plan-main">
          <div class="plan-name">
            {{ plan.name }}
            <span
              v-if="!plan.is_active"
              class="badge inactive"
            >
              已停用
            </span>
          </div>

          <div class="plan-meta">
            <span>额度：{{ plan.quota }} 次</span>
            <span>价格：￥{{ plan.price }}</span>
          </div>
        </div>

        <div class="plan-actions">
          <!-- 编辑 -->
          <button
            class="btn"
            :disabled="editingPlan && editingPlan.id !== plan.id"
            @click="openEdit(plan)"
          >
            编辑
          </button>

          <button
            v-if="plan.is_active"
            class="btn danger"
            @click="disablePlan(plan)"
          >
            停用
          </button>

          <button
            v-else
            class="btn success"
            @click="enablePlan(plan)"
          >
            启用
          </button>
        </div>
      </div>
    </div>

    <!-- 新增套餐弹窗 -->
    <div
      v-if="showCreate"
      class="modal-mask"
      @click.self="showCreate = false"
    >
      <div class="modal">
        <h2>新增套餐</h2>

        <input v-model="form.name" placeholder="套餐名称" />
        <input v-model.number="form.quota" type="number" placeholder="额度（次数）" />
        <input v-model.number="form.price" type="number" placeholder="价格（元）" />

        <div class="modal-actions">
          <button class="btn" @click="showCreate = false">取消</button>
          <button class="btn primary" @click="createPlan">创建</button>
        </div>
      </div>
    </div>

    <!-- 编辑套餐弹窗 -->
    <div
      v-if="editingPlan"
      class="modal-mask"
      @click.self="cancelEdit"
    >
      <div class="modal">
        <h2>编辑套餐</h2>

        <input v-model="editForm.name" placeholder="套餐名称" />
        <input v-model.number="editForm.quota" type="number" placeholder="额度（次数）" />
        <input v-model.number="editForm.price" type="number" placeholder="价格（元）" />

        <div class="modal-actions">
          <button class="btn" @click="cancelEdit">取消</button>
          <button class="btn primary" @click="submitEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  fetchAdminPlans,
  createAdminPlan,
  updateAdminPlan,
  disableAdminPlan,
  enableAdminPlan,
} from '@/api'

const plans = ref([])
const loading = ref(false)
const error = ref('')

const showCreate = ref(false)
const form = ref({
  name: '',
  quota: 0,
  price: 0,
})

// 编辑态
const editingPlan = ref(null)
const editForm = ref({
  name: '',
  quota: 0,
  price: 0,
})

/* 获取套餐列表 */
const fetchPlans = async () => {
  loading.value = true
  error.value = ''
  try {
    plans.value = await fetchAdminPlans()
  } catch (e) {
    console.error(e)
    error.value = '获取套餐失败'
  } finally {
    loading.value = false
  }
}

/* 新增套餐 */
const createPlan = async () => {
  if (!form.value.name || form.value.quota <= 0) {
    alert('请输入完整套餐信息')
    return
  }

  try {
    await createAdminPlan(form.value)
    showCreate.value = false
    form.value = { name: '', quota: 0, price: 0 }
    fetchPlans()
  } catch (e) {
    console.error(e)
    alert('创建套餐失败')
  }
}

/* 启用 / 停用 */
const disablePlan = async (plan) => {
  try {
    await disableAdminPlan(plan.id)
    fetchPlans()
  } catch (e) {
    alert('停用失败')
  }
}

const enablePlan = async (plan) => {
  try {
    await enableAdminPlan(plan.id)
    fetchPlans()
  } catch (e) {
    alert('启用失败')
  }
}

/* 编辑套餐 */
const openEdit = (plan) => {
  editingPlan.value = plan
  editForm.value = {
    name: plan.name,
    quota: plan.quota,
    price: plan.price,
  }
}

const cancelEdit = () => {
  editingPlan.value = null
}

const submitEdit = async () => {
  if (!editingPlan.value) return

  try {
    await updateAdminPlan(editingPlan.value.id, {
      name: editForm.value.name,
      quota: editForm.value.quota,
      price: editForm.value.price,
    })
    editingPlan.value = null
    fetchPlans()
  } catch (e) {
    console.error(e)
    const msg =
      e?.response?.data?.detail ||
      '修改套餐失败（后端校验未通过）'
    alert(msg)
  }
}

onMounted(fetchPlans)
</script>

<style scoped>
/* =========================
 * 页面容器
 * ========================= */

.admin-plans {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px;
  color: var(--text-primary);
}

.title {
  font-size: 28px;
  margin-bottom: 16px;
  color: var(--text-primary);
}

/* =========================
 * 工具栏
 * ========================= */

.toolbar {
  margin-bottom: 16px;
}

/* =========================
 * 提示 / 错误
 * ========================= */

.hint {
  color: var(--text-secondary);
}

.error {
  color: var(--state-danger);
}

/* =========================
 * 套餐列表
 * ========================= */

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-card {
  background: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: 8px;
  padding: 14px;

  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

/* =========================
 * 套餐信息
 * ========================= */

.plan-name {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-primary);
}

.plan-meta {
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  gap: 12px;
  margin-top: 4px;
}

/* 停用标记 */
.badge.inactive {
  background: var(--bg-muted);
  color: var(--text-secondary);
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 6px;
  border: 1px solid var(--border-base);
}

/* =========================
 * 操作区
 * ========================= */

.plan-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* =========================
 * 按钮（统一语义）
 * ========================= */

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;

  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-base);
}

.btn.primary {
  border-color: var(--state-success);
  color: var(--state-success);
}

.btn.success {
  border-color: var(--state-success);
  color: var(--state-success);
}

.btn.danger {
  border-color: var(--state-danger);
  color: var(--state-danger);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* =========================
 * Modal 遮罩
 * ========================= */

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

/* =========================
 * Modal 内容
 * ========================= */

.modal {
  background: var(--bg-card);
  color: var(--text-primary);

  padding: 20px;
  width: 90%;
  max-width: 360px;
  border-radius: 8px;

  display: flex;
  flex-direction: column;
  gap: 10px;

  border: 1px solid var(--border-base);
}

/* 输入框 */
.modal input {
  padding: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-base);
  border-radius: 4px;
}

.modal input::placeholder {
  color: var(--text-muted);
}

/* 操作区 */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
