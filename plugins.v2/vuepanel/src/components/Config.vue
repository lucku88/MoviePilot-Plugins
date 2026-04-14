<template>
  <div class="vuepanel-config">
    <div class="vpc-shell">
      <header class="vpc-card vpc-hero">
        <div class="vpc-copy">
          <div class="vpc-badge">Vue-面板</div>
          <h1 class="vpc-title">配置页</h1>
          <div class="vpc-chip-row">
            <span class="vpc-chip">主题 {{ themeLabel }}</span>
            <span class="vpc-chip">固定任务 {{ fixedCards.length }} 个</span>
            <span class="vpc-chip" v-if="collectionModules.length">多站点模块 {{ collectionModules.length }} 个</span>
            <span class="vpc-chip">定时卡片 {{ scheduledCards.length }}</span>
          </div>
        </div>
        <div class="vpc-action-grid">
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </header>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

      <section class="vpc-card">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">插件级设置</div>
            <h2 class="vpc-section-title">全局选项</h2>
          </div>
        </div>

        <div class="vpc-switch-grid plugin">
          <div class="vpc-switch-card">
            <v-switch v-model="config.enabled" class="vpc-switch" label="启用插件" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.notify" class="vpc-switch" label="开启通知" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.onlyonce" class="vpc-switch" label="保存后执行一次" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.use_proxy" class="vpc-switch" label="使用代理" density="compact" hide-details inset />
          </div>
          <div class="vpc-switch-card">
            <v-switch v-model="config.force_ipv4" class="vpc-switch" label="优先 IPv4" density="compact" hide-details inset />
          </div>
        </div>
      </section>

      <section class="vpc-card" v-if="fixedCards.length">
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">固定模块</div>
            <h2 class="vpc-section-title">固定功能卡片</h2>
          </div>
          <div class="vpc-note">模块默认都是固定单卡，只有你明确说明为多站点模块时，才会开放新增站点。</div>
        </div>

        <div class="vpc-fixed-grid">
          <article
            v-for="card in fixedCards"
            :key="card.id"
            class="vpc-editor fixed"
            :style="toneStyle(card.tone)"
          >
            <div class="vpc-editor-head">
              <div>
                <div class="vpc-kicker">{{ moduleMeta(card.module_key).label }}</div>
                <h3 class="vpc-editor-title">{{ card.title }}</h3>
              </div>
              <span class="vpc-editor-site">{{ card.site_url }}</span>
            </div>

            <div class="vpc-switch-grid compact">
              <div class="vpc-switch-card">
                <v-switch v-model="card.enabled" class="vpc-switch" label="启用" density="compact" hide-details inset />
              </div>
              <div class="vpc-switch-card">
                <v-switch v-model="card.auto_run" class="vpc-switch" label="定时运行" density="compact" hide-details inset />
              </div>
            </div>

            <div class="vpc-field-stack">
              <div class="vpc-field-card">
                <VCronField
                  v-model="card.cron"
                  label="定时运行 Cron"
                  density="comfortable"
                  class="vpc-cron-field"
                />
              </div>

              <div class="vpc-field-card">
                <v-text-field
                  v-model="card.cookie"
                  label="站点 Cookie"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                />
                <div class="vpc-note">{{ fixedCookieNote(card.module_key) }}</div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section
        v-for="module in collectionModules"
        :key="module.key"
        class="vpc-card"
      >
        <div class="vpc-section-head">
          <div>
            <div class="vpc-kicker">多站点模块</div>
            <h2 class="vpc-section-title">{{ module.icon }} {{ module.label }}</h2>
          </div>
          <div class="vpc-toolbar-actions">
            <v-btn color="info" variant="flat" @click="addCollectionCard(module.key)">新增站点</v-btn>
          </div>
        </div>

        <div class="vpc-note">{{ module.description }} 只有这类显式多站点模块才支持新增站点卡。</div>

        <div v-if="!cardsForModule(module.key).length" class="vpc-empty">当前没有站点卡片，点击“新增站点”创建。</div>

        <div v-else class="vpc-site-grid">
          <article
            v-for="(card, index) in cardsForModule(module.key)"
            :key="card.id"
            class="vpc-editor"
            :style="toneStyle(card.tone || module.tone)"
          >
            <div class="vpc-editor-head">
              <div>
                <div class="vpc-kicker">站点 {{ index + 1 }}</div>
                <h3 class="vpc-editor-title">{{ card.site_name || `${module.label} 站点 ${index + 1}` }}</h3>
              </div>
              <div class="vpc-inline-actions">
                <v-btn size="small" variant="text" color="error" @click="removeCollectionCard(module.key, card.id)">删除</v-btn>
              </div>
            </div>

            <div class="vpc-switch-grid compact">
              <div class="vpc-switch-card">
                <v-switch v-model="card.enabled" class="vpc-switch" label="启用" density="compact" hide-details inset />
              </div>
              <div class="vpc-switch-card">
                <v-switch v-model="card.auto_run" class="vpc-switch" label="定时运行" density="compact" hide-details inset />
              </div>
            </div>

            <div class="vpc-field-grid collection" :class="{ 'with-uid': showUidField(module.key) }">
              <v-text-field v-model="card.site_name" label="网站名称" variant="outlined" density="comfortable" hide-details="auto" />
              <v-text-field v-model="card.site_url" label="网站地址" variant="outlined" density="comfortable" hide-details="auto" />
              <v-text-field
                v-if="showUidField(module.key)"
                v-model="card.uid"
                label="UID"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
              />
            </div>

            <div class="vpc-field-stack">
              <div class="vpc-field-card">
                <VCronField
                  v-model="card.cron"
                  label="定时运行 Cron"
                  density="comfortable"
                  class="vpc-cron-field"
                />
              </div>

              <div class="vpc-field-card">
                <v-text-field
                  v-model="card.cookie"
                  label="站点 Cookie"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                />
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const DEFAULT_CARD_CRON = '5 8 * * *'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const message = reactive({ text: '', type: 'success' })
const moduleItems = ref([])
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: DEFAULT_CARD_CRON,
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
})

const singletonModules = computed(() => moduleItems.value.filter((item) => item.singleton !== false))
const collectionModules = computed(() => moduleItems.value.filter((item) => item.singleton === false))
const fixedCards = computed(() => singletonModules.value.map((module) => ensureFixedCard(module.key)))
const scheduledCards = computed(() => config.cards.filter((card) => card.enabled && card.auto_run))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function moduleMeta(moduleKey) {
  return moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '🧩',
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
    singleton: true,
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '40,181,120' },
    azure: { '--vpc-tone-rgb': '46,134,255' },
    amber: { '--vpc-tone-rgb': '255,170,63' },
    rose: { '--vpc-tone-rgb': '230,92,124' },
    violet: { '--vpc-tone-rgb': '132,108,255' },
    slate: { '--vpc-tone-rgb': '120,132,155' },
  }
  return map[tone] || map.azure
}

function fixedCookieNote(moduleKey) {
  return moduleKey === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后可执行。'
}

function showUidField(moduleKey) {
  return moduleKey === 'newapi_checkin'
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey)
  return {
    id: moduleKey,
    title: current.title || meta.label,
    module_key: moduleKey,
    site_name: current.site_name || meta.default_site_name || meta.label,
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: '',
    note: String(current.note || ''),
  }
}

function buildCollectionCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey)
  return {
    id: current.id || nextCardId(moduleKey),
    title: current.title || current.site_name || meta.label,
    module_key: moduleKey,
    site_name: current.site_name || meta.default_site_name || '',
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: showUidField(moduleKey) ? String(current.uid || '225') : '',
    note: String(current.note || ''),
  }
}

function ensureStructure(cards = []) {
  const fixedMap = new Map()
  const collectionMap = new Map()

  for (const module of collectionModules.value) collectionMap.set(module.key, [])

  for (const item of cards) {
    if (!item || typeof item !== 'object') continue
    const moduleKey = String(item.module_key || '')
    if (singletonModules.value.some((module) => module.key === moduleKey)) {
      if (!fixedMap.has(moduleKey)) fixedMap.set(moduleKey, buildFixedCard(moduleKey, item))
      continue
    }
    if (collectionMap.has(moduleKey)) collectionMap.get(moduleKey).push(buildCollectionCard(moduleKey, item))
  }

  const normalized = [
    ...singletonModules.value.map((module) => fixedMap.get(module.key) || buildFixedCard(module.key)),
    ...collectionModules.value.flatMap((module) => {
      const items = collectionMap.get(module.key) || []
      return items.length ? items : [buildCollectionCard(module.key)]
    }),
  ]

  config.cards.splice(0, config.cards.length, ...normalized)
}

function ensureFixedCard(moduleKey) {
  let card = config.cards.find((item) => item.module_key === moduleKey)
  if (!card) {
    card = buildFixedCard(moduleKey)
    config.cards.push(card)
  }
  return card
}

function cardsForModule(moduleKey) {
  return config.cards.filter((card) => card.module_key === moduleKey)
}

function addCollectionCard(moduleKey) {
  config.cards.push(buildCollectionCard(moduleKey))
}

function removeCollectionCard(moduleKey, cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId && card.module_key === moduleKey)
  if (index >= 0) config.cards.splice(index, 1)
  if (!cardsForModule(moduleKey).length) addCollectionCard(moduleKey)
}

function serializeConfig() {
  const cards = [
    ...singletonModules.value.map((module) => buildFixedCard(module.key, ensureFixedCard(module.key))),
    ...collectionModules.value.flatMap((module) =>
      cardsForModule(module.key).map((card) =>
        buildCollectionCard(module.key, {
          ...card,
          title: String(card.site_name || card.title || module.label).trim() || module.label,
        }),
      ),
    ),
  ]

  return {
    ...deepClone(config),
    cards,
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config')
    moduleItems.value = res.module_options || []
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || DEFAULT_CARD_CRON,
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: [],
    })
    ensureStructure(deepClone(res.cards || []))
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await props.api.post('/plugin/VuePanel/config', serializeConfig())
    flash(res.message || '配置已保存')
    await loadConfig()
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

function closePlugin() {
  emit('close')
}

onMounted(async () => {
  await loadConfig()
})
</script>

<style scoped>
.vuepanel-config {
  --vpc-panel: color-mix(in srgb, var(--mp-bg-panel) 96%, transparent);
  --vpc-panel-strong: color-mix(in srgb, var(--mp-bg-card) 96%, transparent);
  --vpc-text: var(--mp-text-primary);
  --vpc-muted: var(--mp-text-secondary);
  --vpc-border: var(--mp-border-color);
  --vpc-border-strong: var(--mp-border-strong);
  --vpc-shadow: var(--mp-shadow-card);
  --vpc-accent: var(--mp-color-primary);
  --vpc-accent-soft: color-mix(in srgb, var(--mp-color-primary) 12%, transparent);
  min-height: 100%;
  padding: 8px 0 18px;
  color: var(--vpc-text);
}

.vuepanel-config,
.vuepanel-config * {
  box-sizing: border-box;
}

.vpc-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 12px;
  display: grid;
  gap: 10px;
}

.vpc-card,
.vpc-editor,
.vpc-switch-card,
.vpc-field-card {
  border: 1px solid var(--vpc-border);
  border-radius: 18px;
  background: var(--vpc-panel);
  box-shadow: var(--vpc-shadow);
  backdrop-filter: blur(16px);
}

.vpc-card {
  padding: 12px;
}

.vpc-hero,
.vpc-chip-row,
.vpc-action-grid,
.vpc-section-head,
.vpc-editor-head,
.vpc-inline-actions,
.vpc-toolbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.vpc-hero {
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, var(--vpc-accent-soft) 0%, transparent 42%), var(--vpc-panel);
}

.vpc-copy {
  flex: 1;
  min-width: 0;
}

.vpc-badge,
.vpc-chip,
.vpc-editor-site {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}

.vpc-badge {
  padding: 5px 10px;
  background: var(--vpc-accent-soft);
  color: var(--vpc-accent);
  font-size: 11px;
  font-weight: 700;
}

.vpc-title,
.vpc-section-title,
.vpc-editor-title {
  margin: 0;
  font-weight: 900;
  letter-spacing: -.02em;
}

.vpc-title {
  margin-top: 8px;
  font-size: clamp(22px, 3.8vw, 30px);
  line-height: 1.05;
}

.vpc-section-title {
  font-size: 17px;
}

.vpc-editor-title {
  font-size: 17px;
  line-height: 1.12;
}

.vpc-chip-row {
  margin-top: 10px;
}

.vpc-chip {
  padding: 6px 10px;
  border: 1px solid var(--vpc-border-strong);
  background: var(--vpc-panel-strong);
  font-size: 11px;
  font-weight: 700;
}

.vpc-action-grid {
  justify-content: flex-end;
  min-width: min(100%, 420px);
}

.vpc-action-grid :deep(.v-btn),
.vpc-toolbar-actions :deep(.v-btn),
.vpc-inline-actions :deep(.v-btn) {
  min-height: 38px;
  border-radius: 12px;
  font-weight: 800;
  text-transform: none;
}

.vpc-kicker,
.vpc-note,
.vpc-editor-site {
  color: var(--vpc-muted);
}

.vpc-kicker {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--vpc-accent);
}

.vpc-note {
  font-size: 11px;
  line-height: 1.65;
}

.vpc-section-head,
.vpc-editor-head {
  justify-content: space-between;
  align-items: flex-start;
}

.vpc-switch-grid,
.vpc-field-grid,
.vpc-fixed-grid,
.vpc-site-grid,
.vpc-field-stack {
  display: grid;
  gap: 10px;
}

.vpc-switch-grid.plugin {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.vpc-switch-grid.compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpc-switch-card {
  padding: 10px 12px;
  background: var(--vpc-panel-strong);
}

.vpc-fixed-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpc-site-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpc-editor {
  position: relative;
  overflow: hidden;
  padding: 12px;
  display: grid;
  gap: 10px;
  background: linear-gradient(180deg, rgba(var(--vpc-tone-rgb, 46, 134, 255), .12), transparent 62%), var(--vpc-panel-strong);
}

.vpc-editor::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 4px;
  background: rgba(var(--vpc-tone-rgb, 46, 134, 255), .48);
}

.vpc-editor-site {
  padding: 4px 9px;
  background: rgba(var(--vpc-tone-rgb, 46, 134, 255), .1);
  font-size: 11px;
  font-weight: 700;
  justify-content: flex-start;
}

.vpc-field-grid.collection {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.vpc-field-grid.collection.with-uid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.vpc-field-card {
  padding: 12px;
  background: linear-gradient(180deg, rgba(var(--vpc-tone-rgb, 46, 134, 255), .06), transparent 100%), var(--vpc-panel-strong);
}

.vpc-empty {
  padding: 18px 16px;
  text-align: center;
  border: 1px dashed var(--vpc-border);
  border-radius: 16px;
  background: var(--vpc-panel-strong);
  color: var(--vpc-muted);
}

:deep(.vuepanel-config .v-field),
:deep(.vuepanel-config .v-selection-control) {
  color: var(--vpc-text);
}

:deep(.vuepanel-config .v-field) {
  background: var(--mp-bg-input);
  border-radius: 14px;
}

:deep(.vuepanel-config .v-field__input),
:deep(.vuepanel-config .v-label),
:deep(.vuepanel-config .v-select__selection-text),
:deep(.vuepanel-config .v-field__outline),
:deep(.vuepanel-config .v-field__append-inner) {
  color: var(--vpc-text);
}

:deep(.vuepanel-config .vpc-switch) {
  width: 100%;
  margin: 0;
}

:deep(.vuepanel-config .vpc-switch .v-selection-control) {
  min-height: 28px;
}

:deep(.vuepanel-config .vpc-switch .v-label) {
  opacity: 1;
  font-weight: 600;
  font-size: 12px;
  line-height: 1.35;
}

:deep(.vuepanel-config .vpc-switch .v-selection-control__wrapper) {
  width: 30px;
  height: 18px;
  margin-right: 6px;
}

:deep(.vuepanel-config .vpc-switch .v-switch__track) {
  min-width: 30px;
  width: 30px;
  height: 18px;
  border-radius: 999px;
}

:deep(.vuepanel-config .vpc-switch .v-switch__thumb) {
  width: 12px;
  height: 12px;
}

:deep(.vuepanel-config .v-field__input) {
  min-height: 40px;
  padding-top: 0;
  padding-bottom: 0;
  font-size: 13px;
}

:deep(.vuepanel-config .v-field__outline) {
  --v-field-border-opacity: 1;
}

:deep(.vuepanel-config .v-selection-control__input > .v-icon),
:deep(.vuepanel-config .v-switch__track) {
  color: var(--vpc-accent);
}

:deep(.vuepanel-config .vpc-cron-field) {
  padding: 0;
  background: transparent;
}

@media (max-width: 1080px) {
  .vpc-switch-grid.plugin,
  .vpc-fixed-grid,
  .vpc-site-grid,
  .vpc-field-grid.collection,
  .vpc-field-grid.collection.with-uid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .vpc-action-grid {
    justify-content: flex-start;
    min-width: 0;
  }
}

@media (max-width: 760px) {
  .vpc-shell {
    padding: 0 10px;
  }

  .vpc-card,
  .vpc-editor,
  .vpc-switch-card,
  .vpc-field-card {
    border-radius: 16px;
  }

  .vpc-card,
  .vpc-editor {
    padding: 12px;
  }

  .vpc-hero,
  .vpc-section-head,
  .vpc-editor-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .vpc-switch-grid.plugin,
  .vpc-switch-grid.compact,
  .vpc-fixed-grid,
  .vpc-site-grid,
  .vpc-field-grid.collection,
  .vpc-field-grid.collection.with-uid {
    grid-template-columns: 1fr;
  }
}
</style>
