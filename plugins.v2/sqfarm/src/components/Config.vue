<template>
  <div ref="rootEl" class="sq-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="sq-shell">
      <section class="sq-hero">
        <div class="sq-hero-copy">
          <div class="sq-badge">SQ农场</div>
          <h1 class="sq-title">配置中心</h1>
          <p class="sq-subtitle">使用站点 Cookie、动态调度和 OCR 自动收菜，售出与种植都可以单独开关。</p>
        </div>
        <div class="sq-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="sq-grid">
        <article class="sq-panel">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">基础开关</div>
              <h2>运行控制</h2>
            </div>
          </div>
          <div class="sq-switch-grid">
            <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
            <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
            <v-switch v-model="config.onlyonce" label="保存后立即执行一次" color="warning" hide-details />
            <v-switch v-model="config.auto_cookie" label="优先使用站点 Cookie" color="info" hide-details />
            <v-switch v-model="config.enable_sell" label="自动售出" color="secondary" hide-details />
            <v-switch v-model="config.enable_plant" label="自动种植" color="secondary" hide-details />
            <v-switch v-model="config.use_proxy" label="使用系统代理" color="info" hide-details />
            <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
          </div>
        </article>

        <article class="sq-panel">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">种植与调度</div>
              <h2>策略配置</h2>
            </div>
          </div>
          <v-select
            v-model="config.prefer_seed"
            :items="seedOptions"
            label="优先种植"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            :menu-props="{ maxHeight: 280 }"
          />
          <div class="sq-note">优先显示当前已解锁种子；如果站点状态还没拉到，会先显示默认种子列表。</div>
          <div class="sq-note">插件不再固定轮询。启用或保存后会先获取一次农场信息，之后只在最近可收时间触发。</div>
          <v-text-field
            v-model="config.schedule_buffer_seconds"
            label="智能调度缓冲秒数"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mt-3"
          />
        </article>

        <article class="sq-panel">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">网络与 OCR</div>
              <h2>连接设置</h2>
            </div>
          </div>
          <v-text-field
            v-model="config.ocr_api_url"
            label="OCR API 地址"
            placeholder="http://ip:8089/api/tr-run/"
            hint="默认推荐 http://ip:8089/api/tr-run/，请把 ip 替换成 Docker 宿主机 IP。"
            persistent-hint
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="config.random_delay_max_seconds"
            label="随机延迟上限(秒)"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="config.http_timeout"
            label="HTTP 超时(秒)"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="config.http_retry_times"
            label="网络重试次数"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="config.http_retry_delay"
            label="网络重试间隔(ms)"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-text-field
            v-model="config.ocr_retry_times"
            label="OCR 重试次数"
            type="number"
            variant="outlined"
            density="comfortable"
          />
        </article>

        <article class="sq-panel">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">OCR 说明</div>
              <h2>trwebocr 容器</h2>
            </div>
          </div>
          <v-alert type="info" variant="tonal" class="mb-3">
            自动收菜验证码依赖 <code>trwebocr</code> 容器。未部署 OCR 时，插件仍可刷新状态，但自动收菜会失败。
          </v-alert>
          <div class="sq-note">推荐先部署 <code>trwebocr</code>，再把 OCR 地址填成 <code>http://ip:8089/api/tr-run/</code>。</div>
          <div class="sq-note">容器安装参考如下：</div>
          <pre class="sq-code">{{ ocrComposeExample }}</pre>
        </article>

        <article class="sq-panel sq-panel-wide">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">手动 Cookie</div>
              <h2>兜底配置</h2>
            </div>
          </div>
          <v-textarea
            v-model="config.cookie"
            label="SQ Cookie"
            rows="7"
            variant="outlined"
            density="comfortable"
            placeholder="例如 c_secure_pass=..."
          />
          <div class="sq-note">
            开启站点 Cookie 后，插件会优先读取 MoviePilot 站点管理中的 <code>si-qi.xyz</code> Cookie。
            这里仍可作为手动兜底。
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const message = reactive({ text: '', type: 'success' })
const seedOptions = ref(['西红柿'])
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_sell: true,
  enable_plant: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  ocr_retry_times: 2,
})

const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
    network_mode: bridge`

let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) {
      return current
    }
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme')) {
    return document.body
  }
  if (document.documentElement?.getAttribute('data-theme')) {
    return document.documentElement
  }
  return null
}

function detectTheme() {
  const themeNode = findThemeNode()
  const themeValue = themeNode?.getAttribute?.('data-theme') || ''
  const darkThemes = new Set(['dark', 'purple', 'transparent'])
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  isDarkTheme.value = darkThemes.has(themeValue) || (!themeValue && !!prefersDark)
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

function normalizeSeeds(items) {
  const normalized = (items || [])
    .map((item) => (typeof item === 'string' ? item : item?.value || item?.name || ''))
    .filter(Boolean)

  if (config.prefer_seed && !normalized.includes(config.prefer_seed)) {
    normalized.unshift(config.prefer_seed)
  }

  return normalized.length ? normalized : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function applySeedOptions(items) {
  seedOptions.value = normalizeSeeds(items)
}

function applyStatusSeedOptions(seedShop) {
  const unlocked = (seedShop || [])
    .filter((seed) => seed.unlocked && seed.name)
    .map((seed) => seed.name)
  if (unlocked.length) {
    applySeedOptions(unlocked)
  }
}

async function loadStatusSeedOptions() {
  try {
    const res = await props.api.get('/plugin/SQFarm/status')
    applyStatusSeedOptions(res?.farm_status?.seed_shop)
  } catch (error) {
    // 保留当前种子选项
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/SQFarm/config')
    Object.assign(config, res || {})
    applySeedOptions(res?.seed_options)
    await loadStatusSeedOptions()
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/config', { ...config })
    if (res.config) {
      Object.assign(config, res.config)
      applySeedOptions(res.config.seed_options)
    }
    flash(res.message || '配置已保存')
    if (config.onlyonce) {
      config.onlyonce = false
    }
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  saving.value = true
  try {
    const res = await props.api.get('/plugin/SQFarm/cookie')
    if (res.config) {
      Object.assign(config, res.config)
      applySeedOptions(res.config.seed_options)
    }
    await loadStatusSeedOptions()
    flash(res.message || 'Cookie 已同步')
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    saving.value = false
  }
}

function closePlugin() {
  emit('close')
}

onMounted(() => {
  detectTheme()
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)')
  mediaQuery?.addEventListener?.('change', detectTheme)
  bindThemeObserver()

  loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.sq-config {
  --sq-bg: linear-gradient(180deg, #f5efe4 0%, #fbf8f2 45%, #f7f4ee 100%);
  --sq-surface: rgba(255, 255, 255, 0.82);
  --sq-surface-strong: rgba(255, 252, 246, 0.96);
  --sq-border: rgba(169, 138, 81, 0.18);
  --sq-shadow: 0 20px 45px rgba(97, 75, 34, 0.08);
  --sq-text: #2f281d;
  --sq-subtle: #726754;
  --sq-soft: #8e846f;
  --sq-accent: #77b05d;
  --sq-accent-strong: #4f8d3a;
  --sq-accent-soft: rgba(119, 176, 93, 0.14);
  min-height: 100%;
  padding: clamp(18px, 2.6vw, 30px);
  background: var(--sq-bg);
  color: var(--sq-text);
}

.sq-config.is-dark-theme {
  --sq-bg: linear-gradient(180deg, #141818 0%, #101413 48%, #0c100f 100%);
  --sq-surface: rgba(24, 30, 29, 0.88);
  --sq-surface-strong: rgba(28, 35, 33, 0.95);
  --sq-border: rgba(133, 157, 123, 0.18);
  --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
  --sq-text: #edf3ea;
  --sq-subtle: #b9c4b4;
  --sq-soft: #8f9d91;
  --sq-accent: #9dd37b;
  --sq-accent-strong: #d1f0c2;
  --sq-accent-soft: rgba(119, 176, 93, 0.18);
}

.sq-shell {
  max-width: 1320px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sq-hero,
.sq-panel {
  border: 1px solid var(--sq-border);
  box-shadow: var(--sq-shadow);
}

.sq-hero {
  padding: clamp(22px, 3vw, 34px);
  border-radius: 30px;
  background:
    radial-gradient(circle at top right, rgba(136, 202, 115, 0.2), transparent 32%),
    radial-gradient(circle at bottom left, rgba(255, 208, 119, 0.18), transparent 28%),
    var(--sq-surface-strong);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px 24px;
  align-items: start;
}

.sq-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--sq-accent-soft);
  color: var(--sq-accent-strong);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.sq-title {
  margin: 14px 0 8px;
  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.05;
  font-weight: 900;
}

.sq-subtitle {
  margin: 0;
  max-width: 680px;
  color: var(--sq-subtle);
  line-height: 1.7;
  font-size: 14px;
}

.sq-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.sq-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.sq-panel {
  border-radius: 28px;
  padding: 22px;
  background: var(--sq-surface);
  backdrop-filter: blur(10px);
}

.sq-panel-wide {
  grid-column: 1 / -1;
}

.sq-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.sq-panel-kicker {
  color: var(--sq-soft);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sq-panel-head h2 {
  margin: 6px 0 0;
  font-size: 24px;
  line-height: 1.1;
  font-weight: 800;
}

.sq-switch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 8px 20px;
}

.sq-note {
  margin-top: 12px;
  color: var(--sq-subtle);
  font-size: 13px;
  line-height: 1.75;
}

.sq-code {
  margin-top: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(244, 236, 220, 0.9);
  border: 1px solid rgba(169, 138, 81, 0.16);
  color: var(--sq-text);
  font-size: 13px;
  line-height: 1.65;
  overflow-x: auto;
}

.sq-config.is-dark-theme .sq-code {
  background: rgba(34, 40, 39, 0.92);
}

@media (max-width: 960px) {
  .sq-hero,
  .sq-grid {
    grid-template-columns: 1fr;
  }

  .sq-actions {
    justify-content: flex-start;
  }
}

@media (prefers-color-scheme: dark) {
  .sq-config {
    --sq-bg: linear-gradient(180deg, #141818 0%, #101413 48%, #0c100f 100%);
    --sq-surface: rgba(24, 30, 29, 0.88);
    --sq-surface-strong: rgba(28, 35, 33, 0.95);
    --sq-border: rgba(133, 157, 123, 0.18);
    --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
    --sq-text: #edf3ea;
    --sq-subtle: #b9c4b4;
    --sq-soft: #8f9d91;
    --sq-accent: #9dd37b;
    --sq-accent-strong: #d1f0c2;
    --sq-accent-soft: rgba(119, 176, 93, 0.18);
  }

  .sq-code {
    background: rgba(34, 40, 39, 0.92);
  }
}

[data-theme="dark"] .sq-config,
[data-theme="purple"] .sq-config,
[data-theme="transparent"] .sq-config {
  --sq-bg: linear-gradient(180deg, #141818 0%, #101413 48%, #0c100f 100%);
  --sq-surface: rgba(24, 30, 29, 0.88);
  --sq-surface-strong: rgba(28, 35, 33, 0.95);
  --sq-border: rgba(133, 157, 123, 0.18);
  --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
  --sq-text: #edf3ea;
  --sq-subtle: #b9c4b4;
  --sq-soft: #8f9d91;
  --sq-accent: #9dd37b;
  --sq-accent-strong: #d1f0c2;
  --sq-accent-soft: rgba(119, 176, 93, 0.18);
}

[data-theme="dark"] .sq-code,
[data-theme="purple"] .sq-code,
[data-theme="transparent"] .sq-code {
  background: rgba(34, 40, 39, 0.92);
}
</style>
