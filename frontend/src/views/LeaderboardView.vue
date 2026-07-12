<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import StarRating from '../components/StarRating.vue'

const rows = ref([])
const tree = ref([])
const loading = ref(true)
const q = ref('')
const categoryId = ref('')

let timer = null

async function load() {
  loading.value = true
  try {
    const params = {}
    if (q.value.trim()) params.q = q.value.trim()
    if (categoryId.value) params.category_id = categoryId.value
    const { data } = await api.get('/api/users/leaderboard', { params })
    rows.value = data
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(load, 250)
}

onMounted(async () => {
  const { data } = await api.get('/api/categories/tree')
  tree.value = data
  await load()
})
</script>

<template>
  <div class="toolbar">
    <h1 class="title" style="margin: 0; flex: 1">Таблица лидеров</h1>
  </div>
  <p class="muted" style="margin-top: -6px">
    Самые активные авторы отзывов. Нажмите на имя, чтобы посмотреть его отзывы.
  </p>

  <div class="toolbar" style="margin: 14px 0 18px">
    <input
      v-model="q"
      placeholder="Поиск по имени…"
      style="max-width: 280px"
      @input="onSearch"
    />
    <select v-model="categoryId" style="max-width: 260px" @change="load">
      <option value="">Все категории</option>
      <template v-for="s in tree" :key="s.id">
        <option :value="s.id">{{ s.name }}</option>
        <option v-for="c in s.children" :key="c.id" :value="c.id">
          &nbsp;&nbsp;— {{ c.name }}
        </option>
      </template>
    </select>
  </div>

  <p v-if="loading" class="muted">Загрузка…</p>
  <p v-else-if="rows.length === 0" class="muted">
    Пока нет отзывов, подходящих под фильтр.
  </p>
  <div v-else class="lb">
    <div
      v-for="(u, i) in rows"
      :key="u.id"
      class="lb-row card"
      :class="{ top: i < 3 }"
    >
      <span class="lb-rank" :class="[`r${i + 1}`]">{{ i + 1 }}</span>
      <router-link :to="{ name: 'user', params: { id: u.id } }" class="lb-name">
        {{ u.username }}
        <span v-if="u.is_admin" class="badge" style="vertical-align: middle">админ</span>
      </router-link>
      <span class="lb-rating muted">
        <StarRating v-if="u.average_rating" :model-value="u.average_rating" />
        <span v-if="u.average_rating">{{ u.average_rating.toFixed(1) }}</span>
      </span>
      <span class="lb-count">
        <strong>{{ u.review_count }}</strong>
        <span class="muted">&nbsp;отз.</span>
      </span>
    </div>
  </div>
</template>

<style scoped>
.lb {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.lb-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
}
.lb-row.top {
  border-color: rgba(232, 176, 75, 0.35);
}
.lb-rank {
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 700;
  font-size: 14px;
  color: var(--muted);
  background: var(--card-2);
}
.lb-rank.r1 {
  color: var(--primary-contrast);
  background: var(--primary);
}
.lb-rank.r2,
.lb-rank.r3 {
  color: var(--primary);
  background: rgba(232, 176, 75, 0.14);
}
.lb-name {
  flex: 1;
  color: var(--text);
  font-weight: 500;
}
.lb-name:hover {
  color: var(--primary);
}
.lb-rating {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.lb-count {
  flex: 0 0 auto;
  min-width: 74px;
  text-align: right;
}

@media (max-width: 560px) {
  .lb-rating {
    display: none;
  }
}
</style>
