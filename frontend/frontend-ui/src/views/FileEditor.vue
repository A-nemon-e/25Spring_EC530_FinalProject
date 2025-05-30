<template>
  <div class="file-editor-container">
    <div class="content-wrapper">
      <!-- 头部卡片 -->
      <div class="header-card" v-loading="loading">
        <div class="header-icon">
          <div class="icon-wrapper">
            <span class="main-icon">✏️</span>
          </div>
        </div>
        <div class="header-content">
          <h1 class="page-title">编辑文件标签</h1>
          <p class="page-subtitle">为您的文件添加标签和分类，让内容更易管理</p>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="main-content">
        <el-form label-width="120px" class="custom-form">
          <!-- 文件名显示 -->
          <div class="form-section">
            <h3 class="section-title">📄 文件信息</h3>
            <div class="form-item-wrapper">
              <el-form-item label="文件名称">
                <div class="file-name-display">
                  <span class="file-icon">📋</span>
                  <span class="file-name">{{ file.name }}</span>
                </div>
              </el-form-item>
            </div>
          </div>

          <!-- 标签管理 -->
          <div class="form-section">
            <h3 class="section-title">🏷️ 标签管理</h3>
            <div class="form-item-wrapper">
              <el-form-item label="添加标签">
                <div class="tag-input-group">
                  <el-autocomplete
                    v-model="tagInput"
                    :fetch-suggestions="searchTags"
                    placeholder="输入主标签或别名进行搜索..."
                    @select="addTag"
                    class="tag-autocomplete"
                    clearable
                  >
                    <template #prefix>
                      <span class="input-icon">🔍</span>
                    </template>
                  </el-autocomplete>
                  <el-button 
                    type="primary" 
                    class="create-tag-btn"
                    @click="tryCreateTag"
                  >
                    <span class="btn-icon">➕</span>
                    创建新标签
                  </el-button>
                </div>
              </el-form-item>

              <!-- 已选标签展示 -->
              <el-form-item label="已选标签">
                <div class="selected-tags-container">
                  <div 
                    v-for="(tagGroup, category) in groupedTags" 
                    :key="category" 
                    class="tag-category-group"
                  >
                    <div class="category-header">
                      <span class="category-name">{{ category }}</span>
                      <div class="category-line"></div>
                    </div>
                    <div class="tag-list">
                      <el-tag
                        v-for="tag in tagGroup"
                        :key="tag.id"
                        closable
                        @close="removeTag(tag.id)"
                        class="custom-tag"
                        :type="getCategoryTagType(category)"
                      >
                        {{ tag.name }}
                      </el-tag>
                    </div>
                  </div>
                  <div v-if="Object.keys(groupedTags).length === 0" class="empty-tags">
                    <div class="empty-icon">🏷️</div>
                    <div class="empty-text">还没有添加任何标签</div>
                  </div>
                </div>
              </el-form-item>
            </div>
          </div>

          <!-- 文件夹选择 -->
          <div class="form-section">
            <h3 class="section-title">📂 保存位置</h3>
            <div class="form-item-wrapper">
              <el-form-item label="选择文件夹">
                <el-tree-select
                  v-model="selectedFolderIds"
                  :data="folderTree"
                  :props="{ label: 'name', children: 'children', value: 'id' }"
                  node-key="id"
                  default-expand-all
                  highlight-current
                  check-strictly
                  placeholder="选择任意数量文件夹"
                  multiple
                  class="folder-tree-select"
                />
              </el-form-item>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button type="primary" size="large" @click="submit" class="submit-btn">
              <span class="btn-icon">💾</span>
              保存修改
            </el-button>
            <el-button size="large" @click="$router.go(-1)" class="cancel-btn">
              <span class="btn-icon">↩️</span>
              返回
            </el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 创建标签对话框 -->
    <el-dialog 
      v-model="dialogCreateTag" 
      title="创建新标签" 
      width="480px"
      class="create-tag-dialog"
    >
      <div class="dialog-content">
        <div class="dialog-icon">
          <span>🏷️</span>
        </div>
        <el-form label-width="80px" class="dialog-form">
          <el-form-item label="标签名">
            <el-input 
              v-model="newTag.name" 
              placeholder="请输入标签名称"
              class="dialog-input"
            />
          </el-form-item>
          <el-form-item label="分类">
            <el-input 
              v-model="newTag.category" 
              placeholder="请输入标签分类"
              class="dialog-input"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogCreateTag = false" class="dialog-cancel-btn">
            取消
          </el-button>
          <el-button type="primary" @click="createTag" class="dialog-confirm-btn">
            <span class="btn-icon">✨</span>
            创建标签
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)

// 响应式数据
const file = ref({ name: '' })
const tagInput = ref('')
const selectedTags = ref([])
const selectedFolderIds = ref([])
const folderTree = ref([])

// 创建标签弹窗
const dialogCreateTag = ref(false)
const newTag = ref({ name: '', category: '' })

// 获取分类标签类型
const getCategoryTagType = (category) => {
  const typeMap = {
    'title': 'primary',
    'author': 'success',
    'subject': 'warning',
    'keyword': 'info'
  }
  return typeMap[category] || 'default'
}

// 搜索标签
const searchTags = async (queryString, cb) => {
  try {
    const res = await axios.get('/api/tags', { params: { q: queryString } })
    cb(res.data.data.map(tag => ({ value: tag.name, ...tag })))
  } catch {
    cb([])
  }
}

// 添加标签
const addTag = (tag) => {
  if (!tag || !tag.id || !tag.name) {
    ElMessage.warning('选择无效标签，请重新搜索')
    return
  }
  if (selectedTags.value.find(t => t.id === tag.id)) {
    ElMessage.warning('标签已添加')
    return
  }
  selectedTags.value.push(tag)
  tagInput.value = ''
}

// 删除标签
const removeTag = (id) => {
  selectedTags.value = selectedTags.value.filter(t => t.id !== id)
}

// 分组展示
const groupedTags = computed(() => {
  const groups = {}
  for (const tag of selectedTags.value) {
    if (!groups[tag.category]) groups[tag.category] = []
    groups[tag.category].push(tag)
  }
  return groups
})

// 打开创建标签弹窗
const tryCreateTag = () => {
  newTag.value = { name: tagInput.value, category: '' }
  dialogCreateTag.value = true
}

// 创建标签
const createTag = async () => {
  if (!newTag.value.name || !newTag.value.category) {
    ElMessage.warning('名称和分类不能为空')
    return
  }
  try {
    const res = await axios.post('/api/tags', newTag.value)
    const createdTag = Array.isArray(res.data.data) ? res.data.data[0] : res.data.data
    if (!createdTag || !createdTag.id) {
      ElMessage.error('创建失败，返回格式错误')
      return
    }
    selectedTags.value.push(createdTag)
    ElMessage.success(res.data.status || '创建成功')
    dialogCreateTag.value = false
    tagInput.value = ''
  } catch (err) {
    const { status, error } = err.response?.data || {}
    ElMessage.error(error ? `${status}：${error}` : (status || '创建失败'))
  }
}

// 获取文件夹树
const getFolders = async () => {
  try {
    const res = await axios.get('/api/folders/tree')
    folderTree.value = res.data.data
  } catch {
    folderTree.value = []
  }
}

// 加载文件详情
const loadFileData = async () => {
  const id = route.query.id
  if (!id) return
  loading.value = true
  try {
    const res = await axios.get(`/api/files/${id}`)
    file.value = res.data.data
    // 处理 tags
    const tagsData = file.value.tags || []
    if (tagsData.length && typeof tagsData[0] === 'number') {
      const allTagsRes = await axios.get('/api/tags')
      const allTags = allTagsRes.data.data
      selectedTags.value = allTags.filter(t => tagsData.includes(t.id))
    } else {
      selectedTags.value = tagsData
    }
    // 处理 folders
    const foldersData = file.value.folders || []
    selectedFolderIds.value = foldersData.map(f => (typeof f === 'object' ? f.id : f))
  } catch (err) {
    ElMessage.error('加载文件详情失败')
  } finally {
    loading.value = false
  }
}

// 提交修改
const submit = async () => {
  const id = route.query.id
  if (!id) return
  if (selectedTags.value.length === 0) {
    ElMessage.warning('请选择至少一个标签')
    return
  }
  if (!selectedTags.value.some(t => t && t.category === 'title')) {
    ElMessage.warning('必须至少选择一个 title 分类的标签')
    return
  }
  try {
    const res = await axios.put(`/api/files/${id}`, {
      tags: selectedTags.value.map(t => t.id),
      folders: selectedFolderIds.value
    })
    ElMessage.success(res.data.status || '修改成功')
  } catch (err) {
    const { status, error } = err.response?.data || {}
    ElMessage.error(error ? `${status}：${error}` : (status || '修改失败'))
  }
}

onMounted(() => {
  getFolders()
  loadFileData()
})
</script>

<style scoped>
.file-editor-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  padding: 32px;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.header-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-icon {
  flex-shrink: 0;
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.3);
}

.main-icon {
  font-size: 36px;
  filter: brightness(0) invert(1);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 16px;
  color: #5a6c7d;
  margin: 0;
  opacity: 0.8;
}

.main-content {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid #e6f3ff;
}

.custom-form {
  .el-form-item {
    margin-bottom: 0;
  }
}

.form-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1890ff;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-item-wrapper {
  background: linear-gradient(135deg, #f8faff 0%, #f0f7ff 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e6f3ff;
}

.file-name-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 12px;
  border: 2px solid #d6e9ff;
  font-weight: 500;
  color: #2c3e50;
}

.file-icon {
  font-size: 20px;
  opacity: 0.7;
}

.file-name {
  flex: 1;
  font-size: 16px;
}

.tag-input-group {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.tag-autocomplete {
  flex: 1;
}

.tag-autocomplete :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  border: 2px solid #e6f3ff;
  transition: all 0.3s ease;
}

.tag-autocomplete :deep(.el-input__wrapper:hover) {
  border-color: #bae0ff;
}

.tag-autocomplete :deep(.el-input__wrapper.is-focus) {
  border-color: #1890ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
}

.input-icon {
  color: #1890ff;
  font-size: 16px;
}

.create-tag-btn {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(82, 196, 26, 0.3);
  transition: all 0.3s ease;
}

.create-tag-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(82, 196, 26, 0.4);
}

.selected-tags-container {
  min-height: 100px;
}

.tag-category-group {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #d6e9ff;
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.category-name {
  font-weight: 600;
  color: #1890ff;
  font-size: 14px;
  margin-right: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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
  gap: 8px;
}

.custom-tag {
  border-radius: 8px;
  font-weight: 500;
  padding: 6px 12px;
  transition: all 0.3s ease;
}

.custom-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-tags {
  text-align: center;
  padding: 40px 20px;
  color: #8c9eff;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
}

.folder-tree-select {
  width: 100%;
}

.folder-tree-select :deep(.el-select__wrapper) {
  border-radius: 12px;
  border: 2px solid #e6f3ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  transition: all 0.3s ease;
}

.folder-tree-select :deep(.el-select__wrapper:hover) {
  border-color: #bae0ff;
}

.folder-tree-select :deep(.el-select__wrapper.is-focused) {
  border-color: #1890ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 32px;
  border-top: 2px solid #f0f7ff;
}

.submit-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  border-radius: 12px;
  padding: 16px 32px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.4);
}

.cancel-btn {
  background: linear-gradient(135deg, #f8faff 0%, #e6f3ff 100%);
  border: 2px solid #d6e9ff;
  color: #1890ff;
  border-radius: 12px;
  padding: 16px 32px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: linear-gradient(135deg, #e6f3ff 0%, #d6e9ff 100%);
  transform: translateY(-2px);
}

.btn-icon {
  margin-right: 8px;
  font-size: 16px;
}

.create-tag-dialog {
  border-radius: 16px;
}

.create-tag-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.create-tag-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  padding: 20px 24px;
}

.create-tag-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.dialog-content {
  padding: 24px;
  text-align: center;
}

.dialog-icon {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.dialog-form {
  text-align: left;
}

.dialog-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 2px solid #e6f3ff;
  transition: all 0.3s ease;
}

.dialog-input :deep(.el-input__wrapper:hover) {
  border-color: #bae0ff;
}

.dialog-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1890ff;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 20px 24px;
  background: #f8faff;
}

.dialog-cancel-btn {
  border-radius: 8px;
  padding: 10px 20px;
}

.dialog-confirm-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

@media (max-width: 1000px) {
  .file-editor-container {
    padding: 16px;
  }
  
  .header-card {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .main-content {
    padding: 24px;
  }
  
  .tag-input-group {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .submit-btn, .cancel-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>