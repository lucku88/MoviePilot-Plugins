<template>
  <div ref="rootEl" class="vp-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vp-shell">
      <header class="vp-card vp-hero">
        <div class="vp-copy">
          <div class="vp-badge">Vue-魔丸</div>
          <h1 class="vp-title">插件配置</h1>
          <div class="vp-chip-row">
            <span class="vp-chip">{{ config.auto_cookie ? '站点 Cookie：自动同步' : '站点 Cookie：手动填写' }}</span>
          </div>
        </div>
        <div class="vp-action-grid">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vp-card">
        <h2 class="vp-section-title">⚙️ 基本设置</h2>
        <div class="vp-switch-grid">
          <div class="vp-switch-card">
            <v-switch v-model="config.enabled" class="vp-switch" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.use_proxy" class="vp-switch" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.notify" class="vp-switch" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.onlyonce" class="vp-switch" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="vp-card vp-panel">
        <h2 class="vp-section-title">🧩 功能设置</h2>

        <div class="vp-switch-grid">
          <div class="vp-switch-card">
            <v-switch v-model="config.auto_cookie" class="vp-switch" label="使用站点 Cookie" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.enable_brick" class="vp-switch" label="搬砖" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.enable_beach" class="vp-switch" label="清沙滩" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.auto_craft" class="vp-switch" label="炼造" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.auto_exchange" class="vp-switch" label="兑换" color="#7c5cff" density="compact" hide-details inset />
          </div>
          <div class="vp-switch-card">
            <v-switch v-model="config.force_ipv4" class="vp-switch" label="优先 IPv4" color="#7c5cff" density="compact" hide-details inset />
          </div>
        </div>

        <div class="vp-field-grid">
          <div class="vp-field-card vp-field-span-2">
            <div class="vp-field-label">站点 Cookie</div>
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
            <div class="vp-note">启用【使用站点 Cookie】后自动读取站点配置，关闭后才可手动修改。</div>
          </div>

          <div class="vp-field-card">
            <div class="vp-field-label">执行周期</div>
            <VCronField
              v-model="config.brick_cron"
              label="搬砖执行周期(cron)"
              density="comfortable"
              class="vp-cron-field"
            />
          </div>

          <div class="vp-field-card">
            <div class="vp-field-label">保留材料数量</div>
            <v-text-field
              v-model="config.reserve_material_count"
              label="每种材料保留数量"
              type="number"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
            />
          </div>

          <div class="vp-field-card">
            <div class="vp-field-label">保留魔丸数量</div>
            <v-text-field
              v-model="config.reserve_magic_pill_count"
              label="魔丸保留数量"
              type="number"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
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
const pluginBase = '/plugin/VuePill'
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
.vp-config{--panel:rgba(255,255,255,.84);--panel-strong:rgba(255,255,255,.94);--text:#24273a;--muted:#757b92;--border:rgba(125,132,170,.2);--shadow:0 20px 48px rgba(17,24,39,.08);--accent:#7c5cff;--accent-soft:rgba(124,92,255,.1);min-height:100%;padding:10px 0 20px;background:transparent;color:var(--text)}
.vp-config.is-dark-theme{--panel:rgba(24,26,37,.82);--panel-strong:rgba(19,21,30,.94);--text:#f4f6ff;--muted:#a0a8c5;--border:rgba(124,92,255,.18);--shadow:0 24px 54px rgba(0,0,0,.32);--accent:#8b6cff;--accent-soft:rgba(139,108,255,.16)}
.vp-config,.vp-config *{box-sizing:border-box}
.vp-shell{max-width:1180px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vp-card{padding:16px;border:1px solid var(--border);border-radius:20px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vp-switch-grid,.vp-field-grid{display:grid;gap:12px}
.vp-hero{background:linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vp-hero{display:flex;gap:14px;justify-content:space-between;align-items:flex-start}
.vp-copy{flex:1;min-width:0}
.vp-badge{display:inline-flex;align-items:center;justify-content:center;width:fit-content;padding:6px 12px;border-radius:999px;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700}
.vp-title{margin:10px 0 6px;font-size:clamp(24px,3.7vw,32px);line-height:1.08;font-weight:900}
.vp-note{color:var(--muted)}
.vp-chip-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.vp-chip{display:inline-flex;align-items:center;justify-content:flex-start;padding:7px 12px;border:1px solid var(--border);border-radius:999px;background:var(--panel-strong);color:var(--text);font-size:12px;font-weight:600}
.vp-action-grid{display:flex;align-items:center;justify-content:flex-end;gap:10px;flex-wrap:nowrap;min-width:min(100%,520px)}
.vp-action-grid :deep(.v-btn){min-height:42px;border-radius:14px;font-weight:800}
.vp-action-grid :deep(.v-btn--variant-flat){min-width:132px}
.vp-action-grid :deep(.v-btn--variant-text){min-width:auto;padding-inline:6px}
.vp-section-title{margin:0 0 14px;font-size:18px;font-weight:900}
.vp-panel{background:linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vp-switch-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vp-switch-card,.vp-field-card{padding:14px;border:1px solid var(--border);border-radius:18px;background:var(--panel-strong)}
.vp-field-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vp-field-span-2{grid-column:span 2}
.vp-field-label{margin-bottom:8px;font-size:13px;font-weight:700;color:var(--muted)}
.vp-note{font-size:12px;line-height:1.65}
.vp-cron-field{padding:0;background:transparent}
:deep(.vp-config .v-field),:deep(.vp-config .v-selection-control){color:var(--text)}
:deep(.vp-config .v-field){background:rgba(255,255,255,.02);border-radius:14px}
:deep(.vp-config .v-field__input),:deep(.vp-config .v-label),:deep(.vp-config .v-select__selection-text),:deep(.vp-config .v-field__outline),:deep(.vp-config .v-field__append-inner){color:var(--text)}
:deep(.vp-config .v-field--disabled){opacity:.82}
:deep(.vp-config .vp-switch){width:100%;margin:0}
:deep(.vp-config .vp-switch .v-selection-control){min-height:28px}
:deep(.vp-config .vp-switch .v-label){opacity:1;font-weight:600;font-size:12px;line-height:1.35}
:deep(.vp-config .vp-switch .v-selection-control__wrapper){width:30px;height:18px;margin-right:6px}
:deep(.vp-config .vp-switch .v-switch__track){min-width:30px;width:30px;height:18px;border-radius:999px}
:deep(.vp-config .vp-switch .v-switch__thumb){width:12px;height:12px}
:deep(.vp-config .v-field__input){min-height:40px;padding-top:0;padding-bottom:0;font-size:13px}
:deep(.vp-config .v-field__outline){--v-field-border-opacity:1}
:deep(.vp-config .v-selection-control__input > .v-icon),:deep(.vp-config .v-switch__track){color:var(--accent)}
@media (max-width:1080px){.vp-switch-grid,.vp-field-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.vp-field-span-2{grid-column:span 2}.vp-action-grid{flex-wrap:wrap;justify-content:flex-start;min-width:0}}
@media (max-width:760px){.vp-shell{padding:0 10px}.vp-card{padding:14px;border-radius:18px}.vp-hero,.vp-switch-grid,.vp-field-grid{grid-template-columns:1fr;display:grid}.vp-field-span-2{grid-column:auto}.vp-action-grid{gap:10px}.vp-action-grid :deep(.v-btn--variant-flat){min-width:0;flex:1 1 calc(50% - 10px)}}
</style>
