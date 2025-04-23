<template>
    <div style="padding: 24px">
      <!-- 搜索栏 -->
      <el-row :gutter="12">
        <el-input v-model="keyword" placeholder="请输入关键词..." style="width: 300px" />
        <el-select v-model="mode" placeholder="搜索类型" style="width: 150px">
          <el-option label="标签" value="tag" />
          <el-option label="文件夹" value="folder" />
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </el-row>
  
      <!-- 已选标签列表 -->
      <el-space v-if="selectedTags.length > 0" wrap style="margin-top: 12px">
        <el-tag
          v-for="tag in selectedTags"
          :key="tag.id"
          closable
          @close="removeTag(tag.id)"
          type="primary"
        >
          {{ tag.name }}
        </el-tag>
        <el-button type="success" @click="searchFiles" size="small">
          搜索文件（共 {{ selectedTags.length }} 个标签）
        </el-button>
      </el-space>
  
      <!-- 分类标签搜索结果 -->
      <div v-if="tags.length > 0" style="margin-top: 24px">
        <div v-for="(tagGroup, category) in groupedTags" :key="category" style="margin-bottom: 24px">
          <el-divider content-position="left">
            <span class="category-divider-text">{{ category }}</span>
          </el-divider>
  
          <el-space wrap size="large">
            <el-card
              v-for="tag in tagGroup"
              :key="tag.id"
              style="width: 280px; background: #fdfdfd"
              shadow="hover"
            >
              <div>
                <div style="font-weight: bold; font-size: 16px;">{{ tag.name }}</div>
                <div style="margin-top: 6px; min-height: 32px;">
                  <template v-if="tag.aliases.length > 0">
                    <el-tag
                      v-for="alias in tag.aliases"
                      :key="alias.id"
                      type="info"
                      size="small"
                      effect="plain"
                      style="margin-right: 4px;"
                    >
                      {{ alias.name }}
                    </el-tag>
                  </template>
                  <template v-else>
                    <el-tag type="info" size="small" disabled>无别名</el-tag>
                  </template>
                </div>
  
                <div style="margin-top: 12px; text-align: right;">
                  <el-button size="small" @click="manageTag(tag)">管理</el-button>
                  <el-button size="small" type="primary" @click="addTag(tag)">添加</el-button>
                </div>
              </div>
            </el-card>
          </el-space>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import axios from 'axios'
  
  const keyword = ref('')
  const mode = ref('tag')
  const tags = ref([])
  const selectedTags = ref([])
  
  // 分组展示 tags
  const groupedTags = computed(() => {
    const groups = {}
    for (const tag of tags.value) {
      if (!groups[tag.category]) {
        groups[tag.category] = []
      }
      groups[tag.category].push(tag)
    }
    return groups
  })
  
  // 执行搜索
  const search = async () => {
    if (mode.value === 'tag') {
      const res = await axios.get('http://localhost:5000/api/tags', {
        params: { q: keyword.value }
      })
      tags.value = res.data.data
  
      // 如果只有一个结果，自动加入选中
      if (tags.value.length === 1) {
        addTag(tags.value[0])
        // tags.value = [] // 清除下方卡片区
      }
    }
  }
  
  // 添加 tag 到选中栏
  const addTag = (tag) => {
    if (!selectedTags.value.find(t => t.id === tag.id)) {
      selectedTags.value.push(tag)
    }
  }
  
  // 从选中栏移除
  const removeTag = (tagId) => {
    selectedTags.value = selectedTags.value.filter(t => t.id !== tagId)
  }
  
  // 跳转标签管理页（待补充）
  const manageTag = (tag) => {
    alert(`跳转管理标签：${tag.name}`)
  }
  
  // 点击搜索文件
  const searchFiles = () => {
    const ids = selectedTags.value.map(t => t.id)
    const query = ids.join(',')
    alert(`调用接口: /api/files?tag_ids=${query}`)
    // 你可以在这里实际发送请求，渲染 FileList 组件
  }
  </script>
  
  <style scoped>
  .category-divider-text {
    font-size: 18px;
    font-weight: bold;
    color: #409EFF;
  }
  </style>
  