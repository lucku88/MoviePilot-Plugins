import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.2.4"


class VueToyReleaseMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = (REPO_ROOT / "plugins.v2" / "vuetoy" / "__init__.py").read_text(encoding="utf-8")
        cls.package = json.loads((REPO_ROOT / "plugins.v2" / "vuetoy" / "package.json").read_text(encoding="utf-8"))
        cls.package_lock = json.loads((REPO_ROOT / "plugins.v2" / "vuetoy" / "package-lock.json").read_text(encoding="utf-8"))
        cls.market = json.loads((REPO_ROOT / "package.v2.json").read_text(encoding="utf-8"))["VueToy"]
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_release_versions_are_consistent(self):
        matched = re.search(r'plugin_version\s*=\s*"([^"]+)"', self.backend)
        self.assertIsNotNone(matched)
        self.assertEqual(EXPECTED_VERSION, matched.group(1))
        self.assertEqual(EXPECTED_VERSION, self.package["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["version"])
        self.assertEqual(EXPECTED_VERSION, self.package_lock["packages"][""]["version"])
        self.assertEqual(EXPECTED_VERSION, self.market["version"])

    def test_market_history_describes_v024_layout_patch(self):
        history = self.market["history"]
        self.assertEqual(f"v{EXPECTED_VERSION}", next(iter(history)))
        note = history[f"v{EXPECTED_VERSION}"]
        for phrase in (
            "左右分区",
            "动态任务",
            "自己展位",
            "主题主色",
            "浅色",
            "深色",
            "手机",
            "保留配置",
        ):
            self.assertIn(phrase, note)

        v023_note = history["v0.2.3"]
        for phrase in ("四列概览", "三列表单", "卡片层级", "保留配置"):
            self.assertIn(phrase, v023_note)

        v022_note = history["v0.2.2"]
        for phrase in ("浅色", "深色", "Vue-农场", "Vue-魔丸", "保留配置"):
            self.assertIn(phrase, v022_note)

        v021_note = history["v0.2.1"]
        for phrase in ("自己展位", "0/3", "保留配置"):
            self.assertIn(phrase, v021_note)

        v020_note = history["v0.2.0"]
        for phrase in (
            "思齐农场",
            "自家展位保护",
            "外展限速",
            "IPv4",
            "IPv6",
            "旧接口",
            "保留配置",
        ):
            self.assertIn(phrase, v020_note)

    def test_readme_lists_version_and_upgrade_behaviour(self):
        self.assertIn(f"| `Vue-玩偶` | `v{EXPECTED_VERSION}` |", self.readme)
        section = self.readme.split("### 🧸 Vue-玩偶", 1)[1].split("### ", 1)[0]
        for phrase in (
            "四列概览",
            "三列表单",
            "左右分区",
            "主题主色",
            "浅色",
            "深色",
            "手机",
            "思齐农场",
            "自家展位保护",
            "外展限速",
            "IPv4",
            "IPv6",
            "旧接口",
            "保留",
        ):
            self.assertIn(phrase, section)

    def test_federation_entries_reference_existing_build_assets(self):
        dist_assets = REPO_ROOT / "plugins.v2" / "vuetoy" / "dist" / "assets"
        entry_files = (
            dist_assets / "assets" / "remoteEntry.js",
            dist_assets / "index.js",
        )
        referenced_assets = set()
        for entry_file in entry_files:
            content = entry_file.read_text(encoding="utf-8")
            referenced_assets.update(
                re.findall(r"__federation_expose_(?:Config|Page)-[a-f0-9]+\.js", content)
            )

        self.assertEqual(2, len(referenced_assets))
        for asset_name in referenced_assets:
            self.assertTrue((dist_assets / asset_name).is_file(), asset_name)


if __name__ == "__main__":
    unittest.main()
