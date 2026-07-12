<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import StarRating from '../components/StarRating.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })

const user = ref(null)
const reviews = ref([])
const tree = ref([])
const loading = ref(true)
const notFound = ref(false)
const q = ref('')
const categoryId = ref(null)
const expandedId = ref(null)
const sort = ref('new') // new | rating
const order = ref('desc')

function formatDate(s) {
  return new Date(s).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Category ids that appear among this user's reviewed products.
const usedCatIds = computed(() => {
  const s = new Set()
  for (const r of reviews.value) {
    for (const c of r.product.categories || []) s.add(c.id)
  }
  return s
})

// Sidebar: only sections/subcategories the user actually has reviews in.
// A section stays visible if it or any of its children were reviewed.
const sidebarSections = computed(() => {
  const result = []
  for (const s of tree.value) {
    const usedChildren = s.children.filter((c) => usedCatIds.value.has(c.id))
    if (usedChildren.length || usedCatIds.value.has(s.id)) {
      result.push({ id: s.id, name: s.name, children: s.children, usedChildren })
    }
  }
  return result
})

// Ids the current selection matches. Selecting a section includes all of
// its subcategories, so e.g. "Пиво" shows under "Алкогольные напитки".
const matchIds = computed(() => {
  if (!categoryId.value) return null
  const section = tree.value.find((s) => s.id === categoryId.value)
  if (section) return new Set([section.id, ...section.children.map((c) => c.id)])
  return new Set([categoryId.value])
})

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  let list = reviews.value.filter((r) => {
    if (matchIds.value && !(r.product.categories || []).some((c) => matchIds.value.has(c.id)))
      return false
    if (term) {
      const hay = `${r.product.name} ${r.text || ''}`.toLowerCase()
      if (!hay.includes(term)) return false
    }
    return true
  })
  const dir = order.value === 'asc' ? 1 : -1
  return [...list].sort((a, b) => {
    if (sort.value === 'rating' && a.rating !== b.rating) {
      return (a.rating - b.rating) * dir
    }
    return (new Date(a.created_at) - new Date(b.created_at)) * dir
  })
})

function pickAll() {
  categoryId.value = null
  expandedId.value = null
}
function pickSection(s) {
  expandedId.value = expandedId.value === s.id && categoryId.value === s.id ? null : s.id
  categoryId.value = s.id
}
function pickChild(c) {
  categoryId.value = c.id
}
function toggleOrder() {
  order.value = order.value === 'desc' ? 'asc' : 'desc'
}

async function load() {
  loading.value = true
  notFound.value = false
  q.value = ''
  categoryId.value = null
  expandedId.value = null
  sort.value = 'new'
  order.value = 'desc'
  try {
    const [u, r, t] = await Promise.all([
      api.get(`/api/users/${props.id}`),
      api.get('/api/reviews', { params: { author_id: props.id } }),
      api.get('/api/categories/tree'),
    ])
    user.value = u.data
    reviews.value = r.data
    tree.value = t.data
  } catch (e) {
    if (e.response?.status === 404) notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <p v-if="loading" class="muted">Загрузка…</p>
  <p v-else-if="notFound" class="muted">Пользователь не найден.</p>

  <template v-else>
    <router-link to="/" class="muted">← Ко всем товарам</router-link>
    <h1 class="title" style="margin-top: 12px">
      {{ user.username }}
      <span v-if="user.is_admin" class="badge" style="vertical-align: middle">админ</span>
    </h1>
    <p class="muted" style="margin-top: -8px">Отзывов: {{ reviews.length }}</p>

    <p v-if="reviews.length === 0" class="muted" style="margin-top: 16px">
      Пользователь ещё не оставил отзывов.
    </p>

    <div v-else class="home-layout" style="margin-top: 16px">
      <!-- Category sidebar (same format as the main page) -->
      <aside class="cat-side">
        <button class="cat-link" :class="{ active: !categoryId }" @click="pickAll">
          Все отзывы
        </button>
        <div v-for="s in sidebarSections" :key="s.id">
          <button
            class="cat-link"
            :class="{ active: categoryId === s.id }"
            @click="pickSection(s)"
          >
            <span>{{ s.name }}</span>
            <span
              v-if="s.usedChildren.length"
              class="cat-arrow"
              :class="{ open: expandedId === s.id }"
            >
              ›
            </span>
          </button>
          <div v-if="expandedId === s.id && s.usedChildren.length" class="cat-children">
            <button
              v-for="c in s.usedChildren"
              :key="c.id"
              class="cat-link child"
              :class="{ active: categoryId === c.id }"
              @click="pickChild(c)"
            >
              {{ c.name }}
            </button>
          </div>
        </div>
      </aside>

      <!-- Reviews -->
      <div class="home-main">
        <div class="toolbar" style="margin-bottom: 16px">
          <input
            v-model="q"
            placeholder="Поиск по товару или тексту…"
            style="max-width: 300px"
          />
          <div class="row" style="gap: 6px; margin-left: auto">
            <select v-model="sort" style="max-width: 170px">
              <option value="new">По дате</option>
              <option value="rating">По оценке</option>
            </select>
            <button
              class="btn secondary order-btn"
              :title="order === 'desc' ? 'По убыванию — нажмите для сортировки по возрастанию' : 'По возрастанию — нажмите для сортировки по убыванию'"
              @click="toggleOrder"
            >
              {{ order === 'desc' ? '↓' : '↑' }}
            </button>
          </div>
        </div>

        <p v-if="filtered.length === 0" class="muted">Под фильтр ничего не подходит.</p>
        <div v-else style="display: flex; flex-direction: column; gap: 12px">
          <div v-for="r in filtered" :key="r.id" class="card">
            <div class="row" style="justify-content: space-between; align-items: flex-start">
              <router-link
                :to="{ name: 'product', params: { id: r.product.id } }"
                class="row"
                style="gap: 10px; color: inherit"
              >
                <span class="ac-thumb-mini">
                  <img v-if="r.product.image_url" :src="r.product.image_url" :alt="r.product.name" />
                  <span v-else class="icon-img sm"></span>
                </span>
                <span>
                  <strong>{{ r.product.name }}</strong>
                  <br />
                  <StarRating :model-value="r.rating" />
                </span>
              </router-link>
              <span class="muted">{{ formatDate(r.created_at) }}</span>
            </div>
            <p v-if="r.text" style="margin: 8px 0 0">{{ r.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<style scoped>
.home-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 22px;
  align-items: start;
}
.cat-side {
  position: sticky;
  top: 76px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 8px;
}
.cat-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: var(--muted);
  font-family: inherit;
  font-size: 14px;
  padding: 7px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.cat-link:hover {
  color: var(--text);
  background: var(--card-2);
}
.cat-link.active {
  color: var(--primary);
  background: rgba(232, 176, 75, 0.1);
}
.cat-link.child {
  font-size: 13px;
  padding-left: 22px;
}
.cat-arrow {
  color: var(--muted);
  transition: transform 0.15s;
  font-size: 16px;
  line-height: 1;
}
.cat-arrow.open {
  transform: rotate(90deg);
}
.cat-children {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 2px;
}
.order-btn {
  padding: 10px 13px;
  font-size: 16px;
  line-height: 1;
}
.ac-thumb-mini {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: var(--bg-2);
  border: 1px solid var(--border);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex: 0 0 auto;
}
.ac-thumb-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 720px) {
  .home-layout {
    grid-template-columns: 1fr;
  }
  .cat-side {
    position: static;
  }
}
</style>
