<template>
  <div class="cover-config">
    <div class="cover-shell">
      <section class="hero-card">
        <div>
          <div class="hero-kicker">媒体库封面生成魔改</div>
          <h1 class="hero-title">配置页</h1>
          <p class="hero-subtitle">
            读取 MoviePilot 已配置的飞牛影视媒体库，按媒体库现有海报拼贴出新的封面图，并尝试自动回写。
          </p>
        </div>
        <div class="hero-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回数据页</v-btn>
          <v-btn color="info" variant="flat" :loading="loading" @click="refreshLibraries">刷新媒体库</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存配置</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">运行控制</div>
            <h2>基础参数</h2>
          </div>
        </div>
        <div class="switch-grid">
          <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
          <v-switch v-model="config.auto_upload" label="生成后自动替换飞牛封面" color="primary" hide-details />
          <v-switch v-model="config.onlyonce" label="保存后立即执行一次" color="warning" hide-details />
          <v-switch v-model="config.notify" label="保留通知开关" color="secondary" hide-details />
        </div>
        <div class="form-grid mt-4">
          <v-text-field v-model="config.cron" label="定时 Cron" placeholder="0 4 * * *" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.image_count" label="拼贴海报数" type="number" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.history_limit" label="历史记录数" type="number" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.http_timeout" label="HTTP 超时(秒)" type="number" variant="outlined" density="comfortable" />
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">数据源</div>
            <h2>MoviePilot 与媒体库选择</h2>
          </div>
        </div>
        <div class="form-grid">
          <v-text-field v-model="config.moviepilot_url" label="MoviePilot 地址" placeholder="http://127.0.0.1:3000" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.moviepilot_api_token" label="MoviePilot API Token" placeholder="X-API-KEY 对应的 Token" variant="outlined" density="comfortable" />
          <v-select
            v-model="config.selected_servers"
            :items="serverOptions"
            item-title="title"
            item-value="value"
            label="媒体服务器"
            multiple
            chips
            clearable
            variant="outlined"
            density="comfortable"
          />
          <v-select
            v-model="config.include_libraries"
            :items="libraryOptions"
            item-title="title"
            item-value="value"
            label="限定媒体库"
            multiple
            chips
            clearable
            variant="outlined"
            density="comfortable"
          />
        </div>
        <p class="panel-note">
          不选媒体库时默认处理所选服务器下的全部媒体库。飞牛影视推荐只勾选需要替换封面的库，便于控制频率和回写风险。
        </p>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">样式</div>
            <h2>封面输出</h2>
          </div>
        </div>
        <div class="form-grid">
          <v-text-field v-model="config.poster_width" label="封面宽度" type="number" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.poster_height" label="封面高度" type="number" variant="outlined" density="comfortable" />
          <v-text-field v-model="config.custom_bg_color" label="背景色覆盖" placeholder="#182233" variant="outlined" density="comfortable" />
        </div>
        <p class="panel-note">
          默认从首张海报提取背景氛围。如果你希望统一风格，可以填一个十六进制颜色覆盖背景色调。
        </p>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">标题规则</div>
            <h2>媒体库命名映射</h2>
          </div>
          <v-btn size="small" variant="tonal" @click="addRule">新增规则</v-btn>
        </div>
        <div v-if="config.title_rules.length" class="rule-list">
          <div v-for="(rule, index) in config.title_rules" :key="index" class="rule-row">
            <v-text-field v-model="rule.match" label="匹配词" variant="outlined" density="comfortable" />
            <v-text-field v-model="rule.title" label="主标题" variant="outlined" density="comfortable" />
            <v-text-field v-model="rule.subtitle" label="副标题" variant="outlined" density="comfortable" />
            <v-btn variant="text" color="error" @click="removeRule(index)">删除</v-btn>
          </div>
        </div>
        <div v-else class="empty-box">
          暂无标题规则。默认直接使用飞牛影视里的媒体库名称和类型。
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">说明</div>
            <h2>当前行为</h2>
          </div>
        </div>
        <ul class="note-list">
          <li v-for="(note, index) in notes" :key="index">{{ note }}</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch'])

const pluginBase = '/plugin/MediaCoverRemix'
const loading = ref(false)
const saving = ref(false)
const serverOptions = ref([])
const libraryOptions = ref([])
const notes = ref([])
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: false,
  onlyonce: false,
  auto_upload: true,
  cron: '',
  moviepilot_url: '',
  moviepilot_api_token: '',
  selected_servers: [],
  include_libraries: [],
  title_rules: [],
  image_count: 4,
  history_limit: 30,
  http_timeout: 20,
  poster_width: 1600,
  poster_height: 900,
  custom_bg_color: '',
})

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function applyConfig(data = {}) {
  serverOptions.value = data.server_options || []
  libraryOptions.value = data.library_options || []
  notes.value = data.notes || []
  Object.assign(config, {
    ...config,
    ...data,
    selected_servers: [...(data.selected_servers || [])],
    include_libraries: [...(data.include_libraries || [])],
    title_rules: [...(data.title_rules || [])],
  })
}

async function loadConfig() {
  loading.value = true
  try {
    const data = await props.api.get(`${pluginBase}/config`)
    applyConfig(data || {})
  } catch (error) {
    flash(error?.message || '读取配置失败', 'error')
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const result = await props.api.post(`${pluginBase}/config`, {
      ...config,
      title_rules: config.title_rules.filter((rule) => rule.match || rule.title || rule.subtitle),
    })
    applyConfig(result?.config || {})
    flash(result?.message || '配置已保存')
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function refreshLibraries() {
  loading.value = true
  try {
    const result = await props.api.post(`${pluginBase}/refresh`, {})
    libraryOptions.value = result?.library_options || result?.status?.library_options || []
    flash('媒体库缓存已刷新')
  } catch (error) {
    flash(error?.message || '刷新媒体库失败', 'error')
  } finally {
    loading.value = false
  }
}

function addRule() {
  config.title_rules.push({ match: '', title: '', subtitle: '' })
}

function removeRule(index) {
  config.title_rules.splice(index, 1)
}

onMounted(() => {
  applyConfig(props.initialConfig || {})
  loadConfig()
})
</script>

<style scoped>
.cover-config {
  padding: 24px;
}

.cover-shell {
  max-width: 1240px;
  margin: 0 auto;
}

.hero-card,
.panel-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(90, 111, 148, 0.14);
  border-radius: 26px;
  padding: 24px 28px;
  box-shadow: 0 16px 40px rgba(19, 33, 68, 0.08);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.hero-kicker,
.panel-kicker {
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

.hero-subtitle,
.panel-note {
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

.switch-grid,
.form-grid,
.rule-row {
  display: grid;
  gap: 16px;
}

.switch-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.form-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.rule-list {
  display: grid;
  gap: 14px;
}

.rule-row {
  grid-template-columns: 1fr 1fr 1fr 40px;
  align-items: start;
}

.note-list {
  margin: 0;
  padding-left: 20px;
  color: #40506c;
  line-height: 1.8;
}

.empty-box {
  padding: 18px;
  border-radius: 18px;
  background: rgba(90, 111, 148, 0.07);
  color: #5c6981;
}

@media (max-width: 960px) {
  .cover-config {
    padding: 16px;
  }

  .hero-card {
    flex-direction: column;
  }

  .rule-row {
    grid-template-columns: 1fr;
  }
}
</style>
