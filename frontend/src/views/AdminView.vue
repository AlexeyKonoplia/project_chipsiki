<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const users = ref([])
const loading = ref(true)
const error = ref('')

// Inline username editing
const editingId = ref(null)
const editName = ref('')
const savingName = ref(false)

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

function startRename(user) {
  editingId.value = user.id
  editName.value = user.username
}
function cancelRename() {
  editingId.value = null
}
// ---------- Category tree management ----------
const catTree = ref([])
const newSection = ref('')
const newChild = ref({}) // section id -> draft subcategory name

async function loadTree() {
  const { data } = await api.get('/api/categories/tree')
  catTree.value = data
}

async function addSection() {
  const name = newSection.value.trim()
  if (!name) return
  try {
    await api.post('/api/categories', { name })
    newSection.value = ''
    await loadTree()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось создать раздел')
  }
}

async function addChild(section) {
  const name = (newChild.value[section.id] || '').trim()
  if (!name) return
  try {
    await api.post('/api/categories', { name, parent_id: section.id })
    newChild.value[section.id] = ''
    await loadTree()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось создать подкатегорию')
  }
}

async function renameCat(cat) {
  const name = prompt('Новое название категории:', cat.name)
  if (!name || !name.trim() || name.trim() === cat.name) return
  try {
    await api.patch(`/api/categories/${cat.id}`, { name: name.trim() })
    await loadTree()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось переименовать категорию')
  }
}

async function removeCat(cat, isSection) {
  const warn = isSection
    ? `Удалить раздел «${cat.name}» вместе со всеми его подкатегориями?`
    : `Удалить категорию «${cat.name}»?`
  if (!confirm(warn + ' Она будет снята со всех товаров.')) return
  try {
    await api.delete(`/api/categories/${cat.id}`)
    await loadTree()
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось удалить категорию')
  }
}

async function saveRename(user) {
  const name = editName.value.trim()
  if (name.length < 3) {
    alert('Имя пользователя должно быть не короче 3 символов')
    return
  }
  if (name === user.username) {
    editingId.value = null
    return
  }
  savingName.value = true
  try {
    const { data } = await api.patch(`/api/admin/users/${user.id}`, { username: name })
    Object.assign(user, data)
    // Keep the current session's displayed name in sync if we renamed ourselves.
    if (user.id === auth.user?.id) auth.user.username = data.username
    editingId.value = null
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось изменить имя')
  } finally {
    savingName.value = false
  }
}

onMounted(() => {
  load()
  loadTree()
})
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
          <th style="text-align: right">Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>
            <template v-if="editingId === u.id">
              <div class="row" style="gap: 6px">
                <input
                  v-model="editName"
                  style="max-width: 180px"
                  @keyup.enter.prevent="saveRename(u)"
                  @keyup.esc="cancelRename"
                />
              </div>
            </template>
            <template v-else>
              <strong>{{ u.username }}</strong>
              <span v-if="u.id === auth.user?.id" class="muted"> (вы)</span>
            </template>
          </td>
          <td class="muted">{{ u.email }}</td>
          <td>
            <span class="badge" :class="{ admin: u.is_admin }">
              {{ u.is_admin ? 'Админ' : 'Пользователь' }}
            </span>
          </td>
          <td style="text-align: right">
            <div class="row" style="gap: 8px; justify-content: flex-end; flex-wrap: wrap">
              <template v-if="editingId === u.id">
                <button class="btn" :disabled="savingName" @click="saveRename(u)">
                  {{ savingName ? '…' : 'Сохранить' }}
                </button>
                <button class="btn secondary" @click="cancelRename">Отмена</button>
              </template>
              <template v-else>
                <button class="btn secondary" @click="startRename(u)">Переименовать</button>
                <button
                  class="btn secondary"
                  :disabled="u.id === auth.user?.id && u.is_admin"
                  @click="toggle(u)"
                >
                  {{ u.is_admin ? 'Снять админа' : 'Сделать админом' }}
                </button>
              </template>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2 style="margin: 28px 0 6px">Категории</h2>
  <p class="muted" style="margin: 0 0 14px">
    Разделы и подкатегории, которые пользователи выбирают при создании карточки товара.
  </p>

  <div class="row" style="margin-bottom: 14px">
    <input
      v-model="newSection"
      placeholder="Новый раздел…"
      style="max-width: 240px"
      @keyup.enter="addSection"
    />
    <button class="btn secondary" @click="addSection">Добавить раздел</button>
  </div>

  <div style="display: flex; flex-direction: column; gap: 12px">
    <div v-for="s in catTree" :key="s.id" class="card">
      <div class="row" style="justify-content: space-between; flex-wrap: wrap">
        <strong>{{ s.name }}</strong>
        <div class="row" style="gap: 8px">
          <button class="btn secondary cat-btn" @click="renameCat(s)">Переименовать</button>
          <button class="btn danger cat-btn" @click="removeCat(s, true)">Удалить</button>
        </div>
      </div>

      <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px">
        <span v-for="c in s.children" :key="c.id" class="badge cat-item">
          {{ c.name }}
          <button class="cat-x" title="Переименовать" @click="renameCat(c)">✎</button>
          <button class="cat-x" title="Удалить" @click="removeCat(c, false)">✕</button>
        </span>
        <span v-if="s.children.length === 0" class="muted" style="font-size: 13px">
          Нет подкатегорий
        </span>
      </div>

      <div class="row" style="margin-top: 10px">
        <input
          v-model="newChild[s.id]"
          placeholder="Новая подкатегория…"
          style="max-width: 220px"
          @keyup.enter="addChild(s)"
        />
        <button class="btn secondary cat-btn" @click="addChild(s)">Добавить</button>
      </div>
    </div>
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
  background: rgba(232, 176, 75, 0.14);
  color: var(--primary);
  border-color: rgba(232, 176, 75, 0.4);
}
.cat-btn {
  padding: 5px 12px;
  font-size: 13px;
}
.cat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.cat-x {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 12px;
  padding: 0 2px;
  line-height: 1;
}
.cat-x:hover {
  color: var(--primary);
}
</style>
