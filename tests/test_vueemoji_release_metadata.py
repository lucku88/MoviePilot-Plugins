import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.2.4"


class VueEmojiReleaseMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = (REPO_ROOT / "plugins.v2" / "vueemoji" / "__init__.py").read_text(encoding="utf-8")
        cls.package = json.loads((REPO_ROOT / "plugins.v2" / "vueemoji" / "package.json").read_text(encoding="utf-8"))
        cls.package_lock = json.loads((REPO_ROOT / "plugins.v2" / "vueemoji" / "package-lock.json").read_text(encoding="utf-8"))
        cls.market = json.loads((REPO_ROOT / "package.v2.json").read_text(encoding="utf-8"))["VueEmoji"]
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_release_versions_are_consistent(self):
        match = re.search(r'plugin_version\s*=\s*"([^"]+)"', self.backend)
        self.assertIsNotNone(match)
        self.assertEqual(EXPECTED_VERSION, match.group(1))
        self.assertEqual(EXPECTED_VERSION, self.package["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["packages"][""]["version"])
        self.assertEqual(EXPECTED_VERSION, self.market["version"])

    def test_market_history_describes_latest_startup_recovery_release(self):
        history = self.market["history"]
        self.assertEqual(f"v{EXPECTED_VERSION}", next(iter(history)))
        note = history[f"v{EXPECTED_VERSION}"]
        for phrase in ("主调度器", "延迟自检", "主动补登记", "自动挖角", "保留配置"):
            self.assertIn(phrase, note)
        self.assertIn("状态页", history["v0.2.0"])
        self.assertIn("自动挖角", history["v0.2.0"])
        self.assertIn("动画预览", history["v0.1.11"])
        self.assertIn("SIQI_EMOJI_DATA.logs", history["v0.1.10"])

    def test_readme_lists_version_and_upgrade_behaviour(self):
        self.assertIn(f"| `Vue-表情` | `v{EXPECTED_VERSION}`", self.readme)
        section = self.readme.split("### 🎭 Vue-表情", 1)[1].split("### ", 1)[0]
        for phrase in (f"v{EXPECTED_VERSION}", "SIQI_EMOJI_DATA.logs", "网页操作日志", "保留配置"):
            self.assertIn(phrase, section)

    def test_federation_entries_reference_existing_build_assets(self):
        dist = REPO_ROOT / "plugins.v2" / "vueemoji" / "dist" / "assets"
        remote_entry = (dist / "assets" / "remoteEntry.js").read_text(encoding="utf-8")
        index_html = (dist / "index.html").read_text(encoding="utf-8")
        index_js = (dist / "index.js").read_text(encoding="utf-8")

        page_match = re.search(r'__federation_expose_Page-[^"\']+\.js', remote_entry)
        config_match = re.search(r'__federation_expose_Config-[^"\']+\.js', remote_entry)
        self.assertIsNotNone(page_match)
        self.assertIsNotNone(config_match)
        self.assertTrue((dist / page_match.group(0)).exists())
        self.assertTrue((dist / config_match.group(0)).exists())

        index_match = re.search(r'index-[^"\']+\.js', index_html)
        if index_match:
            self.assertTrue((dist / index_match.group(0)).exists())
        else:
            self.assertIn('src="./index.js"', index_html)
            self.assertTrue(index_js.strip())


if __name__ == "__main__":
    unittest.main()
