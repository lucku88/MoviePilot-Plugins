<template>
  <div class="vuepanel-page">
    <div class="vpp-shell">
      <header class="vpp-hero">
        <div class="vpp-hero-copy">
          <div class="vpp-kicker">Vue-面板</div>
          <h1 class="vpp-title">{{ dashboard.title || 'Vue-面板' }}</h1>
          <p class="vpp-subtitle">{{ dashboard.subtitle || '每个功能都是独立卡片，可直接配置、查看日志和复制。' }}</p>

          <div class="vpp-chip-row">
            <span class="vpp-chip">主题 {{ themeLabel }}</span>
            <span class="vpp-chip">卡片 {{ cards.length }}</span>
            <span class="vpp-chip">启用 {{ enabledCount }}</span>
            <span class="vpp-chip">下次 {{ status.next_run_time || dashboard.next_run_time || '未启用' }}</span>
            <span class="vpp-chip">最近 {{ status.last_run || '暂无' }}</span>
          </div>
        </div>

        <div class="vpp-hero-actions">
          <v-btn color="primary" variant="flat" :loading="loading.refreshAll" @click="refreshStatus">刷新状态</v-btn>
          <v-btn color="success" variant="flat" :loading="loading.runAll" @click="runAll">执行启用任务</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">全局设置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert
        v-if="message.text"
        :type="message.type"
        variant="tonal"
        rounded="xl"
        class="vpp-alert"
      >
        {{ message.text }}
      </v-alert>

      <section class="vpp-stat-grid">
        <article v-for="item in summaryCards" :key="item.label" class="vpp-stat-card">
          <span class="vpp-stat-label">{{ item.label }}</span>
          <strong class="vpp-stat-value">{{ item.value }}</strong>
        </article>
      </section>

      <section class="vpp-card-grid">
        <article
          v-for="card in cards"
          :key="card.card_id"
          class="vpp-card"
          :class="[{ 'is-enabled': card.enabled, 'is-disabled': !card.enabled }, `level-${runtimeTone(card.level)}`]"
          :style="toneStyle(card.tone)"
        >
          <div class="vpp-card-glow" />

          <div class="vpp-card-head">
            <div class="vpp-logo-wrap">
              <img
                v-if="logoSrc(card)"
                :src="logoSrc(card)"
                :alt="`${card.site_name} logo`"
                class="vpp-logo"
                @error="markLogoFailed(card.card_id)"
              />
              <span v-else class="vpp-logo-fallback">{{ card.module_icon || '•' }}</span>
            </div>

            <div class="vpp-card-copy">
              <div class="vpp-card-title-row">
                <h2 class="vpp-card-title">{{ card.title }}</h2>
                <span class="vpp-status-pill" :class="`is-${card.status_key}`">{{ card.status_label }}</span>
              </div>

              <p class="vpp-card-desc">{{ card.module_summary || 'plugin card' }}</p>

              <div class="vpp-card-meta">
                <span>{{ card.site_name || card.module_name }}</span>
                <span>{{ card.site_domain || card.site_url || '--' }}</span>
              </div>
            </div>
          </div>

          <div class="vpp-runtime-row">
            <span class="vpp-runtime-pill" :class="`is-${runtimeTone(card.level)}`">
              {{ runtimeLabel(card.level) }}
            </span>
            <span class="vpp-runtime-title">{{ card.status_title || '等待刷新' }}</span>
          </div>

          <p class="vpp-runtime-text">{{ card.status_text || '当前还没有可展示的运行状态。' }}</p>

          <div v-if="card.metrics?.length" class="vpp-metric-grid">
            <div v-for="metric in card.metrics.slice(0, 3)" :key="`${card.card_id}-${metric.label}`" class="vpp-metric">
              <span class="vpp-metric-label">{{ metric.label }}</span>
              <strong class="vpp-metric-value">{{ metric.value }}</strong>
            </div>
          </div>

          <div class="vpp-detail-grid">
            <div class="vpp-detail-item">
              <span class="vpp-detail-label">计划</span>
              <strong>{{ scheduleText(card) }}</strong>
            </div>
            <div class="vpp-detail-item">
              <span class="vpp-detail-label">上次执行</span>
              <strong>{{ card.last_run || '暂无' }}</strong>
            </div>
            <div class="vpp-detail-item">
              <span class="vpp-detail-label">日志</span>
              <strong>{{ card.log_count || 0 }} 条</strong>
            </div>
          </div>

          <div v-if="card.note || card.detail_lines?.length" class="vpp-note-box">
            {{ card.note || card.detail_lines?.[0] || card.module_description }}
          </div>

          <div class="vpp-tag-row">
            <span v-for="tag in previewTags(card.tags)" :key="`${card.card_id}-${tag}`" class="vpp-tag">{{ tag }}</span>
          </div>

          <div class="vpp-action-row">
            <v-btn class="vpp-action-btn is-config" variant="text" prepend-icon="mdi-cog-outline" @click="openConfigDialog(card)">配置</v-btn>
            <v-btn class="vpp-action-btn is-logs" variant="text" prepend-icon="mdi-text-box-outline" @click="openLogsDialog(card)">日志</v-btn>
            <v-btn class="vpp-action-btn is-copy" variant="text" prepend-icon="mdi-content-copy" @click="openCopyDialog(card)">复制</v-btn>
          </div>
        </article>
      </section>
    </div>

    <v-dialog v-model="dialog.config" max-width="860">
      <v-card class="vpp-dialog-card vpp-dialog-config">
        <div class="vpp-dialog-head">
          <div>
            <div class="vpp-kicker">配置</div>
            <h3 class="vpp-dialog-title">{{ editor.title || activeDashboardCard?.title || '功能配置' }}</h3>
          </div>
          <span class="vpp-status-pill" :class="`is-${editor.enabled ? 'enabled' : 'disabled'}`">
            {{ editor.enabled ? '启用' : '停用' }}
          </span>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-dialog-banner">
            当前设置会直接写入这张功能卡片，后续多站点需求请通过复制卡片来扩展。
          </div>

          <div class="vpp-switch-grid">
            <label class="vpp-switch-card">
              <span class="vpp-switch-label">启用功能</span>
              <v-switch v-model="editor.enabled" hide-details color="primary" density="compact" />
            </label>
            <label class="vpp-switch-card">
              <span class="vpp-switch-label">定时执行</span>
              <v-switch v-model="editor.auto_run" hide-details color="primary" density="compact" />
            </label>
            <label class="vpp-switch-card">
              <span class="vpp-switch-label">发送通知</span>
              <v-switch v-model="editor.notify" hide-details color="primary" density="compact" />
            </label>
          </div>

          <div class="vpp-form-grid">
            <v-text-field v-model="editor.title" label="功能名称" variant="outlined" density="comfortable" hide-details="auto" />
            <v-text-field v-model="editor.site_name" label="网站名称" variant="outlined" density="comfortable" hide-details="auto" />
            <v-text-field v-model="editor.site_url" label="网站地址" variant="outlined" density="comfortable" hide-details="auto" />
            <v-text-field
              v-if="editor.module_key === 'newapi_checkin'"
              v-model="editor.uid"
              label="UID"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
            />
            <v-text-field v-model="editor.cron" label="Cron" variant="outlined" density="comfortable" hide-details="auto" />
            <v-select
              v-model="editor.tone"
              :items="toneSelectItems"
              item-title="label"
              item-value="value"
              label="卡片色调"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
            />
          </div>

          <v-text-field
            v-model="editor.cookie"
            label="Cookie"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="vpp-field-block"
          />

          <v-textarea
            v-model="editor.note"
            label="功能描述"
            variant="outlined"
            rows="3"
            auto-grow
            hide-details="auto"
            class="vpp-field-block"
          />
        </div>

        <div class="vpp-dialog-actions">
          <v-btn variant="text" @click="dialog.config = false">取消</v-btn>
          <v-btn class="vpp-confirm-btn" variant="text" :loading="saving.config" @click="saveCardConfig">保存配置</v-btn>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.logs" max-width="960">
      <v-card class="vpp-dialog-card vpp-dialog-logs">
        <div class="vpp-dialog-head">
          <div>
            <div class="vpp-kicker">日志</div>
            <h3 class="vpp-dialog-title">{{ activeDashboardCard?.title || '实时日志' }}</h3>
          </div>
          <div class="vpp-log-state">
            <span class="vpp-live-dot" />
            <span>实时轮询中</span>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-log-toolbar">
            <span>{{ activeDashboardCard?.site_name || '--' }}</span>
            <span>{{ activeDashboardCard?.site_domain || activeDashboardCard?.site_url || '--' }}</span>
            <span>最近刷新 {{ lastLogRefresh || '刚刚' }}</span>
          </div>

          <div v-if="!selectedLogs.length" class="vpp-empty-state">
            当前卡片还没有执行日志，先执行一次或等待下次轮询。
          </div>

          <div v-else class="vpp-log-list mp-scroll">
            <article v-for="item in selectedLogs" :key="item.id || `${item.time}-${item.summary}`" class="vpp-log-item">
              <div class="vpp-log-head">
                <strong>{{ item.status_title || item.title || activeDashboardCard?.title }}</strong>
                <span>{{ item.time || '--' }}</span>
              </div>
              <p class="vpp-log-summary">{{ item.summary || '暂无详情' }}</p>
              <div v-if="item.lines?.length" class="vpp-log-lines">
                <span v-for="line in item.lines" :key="`${item.id}-${line}`" class="vpp-log-line">{{ line }}</span>
              </div>
            </article>
          </div>
        </div>

        <div class="vpp-dialog-actions">
          <v-btn variant="text" @click="dialog.logs = false">关闭</v-btn>
          <v-btn class="vpp-action-btn is-logs" variant="text" prepend-icon="mdi-refresh" :loading="loading.cardRefresh" @click="refreshFocusedCard">刷新状态</v-btn>
          <v-btn class="vpp-confirm-btn" variant="text" prepend-icon="mdi-play-circle-outline" :loading="loading.cardRun" @click="runFocusedCard">立即执行</v-btn>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.copy" max-width="680">
      <v-card class="vpp-dialog-card vpp-dialog-copy">
        <div class="vpp-dialog-head">
          <div>
            <div class="vpp-kicker">复制</div>
            <h3 class="vpp-dialog-title">{{ activeDashboardCard?.title || '复制功能卡片' }}</h3>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-dialog-banner">
            复制会生成一张全新的功能卡片，你可以再手动改网站地址、Cookie、UID 和描述。
          </div>

          <div class="vpp-copy-origin">
            <span>复制来源</span>
            <strong>{{ activeDashboardCard?.site_name || '--' }}</strong>
            <span>{{ activeDashboardCard?.module_summary || '--' }}</span>
          </div>

          <v-text-field
            v-model="copyForm.title"
            label="复制功能名称"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="vpp-field-block"
          />

          <v-textarea
            v-model="copyForm.note"
            label="功能描述"
            variant="outlined"
            rows="3"
            auto-grow
            hide-details="auto"
            class="vpp-field-block"
          />
        </div>

        <div class="vpp-dialog-actions">
          <v-btn variant="text" @click="dialog.copy = false">取消</v-btn>
          <v-btn class="vpp-confirm-btn" variant="text" :loading="saving.copy" @click="confirmCopyCard">确定复制</v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const DEFAULT_CRON = '5 8 * * *'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

const emit = defineEmits(['switch', 'close'])

const status = reactive({
  enabled: false,
  next_run_time: '',
  last_run: '',
  history: [],
  dashboard: {},
})

const panelConfig = ref(createEmptyConfig())
const message = reactive({ text: '', type: 'success' })
const dialog = reactive({ config: false, logs: false, copy: false })
const loading = reactive({ refreshAll: false, runAll: false, cardRefresh: false, cardRun: false })
const saving = reactive({ config: false, copy: false })
const failedLogos = reactive({})
const editor = reactive(createCardDraft())
const copyForm = reactive({ title: '', note: '' })
const selectedCardId = ref('')
const lastLogRefresh = ref('')

let logTimer = null

const dashboard = computed(() => status.dashboard || {})
const cards = computed(() => Array.isArray(dashboard.value.cards) ? dashboard.value.cards : [])
const enabledCount = computed(() => cards.value.filter((card) => card.enabled).length)
const summaryCards = computed(() => (dashboard.value.overview || []).slice(0, 6))
const toneSelectItems = computed(() =>
  (panelConfig.value.tone_options || []).map((item) => ({ label: item.label, value: item.key })),
)
const activeDashboardCard = computed(() => cards.value.find((item) => item.card_id === selectedCardId.value) || null)
const selectedLogs = computed(() => {
  const cardId = selectedCardId.value
  const fallbackLogs = activeDashboardCard.value?.log_items || []
  const merged = new Map()
  for (const item of [...fallbackLogs, ...(status.history || [])]) {
    if (!item || item.card_id !== cardId) continue
    const key = item.id || `${item.time || ''}-${item.summary || ''}`
    if (!merged.has(key)) merged.set(key, item)
  }
  return [...merged.values()].sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
})

function createEmptyConfig() {
  return {
    enabled: false,
    notify: true,
    onlyonce: false,
    use_proxy: false,
    force_ipv4: true,
    cron: DEFAULT_CRON,
    http_timeout: 15,
    http_retry_times: 3,
    random_delay_max_seconds: 5,
    cards: [],
    module_options: [],
    tone_options: [],
  }
}

function createCardDraft(source = {}) {
  return {
    id: String(source.id || source.card_id || ''),
    title: String(source.title || ''),
    module_key: String(source.module_key || 'siqi_sign'),
    site_name: String(source.site_name || ''),
    site_url: String(source.site_url || ''),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON),
    tone: String(source.tone || 'azure'),
    cookie: String(source.cookie || ''),
    uid: String(source.uid || ''),
    note: String(source.note || ''),
  }
}

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value ?? null))
}

function moduleMeta(moduleKey) {
  return (panelConfig.value.module_options || []).find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    description: '',
    summary: String(moduleKey || '').replaceAll('_', ' '),
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function normalizeCard(source = {}, options = {}) {
  const meta = moduleMeta(String(source.module_key || source.module || 'siqi_sign'))
  const toneValues = new Set((panelConfig.value.tone_options || []).map((item) => item.key))
  const tone = toneValues.has(source.tone) ? source.tone : (meta.tone || 'azure')
  return {
    id: String(options.newId ? nextCardId(meta.key) : (source.id || source.card_id || nextCardId(meta.key))),
    title: String(source.title || meta.label || '').trim() || meta.label,
    module_key: meta.key,
    site_name: String(source.site_name || meta.default_site_name || meta.label || '').trim() || meta.label,
    site_url: String(source.site_url || meta.default_site_url || '').trim(),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON).trim() || DEFAULT_CRON,
    tone,
    cookie: String(source.cookie || '').trim(),
    uid: meta.key === 'newapi_checkin' ? String(source.uid || '').trim() : '',
    note: String(source.note || '').trim(),
  }
}

function normalizeConfig(source = {}) {
  const next = createEmptyConfig()
  next.enabled = !!source.enabled
  next.notify = source.notify !== false
  next.onlyonce = !!source.onlyonce
  next.use_proxy = !!source.use_proxy
  next.force_ipv4 = source.force_ipv4 !== false
  next.cron = String(source.cron || DEFAULT_CRON)
  next.http_timeout = Number(source.http_timeout || 15)
  next.http_retry_times = Number(source.http_retry_times || 3)
  next.random_delay_max_seconds = Number(source.random_delay_max_seconds || 5)
  next.module_options = Array.isArray(source.module_options) ? deepClone(source.module_options) : []
  next.tone_options = Array.isArray(source.tone_options) ? deepClone(source.tone_options) : []
  next.cards = Array.isArray(source.cards) ? source.cards.map((item) => normalizeCard(item)) : []
  return next
}

function serializeConfig(cardsOverride = null) {
  const cards = Array.isArray(cardsOverride) ? cardsOverride : panelConfig.value.cards
  return {
    enabled: !!panelConfig.value.enabled,
    notify: !!panelConfig.value.notify,
    onlyonce: !!panelConfig.value.onlyonce,
    use_proxy: !!panelConfig.value.use_proxy,
    force_ipv4: panelConfig.value.force_ipv4 !== false,
    cron: String(panelConfig.value.cron || DEFAULT_CRON),
    http_timeout: Number(panelConfig.value.http_timeout || 15),
    http_retry_times: Number(panelConfig.value.http_retry_times || 3),
    random_delay_max_seconds: Number(panelConfig.value.random_delay_max_seconds || 5),
    cards: cards.map((item) => normalizeCard(item)),
  }
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpp-tone-rgb': '38, 183, 120' },
    azure: { '--vpp-tone-rgb': '67, 126, 255' },
    amber: { '--vpp-tone-rgb': '255, 171, 67' },
    rose: { '--vpp-tone-rgb': '231, 92, 128' },
    violet: { '--vpp-tone-rgb': '150, 117, 255' },
    slate: { '--vpp-tone-rgb': '128, 140, 158' },
  }
  return map[tone] || map.azure
}

function runtimeTone(level) {
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  return 'info'
}

function runtimeLabel(level) {
  return {
    success: '正常',
    warning: '待处理',
    error: '异常',
    info: '信息',
  }[level] || '信息'
}

function scheduleText(card) {
  if (!card?.enabled) return '已停用'
  if (!card?.auto_run) return '仅手动执行'
  return card?.next_run_time || card?.cron || '等待调度'
}

function previewTags(tags = []) {
  return Array.isArray(tags) ? tags.slice(0, 4) : []
}

function logoSrc(card) {
  return failedLogos[card.card_id] ? '' : (card.site_logo || '')
}

function markLogoFailed(cardId) {
  failedLogos[cardId] = true
}

function rawCardById(cardId) {
  return (panelConfig.value.cards || []).find((item) => item.id === cardId) || null
}

function openConfigDialog(card) {
  const source = rawCardById(card.card_id) || card
  Object.assign(editor, normalizeCard(source))
  selectedCardId.value = card.card_id
  dialog.config = true
}

function openLogsDialog(card) {
  selectedCardId.value = card.card_id
  dialog.logs = true
}

function openCopyDialog(card) {
  selectedCardId.value = card.card_id
  copyForm.title = `${card.title} 副本`
  copyForm.note = card.note || card.module_description || ''
  dialog.copy = true
}

async function loadStatus(showError = true) {
  try {
    const payload = await props.api.get('/plugin/VuePanel/status')
    status.enabled = !!payload.enabled
    status.next_run_time = payload.next_run_time || ''
    status.last_run = payload.last_run || ''
    status.history = Array.isArray(payload.history) ? payload.history : []
    status.dashboard = payload.dashboard || {}
    panelConfig.value = normalizeConfig(payload.config || {})
    lastLogRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  }
}

async function persistCards(nextCards, successText) {
  const payload = serializeConfig(nextCards)
  const response = await props.api.post('/plugin/VuePanel/config', payload)
  flash(response.message || successText || '配置已保存')
  await loadStatus(false)
  return response
}

async function refreshStatus() {
  loading.refreshAll = true
  try {
    const response = await props.api.post('/plugin/VuePanel/refresh', {})
    flash(response.message || '状态已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '刷新状态失败', 'error')
  } finally {
    loading.refreshAll = false
  }
}

async function runAll() {
  loading.runAll = true
  try {
    const response = await props.api.post('/plugin/VuePanel/run', {})
    flash(response.message || '已执行启用任务')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行任务失败', 'error')
  } finally {
    loading.runAll = false
  }
}

async function saveCardConfig() {
  saving.config = true
  try {
    const nextCards = (panelConfig.value.cards || []).map((item) =>
      item.id === editor.id ? normalizeCard(editor) : normalizeCard(item),
    )
    await persistCards(nextCards, '卡片配置已保存')
    dialog.config = false
  } catch (error) {
    flash(error?.message || '保存卡片配置失败', 'error')
  } finally {
    saving.config = false
  }
}

async function confirmCopyCard() {
  saving.copy = true
  try {
    const source = rawCardById(selectedCardId.value)
    if (!source) throw new Error('未找到复制来源')
    const copyCard = normalizeCard(
      {
        ...source,
        id: nextCardId(source.module_key),
        title: copyForm.title || `${source.title} 副本`,
        note: copyForm.note,
      },
      { newId: true },
    )
    const nextCards = [...(panelConfig.value.cards || []).map((item) => normalizeCard(item)), copyCard]
    await persistCards(nextCards, '卡片已复制')
    dialog.copy = false
  } catch (error) {
    flash(error?.message || '复制卡片失败', 'error')
  } finally {
    saving.copy = false
  }
}

async function runFocusedCard() {
  if (!selectedCardId.value) return
  loading.cardRun = true
  try {
    const response = await props.api.post('/plugin/VuePanel/card/run', { card_id: selectedCardId.value })
    flash(response.message || '卡片执行完成')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片执行失败', 'error')
  } finally {
    loading.cardRun = false
  }
}

async function refreshFocusedCard() {
  if (!selectedCardId.value) return
  loading.cardRefresh = true
  try {
    const response = await props.api.post('/plugin/VuePanel/card/refresh', { card_id: selectedCardId.value })
    flash(response.message || '卡片状态已刷新')
    await loadStatus(false)
  } catch (error) {
    flash(error?.message || '卡片刷新失败', 'error')
  } finally {
    loading.cardRefresh = false
  }
}

function stopLogPolling() {
  if (logTimer) {
    window.clearInterval(logTimer)
    logTimer = null
  }
}

function startLogPolling() {
  stopLogPolling()
  loadStatus(false)
  logTimer = window.setInterval(() => {
    loadStatus(false)
  }, 5000)
}

function closePlugin() {
  emit('close')
}

watch(
  () => dialog.logs,
  (opened) => {
    if (opened) startLogPolling()
    else stopLogPolling()
  },
)

onMounted(async () => {
  panelConfig.value = normalizeConfig(props.initialConfig || {})
  await loadStatus()
})

onBeforeUnmount(() => {
  stopLogPolling()
})
</script>

<style scoped>
.vuepanel-page {
  --vpp-surface: color-mix(in srgb, var(--mp-bg-card) 74%, #151923 26%);
  --vpp-surface-soft: color-mix(in srgb, var(--mp-bg-panel) 70%, #1b1f2b 30%);
  --vpp-surface-muted: rgba(255, 255, 255, 0.045);
  --vpp-line: rgba(255, 255, 255, 0.09);
  --vpp-line-strong: rgba(99, 188, 255, 0.38);
  --vpp-blue: #1ea0ff;
  --vpp-blue-soft: rgba(30, 160, 255, 0.14);
  --vpp-purple: #9b5cff;
  --vpp-purple-soft: rgba(155, 92, 255, 0.16);
  --vpp-green: #67df1b;
  --vpp-green-soft: rgba(103, 223, 27, 0.18);
  min-height: 100%;
  padding: 8px 0 20px;
  color: var(--mp-text-primary);
}

.vuepanel-page,
.vuepanel-page * {
  box-sizing: border-box;
}

.vpp-shell {
  display: grid;
  gap: 12px;
}

.vpp-hero,
.vpp-stat-card,
.vpp-card,
.vpp-dialog-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--vpp-line);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.015));
  backdrop-filter: blur(18px);
}

.vpp-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  background: var(--vpp-surface-soft);
}

.vpp-hero-copy,
.vpp-card-copy {
  min-width: 0;
}

.vpp-kicker {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--mp-text-secondary);
}

.vpp-title {
  margin: 8px 0 6px;
  font-size: clamp(24px, 3vw, 32px);
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.vpp-subtitle {
  max-width: 760px;
  margin: 0;
  color: var(--mp-text-secondary);
  font-size: 13px;
  line-height: 1.7;
}

.vpp-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.vpp-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid var(--vpp-line);
  background: rgba(255, 255, 255, 0.04);
  color: var(--mp-text-secondary);
  font-size: 11px;
  font-weight: 700;
}

.vpp-hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  min-width: 260px;
}

.vpp-hero-actions :deep(.v-btn) {
  min-height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid var(--vpp-line);
  background: rgba(255, 255, 255, 0.05);
  text-transform: none;
  letter-spacing: 0;
  font-weight: 700;
}

.vpp-alert {
  border: 1px solid var(--vpp-line);
}

.vpp-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.vpp-stat-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 74px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--vpp-surface-soft);
}

.vpp-stat-label {
  font-size: 12px;
  color: var(--mp-text-secondary);
}

.vpp-stat-value {
  font-size: 18px;
  font-weight: 800;
  color: #69c9ff;
}

.vpp-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 16px;
}

.vpp-card {
  --vpp-tone-rgb: 67, 126, 255;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 210px;
  padding: 18px;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03)),
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.02), transparent 55%);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.vpp-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(100, 200, 255, 0.4), transparent);
  transform: translateX(-100%);
  transition: transform 0.8s ease;
}

.vpp-card:hover::before {
  transform: translateX(100%);
}

.vpp-card:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: var(--vpp-line-strong);
  box-shadow: 0 12px 35px rgba(100, 200, 255, 0.14);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06)),
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.04), transparent 55%);
}

.vpp-card.is-enabled {
  border-left: 3px solid var(--vpp-blue);
  box-shadow: inset 3px 0 0 rgba(33, 150, 243, 0.18);
}

.vpp-card-glow {
  position: absolute;
  inset: auto -16px 18px auto;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #64c8ff;
  box-shadow: 0 0 12px rgba(100, 200, 255, 0.85);
  opacity: 0.9;
}

.vpp-card-head {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.vpp-logo-wrap {
  position: relative;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.vpp-logo-wrap::after {
  content: '';
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.9);
  background: #7a7a7a;
  box-shadow: 0 0 5px rgba(122, 122, 122, 0.4);
}

.vpp-card.is-enabled .vpp-logo-wrap::after {
  background: #75dc6f;
  box-shadow: 0 0 10px rgba(117, 220, 111, 0.7);
}

.vpp-logo {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  object-fit: cover;
}

.vpp-logo-fallback {
  font-size: 18px;
  line-height: 1;
}

.vpp-card-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.vpp-card-title {
  margin: 0;
  font-size: 15px;
  line-height: 1.25;
  font-weight: 700;
}

.vpp-status-pill,
.vpp-runtime-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
}

.vpp-status-pill.is-enabled {
  color: #ffffff;
  background: var(--vpp-green);
}

.vpp-status-pill.is-disabled {
  color: #ffffff;
  background: rgba(136, 136, 148, 0.88);
}

.vpp-card-desc {
  margin: 4px 0 0;
  color: rgba(219, 227, 236, 0.7);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: lowercase;
}

.vpp-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
  color: rgba(219, 227, 236, 0.62);
  font-size: 12px;
}

.vpp-runtime-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.vpp-runtime-pill {
  border: 1px solid rgba(30, 160, 255, 0.9);
  background: rgba(30, 160, 255, 0.08);
  color: #39b0ff;
}

.vpp-runtime-pill.is-success {
  color: #39b0ff;
}

.vpp-runtime-pill.is-warning {
  border-color: rgba(255, 190, 70, 0.7);
  color: #ffbf4b;
  background: rgba(255, 190, 70, 0.08);
}

.vpp-runtime-pill.is-danger {
  border-color: rgba(255, 91, 91, 0.7);
  color: #ff6969;
  background: rgba(255, 91, 91, 0.08);
}

.vpp-runtime-title {
  color: var(--mp-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.vpp-runtime-text {
  min-height: 40px;
  margin: 0;
  color: rgba(219, 227, 236, 0.7);
  font-size: 12px;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.vpp-metric-grid,
.vpp-note-box {
  display: none;
}

.vpp-detail-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
}

.vpp-detail-item {
  padding: 0;
  border: 0;
  background: transparent;
}

.vpp-detail-label,
.vpp-detail-item strong {
  display: inline;
  font-size: 11px;
}

.vpp-detail-label {
  color: rgba(219, 227, 236, 0.52);
}

.vpp-detail-item strong {
  margin-left: 4px;
  color: rgba(219, 227, 236, 0.82);
  font-weight: 600;
}

.vpp-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: -2px;
}

.vpp-tag {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(30, 160, 255, 0.75);
  background: rgba(30, 160, 255, 0.08);
  color: #39b0ff;
  font-size: 10px;
  font-weight: 700;
}

.vpp-action-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: auto;
}

.vpp-action-btn,
.vpp-confirm-btn {
  min-height: 32px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.11) !important;
  background: rgba(255, 255, 255, 0.05) !important;
  text-transform: none;
  font-weight: 700;
  letter-spacing: 0;
}

.vpp-action-btn {
  color: #8d7cff;
}

.vpp-action-btn.is-copy {
  color: #9d7cff;
}

.vpp-action-btn.is-logs:hover {
  border-color: rgba(33, 150, 243, 0.5);
  box-shadow: 0 0 12px rgba(33, 150, 243, 0.22);
  background: rgba(33, 150, 243, 0.06);
}

.vpp-action-btn.is-config:hover,
.vpp-action-btn.is-copy:hover {
  border-color: rgba(156, 39, 176, 0.5);
  box-shadow: 0 0 12px rgba(156, 39, 176, 0.22);
  background: rgba(156, 39, 176, 0.06);
}

.vpp-action-btn :deep(.v-btn__content),
.vpp-confirm-btn :deep(.v-btn__content) {
  gap: 6px;
}

.vpp-confirm-btn {
  flex: 0 0 auto;
  color: #d08cff;
  border-color: rgba(181, 89, 255, 0.72);
  background: rgba(155, 92, 255, 0.06);
}

.vpp-confirm-btn:hover {
  box-shadow: 0 0 14px rgba(155, 92, 255, 0.24);
  background: rgba(155, 92, 255, 0.1);
}

.vpp-dialog-card {
  border-radius: 18px !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(20, 23, 33, 0.96) !important;
  color: var(--mp-text-primary);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.45);
}

.vpp-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px 10px;
}

.vpp-dialog-title {
  margin: 8px 0 0;
  font-size: 20px;
  line-height: 1.15;
}

.vpp-dialog-body {
  padding: 8px 24px 0;
}

.vpp-dialog-banner {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid rgba(34, 170, 255, 0.12);
  background: rgba(20, 105, 171, 0.2);
  color: #7bd0ff;
  font-size: 13px;
  line-height: 1.7;
}

.vpp-dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 18px 24px 24px;
}

.vpp-switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.vpp-switch-card,
.vpp-copy-origin,
.vpp-log-toolbar,
.vpp-log-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.vpp-switch-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
}

.vpp-switch-label {
  font-size: 13px;
  font-weight: 700;
}

.vpp-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.vpp-field-block {
  margin-top: 12px;
}

.vpp-dialog-card :deep(.v-field) {
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}

.vpp-dialog-card :deep(.v-field__overlay) {
  background: transparent;
}

.vpp-dialog-card :deep(.v-field__outline) {
  --v-field-border-opacity: 0.14;
}

.vpp-dialog-card :deep(.v-label),
.vpp-dialog-card :deep(.v-field__input),
.vpp-dialog-card :deep(textarea) {
  color: rgba(235, 240, 247, 0.92);
}

.vpp-log-state,
.vpp-copy-origin,
.vpp-log-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  color: rgba(219, 227, 236, 0.7);
  font-size: 12px;
  font-weight: 700;
}

.vpp-copy-origin,
.vpp-log-toolbar {
  padding: 12px 14px;
}

.vpp-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #75dc6f;
  box-shadow: 0 0 0 6px rgba(117, 220, 111, 0.18);
  animation: pulse 1.8s ease infinite;
}

.vpp-log-list {
  display: grid;
  gap: 10px;
  max-height: 52vh;
  padding-right: 4px;
}

.vpp-log-item {
  padding: 14px;
}

.vpp-log-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
}

.vpp-log-summary {
  margin: 10px 0 0;
  color: rgba(219, 227, 236, 0.74);
  font-size: 12px;
  line-height: 1.7;
}

.vpp-log-lines {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.vpp-log-line {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(219, 227, 236, 0.72);
  font-size: 11px;
}

.vpp-empty-state {
  padding: 22px 18px;
  border-radius: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.12);
  color: rgba(219, 227, 236, 0.66);
  text-align: center;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.8;
    transform: scale(0.96);
  }
  50% {
    opacity: 1;
    transform: scale(1.08);
  }
}

@media (max-width: 980px) {
  .vpp-hero {
    flex-direction: column;
  }

  .vpp-hero-actions {
    justify-content: flex-start;
    min-width: 0;
  }

  .vpp-switch-grid,
  .vpp-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .vpp-hero,
  .vpp-dialog-head,
  .vpp-dialog-body,
  .vpp-dialog-actions {
    padding-left: 16px;
    padding-right: 16px;
  }

  .vpp-card {
    min-height: auto;
  }

  .vpp-card-title-row,
  .vpp-log-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpp-switch-grid,
  .vpp-form-grid,
  .vpp-action-row {
    grid-template-columns: 1fr;
  }
}
</style>
