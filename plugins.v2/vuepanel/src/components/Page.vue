<template>
  <div class="vuepanel-page">
    <div class="vpp-shell">
      <header class="vpp-control-panel">
        <div class="vpp-panel-left">
          <v-text-field
            v-model="searchQuery"
            class="vpp-search-field"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
            placeholder="搜索功能模块..."
            prepend-inner-icon="mdi-magnify"
          />
        </div>

        <div class="vpp-panel-right">
          <v-btn class="vpp-toolbar-btn" variant="text" prepend-icon="mdi-flash" :loading="loading.runAll" @click="runAll">
            执行启用
            <span class="vpp-toolbar-badge">{{ enabledCount }}</span>
          </v-btn>
          <v-btn class="vpp-toolbar-btn" variant="text" prepend-icon="mdi-refresh" :loading="loading.refreshAll" @click="refreshStatus">刷新</v-btn>
          <v-btn class="vpp-toolbar-btn is-icon" icon="mdi-close" variant="text" @click="closePlugin" />
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
        <article v-for="item in controlStats" :key="item.label" class="vpp-stat-card">
          <div class="vpp-stat-icon-wrap">
            <v-icon :icon="item.icon" size="18" />
          </div>
          <div class="vpp-stat-copy">
            <strong class="vpp-stat-value">{{ item.value }}</strong>
            <span class="vpp-stat-label">{{ item.label }}</span>
          </div>
          <span class="vpp-stat-glow" />
        </article>
      </section>

      <section class="vpp-card-grid">
        <article
          v-for="card in displayCards"
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
                <div class="vpp-card-title-group">
                  <h2 class="vpp-card-title">{{ card.title }}</h2>
                  <p class="vpp-card-desc">{{ card.module_summary || 'plugin card' }}</p>
                </div>
                <span class="vpp-status-pill" :class="`is-${card.status_key}`">{{ card.status_label }}</span>
              </div>

              <div class="vpp-card-meta">
                <span class="vpp-card-meta-item">{{ card.site_name || card.module_name }}</span>
                <span class="vpp-card-meta-item">{{ card.site_domain || card.site_url || '--' }}</span>
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

          <div class="vpp-card-info-stack">
            <div class="vpp-info-section">
              <div class="vpp-info-label">计划</div>
              <div class="vpp-info-value">{{ scheduleText(card) }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">上次执行</div>
              <div class="vpp-info-value">{{ card.last_run || '暂无' }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">日志</div>
              <div class="vpp-info-value">{{ card.log_count || 0 }} 条</div>
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

        <div v-if="!displayCards.length" class="vpp-empty-state vpp-grid-empty">
          {{ searchQuery ? '没有找到匹配的功能模块。' : '当前还没有可展示的功能卡片。' }}
        </div>
      </section>
    </div>

    <v-dialog v-model="dialog.config" max-width="860">
      <v-card class="vpp-dialog-card vpp-dialog-config">
        <div class="vpp-dialog-head">
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-cog-outline" size="24" class="vpp-dialog-icon is-config" />
            <div>
              <div class="vpp-kicker">配置</div>
              <h3 class="vpp-dialog-title">{{ editor.title || activeDashboardCard?.title || '功能配置' }}</h3>
            </div>
          </div>
          <span class="vpp-status-pill" :class="`is-${editor.enabled ? 'enabled' : 'disabled'}`">
            {{ editor.enabled ? '启用' : '停用' }}
          </span>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-target-info">
            <div class="vpp-target-name">{{ editor.title || activeDashboardCard?.title || '功能配置' }}</div>
            <div class="vpp-target-meta">
              {{ editor.site_name || activeDashboardCard?.site_name || '--' }}
              ·
              {{ editor.site_url || activeDashboardCard?.site_domain || activeDashboardCard?.site_url || '--' }}
            </div>
          </div>

          <div class="vpp-dialog-banner">
            当前设置会直接写入这张功能卡片，后续多站点需求请通过复制卡片来扩展。
          </div>

          <div class="vpp-info-stack">
            <div class="vpp-info-section">
              <div class="vpp-info-label">功能模块</div>
              <div class="vpp-info-value">{{ activeDashboardCard?.module_name || editor.module_key }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">站点地址</div>
              <div class="vpp-info-value">{{ editor.site_url || activeDashboardCard?.site_url || '--' }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">调度状态</div>
              <div class="vpp-info-value">{{ scheduleText(editor) }}</div>
            </div>
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">功能开关</div>
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
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">基础设置</div>
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
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-text-box-outline" size="24" class="vpp-dialog-icon is-logs" />
            <div>
              <div class="vpp-kicker">日志</div>
              <h3 class="vpp-dialog-title">{{ activeDashboardCard?.title || '实时日志' }}</h3>
            </div>
          </div>
          <div class="vpp-log-state">
            <span class="vpp-live-dot" />
            <span>实时轮询中</span>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-target-info">
            <div class="vpp-target-name">{{ activeDashboardCard?.title || '实时日志' }}</div>
            <div class="vpp-target-meta">
              {{ activeDashboardCard?.site_name || '--' }}
              ·
              {{ activeDashboardCard?.site_domain || activeDashboardCard?.site_url || '--' }}
            </div>
          </div>

          <div class="vpp-info-stack">
            <div class="vpp-info-section">
              <div class="vpp-info-label">站点</div>
              <div class="vpp-info-value">{{ activeDashboardCard?.site_name || '--' }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">地址</div>
              <div class="vpp-info-value">{{ activeDashboardCard?.site_domain || activeDashboardCard?.site_url || '--' }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">最近刷新</div>
              <div class="vpp-info-value">{{ lastLogRefresh || '刚刚' }}</div>
            </div>
          </div>

          <div class="vpp-dialog-panel vpp-log-panel">
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
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-content-copy" size="24" class="vpp-dialog-icon is-copy" />
            <div>
              <div class="vpp-kicker">复制</div>
              <h3 class="vpp-dialog-title">{{ activeDashboardCard?.title || '复制功能卡片' }}</h3>
            </div>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-target-info">
            <div class="vpp-target-name">{{ activeDashboardCard?.title || '复制功能卡片' }}</div>
            <div class="vpp-target-meta">
              {{ activeDashboardCard?.site_name || '--' }}
              ·
              {{ activeDashboardCard?.site_domain || activeDashboardCard?.site_url || '--' }}
            </div>
          </div>

          <div class="vpp-dialog-banner">
            复制会生成一张全新的功能卡片，你可以再手动改网站地址、Cookie、UID 和描述。
          </div>

          <div class="vpp-info-stack">
            <div class="vpp-info-section">
              <div class="vpp-info-label">复制来源</div>
              <div class="vpp-info-value">{{ activeDashboardCard?.site_name || '--' }}</div>
            </div>
            <div class="vpp-info-section">
              <div class="vpp-info-label">功能说明</div>
              <div class="vpp-info-value">{{ activeDashboardCard?.module_summary || '--' }}</div>
            </div>
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">复制设置</div>
            <v-text-field
              v-model="copyForm.title"
              label="复制功能名称"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
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

const emit = defineEmits(['close'])

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
const searchQuery = ref('')

let logTimer = null

const dashboard = computed(() => status.dashboard || {})
const dashboardCards = computed(() => Array.isArray(dashboard.value.cards) ? dashboard.value.cards : [])
const cards = computed(() => (dashboardCards.value.length ? dashboardCards.value : buildFallbackCards()))
const enabledCount = computed(() => cards.value.filter((card) => card.enabled).length)
const successCount = computed(() => cards.value.filter((card) => card.level === 'success').length)
const errorCount = computed(() => cards.value.filter((card) => card.level === 'error').length)
const displayCards = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()
  if (!keyword) return cards.value
  return cards.value.filter((card) =>
    [
      card.title,
      card.site_name,
      card.site_domain,
      card.site_url,
      card.module_name,
      card.module_summary,
      card.status_text,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(keyword)),
  )
})
const controlStats = computed(() => [
  { label: '总数', value: String(cards.value.length), icon: 'mdi-view-grid-outline' },
  { label: '已启', value: String(enabledCount.value), icon: 'mdi-check-decagram-outline' },
  { label: '正常', value: String(successCount.value), icon: 'mdi-play-circle-outline' },
  { label: '日志', value: String(status.history.length), icon: 'mdi-file-document-outline' },
  { label: '异常', value: String(errorCount.value), icon: 'mdi-alert-circle-outline' },
])
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

function siteDomain(siteUrl) {
  try {
    return new URL(siteUrl).host || ''
  } catch {
    return String(siteUrl || '').replace(/^https?:\/\//i, '').split('/')[0] || ''
  }
}

function siteLogo(siteUrl) {
  try {
    const parsed = new URL(siteUrl)
    if (!parsed.protocol || !parsed.host) return ''
    return `${parsed.protocol}//${parsed.host}/favicon.ico`
  } catch {
    return ''
  }
}

function fallbackStatus(card, meta) {
  if (!card.enabled) {
    return {
      level: 'info',
      status_title: '已停用',
      status_text: '当前功能卡片已停用，启用后即可手动执行或参与定时调度。',
    }
  }
  if (!card.cookie) {
    return {
      level: 'warning',
      status_title: '待配置 Cookie',
      status_text: '请先在配置弹窗中填写 Cookie，保存后再刷新或执行。',
    }
  }
  if (meta.key === 'newapi_checkin' && !card.uid) {
    return {
      level: 'warning',
      status_title: '待配置 UID',
      status_text: 'New API 签到卡片还需要填写 UID 才能正常执行。',
    }
  }
  if (!card.auto_run) {
    return {
      level: 'info',
      status_title: '仅手动执行',
      status_text: '当前已启用，但只会在你手动点击执行时运行。',
    }
  }
  return {
    level: 'info',
    status_title: '等待刷新',
    status_text: '卡片配置已经加载，可以点击刷新或执行启用查看实时状态。',
  }
}

function fallbackTags(card) {
  const tags = []
  tags.push(card.enabled ? '启用' : '停用')
  tags.push(card.auto_run ? '自动执行' : '手动执行')
  if (card.cookie) tags.push('Cookie 已配置')
  if (card.uid) tags.push(`UID ${card.uid}`)
  return tags
}

function buildFallbackCards() {
  return (panelConfig.value.cards || []).map((source) => {
    const card = normalizeCard(source)
    const meta = moduleMeta(card.module_key)
    const logItems = (status.history || [])
      .filter((item) => item?.card_id === card.id)
      .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
      .slice(0, 12)
    const fallback = fallbackStatus(card, meta)

    return {
      ...card,
      card_id: card.id,
      site_domain: siteDomain(card.site_url),
      site_logo: siteLogo(card.site_url),
      module_name: meta.label,
      module_icon: meta.icon || '•',
      module_summary: String(meta.summary || meta.key || '').toLowerCase(),
      module_description: String(meta.description || ''),
      status_label: card.enabled ? '启用' : '停用',
      status_key: card.enabled ? 'enabled' : 'disabled',
      next_run_time: '',
      last_run: logItems[0]?.time || '',
      log_items: logItems,
      log_count: logItems.length,
      cookie_configured: !!card.cookie,
      copy_title: card.title,
      copy_description: card.note || String(meta.description || ''),
      tags: fallbackTags(card),
      metrics: [],
      detail_lines: [],
      ...fallback,
    }
  })
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
  --vpp-surface: color-mix(in srgb, var(--mp-bg-card) 76%, #141a25 24%);
  --vpp-surface-soft: color-mix(in srgb, var(--mp-bg-panel) 74%, #181e2a 26%);
  --vpp-surface-muted: rgba(255, 255, 255, 0.05);
  --vpp-line: rgba(255, 255, 255, 0.09);
  --vpp-line-strong: rgba(99, 188, 255, 0.34);
  --vpp-blue: #1ea0ff;
  --vpp-blue-soft: rgba(30, 160, 255, 0.14);
  --vpp-purple: #9b5cff;
  --vpp-purple-soft: rgba(155, 92, 255, 0.16);
  --vpp-green: #67df1b;
  --vpp-green-soft: rgba(103, 223, 27, 0.18);
  --vpp-text-soft: rgba(219, 227, 236, 0.72);
  --vpp-text-faint: rgba(219, 227, 236, 0.56);
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
  gap: 16px;
  max-width: 1400px;
  margin: 0 auto;
}

.vpp-control-panel,
.vpp-stat-card,
.vpp-card,
.vpp-dialog-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--vpp-line);
  backdrop-filter: blur(18px);
}

.vpp-control-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
}

.vpp-control-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(100, 200, 255, 0.3), transparent);
  animation: vpp-scan 3s infinite;
}

.vpp-panel-left {
  flex: 1;
  min-width: 0;
  max-width: 400px;
}

.vpp-search-field :deep(.v-field) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

.vpp-search-field :deep(.v-field__outline) {
  --v-field-border-opacity: 0.1;
}

.vpp-search-field :deep(.v-field__input),
.vpp-search-field :deep(.v-label),
.vpp-search-field :deep(.v-icon) {
  color: rgba(235, 240, 247, 0.8);
}

.vpp-panel-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vpp-toolbar-btn {
  min-height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  border: 1px solid var(--vpp-line) !important;
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(10px);
  color: #8d7cff;
  text-transform: none;
  letter-spacing: 0;
  font-weight: 700;
  transition: all 0.3s ease;
}

.vpp-toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(100, 200, 255, 0.3) !important;
  box-shadow: 0 0 15px rgba(100, 200, 255, 0.2);
}

.vpp-toolbar-btn.is-icon {
  min-width: 36px;
  padding: 0;
}

.vpp-toolbar-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  margin-left: 2px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ffb400;
  color: #ffffff;
  font-size: 10px;
  font-weight: 800;
}

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

.vpp-alert {
  border: 1px solid var(--vpp-line);
}

.vpp-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.vpp-stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
}

.vpp-stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(100, 200, 255, 0.3);
  box-shadow: 0 6px 20px rgba(100, 200, 255, 0.1);
}

.vpp-stat-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #7ed3ff;
  position: relative;
}

.vpp-stat-icon-wrap::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 9px;
  background: linear-gradient(45deg, transparent, rgba(100, 200, 255, 0.2), transparent);
  z-index: -1;
  animation: vpp-rotate 4s linear infinite;
}

.vpp-stat-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.vpp-stat-value {
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(45deg, #64c8ff, #4080ff);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.vpp-stat-label {
  font-size: 0.7rem;
  color: var(--vpp-text-faint);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.vpp-stat-glow {
  position: absolute;
  top: 50%;
  right: 16px;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #64c8ff;
  box-shadow: 0 0 12px #64c8ff;
  transform: translateY(-50%);
  animation: vpp-pulse-status 2s infinite;
}

.vpp-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.vpp-card {
  --vpp-tone-rgb: 67, 126, 255;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 268px;
  padding: 18px;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03)),
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.03), transparent 62%);
  border-color: rgba(255, 255, 255, 0.15);
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
  border-color: rgba(100, 200, 255, 0.4);
  box-shadow: 0 12px 35px rgba(100, 200, 255, 0.15);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06)),
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.06), transparent 62%);
}

.vpp-card.is-enabled {
  border-left: 3px solid #4caf50;
  box-shadow: inset 3px 0 0 rgba(76, 175, 80, 0.2);
  background:
    linear-gradient(135deg, rgba(76, 175, 80, 0.05), rgba(255, 255, 255, 0.03)),
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.03), transparent 62%);
}

.vpp-card-glow {
  position: absolute;
  top: 24px;
  right: 18px;
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
  margin-bottom: 2px;
}

.vpp-logo-wrap {
  position: relative;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.vpp-card:hover .vpp-logo-wrap {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(100, 200, 255, 0.2);
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
  animation: vpp-pulse-dot 2s infinite;
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

.vpp-card-title-group {
  min-width: 0;
}

.vpp-card-title {
  margin: 0;
  font-size: 1rem;
  line-height: 1.2;
  font-weight: 600;
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
  color: var(--vpp-text-soft);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: lowercase;
}

.vpp-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.vpp-card-meta-item {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
  color: var(--vpp-text-soft);
  font-size: 11px;
  line-height: 1;
}

.vpp-runtime-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: -2px;
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
  min-height: 38px;
  margin: 0;
  color: var(--vpp-text-soft);
  font-size: 12px;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.vpp-metric-grid {
  display: none;
}

.vpp-card-info-stack {
  display: grid;
  gap: 8px;
}

.vpp-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: -4px;
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
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.vpp-action-btn,
.vpp-confirm-btn {
  min-height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.11) !important;
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(10px);
  text-transform: none;
  font-weight: 700;
  letter-spacing: 0;
  transition: all 0.3s ease;
}

.vpp-action-btn {
  flex: 1;
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
  font-size: 12px;
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
  background: color-mix(in srgb, var(--mp-bg-card) 84%, #10141d 16%) !important;
  color: var(--mp-text-primary);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.45);
}

.vpp-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px 8px;
}

.vpp-dialog-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.vpp-dialog-icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.06);
}

.vpp-dialog-icon.is-config {
  color: #d08cff;
}

.vpp-dialog-icon.is-logs {
  color: #64c8ff;
}

.vpp-dialog-icon.is-copy {
  color: #b98cff;
}

.vpp-dialog-title {
  margin: 8px 0 0;
  font-size: 20px;
  line-height: 1.15;
}

.vpp-dialog-body {
  display: grid;
  gap: 16px;
  padding: 8px 24px 0;
}

.vpp-target-info {
  margin-bottom: -2px;
}

.vpp-target-name {
  font-size: 1.08rem;
  font-weight: 600;
}

.vpp-target-meta {
  margin-top: 4px;
  color: var(--vpp-text-faint);
  font-size: 0.88rem;
}

.vpp-dialog-banner {
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

.vpp-info-stack {
  display: grid;
  gap: 10px;
}

.vpp-info-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
}

.vpp-info-label {
  color: var(--vpp-text-faint);
  font-size: 0.86rem;
  font-weight: 600;
}

.vpp-info-value {
  color: var(--mp-text-primary);
  font-size: 0.86rem;
  font-weight: 700;
  text-align: right;
  word-break: break-word;
}

.vpp-card-info-stack .vpp-info-section {
  padding: 10px 12px;
}

.vpp-card-info-stack .vpp-info-label,
.vpp-card-info-stack .vpp-info-value {
  font-size: 12px;
}

.vpp-note-box {
  display: block;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--vpp-text-soft);
  font-size: 12px;
  line-height: 1.7;
}

.vpp-dialog-panel {
  display: grid;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
}

.vpp-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--mp-text-primary);
}

.vpp-switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
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

.vpp-dialog-card :deep(.v-btn__overlay) {
  background: transparent;
}

.vpp-log-state {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--vpp-text-soft);
  font-size: 12px;
  font-weight: 700;
}

.vpp-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #75dc6f;
  box-shadow: 0 0 0 6px rgba(117, 220, 111, 0.18);
  animation: pulse 1.8s ease infinite;
}

.vpp-log-panel {
  padding: 14px;
}

.vpp-log-list {
  display: grid;
  gap: 10px;
  max-height: 50vh;
  padding-right: 4px;
}

.vpp-log-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 14px;
  transition: all 0.2s ease;
}

.vpp-log-item:hover {
  border-color: rgba(100, 200, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
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
  background: rgba(255, 255, 255, 0.02);
}

.vpp-grid-empty {
  grid-column: 1 / -1;
}

@keyframes vpp-scan {
  0%,
  100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
}

@keyframes vpp-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes vpp-pulse-status {
  0%,
  100% {
    opacity: 0.3;
    transform: translateY(-50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateY(-50%) scale(1.2);
  }
}

@keyframes vpp-pulse-dot {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 12px rgba(76, 175, 80, 0.8);
  }
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
  .vpp-control-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .vpp-panel-right {
    flex-wrap: wrap;
  }

  .vpp-switch-grid,
  .vpp-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .vpp-control-panel,
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
  .vpp-log-head,
  .vpp-info-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpp-action-row {
    flex-direction: column;
  }

  .vpp-switch-grid,
  .vpp-form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .vpp-stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .vpp-panel-right {
    justify-content: center;
  }
}
</style>
