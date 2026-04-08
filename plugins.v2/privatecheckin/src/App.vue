<template>
  <v-app>
    <v-main class="pc-shell">
      <v-container max-width="1500" class="py-6">
        <v-tabs v-model="tab" color="primary" class="mb-4">
          <v-tab value="page">数据页</v-tab>
          <v-tab value="config">配置页</v-tab>
        </v-tabs>
        <v-window v-model="tab">
          <v-window-item value="page">
            <PageView :api="api" @switch="tab = $event" @close="handleClose" />
          </v-window-item>
          <v-window-item value="config">
            <ConfigView :api="api" @switch="tab = $event" @close="handleClose" />
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import ConfigView from './components/Config.vue'
import PageView from './components/Page.vue'
import { createRequest } from './utils/request'

const tab = ref('page')
const request = createRequest(import.meta.env.VITE_API_BASE || 'http://localhost:3000')
const api = {
  get: (url, config) => request.get(url, config),
  post: (url, data, config) => request.post(url, data, config),
}

function handleClose() {
  console.log('PrivateCheckin dev shell close event')
}
</script>

<style scoped>
.pc-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(27, 94, 32, 0.1), transparent 34%),
    radial-gradient(circle at top right, rgba(13, 71, 161, 0.1), transparent 30%),
    linear-gradient(180deg, #f4f7f3 0%, #eef3f8 100%);
}
</style>
