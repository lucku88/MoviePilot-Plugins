<template>
  <div ref="rootEl" class="toy-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="toy-shell">
      <header class="toy-config-header">
        <div class="toy-header-copy">
          <div class="toy-badge">SQ玩偶</div>
          <h1 class="toy-page-title">插件配置</h1>
          <p class="toy-page-subtitle">盲盒、回收、展出、获取执行记录。</p>
        </div>
        <div class="toy-header-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="toy-settings-card">
        <h2 class="toy-settings-title">⚙️ 基本设置</h2>
        <div class="toy-switch-grid toy-switch-grid-basic">
          <div class="toy-switch-item">
            <v-switch v-model="config.enabled" class="toy-switch-control" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="toy-switch-item">
            <v-switch v-model="config.use_proxy" class="toy-switch-control" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="toy-switch-item">
            <v-switch v-model="config.notify" class="toy-switch-control" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="toy-switch-item">
            <v-switch v-model="config.onlyonce" class="toy-switch-control" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="toy-settings-card">
        <h2 class="toy-settings-title">🧩 功能设置</h2>

        <div class="toy-switch-grid">
          <div class="toy-switch-item">
            <v-switch v-model="config.auto_cookie" class="toy-switch-control" label="使用站点Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="toy-switch-item">
            <v-switch v-model="config.enable_target" class="toy-switch-control" label="允许外展抢位" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="toy-switch-item">
            <v-switch v-model="config.force_ipv4" class="toy-switch-control" label="优先 IPv4" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="toy-field-grid">
          <div class="toy-field-block">
            <div class="toy-field-label">站点Cookie</div>
            <v-text-field
              v-model="cookieFieldValue"
              label="站点Cookie"
              variant="outlined"
              density="comfortable"
              :disabled="cookieReadonly"
              :readonly="cookieReadonly"
              :placeholder="cookieReadonly ? '使用站点Cookie后自动同步' : '例如 c_secure_pass=...'"
            />
            <div class="toy-note">启用【使用站点Cookie】后自动同步，关闭后才可手动填写。</div>
          </div>

          <div class="toy-field-block">
            <div class="toy-field-label">动作参数</div>
            <div class="toy-inline-grid">
              <v-text-field v-model="config.collect_retry" label="回收重试次数" type="number" variant="outlined" density="comfortable" />
              <v-text-field v-model="config.collect_retry_delay" label="回收重试间隔(ms)" type="number" variant="outlined" density="comfortable" />
              <v-text-field v-model="config.place_loop_limit" label="单轮放置循环上限" type="number" variant="outlined" density="comfortable" />
              <v-text-field v-model="config.place_retry_delay" label="放置循环间隔(ms)" type="number" variant="outlined" density="comfortable" />
              <v-text-field v-model="config.max_target_try" label="随机目标尝试次数" type="number" variant="outlined" density="comfortable" />
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const pluginBase = '/plugin/SQToy'
const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_target: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
  collect_retry: 3,
  collect_retry_delay: 1200,
  place_loop_limit: 10,
  place_retry_delay: 1500,
  max_target_try: 3,
})

const cookieReadonly = computed(() => !!config.auto_cookie)
const cookieFieldValue = computed({
  get() {
    if (config.auto_cookie) {
      return truncateCookie(config.cookie)
    }
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) {
      config.cookie = value || ''
    }
  },
})

let themeObserver = null
let mediaQuery = null

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function truncateCookie(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > 22 ? `${text.slice(0, 22)}...` : text
}

function applyConfig(data = {}) {
  const { capture_tips, ...rest } = data || {}
  Object.assign(config, { ...config, ...rest })
}

async function loadConfig() {
  const data = await props.api.get(`${pluginBase}/config`)
  applyConfig(data || {})
}

async function saveConfig() {
  saving.value = true
  try {
    const result = await props.api.post(`${pluginBase}/config`, { ...config })
    applyConfig(result?.config || {})
    flash(result?.message || '配置已保存')
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  saving.value = true
  try {
    const result = await props.api.get(`${pluginBase}/cookie`)
    applyConfig(result?.config || {})
    flash(result?.message || 'Cookie 已同步')
  } catch (error) {
    flash(error?.message || '同步失败', 'error')
  } finally {
    saving.value = false
  }
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    const classValue = String(current.className || '').toLowerCase()
    if (classValue.includes('theme') || classValue.includes('v-theme--') || classValue.includes('dark') || classValue.includes('light')) {
      return current
    }
    current = current.parentElement
  }
  const bodyClass = String(document.body?.className || '').toLowerCase()
  if (document.body?.getAttribute('data-theme') || bodyClass.includes('theme') || bodyClass.includes('v-theme--') || bodyClass.includes('dark') || bodyClass.includes('light')) {
    return document.body
  }
  const rootClass = String(document.documentElement?.className || '').toLowerCase()
  if (document.documentElement?.getAttribute('data-theme') || rootClass.includes('theme') || rootClass.includes('v-theme--') || rootClass.includes('dark') || rootClass.includes('light')) {
    return document.documentElement
  }
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  const classValue = String(node?.className || '').toLowerCase()
  return ['dark', 'purple', 'transparent'].includes(themeValue)
    || classValue.includes('dark')
    || classValue.includes('theme-dark')
    || classValue.includes('v-theme--dark')
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  const classValue = String(node?.className || '').toLowerCase()
  return themeValue === 'light'
    || classValue.includes('light')
    || classValue.includes('theme-light')
    || classValue.includes('v-theme--light')
}

function detectTheme() {
  const nodes = getThemeNodes()
  if (nodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true
    return
  }
  if (nodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  detectTheme()
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    getThemeNodes().forEach((node) => {
      themeObserver.observe(node, {
        attributes: true,
        subtree: node === document.documentElement || node === document.body,
        attributeFilter: ['data-theme', 'class'],
      })
    })
  }
}

onMounted(async () => {
  detectTheme()
  bindThemeObserver()
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.toy-config {
  min-height: 100vh;
  --toy-bg-start: #f7f4ff;
  --toy-bg-end: #f2e8ff;
  --toy-panel: rgba(255, 255, 255, 0.9);
  --toy-panel-strong: rgba(255, 255, 255, 0.98);
  --toy-border: rgba(124, 92, 255, 0.2);
  --toy-shadow: 0 24px 80px rgba(91, 72, 164, 0.12);
  --toy-text-main: #2b2447;
  --toy-text-soft: rgba(43, 36, 71, 0.72);
  --toy-chip: rgba(124, 92, 255, 0.12);
  background:
    radial-gradient(circle at top left, rgba(140, 110, 255, 0.2), transparent 32%),
    linear-gradient(180deg, var(--toy-bg-start) 0%, var(--toy-bg-end) 100%);
  color: var(--toy-text-main);
}

.toy-config.is-dark-theme {
  --toy-bg-start: #12131d;
  --toy-bg-end: #171828;
  --toy-panel: rgba(26, 28, 39, 0.92);
  --toy-panel-strong: rgba(19, 21, 30, 0.98);
  --toy-border: rgba(124, 92, 255, 0.22);
  --toy-shadow: 0 28px 90px rgba(7, 10, 20, 0.46);
  --toy-text-main: #f3efff;
  --toy-text-soft: rgba(243, 239, 255, 0.72);
  --toy-chip: rgba(124, 92, 255, 0.18);
}

.toy-config,
.toy-config * {
  box-sizing: border-box;
}

.toy-shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 18px 28px;
  display: grid;
  gap: 18px;
}

.toy-config-header,
.toy-settings-card {
  border: 1px solid var(--toy-border);
  border-radius: 28px;
  background: var(--toy-panel);
  box-shadow: var(--toy-shadow);
  backdrop-filter: blur(18px);
}

.toy-config-header {
  padding: 26px 28px;
  display: flex;
  gap: 18px;
  justify-content: space-between;
  align-items: flex-start;
}

.toy-header-copy {
  display: grid;
  gap: 10px;
}

.toy-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 7px 14px;
  border-radius: 999px;
  background: var(--toy-chip);
  color: #8b6cff;
  font-size: 13px;
  font-weight: 800;
}

.toy-page-title {
  margin: 0;
  font-size: clamp(30px, 4vw, 54px);
  font-weight: 800;
  letter-spacing: -0.03em;
}

.toy-page-subtitle,
.toy-note {
  margin: 0;
  color: var(--toy-text-soft);
  font-size: 14px;
  line-height: 1.7;
}

.toy-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.toy-settings-card {
  padding: 24px 26px;
  display: grid;
  gap: 18px;
}

.toy-settings-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
}

.toy-switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.toy-switch-grid-basic {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.toy-switch-item,
.toy-field-block {
  border: 1px solid var(--toy-border);
  border-radius: 22px;
  background: var(--toy-panel-strong);
}

.toy-switch-item {
  padding: 8px 14px;
}

.toy-field-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.5fr);
  gap: 14px;
}

.toy-field-block {
  padding: 16px 16px 14px;
  display: grid;
  gap: 12px;
}

.toy-field-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--toy-text-soft);
}

.toy-inline-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

:deep(.toy-config .toy-switch-control) {
  margin: 0;
  min-height: auto;
}

:deep(.toy-config .toy-switch-control .v-selection-control) {
  min-height: auto;
}

:deep(.toy-config .toy-switch-control .v-label) {
  font-size: 14px;
  font-weight: 700;
  color: var(--toy-text-main);
  opacity: 1;
}

:deep(.toy-config .toy-switch-control .v-selection-control__wrapper) {
  width: 38px;
  height: 22px;
}

:deep(.toy-config .toy-switch-control .v-switch__track) {
  height: 22px;
  min-width: 38px;
  border-radius: 999px;
}

:deep(.toy-config .toy-switch-control .v-switch__thumb) {
  width: 16px;
  height: 16px;
}

:deep(.toy-config .v-field) {
  border-radius: 16px;
  background: transparent;
}

:deep(.toy-config .v-field__input) {
  min-height: 46px;
  color: var(--toy-text-main);
}

:deep(.toy-config .v-label) {
  color: var(--toy-text-soft);
}

@media (max-width: 1080px) {
  .toy-switch-grid-basic,
  .toy-switch-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .toy-field-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .toy-shell {
    padding: 16px 12px 20px;
  }

  .toy-config-header {
    padding: 20px;
    flex-direction: column;
  }

  .toy-header-actions {
    justify-content: flex-start;
  }

  .toy-switch-grid-basic,
  .toy-switch-grid,
  .toy-inline-grid {
    grid-template-columns: 1fr;
  }
}
</style>
