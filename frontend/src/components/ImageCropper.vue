<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

// Lets the user pick / drop / paste an image, choose a crop area & aspect
// ratio, and exposes getFile() so the parent can grab the cropped result.
const src = ref(null)
const cropperRef = ref(null)
const fileInput = ref(null)
const aspect = ref(null) // null = free crop
const dragOver = ref(false)

const ratios = [
  { label: 'Свободно', value: null },
  { label: '1:1', value: 1 },
  { label: '4:3', value: 4 / 3 },
  { label: '3:4', value: 3 / 4 },
  { label: '16:9', value: 16 / 9 },
]

const stencilProps = computed(() => (aspect.value ? { aspectRatio: aspect.value } : {}))

function loadFile(file) {
  if (!file || !file.type.startsWith('image/')) return
  if (src.value) URL.revokeObjectURL(src.value)
  src.value = URL.createObjectURL(file)
}

function onFileInput(e) {
  loadFile(e.target.files[0])
  e.target.value = '' // allow re-selecting the same file later
}

function onDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  loadFile(file)
}

function onPaste(e) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      loadFile(item.getAsFile())
      e.preventDefault()
      break
    }
  }
}

function openPicker() {
  fileInput.value?.click()
}

function setAspect(v) {
  aspect.value = v
}

function clear() {
  if (src.value) URL.revokeObjectURL(src.value)
  src.value = null
  aspect.value = null
}

// Returns a cropped JPEG File, or null if no image was selected.
async function getFile() {
  if (!src.value || !cropperRef.value) return null
  const { canvas } = cropperRef.value.getResult()
  if (!canvas) return null
  return await new Promise((resolve) => {
    canvas.toBlob(
      (blob) => resolve(blob ? new File([blob], 'photo.jpg', { type: 'image/jpeg' }) : null),
      'image/jpeg',
      0.9
    )
  })
}

defineExpose({ getFile })

onMounted(() => document.addEventListener('paste', onPaste))
onBeforeUnmount(() => {
  document.removeEventListener('paste', onPaste)
  if (src.value) URL.revokeObjectURL(src.value)
})
</script>

<template>
  <div class="cropper-wrap">
    <input ref="fileInput" type="file" accept="image/*" hidden @change="onFileInput" />

    <!-- Empty state: click / drop / paste -->
    <div
      v-if="!src"
      class="dropzone"
      :class="{ over: dragOver }"
      tabindex="0"
      @click="openPicker"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <div class="dz-icon">🖼️</div>
      <div class="dz-title">Выберите, перетащите или вставьте фото</div>
      <div class="muted" style="font-size: 12px; margin-top: 4px">
        Нажмите для выбора файла · перетащите сюда · <kbd>Ctrl</kbd> + <kbd>V</kbd> из буфера
      </div>
    </div>

    <!-- Editing state -->
    <template v-else>
      <div class="ratio-row">
        <button
          v-for="r in ratios"
          :key="r.label"
          type="button"
          class="chip"
          :class="{ active: aspect === r.value }"
          @click="setAspect(r.value)"
        >
          {{ r.label }}
        </button>
        <button type="button" class="chip" @click="openPicker">↻ Заменить</button>
        <button type="button" class="chip danger" @click="clear">✕ Убрать</button>
      </div>

      <div class="cropper-box">
        <Cropper
          ref="cropperRef"
          :src="src"
          :stencil-props="stencilProps"
          image-restriction="fit-area"
          class="cropper"
        />
      </div>
      <p class="muted" style="margin: 6px 0 0; font-size: 12px">
        Тяните рамку и её углы, чтобы выбрать область. Колёсиком — масштаб.
      </p>
    </template>
  </div>
</template>

<style scoped>
.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 2px;
  padding: 28px 16px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  background: var(--card-2);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.dropzone:hover,
.dropzone:focus {
  outline: none;
  border-color: var(--primary);
}
.dropzone.over {
  border-color: var(--accent);
  background: rgba(0, 229, 192, 0.08);
}
.dz-icon {
  font-size: 30px;
}
.dz-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  margin-top: 6px;
}
kbd {
  background: #12141b;
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 1px 5px;
  font-size: 11px;
  font-family: inherit;
}
.ratio-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 10px;
}
.chip {
  border: 1px solid var(--border);
  background: var(--card-2);
  color: var(--muted);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.chip:hover {
  color: var(--text);
  border-color: var(--primary);
}
.chip.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.chip.danger:hover {
  color: var(--danger);
  border-color: var(--danger);
}
.cropper-box {
  height: 320px;
  background: #0d0f14;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}
.cropper {
  height: 320px;
}
</style>
