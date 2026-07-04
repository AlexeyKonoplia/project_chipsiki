<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(username.value, email.value, password.value)
    router.push({ name: 'home' })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card" style="max-width: 420px; margin: 40px auto">
    <h1 class="title">Регистрация</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <form @submit.prevent="submit">
      <div class="field">
        <label>Имя пользователя</label>
        <input v-model="username" required minlength="3" autocomplete="username" />
      </div>
      <div class="field">
        <label>Email</label>
        <input v-model="email" type="email" required autocomplete="email" />
      </div>
      <div class="field">
        <label>Пароль (минимум 6 символов)</label>
        <input v-model="password" type="password" required minlength="6" autocomplete="new-password" />
      </div>
      <button class="btn" style="width: 100%" :disabled="loading">
        {{ loading ? 'Создание…' : 'Зарегистрироваться' }}
      </button>
    </form>
    <p class="muted" style="margin-top: 14px">
      Уже есть аккаунт? <router-link to="/login">Войдите</router-link>
    </p>
  </div>
</template>
