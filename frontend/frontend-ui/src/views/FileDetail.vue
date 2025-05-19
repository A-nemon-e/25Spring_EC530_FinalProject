<template>
  <div style="padding: 24px;">
    <!-- 缩略图（占位） -->
    <div class="thumbnail-placeholder">PDF 预览图（占位）</div>

    <!-- 主标题 -->
    <h2 style="margin-top: 16px;">{{ title }}</h2>

    <!-- 标签区域 -->
    <div v-for="(tags, category) in groupedTags" :key="category" style="margin: 8px 0;">
      <strong>{{ category }}：</strong>
      <span v-for="tag in tags" :key="tag.id">
        <el-tooltip
          effect="dark"
          :content="tag.aliases.map(a => a.name).join(' / ')"
          placement="top"
          v-if="tag.aliases.length > 0"
        >
          <el-tag
            size="small"
            style="margin: 4px; cursor: pointer;"
          >
            {{ tag.name }}
          </el-tag>
        </el-tooltip>
        <el-tag
          size="small"
          style="margin: 4px; cursor: pointer;"
          v-else
        >
          {{ tag.name }}
        </el-tag>
      </span>
    </div>

    <!-- 文件信息 -->
    <div style="margin-top: 20px; font-size: 14px; color: #555;">
      <p>文件路径：{{ fileData.upload_path }}</p>
      <p>上传时间：{{ formatDate(fileData.uploaded_at) }}</p>
      <p>文件大小：{{ formatSize(fileData.size) }}</p>
    </div>

    <!-- 所属虚拟文件夹路径 -->
    <div v-if="fileData.folders.length > 0" style="margin-top: 16px;">
      <strong>所属路径：</strong>
      <span
        v-for="folder in fileData.folders"
        :key="folder.id"
        @click="goToFolder(folder.id)"
        style="color: #409EFF; cursor: pointer; text-decoration: underline; margin-right: 12px;"
      >
        {{ buildFullPath(folder.id).join(" / ") }}
      </span>
    </div>

    <!-- 操作按钮 -->
    <div style="margin-top: 24px;">
      <el-button type="primary">下载</el-button>
      <el-button>编辑</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const fileData = ref(null)
const title = ref("")
const groupedTags = ref({})  // category -> [{name, id, aliases}]
const folderDict = ref({})   // folder id -> {id, name, parent_id}

// ==================== 加载核心 ====================

const loadFileData = async () => {
  const res = await axios.get(`/api/files/${route.params.id}`)
  fileData.value = res.data.data

  // 设置主标题
  const titleTag = fileData.value.tags.find(t => t.category === 'title')
  title.value = titleTag ? titleTag.name : fileData.value.name

  // 分组标签（排除 title 类别）
  groupedTags.value = {}
  for (const tag of fileData.value.tags) {
    if (tag.category === 'title') continue
    if (!groupedTags.value[tag.category]) groupedTags.value[tag.category] = []
    groupedTags.value[tag.category].push(tag)
  }

  // 加载文件夹路径
  const treeRes = await axios.get('/api/folders/tree')
  const folders = flatten(treeRes.data.data)
  folderDict.value = Object.fromEntries(folders.map(f => [f.id, f]))
}

const flatten = (tree) => {
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

const buildFullPath = (id) => {
  const path = []
  let current = folderDict.value[id]
  while (current) {
    path.unshift(current.name)
    current = folderDict.value[current.parent_id]
  }
  return path
}

const formatDate = (str) => new Date(str).toLocaleString()
const formatSize = (bytes) => `${(bytes / 1024).toFixed(1)} KB`
const goToFolder = (id) => router.push(`/folder/${id}`)

onMounted(() => loadFileData())
</script>

<style scoped>
.thumbnail-placeholder {
  width: 240px;
  height: 320px;
  background: #f0f0f0;
  border: 1px dashed #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 14px;
  margin-bottom: 20px;
}
</style>
