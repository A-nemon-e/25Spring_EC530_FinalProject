<template>
  <div class="tag-manager" style="padding: 24px;">
    <el-card>
      <template #header>
        <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: space-between;">
          <div style="display: flex; gap: 12px;">
            <el-input
              v-model="query"
              placeholder="按标签名或别名搜索"
              clearable
              @clear="fetchTags"
              @keyup.enter.native="fetchTags"
              style="width: 240px;"
            />
            <el-select
              v-model="categoryFilter"
              placeholder="筛选分类"
              clearable
              @change="fetchTags"
              style="width: 200px;"
            >
              <el-option
                v-for="cat in categoryOptions"
                :key="cat"
                :label="cat"
                :value="cat"
              />
            </el-select>
            <el-button type="primary" icon="el-icon-search" @click="fetchTags">搜索</el-button>
          </div>
          <el-button type="success" @click="openAddDialog">添加标签</el-button>
        </div>
      </template>

      <el-table
        :data="tags"
        v-loading="loading"
        stripe
        style="width: 100%; margin-top: 16px;"
        row-key="id"
      >
        <el-table-column prop="name" label="标签名称" />
        <el-table-column prop="category" label="分类" />
        <el-table-column label="别名">
          <template #default="{ row }">
            <el-tag
              v-for="alias in row.aliases"
              :key="alias.id"
              closable
              @close="onDeleteAlias(alias.id)"
              style="margin: 4px 4px 4px 0;"
            >
              {{ alias.name }}
            </el-tag>
            <el-button type="text" @click="openAliasDialog(row)">+ 添加</el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="onDeleteTag(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加标签 -->
    <el-dialog title="添加新标签" v-model="dialogAdd">
      <el-form :model="formAdd" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="formAdd.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="formAdd.category" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogAdd = false">取消</el-button>
        <el-button type="primary" @click="onAddTag">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑标签 -->
    <el-dialog title="编辑标签" v-model="dialogEdit">
      <el-form :model="formEdit" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="formEdit.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="formEdit.category" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogEdit = false">取消</el-button>
        <el-button type="primary" @click="onUpdateTag">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加别名 -->
    <el-dialog title="添加别名" v-model="dialogAlias">
      <el-form label-width="80px">
        <el-form-item label="别名" required>
          <el-input v-model="formAlias" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogAlias = false">取消</el-button>
        <el-button type="primary" @click="onAddAlias">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

axios.defaults.baseURL = ''

const tags = ref([])
const loading = ref(false)
const query = ref('')
const categoryFilter = ref('')
const categoryOptions = ref([])

const dialogAdd = ref(false)
const dialogEdit = ref(false)
const dialogAlias = ref(false)

const formAdd = ref({ name: '', category: '' })
const formEdit = ref({ id: null, name: '', category: '' })
const formAlias = ref('')
const aliasTagId = ref(null)

// 统一错误提示处理
function showError(err, fallback = '操作失败') {
  const status = err.response?.data?.status || fallback
  const extra = err.response?.data?.error
  ElMessage.error(extra ? `${status}：${extra}` : status)
}

const fetchTags = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/tags', {
      params: { q: query.value || undefined }
    })
    const rawList = Array.isArray(res.data.data) ? res.data.data : []
    tags.value = categoryFilter.value
      ? rawList.filter(tag => tag.category === categoryFilter.value)
      : rawList

    const categorySet = new Set()
    rawList.forEach(tag => {
      if (tag.category) categorySet.add(tag.category)
    })
    categoryOptions.value = Array.from(categorySet)
  } catch (err) {
    showError(err, '加载标签失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  formAdd.value = { name: '', category: '' }
  dialogAdd.value = true
}
const onAddTag = async () => {
  if (!formAdd.value.name.trim()) return ElMessage.warning('名称不能为空')
  try {
    const res = await axios.post('/api/tags', formAdd.value)
    ElMessage.success(res.data.status || '添加成功')
    dialogAdd.value = false
    fetchTags()
  } catch (err) {
    showError(err, '添加失败')
  }
}

const openEditDialog = (row) => {
  formEdit.value = { id: row.id, name: row.name, category: row.category }
  dialogEdit.value = true
}
const onUpdateTag = async () => {
  try {
    const res = await axios.put(`/api/tags/${formEdit.value.id}`, {
      name: formEdit.value.name,
      category: formEdit.value.category
    })
    ElMessage.success(res.data.status || '更新成功')
    dialogEdit.value = false
    fetchTags()
  } catch (err) {
    showError(err, '更新失败')
  }
}

const onDeleteTag = async (tagId) => {
  try {
    await ElMessageBox.confirm('确认删除该标签？请先删除别名/关联的文件（如有）', '警告', { type: 'warning' })
    const res = await axios.delete(`/api/tags/${tagId}`)
    ElMessage.success(res.data.status || '删除成功')
    fetchTags()
  } catch (err) {
    if (err !== 'cancel') showError(err, '删除失败，是否还存在没有删除的别名/关联的文件？')
  }
}

const openAliasDialog = (row) => {
  aliasTagId.value = row.id
  formAlias.value = ''
  dialogAlias.value = true
}
const onAddAlias = async () => {
  if (!formAlias.value.trim()) return ElMessage.warning('别名不能为空')
  try {
    const res = await axios.post(`/api/tags/${aliasTagId.value}/alias`, {
      alias: formAlias.value
    })
    ElMessage.success(res.data.status || '添加别名成功')
    dialogAlias.value = false
    fetchTags()
  } catch (err) {
    showError(err, '添加别名失败')
  }
}

const onDeleteAlias = async (aliasId) => {
  try {
    await ElMessageBox.confirm('确认删除该别名？', '提示', { type: 'warning' })
    const res = await axios.delete(`/api/tags/alias/${aliasId}`)
    ElMessage.success(res.data.status || '删除别名成功')
    fetchTags()
  } catch (err) {
    if (err !== 'cancel') showError(err, '删除别名失败')
  }
}

onMounted(fetchTags)
</script>

<style scoped>
.tag-manager .el-tag {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
