<template>
  <v-text-field
    v-bind="$attrs"
    :model-value="modelValue"
    class="mp-input"
    variant="outlined"
    density="comfortable"
    hide-details="auto"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>

<script setup>
defineOptions({ inheritAttrs: false })

defineProps({
  modelValue: { type: [String, Number], default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
:deep(.mp-input .v-field) {
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-card) 88%, transparent);
  color: var(--mp-text-primary);
}

:deep(.mp-input .v-field__input),
:deep(.mp-input .v-label),
:deep(.mp-input .v-field__outline),
:deep(.mp-input .v-field__append-inner) {
  color: var(--mp-text-primary);
}

:deep(.mp-input .v-field__input) {
  min-height: 40px;
  padding-top: 0;
  padding-bottom: 0;
  font-size: var(--mp-font-md);
}

:deep(.mp-input .v-field__outline) {
  --v-field-border-opacity: 1;
}
</style>
