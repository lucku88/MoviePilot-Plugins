<template>
  <div ref="rootEl" class="sq-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="sq-shell">
      <section class="sq-hero">
        <div class="sq-hero-copy">
          <div class="sq-badge">SQ农场</div>
          <h1 class="sq-title">{{ farm.title || '种菜赚魔力' }}</h1>
          <p class="sq-subtitle">
            最近执行 {{ status.last_run || '暂无' }} · 下次可收 {{ farm.next_run_time || '待识别' }}
          </p>
        </div>
        <div class="sq-actions">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
        <div class="sq-hero-meta">
          <div class="sq-meta-chip">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待下一次运行' }}</div>
          <div class="sq-meta-chip">站点同步 {{ farm.cookie_source || status.cookie_source || '未同步' }}</div>
          <div class="sq-meta-chip">成熟 {{ readySlots.length }} 块</div>
          <div class="sq-meta-chip">空地 {{ emptySlots.length }} 块</div>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="sq-stat-grid">
        <article v-for="item in farm.overview || []" :key="item.label" class="sq-stat-card">
          <div class="sq-stat-label">{{ item.label }}</div>
          <div class="sq-stat-value">{{ item.value }}</div>
        </article>
      </section>

      <section v-if="showSummary" class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">本次摘要</div>
            <h2>任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="sq-summary-list">
          <div v-for="line in summaryLines" :key="line" class="sq-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">收获背包</div>
            <h2>当前库存</h2>
          </div>
        </div>
        <div v-if="farm.inventory?.empty" class="sq-empty">{{ farm.inventory?.empty_text }}</div>
        <div v-else class="sq-bag-grid">
          <article v-for="item in inventoryItems" :key="item.seed_id || item.name" class="sq-bag-card">
            <div class="sq-bag-icon">{{ item.icon }}</div>
            <div class="sq-bag-name">{{ item.name }}</div>
            <div class="sq-bag-meta">数量 {{ item.quantity }}</div>
            <div class="sq-bag-meta">
              售：{{ item.unit_reward }} 魔力/份
              <span class="sq-bag-bonus">+{{ item.sell_bonus_percent || 0 }}%</span>
            </div>
            <div class="sq-bag-sell">
              <input
                class="sq-bag-input"
                type="number"
                min="1"
                :max="item.quantity"
                :value="getSellQuantity(item)"
                :disabled="loading || sellingSeedId === item.seed_id"
                @click.stop
                @input="updateSellQuantity(item, $event)"
              >
              <button
                type="button"
                class="sq-bag-button"
                :disabled="loading || !item.quantity || sellingSeedId === item.seed_id"
                @click.stop="sellInventory(item)"
              >
                {{ sellingSeedId === item.seed_id ? '售出中' : '售出' }}
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head sq-panel-head-wrap">
          <div>
            <div class="sq-panel-kicker">种子商店</div>
            <h2>选择种子后点击空地种植</h2>
          </div>
          <div class="sq-shop-actions">
            <div class="sq-selected-seed">
              当前种子：
              <strong v-if="selectedSeed">{{ selectedSeed.icon }} {{ selectedSeed.name }}</strong>
              <strong v-else>未选择</strong>
            </div>
            <v-btn
              color="success"
              variant="flat"
              :disabled="!selectedSeed || !emptySlots.length || loading"
              @click="plantAllEmpty"
            >
              一键种植空地
            </v-btn>
            <v-btn
              color="warning"
              variant="flat"
              :disabled="!readySlots.length || loading"
              @click="harvestAllReady"
            >
              一键收获
            </v-btn>
          </div>
        </div>
        <div class="sq-seed-grid">
          <button
            v-for="seed in farm.seed_shop || []"
            :key="seed.id"
            type="button"
            class="sq-seed-card"
            :class="{
              'is-locked': !seed.unlocked,
              'is-selected': selectedSeed && Number(selectedSeed.id) === Number(seed.id),
            }"
            :disabled="!seed.unlocked || loading"
            @click="selectSeed(seed)"
          >
            <div class="sq-seed-icon">{{ seed.icon }}</div>
            <div class="sq-seed-name">{{ seed.name }}</div>
            <div class="sq-seed-line">消耗 {{ seed.cost }}</div>
            <div class="sq-seed-line">生长 {{ seed.grow_text }}</div>
            <div class="sq-seed-note">
              {{ seed.unlocked ? (selectedSeed && Number(selectedSeed.id) === Number(seed.id) ? '已选中' : '点击选择') : seed.unlock_text }}
            </div>
          </button>
        </div>
      </section>

      <section class="sq-panel sq-farm-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">农场坑位</div>
            <h2>分组状态</h2>
          </div>
        </div>
        <div class="sq-land-stack">
          <article v-for="group in farm.land_groups || []" :key="group.id" class="sq-land-group">
            <header class="sq-group-head">
              <div>
                <div class="sq-group-name">{{ group.name }}</div>
              </div>
              <div class="sq-group-subtitle">{{ group.subtitle }}</div>
            </header>
            <div class="sq-slot-grid">
              <button
                v-for="slot in group.slots"
                :key="`${group.id}-${slot.slot_index}`"
                type="button"
                class="sq-slot"
                :class="[
                  `is-${slot.state}`,
                  { 'is-clickable': isInteractiveSlot(slot), 'is-busy': actingSlotKey === slotKey(slot) }
                ]"
                :disabled="loading || actingSlotKey === slotKey(slot)"
                @click="handleSlotClick(slot)"
              >
                <div class="sq-slot-top">
                  <span class="sq-slot-index">#{{ slot.slot_index }}</span>
                  <span class="sq-slot-badge">{{ slot.badge }}</span>
                </div>
                <div class="sq-slot-icon">{{ slot.icon }}</div>
                <div class="sq-slot-name">{{ slot.title }}</div>
                <div class="sq-slot-time">{{ slotText(slot) }}</div>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">最近记录</div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="sq-empty">暂无执行记录</div>
        <div v-else class="sq-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="sq-history-item">
            <div class="sq-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div class="sq-history-lines">{{ (item.lines || []).join(' / ') }}</div>
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
const actingSlotKey = ref('')
const sellingSeedId = ref(0)
const rootEl = ref(null)
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const isDarkTheme = ref(false)
const selectedSeedId = ref(null)
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)
const sellInputs = reactive({})
const dismissedSummaryKey = ref('')

let timer = null
let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

const farm = computed(() => status.farm_status || {})
const historyItems = computed(() => status.history || farm.value.history || [])
const summaryLines = computed(() => (farm.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)
const seedShop = computed(() => farm.value.seed_shop || [])
const inventoryItems = computed(() => farm.value.inventory?.items || [])
const unlockedSeeds = computed(() => seedShop.value.filter((seed) => seed.unlocked))
const selectedSeed = computed(() => {
  return seedShop.value.find((seed) => Number(seed.id) === Number(selectedSeedId.value)) || null
})
const allSlots = computed(() => {
  return (farm.value.land_groups || []).flatMap((group) => group.slots || [])
})
const readySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'ready'))
const emptySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'empty'))
const nextRunTs = computed(() => Number(farm.value.next_run_ts || 0) || parseDateTime(farm.value.next_run_time))
const nextTriggerTs = computed(() => Number(farm.value.next_trigger_ts || 0) || parseDateTime(farm.value.next_trigger_time))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') {
    return 0
  }
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/)
  if (!match) {
    return 0
  }
  const [, year, month, day, hour, minute, second] = match
  return Math.floor(
    new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
      Number(hour),
      Number(minute),
      Number(second),
    ).getTime() / 1000,
  )
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

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = ''
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('sqfarm-dismissed-summary') || ''
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('sqfarm-dismissed-summary', key)
    } else {
      window.sessionStorage.removeItem('sqfarm-dismissed-summary')
    }
  }
}

function bindThemeObserver() {
  themeObserver?.disconnect()
  themeObserver = new MutationObserver(() => {
    detectTheme()
  })

  observedThemeNode = findThemeNode()
  for (const node of getThemeNodes()) {
    themeObserver.observe(node, {
      attributes: true,
      subtree: true,
      attributeFilter: ['data-theme', 'class'],
    })
  }
}

function syncSelectedSeed() {
  const available = unlockedSeeds.value
  if (!available.length) {
    selectedSeedId.value = null
    return
  }

  const current = available.find((seed) => Number(seed.id) === Number(selectedSeedId.value))
  if (current) {
    return
  }

  const preferred = available.find((seed) => seed.preferred)
  selectedSeedId.value = Number((preferred || available[0]).id)
}

watch(seedShop, syncSelectedSeed, { immediate: true, deep: true })

watch(summaryKey, () => {
  loadDismissedSummaryKey()
})

watch(
  inventoryItems,
  (items) => {
    const activeKeys = new Set()
    for (const item of items) {
      const key = String(item.seed_id || item.name)
      activeKeys.add(key)
      const current = Number(sellInputs[key])
      sellInputs[key] = current > 0 ? Math.min(current, Number(item.quantity || 1)) : 1
    }
    for (const key of Object.keys(sellInputs)) {
      if (!activeKeys.has(key)) {
        delete sellInputs[key]
      }
    }
  },
  { immediate: true, deep: true },
)

watch(nextRunTs, (value) => {
  if (!value || value > nowTs.value) {
    lastRunAutoRefreshTs.value = 0
  }
})

watch(nextTriggerTs, (value) => {
  if (!value || value > nowTs.value) {
    lastTriggerAutoRefreshTs.value = 0
  }
})

async function loadStatus() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/SQFarm/status')
    Object.assign(status, res || {})
  } catch (error) {
    flash(error?.message || '加载状态失败', 'error')
  } finally {
    loading.value = false
  }
}

async function maybeAutoRefreshStatus() {
  if (loading.value) {
    return
  }

  let shouldRefresh = false
  if (nextRunTs.value && nowTs.value >= nextRunTs.value && nextRunTs.value !== lastRunAutoRefreshTs.value) {
    lastRunAutoRefreshTs.value = nextRunTs.value
    shouldRefresh = true
  }

  if (nextTriggerTs.value && nowTs.value >= nextTriggerTs.value && nextTriggerTs.value !== lastTriggerAutoRefreshTs.value) {
    lastTriggerAutoRefreshTs.value = nextTriggerTs.value
    shouldRefresh = true
  }

  if (shouldRefresh) {
    await loadStatus()
  }
}

async function refreshData() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/refresh', {})
    flash(res.message || '已刷新')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '刷新失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runNow() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/run', {})
    flash(res.message || '执行完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function syncCookie() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/SQFarm/cookie')
    flash(res.message || 'Cookie 已同步')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    loading.value = false
  }
}

function selectSeed(seed) {
  if (!seed?.unlocked) {
    return
  }
  selectedSeedId.value = Number(seed.id)
  flash(`已选择 ${seed.icon} ${seed.name}`)
}

function slotKey(slot) {
  return `${slot.land_id}-${slot.slot_index}`
}

function isInteractiveSlot(slot) {
  return slot.state === 'ready' || slot.state === 'empty'
}

function inventoryKey(item) {
  return String(item.seed_id || item.name)
}

function getSellQuantity(item) {
  const key = inventoryKey(item)
  const current = Number(sellInputs[key])
  if (!current || current < 1) {
    return 1
  }
  return Math.min(current, Number(item.quantity || 1))
}

function updateSellQuantity(item, event) {
  const raw = Number(event?.target?.value || 1)
  const safe = Math.min(Math.max(1, raw || 1), Number(item.quantity || 1))
  sellInputs[inventoryKey(item)] = safe
}

async function plantPlot(slot, seedId) {
  actingSlotKey.value = slotKey(slot)
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/plant-plot', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
      seed_id: seedId,
    })
    flash(res.message || '种植完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '种植失败', 'error')
  } finally {
    actingSlotKey.value = ''
    loading.value = false
  }
}

async function harvestPlot(slot) {
  actingSlotKey.value = slotKey(slot)
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/harvest-plot', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
    })
    flash(res.message || '收菜完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '收菜失败', 'error')
  } finally {
    actingSlotKey.value = ''
    loading.value = false
  }
}

async function sellInventory(item) {
  const seedId = Number(item.seed_id || 0)
  const quantity = getSellQuantity(item)
  if (!seedId || quantity <= 0) {
    flash('售出参数无效', 'warning')
    return
  }

  sellingSeedId.value = seedId
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/sell-inventory', {
      seed_id: seedId,
      quantity,
    })
    flash(res.message || '售出完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '售出失败', 'error')
  } finally {
    sellingSeedId.value = 0
    loading.value = false
  }
}

async function plantAllEmpty() {
  if (!emptySlots.value.length) {
    flash('当前没有可种植空地', 'warning')
    return
  }
  if (!selectedSeed.value) {
    flash('请先选择种子', 'warning')
    return
  }
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/plant-empty', {
      seed_id: selectedSeed.value.id,
    })
    flash(res.message || '一键种植完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '一键种植失败', 'error')
  } finally {
    loading.value = false
  }
}

async function harvestAllReady() {
  if (!readySlots.value.length) {
    flash('当前没有可收获田块', 'warning')
    return
  }
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/harvest-all', {})
    flash(res.message || '一键收获完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '一键收获失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleSlotClick(slot) {
  if (loading.value) {
    return
  }

  if (slot.state === 'ready') {
    await harvestPlot(slot)
    return
  }

  if (slot.state === 'empty') {
    if (!selectedSeed.value) {
      flash('请先在种子商店选择一个种子', 'warning')
      return
    }
    await plantPlot(slot, selectedSeed.value.id)
    return
  }

  if (slot.state === 'growing') {
    flash(`${slot.title} 还需 ${slot.remaining_label || slot.reward_text || '等待成长'}`, 'info')
    return
  }

  if (slot.state === 'expand') {
    flash(`${slot.land_name} 可扩展：${slot.description}`, 'info')
    return
  }

  if (slot.state === 'locked') {
    flash(`${slot.land_name} 这块田暂未解锁`, 'info')
  }
}

function formatRemain(seconds) {
  const sec = Math.max(0, Number(seconds) || 0)
  if (!sec) return '现在可收'
  const hours = Math.floor(sec / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  const secs = sec % 60
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
  return `${secs}秒`
}

function slotText(slot) {
  if (slot.harvest_ts) {
    const remain = slot.harvest_ts - nowTs.value
    if (slot.state === 'growing') return formatRemain(remain)
    if (slot.state === 'ready') return '现在可收'
  }
  return slot.remaining_label || slot.reward_text || ''
}

function closePlugin() {
  if (showSummary.value) {
    dismissSummary()
  }
  emit('close')
}

onMounted(async () => {
  loadDismissedSummaryKey()
  detectTheme()
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)')
  mediaQuery?.addEventListener?.('change', detectTheme)
  bindThemeObserver()

  await loadStatus()
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    void maybeAutoRefreshStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style>
.sq-page {
  --sq-bg: linear-gradient(180deg, #f4f5f8 0%, #fafafb 46%, #f2f4f8 100%);
  --sq-surface: #ffffff;
  --sq-surface-soft: #f6f7fb;
  --sq-panel: rgba(255, 255, 255, 0.92);
  --sq-border: rgba(122, 134, 167, 0.16);
  --sq-shadow: 0 20px 42px rgba(91, 102, 130, 0.1);
  --sq-text: #2f3347;
  --sq-subtle: #6e758e;
  --sq-soft: #8d93aa;
  --sq-accent: #7c5cff;
  --sq-accent-soft: rgba(124, 92, 255, 0.12);
  --sq-ready: linear-gradient(180deg, #e6f6df 0%, #cfeebd 100%);
  --sq-growing: linear-gradient(180deg, #fff0bf 0%, #ffd26a 100%);
  --sq-empty: linear-gradient(180deg, #f3f6ff 0%, #e8eefc 100%);
  --sq-expand: linear-gradient(180deg, #f4f6fb 0%, #ebeff8 100%);
  --sq-locked: linear-gradient(180deg, #edf1f6 0%, #e1e7ef 100%);
  min-height: 100%;
  padding: clamp(16px, 2vw, 22px);
  background: var(--sq-bg);
  color: var(--sq-text);
}

.sq-page.is-dark-theme {
  --sq-bg: linear-gradient(180deg, #171921 0%, #12151d 48%, #0d1017 100%);
  --sq-surface: #1b1f2b;
  --sq-surface-soft: #232838;
  --sq-panel: rgba(24, 28, 39, 0.92);
  --sq-border: rgba(111, 122, 168, 0.2);
  --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
  --sq-text: #eff1f7;
  --sq-subtle: #b5bbd3;
  --sq-soft: #868fae;
  --sq-accent: #8c72ff;
  --sq-accent-soft: rgba(124, 92, 255, 0.18);
  --sq-ready: linear-gradient(180deg, #41653e 0%, #4c8454 100%);
  --sq-growing: linear-gradient(180deg, #8b6b2f 0%, #b98b35 100%);
  --sq-empty: linear-gradient(180deg, #2d3346 0%, #333b53 100%);
  --sq-expand: linear-gradient(180deg, #353d52 0%, #3f4862 100%);
  --sq-locked: linear-gradient(180deg, #31384a 0%, #3a4357 100%);
}

.sq-shell {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sq-hero,
.sq-panel,
.sq-stat-card,
.sq-land-group {
  border: 1px solid var(--sq-border);
  box-shadow: var(--sq-shadow);
}

.sq-hero {
  padding: 22px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(124, 92, 255, 0.14), transparent 28%),
    radial-gradient(circle at bottom left, rgba(255, 184, 0, 0.12), transparent 26%),
    var(--sq-panel);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px 20px;
  align-items: start;
}

.sq-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--sq-accent-soft);
  color: var(--sq-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.sq-title {
  margin: 14px 0 8px;
  font-size: clamp(30px, 4vw, 40px);
  line-height: 1.05;
  font-weight: 900;
}

.sq-subtitle {
  margin: 0;
  color: var(--sq-subtle);
  line-height: 1.7;
  font-size: 14px;
}

.sq-actions,
.sq-hero-meta,
.sq-shop-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.sq-actions {
  justify-content: flex-end;
}

.sq-hero-meta {
  grid-column: 1 / -1;
}

.sq-meta-chip,
.sq-selected-seed {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 13px;
  border-radius: 14px;
  background: var(--sq-surface-soft);
  color: var(--sq-subtle);
  border: 1px solid var(--sq-border);
  font-size: 13px;
  font-weight: 600;
}

.sq-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.sq-stat-card {
  border-radius: 20px;
  padding: 16px;
  background: var(--sq-panel);
  text-align: center;
}

.sq-stat-label {
  color: var(--sq-soft);
  font-size: 13px;
}

.sq-stat-value {
  margin-top: 8px;
  font-size: clamp(26px, 3vw, 34px);
  font-weight: 900;
}

.sq-panel {
  padding: 18px;
  border-radius: 22px;
  background: var(--sq-panel);
}

.sq-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.sq-panel-head-wrap {
  flex-wrap: wrap;
}

.sq-panel-kicker {
  color: var(--sq-soft);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sq-panel-head h2 {
  margin: 6px 0 0;
  font-size: 22px;
  line-height: 1.15;
  font-weight: 800;
}

.sq-summary-list,
.sq-history-list,
.sq-land-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sq-summary-line,
.sq-history-item {
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--sq-surface-soft);
  border: 1px solid var(--sq-border);
}

.sq-empty {
  padding: 36px 18px;
  text-align: center;
  color: var(--sq-soft);
  border-radius: 18px;
  background: var(--sq-surface-soft);
}

.sq-bag-grid,
.sq-seed-grid {
  display: grid;
  gap: 12px;
}

.sq-bag-grid {
  grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
}

.sq-seed-grid {
  grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
}

.sq-bag-card,
.sq-seed-card {
  padding: 14px 12px;
  border-radius: 16px;
  background: var(--sq-surface-soft);
  border: 1px solid var(--sq-border);
  text-align: center;
}

.sq-seed-card {
  appearance: none;
  width: 100%;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.sq-seed-card:hover:not(:disabled),
.sq-slot.is-clickable:hover:not(:disabled) {
  transform: translateY(-1px);
}

.sq-seed-card.is-selected {
  border-color: rgba(102, 187, 106, 0.56);
  box-shadow: 0 0 0 2px rgba(102, 187, 106, 0.14);
}

.sq-seed-card.is-locked {
  opacity: 0.52;
  cursor: not-allowed;
}

.sq-bag-icon,
.sq-seed-icon {
  font-size: 28px;
}

.sq-bag-name,
.sq-seed-name {
  margin-top: 8px;
  font-weight: 800;
}

.sq-bag-meta,
.sq-seed-line,
.sq-seed-note,
.sq-slot-badge,
.sq-slot-desc,
.sq-slot-time,
.sq-group-subtitle,
.sq-history-top span,
.sq-history-lines {
  color: var(--sq-subtle);
  font-size: 12px;
}

.sq-bag-bonus {
  margin-left: 4px;
  color: #e67e22;
  font-weight: 800;
}

.sq-bag-sell {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.sq-bag-input {
  width: 60px;
  height: 32px;
  padding: 4px 8px;
  border-radius: 10px;
  border: 1px solid var(--sq-border);
  background: var(--sq-surface);
  color: var(--sq-text);
  text-align: center;
  outline: none;
}

.sq-bag-button {
  border: none;
  border-radius: 10px;
  padding: 7px 12px;
  font-size: 12px;
  font-weight: 800;
  background: linear-gradient(180deg, #ffb341 0%, #ff9800 100%);
  color: #fff;
  cursor: pointer;
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.sq-bag-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.sq-bag-button:disabled,
.sq-bag-input:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.sq-farm-panel {
  padding: 14px;
}

.sq-land-group {
  padding: 10px;
  border-radius: 18px;
  background: var(--sq-surface);
}

.sq-group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.sq-group-name {
  font-size: 20px;
  font-weight: 800;
}

.sq-slot-grid {
  display: grid;
  grid-template-columns: repeat(10, minmax(0, 1fr));
  gap: 8px;
}

.sq-slot {
  appearance: none;
  width: 100%;
  min-height: 122px;
  padding: 9px 7px 10px;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: flex-start;
  text-align: center;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.sq-slot.is-clickable {
  cursor: pointer;
}

.sq-slot.is-busy {
  opacity: 0.72;
}

.sq-slot.is-growing { background: var(--sq-growing); }
.sq-slot.is-ready { background: var(--sq-ready); }
.sq-slot.is-empty { background: var(--sq-empty); }
.sq-slot.is-expand { background: var(--sq-expand); }
.sq-slot.is-locked { background: var(--sq-locked); }

.sq-slot-top {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
}

.sq-slot-index {
  font-size: 11px;
  color: var(--sq-soft);
  font-weight: 700;
}

.sq-slot-badge {
  font-weight: 700;
}

.sq-slot-icon {
  font-size: 28px;
  line-height: 1;
}

.sq-slot-name {
  font-size: 14px;
  font-weight: 800;
  line-height: 1.2;
}

.sq-slot-desc {
  line-height: 1.35;
}

.sq-slot-time {
  margin-top: auto;
  font-weight: 800;
  color: var(--sq-text);
}

.sq-history-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

@media (max-width: 1280px) {
  .sq-slot-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}

@media (max-width: 980px) {
  .sq-hero,
  .sq-stat-grid {
    grid-template-columns: 1fr;
  }

  .sq-actions {
    justify-content: flex-start;
  }

  .sq-slot-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .sq-slot-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .sq-panel-head,
  .sq-group-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
