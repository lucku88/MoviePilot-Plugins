<template>
  <v-textarea
    v-bind="$attrs"
    :model-value="modelValue"
    class="mp-textarea"
    variant="outlined"
    density="comfortable"
    auto-grow
    rows="2"
    max-rows="4"
    hide-details="auto"
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
:deep(.mp-textarea .v-field) {
  border-radius: var(--mp-radius-md);
  background: var(--mp-bg-input);
}

:deep(.mp-textarea .v-field__input),
:deep(.mp-textarea .v-label),
:deep(.mp-textarea .v-field__outline) {
  color: var(--mp-text-primary);
}

:deep(.mp-textarea textarea) {
  font-size: var(--mp-font-md);
  line-height: 1.55;
}
</style>
