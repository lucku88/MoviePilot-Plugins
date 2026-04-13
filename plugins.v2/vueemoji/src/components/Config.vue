<template>
  <div ref="rootEl" class="emoji-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="emoji-shell">
      <header class="emoji-card emoji-config-header">
        <div class="emoji-header-copy">
          <div class="emoji-badge">Vue-表情</div>
          <h1 class="emoji-page-title">插件配置</h1>
          <div class="emoji-chip-row">
            <span class="emoji-chip">站点 Cookie：{{ config.auto_cookie ? '自动同步' : '手动配置' }}</span>
          </div>
        </div>
        <div class="emoji-header-actions">
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="emoji-card emoji-settings-card emoji-settings-card-basic">
        <h2 class="emoji-settings-title">⚙️ 基本设置</h2>
        <div class="emoji-switch-grid emoji-switch-grid-basic">
          <div class="emoji-switch-item">
            <v-switch v-model="config.enabled" class="emoji-switch-control" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.use_proxy" class="emoji-switch-control" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.notify" class="emoji-switch-control" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.onlyonce" class="emoji-switch-control" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="emoji-card emoji-settings-card emoji-settings-card-feature">
        <h2 class="emoji-settings-title">🧩 功能设置</h2>

        <div class="emoji-switch-grid">
          <div class="emoji-switch-item">
            <v-switch v-model="config.auto_cookie" class="emoji-switch-control" label="使用站点Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.auto_stage" class="emoji-switch-control" label="自动舞台演出" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.auto_spin" class="emoji-switch-control" label="自动老虎机" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.auto_open_bags" class="emoji-switch-control" label="自动开包并收下" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="emoji-switch-item">
            <v-switch v-model="config.force_ipv4" class="emoji-switch-control" label="优先 IPv4" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="emoji-field-grid">
          <div class="emoji-field-block">
            <div class="emoji-field-label">站点Cookie</div>
            <v-text-field
              v-model="cookieFieldValue"
              label="站点Cookie"
              variant="outlined"
              density="comfortable"
              :disabled="cookieReadonly"
              :readonly="cookieReadonly"
              :placeholder="cookieReadonly ? '使用站点Cookie后自动同步' : '例如 c_secure_pass=...'"
            />
            <div class="emoji-note">
              启用【使用站点Cookie】功能后，插件会自动获取已配置站点的cookie，关闭使用站点Cookie功能才可以手动改cookie。
            </div>
          </div>

          <div class="emoji-field-block">
            <div class="emoji-field-label">执行周期</div>
            <VCronField
              v-model="config.spin_cron"
              label="老虎机/开包执行周期(cron)"
              density="comfortable"
              class="emoji-cron-field"
            />
          </div>

          <div class="emoji-field-block">
            <div class="emoji-field-label">演出舞台效果</div>
            <v-select
              v-model="config.auto_stage_effect_key"
              :items="effectOptions"
              item-title="title"
              item-value="value"
              label="演出舞台效果"
              variant="outlined"
              density="comfortable"
              :disabled="!config.auto_stage"
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

const pluginBase = '/plugin/VueEmoji'
const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const effectOptions = ref([{ title: '自动选择演出舞台效果', value: 'auto' }])
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  auto_stage: true,
  auto_spin: false,
  auto_open_bags: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  spin_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
  auto_stage_effect_key: 'auto',
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
  if (Array.isArray(data.effect_options) && data.effect_options.length) {
    effectOptions.value = data.effect_options
  } else {
    effectOptions.value = [{ title: '自动选择演出舞台效果', value: 'auto' }]
  }
  const { effect_options, capture_tips, ...rest } = data || {}
  Object.assign(config, { ...config, ...rest })
  if (!effectOptions.value.some((item) => item.value === config.auto_stage_effect_key)) {
    config.auto_stage_effect_key = 'auto'
  }
}

function buildPayload() {
  return { ...config }
}

async function loadConfig() {
  const data = await props.api.get(`${pluginBase}/config`)
  applyConfig(data || {})
}

async function saveConfig() {
  saving.value = true
  try {
    const result = await props.api.post(`${pluginBase}/config`, buildPayload())
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
.emoji-config {
  --emoji-bg: radial-gradient(circle at top left, rgba(124, 92, 255, 0.12) 0%, transparent 34%), linear-gradient(180deg, #f8f9fd 0%, #eef1f7 100%);
  --emoji-panel: rgba(255, 255, 255, 0.88);
  --emoji-panel-strong: rgba(255, 255, 255, 0.98);
  --emoji-text: #262638;
  --emoji-muted: #767d94;
  --emoji-border: rgba(129, 133, 164, 0.2);
  --emoji-shadow: 0 18px 40px rgba(121, 128, 166, 0.12);
  --emoji-accent: #7c5cff;
  --emoji-accent-soft: rgba(124, 92, 255, 0.08);
  min-height: auto;
  padding: 10px 0 8px;
  background: transparent;
  color: var(--emoji-text);
}

.emoji-config.is-dark-theme {
  --emoji-bg: radial-gradient(circle at top left, rgba(124, 92, 255, 0.16) 0%, transparent 34%), linear-gradient(180deg, rgba(27, 30, 44, 0.96) 0%, #14161f 100%);
  --emoji-panel: rgba(26, 28, 39, 0.9);
  --emoji-panel-strong: rgba(19, 21, 30, 0.98);
  --emoji-text: #f3f5ff;
  --emoji-muted: #9da5c0;
  --emoji-border: rgba(124, 92, 255, 0.2);
  --emoji-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  --emoji-accent: #8b6cff;
  --emoji-accent-soft: rgba(139, 108, 255, 0.14);
}

.emoji-config,
.emoji-config * {
  box-sizing: border-box;
}

.emoji-shell {
  max-width: 1220px;
  margin: 0 auto;
  padding: 0 12px;
  display: grid;
  gap: 14px;
}

.emoji-card,
.emoji-settings-card {
  border: 1px solid var(--emoji-border);
  border-radius: 20px;
  background: var(--emoji-panel);
  box-shadow: var(--emoji-shadow);
  backdrop-filter: blur(16px);
}

.emoji-config-header {
  padding: 16px;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  align-items: flex-start;
  background: radial-gradient(circle at top left, rgba(124, 92, 255, 0.16) 0%, transparent 30%), linear-gradient(135deg, var(--emoji-accent-soft) 0%, transparent 52%), var(--emoji-panel);
}

.emoji-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--emoji-accent-soft);
  color: var(--emoji-accent);
  font-size: 12px;
  font-weight: 800;
}

.emoji-page-title {
  margin: 10px 0 0;
  font-size: clamp(28px, 3.8vw, 36px);
  line-height: 1.05;
  font-weight: 900;
}

.emoji-chip-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.emoji-chip {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  color: var(--emoji-text);
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
}

.emoji-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  justify-content: flex-end;
  min-width: max-content;
}

.emoji-header-actions :deep(.v-btn) {
  min-height: 42px;
  border-radius: 14px;
  font-weight: 800;
}

.emoji-header-actions :deep(.v-btn--variant-flat) {
  min-width: 132px;
}

.emoji-header-actions :deep(.v-btn--variant-text) {
  min-width: auto;
  padding-inline: 6px;
}

.emoji-settings-card {
  padding: 14px;
  display: grid;
  gap: 12px;
}

.emoji-settings-card-basic {
  background: linear-gradient(135deg, rgba(124, 92, 255, 0.08) 0%, transparent 40%), var(--emoji-panel);
}

.emoji-settings-card-feature {
  background: linear-gradient(135deg, rgba(76, 132, 255, 0.09) 0%, transparent 40%), var(--emoji-panel);
}

.emoji-settings-title {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.emoji-switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.emoji-switch-grid-basic {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.emoji-switch-item {
  min-height: 46px;
  padding: 3px 10px;
  border-radius: 14px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  display: flex;
  align-items: center;
}

.emoji-field-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-items: stretch;
}

.emoji-field-block {
  padding: 12px;
  border-radius: 16px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  display: grid;
  align-content: start;
  gap: 8px;
}

.emoji-field-label {
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--emoji-muted);
}

.emoji-note {
  margin-top: 0;
  font-size: 12px;
  line-height: 1.55;
  color: var(--emoji-muted);
}

.emoji-cron-field {
  padding: 0;
  background: transparent;
}

:deep(.emoji-config .v-field),
:deep(.emoji-config .v-selection-control) {
  color: var(--emoji-text);
}

:deep(.emoji-config .v-field) {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 14px;
}

:deep(.emoji-config .v-field__input),
:deep(.emoji-config .v-label),
:deep(.emoji-config .v-select__selection-text),
:deep(.emoji-config .v-field__outline),
:deep(.emoji-config .v-field__append-inner) {
  color: var(--emoji-text);
}

:deep(.emoji-config .v-field--disabled) {
  opacity: 0.82;
}

:deep(.emoji-config .emoji-switch-control) {
  width: 100%;
  margin: 0;
}

:deep(.emoji-config .emoji-switch-control .v-selection-control) {
  min-height: 28px;
}

:deep(.emoji-config .emoji-switch-control .v-label) {
  color: var(--emoji-text);
  opacity: 1;
  font-weight: 700;
  font-size: 12px;
  line-height: 1.35;
}

:deep(.emoji-config .emoji-switch-control .v-selection-control__wrapper) {
  width: 30px;
  height: 18px;
  margin-right: 6px;
}

:deep(.emoji-config .emoji-switch-control .v-switch__track) {
  min-width: 30px;
  width: 30px;
  height: 18px;
  border-radius: 999px;
}

:deep(.emoji-config .emoji-switch-control .v-switch__thumb) {
  width: 12px;
  height: 12px;
}

:deep(.emoji-config .v-field__input) {
  min-height: 40px;
  padding-top: 0;
  padding-bottom: 0;
  font-size: 13px;
}

:deep(.emoji-config .v-field__outline) {
  --v-field-border-opacity: 1;
}

:deep(.emoji-config .v-selection-control__input > .v-icon),
:deep(.emoji-config .v-switch__track) {
  color: var(--emoji-accent);
}

:deep(.emoji-config .v-alert) {
  border-radius: 18px;
}

@media (max-width: 1080px) {
  .emoji-switch-grid,
  .emoji-switch-grid-basic {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .emoji-field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 920px) {
  .emoji-config-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .emoji-header-actions {
    flex-wrap: wrap;
    min-width: 0;
    justify-content: flex-start;
  }
}

@media (max-width: 760px) {
  .emoji-shell {
    padding: 0 10px;
  }

  .emoji-config-header,
  .emoji-settings-card {
    padding: 14px;
    border-radius: 18px;
  }

  .emoji-header-actions,
  .emoji-switch-grid,
  .emoji-switch-grid-basic,
  .emoji-field-grid {
    grid-template-columns: 1fr;
  }

  .emoji-header-actions :deep(.v-btn--variant-flat) {
    min-width: 0;
    flex: 1 1 calc(50% - 10px);
  }
}
</style>
