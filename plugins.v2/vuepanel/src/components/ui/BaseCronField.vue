<template>
  <v-text-field
    v-bind="$attrs"
    :model-value="modelValue"
    class="mp-cron"
    variant="outlined"
    density="compact"
    prepend-inner-icon="mdi-clock-time-four-outline"
    placeholder="例如：24 0 * * *"
    @update:model-value="emit('update:modelValue', normalizeCron($event))"
  />
</template>

<script setup>
defineOptions({ inheritAttrs: false })

defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function normalizeCron(value) {
  return String(value || '').replace(/\s+/g, ' ').trim()
}
</script>

<style scoped>
:deep(.mp-cron .v-field) {
  border-radius: var(--mp-radius-md);
  background: var(--mp-bg-input);
}

:deep(.mp-cron .v-field__input),
:deep(.mp-cron .v-label),
:deep(.mp-cron .v-field__outline) {
  color: var(--mp-text-primary);
}
</style>
