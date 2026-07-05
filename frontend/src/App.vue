<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="navbar">
    <div class="navbar-inner">
      <router-link class="brand" to="/">
        <img src="/icon.png" alt="Чипсеки" class="brand-logo" />
        <span>Чипсеки</span>
      </router-link>
      <div class="spacer"></div>
      <router-link to="/">Товары</router-link>
      <router-link to="/new-review">Оставить отзыв</router-link>
      <router-link v-if="auth.user?.is_admin" to="/admin">Админка</router-link>
      <template v-if="auth.isAuthenticated">
        <router-link :to="{ name: 'user', params: { id: auth.user.id } }">Мои отзывы</router-link>
        <span class="navuser">{{ auth.user?.username }}</span>
        <a href="#" @click.prevent="logout">Выйти</a>
      </template>
      <template v-else>
        <router-link to="/login">Вход</router-link>
        <router-link to="/register">Регистрация</router-link>
      </template>
    </div>
  </div>

  <div class="container">
    <div
      v-if="auth.user && !auth.user.is_admin && !auth.user.is_approved"
      class="error"
      style="background: rgba(232, 176, 75, 0.08); border-color: rgba(232, 176, 75, 0.35); color: var(--primary)"
    >
      Ваш аккаунт ещё не подтверждён администратором. Пока вы можете только читать отзывы —
      писать отзывы и добавлять товары станет доступно после подтверждения.
    </div>
    <router-view />
  </div>
</template>
