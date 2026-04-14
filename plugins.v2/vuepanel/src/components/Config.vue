<template>
  <div class="vuepanel-config">
    <div class="vpc-shell">
      <header class="vpc-hero">
        <div>
          <div class="vpc-kicker">Global Settings</div>
          <h1 class="vpc-title">Vue-面板设置</h1>
          <p class="vpc-subtitle">这里负责插件级开关与运行参数。单卡片的配置、日志和复制，请回到功能面板操作。</p>
          <div class="vpc-chip-row">
            <span class="vpc-chip">主题 {{ themeLabel }}</span>
            <span class="vpc-chip">卡片 {{ config.cards.length }}</span>
            <span class="vpc-chip">启用 {{ enabledCards }}</span>
            <span class="vpc-chip">自动运行 {{ autoCards }}</span>
          </div>
        </div>

        <div class="vpc-hero-actions">
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存设置</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回面板</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vpc-panel">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">Plugin</div>
            <h2 class="vpc-section-title">插件级开关</h2>
          </div>
        </div>

        <div class="vpc-switch-grid">
          <label class="vpc-switch-card">
            <span>启用插件</span>
            <v-switch v-model="config.enabled" hide-details density="compact" color="primary" />
          </label>
          <label class="vpc-switch-card">
            <span>发送通知</span>
            <v-switch v-model="config.notify" hide-details density="compact" color="primary" />
          </label>
          <label class="vpc-switch-card">
            <span>保存后执行一次</span>
            <v-switch v-model="config.onlyonce" hide-details density="compact" color="primary" />
          </label>
          <label class="vpc-switch-card">
            <span>使用代理</span>
            <v-switch v-model="config.use_proxy" hide-details density="compact" color="primary" />
          </label>
          <label class="vpc-switch-card">
            <span>优先 IPv4</span>
            <v-switch v-model="config.force_ipv4" hide-details density="compact" color="primary" />
          </label>
        </div>

        <div class="vpc-form-grid">
          <v-text-field
            v-model="config.http_timeout"
            label="HTTP 超时（秒）"
            type="number"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
          />
          <v-text-field
            v-model="config.http_retry_times"
            label="HTTP 重试次数"
            type="number"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
          />
          <v-text-field
            v-model="config.random_delay_max_seconds"
            label="随机延迟上限（秒）"
            type="number"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
          />
        </div>
      </section>

      <section class="vpc-panel">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">Cards</div>
            <h2 class="vpc-section-title">功能卡片清单</h2>
          </div>
          <span class="vpc-note">复制与编辑入口已移动到主面板卡片内。</span>
        </div>

        <div class="vpc-card-list">
          <article v-for="card in config.cards" :key="card.id" class="vpc-card" :style="toneStyle(card.tone)">
            <div class="vpc-card-top">
              <div>
                <strong class="vpc-card-title">{{ card.title }}</strong>
                <p class="vpc-card-desc">{{ moduleSummary(card.module_key) }}</p>
              </div>
              <span class="vpc-status" :class="`is-${card.enabled ? 'enabled' : 'disabled'}`">
                {{ card.enabled ? '启用' : '停用' }}
              </span>
            </div>
            <div class="vpc-card-meta">
              <span>{{ card.site_name || '--' }}</span>
              <span>{{ card.site_url || '--' }}</span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const DEFAULT_CRON = '5 8 * * *'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive(createConfigState())
const moduleOptions = ref([])

const enabledCards = computed(() => config.cards.filter((item) => item.enabled).length)
const autoCards = computed(() => config.cards.filter((item) => item.enabled && item.auto_run).length)

function createConfigState() {
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
  return moduleOptions.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    summary: String(moduleKey || '').replaceAll('_', ' '),
    tone: 'azure',
  }
}

function moduleSummary(moduleKey) {
  return String(moduleMeta(moduleKey).summary || moduleKey).toLowerCase()
}

function normalizeCard(source = {}) {
  const meta = moduleMeta(source.module_key || 'siqi_sign')
  return {
    id: String(source.id || ''),
    title: String(source.title || meta.label || ''),
    module_key: meta.key,
    site_name: String(source.site_name || meta.default_site_name || ''),
    site_url: String(source.site_url || meta.default_site_url || ''),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON),
    tone: String(source.tone || meta.tone || 'azure'),
    cookie: String(source.cookie || ''),
    uid: String(source.uid || ''),
    note: String(source.note || ''),
  }
}

function normalizeConfig(source = {}) {
  Object.assign(config, createConfigState(), {
    enabled: !!source.enabled,
    notify: source.notify !== false,
    onlyonce: !!source.onlyonce,
    use_proxy: !!source.use_proxy,
    force_ipv4: source.force_ipv4 !== false,
    cron: String(source.cron || DEFAULT_CRON),
    http_timeout: Number(source.http_timeout || 15),
    http_retry_times: Number(source.http_retry_times || 3),
    random_delay_max_seconds: Number(source.random_delay_max_seconds || 5),
    cards: [],
  })
  config.cards.push(...(Array.isArray(source.cards) ? source.cards.map((item) => normalizeCard(item)) : []))
}

function serializeConfig() {
  return {
    enabled: !!config.enabled,
    notify: !!config.notify,
    onlyonce: !!config.onlyonce,
    use_proxy: !!config.use_proxy,
    force_ipv4: config.force_ipv4 !== false,
    cron: String(config.cron || DEFAULT_CRON),
    http_timeout: Number(config.http_timeout || 15),
    http_retry_times: Number(config.http_retry_times || 3),
    random_delay_max_seconds: Number(config.random_delay_max_seconds || 5),
    cards: config.cards.map((item) => normalizeCard(item)),
  }
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '38, 183, 120' },
    azure: { '--vpc-tone-rgb': '67, 126, 255' },
    amber: { '--vpc-tone-rgb': '255, 171, 67' },
    rose: { '--vpc-tone-rgb': '231, 92, 128' },
    violet: { '--vpc-tone-rgb': '150, 117, 255' },
    slate: { '--vpc-tone-rgb': '128, 140, 158' },
  }
  return map[tone] || map.azure
}

async function loadConfig() {
  try {
    const payload = await props.api.get('/plugin/VuePanel/config')
    moduleOptions.value = Array.isArray(payload.module_options) ? deepClone(payload.module_options) : []
    normalizeConfig(payload || {})
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const response = await props.api.post('/plugin/VuePanel/config', serializeConfig())
    flash(response.message || '设置已保存')
    await loadConfig()
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

function closePlugin() {
  emit('close')
}

onMounted(async () => {
  moduleOptions.value = Array.isArray(props.initialConfig?.module_options)
    ? deepClone(props.initialConfig.module_options)
    : []
  normalizeConfig(props.initialConfig || {})
  await loadConfig()
})
</script>

<style scoped>
.vuepanel-config {
  min-height: 100%;
  padding: 8px 0 20px;
  color: var(--mp-text-primary);
}

.vuepanel-config,
.vuepanel-config * {
  box-sizing: border-box;
}

.vpc-shell {
  display: grid;
  gap: 14px;
}

.vpc-hero,
.vpc-panel,
.vpc-card {
  border: 1px solid var(--mp-border-color);
  background: color-mix(in srgb, var(--mp-bg-panel) 92%, transparent);
  box-shadow: var(--mp-shadow-panel);
  backdrop-filter: blur(18px);
}

.vpc-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  border-radius: 28px;
}

.vpc-kicker {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--mp-text-secondary);
}

.vpc-title {
  margin: 10px 0 8px;
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.vpc-subtitle {
  max-width: 760px;
  margin: 0;
  color: var(--mp-text-secondary);
  font-size: 14px;
  line-height: 1.7;
}

.vpc-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.vpc-chip {
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--mp-border-color);
  background: color-mix(in srgb, var(--mp-bg-soft) 70%, transparent);
  color: var(--mp-text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.vpc-hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.vpc-panel {
  padding: 20px;
  border-radius: 24px;
}

.vpc-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.vpc-section-title {
  margin: 8px 0 0;
  font-size: 22px;
  letter-spacing: -0.03em;
}

.vpc-note {
  color: var(--mp-text-secondary);
  font-size: 12px;
}

.vpc-switch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.vpc-switch-card,
.vpc-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--mp-border-color);
  background: color-mix(in srgb, var(--mp-bg-card) 92%, transparent);
}

.vpc-form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.vpc-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.vpc-card {
  --vpc-tone-rgb: 67, 126, 255;
  flex-direction: column;
  align-items: stretch;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--mp-bg-card) 92%, rgba(var(--vpc-tone-rgb), 0.08)), var(--mp-bg-card)),
    linear-gradient(135deg, rgba(var(--vpc-tone-rgb), 0.08), transparent 50%);
}

.vpc-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.vpc-card-title {
  font-size: 16px;
  line-height: 1.3;
}

.vpc-card-desc,
.vpc-card-meta {
  margin: 6px 0 0;
  color: var(--mp-text-secondary);
  font-size: 12px;
  line-height: 1.7;
}

.vpc-card-desc {
  text-transform: lowercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.vpc-card-meta {
  display: grid;
  gap: 2px;
}

.vpc-status {
  padding: 6px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.vpc-status.is-enabled {
  color: #0f8a5a;
  background: rgba(34, 197, 94, 0.14);
}

.vpc-status.is-disabled {
  color: var(--mp-text-secondary);
  background: color-mix(in srgb, var(--mp-text-secondary) 12%, transparent);
}

@media (max-width: 920px) {
  .vpc-hero {
    flex-direction: column;
  }

  .vpc-hero-actions {
    justify-content: flex-start;
  }

  .vpc-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
