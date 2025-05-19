import { createRouter, createWebHistory } from 'vue-router'
import Search from '../views/Search.vue'
import FolderExplorer from '../views/FolderExplorer.vue'
import FileDetail from '../views/FileDetail.vue'

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
  },
  {
    path: '/file/:id',
    component: FileDetail,
    name: 'file-detail'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
