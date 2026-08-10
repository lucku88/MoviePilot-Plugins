import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILES = {
    "Vue-农场": REPO_ROOT / "plugins.v2" / "vuefarm" / "src" / "components" / "Config.vue",
    "Vue-魔丸": REPO_ROOT / "plugins.v2" / "vuepill" / "src" / "components" / "Config.vue",
    "Vue-玩偶": REPO_ROOT / "plugins.v2" / "vuetoy" / "src" / "components" / "Config.vue",
    "Vue-表情": REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Config.vue",
}


class VueCookieUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {
            name: path.read_text(encoding="utf-8")
            for name, path in CONFIG_FILES.items()
        }

    def test_all_plugins_use_compact_siqi_farm_cookie_control(self):
        for name, source in self.sources.items():
            with self.subTest(plugin=name):
                self.assertIn('v-model="config.cookie"', source)
                self.assertIn("<v-text-field", source)
                self.assertIn("站点 Cookie", source)
                self.assertIn("mdi-cookie", source)
                self.assertIn("mdi-eye-outline", source)
                self.assertIn("mdi-eye-off-outline", source)
                self.assertIn("mdi-content-paste", source)
                self.assertIn("syncCookie", source)
                self.assertIn("MoviePilot", source)
                self.assertIn("备用", source)

    def test_cookie_sync_action_is_inside_the_field(self):
        for name, source in self.sources.items():
            with self.subTest(plugin=name):
                cookie_start = source.index('v-model="config.cookie"')
                field_start = source.rfind("<v-text-field", 0, cookie_start)
                field_end = source.find("</v-text-field>", cookie_start)
                field = source[field_start:field_end] if field_start >= 0 and field_end >= 0 else ""
                self.assertIn("#append-inner", field)
                self.assertIn("mdi-content-paste", field)
                self.assertIn("syncCookie", field)
                self.assertNotIn("立即同步站点 Cookie", source)
                self.assertNotIn("从站点同步", source)
                self.assertNotIn('class="cookie-actions"', source)

    def test_automatic_cookie_sync_has_no_separate_switch(self):
        for name, source in self.sources.items():
            with self.subTest(plugin=name):
                self.assertNotIn('v-model="config.auto_cookie"', source)
                self.assertNotIn("自动同步 Cookie</div>", source)


if __name__ == "__main__":
    unittest.main()
