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
          <div class="sq-meta-chip">Cookie {{ farm.cookie_source || status.cookie_source || '未同步' }}</div>
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

      <section v-if="summaryLines.length" class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">本次摘要</div>
            <h2>任务结果</h2>
          </div>
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
          <article v-for="item in farm.inventory?.items || []" :key="item.name" class="sq-bag-card">
            <div class="sq-bag-icon">{{ item.icon }}</div>
            <div class="sq-bag-name">{{ item.name }}</div>
            <div class="sq-bag-meta">数量 {{ item.quantity }}</div>
            <div class="sq-bag-meta">单价 {{ item.unit_reward }}</div>
            <div class="sq-bag-total">+{{ item.total_reward }} 魔力</div>
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
const rootEl = ref(null)
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const isDarkTheme = ref(false)
const selectedSeedId = ref(null)
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)

let timer = null
let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

const farm = computed(() => status.farm_status || {})
const historyItems = computed(() => status.history || farm.value.history || [])
const summaryLines = computed(() => (farm.value.summary || []).filter(Boolean))
const seedShop = computed(() => farm.value.seed_shop || [])
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
    if (current.getAttribute?.('data-theme')) {
      return current
    }
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme')) {
    return document.body
  }
  if (document.documentElement?.getAttribute('data-theme')) {
    return document.documentElement
  }
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
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] })
  }
  themeObserver.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
  if (document.body) {
    themeObserver.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
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
  emit('close')
}

onMounted(async () => {
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

<style scoped>
.sq-page {
  --sq-bg: linear-gradient(180deg, #f4efe7 0%, #fbfaf7 40%, #f3f5f4 100%);
  --sq-surface: #ffffff;
  --sq-surface-soft: #f8f6f1;
  --sq-panel: rgba(255, 255, 255, 0.92);
  --sq-border: rgba(157, 169, 176, 0.18);
  --sq-shadow: 0 18px 40px rgba(74, 96, 117, 0.08);
  --sq-text: #263238;
  --sq-subtle: #66757f;
  --sq-soft: #8a98a2;
  --sq-accent: #66bb6a;
  --sq-accent-soft: rgba(102, 187, 106, 0.12);
  --sq-ready: linear-gradient(180deg, #ddf8d6 0%, #b5e59e 100%);
  --sq-growing: linear-gradient(180deg, #ffe39a 0%, #f8c64f 100%);
  --sq-empty: linear-gradient(180deg, #eef8ea 0%, #dbf1d3 100%);
  --sq-expand: linear-gradient(180deg, #eef6f0 0%, #deecdf 100%);
  --sq-locked: linear-gradient(180deg, #eff3f6 0%, #e4e9ee 100%);
  min-height: 100%;
  padding: clamp(16px, 2vw, 24px);
  background: var(--sq-bg);
  color: var(--sq-text);
}

.sq-page.is-dark-theme {
  --sq-bg: linear-gradient(180deg, #111616 0%, #151b1a 45%, #101515 100%);
  --sq-surface: #1c2321;
  --sq-surface-soft: #222b29;
  --sq-panel: rgba(24, 31, 30, 0.92);
  --sq-border: rgba(124, 148, 133, 0.22);
  --sq-shadow: 0 18px 42px rgba(0, 0, 0, 0.3);
  --sq-text: #edf3f0;
  --sq-subtle: #b7c5bd;
  --sq-soft: #8fa096;
  --sq-accent: #9bd48a;
  --sq-accent-soft: rgba(120, 187, 110, 0.18);
  --sq-ready: linear-gradient(180deg, #49754c 0%, #5a9a63 100%);
  --sq-growing: linear-gradient(180deg, #8f6b2c 0%, #b18632 100%);
  --sq-empty: linear-gradient(180deg, #304a35 0%, #36553d 100%);
  --sq-expand: linear-gradient(180deg, #31433a 0%, #395047 100%);
  --sq-locked: linear-gradient(180deg, #333d42 0%, #3f4b52 100%);
}

.sq-shell {
  max-width: 1320px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sq-hero,
.sq-panel,
.sq-stat-card,
.sq-land-group {
  border: 1px solid var(--sq-border);
  box-shadow: var(--sq-shadow);
}

.sq-hero {
  padding: 24px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(115, 200, 111, 0.18), transparent 28%),
    radial-gradient(circle at bottom left, rgba(255, 193, 7, 0.14), transparent 26%),
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
  font-size: clamp(28px, 4vw, 38px);
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
  min-height: 38px;
  padding: 0 14px;
  border-radius: 16px;
  background: var(--sq-surface-soft);
  color: var(--sq-subtle);
  border: 1px solid var(--sq-border);
  font-size: 13px;
  font-weight: 600;
}

.sq-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.sq-stat-card {
  border-radius: 22px;
  padding: 18px;
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
  padding: 20px;
  border-radius: 24px;
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
  font-size: 24px;
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
  padding: 14px 16px;
  border-radius: 18px;
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
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.sq-seed-grid {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

.sq-bag-card,
.sq-seed-card {
  padding: 16px 14px;
  border-radius: 18px;
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
.sq-bag-total,
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

.sq-bag-total {
  margin-top: 8px;
  color: #e39a2c;
  font-weight: 800;
}

.sq-farm-panel {
  padding: 16px;
}

.sq-land-group {
  padding: 12px;
  border-radius: 20px;
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
  gap: 10px;
}

.sq-slot {
  appearance: none;
  width: 100%;
  min-height: 132px;
  padding: 10px 8px 12px;
  border-radius: 18px;
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
