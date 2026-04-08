<template>
  <div class="cover-page">
    <div class="cover-shell">
      <section class="hero-card">
        <div>
          <div class="hero-kicker">媒体库封面生成魔改</div>
          <h1 class="hero-title">数据页</h1>
          <p class="hero-subtitle">
            手动触发媒体库封面生成，查看最新输出、飞牛回写结果，以及当前媒体服务器探测信息。
          </p>
        </div>
        <div class="hero-actions">
          <v-btn variant="text" @click="emit('switch', 'config')">打开配置页</v-btn>
          <v-btn color="info" variant="flat" :loading="loading" @click="refreshStatus">刷新状态</v-btn>
          <v-btn color="secondary" variant="flat" :loading="inspecting" @click="inspectRuntime">探测飞牛连接</v-btn>
          <v-btn color="primary" variant="flat" :loading="running" @click="runNow">立即生成</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="metric-grid">
        <v-card class="metric-card" rounded="xl">
          <div class="metric-label">运行状态</div>
          <div class="metric-value">{{ status.running ? '执行中' : '空闲' }}</div>
          <div class="metric-desc">启用状态：{{ status.enabled ? '已启用' : '未启用' }}</div>
        </v-card>
        <v-card class="metric-card" rounded="xl">
          <div class="metric-label">最近运行</div>
          <div class="metric-value small">{{ status.last_run || '-' }}</div>
          <div class="metric-desc">{{ status.latest_result?.message || '暂无执行记录' }}</div>
        </v-card>
        <v-card class="metric-card" rounded="xl">
          <div class="metric-label">生成数量</div>
          <div class="metric-value">{{ status.latest_result?.generated_count || 0 }}</div>
          <div class="metric-desc">最近一次执行成功生成的媒体库数量</div>
        </v-card>
        <v-card class="metric-card" rounded="xl">
          <div class="metric-label">回写数量</div>
          <div class="metric-value">{{ status.latest_result?.uploaded_count || 0 }}</div>
          <div class="metric-desc">最近一次成功自动替换的飞牛媒体库数量</div>
        </v-card>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">最新输出</div>
            <h2>媒体库封面预览</h2>
          </div>
        </div>
        <div v-if="resultItems.length" class="preview-grid">
          <v-card v-for="item in resultItems" :key="`${item.server}-${item.library_id}`" class="preview-card" rounded="xl">
            <v-img v-if="item.preview_url" :src="item.preview_url" cover class="preview-image" />
            <div v-else class="preview-fallback">无预览</div>
            <div class="preview-body">
              <div class="preview-title">{{ item.library_name }}</div>
              <div class="preview-meta">{{ item.server }} / {{ item.library_id }}</div>
              <div class="chip-row">
                <v-chip :color="item.success ? 'success' : 'error'" size="small" variant="tonal">
                  {{ item.success ? '已生成' : '失败' }}
                </v-chip>
                <v-chip :color="item.uploaded ? 'primary' : 'default'" size="small" variant="tonal">
                  {{ item.uploaded ? '已回写' : '未回写' }}
                </v-chip>
              </div>
              <p class="preview-message">{{ item.message }}</p>
              <div class="preview-file">{{ item.output_name || item.output_file }}</div>
            </div>
          </v-card>
        </div>
        <div v-else class="empty-box">
          暂无生成结果。先到配置页选中飞牛影视媒体库，再点击“立即生成”。
        </div>
      </section>

      <section class="dual-grid">
        <v-card class="panel-card" rounded="xl">
          <div class="panel-head">
            <div>
              <div class="panel-kicker">执行历史</div>
              <h2>最近任务</h2>
            </div>
          </div>
          <div v-if="historyItems.length" class="history-list">
            <div v-for="(item, index) in historyItems" :key="index" class="history-item">
              <div>
                <div class="history-time">{{ item.time }}</div>
                <div class="history-message">{{ item.message }}</div>
              </div>
              <v-chip :color="item.success ? 'success' : 'error'" size="small" variant="tonal">
                {{ item.success ? '成功' : '失败' }}
              </v-chip>
            </div>
          </div>
          <div v-else class="empty-box">暂无历史记录。</div>
        </v-card>

        <v-card class="panel-card" rounded="xl">
          <div class="panel-head">
            <div>
              <div class="panel-kicker">运行探测</div>
              <h2>飞牛连接信息</h2>
            </div>
          </div>
          <div class="inspect-box">
            <pre>{{ inspectText }}</pre>
          </div>
        </v-card>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch'])

const pluginBase = '/plugin/MediaCoverRemix'
const loading = ref(false)
const running = ref(false)
const inspecting = ref(false)
const message = reactive({ text: '', type: 'success' })
const status = reactive({
  enabled: false,
  running: false,
  last_run: '',
  latest_result: {},
  history: [],
  inspect: {},
})

const resultItems = computed(() => status.latest_result?.items || [])
const historyItems = computed(() => status.history || [])
const inspectText = computed(() => JSON.stringify(status.inspect || {}, null, 2))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function applyStatus(data = {}) {
  Object.assign(status, {
    ...status,
    ...data,
  })
}

async function loadStatus() {
  loading.value = true
  try {
    const data = await props.api.get(`${pluginBase}/status`)
    applyStatus(data || {})
  } catch (error) {
    flash(error?.message || '读取状态失败', 'error')
  } finally {
    loading.value = false
  }
}

async function refreshStatus() {
  loading.value = true
  try {
    const data = await props.api.post(`${pluginBase}/refresh`, {})
    applyStatus(data?.status || data || {})
    flash('状态已刷新')
  } catch (error) {
    flash(error?.message || '刷新状态失败', 'error')
  } finally {
    loading.value = false
  }
}

async function inspectRuntime() {
  inspecting.value = true
  try {
    const data = await props.api.get(`${pluginBase}/inspect`)
    status.inspect = data || {}
    flash('飞牛连接探测已更新')
  } catch (error) {
    flash(error?.message || '探测失败', 'error')
  } finally {
    inspecting.value = false
  }
}

async function runNow() {
  running.value = true
  try {
    const data = await props.api.post(`${pluginBase}/run`, {})
    applyStatus(data?.status || status)
    status.latest_result = data || {}
    flash(data?.message || '任务已执行')
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    running.value = false
  }
}

onMounted(() => {
  loadStatus()
})
</script>

<style scoped>
.cover-page {
  padding: 24px;
}

.cover-shell {
  max-width: 1240px;
  margin: 0 auto;
}

.hero-card,
.panel-card,
.metric-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(90, 111, 148, 0.14);
  box-shadow: 0 16px 40px rgba(19, 33, 68, 0.08);
}

.hero-card,
.panel-card {
  border-radius: 26px;
  padding: 24px 28px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.hero-kicker,
.panel-kicker,
.metric-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #5870a8;
  text-transform: uppercase;
}

.hero-title {
  margin: 10px 0 8px;
  font-size: 32px;
  line-height: 1.15;
}

.hero-subtitle {
  color: #4d5c77;
  max-width: 760px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.metric-grid,
.preview-grid,
.dual-grid {
  display: grid;
  gap: 18px;
}

.metric-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin-bottom: 18px;
}

.metric-card {
  border-radius: 24px;
  padding: 22px;
}

.metric-value {
  margin-top: 12px;
  font-size: 38px;
  font-weight: 700;
  color: #16233f;
}

.metric-value.small {
  font-size: 20px;
}

.metric-desc {
  margin-top: 8px;
  color: #607089;
  line-height: 1.6;
}

.panel-card {
  margin-bottom: 18px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}

.preview-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.preview-card {
  overflow: hidden;
  border: 1px solid rgba(90, 111, 148, 0.12);
}

.preview-image,
.preview-fallback {
  height: 176px;
}

.preview-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #dbe5f7, #eff4fb);
  color: #5d6f8b;
}

.preview-body {
  padding: 18px;
}

.preview-title {
  font-size: 18px;
  font-weight: 700;
  color: #172540;
}

.preview-meta,
.preview-file {
  margin-top: 6px;
  color: #64748f;
  word-break: break-all;
}

.preview-message {
  margin: 14px 0 0;
  color: #31415f;
  line-height: 1.7;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.dual-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.history-list {
  display: grid;
  gap: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(91, 114, 148, 0.08);
}

.history-time {
  font-size: 13px;
  color: #607089;
}

.history-message {
  margin-top: 6px;
  color: #263657;
  line-height: 1.6;
}

.inspect-box {
  border-radius: 18px;
  background: #101722;
  color: #dce8ff;
  padding: 16px;
  min-height: 260px;
  overflow: auto;
}

.inspect-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.6;
}

.empty-box {
  padding: 18px;
  border-radius: 18px;
  background: rgba(90, 111, 148, 0.07);
  color: #5c6981;
}

@media (max-width: 960px) {
  .cover-page {
    padding: 16px;
  }

  .hero-card {
    flex-direction: column;
  }

  .dual-grid {
    grid-template-columns: 1fr;
  }
}
</style>
