<template>
  <div class="folder-explorer-container">
    <div class="content-wrapper">
      <!-- 面包屑导航 -->
      <div class="breadcrumb-section">
        <div class="breadcrumb-header">
          <h2 class="breadcrumb-title">📂 文件夹浏览</h2>
          <div class="breadcrumb-nav">
            <div 
              v-for="(part, index) in currentPath" 
              :key="index"
              class="breadcrumb-item"
              @click="goToFolder(part.id)"
            >
              <span class="breadcrumb-text">{{ part.name }}</span>
              <span v-if="index < currentPath.length - 1" class="breadcrumb-separator">/</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 子文件夹区域 -->
      <div v-if="folders.length > 0" class="folders-section">
        <h3 class="section-title">📁 子文件夹</h3>
        <div class="folder-grid">
          <div
            v-for="folder in folders"
            :key="folder.id"
            class="folder-card"
            @click="goToFolder(folder.id)"
          >
            <div class="folder-icon">📁</div>
            <div class="folder-name">{{ folder.name }}</div>
            <div class="folder-arrow">→</div>
          </div>
        </div>
      </div>

      <!-- 文件区域 -->
      <div v-if="files.length > 0" class="files-section">
        <h3 class="section-title">📄 文件列表</h3>
        <div class="file-list">
          <div
            v-for="file in files"
            :key="file.id"
            class="file-card"
          >
            <!-- 文件缩略图 -->
            <div class="file-thumbnail">
              <div class="thumbnail-icon">📄</div>
            </div>

            <!-- 文件信息 -->
            <div class="file-info">
              <!-- 主标题 -->
              <h4 class="file-title">{{ getFileTitle(file) }}</h4>
              
              <!-- 基本信息 -->
              <div class="file-meta">
                <div class="meta-item">
                  <span class="meta-icon">📅</span>
                  <span class="meta-text">{{ formatDate(file.uploaded_at) }}</span>
                </div>
                <div v-if="file.size" class="meta-item">
                  <span class="meta-icon">📊</span>
                  <span class="meta-text">{{ formatSize(file.size) }}</span>
                </div>
              </div>

              <!-- 所属路径 -->
              <div v-if="file.folders?.length > 0" class="file-paths">
                <span class="paths-label">📍 路径：</span>
                <div class="paths-list">
                  <span
                    v-for="folder in file.folders"
                    :key="folder.id"
                    class="path-item"
                    @click.stop="goToFolder(folder.id)"
                  >
                    {{ folder.full_path?.join(" / ") }}
                  </span>
                </div>
              </div>

              <!-- 标签展示 -->
              <div v-if="getOtherTags(file).length > 0" class="file-tags">
                <div class="tags-list">
                  <div
                    v-for="tag in getOtherTags(file)"
                    :key="tag.id"
                    class="tag-item"
                  >
                    <span class="tag-name">{{ tag.name }}</span>
                    <span class="tag-category">{{ tag.category }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="file-actions">
              <el-button type="primary" size="small" class="action-btn primary">
                <span class="btn-icon">⬇️</span>
                下载
              </el-button>
              <el-button size="small" class="action-btn secondary" @click.stop="goToFile(file.id)">
                <span class="btn-icon">👁️</span>
                详情
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="folders.length === 0 && files.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-title">此文件夹为空</div>
        <div class="empty-description">暂无文件夹或文件</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useFolderExplorerStore } from '../stores/folderStore'

const route = useRoute()
const router = useRouter()
const store = useFolderExplorerStore()

// 响应式 refs
const { folderId, folders, files, currentPath } = storeToRefs(store)
// 方法
const { loadAllFolders, loadFolder } = store

// 初始加载
onMounted(async () => {
  await loadAllFolders()
  if (route.params.id) {
    await loadFolder(route.params.id)
  }
})

// 导航功能
const goToFolder = async (id) => {
  if (id !== route.params.id) {
    await loadFolder(id)
    router.push(`/folder/${id}`)
  } else {
    await loadFolder(id)
  }
}

const goToFile = (fileId) => {
  router.push(`/file/${fileId}`)
}

// 工具函数
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

const formatSize = (bytes) => {
  if (!bytes) return ''
  return `${(bytes / 1024).toFixed(1)} KB`
}
</script>

<style scoped>
.folder-explorer-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  padding: 32px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* 面包屑区域 */
.breadcrumb-section {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.breadcrumb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.breadcrumb-title {
  font-size: 28px;
  font-weight: 700;
  color: #1890ff;
  margin: 0;
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.breadcrumb-item:hover .breadcrumb-text {
  color: #40a9ff;
  transform: translateX(2px);
}

.breadcrumb-text {
  color: #1890ff;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%);
  transition: all 0.3s ease;
}

.breadcrumb-separator {
  color: #8c9eff;
  margin: 0 4px;
  font-weight: 600;
}

/* 公共区域样式 */
.folders-section, .files-section {
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

/* 文件夹网格 */
.folder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.folder-card {
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.folder-card:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.2);
}

.folder-card:hover .folder-arrow {
  opacity: 1;
  transform: translateX(0);
}

.folder-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.folder-name {
  font-weight: 600;
  color: #1890ff;
  font-size: 16px;
  word-break: break-word;
}

.folder-arrow {
  position: absolute;
  top: 16px;
  right: 16px;
  color: #1890ff;
  font-weight: bold;
  font-size: 18px;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

/* 文件列表 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.file-card {
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.file-card:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateX(4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.15);
}

/* 文件缩略图 */
.file-thumbnail {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
  border: 2px solid #d6e9ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail-icon {
  font-size: 24px;
  opacity: 0.6;
}

/* 文件信息 */
.file-info {
  flex: 1;
}

.file-title {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.file-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #5a6c7d;
}

.meta-icon {
  font-size: 12px;
}

.meta-text {
  font-weight: 500;
}

.file-paths {
  margin-bottom: 12px;
}

.paths-label {
  font-size: 14px;
  color: #5a6c7d;
  font-weight: 600;
}

.paths-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.path-item {
  color: #1890ff;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #d6e9ff;
  transition: all 0.3s ease;
}

.path-item:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateY(-1px);
}

.file-tags {
  margin-top: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 8px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.tag-name {
  color: #2c3e50;
  font-weight: 500;
}

.tag-category {
  background: #1890ff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

/* 操作按钮 */
.file-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  min-width: 80px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 1px solid #d6e9ff;
  color: #1890ff;
}

.action-btn.secondary:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #d6e9ff 100%);
  transform: translateY(-1px);
}

.btn-icon {
  margin-right: 4px;
  font-size: 12px;
}

/* 空状态 */
.empty-state {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 80px 32px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
  opacity: 0.6;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 12px;
}

.empty-description {
  color: #8c9eff;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .folder-explorer-container {
    padding: 16px;
  }
  
  .breadcrumb-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .folder-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .file-card {
    flex-direction: column;
    text-align: center;
  }
  
  .file-actions {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }
  
  .section-title {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .folder-grid {
    grid-template-columns: 1fr;
  }
  
  .file-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .paths-list {
    flex-direction: column;
  }
  
  .file-actions {
    flex-direction: column;
  }
}
</style>