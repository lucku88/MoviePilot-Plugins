<template>
  <div class="sqfarm-page">
    <div class="sqfarm-shell">
      <v-card class="sqfarm-card sqfarm-hero" rounded="xl" flat>
        <v-card-text class="sqfarm-hero__body">
          <div class="sqfarm-hero__header">
            <div class="sqfarm-hero__copy">
              <div class="sqfarm-badge">Vue-农场</div>
              <h1 class="sqfarm-title">{{ farm.title || '种菜赚魔力' }}</h1>
              <p class="sqfarm-subtitle">
                最近执行 {{ status.last_run || '暂无' }} · 下次可收 {{ farm.next_run_time || '待识别' }}
              </p>
            </div>
            <div class="sqfarm-actions">
              <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
              <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
              <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
              <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
              <v-btn variant="text" @click="closePlugin">关闭</v-btn>
            </div>
          </div>

          <div class="sqfarm-chip-row">
            <div class="sqfarm-chip">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待下一次运行' }}</div>
            <div class="sqfarm-chip">站点同步 {{ farm.cookie_source || status.cookie_source || '未同步' }}</div>
            <div class="sqfarm-chip">成熟 {{ readySlots.length }} 块</div>
            <div class="sqfarm-chip">空地 {{ emptySlots.length }} 块</div>
          </div>
        </v-card-text>
      </v-card>

      <v-alert
        v-if="message.text"
        :type="message.type"
        variant="tonal"
        rounded="xl"
        class="sqfarm-alert"
      >
        {{ message.text }}
      </v-alert>

      <v-row class="sqfarm-stat-row" dense>
        <v-col
          v-for="item in farm.overview || []"
          :key="item.label"
          cols="12"
          sm="6"
          lg="3"
        >
          <v-card class="sqfarm-card sqfarm-stat-card" rounded="xl" flat>
            <v-card-text>
              <div class="sqfarm-stat-label">{{ item.label }}</div>
              <div class="sqfarm-stat-value">{{ item.value }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-card v-if="showSummary" class="sqfarm-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-section-kicker">本次摘要</div>
          </template>
          <v-card-title>任务结果</v-card-title>
          <template #append>
            <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
          </template>
        </v-card-item>
        <v-card-text>
          <div class="sqfarm-summary-list">
            <div v-for="line in summaryLines" :key="line" class="sqfarm-summary-line">
              {{ line }}
            </div>
          </div>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-section-kicker">收获背包</div>
          </template>
          <v-card-title>当前库存</v-card-title>
        </v-card-item>
        <v-card-text>
          <div v-if="farm.inventory?.empty" class="sqfarm-empty">
            {{ farm.inventory?.empty_text }}
          </div>
          <div v-else class="sqfarm-bag-grid">
            <article v-for="item in inventoryItems" :key="item.seed_id || item.name" class="sqfarm-bag-card">
              <div class="sqfarm-bag-icon">{{ item.icon }}</div>
              <div class="sqfarm-bag-name">{{ item.name }}</div>
              <div class="sqfarm-bag-meta">数量 {{ item.quantity }}</div>
              <div class="sqfarm-bag-meta">
                售：{{ item.unit_reward }} 魔力/份
                <span class="sqfarm-bag-bonus">+{{ item.sell_bonus_percent || 0 }}%</span>
              </div>
              <div class="sqfarm-inline-actions">
                <input
                  class="sqfarm-number"
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
                  class="sqfarm-action-btn is-warning"
                  :disabled="loading || !item.quantity || sellingSeedId === item.seed_id"
                  @click.stop="sellInventory(item)"
                >
                  {{ sellingSeedId === item.seed_id ? '出售中' : '出售' }}
                </button>
              </div>
            </article>
          </div>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-section-kicker">种子商店</div>
          </template>
          <v-card-title>选择种子后点击空地种植</v-card-title>
        </v-card-item>
        <v-card-text>
          <div class="sqfarm-toolbar">
            <div class="sqfarm-chip">
              当前种子：
              <strong v-if="selectedSeed">{{ selectedSeed.icon }} {{ selectedSeed.name }}</strong>
              <strong v-else>未选择</strong>
            </div>
            <div class="sqfarm-actions">
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

          <div class="sqfarm-seed-grid">
            <button
              v-for="seed in farm.seed_shop || []"
              :key="seed.id"
              type="button"
              class="sqfarm-seed-card"
              :class="{
                'is-locked': !seed.unlocked,
                'is-selected': selectedSeed && Number(selectedSeed.id) === Number(seed.id),
              }"
              :disabled="!seed.unlocked || loading"
              @click="selectSeed(seed)"
            >
              <div class="sqfarm-seed-icon">{{ seed.icon }}</div>
              <div class="sqfarm-seed-name">{{ seed.name }}</div>
              <div class="sqfarm-seed-line">消耗 {{ seed.cost }}</div>
              <div class="sqfarm-seed-line">生长 {{ seed.grow_text }}</div>
              <div class="sqfarm-seed-note">
                {{ seed.unlocked ? (selectedSeed && Number(selectedSeed.id) === Number(seed.id) ? '已选中' : '点击选择') : seed.unlock_text }}
              </div>
            </button>
          </div>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-section-kicker">农场坑位</div>
          </template>
          <v-card-title>分组状态</v-card-title>
        </v-card-item>
        <v-card-text class="sqfarm-land-stack">
          <article v-for="group in farm.land_groups || []" :key="group.id" class="sqfarm-group-card">
            <header class="sqfarm-group-head">
              <div class="sqfarm-group-name">{{ group.name }}</div>
              <div class="sqfarm-group-subtitle">{{ group.subtitle }}</div>
            </header>
            <div class="sqfarm-slot-grid">
              <button
                v-for="slot in group.slots"
                :key="`${group.id}-${slot.slot_index}`"
                type="button"
                class="sqfarm-slot"
                :class="[
                  `is-${slot.state}`,
                  { 'is-clickable': isInteractiveSlot(slot), 'is-busy': actingSlotKey === slotKey(slot) }
                ]"
                :disabled="loading || actingSlotKey === slotKey(slot)"
                @click="handleSlotClick(slot)"
              >
                <div class="sqfarm-slot-top">
                  <span class="sqfarm-slot-index">#{{ slot.slot_index }}</span>
                  <span class="sqfarm-slot-badge">{{ slot.badge }}</span>
                </div>
                <div class="sqfarm-slot-icon">{{ slot.icon }}</div>
                <div class="sqfarm-slot-name">{{ slot.title }}</div>
                <div class="sqfarm-slot-time">{{ slotText(slot) }}</div>
              </button>
            </div>
          </article>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-section-kicker">最近记录</div>
          </template>
          <v-card-title>执行历史</v-card-title>
        </v-card-item>
        <v-card-text>
          <div v-if="!historyItems.length" class="sqfarm-empty">暂无执行记录</div>
          <div v-else class="sqfarm-history-list">
            <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="sqfarm-history-item">
              <div class="sqfarm-history-top">
                <strong>{{ item.title }}</strong>
                <span>{{ item.time }}</span>
              </div>
              <div class="sqfarm-history-lines">{{ (item.lines || []).join(' / ') }}</div>
            </article>
          </div>
        </v-card-text>
      </v-card>
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
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const selectedSeedId = ref(null)
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)
const sellInputs = reactive({})
const dismissedSummaryKey = ref('')

let timer = null

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

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = ''
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('vuefarm-dismissed-summary') || ''
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('vuefarm-dismissed-summary', key)
    } else {
      window.sessionStorage.removeItem('vuefarm-dismissed-summary')
    }
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
watch(summaryKey, () => loadDismissedSummaryKey())
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
  if (!value || value > nowTs.value) lastRunAutoRefreshTs.value = 0
})
watch(nextTriggerTs, (value) => {
  if (!value || value > nowTs.value) lastTriggerAutoRefreshTs.value = 0
})

async function loadStatus() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/VueFarm/status')
    Object.assign(status, res || {})
  } catch (error) {
    flash(error?.message || '加载状态失败', 'error')
  } finally {
    loading.value = false
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
  if (shouldRefresh) {
    await loadStatus()
  }
}

async function refreshData() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/refresh', {})
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
    const res = await props.api.post('/plugin/VueFarm/run', {})
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
    const res = await props.api.get('/plugin/VueFarm/cookie')
    flash(res.message || 'Cookie 已同步')
    await loadStatus()
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

function getSellQuantity(item) {
  const key = inventoryKey(item)
  const current = Number(sellInputs[key])
  if (!current || current < 1) return 1
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
    const res = await props.api.post('/plugin/VueFarm/plant-plot', {
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
    const res = await props.api.post('/plugin/VueFarm/harvest-plot', {
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
    flash('出售参数无效', 'warning')
    return
  }
  sellingSeedId.value = seedId
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/sell-inventory', {
      seed_id: seedId,
      quantity,
    })
    flash(res.message || '出售完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '出售失败', 'error')
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
    const res = await props.api.post('/plugin/VueFarm/plant-empty', {
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
    const res = await props.api.post('/plugin/VueFarm/harvest-all', {})
    flash(res.message || '一键收获完成')
    await loadStatus()
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
    if (!selectedSeed.value) {
      flash('请先在种子商店选择一个种子', 'warning')
      return
    }
    return plantPlot(slot, selectedSeed.value.id)
  }
  if (slot.state === 'growing') {
    flash(`${slot.title} 还需 ${slot.remaining_label || slot.reward_text || '等待成熟'}`, 'info')
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
  if (showSummary.value) dismissSummary()
  emit('close')
}

onMounted(async () => {
  loadDismissedSummaryKey()
  await loadStatus()
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    void maybeAutoRefreshStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.sqfarm-page {
  min-height: 100%;
  padding: 20px;
  color: rgb(var(--v-theme-on-surface));
  background:
    radial-gradient(circle at top right, rgb(var(--v-theme-primary) / 0.08), transparent 26%),
    radial-gradient(circle at bottom left, rgb(var(--v-theme-warning) / 0.08), transparent 24%);
}

.sqfarm-shell {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sqfarm-card {
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  background: rgb(var(--v-theme-surface) / 0.88) !important;
  backdrop-filter: blur(14px);
  box-shadow: 0 18px 40px rgb(15 23 42 / 0.08);
}

.sqfarm-hero__body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sqfarm-hero__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.sqfarm-badge,
.sqfarm-chip {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  background: rgb(var(--v-theme-surface-bright) / 0.7);
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 13px;
  font-weight: 600;
}

.sqfarm-badge {
  background: rgb(var(--v-theme-primary) / 0.12);
  color: rgb(var(--v-theme-primary));
  font-weight: 700;
}

.sqfarm-title {
  margin: 14px 0 8px;
  font-size: clamp(34px, 4vw, 42px);
  line-height: 1.05;
  font-weight: 900;
}

.sqfarm-subtitle {
  margin: 0;
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 15px;
  line-height: 1.7;
}

.sqfarm-actions,
.sqfarm-chip-row,
.sqfarm-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.sqfarm-actions {
  justify-content: flex-end;
}

.sqfarm-stat-row {
  margin: 0 -6px;
}

.sqfarm-stat-label {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 13px;
}

.sqfarm-stat-value {
  margin-top: 8px;
  font-size: clamp(26px, 3vw, 34px);
  font-weight: 900;
}

.sqfarm-section-kicker {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sqfarm-summary-list,
.sqfarm-history-list,
.sqfarm-land-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sqfarm-summary-line,
.sqfarm-history-item {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.06);
  background: rgb(var(--v-theme-surface-bright) / 0.78);
}

.sqfarm-empty {
  padding: 36px 18px;
  text-align: center;
  color: rgb(var(--v-theme-on-surface-variant));
  border-radius: 18px;
  background: rgb(var(--v-theme-surface-bright) / 0.72);
}

.sqfarm-bag-grid,
.sqfarm-seed-grid {
  display: grid;
  gap: 12px;
}

.sqfarm-bag-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

.sqfarm-seed-grid {
  margin-top: 16px;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.sqfarm-bag-card,
.sqfarm-seed-card,
.sqfarm-group-card {
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  border-radius: 18px;
  background: rgb(var(--v-theme-surface-bright) / 0.72);
}

.sqfarm-bag-card,
.sqfarm-seed-card {
  padding: 16px 14px;
  text-align: center;
}

.sqfarm-seed-card {
  appearance: none;
  width: 100%;
  cursor: pointer;
  color: inherit;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.sqfarm-seed-card:hover:not(:disabled),
.sqfarm-slot.is-clickable:hover:not(:disabled) {
  transform: translateY(-1px);
}

.sqfarm-seed-card.is-selected {
  border-color: rgb(var(--v-theme-success) / 0.55);
  box-shadow: 0 0 0 2px rgb(var(--v-theme-success) / 0.14);
}

.sqfarm-seed-card.is-locked {
  opacity: 0.52;
  cursor: not-allowed;
}

.sqfarm-bag-icon,
.sqfarm-seed-icon {
  font-size: 28px;
}

.sqfarm-bag-name,
.sqfarm-seed-name {
  margin-top: 8px;
  font-weight: 800;
}

.sqfarm-bag-meta,
.sqfarm-seed-line,
.sqfarm-seed-note,
.sqfarm-slot-badge,
.sqfarm-slot-time,
.sqfarm-group-subtitle,
.sqfarm-history-top span,
.sqfarm-history-lines {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 12px;
}

.sqfarm-bag-bonus {
  margin-left: 4px;
  color: rgb(var(--v-theme-warning));
  font-weight: 800;
}

.sqfarm-inline-actions {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.sqfarm-number {
  width: 68px;
  height: 34px;
  padding: 4px 8px;
  border-radius: 10px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.12);
  background: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
  text-align: center;
  outline: none;
}

.sqfarm-action-btn {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 800;
  color: #fff;
  cursor: pointer;
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.sqfarm-action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.sqfarm-action-btn:disabled,
.sqfarm-number:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.sqfarm-action-btn.is-warning {
  background: linear-gradient(180deg, #ffb341 0%, #ff9800 100%);
}

.sqfarm-land-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sqfarm-group-card {
  padding: 12px;
}

.sqfarm-group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.sqfarm-group-name {
  font-size: 20px;
  font-weight: 800;
}

.sqfarm-slot-grid {
  display: grid;
  grid-template-columns: repeat(10, minmax(0, 1fr));
  gap: 8px;
}

.sqfarm-slot {
  appearance: none;
  width: 100%;
  min-height: 126px;
  padding: 10px 8px;
  border-radius: 16px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: flex-start;
  text-align: center;
  color: inherit;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.sqfarm-slot.is-clickable {
  cursor: pointer;
}

.sqfarm-slot.is-busy {
  opacity: 0.72;
}

.sqfarm-slot.is-growing { background: rgb(var(--v-theme-warning) / 0.22); }
.sqfarm-slot.is-ready { background: rgb(var(--v-theme-success) / 0.22); }
.sqfarm-slot.is-empty { background: rgb(var(--v-theme-info) / 0.14); }
.sqfarm-slot.is-expand { background: rgb(var(--v-theme-on-surface) / 0.06); }
.sqfarm-slot.is-locked { background: rgb(var(--v-theme-on-surface) / 0.08); }

.sqfarm-slot-top {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
}

.sqfarm-slot-index {
  font-size: 11px;
  color: rgb(var(--v-theme-on-surface-variant));
  font-weight: 700;
}

.sqfarm-slot-badge {
  font-weight: 700;
}

.sqfarm-slot-icon {
  font-size: 28px;
  line-height: 1;
}

.sqfarm-slot-name {
  font-size: 14px;
  font-weight: 800;
  line-height: 1.2;
}

.sqfarm-slot-time {
  margin-top: auto;
  font-weight: 800;
  color: rgb(var(--v-theme-on-surface));
}

.sqfarm-history-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

@media (max-width: 1280px) {
  .sqfarm-slot-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}

@media (max-width: 980px) {
  .sqfarm-page {
    padding: 16px;
  }

  .sqfarm-hero__header,
  .sqfarm-group-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .sqfarm-actions {
    justify-content: flex-start;
  }

  .sqfarm-slot-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .sqfarm-slot-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
