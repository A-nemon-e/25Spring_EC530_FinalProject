<template>
  <div class="main-container">
    <!-- 侧边栏 -->
    <!-- <div class="sidebar">
      <div class="sidebar-title">导航</div>
      <el-menu router default-active="/search">
        <el-menu-item index="/search">搜索</el-menu-item>
        <el-menu-item index="/folder/0">文件夹视图</el-menu-item>
        <el-divider />
        <el-menu-item disabled>标签管理（待开发）</el-menu-item>
        <el-menu-item disabled>别名设置（待开发）</el-menu-item>
      </el-menu>
    </div> -->

    <!-- 主体 -->
    <div class="content-area">
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
                <div style="font-weight: bold; font-size: 16px;">
                  {{ getFileTitle(file) }}
                </div>
                <div v-if="getTitleAliases(file).length > 0" style="font-size: 12px; color: gray;">
                  别名：{{ getTitleAliases(file).join(" / ") }}
                </div>
                <div style="font-size: 12px; color: gray; margin-top: 4px;">
                  上传时间：{{ formatDate(file.uploaded_at) }}
                </div>
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
                <div style="margin-top: 8px;">
                  <el-tag
                    v-for="tag in getOtherTags(file)"
                    :key="tag.id"
                    :color="searchStore.getCategoryColor(tag.category)"
                    size="small"
                    style="margin-right: 6px; color: #505055; font-size: 14px; padding: 6px 10px;"
                  >
                    {{ tag.name }}（{{ tag.category }}）
                  </el-tag>
                </div>
              </div>
              <div style="text-align: right;">
                <el-button size="small" type="primary">下载</el-button>
                <el-button size="small" @click.stop="goToFileDetail(file.id)">详情</el-button>
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
    </div>
  </div>
</template>
<script setup>
// import { ref, computed, nextTick } from 'vue'
import { computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '../stores/searchStore'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Folder } from '@element-plus/icons-vue'

const router = useRouter()

// const keyword = ref('')
// const mode = ref('tag')
// const tags = ref([])
// const folders = ref([])
// const selectedItems = ref([])
// const fileResults = ref([])
// const fileTotal = ref(0)
// const currentPage = ref(1)
// const pageSize = ref(20)
const searchStore = useSearchStore()
const {
  keyword,
  mode,
  tags,
  folders,
  selectedItems,
  fileResults,
  fileTotal,
  currentPage,
  pageSize
} = storeToRefs(searchStore)

// ✅ 标签分类分组
const groupedTags = computed(() => {
  const groups = {}
  for (const tag of tags.value) {
    if (!groups[tag.category]) groups[tag.category] = []
    groups[tag.category].push(tag)
  }
  return groups
})

// // ✅ 颜色映射
// const categoryColorMap = ref({})
// const availableColors = [
//   '#f7e1d7', '#edbfb8', '#dedbd2', '#b0c4b1',
//   '#4a5759', '#78290f', '#b8b8ff', '#E84393'
// ]
// let colorIndex = 0
// const getCategoryColor = (category) => {
//   if (!categoryColorMap.value[category]) {
//     categoryColorMap.value[category] = availableColors[colorIndex % availableColors.length]
//     colorIndex++
//   }
//   return categoryColorMap.value[category]
// }


// 使用方法（在模板或 JS 中）



// ✅ 搜索标签或文件夹
const search = async () => {
  if (mode.value === 'tag') {
    const res = await axios.get('http://localhost:5000/api/tags', { params: { q: keyword.value } })
    tags.value = res.data.data
    folders.value = []
    if (tags.value.length === 1) addItem(tags.value[0], 'tag')
  }
  if (mode.value === 'folder') {
    const res = await axios.get('http://localhost:5000/api/folders/search', { params: { q: keyword.value } })
    folders.value = res.data.data
    tags.value = []
  }
}

// ✅ 添加已选项
const addItem = (item, type) => {
  if (!selectedItems.value.find(t => t.id === item.id && t.type === type)) {
    selectedItems.value.push({ id: item.id, name: item.name, type })
  }
}

// ✅ 移除已选项
const removeItem = (item) => {
  selectedItems.value = selectedItems.value.filter(t => !(t.id === item.id && t.type === item.type))
}

// ✅ 跳转管理标签（预留）
const manageTag = (tag) => {
  alert(`跳转管理标签：${tag.name}`)
}

// ✅ 跳转文件夹页面
const openFolder = (folderId) => {
  router.push(`/folder/${folderId}`)
}

// ✅ 跳转文件详情页
const goToFileDetail = (fileId) => {
  router.push(`/file/${fileId}`)
}

// ✅ 获取主标题
const getFileTitle = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag ? titleTag.name : `[无标题] - ${file.name}`
}

// ✅ 获取 title 别名
const getTitleAliases = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag?.aliases?.map(a => a.name) || []
}

// ✅ 其他标签（非 title）
const getOtherTags = (file) => {
  return file.tags.filter(t => t.category !== 'title')
}

// ✅ 格式化时间
const formatDate = (ts) => new Date(ts).toLocaleString()

// ✅ 跳转到文件夹
const goToFolder = (folderId) => {
  router.push(`/folder/${folderId}`)
}

// ✅ 实际请求
const fetchFiles = async () => {
  const tagIds = selectedItems.value.filter(i => i.type === 'tag').map(i => i.id)
  const folderIds = selectedItems.value.filter(i => i.type === 'folder').map(i => i.id)

  const params = new URLSearchParams()
  if (tagIds.length) params.append('tag_ids', tagIds.join(','))
  if (folderIds.length) params.append('folder_ids', folderIds.join(','))
  params.append('page', currentPage.value)
  params.append('size', pageSize.value)

  try {
    const res = await axios.get(`http://localhost:5000/api/files?${params}`)
    const { files, total } = res.data.data
    fileResults.value = files || []
    fileTotal.value = total || 0
  } catch (err) {
    console.error('文件查询失败:', err)
    fileResults.value = []
    fileTotal.value = 0
  }
}

// ✅ 搜索文件并滚动
const searchFiles = async () => {
  currentPage.value = 1
  await fetchFiles()
  nextTick(() => {
    const target = document.getElementById('file-result-block')
    if (target) target.scrollIntoView({ behavior: 'smooth' })
  })
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchFiles()
}



</script>

<style scoped>
.main-container {
  display: flex;
}
.sidebar {
  width: 200px;
  padding: 16px;
  border-right: 1px solid #ddd;
  min-height: 100vh;
}
.sidebar-title {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 16px;
}
.content-area {
  flex: 1;
  background-color: #fafafa;
}
.category-divider-text {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}
</style>
