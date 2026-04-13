<template>
  <div ref="rootEl" class="vuetoy-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vtc-shell">
      <header class="vtc-card vtc-hero">
        <div class="vtc-copy">
          <div class="vtc-badge">Vue-玩偶</div>
          <h1 class="vtc-title">插件配置</h1>
          <div class="vtc-chip-row">
            <span class="vtc-chip">{{ config.auto_cookie ? '站点 Cookie：自动同步' : '站点 Cookie：手动填写' }}</span>
            <span class="vtc-chip">{{ config.auto_collect ? '自动回收：开启' : '自动回收：关闭' }}</span>
            <span class="vtc-chip">{{ config.auto_place ? '自动展出：开启' : '自动展出：关闭' }}</span>
          </div>
        </div>
        <div class="vtc-action-grid">
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vtc-card">
        <h2 class="vtc-section-title">⚙️ 基本设置</h2>
        <div class="vtc-switch-grid">
          <div class="vtc-switch-card">
            <v-switch v-model="config.enabled" class="vtc-switch" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.use_proxy" class="vtc-switch" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.notify" class="vtc-switch" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.onlyonce" class="vtc-switch" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="vtc-card">
        <h2 class="vtc-section-title">🧩 功能设置</h2>
        <div class="vtc-switch-grid">
          <div class="vtc-switch-card">
            <v-switch v-model="config.auto_cookie" class="vtc-switch" label="使用站点 Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.auto_collect" class="vtc-switch" label="自动回收" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.auto_place" class="vtc-switch" label="自动展出" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vtc-switch-card">
            <v-switch v-model="config.force_ipv4" class="vtc-switch" label="优先 IPv4" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="vtc-field-grid">
          <div class="vtc-field-card">
            <div class="vtc-field-label">站点 Cookie</div>
            <v-text-field
              v-model="cookieFieldValue"
              label="站点 Cookie"
              variant="outlined"
              density="comfortable"
              :disabled="cookieReadonly"
              :readonly="cookieReadonly"
              :placeholder="cookieReadonly ? '开启后自动同步站点 Cookie' : '例如 c_secure_pass=...'"
              hide-details="auto"
            />
            <div class="vtc-note">开启使用站点 Cookie 后会自动获取已配置站点的 Cookie，关闭后才可以手动修改。</div>
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

const pluginBase = '/plugin/VueToy'
const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  auto_collect: true,
  auto_place: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
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
  return text.length > 48 ? `${text.slice(0, 48)}...` : text
}

function applyConfig(data = {}) {
  const { capture_tips, ...rest } = data || {}
  Object.assign(config, { ...config, ...rest })
}

async function loadConfig() {
  try {
    const data = await props.api.get(`${pluginBase}/config`)
    applyConfig(data || {})
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const result = await props.api.post(`${pluginBase}/config`, { ...config })
    applyConfig(result?.config || {})
    flash(result?.message || '配置已保存')
    if (config.onlyonce) {
      config.onlyonce = false
    }
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

function closePlugin() {
  emit('close')
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme') || current.className) return current
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme') || document.body?.className) return document.body
  if (document.documentElement?.getAttribute('data-theme') || document.documentElement?.className) return document.documentElement
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  if (['dark', 'purple', 'transparent'].includes(themeValue)) return true
  const className = String(node?.className || '').toLowerCase()
  return ['v-theme--dark', 'theme--dark', 'theme-dark', 'dark'].some((token) => className.includes(token))
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  if (themeValue === 'light') return true
  const className = String(node?.className || '').toLowerCase()
  return ['v-theme--light', 'theme--light', 'theme-light', 'light'].some((token) => className.includes(token))
}

function detectTheme() {
  const themeNodes = getThemeNodes()
  if (themeNodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true
    return
  }
  if (themeNodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  themeObserver?.disconnect?.()
  detectTheme()
  if (!window.MutationObserver) {
    return
  }
  themeObserver = new MutationObserver(detectTheme)
  getThemeNodes().forEach((node) => {
    themeObserver.observe(node, {
      attributes: true,
      subtree: node === document.documentElement || node === document.body,
      attributeFilter: ['data-theme', 'class'],
    })
  })
}

onMounted(async () => {
  detectTheme()
  bindThemeObserver()
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
  applyConfig(props.initialConfig || {})
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.vuetoy-config {
  min-height: 100vh;
  --vtc-bg-start: #fafbff;
  --vtc-bg-end: #eef1f7;
  --vtc-panel: rgba(255, 255, 255, 0.88);
  --vtc-panel-strong: rgba(255, 255, 255, 0.96);
  --vtc-border: rgba(129, 133, 164, 0.18);
  --vtc-chip: rgba(124, 92, 255, 0.1);
  --vtc-text-main: #262638;
  --vtc-text-soft: rgba(118, 119, 139, 0.94);
  --vtc-shadow: 0 20px 48px rgba(121, 128, 166, 0.12);
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.94) 0%, rgba(246, 247, 250, 0.98) 42%, #eef1f7 100%),
    linear-gradient(180deg, var(--vtc-bg-start) 0%, var(--vtc-bg-end) 100%);
  color: var(--vtc-text-main);
}

.vuetoy-config.is-dark-theme {
  --vtc-bg-start: #212534;
  --vtc-bg-end: #14161f;
  --vtc-panel: rgba(26, 28, 39, 0.92);
  --vtc-panel-strong: rgba(19, 21, 30, 0.98);
  --vtc-border: rgba(124, 92, 255, 0.18);
  --vtc-chip: rgba(139, 108, 255, 0.14);
  --vtc-text-main: #f3f5ff;
  --vtc-text-soft: rgba(159, 167, 196, 0.92);
  --vtc-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  background:
    radial-gradient(circle at top, rgba(33, 37, 52, 0.92) 0%, rgba(23, 26, 36, 0.98) 38%, #14161f 100%),
    linear-gradient(180deg, var(--vtc-bg-start) 0%, var(--vtc-bg-end) 100%);
}

.vuetoy-config,
.vuetoy-config * {
  box-sizing: border-box;
}

.vtc-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 18px 16px 26px;
  display: grid;
  gap: 14px;
}

.vtc-card {
  border: 1px solid var(--vtc-border);
  border-radius: 28px;
  background: var(--vtc-panel);
  box-shadow: var(--vtc-shadow);
  backdrop-filter: blur(18px);
}

.vtc-hero,
.vtc-card {
  padding: 20px 22px;
}

.vtc-hero {
  display: grid;
  grid-template-columns: 1.35fr auto;
  gap: 20px;
  align-items: center;
}

.vtc-badge,
.vtc-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}

.vtc-badge {
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 800;
  background: var(--vtc-chip);
  color: #8b6cff;
}

.vtc-title {
  margin: 12px 0 8px;
  font-size: clamp(28px, 3.8vw, 38px);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.vtc-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.vtc-chip {
  padding: 7px 12px;
  border: 1px solid var(--vtc-border);
  background: var(--vtc-panel-strong);
  font-size: 12px;
  color: var(--vtc-text-soft);
}

.vtc-action-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  align-items: center;
}

.vtc-section-title {
  margin: 0 0 14px;
  font-size: 22px;
}

.vtc-switch-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.vtc-switch-card,
.vtc-field-card {
  border: 1px solid var(--vtc-border);
  border-radius: 22px;
  background: var(--vtc-panel-strong);
}

.vtc-switch-card {
  padding: 12px 16px;
}

.vtc-switch :deep(.v-label) {
  font-size: 14px;
}

.vtc-field-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.vtc-field-card {
  padding: 16px;
}

.vtc-field-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--vtc-text-soft);
  margin-bottom: 10px;
}

.vtc-note {
  font-size: 13px;
  line-height: 1.6;
  color: var(--vtc-text-soft);
}

@media (max-width: 1100px) {
  .vtc-hero {
    grid-template-columns: 1fr;
  }

  .vtc-action-grid {
    justify-content: flex-start;
  }

  .vtc-switch-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .vtc-shell {
    padding: 14px 10px 20px;
  }

  .vtc-hero,
  .vtc-card {
    padding: 18px;
  }

  .vtc-title {
    font-size: 30px;
  }

  .vtc-switch-grid {
    grid-template-columns: 1fr;
  }
}
</style>
