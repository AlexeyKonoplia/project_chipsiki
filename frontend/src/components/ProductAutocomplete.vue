<script setup>
import { ref, onBeforeUnmount } from 'vue'
import api from '../api'

// v-model holds the selected product id (or null while typing / unmatched).
const props = defineProps({
  modelValue: { type: [Number, String, null], default: null },
})
const emit = defineEmits(['update:modelValue', 'select'])

const query = ref('')
const results = ref([])
const open = ref(false)
const loading = ref(false)
let timer = null
let blurTimer = null

// Uses @input (not a watch on `query`) so that programmatically setting the
// field in choose() does NOT re-trigger the search / clear the selection.
function onInput() {
  emit('update:modelValue', null)
  clearTimeout(timer)
  if (!query.value.trim()) {
    results.value = []
    open.value = false
    return
  }
  timer = setTimeout(search, 250)
}

async function search() {
  loading.value = true
  try {
    const { data } = await api.get('/api/products', { params: { q: query.value.trim() } })
    results.value = data.slice(0, 8)
    open.value = true
  } finally {
    loading.value = false
  }
}

function choose(p) {
  query.value = p.name
  results.value = []
  open.value = false
  emit('update:modelValue', p.id)
  emit('select', p)
}

function onFocus() {
  if (results.value.length) open.value = true
}

function onBlur() {
  // Delay so a click on a suggestion registers first.
  blurTimer = setTimeout(() => (open.value = false), 150)
}

onBeforeUnmount(() => {
  clearTimeout(timer)
  clearTimeout(blurTimer)
})
</script>

<template>
  <div class="ac">
    <input
      v-model="query"
      placeholder="Начните вводить название товара…"
      autocomplete="off"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />
    <div v-if="open" class="ac-list">
      <div v-if="loading" class="ac-empty muted">Поиск…</div>
      <div v-else-if="results.length === 0" class="ac-empty muted">
        Ничего не найдено — переключитесь на «Добавить новый».
      </div>
      <button
        v-for="p in results"
        :key="p.id"
        type="button"
        class="ac-item"
        @mousedown.prevent="choose(p)"
      >
        <span class="ac-thumb">
          <img v-if="p.image_url" :src="p.image_url" :alt="p.name" />
          <span v-else>📦</span>
        </span>
        <span class="ac-body">
          <span class="ac-name">{{ p.name }}</span>
          <span class="muted" style="font-size: 12px">
            ★ {{ p.average_rating ? p.average_rating.toFixed(1) : '—' }} · {{ p.review_count }} отз.
          </span>
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.ac {
  position: relative;
}
.ac-list {
  position: absolute;
  z-index: 20;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--card-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
}
.ac-empty {
  padding: 12px 14px;
  font-size: 14px;
}
.ac-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  padding: 10px 12px;
  cursor: pointer;
  color: var(--text);
}
.ac-item:hover {
  background: rgba(124, 92, 255, 0.14);
}
.ac-thumb {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: #0d0f14;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex: 0 0 auto;
}
.ac-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ac-body {
  display: flex;
  flex-direction: column;
}
.ac-name {
  font-size: 14px;
  font-weight: 500;
}
</style>
