<!-- src/components/Sidebar.vue -->
<template>
  <el-menu
  :key="activeMenu"                
  :default-active="activeMenu"
  router
  class="el-menu-vertical-demo"
>
    <el-menu-item index="/search">🔍 搜索</el-menu-item>
    <el-menu-item :index="folderViewRoute">📂 文件夹视图</el-menu-item>
    <el-menu-item :index="fileDetailRoute">📄 文件详情视图</el-menu-item>
    <el-divider />
    <el-menu-item index="/tag-manager">🏷️ 标签管理</el-menu-item>
    <el-menu-item index="/alias-manager">🔁 别名设置</el-menu-item>
  </el-menu>
</template>

<script setup>
// import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useFolderExplorerStore } from '../stores/folderStore'

const store = useFolderExplorerStore()

const folderViewRoute = computed(() => {
  return store.folderId ? `/folder/${store.folderId}` : '/folder'
})
import { useFileStore } from '../stores/fileStore'

const fileStore = useFileStore()

const fileDetailRoute = computed(() => {
  // console.log(route.path)
  return fileStore.fileData?.id ? `/file/${fileStore.fileData.id}` : '/file'
})



const route = useRoute()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/folder')) return folderViewRoute.value
  if (path.startsWith('/file')) return fileDetailRoute.value
  if (path.startsWith('/search')) return '/search'
  if (path.startsWith('/tag-manager')) return '/tag-manager'
  if (path.startsWith('/alias-manager')) return '/alias-manager'
  return '/'
})
</script>

<style scoped>
.el-menu-vertical-demo {
  width: 200px;
  height: 100vh;
  border-right: 1px solid #eee;
}
</style>
