<template>
  <div class="page-board">
    <BasePanelCard
      kicker="Vue-面板"
      title="运行监控看板"
      :subtitle="dashboard.subtitle || `当前主题：${themeLabel}。模块状态、通知和执行记录都在同一套看板里集中查看。`"
      tone="primary"
      class="board-hero"
    >
      <template #actions>
        <div class="hero-actions">
          <BaseButton :loading="loading" @click="runAll">执行启用任务</BaseButton>
          <BaseButton variant="secondary" :loading="loading" @click="refreshStatus">刷新状态</BaseButton>
          <BaseButton variant="ghost" @click="emit('switch', 'config')">配置</BaseButton>
          <BaseButton variant="ghost" @click="closePlugin">关闭</BaseButton>
        </div>
      </template>

      <div class="hero-chips">
        <BaseTag tone="primary">主题 {{ themeLabel }}</BaseTag>
        <BaseTag tone="info">计划执行 {{ status.next_run_time || dashboard.next_run_time || '未启用' }}</BaseTag>
        <BaseTag tone="info">最近执行 {{ status.last_run || '暂无' }}</BaseTag>
        <BaseTag tone="success">通知 {{ notifications.length }}</BaseTag>
        <BaseTag tone="warning">日志 {{ activityLogs.length }}</BaseTag>
      </div>
    </BasePanelCard>

    <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

    <section class="stats-grid">
      <SummaryStatCard
        v-for="item in dashboard.overview || []"
        :key="item.label"
        :label="item.label"
        :value="item.value"
        :tone="statTone(item.label)"
      />
    </section>

    <section class="module-grid">
      <BasePanelCard
        v-for="section in moduleSections"
        :key="section.module_key"
        :kicker="section.singleton ? '固定模块' : '多站点模块'"
        :title="`${section.module_icon} ${section.module_name}`"
        :subtitle="moduleSubtitle(section)"
        :tone="section.tone"
      >
        <template #actions>
          <div class="module-head-actions">
            <BaseTag v-for="stat in section.stats || []" :key="`${section.module_key}-${stat.label}`" tone="primary" size="sm">
              {{ stat.label }} {{ stat.value }}
            </BaseTag>
          </div>
        </template>

        <EmptyState
          v-if="!(section.cards || []).length"
          title="暂无状态卡片"
          description="当前模块还没有可展示的状态信息。"
        />

        <div v-else class="task-grid" :class="{ single: section.singleton }">
          <article
            v-for="card in section.cards"
            :key="card.card_id"
            class="task-card"
          >
            <div class="task-card-head">
              <div>
                <div class="task-card-site">{{ card.site_name }}</div>
                <div class="task-card-title">{{ card.status_title }}</div>
              </div>
              <BaseTag :tone="levelTone(card.level)" size="sm" dot>{{ levelText(card.level) }}</BaseTag>
            </div>

            <div v-if="!section.singleton" class="task-card-url">{{ card.site_url }}</div>
            <div class="task-card-summary">{{ card.status_text }}</div>

            <div v-if="card.metrics?.length" class="metric-grid">
              <div v-for="metric in card.metrics" :key="`${card.card_id}-${metric.label}`" class="metric-item">
                <div class="metric-label">{{ metric.label }}</div>
                <div class="metric-value">{{ metric.value }}</div>
              </div>
            </div>

            <div class="tag-row">
              <BaseTag
                v-for="tag in card.tags || []"
                :key="`${card.card_id}-${tag}`"
                :tone="tagColor(tag)"
                size="sm"
              >
                {{ tag }}
              </BaseTag>
            </div>

            <div class="task-meta">
              <div class="meta-block">
                <span class="meta-label">上次执行</span>
                <strong>{{ card.last_run || '未执行' }}</strong>
              </div>
              <div class="meta-block">
                <span class="meta-label">下次计划</span>
                <strong>{{ scheduleText(card) }}</strong>
              </div>
            </div>

            <div v-if="card.detail_lines?.length" class="task-detail">
              <div v-for="line in card.detail_lines" :key="`${card.card_id}-${line}`" class="detail-line">{{ line }}</div>
            </div>

            <div class="task-actions">
              <BaseButton size="sm" :loading="runningCardId === card.card_id" @click="runCard(card)">执行</BaseButton>
              <BaseButton variant="secondary" size="sm" :loading="refreshingCardId === card.card_id" @click="refreshCard(card)">刷新</BaseButton>
            </div>
          </article>
        </div>
      </BasePanelCard>
    </section>

    <section class="feed-grid">
      <NotificationList :items="notifications" />
      <ActivityLogList :items="activityLogs" />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import ActivityLogList from './blocks/ActivityLogList.vue'
import NotificationList from './blocks/NotificationList.vue'
import BaseButton from './ui/BaseButton.vue'
import BasePanelCard from './ui/BasePanelCard.vue'
import BaseTag from './ui/BaseTag.vue'
import EmptyState from './ui/EmptyState.vue'
import SummaryStatCard from './ui/SummaryStatCard.vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

const emit = defineEmits(['switch', 'close'])

const loading = ref(false)
const runningCardId = ref('')
const refreshingCardId = ref('')
const status = reactive({ dashboard: {}, history: [] })
const message = reactive({ text: '', type: 'success' })

const dashboard = computed(() => status.dashboard || {})
const moduleSections = computed(() => dashboard.value.module_sections || [])
const notifications = computed(() => dashboard.value.notifications || [])
const activityLogs = computed(() => dashboard.value.activity_logs || [])

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function statTone(label) {
  if (/成功/.test(label)) return 'success'
  if (/异常/.test(label)) return 'danger'
  if (/待处理|通知/.test(label)) return 'warning'
  return 'default'
}

function levelTone(level) {
  if (level === 'success') return 'success'
  if (level === 'error') return 'danger'
  if (level === 'warning') return 'warning'
  return 'info'
}

function levelText(level) {
  return ({ success: '成功', error: '异常', warning: '待处理', info: '信息' })[level] || '信息'
}

function tagColor(tag) {
  if (tag.includes('已启用')) return 'success'
  if (tag.includes('已停用') || tag.includes('仅手动')) return 'disabled'
  if (tag.includes('Cron 无效')) return 'danger'
  if (tag.includes('Cookie')) return 'primary'
  if (tag.includes('UID')) return 'info'
  return 'warning'
}

function moduleSubtitle(section) {
  if (section.latest_run) return `最近一次执行：${section.latest_run}`
  return section.singleton ? '固定任务卡片，适合快速查看执行和调度状态。' : '多站点模块，适合批量管理同类站点卡片。'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

async function loadStatus(showError = true) {
  try {
    Object.assign(status, await props.api.get('/plugin/VuePanel/status') || {})
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  }
}

async function refreshStatus() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/refresh', {})
    flash(res.message || '已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '刷新失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runAll() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/run', {})
    flash(res.message || '执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runCard(card) {
  runningCardId.value = card.card_id
  try {
    const res = await props.api.post('/plugin/VuePanel/card/run', { card_id: card.card_id })
    flash(res.message || '卡片执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片执行失败', 'error')
  } finally {
    runningCardId.value = ''
  }
}

async function refreshCard(card) {
  refreshingCardId.value = card.card_id
  try {
    const res = await props.api.post('/plugin/VuePanel/card/refresh', { card_id: card.card_id })
    flash(res.message || '卡片状态已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片刷新失败', 'error')
  } finally {
    refreshingCardId.value = ''
  }
}

function closePlugin() {
  emit('close')
}

onMounted(async () => {
  await loadStatus()
})
</script>

<style scoped>
.page-board,
.stats-grid,
.module-grid,
.feed-grid,
.hero-actions,
.hero-chips,
.module-head-actions,
.tag-row,
.task-card-head,
.task-meta,
.task-actions {
  display: grid;
  gap: 12px;
}

.page-board {
  gap: 12px;
}

.board-hero {
  background: linear-gradient(135deg, color-mix(in srgb, var(--mp-color-primary) 14%, transparent) 0%, transparent 42%), var(--mp-bg-panel);
}

.hero-actions,
.hero-chips,
.module-head-actions,
.tag-row,
.task-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-actions {
  justify-content: flex-end;
}

.stats-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.module-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.feed-grid {
  grid-template-columns: minmax(0, .92fr) minmax(0, 1.08fr);
  align-items: start;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.task-grid.single {
  grid-template-columns: 1fr;
}

.task-card {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--mp-border-color);
  border-radius: var(--mp-radius-lg);
  background: color-mix(in srgb, var(--mp-bg-card) 88%, transparent);
}

.task-card-head,
.task-meta {
  display: flex;
  gap: 8px;
  justify-content: space-between;
  align-items: flex-start;
}

.task-card-site,
.task-card-url,
.metric-label,
.meta-label,
.detail-line {
  color: var(--mp-text-secondary);
  font-size: var(--mp-font-sm);
  line-height: 1.6;
}

.task-card-title {
  margin-top: 4px;
  font-size: var(--mp-font-lg);
  font-weight: 800;
  color: var(--mp-text-primary);
}

.task-card-summary {
  font-size: var(--mp-font-md);
  line-height: 1.7;
  color: var(--mp-text-primary);
}

.metric-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric-item,
.meta-block {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 60%, transparent);
}

.metric-value,
.meta-block strong {
  font-size: var(--mp-font-lg);
  font-weight: 800;
  color: var(--mp-text-primary);
}

.task-detail {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 48%, transparent);
}

@media (max-width: 1180px) {
  .stats-grid,
  .module-grid,
  .feed-grid,
  .task-grid,
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .hero-actions,
  .hero-chips,
  .module-head-actions,
  .task-actions,
  .task-card-head,
  .task-meta {
    justify-content: flex-start;
  }

  .stats-grid,
  .module-grid,
  .feed-grid,
  .task-grid,
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
