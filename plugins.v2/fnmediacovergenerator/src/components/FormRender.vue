<script setup>
import { h, resolveComponent } from 'vue'

defineProps({
  config: {
    type: Object,
    required: true,
  },
  model: {
    type: Object,
    required: true,
  },
})

const isExpression = (value) => typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}')
const extractExpression = (value) => value.slice(2, -2).trim()

const parseProps = (rawProps = {}, model) => {
  const parsedProps = {}

  Object.entries(rawProps).forEach(([key, value]) => {
    if (key === 'modelvalue') {
      parsedProps.value = model[value]
      parsedProps['onUpdate:value'] = (newValue) => {
        model[value] = newValue
      }
      return
    }

    if (key === 'model' || key === 'v-model') {
      parsedProps.modelValue = model[value]
      parsedProps['onUpdate:modelValue'] = (newValue) => {
        model[value] = newValue
      }
      return
    }

    if (key.startsWith('model:') || key.startsWith('v-model:')) {
      const propName = key.split(':')[1]
      parsedProps[propName] = model[value]
      parsedProps[`onUpdate:${propName}`] = (newValue) => {
        model[value] = newValue
      }
      return
    }

    if (typeof value === 'string' && isExpression(value)) {
      const expression = extractExpression(value)
      parsedProps[key] = new Function('model', `with(model) { return ${expression} }`)(model)
      return
    }

    if (typeof value === 'string' && value in model) {
      parsedProps[key] = model[value]
      return
    }

    parsedProps[key] = value
  })

  return parsedProps
}

const renderComponent = (config, model) => {
  const { component, props: componentProps = {}, content = [], html, text } = config
  const Component = resolveComponent(component)
  const parsedProps = parseProps(componentProps, model)

  const renderContent = () => {
    if (html) {
      return h(Component, { innerHTML: typeof html === 'string' ? html : model[html] })
    }
    if (text !== undefined) {
      return typeof text === 'string' ? text : model[text]
    }
    if (Array.isArray(content)) {
      return content.map((childConfig) => renderComponent(childConfig, model))
    }
    return null
  }

  return h(Component, parsedProps, {
    default: renderContent,
  })
}
</script>

<template>
  <Component :is="renderComponent(config, model)" />
</template>
