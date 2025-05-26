<!-- src/App.vue -->
<template>
  <div style="display: flex; height: 100vh;">
    <Sidebar />
    <div style="flex: 1; overflow-y: auto;">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
</script>
