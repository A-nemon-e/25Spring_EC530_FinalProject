<template>
  <div class="search-container">
    <div class="content-wrapper">
      <!-- 搜索头部区域 -->
      <div class="search-header">
        <h1 class="page-title">🔍 搜索</h1>
        <div class="search-bar">
          <div class="search-inputs">
            <el-input 
              v-model="keyword" 
              placeholder="请输入关键词..." 
              class="keyword-input"
              size="large"
            >
              <template #prefix>
                <span class="input-icon">🔎</span>
              </template>
            </el-input>
            <el-select 
              v-model="mode" 
              placeholder="搜索类型" 
              class="mode-select"
              size="large"
            >
              <el-option label="🏷️ 标签" value="tag" />
              <el-option label="📁 文件夹" value="folder" />
            </el-select>
            <el-button 
              type="primary" 
              @click="search" 
              size="large"
              class="search-btn"
            >
              <span class="btn-icon">🚀</span>
              搜索
            </el-button>
          </div>
        </div>
      </div>

      <!-- 固定的已选标签栏 -->
      <div v-if="selectedItems.length > 0" class="selected-items-bar">
        <div class="selected-items-content">
          <div class="selected-title">
            <span class="title-icon">✨</span>
            已选择 ({{ selectedItems.length }})
          </div>
          <div class="selected-tags">
            <el-tag
              v-for="item in selectedItems"
              :key="`${item.type}-${item.id}`"
              closable
              @close="removeItem(item)"
              type="primary"
              size="large"
              class="selected-tag"
            >
              <span class="tag-type-icon">{{ item.type === 'tag' ? '🏷️' : '📁' }}</span>
              {{ item.name }}
            </el-tag>
          </div>
          <el-button 
            type="success" 
            @click="searchFiles" 
            size="large"
            class="search-files-btn"
          >
            <span class="btn-icon">📋</span>
            搜索文件
          </el-button>
        </div>
      </div>

      <!-- 标签搜索结果 -->
      <div v-if="tags.length > 0" class="search-results-section">
        <h3 class="section-title">🏷️ 标签搜索结果</h3>
        <div class="tags-container">
          <div 
            v-for="(tagGroup, category) in groupedTags" 
            :key="category" 
            class="tag-category-group"
          >
            <div class="category-header" @click="toggleCategory(category)">
              <div class="category-info">
                <span class="category-name">{{ category }}</span>
                <el-tag size="small" type="info" class="count-tag">{{ tagGroup.length }}</el-tag>
              </div>
              <div class="category-actions">
                <span class="expand-icon" :class="{ 'expanded': !collapsedCategories[category] }">
                  {{ collapsedCategories[category] ? '▶️' : '🔽' }}
                </span>
              </div>
            </div>
            
            <div 
              v-show="!collapsedCategories[category]" 
              class="tag-grid"
            >
              <div
                v-for="tag in tagGroup"
                :key="tag.id"
                class="tag-card"
              >
                <div class="tag-card-content">
                  <div class="tag-main-info">
                    <div class="tag-name">{{ tag.name }}</div>
                    <div class="tag-aliases">
                      <template v-if="tag.aliases.length > 0">
                        <el-tag
                          v-for="alias in tag.aliases"
                          :key="alias.id"
                          type="info"
                          size="small"
                          effect="plain"
                          class="alias-tag"
                        >
                          {{ alias.name }}
                        </el-tag>
                      </template>
                      <template v-else>
                        <span class="no-alias">暂无别名</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="tag-actions">
                    <el-button size="small" class="manage-btn" @click="manageTag(tag)">
                      <span class="btn-icon">⚙️</span>
                      管理
                    </el-button>
                    <el-button 
                      size="small" 
                      type="primary" 
                      class="add-btn"
                      @click="addItem(tag, 'tag')"
                    >
                      <span class="btn-icon">➕</span>
                      添加
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件夹搜索结果 -->
      <div v-if="folders.length > 0" class="search-results-section">
        <h3 class="section-title">📁 文件夹搜索结果</h3>
        <div class="folder-list">
          <div
            v-for="folder in folders"
            :key="folder.id"
            class="folder-card"
          >
            <div class="folder-info">
              <div class="folder-icon">📁</div>
              <div class="folder-path">{{ folder.full_path.join(" / ") }}</div>
            </div>
            <div class="folder-actions">
              <el-button
                size="small"
                class="view-btn"
                @click="openFolder(folder.id)"
              >
                <span class="btn-icon">👁️</span>
                查看
              </el-button>
              <el-button 
                size="small" 
                type="primary" 
                class="add-btn"
                @click="addItem(folder, 'folder')"
              >
                <span class="btn-icon">➕</span>
                添加
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件搜索结果 -->
      <div v-if="fileResults.length > 0" id="file-result-block" class="search-results-section">
        <h3 class="section-title">📄 文件搜索结果</h3>
        <div class="file-list">
          <div
            v-for="file in fileResults"
            :key="file.id"
            class="file-card"
          >
            <div class="file-main-content">
              <div class="file-header">
                <div class="file-title">{{ getFileTitle(file) }}</div>
                <div class="file-actions">
                  <el-button size="small" type="primary" class="download-btn">
                    <span class="btn-icon">⬇️</span>
                    下载
                  </el-button>
                  <el-button 
                    size="small" 
                    class="detail-btn"
                    @click.stop="goToFileDetail(file.id)"
                  >
                    <span class="btn-icon">📋</span>
                    详情
                  </el-button>
                </div>
              </div>
              
              <div v-if="getTitleAliases(file).length > 0" class="file-aliases">
                <span class="aliases-label">别名：</span>
                <span class="aliases-text">{{ getTitleAliases(file).join(" / ") }}</span>
              </div>
              
              <div class="file-meta">
                <div class="meta-item">
                  <span class="meta-icon">📅</span>
                  <span class="meta-text">{{ formatDate(file.uploaded_at) }}</span>
                </div>
              </div>
              
              <div v-if="file.folders.length > 0" class="file-folders">
                <span class="folders-label">📂 所属路径：</span>
                <div class="folder-paths">
                  <span
                    v-for="folder in file.folders"
                    :key="folder.id"
                    @click="goToFolder(folder.id)"
                    class="folder-path-link"
                  >
                    {{ folder.full_path.join(" / ") }}
                  </span>
                </div>
              </div>
              
              <div v-if="getOtherTags(file).length > 0" class="file-tags">
                <el-tag
                  v-for="tag in getOtherTags(file)"
                  :key="tag.id"
                  :style="{ backgroundColor: searchStore.getCategoryColor(tag.category) }"
                  size="small"
                  class="file-tag"
                >
                  {{ tag.name }}（{{ tag.category }}）
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination-container">
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
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '../stores/searchStore'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
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

// 分类折叠状态
const collapsedCategories = ref({})

// 标签分类分组
const groupedTags = computed(() => {
  const groups = {}
  for (const tag of tags.value) {
    if (!groups[tag.category]) groups[tag.category] = []
    groups[tag.category].push(tag)
  }
  return groups
})

// 切换分类展开/收起
const toggleCategory = (category) => {
  collapsedCategories.value[category] = !collapsedCategories.value[category]
}

// 搜索标签或文件夹
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

// 添加已选项
const addItem = (item, type) => {
  if (!selectedItems.value.find(t => t.id === item.id && t.type === type)) {
    selectedItems.value.push({ id: item.id, name: item.name, type })
  }
}

// 移除已选项
const removeItem = (item) => {
  selectedItems.value = selectedItems.value.filter(t => !(t.id === item.id && t.type === item.type))
}

// 跳转管理标签
const manageTag = (tag) => {
  alert(`跳转管理标签：${tag.name}`)
}

// 跳转文件夹页面
const openFolder = (folderId) => {
  router.push(`/folder/${folderId}`)
}

// 跳转文件详情页
const goToFileDetail = (fileId) => {
  router.push(`/file/${fileId}`)
}

// 获取主标题
const getFileTitle = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag ? titleTag.name : `[无标题] - ${file.name}`
}

// 获取 title 别名
const getTitleAliases = (file) => {
  const titleTag = file.tags.find(t => t.category === 'title')
  return titleTag?.aliases?.map(a => a.name) || []
}

// 其他标签（非 title）
const getOtherTags = (file) => {
  return file.tags.filter(t => t.category !== 'title')
}

// 格式化时间
const formatDate = (ts) => new Date(ts).toLocaleString()

// 跳转到文件夹
const goToFolder = (folderId) => {
  router.push(`/folder/${folderId}`)
}

// 实际请求
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

// 搜索文件并滚动
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
.search-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  padding: 32px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

.search-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.page-title {
  font-size: 30px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 24px 0;
  text-align: center;
}

.search-bar {
  display: flex;
  justify-content: center;
}

.search-inputs {
  display: flex;
  gap: 16px;
  align-items: center;
}

.keyword-input {
  width: 320px;
}

.keyword-input :deep(.el-input__inner) {
  border-radius: 12px;
  border: 2px solid #d6e9ff;
  transition: all 0.3s ease;
}

.keyword-input :deep(.el-input__inner:focus) {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.mode-select {
  width: 160px;
}

.mode-select :deep(.el-select__wrapper) {
  border-radius: 12px;
  border: 2px solid #d6e9ff;
}

.search-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  padding: 12px 24px;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
}

.input-icon, .btn-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 固定已选标签栏 */
.selected-items-bar {
  position: sticky;
  top: 20px;
  z-index: 100;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.15);
  border: 2px solid #d6e9ff;
}

.selected-items-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.selected-title {
  font-weight: 600;
  color: #1890ff;
  font-size: 16px;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.title-icon {
  margin-right: 8px;
  font-size: 18px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  
  gap: 8px;
  flex: 1;
}

.selected-tag {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  padding: 8px 10px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  display: flex;
  align-items: center;
}

.tag-type-icon {
  margin-right: 6px;
}

.search-files-btn {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  border: none;
  padding: 10px 20px;
  font-weight: 600;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(82, 196, 26, 0.3);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-files-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(82, 196, 26, 0.4);
}

/* 搜索结果区域 */
.search-results-section {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 24px 0;
}

/* 标签分类组 */
.tags-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tag-category-group {
  border-radius: 16px;
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #e6f3ff 0%, #d6e9ff 100%);
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-header:hover {
  background: linear-gradient(135deg, #d6e9ff 0%, #bae0ff 100%);
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-name {
  font-weight: 600;
  color: #1890ff;
  font-size: 18px;
}

.count-tag {
  background: #1890ff;
  color: white;
  border: none;
}

.expand-icon {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.expand-icon.expanded {
  transform: rotate(0deg);
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 20px;
}

.tag-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.tag-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.2);
}

.tag-card-content {
  padding: 20px;
}

.tag-main-info {
  margin-bottom: 16px;
}

.tag-name {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.tag-aliases {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 24px;
  align-items: center;
}

.alias-tag {
  font-size: 13px;
  padding: 4px 8px;
}

.no-alias {
  color: #8c9eff;
  font-size: 12px;
  font-style: italic;
}

.tag-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.manage-btn {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 1px solid #d6e9ff;
  color: #1890ff;
}

.add-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  color: white;
}

/* 文件夹列表 */
.folder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.folder-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 12px;
  padding: 16px 20px;
  transition: all 0.3s ease;
}

.folder-card:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
}

.folder-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.folder-icon {
  font-size: 20px;
}

.folder-path {
  color: #1890ff;
  font-weight: 500;
}

.folder-actions {
  display: flex;
  gap: 8px;
}

.view-btn {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 1px solid #d6e9ff;
  color: #1890ff;
}

/* 文件列表 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-card {
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.file-card:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.15);
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.file-title {
  font-weight: 600;
  font-size: 18px;
  color: #2c3e50;
  flex: 1;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.download-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  color: white;
}

.detail-btn {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 1px solid #d6e9ff;
  color: #1890ff;
}

.file-aliases {
  margin-bottom: 8px;
  font-size: 14px;
}

.aliases-label {
  color: #8c9eff;
  font-weight: 500;
}

.aliases-text {
  color: #5a6c7d;
}

.file-meta {
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #5a6c7d;
}

.meta-icon {
  margin-right: 6px;
}

.file-folders {
  margin-bottom: 12px;
  font-size: 14px;
}

.folders-label {
  color: #1890ff;
  font-weight: 500;
  margin-bottom: 6px;
  display: block;
}

.folder-paths {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.folder-path-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.folder-path-link:hover {
  color: #40a9ff;
}

.file-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-tag {
  color: #2c3e50 !important;
  font-size: 12px;
  padding: 4px 8px;
  border: none;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e6f3ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-container {
    padding: 16px;
  }
  
  .search-inputs {
    flex-direction: column;
    width: 100%;
  }
  
  .keyword-input, .mode-select {
    width: 100%;
  }
  
  .selected-items-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .tag-grid {
    grid-template-columns: 1fr;
  }
  
  .file-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .file-actions {
    align-self: flex-end;
  }
}
</style>