<template>
  <v-app>
    <v-main class="bg-grey-lighten-4">
      <v-container class="py-6">
        <div class="d-flex flex-wrap ga-3 mb-4">
          <v-btn :variant="view === 'page' ? 'flat' : 'outlined'" color="primary" @click="view = 'page'">页面</v-btn>
          <v-btn :variant="view === 'config' ? 'flat' : 'outlined'" color="primary" @click="view = 'config'">配置</v-btn>
        </div>
        <PageView v-if="view === 'page'" :api="api" @switch="view = 'config'" />
        <ConfigView v-else :api="api" @switch="view = 'page'" />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import ConfigView from './components/Config.vue'
import PageView from './components/Page.vue'
import { createRequest } from './utils/request'

const request = createRequest(import.meta.env.VITE_API_BASE || 'http://localhost:3000')
const view = ref('page')

const api = {
  get: (url, config) => request.get(url, config),
  post: (url, data, config) => request.post(url, data, config),
  put: (url, data, config) => request.put(url, data, config),
}
</script>
