<template>
  <div class="siqi-page">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon"><v-icon icon="mdi-emoticon-excited-outline" size="24" /></div>
        <div class="siqi-topbar__copy"><div class="siqi-topbar__title">Vue-表情</div><div class="siqi-topbar__sub">老虎机、表情包与动态舞台演出</div></div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" aria-label="刷新 Vue-表情状态" :loading="loading" :disabled="loading" @click="refreshData"><v-icon icon="mdi-refresh" size="18" class="mr-sm-1" /><span class="d-none d-sm-inline">刷新</span></v-btn>
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" aria-label="打开 Vue-表情配置" :disabled="loading" @click="switchToConfig"><v-icon icon="mdi-cog-outline" size="18" class="mr-sm-1" /><span class="d-none d-sm-inline">配置</span></v-btn>
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" aria-label="关闭 Vue-表情" :disabled="loading" @click="closePlugin"><v-icon icon="mdi-close" size="18" class="mr-sm-1" /><span class="d-none d-sm-inline">关闭</span></v-btn>
        </v-btn-group>
      </div>
    </div>

    <div class="siqi-content">
      <v-alert v-if="message.text" :type="message.type" density="compact" class="siqi-toast" closable @click:close="message.text = ''">{{ message.text }}</v-alert>
      <div v-if="initialLoading" class="loading-state" role="status" aria-live="polite"><v-progress-linear color="success" indeterminate rounded /><span>正在读取表情状态，请稍候</span></div>

      <template v-else>
        <v-row dense class="mb-3 overview-grid">
          <v-col v-for="(item, index) in overviewStats" :key="item.label" cols="6" md="3">
            <div class="stat-card" :class="'stat-' + (item.tone || statTone(index))">
              <div class="stat-icon"><v-icon :icon="item.icon || statIcon(index)" size="23" /></div>
              <div class="stat-content"><div class="stat-title">{{ item.label }}</div><div class="stat-value">{{ item.value }}</div><div v-if="item.desc" class="stat-desc">{{ item.desc }}</div></div>
            </div>
          </v-col>
        </v-row>

        <v-card flat class="siqi-card next-run-card mb-3">
          <v-card-text class="next-run-body">
            <div class="next-run-icon"><v-icon icon="mdi-calendar-clock-outline" size="23" /></div>
            <div class="next-run-copy">
              <div class="next-run-title">动态运行</div>
              <div class="next-run-guard">按舞台完成时间和老虎机计划动态安排</div>
            </div>
            <div class="next-run-times">
              <div class="next-run-time"><span>计划触发</span><strong>{{ emoji.next_trigger_time || '等待刷新' }}</strong></div>
              <div class="next-run-time"><span>执行时间</span><strong>{{ emoji.next_run_time || '等待刷新' }}</strong></div>
              <v-btn color="success" variant="tonal" size="small" class="schedule-run-btn" :loading="loading" :disabled="loading" @click="runNow"><v-icon icon="mdi-play-circle-outline" size="17" class="mr-1" />立即执行</v-btn>
            </div>
          </v-card-text>
          <div v-if="showSummary" class="summary-panel"><div class="summary-panel__head"><span><v-icon icon="mdi-check-circle-outline" size="17" />本次摘要</span><v-btn icon="mdi-close" size="x-small" variant="text" aria-label="关闭本次摘要" @click="dismissSummary" /></div><div class="summary-lines">{{ summaryLines.join(' / ') }}</div></div>
        </v-card>

        <div class="emoji-hub-grid">
          <v-card flat class="siqi-card slot-card mb-3">
            <v-card-title class="siqi-card-title siqi-card-title--slot d-flex align-center"><v-icon icon="mdi-slot-machine-outline" size="19" color="deep-orange" class="mr-2" />表情老虎机</v-card-title>
            <v-card-text class="slot-card-body">
              <div class="slot-today">今日次数：{{ slotMachine.used || 0 }}/{{ slotMachine.limit || 0 }}（基础{{ slotMachine.base || 0 }} + f(hnr*发种等级) {{ slotMachine.extra || 0 }}）</div>
              <div class="slot-reels slot-reels--large" aria-label="老虎机当前图案"><span v-for="(reel, index) in slotMachine.reels || []" :key="'reel-' + index">{{ reel }}</span></div>
              <div class="slot-center-row"><input v-model="spinCount" class="number-input" type="number" min="1" :max="Math.max(spinMax, 1)" aria-label="老虎机转动次数" /><v-btn color="deep-orange" variant="tonal" size="small" :loading="loading" :disabled="loading || !slotMachine.remaining" @click="spinSlot">转动</v-btn></div>
            </v-card-text>
          </v-card>

          <v-card flat class="siqi-card bag-card mb-3">
            <v-card-title class="siqi-card-title siqi-card-title--bags d-flex align-center"><v-icon icon="mdi-bag-personal-outline" size="19" color="orange" class="mr-2" />我的表情包<v-spacer /><span class="section-count">{{ bags.length }} 个层级</span></v-card-title>
            <v-card-text class="bag-card-body">
              <div class="bag-grid">
                <article v-for="bag in bags" :key="bag.tier" class="bag-item" :style="bagCardStyle(bag)">
                  <div v-if="bag.bg_image" class="bag-image" :style="{ backgroundImage: 'url(' + bag.bg_image + ')' }" /><div v-else class="bag-image bag-image--placeholder"><v-icon icon="mdi-package-variant-closed" size="26" /></div>
                  <div class="bag-copy"><div class="bag-name">{{ bag.name }}</div><div class="bag-count">持有 {{ bag.quantity }}</div></div>
                  <div class="bag-action"><input v-model="openCounts[bag.tier]" class="number-input" type="number" min="1" :max="Math.max(bag.open_max || 1, 1)" :aria-label="bag.name + '开包数量'" /><v-btn color="deep-orange" variant="tonal" size="small" :loading="loading" :disabled="loading || !bag.can_open" @click="openBag(bag)">开包</v-btn></div>
                  <div v-if="bag.upgrade_rule" class="bag-upgrade-row">
                    <div class="bag-upgrade-tip">{{ bag.upgrade_rule.tip }}</div>
                    <div class="bag-upgrade-controls">
                      <span class="bag-upgrade-label">目标数</span>
                      <input v-model="upgradeCounts[bag.upgrade_rule.key]" class="number-input bag-upgrade-input" type="number" min="1" :max="Math.max(bag.upgrade_rule.max_times || 1, 1)" :aria-label="bag.name + '合成次数'" :disabled="loading || !bag.upgrade_rule.enabled" />
                      <v-btn color="deep-orange" variant="tonal" size="small" :loading="loading" :disabled="loading || !bag.upgrade_rule.enabled" @click="upgradeBag(bag)">合成</v-btn>
                    </div>
                  </div>
                </article>
              </div>
              <article v-if="pendingOpenVisible && pendingOpen.items?.length" class="pending-panel">
                <div class="pending-head"><div><strong>待处理开包结果</strong><span>{{ pendingOpen.bag_name }} ×{{ pendingOpen.bag_count }} · 已重开 {{ pendingOpen.reroll_count || 0 }} 次</span></div><v-btn icon="mdi-close" size="x-small" variant="text" aria-label="关闭开包结果" @click="closePendingPanel" /></div>
                <div class="result-grid" :class="{ single: pendingOpen.items.length === 1 }"><article v-for="(item, index) in pendingOpen.items" :key="'pending-' + index" class="result-item"><div class="result-emoji">{{ item.emoji }}</div><div class="result-attr">P{{ item.points }} · M{{ item.magic }}</div><div class="result-owned">已有 {{ item.owned_count }}</div></article></div>
                <div class="pending-actions"><span>下次重开消耗 {{ pendingOpen.next_reroll_cost || 0 }} 魔力</span><div><v-btn color="primary" variant="tonal" size="small" :loading="loading" @click="rerollPending">重开</v-btn><v-btn color="success" variant="tonal" size="small" :loading="loading" @click="acceptPending">收下</v-btn></div></div>
              </article>
            </v-card-text>
          </v-card>
        </div>

        <v-card flat class="siqi-card catalog-card mb-3">
          <v-card-title class="siqi-card-title siqi-card-title--catalog catalog-title-row"><span class="card-title-copy"><v-icon icon="mdi-book-open-page-variant-outline" size="19" color="blue" />表情图鉴</span><span class="catalog-progress"><strong>{{ catalogStat.value }}</strong><small>{{ catalogStat.desc || '按层级切换查看演员' }}</small></span></v-card-title>
          <v-card-text class="catalog-body">
            <div class="tier-tabs"><button v-for="tab in actorTabs" :key="tab.tier" type="button" class="tier-chip" :class="{ active: String(selectedTier) === String(tab.tier) }" :style="tierChipStyle(tab)" @click="selectedTier = String(tab.tier)">{{ tab.name }} {{ tab.owned }}/{{ tab.total || '❓' }}</button></div>
            <div class="sort-tabs" aria-label="表情图鉴排序"><button v-for="item in sortOptions" :key="item.key" type="button" class="sort-chip" :class="{ active: actorSort === item.key }" @click="actorSort = item.key">{{ item.label }}</button></div>
            <div v-if="!currentActors.length" class="empty-state">当前层级暂无可用演员</div>
            <div v-else class="actor-scroll" :class="{ expanded: actorVisibleLimit >= sortedActors.length }">
              <div class="actor-grid"><button v-for="actor in visibleActors" :key="actor.code" type="button" class="actor-card" :style="actorCardStyle(actor)" :disabled="stage.has_active || !actor.can_place || draftRemaining(actor.code) <= 0" @click="pickActor(actor)"><div class="actor-main">{{ actor.emoji }}</div><div class="actor-attr">P{{ actor.points }} · M{{ actor.magic }}</div><div class="actor-count">×{{ draftRemaining(actor.code) }}</div></button></div>
            </div>
            <div v-if="hasMoreActors || actorVisibleLimit > actorLimitStep" class="actor-actions"><v-btn v-if="hasMoreActors" variant="tonal" color="primary" size="small" @click="showMoreActors">显示全部剩余 {{ remainingActorCount }} 个</v-btn><v-btn v-if="actorVisibleLimit > actorLimitStep" variant="text" size="small" @click="collapseActors">收起</v-btn></div>
          </v-card-text>
        </v-card>

        <v-card flat class="siqi-card stage-card mb-3">
          <v-card-title class="siqi-card-title siqi-card-title--stage stage-title-row"><span class="card-title-copy"><v-icon icon="mdi-drama-masks" size="19" color="deep-orange" />表情演出舞台</span><span class="stage-current"><strong>{{ stage.current_effect_name || '未开始' }}</strong><small>{{ stageHeaderMeta }}</small></span></v-card-title>
          <v-card-text class="stage-body">
            <div class="effect-grid" aria-label="舞台效果选择">
              <button v-for="effect in effects" :key="effect.key" type="button" class="effect-card" :class="{ active: selectedEffect === effect.key, locked: !effect.unlocked }" :aria-pressed="selectedEffect === effect.key" :disabled="!effect.unlocked || stage.has_active" @click="selectEffect(effect)">
                <span class="effect-title">{{ effect.name }}</span>
                <span class="effect-boost">积分+{{ effect.point_bonus_pct }}% · 魔力+{{ effect.magic_bonus_pct }}%</span>
                <span class="effect-subline">{{ effect.duration_text || (effect.duration_seconds || 0) + ' 秒' }}</span>
                <span class="effect-unlock">{{ effect.unlocked ? '已解锁' : effect.unlock_text || '未解锁' }}</span>
              </button>
            </div>
            <div class="stage-toolbar">
              <div class="stage-toolbar-copy"><strong v-if="stage.has_active">演出剩余 {{ stageRemainText }}</strong><strong v-else>当前效果 {{ selectedEffectName }}</strong><span>{{ stage.has_active ? '演出结束后可收回奖励' : '已选择 ' + draftCount + ' 位演员' }}</span></div>
              <div class="stage-toolbar-actions"><v-btn color="warning" variant="tonal" size="small" :disabled="loading || stage.has_active || !sortedActors.length" @click="fillCurrentTier">一键放置当前层级</v-btn><v-btn color="primary" variant="tonal" size="small" :disabled="loading || !draftCount || stage.has_active" @click="confirmStage">确认演出</v-btn><v-btn color="success" variant="tonal" size="small" :disabled="loading || !stage.has_active" @click="recallStage">收回演出</v-btn></div>
            </div>
            <div class="stage-rows">
              <article v-for="row in stageRows" :key="row.row_index" class="stage-row-card">
                <div class="stage-row-head"><div><strong>{{ row.name }}</strong><span>解锁声誉 {{ row.unlock_points }}</span></div><div class="stage-row-state">{{ row.unlocked ? '已开 ' + row.slot_count + '/' + row.max_slots + ' 格' : '未解锁' }}</div></div>
                <v-btn v-if="row.unlocked" color="amber-darken-2" variant="tonal" size="small" class="expand-btn" :loading="loading" :disabled="loading || !row.can_expand" @click="expandRow(row)">扩展一格（{{ row.next_expand_cost || 0 }} 魔力）</v-btn>
                <div v-if="row.unlocked" class="stage-slot-grid"><button v-for="slot in row.slots" :key="row.row_index + '-' + slot.slot_index" type="button" class="stage-slot" :class="{ filled: slot.filled, draft: !!draftMap[slotKey(slot)] }" :style="stageSlotStyle(row, slot)" :title="stageSlotTitle(slot)" :disabled="slot.filled || stage.has_active" @click="handleStageSlot(row, slot)"><span v-if="slot.filled" class="stage-slot-emoji">{{ slot.emoji }}</span><span v-else-if="draftMap[slotKey(slot)]" class="stage-slot-emoji">{{ draftMap[slotKey(slot)].emoji }}</span><span v-else class="stage-slot-empty">待定</span></button></div>
              </article>
            </div>
          </v-card-text>
        </v-card>

        <v-card flat class="siqi-card log-card">
          <v-card-title class="siqi-card-title siqi-card-title--logs d-flex align-center"><v-icon icon="mdi-text-box-outline" size="19" color="teal" class="mr-2" />最近30次操作日志</v-card-title>
          <v-card-text class="log-body"><div v-if="!operationLogs.length" class="empty-state">暂无操作日志</div><div v-else class="log-list"><article v-for="(item, index) in operationLogs" :key="item.time + '-' + item.title + '-' + index" class="log-item"><div class="log-item-head"><strong>{{ item.title }}</strong><time>{{ item.time }}</time></div><div class="log-item-detail">{{ item.detail }}</div></article></div></v-card-text>
        </v-card>
      </template>
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

const pluginBase = '/plugin/VueEmoji'
const loading = ref(false)
const initialLoading = ref(true)
const status = reactive({ emoji_status: {}, operation_logs: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
const stageRemainingCapturedTs = ref(nowTs.value)
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
const refreshTimeouts = []

const emoji = computed(() => status.emoji_status || {})
const statsItems = computed(() => emoji.value.stats || [])
const overviewStats = computed(() => statsItems.value.slice(0, 4).map((item, index) => ({
  ...item,
  icon: statIcon(index),
  tone: statTone(index),
})))
const catalogStat = computed(() => (
  statsItems.value.find((item) => String(item?.label || '').includes('图鉴'))
  || { label: '图鉴进度', value: '0/0', desc: '等待刷新' }
))
const slotMachine = computed(() => emoji.value.slot_machine || {})
const bags = computed(() => emoji.value.bags || [])
const pendingOpen = computed(() => emoji.value.pending_open || {})
const actorTabs = computed(() => emoji.value.actor_tabs || [])
const actorsByTier = computed(() => emoji.value.actors_by_tier || {})
const effects = computed(() => emoji.value.effects || [])
const stage = computed(() => emoji.value.stage || {})
const stageRows = computed(() => emoji.value.stage_rows || [])
const operationLogs = computed(() => emoji.value.operation_logs || status.operation_logs || [])
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
  const hasBackendRemaining = stage.value.remaining_seconds !== undefined && stage.value.remaining_seconds !== null && stage.value.remaining_seconds !== ''
  const backendRemaining = Number(stage.value.remaining_seconds || 0)
  if (hasBackendRemaining) {
    const elapsed = Math.max(0, nowTs.value - stageRemainingCapturedTs.value)
    const remaining = Math.max(0, backendRemaining - elapsed)
    if (remaining > 0) {
      return formatCountdown(remaining)
    }
    return stage.value.has_active ? '可收回' : '等待刷新'
  }
  const endTs = Number(stage.value.remaining_end_ts || 0)
  const remaining = Math.max(0, endTs - nowTs.value)
  return remaining > 0 ? formatCountdown(remaining) : (stage.value.has_active ? '可收回' : '等待刷新')
})
const stageTaskMeta = computed(() => (
  stage.value.has_active
    ? `${stage.value.current_effect_name || '舞台效果'} · 演员${Number(stage.value.active_count || 0)}位`
    : '等待安排演员和舞台效果'
))
const stageHeaderMeta = computed(() => {
  if (!stage.value.has_active) return '当前无演出演员'
  const rewards = []
  if (Number(stage.value.expected_points || 0) > 0) rewards.push(`声誉+${stage.value.expected_points}`)
  if (Number(stage.value.expected_magic || 0) > 0) rewards.push(`魔力+${stage.value.expected_magic}`)
  const rewardText = rewards.length ? ` · 预计${rewards.join('，')}` : ''
  return `演员${Number(stage.value.active_count || 0)}位${rewardText}`
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

function statIcon(index) {
  return ['mdi-lightning-bolt-outline', 'mdi-star-circle-outline', 'mdi-hand-coin-outline', 'mdi-slot-machine-outline'][index] || 'mdi-chart-box-outline'
}

function statTone(index) {
  return ['green', 'orange', 'blue', 'red'][index] || 'green'
}

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
  const tones = { 1: '59,130,246', 2: '34,197,94', 3: '245,158,11', 4: '244,63,94' }
  return {
    '--bag-tone': tones[Number(bag?.tier || 0)] || '100,116,139',
    '--bag-badge': bag?.badge_color || 'rgba(var(--v-theme-on-surface), .82)',
  }
}

function stageSlotPalette(tier) {
  const tones = { 1: '59,130,246', 2: '34,197,94', 3: '245,158,11', 4: '244,63,94' }
  const tone = tones[Number(tier || 0)] || '100,116,139'
  return { bg: 'rgba(' + tone + ', .09)', border: 'rgba(' + tone + ', .28)', color: 'rgba(var(--v-theme-on-surface), .84)' }
}

function tierChipStyle(tab) {
  const palette = stageSlotPalette(Number(tab?.tier || 0))
  return {
    '--tier-chip-bg': palette.bg,
    '--tier-chip-border': palette.border,
    '--tier-chip-color': palette.color,
  }
}

function actorCardStyle(actor) {
  const palette = stageSlotPalette(Number(actor?.tier || selectedTier.value || 0))
  return {
    '--actor-card-bg': palette.bg,
    '--actor-card-border': palette.border,
    '--actor-card-color': palette.color,
  }
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
  actorVisibleLimit.value = sortedActors.value.length || actorLimitStep
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
  dismissedSummaryKey.value = window.sessionStorage.getItem('vueemoji-dismissed-summary') || ''
}

function dismissSummary() {
  const key = summaryKey.value
  dismissedSummaryKey.value = key
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('vueemoji-dismissed-summary', key)
    } else {
      window.sessionStorage.removeItem('vueemoji-dismissed-summary')
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
    if (nextStatus?.stage) {
      const receivedAt = Math.floor(Date.now() / 1000)
      nowTs.value = receivedAt
      stageRemainingCapturedTs.value = receivedAt
    }
  }
  if (Array.isArray(payload.history)) {
    // Legacy execution history remains accepted by the backend but is no longer rendered here.
  }
  if (Array.isArray(payload.operation_logs)) {
    status.operation_logs = payload.operation_logs
  } else if (Array.isArray(payload.status?.operation_logs)) {
    status.operation_logs = payload.status.operation_logs
  } else if (Array.isArray(nextStatus?.operation_logs)) {
    status.operation_logs = nextStatus.operation_logs
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

onMounted(async () => {
  loadDismissedSummaryKey()
  try {
    await loadStatus()
  } finally {
    initialLoading.value = false
  }
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    void maybeAutoRefreshStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  dismissSummaryOnExit()
  if (timer) window.clearInterval(timer)
  clearRefreshTimeouts()
})
</script>

<style scoped>
.siqi-page{padding:16px 20px;display:flex;flex-direction:column;gap:16px;min-height:400px;overflow-x:hidden;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',sans-serif;color:rgba(var(--v-theme-on-surface),.85);border:1px solid rgba(var(--v-theme-on-surface),.12);border-radius:8px;background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))}
.siqi-page,.siqi-page *{box-sizing:border-box}.siqi-page :deep(.v-btn){min-height:44px;transition:transform .16s ease,box-shadow .16s ease,filter .16s ease,opacity .16s ease}.siqi-page :deep(.v-btn:not(.v-btn--disabled):hover){transform:translateY(-1px);box-shadow:0 6px 16px rgba(15,23,42,.12);filter:saturate(1.05)}.siqi-page :deep(.v-btn:not(.v-btn--disabled):active){transform:translateY(0) scale(.98)}.siqi-page :deep(.v-btn.v-btn--disabled),.siqi-page button:disabled{cursor:not-allowed;opacity:.55}.siqi-page button:focus-visible,.siqi-page input:focus-visible{outline:2px solid rgba(76,175,80,.55);outline-offset:2px}
.siqi-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:8px}.siqi-topbar__left{display:flex;align-items:center;gap:12px;min-width:0;flex:1}.siqi-topbar__copy{min-width:0}.siqi-topbar__right{display:flex;align-items:center;flex-shrink:0}.siqi-topbar__right :deep(.v-btn-group){flex-wrap:nowrap}.siqi-topbar__icon{width:42px;height:42px;border-radius:11px;background:rgba(76,175,80,.14);display:flex;align-items:center;justify-content:center;color:#2e7d32;flex-shrink:0}.siqi-topbar__title{font-size:16px;font-weight:700;letter-spacing:-.3px;color:rgba(var(--v-theme-on-surface),.88)}.siqi-topbar__sub{margin-top:2px;overflow:hidden;color:rgba(var(--v-theme-on-surface),.55);font-size:11px;text-overflow:ellipsis;white-space:nowrap}
.siqi-content{min-width:0;overflow-x: hidden}.siqi-toast{margin-bottom:12px}.loading-state{display:grid;gap:12px;min-height:160px;padding:24px;place-content:center stretch;border-radius:14px;color:rgba(var(--v-theme-on-surface),.68);background:rgba(var(--v-theme-on-surface),.03);backdrop-filter:blur(20px) saturate(150%);box-shadow:0 2px 10px rgba(0,0,0,.05)}.loading-state span{text-align:center;font-size:12px}
.siqi-card{min-width:0;overflow:hidden;border:.5px solid rgba(var(--v-theme-on-surface),.08);border-radius:14px;background:rgba(var(--v-theme-on-surface),.03);backdrop-filter:blur(20px) saturate(150%);box-shadow:inset 0 1px 0 rgba(var(--v-theme-surface),.2),0 2px 10px rgba(0,0,0,.05)}.siqi-card-title{min-height:44px;padding:10px 16px!important;border-bottom:.5px solid rgba(var(--v-theme-on-surface),.07);color:rgba(var(--v-theme-on-surface),.84);font-size:13px!important;font-weight:700!important;line-height:1.3;white-space:normal}.siqi-card-title :deep(.v-spacer){flex:1 1 auto!important}.siqi-card-title--schedule{background:rgba(76,175,80,.08)}.siqi-card-title--bags{background:rgba(249,115,22,.09)}.siqi-card-title--catalog{background:rgba(59,130,246,.09)}.siqi-card-title--stage{background:rgba(245,158,11,.09)}.siqi-card-title--logs{background:rgba(20,184,166,.08)}.section-count{color:rgba(var(--v-theme-on-surface),.48);font-size:11px;font-weight:600}.card-title-copy{display:inline-flex;align-items:center;gap:8px;min-width:0}
.overview-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0 0 12px!important;}.overview-grid>*{width:auto!important;max-width:none!important;padding:0!important}.stat-card{--stat-rgb:76,175,80;--stat-color:#2e7d32;min-width:0;min-height:78px;display:flex;align-items:center;gap:12px;padding:12px 14px;border:.5px solid rgba(var(--v-theme-on-surface),.08);border-radius:14px;background:rgba(var(--v-theme-on-surface),.03);box-shadow:inset 0 1px 0 rgba(var(--v-theme-surface),.2),0 2px 12px rgba(var(--v-theme-on-surface),.08)}.stat-icon{width:38px;height:38px;flex:0 0 38px;display:grid;place-items:center;border-radius:12px;background:rgba(var(--stat-rgb),.14);color:var(--stat-color)}.stat-green{--stat-rgb:16,185,129;--stat-color:#10b981;background:rgba(16,185,129,.12);border-color:rgba(16,185,129,.24)}.stat-orange{--stat-rgb:245,158,11;--stat-color:#f59e0b;background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.24)}.stat-blue{--stat-rgb:59,130,246;--stat-color:#3b82f6;background:rgba(59,130,246,.12);border-color:rgba(59,130,246,.24)}.stat-red{--stat-rgb:239,68,68;--stat-color:#ef4444;background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.24)}.stat-green .stat-icon,.stat-green .stat-title,.stat-green .stat-value{color:#10b981}.stat-orange .stat-icon,.stat-orange .stat-title,.stat-orange .stat-value{color:#f59e0b}.stat-blue .stat-icon,.stat-blue .stat-title,.stat-blue .stat-value{color:#3b82f6}.stat-red .stat-icon,.stat-red .stat-title,.stat-red .stat-value{color:#ef4444}.stat-content{min-width:0}.stat-title{overflow:hidden;color:rgba(var(--v-theme-on-surface),.55);font-size:11px;font-weight:600;text-overflow:ellipsis;white-space:nowrap}.stat-value{margin-top:2px;overflow:hidden;color:rgba(var(--v-theme-on-surface),.88);font-size:20px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.5px;line-height:1.1;text-overflow:ellipsis;white-space:nowrap}.stat-desc{margin-top:3px;overflow:hidden;color:rgba(var(--v-theme-on-surface),.48);font-size:9px;text-overflow:ellipsis;white-space:nowrap}
.emoji-hub-grid{display:grid;grid-template-columns:minmax(260px,.72fr) minmax(0,1.65fr);gap:12px;align-items:stretch;margin-bottom:12px}.emoji-hub-grid>.siqi-card{height:100%;margin-bottom:0!important}.primary-grid{display:grid;grid-template-columns:minmax(420px,.92fr) minmax(560px,1.25fr);gap:12px;align-items:stretch}.primary-grid>.siqi-card{height:100%}.schedule-board-body,.bag-card-body,.catalog-body,.stage-body{padding:14px!important}.schedule-list{display:flex;flex-direction:column;gap:8px}.schedule-row{min-width:0;min-height:72px;display:grid;grid-template-columns:34px minmax(0,1fr) minmax(120px,auto);align-items:center;gap:10px;padding:10px 12px;border:1px solid rgba(76,175,80,.16);border-radius:12px;background:rgba(var(--v-theme-surface),.86);transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}.schedule-row:hover{transform:translateY(-1px);box-shadow:0 6px 14px rgba(15,23,42,.07)}.schedule-row.tone-blue{border-color:rgba(59,130,246,.18)}.schedule-row.tone-orange{border-color:rgba(249,115,22,.18)}.schedule-row.tone-teal{border-color:rgba(20,184,166,.18)}.schedule-row__icon{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:rgba(34,197,94,.1);color:#22c55e}.schedule-row__icon.tone-blue{background:rgba(59,130,246,.1);color:#3b82f6}.schedule-row__icon.tone-orange{background:rgba(249,115,22,.1);color:#f97316}.schedule-row__icon.tone-teal{background:rgba(20,184,166,.1);color:#14b8a6}.schedule-row__copy{min-width:0}.schedule-row__title{color:rgba(var(--v-theme-on-surface),.82);font-size:12px;font-weight:800}.schedule-row__meta{margin-top:2px;overflow:hidden;color:rgba(var(--v-theme-on-surface),.46);font-size:10px;text-overflow:ellipsis;white-space:nowrap}.schedule-row__value{max-width:210px;overflow:hidden;color:#22c55e;font-size:11px;font-weight:800;font-variant-numeric:tabular-nums;text-align:right;text-overflow:ellipsis;white-space:nowrap}.schedule-row__value.tone-blue{color:#3b82f6}.schedule-row__value.tone-orange{color:#f97316}.schedule-row__value.tone-teal{color:#14b8a6}.schedule-run-btn{min-width:100px!important}.summary-panel{margin-top:10px;padding:10px 12px;border:1px solid rgba(34,197,94,.18);border-radius:12px;background:rgba(34,197,94,.07)}.summary-panel__head{display:flex;align-items:center;justify-content:space-between;gap:10px}.summary-panel__head>span{display:inline-flex;align-items:center;gap:6px;color:#22c55e;font-size:11px;font-weight:800}.summary-lines{color:rgba(var(--v-theme-on-surface),.64);font-size:11px;line-height:1.55}
.slot-center-row,.bag-action{display:flex;align-items:center;gap:6px;min-width:0}.slot-center-row :deep(.v-btn),.bag-action :deep(.v-btn){height:44px;min-height:44px}.number-input{width:58px;height:44px;min-width:0;max-width:100%;padding:0 8px;border:1px solid rgba(var(--v-theme-on-surface),.16);border-radius:10px;color:rgba(var(--v-theme-on-surface),.82);background:rgba(var(--v-theme-surface),.78);font:inherit;font-size:12px;font-variant-numeric:tabular-nums;line-height:44px;text-align:center}
.bag-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.bag-item{min-width:0;display:grid;grid-template-columns:62px minmax(0,1fr) auto;align-items:center;gap:8px;padding:10px;border:1px solid rgba(var(--bag-tone),.2);border-radius:12px;background:linear-gradient(135deg,rgba(var(--bag-tone),.085),rgba(var(--v-theme-surface),.68))}.bag-image{width:62px;height:62px;border-radius:11px;background-position:center;background-size:contain;background-repeat:no-repeat}.bag-image--placeholder{display:grid;place-items:center;color:rgb(var(--bag-tone));background:rgba(var(--bag-tone),.1)}.bag-copy{min-width:0}.bag-name{overflow:hidden;color:var(--bag-badge);font-size:12px;font-weight:800;text-overflow:ellipsis;white-space:nowrap}.bag-count{margin-top:2px;color:rgba(var(--v-theme-on-surface),.48);font-size:10px}.bag-action{justify-content:flex-end}.bag-action .number-input{width:58px}.bag-action :deep(.v-btn){min-width:52px!important}.bag-upgrade-row{grid-column:1/-1;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px;padding:7px 8px;border:1px dashed rgba(var(--bag-tone),.28);border-radius:10px;color:rgba(var(--v-theme-on-surface),.62);font-size:10px}.bag-upgrade-tip{min-width:0;color:rgba(var(--v-theme-on-surface),.5);font-size:9px;line-height:1.35;overflow-wrap:anywhere}.bag-upgrade-controls{display:flex;align-items:center;justify-content:flex-end;gap:7px;min-width:0;justify-self:end}.bag-upgrade-label{white-space:nowrap}.bag-upgrade-row .number-input{height:38px;line-height:38px}.bag-upgrade-row .bag-upgrade-input{width:76px!important;min-width:76px;flex:0 0 76px}.bag-upgrade-row :deep(.v-btn){min-width:52px!important;height:38px;min-height:38px!important}
.pending-panel{margin-top:10px;padding:12px;border:1px solid rgba(59,130,246,.18);border-radius:12px;background:rgba(59,130,246,.055)}.pending-head,.pending-actions{display:flex;align-items:center;justify-content:space-between;gap:12px}.pending-head>div{min-width:0;display:flex;flex-direction:column}.pending-head strong{color:rgba(var(--v-theme-on-surface),.82);font-size:12px}.pending-head span,.pending-actions>span{color:rgba(var(--v-theme-on-surface),.48);font-size:10px}.result-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(74px,1fr));gap:7px;margin:10px 0}.result-item{padding:8px;border-radius:10px;text-align:center;background:rgba(var(--v-theme-surface),.72)}.result-emoji{font-size:25px}.result-attr{color:rgba(var(--v-theme-on-surface),.68);font-size:10px;font-weight:700}.result-owned{color:rgba(var(--v-theme-on-surface),.43);font-size:9px}.pending-actions>div{display:flex;gap:6px}
.catalog-title-row,.stage-title-row{display:flex;align-items:center;justify-content:space-between;gap:14px}.catalog-progress,.stage-current{min-width:0;display:flex;align-items:flex-end;flex-direction:column;text-align:right}.catalog-progress strong,.stage-current strong{color:rgba(var(--v-theme-on-surface),.84);font-size:13px;font-variant-numeric:tabular-nums}.catalog-progress small,.stage-current small{max-width:520px;overflow:hidden;color:rgba(var(--v-theme-on-surface),.45);font-size:10px;font-weight:500;text-overflow:ellipsis;white-space:nowrap}
.tier-tabs{display:flex;gap:7px;overflow-x:auto;padding-bottom:4px;scrollbar-width:thin}.tier-chip,.sort-chip{min-height:44px;padding:0 13px;border:1px solid var(--tier-chip-border,rgba(var(--v-theme-on-surface),.1));border-radius:999px;color:var(--tier-chip-color,rgba(var(--v-theme-on-surface),.68));background:var(--tier-chip-bg,rgba(var(--v-theme-on-surface),.035));font:inherit;font-size:11px;font-weight:800;white-space:nowrap;cursor:pointer}.tier-chip.active{box-shadow:inset 0 0 0 1px currentColor;filter:saturate(1.2)}.sort-tabs{display:flex;justify-content:flex-end;gap:5px;margin:8px 0}.sort-chip{min-width:44px;padding:0 10px;border-color:rgba(var(--v-theme-on-surface),.09);color:rgba(var(--v-theme-on-surface),.55);background:rgba(var(--v-theme-on-surface),.03)}.sort-chip.active{border-color:rgba(59,130,246,.28);color:#3b82f6;background:rgba(59,130,246,.09)}
.actor-scroll{max-height:350px;overflow-y:auto;padding:2px}.actor-scroll.expanded{max-height:560px}.actor-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(58px,1fr));gap:6px}.actor-card{position:relative;min-width:0;min-height:62px;padding:6px 5px;border:1px solid var(--actor-card-border);border-radius:10px;color:var(--actor-card-color);background:var(--actor-card-bg);font:inherit;cursor:pointer}.actor-card:not(:disabled):hover{transform:translateY(-1px);box-shadow:0 5px 12px rgba(15,23,42,.08)}.actor-main{font-size:22px;line-height:1.15}.actor-attr{margin-top:2px;font-size:8px;font-weight:700}.actor-count{position:absolute;top:4px;right:4px;padding:1px 4px;border-radius:999px;color:rgba(var(--v-theme-on-surface),.7);background:rgba(var(--v-theme-surface),.72);font-size:7px}.actor-actions{display:flex;justify-content:center;gap:8px;margin-top:10px}
.effect-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-bottom:10px}.effect-card{min-width:0;min-height:92px;display:flex;align-items:flex-start;flex-direction:column;gap:4px;padding:10px 11px;border:1px solid rgba(249,115,22,.14);border-radius:12px;color:rgba(var(--v-theme-on-surface),.72);background:rgba(249,115,22,.045);font:inherit;text-align:left;cursor:pointer}.effect-card.active{border-color:rgba(249,115,22,.38);background:rgba(249,115,22,.1);box-shadow:inset 0 0 0 1px rgba(249,115,22,.1)}.effect-card.locked{filter:grayscale(.25)}.effect-card:disabled{cursor:not-allowed}.effect-title{color:rgba(var(--v-theme-on-surface),.85);font-size:12px;font-weight:850}.effect-boost{color:#f97316;font-size:10px;font-weight:750}.effect-subline,.effect-unlock{color:rgba(var(--v-theme-on-surface),.46);font-size:10px}
.stage-toolbar{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:0 0 10px;padding:11px 12px;border:1px solid rgba(var(--v-theme-on-surface),.065);border-radius:12px;background:rgba(var(--v-theme-surface),.64)}.stage-toolbar-copy{min-width:0;display:flex;flex-direction:column}.stage-toolbar-copy strong{color:rgba(var(--v-theme-on-surface),.82);font-size:12px}.stage-toolbar-copy span{margin-top:2px;color:rgba(var(--v-theme-on-surface),.46);font-size:10px}.stage-toolbar-actions{display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end}.stage-rows{display:flex;flex-direction:column;gap:9px}.stage-row-card{min-width:0;padding:10px 11px;border:1px solid rgba(var(--v-theme-on-surface),.065);border-radius:12px;background:rgba(var(--v-theme-surface),.6)}.stage-row-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.stage-row-head>div:first-child{min-width:0;display:flex;flex-direction:column}.stage-row-head strong{color:rgba(var(--v-theme-on-surface),.82);font-size:12px}.stage-row-head span,.stage-row-state{color:rgba(var(--v-theme-on-surface),.45);font-size:10px}.expand-btn{margin-top:8px}.stage-slot-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(44px,1fr));gap:6px;margin-top:9px}.stage-slot{min-width:0;min-height:44px;border:1px dashed var(--stage-slot-border,rgba(var(--v-theme-on-surface),.12));border-radius:9px;color:var(--stage-slot-color,rgba(var(--v-theme-on-surface),.66));background:var(--stage-slot-bg,rgba(var(--v-theme-on-surface),.025));font:inherit;cursor:pointer}.stage-slot.draft{border-style:solid;box-shadow:inset 0 0 0 1px var(--stage-slot-border)}.stage-slot-emoji{font-size:18px;line-height:1}.stage-slot-empty{color:rgba(var(--v-theme-on-surface),.35);font-size:8px}
.history-body{max-height:360px;overflow-y:auto;padding:12px!important}.history-list{display:flex;flex-direction:column;overflow:hidden;border:1px solid rgba(var(--v-theme-on-surface),.06);border-radius:12px;background:rgba(var(--v-theme-surface),.68)}.history-item{min-width:0;display:flex;align-items:center;gap:12px;padding:10px 12px;border-bottom:1px solid rgba(var(--v-theme-on-surface),.07);font-size:12px}.history-item:last-child{border-bottom:none}.history-detail{min-width:0;overflow:hidden;color:rgba(var(--v-theme-on-surface),.68);text-overflow:ellipsis;white-space:nowrap}.history-time{margin-left:auto;flex:0 0 auto;color:rgba(var(--v-theme-on-surface),.48);font-size:11px;font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}.empty-state{padding:24px 12px;color:rgba(var(--v-theme-on-surface),.42);font-size:12px;text-align:center}
@media (prefers-reduced-motion: reduce){.siqi-page :deep(.v-btn),.actor-card{transition:none}}
@media (max-width: 1100px){.emoji-hub-grid{grid-template-columns:1fr}.primary-grid{grid-template-columns:1fr}}
@media (max-width: 900px){.overview-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.stage-toolbar{align-items:stretch;flex-direction:column}.stage-toolbar-actions{justify-content:flex-start}}
@media (max-width: 600px){
  .siqi-page{padding:14px}.siqi-topbar{align-items:flex-start;gap:10px}.siqi-topbar__left{min-width:0}.siqi-topbar__right :deep(.v-btn){min-width:44px!important;padding-inline:0!important}.overview-grid>.v-col{padding:4px!important}.stat-card{min-height:76px;padding:10px;gap:8px}.stat-icon{width:34px;height:34px;flex-basis:34px}.stat-value{font-size:17px}.stat-desc{display:none}
  .siqi-card-title{padding-inline:13px!important}.schedule-board-body,.bag-card-body,.catalog-body,.stage-body{padding:12px!important}.schedule-row{grid-template-columns:32px minmax(0,1fr);min-height:70px}.schedule-row__value{grid-column:2;max-width:100%;text-align:left}
  .bag-grid{grid-template-columns:1fr}.bag-item{grid-template-columns:52px minmax(0,1fr)}.bag-image{width:52px;height:52px}.bag-action{grid-column:1/-1}.bag-action .number-input{flex:1;width:auto}.bag-action :deep(.v-btn){flex:1}.bag-upgrade-row{grid-column:1/-1}
  .pending-head,.pending-actions{align-items:stretch;flex-direction:column}.pending-actions>div{width:100%}.pending-actions :deep(.v-btn){flex:1}.catalog-title-row,.stage-title-row{align-items:flex-start;flex-direction:column}.catalog-progress,.stage-current{align-items:flex-start;width:100%;text-align:left}.catalog-progress small,.stage-current small{max-width:100%}
  .sort-tabs{justify-content:flex-start;overflow-x:auto}.actor-grid{grid-template-columns:repeat(5,minmax(0,1fr))}.stage-toolbar-actions{display:grid;grid-template-columns:1fr;width:100%}.stage-toolbar-actions :deep(.v-btn){width:100%}.stage-row-head{align-items:flex-start}.stage-slot-grid{grid-template-columns:repeat(6,minmax(0,1fr))}.history-item{gap:6px;padding-inline:10px}.history-detail{font-size:11px}.history-time{font-size:10px}
}
@media (max-width: 420px){.actor-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.stage-slot-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}

.next-run-card{margin-bottom:12px!important}.next-run-body{display:flex;align-items:center;gap:12px;min-height:72px;padding:10px 14px!important;background:rgba(76,175,80,.08)}.next-run-icon{width:40px;height:40px;display:grid;place-items:center;flex:0 0 40px;border-radius:12px;color:#16a34a;background:rgba(34,197,94,.13)}.next-run-copy{min-width:0;flex:1 1 auto}.next-run-title{font-size:14px;font-weight:800}.next-run-guard{margin-top:3px;color:rgba(var(--v-theme-on-surface),.55);font-size:10px;line-height:1.35}.next-run-times{display:flex;align-items:center;justify-content:flex-end;flex-wrap:wrap;gap:8px}.next-run-time{display:grid;gap:1px;min-width:142px;text-align:right}.next-run-time span{color:rgba(var(--v-theme-on-surface),.52);font-size:10px}.next-run-time strong{color:rgba(var(--v-theme-on-surface),.86);font-size:11px;font-variant-numeric:tabular-nums;white-space:nowrap}.next-run-card .schedule-run-btn{min-width:100px!important;min-height:32px!important;height:32px!important;border-radius:999px!important;font-size:11px!important}.next-run-card .summary-panel{margin:0 14px 12px}.siqi-card-title--slot{background:rgba(249,115,22,.09)}.slot-card{display:flex;flex-direction:column}.slot-card-body{flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;padding:16px!important}.slot-today{color:rgba(var(--v-theme-on-surface),.66);font-size:11px;line-height:1.5}.slot-reels--large{width:100%;max-width:300px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:16px auto}.slot-reels--large span{width:auto;height:68px;display:grid;place-items:center;border:1px solid rgba(249,115,22,.2);border-radius:12px;background:rgba(var(--v-theme-surface),.72);font-size:32px}.slot-center-row{justify-content:center}.slot-center-row .number-input{width:86px}.slot-center-row :deep(.v-btn){min-width:58px!important}.log-card{margin-top:0}.log-body{max-height:430px;overflow-y:auto;padding:12px!important}.log-list{display:grid;gap:8px}.log-item{min-width:0;padding:10px 12px;border:1px solid rgba(var(--v-theme-on-surface),.08);border-radius:11px;background:rgba(var(--v-theme-surface),.68);font-size:11px;line-height:1.5}.log-item-head{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;color:rgba(var(--v-theme-on-surface),.84)}.log-item-head strong{font-size:11px}.log-item-head time{color:rgba(var(--v-theme-on-surface),.5);font-size:10px;font-variant-numeric:tabular-nums}.log-item-detail{margin-top:3px;color:rgba(var(--v-theme-on-surface),.68);overflow-wrap:anywhere;text-align:center}.log-item-detail:empty{display:none}
@media (max-width: 600px){.next-run-body{align-items:flex-start;flex-wrap:wrap}.next-run-copy{flex-basis:calc(100% - 52px)}.next-run-times{width:100%;justify-content:flex-start;padding-left:52px}.next-run-time{min-width:0;flex:1 1 140px;text-align:left}.next-run-time strong{white-space:normal}.slot-card-body{min-height:220px}.slot-reels--large{max-width:none}.slot-reels--large span{height:58px;font-size:28px}.log-item-head,.log-item-detail{text-align:left}.log-item-head{justify-content:flex-start}}
</style>
