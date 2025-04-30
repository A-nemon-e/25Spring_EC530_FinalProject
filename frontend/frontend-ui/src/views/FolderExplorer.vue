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
                :color="getCategoryColor(tag.category)"
                size="small"
                style="margin-right: 6px; color: #505055; font-size: 14px; padding: 6px 10px; height: auto;"
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

const allFoldersDict = ref({})

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

const loadFolder = async () => {
  folderId.value = route.params.id
  const res = await axios.get(`http://localhost:5000/api/folders/${folderId.value}/children`)
  folders.value = res.data.data.folders
  files.value = res.data.data.files
  buildCurrentPath(folderId.value)
}

onMounted(async () => {
  await loadAllFolders()
  await loadFolder()
})

watch(() => route.params.id, async () => {
  await loadFolder()
})

const goToFolder = (id) => {
  router.push(`/folder/${id}`)
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

const categoryColorMap = ref({})
const availableColors = ['#f7e1d7', '#edbfb8', '#dedbd2', '#b0c4b1', '#4a5759', '#78290f', '#b8b8ff', '#E84393']
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
