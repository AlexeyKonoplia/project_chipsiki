<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(route.query.redirect || { name: 'home' })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 420px; margin: 40px auto">
    <h1 class="title">Вход</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <form @submit.prevent="submit">
      <div class="field">
        <label>Имя пользователя или email</label>
        <input v-model="username" required autocomplete="username" placeholder="Имя пользователя или email" />
      </div>
      <div class="field">
        <label>Пароль</label>
        <input v-model="password" type="password" required autocomplete="current-password" />
      </div>
      <button class="btn" style="width: 100%" :disabled="loading">
        {{ loading ? 'Вход…' : 'Войти' }}
      </button>
    </form>
    <p class="muted" style="margin-top: 14px">
      Нет аккаунта? <router-link to="/register">Зарегистрируйтесь</router-link>
    </p>
  </div>
</template>
