<template>
  <VCronField
    v-bind="$attrs"
    :model-value="modelValue"
    class="mp-cron"
    density="comfortable"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>

<script setup>
defineOptions({ inheritAttrs: false })

defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
:deep(.mp-cron .v-field) {
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-card) 88%, transparent);
}

:deep(.mp-cron .v-field__input),
:deep(.mp-cron .v-label),
:deep(.mp-cron .v-field__outline) {
  color: var(--mp-text-primary);
}
</style>
