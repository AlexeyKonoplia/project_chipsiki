<script setup>
import { ref } from 'vue'

// v-model is an array of tag name strings (free-form user tags).
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  max: { type: Number, default: 10 },
})
const emit = defineEmits(['update:modelValue'])

const draft = ref('')

function normalize(raw) {
  return raw.trim().replace(/^#+/, '').trim().toLowerCase()
}

function add() {
  const name = normalize(draft.value)
  draft.value = ''
  if (!name || name.length > 64) return
  if (props.modelValue.includes(name)) return
  if (props.modelValue.length >= props.max) return
  emit('update:modelValue', [...props.modelValue, name])
}

function remove(name) {
  emit('update:modelValue', props.modelValue.filter((t) => t !== name))
}

function onKeydown(e) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    add()
  } else if (e.key === 'Backspace' && !draft.value && props.modelValue.length) {
    remove(props.modelValue[props.modelValue.length - 1])
  }
}
</script>

<template>
  <div>
    <div
      v-if="modelValue.length"
      style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px"
    >
      <span v-for="t in modelValue" :key="t" class="badge selected" @click="remove(t)">
        #{{ t }} ✕
      </span>
    </div>
    <input
      v-model="draft"
      :placeholder="modelValue.length >= max ? `Максимум ${max} тегов` : 'Тег и Enter, например вкусно…'"
      :disabled="modelValue.length >= max"
      style="max-width: 260px"
      @keydown="onKeydown"
      @blur="add"
    />
  </div>
</template>
