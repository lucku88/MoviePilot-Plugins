import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "components" / "Page.vue"
APP_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "App.vue"
INDEX_PATH = ROOT / "plugins.v2" / "vuepill" / "index.html"
ASYNC_GUARD_PATH = (
    ROOT / "plugins.v2" / "vuepill" / "src" / "utils" / "asyncGuards.js"
)


class VuePillFrontendContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE_PATH.read_text(encoding="utf-8")
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.index = INDEX_PATH.read_text(encoding="utf-8")
        cls.compact_page = re.sub(r"\s+", "", cls.page)
        cls.mobile_css = cls.compact_page.split(
            "@media(max-width:600px){", 1
        )[1].rsplit("</style>", 1)[0]

    def assert_page_contains(self, *tokens):
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.page)

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

    def test_status_sections_follow_required_order(self):
        markers = (
            "siqi-topbar",
            'v-for="item in overview"',
            "dynamic-schedule-card",
            "兑换魔力",
            "物品栏",
            "炼造工坊",
            "执行历史",
        )
        positions = [self.page.find(marker) for marker in markers]
        self.assertNotIn(-1, positions, f"页面缺少分区标记：{markers}")
        self.assertEqual(positions, sorted(positions))

    def test_uses_vuepill_api_namespace_and_real_action_paths(self):
        self.assertRegex(self.page, r"const\s+PLUGIN_ID\s*=\s*['\"]VuePill['\"]")
        self.assert_page_contains(
            "/plugin/${PLUGIN_ID}",
            "/status",
            "/refresh",
            "/run",
            "/move-bricks",
            "/clean-beach",
            "/exchange-points",
            "/craft-item",
            "/craft-max-pill",
            "/gift-item",
            "/gift-stats",
        )

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
  {{ pillStatus: emptyFullStatus, history: [] }},
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


if __name__ == "__main__":
    unittest.main()
