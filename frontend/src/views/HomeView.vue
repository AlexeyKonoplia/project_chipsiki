<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const products = ref([])
const categories = ref([])
const loading = ref(true)
const q = ref('')
const categoryId = ref('')

async function load() {
  loading.value = true
  try {
    const params = {}
    if (q.value.trim()) params.q = q.value.trim()
    if (categoryId.value) params.category_id = categoryId.value
    const { data } = await api.get('/api/products', { params })
    products.value = data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/api/categories')
  categories.value = data
  await load()
})
</script>

<template>
  <div class="toolbar">
    <h1 class="title" style="margin: 0; flex: 1">Товары</h1>
    <router-link class="btn" to="/new-product">+ Добавить товар</router-link>
  </div>

  <div class="toolbar">
    <input
      v-model="q"
      placeholder="Поиск по названию…"
      style="max-width: 280px"
      @keyup.enter="load"
    />
    <select v-model="categoryId" style="max-width: 220px" @change="load">
      <option value="">Все категории</option>
      <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
    </select>
    <button class="btn secondary" @click="load">Найти</button>
  </div>

  <p v-if="loading" class="muted">Загрузка…</p>
  <p v-else-if="products.length === 0" class="muted">
    Товаров пока нет. Будьте первым — <router-link to="/new-product">добавьте товар</router-link>.
  </p>
  <div v-else class="grid">
    <ProductCard v-for="p in products" :key="p.id" :product="p" />
  </div>
</template>
