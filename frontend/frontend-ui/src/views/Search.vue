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
          style="font-size: 15px; padding: 15px 8px;"
        >
          {{ item.name }}
        </el-tag>
        <el-button type="success" @click="searchFiles" style="font-size: 14px; padding: 1px 8px;">
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
<div v-if="fileResults.length > 0" id="file-result-block" style="margin-top: 40px">
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
      <!-- 主标题：title 标签或 fallback -->
      <div style="font-weight: bold; font-size: 16px;">
        {{ getFileTitle(file) }}
      </div>

      <!-- title 标签别名（如有） -->
      <div v-if="getTitleAliases(file).length > 0" style="font-size: 12px; color: gray;">
        别名：{{ getTitleAliases(file).join(' / ') }}
      </div>

      <!-- 上传时间 --> 
      <div style="font-size: 12px; color: gray; margin-top: 4px;">
        上传时间：{{ formatDate(file.uploaded_at) }}
      </div>

      <!-- 所属文件夹路径 -->
      <div v-if="file.folders.length > 0" style="margin-top: 6px; font-size: 12px;">
        所属路径：
        <span
          v-for="folder in file.folders"
          :key="folder.id"
          @click="goToFolder(folder.id)"
          style="margin-right: 12px; color: #409EFF; cursor: pointer; text-decoration: underline;"
        >
          {{ folder.full_path.join(" / ") }}
        </span>
      </div>

      <!-- 标签展示 -->
      <div style="margin-top: 8px;">
        <!-- <el-tag
          v-for="tag in getOtherTags(file)"
          :key="tag.id"
          type="info"
          size="small"
          style="margin-right: 6px;"
        >
          {{ tag.name }}（{{ tag.category }}）
        </el-tag> -->
        <el-tag
          v-for="tag in getOtherTags(file)"
          :key="tag.id"
          :color="getCategoryColor(tag.category)"
          size="small"
          style="margin-right: 6px; color: white;"
        >
          {{ tag.name }}（{{ tag.category }}）
        </el-tag>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div style="text-align: right;">
      <el-button size="small" type="primary">下载</el-button>
      <el-button size="small">详情</el-button>
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
  import { nextTick } from 'vue'

  // ✅ 分类 → 颜色 映射
  const categoryColorMap = ref({})

  // ✅ 可用颜色池（自动循环分配）
  const availableColors = [
    '#409EFFe0', // 蓝
    '#67C23Ae0', // 绿
    '#E6A23Ce0', // 橙
    '#F56C6Ce0', // 红
    '#909399e0', // 灰
    '#8E44ADe0', // 紫
    '#1abc9ce0', // 青
    '#E84393e0'  // 粉
  ]

  let colorIndex = 0

  //   ✅ 获取分类对应颜色
  const getCategoryColor = (category) => {
    if (!categoryColorMap.value[category]) {
      const color = availableColors[colorIndex % availableColors.length]
      categoryColorMap.value[category] = color
      colorIndex++
    }
    return categoryColorMap.value[category]
  }

  
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
  
  // const router = useRouter()
  
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
const searchFiles = async () => {
  currentPage.value = 1
  await fetchFiles()
  nextTick(() => {
    const target = document.getElementById("file-result-block")
    if (target) {
      target.scrollIntoView({ behavior: "smooth" })
    }
  })
}
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchFiles()
}


// import { useRouter } from 'vue-router'
const router = useRouter()

// 获取主标题（title 标签或文件名）
const getFileTitle = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag ? titleTag.name : file.name
}

// 获取 title 标签别名（你需要在后端把 aliases 一并传回来）（暂不实现，后端不传）
const getTitleAliases = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag && titleTag.aliases ? titleTag.aliases.map(a => a.name) : []
}

// 过滤掉 title 之外的标签
const getOtherTags = (file) => {
  return file.tags.filter(t => t.category !== 'title')
}

// 时间格式化为本地时区
const formatDate = (ts) => {
  const dt = new Date(ts)
  return dt.toLocaleString()
}

// 跳转文件夹页面
const goToFolder = (folderId) => {
  router.push(`/folder/${folderId}`)
}



  </script>
  
  <style scoped>
  .category-divider-text {
    font-size: 18px;
    font-weight: bold;
    color: #409EFF;
  }
  </style>
  