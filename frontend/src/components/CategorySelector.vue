<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

// v-model is an array of selected category ids.
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const categories = ref([])
const search = ref('')
const adding = ref(false)

onMounted(async () => {
  const { data } = await api.get('/api/categories')
  categories.value = data
})

const selected = computed(() =>
  categories.value.filter((c) => props.modelValue.includes(c.id))
)

// Categories matching the search box, excluding those already selected.
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return categories.value.filter(
    (c) => !props.modelValue.includes(c.id) && (!q || c.name.toLowerCase().includes(q))
  )
})

// Offer to create a new category when the query doesn't match any name exactly.
const canCreate = computed(() => {
  const q = search.value.trim()
  if (!q) return false
  return !categories.value.some((c) => c.name.toLowerCase() === q.toLowerCase())
})

function toggle(id) {
  const set = new Set(props.modelValue)
  set.has(id) ? set.delete(id) : set.add(id)
  emit('update:modelValue', [...set])
}

async function addCategory() {
  const name = search.value.trim()
  if (!name) return
  adding.value = true
  try {
    const { data } = await api.post('/api/categories', { name })
    if (!categories.value.find((c) => c.id === data.id)) {
      categories.value.push(data)
    }
    if (!props.modelValue.includes(data.id)) {
      emit('update:modelValue', [...props.modelValue, data.id])
    }
    search.value = ''
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось создать категорию')
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <div>
    <!-- Currently selected categories (always visible, click to remove) -->
    <div
      v-if="selected.length"
      style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px"
    >
      <span
        v-for="c in selected"
        :key="c.id"
        class="badge selected"
        @click="toggle(c.id)"
      >
        {{ c.name }} ✕
      </span>
    </div>

    <!-- Search / add box -->
    <div class="row" style="margin-bottom: 8px">
      <input
        v-model="search"
        placeholder="Поиск категории…"
        style="max-width: 260px"
        @keyup.enter.prevent="canCreate && addCategory()"
      />
      <button
        v-if="canCreate"
        type="button"
        class="btn secondary"
        :disabled="adding"
        @click="addCategory"
      >
        + Добавить «{{ search.trim() }}»
      </button>
    </div>

    <!-- Matching categories to pick from -->
    <div style="display: flex; flex-wrap: wrap; gap: 6px">
      <span
        v-for="c in filtered"
        :key="c.id"
        class="badge pickable"
        @click="toggle(c.id)"
      >
        {{ c.name }}
      </span>
      <span v-if="filtered.length === 0 && !canCreate" class="muted">
        {{ categories.length === 0 ? 'Категорий пока нет — введите название и добавьте.' : 'Ничего не найдено.' }}
      </span>
    </div>
  </div>
</template>
