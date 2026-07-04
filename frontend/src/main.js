import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './store/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Load current user (if a token is present) before mounting.
const auth = useAuthStore()
auth.fetchMe().finally(() => {
  app.mount('#app')
})
