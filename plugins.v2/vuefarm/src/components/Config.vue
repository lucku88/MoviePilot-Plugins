<template>
  <div ref="rootEl" class="vuefarm-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vfc-shell">
      <header class="vfc-card vfc-hero">
        <div class="vfc-copy">
          <div class="vfc-badge">Vue-农场</div>
          <h1 class="vfc-title">插件配置</h1>
          <div class="vfc-chip-row">
            <span class="vfc-chip">{{ config.auto_cookie ? '站点 Cookie：自动同步' : '站点 Cookie：手动填写' }}</span>
            <span class="vfc-chip">优先种子：{{ config.prefer_seed || '未选择' }}</span>
          </div>
        </div>
        <div class="vfc-action-grid">
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vfc-card">
        <h2 class="vfc-section-title">⚙️ 基本设置</h2>
        <div class="vfc-switch-grid">
          <div class="vfc-switch-card">
            <v-switch v-model="config.enabled" class="vfc-switch" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vfc-switch-card">
            <v-switch v-model="config.use_proxy" class="vfc-switch" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vfc-switch-card">
            <v-switch v-model="config.notify" class="vfc-switch" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vfc-switch-card">
            <v-switch v-model="config.onlyonce" class="vfc-switch" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="vfc-card">
        <h2 class="vfc-section-title">🧩 功能设置</h2>
        <div class="vfc-switch-grid">
          <div class="vfc-switch-card">
            <v-switch v-model="config.auto_cookie" class="vfc-switch" label="使用站点 Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vfc-switch-card">
            <v-switch v-model="config.enable_sell" class="vfc-switch" label="自动出售" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vfc-switch-card">
            <v-switch v-model="config.enable_plant" class="vfc-switch" label="自动种植" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="vfc-field-grid">
          <div class="vfc-field-card">
            <div class="vfc-field-label">站点 Cookie</div>
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
            <div class="vfc-note">启用后自动读取站点 Cookie，关闭后才可手动修改。</div>
          </div>

          <div class="vfc-field-card">
            <div class="vfc-field-label">优先种子</div>
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

          <div class="vfc-field-card">
            <div class="vfc-field-label">OCR API 地址</div>
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

      <section class="vfc-card">
        <h2 class="vfc-section-title">📘 OCR 说明</h2>
        <div class="vfc-note">批量收菜验证码依赖 OCR。未配置 OCR 时，插件仍可刷新状态，并在批量收获失败后尝试逐坑位兜底收菜。</div>
        <div class="vfc-note">推荐先部署 <code>trwebocr</code>，再把 OCR 地址填成 <code>http://ip:8089/api/tr-run/</code>。</div>
        <pre class="vfc-code">{{ ocrComposeExample }}</pre>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({ initialConfig: { type: Object, default: () => ({}) }, api: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
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
    if (config.auto_cookie) return truncateCookie(config.cookie)
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) config.cookie = value || ''
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

function normalizeSeedValue(value) {
  const text = String(value || '').replace(/\s+/g, '').trim()
  if (!text) return ''
  const matched = seedOptions.value.find((item) => String(item || '').replace(/\s+/g, '').trim() === text)
  return matched || String(value || '').trim()
}

function normalizeSeeds(items) {
  const normalized = (items || []).map((item) => (typeof item === 'string' ? item : item?.value || item?.name || '')).filter(Boolean)
  if (config.prefer_seed && !normalized.includes(config.prefer_seed)) normalized.unshift(config.prefer_seed)
  return normalized.length ? normalized : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function applySeedOptions(items) {
  seedOptions.value = normalizeSeeds(items)
}

function applyStatusSeedOptions(seedShop) {
  const unlocked = (seedShop || []).filter((seed) => seed.unlocked && seed.name).map((seed) => seed.name)
  if (unlocked.length) applySeedOptions(unlocked)
}

async function loadStatusSeedOptions() {
  try {
    const res = await props.api.get('/plugin/VueFarm/status')
    applyStatusSeedOptions(res?.farm_status?.seed_shop)
    config.prefer_seed = normalizeSeedValue(config.prefer_seed)
  } catch (error) {}
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VueFarm/config')
    Object.assign(config, res || {})
    applySeedOptions(res?.seed_options)
    config.prefer_seed = normalizeSeedValue(config.prefer_seed)
    await loadStatusSeedOptions()
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const payload = { ...config, prefer_seed: normalizeSeedValue(config.prefer_seed) }
    const res = await props.api.post('/plugin/VueFarm/config', payload)
    if (res.config) {
      Object.assign(config, res.config)
      applySeedOptions(res.config.seed_options)
      config.prefer_seed = normalizeSeedValue(config.prefer_seed)
    }
    flash(res.message || '配置已保存')
    if (config.onlyonce) config.onlyonce = false
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  saving.value = true
  try {
    const res = await props.api.get('/plugin/VueFarm/cookie')
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
    const cls = String(current.className || '').toLowerCase()
    if (cls.includes('theme') || cls.includes('v-theme--') || cls.includes('dark') || cls.includes('light')) return current
    current = current.parentElement
  }
  const bodyCls = String(document.body?.className || '').toLowerCase()
  if (document.body?.getAttribute('data-theme') || bodyCls.includes('theme') || bodyCls.includes('v-theme--') || bodyCls.includes('dark') || bodyCls.includes('light')) return document.body
  const rootCls = String(document.documentElement?.className || '').toLowerCase()
  if (document.documentElement?.getAttribute('data-theme') || rootCls.includes('theme') || rootCls.includes('v-theme--') || rootCls.includes('dark') || rootCls.includes('light')) return document.documentElement
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function detectTheme() {
  const nodes = getThemeNodes()
  const isDark = nodes.some((node) => {
    const theme = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
    const cls = String(node?.className || '').toLowerCase()
    return ['dark', 'purple', 'transparent'].includes(theme) || cls.includes('dark') || cls.includes('theme-dark') || cls.includes('v-theme--dark')
  })
  if (isDark) {
    isDarkTheme.value = true
    return
  }
  const isLight = nodes.some((node) => {
    const theme = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
    const cls = String(node?.className || '').toLowerCase()
    return theme === 'light' || cls.includes('light') || cls.includes('theme-light') || cls.includes('v-theme--light')
  })
  if (isLight) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  detectTheme()
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    getThemeNodes().forEach((node) => themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class'] }))
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
}

function closePlugin() {
  emit('close')
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
.vuefarm-config{--panel:rgba(255,255,255,.84);--panel-strong:rgba(255,255,255,.94);--panel-soft:rgba(255,255,255,.72);--text:#24273a;--muted:#757b92;--border:rgba(125,132,170,.2);--shadow:0 20px 48px rgba(17,24,39,.08);--accent:#7c5cff;--accent-soft:rgba(124,92,255,.1);min-height:100%;padding:10px 0 20px;background:transparent;color:var(--text)}
.vuefarm-config.is-dark-theme{--panel:rgba(24,26,37,.82);--panel-strong:rgba(19,21,30,.94);--panel-soft:rgba(34,36,50,.72);--text:#f4f6ff;--muted:#a0a8c5;--border:rgba(124,92,255,.18);--shadow:0 24px 54px rgba(0,0,0,.32);--accent:#8b6cff;--accent-soft:rgba(139,108,255,.16)}
.vuefarm-config,.vuefarm-config *{box-sizing:border-box}
.vfc-shell{max-width:1180px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vfc-card{padding:16px;border:1px solid var(--border);border-radius:20px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vfc-hero{display:flex;gap:14px;justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(124,92,255,.18) 0%,transparent 34%),linear-gradient(135deg,var(--accent-soft) 0%,transparent 52%),var(--panel)}
.vfc-copy{flex:1;min-width:0}
.vfc-badge,.vfc-chip{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vfc-badge{width:fit-content;padding:6px 12px;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700}
.vfc-title{margin:10px 0 6px;font-size:clamp(24px,3.7vw,32px);line-height:1.08;font-weight:900}
.vfc-chip-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.vfc-chip{padding:7px 12px;border:1px solid var(--border);background:var(--panel-strong);color:var(--text);font-size:12px;font-weight:600;justify-content:flex-start}
.vfc-note{color:var(--muted);font-size:12px;line-height:1.65}
.vfc-action-grid{display:flex;align-items:center;justify-content:flex-end;gap:10px;flex-wrap:nowrap;min-width:min(100%,520px)}
.vfc-action-grid :deep(.v-btn){min-height:42px;border-radius:14px;font-weight:800}
.vfc-action-grid :deep(.v-btn--variant-flat){min-width:132px}
.vfc-action-grid :deep(.v-btn--variant-text){min-width:auto;padding-inline:6px}
.vfc-switch-grid,.vfc-field-grid{display:grid;gap:12px}
.vfc-section-title{margin:0 0 14px;font-size:18px;font-weight:900}
.vfc-switch-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vfc-switch-card,.vfc-field-card{padding:14px;border:1px solid var(--border);border-radius:18px;background:var(--panel-strong)}
.vfc-field-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vfc-field-card:nth-child(1){background:linear-gradient(135deg,rgba(124,92,255,.12) 0%,transparent 48%),var(--panel-strong)}
.vfc-field-card:nth-child(2){background:linear-gradient(135deg,rgba(255,171,64,.12) 0%,transparent 48%),var(--panel-strong)}
.vfc-field-card:nth-child(3){background:linear-gradient(135deg,rgba(76,132,255,.12) 0%,transparent 48%),var(--panel-strong)}
.vfc-field-label{margin-bottom:8px;font-size:13px;font-weight:700;color:var(--muted)}
.vfc-code{margin-top:14px;padding:16px 18px;border-radius:18px;border:1px solid var(--border);background:var(--panel-strong);color:var(--text);font-size:13px;line-height:1.6;overflow-x:auto}
:deep(.vuefarm-config .v-field),:deep(.vuefarm-config .v-selection-control){color:var(--text)}
:deep(.vuefarm-config .v-field){background:rgba(255,255,255,.02);border-radius:14px}
:deep(.vuefarm-config .v-field__input),:deep(.vuefarm-config .v-label),:deep(.vuefarm-config .v-select__selection-text),:deep(.vuefarm-config .v-field__outline),:deep(.vuefarm-config .v-field__append-inner){color:var(--text)}
:deep(.vuefarm-config .v-field--disabled){opacity:.82}
:deep(.vuefarm-config .v-selection-control){min-height:28px}
:deep(.vuefarm-config .v-label){opacity:1;font-weight:600;font-size:12px;line-height:1.35}
:deep(.vuefarm-config .v-selection-control__wrapper){width:30px;height:18px;margin-right:6px}
:deep(.vuefarm-config .v-switch__track){min-width:30px;width:30px;height:18px;border-radius:999px}
:deep(.vuefarm-config .v-switch__thumb){width:12px;height:12px}
:deep(.vuefarm-config .v-field__input){min-height:40px;padding-top:0;padding-bottom:0;font-size:13px}
:deep(.vuefarm-config .v-field__outline){--v-field-border-opacity:1}
:deep(.vuefarm-config .v-selection-control__input > .v-icon),:deep(.vuefarm-config .v-switch__track){color:var(--accent)}
@media (max-width:1080px){.vfc-switch-grid,.vfc-field-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.vfc-action-grid{flex-wrap:wrap;justify-content:flex-start;min-width:0}}
@media (max-width:760px){.vfc-shell{padding:0 10px}.vfc-card{padding:14px;border-radius:18px}.vfc-hero,.vfc-switch-grid,.vfc-field-grid{grid-template-columns:1fr;display:grid}.vfc-action-grid{gap:10px}.vfc-action-grid :deep(.v-btn--variant-flat){min-width:0;flex:1 1 calc(50% - 10px)}}
</style>
