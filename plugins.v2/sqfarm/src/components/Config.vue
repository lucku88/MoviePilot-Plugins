<template>
  <div class="sq-config">
    <div class="sq-head">
      <div>
        <h1 class="sq-title">SQFarm 配置</h1>
        <div class="sq-tip">支持站点 Cookie 同步、动态调度和 OCR 收菜。</div>
      </div>
      <div class="sq-actions">
        <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
        <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步Cookie</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
        <v-btn variant="text" @click="closePlugin">关闭</v-btn>
      </div>
    </div>

    <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">{{ message.text }}</v-alert>

    <div class="sq-form-grid">
      <div class="sq-card">
        <h3>基础开关</h3>
        <div class="sq-switches">
          <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
          <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
          <v-switch v-model="config.onlyonce" label="保存后立即执行一次" color="warning" hide-details />
          <v-switch v-model="config.auto_cookie" label="自动同步站点 Cookie" color="info" hide-details />
          <v-switch v-model="config.use_proxy" label="使用系统代理" color="info" hide-details />
          <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
        </div>
      </div>

      <div class="sq-card">
        <h3>站点与调度</h3>
        <v-text-field v-model="config.site_domain" label="站点域名" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.cron" label="轮询 CRON" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.prefer_seed" label="优先种子" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.schedule_buffer_seconds" label="智能调度缓冲秒数" type="number" variant="outlined" density="comfortable" />
      </div>

      <div class="sq-card">
        <h3>网络与 OCR</h3>
        <v-text-field v-model="config.ocr_api_url" label="OCR API 地址" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.random_delay_max_seconds" label="随机延迟上限(秒)" type="number" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.http_timeout" label="HTTP 超时(秒)" type="number" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.http_retry_times" label="网络重试次数" type="number" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.http_retry_delay" label="网络重试间隔(ms)" type="number" variant="outlined" density="comfortable" class="mb-3" />
        <v-text-field v-model="config.ocr_retry_times" label="OCR 重试次数" type="number" variant="outlined" density="comfortable" />
      </div>

      <div class="sq-card sq-card-wide">
        <h3>手动 Cookie</h3>
        <v-textarea v-model="config.cookie" label="SIQI Cookie" rows="7" variant="outlined" density="comfortable" placeholder="例如 c_secure_pass=..." />
        <div class="sq-note">开启自动同步后，插件会优先读取 MoviePilot 站点管理里的 Cookie。这里仍可作为手动兜底。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  use_proxy: false,
  force_ipv4: true,
  cron: '*/10 * * * *',
  site_domain: 'si-qi.xyz',
  cookie: '',
  ocr_api_url: '',
  prefer_seed: '西红柿',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  ocr_retry_times: 2,
})

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/SQFarm/config')
    Object.assign(config, res || {})
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/config', { ...config })
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
    }
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

onMounted(loadConfig)
</script>

<style scoped>
.sq-config { color: #2c2a26; }
.sq-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
.sq-title { margin: 0; font-size: 30px; font-weight: 800; }
.sq-tip { color: #6f6a5f; font-size: 13px; }
.sq-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.sq-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.sq-card { padding: 20px; border-radius: 24px; background: rgba(255,255,255,0.92); border: 1px solid rgba(219,205,181,0.7); box-shadow: 0 10px 30px rgba(160,123,55,0.08); }
.sq-card h3 { margin: 0 0 16px; font-size: 20px; font-weight: 800; }
.sq-card-wide { grid-column: 1 / -1; }
.sq-switches { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px 20px; }
.sq-note { margin-top: 12px; color: #7b7263; font-size: 13px; }
@media (max-width: 960px) { .sq-head { flex-direction: column; } .sq-form-grid { grid-template-columns: 1fr; } }
</style>
