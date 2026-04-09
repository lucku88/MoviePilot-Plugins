<template>
  <div ref="rootEl" class="emoji-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="emoji-shell">
      <section class="emoji-hero">
        <div class="emoji-copy">
          <div class="emoji-badge">SQ表情</div>
          <h1 class="emoji-title">{{ emoji.title || '表情演出' }}</h1>
          <p class="emoji-subtitle">
            {{ emoji.subtitle || '老虎机、开包、舞台演出、获取执行记录。' }}
          </p>
          <div class="emoji-hero-meta">
            <span class="emoji-meta-chip">最近执行 {{ status.last_run || '暂无' }}</span>
            <span class="emoji-meta-chip">下次运行 {{ emoji.next_run_time || status.next_run_time || '等待刷新' }}</span>
            <span class="emoji-meta-chip">{{ emoji.cookie_source || status.cookie_source || '未同步' }}</span>
          </div>
        </div>
        <div class="emoji-actions">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="switchToConfig">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="emoji-stat-grid">
        <article v-for="item in statsItems" :key="item.label" class="emoji-stat-card">
          <div class="emoji-stat-label">{{ item.label }}</div>
          <div class="emoji-stat-value">{{ item.value }}</div>
          <div v-if="item.desc" class="emoji-stat-desc">{{ item.desc }}</div>
        </article>
      </section>

      <section v-if="showSummary" class="emoji-panel">
        <div class="emoji-section-head emoji-section-head-compact">
          <h2 class="emoji-section-title">✨ 本次摘要</h2>
          <v-btn variant="text" size="small" @click="dismissSummary">关闭</v-btn>
        </div>
        <div class="emoji-summary-list">
          <div v-for="line in summaryLines" :key="line" class="emoji-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-section-head">
          <h2 class="emoji-section-title">🎰 表情老虎机</h2>
          <div class="emoji-panel-note">
            今日次数：{{ slotMachine.used || 0 }}/{{ slotMachine.limit || 0 }}
            <span v-if="slotMachine.base || slotMachine.extra">
              （基础{{ slotMachine.base || 0 }} + f(hnr*等级) {{ slotMachine.extra || 0 }}）
            </span>
          </div>
        </div>
        <div class="slot-layout">
          <div class="slot-reels">
            <div v-for="(item, index) in slotMachine.reels || []" :key="`reel-${index}`" class="slot-cell">
              {{ item }}
            </div>
          </div>
          <div class="slot-actions">
            <input
              v-model="spinCount"
              class="emoji-number-input"
              type="number"
              min="1"
              :max="Math.max(spinMax, 1)"
            />
            <v-btn
              color="deep-orange"
              variant="flat"
              :loading="loading"
              :disabled="loading || !slotMachine.remaining"
              @click="spinSlot"
            >
              转动
            </v-btn>
          </div>
        </div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-section-head">
          <h2 class="emoji-section-title">🎒 我的表情包</h2>
        </div>
        <div class="emoji-bag-grid">
          <article
            v-for="bag in bags"
            :key="bag.tier"
            class="emoji-bag-card"
            :style="bagCardStyle(bag)"
          >
            <div
              v-if="bag.bg_image"
              class="emoji-bag-hero"
              :style="{ backgroundImage: `url(${bag.bg_image})` }"
            />
            <div class="emoji-bag-name" :style="{ color: bag.badge_color || '' }">{{ bag.name }}</div>
            <div class="emoji-bag-count">持有 {{ bag.quantity }}</div>

            <div class="emoji-inline-row">
              <input
                v-model="openCounts[bag.tier]"
                class="emoji-number-input"
                type="number"
                min="1"
                :max="Math.max(bag.open_max || 1, 1)"
              />
              <v-btn
                color="deep-orange"
                variant="flat"
                :loading="loading"
                :disabled="loading || !bag.can_open"
                @click="openBag(bag)"
              >
                开包
              </v-btn>
            </div>

            <template v-if="bag.upgrade_rule">
              <div class="emoji-upgrade-box">
                <div class="emoji-upgrade-row">
                  <span>目标数</span>
                  <input
                    v-model="upgradeCounts[bag.upgrade_rule.key]"
                    class="emoji-number-input"
                    type="number"
                    min="1"
                    :max="Math.max(bag.upgrade_rule.max_times || 1, 1)"
                  />
                  <v-btn
                    color="amber-darken-2"
                    variant="flat"
                    :loading="loading"
                    :disabled="loading || !bag.upgrade_rule.enabled"
                    @click="upgradeBag(bag)"
                  >
                    合成
                  </v-btn>
                </div>
                <div class="emoji-upgrade-tip">{{ bag.upgrade_rule.tip }}</div>
              </div>
            </template>
          </article>
        </div>

        <article v-if="pendingOpenVisible && pendingOpen.items?.length" class="emoji-pending-panel">
          <div class="emoji-section-head emoji-section-head-compact">
            <h3 class="emoji-subsection-title">📦 待处理开包结果</h3>
            <v-btn variant="text" size="small" @click="closePendingPanel">关闭</v-btn>
          </div>
          <div class="emoji-pending-meta">
            <span>{{ pendingOpen.bag_name }} x{{ pendingOpen.bag_count }}</span>
            <span>已重开 {{ pendingOpen.reroll_count || 0 }} 次</span>
            <span>下次重开消耗 {{ pendingOpen.next_reroll_cost || 0 }} 魔力</span>
          </div>
          <div class="emoji-result-grid" :class="{ single: pendingOpen.items.length === 1 }">
            <article v-for="(item, index) in pendingOpen.items" :key="`pending-${index}`" class="emoji-result-item">
              <div class="emoji-result-emoji">{{ item.emoji }}</div>
              <div class="emoji-result-attr">P{{ item.points }} · M{{ item.magic }}</div>
              <div class="emoji-result-owned">已有 {{ item.owned_count }}</div>
            </article>
          </div>
          <div class="emoji-result-actions">
            <v-btn color="primary" variant="flat" :loading="loading" @click="rerollPending">重开</v-btn>
            <v-btn color="success" variant="flat" :loading="loading" @click="acceptPending">收下</v-btn>
          </div>
        </article>
      </section>

      <section class="emoji-panel">
        <div class="emoji-section-head">
          <h2 class="emoji-section-title">📖 表情图鉴</h2>
        </div>

        <div class="emoji-tier-tabs">
          <button
            v-for="tab in actorTabs"
            :key="tab.tier"
            type="button"
            class="emoji-tier-chip"
            :class="{ active: String(selectedTier) === String(tab.tier) }"
            @click="selectedTier = String(tab.tier)"
          >
            {{ tab.name }} {{ tab.owned }}/{{ tab.total || '❓' }}
          </button>
        </div>

        <div class="emoji-sort-tabs">
          <button
            v-for="item in sortOptions"
            :key="item.key"
            type="button"
            class="emoji-sort-chip"
            :class="{ active: actorSort === item.key }"
            @click="actorSort = item.key"
          >
            {{ item.label }}
          </button>
        </div>

        <div v-if="!currentActors.length" class="emoji-empty">当前层级暂无可用演员</div>
        <div v-else class="emoji-actor-scroll">
          <div class="emoji-actor-grid">
            <button
              v-for="actor in visibleActors"
              :key="actor.code"
              type="button"
              class="emoji-actor-card"
              :disabled="stage.has_active || !actor.can_place || draftRemaining(actor.code) <= 0"
              @click="pickActor(actor)"
            >
              <div class="emoji-actor-main">{{ actor.emoji }}</div>
              <div class="emoji-actor-attr">P{{ actor.points }} · M{{ actor.magic }}</div>
              <div class="emoji-actor-count">x{{ draftRemaining(actor.code) }}</div>
            </button>
          </div>
        </div>
        <div v-if="hasMoreActors || actorVisibleLimit > actorLimitStep" class="emoji-actor-actions">
          <v-btn
            v-if="hasMoreActors"
            variant="tonal"
            color="primary"
            size="small"
            @click="showMoreActors"
          >
            显示更多 {{ remainingActorCount }} 个
          </v-btn>
          <v-btn
            v-if="actorVisibleLimit > actorLimitStep"
            variant="text"
            size="small"
            @click="collapseActors"
          >
            收起
          </v-btn>
        </div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-section-head">
          <h2 class="emoji-section-title">🎭 表情演出舞台</h2>
          <div class="emoji-stage-note">
            <span>当前舞台：{{ stage.current_effect_name || '未开始' }}</span>
            <span>{{ stage.current_text || '当前无演出演员' }}</span>
          </div>
        </div>

        <div class="emoji-effect-grid">
          <article
            v-for="effect in effects"
            :key="effect.key"
            class="emoji-effect-card"
            :class="{
              active: selectedEffect === effect.key,
              locked: !effect.unlocked,
            }"
            @click="selectEffect(effect)"
          >
            <div class="emoji-effect-title">{{ effect.name }}</div>
            <div class="emoji-effect-meta">积分+{{ effect.point_bonus_pct }}% · 魔力+{{ effect.magic_bonus_pct }}%</div>
            <div class="emoji-effect-meta">{{ effect.duration_text || `${effect.duration_seconds || 0} 秒` }}</div>
            <div class="emoji-effect-meta">{{ effect.unlocked ? '已解锁' : effect.unlock_text || '未解锁' }}</div>
          </article>
        </div>

        <div class="emoji-stage-toolbar">
          <div class="emoji-stage-toolbar-left">
            <span v-if="stage.has_active">演出剩余 {{ stageRemainText }}</span>
            <span v-else>当前效果 {{ selectedEffectName }}</span>
          </div>
          <div class="emoji-stage-toolbar-right">
            <v-btn
              color="warning"
              variant="flat"
              :disabled="loading || stage.has_active || !sortedActors.length"
              @click="fillCurrentTier"
            >
              一键放置当前层级
            </v-btn>
            <v-btn
              color="primary"
              variant="flat"
              :disabled="loading || !draftCount || stage.has_active"
              @click="confirmStage"
            >
              确认演出
            </v-btn>
            <v-btn
              color="success"
              variant="flat"
              :disabled="loading || !stage.has_active"
              @click="recallStage"
            >
              收回演出
            </v-btn>
          </div>
        </div>

        <div class="emoji-stage-rows">
          <article v-for="row in stageRows" :key="row.row_index" class="emoji-row-card">
            <div class="emoji-row-head">
              <div>
                <strong>{{ row.name }}</strong>
                <span>（解锁声誉 {{ row.unlock_points }}）</span>
              </div>
              <div>{{ row.unlocked ? `已开 ${row.slot_count}/${row.max_slots} 格` : '未解锁' }}</div>
            </div>

            <div class="emoji-row-actions">
              <v-btn
                v-if="row.unlocked"
                color="amber-darken-2"
                variant="flat"
                :loading="loading"
                :disabled="loading || !row.can_expand"
                @click="expandRow(row)"
              >
                扩展一格（{{ row.next_expand_cost || 0 }}魔力）
              </v-btn>
            </div>

            <div v-if="row.unlocked" class="emoji-stage-slot-grid">
              <button
                v-for="slot in row.slots"
                :key="`${row.row_index}-${slot.slot_index}`"
                type="button"
                class="emoji-stage-slot"
                :class="{
                  filled: slot.filled,
                  draft: !!draftMap[slotKey(slot)],
                  active: slot.filled,
                }"
                :style="stageSlotStyle(row, slot)"
                :title="stageSlotTitle(slot)"
                @click="handleStageSlot(row, slot)"
              >
                <template v-if="slot.filled">
                  <div class="emoji-stage-slot-emoji">{{ slot.emoji }}</div>
                  <div class="emoji-stage-slot-meta">P{{ slot.points }} · M{{ slot.magic }}</div>
                  <div class="emoji-stage-slot-time">{{ slotRemainText(slot) }}</div>
                </template>
                <template v-else-if="draftMap[slotKey(slot)]">
                  <div class="emoji-stage-slot-emoji">{{ draftMap[slotKey(slot)].emoji }}</div>
                  <div class="emoji-stage-slot-meta">
                    P{{ draftMap[slotKey(slot)].points }} · M{{ draftMap[slotKey(slot)].magic }}
                  </div>
                  <div class="emoji-stage-slot-time">点击撤回</div>
                </template>
                <template v-else>
                  <div class="emoji-stage-slot-empty">待定</div>
                </template>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="emoji-panel">
        <div class="emoji-section-head">
          <h2 class="emoji-section-title">🧾 最近记录</h2>
        </div>
        <div v-if="!historyItems.length" class="emoji-empty">暂无执行历史</div>
        <div v-else class="emoji-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="emoji-history-item">
            <div class="emoji-history-top">
              <strong>{{ item.title || '任务结果' }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div class="emoji-history-lines">{{ (item.lines || []).join(' / ') }}</div>
            <div v-if="item.next_run" class="emoji-history-next">下次运行 {{ item.next_run }}</div>
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

const pluginBase = '/plugin/SQEmoji'
const loading = ref(false)
const rootEl = ref(null)
const status = reactive({ emoji_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const isDarkTheme = ref(false)
const nowTs = ref(Math.floor(Date.now() / 1000))
const dismissedSummaryKey = ref('')
const hiddenPendingKey = ref('')
const actorLimitStep = 48
const actorVisibleLimit = ref(actorLimitStep)
const selectedTier = ref('1')
const selectedEffect = ref('basic')
const actorSort = ref('points_desc')
const spinCount = ref('1')
const lastRunAutoRefreshTs = ref(0)
const lastTriggerAutoRefreshTs = ref(0)
const lastStageRefreshTs = ref(0)

const openCounts = reactive({})
const upgradeCounts = reactive({})
const draftMap = reactive({})

let timer = null
let themeObserver = null
let mediaQuery = null
const refreshTimeouts = []

const emoji = computed(() => status.emoji_status || {})
const statsItems = computed(() => emoji.value.stats || [])
const slotMachine = computed(() => emoji.value.slot_machine || {})
const bags = computed(() => emoji.value.bags || [])
const pendingOpen = computed(() => emoji.value.pending_open || {})
const actorTabs = computed(() => emoji.value.actor_tabs || [])
const actorsByTier = computed(() => emoji.value.actors_by_tier || {})
const effects = computed(() => emoji.value.effects || [])
const stage = computed(() => emoji.value.stage || {})
const stageRows = computed(() => emoji.value.stage_rows || [])
const historyItems = computed(() => status.history || emoji.value.history || [])
const summaryLines = computed(() => (emoji.value.summary || []).filter(Boolean))
const summaryKey = computed(() => summaryLines.value.join('||'))
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value)
const nextRunTs = computed(() => Number(emoji.value.next_run_ts || 0) || parseDateTime(emoji.value.next_run_time))
const nextTriggerTs = computed(() => Number(emoji.value.next_trigger_ts || 0) || parseDateTime(emoji.value.next_trigger_time))
const spinMax = computed(() => Math.max(1, Math.min(Number(slotMachine.value.remaining || 0), Number(slotMachine.value.max_batch || 1)) || 1))
const pendingKey = computed(() => JSON.stringify(pendingOpen.value || {}))
const pendingOpenVisible = computed(() => !!pendingOpen.value.items?.length && hiddenPendingKey.value !== pendingKey.value)
const selectedEffectName = computed(() => effects.value.find((item) => item.key === selectedEffect.value)?.name || '未选择')
const currentActors = computed(() => actorsByTier.value[String(selectedTier.value)] || [])
const visibleActors = computed(() => sortedActors.value.slice(0, actorVisibleLimit.value))
const hasMoreActors = computed(() => sortedActors.value.length > actorVisibleLimit.value)
const remainingActorCount = computed(() => Math.max(0, sortedActors.value.length - actorVisibleLimit.value))
const stageRemainText = computed(() => {
  const remain = Number(stage.value.remaining_end_ts || 0) - nowTs.value
  if (Number(stage.value.remaining_end_ts || 0) > 0 && remain > 0) {
    return formatCountdown(remain)
  }
  return stage.value.remaining_text || '等待刷新'
})

const sortOptions = [
  { key: 'points_desc', label: 'P↓' },
  { key: 'points_asc', label: 'P↑' },
  { key: 'magic_desc', label: 'M↓' },
  { key: 'magic_asc', label: 'M↑' },
]

const sortedActors = computed(() => {
  const items = [...currentActors.value]
  return items.sort((left, right) => {
    const lPoints = Number(left.points || 0)
    const rPoints = Number(right.points || 0)
    const lMagic = Number(left.magic || 0)
    const rMagic = Number(right.magic || 0)
    if (actorSort.value === 'points_desc') {
      if (rPoints !== lPoints) return rPoints - lPoints
      if (rMagic !== lMagic) return rMagic - lMagic
    }
    if (actorSort.value === 'points_asc') {
      if (lPoints !== rPoints) return lPoints - rPoints
      if (lMagic !== rMagic) return lMagic - rMagic
    }
    if (actorSort.value === 'magic_desc') {
      if (rMagic !== lMagic) return rMagic - lMagic
      if (rPoints !== lPoints) return rPoints - lPoints
    }
    if (actorSort.value === 'magic_asc') {
      if (lMagic !== rMagic) return lMagic - rMagic
      if (lPoints !== rPoints) return lPoints - rPoints
    }
    return String(left.code || '').localeCompare(String(right.code || ''))
  })
})

const draftCount = computed(() => Object.keys(draftMap).length)

watch(
  bags,
  (items) => {
    items.forEach((bag) => {
      if (!openCounts[bag.tier]) openCounts[bag.tier] = '1'
      if (bag.upgrade_rule?.key && !upgradeCounts[bag.upgrade_rule.key]) {
        upgradeCounts[bag.upgrade_rule.key] = '1'
      }
    })
  },
  { immediate: true, deep: true },
)

watch(summaryKey, () => {
  loadDismissedSummaryKey()
})

watch(pendingKey, (nextKey, prevKey) => {
  if (nextKey && nextKey !== prevKey) {
    hiddenPendingKey.value = ''
  }
})

watch(effects, (items) => {
  const active = items.find((item) => item.active && item.unlocked)
  const firstUnlocked = items.find((item) => item.unlocked)
  if (items.some((item) => item.key === selectedEffect.value && item.unlocked)) {
    return
  }
  selectedEffect.value = active?.key || firstUnlocked?.key || 'basic'
}, { immediate: true, deep: true })

watch(actorTabs, (items) => {
  if (items.some((item) => String(item.tier) === String(selectedTier.value))) {
    return
  }
  selectedTier.value = String(items[0]?.tier || 1)
}, { immediate: true, deep: true })

watch([selectedTier, actorSort, currentActors], () => {
  actorVisibleLimit.value = actorLimitStep
}, { deep: true })

watch(() => slotMachine.value.remaining, () => {
  spinCount.value = String(Math.min(normalizePositiveInt(spinCount.value, 1), spinMax.value))
}, { immediate: true })

watch(nextRunTs, (value) => {
  if (!value || value > nowTs.value) lastRunAutoRefreshTs.value = 0
})

watch(nextTriggerTs, (value) => {
  if (!value || value > nowTs.value) lastTriggerAutoRefreshTs.value = 0
})

watch(
  () => stage.value.remaining_end_ts,
  (value) => {
    if (!value || Number(value) > nowTs.value) lastStageRefreshTs.value = 0
  },
)

watch(
  () => stage.value.has_active,
  (hasActive) => {
    if (hasActive) {
      clearDraft()
    }
  },
  { immediate: true },
)

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function normalizePositiveInt(value, fallback = 1) {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const safe = value.replace(/-/g, '/')
  const parsed = Date.parse(safe)
  return Number.isNaN(parsed) ? 0 : Math.floor(parsed / 1000)
}

function formatCountdown(totalSeconds) {
  const safe = Math.max(0, Math.floor(totalSeconds || 0))
  const hours = Math.floor(safe / 3600)
  const minutes = Math.floor((safe % 3600) / 60)
  const seconds = safe % 60
  return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function bagCardStyle(bag) {
  const lightBagBackgrounds = {
    1: '#eef6ff',
    2: '#effff1',
    3: '#fff7e7',
    4: '#fff0f3',
  }
  const lightBagBorders = {
    1: 'rgba(52, 134, 214, 0.24)',
    2: 'rgba(39, 164, 75, 0.24)',
    3: 'rgba(214, 139, 18, 0.24)',
    4: 'rgba(207, 52, 82, 0.22)',
  }
  const darkBagBackgrounds = {
    1: 'linear-gradient(180deg, rgba(33, 43, 56, 0.98) 0%, rgba(26, 34, 44, 0.96) 100%)',
    2: 'linear-gradient(180deg, rgba(27, 47, 37, 0.98) 0%, rgba(23, 39, 31, 0.96) 100%)',
    3: 'linear-gradient(180deg, rgba(52, 40, 19, 0.98) 0%, rgba(43, 34, 17, 0.96) 100%)',
    4: 'linear-gradient(180deg, rgba(55, 28, 38, 0.98) 0%, rgba(45, 23, 31, 0.96) 100%)',
  }
  const darkBagBorders = {
    1: 'rgba(98, 160, 255, 0.28)',
    2: 'rgba(84, 211, 120, 0.22)',
    3: 'rgba(242, 192, 86, 0.22)',
    4: 'rgba(255, 124, 156, 0.2)',
  }
  const tier = Number(bag.tier || 0)
  return {
    '--bag-bg': isDarkTheme.value
      ? (darkBagBackgrounds[tier] || 'rgba(42, 34, 30, 0.96)')
      : (lightBagBackgrounds[tier] || bag.bg_color || ''),
    '--bag-border': isDarkTheme.value
      ? (darkBagBorders[tier] || 'rgba(124, 92, 255, 0.18)')
      : (lightBagBorders[tier] || 'rgba(129, 133, 164, 0.18)'),
    '--bag-badge': bag.badge_color || '',
    '--bag-muted': isDarkTheme.value ? 'rgba(248, 234, 219, 0.82)' : '',
  }
}

function stageSlotPalette(tier) {
  const lightPalettes = {
    1: { bg: '#eef6ff', border: 'rgba(94, 149, 226, 0.34)', color: '#285585' },
    2: { bg: '#effff1', border: 'rgba(90, 185, 108, 0.34)', color: '#2d6336' },
    3: { bg: '#fff7e7', border: 'rgba(226, 171, 69, 0.36)', color: '#7a5a15' },
    4: { bg: '#fff0f3', border: 'rgba(232, 109, 143, 0.34)', color: '#6f3850' },
    default: { bg: '#f7f8fc', border: 'rgba(129, 133, 164, 0.2)', color: '#4b5063' },
  }
  const darkPalettes = {
    1: { bg: 'rgba(37, 65, 102, 0.24)', border: 'rgba(112, 173, 255, 0.3)', color: '#dcecff' },
    2: { bg: 'rgba(45, 93, 57, 0.24)', border: 'rgba(109, 226, 137, 0.3)', color: '#d7ffe1' },
    3: { bg: 'rgba(98, 73, 28, 0.26)', border: 'rgba(255, 205, 109, 0.3)', color: '#ffe9b3' },
    4: { bg: 'rgba(124, 49, 84, 0.22)', border: 'rgba(255, 126, 165, 0.34)', color: '#ffd4e1' },
    default: { bg: 'rgba(255, 255, 255, 0.04)', border: 'rgba(124, 92, 255, 0.18)', color: '#f3f5ff' },
  }
  const paletteMap = isDarkTheme.value ? darkPalettes : lightPalettes
  return paletteMap[tier] || paletteMap.default
}

function stageSlotStyle(row, slot) {
  if (slot.filled) {
    const palette = stageSlotPalette(Number(slot.tier || 0))
    return {
      '--stage-slot-bg': palette.bg,
      '--stage-slot-border': palette.border,
      '--stage-slot-color': palette.color,
    }
  }
  if (draftMap[slotKey(slot)]) {
    const palette = stageSlotPalette(Number(draftMap[slotKey(slot)].tier || 0))
    return {
      '--stage-slot-bg': palette.bg,
      '--stage-slot-border': palette.border,
      '--stage-slot-color': palette.color,
    }
  }
  return {}
}

function stageSlotTitle(slot) {
  if (slot.filled) return slot.emoji || ''
  if (draftMap[slotKey(slot)]) return '点击撤回草拟演员'
  return '点击放置演员'
}

function showMoreActors() {
  actorVisibleLimit.value += actorLimitStep
}

function collapseActors() {
  actorVisibleLimit.value = actorLimitStep
}

function clearRefreshTimeouts() {
  while (refreshTimeouts.length) {
    const timerId = refreshTimeouts.pop()
    window.clearTimeout(timerId)
  }
}

function scheduleFollowupRefreshes() {
  clearRefreshTimeouts()
  for (const delay of [1200, 3200]) {
    const timerId = window.setTimeout(() => {
      void loadStatus(false)
    }, delay)
    refreshTimeouts.push(timerId)
  }
}

function slotKey(slot) {
  return `${slot.row_index}_${slot.slot_index}`
}

function draftUsage(code) {
  return Object.values(draftMap).filter((item) => item.code === code).length
}

function draftRemaining(actor) {
  const current = sortedActors.value.find((item) => item.code === actor) || currentActors.value.find((item) => item.code === actor)
  if (!current) return 0
  return Math.max(0, Number(current.available || 0) - draftUsage(actor))
}

function clearDraft() {
  Object.keys(draftMap).forEach((key) => delete draftMap[key])
}

function nextEmptySlot() {
  for (const row of stageRows.value) {
    if (!row.unlocked) continue
    for (const slot of row.slots || []) {
      if (!slot.filled && !draftMap[slotKey(slot)]) {
        return slot
      }
    }
  }
  return null
}

function selectEffect(effect) {
  if (!effect.unlocked || stage.value.has_active) return
  selectedEffect.value = effect.key
}

function pickActor(actor) {
  if (stage.value.has_active) {
    flash('当前已有演出进行中，请先收回', 'warning')
    return
  }
  if (!actor.can_place || draftRemaining(actor.code) <= 0) {
    flash('该演员当前没有可用数量', 'warning')
    return
  }
  const slot = nextEmptySlot()
  if (!slot) {
    flash('当前没有空舞台格子', 'warning')
    return
  }
  draftMap[slotKey(slot)] = {
    row_index: slot.row_index,
    slot_index: slot.slot_index,
    code: actor.code,
    emoji: actor.emoji,
    points: actor.points,
    magic: actor.magic,
  }
}

function handleStageSlot(row, slot) {
  if (slot.filled || stage.value.has_active) return
  const key = slotKey(slot)
  if (draftMap[key]) {
    delete draftMap[key]
  }
}

function fillCurrentTier() {
  if (stage.value.has_active) {
    flash('当前已有演出进行中，请先收回', 'warning')
    return
  }
  for (const actor of sortedActors.value) {
    let remain = draftRemaining(actor.code)
    while (remain > 0) {
      const slot = nextEmptySlot()
      if (!slot) return
      draftMap[slotKey(slot)] = {
        row_index: slot.row_index,
        slot_index: slot.slot_index,
        code: actor.code,
        emoji: actor.emoji,
        points: actor.points,
        magic: actor.magic,
      }
      remain -= 1
    }
  }
}

function buildPlacements() {
  return Object.values(draftMap)
    .map((item) => ({
      row_index: Number(item.row_index || 0),
      slot_index: Number(item.slot_index || 0),
      emoji_code: item.code,
    }))
    .filter((item) => item.row_index > 0 && item.slot_index > 0 && item.emoji_code)
    .sort((left, right) => {
      if (left.row_index !== right.row_index) return left.row_index - right.row_index
      return left.slot_index - right.slot_index
    })
}

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = ''
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('sqemoji-dismissed-summary') || ''
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('sqemoji-dismissed-summary', key)
    } else {
      window.sessionStorage.removeItem('sqemoji-dismissed-summary')
    }
  }
}

function dismissSummaryOnExit() {
  if (showSummary.value) {
    dismissSummary()
  }
}

function closePendingPanel() {
  hiddenPendingKey.value = pendingKey.value
}

async function loadStatus(showError = true) {
  try {
    const data = await props.api.get(`${pluginBase}/status`)
    applyStatusPayload(data || {})
    return true
  } catch (error) {
    if (showError) {
      flash(error?.message || '加载状态失败', 'error')
    }
    return false
  }
}

function applyStatusPayload(payload = {}) {
  const nextStatus = payload.status?.emoji_status || payload.emoji_status || payload
  if (nextStatus?.stats || nextStatus?.slot_machine || nextStatus?.bags || nextStatus?.stage_rows) {
    status.emoji_status = nextStatus
  }
  if (Array.isArray(payload.history)) {
    status.history = payload.history
  } else if (Array.isArray(payload.status?.history)) {
    status.history = payload.status.history
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

  const stageEndTs = Number(stage.value.remaining_end_ts || 0)
  if (stageEndTs && nowTs.value >= stageEndTs && stageEndTs !== lastStageRefreshTs.value) {
    lastStageRefreshTs.value = stageEndTs
    shouldRefresh = true
  }

  if (shouldRefresh) {
    await loadStatus(false)
  }
}

async function withAction(action, fallback, afterAction = null) {
  loading.value = true
  try {
    const result = await action()
    applyStatusPayload(result || {})
    await loadStatus(false)
    scheduleFollowupRefreshes()
    if (afterAction) {
      afterAction(result)
    }
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

function spinSlot() {
  const count = Math.min(normalizePositiveInt(spinCount.value, 1), spinMax.value)
  spinCount.value = String(count)
  return withAction(() => props.api.post(`${pluginBase}/spin`, { count }), '转动完成')
}

function openBag(bag) {
  const count = Math.min(normalizePositiveInt(openCounts[bag.tier], 1), Math.max(Number(bag.open_max || 1), 1))
  openCounts[bag.tier] = String(count)
  return withAction(() => props.api.post(`${pluginBase}/open-bag`, { tier: bag.tier, count }), '开包完成')
}

function acceptPending() {
  return withAction(
    () => props.api.post(`${pluginBase}/accept-open`),
    '已收下',
    () => {
      hiddenPendingKey.value = ''
    },
  )
}

function rerollPending() {
  return withAction(() => props.api.post(`${pluginBase}/reroll-open`), '已重开')
}

function upgradeBag(bag) {
  const rule = bag.upgrade_rule
  if (!rule) return
  const count = Math.min(normalizePositiveInt(upgradeCounts[rule.key], 1), Math.max(Number(rule.max_times || 1), 1))
  upgradeCounts[rule.key] = String(count)
  return withAction(() => props.api.post(`${pluginBase}/upgrade-bag`, { rule_key: rule.key, times: count }), '合成完成')
}

function expandRow(row) {
  return withAction(() => props.api.post(`${pluginBase}/expand-stage-row`, { row_index: row.row_index }), '扩展完成')
}

function confirmStage() {
  const placements = buildPlacements()
  if (!placements.length) {
    flash('请先选择演员并填入舞台格子', 'warning')
    return
  }
  return withAction(
    () => props.api.post(`${pluginBase}/confirm-stage`, { effect_key: selectedEffect.value, placements }),
    '演出已开始',
    () => clearDraft(),
  )
}

function recallStage() {
  return withAction(() => props.api.post(`${pluginBase}/recall-stage`), '收回成功')
}

function closePlugin() {
  dismissSummaryOnExit()
  emit('close')
}

function switchToConfig() {
  dismissSummaryOnExit()
  emit('switch', 'config')
}

function slotRemainText(slot) {
  const endTs = Number(slot.remaining_end_ts || 0)
  if (endTs) {
    const remain = endTs - nowTs.value
    return remain > 0 ? formatCountdown(remain) : '可收回'
  }
  return slot.remaining_seconds ? formatCountdown(slot.remaining_seconds) : '进行中'
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
  if (nodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true
    return
  }
  if (nodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindThemeObserver() {
  detectTheme()
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    getThemeNodes().forEach((node) => {
      themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class'] })
    })
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
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
  dismissSummaryOnExit()
  if (timer) window.clearInterval(timer)
  clearRefreshTimeouts()
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.emoji-page {
  --emoji-bg: radial-gradient(circle at top, rgba(255, 255, 255, 0.94) 0%, rgba(246, 247, 250, 0.98) 42%, #eef1f7 100%);
  --emoji-panel: rgba(255, 255, 255, 0.9);
  --emoji-panel-strong: rgba(255, 255, 255, 0.98);
  --emoji-text: #262638;
  --emoji-muted: #777a90;
  --emoji-border: rgba(129, 133, 164, 0.18);
  --emoji-shadow: 0 20px 48px rgba(121, 128, 166, 0.12);
  --emoji-accent: #7c5cff;
  --emoji-accent-soft: rgba(124, 92, 255, 0.1);
  min-height: 100%;
  padding: 20px 0 36px;
  background: var(--emoji-bg);
  color: var(--emoji-text);
}

.emoji-page.is-dark-theme {
  --emoji-bg: radial-gradient(circle at top, rgba(33, 37, 52, 0.92) 0%, rgba(23, 26, 36, 0.98) 38%, #14161f 100%);
  --emoji-panel: rgba(26, 28, 39, 0.92);
  --emoji-panel-strong: rgba(19, 21, 30, 0.98);
  --emoji-text: #f3f5ff;
  --emoji-muted: #9fa7c4;
  --emoji-border: rgba(124, 92, 255, 0.18);
  --emoji-shadow: 0 24px 52px rgba(0, 0, 0, 0.32);
  --emoji-accent: #8b6cff;
  --emoji-accent-soft: rgba(139, 108, 255, 0.14);
}

.emoji-page,
.emoji-page * {
  box-sizing: border-box;
}

.emoji-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 14px;
  display: grid;
  gap: 16px;
}

.emoji-hero,
.emoji-panel,
.emoji-stat-card,
.emoji-bag-card,
.emoji-result-item,
.emoji-actor-card,
.emoji-effect-card,
.emoji-row-card,
.emoji-history-item {
  border: 1px solid var(--emoji-border);
  border-radius: 24px;
  background: var(--emoji-panel);
  box-shadow: var(--emoji-shadow);
}

.emoji-hero,
.emoji-panel {
  padding: 18px;
}

.emoji-panel,
.emoji-row-card,
.emoji-history-item,
.emoji-bag-card {
  content-visibility: auto;
  contain-intrinsic-size: 300px;
}

.emoji-hero {
  display: grid;
  gap: 16px;
}

.emoji-badge,
.emoji-tier-chip,
.emoji-sort-chip,
.emoji-meta-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  border-radius: 999px;
}

.emoji-badge {
  padding: 6px 12px;
  background: var(--emoji-accent-soft);
  color: var(--emoji-accent);
  font-size: 12px;
  font-weight: 700;
}

.emoji-title {
  margin: 10px 0 6px;
  font-size: clamp(26px, 4vw, 34px);
  line-height: 1.05;
}

.emoji-subtitle,
.emoji-panel-note,
.emoji-history-lines,
.emoji-history-next,
.emoji-stage-slot-time,
.emoji-effect-meta,
.emoji-upgrade-tip,
.emoji-stat-desc,
.emoji-bag-count {
  color: var(--emoji-muted);
}

.emoji-hero-meta,
.emoji-actions,
.emoji-stat-grid,
.emoji-bag-grid,
.emoji-result-grid,
.emoji-history-list,
.emoji-effect-grid {
  display: grid;
  gap: 12px;
}

.emoji-hero-meta {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.emoji-meta-chip {
  padding: 8px 14px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  color: var(--emoji-text);
  font-size: 13px;
  justify-content: flex-start;
}

.emoji-actions {
  grid-template-columns: repeat(auto-fit, minmax(min(112px, 100%), 1fr));
}

.emoji-stat-grid {
  grid-template-columns: repeat(auto-fit, minmax(min(176px, 100%), 1fr));
}

.emoji-stat-card {
  padding: 16px;
  text-align: center;
  background: var(--emoji-panel-strong);
}

.emoji-stat-label {
  font-size: 13px;
  color: var(--emoji-muted);
  font-weight: 700;
}

.emoji-stat-value {
  margin-top: 10px;
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 900;
}

.emoji-stat-desc {
  margin-top: 8px;
  font-size: 12px;
}

.emoji-section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.emoji-section-head-compact {
  align-items: center;
}

.emoji-section-title,
.emoji-subsection-title {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
}

.emoji-subsection-title {
  font-size: 18px;
}

.emoji-panel-note {
  font-size: 13px;
  line-height: 1.7;
}

.emoji-summary-list {
  display: grid;
  gap: 10px;
}

.emoji-summary-line,
.emoji-history-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--emoji-panel-strong);
  border: 1px solid var(--emoji-border);
}

.slot-layout {
  display: grid;
  gap: 16px;
}

.slot-reels {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  max-width: 460px;
  margin: 0 auto;
}

.slot-cell {
  padding: 14px 10px;
  min-height: 72px;
  border-radius: 18px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  display: grid;
  place-items: center;
  font-size: 32px;
}

.slot-actions,
.emoji-inline-row,
.emoji-upgrade-row,
.emoji-result-actions,
.emoji-tier-tabs,
.emoji-sort-tabs,
.emoji-stage-toolbar,
.emoji-stage-toolbar-left,
.emoji-stage-toolbar-right,
.emoji-pending-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.slot-actions {
  justify-content: center;
}

.emoji-number-input {
  width: 100%;
  max-width: 104px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  color: var(--emoji-text);
  outline: none;
}

.emoji-bag-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.emoji-bag-card {
  padding: 16px;
  background: var(--bag-bg, var(--emoji-panel-strong));
  display: grid;
  gap: 10px;
  color: var(--emoji-text);
  border-color: var(--bag-border, var(--emoji-border));
}

.emoji-bag-hero {
  height: 96px;
  border-radius: 16px;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}

.emoji-bag-name {
  font-size: 20px;
  font-weight: 900;
  text-align: center;
}

.emoji-bag-count,
.emoji-upgrade-tip {
  text-align: center;
  font-size: 13px;
  color: var(--bag-muted, var(--emoji-muted));
  line-height: 1.65;
}

.emoji-page.is-dark-theme .emoji-bag-count,
.emoji-page.is-dark-theme .emoji-upgrade-tip {
  color: rgba(243, 245, 255, 0.86);
}

.emoji-upgrade-box {
  padding: 12px;
  border-radius: 16px;
  border: 1px dashed var(--emoji-border);
  background: rgba(255, 255, 255, 0.2);
  display: grid;
  gap: 8px;
}

.emoji-page.is-dark-theme .emoji-upgrade-box {
  background: rgba(255, 255, 255, 0.04);
}

.emoji-upgrade-row span {
  font-size: 13px;
  color: var(--emoji-muted);
}

.emoji-pending-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 22px;
  background: var(--emoji-panel-strong);
  border: 1px solid var(--emoji-border);
}

.emoji-result-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 12px;
}

.emoji-result-grid.single {
  max-width: 280px;
  margin-left: auto;
  margin-right: auto;
}

.emoji-result-item {
  padding: 18px 14px;
  text-align: center;
  background: transparent;
}

.emoji-result-emoji {
  font-size: 44px;
}

.emoji-result-attr {
  margin-top: 8px;
  font-weight: 800;
}

.emoji-result-owned {
  margin-top: 8px;
  color: #2eb96d;
  font-weight: 700;
}

.emoji-tier-chip,
.emoji-sort-chip {
  border: 1px solid var(--emoji-border);
  background: var(--emoji-panel-strong);
  color: var(--emoji-text);
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
}

.emoji-tier-chip.active,
.emoji-sort-chip.active {
  background: var(--emoji-accent-soft);
  color: var(--emoji-accent);
}

.emoji-actor-scroll {
  max-height: 264px;
  overflow-y: auto;
  padding-right: 4px;
}

.emoji-actor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(62px, 1fr));
  gap: 5px;
}

.emoji-actor-card {
  padding: 6px 4px;
  text-align: center;
  cursor: pointer;
  border: 1px solid rgba(104, 161, 255, 0.3);
  border-radius: 12px;
  background: rgba(245, 250, 255, 0.74);
}

.emoji-page.is-dark-theme .emoji-actor-card {
  background: rgba(35, 40, 56, 0.9);
}

.emoji-actor-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.emoji-actor-card:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.emoji-actor-main {
  font-size: 20px;
  line-height: 1.1;
}

.emoji-actor-attr,
.emoji-actor-count,
.emoji-stage-note,
.emoji-row-head,
.emoji-history-top,
.emoji-pending-meta {
  font-size: 12px;
}

.emoji-effect-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-bottom: 14px;
}

.emoji-effect-card {
  padding: 12px;
  cursor: pointer;
  background: var(--emoji-panel-strong);
}

.emoji-effect-card.active {
  border-color: rgba(124, 92, 255, 0.42);
  box-shadow: inset 0 0 0 1px rgba(124, 92, 255, 0.16);
}

.emoji-effect-card.locked {
  opacity: 0.62;
  cursor: not-allowed;
}

.emoji-effect-title {
  font-size: 16px;
  font-weight: 900;
  margin-bottom: 6px;
}

.emoji-stage-toolbar {
  justify-content: space-between;
  margin-bottom: 16px;
}

.emoji-stage-rows {
  display: grid;
  gap: 14px;
}

.emoji-row-card {
  padding: 14px;
  background: var(--emoji-panel-strong);
}

.emoji-row-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.emoji-row-actions {
  margin-bottom: 12px;
}

.emoji-stage-slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(44px, 1fr));
  gap: 6px;
}

.emoji-stage-slot {
  min-height: 44px;
  border-radius: 10px;
  border: 1px dashed var(--stage-slot-border, var(--emoji-border));
  background: var(--stage-slot-bg, var(--emoji-panel));
  color: var(--stage-slot-color, var(--emoji-text));
  padding: 0;
  text-align: center;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.emoji-stage-slot.filled {
  border-style: solid;
  cursor: default;
}

.emoji-stage-slot.draft {
  border-style: solid;
}

.emoji-stage-slot-emoji {
  font-size: 20px;
  line-height: 1.1;
}

.emoji-stage-slot-meta {
  display: none;
}

.emoji-stage-slot-empty {
  width: 100%;
  height: 100%;
  font-size: 0;
  color: transparent;
}

.emoji-stage-slot-time {
  display: none;
}

.emoji-empty {
  padding: 26px 16px;
  border: 1px dashed var(--emoji-border);
  border-radius: 18px;
  text-align: center;
  color: var(--emoji-muted);
  background: var(--emoji-panel-strong);
}

.emoji-history-list {
  display: grid;
  gap: 10px;
}

.emoji-history-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}

@media (max-width: 860px) {
  .emoji-section-head,
  .emoji-stage-toolbar,
  .emoji-row-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .emoji-panel-note,
  .emoji-stage-note {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .emoji-shell {
    padding: 0 8px;
  }

  .emoji-hero,
  .emoji-panel {
    padding: 18px;
    border-radius: 20px;
  }

  .emoji-hero-meta,
  .emoji-actions,
  .emoji-stat-grid,
  .emoji-bag-grid,
  .emoji-effect-grid {
    grid-template-columns: 1fr;
  }

  .slot-reels {
    max-width: none;
  }
}
</style>
