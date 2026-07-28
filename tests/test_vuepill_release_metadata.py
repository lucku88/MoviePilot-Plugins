import json
import os
import re
import shutil
import subprocess
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "plugins.v2" / "vuepill"
DIST_DIR = PLUGIN_DIR / "dist"
DIST_ASSETS_DIR = DIST_DIR / "assets"
EXPECTED_VERSION = "0.2.0"
NPM_CI_TIMEOUT_SECONDS = 300
NPM_BUILD_TIMEOUT_SECONDS = 180
GENERATED_COPY_NAMES = frozenset(
    {
        ".nyc_output",
        ".playwright-cli",
        ".pytest_cache",
        ".ruff_cache",
        ".vite",
        "__pycache__",
        "coverage",
        "dist",
        "node_modules",
        "playwright-report",
        "test-results",
    }
)
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


def snapshot_tree(root: Path):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def compare_tree_snapshots(expected, actual):
    expected_paths = set(expected)
    actual_paths = set(actual)
    shared_paths = expected_paths & actual_paths
    return {
        "missing": sorted(expected_paths - actual_paths),
        "extra": sorted(actual_paths - expected_paths),
        "changed": sorted(
            path for path in shared_paths if expected[path] != actual[path]
        ),
    }


def format_tree_difference(difference, *, expected_label, actual_label):
    lines = [f"{expected_label} 与 {actual_label} 的文件树不一致："]
    sections = (
        ("missing", f"{actual_label} 缺失"),
        ("extra", f"{actual_label} 多余"),
        ("changed", "内容不同"),
    )
    for key, label in sections:
        paths = difference[key]
        if not paths:
            continue
        lines.append(f"{label}（{len(paths)} 个）：")
        lines.extend(f"  - {path}" for path in paths)
    return "\n".join(lines)


def ignore_generated_copy_paths(_directory, names):
    ignored = []
    for name in names:
        if name in GENERATED_COPY_NAMES:
            ignored.append(name)
            continue
        if name.endswith((".pyc", ".pyo", ".log")):
            ignored.append(name)
            continue
        if name.startswith(".Config.") and name.endswith(".mjs"):
            ignored.append(name)
    return ignored


def find_npm_executable():
    candidates = ("npm.cmd", "npm") if os.name == "nt" else ("npm", "npm.cmd")
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable:
            return executable
    raise AssertionError("找不到 npm 可执行文件（Windows 应提供 npm.cmd）")


def process_output(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def run_checked_command(command, *, cwd: Path, timeout_seconds: int, label: str):
    started_at = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        duration = time.perf_counter() - started_at
        raise AssertionError(
            f"{label} 超过明确超时 {timeout_seconds} 秒（已运行 {duration:.2f} 秒）\n"
            f"stdout:\n{process_output(error.stdout)}\n"
            f"stderr:\n{process_output(error.stderr)}"
        ) from error

    duration = time.perf_counter() - started_at
    if result.returncode != 0:
        raise AssertionError(
            f"{label} 失败，退出码 {result.returncode}，耗时 {duration:.2f} 秒。"
            "网络或 npm 错误不会被跳过。\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return duration, result


class VuePillReleaseMetadataTest(unittest.TestCase):
    def assert_tree_snapshots_equal(
        self,
        expected,
        actual,
        *,
        expected_label,
        actual_label,
    ):
        difference = compare_tree_snapshots(expected, actual)
        if any(difference.values()):
            self.fail(
                format_tree_difference(
                    difference,
                    expected_label=expected_label,
                    actual_label=actual_label,
                )
            )

    def assert_federation_references_resolve(self, dist_assets_dir: Path):
        remote_entries = list(dist_assets_dir.rglob("remoteEntry.js"))
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
            built_assets = sorted(
                path.resolve()
                for path in dist_assets_dir.rglob(
                    f"__federation_expose_{module_name}-*.js"
                )
            )
            self.assertEqual([referenced_asset], built_assets)

    def test_tree_diff_probe_reports_missing_extra_and_changed_files(self):
        with TemporaryDirectory(prefix="vuepill-release-probe-") as temp_dir:
            probe_root = Path(temp_dir)
            baseline_dir = probe_root / "baseline"
            candidate_dir = probe_root / "candidate"
            baseline_dir.mkdir()
            candidate_dir.mkdir()

            (baseline_dir / "same.txt").write_bytes(b"same")
            (candidate_dir / "same.txt").write_bytes(b"same")
            (baseline_dir / "missing.txt").write_bytes(b"baseline only")
            (candidate_dir / "extra.txt").write_bytes(b"candidate only")
            (baseline_dir / "changed.bin").write_bytes(b"before")
            (candidate_dir / "changed.bin").write_bytes(b"after")

            difference = compare_tree_snapshots(
                snapshot_tree(baseline_dir),
                snapshot_tree(candidate_dir),
            )
            message = format_tree_difference(
                difference,
                expected_label="baseline",
                actual_label="candidate",
            )

        self.assertEqual(["missing.txt"], difference["missing"])
        self.assertEqual(["extra.txt"], difference["extra"])
        self.assertEqual(["changed.bin"], difference["changed"])
        self.assertIn("missing.txt", message)
        self.assertIn("extra.txt", message)
        self.assertIn("changed.bin", message)

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
        self.assert_federation_references_resolve(DIST_ASSETS_DIR)

    def test_clean_npm_build_matches_committed_dist_byte_for_byte(self):
        source_lock_before = (PLUGIN_DIR / "package-lock.json").read_bytes()
        source_dist_before = snapshot_tree(DIST_ASSETS_DIR)
        self.assertTrue(source_dist_before, "仓库没有已提交的 VuePill dist/assets 基线")

        def assert_source_release_files_unchanged():
            self.assertEqual(
                source_lock_before,
                (PLUGIN_DIR / "package-lock.json").read_bytes(),
                "clean build 测试修改了源工作树 package-lock.json",
            )
            self.assert_tree_snapshots_equal(
                source_dist_before,
                snapshot_tree(DIST_ASSETS_DIR),
                expected_label="测试前源工作树 dist/assets",
                actual_label="测试后源工作树 dist/assets",
            )

        self.addCleanup(assert_source_release_files_unchanged)

        npm_executable = find_npm_executable()
        with TemporaryDirectory(prefix="vuepill-clean-build-") as temp_dir:
            temp_plugin_dir = Path(temp_dir) / "vuepill"
            shutil.copytree(
                PLUGIN_DIR,
                temp_plugin_dir,
                ignore=ignore_generated_copy_paths,
            )

            required_paths = (
                "package.json",
                "package-lock.json",
                "vite.config.js",
                "index.html",
                "src",
            )
            for relative_path in required_paths:
                with self.subTest(required_path=relative_path):
                    self.assertTrue((temp_plugin_dir / relative_path).exists())

            copied_generated_paths = sorted(
                path.relative_to(temp_plugin_dir).as_posix()
                for path in temp_plugin_dir.rglob("*")
                if path.name in GENERATED_COPY_NAMES
            )
            self.assertEqual(
                [],
                copied_generated_paths,
                "临时工程复制进了应排除的生成目录",
            )

            temp_lock_path = temp_plugin_dir / "package-lock.json"
            self.assertEqual(source_lock_before, temp_lock_path.read_bytes())

            ci_duration, _ci_result = run_checked_command(
                [npm_executable, "ci"],
                cwd=temp_plugin_dir,
                timeout_seconds=NPM_CI_TIMEOUT_SECONDS,
                label="临时副本 npm ci",
            )
            self.assertEqual(
                source_lock_before,
                temp_lock_path.read_bytes(),
                "npm ci 修改了临时副本 package-lock.json",
            )

            build_duration, _build_result = run_checked_command(
                [npm_executable, "run", "build"],
                cwd=temp_plugin_dir,
                timeout_seconds=NPM_BUILD_TIMEOUT_SECONDS,
                label="临时副本 npm run build",
            )
            self.assertEqual(
                source_lock_before,
                temp_lock_path.read_bytes(),
                "npm run build 修改了临时副本 package-lock.json",
            )

            clean_dist_assets = temp_plugin_dir / "dist" / "assets"
            clean_dist_snapshot = snapshot_tree(clean_dist_assets)
            self.assert_tree_snapshots_equal(
                source_dist_before,
                clean_dist_snapshot,
                expected_label="仓库已提交 dist/assets",
                actual_label="临时 clean build dist/assets",
            )
            self.assert_federation_references_resolve(clean_dist_assets)

            print(
                "VuePill clean build："
                f"npm ci {ci_duration:.2f} 秒，"
                f"npm run build {build_duration:.2f} 秒，"
                f"逐字节比对 {len(source_dist_before)} 个文件。",
                flush=True,
            )

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
