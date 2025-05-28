<template>
  <div style="padding: 24px">
    <!-- 当前路径（面包屑） -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="(part, index) in currentPath"
        :key="index"
        @click="goToFolder(part.id)"
        style="cursor: pointer"
      >
        {{ part.name }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 子文件夹展示 -->
    <div v-if="folders.length > 0" style="margin-top: 20px;">
      <el-divider content-position="left">子文件夹</el-divider>
      <el-space wrap>
        <el-card
          v-for="folder in folders"
          :key="folder.id"
          @click="goToFolder(folder.id)"
          style="width: 200px; cursor: pointer;"
          shadow="hover"
        >
          <el-icon><FolderIcon /></el-icon>
          <span style="margin-left: 8px;">{{ folder.name }}</span>
        </el-card>
      </el-space>
    </div>

    <!-- 文件展示 -->
    <div v-if="files.length > 0" style="margin-top: 30px;">
      <el-divider content-position="left">文件</el-divider>
      <el-card
        v-for="file in files"
        :key="file.id"
        
        style="margin-bottom: 14px; cursor: pointer;"
        shadow="hover"
      >
        <div style="display: flex; justify-content: space-between;">
          <div>
            <!-- 主标题 -->
            <div style="font-weight: bold; font-size: 16px;">
              {{ getFileTitle(file) }}
            </div>

            <!-- 上传时间 -->
            <div style="font-size: 12px; color: gray; margin-top: 4px;">
              上传时间：{{ formatDate(file.uploaded_at) }}
            </div>

            <!-- 所属路径 -->
            <div v-if="file.folders?.length > 0" style="margin-top: 6px; font-size: 12px;">
              所属路径：
              <span
                v-for="folder in file.folders"
                :key="folder.id"
                @click="goToFolder(folder.id)"
                style="margin-right: 12px; color: #409EFF; cursor: pointer; text-decoration: underline;"
              >
                {{ folder.full_path?.join(" / ") }}
              </span>
            </div>

            <!-- 标签展示 -->
            <div style="margin-top: 8px;">
              <el-tag
                v-for="tag in getOtherTags(file)"
                :key="tag.id"
                :color="store.getCategoryColor(tag.category)"
                size="small"
                style="margin-right: 6px; color: #505055; font-size: 14px; padding: 6px 10px; height: auto;"
              >
                {{ tag.name }}（{{ tag.category }}）
              </el-tag>
            </div>
          </div>

          <div style="text-align: right;">
            <el-button size="small" type="primary">下载</el-button>
            
            <el-button size="small" @click.stop="goToFile(file.id)">详情</el-button>

          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>

import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useFolderExplorerStore } from '../stores/folderStore'
import { Folder as FolderIcon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useFolderExplorerStore()

// —— 关键：拆出响应式 refs ——  
const { folderId, folders, files, currentPath } = storeToRefs(store)
// 方法直接从 store 上拿  
const { loadAllFolders, loadFolder } = store

// —— 初始加载一次全量目录 + 当前目录 ——  
onMounted(async () => {
  await loadAllFolders()
  if (route.params.id) {
    await loadFolder(route.params.id)
  }
})

// —— 导航按钮：先加载数据，再跳路由 ——  
const goToFolder = async (id) => {
  if (id !== route.params.id) {
    await loadFolder(id)           // ← 数据先更新  
    router.push(`/folder/${id}`)   // ← 再跳路由  
  } else {
    await loadFolder(id)
  }
}

const goToFile = (fileId) => {
  router.push(`/file/${fileId}`)
}

const getFileTitle = (file) => {
  const titleTag = file.tags?.find(t => t.category === 'title')
  return titleTag ? titleTag.name : file.name
}

const getOtherTags = (file) => {
  return file.tags?.filter(t => t.category !== 'title') || []
}

const formatDate = (ts) => {
  return new Date(ts).toLocaleString()
}




</script>

<style scoped>
.el-card:hover {
  border-color: #409EFF;
}
</style>
