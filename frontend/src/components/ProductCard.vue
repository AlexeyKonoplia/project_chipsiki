<script setup>
import StarRating from './StarRating.vue'

defineProps({
  product: { type: Object, required: true },
})
</script>

<template>
  <router-link :to="{ name: 'product', params: { id: product.id } }" class="card" style="color: inherit; display: block">
    <div v-if="product.image_url">
      <img :src="product.image_url" :alt="product.name" class="product-img" />
    </div>
    <div v-else class="product-img placeholder">📦</div>

    <h3 style="margin: 12px 0 4px; font-size: 16px">{{ product.name }}</h3>

    <div class="row" style="margin-bottom: 6px">
      <StarRating :model-value="product.average_rating || 0" />
      <span class="muted">
        {{ product.average_rating ? product.average_rating.toFixed(1) : '—' }}
        ({{ product.review_count }})
      </span>
    </div>

    <div>
      <span v-for="c in product.categories" :key="c.id" class="badge">{{ c.name }}</span>
    </div>
    <div class="muted" style="margin-top: 6px">автор: {{ product.owner.username }}</div>
  </router-link>
</template>
