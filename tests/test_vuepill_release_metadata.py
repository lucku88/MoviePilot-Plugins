import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "plugins.v2" / "vuepill"
DIST_DIR = PLUGIN_DIR / "dist"
EXPECTED_VERSION = "0.2.0"
EXPECTED_HISTORY = (
    "重写 Vue-魔丸 页面和后端：移植 Vue-农场风格，修复真实配方/沙滩状态解析，"
    "加入手动赠送与赠礼统计，并首次升级时重置旧配置和历史。"
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_dist_text():
    asset_paths = sorted(
        path
        for path in DIST_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".js", ".css"}
    )
    return asset_paths, "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in asset_paths
    )


class VuePillReleaseMetadataTest(unittest.TestCase):
    def test_release_versions_are_consistently_v020(self):
        init_source = (PLUGIN_DIR / "__init__.py").read_text(encoding="utf-8")
        version_match = re.search(
            r'plugin_version\s*=\s*["\']([^"\']+)["\']', init_source
        )
        self.assertIsNotNone(version_match, "找不到 VuePill.plugin_version")

        package = read_json(PLUGIN_DIR / "package.json")
        package_lock = read_json(PLUGIN_DIR / "package-lock.json")
        market = read_json(ROOT / "package.v2.json")["VuePill"]

        versions = {
            "plugin_version": version_match.group(1),
            "package.json": package["version"],
            "package-lock.json": package_lock["version"],
            "package-lock root package": package_lock["packages"][""]["version"],
            "package.v2.json": market["version"],
        }
        self.assertEqual(
            {EXPECTED_VERSION},
            set(versions.values()),
            f"VuePill 发布版本不一致：{versions}",
        )

    def test_market_history_and_readme_describe_the_v020_release(self):
        market = read_json(ROOT / "package.v2.json")["VuePill"]
        history = market["history"]
        self.assertEqual("v0.2.0", next(iter(history)))
        self.assertEqual(EXPECTED_HISTORY, history["v0.2.0"])

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required_readme_text = (
            "| `Vue-魔丸` | `v0.2.0` |",
            "Cookie 固定从 MoviePilot 站点管理自动同步",
            "动态沙滩",
            "搬砖使用独立 Cron",
            "`4/4/2/2/2/1`",
            "以页面真实配方为准",
            "自动炼造",
            "分批兑换",
            "默认保留 10 个魔丸",
            "手动赠送需二次确认",
            "赠出",
            "收到",
            "保存配置或 MoviePilot 重启后会自动补跑",
            "首次升级",
            "重置旧配置和历史",
            "默认关闭",
            "手动刷新插件市场",
            "手动更新 `Vue-魔丸`",
            "不会自动安装或更新插件",
        )
        for token in required_readme_text:
            with self.subTest(token=token):
                self.assertIn(token, readme)

    def test_source_has_no_public_cookie_controls(self):
        page_source = (PLUGIN_DIR / "src" / "components" / "Page.vue").read_text(
            encoding="utf-8"
        )
        config_source = (
            PLUGIN_DIR / "src" / "components" / "Config.vue"
        ).read_text(encoding="utf-8")
        frontend_source = f"{page_source}\n{config_source}"

        self.assertIn("Cookie：从 MoviePilot 站点自动同步。", config_source)
        for forbidden in (
            "auto_cookie",
            "config.cookie",
            "cookieFieldValue",
            "syncCookie",
            "同步 Cookie",
            "/cookie",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, frontend_source)
        self.assertNotRegex(
            frontend_source,
            r"<v-(?:text-field|textarea|switch|btn)\b[^>]*(?:Cookie|cookie)",
        )

    def test_dist_federation_references_current_page_and_config_assets(self):
        remote_entries = list(DIST_DIR.rglob("remoteEntry.js"))
        self.assertEqual(1, len(remote_entries), remote_entries)
        remote_entry = remote_entries[0]
        remote_source = remote_entry.read_text(encoding="utf-8", errors="replace")

        for module_name in ("Page", "Config"):
            references = re.findall(
                rf"__federation_import\([\"\']([^\"\']*"
                rf"__federation_expose_{module_name}-[^\"\']+\.js)[\"\']\)",
                remote_source,
            )
            self.assertEqual(1, len(references), references)
            referenced_asset = (remote_entry.parent / references[0]).resolve()
            self.assertTrue(
                referenced_asset.is_file(),
                f"remoteEntry 引用的 {module_name} 产物不存在：{referenced_asset}",
            )
            built_assets = [
                path.resolve()
                for path in DIST_DIR.rglob(
                    f"__federation_expose_{module_name}-*.js"
                )
            ]
            self.assertEqual([referenced_asset], built_assets)

    def test_dist_contains_v020_features_without_legacy_ui(self):
        asset_paths, dist_text = read_dist_text()
        self.assertTrue(asset_paths, "VuePill dist 中没有可检查的 JS/CSS 产物")

        for marker in (
            "siqi-page",
            "siqi-config",
            "gift-item",
            "gift-stats",
            "VCronField",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, dist_text)

        lowered_dist = dist_text.lower()
        for legacy_marker in ("vp-shell", "vp-page", "#7c5cff"):
            with self.subTest(legacy_marker=legacy_marker):
                self.assertNotIn(legacy_marker, lowered_dist)

        for forbidden_cookie_ui in (
            "同步 Cookie",
            "使用站点 Cookie",
            "站点 Cookie：手动填写",
            "cookieFieldValue",
            "auto_cookie",
            "config.cookie",
            "c_secure_pass",
        ):
            with self.subTest(forbidden_cookie_ui=forbidden_cookie_ui):
                self.assertNotIn(forbidden_cookie_ui, dist_text)


if __name__ == "__main__":
    unittest.main()
