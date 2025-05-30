<template>
  <div style="padding: 24px; max-width: 800px; margin: auto">
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>📝 编辑文件标签</span>
        </div>
      </template>

      <el-form label-width="100px">
        <!-- 文件名显示 -->
        <el-form-item label="文件名">
          <el-input :model-value="file.name" disabled />
        </el-form-item>

        <!-- 标签输入 -->
        <el-form-item label="添加标签">
          <el-autocomplete
            v-model="tagInput"
            :fetch-suggestions="searchTags"
            placeholder="输入主标签或别名"
            @select="addTag"
            style="width: 100%"
            clearable
          />
          <el-button type="primary" plain @click="tryCreateTag" style="margin-left: 10px;">创建新标签</el-button>
        </el-form-item>

        <!-- 已选标签分类展示 -->
        <el-form-item label="已选标签">
          <div v-for="(tagGroup, category) in groupedTags" :key="category" style="margin-bottom: 12px;">
            <div style="font-weight: bold; color: #409EFF; margin-bottom: 4px;">{{ category }}</div>
            <el-tag
              v-for="tag in tagGroup"
              :key="tag.id"
              closable
              @close="removeTag(tag.id)"
              style="margin: 4px 6px 4px 0"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </el-form-item>

        <!-- 虚拟文件夹选择 -->
        <el-form-item label="保存位置">
          <el-tree-select
            v-model="selectedFolderIds"
            :data="folderTree"
            :props="{ label: 'name', children: 'children', value: 'id' }"
            node-key="id"
            default-expand-all
            highlight-current
            check-strictly
            placeholder="选择一个或多个文件夹"
            multiple
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submit">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 创建标签对话框 -->
    <el-dialog title="创建新标签" v-model="dialogCreateTag">
      <el-form label-width="80px">
        <el-form-item label="标签名">
          <el-input v-model="newTag.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="newTag.category" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogCreateTag = false">取消</el-button>
        <el-button type="primary" @click="createTag">创建</el-button>
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

// 搜索标签
const searchTags = async (queryString, cb) => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/tags', { params: { q: queryString } })
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
    const res = await axios.post('http://127.0.0.1:5000/api/tags', newTag.value)
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
    const res = await axios.get('http://127.0.0.1:5000/api/folders/tree')
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
    const res = await axios.get(`http://127.0.0.1:5000/api/files/${id}`)
    file.value = res.data.data
    // 处理 tags
    const tagsData = file.value.tags || []
    if (tagsData.length && typeof tagsData[0] === 'number') {
      const allTagsRes = await axios.get('http://127.0.0.1:5000/api/tags')
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
    const res = await axios.put(`http://127.0.0.1:5000/api/files/${id}`, {
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
.el-upload__text {
  margin-top: 10px;
  color: #888;
}
</style>
