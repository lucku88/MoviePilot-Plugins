<template>
  <div ref="rootEl" class="toy-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="toy-shell">
      <section class="toy-hero">
        <div class="toy-copy">
          <div class="toy-badge">SQ玩偶</div>
          <h1 class="toy-title">{{ toy.title || '玩偶抢曝光' }}</h1>
          <p class="toy-subtitle">{{ toy.subtitle || '盲盒、回收、展出、获取执行记录。' }}</p>
          <div class="toy-hero-meta">
            <span>最近执行 {{ status.last_run || '暂无' }}</span>
            <span>下次运行 {{ toy.next_run_time || '等待刷新' }}</span>
            <span>{{ toy.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>
        <div class="toy-actions">
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
        <article v-for="item in overview" :key="item.label" class="toy-overview-card">
          <div class="toy-overview-label">{{ item.label }}</div>
          <div class="toy-overview-value">{{ item.value }}</div>
          <div v-if="item.desc" class="toy-overview-desc">{{ item.desc }}</div>
          <div v-if="item.extra" class="toy-overview-desc">{{ item.extra }}</div>
        </article>
      </section>

      <section v-if="showSummary" class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>任务结果</h2>
          </div>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="toy-summary-list">
          <div v-for="line in summaryLines" :key="line" class="toy-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="toy-panel">
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

      <section class="toy-panel">
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

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>玩偶柜子</h2>
          </div>
        </div>
        <div class="toy-toolbar">
          <div class="toy-sort-group">
            <span>按级别</span>
            <button type="button" class="toy-chip" @click="setSort('quality_rank', 'desc')">高→低</button>
            <button type="button" class="toy-chip" @click="setSort('quality_rank', 'asc')">低→高</button>
          </div>
          <div class="toy-sort-group">
            <span>按可用数量</span>
            <button type="button" class="toy-chip" @click="setSort('available', 'desc')">多→少</button>
            <button type="button" class="toy-chip" @click="setSort('available', 'asc')">少→多</button>
          </div>
          <div class="toy-sort-group">
            <span>按最快冷却</span>
            <button type="button" class="toy-chip" @click="setSort('cooling_count', 'asc')">短→长</button>
            <button type="button" class="toy-chip" @click="setSort('cooling_count', 'desc')">长→短</button>
          </div>
        </div>
        <div class="toy-selected-bar">
          <span>当前选中：</span>
          <strong>{{ selectedDoll ? selectedDoll.name : '未选择玩偶' }}</strong>
          <span v-if="selectedDoll">，点击空展位或目标空位即可上架</span>
        </div>
        <div v-if="!cabinetCards.length" class="toy-empty">暂无可用空位或玩偶，稍后再试</div>
        <div v-else class="toy-cabinet-grid">
          <article
            v-for="doll in cabinetCards"
            :key="doll.doll_key || doll.name"
            class="toy-doll-card"
            :class="{ selected: selectedDollKey === doll.doll_key, disabled: !doll.can_place }"
            @click="selectDoll(doll)"
          >
            <img v-if="doll.image" class="toy-doll-image" :src="doll.image" :alt="doll.name" />
            <div v-else class="toy-doll-placeholder">🧸</div>
            <div class="toy-doll-quality">{{ doll.quality || '未识别' }}</div>
            <div class="toy-doll-name">{{ doll.name }}</div>
            <div class="toy-doll-meta">{{ doll.display_text }}</div>
            <div class="toy-doll-meta">{{ doll.reward_text }}</div>
            <div class="toy-doll-meta">{{ doll.origin }}</div>
            <div class="toy-doll-count">可用/总数 {{ doll.available }} / {{ doll.total }}</div>
            <div class="toy-doll-count">展出{{ doll.display_count }} · 冷却{{ doll.cooling_count }}</div>
            <div v-if="cabinetCooldownText(doll)" class="toy-doll-cooldown">{{ cabinetCooldownText(doll) }}</div>
            <v-btn block size="small" color="deep-orange" variant="flat" :disabled="!doll.can_place" class="mt-3">
              {{ selectedDollKey === doll.doll_key ? '已选择' : '选择上架' }}
            </v-btn>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>我的展柜</h2>
          </div>
        </div>
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
              <div class="toy-slot-empty">空展位</div>
              <div class="toy-slot-tip">{{ selectedDoll ? `可上架 ${selectedDoll.name}` : '先从玩偶柜子选择玩偶' }}</div>
              <v-btn color="deep-orange" variant="flat" :disabled="!selectedDoll || loading" @click="placePersonal(slot)">上架所选玩偶</v-btn>
            </template>
            <template v-else>
              <div class="toy-slot-media">
                <img v-if="slot.image" class="toy-slot-image" :src="slot.image" :alt="slot.doll_name" />
                <div v-else class="toy-slot-empty">🧸</div>
              </div>
              <div class="toy-slot-name">{{ slot.doll_name }}</div>
              <div v-if="slot.owner_name" class="toy-slot-owner">{{ slot.owner_name }}</div>
              <div class="toy-slot-meta">{{ slotRemainText(slot) }}</div>
              <div class="toy-slot-meta">{{ slot.reward_text }}</div>
              <div class="toy-slot-progress"><div class="toy-slot-progress-bar" :style="{ width: `${slot.progress}%` }" /></div>
              <div class="toy-slot-activity" :class="`is-${slotActionKind(slot)}`">{{ slotActivityText(slot) }}</div>
              <v-btn
                :color="slotActionColor(slot)"
                variant="flat"
                :loading="loading"
                :disabled="loading || !slot.viewer_is_occupant"
                @click="collectSlot(slot)"
              >
                {{ slotActionLabel(slot) }}
              </v-btn>
            </template>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>抢占他人展位</h2>
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
          <div class="toy-target-head">{{ targetPanel.username }} · {{ targetPanel.slot_count }} 个展位</div>
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
                <div class="toy-slot-empty">空位可抢</div>
                <div class="toy-slot-tip">{{ selectedDoll ? `抢占为 ${selectedDoll.name}` : '先选择玩偶' }}</div>
                <v-btn color="deep-orange" variant="flat" :disabled="!selectedDoll || loading" @click="placeTarget(slot)">抢占展位</v-btn>
              </template>
              <template v-else-if="slot.empty && slot.cooldown_active">
                <div class="toy-slot-empty">⏳</div>
                <div class="toy-slot-tip">展位冷却中</div>
                <v-btn color="grey-darken-1" variant="flat" disabled>冷却中</v-btn>
              </template>
              <template v-else>
                <div class="toy-slot-media">
                  <img v-if="slot.image" class="toy-slot-image" :src="slot.image" :alt="slot.doll_name" />
                  <div v-else class="toy-slot-empty">🧸</div>
                </div>
                <div class="toy-slot-name">{{ slot.doll_name || slot.status_text }}</div>
                <div v-if="slot.owner_name" class="toy-slot-owner">{{ slot.owner_name }}</div>
                <div class="toy-slot-meta">{{ targetRemainText(slot) }}</div>
                <div v-if="slot.reward_text" class="toy-slot-meta">{{ slot.reward_text }}</div>
                <div class="toy-slot-progress"><div class="toy-slot-progress-bar" :style="{ width: `${slot.progress}%` }" /></div>
                <div class="toy-slot-activity" :class="`is-${slotActionKind(slot)}`">{{ slotActivityText(slot) }}</div>
                <v-btn
                  :color="targetSlotActionColor(slot)"
                  variant="flat"
                  :disabled="loading || !slot.viewer_is_occupant"
                  @click="collectSlot(slot)"
                >
                  {{ targetSlotActionLabel(slot) }}
                </v-btn>
              </template>
            </article>
          </div>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>我的外展记录</h2>
          </div>
        </div>
        <div v-if="!remoteRecords.length" class="toy-empty">暂无外展记录</div>
        <div v-else class="toy-remote-grid">
          <article v-for="item in remoteRecords" :key="`${item.owner_id}-${item.slot_index}`" class="toy-remote-card">
            <img v-if="item.image" class="toy-remote-image" :src="item.image" :alt="item.doll_name" />
            <div class="toy-remote-owner">{{ item.owner_name }}</div>
            <div class="toy-remote-meta">展位 {{ item.slot_index }}</div>
            <div class="toy-remote-meta">{{ item.doll_name }}</div>
            <div class="toy-remote-meta">{{ remoteRemainText(item) }}</div>
            <v-btn size="small" variant="flat" color="primary" :disabled="loading" @click="viewTarget(item.owner_id)">查看</v-btn>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="toy-empty">暂无执行历史</div>
        <div v-else class="toy-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="toy-history-item">
            <div class="toy-history-top">
              <strong>{{ item.title || '任务结果' }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div class="toy-history-lines">{{ (item.lines || []).join(' / ') }}</div>
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

const pluginBase = '/plugin/SQToy'
const loading = ref(false)
const rootEl = ref(null)
const status = reactive({ toy_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const targetKeyword = ref('')
const selectedDollKey = ref('')
const sortField = ref('cooling_count')
const sortDirection = ref('asc')
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
const overview = computed(() => toy.value.overview || [])
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

const cabinetCards = computed(() => {
  const items = [...(toy.value.cabinet || [])]
  return items.sort((left, right) => {
    const field = sortField.value
    const lv = Number(left[field] || 0)
    const rv = Number(right[field] || 0)
    if (lv === rv) return String(left.name || '').localeCompare(String(right.name || ''))
    return sortDirection.value === 'desc' ? rv - lv : lv - rv
  })
})

const selectedDoll = computed(() => cabinetCards.value.find((item) => item.doll_key === selectedDollKey.value) || null)

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
  dismissedSummaryKey.value = window.sessionStorage.getItem('sqtoy-summary-dismissed') || ''
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

function setSort(field, direction) {
  sortField.value = field
  sortDirection.value = direction
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('sqtoy-summary-dismissed', key)
    } else {
      window.sessionStorage.removeItem('sqtoy-summary-dismissed')
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
  --toy-bg-start: #ffffff;
  --toy-bg-end: #eef1f7;
  --toy-panel: rgba(255, 255, 255, 0.9);
  --toy-panel-strong: rgba(255, 255, 255, 0.98);
  --toy-border: rgba(129, 133, 164, 0.18);
  --toy-chip: rgba(124, 92, 255, 0.1);
  --toy-text-main: #262638;
  --toy-text-soft: rgba(118, 119, 139, 0.92);
  --toy-shadow: 0 20px 48px rgba(121, 128, 166, 0.12);
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.95) 0%, rgba(246, 247, 250, 0.98) 42%, #eef1f7 100%),
    linear-gradient(180deg, var(--toy-bg-start) 0%, var(--toy-bg-end) 100%);
  color: var(--toy-text-main);
}

.toy-page.is-dark-theme {
  --toy-bg-start: #212534;
  --toy-bg-end: #14161f;
  --toy-panel: rgba(26, 28, 39, 0.92);
  --toy-panel-strong: rgba(19, 21, 30, 0.98);
  --toy-border: rgba(124, 92, 255, 0.18);
  --toy-chip: rgba(139, 108, 255, 0.14);
  --toy-text-main: #f3f5ff;
  --toy-text-soft: rgba(159, 167, 196, 0.92);
  --toy-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  background:
    radial-gradient(circle at top, rgba(33, 37, 52, 0.92) 0%, rgba(23, 26, 36, 0.98) 38%, #14161f 100%),
    linear-gradient(180deg, var(--toy-bg-start) 0%, var(--toy-bg-end) 100%);
}

.toy-page,
.toy-page * {
  box-sizing: border-box;
}

.toy-shell {
  max-width: 1320px;
  margin: 0 auto;
  padding: 18px 16px 24px;
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
  border-radius: 28px;
  background: var(--toy-panel);
  box-shadow: var(--toy-shadow);
  backdrop-filter: blur(18px);
}

.toy-hero,
.toy-panel {
  padding: 20px 22px;
}

.toy-hero {
  display: grid;
  grid-template-columns: 1.4fr auto;
  gap: 20px;
  align-items: center;
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
  color: #8b6cff;
}

.toy-title {
  margin: 10px 0 6px;
  font-size: clamp(30px, 3.8vw, 42px);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.toy-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--toy-text-soft);
}

.toy-hero-meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toy-hero-meta span {
  padding: 7px 11px;
  border-radius: 999px;
  background: var(--toy-panel-strong);
  border: 1px solid var(--toy-border);
  font-size: 12px;
  color: var(--toy-text-soft);
}

.toy-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  align-items: center;
}

.toy-overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.toy-overview-card {
  padding: 16px;
  text-align: center;
}

.toy-overview-label,
.toy-panel-kicker {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--toy-text-soft);
}

.toy-overview-value {
  font-size: 30px;
  font-weight: 800;
  margin: 8px 0;
}

.toy-overview-desc {
  margin: 6px auto 0;
  padding: 7px 12px;
  background: var(--toy-chip);
  color: var(--toy-text-main);
  font-size: 12px;
}

.toy-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.toy-panel-head h2 {
  margin: 0;
  font-size: 24px;
}

.toy-summary-list,
.toy-history-list {
  display: grid;
  gap: 12px;
}

.toy-summary-line,
.toy-history-item {
  padding: 12px 14px;
  border: 1px solid var(--toy-border);
  border-radius: 18px;
  background: var(--toy-panel-strong);
}

.toy-box-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
}

.toy-box-card {
  padding: 16px;
  text-align: center;
  background: var(--toy-panel-strong);
}

.toy-box-card.locked,
.toy-doll-card.disabled {
  opacity: 0.7;
}

.toy-box-card.compact {
  padding: 16px;
}

.toy-box-image {
  width: 108px;
  height: 148px;
  object-fit: contain;
  margin: 0 auto 12px;
  display: block;
}

.toy-box-image.small {
  width: 82px;
  height: 108px;
}

.toy-box-name {
  font-size: 18px;
  font-weight: 800;
}

.toy-box-desc {
  margin-top: 8px;
  font-size: 13px;
  color: var(--toy-text-soft);
  min-height: 36px;
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

.toy-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: 12px;
}

.toy-sort-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.toy-chip {
  border: 1px solid var(--toy-border);
  padding: 8px 12px;
  background: var(--toy-panel-strong);
  color: inherit;
  cursor: pointer;
  font-size: 13px;
}

.toy-selected-bar {
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 16px;
  background: var(--toy-panel-strong);
  border: 1px solid var(--toy-border);
}

.toy-cabinet-grid,
.toy-slot-grid,
.toy-remote-grid {
  display: grid;
  gap: 16px;
}

.toy-cabinet-grid {
  grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
}

.toy-slot-grid {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.toy-remote-grid {
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
}

.toy-doll-card,
.toy-slot-card,
.toy-remote-card {
  padding: 15px;
  text-align: center;
  background: var(--toy-panel-strong);
}

.toy-doll-card.selected {
  outline: 2px solid rgba(124, 92, 255, 0.75);
}

.toy-slot-card.is-stolen {
  border-color: rgba(255, 145, 111, 0.42);
}

.toy-slot-card.is-ready {
  border-color: rgba(58, 197, 110, 0.34);
}

.toy-doll-image,
.toy-slot-image,
.toy-remote-image {
  width: 96px;
  height: 96px;
  object-fit: contain;
  margin: 0 auto;
  display: block;
}

.toy-slot-media {
  width: 96px;
  height: 96px;
  margin: 0 auto 10px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: rgba(255, 190, 92, 0.1);
}

.toy-doll-placeholder,
.toy-slot-empty {
  width: 88px;
  height: 88px;
  margin: 0 auto 10px;
  display: grid;
  place-items: center;
  font-size: 36px;
  background: rgba(255, 190, 92, 0.1);
  border-radius: 18px;
}

.toy-doll-quality {
  margin: 0 auto 10px;
  padding: 6px 12px;
  background: var(--toy-chip);
  font-size: 12px;
  font-weight: 700;
}

.toy-doll-name,
.toy-slot-name,
.toy-remote-owner {
  font-size: 18px;
  font-weight: 800;
}

.toy-slot-owner {
  margin-top: 6px;
  font-size: 14px;
  font-weight: 700;
  color: #ff5e8a;
}

.toy-doll-meta,
.toy-slot-meta,
.toy-remote-meta,
.toy-doll-count,
.toy-slot-tip,
.toy-history-time {
  margin-top: 6px;
  font-size: 12px;
  color: var(--toy-text-soft);
}

.toy-doll-cooldown {
  margin-top: 10px;
  padding: 7px 12px;
  background: rgba(126, 126, 126, 0.16);
  font-size: 12px;
}

.toy-history-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
  font-size: 13px;
}

.toy-history-lines,
.toy-history-top span {
  font-size: 12px;
  color: var(--toy-text-soft);
}

.toy-slot-index {
  padding: 6px 12px;
  background: var(--toy-chip);
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 10px;
}

.toy-slot-progress {
  margin: 12px 0 10px;
  height: 7px;
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
  margin: 0 auto 12px;
  padding: 7px 12px;
  font-size: 12px;
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
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.toy-target-panel {
  display: grid;
  gap: 14px;
}

.toy-target-head {
  font-size: 18px;
  font-weight: 800;
}

.toy-history-message {
  font-size: 15px;
}

.toy-history-time {
  margin-top: 8px;
}

.toy-empty {
  padding: 22px 14px;
  border: 1px dashed var(--toy-border);
  border-radius: 18px;
  text-align: center;
  color: var(--toy-text-soft);
}

@media (max-width: 1100px) {
  .toy-hero {
    grid-template-columns: 1fr;
  }

  .toy-actions {
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
    font-size: 32px;
  }

  .toy-panel-head h2 {
    font-size: 24px;
  }

  .toy-overview-grid {
    grid-template-columns: 1fr;
  }

  .toy-box-grid,
  .toy-cabinet-grid,
  .toy-slot-grid,
  .toy-remote-grid {
    grid-template-columns: 1fr;
  }
}
</style>
