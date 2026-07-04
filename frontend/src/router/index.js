import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProductDetailView from '../views/ProductDetailView.vue'
import NewProductView from '../views/NewProductView.vue'
import EditProductView from '../views/EditProductView.vue'
import NewReviewView from '../views/NewReviewView.vue'
import AdminView from '../views/AdminView.vue'
import UserReviewsView from '../views/UserReviewsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/products/:id', name: 'product', component: ProductDetailView, props: true },
  { path: '/products/:id/edit', name: 'edit-product', component: EditProductView, props: true, meta: { auth: true } },
  { path: '/new-product', name: 'new-product', component: NewProductView, meta: { auth: true } },
  { path: '/new-review', name: 'new-review', component: NewReviewView, meta: { auth: true } },
  { path: '/admin', name: 'admin', component: AdminView, meta: { auth: true, admin: true } },
  { path: '/users/:id', name: 'user', component: UserReviewsView, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !auth.user?.is_admin) {
    return { name: 'home' }
  }
})

export default router
