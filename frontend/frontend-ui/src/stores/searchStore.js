import { defineStore } from 'pinia'

export const useSearchStore = defineStore('search', {
  state: () => ({
    keyword: '',
    mode: 'tag',
    selectedItems: [],
    tags: [],
    folders: [],
    fileResults: [],
    fileTotal: 0,
    currentPage: 1,
    pageSize: 20,
    categoryColorMap: {},
    availableColors: [
      '#f7e1d7', '#edbfb8', '#dedbd2', '#b0c4b1',
      '#4a5759', '#78290f', '#b8b8ff', '#E84393'
    ],
    colorIndex: 0
  }),
  actions: {
    reset() {
      this.keyword = ''
      this.mode = 'tag'
      this.selectedItems = []
      this.tags = []
      this.folders = []
      this.fileResults = []
      this.fileTotal = 0
      this.currentPage = 1
    },
    getCategoryColor(category) {
      if (!this.categoryColorMap[category]) {
        this.categoryColorMap[category] =
          this.availableColors[this.colorIndex % this.availableColors.length]
        this.colorIndex++
      }
      return this.categoryColorMap[category]
    }
  },
  persist: true  // 如用 pinia-plugin-persistedstate 可开启
})
