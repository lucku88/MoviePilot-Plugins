import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VUEPILL_DIR = ROOT / "plugins.v2" / "vuepill"
PAGE_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "components" / "Page.vue"
CONFIG_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "components" / "Config.vue"
APP_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "App.vue"
INDEX_PATH = ROOT / "plugins.v2" / "vuepill" / "index.html"
DIST_STYLE_PATH = ROOT / "plugins.v2" / "vuepill" / "dist" / "assets" / "style.css"
ASYNC_GUARD_PATH = (
    ROOT / "plugins.v2" / "vuepill" / "src" / "utils" / "asyncGuards.js"
)
CONFIG_VALIDATION_PATH = (
    ROOT / "plugins.v2" / "vuepill" / "src" / "utils" / "configValidation.js"
)


class VuePillFrontendContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE_PATH.read_text(encoding="utf-8")
        cls.config = CONFIG_PATH.read_text(encoding="utf-8")
        cls.config_validation = CONFIG_VALIDATION_PATH.read_text(encoding="utf-8")
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.index = INDEX_PATH.read_text(encoding="utf-8")
        cls.dist_style = DIST_STYLE_PATH.read_text(encoding="utf-8")
        cls.template = cls.page.split("<script setup>", 1)[0]
        cls.compact_page = re.sub(r"\s+", "", cls.page)
        cls.compact_template = re.sub(r"\s+", "", cls.template)
        cls.compact_config = re.sub(r"\s+", "", cls.config)
        cls.compact_dist_style = re.sub(r"\s+", "", cls.dist_style)
        cls.mobile_css = cls.compact_page.split(
            "@media(max-width:600px){", 1
        )[1].rsplit("</style>", 1)[0]

    def assert_page_contains(self, *tokens):
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.page)

    def assert_config_contains(self, *tokens):
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.config)

    def test_config_uses_vuefarm_shell_grids_and_theme_tokens(self):
        self.assert_config_contains(
            'class="siqi-config"',
            'class="siqi-topbar"',
            "siqi-topbar__left",
            "siqi-topbar__right",
            "siqi-switch-grid",
            "siqi-form-grid",
            "rgba(var(--v-theme-on-surface)",
            "rgba(var(--v-theme-surface)",
        )
        self.assertNotRegex(self.config, r'class="[^"]*\bvp-')
        self.assertNotIn("is-dark-theme", self.config)

    def test_config_uses_exact_public_field_whitelist_and_vuefarm_cron(self):
        expected_fields = {
            "enabled",
            "notify",
            "onlyonce",
            "use_proxy",
            "cookie",
            "enable_brick",
            "enable_beach",
            "auto_craft",
            "auto_exchange",
            "brick_cron",
            "schedule_buffer_seconds",
            "reserve_magic_pill_count",
            "random_delay_max_seconds",
            "http_timeout",
            "http_retry_times",
            "http_retry_delay",
        }
        field_block = re.search(
            r"const\s+CONFIG_FIELDS\s*=\s*Object\.freeze\(\[(.*?)\]\)",
            self.config,
            re.DOTALL,
        )
        self.assertIsNotNone(field_block, "配置页必须显式声明提交白名单")
        actual_fields = set(re.findall(r"['\"]([a-z0-9_]+)['\"]", field_block.group(1)))
        self.assertEqual(expected_fields, actual_fields)
        self.assert_config_contains(
            "VCronField",
            'v-model="config.brick_cron"',
            "reserve_magic_pill_count",
            "启用插件",
            "通知",
            "立即运行一次",
            "代理",
            "自动搬砖",
            "动态清沙滩",
            "自动炼造",
            "自动兑换",
            "搬砖 Cron",
            "冷却缓冲",
            "保留魔丸",
            "随机延迟",
            "请求超时",
            "网络重试次数",
            "重试间隔",
        )
        self.assertNotIn("保留材料数量", self.config)

    def test_config_cookie_matches_vuefarm_editable_secret_control(self):
        self.assertIn('v-model="config.cookie"', self.config)
        self.assertIn("站点 Cookie", self.config)
        self.assertIn("showCookie", self.config)
        self.assertIn("cookieAutoFilled", self.config)
        self.assertIn("cookieEdited", self.config)
        self.assertIn("markCookieEdited", self.config)
        self.assertIn("mdi-eye-outline", self.config)
        self.assertIn("mdi-eye-off-outline", self.config)
        self.assertIn("手动 Cookie 优先", self.config)
        self.assertIn("清空后恢复自动同步", self.config)
        self.assertNotIn("auto_cookie", self.config)
        self.assertNotIn("/cookie", self.config)
        self.assertNotIn("syncCookie", self.config)
        self.assertRegex(
            self.config,
            r"<v-textarea[^>]+v-model=\"config\.cookie\"",
        )

    def test_config_defaults_ranges_and_backend_validation_match(self):
        self.assertRegex(self.config, r"brick_cron:\s*['\"]5 0 \* \* \*['\"]")
        self.assertRegex(self.config, r"reserve_magic_pill_count:\s*10\b")
        self.assertRegex(
            self.config,
            r'<v-text-field[^>]+v-model="config\.http_retry_times"[^>]+max="5"',
        )
        self.assertRegex(
            self.config,
            r'<v-text-field[^>]+v-model="config\.http_timeout"[^>]+min="5"',
        )
        self.assertRegex(
            self.config,
            r'<v-text-field[^>]+v-model="config\.http_retry_delay"[^>]+min="200"[^>]+max="60000"',
        )

    def test_config_uses_executable_validation_and_field_errors(self):
        self.assert_config_contains(
            "validateVuePillConfig",
            "const fieldErrors = reactive({})",
            "focusFirstError",
            "validation.firstErrorField",
            "if (!validation.valid)",
            "data-config-field=\"brick_cron\"",
            "fieldErrors.brick_cron",
        )
        self.assertIn("export function parseStrictInteger", self.config_validation)
        self.assertIn("export function validateCronExpression", self.config_validation)
        self.assertIn("export function validateVuePillConfig", self.config_validation)
        self.assertNotIn("v-model.number", self.config)

    def test_config_removes_legacy_ipv4_field_and_migration_warning(self):
        self.assertNotIn("force_ipv4", self.config)
        self.assertNotIn("force_ipv4", self.config_validation)
        self.assertNotIn("强制IPv4", self.config)
        self.assertNotIn("v0.2.0 升级提示", self.config)
        self.assertNotIn("升级后请确认设置再手动开启", self.config)
        self.assertNotIn("siqi-migration-note", self.config)

    def test_config_validation_runtime_rejects_noncanonical_values(self):
        script = r"""
import assert from 'node:assert/strict'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const validationUrl = pathToFileURL(
  path.resolve('src/utils/configValidation.js'),
).href
const {
  DEFAULT_CONFIG,
  INTEGER_CONFIG_RULES,
  validateManualCookie,
  parseStrictInteger,
  validateCronExpression,
  validateVuePillConfig,
} = await import(`${validationUrl}?t=${Date.now()}`)

const sampleRule = { label: '测试字段', min: 0, max: 100 }
for (const value of ['', ' ', '1.5', '1e2', 'NaN', '0x10', '+12', '-1', '01', '12 ']) {
  assert.equal(parseStrictInteger(value, sampleRule).valid, false, String(value))
}
for (const value of [NaN, Infinity, -Infinity, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
  assert.equal(parseStrictInteger(value, sampleRule).valid, false, String(value))
}
assert.deepEqual(parseStrictInteger('12', sampleRule), { valid: true, value: 12, error: '' })
assert.deepEqual(parseStrictInteger(12, sampleRule), { valid: true, value: 12, error: '' })
assert.equal(parseStrictInteger(-1, sampleRule).valid, false)
assert.equal(parseStrictInteger(101, sampleRule).valid, false)

for (const [field, rule] of Object.entries(INTEGER_CONFIG_RULES)) {
  for (const value of [rule.min, String(rule.min), rule.max, String(rule.max)]) {
    const parsed = parseStrictInteger(value, rule)
    assert.equal(parsed.valid, true, `${field}: ${String(value)}`)
    assert.equal(typeof parsed.value, 'number')
  }
  assert.equal(parseStrictInteger(rule.min - 1, rule).valid, false, `${field}: min`)
  assert.equal(parseStrictInteger(rule.max + 1, rule).valid, false, `${field}: max`)
}

for (const value of [
  '',
  ' ',
  '* * * *',
  '* * * * * *',
  '* * * * *\n',
  '60 * * * *',
  '* 24 * * *',
  '* * 0 * *',
  '* * * 13 *',
  '* * * * 8',
  '*/0 * * * *',
  '5-1 * * * *',
  '1,,2 * * * *',
  'foo * * * *',
  '* * * foo *',
  '* * * * foo',
]) {
  assert.equal(validateCronExpression(value).valid, false, JSON.stringify(value))
}
for (const [value, normalized] of [
  ['  5   0 * * *  ', '5 0 * * *'],
  ['*/5 * * * *', '*/5 * * * *'],
  ['0,15,30,45 * * * *', '0,15,30,45 * * * *'],
  ['0-59/5 0-23/2 1-31/3 1-12/2 0-6', '0-59/5 0-23/2 1-31/3 1-12/2 0-6'],
  ['0 0 * JAN MON-FRI', '0 0 * jan mon-fri'],
]) {
  assert.deepEqual(
    validateCronExpression(value),
    { valid: true, value: normalized, error: '' },
    value,
  )
}

const source = {
  ...DEFAULT_CONFIG,
  enabled: true,
  notify: false,
  force_ipv4: true,
  brick_cron: ' 5 0 * * * ',
  schedule_buffer_seconds: '12',
  reserve_magic_pill_count: '10',
  random_delay_max_seconds: '3',
  http_timeout: '12',
  http_retry_times: '5',
  http_retry_delay: '1500',
  cookie: 'sid=manual-cookie-secret',
  unknown_secret: 'must-not-leak',
}
const validation = validateVuePillConfig(source)
assert.equal(validation.valid, true)
assert.equal(validation.payload.brick_cron, '5 0 * * *')
for (const field of Object.keys(INTEGER_CONFIG_RULES)) {
  assert.equal(typeof validation.payload[field], 'number', field)
}
for (const field of [
  'enabled', 'notify', 'onlyonce', 'use_proxy',
  'enable_brick', 'enable_beach', 'auto_craft', 'auto_exchange',
]) {
  assert.equal(typeof validation.payload[field], 'boolean', field)
}
assert.equal(Object.hasOwn(validation.payload, 'force_ipv4'), false)
assert.equal(validation.payload.cookie, 'sid=manual-cookie-secret')
assert.equal(Object.hasOwn(validation.payload, 'unknown_secret'), false)
assert.equal(validateManualCookie('').valid, true)
assert.equal(validateManualCookie('sid=manual-cookie-secret').valid, true)
assert.equal(validateManualCookie('cookie').valid, false)
assert.equal(validateManualCookie('sid=safe\r\nX-Test: value').valid, false)
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=VUEPILL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_config_runtime_keeps_unedited_site_cookie_in_auto_sync_mode(self):
        script = r"""
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { compileScript, parse } from '@vue/compiler-sfc'

const filename = path.resolve('src/components/Config.vue')
const source = await fs.readFile(filename, 'utf8')
const parsed = parse(source, { filename })
assert.deepEqual(parsed.errors, [])
const compiled = compileScript(parsed.descriptor, { id: 'vuepill-cookie-runtime' })
const tempFile = path.join(
  path.dirname(filename),
  `.Config.cookie-runtime-${process.pid}-${Date.now()}.mjs`,
)

const baseConfig = {
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
}
const siteCookie = 'sid=latest-site-cookie; token=latest-site-token'
let currentConfig = {
  ...baseConfig,
  cookie: siteCookie,
  cookie_auto_filled: true,
  cookie_source: '站点同步：si-qi.xyz',
}
const posts = []
const api = {
  get: async () => ({ ...currentConfig }),
  post: async (url, payload) => {
    posts.push({ url, payload: { ...payload } })
    currentConfig = payload.cookie
      ? {
          ...baseConfig,
          cookie: payload.cookie,
          cookie_auto_filled: false,
          cookie_source: '手动配置',
        }
      : {
          ...baseConfig,
          cookie: siteCookie,
          cookie_auto_filled: true,
          cookie_source: '站点同步：si-qi.xyz',
        }
    return { success: true, message: '配置已保存' }
  },
}

const originalWarn = console.warn
const originalSetTimeout = globalThis.setTimeout
const originalClearTimeout = globalThis.clearTimeout
try {
  await fs.writeFile(tempFile, compiled.content, 'utf8')
  const component = (await import(`${pathToFileURL(tempFile).href}?t=${Date.now()}`)).default
  console.warn = () => {}
  const bindings = component.setup(
    { api, initialConfig: {} },
    { attrs: {}, slots: {}, emit() {}, expose() {} },
  )
  console.warn = originalWarn
  globalThis.setTimeout = callback => { callback(); return 1 }
  globalThis.clearTimeout = () => {}

  await bindings.loadConfig()
  assert.equal(bindings.config.cookie, siteCookie)
  assert.equal(bindings.cookieAutoFilled.value, true)
  assert.equal(bindings.cookieEdited.value, false)

  await bindings.saveConfig()
  assert.equal(posts[0].payload.cookie, '')
  assert.equal(bindings.config.cookie, siteCookie)
  assert.equal(bindings.cookieAutoFilled.value, true)
  assert.equal(bindings.cookieEdited.value, false)

  bindings.config.cookie = 'sid=manual-cookie-secret'
  bindings.markCookieEdited()
  await bindings.saveConfig()
  assert.equal(posts[1].payload.cookie, 'sid=manual-cookie-secret')
  assert.equal(bindings.cookieAutoFilled.value, false)
  assert.equal(bindings.cookieEdited.value, false)

  bindings.config.cookie = ''
  bindings.markCookieEdited()
  await bindings.saveConfig()
  assert.equal(posts[2].payload.cookie, '')
  assert.equal(bindings.config.cookie, siteCookie)
  assert.equal(bindings.cookieAutoFilled.value, true)
  assert.equal(bindings.cookieEdited.value, false)
} finally {
  console.warn = originalWarn
  globalThis.setTimeout = originalSetTimeout
  globalThis.clearTimeout = originalClearTimeout
  await fs.rm(tempFile, { force: true })
}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=VUEPILL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_config_runtime_blocks_invalid_save_and_reloads_missing_config(self):
        script = r"""
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { compileScript, parse } from '@vue/compiler-sfc'

const filename = path.resolve('src/components/Config.vue')
const source = await fs.readFile(filename, 'utf8')
const parsed = parse(source, { filename })
assert.deepEqual(parsed.errors, [])
const compiled = compileScript(parsed.descriptor, { id: 'vuepill-config-validation-runtime' })
const tempFile = path.join(
  path.dirname(filename),
  `.Config.validation-runtime-${process.pid}-${Date.now()}.mjs`,
)

const normalizedConfig = {
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
}
const posts = []
let getCalls = 0
const api = {
  get: async () => {
    getCalls += 1
    return { ...normalizedConfig }
  },
  post: async (url, payload) => {
    posts.push({ url, payload: { ...payload } })
    if (posts.length === 1) return { success: true, message: '配置已保存' }
    if (posts.length === 2) {
      return {
        success: false,
        message: '搬砖 Cron 不是有效表达式',
        errors: { brick_cron: '搬砖 Cron 不是有效表达式' },
      }
    }
    return {
      success: true,
      message: '配置已保存',
      config: { ...payload, onlyonce: false },
    }
  },
}

let focused = 0
let focusedSelector = ''
const originalDocument = globalThis.document
const originalWarn = console.warn
const originalSetTimeout = globalThis.setTimeout
const originalClearTimeout = globalThis.clearTimeout
try {
  await fs.writeFile(tempFile, compiled.content, 'utf8')
  const component = (await import(`${pathToFileURL(tempFile).href}?t=${Date.now()}`)).default
  console.warn = () => {}
  const bindings = component.setup(
    { api, initialConfig: { force_ipv4: true } },
    { attrs: {}, slots: {}, emit() {}, expose() {} },
  )
  console.warn = originalWarn
  globalThis.setTimeout = callback => { callback(); return 1 }
  globalThis.clearTimeout = () => {}
  globalThis.document = {
    querySelector(selector) {
      focusedSelector = selector
      return {
        querySelector() {
          return { focus() { focused += 1 } }
        },
      }
    },
  }

  assert.equal(Object.hasOwn(bindings.config, 'force_ipv4'), false)

  bindings.config.schedule_buffer_seconds = '1.5'
  await bindings.saveConfig()
  assert.equal(posts.length, 0)
  assert.match(bindings.fieldErrors.schedule_buffer_seconds, /整数/)
  assert.equal(focused, 1)
  assert.match(focusedSelector, /schedule_buffer_seconds/)
  assert.equal(bindings.config.schedule_buffer_seconds, '1.5')

  bindings.config.schedule_buffer_seconds = '5'
  bindings.config.brick_cron = '* * * *'
  await bindings.saveConfig()
  assert.equal(posts.length, 0)
  assert.match(bindings.fieldErrors.brick_cron, /5 段/)

  Object.assign(bindings.config, {
    ...normalizedConfig,
    onlyonce: true,
    brick_cron: ' 5 0 * * * ',
    schedule_buffer_seconds: '5',
    reserve_magic_pill_count: '10',
    random_delay_max_seconds: '3',
    http_timeout: '12',
    http_retry_times: '5',
    http_retry_delay: '1500',
    cookie: 'sid=manual-cookie-secret',
  })
  await bindings.saveConfig()
  assert.equal(posts.length, 1)
  assert.equal(getCalls, 1)
  assert.equal(posts[0].payload.onlyonce, true)
  assert.equal(posts[0].payload.brick_cron, '5 0 * * *')
  assert.equal(typeof posts[0].payload.schedule_buffer_seconds, 'number')
  assert.equal(Object.hasOwn(posts[0].payload, 'force_ipv4'), false)
  assert.equal(posts[0].payload.cookie, 'sid=manual-cookie-secret')
  assert.equal(bindings.config.onlyonce, false)

  await bindings.saveConfig()
  assert.equal(posts.length, 2)
  assert.equal(posts[1].payload.onlyonce, false)
  assert.equal(bindings.fieldErrors.brick_cron, '搬砖 Cron 不是有效表达式')
  assert.equal(focused, 3)
  assert.match(focusedSelector, /brick_cron/)
  assert.equal(bindings.config.onlyonce, false)

  await bindings.saveConfig()
  assert.equal(posts.length, 3)
  assert.equal(posts[2].payload.onlyonce, false)
} finally {
  globalThis.document = originalDocument
  console.warn = originalWarn
  globalThis.setTimeout = originalSetTimeout
  globalThis.clearTimeout = originalClearTimeout
  await fs.rm(tempFile, { force: true })
}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=VUEPILL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_config_save_is_strict_guarded_and_whitelisted(self):
        self.assert_config_contains(
            "const CONFIG_ENDPOINT = '/plugin/VuePill/config'",
            "createLatestRequestGuard",
            "const loadRequestGuard = createLatestRequestGuard()",
            "const saveRequestGuard = createLatestRequestGuard()",
            "loadRequestGuard.begin()",
            "loadRequestGuard.isCurrent(requestId)",
            "saveRequestGuard.begin()",
            "saveRequestGuard.isCurrent(requestId)",
            "loadRequestGuard.invalidate()",
            "saveRequestGuard.invalidate()",
            "buildConfigPayload",
            "isStrictSuccess(result)",
            "safeResponseMessage(result, '配置已保存')",
            "if (formLocked.value) return",
            "isCompletePublicConfig(result?.config)",
            "applyPublicConfig(result.config)",
            "config.onlyonce = false",
            "await loadConfig({ silent: true })",
        )
        self.assertRegex(
            self.config,
            r"props\.api\.post\(CONFIG_ENDPOINT,\s*payload\)",
        )
        self.assertNotIn("success !== false", self.config)
        self.assertNotRegex(
            self.config,
            r"props\.api\.post\([^\n]+\{\s*\.\.\.config",
        )

    def test_config_locks_every_control_during_load_and_save(self):
        self.assert_config_contains(
            "const configLoading = ref(false)",
            "const configSaving = ref(false)",
            "const formLocked = computed(() => configLoading.value || configSaving.value || upgradeRestartRequired.value)",
            '<fieldset',
            ':disabled="formLocked"',
            ':inert="formLocked"',
            ':aria-busy="formLocked"',
            'v-if="configLoading"',
            ':loading="configSaving"',
            "正在加载配置，请稍候",
        )
        self.assertNotIn("pointer-events:none", self.compact_config)

        for tag_name in ("v-switch", "v-text-field"):
            tags = re.findall(rf"<{tag_name}\b[^>]+>", self.config, re.DOTALL)
            self.assertTrue(tags, f"未找到 {tag_name}")
            for tag in tags:
                with self.subTest(tag_name=tag_name, tag=tag[:80]):
                    self.assertIn(':disabled="formLocked"', tag)

        cron_tag = re.search(r"<VCronField\b[^>]+>", self.config, re.DOTALL)
        self.assertIsNotNone(cron_tag)
        self.assertIn(':disabled="formLocked"', cron_tag.group(0))

        for aria_label in ("状态页", "保存配置"):
            button = re.search(
                rf'<v-btn\b[^>]+aria-label="{aria_label}"[^>]+>',
                self.config,
                re.DOTALL,
            )
            self.assertIsNotNone(button, f"未找到按钮：{aria_label}")
            self.assertIn(':disabled="formLocked"', button.group(0))

    def test_config_upgrade_restart_gate_is_conditional_and_read_only(self):
        self.assert_config_contains(
            "const upgradeRestartRequired = ref(false)",
            "upgrade_restart_required",
            "v-if=\"upgradeRestartRequired\"",
            "请重启 MoviePilot 完成 Vue-魔丸 v0.2.0 升级",
            "upgradeRestartRequired.value",
        )

        field_block = re.search(
            r"const\s+CONFIG_FIELDS\s*=\s*Object\.freeze\(\[(.*?)\]\)",
            self.config,
            re.DOTALL,
        )
        self.assertIsNotNone(field_block)
        self.assertNotIn("upgrade_restart_required", field_block.group(1))

        default_block = re.search(
            r"const\s+DEFAULT_CONFIG\s*=\s*Object\.freeze\(\{(.*?)\}\)",
            self.config,
            re.DOTALL,
        )
        self.assertIsNotNone(default_block)
        self.assertNotIn("upgrade_restart_required", default_block.group(1))

        save_button = re.search(
            r'<v-btn\b[^>]+aria-label="保存配置"[^>]+>',
            self.config,
            re.DOTALL,
        )
        close_button = re.search(
            r'<v-btn\b[^>]+aria-label="关闭配置"[^>]+>',
            self.config,
            re.DOTALL,
        )
        self.assertIsNotNone(save_button)
        self.assertIsNotNone(close_button)
        self.assertIn(':disabled="formLocked"', save_button.group(0))
        self.assertNotIn(":disabled=", close_button.group(0))

    def test_config_upgrade_restart_gate_reads_initial_and_get_state(self):
        script = r"""
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { compileScript, parse } from '@vue/compiler-sfc'

const filename = path.resolve('src/components/Config.vue')
const source = await fs.readFile(filename, 'utf8')
const parsed = parse(source, { filename })
assert.deepEqual(parsed.errors, [])
const compiled = compileScript(parsed.descriptor, { id: 'vuepill-restart-gate-runtime' })
const tempFile = path.join(
  path.dirname(filename),
  `.Config.restart-gate-runtime-${process.pid}-${Date.now()}.mjs`,
)

const normalizedConfig = {
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
}
let restartRequired = true
const posts = []
const api = {
  get: async () => ({ ...normalizedConfig, upgrade_restart_required: restartRequired }),
  post: async (url, payload) => {
    posts.push({ url, payload: { ...payload } })
    return { success: true, message: '配置已保存', config: { ...payload, onlyonce: false } }
  },
}

const originalWarn = console.warn
const originalSetTimeout = globalThis.setTimeout
const originalClearTimeout = globalThis.clearTimeout
try {
  await fs.writeFile(tempFile, compiled.content, 'utf8')
  const component = (await import(`${pathToFileURL(tempFile).href}?t=${Date.now()}`)).default
  console.warn = () => {}
  const bindings = component.setup(
    { api, initialConfig: { ...normalizedConfig, upgrade_restart_required: true } },
    { attrs: {}, slots: {}, emit() {}, expose() {} },
  )
  console.warn = originalWarn
  globalThis.setTimeout = callback => { callback(); return 1 }
  globalThis.clearTimeout = () => {}

  assert.equal(bindings.upgradeRestartRequired.value, true)
  assert.equal(bindings.formLocked.value, true)
  assert.equal(Object.hasOwn(bindings.config, 'upgrade_restart_required'), false)

  await bindings.saveConfig()
  assert.equal(posts.length, 0)

  restartRequired = false
  await bindings.loadConfig()
  assert.equal(bindings.upgradeRestartRequired.value, false)
  assert.equal(bindings.formLocked.value, false)

  await bindings.saveConfig()
  assert.equal(posts.length, 1)
  assert.equal(Object.hasOwn(posts[0].payload, 'upgrade_restart_required'), false)
} finally {
  console.warn = originalWarn
  globalThis.setTimeout = originalSetTimeout
  globalThis.clearTimeout = originalClearTimeout
  await fs.rm(tempFile, { force: true })
}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=VUEPILL_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_config_latest_load_always_applies_complete_whitelist(self):
        load_block = self.config.split("async function loadConfig", 1)[1].split(
            "async function saveConfig", 1
        )[0]
        self.assertIn("loadRequestGuard.begin()", load_block)
        self.assertIn("if (!loadRequestGuard.isCurrent(requestId)) return", load_block)
        self.assertIn("applyPublicConfig(data)", load_block)
        self.assertNotIn("formRevision", load_block)
        self.assertNotIn("revisionAtStart", load_block)
        self.assertNotIn("watch(config", self.config)
        self.assertNotIn("formRevision", self.config)

    def test_config_runtime_preserves_failure_and_applies_onlyonce_reset(self):
        script = r"""
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { compileScript, parse } from '@vue/compiler-sfc'

const filename = path.resolve('src/components/Config.vue')
const source = await fs.readFile(filename, 'utf8')
const parsed = parse(source, { filename })
assert.deepEqual(parsed.errors, [])
const compiled = compileScript(parsed.descriptor, { id: 'vuepill-config-runtime' })
const tempFile = path.join(
  path.dirname(filename),
  `.Config.runtime-${process.pid}-${Date.now()}.mjs`,
)

let resolveSuccess
let responseMode = 'failure'
const posts = []
const api = {
  get: async () => { throw new Error('unexpected reload') },
  post: async (url, payload) => {
    posts.push({ url, payload: { ...payload } })
    if (responseMode === 'failure') {
      return { success: false, message: '保存失败' }
    }
    if (posts.length === 2) {
      await new Promise(resolve => { resolveSuccess = resolve })
    }
    return {
      success: true,
      message: '配置已保存',
      config: { ...payload, onlyonce: false },
    }
  },
}

const originalWarn = console.warn
const originalSetTimeout = globalThis.setTimeout
const originalClearTimeout = globalThis.clearTimeout
try {
  await fs.writeFile(tempFile, compiled.content, 'utf8')
  const component = (await import(`${pathToFileURL(tempFile).href}?t=${Date.now()}`)).default
  console.warn = () => {}
  const bindings = component.setup(
    { api, initialConfig: {} },
    { attrs: {}, slots: {}, emit() {}, expose() {} },
  )
  console.warn = originalWarn
  globalThis.setTimeout = callback => { callback(); return 1 }
  globalThis.clearTimeout = () => {}

  bindings.config.onlyonce = true
  bindings.config.notify = false
  await bindings.saveConfig()
  assert.equal(posts.length, 1)
  assert.equal(posts[0].payload.onlyonce, true)
  assert.equal(bindings.config.onlyonce, true)
  assert.equal(bindings.config.notify, false)
  assert.equal(bindings.formLocked.value, false)

  responseMode = 'success'
  const successfulSave = bindings.saveConfig()
  const duplicateSave = bindings.saveConfig()
  await duplicateSave
  assert.equal(posts.length, 2)
  assert.equal(bindings.formLocked.value, true)
  assert.equal(bindings.configSaving.value, true)
  resolveSuccess()
  await successfulSave
  assert.equal(bindings.config.onlyonce, false)
  assert.equal(bindings.config.notify, false)
  assert.equal(bindings.formLocked.value, false)

  await bindings.saveConfig()
  assert.equal(posts.length, 3)
  assert.equal(posts[2].payload.onlyonce, false)
} finally {
  console.warn = originalWarn
  globalThis.setTimeout = originalSetTimeout
  globalThis.clearTimeout = originalClearTimeout
  await fs.rm(tempFile, { force: true })
}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=VUEPILL_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_config_responsive_layout_prevents_horizontal_scroll(self):
        self.assert_config_contains(
            "@media(max-width:900px)",
            "@media(max-width:600px)",
            "overflow-x:hidden",
            "min-height:44px",
        )
        self.assertRegex(
            self.compact_config,
            r"@media\(max-width:600px\)\{[^}]*\.siqi-config\{[^}]*padding:14px",
        )
        self.assertRegex(
            self.compact_config,
            r"@media\(max-width:600px\)\{.*?\.siqi-topbar\{[^}]*flex-direction:column",
        )
        self.assertRegex(
            self.compact_config,
            r"@media\(max-width:600px\)\{.*?\.siqi-topbar__right\{[^}]*width:100%",
        )

    def test_uses_vuefarm_visual_shell_and_theme_tokens(self):
        self.assert_page_contains(
            'class="siqi-page"',
            'class="siqi-topbar"',
            "siqi-topbar__left",
            "siqi-topbar__right",
            "siqi-card",
            "rgba(var(--v-theme-on-surface)",
            "rgba(var(--v-theme-surface)",
        )
        self.assertNotRegex(self.page, r'class="[^"]*\bvp-')
        self.assertNotIn("#f8f7ff", self.app)

    def test_visual_shell_matches_siqifram_theme(self):
        topbar = self.page.split('<div class="siqi-content">', 1)[0]
        self.assertIn('color="success"', topbar)
        self.assertNotIn('color="orange-darken-1"', topbar)
        self.assertIn(
            "background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))",
            self.compact_page,
        )
        self.assertRegex(
            self.compact_page,
            r"\.siqi-topbar__icon\{[^}]*background:rgba\(76,175,80,.14\)[^}]*color:#2e7d32",
        )
        self.assertNotIn("rgba(245,158,11,.035)", self.compact_page)
        self.assertRegex(
            self.compact_page,
            r"\.stat-card\{[^}]*background:rgba\(var\(--v-theme-(?:surface|on-surface)\),\.[0-9]+\)",
        )
        for tone in ("orange", "green", "blue", "red"):
            with self.subTest(tone=tone):
                self.assertRegex(
                    self.compact_page,
                    rf"\.stat-{tone}\{{[^}}]*--stat-rgb:",
                )
                self.assertNotRegex(
                    self.compact_page,
                    rf"\.stat-{tone}\{{[^}}]*background:",
                )

        self.assertIn(
            "background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))",
            self.compact_config,
        )
        self.assertRegex(
            self.compact_config,
            r"\.siqi-card\{[^}]*background:rgba\(var\(--v-theme-on-surface\),.03\)",
        )
        self.assertNotIn("background:rgba(var(--v-theme-surface),.5)", self.compact_config)
        self.assertNotIn("background:rgba(var(--v-theme-surface),.34)", self.compact_config)

    def test_status_sections_follow_required_order(self):
        markers = (
            "siqi-topbar",
            'v-for="item in overview"',
            "/>动态任务",
            "兑换魔力",
            "物品栏",
            "炼造工坊",
            "执行历史",
        )
        positions = [self.page.find(marker) for marker in markers]
        self.assertNotIn(-1, positions, f"页面缺少分区标记：{markers}")
        self.assertEqual(positions, sorted(positions))

    def test_dynamic_tasks_use_siqifarm_interaction_card_style(self):
        self.assert_page_contains(
            'class="siqi-card schedule-board mb-3"',
            'class="schedule-action-list"',
            "neu-action-card--brick",
            "neu-action-card--beach",
            "今日已完成",
            "冷却中",
            "可以搬砖",
            "可以清理",
        )
        for forbidden in (
            "dynamic-schedule-card",
            "schedule-card--brick",
            "schedule-card--beach",
            "后端标记可执行",
            "后端标记不可执行",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.page)

    def test_task_first_header_and_schedule_grid(self):
        self.assert_page_contains(
            'class="schedule-summary"',
            ':class="{ active: scheduleSummary.active }"',
            "scheduleSummary.text",
            "enabled: false",
            "next_run_time: ''",
            "next_trigger_time: ''",
            "next_trigger_action: ''",
            "function applyStatusMeta(target, meta)",
            "applyStatusMeta(status, update.statusMeta)",
            "function buildScheduleSummary(state = {})",
            "const scheduleSummary = computed(() => buildScheduleSummary(status))",
            "function compactScheduleTime(value)",
            "compactScheduleTime(nextTime)",
            "自动运行正常",
            "等待识别下一次任务",
            "brick.ready === true ? '立即搬砖' : brickStatusLabel",
            "beachActionable ? '清理沙滩' : beachStatusLabel",
        )

        summary = re.search(
            r'<div\s+class="schedule-summary"[\s\S]*?</div>', self.page
        )
        self.assertIsNotNone(summary)
        if summary:
            self.assertIn("<v-icon", summary.group(0))
            self.assertIn("scheduleSummary.text", summary.group(0))
        self.assertRegex(
            self.compact_page,
            r"\.schedule-summary\{[^}]*rgba\(var\(--v-theme-on-surface\)",
        )
        self.assertRegex(
            self.compact_page,
            r"\.schedule-summary\.active\{[^}]*rgba\(34,197,94",
        )
        self.assertRegex(
            self.compact_page,
            r"\.siqi-topbar__right\{[^}]*gap:",
        )
        self.assertRegex(
            self.compact_page,
            r"\.schedule-action-list\{[^}]*display:grid[^}]*grid-template-columns:repeat\(2,minmax\(0,1fr\)\)",
        )
        self.assertRegex(
            self.compact_page,
            r"\.neu-action-card\{[^}]*grid-template-columns:32pxminmax\(0,1fr\)[^}]*align-items:start",
        )
        self.assertRegex(
            self.compact_page,
            r"\.schedule-action\{[^}]*grid-column:1/-1[^}]*width:100%",
        )

        mobile_task_css = re.search(
            r"@media\(max-width:700px\)\{([\s\S]*?)@media\(max-width:600px\)\{",
            self.compact_page,
        )
        self.assertIsNotNone(mobile_task_css)
        if mobile_task_css:
            self.assertRegex(
                mobile_task_css.group(1),
                r"\.schedule-action-list\{[^}]*grid-template-columns:1fr",
            )
            self.assertRegex(
                mobile_task_css.group(1),
                r"\.schedule-summary\{[^}]*display:none",
            )

    def test_task_first_layout_has_mobile_and_theme_guards(self):
        self.assert_page_contains(
            "@media(max-width:1100px)",
            "@media(max-width:700px)",
            "overflow-x:hidden",
            "rgba(var(--v-theme-on-surface)",
            "rgba(var(--v-theme-surface)",
        )
        self.assertNotIn("后端上限", self.page)
        self.assertNotIn("后端返回最大可炼造数量为 0", self.page)
        self.assertNotRegex(
            self.template,
            r"<span(?:\s+[^>]*)?>\s*(?:当前不可赠送|不可赠送)\s*</span>",
        )
        self.assertRegex(
            self.template,
            r'<div class="exchange-stat">\s*<span>最多兑换</span>\s*<strong>\{\{\s*exchange\.max_count\s*\?\?\s*0\s*\}\}</strong>\s*<small>颗</small>\s*</div>',
        )

        mobile_layout = re.search(
            r"@media\(max-width:700px\)\{([\s\S]*?)@media\(max-width:600px\)\{",
            self.compact_page,
        )
        self.assertIsNotNone(mobile_layout)
        if mobile_layout:
            mobile_css = mobile_layout.group(1)
            self.assertRegex(
                mobile_css,
                r"\.overview-grid\{[^}]*grid-template-columns:repeat\(2,minmax\(0,1fr\)\)",
            )
            self.assertRegex(
                mobile_css,
                r"\.primary-grid\{[^}]*grid-template-columns:1fr",
            )
            self.assertRegex(
                mobile_css,
                r"\.schedule-action-list\{[^}]*grid-template-columns:1fr",
            )
            self.assertRegex(
                mobile_css,
                r"\.inventory-grid\{[^}]*grid-template-columns:repeat\(3,minmax\(0,1fr\)\)",
            )
            self.assertRegex(
                mobile_css,
                r"\.recipe-grid\{[^}]*grid-template-columns:1fr",
            )
            self.assertRegex(
                mobile_css,
                r"\.schedule-summary\{[^}]*display:none",
            )

    def test_task_first_skeleton_matches_loaded_layout(self):
        skeleton = self.page.split(
            '<div v-if="initialLoading" class="page-skeleton">', 1
        )[1].split("<template v-else>", 1)[0]

        self.assertIn('class="overview-grid mb-3"', skeleton)
        self.assertIn('v-for="index in 4"', skeleton)
        self.assertIn('class="primary-grid mb-3"', skeleton)
        self.assertIn('class="schedule-action-list"', skeleton)
        self.assertIn('v-for="index in 2"', skeleton)
        self.assertIn("exchange-skeleton", skeleton)
        self.assertIn('class="inventory-grid"', skeleton)
        self.assertIn('v-for="index in 7"', skeleton)
        self.assertIn('class="recipe-grid"', skeleton)
        self.assertIn('v-for="index in 3"', skeleton)
        self.assertIn("history-skeleton", skeleton)
        self.assertNotIn("<v-btn", skeleton)

    def test_compact_schedule_time_requires_complete_timestamp(self):
        function_match = re.search(
            r"function compactScheduleTime\(value\) \{[\s\S]*?\n\}",
            self.page,
        )
        self.assertIsNotNone(function_match)

        script = f"""
import assert from 'node:assert/strict'

{function_match.group(0)}

assert.equal(compactScheduleTime('2026-08-02 11:25:58'), '08-02 11:25')
assert.equal(compactScheduleTime('2026-08-02 11:25'), '2026-08-02 11:25')
assert.equal(compactScheduleTime(' 2026-08-02 11:25:58 '), ' 2026-08-02 11:25:58 ')
assert.equal(compactScheduleTime('2026-08-02 11:25:58 extra'), '2026-08-02 11:25:58 extra')
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_schedule_summary_and_status_meta_execute_production_functions(self):
        def extract_function(name):
            match = re.search(
                rf"function {name}\([^)]*\) \{{[\s\S]*?\n\}}",
                self.page,
            )
            self.assertIsNotNone(match, f"Page.vue 必须声明纯函数 {name}")
            return match.group(0)

        production_source = "\n\n".join(
            extract_function(name)
            for name in (
                "compactScheduleTime",
                "applyStatusMeta",
                "buildScheduleSummary",
            )
        )
        script = f"""
import assert from 'node:assert/strict'

const source = {json.dumps(production_source, ensure_ascii=False)}
const functions = new Function(
  source + '\\nreturn {{ compactScheduleTime, applyStatusMeta, buildScheduleSummary }}',
)()
const {{ applyStatusMeta, buildScheduleSummary }} = functions

assert.deepEqual(
  buildScheduleSummary({{ enabled: false }}),
  {{ active: false, text: '自动运行未启用' }},
)
assert.deepEqual(
  buildScheduleSummary({{ enabled: true }}),
  {{ active: false, text: '等待识别下一次任务' }},
)

const fullState = {{
  enabled: true,
  next_run_time: '2026-08-02 11:20:00',
  next_trigger_time: '2026-08-02 11:25:58',
  next_trigger_action: '清沙滩',
}}
assert.deepEqual(
  buildScheduleSummary(fullState),
  {{ active: true, text: '自动运行正常 · 下一项：清沙滩 08-02 11:25' }},
)

const partialState = {{ ...fullState, next_trigger_action: '搬砖' }}
const retainedTime = partialState.next_trigger_time
assert.equal(
  applyStatusMeta(partialState, {{ next_trigger_action: '清沙滩' }}),
  partialState,
)
assert.equal(partialState.next_trigger_time, retainedTime)
assert.deepEqual(
  buildScheduleSummary(partialState),
  {{ active: true, text: '自动运行正常 · 下一项：清沙滩 08-02 11:25' }},
)

assert.deepEqual(
  buildScheduleSummary({{
    enabled: true,
    next_run_time: '2026-08-03 09:40:00',
    next_trigger_time: '2026-08-03 09:45:00',
    next_trigger_action: '兑换',
  }}),
  {{ active: true, text: '自动运行正常 · 下一项：兑换 08-03 09:45' }},
)
assert.deepEqual(
  buildScheduleSummary({{
    enabled: true,
    next_run_time: '明天上午',
    next_trigger_action: '任务',
  }}),
  {{ active: true, text: '自动运行正常 · 下一项：任务 明天上午' }},
)

const retainedMeta = {{
  enabled: true,
  next_run_time: '旧时间',
  next_trigger_action: '旧动作',
}}
applyStatusMeta(retainedMeta, null)
applyStatusMeta(retainedMeta, undefined)
applyStatusMeta(retainedMeta, {{}})
assert.deepEqual(retainedMeta, {{
  enabled: true,
  next_run_time: '旧时间',
  next_trigger_action: '旧动作',
}})
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_page_matches_siqifram_card_density(self):
        self.assertRegex(
            self.compact_page,
            r"\.siqi-card-title\{[^}]*min-height:44px",
        )
        for tone in ("orange", "green", "blue", "red"):
            with self.subTest(tone=tone):
                self.assertNotRegex(
                    self.compact_page,
                    rf"\.stat-{tone}\{{[^}}]*background:",
                )

    def test_numeric_config_fields_are_vertically_centered(self):
        self.assertGreaterEqual(self.config.count("siqi-number-input"), 6)
        self.assertRegex(
            self.config,
            r'<style>[\s\S]*?\.siqi-config\s+\.siqi-number-input\s+\[class~="v-field__input"\]\{[^}]*align-items:center',
        )
        self.assertRegex(
            self.config,
            r'<style>[\s\S]*?\.siqi-config\s+\.siqi-number-input\s+\[class~="v-field__prepend-inner"\]\{[^}]*align-self:center',
        )
        self.assertRegex(
            self.dist_style,
            r'\.siqi-config\s+\.siqi-number-input\s+\[class~="v-field__input"\]\{[^}]*align-items:center',
        )
        self.assertRegex(
            self.dist_style,
            r'\.siqi-config\s+\.siqi-number-input\s+\[class~="v-field__prepend-inner"\]\{[^}]*align-self:center',
        )

    def test_uses_vuepill_api_namespace_and_real_action_paths(self):
        self.assertRegex(self.page, r"const\s+PLUGIN_ID\s*=\s*['\"]VuePill['\"]")
        self.assert_page_contains(
            "/plugin/${PLUGIN_ID}",
            "/status",
            "/refresh",
            "/move-bricks",
            "/clean-beach",
            "/exchange-points",
            "/craft-item",
            "/craft-max-pill",
            "/gift-item",
            "/gift-stats",
        )
        self.assertNotIn("/run", self.page)

    def test_gift_dialog_has_validation_confirmation_and_busy_feedback(self):
        self.assert_page_contains(
            "v-dialog",
            "gift-item",
            "target_uid",
            "quantity",
            "确认赠送",
            "再次确认",
            "取消",
            ":loading=",
            ":disabled=",
        )
        self.assertRegex(self.page, r'aria-label="[^"]+"')
        self.assert_page_contains(
            ':persistent="giftLoading"',
            "if (giftLoading.value) return",
            "giftConfirmationSnapshot",
            "giftDialogToken",
            "giftRequestGuard",
            "sameGiftSnapshot",
        )

    def test_gift_stats_supports_direction_range_and_summaries(self):
        self.assert_page_contains(
            "gift-stats",
            "giftStatsDraftDirection",
            "giftStatsDraftRange",
            "giftStatsAppliedDirection",
            "giftStatsAppliedRange",
            "giftStatsRequestGuard",
            "resolveGiftStatsFilters",
            'v-model="giftStatsDraftDirection"',
            'v-model="giftStatsDraftRange"',
            "最近30天",
            "全部",
            "赠出",
            "收到",
            "总事件数",
            "总数量",
            "用户汇总",
            "物品汇总",
        )
        self.assertRegex(
            self.page,
            r'<v-btn-toggle[^>]+v-model="giftStatsDraftDirection"[^>]+:disabled="giftStatsLoading"',
        )
        self.assertRegex(
            self.page,
            r'<v-btn-toggle[^>]+v-model="giftStatsDraftRange"[^>]+:disabled="giftStatsLoading"',
        )
        self.assertIn("giftStatsRequestGuard.isCurrent(requestId)", self.page)

    def test_initial_loading_and_status_requests_are_guarded(self):
        self.assert_page_contains(
            "createLatestRequestGuard",
            "const statusRequestGuard = createLatestRequestGuard()",
            "const writeActionsDisabled = computed(() => initialLoading.value",
            "statusRequestGuard.begin()",
            "statusRequestGuard.isCurrent(requestId)",
            "statusRequestGuard.invalidate()",
            "if (initialLoading.value || actionLoading.value) return null",
            ':disabled="initialLoading || giftStatsLoading"',
        )
        self.assertGreaterEqual(self.page.count("writeActionsDisabled"), 8)

    def test_pending_beach_trash_remains_manually_actionable(self):
        self.assert_page_contains(
            "const beachActionable = computed(",
            "beach.value.ready === true",
            "beach.value.can_collect === true",
            "beach.value.has_trash === true",
            ':disabled="writeActionsDisabled || !beachActionable"',
        )

    def test_post_actions_require_explicit_success(self):
        self.assertGreaterEqual(self.page.count("isStrictSuccess(result)"), 3)
        self.assertIn("safeResponseMessage", self.page)
        self.assertIn("extractStatusPayload", self.page)
        self.assertIn("const actionRequestGuard = createLatestRequestGuard()", self.page)
        self.assertNotRegex(self.page, r"\.success\s*!==\s*false")

        run_action = self.page.split("async function runAction", 1)[1].split(
            "function quantityError", 1
        )[0]
        strict_action_check = "if (!isStrictSuccess(result))"
        self.assertIn(strict_action_check, run_action)
        self.assertNotIn("!statusApplied ||", run_action)
        self.assertLess(
            run_action.index("applyStatusPayload(result)"),
            run_action.index(strict_action_check),
        )
        self.assertIn("if (!statusApplied) await loadStatus({ silent: true })", run_action)
        self.assertIn("actionRequestGuard.isCurrent(requestId)", run_action)

        submit_gift = self.page.split("async function submitGift", 1)[1].split(
            "async function openGiftStats", 1
        )[0]
        self.assertIn(strict_action_check, submit_gift)
        self.assertNotIn("!statusApplied ||", submit_gift)
        self.assertLess(
            submit_gift.index("applyStatusPayload(result)"),
            submit_gift.index(strict_action_check),
        )
        self.assertIn("if (!statusApplied) await loadStatus({ silent: true })", submit_gift)

    def test_async_guard_runtime_rejects_stale_requests_and_invalid_success(self):
        script = f"""
import assert from 'node:assert/strict'
import {{
  createLatestRequestGuard,
  isStrictSuccess,
  resolveGiftStatsFilters,
  safeResponseMessage,
}} from {ASYNC_GUARD_PATH.as_uri()!r}

const guard = createLatestRequestGuard()
const first = guard.begin()
const second = guard.begin()
assert.equal(guard.isCurrent(first), false)
assert.equal(guard.isCurrent(second), true)
guard.invalidate()
assert.equal(guard.isCurrent(second), false)

const responseGuard = createLatestRequestGuard()
const applied = []
let resolveOld
let resolveNew
const oldResponse = new Promise(resolve => {{ resolveOld = resolve }})
const newResponse = new Promise(resolve => {{ resolveNew = resolve }})
const applyLatest = async promise => {{
  const requestId = responseGuard.begin()
  const value = await promise
  if (responseGuard.isCurrent(requestId)) applied.push(value)
}}
const oldRun = applyLatest(oldResponse)
const newRun = applyLatest(newResponse)
resolveNew('new-filter')
await newRun
resolveOld('old-filter')
await oldRun
assert.deepEqual(applied, ['new-filter'])

assert.equal(isStrictSuccess(null), false)
assert.equal(isStrictSuccess({{}}), false)
assert.equal(isStrictSuccess({{ success: 'true' }}), false)
assert.equal(isStrictSuccess({{ success: false }}), false)
assert.equal(isStrictSuccess({{ success: true }}), true)

const requested = {{ direction: 'out', range: '30' }}
assert.deepEqual(
  resolveGiftStatsFilters({{ direction: 'in', range: 'all' }}, requested),
  {{ direction: 'in', range: 'all' }},
)
assert.deepEqual(
  resolveGiftStatsFilters({{ direction: 'sideways', range: 30 }}, requested),
  requested,
)
assert.equal(safeResponseMessage({{ message: {{ bad: true }} }}, 'fallback'), 'fallback')
assert.equal(safeResponseMessage({{ message: '  ok  ' }}, 'fallback'), 'ok')
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_partial_failure_runtime_applies_valid_status_without_success(self):
        script = f"""
import assert from 'node:assert/strict'
import {{
  extractStatusPayload,
  isStrictSuccess,
  safeResponseMessage,
}} from {ASYNC_GUARD_PATH.as_uri()!r}

const latestPillStatus = {{
  schema_version: '0.2.0',
  overview: [{{ label: '当前魔丸数', value: 2 }}],
  brick: {{}},
  beach: {{}},
  exchange: {{ max_count: 3, reserve: 10 }},
  inventory: {{ items: [{{ name: '魔丸', count: 2 }}] }},
  recipes: [{{ craft_id: 6, max_count: 1, enabled: true }}],
  history: [{{ text: '旧记录', time: '11:59' }}],
}}
const response = {{
  success: false,
  message: '部分完成',
  pill_status: latestPillStatus,
  status: {{ history: [{{ text: '炼造 2 颗', time: '12:00' }}] }},
}}
const current = {{ pill_status: {{ inventory: {{ items: [] }} }}, history: [] }}
const update = extractStatusPayload(response)
assert.deepEqual(update, {{
  pillStatus: latestPillStatus,
  history: response.status.history,
  statusMeta: {{}},
}})
current.pill_status = update.pillStatus
current.history = update.history
assert.equal(current.pill_status.inventory.items[0].count, 2)
assert.equal(current.pill_status.recipes[0].max_count, 1)
assert.equal(current.pill_status.exchange.max_count, 3)
assert.equal(isStrictSuccess(response), false)
assert.equal(safeResponseMessage(response, '炼造失败'), '部分完成')

const emptyFullStatus = {{
  overview: [],
  brick: {{}},
  beach: {{}},
  exchange: {{}},
  inventory: {{ items: [] }},
  recipes: [],
  history: [],
}}
assert.deepEqual(
  extractStatusPayload({{ pill_status: emptyFullStatus }}),
  {{ pillStatus: emptyFullStatus, history: [], statusMeta: {{}} }},
)

assert.equal(extractStatusPayload(null), null)
assert.equal(extractStatusPayload({{}}), null)
assert.equal(extractStatusPayload({{ pill_status: {{ overview: [] }} }}), null)
assert.equal(extractStatusPayload({{ pill_status: {{ exchange: {{}} }} }}), null)
assert.equal(extractStatusPayload({{
  pill_status: {{ overview: [{{ label: '魔力', value: 1 }}] }},
}}), null)
assert.equal(extractStatusPayload({{ success: false, pill_status: {{ forged: true }} }}), null)
assert.equal(extractStatusPayload({{ success: false, status: {{ pill_status: [] }} }}), null)

const mismatches = [
  {{ ...emptyFullStatus, overview: {{}} }},
  {{ ...emptyFullStatus, overview: [null] }},
  {{ ...emptyFullStatus, brick: [] }},
  {{ ...emptyFullStatus, beach: null }},
  {{ ...emptyFullStatus, exchange: [] }},
  {{ ...emptyFullStatus, inventory: [] }},
  {{ ...emptyFullStatus, inventory: {{ items: {{}} }} }},
  {{ ...emptyFullStatus, inventory: {{ items: [[]] }} }},
  {{ ...emptyFullStatus, recipes: {{}} }},
  {{ ...emptyFullStatus, recipes: [null] }},
  {{ ...emptyFullStatus, history: {{}} }},
  {{ ...emptyFullStatus, history: ['bad'] }},
]
for (const pillStatus of mismatches) {{
  assert.equal(extractStatusPayload({{ pill_status: pillStatus }}), null)
}}

const customPrototype = Object.assign(Object.create({{ inherited: true }}), emptyFullStatus)
assert.equal(extractStatusPayload({{ pill_status: customPrototype }}), null)
const nullPrototype = Object.assign(Object.create(null), emptyFullStatus)
assert.equal(extractStatusPayload({{ pill_status: nullPrototype }}), null)
const oddRecipes = []
Object.setPrototypeOf(oddRecipes, {{}})
assert.equal(
  extractStatusPayload({{ pill_status: {{ ...emptyFullStatus, recipes: oddRecipes }} }}),
  null,
)
let getterReads = 0
const accessorStatus = {{ ...emptyFullStatus }}
Object.defineProperty(accessorStatus, 'overview', {{
  enumerable: true,
  get() {{
    getterReads += 1
    return []
  }},
}})
assert.equal(extractStatusPayload({{ pill_status: accessorStatus }}), null)
assert.equal(getterReads, 0)

const forgedSuccess = {{ success: true, pill_status: {{ forged: true }} }}
assert.equal(isStrictSuccess(forgedSuccess), true)
assert.equal(extractStatusPayload(forgedSuccess), null)
const incompleteFailure = {{ success: false, pill_status: {{ overview: [] }} }}
assert.equal(isStrictSuccess(incompleteFailure), false)
assert.equal(extractStatusPayload(incompleteFailure), null)
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_status_payload_keeps_scheduler_metadata(self):
        script = f"""
import assert from 'node:assert/strict'
import {{ extractStatusPayload }} from {ASYNC_GUARD_PATH.as_uri()!r}

const pillStatus = {{
  overview: [],
  brick: {{}},
  beach: {{}},
  exchange: {{}},
  inventory: {{ items: [] }},
  recipes: [],
  history: [],
}}

const directResponse = {{
  pill_status: pillStatus,
  enabled: true,
  next_run_time: '2026-08-02 12:00:00',
  next_trigger_time: '2026-08-02 12:05:00',
  next_trigger_action: 'forge',
  last_run_time: 'must not leak',
}}
assert.deepEqual(extractStatusPayload(directResponse), {{
  pillStatus,
  history: [],
  statusMeta: {{
    enabled: true,
    next_run_time: '2026-08-02 12:00:00',
    next_trigger_time: '2026-08-02 12:05:00',
    next_trigger_action: 'forge',
  }},
}})

const nestedResponse = {{
  status: {{
    pill_status: pillStatus,
    enabled: false,
    next_run_time: '2026-08-03 08:00:00',
    next_trigger_time: '2026-08-03 08:10:00',
    next_trigger_action: 'collect',
    scheduler_token: 'must not leak',
  }},
}}
assert.deepEqual(extractStatusPayload(nestedResponse), {{
  pillStatus,
  history: [],
  statusMeta: {{
    enabled: false,
    next_run_time: '2026-08-03 08:00:00',
    next_trigger_time: '2026-08-03 08:10:00',
    next_trigger_action: 'collect',
  }},
}})

assert.deepEqual(extractStatusPayload({{ pill_status: pillStatus }}), {{
  pillStatus,
  history: [],
  statusMeta: {{}},
}})

const mixedResponse = {{
  pill_status: pillStatus,
  enabled: true,
  next_run_time: 'direct run',
  next_trigger_time: 'direct trigger',
  next_trigger_action: 'direct action',
  status: {{
    enabled: false,
    next_trigger_time: 'nested trigger',
  }},
}}
assert.deepEqual(extractStatusPayload(mixedResponse).statusMeta, {{
  enabled: false,
  next_trigger_time: 'nested trigger',
  next_run_time: 'direct run',
  next_trigger_action: 'direct action',
}})

const wrongTypes = {{
  pill_status: pillStatus,
  enabled: 'true',
  next_run_time: 123,
  next_trigger_time: null,
  next_trigger_action: false,
}}
assert.deepEqual(extractStatusPayload(wrongTypes).statusMeta, {{}})

let getterReads = 0
const accessorStatus = {{ next_run_time: 'must be ignored' }}
Object.defineProperty(accessorStatus, 'enabled', {{
  enumerable: true,
  get() {{
    getterReads += 1
    return true
  }},
}})
assert.deepEqual(
  extractStatusPayload({{ pill_status: pillStatus, status: accessorStatus }}).statusMeta,
  {{}},
)
assert.equal(getterReads, 0)

const customPrototypeStatus = Object.assign(
  Object.create({{ enabled: true }}),
  {{ next_run_time: 'must be ignored' }},
)
assert.deepEqual(
  extractStatusPayload({{ pill_status: pillStatus, status: customPrototypeStatus }}).statusMeta,
  {{}},
)

const originalEnabledDescriptor = Object.getOwnPropertyDescriptor(
  Object.prototype,
  'enabled',
)
const originalNextRunTimeDescriptor = Object.getOwnPropertyDescriptor(
  Object.prototype,
  'next_run_time',
)
let inheritedEnabledWrites = 0
try {{
  Object.defineProperty(Object.prototype, 'enabled', {{
    configurable: true,
    set() {{
      inheritedEnabledWrites += 1
    }},
  }})
  Object.defineProperty(Object.prototype, 'next_run_time', {{
    configurable: true,
    value: 'polluted run time',
    writable: false,
  }})

  const pollutedMeta = extractStatusPayload({{
    pill_status: pillStatus,
    enabled: true,
    next_run_time: 'safe run time',
  }}).statusMeta
  assert.equal(Object.getPrototypeOf(pollutedMeta), Object.prototype)
  assert.deepEqual(Object.getOwnPropertyDescriptor(pollutedMeta, 'enabled'), {{
    value: true,
    enumerable: true,
    configurable: true,
    writable: true,
  }})
  assert.deepEqual(Object.getOwnPropertyDescriptor(pollutedMeta, 'next_run_time'), {{
    value: 'safe run time',
    enumerable: true,
    configurable: true,
    writable: true,
  }})
  assert.equal(inheritedEnabledWrites, 0)
}} finally {{
  if (originalEnabledDescriptor) {{
    Object.defineProperty(Object.prototype, 'enabled', originalEnabledDescriptor)
  }} else {{
    delete Object.prototype.enabled
  }}
  if (originalNextRunTimeDescriptor) {{
    Object.defineProperty(
      Object.prototype,
      'next_run_time',
      originalNextRunTimeDescriptor,
    )
  }} else {{
    delete Object.prototype.next_run_time
  }}
}}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_inventory_recipes_and_exchange_use_backend_limits(self):
        self.assert_page_contains(
            "inventory.items",
            'v-for="recipe in recipes"',
            "recipe.craft_id",
            "recipe.ingredients",
            "recipe.max_count",
            "recipe.enabled",
            "exchange.max_count",
            "reserve",
        )
        self.assertRegex(self.page, r':max="[^\"]*recipe\.max_count')
        self.assertRegex(self.page, r':max="[^\"]*exchange\.max_count')
        self.assertIn("exchange.value.reserve", self.page)
        self.assertNotIn("reserve_count", self.page)
        self.assertNotIn("reserve_magic_pill_count", self.page)
        self.assertNotIn("后端未返回 reserve", self.page)
        self.assertNotRegex(
            self.page,
            r"exchange(?:\.value)?\.reserve\s*(?:\?\?|\|\|)\s*10",
        )
        self.assertNotRegex(
            self.compact_page,
            r"exchangeReserve=computed\([^}]*:10\}",
        )

    def test_inventory_and_workshop_use_full_width_compact_grids(self):
        self.assertRegex(
            self.compact_page,
            r"\.resource-grid\{[^}]*grid-template-columns:1fr",
        )
        self.assertRegex(
            self.compact_page,
            r"\.inventory-grid\{[^}]*grid-template-columns:repeat\(7,minmax\(0,1fr\)\)",
        )
        self.assertRegex(
            self.compact_page,
            r"\.recipe-grid\{[^}]*grid-template-columns:repeat\(3,minmax\(0,1fr\)\)",
        )
        self.assert_page_contains(
            "inventoryCounts",
            "ingredientCount",
            "ingredientEnough",
            "gift-item--static",
            'v-if="canGiftItem(item)"',
            "{{ name }} {{ ingredientCount(name) }}/{{ required }}",
            "'ingredient-ready': ingredientEnough(name, required)",
        )
        self.assertRegex(
            self.compact_page,
            r"\.gift-item--static:disabled\{[^}]*opacity:1[^}]*cursor:default",
        )
        self.assertRegex(
            self.compact_page,
            r"@media\(max-width:1100px\)\{.*?\.inventory-grid\{[^}]*repeat\(5,minmax\(0,1fr\)\).*?\.recipe-grid\{[^}]*repeat\(2,minmax\(0,1fr\)\)",
        )
        self.assertRegex(
            self.compact_page,
            r"@media\(max-width:700px\)\{.*?\.inventory-grid\{[^}]*repeat\(3,minmax\(0,1fr\)\).*?\.recipe-grid\{[^}]*grid-template-columns:1fr",
        )
        self.assertRegex(
            self.compact_page,
            r"@media\(max-width:900px\)\{.*?\.stats-columns\{[^}]*grid-template-columns:1fr",
        )
        self.assertNotRegex(
            self.mobile_css,
            r"\.inventory-grid\{[^}]*grid-template-columns:1fr",
        )

    def test_inventory_quantity_normalization_runtime_is_consistent(self):
        def extract_function(name):
            match = re.search(
                rf"function {name}\([^)]*\) \{{[\s\S]*?\n\}}",
                self.page,
            )
            self.assertIsNotNone(match, f"Page.vue 必须声明 {name}")
            return match.group(0)

        function_names = (
            "normalizedInventoryCount",
            "normalizedIngredientRequirement",
            "buildInventoryCounts",
            "ingredientCount",
            "ingredientEnough",
            "canGiftItem",
        )
        functions = {name: extract_function(name) for name in function_names}
        gift_max_match = re.search(
            r"const giftMaxQuantity = computed\(\(\) => [^\n]+\)",
            self.page,
        )
        self.assertIsNotNone(gift_max_match, "必须保留赠送数量上限 computed")
        self.assertIn(
            "const inventoryCounts = computed(() => buildInventoryCounts(inventoryItems.value))",
            self.page,
        )
        self.assertIn(
            "normalizedInventoryCount(item?.count) > 0",
            functions["canGiftItem"],
        )
        self.assertIn(
            "normalizedInventoryCount(selectedGiftItem.value?.count)",
            gift_max_match.group(0),
        )

        script = (
            "import assert from 'node:assert/strict'\n\n"
            + functions["normalizedInventoryCount"]
            + "\n\n"
            + functions["normalizedIngredientRequirement"]
            + "\n\n"
            + functions["buildInventoryCounts"]
            + "\n\n"
            + functions["ingredientCount"]
            + "\n\n"
            + functions["ingredientEnough"]
            + "\n\nconst writeActionsDisabled = { value: false }\n"
            + functions["canGiftItem"]
            + "\n\nconst computed = getter => ({ get value() { return getter() } })\n"
            + "const selectedGiftItem = { value: null }\n"
            + gift_max_match.group(0)
            + "\n\n"
            + """
for (const value of [NaN, Infinity, -Infinity, -1, 1.5, '1.5']) {
  assert.equal(normalizedInventoryCount(value), 0)
}
assert.equal(normalizedInventoryCount('7'), 7)
assert.equal(normalizedInventoryCount(0), 0)
assert.equal(normalizedInventoryCount(Number.MAX_SAFE_INTEGER + 1), 0)

const duplicateCounts = buildInventoryCounts([
  { name: ' ore ', count: '2' },
  { name: 'ore', count: 3 },
  { name: 'ore', count: Infinity },
  { name: 'ore', count: -4 },
  { name: 'ore', count: 1.5 },
  { name: ' ', count: 100 },
])
assert.equal(duplicateCounts.get('ore'), 5)
assert.equal(duplicateCounts.has(''), false)
assert.equal(
  buildInventoryCounts([
    { name: 'cap', count: Number.MAX_SAFE_INTEGER },
    { name: 'cap', count: 1 },
  ]).get('cap'),
  Number.MAX_SAFE_INTEGER,
)

for (const required of [NaN, Infinity, -Infinity, -1, 0, 1.5, '1.5']) {
  assert.equal(normalizedIngredientRequirement(required), null)
}
assert.equal(normalizedIngredientRequirement('2'), 2)

const inventoryCounts = {
  value: buildInventoryCounts([{ name: 'ore', count: '3' }]),
}
for (const required of [NaN, Infinity, -1, 0, 1.5, '1.5']) {
  assert.equal(ingredientEnough('ore', required), false)
}
assert.equal(ingredientEnough('ore', 2), true)
assert.equal(ingredientEnough('ore', '3'), true)
assert.equal(ingredientEnough('ore', 4), false)
assert.equal(ingredientEnough('missing', 1), false)

for (const count of [NaN, Infinity, -1, 0, 1.5, '1.5']) {
  assert.equal(canGiftItem({ giftable: true, count }), false)
}
assert.equal(canGiftItem({ giftable: true, count: '2' }), true)
assert.equal(canGiftItem({ giftable: false, count: 2 }), false)
writeActionsDisabled.value = true
assert.equal(canGiftItem({ giftable: true, count: 2 }), false)
writeActionsDisabled.value = false

selectedGiftItem.value = { count: Infinity }
assert.equal(giftMaxQuantity.value, 0)
selectedGiftItem.value = { count: 1.5 }
assert.equal(giftMaxQuantity.value, 0)
selectedGiftItem.value = { count: '12' }
assert.equal(giftMaxQuantity.value, 12)
selectedGiftItem.value = { count: 600 }
assert.equal(giftMaxQuantity.value, 500)
"""
        )
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)

    def test_history_is_single_line_with_time_on_the_right(self):
        self.assert_page_contains(
            "执行历史",
            'class="history-item"',
            'class="history-detail"',
            'class="history-time"',
        )
        self.assertRegex(
            self.compact_page,
            r"\.history-item\{[^}]*grid-template-columns:minmax\(0,1fr\)auto",
        )
        self.assertRegex(
            self.compact_page,
            r"\.history-(?:right|time)\{[^}]*text-align:right",
        )
        self.assertRegex(
            self.compact_page,
            r"\.history-detail\{[^}]*overflow:hidden[^}]*text-overflow:ellipsis[^}]*white-space:nowrap",
        )
        self.assertNotRegex(
            self.mobile_css,
            r"\.history-item\{[^}]*grid-template-columns:minmax\(0,1fr\)(?:;|\})",
        )
        self.assertNotRegex(
            self.mobile_css,
            r"\.history-time\{[^}]*text-align:left",
        )
        self.assertNotIn("justify-self:start", self.mobile_css)
        self.assertNotIn("任务结果", self.page)

    def test_mobile_layout_and_touch_targets_follow_farm_behavior(self):
        self.assert_page_contains("@media", "max-width:600px", "overflow-x:hidden")
        self.assertRegex(
            self.compact_page,
            r"\.siqi-page:deep\(\.v-btn\)\{[^}]*min-height:44px",
        )

    def test_overview_grid_and_card_actions_do_not_depend_on_host_helpers(self):
        self.assertRegex(
            self.compact_page,
            r"\.overview-grid\{[^}]*display:grid[^}]*grid-template-columns:repeat\(4,minmax\(0,1fr\)\)",
        )
        self.assertRegex(
            self.compact_page,
            r"\.siqi-card-title:deep\(\.v-spacer\)\{[^}]*flex:1",
        )

    def test_page_title_is_vuepill_and_status_page_has_no_cookie_action(self):
        self.assertIn("<title>Vue-魔丸</title>", self.index)
        self.assertNotIn("同步 Cookie", self.page)

    def test_status_toolbar_and_zero_limit_recipes_are_not_noisy(self):
        for removed in (
            'aria-label="立即执行 Vue-魔丸"',
            '@click="runNow"',
            "async function runNow()",
            "后端返回最大可炼造数量为 0",
        ):
            with self.subTest(removed=removed):
                self.assertNotIn(removed, self.page)
        self.assertIn('v-if="Number(recipe.max_count || 0) > 0"', self.page)
        self.assertIn('v-if="recipeUnavailableReason(recipe)"', self.page)
        self.assertRegex(
            self.page,
            r"if \(Number\(recipe\.max_count \|\| 0\) <= 0\) return ''",
        )
        self.assertRegex(
            self.page,
            r"function recipeQuantityError\(recipe\)\s*\{\s*const maximum = Number\(recipe\.max_count \|\| 0\)\s*if \(maximum <= 0\) return ''",
        )
        self.assertRegex(
            self.page,
            r"recipe\.status && !/材料不足\|炼造上限为\\s\*0\|最大可炼造数量为\\s\*0/",
        )


if __name__ == "__main__":
    unittest.main()
