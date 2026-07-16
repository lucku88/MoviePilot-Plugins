<template>
  <div class="siqi-config">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon">
          <v-icon icon="mdi-cog-outline" size="24" />
        </div>
        <div>
          <div class="siqi-topbar__title">Vue-农场 · 配置</div>
          <div class="siqi-topbar__sub">管理动态收菜、自动化策略与农场互动</div>
        </div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" @click="emit('switch', 'page')">
            <v-icon icon="mdi-view-dashboard" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">状态页</span>
          </v-btn>
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" @click="saveConfig" :loading="saving">
            <v-icon icon="mdi-content-save" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">保存</span>
          </v-btn>
          <v-btn color="success" size="small" min-width="40" class="px-0 px-sm-3" @click="emit('close')">
            <v-icon icon="mdi-close" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">关闭</span>
          </v-btn>
        </v-btn-group>
      </div>
    </div>

    <v-alert v-if="message" :type="messageType" density="compact" class="siqi-toast" closable @click:close="message=''">{{ message }}</v-alert>

    <div class="siqi-config-col">
      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-toggle-switch-outline" size="18" color="#22c55e" class="mr-1" />基础设置
          </span>
        </div>
        <div class="siqi-switch-grid">
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enabled}" style="--siqi-accent:34,197,94">
            <div class="siqi-switch-main"><v-icon icon="mdi-power-plug" size="18" /><div><div class="siqi-switch-label">启用插件</div><div class="siqi-switch-desc">开启定时任务与页面功能</div></div></div>
            <v-switch v-model="config.enabled" color="green" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.notify}" style="--siqi-accent:59,130,246">
            <div class="siqi-switch-main"><v-icon icon="mdi-bell-outline" size="18" /><div><div class="siqi-switch-label">开启通知</div><div class="siqi-switch-desc">任务完成后发送站内通知</div></div></div>
            <v-switch v-model="config.notify" color="blue" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.use_proxy}" style="--siqi-accent:139,92,246">
            <div class="siqi-switch-main"><v-icon icon="mdi-lan-connect" size="18" /><div><div class="siqi-switch-label">使用代理</div><div class="siqi-switch-desc">请求站点时使用系统代理</div></div></div>
            <v-switch v-model="config.use_proxy" color="purple" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.force_ipv4}" style="--siqi-accent:14,165,233">
            <div class="siqi-switch-main"><v-icon icon="mdi-ip-network-outline" size="18" /><div><div class="siqi-switch-label">强制 IPv4</div><div class="siqi-switch-desc">避免部分环境 IPv6 请求不稳定</div></div></div>
            <v-switch v-model="config.force_ipv4" color="info" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enable_ocr_harvest}" style="--siqi-accent:245,158,11">
            <div class="siqi-switch-main"><v-icon icon="mdi-image-search-outline" size="18" /><div><div class="siqi-switch-label">OCR 批量收菜</div><div class="siqi-switch-desc">关闭时直接快速逐坑位收菜并复查漏收</div></div></div>
            <v-switch v-model="config.enable_ocr_harvest" color="orange" hide-details density="compact" />
          </div>
        </div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-robot-outline" size="18" color="#f59e0b" class="mr-1" />自动化策略
          </span>
        </div>
        <div class="siqi-switch-grid">
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.onlyonce}" style="--siqi-accent:245,158,11">
            <div class="siqi-switch-main"><v-icon icon="mdi-play-circle-outline" size="18" /><div><div class="siqi-switch-label">立即运行一次</div><div class="siqi-switch-desc">保存后执行一次完整农场任务</div></div></div>
            <v-switch v-model="config.onlyonce" color="orange" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enable_plant}" style="--siqi-accent:34,197,94">
            <div class="siqi-switch-main"><v-icon icon="mdi-seed" size="18" /><div><div class="siqi-switch-label">自动补种</div><div class="siqi-switch-desc">为空地补种默认种子</div></div></div>
            <v-switch v-model="config.enable_plant" color="green" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.auto_steal}" style="--siqi-accent:239,68,68">
            <div class="siqi-switch-main"><v-icon icon="mdi-incognito" size="18" /><div><div class="siqi-switch-label">自动偷菜</div><div class="siqi-switch-desc">每日尝试偷取一次</div></div></div>
            <v-switch v-model="config.auto_steal" color="red" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.auto_like}" style="--siqi-accent:236,72,153">
            <div class="siqi-switch-main"><v-icon icon="mdi-thumb-up-outline" size="18" /><div><div class="siqi-switch-label">自动点赞</div><div class="siqi-switch-desc">随机批量点赞农场</div></div></div>
            <v-switch v-model="config.auto_like" color="pink" hide-details density="compact" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enable_sell}" style="--siqi-accent:14,165,233">
            <div class="siqi-switch-main"><v-icon icon="mdi-cash-sync" size="18" /><div><div class="siqi-switch-label">自动出售</div><div class="siqi-switch-desc">出售收获背包库存</div></div></div>
            <v-switch v-model="config.enable_sell" color="info" hide-details density="compact" />
          </div>
        </div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-tune-variant" size="18" color="#0ea5e9" class="mr-1" />参数设置
          </span>
        </div>
        <div class="siqi-form-grid">
          <v-select v-model="config.prefer_seed" :items="seedOptions" label="优先种植" density="compact" variant="outlined" hide-details class="siqi-input seed-select" prepend-inner-icon="mdi-sprout" :loading="seedLoading">
            <template #item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps">
                <template #subtitle>
                  <span v-if="item.raw.locked" class="text-error">未解锁：需总收获 {{ item.raw.unlockHarvest }}</span>
                  <span v-else class="text-medium-emphasis">已解锁</span>
                </template>
              </v-list-item>
            </template>
          </v-select>
          <v-text-field v-model.number="config.schedule_buffer_seconds" label="成熟后缓冲（秒）" type="number" min="0" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-clock-fast" />
          <v-text-field v-model.number="config.random_delay_max_seconds" label="随机延迟上限（秒）" type="number" min="0" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-sand" />
          <v-text-field v-model.number="config.http_timeout" label="请求超时（秒）" type="number" min="3" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-alert-outline" />
          <v-text-field v-model.number="config.http_retry_times" label="网络重试次数" type="number" min="1" max="5" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-reload" />
          <v-text-field v-model.number="retryDelaySeconds" label="重试间隔（秒）" type="number" min="0.2" step="0.1" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-outline" />
        </div>
        <div class="siqi-field-hint">插件按最早真实成熟时间自动运行；优先种子来自站点种子商店，并会自动识别是否已解锁。</div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-image-search-outline" size="18" color="#f59e0b" class="mr-1" />OCR 批量收菜
          </span>
        </div>
        <div class="siqi-form-grid">
          <v-text-field v-model="config.ocr_api_url" label="OCR API 地址" density="compact" variant="outlined" hide-details class="siqi-input siqi-wide-field" prepend-inner-icon="mdi-link-variant" :disabled="!config.enable_ocr_harvest" />
          <v-text-field v-model.number="config.ocr_retry_times" label="验证码识别次数" type="number" min="1" max="3" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-restore" :disabled="!config.enable_ocr_harvest" />
        </div>
        <div class="siqi-field-hint">默认关闭。开启并填写 OCR 地址后才会批量收菜；失败后会立刻切换逐坑位收菜，并再次检查是否漏收。</div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-incognito" size="18" color="#ef4444" class="mr-1" />偷菜与互动
          </span>
        </div>
        <div class="siqi-form-grid">
          <v-select
            v-model="config.steal_crop"
            :items="stealCropOptions"
            label="偷菜作物（可多选）"
            density="compact"
            variant="outlined"
            hide-details
            multiple
            chips
            closable-chips
            clearable
            class="siqi-input seed-select steal-crop-select"
            prepend-inner-icon="mdi-food-apple-outline"
            @update:model-value="onStealCropChange"
          />
          <v-text-field v-model.number="config.steal_visit_count" label="每轮随机访问人数" type="number" min="1" max="30" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-account-multiple-outline" />
          <v-select v-model="config.social_cron" :items="socialCronOptions" label="互动检查间隔" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-calendar-clock" />
        </div>
        <v-textarea v-model="config.steal_time_windows" label="偷菜时间段" rows="2" auto-grow variant="outlined" class="siqi-input mt-3" prepend-inner-icon="mdi-clock-outline" hint="多个时间段用逗号分隔，例如：07:00-09:00,12:00-14:00,18:00-23:00" persistent-hint />
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-cookie" size="18" color="#8b5cf6" class="mr-1" />站点 Cookie
          </span>
          <v-btn color="deep-purple" variant="tonal" size="small" :loading="syncingCookie" @click="syncCookie">
            <v-icon icon="mdi-sync" size="16" class="mr-1" />从站点同步
          </v-btn>
        </div>
        <v-textarea v-model="config.cookie" label="站点 Cookie（自动同步）" rows="2" auto-grow variant="outlined" class="siqi-input" :class="{'siqi-secret-input': !showCookie}" prepend-inner-icon="mdi-cookie" autocomplete="off">
          <template #append-inner>
            <v-btn variant="text" density="comfortable" size="x-small" icon class="siqi-secret-toggle" @click.stop="showCookie = !showCookie">
              <v-icon :icon="showCookie ? 'mdi-eye-off-outline' : 'mdi-eye-outline'" size="18" />
            </v-btn>
          </template>
        </v-textarea>
        <div class="siqi-field-hint">插件会在启动、保存配置和每次请求前自动读取 MoviePilot 站点 Cookie；右上角按钮可立即同步，输入框内容仅在站点同步失败时作为备用。</div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'

const props = defineProps({ api: Object, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])
const PLUGIN_ID = 'VueFarm'
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  enable_sell: true,
  enable_plant: true,
  enable_ocr_harvest: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
  ocr_retry_times: 3,
  auto_steal: false,
  auto_like: false,
  steal_crop: ['全部作物'],
  steal_visit_count: 5,
  steal_time_windows: '07:00-09:00,12:00-14:00,18:00-23:00',
  social_cron: '*/5 * * * *',
  ...props.initialConfig
})
const loading = ref(false)
const saving = ref(false)
const syncingCookie = ref(false)
const seedLoading = ref(false)
const showCookie = ref(false)
const seedOptions = ref([{ title: '🍅 西红柿', value: '西红柿', locked: false, unlockHarvest: 0 }])
const stealCropOptions = ref(['全部作物', '西红柿'])
const socialCronOptions = [
  { title: '每 5 分钟', value: '*/5 * * * *' },
  { title: '每 10 分钟', value: '*/10 * * * *' },
  { title: '每 15 分钟', value: '*/15 * * * *' },
  { title: '每 30 分钟', value: '*/30 * * * *' }
]
const message = ref('')
const messageType = ref('success')
let messageTimer = null

const retryDelaySeconds = computed({
  get: () => Number(config.http_retry_delay || 0) / 1000,
  set: value => { config.http_retry_delay = Math.max(200, Math.round(Number(value || 0) * 1000)) }
})
const apiGet = path => props.api.get(`/plugin/${PLUGIN_ID}${path}`)
const apiPost = (path, data) => props.api.post(`/plugin/${PLUGIN_ID}${path}`, data)

function numberValue(value) {
  const parsed = Number(String(value ?? '').replace(/,/g, ''))
  return Number.isFinite(parsed) ? parsed : 0
}

function normalizeStealCropValues(value) {
  let source = value
  if (typeof source === 'string') {
    const text = source.trim()
    if (text.startsWith('[') && text.endsWith(']')) {
      try {
        const parsed = JSON.parse(text)
        if (Array.isArray(parsed)) source = parsed
      } catch (e) {
        // 兼容旧版本保存的非标准文本，继续按逗号拆分。
      }
    }
  }
  const values = Array.isArray(source)
    ? source.map(item => String(item || '').trim()).filter(Boolean)
    : String(source || '').split(/[,，;；\n\r]+/).map(item => item.trim()).filter(Boolean)
  const unique = [...new Set(values)]
  if (!unique.length) return ['全部作物']
  if (unique.includes('全部作物') && unique.length > 1) {
    return unique[unique.length - 1] === '全部作物'
      ? ['全部作物']
      : unique.filter(item => item !== '全部作物')
  }
  return unique
}

function onStealCropChange(value) {
  config.steal_crop = normalizeStealCropValues(value)
}

function show(text, type = 'success') {
  message.value = text
  messageType.value = type
  if (messageTimer) clearTimeout(messageTimer)
  messageTimer = setTimeout(() => {
    if (message.value === text) message.value = ''
    messageTimer = null
  }, 3000)
}

async function loadConfig() {
  loading.value = true
  try {
    const res = await apiGet('/config')
    Object.assign(config, res)
    config.steal_crop = normalizeStealCropValues(res.steal_crop)
  } catch (e) {
    show(`加载失败：${e.message}`, 'error')
  } finally {
    loading.value = false
  }
}

async function loadSeeds() {
  seedLoading.value = true
  try {
    const res = await apiGet('/data')
    const seeds = Array.isArray(res?.seeds) ? res.seeds : []
    const totalHarvest = numberValue(res?.user_stats?.total_harvest)
    if (seeds.length) {
      seedOptions.value = seeds.map(seed => {
        const locked = totalHarvest < numberValue(seed.unlock_harvest)
        return {
          title: `${seed.icon || '🌱'} ${seed.name || `种子 ${seed.id}`}`,
          value: String(seed.name || ''),
          locked,
          unlockHarvest: seed.unlock_harvest || 0,
          props: { disabled: locked }
        }
      })
      stealCropOptions.value = ['全部作物', ...seeds.map(seed => String(seed.name || '').trim()).filter(Boolean)]
    }
  } catch (e) {
    show(`种子列表加载失败：${e.message}`, 'error')
  } finally {
    seedLoading.value = false
  }
}

async function syncCookie() {
  syncingCookie.value = true
  try {
    const res = await apiGet('/cookie')
    if (res.config) {
      Object.assign(config, res.config)
      config.steal_crop = normalizeStealCropValues(config.steal_crop)
    }
    show(res.message || (res.success ? 'Cookie 同步成功' : 'Cookie 同步失败'), res.success ? 'success' : 'error')
  } catch (e) {
    show(`Cookie 同步失败：${e.message}`, 'error')
  } finally {
    syncingCookie.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await apiPost('/config', {
      ...config,
      steal_crop: normalizeStealCropValues(config.steal_crop)
    })
    if (res.config) Object.assign(config, res.config)
    config.steal_crop = normalizeStealCropValues(config.steal_crop)
    show(res.message || (res.success ? '保存成功' : '保存失败'), res.success ? 'success' : 'error')
  } catch (e) {
    show(`保存失败：${e.message}`, 'error')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadConfig()
  await loadSeeds()
})
</script>

<style scoped>
.siqi-config{padding:16px 20px;display:flex;flex-direction:column;gap:16px;min-height:400px;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',sans-serif;color:rgba(var(--v-theme-on-surface),.85);border:1px solid rgba(var(--v-theme-on-surface),.12);border-radius:8px;background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))}
.siqi-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:8px}.siqi-topbar__left{display:flex;align-items:center;gap:12px;min-width:0;flex:1}.siqi-topbar__right{display:flex;align-items:center;gap:10px;flex-shrink:0}.siqi-topbar__right :deep(.v-btn-group){flex-wrap:nowrap}.siqi-topbar__icon{width:42px;height:42px;border-radius:11px;background:rgba(76,175,80,.14);display:flex;align-items:center;justify-content:center;color:#2e7d32;flex-shrink:0}.siqi-topbar__title{font-size:16px;font-weight:700;letter-spacing:-.3px;color:rgba(var(--v-theme-on-surface),.88)}.siqi-topbar__sub{font-size:11px;color:rgba(var(--v-theme-on-surface),.55);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.siqi-toast{position:fixed!important;top:18px!important;left:50%!important;transform:translateX(-50%)!important;z-index:99999!important;width:min(520px,calc(100vw - 32px))!important;margin:0!important;box-shadow:0 12px 36px rgba(15,23,42,.18)!important;border-radius:12px!important}
.siqi-config-col{display:flex;flex-direction:column;gap:16px}.siqi-card{background:rgba(var(--v-theme-on-surface),.03);backdrop-filter:blur(20px) saturate(150%);border-radius:14px;border:.5px solid rgba(var(--v-theme-on-surface),.08);box-shadow:0 2px 10px rgba(0,0,0,.05);padding:14px 16px;display:flex;flex-direction:column;gap:14px}.siqi-card__header{display:flex;align-items:center;justify-content:space-between;gap:12px}.siqi-card__title{font-size:13px;font-weight:700;color:rgba(var(--v-theme-on-surface),.85)}
.siqi-switch-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.siqi-switch-item{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px;border-radius:12px;background:rgba(var(--v-theme-on-surface),.025);border:.5px solid rgba(var(--v-theme-on-surface),.06);transition:background .2s ease,border-color .2s ease,transform .2s ease}.siqi-switch-item:hover{transform:translateY(-1px)}.siqi-switch-item--active{background:rgba(var(--siqi-accent,34,197,94),.07);border-color:rgba(var(--siqi-accent,34,197,94),.18)}.siqi-switch-main{display:flex;align-items:center;gap:10px;min-width:0;flex:1;color:rgba(var(--v-theme-on-surface),.58)}.siqi-switch-item--active .siqi-switch-main{color:rgb(var(--siqi-accent,34,197,94))}.siqi-switch-label{font-size:13px;font-weight:600;color:rgba(var(--v-theme-on-surface),.86)}.siqi-switch-desc{font-size:11px;color:rgba(var(--v-theme-on-surface),.46);line-height:1.35;margin-top:1px}.siqi-switch-item :deep(.v-switch){flex:0 0 auto}.siqi-switch-item :deep(.v-selection-control){min-height:unset}.siqi-switch-item :deep(.v-input__details){display:none}
.siqi-form-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.siqi-cron-field,.siqi-wide-field{grid-column:span 2}.siqi-input :deep(.v-field){border-radius:12px}.siqi-input :deep(.v-field__loader){left:1px;right:1px;width:auto;border-radius:12px 12px 0 0;overflow:hidden}.seed-select :deep(.v-input__control){border-radius:12px;clip-path:inset(-10px 0 0 0 round 12px)}.seed-select :deep(.v-input__loader){left:1px!important;right:1px!important;width:auto!important;margin:0!important;overflow:hidden!important;border-radius:12px 12px 0 0!important}.seed-select :deep(.v-progress-linear){border-radius:12px 12px 0 0;overflow:hidden}.siqi-secret-input :deep(textarea){-webkit-text-security:disc}.siqi-secret-toggle{min-width:28px;width:28px;height:28px;color:rgba(var(--v-theme-on-surface),.55)}.siqi-secret-toggle :deep(.v-btn__overlay),.siqi-secret-toggle :deep(.v-btn__underlay){display:none}.siqi-field-hint{font-size:11px;line-height:1.5;color:rgba(var(--v-theme-on-surface),.48);margin-top:-6px}
@media(max-width:900px){.siqi-switch-grid,.siqi-form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:600px){.siqi-config{padding:14px}.siqi-topbar{align-items:flex-start;gap:10px}.siqi-topbar__left{min-width:0}.siqi-topbar__right :deep(.v-btn){min-width:36px!important;padding-inline:0!important}.siqi-switch-grid,.siqi-form-grid{grid-template-columns:1fr}.siqi-cron-field,.siqi-wide-field{grid-column:span 1}.siqi-switch-item{align-items:center}}
</style>
