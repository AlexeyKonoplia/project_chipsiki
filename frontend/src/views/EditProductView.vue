<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../store/auth'
import CategorySelector from '../components/CategorySelector.vue'
import ImageCropper from '../components/ImageCropper.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const auth = useAuthStore()

const name = ref('')
const description = ref('')
const categoryIds = ref([])
const currentImage = ref(null)
const removeImage = ref(false)
const cropper = ref(null)

const loading = ref(true)
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get(`/api/products/${props.id}`)
    // Permission check on the client (backend enforces too).
    if (!auth.user || (!auth.user.is_admin && auth.user.id !== data.owner.id)) {
      router.replace({ name: 'product', params: { id: props.id } })
      return
    }
    name.value = data.name
    description.value = data.description || ''
    categoryIds.value = data.categories.map((c) => c.id)
    currentImage.value = data.image_url
  } catch {
    error.value = 'Не удалось загрузить товар'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  if (!name.value.trim()) {
    error.value = 'Укажите название товара'
    return
  }
  saving.value = true
  try {
    const form = new FormData()
    form.append('name', name.value.trim())
    if (description.value.trim()) form.append('description', description.value.trim())
    categoryIds.value.forEach((cid) => form.append('category_ids', cid))
    const file = cropper.value ? await cropper.value.getFile() : null
    if (file) {
      form.append('image', file)
    } else if (removeImage.value) {
      form.append('remove_image', 'true')
    }
    await api.patch(`/api/products/${props.id}`, form)
    router.push({ name: 'product', params: { id: props.id } })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сохранить изменения'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <p v-if="loading" class="muted">Загрузка…</p>
  <div v-else class="card" style="max-width: 560px; margin: 0 auto">
    <h1 class="title">Редактировать товар</h1>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="field">
      <label>Название *</label>
      <input v-model="name" />
    </div>
    <div class="field">
      <label>Описание</label>
      <textarea v-model="description" rows="3"></textarea>
    </div>
    <div class="field">
      <label>Категории</label>
      <CategorySelector v-model="categoryIds" />
    </div>

    <div class="field">
      <label>Текущее фото</label>
      <div v-if="currentImage && !removeImage" class="row" style="align-items: flex-start">
        <img :src="currentImage" class="product-img" style="max-width: 200px; height: 130px" />
      </div>
      <p v-else class="muted" style="margin: 0 0 8px">Нет фото</p>
      <label v-if="currentImage" class="row" style="cursor: pointer; margin-bottom: 10px">
        <input type="checkbox" v-model="removeImage" style="width: auto" />
        <span style="margin-left: 6px">Удалить текущее фото</span>
      </label>
    </div>

    <div class="field">
      <label>Заменить фото (необязательно)</label>
      <ImageCropper ref="cropper" />
    </div>

    <div class="row">
      <button class="btn" :disabled="saving" @click="save">
        {{ saving ? 'Сохранение…' : 'Сохранить' }}
      </button>
      <router-link class="btn secondary" :to="{ name: 'product', params: { id } }">
        Отмена
      </router-link>
    </div>
  </div>
</template>
