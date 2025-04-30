<template>
    <div style="padding: 24px">
      <!-- 当前路径（面包屑） -->
      <el-breadcrumb separator="/">
        <el-breadcrumb-item @click="goToRoot" style="cursor: pointer">根目录</el-breadcrumb-item>
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
            <el-icon><Folder /></el-icon>
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
          style="margin-bottom: 14px"
          shadow="hover"
        >
          <div style="display: flex; justify-content: space-between;">
            <div>
              <div style="font-weight: bold; font-size: 16px;">{{ getFileTitle(file) }}</div>
              <div v-if="getTitleAliases(file).length > 0" style="font-size: 12px; color: gray;">
                别名：{{ getTitleAliases(file).join(' / ') }}
              </div>
              <div style="font-size: 12px; color: gray; margin-top: 4px;">
                上传时间：{{ formatDate(file.uploaded_at) }}
              </div>
              <div style="margin-top: 8px;">
                <el-tag
                  v-for="tag in getOtherTags(file)"
                  :key="tag.id"
                  :color="getCategoryColor(tag.category)"
                  size="small"
                  style="margin-right: 6px; color: white; font-size: 14px; padding: 6px 10px;"
                >
                  {{ tag.name }}（{{ tag.category }}）
                </el-tag>
              </div>
            </div>
            <div style="text-align: right;">
              <el-button size="small" type="primary">下载</el-button>
              <el-button size="small">详情</el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import axios from 'axios'
  import { Folder } from '@element-plus/icons-vue'
  
  const route = useRoute()
  const router = useRouter()
  
  const folderId = ref(null)
  const folders = ref([])
  const files = ref([])
  const currentPath = ref([])
  
  // 所有文件夹字典（一次性加载）
  const allFoldersDict = ref({})
  
  // ==================== 加载核心 ====================
  
  const loadAllFolders = async () => {
    const res = await axios.get('http://localhost:5000/api/folders/tree')
    const folderList = flattenFolders(res.data.data)
    allFoldersDict.value = Object.fromEntries(folderList.map(f => [f.id, f]))
  }
  
  const flattenFolders = (tree) => {
    const result = []
    const dfs = (nodes) => {
      for (const node of nodes) {
        result.push({ id: node.id, name: node.name, parent_id: node.parent_id })
        if (node.children) dfs(node.children)
      }
    }
    dfs(tree)
    return result
  }
  
  const buildCurrentPath = (id) => {
    const path = []
    let current = allFoldersDict.value[id]
    while (current) {
      path.unshift(current)
      current = allFoldersDict.value[current.parent_id]
    }
    currentPath.value = path
  }
  
  // ==================== 主加载函数 ====================
  
  const loadFolder = async () => {
    folderId.value = route.params.id || '0'
    const res = await axios.get(`http://localhost:5000/api/folders/${folderId.value}/children`)
    folders.value = res.data.data.folders
    files.value = res.data.data.files
  
    buildCurrentPath(folderId.value)
  }
  
  // ==================== 页面行为 ====================
  
  onMounted(async () => {
    await loadAllFolders()
    await loadFolder()
  })
  
  watch(() => route.params.id, async () => {
    await loadFolder()
  })
  
  // ==================== 路由跳转 ====================
  
  const goToFolder = (id) => {
    router.push(`/folder/${id}`)
  }
  
  const goToRoot = () => {
    router.push('/folder/0')
  }
  
  // ==================== 标签显示工具 ====================
  
  const getFileTitle = (file) => {
    const titleTag = file.tags?.find(t => t.category === 'title')
    return titleTag ? titleTag.name : file.name
  }
  
  const getTitleAliases = (file) => {
    const titleTag = file.tags?.find(t => t.category === 'title')
    return titleTag && titleTag.aliases ? titleTag.aliases.map(a => a.name) : []
  }
  
  const getOtherTags = (file) => {
    return file.tags?.filter(t => t.category !== 'title') || []
  }
  
  const formatDate = (ts) => {
    return new Date(ts).toLocaleString()
  }
  
  // ==================== 颜色映射 ====================
  
  const categoryColorMap = ref({})
  const availableColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD']
  let colorIndex = 0
  const getCategoryColor = (category) => {
    if (!categoryColorMap.value[category]) {
      categoryColorMap.value[category] = availableColors[colorIndex % availableColors.length]
      colorIndex++
    }
    return categoryColorMap.value[category]
  }
  </script>
  
  <style scoped>
  .el-card:hover {
    border-color: #409EFF;
  }
  </style>
  