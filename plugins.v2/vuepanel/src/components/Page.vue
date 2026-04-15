<template>
  <div ref="rootEl" class="vuepanel-page" :class="themeClass">
    <div class="vpp-shell">
      <header class="vpp-control-panel">
        <div class="vpp-panel-left">
          <v-text-field
            v-model="searchQuery"
            class="vpp-search-field"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            placeholder="搜索功能模块..."
            prepend-inner-icon="mdi-magnify"
            @click:clear="clearSearch"
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
        </article>
      </section>

      <section class="vpp-card-grid">
        <article
          v-for="card in displayCards"
          :key="card.card_id"
          class="vpp-card"
          :class="[{ 'is-enabled': card.enabled, 'is-disabled': !card.enabled }, `level-${runtimeTone(card.level)}`]"
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
                  <p class="vpp-card-desc">{{ cardSubtitle(card) }}</p>
                </div>
                <span class="vpp-status-pill" :class="`is-${card.status_key}`">{{ card.status_label }}</span>
              </div>

              <div class="vpp-card-meta">
                <span class="vpp-card-meta-item">{{ card.site_name || card.module_name }}</span>
                <span class="vpp-card-meta-item">{{ card.site_domain || card.site_url || '--' }}</span>
              </div>
            </div>
          </div>

          <div v-if="cardStatusSummary(card)" class="vpp-card-body">
            <p class="vpp-card-note">{{ cardStatusSummary(card) }}</p>
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

    <v-dialog v-model="dialog.config" max-width="760">
      <v-card class="vpp-dialog-card is-config" :class="themeClass">
        <div class="vpp-dialog-head">
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-cog-outline" size="22" class="vpp-dialog-icon is-config" />
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
          <div class="vpp-dialog-meta">
            <span class="vpp-meta-chip">{{ editor.site_name || '--' }}</span>
            <span class="vpp-meta-chip">{{ editor.cron || DEFAULT_CRON }}</span>
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">开关</div>
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
              <label class="vpp-switch-card is-emphasis">
                <span class="vpp-switch-label">立即运行一次</span>
                <v-switch v-model="editor.run_once" hide-details color="primary" density="compact" />
              </label>
            </div>
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">基础设置</div>
            <div class="vpp-form-grid">
              <v-text-field v-model="editor.title" label="功能名称" variant="outlined" density="compact" hide-details="auto" />
              <v-text-field v-model="editor.site_name" label="网站名称" variant="outlined" density="compact" hide-details="auto" />
              <v-text-field
                v-model="editor.site_url"
                label="网站地址"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
              <BaseCronField
                v-model="editor.cron"
                label="Cron"
                class="vpp-cron-field"
              />
              <v-text-field
                v-if="editor.module_key === 'newapi_checkin'"
                v-model="editor.uid"
                label="UID"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
              <template v-if="editor.module_key === 'siqi_dineout'">
                <v-text-field
                  v-model="editor.breakfast_target"
                  label="早餐用户名"
                  placeholder="例如：xiaosa"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                />
                <v-text-field
                  v-model="editor.lunch_target"
                  label="中餐用户名"
                  placeholder="例如：shigandang"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                />
                <v-text-field
                  v-model="editor.dinner_target"
                  label="晚餐用户名"
                  placeholder="例如：yulliam"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                />
              </template>
              <v-text-field
                v-model="editor.cookie"
                label="Cookie"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="vpp-field-span-2"
              />
              <v-textarea
                v-model="editor.note"
                label="功能描述"
                variant="outlined"
                rows="2"
                auto-grow
                density="compact"
                hide-details="auto"
                class="vpp-field-span-2"
              />
            </div>
          </div>
        </div>

        <div class="vpp-dialog-actions">
          <div class="vpp-dialog-actions-left">
            <v-btn
              class="vpp-action-btn is-delete"
              :class="{ 'is-disabled-control': !canDeleteCard(activeDashboardCard || editor) }"
              variant="text"
              prepend-icon="mdi-delete-outline"
              :disabled="!canDeleteCard(activeDashboardCard || editor)"
              :loading="saving.delete && deletingCardId === editor.id"
              @click="deleteCurrentCard"
            >
              删除卡片
            </v-btn>
          </div>
          <div class="vpp-dialog-actions-right">
            <v-btn variant="text" @click="dialog.config = false">取消</v-btn>
            <v-btn class="vpp-confirm-btn" variant="text" :loading="saving.config" @click="saveCardConfig">保存配置</v-btn>
          </div>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.logs" max-width="900">
      <v-card class="vpp-dialog-card is-logs" :class="themeClass">
        <div class="vpp-dialog-head">
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-text-box-outline" size="22" class="vpp-dialog-icon is-logs" />
            <div>
              <div class="vpp-kicker">日志</div>
              <h3 class="vpp-dialog-title">{{ currentLogCard?.title || '实时日志' }}</h3>
            </div>
          </div>
          <div class="vpp-log-state">
            <span class="vpp-live-dot" />
            <span>实时轮询中</span>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-dialog-meta">
            <span class="vpp-meta-chip">{{ currentLogCard?.site_name || '--' }}</span>
            <span class="vpp-meta-chip">{{ currentLogCard?.site_domain || currentLogCard?.site_url || '--' }}</span>
            <span class="vpp-meta-chip">最近刷新 {{ lastLogRefresh || '--' }}</span>
          </div>

          <div class="vpp-dialog-panel vpp-log-panel">
            <div class="vpp-section-title">日志列表</div>
            <div v-if="!selectedLogs.length" class="vpp-empty-state">
              当前卡片还没有执行日志，先执行一次或等待下次轮询。
            </div>

            <div v-else class="vpp-log-table">
              <div class="vpp-log-table-head">
                <span>时间</span>
                <span>状态</span>
                <span>详情</span>
              </div>

              <div class="vpp-log-table-body mp-scroll">
                <article v-for="item in selectedLogs" :key="item.id || `${item.time}-${item.summary}`" class="vpp-log-row">
                  <div class="vpp-log-time">{{ item.time || '--' }}</div>
                  <div class="vpp-log-status">
                    <span class="vpp-runtime-pill" :class="`is-${logTone(item)}`">{{ logStatusLabel(item) }}</span>
                  </div>
                  <div class="vpp-log-detail">
                    <div class="vpp-log-summary">{{ logDetail(item) }}</div>
                    <div v-if="item.lines?.length" class="vpp-log-lines">
                      <span v-for="line in item.lines" :key="`${item.id}-${line}`" class="vpp-log-line">{{ line }}</span>
                    </div>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>

        <div class="vpp-dialog-actions">
          <div class="vpp-dialog-actions-left" />
          <div class="vpp-dialog-actions-right">
            <v-btn variant="text" @click="dialog.logs = false">关闭</v-btn>
            <v-btn class="vpp-action-btn is-logs" variant="text" prepend-icon="mdi-refresh" :loading="loading.cardRefresh" @click="refreshFocusedCard">刷新状态</v-btn>
            <v-btn class="vpp-confirm-btn" variant="text" prepend-icon="mdi-play-circle-outline" :loading="loading.cardRun" @click="runFocusedCard">立即执行</v-btn>
          </div>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog.copy" max-width="560">
      <v-card class="vpp-dialog-card is-copy" :class="themeClass">
        <div class="vpp-dialog-head">
          <div class="vpp-dialog-title-wrap">
            <v-icon icon="mdi-content-copy" size="22" class="vpp-dialog-icon is-copy" />
            <div>
              <div class="vpp-kicker">复制</div>
              <h3 class="vpp-dialog-title">{{ activeDashboardCard?.title || '复制功能卡片' }}</h3>
            </div>
          </div>
        </div>

        <div class="vpp-dialog-body">
          <div class="vpp-dialog-meta">
            <span class="vpp-meta-chip">{{ activeDashboardCard?.site_name || '--' }}</span>
          </div>

          <div class="vpp-dialog-hint">
            复制会生成一张全新的功能卡片，你可以再手动改网站地址、Cookie、UID 和描述。
          </div>

          <div class="vpp-dialog-panel">
            <div class="vpp-section-title">复制设置</div>
            <div class="vpp-form-grid is-single">
              <v-text-field
                v-model="copyForm.title"
                label="复制功能名称"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />

              <v-textarea
                v-model="copyForm.note"
                label="功能描述"
                variant="outlined"
                rows="2"
                auto-grow
                density="compact"
                hide-details="auto"
              />
            </div>
          </div>
        </div>

        <div class="vpp-dialog-actions">
          <div class="vpp-dialog-actions-left" />
          <div class="vpp-dialog-actions-right">
            <v-btn variant="text" @click="dialog.copy = false">取消</v-btn>
            <v-btn class="vpp-confirm-btn" variant="text" :loading="saving.copy" @click="confirmCopyCard">确定复制</v-btn>
          </div>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import BaseCronField from './ui/BaseCronField.vue'
import { usePanelTheme } from '../composables/usePanelTheme'

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
const saving = reactive({ config: false, copy: false, delete: false })
const failedLogos = reactive({})
const editor = reactive(createCardDraft())
const copyForm = reactive({ title: '', note: '' })
const selectedCardId = ref('')
const lastLogRefresh = ref('')
const searchQuery = ref('')
const deletingCardId = ref('')
const logCardSeed = ref(null)
const rootEl = ref(null)

let logTimer = null

const { themeName: detectedThemeName } = usePanelTheme(rootEl)
const themeValue = computed(() => String(props.themeName || 'light').toLowerCase())
const fallbackThemeName = computed(() => (themeValue.value === 'custom' ? 'light' : themeValue.value))
const resolvedThemeName = computed(() => {
  const detected = String(detectedThemeName.value || '').toLowerCase()
  if (['light', 'dark', 'purple', 'transparent'].includes(detected)) return detected
  return fallbackThemeName.value
})
const themeClass = computed(() => `vpp-theme--${resolvedThemeName.value}`)

const dashboard = computed(() => status.dashboard || {})
const dashboardCards = computed(() => Array.isArray(dashboard.value.cards) ? dashboard.value.cards : [])
const historyItems = computed(() => {
  if (Array.isArray(status.history) && status.history.length) return status.history
  return Array.isArray(dashboard.value.history) ? dashboard.value.history : []
})
const cards = computed(() => (dashboardCards.value.length ? dashboardCards.value : buildFallbackCards()))
const enabledCount = computed(() => cards.value.filter((card) => card.enabled).length)
const autoCount = computed(() => cards.value.filter((card) => card.auto_run).length)
const copyCount = computed(() => cards.value.filter((card) => canDeleteCard(card)).length)
const displayCards = computed(() => {
  const keyword = String(searchQuery.value ?? '').trim().toLowerCase()
  if (!keyword) return cards.value
  return cards.value.filter((card) =>
    [
      card.title,
      card.site_name,
      card.site_domain,
      card.site_url,
      card.module_name,
      card.module_summary,
      card.module_description,
      card.status_text,
      card.note,
      card.breakfast_target,
      card.lunch_target,
      card.dinner_target,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(keyword)),
  )
})

function clearSearch() {
  searchQuery.value = ''
}

const controlStats = computed(() => [
  { label: '功能卡片', value: String(cards.value.length), icon: 'mdi-view-grid-outline' },
  { label: '启用中', value: String(enabledCount.value), icon: 'mdi-toggle-switch-outline' },
  { label: '定时执行', value: String(autoCount.value), icon: 'mdi-clock-outline' },
  { label: '可删除复制卡', value: String(copyCount.value), icon: 'mdi-content-copy' },
])
const activeDashboardCard = computed(() => cards.value.find((item) => item.card_id === selectedCardId.value) || null)
const currentLogCard = computed(() => activeDashboardCard.value || logCardSeed.value || null)
const latestStateLog = computed(() => {
  const card = currentLogCard.value
  if (!card) return null
  const entry = cardToLogEntry(card)
  if (!entry) return null
  return {
    ...entry,
    id: `latest-${entry.card_id || card.card_id || card.id || 'item'}-${entry.time || 'state'}`,
  }
})
const selectedLogs = computed(() => {
  const card = currentLogCard.value
  if (!card) return []
  const fallbackLogs = card.log_items || []
  const merged = new Map()
  for (const item of [latestStateLog.value, ...fallbackLogs, ...historyItems.value]) {
    if (!logMatchesCard(item, card)) continue
    const key = logEntryKey(item)
    if (!merged.has(key)) merged.set(key, item)
  }
  const items = [...merged.values()].sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  if (items.length) return items
  const fallbackItem = cardToLogEntry(card)
  return fallbackItem ? [fallbackItem] : []
})

function createEmptyConfig() {
  return {
    enabled: true,
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
    breakfast_target: String(source.breakfast_target || ''),
    lunch_target: String(source.lunch_target || ''),
    dinner_target: String(source.dinner_target || ''),
    note: String(source.note || ''),
    run_once: false,
  }
}

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value ?? null))
}

function normalizeCronExpression(value) {
  return String(value || '').replace(/\s+/g, ' ').trim()
}

function findCardFromPayload(payload, cardId) {
  const source = payload?.status?.config || payload?.config || payload?.status?.dashboard || payload?.dashboard || {}
  const cards = Array.isArray(source?.cards) ? source.cards : []
  return cards.find((item) => String(item?.id || item?.card_id || '') === String(cardId || '')) || null
}

function findDashboardCardFromPayload(payload, cardId) {
  const source = payload?.status?.dashboard || payload?.dashboard || {}
  const cards = Array.isArray(source?.cards) ? source.cards : []
  return cards.find((item) => String(item?.card_id || item?.id || '') === String(cardId || '')) || null
}

function moduleMeta(moduleKey) {
  return (panelConfig.value.module_options || []).find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '•',
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

function getCardId(card) {
  return String(card?.id || card?.card_id || '')
}

function normalizeCardWithMeta(source = {}, metaSource = null, toneOptions = null, options = {}) {
  const meta = metaSource || moduleMeta(String(source.module_key || source.module || 'siqi_sign'))
  const toneValues = new Set((toneOptions || panelConfig.value.tone_options || []).map((item) => item.key))
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
    breakfast_target: meta.key === 'siqi_dineout' ? String(source.breakfast_target || '').trim() : '',
    lunch_target: meta.key === 'siqi_dineout' ? String(source.lunch_target || '').trim() : '',
    dinner_target: meta.key === 'siqi_dineout' ? String(source.dinner_target || '').trim() : '',
    note: String(source.note || '').trim(),
  }
}

function normalizeCard(source = {}, options = {}) {
  return normalizeCardWithMeta(source, null, null, options)
}

function normalizeConfig(source = {}) {
  const next = createEmptyConfig()
  next.enabled = source.enabled !== false
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
  next.cards = Array.isArray(source.cards)
    ? source.cards.map((item) => {
      const meta = next.module_options.find((module) => module.key === String(item.module_key || item.module || 'siqi_sign')) || null
      return normalizeCardWithMeta(item, meta, next.tone_options)
    })
    : []
  for (const meta of next.module_options) {
    if (next.cards.some((item) => item.module_key === meta.key)) continue
    next.cards.push(normalizeCardWithMeta({
      module_key: meta.key,
      title: meta.label,
      site_name: meta.default_site_name || meta.label,
      site_url: meta.default_site_url || '',
      enabled: false,
      auto_run: true,
      notify: true,
      cron: DEFAULT_CRON,
      tone: meta.tone || 'azure',
      note: '',
    }, meta, next.tone_options))
  }
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
  if (meta.key === 'siqi_dineout' && ![card.breakfast_target, card.lunch_target, card.dinner_target].some(Boolean)) {
    return {
      level: 'warning',
      status_title: '待配置餐馆',
      status_text: '请先填写早餐 / 中餐 / 晚餐要前往的用户名。',
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
  const dineoutTargets = [card.breakfast_target, card.lunch_target, card.dinner_target].filter(Boolean)
  if (dineoutTargets.length) tags.push(`目标 ${dineoutTargets.length} 家`)
  return tags
}

function buildFallbackCards() {
  return (panelConfig.value.cards || []).map((source) => {
    const card = normalizeCard(source)
    const meta = moduleMeta(card.module_key)
    const fallbackCard = { ...card, card_id: card.id }
    const logItems = historyItems.value
      .filter((item) => logMatchesCard(item, fallbackCard))
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
  const normalizedCards = cards.map((item) => normalizeCard(item))
  return {
    // Keep the plugin itself active; real control lives on each card's enabled/cron state.
    enabled: true,
    notify: !!panelConfig.value.notify,
    onlyonce: !!panelConfig.value.onlyonce,
    use_proxy: !!panelConfig.value.use_proxy,
    force_ipv4: panelConfig.value.force_ipv4 !== false,
    cron: String(panelConfig.value.cron || DEFAULT_CRON),
    http_timeout: Number(panelConfig.value.http_timeout || 15),
    http_retry_times: Number(panelConfig.value.http_retry_times || 3),
    random_delay_max_seconds: Number(panelConfig.value.random_delay_max_seconds || 5),
    cards: normalizedCards,
  }
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

function logTone(item) {
  const level = String(item?.level || '').toLowerCase()
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  const text = `${item?.status_title || ''} ${item?.summary || ''}`.toLowerCase()
  if (/(error|fail|异常|失败)/.test(text)) return 'danger'
  if (/(warning|待|cookie|uid)/.test(text)) return 'warning'
  if (/(success|完成|成功|签到|领取)/.test(text)) return 'success'
  return 'info'
}

function logStatusLabel(item) {
  return item?.status_title || item?.title || runtimeLabel(item?.level)
}

function logDetail(item) {
  if (item?.summary) return item.summary
  const lines = Array.isArray(item?.lines) ? item.lines.filter(Boolean) : []
  if (lines.length) return lines[0]
  return '暂无详情'
}

function logEntryKey(item) {
  if (!item) return ''
  return [
    String(item.card_id || '').trim(),
    String(item.time || '').trim(),
    String(item.status_title || item.title || '').trim(),
    String(item.summary || '').trim(),
    Array.isArray(item.lines) ? item.lines.filter(Boolean).join('|') : '',
  ].join('::')
}

function cardToLogEntry(card) {
  if (!card) return null
  const time = String(card.last_run || card.last_checked || '').trim()
  const summary = String(card.status_text || '').trim()
  const lines = Array.isArray(card.detail_lines) ? card.detail_lines.filter(Boolean) : []
  const title = String(card.title || '').trim()
  if (!time && !summary && !lines.length && !title) return null
  return {
    id: `card-fallback-${card.card_id || card.id || 'item'}-${time || 'now'}`,
    time: time || '--',
    title: title || '最近状态',
    summary,
    status_title: String(card.status_title || '最近状态').trim(),
    level: String(card.level || 'info').trim(),
    lines,
    card_id: String(card.card_id || card.id || '').trim(),
    module_key: String(card.module_key || '').trim(),
    site_name: String(card.site_name || '').trim(),
    site_url: String(card.site_url || '').trim(),
  }
}

function logMatchesCard(item, card) {
  if (!item || !card) return false
  const cardId = String(card.card_id || card.id || '').trim()
  const itemCardId = String(item.card_id || '').trim()
  if (cardId && itemCardId && cardId === itemCardId) return true

  const cardModule = String(card.module_key || '').trim()
  const itemModule = String(item.module_key || '').trim()
  if (!cardModule || !itemModule || cardModule !== itemModule) return false

  const cardSiteUrl = String(card.site_url || '').trim().toLowerCase()
  const itemSiteUrl = String(item.site_url || '').trim().toLowerCase()
  if (cardSiteUrl && itemSiteUrl && cardSiteUrl === itemSiteUrl) return true

  const cardSiteName = String(card.site_name || '').trim().toLowerCase()
  const itemSiteName = String(item.site_name || '').trim().toLowerCase()
  if (cardSiteName && itemSiteName && cardSiteName === itemSiteName) return true

  const cardTitle = String(card.title || '').trim().toLowerCase()
  const itemTitle = String(item.title || '').trim().toLowerCase()
  return Boolean(cardTitle && itemTitle && cardTitle === itemTitle)
}

function scheduleText(card) {
  if (!card?.enabled) return '已停用'
  if (!card?.auto_run) return '仅手动执行'
  return card?.next_run_time || card?.cron || '等待调度'
}

function cardSubtitle(card) {
  return String(cardDescription(card) || card?.module_summary || 'plugin card').trim()
}

function cardDescription(card) {
  return String(card?.note || card?.module_description || card?.status_text || '暂无说明').trim()
}

function cardStatusSummary(card) {
  const summary = String(card?.status_text || scheduleText(card) || '').trim()
  if (!summary) return ''
  if (summary === '卡片配置已经加载，可以点击刷新或执行启用查看实时状态。') return ''
  return summary
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

function canDeleteCard(card) {
  const cardId = getCardId(card)
  return Boolean(cardId) && !cardId.endsWith('-default')
}

function openConfigDialog(card) {
  const source = rawCardById(card.card_id) || card
  Object.assign(editor, normalizeCard(source))
  editor.run_once = false
  selectedCardId.value = card.card_id
  dialog.config = true
}

function openLogsDialog(card) {
  selectedCardId.value = card.card_id
  logCardSeed.value = deepClone(card)
  dialog.logs = true
}

function openCopyDialog(card) {
  selectedCardId.value = card.card_id
  copyForm.title = `${card.title} 副本`
  copyForm.note = card.note || card.module_description || ''
  dialog.copy = true
}

function applyStatusPayload(payload = {}) {
  const source = payload?.status && typeof payload.status === 'object' ? payload.status : payload
  if (!source || typeof source !== 'object') return false

  if ('enabled' in source) status.enabled = !!source.enabled
  status.next_run_time = source.next_run_time || ''
  status.last_run = source.last_run || ''
  status.history = Array.isArray(source.history)
    ? source.history
    : (Array.isArray(source.dashboard?.history) ? source.dashboard.history : [])
  status.dashboard = source.dashboard || payload.dashboard || {}
  if (source.config || payload.config) panelConfig.value = normalizeConfig(source.config || payload.config || {})
  lastLogRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  return true
}

async function loadStatus(showError = true) {
  try {
    const payload = await props.api.get('/plugin/VuePanel/status')
    applyStatusPayload(payload)
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  }
}

async function persistCards(nextCards, successText) {
  const payload = serializeConfig(nextCards)
  const response = await props.api.post('/plugin/VuePanel/config', payload)
  applyStatusPayload(response)
  flash(response.message || successText || '配置已保存')
  if (!response?.status) await loadStatus(false)
  return response
}

async function refreshStatus() {
  loading.refreshAll = true
  try {
    const response = await props.api.post('/plugin/VuePanel/refresh', {})
    applyStatusPayload(response)
    flash(response.message || '状态已刷新')
    if (!response?.status) await loadStatus(false)
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
    applyStatusPayload(response)
    flash(response.message || '已执行启用任务')
    if (!response?.status) await loadStatus(false)
  } catch (error) {
    flash(error?.message || '执行任务失败', 'error')
  } finally {
    loading.runAll = false
  }
}

async function saveCardConfig() {
  saving.config = true
  try {
    const runAfterSave = !!editor.run_once
    const requestedCron = normalizeCronExpression(editor.cron)
    let matched = false
    const nextCards = (panelConfig.value.cards || []).map((item) => {
      if (item.id === editor.id) {
        matched = true
        return normalizeCard(editor)
      }
      return normalizeCard(item)
    })
    if (!matched) nextCards.push(normalizeCard(editor))
    const response = await persistCards(nextCards, runAfterSave ? '卡片配置已保存，准备立即执行' : '卡片配置已保存')
    const savedCard = findCardFromPayload(response, editor.id)
    const dashboardCard = findDashboardCardFromPayload(response, editor.id)
    const effectiveCron = normalizeCronExpression(savedCard?.cron || '')
    if (effectiveCron && requestedCron && effectiveCron !== requestedCron) {
      flash(`Cron 实际生效为 ${effectiveCron}，与当前输入 ${requestedCron} 不一致，请重新保存一次。`, 'warning')
      return
    }
    if (savedCard?.enabled && savedCard?.auto_run && effectiveCron && !dashboardCard?.next_run_time) {
      flash(`Cron 已保存为 ${effectiveCron}，但暂未计算出下次运行时间，请检查表达式。`, 'warning')
      return
    }
    if (!runAfterSave && dashboardCard?.enabled && dashboardCard?.auto_run && dashboardCard?.next_run_time) {
      flash(`卡片配置已保存，下次运行：${dashboardCard.next_run_time}`)
    }
    if (runAfterSave) {
      const runResponse = await props.api.post('/plugin/VuePanel/card/run', { card_id: editor.id })
      applyStatusPayload(runResponse)
      flash(runResponse.message || '卡片已保存并立即执行一次')
    }
    editor.run_once = false
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

async function deleteCard(card) {
  const cardId = getCardId(card)
  if (!canDeleteCard(card)) return
  const target = rawCardById(cardId) || normalizeCard(card)
  const title = target.title || '当前卡片'
  if (typeof window !== 'undefined' && !window.confirm(`确认删除“${title}”吗？`)) return

  saving.delete = true
  deletingCardId.value = cardId
  try {
    const nextCards = (panelConfig.value.cards || [])
      .filter((item) => item.id !== cardId)
      .map((item) => normalizeCard(item))
    await persistCards(nextCards, '卡片已删除')
    if (selectedCardId.value === cardId) {
      dialog.config = false
      dialog.logs = false
      dialog.copy = false
      selectedCardId.value = ''
    }
  } catch (error) {
    flash(error?.message || '删除卡片失败', 'error')
  } finally {
    saving.delete = false
    deletingCardId.value = ''
  }
}

async function deleteCurrentCard() {
  await deleteCard(activeDashboardCard.value || editor)
}

async function runFocusedCard() {
  if (!selectedCardId.value) return
  loading.cardRun = true
  try {
    const response = await props.api.post('/plugin/VuePanel/card/run', { card_id: selectedCardId.value })
    applyStatusPayload(response)
    flash(response.message || '卡片执行完成')
    if (!response?.status) await loadStatus(false)
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
    applyStatusPayload(response)
    flash(response.message || '卡片状态已刷新')
    if (!response?.status) await loadStatus(false)
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
    else {
      stopLogPolling()
      logCardSeed.value = null
    }
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
.vuepanel-page,
.vpp-dialog-card {
  --vpp-theme-rgb: var(--v-theme-primary);
  --vpp-accent-rgb: var(--v-theme-primary);
  --vpp-surface: rgba(var(--v-theme-surface), 0.96);
  --vpp-surface-soft: rgba(var(--v-theme-surface), 0.93);
  --vpp-surface-muted: rgba(var(--v-theme-surface-variant), 0.08);
  --vpp-surface-strong: rgba(var(--v-theme-surface), 0.99);
  --vpp-line: rgba(var(--v-border-color), 0.18);
  --vpp-line-strong: rgba(var(--v-theme-primary), 0.24);
  --vpp-page-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.95)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.03), rgba(var(--v-theme-primary), 0.03) 10px, transparent 10px, transparent 20px);
  --vpp-panel-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.95)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.03), rgba(var(--v-theme-primary), 0.03) 10px, transparent 10px, transparent 20px);
  --vpp-panel-section-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.97), rgba(var(--v-theme-surface), 0.94)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.025), rgba(var(--v-theme-primary), 0.025) 10px, transparent 10px, transparent 20px);
  --vpp-stat-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.985), rgba(var(--v-theme-surface), 0.955)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.03), rgba(var(--v-theme-primary), 0.03) 10px, transparent 10px, transparent 20px);
  --vpp-card-bg:
    linear-gradient(135deg, rgba(var(--v-theme-primary), 0.07), rgba(var(--v-theme-surface), 0.98) 42%, rgba(var(--v-theme-surface), 0.95)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.022), rgba(var(--v-theme-primary), 0.022) 10px, transparent 10px, transparent 20px);
  --vpp-card-hover-bg:
    linear-gradient(135deg, rgba(var(--v-theme-primary), 0.12), rgba(var(--v-theme-surface), 0.99) 42%, rgba(var(--v-theme-surface), 0.96)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.03), rgba(var(--v-theme-primary), 0.03) 10px, transparent 10px, transparent 20px);
  --vpp-note-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.94)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.035), rgba(var(--v-theme-primary), 0.035) 10px, transparent 10px, transparent 20px);
  --vpp-chip-bg: rgba(var(--v-theme-primary), 0.08);
  --vpp-field-bg: rgba(var(--v-theme-surface), 0.92);
  --vpp-toolbar-bg: rgba(var(--v-theme-surface), 0.9);
  --vpp-button-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.96), rgba(var(--v-theme-surface), 0.93)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.022), rgba(var(--v-theme-primary), 0.022) 10px, transparent 10px, transparent 20px);
  --vpp-footer-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.95)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.02), rgba(var(--v-theme-primary), 0.02) 10px, transparent 10px, transparent 20px);
  --vpp-dialog-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.95)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.03), rgba(var(--v-theme-primary), 0.03) 10px, transparent 10px, transparent 20px);
  --vpp-dialog-panel-bg:
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.97), rgba(var(--v-theme-surface), 0.94)),
    repeating-linear-gradient(45deg, rgba(var(--v-theme-primary), 0.025), rgba(var(--v-theme-primary), 0.025) 10px, transparent 10px, transparent 20px);
  --vpp-card-shadow: 0 1px 2px rgba(var(--v-border-color), 0.05);
  --vpp-card-hover-shadow: 0 3px 6px rgba(var(--v-border-color), 0.1);
  --vpp-dialog-shadow: 0 10px 28px rgba(var(--v-border-color), 0.16);
  --vpp-shine-band: rgba(255, 255, 255, 0.18);
  --vpp-shine-accent: rgba(var(--v-theme-primary), 0.72);
  --vpp-shine-sweep: rgba(var(--v-theme-primary), 0.12);
  --vpp-blue: #4ca8ff;
  --vpp-green: #2db870;
  --vpp-yellow: #e9a23b;
  --vpp-red: #e36060;
  --vpp-text: rgb(var(--v-theme-on-surface));
  --vpp-text-soft: rgba(var(--v-theme-on-surface), 0.76);
  --vpp-text-faint: rgba(var(--v-theme-on-surface), 0.58);
  min-height: 100%;
  padding: 8px 0 20px;
  color: var(--vpp-text);
}

.vuepanel-page.vpp-theme--dark,
.vpp-dialog-card.vpp-theme--dark {
  --vpp-line: rgba(var(--v-border-color), 0.24);
  --vpp-line-strong: rgba(var(--v-theme-primary), 0.28);
  --vpp-card-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
  --vpp-card-hover-shadow: 0 4px 10px rgba(0, 0, 0, 0.24);
  --vpp-dialog-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
  --vpp-shine-band: rgba(255, 255, 255, 0.1);
  --vpp-shine-accent: rgba(var(--v-theme-primary), 0.68);
  --vpp-shine-sweep: rgba(var(--v-theme-primary), 0.08);
}

.vuepanel-page.vpp-theme--purple,
.vpp-dialog-card.vpp-theme--purple {
  --vpp-line: rgba(var(--v-border-color), 0.22);
  --vpp-line-strong: rgba(var(--v-theme-primary), 0.3);
  --vpp-card-shadow: 0 1px 2px rgba(16, 8, 28, 0.16);
  --vpp-card-hover-shadow: 0 4px 10px rgba(16, 8, 28, 0.22);
  --vpp-dialog-shadow: 0 14px 34px rgba(16, 8, 28, 0.26);
  --vpp-shine-band: rgba(255, 255, 255, 0.11);
  --vpp-shine-accent: rgba(var(--v-theme-primary), 0.74);
  --vpp-shine-sweep: rgba(var(--v-theme-primary), 0.1);
}

.vuepanel-page.vpp-theme--transparent,
.vpp-dialog-card.vpp-theme--transparent {
  --vpp-line: rgba(var(--v-border-color), 0.22);
  --vpp-line-strong: rgba(var(--v-theme-primary), 0.28);
  --vpp-card-shadow: 0 1px 2px rgba(0, 0, 0, 0.14);
  --vpp-card-hover-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  --vpp-dialog-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
  --vpp-shine-band: rgba(255, 255, 255, 0.09);
  --vpp-shine-accent: rgba(var(--v-theme-primary), 0.7);
  --vpp-shine-sweep: rgba(var(--v-theme-primary), 0.08);
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
  padding: 2px;
}

.vuepanel-page {
  position: relative;
  background: var(--vpp-page-bg);
  border-radius: 22px;
}

.vpp-control-panel,
.vpp-stat-card,
.vpp-card,
.vpp-dialog-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--vpp-line);
  backdrop-filter: blur(18px);
  box-shadow: var(--vpp-card-shadow);
}

.vpp-control-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--vpp-panel-bg);
}

.vpp-control-panel::before,
.vpp-stat-card::before,
.vpp-dialog-panel::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(var(--vpp-theme-rgb), 0.84), transparent);
  opacity: 0.85;
  pointer-events: none;
}

.vpp-panel-left {
  flex: 1;
  min-width: 0;
  max-width: 420px;
}

.vpp-search-field :deep(.v-field) {
  border-radius: 12px;
  background: var(--vpp-field-bg) !important;
}

.vpp-search-field :deep(.v-field__outline) {
  --v-field-border-opacity: 0.18;
}

.vpp-search-field :deep(.v-field__input),
.vpp-search-field :deep(.v-label),
.vpp-search-field :deep(.v-icon),
.vpp-search-field :deep(input) {
  color: var(--vpp-text);
  -webkit-text-fill-color: var(--vpp-text);
}

.vpp-panel-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vpp-toolbar-btn {
  min-height: 34px;
  padding: 0 14px;
  border-radius: 11px;
  border: 1px solid var(--vpp-line) !important;
  background: var(--vpp-toolbar-bg) !important;
  color: var(--vpp-text);
  text-transform: none;
  letter-spacing: 0;
  font-weight: 700;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease, background 0.24s ease;
}

.vpp-toolbar-btn:hover {
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(var(--vpp-theme-rgb), 0.16), rgba(var(--vpp-theme-rgb), 0.05) 56%, transparent) !important;
  border-color: var(--vpp-line-strong) !important;
  box-shadow: 0 14px 28px color-mix(in srgb, var(--mp-shadow-color) 82%, transparent);
}

.vpp-toolbar-btn.is-icon {
  min-width: 34px;
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
  background: var(--vpp-yellow);
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
  color: var(--vpp-text-faint);
}

.vpp-alert {
  border: 1px solid var(--vpp-line);
  background: color-mix(in srgb, var(--vpp-field-bg) 92%, transparent);
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
  padding: 14px;
  border-radius: 16px;
  background: var(--vpp-stat-bg);
  transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease, background 0.28s ease;
}

.vpp-stat-card:hover {
  transform: translateY(-3px);
  border-color: var(--vpp-line-strong);
  box-shadow: var(--vpp-card-hover-shadow);
}

.vpp-stat-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(var(--vpp-theme-rgb), 0.18);
  background: linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.16), rgba(var(--vpp-theme-rgb), 0.06));
  color: rgb(var(--vpp-theme-rgb));
}

.vpp-stat-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.vpp-stat-value {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
  color: var(--vpp-text);
}

.vpp-stat-label {
  font-size: 11px;
  color: var(--vpp-text-faint);
  font-weight: 700;
}

.vpp-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.vpp-card {
  --vpp-tone-rgb: var(--vpp-theme-rgb);
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 224px;
  padding: 18px;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.08), transparent 34%),
    linear-gradient(135deg, rgba(var(--vpp-tone-rgb), 0.05), transparent 55%),
    var(--vpp-card-bg);
  backdrop-filter: blur(20px);
  box-shadow: var(--vpp-card-shadow);
  transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease, background 0.28s ease;
}

.vpp-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--vpp-shine-band), var(--vpp-shine-accent), transparent);
  transform: translateX(-100%);
  transition: transform 0.72s ease;
  z-index: 1;
}

.vpp-card::after {
  content: '';
  position: absolute;
  top: -30%;
  left: -62%;
  width: 42%;
  height: 190%;
  background: linear-gradient(115deg, transparent, var(--vpp-shine-sweep), rgba(255, 255, 255, 0.18), transparent);
  transform: translateX(0) rotate(18deg);
  opacity: 0;
  transition: transform 0.72s ease, opacity 0.28s ease;
  pointer-events: none;
}

.vpp-card:hover::before {
  transform: translateX(100%);
}

.vpp-card:hover::after {
  transform: translateX(340%) rotate(18deg);
  opacity: 1;
}

.vpp-card:hover {
  transform: translateY(-7px);
  border-color: color-mix(in srgb, rgba(var(--vpp-theme-rgb), 0.3) 65%, var(--vpp-line));
  box-shadow: var(--vpp-card-hover-shadow);
  background:
    linear-gradient(180deg, rgba(var(--vpp-tone-rgb), 0.14), transparent 32%),
    linear-gradient(135deg, rgba(var(--vpp-tone-rgb), 0.08), transparent 56%),
    var(--vpp-card-hover-bg);
}

.vpp-card.is-enabled {
  border-color: color-mix(in srgb, rgba(45, 184, 112, 0.28) 60%, var(--vpp-line));
}

.vpp-card.is-disabled {
  opacity: 0.94;
}

.vpp-card-glow {
  position: absolute;
  inset: 0 0 auto;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(var(--vpp-theme-rgb), 0.88), transparent);
  opacity: 0.84;
}

.vpp-card-head {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.vpp-logo-wrap {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.2), rgba(var(--vpp-theme-rgb), 0.07)),
    color-mix(in srgb, var(--vpp-surface-muted) 86%, transparent);
  border: 1px solid color-mix(in srgb, rgba(var(--vpp-theme-rgb), 0.26) 65%, var(--vpp-line));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
  min-width: 0;
}

.vpp-card-title-group {
  min-width: 0;
}

.vpp-card-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--vpp-text);
}

.vpp-status-pill,
.vpp-mini-pill,
.vpp-runtime-pill,
.vpp-meta-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.vpp-status-pill {
  font-size: 11px;
  font-weight: 800;
  margin-left: auto;
  border: 1px solid var(--vpp-line);
  background: color-mix(in srgb, var(--vpp-chip-bg) 88%, transparent);
}

.vpp-status-pill.is-enabled {
  color: var(--vpp-green);
  border-color: rgba(45, 184, 112, 0.28);
  background: rgba(45, 184, 112, 0.14);
}

.vpp-status-pill.is-disabled {
  color: var(--vpp-text-faint);
  border-color: rgba(140, 138, 158, 0.28);
  background: rgba(140, 138, 158, 0.14);
}

.vpp-card-desc {
  margin: 5px 0 0;
  color: var(--vpp-text-soft);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  min-height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  border: 1px solid var(--vpp-line);
  background: var(--vpp-chip-bg);
  color: var(--vpp-text-soft);
  font-size: 11px;
  line-height: 1;
}

.vpp-runtime-pill {
  border: 1px solid rgba(76, 168, 255, 0.4);
  background: rgba(76, 168, 255, 0.1);
  color: var(--vpp-blue);
  font-size: 11px;
  font-weight: 800;
}

.vpp-runtime-pill.is-success {
  border-color: rgba(45, 184, 112, 0.42);
  background: rgba(45, 184, 112, 0.12);
  color: var(--vpp-green);
}

.vpp-runtime-pill.is-warning {
  border-color: rgba(233, 162, 59, 0.42);
  color: var(--vpp-yellow);
  background: rgba(233, 162, 59, 0.12);
}

.vpp-runtime-pill.is-danger {
  border-color: rgba(227, 96, 96, 0.42);
  color: var(--vpp-red);
  background: rgba(227, 96, 96, 0.12);
}

.vpp-card-body {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--vpp-line);
  background:
    linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.08), transparent 54%),
    var(--vpp-note-bg);
}

.vpp-card-note {
  margin: 0;
  color: var(--vpp-text-soft);
  font-size: 12px;
  line-height: 1.65;
  min-height: 40px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.vpp-mini-pill {
  font-size: 12px;
  font-weight: 800;
}

.vpp-mini-pill.is-enabled {
  color: #ffffff;
  background: var(--vpp-green);
}

.vpp-mini-pill.is-disabled {
  color: #ffffff;
  background: rgba(136, 136, 148, 0.88);
}

.vpp-action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.vpp-action-btn,
.vpp-confirm-btn {
  min-height: 34px;
  border-radius: 11px;
  border: 1px solid var(--vpp-line) !important;
  background: var(--vpp-field-bg) !important;
  text-transform: none;
  font-weight: 700;
  letter-spacing: 0;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease, background 0.24s ease;
}

.vpp-action-btn {
  flex: 1 1 0;
  color: var(--vpp-text);
}

.vpp-action-btn:hover,
.vpp-confirm-btn:hover {
  transform: translateY(-2px);
  border-color: var(--vpp-line-strong) !important;
  box-shadow: 0 14px 28px color-mix(in srgb, var(--mp-shadow-color) 82%, transparent);
  background: linear-gradient(135deg, rgba(var(--vpp-theme-rgb), 0.16), rgba(var(--vpp-theme-rgb), 0.06) 58%, transparent) !important;
}

.vpp-action-btn.is-delete {
  flex-basis: auto;
  color: var(--vpp-red);
}

.vpp-action-btn.is-delete:hover {
  border-color: rgba(227, 96, 96, 0.44);
  box-shadow: 0 12px 26px rgba(227, 96, 96, 0.14);
  background: rgba(227, 96, 96, 0.08);
}

.vpp-action-btn.is-delete.is-disabled-control {
  color: var(--vpp-text-faint);
  opacity: 0.5;
  box-shadow: none;
}

.vpp-action-btn :deep(.v-btn__content),
.vpp-confirm-btn :deep(.v-btn__content) {
  gap: 6px;
  font-size: 12px;
}

.vpp-confirm-btn {
  color: rgb(var(--vpp-theme-rgb));
  border-color: rgba(var(--vpp-theme-rgb), 0.2) !important;
  background: linear-gradient(135deg, rgba(var(--vpp-theme-rgb), 0.14), rgba(var(--vpp-theme-rgb), 0.06) 58%, transparent) !important;
}

.vpp-dialog-card {
  --mp-bg-input: var(--vpp-field-bg);
  --mp-text-primary: var(--vpp-text);
  --mp-radius-md: 12px;
  border-radius: 20px !important;
  border: 1px solid var(--vpp-line);
  background: var(--vpp-dialog-bg) !important;
  color: var(--vpp-text);
  backdrop-filter: blur(20px);
  box-shadow: var(--vpp-dialog-shadow);
  overflow: hidden;
}

.vpp-dialog-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(var(--vpp-accent-rgb), 0.92), transparent);
}

.vpp-dialog-card.is-config {
  --vpp-accent-rgb: var(--vpp-theme-rgb);
}

.vpp-dialog-card.is-logs {
  --vpp-accent-rgb: var(--vpp-theme-rgb);
}

.vpp-dialog-card.is-copy {
  --vpp-accent-rgb: var(--vpp-theme-rgb);
}

.vpp-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px 20px 10px;
  border-bottom: 1px solid color-mix(in srgb, rgba(var(--vpp-theme-rgb), 0.12) 68%, var(--vpp-line));
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
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--vpp-line);
  background: linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.18), transparent 70%), var(--vpp-surface-muted);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
  color: rgb(var(--vpp-theme-rgb));
}

.vpp-dialog-icon.is-config {
  color: rgb(var(--vpp-theme-rgb));
}

.vpp-dialog-icon.is-logs {
  color: rgb(var(--vpp-theme-rgb));
}

.vpp-dialog-icon.is-copy {
  color: rgb(var(--vpp-theme-rgb));
}

.vpp-dialog-title {
  margin: 4px 0 0;
  font-size: 18px;
  line-height: 1.2;
  color: var(--vpp-text);
}

.vpp-dialog-body {
  display: grid;
  gap: 12px;
  padding: 14px 20px 0;
}

.vpp-dialog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.vpp-meta-chip {
  border: 1px solid var(--vpp-line);
  background: var(--vpp-chip-bg);
  color: var(--vpp-text-soft);
  font-size: 11px;
  font-weight: 600;
}

.vpp-dialog-hint {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--vpp-line);
  background: linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.12), transparent 80%);
  color: var(--vpp-text-soft);
  font-size: 12px;
  line-height: 1.6;
}

.vpp-dialog-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px 20px;
}

.vpp-dialog-actions-left,
.vpp-dialog-actions-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vpp-dialog-panel {
  position: relative;
  display: grid;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid color-mix(in srgb, rgba(var(--vpp-theme-rgb), 0.24) 60%, var(--vpp-line));
  background:
    linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.08), transparent 44%),
    var(--vpp-dialog-panel-bg);
}

.vpp-section-title {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, rgba(var(--vpp-theme-rgb), 0.18) 60%, var(--vpp-line));
  background: linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.12), transparent 96%), var(--vpp-chip-bg);
  font-size: 13px;
  font-weight: 800;
  color: var(--vpp-text);
}

.vpp-switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.vpp-switch-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-height: 56px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--vpp-line);
  background: color-mix(in srgb, var(--vpp-field-bg) 92%, transparent);
}

.vpp-switch-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--vpp-text);
}

.vpp-switch-card :deep(.v-switch) {
  margin-inline-start: 0;
}

.vpp-switch-card.is-emphasis {
  border-color: rgba(var(--vpp-theme-rgb), 0.24);
  background: linear-gradient(135deg, rgba(var(--vpp-theme-rgb), 0.12), rgba(var(--vpp-theme-rgb), 0.04) 54%, transparent);
}

.vpp-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.vpp-form-grid.is-single {
  grid-template-columns: 1fr;
}

.vpp-field-span-2 {
  grid-column: span 2;
}

.vpp-dialog-card :deep(.v-field) {
  border-radius: 12px;
  background: var(--vpp-field-bg) !important;
  color: var(--vpp-text) !important;
  box-shadow: none !important;
}

.vpp-dialog-card :deep(.v-field__overlay) {
  background: transparent;
}

.vpp-dialog-card :deep(.v-field__outline) {
  --v-field-border-opacity: 0.22;
}

.vpp-dialog-card :deep(.v-field--variant-outlined .v-field__outline__start),
.vpp-dialog-card :deep(.v-field--variant-outlined .v-field__outline__notch::before),
.vpp-dialog-card :deep(.v-field--variant-outlined .v-field__outline__notch::after),
.vpp-dialog-card :deep(.v-field--variant-outlined .v-field__outline__end) {
  border-color: var(--vpp-line) !important;
}

.vpp-dialog-card :deep(.v-field.v-field--focused .v-field__outline__start),
.vpp-dialog-card :deep(.v-field.v-field--focused .v-field__outline__notch::before),
.vpp-dialog-card :deep(.v-field.v-field--focused .v-field__outline__notch::after),
.vpp-dialog-card :deep(.v-field.v-field--focused .v-field__outline__end) {
  border-color: rgba(var(--vpp-theme-rgb), 0.44) !important;
}

.vpp-dialog-card :deep(.v-label),
.vpp-dialog-card :deep(.v-field-label),
.vpp-dialog-card :deep(.v-field__input),
.vpp-dialog-card :deep(.v-field__prepend-inner),
.vpp-dialog-card :deep(.v-field__append-inner),
.vpp-dialog-card :deep(.v-select__selection),
.vpp-dialog-card :deep(.v-select__selection-text),
.vpp-dialog-card :deep(input),
.vpp-dialog-card :deep(textarea) {
  color: var(--vpp-text) !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--vpp-text) !important;
}

.vpp-dialog-card :deep(.v-selection-control__wrapper),
.vpp-dialog-card :deep(.v-selection-control .v-label),
.vpp-dialog-card :deep(.v-field .v-icon),
.vpp-dialog-card :deep(.v-selection-control__input .v-icon),
.vpp-dialog-card :deep(.v-messages__message) {
  color: var(--vpp-text) !important;
}

.vpp-dialog-card :deep(.v-field-label--floating),
.vpp-dialog-card :deep(.v-label.v-field-label) {
  color: var(--vpp-text-soft) !important;
}

.vpp-dialog-card :deep(input::placeholder),
.vpp-dialog-card :deep(textarea::placeholder) {
  color: var(--vpp-text-faint) !important;
  opacity: 1 !important;
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
  background: var(--vpp-green);
  box-shadow: 0 0 0 6px rgba(45, 184, 112, 0.18);
  animation: pulse 1.8s ease infinite;
}

.vpp-log-panel {
  padding: 12px;
}

.vpp-log-table {
  display: grid;
  gap: 10px;
}

.vpp-log-table-head,
.vpp-log-row {
  display: grid;
  grid-template-columns: 140px 96px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.vpp-log-table-head {
  padding: 0 10px;
  color: var(--vpp-text-faint);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.vpp-log-table-body {
  display: grid;
  gap: 8px;
  max-height: 50vh;
  padding-right: 4px;
}

.vpp-log-row {
  padding: 10px;
  border-radius: 14px;
  border: 1px solid var(--vpp-line);
  background:
    linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.06), transparent 56%),
    color-mix(in srgb, var(--vpp-field-bg) 94%, transparent);
}

.vpp-log-time {
  font-size: 12px;
  font-weight: 700;
  color: var(--vpp-text-soft);
}

.vpp-log-status {
  display: flex;
  align-items: flex-start;
}

.vpp-log-detail {
  min-width: 0;
}

.vpp-log-summary {
  margin: 0;
  color: var(--vpp-text);
  font-size: 12px;
  line-height: 1.6;
  word-break: break-word;
}

.vpp-log-lines {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.vpp-log-line {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--vpp-chip-bg);
  color: var(--vpp-text-soft);
  font-size: 11px;
}

.vpp-empty-state {
  padding: 20px 18px;
  border-radius: 14px;
  border: 1px dashed var(--vpp-line);
  color: var(--vpp-text-soft);
  text-align: center;
  background:
    linear-gradient(180deg, rgba(var(--vpp-theme-rgb), 0.05), transparent 62%),
    color-mix(in srgb, var(--vpp-field-bg) 94%, transparent);
}

.vpp-grid-empty {
  grid-column: 1 / -1;
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

  .vpp-switch-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .vuepanel-page {
    border-radius: 18px;
  }

  .vpp-dialog-head,
  .vpp-dialog-body,
  .vpp-dialog-actions {
    padding-left: 16px;
    padding-right: 16px;
  }

  .vpp-log-table-head,
  .vpp-log-row {
    grid-template-columns: 1fr;
  }

  .vpp-card-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpp-status-pill {
    margin-left: 0;
  }

  .vpp-field-span-2 {
    grid-column: auto;
  }

  .vpp-form-grid {
    grid-template-columns: 1fr;
  }

  .vpp-dialog-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .vpp-dialog-actions-left,
  .vpp-dialog-actions-right {
    width: 100%;
    justify-content: stretch;
    flex-wrap: wrap;
  }

  .vpp-dialog-actions-right > * {
    flex: 1 1 auto;
  }
}

@media (max-width: 560px) {
  .vpp-card-title-row,
  .vpp-dialog-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpp-action-row {
    flex-direction: column;
  }

  .vpp-action-btn,
  .vpp-confirm-btn,
  .vpp-action-btn.is-delete {
    flex: 1 1 auto;
  }
}
</style>
