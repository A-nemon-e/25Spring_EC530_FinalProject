<template>
  <div v-if="fileData.name" style="padding: 24px;">
    <!-- 缩略图占位 -->
    <div class="thumbnail-placeholder">PDF 预览图（占位）</div>

    <!-- 主标题 -->
    <div style="display: flex; align-items: center;">
      <h2 style="margin-top: 16px; margin-right: 12px;">
        <el-tooltip
          effect="dark"
          :content="titleAliases.join(' / ')"
          placement="top"
          v-if="titleAliases.length > 0"
        >
          {{ title }}
        </el-tooltip>
        <span v-else>{{ title }}</span>
      </h2>
      <el-tag type="warning" size="small" v-if="isFallbackTitle">无Title标签，显示文件名</el-tag>
    </div>

    <!-- 标签展示 -->
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
            @click="openTagEditor(tag)"
          >
            {{ tag.name }}
          </el-tag>
        </el-tooltip>
        <el-tag
          size="small"
          style="margin: 4px; cursor: pointer;"
          @click="openTagEditor(tag)"
          v-else
        >
          {{ tag.name }}
        </el-tag>
      </span>
    </div>

    <!-- 文件基本信息 -->
    <div style="margin-top: 20px; font-size: 14px; color: #555;">
      <p>文件路径：{{ fileData.upload_path }}</p>
      <p>上传时间：{{ formatDate(fileData.uploaded_at) }}</p>
      <p>文件大小：{{ formatSize(fileData.size) }}</p>
    </div>

    <!-- 所属虚拟文件夹 -->
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
      <el-button @click="editFile">编辑</el-button>
    </div>

    <!-- 标签编辑对话框（预留） -->
    <el-dialog
      v-model="isTagEditorVisible"
      title="编辑标签"
      width="400px"
    >
      <p>这是标签编辑对话框（功能暂不实现）。</p>
      <div slot="footer" class="dialog-footer">
        <el-button @click="isTagEditorVisible = false">取消</el-button>
        <el-button type="primary" @click="isTagEditorVisible = false">确认</el-button>
      </div>
    </el-dialog>
  </div>

  <!-- 骨架屏 -->
  <div v-else style="padding: 24px;">
    <el-skeleton rows="6" animated />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// 初始化文件数据
const fileData = ref({
  id: '',
  name: '',
  size: 0,
  upload_path: '',
  uploaded_at: '',
  tags: [],
  folders: []
})

const title = ref("")
const titleAliases = ref([])
const isFallbackTitle = ref(false)
const groupedTags = ref({})  // category -> [{name, id, aliases}]
const folderDict = ref({})   // folder id -> {id, name, parent_id}
const isTagEditorVisible = ref(false)
const currentEditingTag = ref(null)

// ==================== 加载文件信息 ====================

const loadFileData = async () => {
  try {
    const fileId = route.params.id
    const res = await axios.get(`http://localhost:5000/api/files/${fileId}`)

    // 设置文件基本信息
    fileData.value = res.data.data || {}

    // 设置主标题
    const titleTag = fileData.value.tags.find(t => t.category === 'title')
    if (titleTag) {
      title.value = titleTag.name
      titleAliases.value = titleTag.aliases.map(a => a.name)
      isFallbackTitle.value = false
    } else {
      title.value = fileData.value.name
      titleAliases.value = []
      isFallbackTitle.value = true
    }

    // 分组标签（排除 title 类别）
    groupedTags.value = {}
    for (const tag of fileData.value.tags) {
      if (tag.category === 'title') continue
      if (!groupedTags.value[tag.category]) groupedTags.value[tag.category] = []
      groupedTags.value[tag.category].push(tag)
    }

    // 加载文件夹路径
    const treeRes = await axios.get('http://localhost:5000/api/folders/tree')
    const folders = flatten(treeRes.data.data)
    folderDict.value = Object.fromEntries(folders.map(f => [f.id, f]))
  } catch (error) {
    console.error("加载文件信息失败：", error)
    alert("加载文件信息失败，请检查后端是否正常运行")
  }
}

// 展平文件夹树
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

// 标签编辑预留
const openTagEditor = (tag) => {
  currentEditingTag.value = tag
  isTagEditorVisible.value = true
}

const editFile = () => {
  alert("跳转到文件编辑页面（暂不实现）")
}

onMounted(() => loadFileData())
</script>

<style scoped>
.thumbnail-placeholder {
  width: 200px;
  height: 200px;
  background-color: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-weight: bold;
  margin-bottom: 16px;
}
</style>
