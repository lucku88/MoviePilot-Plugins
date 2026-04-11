<template>
  <div class="sqfarm-config-page">
    <div class="sqfarm-config-shell">
      <v-card class="sqfarm-config-card" rounded="xl" flat>
        <v-card-text class="sqfarm-config-hero">
          <div class="sqfarm-config-copy">
            <div class="sqfarm-config-badge">Vue-农场</div>
            <h1 class="sqfarm-config-title">插件配置</h1>
            <p class="sqfarm-config-subtitle">收菜、种植、出售、获取执行记录。</p>
          </div>
          <div class="sqfarm-config-actions">
            <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
            <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
            <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
            <v-btn variant="text" @click="closePlugin">关闭</v-btn>
          </div>
        </v-card-text>
      </v-card>

      <v-alert
        v-if="message.text"
        :type="message.type"
        variant="tonal"
        rounded="xl"
      >
        {{ message.text }}
      </v-alert>

      <v-card class="sqfarm-config-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-config-kicker">基本设置</div>
          </template>
          <v-card-title>基础开关</v-card-title>
        </v-card-item>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6" xl="3">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.enabled" label="启用插件" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
            <v-col cols="12" md="6" xl="3">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.use_proxy" label="使用代理" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
            <v-col cols="12" md="6" xl="3">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.notify" label="开启通知" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
            <v-col cols="12" md="6" xl="3">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.onlyonce" label="立即运行一次" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-config-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-config-kicker">功能设置</div>
          </template>
          <v-card-title>农场流程</v-card-title>
        </v-card-item>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.auto_cookie" label="使用站点 Cookie" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.enable_sell" label="自动出售" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="sqfarm-switch-card">
                <v-switch v-model="config.enable_plant" label="自动种植" color="#7c5cff" density="compact" hide-details inset />
              </div>
            </v-col>
          </v-row>

          <v-row class="mt-1">
            <v-col cols="12" lg="4">
              <div class="sqfarm-field-card">
                <div class="sqfarm-field-title">站点 Cookie</div>
                <v-text-field
                  v-model="cookieFieldValue"
                  label="站点 Cookie"
                  variant="outlined"
                  density="comfortable"
                  :disabled="cookieReadonly"
                  :readonly="cookieReadonly"
                  :placeholder="cookieReadonly ? '启用站点 Cookie 后自动同步' : '例如 c_secure_pass=...'"
                  hide-details="auto"
                />
                <div class="sqfarm-field-note">启用后自动读取站点 Cookie，关闭后才可手动修改。</div>
              </div>
            </v-col>

            <v-col cols="12" lg="4">
              <div class="sqfarm-field-card">
                <div class="sqfarm-field-title">优先种子</div>
                <v-select
                  v-model="config.prefer_seed"
                  :items="seedOptions"
                  label="优先种子"
                  variant="outlined"
                  density="comfortable"
                  :menu-props="{ maxHeight: 280 }"
                  hide-details="auto"
                />
              </div>
            </v-col>

            <v-col cols="12" lg="4">
              <div class="sqfarm-field-card">
                <div class="sqfarm-field-title">OCR API 地址</div>
                <v-text-field
                  v-model="config.ocr_api_url"
                  label="OCR API 地址"
                  variant="outlined"
                  density="comfortable"
                  placeholder="http://ip:8089/api/tr-run/"
                  hide-details="auto"
                />
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card class="sqfarm-config-card" rounded="xl" flat>
        <v-card-item>
          <template #prepend>
            <div class="sqfarm-config-kicker">OCR 说明</div>
          </template>
          <v-card-title>验证码识别</v-card-title>
        </v-card-item>
        <v-card-text>
          <div class="sqfarm-field-note">
            批量收菜验证码依赖 OCR。未配置 OCR 时，插件仍可刷新状态，并在批量收获失败后尝试逐坑位兜底收菜。
          </div>
          <div class="sqfarm-field-note">
            推荐先部署 <code>trwebocr</code>，再把 OCR 地址填成 <code>http://ip:8089/api/tr-run/</code>。
          </div>
          <pre class="sqfarm-code">{{ ocrComposeExample }}</pre>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
  api: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
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
})

const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    environment:
      - TZ=Asia/Shanghai`

const cookieReadonly = computed(() => !!config.auto_cookie)
const cookieFieldValue = computed({
  get() {
    if (config.auto_cookie) {
      return truncateCookie(config.cookie)
    }
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) {
      config.cookie = value || ''
    }
  },
})

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function truncateCookie(value) {
  const text = String(value || '').trim()
  if (!text) return ''
  return text.length > 36 ? `${text.slice(0, 36)}...` : text
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
    const res = await props.api.get('/plugin/VueFarm/status')
    applyStatusSeedOptions(res?.farm_status?.seed_shop)
  } catch (error) {
    // 保留当前种子列表
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VueFarm/config')
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
    const res = await props.api.post('/plugin/VueFarm/config', { ...config })
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
    const res = await props.api.get('/plugin/VueFarm/cookie')
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
  loadConfig()
})
</script>

<style scoped>
.sqfarm-config-page {
  min-height: 100%;
  padding: 20px;
  color: rgb(var(--v-theme-on-surface));
  background:
    radial-gradient(circle at top right, rgb(var(--v-theme-primary) / 0.08), transparent 26%),
    radial-gradient(circle at bottom left, rgb(var(--v-theme-warning) / 0.08), transparent 24%);
}

.sqfarm-config-shell {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sqfarm-config-card {
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  background: rgb(var(--v-theme-surface) / 0.88) !important;
  backdrop-filter: blur(14px);
  box-shadow: 0 18px 40px rgb(15 23 42 / 0.08);
}

.sqfarm-config-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.sqfarm-config-badge {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgb(var(--v-theme-primary) / 0.12);
  color: rgb(var(--v-theme-primary));
  font-size: 13px;
  font-weight: 700;
}

.sqfarm-config-title {
  margin: 14px 0 8px;
  font-size: clamp(34px, 4vw, 42px);
  line-height: 1.05;
  font-weight: 900;
}

.sqfarm-config-subtitle {
  margin: 0;
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 15px;
  line-height: 1.7;
}

.sqfarm-config-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.sqfarm-config-kicker {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sqfarm-switch-card,
.sqfarm-field-card {
  height: 100%;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  background: rgb(var(--v-theme-surface-bright) / 0.74);
}

.sqfarm-switch-card :deep(.v-selection-control) {
  min-height: 36px;
}

.sqfarm-switch-card :deep(.v-selection-control__wrapper) {
  transform: scale(0.82);
  transform-origin: left center;
}

.sqfarm-switch-card :deep(.v-label) {
  opacity: 1;
  color: rgb(var(--v-theme-on-surface));
  font-weight: 700;
}

.sqfarm-field-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 800;
  color: rgb(var(--v-theme-on-surface-variant));
}

.sqfarm-field-note {
  margin-top: 10px;
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 13px;
  line-height: 1.75;
}

.sqfarm-code {
  margin-top: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgb(var(--v-theme-on-surface) / 0.08);
  background: rgb(var(--v-theme-surface-bright) / 0.74);
  color: rgb(var(--v-theme-on-surface));
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
}

@media (max-width: 980px) {
  .sqfarm-config-page {
    padding: 16px;
  }

  .sqfarm-config-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .sqfarm-config-actions {
    justify-content: flex-start;
  }
}
</style>
