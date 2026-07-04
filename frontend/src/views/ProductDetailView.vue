<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../store/auth'
import StarRating from '../components/StarRating.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const auth = useAuthStore()
const router = useRouter()

const product = ref(null)
const reviews = ref([])
const loading = ref(true)
const notFound = ref(false)
const deleting = ref(false)

const canDelete = computed(
  () =>
    product.value &&
    auth.user &&
    (auth.user.is_admin || auth.user.id === product.value.owner.id)
)

function formatDate(s) {
  return new Date(s).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function removeProduct() {
  if (!confirm(`Удалить товар «${product.value.name}» вместе со всеми отзывами?`)) return
  deleting.value = true
  try {
    await api.delete(`/api/products/${product.value.id}`)
    router.push({ name: 'home' })
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось удалить товар')
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/api/products/${props.id}`)
    product.value = data
    const res = await api.get('/api/reviews', { params: { product_id: props.id } })
    reviews.value = res.data
  } catch (e) {
    if (e.response?.status === 404) notFound.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <p v-if="loading" class="muted">Загрузка…</p>
  <p v-else-if="notFound" class="muted">Товар не найден.</p>

  <template v-else>
    <router-link to="/" class="muted">← Ко всем товарам</router-link>

    <div class="card" style="margin-top: 12px">
      <div style="display: flex; gap: 20px; flex-wrap: wrap">
        <div style="flex: 0 0 240px">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="product-img" style="height: 220px" />
          <div v-else class="product-img placeholder" style="height: 220px">📦</div>
        </div>
        <div style="flex: 1; min-width: 240px">
          <h1 class="title" style="margin-bottom: 8px">{{ product.name }}</h1>
          <div class="row" style="margin-bottom: 10px">
            <StarRating :model-value="product.average_rating || 0" style="font-size: 22px" />
            <span class="muted">
              {{ product.average_rating ? product.average_rating.toFixed(1) : 'нет оценок' }}
              · {{ product.review_count }} отзыв(ов)
            </span>
          </div>
          <div style="margin-bottom: 10px">
            <span v-for="c in product.categories" :key="c.id" class="badge">{{ c.name }}</span>
          </div>
          <p v-if="product.description">{{ product.description }}</p>
          <p class="muted">Добавил: {{ product.owner.username }} · {{ formatDate(product.created_at) }}</p>
          <div class="row" style="gap: 10px">
            <router-link class="btn" :to="{ name: 'new-review', query: { product_id: product.id } }">
              Оставить отзыв
            </router-link>
            <button v-if="canDelete" class="btn danger" :disabled="deleting" @click="removeProduct">
              {{ deleting ? 'Удаление…' : '🗑 Удалить товар' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <h2 style="margin: 24px 0 12px">Отзывы</h2>
    <p v-if="reviews.length === 0" class="muted">Пока нет отзывов. Будьте первым!</p>
    <div v-else style="display: flex; flex-direction: column; gap: 12px">
      <div v-for="r in reviews" :key="r.id" class="card">
        <div class="row" style="justify-content: space-between">
          <div class="row">
            <strong>{{ r.author.username }}</strong>
            <StarRating :model-value="r.rating" />
          </div>
          <span class="muted">{{ formatDate(r.created_at) }}</span>
        </div>
        <p v-if="r.text" style="margin: 8px 0 0">{{ r.text }}</p>
      </div>
    </div>
  </template>
</template>
