<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const users = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/admin/users')
    users.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить пользователей'
  } finally {
    loading.value = false
  }
}

async function toggle(user) {
  const next = !user.is_admin
  try {
    const { data } = await api.patch(`/api/admin/users/${user.id}`, { is_admin: next })
    Object.assign(user, data)
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось изменить права')
  }
}

onMounted(load)
</script>

<template>
  <h1 class="title">Администрирование</h1>
  <p class="muted" style="margin-top: -8px">
    Управление правами администраторов. Администраторы могут удалять любые товары.
  </p>

  <div v-if="error" class="error">{{ error }}</div>
  <p v-if="loading" class="muted">Загрузка…</p>

  <div v-else class="card" style="padding: 0; overflow: hidden">
    <table class="admin-table">
      <thead>
        <tr>
          <th>Пользователь</th>
          <th>Email</th>
          <th>Роль</th>
          <th style="text-align: right">Действие</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>
            <strong>{{ u.username }}</strong>
            <span v-if="u.id === auth.user?.id" class="muted"> (вы)</span>
          </td>
          <td class="muted">{{ u.email }}</td>
          <td>
            <span class="badge" :class="{ admin: u.is_admin }">
              {{ u.is_admin ? 'Админ' : 'Пользователь' }}
            </span>
          </td>
          <td style="text-align: right">
            <button
              class="btn secondary"
              :disabled="u.id === auth.user?.id && u.is_admin"
              @click="toggle(u)"
            >
              {{ u.is_admin ? 'Снять админа' : 'Сделать админом' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.admin-table th {
  text-align: left;
  color: var(--muted);
  font-weight: 500;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}
.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}
.admin-table tr:last-child td {
  border-bottom: none;
}
.badge.admin {
  background: rgba(0, 229, 192, 0.16);
  color: var(--accent);
  border-color: rgba(0, 229, 192, 0.3);
}
</style>
