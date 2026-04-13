<template>
  <v-app>
    <v-main class="vp-app-shell">
      <v-container max-width="1460">
        <v-tabs v-model="tab" color="primary" class="mb-4">
          <v-tab value="page">状态页</v-tab>
          <v-tab value="config">配置页</v-tab>
        </v-tabs>
        <v-window v-model="tab">
          <v-window-item value="page">
            <PageView :api="api" :initial-config="pluginConfig" @switch="tab = $event" @close="handleClose" />
          </v-window-item>
          <v-window-item value="config">
            <ConfigView :api="api" :initial-config="pluginConfig" @switch="tab = $event" @close="handleClose" />
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ConfigView from './components/Config.vue'
import PageView from './components/Page.vue'
import { createRequest } from './utils/request'

const tab = ref('page')
const pluginConfig = reactive({})
const request = createRequest(import.meta.env.VITE_API_BASE || 'http://localhost:3000')
const api = {
  get: (url, config) => request.get(url, config),
  post: (url, data, config) => request.post(url, data, config),
}

function handleClose() {
  console.log('VuePanel dev shell close event')
}
</script>

<style scoped>
.vp-app-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(35, 157, 232, 0.14), transparent 30%),
    radial-gradient(circle at bottom right, rgba(39, 174, 96, 0.1), transparent 28%),
    linear-gradient(180deg, #f6f8fc 0%, #eef3fb 100%);
}
</style>
