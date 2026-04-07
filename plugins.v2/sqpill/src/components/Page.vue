<template>
  <div ref="rootEl" class="pill-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pill-shell">
      <section class="pill-hero">
        <div class="pill-copy">
          <div class="pill-badge">SQ魔丸</div>
          <h1 class="pill-title">{{ pill.title || '搬砖捡破烂炼魔丸' }}</h1>
          <p class="pill-subtitle">
            {{ pill.subtitle || '自动搬砖、自动清沙滩，支持清沙滩后自动炼造和自动兑换。' }}
          </p>
          <div class="pill-hero-meta">
            <span>最近执行 {{ status.last_run || '暂无' }}</span>
            <span>下次运行 {{ pill.next_run_time || '等待刷新' }}</span>
            <span>Cookie {{ pill.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>
        <div class="pill-actions">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="deep-orange" variant="flat" :loading="loading" @click="moveBricks">立即搬砖</v-btn>
          <v-btn color="teal" variant="flat" :loading="loading" @click="cleanBeach">清理沙滩</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="pill-stat-grid">
        <article v-for="item in overview" :key="item.label" class="pill-stat-card">
          <div class="pill-stat-label">{{ item.label }}</div>
          <div class="pill-stat-value">{{ item.value }}</div>
        </article>
      </section>

      <section v-if="showSummary" class="pill-panel">
        <div class="pill-panel-head">
          <div>
            <div class="pill-panel-kicker">本次摘要</div>
            <h2>任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="pill-summary-list">
          <div v-for="line in summaryLines" :key="line" class="pill-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="pill-action-grid">
        <article class="pill-panel pill-status-card">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">搬砖工坊</div>
              <h2>搬砖状态</h2>
            </div>
            <span class="pill-status-chip" :class="{ ready: brick.ready }">
              {{ brick.ready ? '可执行' : '冷却中' }}
            </span>
          </div>
          <div class="pill-status-body">
            <div class="pill-status-title">{{ brickHeadline }}</div>
            <div class="pill-status-countdown">{{ brickCountdownText }}</div>
            <div class="pill-status-desc">{{ brick.status_text || '等待刷新' }}</div>
            <div class="pill-inline-meta">
              <span>口袋 {{ brick.bag_count || 0 }} 块</span>
              <span>今日 {{ brick.daily_bricks || 0 }}/{{ brick.daily_limit || 50 }}</span>
            </div>
          </div>
        </article>

        <article class="pill-panel pill-status-card">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">沙滩捡破烂</div>
              <h2>冷却动态时间</h2>
            </div>
            <span class="pill-status-chip" :class="{ ready: beach.ready }">
              {{ beach.ready ? '可清理' : '冷却中' }}
            </span>
          </div>
          <div class="pill-status-body">
            <div class="pill-status-title">{{ beachHeadline }}</div>
            <div class="pill-status-countdown">{{ beachCountdownText }}</div>
            <div class="pill-status-desc">{{ beach.status_text || '等待刷新' }}</div>
            <div class="pill-inline-meta">
              <span v-if="beach.level_text">{{ beach.level_text }}</span>
              <span v-if="beach.hnr_text">HNR {{ beach.hnr_text }}</span>
            </div>
          </div>
        </article>
      </section>

      <section class="pill-panel">
        <div class="pill-panel-head">
          <div>
            <div class="pill-panel-kicker">物品栏</div>
            <h2>当前库存</h2>
          </div>
        </div>

        <div class="pill-toolkit">
          <div class="pill-tool-block">
            <div class="pill-tool-head">
              <div class="pill-tool-title">⚗️ 一键炼造魔丸</div>
              <div class="pill-tool-meta">
                <span>最大可炼造 {{ magicPillMax }} 颗</span>
                <span v-if="magicPillRecipe?.materials?.length">材料：{{ magicPillRecipe.materials.join(' / ') }}</span>
              </div>
            </div>
            <div class="pill-tool-row">
              <label class="pill-inline-field">
                <span>数量</span>
                <input
                  v-model="pillCraftQuantity"
                  class="pill-number-input"
                  type="number"
                  min="1"
                  :max="Math.max(magicPillMax, 1)"
                />
              </label>
              <v-btn variant="text" :disabled="!magicPillMax" @click="setPillCraftMax">最大</v-btn>
              <v-btn
                color="deep-purple-accent-3"
                variant="flat"
                :loading="loading"
                :disabled="loading || !magicPillMax"
                @click="craftMagicPill"
              >
                一键炼造
              </v-btn>
            </div>
          </div>

          <div class="pill-tool-block">
            <div class="pill-tool-head">
              <div class="pill-tool-title">💰 兑换魔力</div>
              <div class="pill-tool-meta">
                <span>价格 {{ exchangePriceText }}</span>
                <span>可兑换 {{ exchange.max_count || 0 }} 颗</span>
              </div>
            </div>
            <div class="pill-tool-row">
              <label class="pill-inline-field">
                <span>数量</span>
                <input
                  v-model="exchangeQuantity"
                  class="pill-number-input"
                  type="number"
                  min="1"
                  :max="Math.max(Number(exchange.max_count || 0), 1)"
                />
              </label>
              <v-btn
                color="amber-darken-2"
                variant="flat"
                :loading="loading"
                :disabled="loading || !exchange.action_ready"
                @click="exchangePoints"
              >
                兑换魔力
              </v-btn>
            </div>
          </div>
        </div>

        <div v-if="pill.inventory?.empty" class="pill-empty">{{ pill.inventory?.empty_text }}</div>
        <div v-else class="pill-inventory-grid">
          <article v-for="item in inventoryItems" :key="item.name" class="pill-inventory-card" :class="{ active: item.has_items }">
            <div class="pill-item-icon">{{ item.icon }}</div>
            <div class="pill-item-name">{{ item.name }}</div>
            <div class="pill-item-count">{{ item.count }}</div>
          </article>
        </div>
      </section>

      <section class="pill-panel">
        <div class="pill-panel-head">
          <div>
            <div class="pill-panel-kicker">最近记录</div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="pill-empty">暂无执行记录</div>
        <div v-else class="pill-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="pill-history-item">
            <div class="pill-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div class="pill-history-lines">{{ (item.lines || []).join(' / ') }}</div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

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
const pluginBase = '/plugin/SQPill'

let timer = null
let themeObserver = null
let mediaQuery = null
let observedThemeNode = null
let pendingRefreshTimer = null

const pill = computed(() => status.pill_status || {})
const overview = computed(() => pill.value.overview || [])
const exchange = computed(() => pill.value.exchange || {})
const brick = computed(() => pill.value.brick || {})
const beach = computed(() => pill.value.beach || {})
const inventoryItems = computed(() => pill.value.inventory?.items || [])
const crafting = computed(() => pill.value.crafting || {})
const magicPillMax = computed(() => Number(crafting.value.magic_pill_max || 0))
const magicPillRecipe = computed(() => crafting.value.magic_pill_recipe || {})
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

const brickHeadline = computed(() => {
  if (brick.value.ready) return '可立即搬砖'
  if (Number(brick.value.daily_bricks || 0) >= Number(brick.value.daily_limit || 50)) return '今日已达上限'
  return '等待搬砖'
})

const beachHeadline = computed(() => (beach.value.ready ? '可立即清理' : '冷却中'))

const brickCountdownText = computed(() => {
  if (brick.value.ready) return '现在可以开始搬砖'
  const remain = brickResetTs.value - nowTs.value
  if (brickResetTs.value && remain > 0) {
    return `明日可搬: ${formatCountdown(remain)}`
  }
  return brick.value.status_text || '等待刷新'
})

const beachCountdownText = computed(() => {
  if (beach.value.ready) return '现在可以进入沙滩'
  const remain = beachReadyTs.value - nowTs.value
  if (beachReadyTs.value && remain > 0) {
    return `下次清理: ${formatCountdown(remain)}`
  }
  return beach.value.status_text || '等待刷新'
})

function normalizePositiveInt(value, fallback = 1) {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

watch(summaryKey, (nextKey, prevKey) => {
  if (nextKey && nextKey !== prevKey) {
    dismissedSummaryKey.value = ''
  }
})

watch(
  () => exchange.value.max_count,
  (maxCount) => {
    const limit = Math.max(normalizePositiveInt(maxCount, 1), 1)
    exchangeQuantity.value = String(Math.min(normalizePositiveInt(exchangeQuantity.value, 1), limit))
  },
  { immediate: true },
)

watch(
  () => magicPillMax.value,
  (maxCount) => {
    const limit = Math.max(normalizePositiveInt(maxCount, 1), 1)
    pillCraftQuantity.value = String(Math.min(normalizePositiveInt(pillCraftQuantity.value, 1), limit))
  },
  { immediate: true },
)

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const safe = value.replace(/-/g, '/')
  const parsed = Date.parse(safe)
  return Number.isNaN(parsed) ? 0 : Math.floor(parsed / 1000)
}

function formatCountdown(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds || 0))
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const seconds = safeSeconds % 60
  return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function closePlugin() {
  if (showSummary.value) {
    dismissSummary()
  }
  emit('close')
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('sqpill-dismissed-summary', key)
    } else {
      window.sessionStorage.removeItem('sqpill-dismissed-summary')
    }
  }
}

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = ''
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('sqpill-dismissed-summary') || ''
}

async function loadStatus() {
  const data = await props.api.get(`${pluginBase}/status`)
  applyStatusPayload(data)
}

function applyStatusPayload(payload = {}) {
  const nextStatus = payload?.status?.pill_status || payload?.pill_status || {}
  if (Object.keys(nextStatus).length) {
    status.pill_status = nextStatus
  }
  if (Array.isArray(payload?.history)) {
    status.history = payload.history
  } else if (Array.isArray(payload?.status?.history)) {
    status.history = payload.status.history
  }

  const runTs = Number(status.pill_status?.next_run_ts || 0) || parseDateTime(status.pill_status?.next_run_time)
  const triggerTs = Number(status.pill_status?.next_trigger_ts || 0) || parseDateTime(status.pill_status?.next_trigger_time)
  if (runTs && nowTs.value >= runTs) {
    lastRunAutoRefreshTs.value = runTs
  }
  if (triggerTs && nowTs.value >= triggerTs) {
    lastTriggerAutoRefreshTs.value = triggerTs
  }
  if (brickResetTs.value && nowTs.value >= brickResetTs.value) {
    lastBrickCooldownRefreshTs.value = brickResetTs.value
  }
  if (beachReadyTs.value && nowTs.value >= beachReadyTs.value) {
    lastBeachCooldownRefreshTs.value = beachReadyTs.value
  }
}

async function silentRefreshStatus() {
  try {
    await loadStatus()
  } catch (error) {
    console.warn('[SQPill] silent refresh failed', error)
  }
}

function scheduleFollowUpRefresh(delay = 1200) {
  if (pendingRefreshTimer) {
    window.clearTimeout(pendingRefreshTimer)
  }
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
    if (!silent) {
      flash(result?.message || '操作完成')
    }
  } catch (error) {
    if (!silent) {
      flash(error?.message || '操作失败', 'error')
    }
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  await doAction(() => props.api.post(`${pluginBase}/refresh`))
}

async function runNow() {
  await doAction(() => props.api.post(`${pluginBase}/run`))
}

async function syncCookie() {
  await doAction(() => props.api.get(`${pluginBase}/cookie`))
}

async function moveBricks() {
  await doAction(() => props.api.post(`${pluginBase}/move-bricks`))
}

async function cleanBeach() {
  await doAction(() => props.api.post(`${pluginBase}/clean-beach`))
}

async function exchangePoints() {
  if (!exchange.value.action_ready) {
    flash('当前没有可兑换的魔丸', 'warning')
    return
  }
  const limit = Math.max(normalizePositiveInt(exchange.value.max_count, 1), 1)
  const quantity = Math.min(normalizePositiveInt(exchangeQuantity.value, 1), limit)
  exchangeQuantity.value = String(quantity)
  await doAction(() => props.api.post(`${pluginBase}/exchange-points`, { quantity }))
}

function setPillCraftMax() {
  if (!magicPillMax.value) return
  pillCraftQuantity.value = String(magicPillMax.value)
}

async function craftMagicPill() {
  if (!magicPillMax.value) {
    flash('当前材料不足，无法炼造魔丸', 'warning')
    return
  }
  const quantity = Math.min(normalizePositiveInt(pillCraftQuantity.value, 1), magicPillMax.value)
  pillCraftQuantity.value = String(quantity)
  await doAction(() => props.api.post(`${pluginBase}/craft-max-pill`, { quantity }))
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme')) return document.body
  if (document.documentElement?.getAttribute('data-theme')) return document.documentElement
  return null
}

function detectTheme() {
  const themeNode = findThemeNode()
  const themeValue = themeNode?.getAttribute?.('data-theme') || ''
  const darkThemes = new Set(['dark', 'purple', 'transparent'])
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  isDarkTheme.value = darkThemes.has(themeValue) || (!themeValue && !!prefersDark)
}

function bindThemeObserver() {
  themeObserver?.disconnect()
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode()
    if (nextNode && nextNode !== observedThemeNode) {
      bindThemeObserver()
      return
    }
    detectTheme()
  })
  observedThemeNode = findThemeNode()
  if (observedThemeNode) {
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme', 'class'] })
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
  detectTheme()
  bindThemeObserver()
  loadDismissedSummaryKey()
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
  await loadStatus()
  timer = window.setInterval(tick, 1000)
})

watch(summaryKey, () => {
  loadDismissedSummaryKey()
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
  if (pendingRefreshTimer) window.clearTimeout(pendingRefreshTimer)
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.pill-page {
  --pill-bg: linear-gradient(180deg, #f7f2e8 0%, #f0ece2 100%);
  --pill-card: rgba(255, 255, 255, 0.88);
  --pill-card-strong: #ffffff;
  --pill-text: #203135;
  --pill-muted: #60757c;
  --pill-border: rgba(60, 83, 84, 0.16);
  --pill-shadow: 0 16px 30px rgba(90, 78, 36, 0.08);
  --pill-accent: #ff8f3d;
  --pill-accent-soft: rgba(255, 143, 61, 0.14);
  min-height: 100%;
  padding: 20px 0 32px;
  background: var(--pill-bg);
  color: var(--pill-text);
  overflow-x: hidden;
}

.pill-page,
.pill-page * {
  box-sizing: border-box;
}

.pill-page.is-dark-theme {
  --pill-bg: linear-gradient(180deg, #151b1b 0%, #101515 100%);
  --pill-card: rgba(26, 34, 34, 0.92);
  --pill-card-strong: #1f2727;
  --pill-text: #f2f0e7;
  --pill-muted: #98aca8;
  --pill-border: rgba(166, 192, 183, 0.16);
  --pill-shadow: 0 20px 40px rgba(0, 0, 0, 0.28);
  --pill-accent: #ffb24c;
  --pill-accent-soft: rgba(255, 178, 76, 0.18);
}

.pill-shell {
  width: 100%;
  max-width: 1080px;
  min-width: 0;
  padding: 0 12px;
  margin: 0 auto;
  display: grid;
  gap: 16px;
}

.pill-hero,
.pill-panel {
  border-radius: 28px;
  padding: 20px;
  background: var(--pill-card);
  border: 1px solid var(--pill-border);
  box-shadow: var(--pill-shadow);
}

.pill-hero {
  display: grid;
  gap: 14px;
}

.pill-badge,
.pill-status-chip {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.pill-badge {
  background: var(--pill-accent-soft);
  color: var(--pill-accent);
}

.pill-title {
  margin: 10px 0 6px;
  font-size: clamp(24px, 3.4vw, 36px);
  line-height: 1.05;
}

.pill-subtitle,
.pill-panel-note,
.pill-history-lines,
.pill-status-desc {
  color: var(--pill-muted);
}

.pill-hero-meta,
.pill-actions,
.pill-stat-grid,
.pill-action-grid,
.pill-inventory-grid,
.pill-history-list {
  display: grid;
  gap: 12px;
}

.pill-hero-meta {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  font-size: 13px;
}

.pill-actions {
  grid-template-columns: repeat(auto-fit, minmax(min(108px, 100%), 1fr));
}

.pill-stat-grid {
  grid-template-columns: repeat(auto-fit, minmax(min(160px, 100%), 1fr));
}

.pill-stat-card,
.pill-summary-line,
.pill-history-item,
.pill-inventory-card,
.pill-tool-block {
  border-radius: 22px;
  border: 1px solid var(--pill-border);
  background: var(--pill-card-strong);
}

.pill-stat-card {
  padding: 18px;
}

.pill-stat-label,
.pill-panel-kicker,
.pill-card-label {
  color: var(--pill-muted);
  font-size: 13px;
  font-weight: 700;
}

.pill-stat-value {
  margin-top: 10px;
  font-size: clamp(26px, 4vw, 38px);
  font-weight: 900;
}

.pill-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.pill-panel-head h2 {
  margin: 6px 0 0;
  font-size: 24px;
}

.pill-summary-list {
  display: grid;
  gap: 12px;
}

.pill-summary-line,
.pill-history-item {
  padding: 16px 18px;
}

.pill-action-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: start;
}

.pill-status-card {
  padding: 18px;
}

.pill-status-chip {
  color: #88612b;
  background: rgba(255, 179, 76, 0.16);
}

.pill-status-chip.ready {
  color: #1d8c57;
  background: rgba(47, 193, 120, 0.16);
}

.pill-status-body {
  display: grid;
  gap: 10px;
}

.pill-status-title {
  font-size: clamp(24px, 3.4vw, 34px);
  font-weight: 900;
  line-height: 1.05;
}

.pill-status-countdown {
  font-size: clamp(18px, 2vw, 22px);
  font-weight: 800;
  color: var(--pill-accent);
}

.pill-inline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-inline-meta span {
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--pill-accent-soft);
  color: var(--pill-accent);
  font-size: 12px;
  font-weight: 700;
}

.pill-toolkit {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.pill-tool-block {
  padding: 14px 16px;
  display: grid;
  gap: 12px;
}

.pill-tool-head {
  display: grid;
  gap: 6px;
}

.pill-tool-title {
  font-size: 16px;
  font-weight: 900;
}

.pill-tool-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  color: var(--pill-muted);
  font-size: 12px;
}

.pill-tool-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 10px;
}

.pill-inline-field {
  min-width: 116px;
  display: grid;
  gap: 8px;
  font-size: 13px;
  color: var(--pill-muted);
}

.pill-number-input {
  width: 100%;
  border: 1px solid var(--pill-border);
  border-radius: 14px;
  background: var(--pill-card-strong);
  color: var(--pill-text);
  padding: 12px 14px;
  outline: none;
}

.pill-number-input:focus {
  border-color: rgba(255, 143, 61, 0.5);
  box-shadow: 0 0 0 3px rgba(255, 143, 61, 0.12);
}

.pill-inventory-grid {
  grid-template-columns: repeat(auto-fit, minmax(min(78px, 100%), 1fr));
}

.pill-inventory-card {
  padding: 10px 8px;
  display: grid;
  gap: 4px;
  text-align: center;
}

.pill-inventory-card.active {
  border-color: rgba(41, 161, 98, 0.36);
  box-shadow: inset 0 0 0 1px rgba(41, 161, 98, 0.18);
}

.pill-item-icon {
  font-size: 16px;
}

.pill-item-name {
  font-size: 11px;
  font-weight: 800;
}

.pill-item-count {
  font-size: 14px;
  font-weight: 900;
}

.pill-history-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.pill-empty {
  padding: 24px;
  text-align: center;
  color: var(--pill-muted);
}

@media (max-width: 860px) {
  .pill-action-grid,
  .pill-toolkit {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .pill-shell {
    padding: 0 8px;
  }

  .pill-hero,
  .pill-panel {
    padding: 18px;
    border-radius: 22px;
  }

  .pill-panel-head {
    flex-direction: column;
  }

  .pill-tool-row {
    width: 100%;
    justify-content: stretch;
  }
}
</style>
