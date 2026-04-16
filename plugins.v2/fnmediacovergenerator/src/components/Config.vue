<template>
  <section class="cfg-shell">
    <div class="cfg-head">
      <div>
        <div class="cfg-kicker">FnMediaCoverGenerator</div>
        <h2 class="cfg-title">插件配置</h2>
      </div>
      <div class="d-flex flex-wrap ga-2">
        <v-btn variant="text" color="primary" @click="emit('switch')">查看页面</v-btn>
        <v-btn variant="flat" color="primary" :loading="saving" :disabled="loading || !formItems.length" @click="saveConfig">保存配置</v-btn>
      </div>
    </div>

    <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
      {{ message.text }}
    </v-alert>

    <v-skeleton-loader v-if="loading" type="article, article, article" />

    <template v-else>
      <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4">
        {{ loadError }}
      </v-alert>

      <div v-if="formItems.length" class="cfg-form">
        <FormRender
          v-for="(item, index) in formItems"
          :key="index"
          :config="item"
          :model="configForm"
        />
      </div>

      <v-alert v-else type="warning" variant="tonal">
        未读取到配置表单，请检查插件是否已正确加载。
      </v-alert>
    </template>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import FormRender from './FormRender.vue'

const PLUGIN_ID = 'FnMediaCoverGenerator'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const loading = ref(true)
const saving = ref(false)
const loadError = ref('')
const formItems = ref([])
const configForm = reactive({})
const message = reactive({ text: '', type: 'info' })

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value ?? {}))
}

function assignModel(target, payload) {
  Object.keys(target).forEach((key) => {
    delete target[key]
  })
  Object.entries(payload || {}).forEach(([key, value]) => {
    target[key] = value
  })
}

async function loadSchema() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await props.api.get(`plugin/form/${PLUGIN_ID}`)
    formItems.value = Array.isArray(result?.conf) ? result.conf : []
    assignModel(configForm, cloneValue(result?.model || props.initialConfig))
  } catch (error) {
    formItems.value = []
    assignModel(configForm, cloneValue(props.initialConfig))
    loadError.value = error?.message || '加载配置表单失败'
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  message.text = ''
  try {
    const result = await props.api.put(`plugin/${PLUGIN_ID}`, cloneValue(configForm))
    if (result?.success === false) {
      throw new Error(result?.message || '配置保存失败')
    }
    message.type = 'success'
    message.text = result?.message || '配置已保存'
  } catch (error) {
    message.type = 'error'
    message.text = error?.message || '配置保存失败'
  } finally {
    saving.value = false
  }
}

loadSchema()
</script>

<style scoped>
.cfg-shell {
  display: grid;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(180deg, rgba(var(--v-theme-surface), 1) 0%, rgba(var(--v-theme-surface-variant), 0.18) 100%);
}

.cfg-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.cfg-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-primary), 0.88);
}

.cfg-title {
  margin: 6px 0 0;
  font-size: 28px;
  line-height: 1.1;
}

.cfg-form {
  display: grid;
  gap: 12px;
}

@media (max-width: 720px) {
  .cfg-shell {
    padding: 16px;
  }

  .cfg-title {
    font-size: 24px;
  }
}
</style>
