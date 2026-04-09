<template>
  <div ref="rootEl" class="emoji-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="emoji-shell">
      <section class="emoji-hero">
        <div>
          <div class="emoji-badge">SQ表情</div>
          <h1 class="emoji-title">配置中心</h1>
          <p class="emoji-subtitle">管理老虎机/开包时间、自动舞台演出和 Cookie 同步。</p>
        </div>
        <div class="emoji-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="emoji-panel">
        <div class="emoji-panel-head">
          <div>
            <div class="emoji-panel-kicker">基础开关</div>
            <h2>运行控制</h2>
          </div>
        </div>
        <div class="emoji-switch-grid">
          <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
          <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
          <v-switch v-model="config.onlyonce" label="保存后执行一次" color="warning" hide-details />
          <v-switch v-model="config.auto_cookie" label="优先使用站点 Cookie" color="info" hide-details />
          <v-switch v-model="config.auto_stage" label="自动舞台演出" color="deep-orange" hide-details />
          <v-switch v-model="config.auto_spin" label="自动清空当日老虎机次数" color="deep-purple" hide-details />
          <v-switch v-model="config.auto_open_bags" label="自动开包并自动收下" color="teal" hide-details />
          <v-switch v-model="config.use_proxy" label="使用代理" color="secondary" hide-details />
          <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
        </div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-panel-head">
          <div>
            <div class="emoji-panel-kicker">调度策略</div>
            <h2>时间配置</h2>
          </div>
        </div>
        <VCronField
          v-model="config.spin_cron"
          label="老虎机/开包执行周期(cron)"
          hint="例如：5 0 * * * 表示每天 00:05 执行老虎机和自动开包"
          persistent-hint
          density="compact"
          class="emoji-cron-field"
        />
        <div class="emoji-form-grid">
          <v-select
            v-model="config.auto_stage_effect_key"
            :items="effectOptions"
            item-title="title"
            item-value="value"
            label="自动演出舞台效果"
            variant="outlined"
            density="comfortable"
            :disabled="!config.auto_stage"
          />
        </div>
        <div class="emoji-note">自动老虎机和自动开包按上面的 CRON 运行；舞台效果下拉只显示已解锁项。</div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-panel-head">
          <div>
            <div class="emoji-panel-kicker">手动 Cookie</div>
            <h2>Cookie 兜底</h2>
          </div>
        </div>
        <v-textarea
          v-model="config.cookie"
          label="SQ Cookie"
          rows="6"
          variant="outlined"
          density="comfortable"
          placeholder="例如 c_secure_pass=..."
        />
        <div class="emoji-note">
          默认读取 <code>si-qi.xyz</code> 站点配置中的 Cookie。开启“优先使用站点 Cookie”后，会优先使用 MoviePilot 站点管理中的值。
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const pluginBase = '/plugin/SQEmoji'
const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const effectOptions = ref([{ title: '自动选择最佳舞台效果', value: 'auto' }])
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

let themeObserver = null
let mediaQuery = null

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function applyConfig(data = {}) {
  if (Array.isArray(data.effect_options) && data.effect_options.length) {
    effectOptions.value = data.effect_options
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
  --emoji-bg: linear-gradient(180deg, #f7f0e2 0%, #f4f2ef 100%);
  --emoji-card: rgba(255, 255, 255, 0.9);
  --emoji-text: #5a330d;
  --emoji-muted: #9b7855;
  --emoji-border: rgba(232, 168, 104, 0.28);
  --emoji-shadow: 0 18px 36px rgba(167, 120, 63, 0.08);
  --emoji-accent: #df7a11;
  --emoji-accent-soft: rgba(223, 122, 17, 0.12);
  min-height: 100vh;
  padding: 20px 0 32px;
  background: var(--emoji-bg);
  color: var(--emoji-text);
}

.emoji-config.is-dark-theme {
  --emoji-bg: linear-gradient(180deg, #181513 0%, #121010 100%);
  --emoji-card: rgba(31, 24, 22, 0.92);
  --emoji-text: #f8eadb;
  --emoji-muted: #ccb298;
  --emoji-border: rgba(255, 185, 106, 0.18);
  --emoji-shadow: 0 20px 40px rgba(0, 0, 0, 0.28);
  --emoji-accent: #ffb24c;
  --emoji-accent-soft: rgba(255, 178, 76, 0.14);
}

.emoji-shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 12px;
  display: grid;
  gap: 16px;
}

.emoji-hero,
.emoji-panel {
  border: 1px solid var(--emoji-border);
  border-radius: 24px;
  background: var(--emoji-card);
  box-shadow: var(--emoji-shadow);
  padding: 20px;
}

.emoji-hero {
  display: grid;
  gap: 14px;
}

.emoji-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--emoji-accent-soft);
  color: var(--emoji-accent);
  font-size: 12px;
  font-weight: 700;
}

.emoji-title {
  margin: 10px 0 6px;
  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.05;
}

.emoji-subtitle,
.emoji-note {
  color: var(--emoji-muted);
}

.emoji-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(108px, 100%), 1fr));
  gap: 12px;
}

.emoji-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.emoji-panel-head h2 {
  margin: 6px 0 0;
  font-size: 24px;
}

.emoji-panel-kicker {
  font-size: 13px;
  color: var(--emoji-muted);
  font-weight: 700;
}

.emoji-switch-grid,
.emoji-form-grid {
  display: grid;
  gap: 14px 18px;
}

.emoji-switch-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.emoji-form-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.emoji-note {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.7;
}

@media (max-width: 860px) {
  .emoji-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .emoji-switch-grid,
  .emoji-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
