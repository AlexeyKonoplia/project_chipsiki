<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// v-model is an array of selected category ids.
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const categories = ref([])
const newName = ref('')
const adding = ref(false)

onMounted(async () => {
  const { data } = await api.get('/api/categories')
  categories.value = data
})

function toggle(id) {
  const set = new Set(props.modelValue)
  set.has(id) ? set.delete(id) : set.add(id)
  emit('update:modelValue', [...set])
}

async function addCategory() {
  const name = newName.value.trim()
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
    newName.value = ''
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <div>
    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px">
      <span
        v-for="c in categories"
        :key="c.id"
        class="badge"
        :style="{
          cursor: 'pointer',
          background: modelValue.includes(c.id) ? 'var(--primary)' : '#eef2ff',
          color: modelValue.includes(c.id) ? '#fff' : 'var(--primary-dark)',
        }"
        @click="toggle(c.id)"
      >
        {{ c.name }}
      </span>
      <span v-if="categories.length === 0" class="muted">Категорий пока нет — создайте новую.</span>
    </div>
    <div class="row">
      <input
        v-model="newName"
        placeholder="Новая категория"
        style="max-width: 220px"
        @keyup.enter.prevent="addCategory"
      />
      <button type="button" class="btn secondary" :disabled="adding" @click="addCategory">
        + Добавить
      </button>
    </div>
  </div>
</template>
