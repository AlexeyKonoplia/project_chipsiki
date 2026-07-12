<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import StarRating from '../components/StarRating.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })

const user = ref(null)
const reviews = ref([])
const loading = ref(true)
const notFound = ref(false)
const q = ref('')
const categoryId = ref('')

function formatDate(s) {
  return new Date(s).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Categories present among this user's reviewed products (for the filter).
const categoryOptions = computed(() => {
  const map = new Map()
  for (const r of reviews.value) {
    for (const c of r.product.categories || []) map.set(c.id, c.name)
  }
  return [...map.entries()]
    .map(([id, name]) => ({ id, name }))
    .sort((a, b) => a.name.localeCompare(b.name, 'ru'))
})

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  const cat = categoryId.value ? Number(categoryId.value) : null
  return reviews.value.filter((r) => {
    if (cat && !(r.product.categories || []).some((c) => c.id === cat)) return false
    if (term) {
      const hay = `${r.product.name} ${r.text || ''}`.toLowerCase()
      if (!hay.includes(term)) return false
    }
    return true
  })
})

async function load() {
  loading.value = true
  notFound.value = false
  q.value = ''
  categoryId.value = ''
  try {
    const [u, r] = await Promise.all([
      api.get(`/api/users/${props.id}`),
      api.get('/api/reviews', { params: { author_id: props.id } }),
    ])
    user.value = u.data
    reviews.value = r.data
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

    <div v-if="reviews.length" class="toolbar" style="margin: 12px 0 16px">
      <input
        v-model="q"
        placeholder="Поиск по товару или тексту…"
        style="max-width: 280px"
      />
      <select v-model="categoryId" style="max-width: 240px">
        <option value="">Все категории</option>
        <option v-for="c in categoryOptions" :key="c.id" :value="c.id">
          {{ c.name }}
        </option>
      </select>
    </div>

    <p v-if="reviews.length === 0" class="muted">Пользователь ещё не оставил отзывов.</p>
    <p v-else-if="filtered.length === 0" class="muted">
      Под фильтр ничего не подходит.
    </p>
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
  </template>
</template>

<style scoped>
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
</style>
