<template>
  <div ref="rootEl" class="vuepanel-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vpc-shell">
      <header class="vpc-card vpc-hero">
        <div class="vpc-copy">
          <div class="vpc-badge">Vue-面板</div>
          <h1 class="vpc-title">卡片配置</h1>
          <div class="vpc-chip-row">
            <span class="vpc-chip">配置卡片 {{ config.cards.length }}</span>
            <span class="vpc-chip">启用插件 {{ config.enabled ? '是' : '否' }}</span>
            <span class="vpc-chip">计划执行 {{ config.cron || '未设置' }}</span>
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
        <h2 class="vpc-section-title">插件级设置</h2>
        <div class="vpc-switch-grid">
          <div class="vpc-switch-card"><v-switch v-model="config.enabled" label="启用插件" density="compact" hide-details inset /></div>
          <div class="vpc-switch-card"><v-switch v-model="config.notify" label="发送通知" density="compact" hide-details inset /></div>
          <div class="vpc-switch-card"><v-switch v-model="config.onlyonce" label="保存后执行一次" density="compact" hide-details inset /></div>
          <div class="vpc-switch-card"><v-switch v-model="config.use_proxy" label="使用代理环境" density="compact" hide-details inset /></div>
          <div class="vpc-switch-card"><v-switch v-model="config.force_ipv4" label="强制 IPv4" density="compact" hide-details inset /></div>
        </div>
        <div class="vpc-field-grid plugin">
          <v-text-field v-model="config.cron" label="Cron" variant="outlined" density="comfortable" hide-details="auto" />
          <v-text-field v-model.number="config.http_timeout" label="超时秒数" type="number" variant="outlined" density="comfortable" hide-details="auto" />
          <v-text-field v-model.number="config.http_retry_times" label="重试次数" type="number" variant="outlined" density="comfortable" hide-details="auto" />
          <v-text-field v-model.number="config.random_delay_max_seconds" label="随机延迟秒数" type="number" variant="outlined" density="comfortable" hide-details="auto" />
        </div>
      </section>

      <section class="vpc-card">
        <div class="vpc-toolbar">
          <div>
            <h2 class="vpc-section-title">配置卡片</h2>
            <div class="vpc-note">一张配置卡片只控制一张状态卡片。展示 / 隐藏 / 样式 / 功能都在这里独立配置。</div>
          </div>
          <div class="vpc-toolbar-actions">
            <v-btn color="success" variant="flat" @click="addCard('siqi_sign')">新增思齐签到</v-btn>
            <v-btn color="warning" variant="flat" @click="addCard('hnr_claim')">新增 HNR 领取</v-btn>
            <v-btn color="info" variant="flat" @click="addCard('newapi_checkin')">新增 New API</v-btn>
          </div>
        </div>
      </section>

      <section v-if="!groupedCards.length" class="vpc-card vpc-empty">
        当前没有配置卡片。点击上面的新增按钮创建第一张卡片。
      </section>

      <section v-for="group in groupedCards" :key="group.site_key" class="vpc-card">
        <div class="vpc-group-head">
          <div>
            <div class="vpc-kicker">网站分组</div>
            <h2 class="vpc-group-title">{{ group.site_name }}</h2>
            <div class="vpc-note">{{ group.site_url }}</div>
          </div>
          <div class="vpc-note">{{ group.cards_count }} 张配置卡片</div>
        </div>

        <div class="vpc-module-stack">
          <div v-for="module in group.modules" :key="module.module_key" class="vpc-module">
            <div class="vpc-module-head">
              <h3>{{ module.module_icon }} {{ module.module_name }}</h3>
              <span>{{ module.cards.length }} 张</span>
            </div>

            <div class="vpc-card-grid">
              <article
                v-for="card in module.cards"
                :key="card.id"
                class="vpc-editor"
                :style="toneStyle(card.tone)"
              >
                <div class="vpc-editor-head">
                  <div>
                    <div class="vpc-kicker">状态卡片绑定</div>
                    <h4>{{ card.title || module.module_name }}</h4>
                  </div>
                  <div class="vpc-inline-actions">
                    <v-btn size="small" variant="text" @click="duplicateCard(card)">复制</v-btn>
                    <v-btn size="small" variant="text" color="error" @click="removeCard(card.id)">删除</v-btn>
                  </div>
                </div>

                <div class="vpc-switch-grid compact">
                  <div class="vpc-switch-card"><v-switch v-model="card.enabled" label="启用" density="compact" hide-details inset /></div>
                  <div class="vpc-switch-card"><v-switch v-model="card.auto_run" label="自动执行" density="compact" hide-details inset /></div>
                  <div class="vpc-switch-card"><v-switch v-model="card.show_status" label="显示状态卡片" density="compact" hide-details inset /></div>
                  <div class="vpc-switch-card"><v-switch v-model="card.notify" label="发送通知" density="compact" hide-details inset /></div>
                </div>

                <div class="vpc-field-grid">
                  <v-text-field v-model="card.title" label="卡片标题" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-select v-model="card.module_key" :items="moduleItems" item-title="label" item-value="key" label="功能模块" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-select v-model="card.tone" :items="toneItems" item-title="label" item-value="key" label="卡片样式" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-text-field v-model="card.site_name" label="网站名称" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-text-field v-model="card.site_url" label="网站地址" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-text-field v-if="card.module_key === 'newapi_checkin'" v-model="card.uid" label="UID" variant="outlined" density="comfortable" hide-details="auto" />
                  <v-textarea v-model="card.cookie" label="Cookie" variant="outlined" density="comfortable" rows="2" auto-grow hide-details="auto" class="vpc-span-2" />
                  <v-textarea v-model="card.note" label="备注 / 状态卡片补充说明" variant="outlined" density="comfortable" rows="2" auto-grow hide-details="auto" class="vpc-span-2" />
                </div>
              </article>
            </div>
          </div>
        </div>
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
const moduleItems = ref([])
const toneItems = ref([])
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: '5 8 * * *',
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
})

let themeObserver = null
let mediaQuery = null

const groupedCards = computed(() => {
  const groups = new Map()
  for (const card of config.cards) {
    const siteKey = `${card.site_name}|${card.site_url}`.toLowerCase()
    if (!groups.has(siteKey)) {
      groups.set(siteKey, {
        site_key: siteKey,
        site_name: card.site_name || '未命名网站',
        site_url: card.site_url || '',
        cards_count: 0,
        modules: new Map(),
      })
    }
    const group = groups.get(siteKey)
    group.cards_count += 1
    const moduleKey = card.module_key || 'siqi_sign'
    const moduleMeta = moduleItems.value.find((item) => item.key === moduleKey) || { key: moduleKey, label: moduleKey, icon: '🧩' }
    if (!group.modules.has(moduleKey)) {
      group.modules.set(moduleKey, {
        module_key: moduleKey,
        module_name: moduleMeta.label,
        module_icon: moduleMeta.icon || '🧩',
        cards: [],
      })
    }
    group.modules.get(moduleKey).cards.push(card)
  }
  return Array.from(groups.values()).map((group) => ({ ...group, modules: Array.from(group.modules.values()) }))
})

function flash(text, type = 'success') {
  message.text = text
  message.type = type
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

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function createCard(moduleKey = 'siqi_sign') {
  const moduleMeta = moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    default_site_name: '新站点',
    default_site_url: '',
  }
  return {
    id: nextCardId(moduleKey),
    title: moduleMeta.label,
    module_key: moduleKey,
    site_name: moduleMeta.default_site_name || '新站点',
    site_url: moduleMeta.default_site_url || '',
    enabled: false,
    auto_run: true,
    show_status: true,
    notify: true,
    tone: toneItems.value[0]?.key || 'azure',
    cookie: '',
    uid: moduleKey === 'newapi_checkin' ? '225' : '',
    note: '',
  }
}

function addCard(moduleKey) {
  config.cards.push(createCard(moduleKey))
}

function duplicateCard(card) {
  const copied = deepClone(card)
  copied.id = nextCardId(card.module_key)
  copied.title = `${card.title || '卡片'} 复制`
  config.cards.push(copied)
}

function removeCard(cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId)
  if (index >= 0) config.cards.splice(index, 1)
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config')
    moduleItems.value = res.module_options || []
    toneItems.value = res.tone_options || []
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || '5 8 * * *',
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: deepClone(res.cards || []),
    })
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const payload = deepClone(config)
    const res = await props.api.post('/plugin/VuePanel/config', payload)
    moduleItems.value = res.config?.module_options || moduleItems.value
    toneItems.value = res.config?.tone_options || toneItems.value
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
.vuepanel-config{--panel:rgba(255,255,255,.86);--panel-strong:rgba(255,255,255,.96);--text:#1f2937;--muted:#6b7280;--border:rgba(120,132,155,.18);--shadow:0 22px 48px rgba(15,23,42,.08);min-height:100%;padding:10px 0 20px;color:var(--text)}
.vuepanel-config.is-dark-theme{--panel:rgba(17,24,39,.82);--panel-strong:rgba(15,23,42,.94);--text:#f5f7fb;--muted:#a7b0c1;--border:rgba(120,132,155,.24);--shadow:0 24px 52px rgba(0,0,0,.3)}
.vuepanel-config,.vuepanel-config *{box-sizing:border-box}
.vpc-shell{max-width:1240px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vpc-card,.vpc-editor{border:1px solid var(--border);border-radius:22px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(18px)}
.vpc-card{padding:16px}
.vpc-hero,.vpc-chip-row,.vpc-action-grid,.vpc-toolbar,.vpc-toolbar-actions,.vpc-group-head,.vpc-module-head,.vpc-editor-head,.vpc-inline-actions{display:flex;gap:10px;flex-wrap:wrap}
.vpc-hero{justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(46,134,255,.16),transparent 34%),linear-gradient(135deg,rgba(40,181,120,.12) 0%,transparent 54%),var(--panel)}
.vpc-badge,.vpc-chip{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vpc-badge{padding:6px 12px;background:rgba(46,134,255,.12);color:#2363d1;font-size:12px;font-weight:700}
.vpc-title,.vpc-group-title{margin:10px 0 0;font-weight:900;letter-spacing:-.02em}
.vpc-title{font-size:clamp(24px,4vw,34px);line-height:1.06}
.vpc-group-title{font-size:20px}
.vpc-chip-row{margin-top:12px}
.vpc-chip{padding:7px 12px;border:1px solid var(--border);background:var(--panel-strong);font-size:12px;font-weight:700}
.vpc-action-grid{justify-content:flex-end;min-width:min(100%,460px)}
.vpc-action-grid :deep(.v-btn),.vpc-toolbar-actions :deep(.v-btn){border-radius:14px;font-weight:800}
.vpc-section-title{margin:0 0 14px;font-size:18px;font-weight:900}
.vpc-note{color:var(--muted);font-size:12px;line-height:1.65}
.vpc-switch-grid,.vpc-field-grid,.vpc-card-grid,.vpc-module-stack{display:grid;gap:12px}
.vpc-switch-grid{grid-template-columns:repeat(5,minmax(0,1fr))}
.vpc-switch-grid.compact{grid-template-columns:repeat(4,minmax(0,1fr))}
.vpc-switch-card,.vpc-editor{background:var(--panel-strong)}
.vpc-switch-card{padding:14px;border:1px solid var(--border);border-radius:18px}
.vpc-field-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vpc-field-grid.plugin{grid-template-columns:repeat(4,minmax(0,1fr))}
.vpc-toolbar,.vpc-group-head,.vpc-module-head,.vpc-editor-head{justify-content:space-between;align-items:flex-start}
.vpc-kicker{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#2f6ef2}
.vpc-card-grid{grid-template-columns:repeat(auto-fit,minmax(360px,1fr))}
.vpc-editor{position:relative;overflow:hidden;padding:14px;display:grid;gap:12px;background:linear-gradient(180deg,rgba(var(--vpc-tone-rgb,46,134,255),.12),transparent 62%),var(--panel-strong)}
.vpc-editor::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:rgba(var(--vpc-tone-rgb,46,134,255),.5)}
.vpc-editor h4,.vpc-module-head h3{margin:0;font-weight:900}
.vpc-inline-actions{justify-content:flex-end}
.vpc-span-2{grid-column:span 2}
.vpc-empty{padding:34px 18px;text-align:center}
:deep(.vuepanel-config .v-field),:deep(.vuepanel-config .v-selection-control){color:var(--text)}
:deep(.vuepanel-config .v-field){background:rgba(255,255,255,.02);border-radius:14px}
:deep(.vuepanel-config .v-field__input),:deep(.vuepanel-config .v-label),:deep(.vuepanel-config .v-select__selection-text),:deep(.vuepanel-config .v-field__outline){color:var(--text)}
:deep(.vuepanel-config .v-selection-control__wrapper){width:30px;height:18px;margin-right:6px}
:deep(.vuepanel-config .v-switch__track){min-width:30px;width:30px;height:18px}
:deep(.vuepanel-config .v-switch__thumb){width:12px;height:12px}
@media (max-width:1180px){.vpc-switch-grid,.vpc-switch-grid.compact,.vpc-field-grid,.vpc-field-grid.plugin{grid-template-columns:repeat(2,minmax(0,1fr))}.vpc-action-grid{justify-content:flex-start;min-width:0}}
@media (max-width:760px){.vpc-shell{padding:0 10px}.vpc-card,.vpc-editor{border-radius:18px}.vpc-card{padding:14px}.vpc-hero,.vpc-toolbar,.vpc-group-head,.vpc-module-head,.vpc-editor-head{flex-direction:column;align-items:flex-start}.vpc-field-grid,.vpc-field-grid.plugin,.vpc-switch-grid,.vpc-switch-grid.compact,.vpc-card-grid{grid-template-columns:1fr}.vpc-span-2{grid-column:auto}}
</style>
