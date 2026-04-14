<template>
  <div class="config-page">
    <BasePanelCard
      kicker="Vue-面板"
      title="模块化配置后台"
      :subtitle="`当前主题：${themeLabel}。模块默认按固定单卡管理，只有明确声明的功能才会开放站点子卡。`"
      tone="primary"
      class="config-hero"
    >
      <template #actions>
        <div class="hero-actions">
          <BaseButton :loading="saving" @click="saveConfig">保存</BaseButton>
          <BaseButton variant="secondary" @click="emit('switch', 'page')">运行看板</BaseButton>
          <BaseButton variant="ghost" @click="closePlugin">关闭</BaseButton>
        </div>
      </template>

      <div class="hero-chips">
        <BaseTag tone="primary">主题 {{ themeLabel }}</BaseTag>
        <BaseTag tone="success">固定模块 {{ singletonModules.length }}</BaseTag>
        <BaseTag tone="info">多站点模块 {{ collectionModules.length }}</BaseTag>
        <BaseTag tone="warning">定时卡 {{ scheduledCards.length }}</BaseTag>
      </div>
    </BasePanelCard>

    <v-alert v-if="message.text" :type="message.type" variant="tonal" rounded="xl">{{ message.text }}</v-alert>

    <BasePanelCard
      kicker="插件级设置"
      title="全局选项"
      subtitle="这里只保留插件级开关，不把单卡 Cron、Cookie 和站点字段混进全局层。"
      tone="azure"
      compact
    >
      <div class="global-grid">
        <div class="switch-tile">
          <BaseSwitch v-model="config.enabled" label="启用插件" hint="关闭后所有卡片都不会自动执行。" />
        </div>
        <div class="switch-tile">
          <BaseSwitch v-model="config.notify" label="开启通知" hint="执行结果会写入状态页通知区。" />
        </div>
        <div class="switch-tile">
          <BaseSwitch v-model="config.onlyonce" label="保存后执行一次" hint="用于快速校验配置是否可用。" />
        </div>
        <div class="switch-tile">
          <BaseSwitch v-model="config.use_proxy" label="使用代理" hint="请求跟随宿主代理设置。" />
        </div>
        <div class="switch-tile">
          <BaseSwitch v-model="config.force_ipv4" label="优先 IPv4" hint="保留原有网络访问偏好。" />
        </div>
      </div>
    </BasePanelCard>

    <section class="module-stack">
      <BasePanelCard
        v-for="module in singletonModules"
        :key="module.key"
        kicker="固定模块"
        :title="`${module.icon} ${module.label}`"
        :subtitle="module.description"
        :tone="module.tone"
        compact
      >
        <article class="task-editor fixed" :style="toneStyle(ensureFixedCard(module.key).tone || module.tone)">
          <div class="task-head">
            <div>
              <div class="task-kicker">{{ module.label }}</div>
              <div class="task-title">{{ ensureFixedCard(module.key).title }}</div>
              <div class="task-subtitle">{{ ensureFixedCard(module.key).site_url }}</div>
            </div>
            <BaseTag :tone="ensureFixedCard(module.key).enabled ? 'success' : 'disabled'" size="sm">
              {{ ensureFixedCard(module.key).enabled ? '已启用' : '已停用' }}
            </BaseTag>
          </div>

          <div class="task-switch-row">
            <div class="switch-tile compact">
              <BaseSwitch v-model="ensureFixedCard(module.key).enabled" label="启用" />
            </div>
            <div class="switch-tile compact">
              <BaseSwitch v-model="ensureFixedCard(module.key).auto_run" label="定时运行" />
            </div>
          </div>

          <div class="task-field-grid fixed-grid">
            <div class="field-block">
              <BaseCronField v-model="ensureFixedCard(module.key).cron" label="定时运行 Cron" />
            </div>
            <div class="field-block field-span-2">
              <BaseTextarea
                v-model="ensureFixedCard(module.key).cookie"
                label="站点 Cookie"
                placeholder="例如 c_secure_pass=..."
              />
              <div class="field-note">{{ fixedCookieNote(module.key) }}</div>
            </div>
          </div>
        </article>
      </BasePanelCard>

      <BasePanelCard
        v-for="module in collectionModules"
        :key="module.key"
        kicker="多站点模块"
        :title="`${module.icon} ${module.label}`"
        :subtitle="`${module.description} 只有这类显式多站点模块才支持在模块内继续新增站点卡。`"
        :tone="module.tone"
        compact
      >
        <template #actions>
          <BaseButton variant="secondary" @click="addCollectionCard(module.key)">新增站点</BaseButton>
        </template>

        <EmptyState
          v-if="!cardsForModule(module.key).length"
          title="暂无站点卡片"
          description="点击右上角新增站点，把不同网站和 Cookie 独立管理。"
        />

        <div v-else class="site-grid">
          <article
            v-for="(card, index) in cardsForModule(module.key)"
            :key="card.id"
            class="task-editor"
            :style="toneStyle(card.tone || module.tone)"
          >
            <div class="task-head">
              <div>
                <div class="task-kicker">站点 {{ index + 1 }}</div>
                <div class="task-title">{{ card.site_name || `${module.label} 站点 ${index + 1}` }}</div>
                <div class="task-subtitle">{{ card.site_url || '未填写站点地址' }}</div>
              </div>
              <div class="task-head-actions">
                <BaseTag :tone="card.enabled ? 'success' : 'disabled'" size="sm">{{ card.enabled ? '已启用' : '已停用' }}</BaseTag>
                <BaseButton variant="ghost" size="sm" @click="removeCollectionCard(module.key, card.id)">删除</BaseButton>
              </div>
            </div>

            <div class="task-switch-row">
              <div class="switch-tile compact">
                <BaseSwitch v-model="card.enabled" label="启用" />
              </div>
              <div class="switch-tile compact">
                <BaseSwitch v-model="card.auto_run" label="定时运行" />
              </div>
            </div>

            <div class="task-field-grid collection-grid">
              <div class="field-block">
                <BaseInput v-model="card.site_name" label="网站名称" placeholder="例如 Open 站点" />
              </div>
              <div class="field-block">
                <BaseInput v-model="card.site_url" label="网站地址" placeholder="https://example.com" />
              </div>
              <div class="field-block" v-if="showUidField(module.key)">
                <BaseInput v-model="card.uid" label="UID" placeholder="例如 225" />
              </div>
              <div class="field-block" :class="{ 'field-span-2': !showUidField(module.key) }">
                <BaseCronField v-model="card.cron" label="定时运行 Cron" />
              </div>
              <div class="field-block field-span-3">
                <BaseTextarea v-model="card.cookie" label="站点 Cookie" placeholder="每个站点使用各自 Cookie" />
              </div>
            </div>
          </article>
        </div>
      </BasePanelCard>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import BaseButton from './ui/BaseButton.vue'
import BaseCronField from './ui/BaseCronField.vue'
import BaseInput from './ui/BaseInput.vue'
import BasePanelCard from './ui/BasePanelCard.vue'
import BaseSwitch from './ui/BaseSwitch.vue'
import BaseTag from './ui/BaseTag.vue'
import BaseTextarea from './ui/BaseTextarea.vue'
import EmptyState from './ui/EmptyState.vue'

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
    description: '',
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
    emerald: { '--task-tone': '31, 168, 104' },
    azure: { '--task-tone': '79, 134, 255' },
    amber: { '--task-tone': '229, 155, 47' },
    rose: { '--task-tone': '220, 87, 87' },
    violet: { '--task-tone': '139, 92, 246' },
    slate: { '--task-tone': '120, 132, 155' },
  }
  return map[tone] || map.azure
}

function fixedCookieNote(moduleKey) {
  return moduleKey === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后即可执行。'
}

function showUidField(moduleKey) {
  return moduleKey === 'newapi_checkin'
}

function cardsForModule(moduleKey) {
  return config.cards.filter((card) => card.module_key === moduleKey)
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey)
  return {
    id: moduleKey,
    title: meta.label,
    module_key: moduleKey,
    site_name: meta.default_site_name || meta.label,
    site_url: meta.default_site_url || '',
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
.config-page {
  display: grid;
  gap: 10px;
  padding-inline: 2px;
}

.config-hero {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--mp-color-primary) 12%, transparent) 0%, transparent 44%),
    var(--mp-bg-panel);
}

.hero-actions,
.hero-chips,
.task-head,
.task-head-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-actions {
  justify-content: flex-end;
}

.global-grid,
.task-switch-row,
.task-field-grid,
.site-grid,
.module-stack {
  display: grid;
  gap: 10px;
}

.global-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.module-stack {
  gap: 10px;
}

.site-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.task-editor {
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

.task-editor.fixed {
  min-height: 100%;
}

.task-head {
  justify-content: space-between;
  align-items: flex-start;
}

.task-kicker {
  font-size: var(--mp-font-xs);
  font-weight: 800;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: color-mix(in srgb, rgb(var(--task-tone)) 78%, var(--mp-text-primary));
}

.task-title {
  margin-top: 2px;
  font-size: var(--mp-font-lg);
  font-weight: 900;
  color: var(--mp-text-primary);
}

.task-subtitle,
.field-note {
  font-size: var(--mp-font-sm);
  line-height: 1.55;
  color: var(--mp-text-secondary);
}

.task-switch-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.task-field-grid.fixed-grid {
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr) minmax(0, 1.1fr);
}

.task-field-grid.collection-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.field-block {
  display: grid;
  gap: 6px;
}

.field-span-2 {
  grid-column: span 2;
}

.field-span-3 {
  grid-column: span 3;
}

.switch-tile {
  padding: 10px 11px;
  border: 1px solid var(--mp-border-color);
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-card) 92%, transparent);
}

.switch-tile.compact {
  padding: 8px 10px;
}

@media (max-width: 1180px) {
  .global-grid,
  .site-grid,
  .task-field-grid.fixed-grid,
  .task-field-grid.collection-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .field-span-3 {
    grid-column: span 2;
  }
}

@media (max-width: 760px) {
  .config-page {
    padding-inline: 0;
  }

  .hero-actions,
  .hero-chips,
  .task-head,
  .task-head-actions {
    justify-content: flex-start;
  }

  .global-grid,
  .task-switch-row,
  .site-grid,
  .task-field-grid.fixed-grid,
  .task-field-grid.collection-grid {
    grid-template-columns: 1fr;
  }

  .field-span-2,
  .field-span-3 {
    grid-column: auto;
  }
}
</style>
