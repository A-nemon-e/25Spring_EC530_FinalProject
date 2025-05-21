<template>
  <el-container style="min-height: 100vh">
    <!-- 左侧导航栏 -->
    <!-- <el-aside width="200px" style="background-color: #f2f2f2">
      <el-menu router :default-active="$route.path">
        <el-menu-item index="/search">🔍 搜索</el-menu-item>
        <el-menu-item index="/folder/0">📁 文件夹视图</el-menu-item>
        <el-divider />
        <el-menu-item index="/tags">🏷️ 标签管理（预留）</el-menu-item>
        <el-menu-item index="/aliases">🧩 别名设置（预留）</el-menu-item>
      </el-menu>
    </el-aside> -->
    
    <Sidebar />
    <!-- 主视图区 -->
    <el-main style="background-color: white; padding: 0">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'

</script>

<style scoped>
</style>
