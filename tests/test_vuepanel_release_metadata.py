import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.1.39"


class VuePanelReleaseMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin_dir = REPO_ROOT / "plugins.v2" / "vuepanel"
        cls.backend = (cls.plugin_dir / "__init__.py").read_text(encoding="utf-8")
        cls.package = json.loads((cls.plugin_dir / "package.json").read_text(encoding="utf-8"))
        cls.package_lock = json.loads((cls.plugin_dir / "package-lock.json").read_text(encoding="utf-8"))
        cls.market = json.loads((REPO_ROOT / "package.v2.json").read_text(encoding="utf-8"))["VuePanel"]
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_release_versions_are_consistent(self):
        match = re.search(r'plugin_version\s*=\s*"([^"]+)"', self.backend)
        self.assertIsNotNone(match)
        self.assertEqual(EXPECTED_VERSION, match.group(1))
        self.assertEqual(EXPECTED_VERSION, self.package["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["packages"][""]["version"])
        self.assertEqual(EXPECTED_VERSION, self.market["version"])

    def test_market_history_describes_scheduler_startup_fix(self):
        history = self.market["history"]
        self.assertEqual(f"v{EXPECTED_VERSION}", next(iter(history)))
        note = history[f"v{EXPECTED_VERSION}"]
        for phrase in ("启动", "热重载", "总调度器", "漏注册", "保留配置"):
            self.assertIn(phrase, note)

    def test_readme_lists_current_version_and_startup_fix(self):
        self.assertIn(f"| `Vue-面板` | `v{EXPECTED_VERSION}` |", self.readme)
        section = self.readme.split("### 📊 Vue-面板", 1)[1].split("### ", 1)[0]
        for phrase in (f"v{EXPECTED_VERSION}", "总调度器", "漏注册", "保留配置"):
            self.assertIn(phrase, section)

    def test_federation_page_contains_current_version(self):
        dist_assets = self.plugin_dir / "dist" / "assets"
        remote_entry = (dist_assets / "assets" / "remoteEntry.js").read_text(encoding="utf-8")
        page_match = re.search(r'__federation_expose_Page-[^"\']+\.js', remote_entry)
        self.assertIsNotNone(page_match)
        page_asset = dist_assets / page_match.group(0)
        self.assertTrue(page_asset.is_file(), page_asset.name)
        self.assertIn(EXPECTED_VERSION, page_asset.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
