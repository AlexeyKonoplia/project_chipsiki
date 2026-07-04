<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  editable: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const stars = [1, 2, 3, 4, 5]
const rounded = computed(() => Math.round(props.modelValue))

function pick(n) {
  if (props.editable) emit('update:modelValue', n)
}
</script>

<template>
  <span class="stars" :style="{ cursor: editable ? 'pointer' : 'default' }">
    <span v-for="n in stars" :key="n" @click="pick(n)">
      {{ n <= rounded ? '★' : '☆' }}
    </span>
  </span>
</template>
