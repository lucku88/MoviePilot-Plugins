import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const pageSource = readFileSync(new URL('../src/components/Page.vue', import.meta.url), 'utf8')

assert.match(
  pageSource,
  /:class="\{ 'is-backend-reloading': backendUpdate\.loading \}"/,
  '状态页应在后端重载期间进入统一的交互锁定状态',
)
assert.match(
  pageSource,
  /:aria-busy="backendUpdate\.loading"/,
  '状态页应向辅助设备标记后端重载中的忙碌状态',
)
assert.match(
  pageSource,
  /\.vpp-shell\.is-backend-reloading\s*>\s*:not\(\.vpp-version-alert\)[\s\S]*?pointer-events:\s*none/,
  '除版本提示外的页面操作在重载期间必须禁止点击',
)
