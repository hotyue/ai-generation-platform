<template>
  <div class="admin-users">
    <h1 class="title">用户管理</h1>

    <div v-if="loading" class="hint">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="user-list">
      <div v-for="u in users" :key="u.id" class="user-card">
        <div class="user-main">
          <div class="user-name">
            {{ u.username }}
            <span v-if="u.role === 'admin'" class="badge admin">Admin</span>
          </div>

          <div class="user-meta">
            <div>ID：{{ u.id }}</div>
            <div>额度：{{ u.quota }}</div>
          </div>

          <div class="meta">
            状态：
            <span :class="u.is_active ? 'active' : 'inactive'">
              {{ u.is_active ? '启用' : '禁用' }}
            </span>
          </div>
        </div>

        <div class="actions">
          <button class="btn primary" @click="openGrant(u)">充值</button>
          <button class="btn" @click="openPlan(u)">绑定套餐</button>
        </div>
      </div>
    </div>

    <!-- 充值弹窗 -->
    <div v-if="grantVisible" class="modal-mask" @click.self="closeGrant">
      <div class="modal-card">
        <h3>人工充值</h3>
        <p class="modal-user">用户：{{ currentUser?.username }}</p>

        <input
          v-model.number="grantQuota"
          type="number"
          min="1"
          placeholder="输入充值额度"
        />

        <div class="modal-actions">
          <button class="btn primary" @click="submitGrant">确认充值</button>
          <button class="btn ghost" @click="closeGrant">取消</button>
        </div>

        <p v-if="grantError" class="error">{{ grantError }}</p>
      </div>
    </div>

    <!-- 套餐绑定弹窗 -->
    <div v-if="planVisible" class="modal-mask" @click.self="closePlan">
      <div class="modal-card">
        <h3>绑定套餐</h3>
        <p class="modal-user">用户：{{ currentUser?.username }}</p>

        <select v-model="selectedPlanId">
          <option value="">请选择套餐</option>
          <option
            v-for="p in plans"
            :key="p.id"
            :value="p.id"
            :disabled="!p.is_active"
          >
            {{ p.name }}（{{ p.quota }} 次，￥{{ p.price }}）
          </option>
        </select>

        <div class="modal-actions">
          <button
            class="btn primary"
            :disabled="!selectedPlanId"
            @click="submitPlan"
          >
            绑定套餐
          </button>
          <button class="btn ghost" @click="closePlan">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'

import {
  fetchAdminUsers,
  fetchAdminPlans,
  grantUserQuota,
  applyUserPlan,
} from '@/api'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const users = ref([])
const plans = ref([])
const loading = ref(false)
const error = ref('')

/* =========================
   获取用户列表
========================= */
const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    users.value = await fetchAdminUsers()
/*    users.value = data  */
  } catch (e) {
    console.error(e)
    error.value = '获取用户列表失败'
  } finally {
    loading.value = false
  }
}

/* =========================
   获取套餐列表
========================= */
const fetchPlans = async () => {
  try {
    plans.value = await fetchAdminPlans()
/*    plans.value = data  */
  } catch (e) {
    console.error('获取套餐失败', e)
  }
}

/* =========================
   充值逻辑
========================= */
const grantVisible = ref(false)
const currentUser = ref(null)
const grantQuota = ref(1)
const grantError = ref('')

const openGrant = (u) => {
  currentUser.value = u
  grantQuota.value = 1
  grantError.value = ''
  grantVisible.value = true
}

const closeGrant = () => {
  grantVisible.value = false
}

const submitGrant = async () => {
  if (grantQuota.value <= 0) {
    grantError.value = '额度必须大于 0'
    return
  }

  try {
    await grantUserQuota(
      currentUser.value.id,
      grantQuota.value
    )

    closeGrant()
    fetchUsers()
  } catch (e) {
    console.error(e)
    grantError.value = '充值失败'
  }
}

/* =========================
   套餐绑定逻辑
========================= */
const planVisible = ref(false)
const selectedPlanId = ref('')

const openPlan = (u) => {
  currentUser.value = u
  selectedPlanId.value = ''
  planVisible.value = true
}

const closePlan = () => {
  planVisible.value = false
}

const submitPlan = async () => {
  if (!selectedPlanId.value) return

  try {
    await applyUserPlan(
      currentUser.value.id,
      selectedPlanId.value
    )

    closePlan()
    fetchUsers()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchUsers()
  fetchPlans()
})
</script>

<style scoped>
.admin-users {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px;
}

.title {
  font-size: 32px;
  margin-bottom: 16px;
}

.hint {
  text-align: center;
  color: #666;
}

.error {
  color: red;
  text-align: center;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.user-name {
  font-weight: bold;
  font-size: 18px;
}

.tag.admin {
  background: #111827;
  color: #fff;
  font-size: 12px;
  padding: 2px 6px;
  margin-left: 6px;
  border-radius: 4px;
}

.user-meta {
  font-size: 14px;
  color: #555;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.primary {
  background: #2563eb;
  color: #fff;
}

.ok {
  color: #16a34a;
}

/* =========================
   Modal
========================= */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  width: 90%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-user {
  font-size: 14px;
  color: #555;
}

.modal-card input,
.modal-card select {
  padding: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* =========================
   PC 适配
========================= */
@media (min-width: 640px) {
  .user-card {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .user-main {
    flex: 1;
  }
}
</style>
