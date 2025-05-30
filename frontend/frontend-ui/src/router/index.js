// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Search from '../views/Search.vue'
import FolderExplorer from '../views/FolderExplorer.vue'
import FileDetail from '../views/FileDetail.vue'
import FileTagger from '../views/FileUploader.vue'
import FileEditor from '../views/FileEditor.vue'

const routes = [
  { path: '/', redirect: '/search' },
  { path: '/search', component: Search },
  { path: '/folder/:id', component: FolderExplorer },
  { path: '/file/:id', component: FileDetail },
  // 可选扩展
  {
  path: '/tag-manager',
  name: 'TagManager',
  component: () => import('../views/TagManager.vue')
},
{
    path: '/upload-file',
    name: 'FileTagger',
    component: FileTagger
  },
  {
    path: '/tagger',
    name: 'FileEditor',
    component: FileEditor,
  },

  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
