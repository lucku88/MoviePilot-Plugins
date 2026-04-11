<template>
  <v-app>
    <v-main class="pa-4 sq-dev-shell">
        <v-container max-width="1440">
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
  console.log('VuePill dev shell close event')
}
</script>

<style scoped>
.sq-dev-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(124, 92, 255, 0.12), transparent 34%),
    linear-gradient(180deg, #f8f7ff 0%, #f4f6fb 100%);
}
</style>

