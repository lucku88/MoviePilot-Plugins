<template>
  <div ref="rootEl" class="toy-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="toy-shell">
      <section class="toy-hero">
        <div class="toy-copy">
          <div class="toy-badge">Vue-玩偶</div>
          <h1 class="toy-title">{{ toy.title || '盲盒抢曝光' }}</h1>
          <div class="toy-chip-row">
            <span class="toy-chip">下次运行 {{ toy.next_run_time || '等待刷新' }}</span>
            <span class="toy-chip">计划触发 {{ toy.next_trigger_time || status.next_trigger_time || '等待刷新' }}</span>
            <span class="toy-chip">{{ toy.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>
        <div class="toy-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="toy-overview-grid">
        <article v-for="item in overviewCards" :key="item.label" class="toy-overview-card">
          <div class="toy-overview-label">{{ item.label }}</div>
          <div class="toy-overview-value">{{ item.value }}</div>
          <div v-if="item.desc && !item.hideMeta" class="toy-overview-desc">{{ item.desc }}</div>
          <div v-if="item.extra && !item.hideMeta" class="toy-overview-desc">{{ item.extra }}</div>
        </article>
      </section>

      <section v-if="showSummary" class="toy-panel toy-panel-summary">
        <div class="toy-panel-head">
          <div>
            <div class="toy-panel-kicker">本次摘要</div>
            <h2>任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="toy-summary-list">
          <div v-for="line in summaryLines" :key="line" class="toy-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="toy-panel toy-panel-shop">
        <div class="toy-panel-head">
          <div>
            <h2>玩偶盲盒商店</h2>
          </div>
        </div>
        <div v-if="!shopBoxes.length" class="toy-empty">暂未获取到盲盒商店数据</div>
        <div v-else class="toy-box-grid">
          <article v-for="box in shopBoxes" :key="box.box_key || box.name" class="toy-box-card" :class="{ locked: box.locked }">
            <img v-if="box.image" class="toy-box-image" :src="box.image" :alt="box.name" />
            <div class="toy-box-name">{{ box.name }}</div>
            <div class="toy-box-desc">{{ box.desc }}</div>
            <div v-if="box.lock_text" class="toy-box-lock">{{ box.lock_text }}</div>
            <div class="toy-box-actions">
              <input
                v-model="buyQuantities[box.box_key]"
                class="toy-number-input"
                type="number"
                min="1"
              />
              <v-btn
                color="deep-orange"
                variant="flat"
                :loading="loading"
                :disabled="loading || box.buy_enabled === false"
                @click="buyBox(box)"
              >
                购买
              </v-btn>
            </div>
          </article>
        </div>
      </section>

      <section class="toy-panel toy-panel-owned">
        <div class="toy-panel-head">
          <div>
            <h2>我的盲盒</h2>
          </div>
        </div>
        <div v-if="!myBoxes.length" class="toy-empty">暂无盲盒，去商店看看吧</div>
        <div v-else class="toy-box-grid">
          <article v-for="box in myBoxes" :key="`owned-${box.box_key || box.name}`" class="toy-box-card compact">
            <img v-if="box.image" class="toy-box-image small" :src="box.image" :alt="box.name" />
            <div class="toy-box-name">{{ box.name }}</div>
            <div class="toy-box-desc">拥有 {{ box.count }} 个</div>
            <div class="toy-box-actions">
              <input
                v-model="openQuantities[box.box_key || box.name]"
                class="toy-number-input"
                type="number"
                min="1"
                :max="Math.max(Number(box.count || 0), 1)"
              />
              <v-btn color="pink" variant="flat" :loading="loading" :disabled="loading || !Number(box.count || 0)" @click="openBox(box)">开启</v-btn>
            </div>
          </article>
        </div>
      </section>

      <section class="toy-panel toy-panel-cabinet">
        <div class="toy-panel-head">
          <div class="toy-panel-heading">
            <h2>玩偶柜子</h2>
            <div class="toy-panel-info">当前 {{ cabinetCards.length }} 个玩偶</div>
          </div>
        </div>
        <div class="toy-section-tools">
          <div class="toy-selected-bar">
            <span>当前选中：</span>
            <strong>{{ selectedDoll ? selectedDoll.name : '未选择玩偶' }}</strong>
            <span v-if="selectedDoll">，点击空展位或目标空位即可上架</span>
          </div>
          <div class="toy-toolbar single">
            <div class="toy-sort-group">
              <button type="button" class="toy-chip is-active">按最快冷却</button>
            </div>
          </div>
        </div>
        <div v-if="!cabinetCards.length" class="toy-empty">暂无可上架玩偶</div>
        <div
          v-else
          class="toy-grid-shell toy-grid-shell-cabinet"
          :style="sectionShellStyle('cabinet')"
          data-virtual-ready="true"
        >
          <div class="toy-cabinet-grid">
            <article
              v-for="doll in cabinetCards"
              :key="doll.doll_key || doll.name"
              class="toy-doll-card"
              :class="{ selected: selectedDollKey === doll.doll_key, disabled: !doll.can_place }"
              @click="selectDoll(doll)"
            >
              <div class="toy-doll-quality-row">
                <div class="toy-doll-quality">{{ doll.quality || '未识别' }}</div>
                <div v-if="doll.origin" class="toy-doll-origin">{{ doll.origin }}</div>
              </div>
              <img v-if="doll.image" class="toy-doll-image" :src="doll.image" :alt="doll.name" />
              <div v-else class="toy-doll-placeholder">🧸</div>
              <div class="toy-doll-name">{{ doll.name }}</div>
              <div class="toy-doll-meta">{{ doll.reward_text }}</div>
              <div class="toy-doll-stats">
                <span>可用 {{ doll.available }}</span>
                <span>总数 {{ doll.total }}</span>
                <span>展出 {{ doll.display_count }}</span>
              </div>
              <div v-if="cabinetCooldownText(doll)" class="toy-doll-cooldown">{{ cabinetCooldownText(doll) }}</div>
              <v-btn block size="small" color="deep-orange" variant="flat" :disabled="!doll.can_place" class="toy-card-action">
                {{ selectedDollKey === doll.doll_key ? '已选择' : '选择上架' }}
              </v-btn>
            </article>
          </div>
        </div>
      </section>

      <section class="toy-panel toy-panel-booth">
        <div class="toy-panel-head">
          <div class="toy-panel-heading">
            <h2>我的展柜</h2>
            <div class="toy-panel-info">最多 18 个展位，当前 {{ personalSlots.length }} 个位置</div>
          </div>
        </div>
        <div class="toy-grid-shell toy-grid-shell-booth" :style="sectionShellStyle('booth')" data-virtual-ready="true">
          <div class="toy-slot-grid">
            <article
              v-for="slot in personalSlots"
              :key="`personal-${slot.slot_index}`"
              class="toy-slot-card"
              :class="{
                empty: slot.empty,
                'is-stolen': slot.is_other_occupant,
                'is-ready': slotActionKind(slot) === 'ready',
              }"
            >
              <div class="toy-slot-index">展位 {{ slot.slot_index }}</div>
              <template v-if="slot.empty">
                <div class="toy-slot-body toy-slot-body-empty">
                  <div class="toy-slot-empty">空展位</div>
                  <div class="toy-slot-tip">{{ selectedDoll ? `可上架 ${selectedDoll.name}` : '先从玩偶柜子选择玩偶' }}</div>
                </div>
                <v-btn color="deep-orange" variant="flat" class="toy-slot-action-btn" :disabled="!selectedDoll || loading" @click="placePersonal(slot)">上架所选玩偶</v-btn>
              </template>
              <template v-else>
                <div class="toy-slot-main">
                  <div class="toy-slot-media">
                    <img v-if="slot.image" class="toy-slot-image" :src="slot.image" :alt="slot.doll_name" />
                    <div v-else class="toy-slot-empty">🧸</div>
                  </div>
                  <div class="toy-slot-body">
                    <div class="toy-slot-name">{{ slot.doll_name }}</div>
                    <div v-if="slot.owner_name" class="toy-slot-owner">{{ slot.owner_name }}</div>
                    <div class="toy-slot-meta">{{ slotRemainText(slot) }}</div>
                    <div class="toy-slot-meta">{{ slot.reward_text }}</div>
                  </div>
                </div>
                <div class="toy-slot-progress"><div class="toy-slot-progress-bar" :style="{ width: `${slot.progress}%` }" /></div>
                <div class="toy-slot-foot">
                  <div class="toy-slot-activity" :class="`is-${slotActionKind(slot)}`">{{ slotActivityText(slot) }}</div>
                  <v-btn
                    :color="slotActionColor(slot)"
                    variant="flat"
                    class="toy-slot-action-btn"
                    :loading="loading"
                    :disabled="loading || !slot.viewer_is_occupant"
                    @click="collectSlot(slot)"
                  >
                    {{ slotActionLabel(slot) }}
                  </v-btn>
                </div>
              </template>
            </article>
          </div>
        </div>
      </section>

      <section class="toy-panel toy-panel-target">
        <div class="toy-panel-head">
          <div class="toy-panel-heading">
            <h2>抢占他人展位</h2>
            <div v-if="targetPanel.slots?.length" class="toy-panel-info">{{ targetPanel.username }} · {{ targetPanel.slot_count }} 个展位</div>
          </div>
        </div>
        <div class="toy-target-controls">
          <v-btn color="deep-orange" variant="flat" :loading="loading" @click="randomTarget">随机匹配</v-btn>
          <div class="toy-search">
            <input v-model="targetKeyword" class="toy-text-input" placeholder="输入用户名或用户 ID" />
            <v-btn variant="flat" color="primary" :loading="loading" @click="viewTarget()">前往展台</v-btn>
          </div>
        </div>
        <div v-if="!targetPanel.slots?.length" class="toy-empty">尚未选择目标</div>
        <div v-else class="toy-target-panel">
          <div class="toy-grid-shell toy-grid-shell-target" :style="sectionShellStyle('target')" data-virtual-ready="true">
            <div class="toy-slot-grid">
              <article
                v-for="slot in targetPanel.slots"
                :key="`target-${slot.owner_id}-${slot.slot_index}`"
                class="toy-slot-card"
                :class="{
                  empty: slot.empty,
                  'is-stolen': slot.is_other_occupant,
                  'is-ready': slotActionKind(slot) === 'ready',
                }"
              >
                <div class="toy-slot-index">展位 {{ slot.slot_index }}</div>
                <template v-if="slot.empty && !slot.cooldown_active">
                  <div class="toy-slot-body toy-slot-body-empty">
                    <div class="toy-slot-empty">空位可抢</div>
                    <div class="toy-slot-tip">{{ selectedDoll ? `抢占为 ${selectedDoll.name}` : '先选择玩偶' }}</div>
                  </div>
                  <v-btn color="deep-orange" variant="flat" class="toy-slot-action-btn" :disabled="!selectedDoll || loading" @click="placeTarget(slot)">抢占展位</v-btn>
                </template>
                <template v-else-if="slot.empty && slot.cooldown_active">
                  <div class="toy-slot-body toy-slot-body-empty">
                    <div class="toy-slot-empty">⏳</div>
                    <div class="toy-slot-tip">展位冷却中</div>
                  </div>
                  <v-btn color="grey-darken-1" variant="flat" class="toy-slot-action-btn" disabled>冷却中</v-btn>
                </template>
                <template v-else>
                  <div class="toy-slot-main">
                    <div class="toy-slot-media">
                      <img v-if="slot.image" class="toy-slot-image" :src="slot.image" :alt="slot.doll_name" />
                      <div v-else class="toy-slot-empty">🧸</div>
                    </div>
                    <div class="toy-slot-body">
                      <div class="toy-slot-name">{{ slot.doll_name || slot.status_text }}</div>
                      <div v-if="slot.owner_name" class="toy-slot-owner">{{ slot.owner_name }}</div>
                      <div class="toy-slot-meta">{{ targetRemainText(slot) }}</div>
                      <div v-if="slot.reward_text" class="toy-slot-meta">{{ slot.reward_text }}</div>
                    </div>
                  </div>
                  <div class="toy-slot-progress"><div class="toy-slot-progress-bar" :style="{ width: `${slot.progress}%` }" /></div>
                  <div class="toy-slot-foot">
                    <div class="toy-slot-activity" :class="`is-${slotActionKind(slot)}`">{{ slotActivityText(slot) }}</div>
                    <v-btn
                      :color="targetSlotActionColor(slot)"
                      variant="flat"
                      class="toy-slot-action-btn"
                      :disabled="loading || !slot.viewer_is_occupant"
                      @click="collectSlot(slot)"
                    >
                      {{ targetSlotActionLabel(slot) }}
                    </v-btn>
                  </div>
                </template>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section class="toy-panel toy-panel-remote">
        <div class="toy-panel-head">
          <div class="toy-panel-heading">
            <h2>我的外展记录</h2>
            <div class="toy-panel-info">{{ remoteRecords.length }} 条记录</div>
          </div>
        </div>
        <div v-if="!remoteRecords.length" class="toy-empty">暂无外展记录</div>
        <div v-else class="toy-grid-shell toy-grid-shell-remote" :style="sectionShellStyle('remote')" data-virtual-ready="true">
          <div class="toy-remote-grid">
            <article v-for="item in remoteRecords" :key="`${item.owner_id}-${item.slot_index}`" class="toy-remote-card">
              <div class="toy-remote-main">
                <img v-if="item.image" class="toy-remote-image" :src="item.image" :alt="item.doll_name" />
                <div class="toy-remote-body">
                  <div class="toy-remote-owner">{{ item.owner_name }}</div>
                  <div class="toy-remote-meta">展位 {{ item.slot_index }}</div>
                  <div class="toy-remote-meta">{{ item.doll_name }}</div>
                  <div class="toy-remote-meta">{{ remoteRemainText(item) }}</div>
                </div>
              </div>
              <v-btn size="small" variant="flat" color="primary" class="toy-remote-action" :disabled="loading" @click="viewTarget(item.owner_id)">查看</v-btn>
            </article>
          </div>
        </div>
      </section>

      <section class="toy-panel toy-panel-history">
        <div class="toy-panel-head">
          <div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="toy-empty">暂无执行历史</div>
        <div v-else class="toy-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="toy-history-item">
            <div class="toy-history-top">
              <strong>{{ historyTitle(item) }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div v-if="historyDetailLines(item).length" class="toy-history-lines">{{ historyDetailLines(item).join(' / ') }}</div>
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

const pluginBase = '/plugin/VueToy'
const loading = ref(false)
const rootEl = ref(null)
const status = reactive({ toy_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const targetKeyword = ref('')
const selectedDollKey = ref('')
const buyQuantities = reactive({})
const openQuantities = reactive({})
const transientTargetPanel = ref({})
const isDarkTheme = ref(false)
const dismissedSummaryKey = ref('')
const nowTs = ref(Math.floor(Date.now() / 1000))
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)

let timer = null
let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

const toy = computed(() => status.toy_status || {})
const overviewCards = computed(() => (toy.value.overview || []).map((item) => ({ ...item, hideMeta: item.label === '\u6211\u7684\u5c55\u67dc' })))
const shopBoxes = computed(() => toy.value.shop_boxes || [])
const myBoxes = computed(() => toy.value.my_boxes || [])
const personalSlots = computed(() => toy.value.personal_slots || [])
const targetPanel = computed(() => {
  const panel = transientTargetPanel.value || {}
  if (panel.slots?.length) {
    return panel
  }
  return toy.value.target_panel || {}
})
const remoteRecords = computed(() => toy.value.remote_records || [])
const historyItems = computed(() => status.history || toy.value.history || [])
const summaryLines = computed(() => (toy.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)
const nextRunTs = computed(() => Number(toy.value.next_run_ts || 0) || parseDateTime(toy.value.next_run_time))
const nextTriggerTs = computed(() => Number(toy.value.next_trigger_ts || 0) || parseDateTime(toy.value.next_trigger_time))

// Virtual-ready section metrics. Large lists still render normally today,
// but the shell already exposes stable heights and density rules for future
// row-windowing without rewriting the page structure again.
const SECTION_LAYOUT = {
  cabinet: { maxHeight: 556, minCard: 146, rowHeight: 190, overscan: 4, threshold: 84 },
  booth: { maxHeight: 496, minCard: 186, rowHeight: 178, overscan: 2, threshold: 24 },
  target: { maxHeight: 496, minCard: 186, rowHeight: 178, overscan: 2, threshold: 24 },
  remote: { maxHeight: 560, minCard: 172, rowHeight: 154, overscan: 5, threshold: 120 },
}

const cabinetCards = computed(() => {
  const items = [...(toy.value.cabinet || [])]
  return items.sort((left, right) => {
    const leftScore = cabinetSortScore(left)
    const rightScore = cabinetSortScore(right)
    if (leftScore.bucket !== rightScore.bucket) return leftScore.bucket - rightScore.bucket
    if (leftScore.availableAt !== rightScore.availableAt) return leftScore.availableAt - rightScore.availableAt
    if (leftScore.available !== rightScore.available) return rightScore.available - leftScore.available
    if (leftScore.qualityRank !== rightScore.qualityRank) return rightScore.qualityRank - leftScore.qualityRank
    return String(left.name || '').localeCompare(String(right.name || ''))
  })
})

const selectedDoll = computed(() => cabinetCards.value.find((item) => item.doll_key === selectedDollKey.value) || null)

function sectionShellStyle(sectionName) {
  const config = SECTION_LAYOUT[sectionName]
  if (!config) {
    return {}
  }
  return {
    '--toy-shell-max-height': `${config.maxHeight}px`,
    '--toy-grid-min-card': `${config.minCard}px`,
    '--toy-virtual-row-height': `${config.rowHeight}px`,
    '--toy-virtual-overscan': String(config.overscan),
    '--toy-virtual-threshold': String(config.threshold),
  }
}

watch(
  shopBoxes,
  (items) => {
    items.forEach((item) => {
      if (!buyQuantities[item.box_key]) buyQuantities[item.box_key] = String(item.default_quantity || 1)
    })
  },
  { immediate: true },
)

watch(
  myBoxes,
  (items) => {
    items.forEach((item) => {
      const key = item.box_key || item.name
      if (!openQuantities[key]) openQuantities[key] = String(item.default_quantity || 1)
    })
  },
  { immediate: true },
)

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

function historyTitle(item = {}) {
  return String(item.title || '').trim() || '任务结果'
}

function historyDetailLines(item = {}) {
  return Array.isArray(item.lines) ? item.lines.filter(Boolean) : []
}

function cabinetSortScore(item = {}) {
  const available = Number(item.available || 0)
  const coolingCount = Number(item.cooling_count || 0)
  const cooldownUntilTs = Number(item.cooldown_until_ts || 0)
  const qualityRank = Number(item.quality_rank || 0)
  if (available > 0) {
    return {
      bucket: 0,
      availableAt: 0,
      available,
      qualityRank,
    }
  }
  if (coolingCount > 0) {
    return {
      bucket: 1,
      availableAt: cooldownUntilTs || Number.MAX_SAFE_INTEGER,
      available,
      qualityRank,
    }
  }
  return {
    bucket: 2,
    availableAt: Number.MAX_SAFE_INTEGER,
    available,
    qualityRank,
  }
}

function applyPayload(payload = {}) {
  if (payload.status && payload.status.toy_status) {
    Object.assign(status, payload.status)
  } else if (payload.toy_status || payload.history || payload.config) {
    Object.assign(status, payload)
  }
  if (payload.toy_status && !payload.status) {
    status.toy_status = payload.toy_status
  }
  if (payload.target_panel && status.toy_status) {
    transientTargetPanel.value = payload.target_panel
  }
  if (payload.target_panel && !status.toy_status) {
    transientTargetPanel.value = payload.target_panel
  }
}

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = ''
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('vuetoy-summary-dismissed') || ''
}

watch(summaryKey, () => {
  loadDismissedSummaryKey()
})

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

async function loadStatus(showError = true) {
  try {
    const data = await props.api.get(`${pluginBase}/status`)
    Object.assign(status, data || {})
    return true
  } catch (error) {
    if (showError) {
      flash(error?.message || '加载状态失败', 'error')
    }
    return false
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
    await loadStatus(false)
  }
}

async function withAction(action, fallback) {
  loading.value = true
  try {
    const result = await action()
    applyPayload(result || {})
    await loadStatus(false)
    window.setTimeout(() => {
      void loadStatus(false)
    }, 1200)
    window.setTimeout(() => {
      void loadStatus(false)
    }, 3000)
    flash(result?.message || fallback)
  } catch (error) {
    flash(error?.message || fallback, 'error')
  } finally {
    loading.value = false
  }
}

function refreshData() {
  return withAction(() => props.api.post(`${pluginBase}/refresh`), '状态已刷新')
}

function runNow() {
  return withAction(() => props.api.post(`${pluginBase}/run`), '执行完成')
}

function syncCookie() {
  return withAction(() => props.api.get(`${pluginBase}/cookie`), 'Cookie 已同步')
}

function buyBox(box) {
  return withAction(
    () =>
      props.api.post(`${pluginBase}/buy-box`, {
        box_key: box.box_key,
        quantity: Number(buyQuantities[box.box_key] || 1),
      }),
    '购买成功',
  )
}

function openBox(box) {
  const key = box.box_key || box.name
  return withAction(
    () =>
      props.api.post(`${pluginBase}/open-box`, {
        box_key: box.box_key,
        quantity: Number(openQuantities[key] || 1),
      }),
    '开启完成',
  )
}

function selectDoll(doll) {
  if (!doll.can_place) return
  selectedDollKey.value = selectedDollKey.value === doll.doll_key ? '' : doll.doll_key
}

function collectSlot(slot) {
  return withAction(
    () =>
      props.api.post(`${pluginBase}/collect-slot`, {
        owner_id: slot.owner_id,
        slot_index: slot.slot_index,
      }),
    '收回成功',
  )
}

function placePersonal(slot) {
  if (!selectedDoll.value) return
  return withAction(
    () =>
      props.api.post(`${pluginBase}/place-personal`, {
        owner_id: slot.owner_id,
        slot_index: slot.slot_index,
        doll_key: selectedDoll.value.doll_key,
        doll_name: selectedDoll.value.name,
      }),
    '上架成功',
  )
}

function randomTarget() {
  return withAction(() => props.api.post(`${pluginBase}/random-target`), '已匹配目标')
}

function viewTarget(ownerId = null) {
  const keyword = ownerId ?? targetKeyword.value
  return withAction(() => props.api.post(`${pluginBase}/view-target`, { keyword }), '已加载目标展台')
}

function placeTarget(slot) {
  if (!selectedDoll.value) return
  return withAction(
    () =>
      props.api.post(`${pluginBase}/place-target`, {
        owner_id: slot.owner_id,
        slot_index: slot.slot_index,
        doll_key: selectedDoll.value.doll_key,
        doll_name: selectedDoll.value.name,
      }),
    '抢占成功',
  )
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('vuetoy-summary-dismissed', key)
    } else {
      window.sessionStorage.removeItem('vuetoy-summary-dismissed')
    }
  }
}

function closePlugin() {
  if (showSummary.value) {
    dismissSummary()
  }
  transientTargetPanel.value = {}
  targetKeyword.value = ''
  emit('close')
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme') || current.className) return current
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme') || document.body?.className) return document.body
  if (document.documentElement?.getAttribute('data-theme') || document.documentElement?.className) return document.documentElement
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  if (['dark', 'purple', 'transparent'].includes(themeValue)) {
    return true
  }
  const className = String(node?.className || '').toLowerCase()
  return ['v-theme--dark', 'theme--dark', 'theme-dark', 'dark'].some((token) => className.includes(token))
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase()
  if (['light'].includes(themeValue)) {
    return true
  }
  const className = String(node?.className || '').toLowerCase()
  return ['v-theme--light', 'theme--light', 'theme-light', 'light'].some((token) => className.includes(token))
}

function detectTheme() {
  const themeNodes = getThemeNodes()
  if (themeNodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true
    return
  }
  if (themeNodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  themeObserver?.disconnect?.()
  detectTheme()
  observedThemeNode = findThemeNode()
  if (!window.MutationObserver) {
    return
  }
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode()
    if (nextNode !== observedThemeNode) {
      bindThemeObserver()
      return
    }
    detectTheme()
  })
  getThemeNodes().forEach((node) => {
    themeObserver.observe(node, {
      attributes: true,
      subtree: node === document.documentElement || node === document.body,
      attributeFilter: ['data-theme', 'class'],
    })
  })
}

function slotActionKind(slot) {
  if (!slot) return 'empty'
  if (slot.empty) {
    return slot.cooldown_active ? 'cooldown' : 'empty'
  }
  if (!slot.viewer_is_occupant) {
    return 'blocked'
  }
  const endTs = Number(slot.remaining_end_ts || 0)
  if (slot.can_collect || (endTs && endTs - nowTs.value <= 0)) {
    return 'ready'
  }
  return 'early'
}

function slotActionLabel(slot) {
  const kind = slotActionKind(slot)
  if (kind === 'ready') return '收回玩偶'
  if (kind === 'early') return '提前收回'
  return slot?.action_label || '被抢占'
}

function slotActionColor(slot) {
  const kind = slotActionKind(slot)
  if (kind === 'ready') return 'success'
  if (kind === 'early') return 'amber-darken-2'
  if (kind === 'blocked') return 'grey-darken-1'
  return 'deep-orange'
}

function targetSlotActionLabel(slot) {
  const kind = slotActionKind(slot)
  if (kind === 'blocked') {
    return slot?.action_label || '已被占用'
  }
  return slotActionLabel(slot)
}

function targetSlotActionColor(slot) {
  const kind = slotActionKind(slot)
  if (kind === 'blocked') return 'grey-darken-1'
  return slotActionColor(slot)
}

function slotActivityText(slot) {
  if (!slot) return ''
  if (slot.empty) {
    return slot.cooldown_active ? '展位冷却中' : '空位可上架'
  }
  const kind = slotActionKind(slot)
  if (kind === 'ready') {
    return '展出完成，可以收回玩偶'
  }
  if (kind === 'blocked') {
    return '正在展出中，获取曝光中...'
  }
  return slot?.activity_text || '正在展出中，获取曝光中...'
}

function formatRemain(seconds) {
  const sec = Math.max(0, Number(seconds) || 0)
  if (!sec) return '现在可回收'
  const hours = Math.floor(sec / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  const secs = sec % 60
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
  return `${secs}秒`
}

function cabinetCooldownText(doll) {
  const coolingCount = Number(doll?.cooling_count || 0)
  if (!coolingCount) {
    return ''
  }
  const untilTs = Number(doll?.cooldown_until_ts || 0)
  if (!untilTs) {
    return doll?.cooldown_text || ''
  }
  const remain = untilTs - nowTs.value
  return remain > 0 ? `冷却中 x${coolingCount} · 最快${formatRemain(remain)}` : `冷却中 x${coolingCount}`
}

function slotRemainText(slot) {
  const endTs = Number(slot?.remaining_end_ts || 0)
  if (endTs) {
    const remain = endTs - nowTs.value
    return remain > 0 ? `距完成 ${formatRemain(remain)}` : '已可回收'
  }
  const fallback = String(slot?.remaining_text || '')
  if (!fallback) return slot?.viewer_is_occupant ? '已可回收' : (slot?.status_text || '')
  if (fallback === '已可回收' || fallback.startsWith('距完成')) return fallback
  return `距完成 ${fallback}`
}

function targetRemainText(slot) {
  if (!slot) {
    return ''
  }
  if (slot.empty && !slot.cooldown_active) {
    return '空位可抢'
  }
  if (slot.empty && slot.cooldown_active) {
    return '展位冷却中'
  }
  const endTs = Number(slot.remaining_end_ts || 0)
  if (endTs) {
    const remain = endTs - nowTs.value
    return remain > 0 ? `距完成 ${formatRemain(remain)}` : '已可回收'
  }
  const fallback = String(slot.remaining_text || '')
  if (!fallback) return slot.status_text || ''
  if (fallback === '已可回收' || fallback.startsWith('距完成')) return fallback
  return `距完成 ${fallback}`
}

function remoteRemainText(item) {
  const endTs = Number(item?.remaining_end_ts || 0)
  if (endTs) {
    const remain = endTs - nowTs.value
    return remain > 0 ? `距完成 ${formatRemain(remain)}` : '已可回收'
  }
  const fallback = String(item?.remaining_text || '')
  if (!fallback) return '已可回收'
  if (fallback === '已可回收' || fallback.startsWith('距完成')) return fallback
  return `距完成 ${fallback}`
}

onMounted(async () => {
  loadDismissedSummaryKey()
  detectTheme()
  bindThemeObserver()
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
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
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.toy-page {
  min-height: 100vh;
  --toy-bg-start: #fafbff;
  --toy-bg-end: #eef1f7;
  --toy-panel: rgba(255, 255, 255, 0.88);
  --toy-panel-strong: rgba(255, 255, 255, 0.96);
  --toy-border: rgba(129, 133, 164, 0.16);
  --toy-border-strong: rgba(124, 92, 255, 0.26);
  --toy-chip: rgba(124, 92, 255, 0.1);
  --toy-text-main: #262638;
  --toy-text-soft: rgba(118, 119, 139, 0.92);
  --toy-shadow: 0 20px 48px rgba(121, 128, 166, 0.12);
  --toy-accent: #7c5cff;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.94) 0%, rgba(246, 247, 250, 0.98) 42%, #eef1f7 100%),
    linear-gradient(180deg, var(--toy-bg-start) 0%, var(--toy-bg-end) 100%);
  color: var(--toy-text-main);
}

.toy-page.is-dark-theme {
  --toy-bg-start: #212534;
  --toy-bg-end: #14161f;
  --toy-panel: rgba(26, 28, 39, 0.92);
  --toy-panel-strong: rgba(19, 21, 30, 0.98);
  --toy-border: rgba(124, 92, 255, 0.16);
  --toy-border-strong: rgba(124, 92, 255, 0.34);
  --toy-chip: rgba(139, 108, 255, 0.14);
  --toy-text-main: #f3f5ff;
  --toy-text-soft: rgba(159, 167, 196, 0.92);
  --toy-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  --toy-accent: #9b82ff;
  background:
    radial-gradient(circle at top, rgba(33, 37, 52, 0.92) 0%, rgba(23, 26, 36, 0.98) 38%, #14161f 100%),
    linear-gradient(180deg, var(--toy-bg-start) 0%, var(--toy-bg-end) 100%);
}

.toy-page,
.toy-page * {
  box-sizing: border-box;
}

.toy-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 12px 18px;
  display: grid;
  gap: 14px;
}

.toy-hero,
.toy-panel,
.toy-overview-card,
.toy-box-card,
.toy-doll-card,
.toy-slot-card,
.toy-remote-card,
.toy-history-item {
  border: 1px solid var(--toy-border);
  border-radius: 20px;
  background: var(--toy-panel);
  box-shadow: var(--toy-shadow);
  backdrop-filter: blur(16px);
}

.toy-hero,
.toy-panel {
  padding: 16px;
}

.toy-hero {
  display: flex;
  gap: 14px;
  justify-content: space-between;
  align-items: flex-start;
  background:
    radial-gradient(circle at top left, rgba(124, 92, 255, 0.16) 0%, transparent 34%),
    linear-gradient(135deg, rgba(124, 92, 255, 0.08) 0%, transparent 52%),
    var(--toy-panel);
}

.toy-copy {
  flex: 1;
  min-width: 0;
}

.toy-badge,
.toy-chip,
.toy-overview-desc,
.toy-doll-quality,
.toy-doll-cooldown,
.toy-slot-index,
.toy-slot-activity {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}

.toy-badge {
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 800;
  background: var(--toy-chip);
  color: var(--toy-accent);
}

.toy-title {
  margin: 10px 0 0;
  font-size: clamp(28px, 3.8vw, 40px);
  line-height: 1.06;
  letter-spacing: -0.03em;
}

.toy-chip-row {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.toy-chip-row span {
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--toy-border);
  background: var(--toy-panel-strong);
  font-size: 12px;
  font-weight: 600;
  color: var(--toy-text-main);
}

.toy-action-grid {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: nowrap;
  min-width: min(100%, 560px);
}

.toy-action-grid :deep(.v-btn) {
  min-height: 42px;
  border-radius: 14px;
  font-weight: 800;
}

.toy-action-grid :deep(.v-btn--variant-flat) {
  min-width: 132px;
}

.toy-action-grid :deep(.v-btn--variant-text) {
  min-width: auto;
  padding-inline: 6px;
}

.toy-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.toy-overview-card {
  position: relative;
  overflow: hidden;
  padding: 14px 15px;
  text-align: left;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06) 0%, transparent 100%), var(--toy-panel-strong);
}

.toy-overview-card::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: rgba(124, 92, 255, 0.22);
}

.toy-overview-card:nth-child(1)::before {
  background: rgba(124, 92, 255, 0.42);
}

.toy-overview-card:nth-child(2)::before {
  background: rgba(255, 160, 67, 0.42);
}

.toy-overview-card:nth-child(3)::before {
  background: rgba(76, 132, 255, 0.42);
}

.toy-overview-card:nth-child(4)::before {
  background: rgba(244, 114, 182, 0.42);
}

.toy-overview-label,
.toy-panel-kicker {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--toy-text-soft);
}

.toy-overview-value {
  margin: 10px 0 0;
  font-size: 28px;
  font-weight: 800;
}

.toy-overview-desc {
  margin: 8px 0 0;
  padding: 6px 10px;
  background: var(--toy-chip);
  color: var(--toy-text-main);
  font-size: 12px;
}

.toy-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.toy-panel-head h2 {
  margin: 0;
  font-size: 18px;
  line-height: 1.15;
}

.toy-panel-heading {
  display: grid;
  gap: 4px;
}

.toy-panel-info {
  font-size: 12px;
  font-weight: 600;
  color: var(--toy-text-soft);
}

.toy-panel-kicker {
  margin-bottom: 4px;
}

.toy-panel-summary {
  background:
    radial-gradient(circle at top left, rgba(124, 92, 255, 0.08), transparent 32%),
    var(--toy-panel);
}

.toy-panel-shop {
  background:
    radial-gradient(circle at top right, rgba(255, 185, 92, 0.08), transparent 30%),
    var(--toy-panel);
}

.toy-panel-owned {
  background:
    radial-gradient(circle at top left, rgba(255, 112, 154, 0.06), transparent 28%),
    var(--toy-panel);
}

.toy-panel-cabinet {
  background:
    radial-gradient(circle at top left, rgba(74, 137, 255, 0.07), transparent 28%),
    var(--toy-panel);
}

.toy-panel-booth {
  background:
    radial-gradient(circle at top right, rgba(124, 92, 255, 0.07), transparent 28%),
    var(--toy-panel);
}

.toy-panel-target {
  background:
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.07), transparent 28%),
    var(--toy-panel);
}

.toy-panel-remote {
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.06), transparent 28%),
    var(--toy-panel);
}

.toy-panel-history {
  background:
    radial-gradient(circle at top left, rgba(146, 152, 176, 0.08), transparent 28%),
    var(--toy-panel);
}

.toy-summary-list,
.toy-history-list {
  display: grid;
  gap: 10px;
}

.toy-summary-line {
  padding: 13px 15px;
  border: 1px solid var(--toy-border);
  border-radius: 18px;
  background: var(--toy-panel-strong);
  font-size: 13px;
  line-height: 1.6;
}

.toy-box-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(182px, 1fr));
  gap: 10px;
}

.toy-box-card {
  padding: 14px 14px 12px;
  text-align: center;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, transparent 100%), var(--toy-panel-strong);
}

.toy-box-card.locked,
.toy-doll-card.disabled {
  opacity: 0.7;
}

.toy-box-image {
  width: 102px;
  height: 142px;
  object-fit: contain;
  margin: 0 auto 12px;
  display: block;
}

.toy-box-image.small {
  width: 78px;
  height: 102px;
}

.toy-box-name {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.3;
}

.toy-box-desc {
  margin-top: 8px;
  min-height: 34px;
  font-size: 13px;
  color: var(--toy-text-soft);
  line-height: 1.5;
}

.toy-box-lock {
  display: block;
  margin-top: 8px;
  color: #ff7c7c;
  font-size: 13px;
}

.toy-box-actions,
.toy-search {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
}

.toy-number-input,
.toy-text-input {
  width: 100%;
  min-width: 0;
  border: 1px solid var(--toy-border);
  background: var(--toy-panel-strong);
  color: inherit;
  border-radius: 14px;
  padding: 10px 12px;
  outline: none;
}

.toy-number-input:focus,
.toy-text-input:focus {
  border-color: var(--toy-border-strong);
  box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.1);
}

.toy-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.toy-section-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.toy-sort-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toy-chip {
  border: 1px solid var(--toy-border);
  padding: 8px 12px;
  background: var(--toy-panel-strong);
  color: inherit;
  cursor: default;
  font-size: 13px;
}

.toy-chip.is-active {
  background: rgba(124, 92, 255, 0.12);
  border-color: rgba(124, 92, 255, 0.28);
  color: var(--toy-accent);
}

.toy-selected-bar {
  margin-bottom: 0;
  padding: 10px 12px;
  border: 1px solid var(--toy-border);
  border-radius: 16px;
  background: var(--toy-panel-strong);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
  line-height: 1.5;
  flex: 1 1 280px;
  min-width: min(100%, 320px);
}

.toy-grid-shell {
  position: relative;
  max-height: min(var(--toy-shell-max-height, 560px), 68vh);
  overflow: auto;
  padding-right: 6px;
  scrollbar-gutter: stable;
  content-visibility: auto;
  contain: layout paint style;
  contain-intrinsic-size: calc(var(--toy-virtual-row-height, 200px) * 3);
}

.toy-grid-shell::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.toy-grid-shell::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(124, 92, 255, 0.22);
}

.toy-grid-shell::-webkit-scrollbar-track {
  background: transparent;
}

.toy-cabinet-grid,
.toy-slot-grid,
.toy-remote-grid {
  display: grid !important;
  gap: 10px;
  align-items: start;
  justify-items: stretch;
  grid-auto-flow: row dense;
  grid-template-columns: repeat(auto-fit, minmax(var(--toy-grid-min-card, 152px), 1fr));
}

.toy-cabinet-grid {
  grid-template-columns: repeat(auto-fit, minmax(var(--toy-grid-min-card, 146px), 1fr));
}

.toy-panel-booth .toy-slot-grid {
  grid-template-columns: repeat(auto-fit, minmax(var(--toy-grid-min-card, 186px), 1fr));
}

.toy-panel-target .toy-slot-grid {
  grid-template-columns: repeat(auto-fit, minmax(var(--toy-grid-min-card, 186px), 1fr));
}

.toy-remote-grid {
  grid-template-columns: repeat(auto-fit, minmax(var(--toy-grid-min-card, 172px), 1fr));
}

.toy-doll-card,
.toy-slot-card,
.toy-remote-card {
  width: auto !important;
  min-width: 0;
  max-width: none;
  padding: 11px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.04) 0%, transparent 100%), var(--toy-panel-strong);
  transition:
    border-color 0.18s ease,
    transform 0.18s ease,
    background-color 0.18s ease;
}

.toy-doll-card:hover,
.toy-slot-card:hover,
.toy-remote-card:hover {
  transform: translateY(-1px);
  border-color: rgba(124, 92, 255, 0.26);
}

.toy-doll-card {
  display: grid;
  align-content: start;
  justify-items: stretch;
  gap: 5px;
  min-height: 188px;
  grid-template-rows: auto auto auto auto 1fr auto;
}

.toy-slot-card,
.toy-remote-card {
  display: grid;
  align-content: start;
  align-items: start;
  grid-template-rows: auto auto auto 1fr;
  gap: 7px;
  min-height: 176px;
}

.toy-remote-card {
  min-height: 148px;
  grid-template-rows: auto 1fr auto;
}

.toy-doll-card.selected {
  border-color: rgba(124, 92, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(124, 92, 255, 0.2), var(--toy-shadow);
}

.toy-slot-card.is-stolen {
  border-color: rgba(255, 145, 111, 0.32);
}

.toy-slot-card.is-ready {
  border-color: rgba(58, 197, 110, 0.28);
}

.toy-doll-image,
.toy-slot-image,
.toy-remote-image {
  width: 50px;
  height: 50px;
  object-fit: contain;
  margin: 0;
  display: block;
}

.toy-slot-media {
  width: 56px;
  height: 56px;
  margin: 0;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: rgba(255, 190, 92, 0.1);
  flex-shrink: 0;
}

.toy-doll-placeholder,
.toy-slot-empty {
  width: 50px;
  height: 50px;
  margin: 0;
  display: grid;
  place-items: center;
  font-size: 18px;
  border-radius: 14px;
  background: rgba(255, 190, 92, 0.1);
}

.toy-doll-quality-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 0;
}

.toy-doll-quality {
  padding: 3px 7px;
  background: var(--toy-chip);
  font-size: 9px;
  font-weight: 700;
}

.toy-doll-origin {
  font-size: 9px;
  color: var(--toy-text-soft);
}

.toy-doll-name,
.toy-slot-name,
.toy-remote-owner {
  font-size: 14px;
  font-weight: 800;
  line-height: 1.3;
}

.toy-doll-name {
  text-align: left;
}

.toy-slot-owner {
  margin-top: 0;
  font-size: 10px;
  font-weight: 700;
  color: #ff5e8a;
}

.toy-doll-meta,
.toy-slot-meta,
.toy-remote-meta,
.toy-slot-tip {
  margin-top: 0;
  font-size: 10px;
  color: var(--toy-text-soft);
  line-height: 1.35;
}

.toy-doll-stats {
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 1px;
}

.toy-doll-stats span {
  padding: 3px 6px;
  border-radius: 999px;
  border: 1px solid rgba(124, 92, 255, 0.14);
  background: rgba(124, 92, 255, 0.08);
  font-size: 9px;
  color: var(--toy-text-soft);
}

.toy-doll-cooldown {
  margin-top: 1px;
  padding: 4px 8px;
  background: rgba(126, 126, 126, 0.12);
  font-size: 9px;
  color: var(--toy-text-soft);
  width: fit-content;
}

.toy-card-action {
  margin-top: 2px;
}

.toy-slot-index {
  align-self: flex-start;
  padding: 4px 8px;
  margin-bottom: 0;
  background: var(--toy-chip);
  font-size: 9px;
  font-weight: 700;
}

.toy-slot-main,
.toy-remote-main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  width: 100%;
}

.toy-slot-body,
.toy-remote-body {
  min-width: 0;
  flex: 1;
  display: grid;
  gap: 2px;
  text-align: left;
}

.toy-slot-body-empty {
  display: grid;
  align-content: start;
  justify-items: start;
  gap: 5px;
  min-height: 56px;
}

.toy-slot-body-empty .toy-slot-empty {
  width: auto;
  min-width: 48px;
  padding: 0 10px;
}

.toy-slot-progress {
  margin: 0;
  width: 100%;
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 190, 92, 0.14);
  overflow: hidden;
}

.toy-slot-progress-bar {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #ffd27b 0%, #ff8a4c 100%);
}

.toy-slot-activity {
  margin: 0;
  padding: 5px 9px;
  width: fit-content;
  font-size: 9px;
  font-weight: 700;
  background: rgba(255, 190, 92, 0.14);
  color: var(--toy-text-main);
}

.toy-slot-activity.is-ready {
  background: rgba(58, 197, 110, 0.16);
  color: #20a254;
}

.toy-slot-activity.is-early {
  background: rgba(255, 184, 77, 0.2);
  color: #ca7a00;
}

.toy-slot-activity.is-blocked,
.toy-slot-activity.is-cooldown {
  background: rgba(146, 152, 176, 0.14);
  color: var(--toy-text-soft);
}

.toy-target-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 10px;
}

.toy-target-panel {
  display: grid;
  gap: 8px;
}

.toy-slot-foot {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  align-content: flex-end;
}

.toy-slot-action-btn,
.toy-remote-action {
  width: auto;
}

.toy-card-action,
.toy-slot-action-btn,
.toy-remote-action {
  min-height: 32px;
  border-radius: 10px;
  font-weight: 700;
}

.toy-slot-action-btn {
  min-width: 92px;
  margin-left: auto;
}

.toy-remote-action {
  min-width: 72px;
  margin-left: auto;
}

.toy-empty {
  padding: 18px 12px;
  border: 1px dashed var(--toy-border);
  border-radius: 18px;
  text-align: center;
  color: var(--toy-text-soft);
  font-size: 12px;
}

.toy-history-item {
  position: relative;
  overflow: hidden;
  padding: 15px 16px 14px 18px;
  border-radius: 20px;
  border: 1px solid var(--toy-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%), var(--toy-panel-strong);
}

.toy-history-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, rgba(124, 92, 255, 0.54) 0%, rgba(99, 102, 241, 0.18) 100%);
}

.toy-history-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.toy-history-top strong {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  line-height: 1.45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toy-history-top span {
  flex-shrink: 0;
  white-space: nowrap;
  font-size: 12px;
  color: var(--toy-text-soft);
}

.toy-history-lines {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--toy-text-soft);
}

@media (max-width: 1100px) {
  .toy-hero {
    grid-template-columns: 1fr;
  }

  .toy-action-grid {
    justify-content: flex-start;
  }

  .toy-overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .toy-shell {
    padding: 14px 10px 20px;
  }

  .toy-hero,
  .toy-panel {
    padding: 18px;
  }

  .toy-title {
    font-size: 30px;
  }

  .toy-panel-head h2 {
    font-size: 20px;
  }

  .toy-overview-grid,
  .toy-box-grid {
    grid-template-columns: 1fr;
  }

  .toy-cabinet-grid {
    grid-template-columns: repeat(auto-fit, minmax(126px, 1fr));
  }

  .toy-panel-booth .toy-slot-grid {
    grid-template-columns: repeat(auto-fit, minmax(162px, 1fr));
  }

  .toy-panel-target .toy-slot-grid,
  .toy-remote-grid {
    grid-template-columns: repeat(auto-fit, minmax(154px, 1fr));
  }

  .toy-section-tools,
  .toy-toolbar {
    justify-content: flex-start;
  }

  .toy-history-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}

.toy-cabinet-grid > *,
.toy-slot-grid > *,
.toy-remote-grid > * {
  min-width: 0;
}
</style>
