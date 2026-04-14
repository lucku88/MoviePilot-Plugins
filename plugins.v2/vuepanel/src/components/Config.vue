<template>
  <div ref="rootEl" class="vuepanel-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vpc-shell">
      <header class="vpc-card vpc-hero">
        <div class="vpc-copy">
          <div class="vpc-badge">Vue-面板</div>
          <h1 class="vpc-title">配置页</h1>
          <div class="vpc-chip-row">
            <span class="vpc-chip">固定任务 2 个</span>
            <span class="vpc-chip">New API 站点 {{ newApiCards.length }}</span>
            <span class="vpc-chip">定时卡片 {{ scheduledCards.length }}</span>
          </div>
        </div>
        <div class="vpc-action-grid">
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vpc-card">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">插件级设置</div>
            <h2 class="vpc-section-title">全局选项</h2>
          </div>
        </div>

        <div class="vpc-switch-grid plugin">
          <div class="vpc-switch-card">
            <v-switch v-model="config.enabled" class="vpc-switch" label="启用插件" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.notify" class="vpc-switch" label="开启通知" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.onlyonce" class="vpc-switch" label="保存后执行一次" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.use_proxy" class="vpc-switch" label="使用代理" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.force_ipv4" class="vpc-switch" label="优先 IPv4" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="vpc-card">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">固定模块</div>
            <h2 class="vpc-section-title">思齐签到 / HNR领取</h2>
          </div>
          <div class="vpc-note">固定模块各保留 1 张卡片，单独控制启用、Cron 和 Cookie。</div>
        </div>

        <div class="vpc-fixed-grid">
          <article
            v-for="card in fixedCards"
            :key="card.id"
            class="vpc-editor fixed"
            :style="toneStyle(card.tone)"
          >
            <div class="vpc-editor-head">
              <div>
                <div class="vpc-kicker">{{ moduleMeta(card.module_key).label }}</div>
                <h3 class="vpc-editor-title">{{ card.title }}</h3>
              </div>
              <span class="vpc-editor-site">{{ card.site_url }}</span>
            </div>

            <div class="vpc-switch-grid compact">
              <div class="vpc-switch-card">
                <v-switch v-model="card.enabled" class="vpc-switch" label="启用" density="compact" hide-details inset />
              </div>
              <div class="vpc-switch-card">
                <v-switch v-model="card.auto_run" class="vpc-switch" label="定时运行" density="compact" hide-details inset />
              </div>
            </div>

            <div class="vpc-field-stack">
              <div class="vpc-field-card">
                <VCronField
                  v-model="card.cron"
                  label="定时运行 Cron"
                  density="comfortable"
                  class="vpc-cron-field"
                />
              </div>

              <div class="vpc-field-card">
                <v-text-field
                  v-model="card.cookie"
                  label="站点 Cookie"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                />
                <div class="vpc-note">{{ fixedCookieNote(card.module_key) }}</div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="vpc-card">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">多站点模块</div>
            <h2 class="vpc-section-title">New API签到</h2>
          </div>
          <div class="vpc-toolbar-actions">
            <v-btn color="info" variant="flat" @click="addNewApiCard">新增站点</v-btn>
          </div>
        </div>

        <div class="vpc-note">所有 New API 站点统一收纳在这个模块内，每张站点卡独立保存启用、Cron、网站和 Cookie。</div>

        <div v-if="!newApiCards.length" class="vpc-empty">当前没有 New API 站点，点击“新增站点”创建。</div>

        <div v-else class="vpc-site-grid">
          <article
            v-for="(card, index) in newApiCards"
            :key="card.id"
            class="vpc-editor"
            :style="toneStyle(card.tone)"
          >
            <div class="vpc-editor-head">
              <div>
                <div class="vpc-kicker">站点 {{ index + 1 }}</div>
                <h3 class="vpc-editor-title">{{ card.site_name || `New API 站点 ${index + 1}` }}</h3>
              </div>
              <div class="vpc-inline-actions">
                <v-btn size="small" variant="text" color="error" @click="removeNewApiCard(card.id)">删除</v-btn>
              </div>
            </div>

            <div class="vpc-switch-grid compact">
              <div class="vpc-switch-card">
                <v-switch v-model="card.enabled" class="vpc-switch" label="启用" density="compact" hide-details inset />
              </div>
              <div class="vpc-switch-card">
                <v-switch v-model="card.auto_run" class="vpc-switch" label="定时运行" density="compact" hide-details inset />
              </div>
            </div>

            <div class="vpc-field-grid newapi">
              <v-text-field v-model="card.site_name" label="网站名称" variant="outlined" density="comfortable" hide-details="auto" />
              <v-text-field v-model="card.site_url" label="网站地址" variant="outlined" density="comfortable" hide-details="auto" />
              <v-text-field v-model="card.uid" label="UID" variant="outlined" density="comfortable" hide-details="auto" />
            </div>

            <div class="vpc-field-stack">
              <div class="vpc-field-card">
                <v-text-field
                  v-model="card.cookie"
                  label="站点 Cookie"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                />
              </div>

              <div class="vpc-field-card">
                <VCronField
                  v-model="card.cron"
                  label="定时运行 Cron"
                  density="comfortable"
                  class="vpc-cron-field"
                />
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const DEFAULT_CARD_CRON = '5 8 * * *'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
const message = reactive({ text: '', type: 'success' })
const moduleItems = ref([])
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: DEFAULT_CARD_CRON,
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
})

let themeObserver = null
let mediaQuery = null

const fixedCards = computed(() => ['siqi_sign', 'hnr_claim'].map((key) => ensureFixedCard(key)))
const newApiCards = computed(() => config.cards.filter((card) => card.module_key === 'newapi_checkin'))
const scheduledCards = computed(() => config.cards.filter((card) => card.enabled && card.auto_run))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function moduleMeta(moduleKey) {
  return moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '🧩',
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '40,181,120' },
    azure: { '--vpc-tone-rgb': '46,134,255' },
    amber: { '--vpc-tone-rgb': '255,170,63' },
    rose: { '--vpc-tone-rgb': '230,92,124' },
    violet: { '--vpc-tone-rgb': '132,108,255' },
    slate: { '--vpc-tone-rgb': '120,132,155' },
  }
  return map[tone] || map.azure
}

function fixedCookieNote(moduleKey) {
  return moduleKey === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后可执行。'
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey)
  return {
    id: moduleKey,
    title: meta.label,
    module_key: moduleKey,
    site_name: meta.default_site_name || '思齐主站',
    site_url: meta.default_site_url || 'https://si-qi.xyz',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: '',
    note: String(current.note || ''),
  }
}

function buildNewApiCard(current = {}) {
  const meta = moduleMeta('newapi_checkin')
  return {
    id: current.id || nextCardId('newapi_checkin'),
    title: current.title || current.site_name || meta.label,
    module_key: 'newapi_checkin',
    site_name: current.site_name || meta.default_site_name || '',
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: String(current.uid || '225'),
    note: String(current.note || ''),
  }
}

function ensureStructure(cards = []) {
  const fixedMap = new Map()
  const newApi = []
  for (const item of cards) {
    if (!item || typeof item !== 'object') continue
    if (item.module_key === 'siqi_sign' || item.module_key === 'hnr_claim') {
      if (!fixedMap.has(item.module_key)) fixedMap.set(item.module_key, buildFixedCard(item.module_key, item))
      continue
    }
    if (item.module_key === 'newapi_checkin') newApi.push(buildNewApiCard(item))
  }

  const normalized = [
    fixedMap.get('siqi_sign') || buildFixedCard('siqi_sign'),
    fixedMap.get('hnr_claim') || buildFixedCard('hnr_claim'),
    ...(newApi.length ? newApi : [buildNewApiCard()]),
  ]

  config.cards.splice(0, config.cards.length, ...normalized)
}

function ensureFixedCard(moduleKey) {
  let card = config.cards.find((item) => item.module_key === moduleKey)
  if (!card) {
    card = buildFixedCard(moduleKey)
    config.cards.push(card)
  }
  return card
}

function addNewApiCard() {
  config.cards.push(buildNewApiCard())
}

function removeNewApiCard(cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId && card.module_key === 'newapi_checkin')
  if (index >= 0) config.cards.splice(index, 1)
  if (!newApiCards.value.length) addNewApiCard()
}

function serializeConfig() {
  const cards = [
    buildFixedCard('siqi_sign', ensureFixedCard('siqi_sign')),
    buildFixedCard('hnr_claim', ensureFixedCard('hnr_claim')),
    ...newApiCards.value.map((card) => buildNewApiCard({
      ...card,
      title: String(card.site_name || card.title || 'New API签到').trim() || 'New API签到',
    })),
  ]

  return {
    ...deepClone(config),
    cards,
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config')
    moduleItems.value = res.module_options || []
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || DEFAULT_CARD_CRON,
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: [],
    })
    ensureStructure(deepClone(res.cards || []))
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/config', serializeConfig())
    flash(res.message || '配置已保存')
    await loadConfig()
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
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
  return document.body
}

function detectTheme() {
  const nodes = [findThemeNode(), document.documentElement, document.body].filter(Boolean)
  const isDark = nodes.some((node) => {
    const theme = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
    const cls = String(node?.className || '').toLowerCase()
    return ['dark', 'purple', 'transparent'].includes(theme) || cls.includes('dark') || cls.includes('theme-dark') || cls.includes('v-theme--dark')
  })
  isDarkTheme.value = isDark || !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  detectTheme()
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    ;[findThemeNode(), document.documentElement, document.body].filter(Boolean).forEach((node) => {
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
.vuepanel-config{--panel:rgba(255,255,255,.86);--panel-strong:rgba(255,255,255,.96);--text:#1f2937;--muted:#6b7280;--border:rgba(124,92,255,.18);--shadow:0 16px 36px rgba(15,23,42,.08);--accent:#7c5cff;--accent-soft:rgba(124,92,255,.12);min-height:100%;padding:8px 0 18px;color:var(--text)}
.vuepanel-config.is-dark-theme{--panel:rgba(17,24,39,.82);--panel-strong:rgba(15,23,42,.94);--text:#f5f7fb;--muted:#a7b0c1;--border:rgba(124,92,255,.2);--shadow:0 20px 42px rgba(0,0,0,.28);--accent:#8b6cff;--accent-soft:rgba(139,108,255,.16)}
.vuepanel-config,.vuepanel-config *{box-sizing:border-box}
.vpc-shell{max-width:1180px;margin:0 auto;padding:0 12px;display:grid;gap:10px}
.vpc-card,.vpc-editor,.vpc-switch-card,.vpc-field-card{border:1px solid var(--border);border-radius:18px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vpc-card{padding:12px}
.vpc-hero,.vpc-chip-row,.vpc-action-grid,.vpc-section-head,.vpc-editor-head,.vpc-inline-actions,.vpc-toolbar-actions{display:flex;gap:8px;flex-wrap:wrap}
.vpc-hero{justify-content:space-between;align-items:flex-start;background:linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vpc-copy{flex:1;min-width:0}
.vpc-badge,.vpc-chip,.vpc-editor-site{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vpc-badge{padding:5px 10px;background:var(--accent-soft);color:var(--accent);font-size:11px;font-weight:700}
.vpc-title,.vpc-section-title,.vpc-editor-title{margin:0;font-weight:900;letter-spacing:-.02em}
.vpc-title{margin-top:8px;font-size:clamp(22px,3.8vw,30px);line-height:1.05}
.vpc-section-title{font-size:17px}
.vpc-editor-title{font-size:17px;line-height:1.12}
.vpc-chip-row{margin-top:10px}
.vpc-chip{padding:6px 10px;border:1px solid var(--border);background:var(--panel-strong);font-size:11px;font-weight:700}
.vpc-action-grid{justify-content:flex-end;min-width:min(100%,420px)}
.vpc-action-grid :deep(.v-btn),.vpc-toolbar-actions :deep(.v-btn){min-height:38px;border-radius:12px;font-weight:800}
.vpc-kicker,.vpc-note,.vpc-editor-site{color:var(--muted)}
.vpc-kicker{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.vpc-note{font-size:11px;line-height:1.65}
.vpc-section-head,.vpc-editor-head{justify-content:space-between;align-items:flex-start}
.vpc-switch-grid,.vpc-field-grid,.vpc-fixed-grid,.vpc-site-grid,.vpc-field-stack{display:grid;gap:10px}
.vpc-switch-grid.plugin{grid-template-columns:repeat(5,minmax(0,1fr))}
.vpc-switch-grid.compact{grid-template-columns:repeat(2,minmax(0,1fr))}
.vpc-switch-card{padding:10px 12px;background:var(--panel-strong)}
.vpc-fixed-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.vpc-site-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.vpc-editor{position:relative;overflow:hidden;padding:12px;display:grid;gap:10px;background:linear-gradient(180deg,rgba(var(--vpc-tone-rgb,46,134,255),.12),transparent 62%),var(--panel-strong)}
.vpc-editor::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:rgba(var(--vpc-tone-rgb,46,134,255),.48)}
.vpc-editor-site{padding:4px 9px;background:rgba(var(--vpc-tone-rgb,46,134,255),.1);font-size:11px;font-weight:700;justify-content:flex-start}
.vpc-field-grid.newapi{grid-template-columns:repeat(3,minmax(0,1fr))}
.vpc-field-card{padding:12px;background:rgba(var(--vpc-tone-rgb,46,134,255),.06)}
.vpc-field-stack{grid-template-columns:1fr}
.vpc-empty{padding:18px 16px;text-align:center;border:1px dashed var(--border);border-radius:16px;background:var(--panel-strong);color:var(--muted)}
:deep(.vuepanel-config .v-field),:deep(.vuepanel-config .v-selection-control){color:var(--text)}
:deep(.vuepanel-config .v-field){background:rgba(255,255,255,.02);border-radius:14px}
:deep(.vuepanel-config .v-field__input),:deep(.vuepanel-config .v-label),:deep(.vuepanel-config .v-select__selection-text),:deep(.vuepanel-config .v-field__outline),:deep(.vuepanel-config .v-field__append-inner){color:var(--text)}
:deep(.vuepanel-config .vpc-switch){width:100%;margin:0}
:deep(.vuepanel-config .vpc-switch .v-selection-control){min-height:28px}
:deep(.vuepanel-config .vpc-switch .v-label){opacity:1;font-weight:600;font-size:12px;line-height:1.35}
:deep(.vuepanel-config .vpc-switch .v-selection-control__wrapper){width:30px;height:18px;margin-right:6px}
:deep(.vuepanel-config .vpc-switch .v-switch__track){min-width:30px;width:30px;height:18px;border-radius:999px}
:deep(.vuepanel-config .vpc-switch .v-switch__thumb){width:12px;height:12px}
:deep(.vuepanel-config .v-field__input){min-height:40px;padding-top:0;padding-bottom:0;font-size:13px}
:deep(.vuepanel-config .v-field__outline){--v-field-border-opacity:1}
:deep(.vuepanel-config .v-selection-control__input > .v-icon),:deep(.vuepanel-config .v-switch__track){color:var(--accent)}
:deep(.vuepanel-config .vpc-cron-field){padding:0;background:transparent}
@media (max-width:1080px){.vpc-switch-grid.plugin,.vpc-fixed-grid,.vpc-site-grid,.vpc-field-grid.newapi{grid-template-columns:repeat(2,minmax(0,1fr))}.vpc-action-grid{justify-content:flex-start;min-width:0}}
@media (max-width:760px){.vpc-shell{padding:0 10px}.vpc-card,.vpc-editor,.vpc-switch-card,.vpc-field-card{border-radius:16px}.vpc-card,.vpc-editor{padding:12px}.vpc-hero,.vpc-section-head,.vpc-editor-head{flex-direction:column;align-items:flex-start}.vpc-switch-grid.plugin,.vpc-switch-grid.compact,.vpc-fixed-grid,.vpc-site-grid,.vpc-field-grid.newapi{grid-template-columns:1fr}}
</style>
