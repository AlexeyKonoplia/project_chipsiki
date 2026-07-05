<script setup>
import { ref, computed } from 'vue'

// Shows up to `limit` hashtags with an expand/collapse toggle for the rest.
const props = defineProps({
  tags: { type: Array, default: () => [] },
  limit: { type: Number, default: 3 },
})

const expanded = ref(false)
const visible = computed(() =>
  expanded.value ? props.tags : props.tags.slice(0, props.limit)
)
const hiddenCount = computed(() => props.tags.length - props.limit)

function toggle(e) {
  // The list may live inside a router-link card; don't navigate.
  e.preventDefault()
  e.stopPropagation()
  expanded.value = !expanded.value
}
</script>

<template>
  <div v-if="tags.length" class="taglist">
    <span v-for="t in visible" :key="t.id" class="tag">#{{ t.name }}</span>
    <button v-if="hiddenCount > 0" type="button" class="tag more" @click="toggle">
      {{ expanded ? 'Свернуть' : `Ещё ${hiddenCount}` }}
    </button>
  </div>
</template>

<style scoped>
.taglist {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 6px;
  align-items: center;
}
.tag {
  font-size: 12px;
  color: var(--primary);
  background: rgba(232, 176, 75, 0.09);
  border: 1px solid rgba(232, 176, 75, 0.25);
  border-radius: 999px;
  padding: 2px 9px;
}
.tag.more {
  cursor: pointer;
  font-family: inherit;
  color: var(--muted);
  background: var(--card-2);
  border-color: var(--border);
  transition: color 0.15s, border-color 0.15s;
}
.tag.more:hover {
  color: var(--text);
  border-color: var(--primary);
}
</style>
