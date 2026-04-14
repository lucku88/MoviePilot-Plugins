<template>
  <div ref="rootEl" class="mp-panel" :class="themeClass" :style="themeStyle">
    <v-app class="mp-app">
      <v-main>
        <v-container fluid class="mp-shell">
          <v-tabs v-model="tab" color="primary" class="mp-tabs" grow>
            <v-tab value="page">功能面板</v-tab>
            <v-tab value="config">全局设置</v-tab>
          </v-tabs>

          <v-window v-model="tab" class="mp-window">
            <v-window-item value="page">
              <PageView
                :api="api"
                :initial-config="pluginConfig"
                :theme-name="themeName"
                :theme-label="themeLabel"
                @switch="tab = $event"
                @close="handleClose"
              />
            </v-window-item>
            <v-window-item value="config">
              <ConfigView
                :api="api"
                :initial-config="pluginConfig"
                :theme-name="themeName"
                :theme-label="themeLabel"
                @switch="tab = $event"
                @close="handleClose"
              />
            </v-window-item>
          </v-window>
        </v-container>
      </v-main>
    </v-app>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ConfigView from './components/Config.vue'
import PageView from './components/Page.vue'
import { usePanelTheme } from './composables/usePanelTheme'
import { createRequest } from './utils/request'
import './styles/panel-theme.css'

const tab = ref('page')
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
.mp-window {
  background: transparent;
}
</style>
