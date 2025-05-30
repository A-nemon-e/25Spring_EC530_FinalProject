<template>
  <div v-if="fileData" class="file-detail-container">
    <!-- 主内容区域 -->
    <div class="content-wrapper">
      <!-- 头部区域 -->
      <div class="header-section">
        <!-- 缩略图 -->
        <div class="thumbnail-container">
          <div class="thumbnail-placeholder">
            <div class="thumbnail-icon">📄</div>
            <div class="thumbnail-text">PDF 预览</div>
          </div>
        </div>

        <!-- 文件信息卡片 -->
        <div class="file-info-card">
          <!-- 主标题 -->
          <div class="title-section">
            <h1 class="file-title" @click="openTagEditor(titleTag)">
              <el-tooltip
                v-if="titleAliases.length > 0"
                effect="dark"
                :content="titleAliases.join(' / ')"
                placement="top"
              >
                <span>{{ title }}</span>
              </el-tooltip>
              <span v-else>{{ title }}</span>
            </h1>
            <el-tag 
              v-if="isFallbackTitle" 
              type="warning" 
              size="small" 
              class="fallback-tag"
            >
              无Title标签，显示文件名
            </el-tag>
          </div>

          <!-- 文件基本信息 -->
          <div class="basic-info">
            <div class="info-item">
              <span class="info-label">📍 文件路径</span>
              <span class="info-value">{{ fileData.upload_path }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">📅 上传时间</span>
              <span class="info-value">{{ formatDate(fileData.uploaded_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">📊 文件大小</span>
              <span class="info-value">{{ formatSize(fileData.size) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button @click="downloadFile(fileData.id)" type="primary" size="large" class="primary-btn">
              <span class="btn-icon">⬇️</span>
              下载文件
            </el-button>
            <el-button size="large" class="secondary-btn" @click="editFile">
              <span class="btn-icon">✏️</span>
              编辑
            </el-button>
            <el-button type="danger" size="large" class="danger-btn" @click="deleteFile">
              <span class="btn-icon">🗑️</span>
              删除文件
            </el-button>

          </div>
        </div>
      </div>

      <!-- 标签区域 -->
      <div class="tags-section">
        <h3 class="section-title" style="display: inline;">🏷️ 标签信息</h3>
        <h6 class="section-subtitle" style="display: inline; margin-left: 8px;">（点击编辑）</h6>
        <div class="tags-container">
          <div 
            v-for="(tags, category) in groupedTags" 
            :key="category" 
            class="tag-category"
          >
            <div class="category-header">
              <span class="category-name">{{ category }}</span>
              <div class="category-line"></div>
            </div>
            <div class="tag-list">
              <div 
                v-for="tag in tags" 
                :key="tag.id"
                class="tag-item"
                @click="openTagEditor(tag)"
              >
                <el-tooltip
                  v-if="tag.aliases.length > 0"
                  effect="dark"
                  :content="tag.aliases.map(a => a.name).join(' / ')"
                  placement="top"
                >
                  <div class="tag-content">
                    <span class="tag-name">{{ tag.name }}</span>
                    <span class="alias-count">+{{ tag.aliases.length }}</span>
                  </div>
                </el-tooltip>
                <div v-else class="tag-content">
                  <span class="tag-name">{{ tag.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 所属路径区域 -->
      <div v-if="fileData?.folders?.length > 0" class="folders-section">
        <h3 class="section-title">📂 所属路径</h3>
        <div class="folder-list">
          <div
            v-for="folder in fileData.folders"
            :key="folder.id"
            class="folder-item"
            @click="goToFolder(folder.id)"
          >
            <div class="folder-path">
              {{ buildFullPath(folder.id).join(" / ") }}
            </div>
            <div class="folder-arrow">→</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签编辑对话框 -->
    <el-dialog
      v-model="isTagEditorVisible"
      title="编辑标签"
      width="500px"
      class="tag-dialog"
    >
      <div class="dialog-content">
        <p>标签编辑功能正在开发中...</p>
        <div class="dialog-placeholder">
          <div class="placeholder-icon">🔧</div>
          <div class="placeholder-text">敬请期待</div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="isTagEditorVisible = false">取消</el-button>
          <el-button type="primary" @click="isTagEditorVisible = false">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>

  <!-- 骨架屏 -->
  <div v-else class="skeleton-container">
    <div class="skeleton-content">
      <el-skeleton rows="8" animated />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFileStore } from '../stores/fileStore'
import axios from 'axios'

const store = useFileStore()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  store.loadFileData(route.params.id)
})

const buildFullPath = store.buildFullPath
const fileData = computed(() => store.fileData)

const titleTag = computed(() =>
  fileData.value?.tags?.find((t) => t.category === 'title') ?? null
)

const title = computed(() =>
  titleTag.value ? titleTag.value.name : fileData.value?.name ?? ''
)

const titleAliases = computed(() =>
  titleTag.value ? titleTag.value.aliases.map((a) => a.name) : []
)

const isFallbackTitle = computed(() => !titleTag.value)

const groupedTags = computed(() => {
  const result = {}
  if (!fileData.value?.tags) return result
  for (const tag of fileData.value.tags) {
    if (tag.category === 'title') continue
    if (!result[tag.category]) result[tag.category] = []
    result[tag.category].push(tag)
  }
  return result
})

const isTagEditorVisible = ref(false)
const currentEditingTag = ref(null)

const formatDate = (str) => new Date(str).toLocaleString()
const formatSize = (bytes) => `${(bytes / 1024).toFixed(1)} KB`
const goToFolder = (id) => router.push(`/folder/${id}`)

const downloadFile = async (fileId) => {
  try {
    const response = await axios.get(`/api/files/download/${fileId}`, {
      responseType: 'blob', // 关键点：告诉 axios 这是一个二进制流
    })

    // 从后端 Content-Disposition 中解析文件名（可选）
    let filename = 'downloaded.pdf'
    const disposition = response.headers['content-disposition']
    if (disposition && disposition.includes('filename=')) {
      filename = decodeURIComponent(disposition.split('filename=')[1].replace(/["']/g, ''))
    }

    // 创建 blob 链接
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)

    // 创建 a 标签触发下载
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // 释放 URL 对象
    window.URL.revokeObjectURL(url)
  } catch (err) {
    alert(err+'下载失败')
  }
}


const openTagEditor = (tag) => {
  if (!tag && !title) return
  currentEditingTag.value = tag
  isTagEditorVisible.value = true
}

const editFile = () => {
  if (!fileData.value?.id) {
    alert('当前文件无 ID，无法编辑')
    return
  }
  router.push({
    path: '/tagger',
    query: { id: fileData.value?.id }
  })
}
const deleteFile = async () => {
  if (!fileData.value?.id) {
    alert('无法删除：文件 ID 缺失')
    return
  }

  const confirmed = window.confirm('确定要删除此文件吗？此操作无法撤销。')
  if (!confirmed) return

  try {
    const response = await fetch(`/api/files/${fileData.value.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()

    if (data.code === 200) {
      alert('文件删除成功')
      router.back()  // 🔁 返回上一页
    } else {
      alert('删除失败：' + (data.error || '未知错误'))
    }
  } catch (err) {
    alert('删除请求失败：' + err.message)
    console.error(err)
  }
}

</script>

<style scoped>
.file-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  padding: 32px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  gap: 32px;
  margin-bottom: 40px;
  align-items: flex-start;
}

.thumbnail-container {
  flex-shrink: 0;
}

.thumbnail-placeholder {
  width: 240px;
  height: 320px;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
  border: 2px dashed #d6e9ff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.1);
  transition: all 0.3s ease;
}

.thumbnail-placeholder:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(24, 144, 255, 0.15);
}

.thumbnail-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.thumbnail-text {
  color: #8c9eff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.file-info-card {
  flex: 1;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.title-section {
  margin-bottom: 32px;
}

.file-title {
  font-size: 32px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 12px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  line-height: 1.2;
}

.file-title:hover {
  color: #40a9ff;
  transform: translateX(4px);
}

.fallback-tag {
  font-size: 12px;
  padding: 4px 8px;
}

.basic-info {
  margin-bottom: 32px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f7ff;
}

.info-label {
  font-weight: 600;
  color: #5a6c7d;
  width: 120px;
  font-size: 14px;
}

.info-value {
  color: #2c3e50;
  font-size: 14px;
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.primary-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
}

.secondary-btn {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 1px solid #d6e9ff;
  color: #1890ff;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.secondary-btn:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #d6e9ff 100%);
  transform: translateY(-2px);
}

.btn-icon {
  margin-right: 8px;
  font-size: 16px;
}

.tags-section, .folders-section {
  margin-bottom: 40px;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 24px 0;
}

.section-subtitle {
  font-size: 15px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 24px 0;
}

.tags-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tag-category {
  border-radius: 12px;
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  padding: 20px;
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.category-name {
  font-weight: 600;
  color: #1890ff;
  font-size: 16px;
  margin-right: 16px;
}

.category-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, #1890ff 0%, transparent 100%);
  border-radius: 1px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-item {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.08);
}

.tag-item:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-name {
  color: #2c3e50;
  font-weight: 500;
  font-size: 14px;
}

.alias-count {
  background: #1890ff;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 600;
}

.folder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.folder-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border: 1px solid #d6e9ff;
  border-radius: 12px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.folder-item:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #f0f7ff 100%);
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
}

.folder-path {
  color: #1890ff;
  font-weight: 500;
  text-decoration: underline;
}

.folder-arrow {
  color: #1890ff;
  font-weight: bold;
  font-size: 18px;
}

.skeleton-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  padding: 32px;
}

.skeleton-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
}

.tag-dialog .dialog-content {
  text-align: center;
  padding: 40px 20px;
}

.dialog-placeholder {
  margin-top: 20px;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.placeholder-text {
  color: #8c9eff;
  font-weight: 600;
  font-size: 16px;
}
.danger-btn {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(255, 77, 79, 0.3);
  transition: all 0.3s ease;
}

.danger-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 77, 79, 0.4);
}


@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: center;
  }
  
  .thumbnail-placeholder {
    width: 200px;
    height: 260px;
  }
  
  .file-info-card {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>