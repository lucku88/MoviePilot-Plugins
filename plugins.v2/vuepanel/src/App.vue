<template>
  <div ref="rootEl" class="mp-panel" :class="themeClass" :style="themeStyle">
    <v-app class="mp-app">
      <v-main>
        <v-container fluid class="mp-shell">
          <div class="mp-page">
            <PageView
              :api="api"
              :initial-config="pluginConfig"
              :theme-name="themeName"
              :theme-label="themeLabel"
              @close="handleClose"
            />
          </div>
        </v-container>
      </v-main>
    </v-app>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import PageView from './components/Page.vue'
import { usePanelTheme } from './composables/usePanelTheme'
import { createRequest } from './utils/request'
import './styles/panel-theme.css'

const pluginConfig = reactive({})
const rootEl = ref(null)
const request = createRequest(import.meta.env.VITE_API_BASE || 'http://localhost:3000')
const { themeName, themeLabel, themeClass, themeStyle } = usePanelTheme(rootEl)

const api = {
  get: (url, config) => request.get(url, config),
  post: (url, data, config) => request.post(url, data, config),
}

function handleClose() {
  console.log('VuePanel dev shell close event')
}
</script>

<style scoped>
.mp-app,
.mp-page {
  background: transparent;
}
</style>
