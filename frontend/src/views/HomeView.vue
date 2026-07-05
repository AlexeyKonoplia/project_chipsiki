<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../store/auth'
import ProductCard from '../components/ProductCard.vue'

const auth = useAuthStore()
const canWrite = computed(
  () => !!auth.user && (auth.user.is_admin || auth.user.is_approved)
)

const products = ref([])
const catTree = ref([])
const loading = ref(true)
const q = ref('')
const categoryId = ref(null)
const expandedId = ref(null) // which section is unfolded in the sidebar

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

function pickAll() {
  categoryId.value = null
  expandedId.value = null
  load()
}

function pickSection(s) {
  // Clicking a section filters by it (subcategories included) and unfolds it.
  expandedId.value = expandedId.value === s.id && categoryId.value === s.id ? null : s.id
  categoryId.value = s.id
  load()
}

function pickChild(c) {
  categoryId.value = c.id
  load()
}

onMounted(async () => {
  const { data } = await api.get('/api/categories/tree')
  catTree.value = data
  await load()
})
</script>

<template>
  <div class="toolbar">
    <h1 class="title" style="margin: 0; flex: 1">Товары</h1>
    <router-link v-if="canWrite" class="btn" to="/new-product">+ Добавить товар</router-link>
  </div>

  <div class="home-layout">
    <!-- Category sidebar -->
    <aside class="cat-side">
      <button class="cat-link" :class="{ active: !categoryId }" @click="pickAll">
        Все категории
      </button>
      <div v-for="s in catTree" :key="s.id">
        <button
          class="cat-link"
          :class="{ active: categoryId === s.id }"
          @click="pickSection(s)"
        >
          <span>{{ s.name }}</span>
          <span v-if="s.children.length" class="cat-arrow" :class="{ open: expandedId === s.id }">
            ›
          </span>
        </button>
        <div v-if="expandedId === s.id && s.children.length" class="cat-children">
          <button
            v-for="c in s.children"
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

    <!-- Products -->
    <div class="home-main">
      <div class="toolbar" style="margin-bottom: 16px">
        <input
          v-model="q"
          placeholder="Поиск: название, категория или тег…"
          style="max-width: 340px"
          @keyup.enter="load"
        />
        <button class="btn secondary" @click="load">Найти</button>
      </div>

      <p v-if="loading" class="muted">Загрузка…</p>
      <p v-else-if="products.length === 0" class="muted">
        Ничего не найдено.
        <template v-if="canWrite">
          Будьте первым — <router-link to="/new-product">добавьте товар</router-link>.
        </template>
      </p>
      <div v-else class="grid">
        <ProductCard v-for="p in products" :key="p.id" :product="p" />
      </div>
    </div>
  </div>
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

@media (max-width: 720px) {
  .home-layout {
    grid-template-columns: 1fr;
  }
  .cat-side {
    position: static;
  }
}
</style>
