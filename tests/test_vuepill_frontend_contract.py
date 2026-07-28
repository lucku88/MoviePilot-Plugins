import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "components" / "Page.vue"
APP_PATH = ROOT / "plugins.v2" / "vuepill" / "src" / "App.vue"
INDEX_PATH = ROOT / "plugins.v2" / "vuepill" / "index.html"


class VuePillFrontendContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE_PATH.read_text(encoding="utf-8")
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.index = INDEX_PATH.read_text(encoding="utf-8")
        cls.compact_page = re.sub(r"\s+", "", cls.page)

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

    def test_gift_stats_supports_direction_range_and_summaries(self):
        self.assert_page_contains(
            "gift-stats",
            "giftStatsDirection",
            "giftStatsRange",
            "最近30天",
            "全部",
            "赠出",
            "收到",
            "总事件数",
            "总数量",
            "用户汇总",
            "物品汇总",
        )

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
