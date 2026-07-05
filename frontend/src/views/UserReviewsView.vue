<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import StarRating from '../components/StarRating.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })

const user = ref(null)
const reviews = ref([])
const loading = ref(true)
const notFound = ref(false)

function formatDate(s) {
  return new Date(s).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function load() {
  loading.value = true
  notFound.value = false
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

    <p v-if="reviews.length === 0" class="muted">Пользователь ещё не оставил отзывов.</p>
    <div v-else style="display: flex; flex-direction: column; gap: 12px">
      <div v-for="r in reviews" :key="r.id" class="card">
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
