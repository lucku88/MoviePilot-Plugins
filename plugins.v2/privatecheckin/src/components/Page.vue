<template>
  <div ref="rootEl" class="pc-page" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pc-shell">
      <section class="pc-hero">
        <div>
          <div class="pc-badge">自用签到</div>
          <h1 class="pc-title">数据页</h1>
          <p class="pc-subtitle">
            最近运行 {{ status.last_run || '暂无记录' }} · 下次计划 {{ status.next_run_time || '未启用或 Cron 无效' }}
          </p>
        </div>
        <div class="pc-actions">
          <v-btn color="success" variant="flat" :loading="loading" @click="runAll">立即执行全部</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="loadStatus">刷新状态</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置页</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="pc-stat-grid">
        <article class="pc-stat-card">
          <div class="pc-stat-label">启用任务</div>
          <div class="pc-stat-value">{{ status.enabled_task_count || 0 }}</div>
        </article>
        <article class="pc-stat-card">
          <div class="pc-stat-label">累计成功</div>
          <div class="pc-stat-value">{{ status.total_success_count || 0 }}</div>
        </article>
        <article class="pc-stat-card">
          <div class="pc-stat-label">累计失败</div>
          <div class="pc-stat-value">{{ status.total_fail_count || 0 }}</div>
        </article>
        <article class="pc-stat-card">
          <div class="pc-stat-label">强 CF 兜底</div>
          <div class="pc-stat-value">{{ status.flaresolverr_enabled ? 'FlareSolverr 已配置' : 'Playwright / 请求' }}</div>
        </article>
      </section>

      <section v-if="summaryLines.length" class="pc-panel">
        <div class="pc-panel-head">
          <div>
            <div class="pc-kicker">最近摘要</div>
            <h2>本轮执行结果</h2>
          </div>
        </div>
        <div class="pc-summary-list">
          <div v-for="line in summaryLines" :key="line" class="pc-summary-line">{{ line }}</div>
        </div>
      </section>

      <section class="pc-panel">
        <div class="pc-panel-head pc-panel-head-wrap">
          <div>
            <div class="pc-kicker">任务面板</div>
            <h2>站点签到 / 领取任务</h2>
          </div>
        </div>

        <div v-if="!tasks.length" class="pc-empty">
          暂无任务，请先去配置页新增。
        </div>

        <div v-else class="pc-task-grid">
          <article v-for="task in tasks" :key="task.id" class="pc-task-card">
            <header class="pc-task-head">
              <div>
                <div class="pc-task-name">{{ task.name }}</div>
                <div class="pc-mini">{{ task.task_type_label }} · {{ task.cf_mode_label }}</div>
              </div>
              <v-chip :color="resolveStatusColor(task.last_result)" size="small" variant="tonal">
                {{ resolveStatusText(task.last_result) }}
              </v-chip>
            </header>

            <div class="pc-chip-row">
              <v-chip size="small" variant="tonal">{{ task.enabled ? '已启用' : '未启用' }}</v-chip>
              <v-chip size="small" variant="tonal">{{ task.cookie_source || (task.use_moviepilot_cookie ? '待同步站点 Cookie' : '手动 Cookie') }}</v-chip>
              <v-chip size="small" variant="tonal">{{ task.last_method || '待执行' }}</v-chip>
            </div>

            <div class="pc-task-meta">
              <div><strong>任务地址：</strong>{{ task.target_url || '未填写' }}</div>
              <div><strong>站点地址：</strong>{{ task.site_url || '未填写' }}</div>
              <div><strong>最近执行：</strong>{{ task.last_run || '暂无记录' }}</div>
              <div><strong>最近结果：</strong>{{ task.last_message || '暂无' }}</div>
              <div><strong>成功/失败：</strong>{{ task.success_count || 0 }} / {{ task.fail_count || 0 }}</div>
            </div>

            <div v-if="task.recent?.length" class="pc-recent-list">
              <div class="pc-mini">最近 6 次</div>
              <div v-for="item in task.recent" :key="`${item.time}-${item.message}`" class="pc-recent-item">
                <span>{{ item.time }}</span>
                <span>{{ item.success ? '成功' : '失败' }}</span>
                <span>{{ item.message }}</span>
              </div>
            </div>

            <div class="pc-task-actions">
              <v-btn color="success" variant="flat" size="small" :loading="loadingTaskId === task.id" @click="runTask(task.id)">
                运行此任务
              </v-btn>
              <v-btn v-if="task.target_url" :href="task.target_url" target="_blank" rel="noreferrer" variant="text" size="small">
                打开地址
              </v-btn>
            </div>
          </article>
        </div>
      </section>

      <section class="pc-grid">
        <article class="pc-panel">
          <div class="pc-panel-head">
            <div>
              <div class="pc-kicker">执行历史</div>
              <h2>最近 30 条</h2>
            </div>
          </div>
          <div v-if="!historyItems.length" class="pc-empty">暂无执行记录</div>
          <div v-else class="pc-history-list">
            <article v-for="item in historyItems" :key="`${item.time}-${item.name}-${item.method}`" class="pc-history-item">
              <div class="pc-history-top">
                <strong>{{ item.name }}</strong>
                <span>{{ item.time }}</span>
              </div>
              <div class="pc-mini">
                {{ item.success ? '成功' : '失败' }} · {{ item.method || '未知方式' }} · {{ item.message }}
              </div>
            </article>
          </div>
        </article>

        <article class="pc-panel">
          <div class="pc-panel-head">
            <div>
              <div class="pc-kicker">运行说明</div>
              <h2>CF / Cookie 提示</h2>
            </div>
          </div>
          <div class="pc-guide-list">
            <div v-for="guide in status.guides || []" :key="guide" class="pc-guide-item">{{ guide }}</div>
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
})

const emit = defineEmits(['switch', 'close'])

const rootEl = ref(null)
const loading = ref(false)
const loadingTaskId = ref('')
const isDarkTheme = ref(false)
const message = reactive({ text: '', type: 'success' })
const status = reactive({
  enabled_task_count: 0,
  total_success_count: 0,
  total_fail_count: 0,
  summary: [],
  tasks: [],
  history: [],
  guides: [],
})

let themeObserver = null
let observedThemeNode = null

const tasks = computed(() => status.tasks || [])
const historyItems = computed(() => status.history || [])
const summaryLines = computed(() => status.summary || [])

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function resolveStatusText(result) {
  if (result === 'success') return '成功'
  if (result === 'error') return '失败'
  return '待执行'
}

function resolveStatusColor(result) {
  if (result === 'success') return 'success'
  if (result === 'error') return 'error'
  return 'default'
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
  const node = findThemeNode()
  const themeValue = node?.getAttribute?.('data-theme') || ''
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  isDarkTheme.value = ['dark', 'purple', 'transparent'].includes(themeValue) || (!themeValue && !!prefersDark)
}

function bindThemeObserver() {
  themeObserver?.disconnect()
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode()
    if (nextNode && nextNode !== observedThemeNode) {
      bindThemeObserver()
      return
    }
    detectTheme()
  })

  observedThemeNode = findThemeNode()
  if (observedThemeNode) {
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] })
  }
  themeObserver.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
  if (document.body) {
    themeObserver.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
  }
}

function applyStatus(payload) {
  Object.assign(status, payload || {})
}

async function loadStatus() {
  loading.value = true
  try {
    const payload = await props.api.get('/plugin/PrivateCheckin/status')
    applyStatus(payload)
  } catch (error) {
    flash(error?.message || '加载状态失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runAll() {
  loading.value = true
  try {
    const payload = await props.api.post('/plugin/PrivateCheckin/run', { force: true })
    applyStatus(payload?.status || status)
    flash(payload?.message || '执行完成', payload?.success === false ? 'warning' : 'success')
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runTask(taskId) {
  loadingTaskId.value = taskId
  try {
    const payload = await props.api.post('/plugin/PrivateCheckin/run', { task_id: taskId, force: true })
    applyStatus(payload?.status || status)
    flash(payload?.message || '任务执行完成', payload?.success === false ? 'warning' : 'success')
  } catch (error) {
    flash(error?.message || '任务执行失败', 'error')
  } finally {
    loadingTaskId.value = ''
  }
}

onMounted(() => {
  loadStatus()
  detectTheme()
  bindThemeObserver()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
})
</script>

<style scoped>
.pc-page {
  color: #13251a;
}

.pc-shell {
  display: grid;
  gap: 20px;
}

.pc-hero,
.pc-panel,
.pc-stat-card,
.pc-task-card {
  border: 1px solid rgba(21, 70, 52, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(12px);
  box-shadow: 0 18px 50px rgba(18, 48, 39, 0.08);
}

.pc-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.pc-badge,
.pc-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(19, 89, 59, 0.1);
  color: #12573a;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pc-title {
  margin: 14px 0 8px;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.08;
}

.pc-subtitle {
  margin: 0;
  color: #506355;
  line-height: 1.7;
}

.pc-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.pc-stat-grid,
.pc-task-grid,
.pc-grid {
  display: grid;
  gap: 20px;
}

.pc-stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.pc-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.pc-panel,
.pc-stat-card,
.pc-task-card {
  padding: 24px;
}

.pc-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.pc-panel-head-wrap {
  flex-wrap: wrap;
}

.pc-panel-head h2 {
  margin: 10px 0 0;
  font-size: 22px;
}

.pc-stat-label,
.pc-mini {
  color: #5d6d62;
  line-height: 1.7;
  font-size: 14px;
}

.pc-stat-value {
  margin-top: 10px;
  font-size: clamp(22px, 3vw, 34px);
  line-height: 1.12;
  font-weight: 700;
}

.pc-summary-list,
.pc-guide-list,
.pc-history-list {
  display: grid;
  gap: 10px;
}

.pc-summary-line,
.pc-guide-item,
.pc-history-item,
.pc-recent-item {
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(18, 87, 58, 0.06);
}

.pc-task-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.pc-task-head,
.pc-history-top,
.pc-task-actions,
.pc-chip-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.pc-chip-row {
  margin: 14px 0;
}

.pc-task-name {
  font-size: 22px;
  font-weight: 700;
}

.pc-task-meta,
.pc-recent-list {
  display: grid;
  gap: 8px;
}

.pc-task-meta {
  margin-bottom: 14px;
  color: #213428;
  line-height: 1.7;
}

.pc-recent-list {
  margin-bottom: 16px;
}

.pc-recent-item {
  display: grid;
  gap: 2px;
}

.pc-empty {
  padding: 24px;
  border-radius: 18px;
  background: rgba(18, 87, 58, 0.06);
  color: #46614f;
}

.is-dark-theme .pc-page {
  color: #ecf4ee;
}

.is-dark-theme .pc-hero,
.is-dark-theme .pc-panel,
.is-dark-theme .pc-stat-card,
.is-dark-theme .pc-task-card {
  background: rgba(18, 25, 22, 0.9);
  border-color: rgba(133, 190, 162, 0.16);
  box-shadow: 0 24px 56px rgba(0, 0, 0, 0.34);
}

.is-dark-theme .pc-subtitle,
.is-dark-theme .pc-stat-label,
.is-dark-theme .pc-mini,
.is-dark-theme .pc-empty,
.is-dark-theme .pc-task-meta {
  color: #b8c9be;
}

.is-dark-theme .pc-badge,
.is-dark-theme .pc-kicker {
  background: rgba(74, 182, 120, 0.16);
  color: #98efb0;
}

.is-dark-theme .pc-summary-line,
.is-dark-theme .pc-guide-item,
.is-dark-theme .pc-history-item,
.is-dark-theme .pc-recent-item {
  background: rgba(90, 132, 110, 0.12);
}

@media (max-width: 1080px) {
  .pc-grid,
  .pc-task-grid,
  .pc-stat-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .pc-hero,
  .pc-task-head,
  .pc-task-actions,
  .pc-history-top {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
