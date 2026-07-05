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
const sort = ref('new')
const order = ref('desc')

function toggleOrder() {
  order.value = order.value === 'desc' ? 'asc' : 'desc'
  load()
}

// Age-gated sections: their products are excluded from the general
// listing and the section opens only after the 18+ confirmation.
const ADULT_SECTIONS = ['алкогольные напитки', 'табак']
const AGE_KEY = 'age_confirmed'

// The last category the user was browsing, restored when they come back
// to the listing (e.g. via "Ко всем товарам"). 'all' = explicit "no filter".
const LAST_CAT_KEY = 'last_category_id'

function rememberCategory() {
  localStorage.setItem(
    LAST_CAT_KEY,
    categoryId.value === null ? 'all' : String(categoryId.value)
  )
}

// The signature category of the site (the service is named after it).
// It is pinned on top of the sidebar and pre-selected on page load.
const brandCat = ref(null)

function findBrandCategory(tree) {
  const all = []
  for (const s of tree) {
    all.push(s, ...s.children)
  }
  return (
    all.find((c) => c.name.toLowerCase() === 'чипсы и снеки') ||
    all.find((c) => c.name.toLowerCase().includes('чипс')) ||
    null
  )
}
const isAdult = (s) => ADULT_SECTIONS.includes(s.name.toLowerCase())

const ageModal = ref(false)
const pendingSection = ref(null)

// "+ Добавить товар" carries the current category so the creation form
// pre-selects it.
const newProductRoute = computed(() => ({
  path: '/new-product',
  query: categoryId.value ? { category_id: categoryId.value } : {},
}))

async function load() {
  loading.value = true
  try {
    const params = { sort: sort.value, order: order.value }
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
  rememberCategory()
  load()
}

function applySection(s) {
  // Clicking a section filters by it (subcategories included) and unfolds it.
  expandedId.value = expandedId.value === s.id && categoryId.value === s.id ? null : s.id
  categoryId.value = s.id
  rememberCategory()
  load()
}

function pickSection(s) {
  if (isAdult(s) && localStorage.getItem(AGE_KEY) !== '1') {
    pendingSection.value = s
    ageModal.value = true
    return
  }
  applySection(s)
}

function confirmAge() {
  localStorage.setItem(AGE_KEY, '1')
  ageModal.value = false
  const s = pendingSection.value
  pendingSection.value = null
  if (s) applySection(s)
}

function declineAge() {
  ageModal.value = false
  pendingSection.value = null
}

function pickChild(c) {
  categoryId.value = c.id
  rememberCategory()
  load()
}

onMounted(async () => {
  const { data } = await api.get('/api/categories/tree')
  catTree.value = data
  brandCat.value = findBrandCategory(data)

  // Restore the last category the user was browsing; fall back to the
  // site's namesake category on the very first visit.
  const stored = localStorage.getItem(LAST_CAT_KEY)
  const all = []
  for (const s of data) all.push(s, ...s.children)
  const storedCat =
    stored && stored !== 'all' ? all.find((c) => c.id === Number(stored)) : null
  if (storedCat) {
    const section = data.find(
      (s) => s.id === storedCat.id || s.children.some((c) => c.id === storedCat.id)
    )
    if (section && isAdult(section) && localStorage.getItem(AGE_KEY) !== '1') {
      // The age confirmation is gone — don't reopen an 18+ section silently.
      if (brandCat.value) categoryId.value = brandCat.value.id
    } else {
      categoryId.value = storedCat.id
      if (section && section.children.length) expandedId.value = section.id
    }
  } else if (stored !== 'all' && brandCat.value) {
    categoryId.value = brandCat.value.id
  }
  await load()
})
</script>

<template>
  <div class="toolbar">
    <h1 class="title" style="margin: 0; flex: 1">Товары</h1>
    <router-link v-if="canWrite" class="btn" :to="newProductRoute">+ Добавить товар</router-link>
  </div>

  <div class="home-layout">
    <!-- Category sidebar -->
    <aside class="cat-side">
      <button
        v-if="brandCat"
        class="cat-link brand"
        :class="{ active: categoryId === brandCat.id }"
        title="Категория, в честь которой назван сайт"
        @click="pickChild(brandCat)"
      >
        <span>{{ brandCat.name }}</span>
        <span class="brand-chip">это мы</span>
      </button>
      <button class="cat-link" :class="{ active: !categoryId }" @click="pickAll">
        Все категории
      </button>
      <div v-for="s in catTree" :key="s.id">
        <button
          class="cat-link"
          :class="{ active: categoryId === s.id }"
          @click="pickSection(s)"
        >
          <span>
            {{ s.name }}
            <span v-if="isAdult(s)" class="age-chip">18+</span>
          </span>
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
        <div class="row" style="gap: 6px; margin-left: auto">
          <select v-model="sort" style="max-width: 190px" @change="load">
            <option value="new">По дате добавления</option>
            <option value="rating">По оценке</option>
            <option value="reviews">По числу отзывов</option>
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

      <p v-if="loading" class="muted">Загрузка…</p>
      <p v-else-if="products.length === 0" class="muted">
        Ничего не найдено.
        <template v-if="canWrite">
          Будьте первым — <router-link :to="newProductRoute">добавьте товар</router-link>.
        </template>
      </p>
      <div v-else class="grid">
        <ProductCard v-for="p in products" :key="p.id" :product="p" />
      </div>
    </div>
  </div>

  <!-- 18+ age gate -->
  <div v-if="ageModal" class="age-overlay" @click.self="declineAge">
    <div class="age-modal card">
      <div class="age-badge">18+</div>
      <h2 style="margin: 12px 0 6px">Раздел для совершеннолетних</h2>
      <p class="muted" style="margin: 0 0 18px">
        Этот раздел содержит товары для совершеннолетних. Вам уже исполнилось 18 лет?
      </p>
      <div class="row" style="justify-content: center">
        <button class="btn" @click="confirmAge">Да, мне есть 18</button>
        <button class="btn secondary" @click="declineAge">Нет</button>
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
.cat-link.brand {
  color: var(--text);
  border: 1px solid rgba(232, 176, 75, 0.35);
  background: rgba(232, 176, 75, 0.06);
  margin-bottom: 4px;
}
.cat-link.brand:hover,
.cat-link.brand.active {
  color: var(--primary);
  border-color: var(--primary);
  background: rgba(232, 176, 75, 0.12);
}
.brand-chip {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--primary-contrast);
  background: var(--primary);
  border-radius: 999px;
  padding: 2px 7px;
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

.age-chip {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  color: var(--danger);
  border: 1px solid rgba(225, 91, 109, 0.5);
  border-radius: 4px;
  padding: 0 4px;
  margin-left: 4px;
  vertical-align: 1px;
}

.age-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.age-modal {
  max-width: 380px;
  width: 100%;
  text-align: center;
  padding: 26px 22px;
}
.age-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid var(--danger);
  color: var(--danger);
  font-weight: 700;
  font-size: 17px;
  margin: 0 auto;
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
