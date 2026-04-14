<template>
  <PageView
    :api="api"
    :initial-config="initialConfig"
    :theme-name="themeName"
    :theme-label="themeLabel"
    @close="emit('close')"
  />
</template>

<script setup>
import PageView from './Page.vue'

defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

const emit = defineEmits(['close'])
</script>
