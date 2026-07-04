<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import CategorySelector from '../components/CategorySelector.vue'
import ImageCropper from '../components/ImageCropper.vue'

const router = useRouter()

const name = ref('')
const description = ref('')
const categoryIds = ref([])
const cropper = ref(null)
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (!name.value.trim()) {
    error.value = 'Укажите название товара'
    return
  }
  loading.value = true
  try {
    const form = new FormData()
    form.append('name', name.value.trim())
    if (description.value.trim()) form.append('description', description.value.trim())
    categoryIds.value.forEach((id) => form.append('category_ids', id))
    const file = cropper.value ? await cropper.value.getFile() : null
    if (file) form.append('image', file)

    const { data } = await api.post('/api/products', form)
    router.push({ name: 'product', params: { id: data.id } })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось создать товар'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 560px; margin: 0 auto">
    <h1 class="title">Новый товар</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <form @submit.prevent="submit">
      <div class="field">
        <label>Название *</label>
        <input v-model="name" required />
      </div>
      <div class="field">
        <label>Описание (необязательно)</label>
        <textarea v-model="description" rows="3"></textarea>
      </div>
      <div class="field">
        <label>Категории</label>
        <CategorySelector v-model="categoryIds" />
      </div>
      <div class="field">
        <label>Фото</label>
        <ImageCropper ref="cropper" />
      </div>
      <button class="btn" :disabled="loading">
        {{ loading ? 'Сохранение…' : 'Создать товар' }}
      </button>
    </form>
  </div>
</template>
