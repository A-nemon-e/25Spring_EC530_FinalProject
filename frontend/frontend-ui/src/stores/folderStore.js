import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import axios from 'axios'

export const useFolderExplorerStore = defineStore('folderExplorer', () => {
  // ✅ 保留 ref
  const folderId = ref(null)
  const folders = ref([])
  const files = ref([])
  const currentPath = ref([])
  const allFoldersDict = ref({})

  // ✅ 方法不变
  const flattenFolders = (tree) => {
    const result = []
    const dfs = (nodes) => {
      if (!Array.isArray(nodes)) return
      for (const node of nodes) {
        result.push({ id: node.id, name: node.name, parent_id: node.parent_id })
        if (Array.isArray(node.children)) dfs(node.children)
      }
    }
    dfs(tree)
    return result
  }

  const loadAllFolders = async () => {
    const res = await axios.get('/api/folders/tree')
    const folderList = flattenFolders(res.data.data)
    allFoldersDict.value = Object.fromEntries(folderList.map(f => [f.id, f]))
  }

  const buildCurrentPath = (id) => {
    const path = []
    let current = allFoldersDict.value[id]
    while (current) {
      path.unshift(current)
      current = allFoldersDict.value[current.parent_id]
    }
    currentPath.value = path
  }



const loadFolder = async (id) => {
//   loading.value = true
  folderId.value = id
  const res = await axios.get(`/api/folders/${id}/children`)
  folders.value = res.data.data.folders
  files.value = res.data.data.files
  buildCurrentPath(id)
 
}


  // ✅ 保留颜色映射逻辑
  const categoryColorMap = ref({})
  const availableColors = [
    '#f7e1d7', '#edbfb8', '#dedbd2', '#b0c4b1',
    '#4a5759', '#78290f', '#b8b8ff', '#E84393'
  ]
  let colorIndex = 0

  const getCategoryColor = (category) => {
    if (!categoryColorMap.value[category]) {
      categoryColorMap.value[category] =
        availableColors[colorIndex % availableColors.length]
      colorIndex++
    }
    return categoryColorMap.value[category]
  }
  

  // ✅ 不要 reactive，保持 ref 正常使用
  return {
    folderId,
    folders,
    files,
    currentPath,
    allFoldersDict,
    loadAllFolders,
    loadFolder,
    getCategoryColor
  }
})
