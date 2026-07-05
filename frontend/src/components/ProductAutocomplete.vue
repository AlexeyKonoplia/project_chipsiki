<script setup>
import { ref, onBeforeUnmount } from 'vue'
import api from '../api'

// v-model holds the selected product id (or null when nothing is chosen).
const props = defineProps({
  modelValue: { type: [Number, String, null], default: null },
})
const emit = defineEmits(['update:modelValue', 'select'])

const query = ref('')
const results = ref([])
const open = ref(false)
const loading = ref(false)
const selected = ref(null) // the chosen product object (shown as a pill)
let timer = null

function onInput() {
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
  // Explicit selection: show the pill and set the id unambiguously.
  selected.value = p
  query.value = ''
  results.value = []
  open.value = false
  emit('update:modelValue', p.id)
  emit('select', p)
}

function clearSelection() {
  selected.value = null
  emit('update:modelValue', null)
}

function onFocus() {
  if (results.value.length) open.value = true
}
function onBlur() {
  setTimeout(() => (open.value = false), 150)
}

// Lets the parent preselect a product (e.g. from ?product_id=).
function setSelected(product) {
  selected.value = product
  emit('update:modelValue', product.id)
}
defineExpose({ setSelected })

onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="ac">
    <!-- Selected state: a clear pill with a reset button -->
    <div v-if="selected" class="ac-selected">
      <span class="ac-thumb">
        <img v-if="selected.image_url" :src="selected.image_url" :alt="selected.name" />
        <span v-else class="icon-img sm"></span>
      </span>
      <span class="ac-body">
        <span class="ac-name">{{ selected.name }}</span>
        <span class="muted" style="font-size: 12px">
          ★ {{ selected.average_rating ? selected.average_rating.toFixed(1) : '—' }}
          · {{ selected.review_count }} отз.
        </span>
      </span>
      <button type="button" class="ac-clear" title="Выбрать другой" @click="clearSelection">
        ✕
      </button>
    </div>

    <!-- Search state -->
    <template v-else>
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
            <span v-else class="icon-img sm"></span>
          </span>
          <span class="ac-body">
            <span class="ac-name">{{ p.name }}</span>
            <span class="muted" style="font-size: 12px">
              ★ {{ p.average_rating ? p.average_rating.toFixed(1) : '—' }} · {{ p.review_count }} отз.
            </span>
          </span>
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.ac {
  position: relative;
}
.ac-selected {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border: 1px solid var(--primary);
  border-radius: 10px;
  background: rgba(232, 176, 75, 0.08);
}
.ac-clear {
  margin-left: auto;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  border-radius: 8px;
  width: 30px;
  height: 30px;
  cursor: pointer;
  flex: 0 0 auto;
}
.ac-clear:hover {
  color: var(--danger);
  border-color: var(--danger);
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
  background: rgba(232, 176, 75, 0.1);
}
.ac-thumb {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: var(--bg-2);
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
