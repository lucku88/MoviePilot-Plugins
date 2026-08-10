import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Page.vue"
CONFIG = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Config.vue"


class VueEmojiRecruitFrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.compact_config = "".join(cls.config.split())

    def test_config_exposes_independent_recruit_controls(self):
        for expected in (
            "config.auto_recruit",
            "config.recruit_tiers",
            "config.recruit_time_windows",
            "config.recruit_interval_minutes",
            "config.recruit_visit_count",
            "新人",
            "实力",
            "知名",
            "顶流",
            "07:00-23:00",
        ):
            self.assertIn(expected, self.config)

    def test_recruit_filters_use_farm_style_compact_row(self):
        for expected in (
            'class="siqi-form-grid recruit-settings-grid"',
            'class="siqi-input recruit-tier-select"',
            'density="compact"',
            'clearable',
            'class="siqi-field-hint recruit-settings-hint"',
        ):
            self.assertIn(expected, self.config)
        self.assertIn(".recruit-settings-grid{align-items:center}", self.compact_config)

    def test_page_exposes_recruit_status_and_manual_endpoint(self):
        for expected in (
            "emoji.recruit",
            "自动挖角",
            "next_check_time",
            "recruit_tiers",
            "recruit_time_windows",
            "@click=\"recruitNow\"",
            "/recruit",
        ):
            self.assertIn(expected, self.page)

    def test_recruit_card_uses_shared_theme_shell(self):
        self.assertIn("recruit-card", self.page)
        self.assertIn("siqi-card-title--recruit", self.page)
        self.assertNotIn("#1f", self.page)
        self.assertNotIn("background:#", self.page)


if __name__ == "__main__":
    unittest.main()
