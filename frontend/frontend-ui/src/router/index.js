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
    name: 'search',
    component: Search
  },
  {
    path: '/folder/:id',
    name: 'folder',
    component: FolderExplorer
  },
  {
    path: '/file/:id',
    name: 'file-detail',
    component: FileDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
