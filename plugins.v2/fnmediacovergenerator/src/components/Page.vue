<template>
  <section class="cover-page">
    <div class="hero-card">
      <div>
        <div class="hero-kicker">FnMediaCoverGenerator</div>
        <h1 class="hero-title">飞牛影视媒体库封面生成</h1>
        <div class="hero-meta">
          <v-chip size="small" color="primary" variant="flat">当前风格 {{ state.cover_style || 'static_1' }}</v-chip>
          <span>最近执行时间：{{ state.latest_time || '-' }}</span>
        </div>
      </div>
      <div class="hero-actions">
        <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新</v-btn>
        <v-btn v-if="show_switch" color="primary" variant="text" @click="emit('switch')">配置</v-btn>
        <v-btn variant="text" @click="emit('close')">关闭</v-btn>
      </div>
    </div>

    <v-alert v-if="message.text" :type="message.type" variant="tonal">
      {{ message.text }}
    </v-alert>

    <v-card variant="outlined">
      <v-card-text class="summary-card">
        <div class="summary-main">{{ state.latest_message || '还没有执行记录' }}</div>
        <div class="summary-sub">{{ state.latest_time || '-' }}</div>
        <v-alert
          :type="state.setup_warnings?.length ? 'warning' : 'info'"
          variant="tonal"
          density="compact"
          class="mt-4"
        >
          {{ state.setup_warnings?.length ? state.setup_warnings.join('；') : '当前风格会直接作用于飞牛媒体库静态封面。' }}
        </v-alert>
      </v-card-text>
    </v-card>

    <v-card variant="outlined">
      <v-tabs v-model="tab" color="primary" grow>
        <v-tab value="generate">封面生成</v-tab>
        <v-tab value="history">历史封面</v-tab>
        <v-tab value="clean">清理缓存</v-tab>
      </v-tabs>
      <v-divider />

      <v-window v-model="tab">
        <v-window-item value="generate">
          <v-card-text>
            <div class="action-row">
              <div class="text-body-2 text-medium-emphasis">点击风格卡片可直接切换；风格切换后会同步刷新当前状态。</div>
              <v-btn color="primary" variant="flat" :loading="actionKey === 'generate'" @click="runAction('generate', `${pluginBase}/generate_now`)">
                立即生成当前风格
              </v-btn>
            </div>
            <v-row>
              <v-col v-for="card in state.style_cards || []" :key="card.index" cols="12" sm="6" md="3">
                <v-card
                  class="style-card"
                  :class="{ selected: card.selected }"
                  :elevation="card.selected ? 6 : 2"
                  @click="runAction(`style-${card.index}`, `${pluginBase}/select_style_${card.index}`)"
                >
                  <v-img :src="card.preview_src" aspect-ratio="16/9" cover />
                  <v-card-text class="py-3">
                    <div class="d-flex align-center justify-space-between ga-2">
                      <div>
                        <div class="text-subtitle-1 font-weight-medium">{{ card.name }}</div>
                        <div class="text-caption text-medium-emphasis">{{ card.variant }}</div>
                      </div>
                      <v-chip :color="card.selected ? 'primary' : 'default'" size="small" :variant="card.selected ? 'flat' : 'outlined'">
                        {{ card.selected ? '当前' : '切换' }}
                      </v-chip>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-window-item>

        <v-window-item value="history">
          <v-card-text>
            <div class="action-row">
              <div class="text-body-2 text-medium-emphasis">
                最多展示 {{ state.history_limit || 0 }} 张历史封面。现在勾选只在当前页面本地生效，删除时才会请求后端，所以不会再一张一闪。
              </div>
              <div class="d-flex flex-wrap ga-2 justify-end">
                <v-btn variant="text" size="small" :disabled="!historyItems.length" @click="selectAllHistory">全选当前页</v-btn>
                <v-btn variant="text" size="small" :disabled="!selectedPaths.length" @click="clearHistorySelection">清空选择</v-btn>
                <v-btn
                  color="error"
                  variant="flat"
                  size="small"
                  :disabled="!selectedPaths.length"
                  :loading="actionKey === 'delete-selected'"
                  @click="deleteSelectedHistory"
                >
                  删除已选（{{ selectedPaths.length }}）
                </v-btn>
              </div>
            </div>

            <v-row v-if="historyItems.length">
              <v-col v-for="item in historyItems" :key="item.path" cols="12" sm="6" md="4" lg="3">
                <v-card class="history-card" :class="{ selected: isSelected(item.path) }" variant="flat" elevation="3">
                  <div class="history-check">
                    <v-btn
                      size="small"
                      :color="isSelected(item.path) ? 'primary' : 'default'"
                      :variant="isSelected(item.path) ? 'flat' : 'outlined'"
                      @click.stop="toggleHistorySelection(item.path)"
                    >
                      {{ isSelected(item.path) ? '已选' : '选择' }}
                    </v-btn>
                  </div>
                  <v-img :src="item.src" aspect-ratio="16/9" cover @click="toggleHistorySelection(item.path)" />
                  <v-card-text class="pb-2">
                    <div class="text-body-2 history-name">{{ item.name }}</div>
                    <div class="text-caption text-medium-emphasis">{{ item.mtime }} / {{ item.size }}</div>
                  </v-card-text>
                  <v-card-actions class="pt-0">
                    <v-btn
                      color="error"
                      variant="text"
                      size="small"
                      :loading="actionKey === `delete-${item.path}`"
                      @click.stop="deleteSingleHistory(item)"
                    >
                      删除
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>

            <v-alert v-else type="info" variant="tonal">还没有可展示的历史封面。</v-alert>
          </v-card-text>
        </v-window-item>

        <v-window-item value="clean">
          <v-card-text class="clean-grid">
            <v-card variant="tonal" color="error">
              <v-card-title>清理图片缓存</v-card-title>
              <v-card-text>只会清理生成源图缓存，不会删除已保存的历史封面。</v-card-text>
              <v-card-actions>
                <v-btn color="error" variant="flat" :loading="actionKey === 'clean-images'" @click="runAction('clean-images', `${pluginBase}/clean_images`)">
                  立即清理
                </v-btn>
              </v-card-actions>
            </v-card>

            <v-card variant="tonal" color="warning">
              <v-card-title>清理字体缓存</v-card-title>
              <v-card-text>清理后会重新下载或重新读取你配置的字体资源。</v-card-text>
              <v-card-actions>
                <v-btn color="warning" variant="flat" :loading="actionKey === 'clean-fonts'" @click="runAction('clean-fonts', `${pluginBase}/clean_fonts`)">
                  立即清理
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-card-text>
        </v-window-item>
      </v-window>
    </v-card>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const PLUGIN_ID = 'FnMediaCoverGenerator'
const pluginBase = `plugin/${PLUGIN_ID}`

const props = defineProps({
  api: { type: Object, required: true },
  show_switch: { type: Boolean, default: true },
})

const emit = defineEmits(['switch', 'close'])

const loading = ref(false)
const actionKey = ref('')
const tab = ref('generate')
const state = reactive({
  latest_message: '',
  latest_time: '',
  setup_warnings: [],
  cover_style: 'static_1',
  cover_style_index: 1,
  history_limit: 0,
  history_items: [],
  style_cards: [],
})
const selectedPaths = ref([])
const message = reactive({ text: '', type: 'info' })

const historyItems = computed(() => state.history_items || [])
const show_switch = computed(() => props.show_switch !== false)

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value ?? {}))
}

function assignState(payload) {
  const next = cloneValue(payload)
  Object.keys(state).forEach((key) => {
    state[key] = next[key] ?? (Array.isArray(state[key]) ? [] : '')
  })
  Object.entries(next).forEach(([key, value]) => {
    state[key] = value
  })
  const visible = new Set((next.history_items || []).map((item) => item.path))
  selectedPaths.value = selectedPaths.value.filter((item) => visible.has(item))
}

async function refreshData() {
  loading.value = true
  try {
    const result = await props.api.get(`${pluginBase}/page_data`)
    assignState(result?.data || {})
  } catch (error) {
    message.type = 'error'
    message.text = error?.message || '页面数据加载失败'
  } finally {
    loading.value = false
  }
}

async function runAction(key, apiPath, payload = {}) {
  actionKey.value = key
  try {
    const result = await props.api.post(apiPath, payload)
    message.type = result?.success === false ? 'warning' : 'success'
    message.text = result?.message || '操作已完成'
    await refreshData()
  } catch (error) {
    message.type = 'error'
    message.text = error?.message || '操作失败'
  } finally {
    actionKey.value = ''
  }
}

function isSelected(path) {
  return selectedPaths.value.includes(path)
}

function toggleHistorySelection(path) {
  if (!path) {
    return
  }
  if (isSelected(path)) {
    selectedPaths.value = selectedPaths.value.filter((item) => item !== path)
    return
  }
  selectedPaths.value = [...selectedPaths.value, path]
}

function selectAllHistory() {
  selectedPaths.value = historyItems.value.map((item) => item.path).filter(Boolean)
}

function clearHistorySelection() {
  selectedPaths.value = []
}

async function deleteSelectedHistory() {
  if (!selectedPaths.value.length) {
    return
  }
  if (!window.confirm(`确认删除已选的 ${selectedPaths.value.length} 张历史封面吗？`)) {
    return
  }
  const current = [...selectedPaths.value]
  await runAction('delete-selected', `${pluginBase}/delete_saved_cover`, { files: current })
  selectedPaths.value = []
}

async function deleteSingleHistory(item) {
  if (!item?.path) {
    return
  }
  if (!window.confirm(`确认删除 ${item.name || '这张封面'} 吗？`)) {
    return
  }
  await runAction(`delete-${item.path}`, `${pluginBase}/delete_saved_cover`, { file: item.path })
  selectedPaths.value = selectedPaths.value.filter((path) => path !== item.path)
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.cover-page {
  display: grid;
  gap: 16px;
  padding: 20px;
  background:
    radial-gradient(circle at top left, rgba(var(--v-theme-primary), 0.08), transparent 28%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), 1) 0%, rgba(var(--v-theme-surface-variant), 0.16) 100%);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(var(--v-border-color), 0.16);
  background: rgba(var(--v-theme-surface), 0.92);
  box-shadow: 0 18px 42px rgba(var(--v-border-color), 0.12);
}

.hero-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-primary), 0.88);
}

.hero-title {
  margin: 8px 0 0;
  font-size: clamp(26px, 4vw, 36px);
  line-height: 1.08;
}

.hero-meta {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.hero-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.summary-card {
  padding: 20px !important;
}

.summary-main {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.4;
}

.summary-sub {
  margin-top: 6px;
  font-size: 13px;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.style-card {
  cursor: pointer;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.style-card:hover {
  transform: translateY(-2px);
  border-color: rgba(var(--v-theme-primary), 0.28);
}

.style-card.selected {
  border-color: rgba(var(--v-theme-primary), 0.5);
  box-shadow: 0 0 0 1px rgba(var(--v-theme-primary), 0.18);
}

.history-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.history-card:hover {
  transform: translateY(-2px);
}

.history-card.selected {
  border-color: rgba(var(--v-theme-primary), 0.5);
  box-shadow: 0 0 0 1px rgba(var(--v-theme-primary), 0.18);
}

.history-check {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
}

.history-name {
  min-height: 2.8em;
  overflow-wrap: anywhere;
}

.clean-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

@media (max-width: 720px) {
  .cover-page {
    padding: 16px;
  }

  .hero-card,
  .summary-card {
    padding: 16px;
  }

  .hero-actions {
    width: 100%;
  }
}
</style>
