<template>
  <div style="padding: 24px; max-width: 800px; margin: auto">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>📤 文件打标器</span>
        </div>
      </template>

      <!-- 标签输入 -->
      <el-form label-width="100px">
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
            :node-key="'id'"
            default-expand-all
            highlight-current
            check-strictly
            placeholder="选择一个或多个文件夹"
            multiple
          />
        </el-form-item>

        <!-- 上传 PDF 文件 -->
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="onFileChange"
            :before-upload="beforeUpload"
            :http-request="customUpload"
            accept=".pdf"
            drag
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">拖拽或点击上传 PDF 文件</div>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submit">提交上传</el-button>
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
import { ElMessage } from 'element-plus'
import axios from 'axios'

const tagInput = ref('')
const selectedTags = ref([])
const selectedFolderIds = ref([])
const folderTree = ref([])
const file = ref(null)
const dialogCreateTag = ref(false)
const newTag = ref({ name: '', category: '' })

const searchTags = async (queryString, cb) => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/tags', { params: { q: queryString } })
    const list = res.data.data.map(tag => ({ value: tag.name, ...tag }))
    cb(list)
  } catch (err) {
    cb([])
  }
}
const tryCreateTag = () => {
  newTag.value.name = tagInput.value.trim()
  if (!newTag.value.name) {
    ElMessage.warning('请输入标签名')
    return
  }
  dialogCreateTag.value = true
}
const removeTag = (id) => {
  selectedTags.value = selectedTags.value.filter(t => t.id !== id)
}

const groupedTags = computed(() => {
  const groups = {}
  for (const tag of selectedTags.value) {
    if (!groups[tag.category]) groups[tag.category] = []
    groups[tag.category].push(tag)
  }
  return groups
})

const createTag = async () => {
  if (!newTag.value.name || !newTag.value.category) {
    ElMessage.warning('名称和分类不能为空')
    return
  }
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/tags', newTag.value)
    // const createdTag = res.data?.data?.[0]
    const raw = res.data?.data
    const createdTag = Array.isArray(raw) ? raw[0] : raw

    if (!createdTag || !createdTag.id){
    //   ElMessage.error('创建失败，返回格式错误')
    const msg = err.response?.data?.status || '创建失败'
    const extra = err.response?.data?.error
    ElMessage.error(extra ? `${msg}：${extra}` : msg)
      return
    }
    selectedTags.value.push(createdTag)
    ElMessage.success(res.data.status || '创建成功')
    dialogCreateTag.value = false
    tagInput.value = ''
  } catch (err) {
    const msg = err.response?.data?.status || '创建失败'
    const extra = err.response?.data?.error
    ElMessage.error(extra ? `${msg}：${extra}` : msg)
    // 保持 dialogCreateTag 打开
  }
}

const addTag = (tag) => {
  if (!tag || typeof tag !== 'object' || !tag.id || !tag.name) {
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

const getFolders = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/folders/tree')
    folderTree.value = res.data.data
  } catch (err) {
    folderTree.value = []
  }
}

const uploadRef = ref()
const onFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}

const beforeUpload = (rawFile) => {
  if (!rawFile.type.includes('pdf')) {
    ElMessage.error('只支持 PDF 文件')
    return false
  }
  return true
}

const submit = () => {
  if (!file.value) {
    ElMessage.warning('请上传文件')
    return
  }
  if (selectedTags.value.length === 0) {
    ElMessage.warning('请选择至少一个标签')
    return
  }
  if (!selectedTags.value.some(t => t && t.category === 'title')) {
    ElMessage.warning('必须至少选择一个 title 分类的标签')
    return
  }
  uploadRef.value.submit()
}

const customUpload = async (uploadOption) => {
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('tags', JSON.stringify(selectedTags.value.map(t => t.id)))
  formData.append('folders', JSON.stringify(selectedFolderIds.value))

  try {
    const res = await axios.post('http://127.0.0.1:5000/api/files/upload', formData)
    ElMessage.success(res.data.status || '上传成功')
    file.value = null
    selectedTags.value = []
    selectedFolderIds.value = []
    uploadRef.value.clearFiles()
  } catch (err) {
    ElMessage.error(err.response?.data?.status || '上传失败')
  }
}

onMounted(() => {
  getFolders()
})
</script>

<style scoped>
.el-upload__text {
  margin-top: 10px;
  color: #888;
}
</style>
