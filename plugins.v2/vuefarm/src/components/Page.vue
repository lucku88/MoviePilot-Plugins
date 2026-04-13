<template>
  <div ref="rootEl" class="vuefarm-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="vuefarm-shell">
      <section class="vf-card vf-hero">
        <div class="vf-hero-copy">
          <div class="vf-badge">Vue-农场</div>
          <h1 class="vf-title">{{ farm.title || '种菜赚魔力' }}</h1>
          <div class="vf-chip-row">
            <span v-if="showLastRunChip" class="vf-chip">最近执行 {{ status.last_run }}</span>
            <span class="vf-chip">下次可收 {{ farm.next_run_time || '待识别' }}</span>
            <span class="vf-chip">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待下一次运行' }}</span>
            <span class="vf-chip">{{ farm.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>
        <div class="vf-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vf-stat-grid">
        <article v-for="item in farm.overview || []" :key="item.label" class="vf-card vf-stat">
          <div class="vf-stat-label">{{ item.label }}</div>
          <div class="vf-stat-value">{{ item.value }}</div>
        </article>
          <article class="vf-card vf-stat vf-stat-accent">
            <div class="vf-stat-label">农场快照</div>
            <div class="vf-pill-row">
              <span class="vf-pill ok">成熟 {{ readySlots.length }}</span>
              <span class="vf-pill info">空地 {{ emptySlots.length }}</span>
            <span class="vf-pill pri">库存 {{ inventoryItems.length }}</span>
          </div>
        </article>
      </section>

      <section v-if="showSummary" class="vf-card vf-summary">
        <div class="vf-head compact">
          <div>
            <div class="vf-kicker">本次摘要</div>
            <h2 class="vf-section-title">任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="vf-list">
          <div v-for="line in summaryLines" :key="line" class="vf-list-item">{{ line }}</div>
        </div>
      </section>

      <section class="vf-grid-2">
        <article class="vf-card vf-panel green">
          <div class="vf-head">
            <div>
              <h2 class="vf-section-title">收获背包</h2>
            </div>
            <div class="vf-note">可出售作物 {{ inventoryItems.length }} 项</div>
          </div>
          <div v-if="farm.inventory?.empty" class="vf-empty">{{ farm.inventory?.empty_text }}</div>
          <div v-else class="vf-bag-grid">
            <article v-for="item in inventoryItems" :key="item.seed_id || item.name" class="vf-bag-card" :style="cardToneStyle(item.name)">
              <div class="vf-bag-top">
                <div class="vf-bag-icon">{{ item.icon }}</div>
                <div class="vf-bag-main">
                  <div class="vf-bag-name">{{ item.name }}</div>
                  <div class="vf-bag-meta">数量 {{ item.quantity }}</div>
                </div>
              </div>
              <div class="vf-bag-line">售价 {{ item.unit_reward }} 魔力/份 <span class="vf-bonus">+{{ item.sell_bonus_percent || 0 }}%</span></div>
              <div class="vf-inline">
                <input class="vf-number" type="number" min="1" :max="item.quantity" :value="getSellQuantity(item)" :disabled="loading || sellingSeedId === item.seed_id" @click.stop @input="updateSellQuantity(item, $event)">
                <button type="button" class="vf-btn warn" :disabled="loading || !item.quantity || sellingSeedId === item.seed_id" @click.stop="sellInventory(item)">{{ sellingSeedId === item.seed_id ? '出售中' : '出售' }}</button>
              </div>
            </article>
          </div>
        </article>

        <article class="vf-card vf-panel amber">
          <div class="vf-head">
            <div>
              <h2 class="vf-section-title">种子商店</h2>
            </div>
            <div class="vf-note">当前种子：<strong v-if="selectedSeed">{{ selectedSeed.icon }} {{ selectedSeed.name }}</strong><strong v-else>未选择</strong></div>
          </div>
          <div class="vf-toolbar">
            <v-btn color="success" variant="flat" :disabled="!selectedSeed || !emptySlots.length || loading" @click="plantAllEmpty">一键种植空地</v-btn>
            <v-btn color="warning" variant="flat" :disabled="!readySlots.length || loading" @click="harvestAllReady">一键收获</v-btn>
          </div>
          <div class="vf-seed-grid">
            <button v-for="seed in farm.seed_shop || []" :key="seed.id" type="button" class="vf-seed-card" :class="{ locked: !seed.unlocked, active: selectedSeed && Number(selectedSeed.id) === Number(seed.id) }" :style="cardToneStyle(seed.name)" :disabled="!seed.unlocked || loading" @click="selectSeed(seed)">
              <div class="vf-seed-icon">{{ seed.icon }}</div>
              <div class="vf-seed-name">{{ seed.name }}</div>
              <div class="vf-seed-meta">消耗 {{ seed.cost }}</div>
              <div class="vf-seed-meta">生长 {{ seed.grow_text }}</div>
              <div class="vf-seed-note">{{ seed.unlocked ? (selectedSeed && Number(selectedSeed.id) === Number(seed.id) ? '已选中' : '点击选择') : seed.unlock_text }}</div>
            </button>
          </div>
        </article>
      </section>

      <section class="vf-card vf-panel blue">
        <div class="vf-head">
          <div>
            <h2 class="vf-section-title">农场坑位</h2>
          </div>
          <div class="vf-note">成熟可收、空地可种，其余坑位展示状态</div>
        </div>
        <div class="vf-group-stack">
          <article v-for="group in farm.land_groups || []" :key="group.id" class="vf-group">
            <header class="vf-group-head">
              <div class="vf-group-main">
                <div class="vf-group-name-row">
                  <div class="vf-group-name">{{ group.name }}</div>
                  <span class="vf-group-count">{{ (group.slots || []).length }} 块</span>
                </div>
                <div class="vf-group-sub">{{ group.subtitle }}</div>
              </div>
              <div class="vf-group-pill-row">
                <span class="vf-group-pill ready">成熟 {{ groupReadyCount(group) }}</span>
                <span class="vf-group-pill empty">空地 {{ groupEmptyCount(group) }}</span>
              </div>
            </header>
            <div class="vf-slot-grid">
              <button
                v-for="slot in group.slots"
                :key="`${group.id}-${slot.slot_index}`"
                type="button"
                class="vf-slot"
                :class="[slot.state, { clickable: isInteractiveSlot(slot), busy: actingSlotKey === slotKey(slot) }]"
                :style="slotToneStyle(slot)"
                :disabled="loading || actingSlotKey === slotKey(slot)"
                @click="handleSlotClick(slot)"
              >
                <div class="vf-slot-top">
                  <span class="vf-slot-index">#{{ slot.slot_index }}</span>
                  <span class="vf-slot-badge">{{ slot.badge }}</span>
                </div>
                <div class="vf-slot-icon">{{ slot.icon }}</div>
                <div class="vf-slot-name">{{ slot.title }}</div>
                <div class="vf-slot-time">{{ slotText(slot) }}</div>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="vf-card vf-panel slate">
        <div class="vf-head">
          <div>
            <h2 class="vf-section-title">执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="vf-empty">暂无执行记录</div>
        <div v-else class="vf-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="vf-history">
            <div class="vf-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div v-if="item.lines?.length" class="vf-history-lines">{{ (item.lines || []).join(' / ') }}</div>
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

const rootEl = ref(null)
const isDarkTheme = ref(false)
const loading = ref(false)
const actingSlotKey = ref('')
const sellingSeedId = ref(0)
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const selectedSeedId = ref(null)
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)
const dismissedSummaryKey = ref('')
const sellInputs = reactive({})

let timer = null
let themeObserver = null
let mediaQuery = null

const farm = computed(() => status.farm_status || {})
const historyItems = computed(() => status.history || farm.value.history || [])
const summaryLines = computed(() => (farm.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)
const seedShop = computed(() => farm.value.seed_shop || [])
const inventoryItems = computed(() => farm.value.inventory?.items || [])
const unlockedSeeds = computed(() => seedShop.value.filter((seed) => seed.unlocked))
const selectedSeed = computed(() => seedShop.value.find((seed) => Number(seed.id) === Number(selectedSeedId.value)) || null)
const allSlots = computed(() => (farm.value.land_groups || []).flatMap((group) => group.slots || []))
const readySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'ready'))
const emptySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'empty'))
const nextRunTs = computed(() => Number(farm.value.next_run_ts || 0) || parseDateTime(farm.value.next_run_time))
const nextTriggerTs = computed(() => Number(farm.value.next_trigger_ts || 0) || parseDateTime(farm.value.next_trigger_time))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/)
  if (!match) return 0
  const [, year, month, day, hour, minute, second] = match
  return Math.floor(new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second)).getTime() / 1000)
}

function loadDismissedSummaryKey() {
  dismissedSummaryKey.value = typeof window !== 'undefined' && window.sessionStorage
    ? (window.sessionStorage.getItem('vuefarm-dismissed-summary') || '')
    : ''
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) window.sessionStorage.setItem('vuefarm-dismissed-summary', key)
    else window.sessionStorage.removeItem('vuefarm-dismissed-summary')
  }
}

function syncSelectedSeed() {
  if (!unlockedSeeds.value.length) {
    selectedSeedId.value = null
    return
  }
  if (unlockedSeeds.value.some((seed) => Number(seed.id) === Number(selectedSeedId.value))) return
  const preferred = unlockedSeeds.value.find((seed) => seed.preferred)
  selectedSeedId.value = Number((preferred || unlockedSeeds.value[0]).id)
}

watch(seedShop, syncSelectedSeed, { immediate: true, deep: true })
watch(summaryKey, loadDismissedSummaryKey)
watch(inventoryItems, (items) => {
  const active = new Set()
  for (const item of items) {
    const key = String(item.seed_id || item.name)
    active.add(key)
    const current = Number(sellInputs[key])
    sellInputs[key] = current > 0 ? Math.min(current, Number(item.quantity || 1)) : 1
  }
  for (const key of Object.keys(sellInputs)) {
    if (!active.has(key)) delete sellInputs[key]
  }
}, { immediate: true, deep: true })
watch(nextRunTs, (value) => { if (!value || value > nowTs.value) lastRunAutoRefreshTs.value = 0 })
watch(nextTriggerTs, (value) => { if (!value || value > nowTs.value) lastTriggerAutoRefreshTs.value = 0 })

async function loadStatus(showError = true) {
  try {
    Object.assign(status, await props.api.get('/plugin/VueFarm/status') || {})
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  }
}

async function maybeAutoRefreshStatus() {
  if (loading.value) return
  let shouldRefresh = false
  if (nextRunTs.value && nowTs.value >= nextRunTs.value && nextRunTs.value !== lastRunAutoRefreshTs.value) {
    lastRunAutoRefreshTs.value = nextRunTs.value
    shouldRefresh = true
  }
  if (nextTriggerTs.value && nowTs.value >= nextTriggerTs.value && nextTriggerTs.value !== lastTriggerAutoRefreshTs.value) {
    lastTriggerAutoRefreshTs.value = nextTriggerTs.value
    shouldRefresh = true
  }
  if (shouldRefresh) await loadStatus(false)
}

async function refreshData() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/refresh', {})
    flash(res.message || '已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '刷新失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runNow() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/run', {})
    flash(res.message || '执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function syncCookie() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/VueFarm/cookie')
    flash(res.message || 'Cookie 已同步')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    loading.value = false
  }
}

function selectSeed(seed) {
  if (!seed?.unlocked) return
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

function toneRgbByName(name) {
  const text = String(name || '')
  if (text.includes('萝卜')) return '92,164,255'
  if (text.includes('西红柿')) return '255,122,138'
  if (text.includes('玉米')) return '255,191,87'
  if (text.includes('茄子')) return '155,118,255'
  if (text.includes('蘑菇')) return '255,146,176'
  if (text.includes('樱桃')) return '255,102,146'
  return '71,186,128'
}

function cardToneStyle(name) {
  return { '--vf-tone-rgb': toneRgbByName(name) }
}

function slotToneStyle(slot) {
  const state = String(slot?.state || '')
  if (state === 'empty') return { '--vf-slot-rgb': '76,132,255' }
  if (state === 'expand') return { '--vf-slot-rgb': '255,171,64' }
  if (state === 'locked') return { '--vf-slot-rgb': '148,163,184' }
  return { '--vf-slot-rgb': toneRgbByName(slot?.title || slot?.name || '') }
}

function groupReadyCount(group) {
  return (group?.slots || []).filter((slot) => slot.state === 'ready').length
}

function groupEmptyCount(group) {
  return (group?.slots || []).filter((slot) => slot.state === 'empty').length
}

function getSellQuantity(item) {
  const key = inventoryKey(item)
  const current = Number(sellInputs[key])
  return !current || current < 1 ? 1 : Math.min(current, Number(item.quantity || 1))
}

function updateSellQuantity(item, event) {
  const raw = Number(event?.target?.value || 1)
  sellInputs[inventoryKey(item)] = Math.min(Math.max(1, raw || 1), Number(item.quantity || 1))
}

async function plantPlot(slot, seedId) {
  actingSlotKey.value = slotKey(slot)
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/plant-plot', { land_id: slot.land_id, slot_index: slot.slot_index, seed_id: seedId })
    flash(res.message || '种植完成')
    await loadStatus(false)
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
    const res = await props.api.post('/plugin/VueFarm/harvest-plot', { land_id: slot.land_id, slot_index: slot.slot_index })
    flash(res.message || '收菜完成')
    await loadStatus(false)
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
    flash('出售参数无效', 'warning')
    return
  }
  sellingSeedId.value = seedId
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/sell-inventory', { seed_id: seedId, quantity })
    flash(res.message || '出售完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '出售失败', 'error')
  } finally {
    sellingSeedId.value = 0
    loading.value = false
  }
}

async function plantAllEmpty() {
  if (!emptySlots.value.length) return flash('当前没有可种植空地', 'warning')
  if (!selectedSeed.value) return flash('请先选择种子', 'warning')
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/plant-empty', { seed_id: selectedSeed.value.id })
    flash(res.message || '一键种植完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '一键种植失败', 'error')
  } finally {
    loading.value = false
  }
}

async function harvestAllReady() {
  if (!readySlots.value.length) return flash('当前没有可收获田块', 'warning')
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/harvest-all', {})
    flash(res.message || '一键收获完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '一键收获失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleSlotClick(slot) {
  if (loading.value) return
  if (slot.state === 'ready') return harvestPlot(slot)
  if (slot.state === 'empty') {
    if (!selectedSeed.value) return flash('请先在种子商店选择一个种子', 'warning')
    return plantPlot(slot, selectedSeed.value.id)
  }
  if (slot.state === 'growing') return flash(`${slot.title} 还需 ${slot.remaining_label || slot.reward_text || '等待成熟'}`, 'info')
  if (slot.state === 'expand') return flash(`${slot.land_name} 可扩展：${slot.description}`, 'info')
  if (slot.state === 'locked') flash(`${slot.land_name} 这块田暂未解锁`, 'info')
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
  loadDismissedSummaryKey()
  bindThemeObserver()
  await loadStatus()
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    void maybeAutoRefreshStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.vuefarm-page{--panel:rgba(255,255,255,.84);--panel-strong:rgba(255,255,255,.94);--panel-soft:rgba(255,255,255,.72);--text:#24273a;--muted:#757b92;--border:rgba(125,132,170,.2);--shadow:0 20px 48px rgba(17,24,39,.08);--accent:#7c5cff;--accent-soft:rgba(124,92,255,.1);min-height:100%;padding:10px 0 20px;background:transparent;color:var(--text)}
.vuefarm-page.is-dark-theme{--panel:rgba(24,26,37,.82);--panel-strong:rgba(19,21,30,.94);--panel-soft:rgba(34,36,50,.72);--text:#f4f6ff;--muted:#a0a8c5;--border:rgba(124,92,255,.18);--shadow:0 24px 54px rgba(0,0,0,.32);--accent:#8b6cff;--accent-soft:rgba(139,108,255,.16)}
.vuefarm-page,.vuefarm-page *{box-sizing:border-box}
.vuefarm-shell{max-width:1180px;margin:0 auto;padding:0 14px;display:grid;gap:14px}
.vf-card,.vf-bag-card,.vf-group,.vf-history,.vf-list-item{border:1px solid var(--border);border-radius:20px;background:var(--panel);box-shadow:var(--shadow);backdrop-filter:blur(16px)}
.vf-card{padding:16px}
.vf-hero,.vf-head,.vf-group-head,.vf-history-top,.vf-toolbar,.vf-inline,.vf-chip-row,.vf-pill-row{display:flex;gap:10px;flex-wrap:wrap}
.vf-hero{justify-content:space-between;align-items:flex-start;background:radial-gradient(circle at top left,rgba(124,92,255,.18) 0%,transparent 34%),linear-gradient(135deg,var(--accent-soft) 0%,transparent 52%),var(--panel)}
.vf-hero-copy{flex:1;min-width:0}
.vf-badge,.vf-chip,.vf-pill{display:inline-flex;align-items:center;justify-content:center;border-radius:999px}
.vf-badge{padding:6px 12px;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700}
.vf-title{margin:10px 0 2px;font-size:clamp(24px,3.7vw,34px);line-height:1.06;font-weight:900;letter-spacing:-.02em}
.vf-note,.vf-seed-note,.vf-history-lines,.vf-history-top span,.vf-group-sub,.vf-slot-badge,.vf-slot-time,.vf-bag-meta,.vf-seed-meta,.vf-stat-label{color:var(--muted)}
.vf-chip-row{margin-top:10px}
.vf-chip{padding:7px 12px;border:1px solid var(--border);background:var(--panel-strong);color:var(--text);font-size:12px;font-weight:600;justify-content:flex-start}
.vf-action-grid,.vf-stat-grid,.vf-bag-grid,.vf-seed-grid,.vf-list,.vf-group-stack{display:grid;gap:12px}
.vf-action-grid{display:flex;align-items:center;justify-content:flex-end;gap:10px;flex-wrap:nowrap;min-width:min(100%,560px)}
.vf-action-grid :deep(.v-btn){min-height:42px;border-radius:14px;font-weight:800}
.vf-action-grid :deep(.v-btn--variant-flat){min-width:132px}
.vf-action-grid :deep(.v-btn--variant-text){min-width:auto;padding-inline:6px}
.vf-stat-grid{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.vf-stat{position:relative;overflow:hidden;padding:13px 15px;background:linear-gradient(180deg,rgba(255,255,255,.06) 0%,transparent 100%),var(--panel-strong)}
.vf-stat::before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:rgba(124,92,255,.22)}
.vf-stat:nth-child(1)::before{background:rgba(124,92,255,.42)}
.vf-stat:nth-child(2)::before{background:rgba(255,160,67,.42)}
.vf-stat:nth-child(3)::before{background:rgba(76,132,255,.42)}
.vf-stat:nth-child(4)::before{background:rgba(34,197,171,.42)}
.vf-stat:nth-child(5)::before{background:rgba(244,114,182,.42)}
.vf-stat-accent{background:radial-gradient(circle at top left,rgba(124,92,255,.18) 0%,transparent 42%),var(--panel-strong)}
.vf-stat-value{margin-top:9px;font-size:clamp(22px,3vw,30px);font-weight:900;line-height:1}
.vf-pill-row{margin-top:10px}
.vf-pill{min-height:30px;padding:0 12px;font-size:12px;font-weight:700}
.vf-pill.ok{background:rgba(46,185,109,.14);color:#24a15f}
.vf-pill.info{background:rgba(76,132,255,.12);color:#3470e0}
.vf-pill.pri{background:var(--accent-soft);color:var(--accent)}
.vf-grid-2{display:grid;gap:14px;grid-template-columns:minmax(0,.94fr) minmax(0,1.06fr)}
.vf-kicker{color:var(--muted);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.vf-head{justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.vf-head.compact{align-items:center}
.vf-section-title{margin:2px 0 0;font-size:18px;font-weight:900}
.vf-empty{padding:34px 18px;text-align:center;color:var(--muted);border-radius:18px;border:1px dashed var(--border);background:var(--panel-strong)}
.vf-panel{box-shadow:0 18px 38px rgba(17,24,39,.08)}
.vf-panel.green{background:linear-gradient(135deg,rgba(46,185,109,.1) 0%,transparent 42%),var(--panel)}
.vf-panel.amber{background:linear-gradient(135deg,rgba(255,171,64,.12) 0%,transparent 42%),var(--panel)}
.vf-panel.blue{background:linear-gradient(135deg,rgba(76,132,255,.1) 0%,transparent 42%),var(--panel)}
.vf-panel.slate,.vf-summary{background:linear-gradient(135deg,var(--accent-soft) 0%,transparent 42%),var(--panel)}
.vf-list{display:grid;gap:12px}
.vf-list-item,.vf-history{position:relative;overflow:hidden;padding:14px 16px 13px 18px;background:linear-gradient(180deg,rgba(255,255,255,.03) 0%,transparent 100%),var(--panel-strong)}
.vf-list-item::before,.vf-history::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,rgba(124,92,255,.54) 0%,rgba(99,102,241,.18) 100%)}
.vf-bag-grid{grid-template-columns:repeat(auto-fit,minmax(162px,1fr))}
.vf-bag-card{position:relative;overflow:hidden;padding:11px;display:grid;gap:8px;background:linear-gradient(180deg,rgba(var(--vf-tone-rgb,124,92,255),.14) 0%,transparent 58%),var(--panel-strong);border-color:rgba(var(--vf-tone-rgb,124,92,255),.22)}
.vf-bag-card::after{content:'';position:absolute;left:12px;right:12px;bottom:0;height:3px;border-radius:999px 999px 0 0;background:rgba(var(--vf-tone-rgb,124,92,255),.24)}
.vf-bag-top{display:flex;align-items:center;gap:12px}
.vf-bag-icon,.vf-seed-icon,.vf-slot-icon{display:grid;place-items:center;border-radius:16px}
.vf-bag-icon{width:44px;height:44px;font-size:22px;background:rgba(var(--vf-tone-rgb,124,92,255),.15);box-shadow:inset 0 0 0 1px rgba(var(--vf-tone-rgb,124,92,255),.14)}
.vf-bag-name,.vf-seed-name,.vf-slot-name,.vf-group-name{font-weight:800;line-height:1.3}
.vf-bag-line{font-size:12px;color:var(--text);display:flex;gap:6px;flex-wrap:wrap}
.vf-bonus{color:#f59e0b;font-weight:800}
.vf-inline{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.vf-number{width:76px;height:38px;padding:6px 10px;border-radius:12px;border:1px solid var(--border);background:var(--panel);color:var(--text);text-align:center;outline:none}
.vf-btn{border:none;border-radius:12px;padding:9px 14px;font-size:12px;font-weight:800;color:#fff;cursor:pointer}
.vf-btn:disabled,.vf-number:disabled{opacity:.58;cursor:not-allowed}
.vf-btn.warn{background:linear-gradient(180deg,#ffb347 0%,#ff9800 100%)}
.vf-toolbar{margin-bottom:12px}
.vf-seed-grid{grid-template-columns:repeat(auto-fit,minmax(132px,1fr))}
.vf-seed-card{position:relative;overflow:hidden;appearance:none;width:100%;padding:11px 10px;border-radius:18px;border:1px solid rgba(var(--vf-tone-rgb,255,171,64),.22);background:linear-gradient(180deg,rgba(var(--vf-tone-rgb,255,171,64),.12) 0%,transparent 62%),var(--panel-strong);color:inherit;display:grid;gap:5px;justify-items:center;text-align:center;cursor:pointer;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease,opacity .18s ease}
.vf-seed-card.active{border-color:rgba(var(--vf-tone-rgb,46,185,109),.44);box-shadow:0 0 0 2px rgba(var(--vf-tone-rgb,46,185,109),.12),0 14px 26px rgba(17,24,39,.08);transform:translateY(-1px)}
.vf-seed-card.locked{opacity:.52;filter:saturate(.78);cursor:not-allowed}
.vf-seed-icon{width:42px;height:42px;font-size:22px;background:rgba(var(--vf-tone-rgb,255,171,64),.15);box-shadow:inset 0 0 0 1px rgba(var(--vf-tone-rgb,255,171,64),.14)}
.vf-group{padding:11px;background:linear-gradient(180deg,rgba(255,255,255,.03) 0%,transparent 100%),var(--panel-strong)}
.vf-group-head{justify-content:space-between;align-items:center;margin-bottom:10px;padding:10px 12px;border-radius:16px;background:linear-gradient(135deg,rgba(255,255,255,.05) 0%,transparent 100%),rgba(255,255,255,.02);border:1px solid rgba(124,92,255,.1)}
.vf-group-main{display:grid;gap:4px;min-width:0}
.vf-group-name-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.vf-group-name{font-size:16px}
.vf-group-count{display:inline-flex;align-items:center;justify-content:center;padding:4px 8px;border-radius:999px;background:var(--accent-soft);color:var(--accent);font-size:11px;font-weight:800}
.vf-group-pill-row{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.vf-group-pill{display:inline-flex;align-items:center;justify-content:center;min-height:28px;padding:0 10px;border-radius:999px;font-size:11px;font-weight:800}
.vf-group-pill.ready{background:rgba(46,185,109,.12);color:#24a15f}
.vf-group-pill.empty{background:rgba(76,132,255,.12);color:#3470e0}
.vf-slot-grid{display:grid;gap:8px;grid-template-columns:repeat(10,minmax(0,1fr))}
.vf-slot{position:relative;overflow:hidden;appearance:none;width:100%;min-height:98px;padding:8px 7px 7px;border-radius:16px;border:1px solid rgba(var(--vf-slot-rgb,124,92,255),.24);display:flex;flex-direction:column;gap:5px;align-items:center;text-align:center;background:linear-gradient(180deg,rgba(var(--vf-slot-rgb,124,92,255),.14) 0%,transparent 60%),var(--panel);color:inherit;box-shadow:inset 0 1px 0 rgba(255,255,255,.18);transition:transform .18s ease,opacity .18s ease,border-color .18s ease,box-shadow .18s ease}
.vf-slot::before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:rgba(var(--vf-slot-rgb,124,92,255),.46)}
.vf-slot.clickable{cursor:pointer}
.vf-slot.clickable:hover{transform:translateY(-2px);box-shadow:0 14px 28px rgba(17,24,39,.08),inset 0 1px 0 rgba(255,255,255,.18)}
.vf-slot.busy{opacity:.72}
.vf-slot-top{width:100%;display:flex;justify-content:space-between;gap:4px;align-items:center}
.vf-slot-index{font-size:11px;color:var(--muted);font-weight:700}
.vf-slot-badge{padding:3px 8px;border-radius:999px;background:rgba(var(--vf-slot-rgb,124,92,255),.12);font-size:11px;font-weight:700}
.vf-slot-icon{width:32px;height:32px;font-size:18px;background:rgba(var(--vf-slot-rgb,124,92,255),.13);box-shadow:inset 0 0 0 1px rgba(var(--vf-slot-rgb,124,92,255),.14)}
.vuefarm-page.is-dark-theme .vf-slot{box-shadow:inset 0 1px 0 rgba(255,255,255,.05)}
.vuefarm-page.is-dark-theme .vf-slot.clickable:hover{box-shadow:0 18px 34px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.05)}
.vuefarm-page.is-dark-theme .vf-slot-icon{background:rgba(var(--vf-slot-rgb,124,92,255),.16)}
.vf-slot-name{font-size:12px}
.vf-slot-time{margin-top:auto;padding:4px 8px;border-radius:999px;background:rgba(var(--vf-slot-rgb,124,92,255),.12);font-size:10px;font-weight:800;line-height:1.2}
.vf-slot-time:empty{display:none}
.vf-history-top{display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:nowrap;margin-bottom:0}
.vf-history-top strong{flex:1;min-width:0;font-size:14px;line-height:1.45;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vf-history-top span{font-size:12px;white-space:nowrap}
.vf-history-lines{margin-top:8px;font-size:12px;line-height:1.7}
@media (max-width:1280px){.vf-slot-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}
@media (max-width:1024px){.vf-grid-2{grid-template-columns:1fr}}
@media (max-width:920px){.vf-hero,.vf-head,.vf-group-head,.vf-history-top{flex-direction:column;align-items:flex-start}.vf-action-grid{min-width:100%;flex-wrap:wrap;justify-content:flex-start}.vf-group-pill-row{justify-content:flex-start}.vf-history-top strong{white-space:normal}}
@media (max-width:760px){.vuefarm-shell{padding:0 10px}.vf-card,.vf-bag-card,.vf-group,.vf-history,.vf-list-item{border-radius:18px}.vf-card{padding:14px}.vf-slot-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.vf-stat-grid,.vf-bag-grid,.vf-seed-grid{grid-template-columns:1fr}.vf-action-grid :deep(.v-btn--variant-flat){min-width:0;flex:1 1 calc(50% - 10px)}}
@media (max-width:560px){.vf-slot-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.vf-bag-top,.vf-inline{flex-direction:column;align-items:stretch}.vf-number{width:100%}}
</style>
