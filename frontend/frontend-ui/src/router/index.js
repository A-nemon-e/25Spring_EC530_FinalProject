import { createRouter, createWebHistory } from 'vue-router'
import Search from '../views/Search.vue'
import FolderExplorer from '../views/FolderExplorer.vue'

const routes = [
  {
    path: '/',
    redirect: '/search'
  },
  {
    path: '/search',
    component: Search
  },
  {
    path: '/folder/:id',
    component: FolderExplorer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
