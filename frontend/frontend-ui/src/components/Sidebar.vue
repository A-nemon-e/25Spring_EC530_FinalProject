<template>
  <div class="sidebar-container">
    <!-- 主导航区域 -->
    <div class="main-nav">
      <el-menu
        :key="activeMenu"
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="#f8faff"
        text-color="#2c3e50"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/search" class="menu-item">
          <span class="menu-icon">🔍</span>
          <span class="menu-text">搜索</span>
        </el-menu-item>
        <el-menu-item :index="folderViewRoute" class="menu-item">
          <span class="menu-icon">📂</span>
          <span class="menu-text">文件夹视图</span>
        </el-menu-item>
        <el-menu-item :index="fileDetailRoute" class="menu-item">
          <span class="menu-icon">📄</span>
          <span class="menu-text">文件详情视图</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 分割线 -->
    <div class="divider"></div>

    <!-- 设置区域 -->
    <div class="settings-nav">
      <div class="settings-title">设置</div>
      <el-menu
        :key="activeMenu"
        :default-active="activeMenu"
        router
        class="sidebar-menu settings-menu"
        background-color="#f0f7ff"
        text-color="#5a6c7d"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/tag-manager" class="menu-item settings-item">
          <span class="menu-icon">🏷️</span>
          <span class="menu-text">标签管理</span>
        </el-menu-item>
        <el-menu-item index="/alias-manager" class="menu-item settings-item">
          <span class="menu-icon">🔁</span>
          <span class="menu-text">别名设置</span>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useFolderExplorerStore } from '../stores/folderStore'
import { useFileStore } from '../stores/fileStore'

const store = useFolderExplorerStore()
const fileStore = useFileStore()
const route = useRoute()

const folderViewRoute = computed(() => {
  return store.folderId ? `/folder/${store.folderId}` : '/folder'
})

const fileDetailRoute = computed(() => {
  return fileStore.fileData?.id ? `/file/${fileStore.fileData.id}` : '/file'
})

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
.sidebar-container {
  width: 220px;
  height: 100vh;
  background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
  border-right: 2px solid #e6f3ff;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(24, 144, 255, 0.08);
}

.main-nav {
  flex: 1;
  padding: 20px 0;
}

.sidebar-menu {
  border: none !important;
  background: transparent !important;
}

.menu-item {
  margin: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  padding: 0 16px !important;
  height: 48px !important;
  line-height: 48px !important;
}

.menu-item:hover {
  background: linear-gradient(90deg, #e6f3ff 0%, #f0f7ff 100%) !important;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.menu-item.is-active {
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.menu-item.is-active .menu-text,
.menu-item.is-active .menu-icon {
  color: white !important;
}

.menu-icon {
  font-size: 18px;
  margin-right: 12px;
  display: inline-block;
  width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.divider {
  height: 1px;
  margin: 0 20px;
  background: linear-gradient(90deg, transparent 0%, #d6e9ff 50%, transparent 100%);
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 4px;
  background: #1890ff;
  border-radius: 2px;
  opacity: 0.3;
}

.settings-nav {
  padding: 20px 0 30px 0;
  background: rgba(240, 247, 255, 0.6);
  border-top: 1px solid #e6f3ff;
}

.settings-title {
  padding: 0 20px 16px 20px;
  font-size: 12px;
  font-weight: 600;
  color: #8c9eff;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
}

.settings-title::after {
  content: '';
  position: absolute;
  bottom: 8px;
  left: 20px;
  width: 30px;
  height: 2px;
  background: #8c9eff;
  border-radius: 1px;
  opacity: 0.5;
}

.settings-menu {
  background: transparent !important;
}

.settings-item {
  margin: 4px 16px;
  font-size: 13px;
}

.settings-item:hover {
  background: linear-gradient(90deg, #f0f7ff 0%, #e6f3ff 100%) !important;
}

.settings-item.is-active {
  background: linear-gradient(90deg, #597ef7 0%, #85a5ff 100%) !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar-container {
    width: 200px;
  }
  
  .menu-text {
    font-size: 13px;
  }
  
  .menu-icon {
    font-size: 16px;
  }
}

/* 滚动条美化 */
.sidebar-container::-webkit-scrollbar {
  width: 4px;
}

.sidebar-container::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-container::-webkit-scrollbar-thumb {
  background: #d6e9ff;
  border-radius: 2px;
}

.sidebar-container::-webkit-scrollbar-thumb:hover {
  background: #bae0ff;
}
</style>