<template>
  <div class="page-board">
    <BasePanelCard
      kicker="Vue-面板"
      title="运行监控看板"
      :subtitle="dashboard.subtitle || `当前主题：${themeLabel}。模块状态、调度和最近执行记录按模块拆开查看。`"
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
        <BaseTag tone="success">模块 {{ moduleSections.length }}</BaseTag>
        <BaseTag tone="warning">日志 {{ activityLogCount }}</BaseTag>
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

    <section class="module-stack">
      <BasePanelCard
        v-for="section in moduleSections"
        :key="section.module_key"
        :kicker="section.singleton ? '固定模块' : '多站点模块'"
        :title="`${section.module_icon} ${section.module_name}`"
        :subtitle="moduleSubtitle(section)"
        :tone="section.tone"
        compact
      >
        <template #actions>
          <div class="module-head-actions">
            <BaseTag v-for="stat in section.stats || []" :key="`${section.module_key}-${stat.label}`" tone="primary" size="sm">
              {{ stat.label }} {{ stat.value }}
            </BaseTag>
          </div>
        </template>

        <div class="module-layout" :class="{ single: section.singleton }">
          <div class="task-grid" :class="{ single: section.singleton }">
            <EmptyState
              v-if="!(section.cards || []).length"
              title="暂无状态卡片"
              description="当前模块还没有可展示的状态信息。"
            />

            <article
              v-for="card in section.cards || []"
              :key="card.card_id"
              class="task-card"
              :style="toneStyle(card.tone || section.tone)"
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

              <div v-if="card.detail_lines?.length" class="task-detail">
                <div v-for="line in card.detail_lines" :key="`${card.card_id}-${line}`" class="detail-line">{{ line }}</div>
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

              <div class="task-actions">
                <BaseButton size="sm" :loading="runningCardId === card.card_id" @click="runCard(card)">执行</BaseButton>
                <BaseButton variant="secondary" size="sm" :loading="refreshingCardId === card.card_id" @click="refreshCard(card)">刷新</BaseButton>
              </div>
            </article>
          </div>

          <aside class="module-side">
            <section class="side-block">
              <div class="side-head">
                <div class="side-title">通知</div>
                <BaseTag tone="violet" size="sm">{{ sectionNotifications(section).length }}</BaseTag>
              </div>

              <div v-if="!sectionNotifications(section).length" class="side-empty">当前模块暂无需要关注的通知。</div>

              <div v-else class="side-list">
                <article
                  v-for="item in sectionNotifications(section).slice(0, 4)"
                  :key="`${section.module_key}-notice-${item.id}`"
                  class="side-item notice"
                >
                  <div class="side-item-head">
                    <BaseTag :tone="levelTone(item.level)" size="sm" dot>{{ levelText(item.level) }}</BaseTag>
                    <span class="side-time">{{ item.time }}</span>
                  </div>
                  <div class="side-item-title">{{ item.title }}</div>
                  <div class="side-item-summary">{{ item.summary }}</div>
                </article>
              </div>
            </section>

            <section class="side-block">
              <div class="side-head">
                <div class="side-title">最近记录</div>
                <BaseTag tone="primary" size="sm">{{ sectionLogs(section).length }}</BaseTag>
              </div>

              <div v-if="!sectionLogs(section).length" class="side-empty">执行或刷新后，最近记录会显示在这里。</div>

              <div v-else class="side-list">
                <article
                  v-for="item in sectionLogs(section).slice(0, 6)"
                  :key="`${section.module_key}-log-${item.id}`"
                  class="side-item log"
                >
                  <div class="side-item-head">
                    <div class="side-item-title">{{ item.title }}</div>
                    <span class="side-time">{{ item.time }}</span>
                  </div>
                  <div v-if="item.site_name" class="side-item-meta">{{ item.site_name }}</div>
                  <div class="side-item-summary">{{ item.summary }}</div>
                  <div v-if="item.lines?.length" class="side-item-detail">{{ item.lines.join(' / ') }}</div>
                </article>
              </div>
            </section>
          </aside>
        </div>
      </BasePanelCard>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
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
const activityLogCount = computed(() => moduleSections.value.reduce((total, section) => total + sectionLogs(section).length, 0))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function toneStyle(tone) {
  const map = {
    emerald: { '--task-tone': '31, 168, 104' },
    azure: { '--task-tone': '79, 134, 255' },
    amber: { '--task-tone': '229, 155, 47' },
    rose: { '--task-tone': '220, 87, 87' },
    violet: { '--task-tone': '139, 92, 246' },
    slate: { '--task-tone': '120, 132, 155' },
  }
  return map[tone] || map.azure
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
  return section.singleton ? '固定任务单卡，适合快速查看当前状态和调度信息。' : '显式多站点模块，站点卡之间完全独立。'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function fallbackLogFromCard(section, card) {
  const time = card.last_run || card.last_checked || ''
  if (!time) return null
  return {
    id: `fallback-${card.card_id}-${time}`,
    title: card.status_title || card.site_name || section.module_name,
    summary: card.status_text || '',
    level: card.level || 'info',
    time,
    lines: card.detail_lines || [],
    site_name: card.site_name || '',
    site_url: card.site_url || '',
  }
}

function sectionLogs(section) {
  const logs = Array.isArray(section?.activity_logs) ? section.activity_logs.filter(Boolean) : []
  if (logs.length) return logs
  return (section?.cards || []).map((card) => fallbackLogFromCard(section, card)).filter(Boolean)
}

function sectionNotifications(section) {
  const notices = Array.isArray(section?.notifications) ? section.notifications.filter(Boolean) : []
  if (notices.length) return notices
  return sectionLogs(section).filter((item) => item.level === 'warning' || item.level === 'error').slice(0, 4)
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
.page-board {
  display: grid;
  gap: 10px;
  padding-inline: 2px;
}

.board-hero {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--mp-color-primary) 12%, transparent) 0%, transparent 44%),
    var(--mp-bg-panel);
}

.hero-actions,
.hero-chips,
.module-head-actions,
.tag-row,
.task-actions,
.task-card-head,
.task-meta,
.side-head,
.side-item-head {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-actions {
  justify-content: flex-end;
}

.stats-grid,
.module-stack,
.module-layout,
.task-grid,
.metric-grid,
.module-side,
.side-list {
  display: grid;
  gap: 10px;
}

.stats-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.module-layout {
  grid-template-columns: minmax(0, 1.75fr) minmax(300px, 0.95fr);
  align-items: start;
}

.module-layout.single {
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.9fr);
}

.task-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.task-grid.single {
  grid-template-columns: 1fr;
}

.task-card {
  --task-tone: 79, 134, 255;
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid color-mix(in srgb, rgb(var(--task-tone)) 22%, var(--mp-border-color));
  border-radius: var(--mp-radius-lg);
  background:
    linear-gradient(180deg, color-mix(in srgb, rgb(var(--task-tone)) 8%, transparent), transparent 42%),
    color-mix(in srgb, var(--mp-bg-card) 96%, transparent);
  box-shadow: 0 10px 22px color-mix(in srgb, var(--mp-shadow-color) 72%, transparent);
}

.task-card-head,
.task-meta,
.side-head,
.side-item-head {
  justify-content: space-between;
  align-items: flex-start;
}

.task-card-site,
.task-card-url,
.metric-label,
.meta-label,
.detail-line,
.side-item-meta,
.side-item-summary,
.side-item-detail,
.side-time,
.side-empty {
  color: var(--mp-text-secondary);
  font-size: var(--mp-font-sm);
  line-height: 1.55;
}

.task-card-title,
.side-item-title {
  margin-top: 2px;
  font-size: var(--mp-font-lg);
  font-weight: 900;
  color: var(--mp-text-primary);
}

.task-card-summary {
  font-size: var(--mp-font-md);
  line-height: 1.6;
  color: var(--mp-text-primary);
}

.metric-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric-item,
.meta-block,
.side-block {
  display: grid;
  gap: 4px;
  padding: 10px 11px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 55%, var(--mp-bg-panel-strong));
  border: 1px solid color-mix(in srgb, var(--mp-border-color) 76%, transparent);
}

.metric-value,
.meta-block strong {
  font-size: var(--mp-font-lg);
  font-weight: 850;
  color: var(--mp-text-primary);
}

.task-detail {
  display: grid;
  gap: 5px;
  padding: 10px 11px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 42%, transparent);
}

.module-side {
  align-content: start;
}

.side-title {
  font-size: var(--mp-font-md);
  font-weight: 850;
  color: var(--mp-text-primary);
}

.side-list {
  gap: 8px;
}

.side-item {
  display: grid;
  gap: 6px;
  padding: 10px 11px;
  border-radius: var(--mp-radius-md);
  border: 1px solid color-mix(in srgb, var(--mp-border-color) 78%, transparent);
  background: color-mix(in srgb, var(--mp-bg-card) 94%, transparent);
}

.side-item.notice {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--mp-color-secondary) 7%, transparent), transparent 42%),
    color-mix(in srgb, var(--mp-bg-card) 94%, transparent);
}

.side-item.log {
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--mp-color-primary) 7%, transparent), transparent 42%),
    color-mix(in srgb, var(--mp-bg-card) 94%, transparent);
}

@media (max-width: 1180px) {
  .stats-grid,
  .task-grid,
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .module-layout,
  .module-layout.single {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .page-board {
    padding-inline: 0;
  }

  .hero-actions,
  .hero-chips,
  .module-head-actions,
  .task-actions,
  .task-card-head,
  .task-meta,
  .side-head,
  .side-item-head {
    justify-content: flex-start;
  }

  .stats-grid,
  .task-grid,
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
