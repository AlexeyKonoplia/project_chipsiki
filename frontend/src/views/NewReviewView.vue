<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'
import StarRating from '../components/StarRating.vue'
import CategorySelector from '../components/CategorySelector.vue'
import ProductAutocomplete from '../components/ProductAutocomplete.vue'
import ImageCropper from '../components/ImageCropper.vue'

const router = useRouter()
const route = useRoute()

const mode = ref('existing') // 'existing' | 'new'
const selectedProductId = ref(null)
const autocomplete = ref(null)

// New-product fields
const name = ref('')
const description = ref('')
const categoryIds = ref([])
const cropper = ref(null)

// Review fields
const rating = ref(0)
const text = ref('')

const error = ref('')
const loading = ref(false)

const canSubmit = computed(() => {
  if (rating.value < 1) return false
  if (mode.value === 'existing') return !!selectedProductId.value
  return !!name.value.trim()
})

onMounted(async () => {
  // Allow pre-selecting a product via ?product_id= (from the product page).
  if (route.query.product_id) {
    try {
      const { data } = await api.get(`/api/products/${route.query.product_id}`)
      autocomplete.value?.setSelected(data)
    } catch {
      /* ignore */
    }
  }
})

async function submit() {
  error.value = ''
  if (!canSubmit.value) {
    error.value = 'Поставьте оценку и выберите/добавьте товар'
    return
  }
  loading.value = true
  try {
    let productId = selectedProductId.value

    // If adding a new product, create it first (supports cropped photo upload).
    if (mode.value === 'new') {
      const form = new FormData()
      form.append('name', name.value.trim())
      if (description.value.trim()) form.append('description', description.value.trim())
      categoryIds.value.forEach((id) => form.append('category_ids', id))
      const file = cropper.value ? await cropper.value.getFile() : null
      if (file) form.append('image', file)
      const { data: product } = await api.post('/api/products', form)
      productId = product.id
    }

    await api.post('/api/reviews', {
      rating: rating.value,
      text: text.value.trim() || null,
      product_id: productId,
    })

    router.push({ name: 'product', params: { id: productId } })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сохранить отзыв'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 620px; margin: 0 auto">
    <h1 class="title">Оставить отзыв</h1>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="field">
      <label>Товар</label>
      <div class="seg" style="margin-bottom: 12px">
        <button
          type="button"
          class="seg-btn"
          :class="{ active: mode === 'existing' }"
          @click="mode = 'existing'"
        >
          Выбрать существующий
        </button>
        <button
          type="button"
          class="seg-btn"
          :class="{ active: mode === 'new' }"
          @click="mode = 'new'"
        >
          Добавить новый
        </button>
      </div>

      <div v-if="mode === 'existing'">
        <ProductAutocomplete ref="autocomplete" v-model="selectedProductId" />
      </div>

      <div v-else class="card" style="background: var(--card-2)">
        <div class="field">
          <label>Название *</label>
          <input v-model="name" />
        </div>
        <div class="field">
          <label>Описание (необязательно)</label>
          <textarea v-model="description" rows="2"></textarea>
        </div>
        <div class="field">
          <label>Категории</label>
          <CategorySelector v-model="categoryIds" />
        </div>
        <div class="field" style="margin-bottom: 0">
          <label>Фото</label>
          <ImageCropper ref="cropper" />
        </div>
      </div>
    </div>

    <div class="field">
      <label>Оценка *</label>
      <StarRating v-model="rating" editable style="font-size: 30px" />
    </div>

    <div class="field">
      <label>Текст отзыва (необязательно)</label>
      <textarea v-model="text" rows="4" placeholder="Поделитесь впечатлениями…"></textarea>
    </div>

    <button class="btn" :disabled="loading || !canSubmit" @click="submit">
      {{ loading ? 'Отправка…' : 'Опубликовать отзыв' }}
    </button>
  </div>
</template>
