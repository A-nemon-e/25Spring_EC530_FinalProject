import { defineStore } from 'pinia'

export const useFileStore = defineStore('file', {
  state: () => ({
    fileDetailCache: {}
  }),
  actions: {
    cacheFile(file) {
      this.fileDetailCache[file.id] = file
    },
    getCachedFile(id) {
      return this.fileDetailCache[id] || null
    }
  }
})