<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

// v-model is an array of selected category ids. The category tree itself is
// fixed — only admins can change it (on the admin page).
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const tree = ref([])
const search = ref('')

onMounted(async () => {
  const { data } = await api.get('/api/categories/tree')
  tree.value = data
})

// id -> category, across the whole tree.
const byId = computed(() => {
  const map = new Map()
  for (const section of tree.value) {
    map.set(section.id, section)
    for (const child of section.children) map.set(child.id, child)
  }
  return map
})

const selected = computed(() =>
  props.modelValue.map((id) => byId.value.get(id)).filter(Boolean)
)

// Sections with their pickable items filtered by the search query.
// A section without subcategories is pickable itself.
const groups = computed(() => {
  const q = search.value.trim().toLowerCase()
  const result = []
  for (const section of tree.value) {
    const items = section.children.length ? section.children : [section]
    const visible = items.filter(
      (c) =>
        !props.modelValue.includes(c.id) &&
        (!q || c.name.toLowerCase().includes(q) || section.name.toLowerCase().includes(q))
    )
    if (visible.length) result.push({ section, items: visible })
  }
  return result
})

function toggle(id) {
  const set = new Set(props.modelValue)
  set.has(id) ? set.delete(id) : set.add(id)
  emit('update:modelValue', [...set])
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

    <!-- Search box -->
    <input
      v-model="search"
      placeholder="Поиск категории…"
      style="max-width: 260px; margin-bottom: 10px"
    />

    <!-- Grouped categories to pick from -->
    <div v-if="groups.length" class="cat-groups">
      <div v-for="g in groups" :key="g.section.id" class="cat-group">
        <div class="cat-group-name muted">{{ g.section.name }}</div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px">
          <span
            v-for="c in g.items"
            :key="c.id"
            class="badge pickable"
            @click="toggle(c.id)"
          >
            {{ c.name }}
          </span>
        </div>
      </div>
    </div>
    <p v-else class="muted" style="margin: 0">
      {{ tree.length === 0 ? 'Категории ещё не заведены.' : 'Ничего не найдено.' }}
    </p>
  </div>
</template>

<style scoped>
.cat-groups {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 260px;
  overflow-y: auto;
  padding-right: 4px;
}
.cat-group-name {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 4px;
}
</style>
