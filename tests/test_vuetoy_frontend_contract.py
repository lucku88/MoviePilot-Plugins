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
        self.assertIn("@media (max-width: 720px)", self.page)
        self.assertIn("@media (max-width: 720px)", self.config)
        self.assertIn("overflow-x: hidden", self.page)
        self.assertIn("min-height: 44px", self.page)
        self.assertIn("min-height: 44px", self.config)


if __name__ == "__main__":
    unittest.main()
