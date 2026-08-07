import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE = REPO_ROOT / "plugins.v2" / "vuetoy" / "src" / "components" / "Page.vue"
CONFIG = REPO_ROOT / "plugins.v2" / "vuetoy" / "src" / "components" / "Config.vue"


class VueToyFrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.compact_page = re.sub(r"\s+", "", cls.page)
        cls.compact_config = re.sub(r"\s+", "", cls.config)

    def test_status_page_uses_siqifarm_adaptive_shell(self):
        for expected in (
            'class="siqi-page"',
            'class="siqi-topbar"',
            'class="siqi-card next-run-card',
            'class="stat-card',
            'class="siqi-card personal-booth-card',
            'class="siqi-card cabinet-card',
            'class="siqi-card target-card',
            'class="siqi-card remote-card',
            'class="siqi-card activity-card',
        ):
            self.assertIn(expected, self.page)

        for forbidden in ("toy-hero", "isDarkTheme", "MutationObserver", "prefers-color-scheme"):
            self.assertNotIn(forbidden, self.page)

    def test_status_page_keeps_all_manual_game_actions(self):
        for endpoint in (
            "/refresh",
            "/run",
            "/collect-slot",
            "/recycle-doll",
            "/place-personal",
            "/random-target",
            "/view-target",
            "/place-target",
            "/buy-box",
            "/open-box",
        ):
            self.assertIn(endpoint, self.page)

    def test_status_page_reads_backend_guard_hours(self):
        self.assertIn("placementGuard.value.hours", self.page)

    def test_status_page_orders_boxes_then_personal_target_remote_and_latest_logs(self):
        schedule = self.page.index('class="siqi-card next-run-card')
        shop = self.page.index('class="siqi-card box-card')
        cabinet = self.page.index('class="siqi-card cabinet-card')
        personal = self.page.index('class="siqi-card personal-booth-card')
        target = self.page.index('class="siqi-card target-card')
        remote = self.page.index('class="siqi-card remote-card')
        activity = self.page.index('class="siqi-card activity-card')

        self.assertLess(schedule, shop)
        self.assertLess(shop, cabinet)
        self.assertLess(cabinet, personal)
        self.assertLess(personal, target)
        self.assertLess(target, remote)
        self.assertLess(remote, activity)

    def test_status_page_removes_execution_history_and_adds_cabinet_recycle(self):
        self.assertNotIn(">执行历史</", self.page)
        self.assertIn("最新操作记录", self.page)
        self.assertIn("openRecycleDialog", self.page)
        self.assertIn("recycleDoll", self.page)
        self.assertIn("recycleDialog", self.page)
        self.assertIn("idle", self.page)
        self.assertIn("can_recycle", self.page)

    def test_latest_activity_is_one_line_with_right_aligned_time(self):
        self.assertIn('class="activity-row"', self.page)
        self.assertIn("<time>{{ item.time }}</time>", self.page)
        self.assertRegex(self.page, r"\.activity-row time\s*\{[^}]*margin-left:\s*auto")

    def test_config_matches_siqifarm_and_exposes_guard_parameter(self):
        for expected in (
            'class="siqi-config"',
            'class="siqi-topbar"',
            'v-model="config.self_slot_guard_hours"',
            'v-model="config.random_delay_max_seconds"',
            'v-model="config.auto_collect"',
            'v-model="config.auto_place"',
            'v-model="config.cookie"',
            "cookieVisible",
            "/cookie",
        ):
            self.assertIn(expected, self.config)

        self.assertNotIn('v-model="config.force_ipv4"', self.config)
        self.assertNotIn('v-model="config.auto_cookie"', self.config)

    def test_pages_have_mobile_layout_without_horizontal_overflow(self):
        self.assertIn("@media (max-width: 600px)", self.page)
        self.assertIn("@media (max-width: 600px)", self.config)
        self.assertIn("overflow-x: hidden", self.page)
        self.assertIn("min-height: 44px", self.page)
        self.assertIn("min-height: 44px", self.config)

    def test_pages_reuse_farm_and_pill_theme_shell(self):
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

        for legacy_token in (
            "position:sticky",
            "var(--v-border-color)",
            "color:rgb(var(--v-theme-on-background))",
        ):
            self.assertNotIn(legacy_token, self.compact_page)
            self.assertNotIn(legacy_token, self.compact_config)

    def test_config_uses_shared_siqifarm_form_classes(self):
        for expected in (
            'class="siqi-switch-grid"',
            'class="siqi-switch-item',
            'class="siqi-switch-main"',
            'class="siqi-switch-label"',
            'class="siqi-switch-desc"',
            'class="siqi-form-grid"',
            'class="siqi-field"',
        ):
            self.assertIn(expected, self.config)

    def test_status_page_uses_the_same_overview_and_title_contract_as_vuepill(self):
        for expected in (
            'class="mb-3 overview-grid"',
            'class="stat-content"',
            'class="stat-title"',
            'class="siqi-card-title d-flex align-center"',
            '<v-spacer />',
        ):
            self.assertIn(expected, self.page)

        for expected in (
            ".overview-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0012px!important;}",
            ".overview-grid>*{width:auto!important;max-width:none!important;padding:0!important;}",
            ".siqi-card-title:deep(.v-spacer){flex:11auto!important;}",
        ):
            self.assertIn(expected, self.compact_page)

    def test_status_page_uses_the_same_desktop_bento_rhythm_as_farm_and_pill(self):
        for expected in (
            'class="siqi-card next-run-card',
            'class="two-column-grid mb-3"',
            'class="interaction-grid mb-3"',
            'class="personal-booth-body"',
        ):
            self.assertIn(expected, self.page)

        for expected in (
            ".next-run-body{display:flex;align-items:center;gap:12px;",
            ".interaction-grid{display:grid;grid-template-columns:1fr;gap:12px;align-items:stretch;}",
            ".personal-booth-card{display:flex!important;flex-direction:column;",
            ".personal-booth-body{display:flex;flex:1;}",
            ".personal-booth-card.slot-grid{width:100%;}",
            "@media(max-width:720px)",
        ):
            self.assertIn(expected, self.compact_page)

    def test_next_run_card_does_not_follow_moviepilot_primary_color(self):
        self.assertIn('class="next-run-time"', self.page)
        self.assertIn('class="next-run-guard"', self.page)
        self.assertNotIn("color:rgb(var(--v-theme-primary))", self.compact_page)

        for expected in (
            ".next-run-icon{display:grid;place-items:center;",
            "color:#16a34a;",
            ".next-run-guard{color:#d97706;}",
        ):
            self.assertIn(expected, self.compact_page)

    def test_manual_run_action_follows_farm_and_pill_toolbar_hierarchy(self):
        topbar = self.page.split('<div class="siqi-content">', 1)[0]
        self.assertNotIn('aria-label="立即执行 Vue-玩偶"', topbar)
        self.assertIn('class="schedule-run-btn"', self.page)
        self.assertIn('@click="runNow"', self.page)

    def test_config_uses_the_same_three_column_shell_as_vuepill(self):
        self.assertNotIn("siqi-switch-grid--two", self.config)
        self.assertIn('class="siqi-input siqi-number-input"', self.config)

        for expected in (
            ".siqi-form-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;min-width:0;}",
            "@media(max-width:900px)",
            "@media(max-width:600px)",
        ):
            self.assertIn(expected, self.compact_config)

        self.assertRegex(
            self.compact_config,
            r"\.siqi-card\{[^}]*box-shadow:inset01px0rgba\(var\(--v-theme-surface\),\.2\),02px10pxrgba\(0,0,0,\.05\)",
        )


if __name__ == "__main__":
    unittest.main()
