<template>
  <div ref="rootEl" class="pill-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pill-shell">
      <header class="pill-config-header">
        <div class="pill-header-copy">
          <div class="pill-badge">SQ魔丸</div>
          <h1 class="pill-page-title">插件配置</h1>
          <p class="pill-page-subtitle">兑换、搬砖、清沙滩、炼造、获取执行记录。</p>
        </div>
        <div class="pill-header-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="pill-settings-card">
        <h2 class="pill-settings-title">⚙️ 基本设置</h2>
        <div class="pill-switch-grid pill-switch-grid-basic">
          <div class="pill-switch-item">
            <v-switch v-model="config.enabled" class="pill-switch-control" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.use_proxy" class="pill-switch-control" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.notify" class="pill-switch-control" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.onlyonce" class="pill-switch-control" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="pill-settings-card">
        <h2 class="pill-settings-title">🧩 功能设置</h2>

        <div class="pill-switch-grid">
          <div class="pill-switch-item">
            <v-switch v-model="config.auto_cookie" class="pill-switch-control" label="使用站点Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.enable_brick" class="pill-switch-control" label="搬砖" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.enable_beach" class="pill-switch-control" label="清沙滩" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.auto_craft" class="pill-switch-control" label="炼造" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.auto_exchange" class="pill-switch-control" label="兑换" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="pill-switch-item">
            <v-switch v-model="config.force_ipv4" class="pill-switch-control" label="优先 IPv4" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="pill-field-grid">
          <div class="pill-field-block">
            <div class="pill-field-label">站点Cookie</div>
            <v-text-field
              v-model="cookieFieldValue"
              label="站点Cookie"
              variant="outlined"
              density="comfortable"
              :disabled="cookieReadonly"
              :readonly="cookieReadonly"
              :placeholder="cookieReadonly ? '启用站点Cookie后自动同步' : '例如 c_secure_pass=...'"
            />
            <div class="pill-note">
              启用【使用站点Cookie】后会自动读取已配置站点的 Cookie，关闭后才可手动修改。
            </div>
          </div>

          <div class="pill-field-block">
            <div class="pill-field-label">执行周期</div>
            <VCronField
              v-model="config.brick_cron"
              label="搬砖执行周期(cron)"
              density="comfortable"
              class="pill-cron-field"
            />
          </div>

          <div class="pill-field-block">
            <div class="pill-field-label">保留材料数量</div>
            <v-text-field
              v-model="config.reserve_material_count"
              label="每种材料保留数量"
              type="number"
              variant="outlined"
              density="comfortable"
            />
          </div>

          <div class="pill-field-block">
            <div class="pill-field-label">保留魔丸数量</div>
            <v-text-field
              v-model="config.reserve_magic_pill_count"
              label="魔丸保留数量"
              type="number"
              variant="outlined"
              density="comfortable"
            />
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

const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const pluginBase = '/plugin/SQPill'
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  move_delay_min_ms: 30,
  move_delay_max_ms: 80,
  ready_retry_seconds: 60,
  reserve_material_count: 0,
  reserve_magic_pill_count: 0,
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
  Object.assign(config, {
    ...config,
    ...data,
  })
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
      themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class'] })
    })
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
}

onMounted(async () => {
  bindThemeObserver()
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.pill-config {
  --pill-bg: radial-gradient(circle at top, rgba(255, 255, 255, 0.95) 0%, rgba(246, 247, 250, 0.98) 42%, #eef1f7 100%);
  --pill-panel: rgba(255, 255, 255, 0.9);
  --pill-panel-strong: rgba(255, 255, 255, 0.98);
  --pill-text: #262638;
  --pill-muted: #76778b;
  --pill-border: rgba(129, 133, 164, 0.18);
  --pill-shadow: 0 20px 48px rgba(121, 128, 166, 0.12);
  --pill-accent: #7c5cff;
  --pill-accent-soft: rgba(124, 92, 255, 0.1);
  min-height: auto;
  padding: 10px 0 8px;
  background: transparent;
  color: var(--pill-text);
}

.pill-config.is-dark-theme {
  --pill-bg: radial-gradient(circle at top, rgba(33, 37, 52, 0.92) 0%, rgba(23, 26, 36, 0.98) 38%, #14161f 100%);
  --pill-panel: rgba(26, 28, 39, 0.92);
  --pill-panel-strong: rgba(19, 21, 30, 0.98);
  --pill-text: #f3f5ff;
  --pill-muted: #9fa7c4;
  --pill-border: rgba(124, 92, 255, 0.18);
  --pill-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  --pill-accent: #8b6cff;
  --pill-accent-soft: rgba(139, 108, 255, 0.14);
}

.pill-config,
.pill-config * {
  box-sizing: border-box;
}

.pill-shell {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
  display: grid;
  gap: 14px;
}

.pill-config-header,
.pill-settings-card {
  border: 1px solid var(--pill-border);
  border-radius: 18px;
  background: var(--pill-panel);
  box-shadow: var(--pill-shadow);
}

.pill-config-header {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.pill-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--pill-accent-soft);
  color: var(--pill-accent);
  font-size: 12px;
  font-weight: 700;
}

.pill-page-title {
  margin: 10px 0 6px;
  font-size: clamp(24px, 3.8vw, 32px);
  line-height: 1.08;
}

.pill-page-subtitle,
.pill-note {
  color: var(--pill-muted);
}

.pill-header-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
  gap: 10px;
}

.pill-settings-card {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.pill-settings-title {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.pill-switch-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.pill-switch-grid-basic {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.pill-switch-item {
  min-height: 44px;
  padding: 2px 8px;
  border-radius: 14px;
  border: 1px solid var(--pill-border);
  background: var(--pill-panel-strong);
  display: flex;
  align-items: center;
}

.pill-field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  align-items: stretch;
}

.pill-field-block {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--pill-border);
  background: var(--pill-panel-strong);
  display: grid;
  align-content: start;
  gap: 8px;
}

.pill-field-label {
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--pill-muted);
}

.pill-note {
  margin-top: 0;
  font-size: 12px;
  line-height: 1.45;
}

.pill-cron-field {
  padding: 0;
  background: transparent;
}

:deep(.pill-config .v-field),
:deep(.pill-config .v-selection-control) {
  color: var(--pill-text);
}

:deep(.pill-config .v-field) {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 14px;
}

:deep(.pill-config .v-field__input),
:deep(.pill-config .v-label),
:deep(.pill-config .v-select__selection-text),
:deep(.pill-config .v-field__outline),
:deep(.pill-config .v-field__append-inner) {
  color: var(--pill-text);
}

:deep(.pill-config .v-field--disabled) {
  opacity: 0.82;
}

:deep(.pill-config .pill-switch-control) {
  width: 100%;
  margin: 0;
}

:deep(.pill-config .pill-switch-control .v-selection-control) {
  min-height: 28px;
}

:deep(.pill-config .pill-switch-control .v-label) {
  color: var(--pill-text);
  opacity: 1;
  font-weight: 600;
  font-size: 12px;
  line-height: 1.35;
}

:deep(.pill-config .pill-switch-control .v-selection-control__wrapper) {
  width: 30px;
  height: 18px;
  margin-right: 6px;
}

:deep(.pill-config .pill-switch-control .v-switch__track) {
  min-width: 30px;
  width: 30px;
  height: 18px;
  border-radius: 999px;
}

:deep(.pill-config .pill-switch-control .v-switch__thumb) {
  width: 12px;
  height: 12px;
}

:deep(.pill-config .v-field__input) {
  min-height: 40px;
  padding-top: 0;
  padding-bottom: 0;
  font-size: 13px;
}

:deep(.pill-config .v-field__outline) {
  --v-field-border-opacity: 1;
}

:deep(.pill-config .v-selection-control__input > .v-icon),
:deep(.pill-config .v-switch__track) {
  color: var(--pill-accent);
}

:deep(.pill-config .v-alert) {
  border-radius: 18px;
}

@media (max-width: 1080px) {
  .pill-switch-grid,
  .pill-switch-grid-basic,
  .pill-field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .pill-shell {
    padding: 0 10px;
  }

  .pill-config-header,
  .pill-settings-card {
    padding: 18px 16px;
    border-radius: 20px;
  }

  .pill-header-actions,
  .pill-switch-grid,
  .pill-switch-grid-basic,
  .pill-field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
