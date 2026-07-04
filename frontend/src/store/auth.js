import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    setSession(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
    async register(username, email, password) {
      const { data } = await api.post('/api/auth/register', { username, email, password })
      this.setSession(data.access_token, data.user)
    },
    async login(username, password) {
      // OAuth2PasswordRequestForm expects x-www-form-urlencoded.
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const { data } = await api.post('/api/auth/login', form)
      this.setSession(data.access_token, data.user)
    },
    async fetchMe() {
      if (!this.token) return
      try {
        const { data } = await api.get('/api/auth/me')
        this.user = data
      } catch {
        this.logout()
      }
    },
  },
})
