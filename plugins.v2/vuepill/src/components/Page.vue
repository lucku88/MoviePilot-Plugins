<template>
  <div ref="rootEl" class="vp-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vp-shell">
      <section class="vp-card vp-hero">
        <div class="vp-copy">
          <div class="vp-badge">Vue-魔丸</div>
          <h1 class="vp-title">{{ pill.title || '搬砖捡破烂炼魔丸' }}</h1>

          <div class="vp-chip-row">
            <span class="vp-chip">最近执行 {{ status.last_run || '暂无' }}</span>
            <span class="vp-chip">下次运行 {{ pill.next_run_time || '等待刷新' }}</span>
            <span class="vp-chip">计划触发 {{ pill.next_trigger_time || '等待刷新' }}</span>
            <span class="vp-chip">{{ pill.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>

        <div class="vp-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vp-stats">
        <article v-for="item in overview" :key="item.label" class="vp-card vp-stat">
          <div class="vp-kicker">{{ item.label }}</div>
          <div class="vp-value">{{ item.value }}</div>
        </article>
        <article class="vp-card vp-stat vp-stat-focus">
          <div class="vp-kicker">库存快照</div>
          <div class="vp-value">{{ inventoryTotal }}</div>
          <div class="vp-stat-note">物品 {{ inventoryKinds }} 类</div>
        </article>
      </section>

      <section v-if="showSummary" class="vp-card vp-summary">
        <div class="vp-head compact">
          <div>
            <div class="vp-kicker">本次摘要</div>
            <h2 class="vp-section-title">任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="vp-list">
          <div v-for="line in summaryLines" :key="line" class="vp-list-item">{{ line }}</div>
        </div>
      </section>

      <section class="vp-grid-2">
        <article class="vp-card vp-panel brick">
          <div class="vp-head vp-head-action">
            <div>
              <div class="vp-kicker">搬砖工坊</div>
              <h2 class="vp-section-title">搬砖状态</h2>
            </div>
            <div class="vp-card-action-slot">
              <v-btn
                v-if="brick.ready"
                color="deep-orange"
                variant="flat"
                size="small"
                class="vp-card-action-btn"
                :loading="loading"
                @click="moveBricks"
              >
                立即搬砖
              </v-btn>
              <span v-else class="vp-state">冷却中</span>
            </div>
          </div>
          <div class="vp-title-strong">{{ brickHeadline }}</div>
          <div class="vp-countdown">{{ brickCountdownText }}</div>
          <div class="vp-facts">
            <div class="vp-fact">
              <span class="vp-kicker">今日进度</span>
              <strong>{{ brick.daily_bricks || 0 }}/{{ brick.daily_limit || 50 }}</strong>
            </div>
            <div class="vp-fact">
              <span class="vp-kicker">下次模式</span>
              <strong>{{ pill.next_run_action_label || '整轮执行' }}</strong>
            </div>
          </div>
        </article>

        <article class="vp-card vp-panel beach">
          <div class="vp-head vp-head-action">
            <div>
              <div class="vp-kicker">沙滩捡破烂</div>
              <h2 class="vp-section-title">沙滩状态</h2>
            </div>
            <div class="vp-card-action-slot">
              <v-btn
                v-if="beach.ready"
                color="teal"
                variant="flat"
                size="small"
                class="vp-card-action-btn"
                :loading="loading"
                @click="cleanBeach"
              >
                清理沙滩
              </v-btn>
              <span v-else class="vp-state">冷却中</span>
            </div>
          </div>
          <div class="vp-title-strong">{{ beachHeadline }}</div>
          <div class="vp-countdown">{{ beachCountdownText }}</div>
          <div class="vp-facts">
            <div class="vp-fact">
              <span class="vp-kicker">当前结果</span>
              <strong>{{ beach.status_text || (beach.ready ? '已就绪' : '等待冷却') }}</strong>
            </div>
            <div class="vp-fact">
              <span class="vp-kicker">自动后续</span>
              <strong>{{ autoFollowText }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="vp-card vp-panel stash">
        <div class="vp-head">
          <div>
            <h2 class="vp-section-title">当前库存</h2>
          </div>
          <div class="vp-note">材料、工具和魔丸会在这里汇总显示。</div>
        </div>

        <div class="vp-tool-grid">
          <article class="vp-tool craft">
            <div class="vp-tool-title">⚗️ 一键炼造魔丸</div>
            <div class="vp-note">
              最大可炼造 {{ magicPillMax }} 颗
              <span v-if="magicPillRecipe?.materials?.length"> · 材料 {{ magicPillRecipe.materials.join(' / ') }}</span>
            </div>
            <div class="vp-inline">
              <label class="vp-field">
                <span>数量</span>
                <input v-model="pillCraftQuantity" class="vp-input" type="number" min="1" :max="Math.max(magicPillMax, 1)" />
              </label>
              <v-btn variant="text" :disabled="!magicPillMax" @click="setPillCraftMax">最大</v-btn>
              <v-btn color="deep-purple-accent-3" variant="flat" :loading="loading" :disabled="loading || !magicPillMax" @click="craftMagicPill">一键炼造</v-btn>
            </div>
          </article>

          <article class="vp-tool exchange">
            <div class="vp-tool-title">💰 兑换魔力</div>
            <div class="vp-note">价格 {{ exchangePriceText }} · 可兑换 {{ exchange.max_count || 0 }} 颗</div>
            <div class="vp-inline">
              <label class="vp-field">
                <span>数量</span>
                <input v-model="exchangeQuantity" class="vp-input" type="number" min="1" :max="Math.max(Number(exchange.max_count || 0), 1)" />
              </label>
              <v-btn color="amber-darken-2" variant="flat" :loading="loading" :disabled="loading || !exchange.action_ready" @click="exchangePoints">兑换魔力</v-btn>
            </div>
          </article>
        </div>

        <div v-if="pill.inventory?.empty" class="vp-empty">{{ pill.inventory?.empty_text }}</div>
        <div v-else class="vp-items">
          <article v-for="item in inventoryItems" :key="item.name" class="vp-item" :class="{ active: item.has_items }" :style="itemToneStyle(item)">
            <div class="vp-item-icon-wrap">
              <div class="vp-item-icon">{{ item.icon }}</div>
            </div>
            <div class="vp-item-body">
              <div class="vp-item-name">{{ item.name }}</div>
              <div class="vp-item-count">{{ item.count }}</div>
            </div>
          </article>
        </div>
      </section>

      <section class="vp-card vp-panel history">
        <div class="vp-head">
          <div>
            <h2 class="vp-section-title">执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="vp-empty">暂无执行记录</div>
        <div v-else class="vp-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="vp-history">
            <div class="vp-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div v-if="item.lines?.length" class="vp-history-lines">{{ (item.lines || []).join(' / ') }}</div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const loading = ref(false)
const rootEl = ref(null)
const status = reactive({ pill_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const isDarkTheme = ref(false)
const dismissedSummaryKey = ref('')
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)
const lastBrickCooldownRefreshTs = ref(0)
const lastBeachCooldownRefreshTs = ref(0)
const pluginBase = '/plugin/VuePill'

let timer = null
let themeObserver = null
let mediaQuery = null
let pendingRefreshTimer = null

const pill = computed(() => status.pill_status || {})
const overview = computed(() => pill.value.overview || [])
const exchange = computed(() => pill.value.exchange || {})
const brick = computed(() => pill.value.brick || {})
const beach = computed(() => pill.value.beach || {})
const inventoryItems = computed(() => pill.value.inventory?.items || [])
const crafting = computed(() => pill.value.crafting || {})
const magicPillMax = computed(() => Number(crafting.value.magic_pill_max || 0))
const magicPillRecipe = computed(() => pill.value.crafting?.magic_pill_recipe || {})
const historyItems = computed(() => status.history || pill.value.history || [])
const summaryLines = computed(() => (pill.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)
const nextRunTs = computed(() => Number(pill.value.next_run_ts || 0) || parseDateTime(pill.value.next_run_time))
const nextTriggerTs = computed(() => Number(pill.value.next_trigger_ts || 0) || parseDateTime(pill.value.next_trigger_time))
const brickResetTs = computed(() => Number(brick.value.next_reset_ts || 0) || parseDateTime(brick.value.next_reset_time))
const beachReadyTs = computed(() => Number(beach.value.next_ready_ts || 0) || parseDateTime(beach.value.next_ready_time))
const exchangePriceText = computed(() => (exchange.value.pill_price ? `${exchange.value.pill_price} 魔力/颗` : '待识别'))
const exchangeQuantity = ref('1')
const pillCraftQuantity = ref('1')
const inventoryKinds = computed(() => inventoryItems.value.length)
const inventoryTotal = computed(() => inventoryItems.value.reduce((sum, item) => sum + Number(item.count || 0), 0))

const autoFollowText = computed(() => {
  const actions = []
  if (magicPillMax.value > 0) actions.push('炼造')
  if (exchange.value.action_ready) actions.push('兑换')
  return actions.length ? actions.join(' / ') : '无自动后续'
})
const brickHeadline = computed(() => brick.value.ready ? '可立即搬砖' : (Number(brick.value.daily_bricks || 0) >= Number(brick.value.daily_limit || 50) ? '今日已达上限' : '等待搬砖'))
const beachHeadline = computed(() => (beach.value.ready ? '可立即清理' : '沙滩冷却中'))
const brickCountdownText = computed(() => {
  if (brick.value.ready) return '现在可以开始搬砖'
  const remain = brickResetTs.value - nowTs.value
  return brickResetTs.value && remain > 0 ? `明日可搬：${formatCountdown(remain)}` : (brick.value.status_text || '等待刷新')
})
const beachCountdownText = computed(() => {
  if (beach.value.ready) return '现在可以进入沙滩'
  const remain = beachReadyTs.value - nowTs.value
  return beachReadyTs.value && remain > 0 ? `下次清理：${formatCountdown(remain)}` : (beach.value.status_text || '等待刷新')
})

watch(summaryKey, (nextKey, prevKey) => { if (nextKey && nextKey !== prevKey) dismissedSummaryKey.value = '' })
watch(() => exchange.value.max_count, (maxCount) => { const limit = Math.max(normalizePositiveInt(maxCount, 1), 1); exchangeQuantity.value = String(Math.min(normalizePositiveInt(exchangeQuantity.value, 1), limit)) }, { immediate: true })
watch(() => magicPillMax.value, (maxCount) => { const limit = Math.max(normalizePositiveInt(maxCount, 1), 1); pillCraftQuantity.value = String(Math.min(normalizePositiveInt(pillCraftQuantity.value, 1), limit)) }, { immediate: true })
watch(summaryKey, loadDismissedSummaryKey)

function normalizePositiveInt(value, fallback = 1) {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const parsed = Date.parse(value.replace(/-/g, '/'))
  return Number.isNaN(parsed) ? 0 : Math.floor(parsed / 1000)
}

function formatCountdown(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds || 0))
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const seconds = safeSeconds % 60
  return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function toneRgbByName(name) {
  const text = String(name || '')
  if (text.includes('砖')) return '255,119,64'
  if (text.includes('木')) return '171,121,79'
  if (text.includes('塑料') || text.includes('胶') || text.includes('瓶')) return '78,151,255'
  if (text.includes('螺丝') || text.includes('旧电池') || text.includes('能量')) return '82,183,110'
  if (text.includes('铜')) return '226,165,98'
  if (text.includes('工具')) return '104,122,255'
  if (text.includes('魔丸胚胎')) return '255,132,179'
  if (text.includes('魔丸')) return '139,108,255'
  if (text.includes('蟑螂')) return '74,194,173'
  return '124,92,255'
}

function itemToneStyle(item) {
  return { '--vp-tone-rgb': toneRgbByName(item?.name) }
}

function closePlugin() {
  if (showSummary.value) dismissSummary()
  emit('close')
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    key ? window.sessionStorage.setItem('vuepill-dismissed-summary', key) : window.sessionStorage.removeItem('vuepill-dismissed-summary')
  }
}

function loadDismissedSummaryKey() {
  dismissedSummaryKey.value = typeof window !== 'undefined' && window.sessionStorage ? (window.sessionStorage.getItem('vuepill-dismissed-summary') || '') : ''
}

async function loadStatus() {
  applyStatusPayload(await props.api.get(`${pluginBase}/status`))
}

function applyStatusPayload(payload = {}) {
  const nextStatus = payload?.status?.pill_status || payload?.pill_status || {}
  if (Object.keys(nextStatus).length) status.pill_status = nextStatus
  if (Array.isArray(payload?.history)) status.history = payload.history
  else if (Array.isArray(payload?.status?.history)) status.history = payload.status.history
  const runTs = Number(status.pill_status?.next_run_ts || 0) || parseDateTime(status.pill_status?.next_run_time)
  const triggerTs = Number(status.pill_status?.next_trigger_ts || 0) || parseDateTime(status.pill_status?.next_trigger_time)
  if (runTs && nowTs.value >= runTs) lastRunAutoRefreshTs.value = runTs
  if (triggerTs && nowTs.value >= triggerTs) lastTriggerAutoRefreshTs.value = triggerTs
  if (brickResetTs.value && nowTs.value >= brickResetTs.value) lastBrickCooldownRefreshTs.value = brickResetTs.value
  if (beachReadyTs.value && nowTs.value >= beachReadyTs.value) lastBeachCooldownRefreshTs.value = beachReadyTs.value
}

async function silentRefreshStatus() {
  try {
    await loadStatus()
  } catch (error) {
    console.warn('[VuePill] silent refresh failed', error)
  }
}

function scheduleFollowUpRefresh(delay = 1200) {
  if (pendingRefreshTimer) window.clearTimeout(pendingRefreshTimer)
  pendingRefreshTimer = window.setTimeout(() => {
    pendingRefreshTimer = null
    silentRefreshStatus()
  }, delay)
}

async function doAction(action, { silent = false } = {}) {
  loading.value = true
  try {
    const result = await action()
    applyStatusPayload(result)
    await silentRefreshStatus()
    scheduleFollowUpRefresh()
    if (!silent) flash(result?.message || '操作完成')
  } catch (error) {
    if (!silent) flash(error?.message || '操作失败', 'error')
  } finally {
    loading.value = false
  }
}

async function refreshData() { await doAction(() => props.api.post(`${pluginBase}/refresh`)) }
async function runNow() { await doAction(() => props.api.post(`${pluginBase}/run`)) }
async function syncCookie() { await doAction(() => props.api.get(`${pluginBase}/cookie`)) }
async function moveBricks() { await doAction(() => props.api.post(`${pluginBase}/move-bricks`)) }
async function cleanBeach() { await doAction(() => props.api.post(`${pluginBase}/clean-beach`)) }

async function exchangePoints() {
  if (!exchange.value.action_ready) return flash('当前没有可兑换的魔丸', 'warning')
  const limit = Math.max(normalizePositiveInt(exchange.value.max_count, 1), 1)
  const quantity = Math.min(normalizePositiveInt(exchangeQuantity.value, 1), limit)
  exchangeQuantity.value = String(quantity)
  await doAction(() => props.api.post(`${pluginBase}/exchange-points`, { quantity }))
}

function setPillCraftMax() {
  if (magicPillMax.value) pillCraftQuantity.value = String(magicPillMax.value)
}

async function craftMagicPill() {
  if (!magicPillMax.value) return flash('当前材料不足，无法炼造魔丸', 'warning')
  const quantity = Math.min(normalizePositiveInt(pillCraftQuantity.value, 1), magicPillMax.value)
  pillCraftQuantity.value = String(quantity)
  await doAction(() => props.api.post(`${pluginBase}/craft-max-pill`, { quantity }))
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    const classValue = String(current.className || '').toLowerCase()
    if (classValue.includes('theme') || classValue.includes('v-theme--') || classValue.includes('dark') || classValue.includes('light')) return current
    current = current.parentElement
  }
  const bodyClass = String(document.body?.className || '').toLowerCase()
  if (document.body?.getAttribute('data-theme') || bodyClass.includes('theme') || bodyClass.includes('v-theme--') || bodyClass.includes('dark') || bodyClass.includes('light')) return document.body
  const rootClass = String(document.documentElement?.className || '').toLowerCase()
  if (document.documentElement?.getAttribute('data-theme') || rootClass.includes('theme') || rootClass.includes('v-theme--') || rootClass.includes('dark') || rootClass.includes('light')) return document.documentElement
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  const classValue = String(node?.className || '').toLowerCase()
  return ['dark', 'purple', 'transparent'].includes(themeValue) || classValue.includes('dark') || classValue.includes('theme-dark') || classValue.includes('v-theme--dark')
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  const classValue = String(node?.className || '').toLowerCase()
  return themeValue === 'light' || classValue.includes('light') || classValue.includes('theme-light') || classValue.includes('v-theme--light')
}

function detectTheme() {
  const nodes = getThemeNodes()
  if (nodes.some(nodeHasDarkHint)) return (isDarkTheme.value = true)
  if (nodes.some(nodeHasLightHint)) return (isDarkTheme.value = false)
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

function tick() {
  nowTs.value = Math.floor(Date.now() / 1000)
  if (nextRunTs.value && nowTs.value >= nextRunTs.value && lastRunAutoRefreshTs.value !== nextRunTs.value) {
    lastRunAutoRefreshTs.value = nextRunTs.value
    doAction(() => props.api.post(`${pluginBase}/refresh`), { silent: true })
  }
  if (nextTriggerTs.value && nowTs.value >= nextTriggerTs.value && lastTriggerAutoRefreshTs.value !== nextTriggerTs.value) {
    lastTriggerAutoRefreshTs.value = nextTriggerTs.value
    doAction(() => props.api.post(`${pluginBase}/refresh`), { silent: true })
  }
  if (brickResetTs.value && nowTs.value >= brickResetTs.value && lastBrickCooldownRefreshTs.value !== brickResetTs.value) {
    lastBrickCooldownRefreshTs.value = brickResetTs.value
    silentRefreshStatus()
  }
  if (beachReadyTs.value && nowTs.value >= beachReadyTs.value && lastBeachCooldownRefreshTs.value !== beachReadyTs.value) {
    lastBeachCooldownRefreshTs.value = beachReadyTs.value
    silentRefreshStatus()
  }
}

onMounted(async () => {
  bindThemeObserver()
  loadDismissedSummaryKey()
  await loadStatus()
  timer = window.setInterval(tick, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
  if (pendingRefreshTimer) window.clearTimeout(pendingRefreshTimer)
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.vp-page{--panel:rgba(255,255,255,.84);--panel-strong:rgba(255,255,255,.94);--panel-soft:rgba(255,255,255,.72);--text:#24273a;--muted:#757b92;--border:rgba(125,132,170,.2);--shadow:0 20px 48px rgba(17,24,39,.08);--accent:#7c5cff;--accent-soft:rgba(124,92,255,.1);min-height:100%;padding:10px 0 20px;background:transparent;color:var(--text)}
.vp-page.is-dark-theme{--panel:rgba(24,26,37,.82);--panel-strong:rgba(19,21,30,.94);--panel-soft:rgba(34,36,50,.72);--text:#f4f6ff;--muted:#a0a8c5;--border:rgba(124,92,255,.18);--shadow:0 24px 54px rgba(0,0,0,.32);--accent:#8b6cff;--accent-soft:rgba(139,108,255,.16)}
.vp-page,.vp-page *{box-sizing:border-box}
.vp-shell{max-width:1180px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vp-card,.vp-list-item,.vp-history,.vp-item,.vp-tool{border:1px solid var(--border);border-radius:20px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vp-card{padding:16px}
.vp-hero,.vp-head,.vp-chip-row{display:flex;gap:10px;flex-wrap:wrap}
.vp-hero{justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(124,92,255,.18) 0%,transparent 34%),linear-gradient(135deg,var(--accent-soft) 0%,transparent 52%),var(--panel)}
.vp-copy{flex:1;min-width:0}
.vp-badge,.vp-chip,.vp-state{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vp-badge{width:fit-content;padding:6px 12px;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700}
.vp-title{margin:10px 0 6px;font-size:clamp(24px,3.7vw,34px);line-height:1.06;font-weight:900;letter-spacing:-.02em}
.vp-subtitle,.vp-note,.vp-history-top span,.vp-kicker,.vp-tool .vp-note,.vp-history-lines,.vp-stat-note{color:var(--muted)}
.vp-subtitle{margin:0;font-size:14px;line-height:1.7;max-width:720px}
.vp-chip-row{margin-top:12px}
.vp-chip{padding:7px 12px;border:1px solid var(--border);background:var(--panel-strong);color:var(--text);font-size:12px;font-weight:600;justify-content:flex-start}
.vp-action-grid{display:flex;align-items:center;justify-content:flex-end;gap:10px;flex-wrap:nowrap;min-width:min(100%,560px)}
.vp-action-grid :deep(.v-btn){min-height:42px;border-radius:14px;font-weight:800}
.vp-action-grid :deep(.v-btn--variant-flat){min-width:132px}
.vp-action-grid :deep(.v-btn--variant-text){min-width:auto;padding-inline:6px}
.vp-stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.vp-stat{padding:14px 16px;background:linear-gradient(180deg,rgba(255,255,255,.06) 0%,transparent 100%),var(--panel-strong);position:relative;overflow:hidden}
.vp-stat::before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:rgba(124,92,255,.22)}
.vp-stat:nth-child(1)::before{background:rgba(124,92,255,.42)}
.vp-stat:nth-child(2)::before{background:rgba(255,160,67,.42)}
.vp-stat:nth-child(3)::before{background:rgba(76,132,255,.42)}
.vp-stat:nth-child(4)::before{background:rgba(34,197,171,.42)}
.vp-stat-focus{background:radial-gradient(circle at top left,rgba(124,92,255,.18) 0%,transparent 42%),var(--panel-strong)}
.vp-value{margin-top:10px;font-size:clamp(22px,3vw,30px);font-weight:900;line-height:1}
.vp-stat-note{margin-top:8px;font-size:12px;font-weight:600}
.vp-head{justify-content:space-between;align-items:flex-start;margin-bottom:14px}
.vp-head-action{align-items:center}
.vp-head.compact{align-items:center}
.vp-section-title{margin:0;font-size:20px;font-weight:900;line-height:1.15}
.vp-summary{background:linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vp-list{display:grid;gap:12px}
.vp-list-item,.vp-history{padding:14px 16px;background:var(--panel-strong)}
.vp-grid-2{display:grid;gap:14px;grid-template-columns:repeat(2,minmax(0,1fr))}
.vp-panel.brick{background:linear-gradient(135deg,rgba(255,160,67,.14) 0%,transparent 42%),var(--panel)}
.vp-panel.beach{background:linear-gradient(135deg,rgba(34,197,171,.12) 0%,transparent 42%),var(--panel)}
.vp-panel.stash{background:radial-gradient(circle at top left,rgba(124,92,255,.12) 0%,transparent 36%),linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vp-panel.history{background:linear-gradient(135deg,rgba(99,102,241,.12) 0%,transparent 44%),var(--panel)}
.vp-state{min-height:30px;padding:0 12px;font-size:12px;font-weight:800;color:#88612b;background:rgba(255,179,76,.16)}
.vp-state.ready{color:#1d8c57;background:rgba(47,193,120,.16)}
.vp-title-strong{font-size:clamp(24px,3vw,32px);line-height:1.04;font-weight:900}
.vp-countdown{margin-top:8px;font-size:clamp(16px,1.9vw,20px);font-weight:900;color:var(--accent)}
.vp-facts{display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr));margin-top:14px}
.vp-fact{padding:12px;border-radius:16px;border:1px solid var(--border);background:var(--panel-strong);display:grid;gap:6px}
.vp-fact strong{font-size:15px}
.vp-card-action-slot{display:flex;align-items:center;justify-content:flex-end;min-width:118px}
.vp-card-action-btn{min-height:34px;border-radius:999px;font-weight:800;min-width:118px}
.vp-tool-grid{display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr));margin-bottom:14px}
.vp-tool{padding:14px;display:grid;gap:12px;background:var(--panel-strong)}
.vp-tool.craft{background:linear-gradient(135deg,rgba(124,92,255,.14) 0%,transparent 48%),var(--panel-strong)}
.vp-tool.exchange{background:linear-gradient(135deg,rgba(255,171,64,.14) 0%,transparent 48%),var(--panel-strong)}
.vp-tool-title{font-size:16px;font-weight:900}
.vp-inline{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px}
.vp-field{min-width:120px;display:grid;gap:8px;font-size:13px;color:var(--muted)}
.vp-input{width:100%;height:40px;padding:10px 12px;border:1px solid var(--border);border-radius:14px;background:var(--panel);color:var(--text);outline:none}
.vp-input:focus{border-color:rgba(124,92,255,.48);box-shadow:0 0 0 3px rgba(124,92,255,.12)}
.vp-items{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(118px,1fr))}
.vp-item{position:relative;overflow:hidden;padding:10px 10px 9px;display:grid;grid-template-columns:48px minmax(0,1fr);gap:10px;align-items:center;background:linear-gradient(180deg,rgba(var(--vp-tone-rgb,124,92,255),.18) 0%,transparent 70%),var(--panel-strong);border-color:rgba(var(--vp-tone-rgb,124,92,255),.28)}
.vp-item::after{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:rgba(var(--vp-tone-rgb,124,92,255),.4)}
.vp-item.active{box-shadow:0 14px 28px rgba(17,24,39,.08)}
.vp-item-icon-wrap{display:grid;place-items:center}
.vp-item-icon{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;font-size:22px;background:rgba(var(--vp-tone-rgb,124,92,255),.2);box-shadow:inset 0 0 0 1px rgba(var(--vp-tone-rgb,124,92,255),.22)}
.vp-item-body{min-width:0;display:grid;gap:4px}
.vp-item-name{font-size:12px;font-weight:800;line-height:1.3;word-break:break-all}
.vp-item-count{font-size:17px;font-weight:900;line-height:1}
.vp-history{position:relative;overflow:hidden;padding:15px 16px 14px 18px;background:linear-gradient(180deg,rgba(255,255,255,.03) 0%,transparent 100%),var(--panel-strong)}
.vp-history::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,rgba(124,92,255,.54) 0%,rgba(99,102,241,.18) 100%)}
.vp-history-top{display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:nowrap;margin-bottom:0}
.vp-history-top strong{flex:1;min-width:0;font-size:14px;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vp-history-top span{font-size:12px;white-space:nowrap}
.vp-history-lines{margin-top:8px;font-size:12px;line-height:1.7}
.vp-empty{padding:34px 18px;text-align:center;color:var(--muted);border-radius:18px;border:1px dashed var(--border);background:var(--panel-strong)}
@media (max-width:1120px){.vp-stats{grid-template-columns:repeat(3,minmax(0,1fr))}.vp-grid-2,.vp-tool-grid{grid-template-columns:1fr}.vp-action-grid{flex-wrap:wrap;justify-content:flex-start;min-width:0}}
@media (max-width:920px){.vp-head{flex-direction:column;align-items:flex-start}.vp-head-action{align-items:flex-start}.vp-card-action-slot{justify-content:flex-start;min-width:0}.vp-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.vp-action-grid{justify-content:flex-start}}
@media (max-width:760px){.vp-shell{padding:0 10px}.vp-card,.vp-list-item,.vp-history,.vp-item,.vp-tool{border-radius:18px}.vp-card{padding:14px}.vp-facts,.vp-items,.vp-stats{grid-template-columns:1fr}.vp-action-grid{gap:10px}.vp-action-grid :deep(.v-btn--variant-flat){min-width:0;flex:1 1 calc(50% - 10px)}.vp-history-top{flex-direction:column;align-items:flex-start;gap:6px}}
</style>
