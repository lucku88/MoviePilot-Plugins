import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const THEME_MAP = [
  { match: /transparent|glass|blur|透明/i, value: 'transparent', label: '透明' },
  { match: /purple|violet|fantasy|幻紫/i, value: 'purple', label: '幻紫' },
  { match: /dark|night|深色/i, value: 'dark', label: '深色' },
  { match: /light|浅色/i, value: 'light', label: '浅色' },
]

function parseColorToken(value, fallback) {
  const text = String(value || '').trim()
  if (!text) return fallback
  if (/^\d+\s*,\s*\d+\s*,\s*\d+/.test(text)) return `rgb(${text})`
  return text
}

function luminanceFromColor(color) {
  const match = String(color || '').match(/rgba?\(([^)]+)\)/i)
  if (!match) return 255
  const [r, g, b] = match[1].split(',').slice(0, 3).map((item) => Number.parseFloat(item.trim()) || 0)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function hasThemeHint(className = '') {
  return className.includes('theme')
    || className.includes('v-theme--')
    || className.includes('dark')
    || className.includes('light')
    || className.includes('purple')
    || className.includes('transparent')
}

function isInternalThemeNode(node) {
  const className = String(node?.className || '').toLowerCase()
  return className.includes('mp-theme-')
    || className.includes('vpp-theme-')
    || className.includes('mp-panel')
    || className.includes('vuepanel-page')
}

export function usePanelTheme(rootEl) {
  const themeName = ref('light')
  const themeLabel = ref('浅色')
  const themeStyle = reactive({})

  let themeObserver = null
  let mediaQuery = null

  function resolveThemeNode() {
    let current = rootEl?.value?.parentElement || rootEl?.value
    while (current) {
      if (!isInternalThemeNode(current) && current.getAttribute?.('data-theme')) return current
      const className = String(current.className || '').toLowerCase()
      if (!isInternalThemeNode(current) && hasThemeHint(className)) return current
      current = current.parentElement
    }

    const body = document.body
    const root = document.documentElement
    if (body && !isInternalThemeNode(body)) {
      const bodyClass = String(body.className || '').toLowerCase()
      if (body.getAttribute?.('data-theme') || hasThemeHint(bodyClass)) return body
    }
    if (root && !isInternalThemeNode(root)) {
      const rootClass = String(root.className || '').toLowerCase()
      if (root.getAttribute?.('data-theme') || hasThemeHint(rootClass)) return root
    }
    return body || root
  }

  function resolveThemeValue(node) {
    const raw = `${node?.getAttribute?.('data-theme') || ''} ${node?.className || ''}`.trim()
    for (const item of THEME_MAP) {
      if (item.match.test(raw)) return item
    }
    return null
  }

  function readHostColor(node, names, fallback) {
    const style = window.getComputedStyle(node)
    for (const name of names) {
      const value = style.getPropertyValue(name)
      if (value) return parseColorToken(value, fallback)
    }
    return fallback
  }

  function updateTheme() {
    const node = resolveThemeNode()
    const detected = resolveThemeValue(node)
    const style = window.getComputedStyle(node)
    const pageBg = parseColorToken(style.backgroundColor, '#eef3fb')
    const text = parseColorToken(style.color, '#182132')
    const prefersDark = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches

    if (detected) {
      themeName.value = detected.value
      themeLabel.value = detected.label
    } else {
      const bgLuminance = luminanceFromColor(pageBg)
      themeName.value = bgLuminance < 140 || prefersDark ? 'dark' : 'custom'
      themeLabel.value = themeName.value === 'dark' ? '深色' : '自定义'
    }

    themeStyle['--mp-host-primary'] = readHostColor(node, ['--v-theme-primary', '--theme-primary'], '#4f86ff')
    themeStyle['--mp-host-secondary'] = readHostColor(node, ['--v-theme-secondary', '--theme-secondary'], '#8b5cf6')
    themeStyle['--mp-host-surface'] = readHostColor(node, ['--v-theme-surface', '--theme-surface'], '#ffffff')
    themeStyle['--mp-host-background'] = readHostColor(node, ['--v-theme-background', '--theme-background'], pageBg)
    themeStyle['--mp-host-on-surface'] = readHostColor(node, ['--v-theme-on-surface', '--theme-on-surface'], text)
    themeStyle['--mp-host-muted'] = readHostColor(node, ['--v-theme-on-surface-variant', '--theme-muted'], '#64748b')
    themeStyle['--mp-host-outline'] = readHostColor(node, ['--v-border-color', '--theme-border'], 'rgba(15, 23, 42, 0.14)')
  }

  function bindThemeObserver() {
    updateTheme()
    if (window.MutationObserver) {
      themeObserver = new MutationObserver(updateTheme)
      ;[resolveThemeNode(), document.documentElement, document.body].filter(Boolean).forEach((node) => {
        themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class', 'style'] })
      })
    }
    if (window.matchMedia) {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener?.('change', updateTheme)
    }
  }

  onMounted(bindThemeObserver)
  onBeforeUnmount(() => {
    themeObserver?.disconnect?.()
    mediaQuery?.removeEventListener?.('change', updateTheme)
  })

  return {
    themeName,
    themeLabel,
    themeStyle,
    themeClass: computed(() => `mp-theme-${themeName.value}`),
  }
}
