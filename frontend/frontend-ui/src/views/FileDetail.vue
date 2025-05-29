<template>
  <div v-if="fileData" style="padding: 24px;">
    <!-- 缩略图占位 -->
    <div class="thumbnail-placeholder">PDF 预览图（占位）</div>

    <!-- 主标题 -->
    <div style="display: flex; align-items: center;">
      <!-- <h2 style="margin-top: 16px; margin-right: 12px;">
        <el-tooltip
          effect="dark"
          :content="titleAliases.join(' / ')"
          placement="top"
          v-if="titleAliases.length > 0"
        >
          {{ title }}
        </el-tooltip>
        <span v-else>{{ title }}</span>
      </h2> -->
      <h2 style="margin-top: 16px; margin-right: 12px; cursor: pointer;" @click="openTagEditor(titleTag)">
        <el-tooltip
          v-if="titleAliases.length > 0"
          effect="dark"
          :content="titleAliases.join(' / ')"
          placement="top"
        >
          <span>{{ title }}</span>
        </el-tooltip>
        <span v-else>{{ title }}</span>
      </h2>

      <el-tag type="warning" size="small" v-if="isFallbackTitle">无Title标签，显示文件名</el-tag>
    </div>

    <!-- 标签展示 -->
    <div v-for="(tags, category) in groupedTags" :key="category" style="margin: 8px 0;">
      <strong>{{ category }}：</strong>
      <span v-for="tag in tags" :key="tag.id">
        <el-tooltip
          effect="dark"
          :content="tag.aliases.map(a => a.name).join(' / ')"
          placement="top"
          v-if="tag.aliases.length > 0"
        >
          <el-tag
            size="large"
            style="margin: 2px; cursor: pointer;"
            @click="openTagEditor(tag)"
          >
            {{ tag.name }}
          </el-tag>
        </el-tooltip>
        <el-tag
          size="large"
          style="margin: 2px; cursor: pointer;"
          @click="openTagEditor(tag)"
          v-else
        >
          {{ tag.name }}
        </el-tag>
      </span>
    </div>

    <!-- 文件基本信息 -->
    <div style="margin-top: 20px; font-size: 15px; color: #555;">
      <p>文件路径：{{ fileData.upload_path }}</p>
      <p>上传时间：{{ formatDate(fileData.uploaded_at) }}</p>
      <p>文件大小：{{ formatSize(fileData.size) }}</p>
    </div>

    <!-- 所属虚拟文件夹 -->
    <div v-if="fileData && fileData.folders && fileData.folders.length > 0">
      <strong>所属路径：</strong>
      <span
        v-for="folder in fileData.folders"
        :key="folder.id"
        @click="goToFolder(folder.id)"
        style="color: #409EFF; cursor: pointer; text-decoration: underline; margin-right: 12px;"
      >
        {{ buildFullPath(folder.id).join(" / ") }}
      </span>
    </div>

    <!-- 操作按钮 -->
    <div style="margin-top: 24px;">
      <el-button type="primary">下载</el-button>
      <el-button @click="editFile">编辑</el-button>
    </div>

    <!-- 标签编辑对话框（预留） -->
    <el-dialog
      v-model="isTagEditorVisible"
      title="编辑标签"
      width="400px"
    >
      <p>这是标签编辑对话框（功能暂不实现）。</p>
      <div slot="footer" class="dialog-footer">
        <el-button @click="isTagEditorVisible = false">取消</el-button>
        <el-button type="primary" @click="isTagEditorVisible = false">确认</el-button>
      </div>
    </el-dialog>
  </div>

  <!-- 骨架屏 -->
  <div v-else style="padding: 24px;">
    <el-skeleton rows="6" animated />
  </div>
</template>

<script setup>
// import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
// import { useRoute } from 'vue-router'
import { onMounted, ref, computed } from 'vue'
import { useFileStore } from '../stores/fileStore'

// const route = useRoute()
const store = useFileStore()

onMounted(() => {
  store.loadFileData(route.params.id)
})

// 以下原来的变量都改成 computed 或直接从 store 拿值
// const fileData = computed(() => store.fileData)
const buildFullPath = store.buildFullPath


const route = useRoute()
const router = useRouter()



// const title = ref("")
// const titleAliases = ref([])
// const isFallbackTitle = ref(false)
// const groupedTags = ref({})  // category -> [{name, id, aliases}]

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

const folderDict = ref({})   // folder id -> {id, name, parent_id}
const isTagEditorVisible = ref(false)
const currentEditingTag = ref(null)

// ==================== 加载文件信息 ============已改为store获取==



// 展平文件夹树 已改为store获取=


const formatDate = (str) => new Date(str).toLocaleString()
const formatSize = (bytes) => `${(bytes / 1024).toFixed(1)} KB`
const goToFolder = (id) => router.push(`/folder/${id}`)

// 标签编辑预留
// const openTagEditor = (tag) => {
//   currentEditingTag.value = tag
//   isTagEditorVisible.value = true
// }
const openTagEditor = (tag) => {
  if (!tag && !title) return  //  如果传入的是 null 或 undefined，直接忽略
  currentEditingTag.value = tag
  isTagEditorVisible.value = true
}



const editFile = () => {
  alert("跳转到文件编辑页面（暂不实现）")
}

// onMounted(() => loadFileData())
</script>

<style scoped>
.thumbnail-placeholder {
  width: 200px;
  height: 200px;
  background-color: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-weight: bold;
  margin-bottom: 16px;
}
</style>
