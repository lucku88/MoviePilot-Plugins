<template>
  <div ref="rootEl" class="vuepanel-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vp-shell">
      <section class="vp-card vp-hero">
        <div class="vp-copy">
          <div class="vp-badge">Vue-面板</div>
          <h1 class="vp-title">{{ dashboard.title || '模块状态页' }}</h1>
          <div class="vp-chip-row">
            <span class="vp-chip">计划执行 {{ status.next_run_time || dashboard.next_run_time || '未启用' }}</span>
            <span class="vp-chip">最近执行 {{ status.last_run || '暂无' }}</span>
            <span class="vp-chip">模块 {{ moduleSections.length }} 个</span>
            <span class="vp-chip">卡片 {{ cardCount }} 张</span>
          </div>
        </div>
        <div class="vp-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runAll">执行启用任务</v-btn>
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

      <section
        v-for="section in moduleSections"
        :key="section.module_key"
        class="vp-card vp-module"
        :style="toneStyle(section.tone)"
      >
        <div class="vp-module-head">
          <div>
            <div class="vp-kicker">{{ section.singleton ? '固定模块' : '多站点模块' }}</div>
            <h2 class="vp-section-title">{{ section.module_icon }} {{ section.module_name }}</h2>
          </div>

          <div class="vp-pill-row">
            <span v-for="stat in section.stats || []" :key="`${section.module_key}-${stat.label}`" class="vp-pill">{{ stat.label }} {{ stat.value }}</span>
            <span v-if="section.latest_run" class="vp-pill">最近 {{ section.latest_run }}</span>
          </div>
        </div>

        <div class="vp-module-body" :class="{ 'is-single': section.singleton }">
          <div class="vp-card-grid" :class="{ single: section.singleton, multi: !section.singleton }">
            <article
              v-for="card in section.cards || []"
              :key="card.card_id"
              class="vp-panel"
              :class="`is-${card.level || 'info'}`"
              :style="toneStyle(card.tone)"
            >
              <div class="vp-panel-top">
                <div>
                  <div class="vp-panel-kicker">{{ card.site_name }}</div>
                  <div class="vp-panel-title">{{ card.status_title }}</div>
                </div>
                <span class="vp-level">{{ levelLabel(card.level) }}</span>
              </div>

              <div v-if="!section.singleton" class="vp-panel-site">{{ card.site_url }}</div>
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

              <div class="vp-meta-grid">
                <div class="vp-meta-item">
                  <span class="vp-meta-label">执行</span>
                  <strong>{{ card.last_run || '未执行' }}</strong>
                </div>
                <div class="vp-meta-item">
                  <span class="vp-meta-label">计划</span>
                  <strong>{{ scheduleText(card) }}</strong>
                </div>
              </div>

              <div class="vp-btn-row">
                <v-btn color="primary" variant="flat" :loading="runningCardId === card.card_id" @click="runCard(card)">执行</v-btn>
                <v-btn variant="text" :loading="refreshingCardId === card.card_id" @click="refreshCard(card)">刷新</v-btn>
              </div>
            </article>
          </div>

          <aside class="vp-history-panel">
            <div class="vp-history-head">
              <div>
                <div class="vp-kicker">模块记录</div>
                <div class="vp-history-title">最近执行信息</div>
              </div>
              <span class="vp-note">{{ (section.history || []).length }} 条</span>
            </div>

            <div v-if="!(section.history || []).length" class="vp-empty">当前模块还没有执行记录。</div>

            <div v-else class="vp-history-list">
              <article v-for="item in section.history" :key="`${section.module_key}-${item.time}-${item.title}`" class="vp-history-item">
                <div class="vp-history-top">
                  <strong>{{ historyTitle(section, item) }}</strong>
                  <span>{{ item.time }}</span>
                </div>
                <div v-if="historyMeta(section, item)" class="vp-history-meta">{{ historyMeta(section, item) }}</div>
                <div v-if="item.lines?.length" class="vp-history-lines">{{ item.lines.join(' / ') }}</div>
              </article>
            </div>
          </aside>
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
const moduleSections = computed(() => dashboard.value.module_sections || [])
const cardCount = computed(() => moduleSections.value.reduce((total, section) => total + (section.cards?.length || 0), 0))

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

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function historyTitle(section, item) {
  if (!section?.singleton) return item?.site_name || item?.title || section?.module_name || ''
  return item?.title || section?.module_name || ''
}

function historyMeta(section, item) {
  if (section?.singleton) return item?.site_name || item?.site_url || ''
  const parts = []
  if (item?.title && item.title !== item?.site_name) parts.push(item.title)
  if (item?.site_url) parts.push(item.site_url)
  return parts.join(' / ')
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
  await loadStatus()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.vuepanel-page{--panel:rgba(255,255,255,.86);--panel-strong:rgba(255,255,255,.96);--text:#1f2937;--muted:#6b7280;--border:rgba(120,132,155,.18);--shadow:0 16px 36px rgba(15,23,42,.08);min-height:100%;padding:8px 0 18px;color:var(--text)}
.vuepanel-page.is-dark-theme{--panel:rgba(17,24,39,.82);--panel-strong:rgba(15,23,42,.94);--text:#f5f7fb;--muted:#a7b0c1;--border:rgba(120,132,155,.24);--shadow:0 20px 42px rgba(0,0,0,.28)}
.vuepanel-page,.vuepanel-page *{box-sizing:border-box}
.vp-shell{max-width:1180px;margin:0 auto;padding:0 12px;display:grid;gap:10px}
.vp-card,.vp-panel,.vp-history-panel,.vp-history-item{border:1px solid var(--border);border-radius:18px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vp-card{padding:12px}
.vp-hero,.vp-chip-row,.vp-action-grid,.vp-module-head,.vp-pill-row,.vp-panel-top,.vp-tag-row,.vp-btn-row,.vp-history-head,.vp-history-top{display:flex;gap:8px;flex-wrap:wrap}
.vp-hero{justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(46,134,255,.14),transparent 34%),linear-gradient(135deg,rgba(40,181,120,.1) 0%,transparent 54%),var(--panel)}
.vp-copy{flex:1;min-width:0}
.vp-badge,.vp-chip,.vp-pill,.vp-tag,.vp-level,.vp-panel-site{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vp-badge{padding:5px 10px;background:rgba(46,134,255,.12);color:#2363d1;font-size:11px;font-weight:700}
.vp-title,.vp-section-title,.vp-panel-title,.vp-history-title{margin:0;font-weight:900;letter-spacing:-.02em}
.vp-title{margin-top:8px;font-size:clamp(22px,3.8vw,30px);line-height:1.05}
.vp-section-title{font-size:18px}
.vp-panel-title{font-size:18px;line-height:1.12}
.vp-history-title{font-size:14px}
.vp-chip-row{margin-top:10px}
.vp-chip,.vp-pill{padding:6px 10px;border:1px solid var(--border);background:var(--panel-strong);font-size:11px;font-weight:700}
.vp-action-grid{justify-content:flex-end;min-width:min(100%,420px)}
.vp-action-grid :deep(.v-btn),.vp-btn-row :deep(.v-btn){border-radius:12px;font-weight:800}
.vp-action-grid :deep(.v-btn){min-height:38px}
.vp-note,.vp-stat-label,.vp-kicker,.vp-panel-text,.vp-panel-site,.vp-metric-label,.vp-detail-item,.vp-history-meta,.vp-history-lines,.vp-history-top span,.vp-meta-label{color:var(--muted)}
.vp-kicker{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#2f6ef2}
.vp-stat-grid,.vp-card-grid,.vp-metric-grid,.vp-history-list,.vp-module-body,.vp-meta-grid{display:grid;gap:10px}
.vp-stat-grid{grid-template-columns:repeat(5,minmax(0,1fr))}
.vp-stat{padding:12px;background:linear-gradient(180deg,rgba(255,255,255,.05) 0%,transparent 100%),var(--panel-strong)}
.vp-stat-value{margin-top:6px;font-size:24px;font-weight:900}
.vp-module{position:relative;overflow:hidden;display:grid;gap:12px;background:linear-gradient(180deg,rgba(var(--vp-tone-rgb,46,134,255),.08),transparent 52%),var(--panel)}
.vp-module::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:rgba(var(--vp-tone-rgb,46,134,255),.48)}
.vp-module-head{justify-content:space-between;align-items:flex-start}
.vp-module-body.is-single{grid-template-columns:minmax(0,1.05fr) minmax(300px,.95fr);align-items:start}
.vp-card-grid.single{grid-template-columns:1fr}
.vp-card-grid.multi{grid-template-columns:repeat(2,minmax(0,1fr))}
.vp-panel{position:relative;overflow:hidden;padding:12px;display:grid;gap:8px;background:linear-gradient(180deg,rgba(var(--vp-tone-rgb,46,134,255),.12),transparent 62%),var(--panel-strong)}
.vp-panel::before{content:'';position:absolute;left:0;right:0;top:0;height:4px;background:rgba(var(--vp-tone-rgb,46,134,255),.48)}
.vp-panel-top{justify-content:space-between;align-items:flex-start}
.vp-level{padding:5px 9px;background:rgba(var(--vp-tone-rgb,46,134,255),.12);font-size:11px;font-weight:800}
.vp-panel-site{justify-content:flex-start;padding:4px 8px;background:rgba(var(--vp-tone-rgb,46,134,255),.08);font-size:11px;font-weight:700}
.vp-panel-text{font-size:12px;line-height:1.6}
.vp-metric-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vp-metric{padding:8px 10px;border-radius:14px;border:1px solid rgba(var(--vp-tone-rgb,46,134,255),.16);background:rgba(var(--vp-tone-rgb,46,134,255),.07)}
.vp-metric-value{margin-top:3px;font-size:16px;font-weight:900}
.vp-tag-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,max-content));gap:6px}
.vp-tag{padding:6px 9px;background:rgba(var(--vp-tone-rgb,46,134,255),.11);font-size:11px;font-weight:700;justify-content:flex-start}
.vp-detail-list{display:grid;gap:6px;padding:8px 10px;border-radius:14px;background:rgba(120,132,155,.08)}
.vp-detail-item{font-size:11px;line-height:1.5}
.vp-meta-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.vp-meta-item{padding:8px 10px;border-radius:14px;background:rgba(120,132,155,.08);display:grid;gap:4px}
.vp-meta-label{font-size:11px}
.vp-meta-item strong{font-size:12px;line-height:1.5}
.vp-btn-row{justify-content:flex-end}
.vp-history-panel{padding:12px;background:linear-gradient(180deg,rgba(var(--vp-tone-rgb,46,134,255),.08),transparent 44%),var(--panel-strong)}
.vp-history-head{justify-content:space-between;align-items:flex-start}
.vp-history-list{gap:8px}
.vp-history-item{padding:12px 14px;background:linear-gradient(180deg,rgba(255,255,255,.04),transparent),var(--panel-strong)}
.vp-history-top{justify-content:space-between;align-items:center;flex-wrap:nowrap}
.vp-history-top strong{flex:1;min-width:0;font-size:13px;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vp-history-top span{font-size:12px;white-space:nowrap}
.vp-history-meta{margin-top:6px;font-size:11px;line-height:1.6}
.vp-history-lines{margin-top:6px;font-size:11px;line-height:1.65}
.vp-empty{padding:16px;text-align:center;border:1px dashed var(--border);border-radius:16px;background:var(--panel-strong);color:var(--muted)}
@media (max-width:1080px){.vp-action-grid{justify-content:flex-start;min-width:0}.vp-stat-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.vp-module-body.is-single,.vp-card-grid.multi,.vp-metric-grid{grid-template-columns:1fr}}
@media (max-width:760px){.vp-shell{padding:0 10px}.vp-card,.vp-panel,.vp-history-panel,.vp-history-item{border-radius:16px}.vp-card,.vp-panel,.vp-history-panel{padding:12px}.vp-hero,.vp-module-head,.vp-panel-top,.vp-history-head,.vp-history-top{flex-direction:column;align-items:flex-start}.vp-stat-grid,.vp-meta-grid{grid-template-columns:1fr}.vp-btn-row{justify-content:stretch}.vp-btn-row :deep(.v-btn){flex:1 1 calc(50% - 8px)}}
</style>
