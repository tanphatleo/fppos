import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
<<<<<<< HEAD
=======
import Sale from '@/views/Sale.vue'
>>>>>>> temp-fix

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
<<<<<<< HEAD
=======
    path: '/sale',
    name: 'sale',
    component: Sale
  },
  {
>>>>>>> temp-fix
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
