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
            'class="siqi-card schedule-board',
            'class="stat-card',
            'class="siqi-card personal-booth-card',
            'class="siqi-card cabinet-card',
            'class="siqi-card target-card',
            'class="siqi-card history-card',
        ):
            self.assertIn(expected, self.page)

        for forbidden in ("toy-hero", "isDarkTheme", "MutationObserver", "prefers-color-scheme"):
            self.assertNotIn(forbidden, self.page)

    def test_status_page_keeps_all_manual_game_actions(self):
        for endpoint in (
            "/refresh",
            "/run",
            "/collect-slot",
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

    def test_personal_booth_is_rendered_before_cabinet_and_remote_target(self):
        personal = self.page.index('class="siqi-card personal-booth-card')
        cabinet = self.page.index('class="siqi-card cabinet-card')
        target = self.page.index('class="siqi-card target-card')

        self.assertLess(personal, cabinet)
        self.assertLess(cabinet, target)

    def test_history_is_one_line_with_right_aligned_time(self):
        self.assertIn('class="history-main"', self.page)
        self.assertIn('class="history-time"', self.page)
        self.assertIn("parts.join(' / ')", self.page)
        self.assertRegex(self.page, r"\.history-time\s*\{[^}]*margin-left:\s*auto")

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
