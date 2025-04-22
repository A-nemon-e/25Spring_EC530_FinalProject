<template>
    <div style="padding: 24px">
      <el-row :gutter="12">
        <el-input v-model="keyword" placeholder="请输入关键词..." style="width: 300px" />
        <el-select v-model="mode" placeholder="搜索类型" style="width: 150px">
          <el-option label="标签" value="tag" />
          <el-option label="文件夹" value="folder" />
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </el-row>
  
      <div v-if="tags.length === 1" style="margin-top: 20px">
        <el-card>
          <div>
            <strong>{{ tags[0].name }}</strong>（{{ tags[0].category }}）<br />
            <small>别名：{{ tags[0].aliases.map(a => a.name).join(' / ') }}</small>
          </div>
          <div style="margin-top: 10px">
            <el-button size="small">管理标签</el-button>
            <el-button type="primary" size="small" @click="searchFiles(tags[0].id)">查看文件</el-button>
          </div>
        </el-card>
      </div>
  
      <div v-else-if="tags.length > 1" style="margin-top: 20px">
        <el-card v-for="tag in tags" :key="tag.id" style="margin-bottom: 10px">
          <div>
            <strong>{{ tag.name }}</strong>（{{ tag.category }}）
            <el-button size="small" style="margin-left: 12px">管理</el-button>
            <el-button size="small" type="primary" @click="searchFiles(tag.id)">搜索文件</el-button>
          </div>
          <div style="font-size: 12px; color: gray; margin-top: 5px">
            别名：{{ tag.aliases.map(a => a.name).join(' / ') }}
          </div>
        </el-card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const keyword = ref('')
  const mode = ref('tag')
  const tags = ref([])
  
  const search = async () => {
    if (mode.value === 'tag') {
      const res = await axios.get('http://localhost:5000/api/tags', {
        params: { q: keyword.value }
      })
      tags.value = res.data.data
    }
  }
  
  const searchFiles = async (tagId) => {
    alert(`你点击了搜索文件，下一步调用 /api/files?tag_ids=${tagId}`)
  }
  </script>
  