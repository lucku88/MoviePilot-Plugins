<template>
  <div class="vuepanel-page">
    <div class="vpp-shell">
      <header class="vpp-card vpp-hero">
        <div class="vpp-copy">
          <div class="vpp-badge">Vue-面板</div>
          <h1 class="vpp-title">{{ dashboard.title || '状态页' }}</h1>
          <div class="vpp-chip-row">
            <span class="vpp-chip">主题 {{ themeLabel }}</span>
            <span class="vpp-chip">计划执行 {{ status.next_run_time || dashboard.next_run_time || '未启用' }}</span>
            <span class="vpp-chip">最近执行 {{ status.last_run || '暂无' }}</span>
            <span class="vpp-chip">模块 {{ moduleSections.length }} 个</span>
            <span class="vpp-chip">日志 {{ activityLogCount }}</span>
          </div>
        </div>

        <div class="vpp-action-grid">
          <v-btn color="success" variant="flat" :loading="loading" @click="runAll">执行启用任务</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshStatus">刷新状态</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vpp-stat-grid">
        <article v-for="item in summaryCards" :key="item.label" class="vpp-card vpp-stat">
          <div class="vpp-stat-label">{{ item.label }}</div>
          <div class="vpp-stat-value">{{ item.value }}</div>
        </article>
      </section>

      <section
        v-for="section in moduleSections"
        :key="section.module_key"
        class="vpp-card vpp-module"
        :style="toneStyle(section.tone)"
      >
        <div class="vpp-module-head">
          <div>
            <div class="vpp-kicker">{{ section.singleton ? '固定模块' : '多站点模块' }}</div>
            <h2 class="vpp-section-title">{{ section.module_icon }} {{ section.module_name }}</h2>
          </div>

          <div class="vpp-pill-row">
            <span v-for="stat in section.stats || []" :key="`${section.module_key}-${stat.label}`" class="vpp-pill">
              {{ stat.label }} {{ stat.value }}
            </span>
            <span v-if="section.latest_run" class="vpp-pill">最近 {{ section.latest_run }}</span>
          </div>
        </div>

        <div class="vpp-module-body" :class="{ single: section.singleton }">
          <div class="vpp-card-grid" :class="{ single: section.singleton, multi: !section.singleton }">
            <article
              v-for="card in section.cards || []"
              :key="card.card_id"
              class="vpp-panel"
              :style="toneStyle(card.tone || section.tone)"
            >
              <div class="vpp-panel-top">
                <div>
                  <div class="vpp-panel-kicker">{{ card.site_name }}</div>
                  <div class="vpp-panel-title">{{ card.status_title }}</div>
                </div>
                <span class="vpp-level" :class="`is-${cardLevel(card.level)}`">{{ levelLabel(card.level) }}</span>
              </div>

              <div v-if="!section.singleton" class="vpp-panel-site">{{ card.site_url }}</div>
              <div class="vpp-panel-text">{{ card.status_text }}</div>

              <div v-if="card.metrics?.length" class="vpp-metric-grid">
                <div v-for="metric in card.metrics" :key="`${card.card_id}-${metric.label}`" class="vpp-metric">
                  <div class="vpp-metric-label">{{ metric.label }}</div>
                  <div class="vpp-metric-value">{{ metric.value }}</div>
                </div>
              </div>

              <div v-if="card.tags?.length" class="vpp-tag-row">
                <span
                  v-for="tag in card.tags"
                  :key="`${card.card_id}-${tag}`"
                  class="vpp-tag"
                  :class="`is-${tagTone(tag)}`"
                >
                  {{ tag }}
                </span>
              </div>

              <div v-if="card.detail_lines?.length" class="vpp-detail-list">
                <div v-for="line in card.detail_lines" :key="`${card.card_id}-${line}`" class="vpp-detail-item">{{ line }}</div>
              </div>

              <div class="vpp-meta-grid">
                <div class="vpp-meta-item">
                  <span class="vpp-meta-label">执行</span>
                  <strong>{{ card.last_run || '未执行' }}</strong>
                </div>
                <div class="vpp-meta-item">
                  <span class="vpp-meta-label">计划</span>
                  <strong>{{ scheduleText(card) }}</strong>
                </div>
              </div>

              <div class="vpp-btn-row">
                <v-btn color="primary" variant="flat" :loading="runningCardId === card.card_id" @click="runCard(card)">执行</v-btn>
                <v-btn variant="text" :loading="refreshingCardId === card.card_id" @click="refreshCard(card)">刷新</v-btn>
              </div>
            </article>

            <div v-if="!(section.cards || []).length" class="vpp-empty">
              当前模块还没有可显示的状态卡片。
            </div>
          </div>

          <aside class="vpp-side-stack">
            <section v-if="sectionNotifications(section).length" class="vpp-side-card">
              <div class="vpp-side-head">
                <div>
                  <div class="vpp-kicker">模块通知</div>
                  <div class="vpp-side-title">需要关注的变化</div>
                </div>
                <span class="vpp-side-count">{{ sectionNotifications(section).length }}</span>
              </div>

              <div class="vpp-side-list">
                <article
                  v-for="item in sectionNotifications(section).slice(0, 3)"
                  :key="`${section.module_key}-notice-${item.id}`"
                  class="vpp-side-item notice"
                >
                  <div class="vpp-side-top">
                    <strong>{{ item.title }}</strong>
                    <span class="vpp-side-time">{{ item.time }}</span>
                  </div>
                  <div class="vpp-side-summary">{{ item.summary }}</div>
                </article>
              </div>
            </section>

            <section class="vpp-side-card">
              <div class="vpp-side-head">
                <div>
                  <div class="vpp-kicker">执行记录</div>
                  <div class="vpp-side-title">最近日志</div>
                </div>
                <span class="vpp-side-count">{{ sectionLogs(section).length }}</span>
              </div>

              <div v-if="!sectionLogs(section).length" class="vpp-empty">
                当前模块还没有执行记录。
              </div>

              <div v-else class="vpp-side-list">
                <article
                  v-for="item in sectionLogs(section).slice(0, 6)"
                  :key="`${section.module_key}-log-${item.id}`"
                  class="vpp-side-item log"
                >
                  <div class="vpp-side-top">
                    <strong>{{ historyTitle(section, item) }}</strong>
                    <span class="vpp-side-time">{{ item.time }}</span>
                  </div>
                  <div v-if="historyMeta(section, item)" class="vpp-side-meta">{{ historyMeta(section, item) }}</div>
                  <div class="vpp-side-summary">{{ historySummary(item) }}</div>
                  <div v-if="item.lines?.length" class="vpp-side-lines">{{ item.lines.join(' / ') }}</div>
                </article>
              </div>
            </section>
          </aside>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

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
const summaryCards = computed(() => {
  const overview = dashboard.value.overview || []
  const map = new Map(overview.map((item) => [item.label, item]))
  const preferred = ['配置卡片', '状态卡片', '自动执行', '成功状态', '异常状态']
  const picked = preferred.map((label) => map.get(label)).filter(Boolean)
  return picked.length ? picked : overview.slice(0, 5)
})

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpp-tone-rgb': '40,181,120' },
    azure: { '--vpp-tone-rgb': '46,134,255' },
    amber: { '--vpp-tone-rgb': '255,170,63' },
    rose: { '--vpp-tone-rgb': '230,92,124' },
    violet: { '--vpp-tone-rgb': '132,108,255' },
    slate: { '--vpp-tone-rgb': '120,132,155' },
  }
  return map[tone] || map.azure
}

function cardLevel(level) {
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  return 'info'
}

function levelLabel(level) {
  return ({ success: '正常', warning: '待处理', error: '异常', info: '信息' })[level] || '信息'
}

function tagTone(tag) {
  if (tag.includes('已启用')) return 'success'
  if (tag.includes('已停用')) return 'disabled'
  if (tag.includes('Cron 无效')) return 'danger'
  if (tag.includes('Cookie')) return 'primary'
  if (tag.includes('UID')) return 'info'
  return 'warning'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function fallbackLogFromCard(section, card) {
  const time = String(card?.last_run || card?.last_checked || '').trim()
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

function historySummary(item) {
  return item.summary || (item.lines || []).join(' / ') || '暂无详情'
}

function historyTitle(section, item) {
  if (!section?.singleton) return item?.site_name || item?.title || section?.module_name || ''
  return item?.title || section?.module_name || ''
}

function historyMeta(section, item) {
  if (section?.singleton) return item?.site_name || item?.site_url || ''
  const parts = []
  if (item?.title && item.title !== item?.site_name) parts.push(item.title)
  if (item?.site_url) parts.push(item.site_url)
  return parts.join(' / ')
}

function sectionLogs(section) {
  const activityLogs = Array.isArray(section?.activity_logs) ? section.activity_logs.filter(Boolean) : []
  if (activityLogs.length) {
    return activityLogs.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }

  const historyLogs = Array.isArray(section?.history)
    ? section.history
        .filter(Boolean)
        .map((item) => ({
          id: item.id || `${section.module_key}-${item.time || item.title}`,
          title: item.title || item.status_title || section.module_name,
          summary: item.summary || '',
          level: item.level || 'info',
          time: item.time || '',
          lines: item.lines || [],
          site_name: item.site_name || '',
          site_url: item.site_url || '',
        }))
        .filter((item) => item.time)
    : []
  if (historyLogs.length) {
    return historyLogs.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }

  return (section?.cards || [])
    .map((card) => fallbackLogFromCard(section, card))
    .filter(Boolean)
    .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
}

function sectionNotifications(section) {
  const notices = Array.isArray(section?.notifications) ? section.notifications.filter(Boolean) : []
  if (notices.length) {
    return notices.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }
  return sectionLogs(section).filter((item) => item.level === 'warning' || item.level === 'error').slice(0, 4)
}

async function loadStatus(showError = true) {
  try {
    Object.assign(status, (await props.api.get('/plugin/VuePanel/status')) || {})
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
.vuepanel-page {
  --vpp-panel: color-mix(in srgb, var(--mp-bg-panel) 96%, transparent);
  --vpp-panel-strong: color-mix(in srgb, var(--mp-bg-card) 96%, transparent);
  --vpp-text: var(--mp-text-primary);
  --vpp-muted: var(--mp-text-secondary);
  --vpp-border: var(--mp-border-color);
  --vpp-border-strong: var(--mp-border-strong);
  --vpp-shadow: var(--mp-shadow-card);
  --vpp-accent: var(--mp-color-primary);
  --vpp-accent-soft: color-mix(in srgb, var(--mp-color-primary) 12%, transparent);
  min-height: 100%;
  padding: 8px 0 18px;
  color: var(--vpp-text);
}

.vuepanel-page,
.vuepanel-page * {
  box-sizing: border-box;
}

.vpp-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 12px;
  display: grid;
  gap: 10px;
}

.vpp-card,
.vpp-panel,
.vpp-side-card {
  border: 1px solid var(--vpp-border);
  border-radius: 18px;
  background: var(--vpp-panel);
  box-shadow: var(--vpp-shadow);
  backdrop-filter: blur(16px);
}

.vpp-card,
.vpp-panel,
.vpp-side-card {
  padding: 12px;
}

.vpp-hero,
.vpp-chip-row,
.vpp-action-grid,
.vpp-module-head,
.vpp-pill-row,
.vpp-panel-top,
.vpp-tag-row,
.vpp-btn-row,
.vpp-side-head,
.vpp-side-top {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.vpp-hero {
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, var(--vpp-accent-soft) 0%, transparent 42%), var(--vpp-panel);
}

.vpp-copy {
  flex: 1;
  min-width: 0;
}

.vpp-badge,
.vpp-chip,
.vpp-pill,
.vpp-panel-site,
.vpp-level,
.vpp-tag,
.vpp-side-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}

.vpp-badge {
  padding: 5px 10px;
  background: var(--vpp-accent-soft);
  color: var(--vpp-accent);
  font-size: 11px;
  font-weight: 700;
}

.vpp-title,
.vpp-section-title,
.vpp-panel-title,
.vpp-side-title {
  margin: 0;
  font-weight: 900;
  letter-spacing: -0.02em;
}

.vpp-title {
  margin-top: 8px;
  font-size: clamp(22px, 3.8vw, 30px);
  line-height: 1.05;
}

.vpp-section-title,
.vpp-panel-title {
  font-size: 17px;
  line-height: 1.12;
}

.vpp-side-title {
  font-size: 14px;
}

.vpp-chip-row {
  margin-top: 10px;
}

.vpp-chip,
.vpp-pill {
  padding: 6px 10px;
  border: 1px solid var(--vpp-border-strong);
  background: var(--vpp-panel-strong);
  font-size: 11px;
  font-weight: 700;
}

.vpp-action-grid {
  justify-content: flex-end;
  min-width: min(100%, 420px);
}

.vpp-action-grid :deep(.v-btn),
.vpp-btn-row :deep(.v-btn) {
  min-height: 38px;
  border-radius: 12px;
  font-weight: 800;
  text-transform: none;
}

.vpp-kicker,
.vpp-stat-label,
.vpp-panel-kicker,
.vpp-panel-text,
.vpp-panel-site,
.vpp-metric-label,
.vpp-detail-item,
.vpp-meta-label,
.vpp-side-meta,
.vpp-side-summary,
.vpp-side-lines,
.vpp-side-time {
  color: var(--vpp-muted);
}

.vpp-kicker {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--vpp-accent);
}

.vpp-stat-grid,
.vpp-module-body,
.vpp-card-grid,
.vpp-metric-grid,
.vpp-meta-grid,
.vpp-side-stack,
.vpp-side-list,
.vpp-detail-list {
  display: grid;
  gap: 10px;
}

.vpp-stat-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.vpp-stat {
  background: linear-gradient(180deg, color-mix(in srgb, var(--mp-color-primary) 7%, transparent) 0%, transparent 100%), var(--vpp-panel-strong);
}

.vpp-stat-value {
  margin-top: 6px;
  font-size: 24px;
  font-weight: 900;
}

.vpp-module {
  display: grid;
  gap: 12px;
  background: linear-gradient(180deg, rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.08), transparent 52%), var(--vpp-panel);
}

.vpp-module-head {
  justify-content: space-between;
  align-items: flex-start;
}

.vpp-module-body {
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.9fr);
  align-items: start;
}

.vpp-module-body.single {
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.88fr);
}

.vpp-card-grid.single {
  grid-template-columns: 1fr;
}

.vpp-card-grid.multi {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpp-panel {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 8px;
  background: linear-gradient(180deg, rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.12), transparent 62%), var(--vpp-panel-strong);
}

.vpp-panel::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 4px;
  background: rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.48);
}

.vpp-panel-top,
.vpp-side-top {
  justify-content: space-between;
  align-items: flex-start;
}

.vpp-level,
.vpp-tag,
.vpp-panel-site,
.vpp-side-count {
  font-size: 11px;
  font-weight: 700;
}

.vpp-level {
  padding: 5px 9px;
  background: rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.12);
  color: var(--vpp-text);
}

.vpp-level.is-success {
  background: color-mix(in srgb, var(--mp-color-success) 16%, transparent);
  color: var(--mp-color-success);
}

.vpp-level.is-warning {
  background: color-mix(in srgb, var(--mp-color-warning) 18%, transparent);
  color: var(--mp-color-warning);
}

.vpp-level.is-danger {
  background: color-mix(in srgb, var(--mp-color-danger) 16%, transparent);
  color: var(--mp-color-danger);
}

.vpp-panel-site {
  justify-content: flex-start;
  padding: 4px 8px;
  background: rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.08);
}

.vpp-panel-text,
.vpp-side-summary,
.vpp-side-lines {
  font-size: 12px;
  line-height: 1.6;
}

.vpp-metric-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.vpp-metric,
.vpp-meta-item {
  padding: 8px 10px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--mp-bg-input) 94%, transparent);
  border: 1px solid color-mix(in srgb, var(--vpp-border) 92%, transparent);
}

.vpp-metric-value {
  margin-top: 4px;
  font-size: 15px;
  font-weight: 900;
}

.vpp-tag-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, max-content));
  gap: 6px;
}

.vpp-tag {
  justify-content: flex-start;
  padding: 6px 9px;
  background: rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.11);
  color: var(--vpp-text);
}

.vpp-tag.is-success {
  background: color-mix(in srgb, var(--mp-color-success) 14%, transparent);
  color: var(--mp-color-success);
}

.vpp-tag.is-danger {
  background: color-mix(in srgb, var(--mp-color-danger) 14%, transparent);
  color: var(--mp-color-danger);
}

.vpp-tag.is-warning {
  background: color-mix(in srgb, var(--mp-color-warning) 16%, transparent);
  color: var(--mp-color-warning);
}

.vpp-tag.is-disabled {
  background: color-mix(in srgb, var(--mp-color-disabled) 14%, transparent);
  color: var(--mp-color-disabled);
}

.vpp-tag.is-primary {
  background: color-mix(in srgb, var(--mp-color-primary) 14%, transparent);
  color: var(--mp-color-primary);
}

.vpp-tag.is-info {
  background: color-mix(in srgb, var(--mp-color-secondary) 14%, transparent);
  color: var(--mp-color-secondary);
}

.vpp-detail-list {
  padding: 8px 10px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--mp-bg-input) 92%, transparent);
}

.vpp-detail-item,
.vpp-meta-label,
.vpp-side-meta,
.vpp-side-time {
  font-size: 11px;
}

.vpp-meta-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpp-meta-item {
  display: grid;
  gap: 4px;
}

.vpp-meta-item strong,
.vpp-side-top strong {
  font-size: 12px;
  line-height: 1.5;
}

.vpp-btn-row {
  justify-content: flex-end;
}

.vpp-side-stack {
  align-content: start;
}

.vpp-side-card {
  background: linear-gradient(180deg, rgba(var(--vpp-tone-rgb, 46, 134, 255), 0.08), transparent 52%), var(--vpp-panel-strong);
}

.vpp-side-head {
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.vpp-side-count {
  min-width: 30px;
  padding: 4px 8px;
  background: var(--vpp-accent-soft);
  color: var(--vpp-accent);
}

.vpp-side-item {
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--vpp-border);
  background: color-mix(in srgb, var(--mp-bg-input) 92%, transparent);
}

.vpp-side-top strong {
  flex: 1;
  min-width: 0;
}

.vpp-empty {
  padding: 16px;
  text-align: center;
  border: 1px dashed var(--vpp-border);
  border-radius: 16px;
  background: var(--vpp-panel-strong);
  color: var(--vpp-muted);
}

@media (max-width: 1080px) {
  .vpp-action-grid {
    justify-content: flex-start;
    min-width: 0;
  }

  .vpp-stat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .vpp-module-body,
  .vpp-module-body.single,
  .vpp-card-grid.multi,
  .vpp-metric-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .vpp-shell {
    padding: 0 10px;
  }

  .vpp-card,
  .vpp-panel,
  .vpp-side-card {
    border-radius: 16px;
    padding: 12px;
  }

  .vpp-hero,
  .vpp-module-head,
  .vpp-panel-top,
  .vpp-side-head,
  .vpp-side-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpp-stat-grid,
  .vpp-meta-grid {
    grid-template-columns: 1fr;
  }

  .vpp-btn-row {
    justify-content: stretch;
  }

  .vpp-btn-row :deep(.v-btn) {
    flex: 1 1 calc(50% - 8px);
  }
}
</style>
