// stores/filestore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useFileStore = defineStore('file', () => {
  const fileData = ref(null)
  const folderDict = ref({})

  const loadFileData = async (id) => {
    const res = await axios.get(`http://localhost:5000/api/files/${id}`)
    fileData.value = res.data.data

    const treeRes = await axios.get('http://localhost:5000/api/folders/tree')
    const folders = flatten(treeRes.data.data)
    folderDict.value = Object.fromEntries(folders.map(f => [f.id, f]))
  }

  const flatten = (tree) => {
    const result = []
    const dfs = (nodes) => {
      for (const node of nodes) {
        result.push({ id: node.id, name: node.name, parent_id: node.parent_id })
        if (node.children) dfs(node.children)
      }
    }
    dfs(tree)
    return result
  }

  const buildFullPath = (id) => {
    const path = []
    let current = folderDict.value[id]
    while (current) {
      path.unshift(current.name)
      current = folderDict.value[current.parent_id]
    }
    return path
  }

  return {
    fileData,
    folderDict,
    loadFileData,
    buildFullPath
  }
})
