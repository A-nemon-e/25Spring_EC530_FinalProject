<!-- src/components/Sidebar.vue -->
<template>
  <el-menu :default-active="activeMenu" router class="el-menu-vertical-demo">
    <el-menu-item index="/search">🔍 搜索</el-menu-item>
    <el-menu-item index="/folder">📁 文件夹视图</el-menu-item>
    <el-menu-item index="/file">📄 文件详情视图</el-menu-item>
    <el-divider />
    <el-menu-item index="/tag-manager">🏷️ 标签管理</el-menu-item>
    <el-menu-item index="/alias-manager">🔁 别名设置</el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/folder')) return '/folder'
  if (path.startsWith('/file')) return '/file'
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
