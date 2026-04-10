<template>
  <div ref="rootEl" class="farm-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="farm-shell">
      <header class="farm-hero">
        <div class="farm-copy">
          <div class="farm-badge">SQ农场2</div>
          <h1 class="farm-title">插件配置</h1>
          <p class="farm-subtitle">收菜、种植、出售、获取执行记录。</p>
        </div>
        <div class="farm-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="farm-card">
        <h2 class="farm-section-title">⚙️ 基本设置</h2>
        <div class="farm-switch-grid farm-switch-grid-basic">
          <div class="farm-switch-item">
            <v-switch v-model="config.enabled" class="farm-switch" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="farm-switch-item">
            <v-switch v-model="config.use_proxy" class="farm-switch" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="farm-switch-item">
            <v-switch v-model="config.notify" class="farm-switch" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="farm-switch-item">
            <v-switch v-model="config.onlyonce" class="farm-switch" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="farm-card">
        <h2 class="farm-section-title">🧩 功能设置</h2>

        <div class="farm-switch-grid">
          <div class="farm-switch-item">
            <v-switch v-model="config.auto_cookie" class="farm-switch" label="使用站点 Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="farm-switch-item">
            <v-switch v-model="config.enable_sell" class="farm-switch" label="自动出售" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="farm-switch-item">
            <v-switch v-model="config.enable_plant" class="farm-switch" label="自动种植" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="farm-field-grid">
          <div class="farm-field-card">
            <div class="farm-field-title">站点 Cookie</div>
            <v-text-field
              v-model="cookieFieldValue"
              label="站点 Cookie"
              variant="outlined"
              density="comfortable"
              :disabled="cookieReadonly"
              :readonly="cookieReadonly"
              :placeholder="cookieReadonly ? '启用站点 Cookie 后自动同步' : '例如 c_secure_pass=...'"
              hide-details="auto"
            />
            <div class="farm-field-note">
              启用【使用站点 Cookie】后会自动读取已配置站点的 Cookie，关闭后才可以手动修改。
            </div>
          </div>

          <div class="farm-field-card">
            <div class="farm-field-title">优先种子</div>
            <v-select
              v-model="config.prefer_seed"
              :items="seedOptions"
              label="优先种子"
              variant="outlined"
              density="comfortable"
              :menu-props="{ maxHeight: 280 }"
              hide-details="auto"
            />
          </div>

          <div class="farm-field-card">
            <div class="farm-field-title">OCR API 地址</div>
            <v-text-field
              v-model="config.ocr_api_url"
              label="OCR API 地址"
              variant="outlined"
              density="comfortable"
              placeholder="http://ip:8089/api/tr-run/"
              hide-details="auto"
            />
          </div>
        </div>
      </section>

      <section class="farm-card">
        <h2 class="farm-section-title">📝 OCR 说明</h2>
        <div class="farm-note">
          批量收菜验证码依赖 OCR。未配置 OCR 时，插件仍可刷新状态，并在批量收菜失败后尝试逐坑位兜底收菜。
        </div>
        <div class="farm-note">推荐先部署 <code>trwebocr</code>，再把 OCR 地址填成 <code>http://ip:8089/api/tr-run/</code>。</div>
        <pre class="farm-code">{{ ocrComposeExample }}</pre>
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
const message = reactive({ text: '', type: 'success' })
const seedOptions = ref(['西红柿'])
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_sell: true,
  enable_plant: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
})

const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    environment:
      - TZ=Asia/Shanghai`

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
  return text.length > 36 ? `${text.slice(0, 36)}...` : text
}

function normalizeSeeds(items) {
  const normalized = (items || [])
    .map((item) => (typeof item === 'string' ? item : item?.value || item?.name || ''))
    .filter(Boolean)

  if (config.prefer_seed && !normalized.includes(config.prefer_seed)) {
    normalized.unshift(config.prefer_seed)
  }

  return normalized.length ? normalized : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function applySeedOptions(items) {
  seedOptions.value = normalizeSeeds(items)
}

function applyStatusSeedOptions(seedShop) {
  const unlocked = (seedShop || [])
    .filter((seed) => seed.unlocked && seed.name)
    .map((seed) => seed.name)
  if (unlocked.length) {
    applySeedOptions(unlocked)
  }
}

async function loadStatusSeedOptions() {
  try {
    const res = await props.api.get('/plugin/SQFarm2/status')
    applyStatusSeedOptions(res?.farm_status?.seed_shop)
  } catch (error) {
    // 保留当前种子列表
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/SQFarm2/config')
    Object.assign(config, res || {})
    applySeedOptions(res?.seed_options)
    await loadStatusSeedOptions()
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm2/config', { ...config })
    if (res.config) {
      Object.assign(config, res.config)
      applySeedOptions(res.config.seed_options)
    }
    flash(res.message || '配置已保存')
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
    const res = await props.api.get('/plugin/SQFarm2/cookie')
    if (res.config) {
      Object.assign(config, res.config)
      applySeedOptions(res.config.seed_options)
    }
    await loadStatusSeedOptions()
    flash(res.message || 'Cookie 已同步')
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
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
  const hasDark = nodes.some((node) => nodeHasDarkHint(node))
  const hasLight = nodes.some((node) => nodeHasLightHint(node))
  if (hasDark) {
    isDarkTheme.value = true
    return
  }
  if (hasLight) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  themeObserver?.disconnect()
  themeObserver = new MutationObserver(() => {
    detectTheme()
  })

  for (const node of getThemeNodes()) {
    themeObserver.observe(node, {
      attributes: true,
      subtree: true,
      attributeFilter: ['data-theme', 'class'],
    })
  }
}

function closePlugin() {
  emit('close')
}

onMounted(() => {
  detectTheme()
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)')
  mediaQuery?.addEventListener?.('change', detectTheme)
  bindThemeObserver()
  loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style>
.farm-config {
  --farm-bg: linear-gradient(180deg, #f4f5f8 0%, #fafafb 46%, #f2f4f8 100%);
  --farm-surface: rgba(255, 255, 255, 0.86);
  --farm-surface-strong: rgba(255, 255, 255, 0.96);
  --farm-border: rgba(122, 134, 167, 0.16);
  --farm-shadow: 0 20px 42px rgba(91, 102, 130, 0.1);
  --farm-text: #2f3347;
  --farm-subtle: #6e758e;
  --farm-soft: #8d93aa;
  --farm-accent: #7c5cff;
  --farm-accent-soft: rgba(124, 92, 255, 0.12);
  min-height: 100%;
  padding: clamp(18px, 2.4vw, 28px);
  background: var(--farm-bg);
  color: var(--farm-text);
}

.farm-config.is-dark-theme {
  --farm-bg: linear-gradient(180deg, #171921 0%, #12151d 48%, #0d1017 100%);
  --farm-surface: rgba(24, 28, 39, 0.88);
  --farm-surface-strong: rgba(24, 28, 39, 0.96);
  --farm-border: rgba(111, 122, 168, 0.2);
  --farm-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
  --farm-text: #eff1f7;
  --farm-subtle: #b5bbd3;
  --farm-soft: #868fae;
  --farm-accent: #8c72ff;
  --farm-accent-soft: rgba(124, 92, 255, 0.18);
}

.farm-shell {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.farm-hero,
.farm-card {
  border: 1px solid var(--farm-border);
  box-shadow: var(--farm-shadow);
}

.farm-hero {
  padding: clamp(22px, 3vw, 32px);
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(124, 92, 255, 0.14), transparent 28%),
    radial-gradient(circle at bottom left, rgba(255, 184, 0, 0.12), transparent 26%),
    var(--farm-surface-strong);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px 24px;
  align-items: start;
}

.farm-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--farm-accent-soft);
  color: var(--farm-accent);
  font-size: 12px;
  font-weight: 700;
}

.farm-title {
  margin: 14px 0 8px;
  font-size: clamp(30px, 4vw, 40px);
  line-height: 1.05;
  font-weight: 900;
}

.farm-subtitle {
  margin: 0;
  color: var(--farm-subtle);
  font-size: 15px;
}

.farm-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.farm-card {
  padding: 22px;
  border-radius: 24px;
  background: var(--farm-surface);
  backdrop-filter: blur(12px);
}

.farm-section-title {
  margin: 0 0 18px;
  font-size: 28px;
  line-height: 1.1;
  font-weight: 900;
}

.farm-switch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.farm-switch-grid-basic {
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}

.farm-switch-item {
  display: flex;
  align-items: center;
  min-height: 72px;
  padding: 0 14px;
  border: 1px solid var(--farm-border);
  border-radius: 22px;
  background: color-mix(in srgb, var(--farm-surface-strong) 92%, transparent);
}

.farm-switch .v-selection-control {
  min-height: 36px;
}

.farm-switch .v-selection-control__wrapper {
  transform: scale(0.82);
  transform-origin: left center;
}

.farm-switch .v-label {
  opacity: 1;
  color: var(--farm-text);
  font-weight: 700;
}

.farm-field-grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.farm-field-card {
  min-height: 0;
  padding: 16px;
  border-radius: 22px;
  border: 1px solid var(--farm-border);
  background: color-mix(in srgb, var(--farm-surface-strong) 94%, transparent);
}

.farm-field-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 800;
  color: var(--farm-subtle);
}

.farm-field-note,
.farm-note {
  color: var(--farm-subtle);
  font-size: 13px;
  line-height: 1.75;
}

.farm-field-note {
  margin-top: 10px;
}

.farm-code {
  margin-top: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid var(--farm-border);
  background: rgba(245, 247, 252, 0.92);
  color: var(--farm-text);
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
}

.farm-config.is-dark-theme .farm-code {
  background: rgba(31, 36, 49, 0.92);
}

@media (max-width: 980px) {
  .farm-hero {
    grid-template-columns: 1fr;
  }

  .farm-actions {
    justify-content: flex-start;
  }

  .farm-field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
