<template>
  <div ref="rootEl" class="siqi-farm-page" :class="{ 'is-dark': isDarkTheme }">
    <v-snackbar v-model="notice.show" :color="notice.type" location="top" timeout="3200">
      {{ notice.text }}
    </v-snackbar>

    <v-dialog v-model="stealDialog" max-width="1040" scrollable persistent>
      <v-card class="siqi-dialog">
        <div class="dialog-head">
          <div class="dialog-avatar steal">🥷</div>
          <div class="dialog-copy">
            <div class="dialog-title">{{ stealTarget.victim_desc_name || stealTarget.victim_name || '随机偷菜' }}</div>
            <div class="dialog-subtitle">
              随机访问农场，点击成熟作物进行偷菜。自动任务会按配置的作物和人数执行。
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" :disabled="stealLoading" @click="closeStealDialog" />
        </div>

        <v-card-text class="dialog-body">
          <div class="dialog-toolbar">
            <v-select
              v-model="manualStealCrop"
              :items="stealCropOptions"
              label="只显示这种作物"
              density="compact"
              variant="outlined"
              hide-details
              class="dialog-select"
            />
            <div class="dialog-chips">
              <span class="mini-chip">已偷 {{ stolenCount }}</span>
              <span class="mini-chip">收益 {{ stolenReward }} 魔力</span>
              <span v-if="stealMax > 0" class="mini-chip">今日剩余 {{ stealRemaining }}/{{ stealMax }}</span>
            </div>
            <v-btn color="red" variant="tonal" :loading="stealLoading" :disabled="stolenCount > 0" @click="loadStealTarget">
              换一个农场
            </v-btn>
          </div>

          <div v-if="stealLoading && !stealLandGroups.length" class="dialog-empty">正在寻找可访问农场...</div>
          <div v-else-if="!stealLandGroups.length" class="dialog-empty">当前没有可展示的农场</div>
          <div v-else class="steal-land-list">
            <section v-for="land in stealLandGroups" :key="land.id" class="steal-land">
              <div class="steal-land-head">
                <strong>{{ land.name || `农场 ${land.id}` }}</strong>
                <span>坑位 {{ stealPlotsForLand(land).length }}</span>
              </div>
              <div v-if="land.unlocked !== undefined && !Number(land.unlocked)" class="dialog-empty compact">该农场尚未解锁</div>
              <div v-else class="steal-plot-grid">
                <button
                  v-for="plot in stealPlotsForLand(land)"
                  :key="`${land.id}-${plot.plot_index}`"
                  type="button"
                  class="steal-plot"
                  :class="stealPlotClass(plot)"
                  :disabled="!isStealablePlot(plot) || stealLoading || stealRemaining <= 0"
                  @click="stealPlotAction(land, plot)"
                >
                  <span class="plot-index">#{{ Number(plot.plot_index || 0) + 1 }}</span>
                  <span class="plot-icon">{{ cropIcon(targetSeedName(plot)) }}</span>
                  <strong>{{ targetSeedName(plot) || '空地' }}</strong>
                  <small>{{ stealPlotText(plot) }}</small>
                </button>
              </div>
            </section>
          </div>
        </v-card-text>

        <v-card-actions class="dialog-actions">
          <v-btn variant="text" :disabled="stealLoading" @click="closeStealDialog">关闭</v-btn>
          <v-btn color="success" variant="flat" :loading="stealLoading" :disabled="stolenCount <= 0" @click="finishStealing(true)">
            完成偷菜
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="likeDialog" max-width="660" persistent>
      <v-card class="siqi-dialog">
        <div class="dialog-head">
          <div class="dialog-avatar like">👍</div>
          <div class="dialog-copy">
            <div class="dialog-title">一键点赞</div>
            <div class="dialog-subtitle">随机填充用户名，也可以自己修改名单，再按顺序批量点赞。</div>
          </div>
          <v-btn icon="mdi-close" variant="text" :disabled="likeLoading" @click="likeDialog = false" />
        </div>
        <v-card-text class="dialog-body">
          <v-textarea
            v-model="likeUsernames"
            label="点赞用户名"
            placeholder="每行一个用户名，也支持逗号分隔"
            rows="6"
            auto-grow
            variant="outlined"
            hide-details="auto"
          />
          <div class="like-hint">自动点赞每天最多执行一轮；没有目标时当天不会反复请求。</div>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-btn color="primary" variant="tonal" :loading="likeLoading" @click="loadLikeTargets">随机填充</v-btn>
          <v-spacer />
          <v-btn variant="text" :disabled="likeLoading" @click="likeDialog = false">关闭</v-btn>
          <v-btn color="pink" variant="flat" :loading="likeLoading" :disabled="!likeUsernames.trim()" @click="submitLikeBatch">一键点赞</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="siqi-shell">
      <header class="siqi-topbar">
        <div class="topbar-left">
          <div class="topbar-mark">🌱</div>
          <div>
            <h1>Vue-农场</h1>
            <p>动态收菜、自动补种、背包出售与农场互动</p>
          </div>
        </div>
        <div class="topbar-actions">
          <v-btn icon="mdi-refresh" variant="text" :loading="loading" title="刷新农场" @click="refreshData" />
          <v-btn icon="mdi-cog-outline" variant="text" title="打开配置" @click="emit('switch', 'config')" />
          <v-btn icon="mdi-close" variant="text" title="关闭" @click="emit('close')" />
        </div>
      </header>

      <section class="siqi-card hero-card">
        <div class="hero-copy">
          <div class="eyebrow">动态智能调度</div>
          <h2>最近收菜 {{ farm.next_run_time || '待识别' }}</h2>
          <p>插件按每块田的真实成熟时间运行，并在成熟时间后延迟 {{ Number(config.schedule_buffer_seconds || 5) }} 秒执行，避免卡在临界一秒。</p>
          <div class="status-row">
            <span class="status-chip" :class="status.enabled ? 'ok' : 'muted'">{{ status.enabled ? '插件已启用' : '插件未启用' }}</span>
            <span class="status-chip">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待识别' }}</span>
            <span class="status-chip">Cookie {{ farm.cookie_source || status.cookie_source || '未识别' }}</span>
          </div>
        </div>
        <div class="hero-actions">
          <v-btn color="primary" variant="tonal" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="orange" variant="flat" :disabled="!readySlots.length || loading" @click="harvestAllReady">一键收获</v-btn>
          <v-btn color="green" variant="flat" :disabled="!selectedSeed || !emptySlots.length || loading" @click="plantAllEmpty">一键种植</v-btn>
        </div>
      </section>

      <section class="stat-grid">
        <article v-for="item in farm.overview || []" :key="item.label" class="stat-card" :class="item.accent">
          <span>{{ overviewIcon(item.label) }}</span>
          <div>
            <small>{{ item.label }}</small>
            <strong>{{ formatNumber(item.value) }}</strong>
          </div>
        </article>
      </section>

      <section class="siqi-card interact-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">农场互动</div>
            <h2>偷菜与点赞</h2>
          </div>
          <span class="section-note">自动偷菜：每个设置时段只执行一轮</span>
        </div>
        <div class="interact-grid">
          <article class="action-card steal-action">
            <div class="action-icon">🥷</div>
            <div class="action-copy">
              <strong>偷菜</strong>
              <span>目标 {{ config.steal_crop || '全部作物' }}，每轮随机访问 {{ config.steal_visit_count || 5 }} 位不同用户</span>
              <small>{{ stealDoneToday ? '今天可偷次数已经用完' : (config.steal_time_windows || '全天执行一轮') }}</small>
            </div>
            <div class="action-buttons">
              <v-btn color="red" variant="tonal" :loading="socialAction === 'steal'" @click="runAutoSteal">按配置偷菜</v-btn>
              <v-btn color="red" variant="flat" @click="openStealDialog">选择坑位</v-btn>
            </div>
          </article>
          <article class="action-card like-action">
            <div class="action-icon">👍</div>
            <div class="action-copy">
              <strong>农场点赞</strong>
              <span>随机获取可点赞用户名并批量完成，每天自动执行一轮</span>
              <small>{{ likeDoneToday ? '今天已完成或已检查' : '今天尚未执行' }}</small>
            </div>
            <div class="action-buttons">
              <v-btn color="pink" variant="tonal" :loading="socialAction === 'like'" @click="runAutoLike">随机点赞</v-btn>
              <v-btn color="pink" variant="flat" @click="openLikeDialog">编辑名单</v-btn>
            </div>
          </article>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">种植策略</div>
            <h2>种子商店</h2>
          </div>
          <span class="section-note">当前选择：{{ selectedSeed ? `${selectedSeed.icon}${selectedSeed.name}` : '暂无可用种子' }}</span>
        </div>
        <div class="seed-grid">
          <button
            v-for="seed in seedShop"
            :key="seed.id"
            type="button"
            class="seed-card"
            :class="{ active: selectedSeed && Number(selectedSeed.id) === Number(seed.id), locked: !seed.unlocked }"
            :disabled="!seed.unlocked || loading"
            @click="selectSeed(seed)"
          >
            <span class="seed-icon">{{ seed.icon }}</span>
            <strong>{{ seed.name }}</strong>
            <small>消耗 {{ formatNumber(seed.cost) }} · 收获 {{ formatNumber(seed.reward) }}</small>
            <small>{{ seed.grow_text }}</small>
            <em>{{ seed.unlocked ? (seed.preferred ? '配置优先种子' : '点击选择') : seed.unlock_text }}</em>
          </button>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">田地管理</div>
            <h2>农场坑位</h2>
          </div>
          <div class="summary-chips">
            <span>成熟 {{ readySlots.length }}</span>
            <span>空地 {{ emptySlots.length }}</span>
          </div>
        </div>
        <div class="land-list">
          <article v-for="group in farm.land_groups || []" :key="group.id" class="land-card">
            <div class="land-head">
              <div>
                <strong>{{ group.name }}</strong>
                <small>{{ group.subtitle }}</small>
              </div>
              <span>{{ groupReadyCount(group) }} 可收 · {{ groupEmptyCount(group) }} 空地</span>
            </div>
            <div class="plot-grid">
              <button
                v-for="slot in group.slots || []"
                :key="`${group.id}-${slot.slot_index}`"
                type="button"
                class="farm-plot"
                :class="[slot.state, { clickable: isInteractiveSlot(slot), busy: actingSlotKey === slotKey(slot) }]"
                :disabled="loading || actingSlotKey === slotKey(slot)"
                @click="handleSlotClick(slot)"
              >
                <span class="plot-index">#{{ slot.slot_index }}</span>
                <span class="plot-icon">{{ slot.icon }}</span>
                <strong>{{ slot.title }}</strong>
                <small>{{ slotText(slot) }}</small>
                <em>{{ slot.badge }}</em>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">收获背包</div>
            <h2>库存与出售</h2>
          </div>
          <v-btn color="orange" variant="tonal" :loading="sellingAll" :disabled="!inventoryItems.length || loading" @click="sellAllInventory">一键出售</v-btn>
        </div>
        <div v-if="!inventoryItems.length" class="empty-state">背包空空如也，成熟作物收获后会出现在这里。</div>
        <div v-else class="inventory-grid">
          <article v-for="item in inventoryItems" :key="item.seed_id || item.name" class="inventory-card">
            <span class="inventory-icon">{{ item.icon }}</span>
            <div class="inventory-copy">
              <strong>{{ item.name }}</strong>
              <small>库存 {{ item.quantity }} · 单价 {{ item.unit_reward }} 魔力</small>
            </div>
            <div class="inventory-actions">
              <input :value="getSellQuantity(item)" type="number" min="1" :max="item.quantity" @input="updateSellQuantity(item, $event)" />
              <v-btn color="orange" size="small" variant="tonal" :loading="sellingSeedId === Number(item.seed_id)" @click="sellInventory(item)">出售</v-btn>
            </div>
          </article>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">运行记录</div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="empty-state">暂无执行记录</div>
        <div v-else class="history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`">
            <span>{{ historySummary(item) }}</span>
            <time>{{ item.time }}</time>
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
const socialAction = ref('')
const actingSlotKey = ref('')
const sellingSeedId = ref(0)
const sellingAll = ref(false)
const selectedSeedId = ref(null)
const status = reactive({ farm_status: {}, history: [], config: {} })
const notice = reactive({ show: false, text: '', type: 'success' })
const sellInputs = reactive({})
const nowTs = ref(Math.floor(Date.now() / 1000))
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)

const stealDialog = ref(false)
const stealLoading = ref(false)
const stealTarget = reactive({})
const stolenCount = ref(0)
const stolenReward = ref(0)
const manualStealCrop = ref('全部作物')

const likeDialog = ref(false)
const likeLoading = ref(false)
const likeUsernames = ref('')

let timer = null
let themeObserver = null
let mediaQuery = null

const farm = computed(() => status.farm_status || {})
const config = computed(() => status.config || props.initialConfig || {})
const historyItems = computed(() => status.history || farm.value.history || [])
const seedShop = computed(() => farm.value.seed_shop || [])
const unlockedSeeds = computed(() => seedShop.value.filter((seed) => seed.unlocked))
const selectedSeed = computed(() => seedShop.value.find((seed) => Number(seed.id) === Number(selectedSeedId.value)) || null)
const inventoryItems = computed(() => farm.value.inventory?.items || [])
const allSlots = computed(() => (farm.value.land_groups || []).flatMap((group) => group.slots || []))
const readySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'ready'))
const emptySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'empty'))
const nextRunTs = computed(() => Number(farm.value.next_run_ts || 0) || parseDateTime(farm.value.next_run_time))
const nextTriggerTs = computed(() => Number(farm.value.next_trigger_ts || 0) || parseDateTime(farm.value.next_trigger_time))
const stealDoneToday = computed(() => Boolean(farm.value.social?.steal_done_today))
const likeDoneToday = computed(() => Boolean(farm.value.social?.like_done_today))
const stealCropOptions = computed(() => ['全部作物', ...seedShop.value.map((seed) => seed.name).filter(Boolean)])
const targetSeedMap = computed(() => Object.fromEntries((stealTarget.seeds || []).map((seed) => [String(seed.id), seed])))
const stealLandGroups = computed(() => {
  const lands = Array.isArray(stealTarget.victim_lands) ? stealTarget.victim_lands : []
  if (lands.length) return lands
  const ids = [...new Set((stealTarget.victim_plots || []).map((plot) => Number(plot.land_id || 0)).filter(Boolean))]
  return ids.map((id) => ({ id, name: `农场 ${id}`, unlocked: 1 }))
})
const stealMax = computed(() => Number(stealTarget.max_steal_count || 0))
const stealRemaining = computed(() => {
  if (!stealMax.value) return 999
  return Math.max(0, stealMax.value - Number(stealTarget.steal_count_today || 0) - stolenCount.value)
})

function flash(text, type = 'success') {
  notice.text = text
  notice.type = type
  notice.show = true
}

function formatNumber(value) {
  const number = Number(value || 0)
  return Number.isFinite(number) ? number.toLocaleString('zh-CN') : value
}

function overviewIcon(label) {
  if (String(label).includes('魔力')) return '🪄'
  if (String(label).includes('种植')) return '🌾'
  if (String(label).includes('偷菜')) return '🥷'
  if (String(label).includes('点赞')) return '👍'
  return '🌱'
}

function cropIcon(name) {
  const text = String(name || '')
  if (text.includes('萝卜')) return '🥕'
  if (text.includes('西红柿')) return '🍅'
  if (text.includes('玉米')) return '🌽'
  if (text.includes('茄子')) return '🍆'
  if (text.includes('蘑菇')) return '🍄'
  if (text.includes('樱桃')) return '🍒'
  return '🌱'
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/)
  if (!match) return 0
  const [, year, month, day, hour, minute, second] = match
  return Math.floor(new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second)).getTime() / 1000)
}

function syncSelectedSeed() {
  if (!unlockedSeeds.value.length) return (selectedSeedId.value = null)
  if (unlockedSeeds.value.some((seed) => Number(seed.id) === Number(selectedSeedId.value))) return
  const preferred = unlockedSeeds.value.find((seed) => seed.preferred)
  selectedSeedId.value = Number((preferred || unlockedSeeds.value[0]).id)
}

watch(seedShop, syncSelectedSeed, { immediate: true, deep: true })
watch(inventoryItems, (items) => {
  const active = new Set()
  for (const item of items) {
    const key = String(item.seed_id || item.name)
    active.add(key)
    const current = Number(sellInputs[key])
    sellInputs[key] = current > 0 ? Math.min(current, Number(item.quantity || 1)) : 1
  }
  for (const key of Object.keys(sellInputs)) if (!active.has(key)) delete sellInputs[key]
}, { immediate: true, deep: true })
watch(nextRunTs, (value) => { if (!value || value > nowTs.value) lastRunAutoRefreshTs.value = 0 })
watch(nextTriggerTs, (value) => { if (!value || value > nowTs.value) lastTriggerAutoRefreshTs.value = 0 })

async function loadStatus(showError = true) {
  try {
    Object.assign(status, await props.api.get('/plugin/VueFarm/status') || {})
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载农场状态失败', 'error')
    return false
  }
}

async function refreshData() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/refresh', {})
    flash(res.message || '农场数据已刷新')
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
    flash(res.message || '执行完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runAutoSteal() {
  socialAction.value = 'steal'
  try {
    const res = await props.api.post('/plugin/VueFarm/steal', {})
    flash(res.message || '偷菜任务完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '偷菜失败', 'error')
  } finally {
    socialAction.value = ''
  }
}

async function runAutoLike() {
  socialAction.value = 'like'
  try {
    const res = await props.api.post('/plugin/VueFarm/like', {})
    flash(res.message || '点赞任务完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '点赞失败', 'error')
  } finally {
    socialAction.value = ''
  }
}

function selectSeed(seed) {
  selectedSeedId.value = Number(seed.id)
  flash(`已选择 ${seed.icon}${seed.name}`)
}

function slotKey(slot) { return `${slot.land_id}-${slot.slot_index}` }
function isInteractiveSlot(slot) { return slot.state === 'ready' || slot.state === 'empty' }
function groupReadyCount(group) { return (group?.slots || []).filter((slot) => slot.state === 'ready').length }
function groupEmptyCount(group) { return (group?.slots || []).filter((slot) => slot.state === 'empty').length }

function getSellQuantity(item) {
  const key = String(item.seed_id || item.name)
  const current = Number(sellInputs[key])
  return !current || current < 1 ? 1 : Math.min(current, Number(item.quantity || 1))
}

function updateSellQuantity(item, event) {
  const value = Number(event?.target?.value || 1)
  sellInputs[String(item.seed_id || item.name)] = Math.min(Math.max(1, value || 1), Number(item.quantity || 1))
}

async function plantPlot(slot, seedId) {
  actingSlotKey.value = slotKey(slot)
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/plant-plot', { land_id: slot.land_id, slot_index: slot.slot_index, seed_id: seedId })
    flash(res.message || '种植完成', res.success === false ? 'error' : 'success')
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
    flash(res.message || '收菜完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '收菜失败', 'error')
  } finally {
    actingSlotKey.value = ''
    loading.value = false
  }
}

async function harvestAllReady() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/harvest-all', {})
    flash(res.message || '一键收获完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '一键收获失败', 'error')
  } finally {
    loading.value = false
  }
}

async function plantAllEmpty() {
  if (!selectedSeed.value) return flash('请先选择种子', 'warning')
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/plant-empty', { seed_id: selectedSeed.value.id })
    flash(res.message || '一键种植完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '一键种植失败', 'error')
  } finally {
    loading.value = false
  }
}

async function sellInventory(item) {
  sellingSeedId.value = Number(item.seed_id)
  try {
    const res = await props.api.post('/plugin/VueFarm/sell-inventory', { seed_id: item.seed_id, quantity: getSellQuantity(item) })
    flash(res.message || '出售完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '出售失败', 'error')
  } finally {
    sellingSeedId.value = 0
  }
}

async function sellAllInventory() {
  sellingAll.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/sell-all', {})
    flash(res.message || '一键出售完成', res.success === false ? 'error' : 'success')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '一键出售失败', 'error')
  } finally {
    sellingAll.value = false
  }
}

function handleSlotClick(slot) {
  if (slot.state === 'ready') return harvestPlot(slot)
  if (slot.state === 'empty') {
    if (!selectedSeed.value) return flash('请先选择种子', 'warning')
    return plantPlot(slot, selectedSeed.value.id)
  }
  if (slot.state === 'growing') flash(`${slot.title} 还需要 ${slotText(slot)}`, 'info')
  if (slot.state === 'locked') flash('该坑位尚未解锁', 'info')
}

function formatRemain(seconds) {
  const value = Math.max(0, Number(seconds) || 0)
  if (!value) return '现在可收'
  const days = Math.floor(value / 86400)
  const hours = Math.floor((value % 86400) / 3600)
  const minutes = Math.floor((value % 3600) / 60)
  const secs = value % 60
  if (days) return `${days}天${hours}小时`
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
  return `${secs}秒`
}

function slotText(slot) {
  if (slot.harvest_ts) {
    if (slot.state === 'ready') return '现在可收'
    if (slot.state === 'growing') return formatRemain(slot.harvest_ts - nowTs.value)
  }
  return slot.remaining_label || slot.reward_text || ''
}

function historySummary(item) {
  const title = String(item?.title || '').trim()
  const hiddenTitles = ['🌱Vue-农场运行', '⚠️Vue-农场异常', '❌Vue-农场异常', '【🌱Vue-农场】任务报告', '【🌱农场报告】', '【⚠️农场异常】']
  const lines = hiddenTitles.includes(title.replace(/\s+/g, '')) ? [] : (title ? [title] : [])
  for (const line of item?.lines || []) {
    const text = String(line || '').trim()
    if (text && !text.startsWith('⏰下次可收：')) lines.push(text)
  }
  return lines.join(' / ')
}

async function openStealDialog() {
  manualStealCrop.value = config.value.steal_crop || '全部作物'
  stolenCount.value = 0
  stolenReward.value = 0
  stealDialog.value = true
  await loadStealTarget()
}

async function loadStealTarget() {
  stealLoading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/steal-target', {})
    Object.keys(stealTarget).forEach((key) => delete stealTarget[key])
    Object.assign(stealTarget, res || {})
    if (res.success === false) flash(res.message || res.msg || '没有找到可访问农场', 'warning')
  } catch (error) {
    flash(error?.message || '获取偷菜目标失败', 'error')
  } finally {
    stealLoading.value = false
  }
}

function stealPlotsForLand(land) {
  const landId = Number(land.id || land.land_id || 0)
  const source = (stealTarget.victim_plots || []).filter((plot) => Number(plot.land_id || 0) === landId)
  const count = Math.max(Number(land.effective_plot_count || land.plot_count || 0), ...source.map((plot) => Number(plot.plot_index || 0) + 1), 0)
  const map = new Map(source.map((plot) => [Number(plot.plot_index || 0), plot]))
  return Array.from({ length: count }, (_, index) => map.get(index) || { land_id: landId, plot_index: index })
}

function targetSeedName(plot) {
  return String(plot.seed_name || plot.name || targetSeedMap.value[String(plot.seed_id)]?.name || '')
}

function targetPlotReady(plot) {
  const flag = (value) => value === true || value === 1 || ['1', 'true', 'yes', 'on'].includes(String(value || '').toLowerCase())
  return Boolean(flag(plot.is_ready) || flag(plot.ready) || flag(plot.can_steal) || (Number(plot.harvest_time || 0) > 0 && Number(plot.harvest_time) <= nowTs.value))
}

function isStealablePlot(plot) {
  if (!plot.seed_id || plot.stolen || !targetPlotReady(plot)) return false
  const crop = targetSeedName(plot)
  return manualStealCrop.value === '全部作物' || crop.includes(manualStealCrop.value)
}

function stealPlotClass(plot) {
  return { planted: Boolean(plot.seed_id), ready: targetPlotReady(plot), stealable: isStealablePlot(plot), stolen: Boolean(plot.stolen) }
}

function stealPlotText(plot) {
  if (plot.stolen) return '已偷'
  if (!plot.seed_id) return '空地'
  if (isStealablePlot(plot)) return '点击偷菜'
  if (targetPlotReady(plot)) return '不符合筛选'
  return '成长中'
}

async function stealPlotAction(land, plot) {
  stealLoading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/steal-plot', {
      victim_id: stealTarget.victim_id,
      land_id: land.id || plot.land_id,
      plot_index: plot.plot_index,
    })
    if (res.success) {
      plot.stolen = true
      stolenCount.value += 1
      stolenReward.value += Number(res.reward || 0)
      flash(res.msg || res.message || `偷到 ${targetSeedName(plot)}`)
    } else {
      flash(res.msg || res.message || '偷菜失败', 'error')
    }
  } catch (error) {
    flash(error?.message || '偷菜失败', 'error')
  } finally {
    stealLoading.value = false
  }
}

async function finishStealing(closeAfter = true) {
  stealLoading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/steal-finish', { stolen_count: stolenCount.value, reward: stolenReward.value })
    flash(res.message || res.msg || '偷菜会话已完成', res.success === false ? 'error' : 'success')
    if (res.success !== false) {
      stolenCount.value = 0
      stolenReward.value = 0
      if (closeAfter) stealDialog.value = false
      await loadStatus(false)
    }
  } catch (error) {
    flash(error?.message || '完成偷菜失败', 'error')
  } finally {
    stealLoading.value = false
  }
}

async function closeStealDialog() {
  if (stolenCount.value > 0) return finishStealing(true)
  stealDialog.value = false
}

async function openLikeDialog() {
  likeDialog.value = true
  if (!likeUsernames.value.trim()) await loadLikeTargets()
}

async function loadLikeTargets() {
  likeLoading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/like-targets', {})
    if (res.success === false) return flash(res.message || res.msg || '获取点赞名单失败', 'warning')
    likeUsernames.value = (res.usernames || []).join('\n')
    if (!likeUsernames.value) flash('当前没有可点赞目标', 'info')
  } catch (error) {
    flash(error?.message || '获取点赞名单失败', 'error')
  } finally {
    likeLoading.value = false
  }
}

async function submitLikeBatch() {
  likeLoading.value = true
  try {
    const res = await props.api.post('/plugin/VueFarm/like-batch', { usernames: likeUsernames.value })
    flash(res.message || res.msg || '点赞完成', res.success === false ? 'error' : 'success')
    if (res.success) {
      likeDialog.value = false
      await loadStatus(false)
    }
  } catch (error) {
    flash(error?.message || '批量点赞失败', 'error')
  } finally {
    likeLoading.value = false
  }
}

async function maybeAutoRefreshStatus() {
  if (loading.value) return
  let refresh = false
  if (nextRunTs.value && nowTs.value >= nextRunTs.value && lastRunAutoRefreshTs.value !== nextRunTs.value) {
    lastRunAutoRefreshTs.value = nextRunTs.value
    refresh = true
  }
  if (nextTriggerTs.value && nowTs.value >= nextTriggerTs.value && lastTriggerAutoRefreshTs.value !== nextTriggerTs.value) {
    lastTriggerAutoRefreshTs.value = nextTriggerTs.value
    refresh = true
  }
  if (refresh) await loadStatus(false)
}

function detectTheme() {
  const themeNode = rootEl.value?.closest?.('.v-theme--dark, .v-theme--light')
  if (themeNode?.classList?.contains('v-theme--dark')) {
    isDarkTheme.value = true
    return
  }
  if (themeNode?.classList?.contains('v-theme--light')) {
    isDarkTheme.value = false
    return
  }
  const root = document.documentElement
  const body = document.body
  const text = `${root?.getAttribute('data-theme') || ''} ${root?.className || ''} ${body?.getAttribute('data-theme') || ''} ${body?.className || ''}`.toLowerCase()
  if (text.includes('dark')) isDarkTheme.value = true
  else if (text.includes('light')) isDarkTheme.value = false
  else isDarkTheme.value = Boolean(mediaQuery?.matches)
}

onMounted(async () => {
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)') || null
  mediaQuery?.addEventListener?.('change', detectTheme)
  themeObserver = new MutationObserver(detectTheme)
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  if (document.body) themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  detectTheme()
  await loadStatus()
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    maybeAutoRefreshStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.siqi-farm-page{--bg:#f4f7f5;--panel:#fff;--panel-2:#f8faf9;--text:#1f2d25;--muted:#6f7d75;--line:#dfe7e2;--green:#22a35a;--green-soft:#e8f7ee;--shadow:0 8px 24px rgba(32,72,48,.07);min-height:100%;padding:12px 0 28px;color:var(--text);background:transparent}.siqi-farm-page.is-dark{--bg:#151a17;--panel:#1d2420;--panel-2:#242d28;--text:#eef7f1;--muted:#a4b3aa;--line:#344039;--green:#4ade80;--green-soft:rgba(74,222,128,.12);--shadow:0 10px 30px rgba(0,0,0,.25)}.siqi-farm-page,.siqi-farm-page *{box-sizing:border-box}.siqi-shell{max-width:1220px;margin:0 auto;padding:0 14px;display:grid;gap:14px}.siqi-topbar,.section-head,.hero-card,.dialog-head,.dialog-toolbar,.dialog-actions,.land-head,.steal-land-head,.inventory-card,.history-list article{display:flex;align-items:center}.siqi-topbar{justify-content:space-between;gap:16px;padding:8px 4px 12px;border-bottom:1px solid var(--line)}.topbar-left{display:flex;align-items:center;gap:12px;min-width:0}.topbar-mark{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:var(--green-soft);font-size:23px}.topbar-left h1{margin:0;font-size:21px;font-weight:900}.topbar-left p{margin:2px 0 0;color:var(--muted);font-size:12px}.topbar-actions{display:flex;gap:2px}.siqi-card{padding:16px;border:1px solid var(--line);border-radius:12px;background:var(--panel);box-shadow:var(--shadow)}.hero-card{justify-content:space-between;gap:18px;border-left:4px solid var(--green)}.hero-copy{min-width:0}.eyebrow{margin-bottom:5px;color:var(--green);font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.hero-copy h2,.section-head h2{margin:0;font-size:18px;font-weight:900}.hero-copy p{max-width:720px;margin:7px 0 0;color:var(--muted);font-size:12px;line-height:1.65}.status-row,.summary-chips,.dialog-chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:11px}.status-chip,.summary-chips span,.mini-chip{padding:5px 9px;border:1px solid var(--line);border-radius:999px;background:var(--panel-2);font-size:11px;font-weight:700}.status-chip.ok{color:var(--green);background:var(--green-soft)}.status-chip.muted{color:var(--muted)}.hero-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.hero-actions :deep(.v-btn),.action-buttons :deep(.v-btn){border-radius:7px;font-weight:800}.stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.stat-card{display:flex;align-items:center;gap:12px;padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--panel);box-shadow:var(--shadow)}.stat-card>span{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:var(--panel-2);font-size:20px}.stat-card div{display:grid;gap:3px}.stat-card small{color:var(--muted);font-size:11px}.stat-card strong{font-size:21px;line-height:1}.stat-card.amber{border-top:3px solid #f59e0b}.stat-card.cyan{border-top:3px solid #06b6d4}.stat-card.green{border-top:3px solid #22c55e}.stat-card.indigo{border-top:3px solid #6366f1}.section-head{justify-content:space-between;gap:12px;margin-bottom:14px}.section-note{color:var(--muted);font-size:11px}.interact-card{border-left:4px solid #ef4444}.interact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.action-card{display:grid;grid-template-columns:44px minmax(0,1fr) auto;align-items:center;gap:12px;padding:14px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.action-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:11px;font-size:23px}.steal-action .action-icon{background:rgba(239,68,68,.12)}.like-action .action-icon{background:rgba(236,72,153,.12)}.action-copy{display:grid;gap:3px}.action-copy strong{font-size:14px}.action-copy span,.action-copy small{color:var(--muted);font-size:11px;line-height:1.45}.action-buttons{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}.seed-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}.seed-card,.farm-plot,.steal-plot{position:relative;border:1px solid var(--line);background:var(--panel-2);color:var(--text);transition:.18s ease}.seed-card{display:grid;justify-items:center;gap:4px;min-height:132px;padding:12px 8px;border-radius:11px;cursor:pointer}.seed-card:hover:not(:disabled),.seed-card.active{transform:translateY(-2px);border-color:var(--green);box-shadow:0 8px 18px rgba(34,163,90,.12)}.seed-card.active{background:var(--green-soft)}.seed-card.locked{opacity:.48;cursor:not-allowed}.seed-icon{font-size:26px}.seed-card strong{font-size:13px}.seed-card small,.seed-card em{color:var(--muted);font-size:10px;font-style:normal;text-align:center}.seed-card em{color:var(--green);font-weight:800}.land-list{display:grid;gap:12px}.land-card{padding:13px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.land-head{justify-content:space-between;gap:10px;margin-bottom:11px}.land-head div{display:grid;gap:2px}.land-head strong{font-size:14px}.land-head small,.land-head>span{color:var(--muted);font-size:10px}.plot-grid,.steal-plot-grid{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:7px}.farm-plot,.steal-plot{display:grid;justify-items:center;align-content:center;gap:3px;min-height:92px;padding:9px 5px;border-radius:9px;cursor:default}.farm-plot.clickable,.steal-plot.stealable{cursor:pointer}.farm-plot.clickable:hover,.steal-plot.stealable:hover{transform:translateY(-2px);box-shadow:0 7px 15px rgba(24,66,39,.12)}.farm-plot.ready,.steal-plot.ready{border-color:rgba(245,158,11,.5);background:rgba(245,158,11,.09)}.farm-plot.empty{border-style:dashed;color:#3b82f6}.farm-plot.locked,.farm-plot.expand{opacity:.55}.farm-plot.busy{opacity:.55}.plot-index{position:absolute;top:4px;left:5px;color:var(--muted);font-size:9px}.plot-icon{font-size:22px}.farm-plot strong,.steal-plot strong{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}.farm-plot small,.farm-plot em,.steal-plot small{color:var(--muted);font-size:9px;font-style:normal}.farm-plot em{color:var(--green);font-weight:800}.inventory-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.inventory-card{gap:11px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.inventory-icon{font-size:25px}.inventory-copy{display:grid;gap:2px;min-width:0;flex:1}.inventory-copy strong{font-size:13px}.inventory-copy small{color:var(--muted);font-size:10px}.inventory-actions{display:flex;align-items:center;gap:7px}.inventory-actions input{width:64px;height:32px;padding:0 8px;border:1px solid var(--line);border-radius:7px;background:var(--panel);color:var(--text)}.history-list{display:grid;gap:7px}.history-list article{justify-content:space-between;gap:14px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--panel-2)}.history-list span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}.history-list time{flex:none;color:var(--muted);font-size:10px}.empty-state,.dialog-empty{padding:24px;border:1px dashed var(--line);border-radius:10px;color:var(--muted);text-align:center;font-size:12px}.siqi-dialog{border-radius:14px!important;background:var(--panel)!important;color:var(--text)!important}.dialog-head{gap:12px;padding:16px;border-bottom:1px solid var(--line)}.dialog-avatar{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;font-size:24px}.dialog-avatar.steal{background:rgba(239,68,68,.12)}.dialog-avatar.like{background:rgba(236,72,153,.12)}.dialog-copy{flex:1;min-width:0}.dialog-title{font-size:17px;font-weight:900}.dialog-subtitle,.like-hint{margin-top:3px;color:var(--muted);font-size:11px;line-height:1.5}.dialog-body{background:var(--panel)!important}.dialog-toolbar{gap:10px;flex-wrap:wrap;margin-bottom:13px}.dialog-select{max-width:220px}.dialog-chips{flex:1;margin-top:0}.dialog-actions{padding:12px 16px;border-top:1px solid var(--line)}.steal-land-list{display:grid;gap:12px}.steal-land{padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.steal-land-head{justify-content:space-between;margin-bottom:9px}.steal-land-head strong{font-size:13px}.steal-land-head span{color:var(--muted);font-size:10px}.steal-plot.stealable{border-color:#ef4444}.steal-plot.stolen{opacity:.5}.dialog-empty.compact{padding:14px}.like-hint{padding:10px 0 0}.summary-chips{margin-top:0}.summary-chips span{color:var(--muted)}
@media(max-width:1100px){.seed-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.plot-grid,.steal-plot-grid{grid-template-columns:repeat(5,minmax(0,1fr))}.stat-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.action-card{grid-template-columns:42px minmax(0,1fr)}.action-buttons{grid-column:1/-1;justify-content:flex-start}}
@media(max-width:760px){.siqi-shell{padding:0 9px}.siqi-topbar,.hero-card,.section-head{align-items:flex-start}.hero-card{flex-direction:column}.hero-actions{width:100%;justify-content:flex-start}.hero-actions :deep(.v-btn){flex:1}.interact-grid,.inventory-grid{grid-template-columns:1fr}.plot-grid,.steal-plot-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.history-list article{align-items:flex-start;flex-direction:column}.history-list span{white-space:normal}.history-list time{align-self:flex-end}.dialog-toolbar{align-items:stretch;flex-direction:column}.dialog-select{max-width:none}.topbar-left p{display:none}}
@media(max-width:520px){.stat-grid,.seed-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.plot-grid,.steal-plot-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.topbar-actions :deep(.v-btn){width:34px;height:34px}.action-card{grid-template-columns:38px minmax(0,1fr)}.inventory-card{align-items:flex-start;flex-wrap:wrap}.inventory-actions{width:100%;justify-content:flex-end}}
.siqi-farm-page{width:100%;max-width:100%;overflow-x:hidden}.siqi-shell{width:100%;min-width:0}.siqi-card,.action-card,.land-card,.inventory-card,.stat-card{min-width:0;max-width:100%}
@media(max-width:760px){.siqi-topbar,.hero-card,.section-head{width:100%;flex-direction:column}.topbar-actions,.hero-actions,.action-buttons{width:100%}.topbar-actions,.action-buttons{justify-content:flex-start}.action-buttons :deep(.v-btn){flex:1}.siqi-farm-page :deep(.v-input),.siqi-farm-page :deep(.v-field){min-width:0;max-width:100%}}
</style>
