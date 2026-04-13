<template>
  <div ref="rootEl" class="vuepanel-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vp-shell">
      <section class="vp-card vp-hero">
        <div class="vp-hero-copy">
          <div class="vp-badge">Vue-面板</div>
          <h1 class="vp-title">{{ dashboard.title || '网站 / 功能模块面板' }}</h1>
          <p class="vp-subtitle">{{ dashboard.subtitle || '每张配置卡片都拥有独立站点、独立功能和独立样式。' }}</p>
          <div class="vp-chip-row">
            <span class="vp-chip">计划执行 {{ status.next_run_time || dashboard.next_run_time || '未启用' }}</span>
            <span class="vp-chip">最近执行 {{ status.last_run || '暂无' }}</span>
            <span class="vp-chip">隐藏卡片 {{ dashboard.hidden_count || '0' }}</span>
          </div>
        </div>
        <div class="vp-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runAll">执行启用卡片</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshStatus">刷新状态</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vp-stat-grid">
        <article v-for="item in dashboard.overview || []" :key="item.label" class="vp-card vp-stat">
          <div class="vp-stat-label">{{ item.label }}</div>
          <div class="vp-stat-value">{{ item.value }}</div>
        </article>
      </section>

      <section v-if="!groups.length" class="vp-card vp-empty">
        当前没有可展示的状态卡片。去配置页新增卡片，或把已存在卡片设为显示。
      </section>

      <section v-for="group in groups" :key="group.site_key" class="vp-card vp-site">
        <header class="vp-site-head">
          <div>
            <div class="vp-site-kicker">网站分组</div>
            <h2 class="vp-site-title">{{ group.site_name }}</h2>
            <div class="vp-site-url">{{ group.site_url }}</div>
          </div>
          <div class="vp-site-note">{{ group.subtitle }}</div>
        </header>

        <div class="vp-module-stack">
          <article v-for="module in group.modules || []" :key="module.module_key" class="vp-module">
            <div class="vp-module-head">
              <h3>{{ module.module_icon }} {{ module.module_name }}</h3>
              <span>{{ (module.cards || []).length }} 张卡片</span>
            </div>

            <div class="vp-card-grid">
              <article
                v-for="card in module.cards || []"
                :key="card.card_id"
                class="vp-panel"
                :class="`is-${card.level || 'info'}`"
                :style="toneStyle(card.tone)"
              >
                <div class="vp-panel-top">
                  <div>
                    <div class="vp-panel-kicker">{{ card.title }}</div>
                    <div class="vp-panel-title">{{ card.status_title }}</div>
                  </div>
                  <span class="vp-level">{{ levelLabel(card.level) }}</span>
                </div>

                <div class="vp-panel-text">{{ card.status_text }}</div>

                <div v-if="card.metrics?.length" class="vp-metric-grid">
                  <div v-for="metric in card.metrics" :key="`${card.card_id}-${metric.label}`" class="vp-metric">
                    <div class="vp-metric-label">{{ metric.label }}</div>
                    <div class="vp-metric-value">{{ metric.value }}</div>
                  </div>
                </div>

                <div class="vp-tag-row">
                  <span v-for="tag in card.tags || []" :key="`${card.card_id}-${tag}`" class="vp-tag">{{ tag }}</span>
                </div>

                <div v-if="card.detail_lines?.length" class="vp-detail-list">
                  <div v-for="line in card.detail_lines" :key="`${card.card_id}-${line}`" class="vp-detail-item">{{ line }}</div>
                </div>

                <div class="vp-meta-row">
                  <span>上次执行 {{ card.last_run || '未执行' }}</span>
                  <span>最近检查 {{ card.last_checked || '未检查' }}</span>
                </div>

                <div class="vp-btn-row">
                  <v-btn color="primary" variant="flat" :loading="runningCardId === card.card_id" @click="runCard(card)">执行</v-btn>
                  <v-btn variant="text" :loading="refreshingCardId === card.card_id" @click="refreshCard(card)">刷新</v-btn>
                </div>
              </article>
            </div>
          </article>
        </div>
      </section>

      <section class="vp-card">
        <div class="vp-site-head compact">
          <div>
            <div class="vp-site-kicker">执行历史</div>
            <h2 class="vp-site-title">最近记录</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="vp-empty mini">暂无执行记录</div>
        <div v-else class="vp-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="vp-history-item">
            <div class="vp-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div v-if="item.lines?.length" class="vp-history-lines">{{ item.lines.join(' / ') }}</div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const rootEl = ref(null)
const isDarkTheme = ref(false)
const loading = ref(false)
const runningCardId = ref('')
const refreshingCardId = ref('')
const status = reactive({ dashboard: {}, history: [] })
const message = reactive({ text: '', type: 'success' })

let themeObserver = null
let mediaQuery = null

const dashboard = computed(() => status.dashboard || {})
const groups = computed(() => dashboard.value.groups || [])
const historyItems = computed(() => status.history || dashboard.value.history || [])

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vp-tone-rgb': '40,181,120' },
    azure: { '--vp-tone-rgb': '46,134,255' },
    amber: { '--vp-tone-rgb': '255,170,63' },
    rose: { '--vp-tone-rgb': '230,92,124' },
    violet: { '--vp-tone-rgb': '132,108,255' },
    slate: { '--vp-tone-rgb': '120,132,155' },
  }
  return map[tone] || map.azure
}

function levelLabel(level) {
  return ({ success: '正常', warning: '待处理', error: '异常', info: '信息' })[level] || '信息'
}

async function loadStatus(showError = true) {
  try {
    Object.assign(status, await props.api.get('/plugin/VuePanel/status') || {})
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  }
}

async function refreshStatus() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/refresh', {})
    flash(res.message || '已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '刷新失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runAll() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/run', {})
    flash(res.message || '执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runCard(card) {
  runningCardId.value = card.card_id
  try {
    const res = await props.api.post('/plugin/VuePanel/card/run', { card_id: card.card_id })
    flash(res.message || '卡片执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片执行失败', 'error')
  } finally {
    runningCardId.value = ''
  }
}

async function refreshCard(card) {
  refreshingCardId.value = card.card_id
  try {
    const res = await props.api.post('/plugin/VuePanel/card/refresh', { card_id: card.card_id })
    flash(res.message || '卡片状态已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片刷新失败', 'error')
  } finally {
    refreshingCardId.value = ''
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
  if (isDark) {
    isDarkTheme.value = true
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
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
  await loadStatus()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.vuepanel-page{--panel:rgba(255,255,255,.86);--panel-strong:rgba(255,255,255,.96);--text:#1f2937;--muted:#6b7280;--border:rgba(120,132,155,.18);--shadow:0 22px 48px rgba(15,23,42,.08);min-height:100%;padding:10px 0 20px;color:var(--text)}
.vuepanel-page.is-dark-theme{--panel:rgba(17,24,39,.82);--panel-strong:rgba(15,23,42,.94);--text:#f5f7fb;--muted:#a7b0c1;--border:rgba(120,132,155,.24);--shadow:0 24px 52px rgba(0,0,0,.3)}
.vuepanel-page,.vuepanel-page *{box-sizing:border-box}
.vp-shell{max-width:1240px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vp-card,.vp-panel,.vp-history-item{border:1px solid var(--border);border-radius:22px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(18px)}
.vp-card{padding:16px}
.vp-hero,.vp-site-head,.vp-panel-top,.vp-chip-row,.vp-tag-row,.vp-meta-row,.vp-btn-row,.vp-action-grid{display:flex;gap:10px;flex-wrap:wrap}
.vp-hero{justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(46,134,255,.16),transparent 34%),linear-gradient(135deg,rgba(40,181,120,.12) 0%,transparent 54%),var(--panel)}
.vp-badge,.vp-chip,.vp-tag,.vp-level{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vp-badge{padding:6px 12px;background:rgba(46,134,255,.12);color:#2363d1;font-size:12px;font-weight:700}
.vp-title,.vp-site-title{margin:10px 0 0;font-weight:900;letter-spacing:-.02em}
.vp-title{font-size:clamp(24px,4vw,34px);line-height:1.06}
.vp-site-title{font-size:20px}
.vp-subtitle,.vp-site-url,.vp-site-note,.vp-stat-label,.vp-metric-label,.vp-detail-item,.vp-history-lines,.vp-history-top span,.vp-panel-text,.vp-meta-row{color:var(--muted)}
.vp-chip-row{margin-top:12px}
.vp-chip{padding:7px 12px;border:1px solid var(--border);background:var(--panel-strong);font-size:12px;font-weight:700}
.vp-action-grid{justify-content:flex-end;min-width:min(100%,520px)}
.vp-action-grid :deep(.v-btn){min-height:42px;border-radius:14px;font-weight:800}
.vp-stat-grid,.vp-card-grid,.vp-metric-grid,.vp-history-list,.vp-module-stack{display:grid;gap:12px}
.vp-stat-grid{grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}
.vp-stat{padding:14px;background:linear-gradient(180deg,rgba(255,255,255,.05) 0%,transparent 100%),var(--panel-strong)}
.vp-stat-value{margin-top:8px;font-size:30px;font-weight:900}
.vp-empty{padding:36px 20px;text-align:center}
.vp-empty.mini{padding:28px 16px}
.vp-site{display:grid;gap:12px}
.vp-site-head{justify-content:space-between;align-items:flex-start}
.vp-site-head.compact{margin-bottom:4px}
.vp-site-kicker,.vp-panel-kicker{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#2f6ef2}
.vp-module{display:grid;gap:10px}
.vp-module-head{display:flex;align-items:center;justify-content:space-between;gap:10px}
.vp-module-head h3{margin:0;font-size:16px;font-weight:900}
.vp-card-grid{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.vp-panel{position:relative;overflow:hidden;padding:14px;display:grid;gap:10px;background:linear-gradient(180deg,rgba(var(--vp-tone-rgb,46,134,255),.12),transparent 62%),var(--panel-strong)}
.vp-panel::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:rgba(var(--vp-tone-rgb,46,134,255),.5)}
.vp-panel-top{justify-content:space-between;align-items:flex-start}
.vp-panel-title{margin-top:4px;font-size:20px;font-weight:900;line-height:1.15}
.vp-level{padding:6px 10px;background:rgba(var(--vp-tone-rgb,46,134,255),.12);font-size:12px;font-weight:800}
.vp-panel.is-success .vp-level{color:#1c9c60}
.vp-panel.is-warning .vp-level{color:#cb7a00}
.vp-panel.is-error .vp-level{color:#d33d5b}
.vp-metric-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vp-metric{padding:10px 12px;border-radius:16px;border:1px solid rgba(var(--vp-tone-rgb,46,134,255),.18);background:rgba(var(--vp-tone-rgb,46,134,255),.08)}
.vp-metric-value{margin-top:4px;font-size:18px;font-weight:900}
.vp-tag-row,.vp-detail-list,.vp-history-list{display:grid;gap:8px}
.vp-tag-row{grid-template-columns:repeat(auto-fit,minmax(120px,max-content))}
.vp-tag{padding:7px 10px;background:rgba(var(--vp-tone-rgb,46,134,255),.12);font-size:12px;font-weight:700;justify-content:flex-start}
.vp-detail-list{padding:10px 12px;border-radius:16px;background:rgba(120,132,155,.08)}
.vp-meta-row{justify-content:space-between;font-size:12px}
.vp-btn-row{justify-content:flex-end}
.vp-btn-row :deep(.v-btn){border-radius:12px;font-weight:800}
.vp-history-item{padding:14px 16px;background:linear-gradient(180deg,rgba(255,255,255,.04),transparent),var(--panel-strong)}
.vp-history-top{display:flex;justify-content:space-between;gap:10px}
.vp-history-top strong{font-size:14px}
@media (max-width:1024px){.vp-action-grid{justify-content:flex-start;min-width:0}.vp-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:760px){.vp-shell{padding:0 10px}.vp-card,.vp-panel,.vp-history-item{border-radius:18px}.vp-card{padding:14px}.vp-hero,.vp-site-head,.vp-panel-top,.vp-history-top{flex-direction:column;align-items:flex-start}.vp-card-grid,.vp-stat-grid,.vp-metric-grid{grid-template-columns:1fr}.vp-btn-row{justify-content:stretch}.vp-btn-row :deep(.v-btn){flex:1 1 calc(50% - 8px)}}
</style>
