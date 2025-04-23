<template>
    <div style="padding: 24px">
      <!-- 搜索栏 -->
      <el-row :gutter="12">
        <el-input v-model="keyword" placeholder="请输入关键词..." style="width: 300px" />
        <el-select v-model="mode" placeholder="搜索类型" style="width: 150px">
          <el-option label="标签" value="tag" />
          <el-option label="文件夹" value="folder" />
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </el-row>
  
      <!-- 已选标签/文件夹栏 -->
      <el-space v-if="selectedItems.length > 0" wrap style="margin-top: 12px">
        <el-tag
          v-for="item in selectedItems"
          :key="`${item.type}-${item.id}`"
          closable
          @close="removeItem(item)"
          type="primary"
        >
          {{ item.name }}
        </el-tag>
        <el-button type="success" @click="searchFiles" size="small">
          搜索文件（共 {{ selectedItems.length }} 项）
        </el-button>
      </el-space>
  
      <!-- 标签搜索结果 -->
      <div v-if="tags.length > 0" style="margin-top: 24px">
        <div v-for="(tagGroup, category) in groupedTags" :key="category" style="margin-bottom: 24px">
          <el-divider content-position="left">
            <span class="category-divider-text">{{ category }}</span>
          </el-divider>
  
          <el-space wrap size="large">
            <el-card
              v-for="tag in tagGroup"
              :key="tag.id"
              style="width: 280px; background: #fdfdfd"
              shadow="hover"
            >
              <div>
                <div style="font-weight: bold; font-size: 16px;">{{ tag.name }}</div>
                <div style="margin-top: 6px; min-height: 32px;">
                  <template v-if="tag.aliases.length > 0">
                    <el-tag
                      v-for="alias in tag.aliases"
                      :key="alias.id"
                      type="info"
                      size="small"
                      effect="plain"
                      style="margin-right: 4px;"
                    >
                      {{ alias.name }}
                    </el-tag>
                  </template>
                  <template v-else>
                    <el-tag type="info" size="small" disabled>无别名</el-tag>
                  </template>
                </div>
  
                <div style="margin-top: 12px; text-align: right;">
                  <el-button size="small" @click="manageTag(tag)">管理</el-button>
                  <el-button size="small" type="primary" @click="addItem(tag, 'tag')">添加</el-button>
                </div>
              </div>
            </el-card>
          </el-space>
        </div>
      </div>
  
      <!-- 文件夹搜索结果 -->
      <div v-if="folders.length > 0" style="margin-top: 24px">
        <el-divider content-position="left">
          <span class="category-divider-text">文件夹搜索结果</span>
        </el-divider>
  
        <el-card
          v-for="folder in folders"
          :key="folder.id"
          style="margin-bottom: 12px"
          shadow="hover"
        >
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 14px;">
              <el-icon><Folder /></el-icon>
              <span style="margin-left: 8px;">{{ folder.full_path.join(" / ") }}</span>
            </div>
            <div>
              <el-button
                size="small"
                @click="openFolder(folder.id)"
                style="margin-right: 8px"
              >
                查看
              </el-button>
              <el-button size="small" type="primary" @click="addItem(folder, 'folder')">添加</el-button>
            </div>
          </div>
        </el-card>
      </div>
      <!-- 文件搜索结果 -->
<div v-if="fileResults.length > 0" style="margin-top: 40px">
  <el-divider content-position="left">
    <span class="category-divider-text">文件搜索结果</span>
  </el-divider>

  <el-card
    v-for="file in fileResults"
    :key="file.id"
    style="margin-bottom: 14px"
    shadow="hover"
  >
    <div style="display: flex; justify-content: space-between;">
      <div>
        <div><strong>{{ file.name }}</strong></div>
        <div style="font-size: 12px; color: gray;">大小：{{ file.size }} 字节</div>
        <div style="font-size: 12px;">上传路径：{{ file.upload_path }}</div>
        <div style="font-size: 12px;">上传时间：{{ file.uploaded_at }}</div>

        <div style="margin-top: 8px;">
          <el-tag
            v-for="tag in file.tags"
            :key="tag.id"
            type="info"
            size="small"
            style="margin-right: 6px;"
          >
            {{ tag.name }}（{{ tag.category }}）
          </el-tag>
        </div>

        <div style="margin-top: 6px; font-size: 12px; color: gray;">
          所属路径：
          <span v-for="folder in file.folders" :key="folder.id" style="margin-right: 12px;">
            {{ folder.full_path.join(" / ") }}
          </span>
        </div>
      </div>
    </div>
  </el-card>

  <div style="text-align: center; margin-top: 20px;">
    <el-pagination
      background
      layout="prev, pager, next"
      :total="fileTotal"
      :page-size="pageSize"
      :current-page="currentPage"
      @current-change="handlePageChange"
    />
  </div>
</div>
    </div>
    
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'
  import { Folder } from '@element-plus/icons-vue'
  
  const fileList = ref([])
  const fileTotal = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const fileResults = ref([])
//   const fileResults = ref([])
//   const fileTotal = ref(0)
  const currentPage = ref(1)
//   const pageSize = ref(20)




  const keyword = ref('')
  const mode = ref('tag')
  const tags = ref([])
  const folders = ref([])
  const selectedItems = ref([]) // 统一管理已选项（标签/文件夹）
  
  const router = useRouter()
  
  // 标签按类别分组
  const groupedTags = computed(() => {
    const groups = {}
    for (const tag of tags.value) {
      if (!groups[tag.category]) {
        groups[tag.category] = []
      }
      groups[tag.category].push(tag)
    }
    return groups
  })
  
  // 搜索逻辑
  const search = async () => {
    if (mode.value === 'tag') {
      const res = await axios.get('http://localhost:5000/api/tags', {
        params: { q: keyword.value }
      })
      tags.value = res.data.data
      folders.value = []
  
      if (tags.value.length === 1) {
        addItem(tags.value[0], 'tag')
      }
    }
  
    if (mode.value === 'folder') {
      const res = await axios.get('http://localhost:5000/api/folders/search', {
        params: { q: keyword.value }
      })
      folders.value = res.data.data
      tags.value = []
    }
  }
  
  // 添加项（标签 or 文件夹）
  const addItem = (item, type) => {
    const exists = selectedItems.value.find(t => t.id === item.id && t.type === type)
    if (!exists) {
      selectedItems.value.push({
        id: item.id,
        name: item.name,
        type
      })
    }
  }
  
  // 移除项
  const removeItem = (item) => {
    selectedItems.value = selectedItems.value.filter(t => !(t.id === item.id && t.type === item.type))
  }
  
  // 跳转管理标签（占位）
  const manageTag = (tag) => {
    alert(`跳转管理标签：${tag.name}`)
  }
  
  // 打开文件夹页面
  const openFolder = (folderId) => {
    router.push(`/folder/${folderId}`)
  }

  // d实际查询函数
  const fetchFiles = async () => {
  const tagIds = selectedItems.value
    .filter(item => item.type === 'tag')
    .map(item => item.id)

  const folderIds = selectedItems.value
    .filter(item => item.type === 'folder')
    .map(item => item.id)

  const queryParams = new URLSearchParams()
  if (tagIds.length > 0) queryParams.append("tag_ids", tagIds.join(","))
  if (folderIds.length > 0) queryParams.append("folder_ids", folderIds.join(","))
  queryParams.append("page", currentPage.value)
  queryParams.append("size", pageSize.value)

  const url = `http://localhost:5000/api/files?${queryParams.toString()}`

  try {
    const res = await axios.get(url)

    if (res.data.status !== "success" || !res.data.data) {
      console.error("接口响应异常：", res.data)
      fileResults.value = []
      fileTotal.value = 0
      return
    }

    const { files, total } = res.data.data
    fileResults.value = files || []
    fileTotal.value = total || 0
  } catch (err) {
    console.error("请求文件数据失败：", err)
    fileResults.value = []
    fileTotal.value = 0
  }
}

  
  // 搜索文件：统一构造 tag_ids
//   const searchFiles = () => {
//   const tagIds = selectedItems.value
//     .filter(item => item.type === 'tag')
//     .map(item => item.id)

//   const folderIds = selectedItems.value
//     .filter(item => item.type === 'folder')
//     .map(item => item.id)

//   // 构造查询参数
//   const queryParams = new URLSearchParams()
//   if (tagIds.length > 0) queryParams.append("tag_ids", tagIds.join(","))
//   if (folderIds.length > 0) queryParams.append("folder_ids", folderIds.join(","))

//   const url = `/api/files?${queryParams.toString()}`
//   alert(`调用接口：${url}`)

//   // TODO: axios.get(url).then(...)
  
// }}
const searchFiles = () => {
  currentPage.value = 1
  fetchFiles()
}
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchFiles()
}



  </script>
  
  <style scoped>
  .category-divider-text {
    font-size: 18px;
    font-weight: bold;
    color: #409EFF;
  }
  </style>
  