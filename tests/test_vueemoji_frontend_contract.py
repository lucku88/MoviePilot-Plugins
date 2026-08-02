import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Page.vue"
CONFIG = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Config.vue"


class VueEmojiFrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.compact_page = re.sub(r"\s+", "", cls.page)
        cls.compact_config = re.sub(r"\s+", "", cls.config)

    def test_status_page_uses_shared_adaptive_shell(self):
        for expected in (
            'class="siqi-page"',
            'class="siqi-topbar"',
            'class="mb-3 overview-grid"',
            'class="stat-card',
            'class="primary-grid mb-3"',
            'class="siqi-card schedule-board',
            'class="siqi-card bag-card',
            'class="siqi-card catalog-card',
            'class="siqi-card stage-card',
            'class="siqi-card history-card',
        ):
            self.assertIn(expected, self.page)

        for forbidden in (
            "emoji-hero",
            "isDarkTheme",
            "MutationObserver",
            "prefers-color-scheme",
        ):
            self.assertNotIn(forbidden, self.page)

    def test_status_page_keeps_all_manual_actions(self):
        for endpoint in (
            "/refresh",
            "/run",
            "/cookie",
            "/spin",
            "/open-bag",
            "/accept-open",
            "/reroll-open",
            "/upgrade-bag",
            "/expand-stage-row",
            "/confirm-stage",
            "/recall-stage",
        ):
            self.assertIn(endpoint, self.page)

    def test_toolbar_matches_farm_pill_and_toy_hierarchy(self):
        topbar = self.page.split('<div class="siqi-content">', 1)[0]
        for expected in (
            'aria-label="刷新 Vue-表情状态"',
            'aria-label="打开 Vue-表情配置"',
            'aria-label="关闭 Vue-表情"',
        ):
            self.assertIn(expected, topbar)

        self.assertNotIn('aria-label="立即执行 Vue-表情"', topbar)
        self.assertNotIn("同步 Cookie", topbar)
        self.assertIn('class="schedule-run-btn"', self.page)
        self.assertIn('@click="runNow"', self.page)

    def test_overview_is_four_cards_and_catalog_keeps_progress(self):
        self.assertIn("const overviewStats = computed", self.page)
        self.assertIn("const catalogStat = computed", self.page)
        self.assertIn("v-for=\"(item, index) in overviewStats\"", self.page)
        self.assertIn("catalogStat", self.page)
        self.assertIn(
            ".overview-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0012px!important;}",
            self.compact_page,
        )

    def test_status_page_matches_shared_tone_cards_and_section_headers(self):
        self.assertIn(
            "return ['green', 'orange', 'blue', 'red'][index] || 'green'",
            self.page,
        )
        for expected in (
            'siqi-card-title--schedule',
            'siqi-card-title--bags',
            'siqi-card-title--catalog',
            'siqi-card-title--stage',
            'siqi-card-title--history',
            '.stat-card{--stat-rgb:',
            '.stat-red{--stat-rgb:239,68,68;',
            '.siqi-card-title--schedule{background:rgba(76,175,80,.08)}',
            '.siqi-card-title--bags{background:rgba(249,115,22,.09)}',
            '.siqi-card-title--catalog{background:rgba(59,130,246,.09)}',
            '.siqi-card-title--stage{background:rgba(245,158,11,.09)}',
            '.siqi-card-title--history{background:rgba(20,184,166,.08)}',
        ):
            self.assertIn(expected, self.compact_page)

        self.assertIn(
            '.siqi-card-title{min-height:44px;',
            self.compact_page,
        )

    def test_history_is_one_line_with_right_aligned_time(self):
        self.assertIn('class="history-detail"', self.page)
        self.assertIn('class="history-time"', self.page)
        self.assertRegex(self.page, r"\.history-time\s*\{[^}]*margin-left:\s*auto")

    def test_config_uses_shared_form_shell(self):
        for expected in (
            'class="siqi-config"',
            'class="siqi-topbar"',
            'class="siqi-switch-grid"',
            'class="siqi-switch-item',
            'class="siqi-switch-main"',
            'class="siqi-switch-label"',
            'class="siqi-switch-desc"',
            'class="siqi-form-grid"',
            'class="siqi-field"',
            'v-model="config.spin_cron"',
            'v-model="config.auto_stage_effect_key"',
            'v-model="config.random_delay_max_seconds"',
            'v-model="config.cookie"',
            "cookieVisible",
            "VCronField",
        ):
            self.assertIn(expected, self.config)

        for forbidden in ("isDarkTheme", "MutationObserver", "prefers-color-scheme"):
            self.assertNotIn(forbidden, self.config)

    def test_config_removes_legacy_ipv4_field(self):
        self.assertNotIn("config.force_ipv4", self.config)
        self.assertNotIn("force_ipv4:", self.config)
        self.assertNotIn("force_ipv4", self.config)
        self.assertNotIn("优先 IPv4", self.config)
        self.assertIn(
            "const legacyIpv4Key = ['force', 'ipv4'].join('_')",
            self.config,
        )
        self.assertIn("delete rest[legacyIpv4Key]", self.config)

    def test_pages_reuse_shared_theme_tokens(self):
        shared_tokens = (
            "color:rgba(var(--v-theme-on-surface),.85)",
            "border:1pxsolidrgba(var(--v-theme-on-surface),.12)",
            "background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))",
            "backdrop-filter:blur(20px)saturate(150%)",
            "border:.5pxsolidrgba(var(--v-theme-on-surface),.08)",
            "box-shadow:02px10pxrgba(0,0,0,.05)",
        )
        for token in shared_tokens:
            self.assertIn(token, self.compact_page)
            self.assertIn(token, self.compact_config)

    def test_pages_have_mobile_layout_without_horizontal_overflow(self):
        self.assertIn("@media (max-width: 600px)", self.page)
        self.assertIn("@media (max-width: 600px)", self.config)
        self.assertIn("overflow-x: hidden", self.page)
        self.assertIn("overflow-x: hidden", self.config)
        self.assertIn("min-height:44px", self.compact_page)
        self.assertIn("min-height: 44px", self.config)

    def test_stage_uses_one_remaining_time_source(self):
        self.assertIn("Number(stage.value.remaining_seconds || 0)", self.page)
        self.assertNotIn("meta: stage.value.current_text", self.page)
        self.assertNotIn("stage.current_text", self.page)
        self.assertIn("stage.value.current_effect_name", self.page)
        self.assertIn("stage.value.active_count", self.page)

    def test_action_number_inputs_are_centered_and_mobile_safe(self):
        self.assertRegex(
            self.page,
            r"\.number-input\s*\{[^}]*height:\s*44px[^}]*text-align:\s*center",
        )
        self.assertRegex(
            self.page,
            r"\.slot-machine-action,\.bag-action\s*\{[^}]*align-items:\s*center[^}]*min-width:\s*0",
        )
        self.assertIn(
            ".slot-machine-action:deep(.v-btn),.bag-action:deep(.v-btn){height:44px",
            self.compact_page,
        )


if __name__ == "__main__":
    unittest.main()
