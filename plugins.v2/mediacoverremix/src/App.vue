<template>
  <v-app>
    <v-main class="remix-dev-shell">
      <v-container class="py-8" max-width="1360">
        <v-card class="remix-dev-card" rounded="xl">
          <v-tabs v-model="tab" color="primary" class="px-4 pt-4">
            <v-tab value="page">数据页</v-tab>
            <v-tab value="config">配置页</v-tab>
          </v-tabs>
          <v-window v-model="tab">
            <v-window-item value="page">
              <PageView :api="api" :initial-config="pluginConfig" @switch="tab = $event" />
            </v-window-item>
            <v-window-item value="config">
              <ConfigView :api="api" :initial-config="pluginConfig" @switch="tab = $event" />
            </v-window-item>
          </v-window>
        </v-card>
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
</script>

<style scoped>
.remix-dev-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(67, 97, 238, 0.15), transparent 32%),
    radial-gradient(circle at bottom right, rgba(0, 180, 216, 0.16), transparent 28%),
    linear-gradient(180deg, #eef3fb 0%, #e7edf8 100%);
}

.remix-dev-card {
  overflow: hidden;
  border: 1px solid rgba(78, 103, 141, 0.12);
  box-shadow: 0 28px 80px rgba(10, 23, 55, 0.12);
}
</style>
