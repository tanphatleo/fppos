import { createRouter, createWebHistory } from 'vue-router'
import Sale from '@/views/Sale.vue'
import Manage from '@/views/Manage.vue'
import SignIn from '@/views/SignIn.vue'

const routes = [
  {
    path: '/',
    redirect: '/sale'
  },
  {
    path: '/sale',
    name: 'sale',
    component: Sale
  },
  {
    path: '/manage',
    name: 'manage',
    component: Manage
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/signin',
    name: 'signin',
    component: SignIn
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
