<template>
  <div ref="rootEl" class="toy-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="toy-shell">
      <section class="toy-hero">
        <div class="toy-copy">
          <div class="toy-badge">SQ玩偶</div>
          <h1 class="toy-title">{{ toy.title || '玩偶抢曝光' }}</h1>
          <p class="toy-subtitle">{{ toy.subtitle || '盲盒抽玩偶、自动回收、个人展位与外展抢位。' }}</p>
          <div class="toy-hero-meta">
            <span>最近执行 {{ status.last_run || '暂无' }}</span>
            <span>下次运行 {{ toy.next_run_time || '等待刷新' }}</span>
            <span>Cookie {{ toy.cookie_source || status.cookie_source || '未同步' }}</span>
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
            <div class="toy-panel-kicker">本次摘要</div>
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
            <div class="toy-panel-kicker">盲盒商店</div>
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
            <div class="toy-panel-kicker">我的盲盒</div>
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
            <div class="toy-panel-kicker">玩偶柜子</div>
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
            <div v-if="doll.cooldown_text" class="toy-doll-cooldown">{{ doll.cooldown_text }}</div>
            <v-btn block size="small" color="deep-orange" variant="flat" :disabled="!doll.can_place" class="mt-3">
              {{ selectedDollKey === doll.doll_key ? '已选择' : '选择上架' }}
            </v-btn>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <div class="toy-panel-kicker">我的展柜</div>
            <h2>我的展柜</h2>
          </div>
        </div>
        <div class="toy-slot-grid">
          <article v-for="slot in personalSlots" :key="`personal-${slot.slot_index}`" class="toy-slot-card" :class="{ empty: slot.empty }">
            <div class="toy-slot-index">展位 {{ slot.slot_index }}</div>
            <template v-if="slot.empty">
              <div class="toy-slot-empty">空展位</div>
              <div class="toy-slot-tip">{{ selectedDoll ? `可上架 ${selectedDoll.name}` : '先从玩偶柜子选择玩偶' }}</div>
              <v-btn color="deep-orange" variant="flat" :disabled="!selectedDoll || loading" @click="placePersonal(slot)">上架所选玩偶</v-btn>
            </template>
            <template v-else>
              <img v-if="slot.image" class="toy-slot-image" :src="slot.image" :alt="slot.doll_name" />
              <div class="toy-slot-name">{{ slot.doll_name }}</div>
              <div class="toy-slot-meta">{{ slot.remaining_text }}</div>
              <div class="toy-slot-meta">{{ slot.reward_text }}</div>
              <div class="toy-slot-progress"><div class="toy-slot-progress-bar" :style="{ width: `${slot.progress}%` }" /></div>
              <v-btn
                color="primary"
                variant="flat"
                :loading="loading"
                @click="collectSlot(slot)"
              >
                {{ slot.can_collect ? '收回玩偶' : '尝试收回' }}
              </v-btn>
            </template>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <div class="toy-panel-kicker">外展抢位</div>
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
            <article v-for="slot in targetPanel.slots" :key="`target-${slot.owner_id}-${slot.slot_index}`" class="toy-slot-card" :class="{ empty: slot.empty }">
              <div class="toy-slot-index">展位 {{ slot.slot_index }}</div>
              <template v-if="slot.empty && !slot.cooldown_active">
                <div class="toy-slot-empty">空位可抢</div>
                <div class="toy-slot-tip">{{ selectedDoll ? `抢占为 ${selectedDoll.name}` : '先选择玩偶' }}</div>
                <v-btn color="deep-orange" variant="flat" :disabled="!selectedDoll || loading" @click="placeTarget(slot)">抢占展位</v-btn>
              </template>
              <template v-else>
                <div class="toy-slot-name">{{ slot.doll_name || slot.state_text }}</div>
                <div class="toy-slot-meta">{{ slot.remaining_text }}</div>
                <div class="toy-slot-meta">{{ slot.state_text }}</div>
                <v-btn v-if="slot.viewer_is_occupant" color="primary" variant="flat" :disabled="loading" @click="collectSlot(slot)">
                  {{ slot.can_collect ? '收回玩偶' : '尝试收回' }}
                </v-btn>
              </template>
            </article>
          </div>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <div class="toy-panel-kicker">外展记录</div>
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
            <div class="toy-remote-meta">{{ item.remaining_text }}</div>
            <v-btn size="small" variant="flat" color="primary" :disabled="loading" @click="viewTarget(item.owner_id)">查看</v-btn>
          </article>
        </div>
      </section>

      <section class="toy-panel">
        <div class="toy-panel-head">
          <div>
            <div class="toy-panel-kicker">最近记录</div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyLogs.length" class="toy-empty">暂无执行历史</div>
        <div v-else class="toy-history-list">
          <article v-for="item in historyLogs" :key="`${item.time}-${item.message}`" class="toy-history-item">
            <div class="toy-history-message">{{ item.message }}</div>
            <div class="toy-history-time">{{ item.time }}</div>
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
const isDarkTheme = ref(false)
const dismissedSummaryKey = ref('')

let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

const toy = computed(() => status.toy_status || {})
const overview = computed(() => toy.value.overview || [])
const shopBoxes = computed(() => toy.value.shop_boxes || [])
const myBoxes = computed(() => toy.value.my_boxes || [])
const personalSlots = computed(() => toy.value.personal_slots || [])
const targetPanel = computed(() => toy.value.target_panel || {})
const remoteRecords = computed(() => toy.value.remote_records || [])
const historyLogs = computed(() => toy.value.history_logs || [])
const summaryLines = computed(() => (toy.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)

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
    status.toy_status.target_panel = payload.target_panel
  }
}

async function loadStatus() {
  const data = await props.api.get(`${pluginBase}/status`)
  Object.assign(status, data || {})
}

async function withAction(action, fallback) {
  loading.value = true
  try {
    const result = await action()
    applyPayload(result || {})
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
  dismissedSummaryKey.value = summaryKey.value
  sessionStorage.setItem('sqtoy-summary-dismissed', dismissedSummaryKey.value)
}

function closePlugin() {
  emit('close')
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
  if (darkThemes.has(themeValue)) {
    isDarkTheme.value = true
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindTheme() {
  detectTheme()
  observedThemeNode = findThemeNode()
  if (observedThemeNode && window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] })
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
}

onMounted(async () => {
  dismissedSummaryKey.value = sessionStorage.getItem('sqtoy-summary-dismissed') || ''
  bindTheme()
  await loadStatus()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.toy-page { min-height: 100vh; background: linear-gradient(180deg, #fff8f1 0%, #f7efe8 100%); color: #402616; }
.toy-page.is-dark-theme { background: linear-gradient(180deg, #141313 0%, #1b1716 100%); color: #f7ebdf; }
.toy-shell { max-width: 1480px; margin: 0 auto; padding: 20px 16px 40px; display: grid; gap: 18px; }
.toy-hero, .toy-panel, .toy-overview-card, .toy-box-card, .toy-doll-card, .toy-slot-card, .toy-remote-card, .toy-history-item {
  border: 1px solid rgba(255, 165, 93, 0.28); border-radius: 24px; background: rgba(255,255,255,0.82);
  box-shadow: 0 18px 48px rgba(255, 166, 102, 0.08);
}
.is-dark-theme .toy-hero, .is-dark-theme .toy-panel, .is-dark-theme .toy-overview-card, .is-dark-theme .toy-box-card, .is-dark-theme .toy-doll-card, .is-dark-theme .toy-slot-card, .is-dark-theme .toy-remote-card, .is-dark-theme .toy-history-item {
  background: rgba(27, 24, 22, 0.88); box-shadow: none; border-color: rgba(255, 171, 111, 0.16);
}
.toy-hero, .toy-panel { padding: 22px; }
.toy-hero { display: grid; grid-template-columns: 1.5fr auto; gap: 20px; align-items: center; }
.toy-badge, .toy-chip, .toy-overview-desc, .toy-doll-quality, .toy-doll-cooldown, .toy-slot-index {
  display: inline-flex; align-items: center; justify-content: center; border-radius: 999px;
}
.toy-badge { padding: 6px 12px; font-size: 13px; font-weight: 700; background: rgba(255, 155, 72, 0.18); color: #d96a21; }
.toy-title { margin: 12px 0 8px; font-size: 42px; line-height: 1.05; }
.toy-subtitle { margin: 0; font-size: 15px; opacity: 0.86; }
.toy-hero-meta { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 10px 18px; font-size: 13px; opacity: 0.78; }
.toy-actions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; align-items: center; }
.toy-overview-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.toy-overview-card { padding: 20px; text-align: center; }
.toy-overview-label, .toy-panel-kicker { font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.72; }
.toy-overview-value { font-size: 38px; font-weight: 800; margin: 10px 0; }
.toy-overview-desc { margin: 6px auto 0; padding: 6px 12px; background: rgba(255, 164, 88, 0.12); color: inherit; font-size: 12px; }
.toy-panel-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 18px; }
.toy-panel-head h2 { margin: 8px 0 0; font-size: 32px; }
.toy-summary-list, .toy-history-list { display: grid; gap: 12px; }
.toy-summary-line, .toy-history-item { padding: 16px 18px; }
.toy-box-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.toy-box-card { padding: 18px; text-align: center; }
.toy-box-card.locked { opacity: 0.68; }
.toy-box-card.compact { padding: 16px; }
.toy-box-image { width: 112px; height: 150px; object-fit: contain; margin: 0 auto 12px; display: block; }
.toy-box-image.small { width: 84px; height: 112px; }
.toy-box-name { font-size: 22px; font-weight: 800; }
.toy-box-desc { margin-top: 10px; font-size: 14px; opacity: 0.82; min-height: 42px; }
.toy-box-lock { display: block; margin-top: 8px; color: #da6b3a; font-size: 13px; }
.toy-box-actions, .toy-search { display: flex; gap: 10px; align-items: center; justify-content: center; margin-top: 16px; }
.toy-number-input, .toy-text-input {
  width: 100%; min-width: 0; border: 1px solid rgba(255, 165, 93, 0.35); background: rgba(255,255,255,0.72);
  color: inherit; border-radius: 12px; padding: 10px 12px; outline: none;
}
.is-dark-theme .toy-number-input, .is-dark-theme .toy-text-input { background: rgba(255,255,255,0.04); }
.toy-toolbar { display: flex; flex-wrap: wrap; gap: 12px 24px; margin-bottom: 14px; }
.toy-sort-group { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.toy-chip { border: 0; padding: 8px 12px; background: rgba(255, 166, 84, 0.14); color: inherit; cursor: pointer; font-size: 13px; }
.toy-selected-bar { margin-bottom: 16px; padding: 12px 16px; border-radius: 16px; background: rgba(255, 165, 93, 0.08); }
.toy-cabinet-grid, .toy-slot-grid, .toy-remote-grid { display: grid; gap: 16px; }
.toy-cabinet-grid { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
.toy-slot-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.toy-remote-grid { grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
.toy-doll-card, .toy-slot-card, .toy-remote-card { padding: 18px; text-align: center; }
.toy-doll-card.selected { outline: 2px solid rgba(255, 150, 62, 0.8); }
.toy-doll-card.disabled { opacity: 0.75; }
.toy-doll-image, .toy-slot-image, .toy-remote-image { width: 96px; height: 96px; object-fit: contain; margin: 0 auto 12px; display: block; }
.toy-doll-placeholder, .toy-slot-empty { width: 96px; height: 96px; margin: 0 auto 12px; display: grid; place-items: center; font-size: 40px; background: rgba(255, 164, 88, 0.08); border-radius: 20px; }
.toy-doll-quality { margin: 0 auto 10px; padding: 6px 12px; background: rgba(255, 166, 84, 0.2); font-size: 12px; font-weight: 700; }
.toy-doll-name, .toy-slot-name, .toy-remote-owner { font-size: 22px; font-weight: 800; }
.toy-doll-meta, .toy-slot-meta, .toy-remote-meta, .toy-doll-count, .toy-slot-tip, .toy-history-time { margin-top: 8px; font-size: 13px; opacity: 0.8; }
.toy-doll-cooldown { margin-top: 10px; padding: 7px 12px; background: rgba(126, 126, 126, 0.18); font-size: 12px; }
.toy-slot-index { padding: 6px 12px; background: rgba(255, 166, 84, 0.14); font-size: 12px; font-weight: 700; margin-bottom: 14px; }
.toy-slot-progress { margin: 14px 0; height: 8px; border-radius: 999px; background: rgba(255, 165, 93, 0.14); overflow: hidden; }
.toy-slot-progress-bar { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #ffb56f 0%, #ff8747 100%); }
.toy-target-controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 16px; }
.toy-target-panel { display: grid; gap: 14px; }
.toy-target-head { font-size: 18px; font-weight: 800; }
.toy-history-message { font-size: 15px; }
.toy-history-time { margin-top: 8px; }
.toy-empty { padding: 28px 16px; border: 1px dashed rgba(255, 165, 93, 0.4); border-radius: 18px; text-align: center; opacity: 0.76; }

@media (max-width: 1100px) {
  .toy-hero { grid-template-columns: 1fr; }
  .toy-actions { justify-content: flex-start; }
  .toy-overview-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 640px) {
  .toy-shell { padding: 14px 10px 28px; }
  .toy-title { font-size: 32px; }
  .toy-panel-head h2 { font-size: 26px; }
  .toy-overview-grid { grid-template-columns: 1fr; }
  .toy-box-grid, .toy-cabinet-grid, .toy-slot-grid, .toy-remote-grid { grid-template-columns: 1fr; }
}
</style>
