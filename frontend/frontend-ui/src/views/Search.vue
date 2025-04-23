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
  
      <!-- <div v-if="tags.length === 1" style="margin-top: 20px">
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
      </div> -->
  
      <!-- <div v-else-if="tags.length > 1" style="margin-top: 24px"> -->
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
                <div style="margin-top: 6px;">
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
                        <el-tag type="info" size="small"  disabled>无别名</el-tag>
                    </template>
                    </div>

                </div>
                <div style="margin-top: 12px; text-align: right;">
                    <el-button size="small" @click="manageTag(tag)">管理</el-button>
                    <el-button size="small" type="primary" @click="searchFiles(tag.id)">搜索文件</el-button>
                </div>
                </div>
            </el-card>
            </el-space>
        </div>
        </div>

    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import { computed } from 'vue'

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
  

  <style scoped>
  .category-divider-text {
    font-size: 18px;
    font-weight: bold;
    color: #000000;
  }
  </style>
