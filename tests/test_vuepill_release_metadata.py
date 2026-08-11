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
EXPECTED_VERSION = "0.2.19"
NPM_CI_TIMEOUT_SECONDS = 300
NPM_BUILD_TIMEOUT_SECONDS = 180
BUILD_INPUT_PATHS = (
    "package.json",
    "package-lock.json",
    "index.html",
    "vite.config.js",
    "src/App.vue",
    "src/main.js",
    "src/components/Config.vue",
    "src/components/Page.vue",
    "src/utils/asyncGuards.js",
    "src/utils/configValidation.js",
    "src/utils/request.js",
)
EXPECTED_HISTORY_V0219 = (
    "修复 Vue-魔丸 在 MoviePilot 容器重启后主调度器可能先于插件加载完成、导致搬砖和沙滩任务未登记的问题；"
    "插件启动后会延迟自检并主动补登记，失败时继续重试，不改变搬砖 Cron、沙滩冷却和补跑规则。"
    "v0.2.x 小版本升级继续保留配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0218 = (
    "修复 Vue-魔丸 在 MoviePilot 容器更新后，后台插件同步再次初始化时停止旧实例会误删总调度任务的问题；"
    "现在插件只清理自己的临时任务，总调度任务由 MoviePilot 统一替换，即使后续同步流程中断也不会让"
    "搬砖和沙滩任务消失。v0.2.x 小版本升级继续保留配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0217 = (
    "修复 Vue-魔丸 在 MoviePilot 启动阶段清理旧任务时提前创建总调度器，"
    "导致插件尚未完成加载就被漏注册的问题；现在仅复用已经存在的总调度器，"
    "容器重启或更新后会正常注册初始化任务，并继续按搬砖 Cron 和沙滩冷却规则补跑。"
    "v0.2.x 小版本升级继续保留配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V029 = (
    "精简兑换魔力区域说明，物品栏与炼造工坊改为分别占据整行；新增批量赠送，"
    "可勾选多种物品共用一个 UID，后端先完整校验再顺序赠送，并在部分失败时停止和报告"
    "已成功项目；同一请求编号只执行一次，网络响应丢失后重试不会重复赠送。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0210 = (
    "修复 si-qi.xyz 真实赠送接口要求使用 uid 而插件发送 target_uid 导致的参数错误；"
    "单件赠送和批量赠送均已修正，继续保留批量完整校验、按顺序赠送、失败即停和请求防重复机制。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0211 = (
    "微调兑换与炼造工坊布局：隐藏后端上限提示，缩小数量输入框并让炼造配方改为紧凑三列；"
    "赠送功能仅允许砖块、木材、塑料袋、瓶子、螺丝、旧电池、破铜片和蚯蚓等基础垃圾，"
    "前后端同时校验，避免赠送合成物品。v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0213 = (
    "微调 Vue-魔丸 炼造工坊三列配方的操作区：数量框和炼造按钮统一靠右对齐，减少卡片空白，"
    "并保持浅色、深色和移动端布局；不可赠送物品不显示赠送控件。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0214 = (
    "修正 Vue-魔丸 炼造工坊操作区：配方名称与数量框、炼造按钮合并到同一行，材料独立排列，"
    "去掉重复的红色上限提示；手机端按标题、材料、操作纵向排列，并继续适配浅色和深色主题。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0216 = (
    "修复 Vue-魔丸 在 MoviePilot 容器重启或更新后，启动初始化和动态一次性任务可能因调度器"
    "启动较慢而被判定为错过的问题；任务迟到后仍会执行一次状态刷新，并沿用现有规则判断是否补跑。"
    "v0.2.x 小版本升级继续保留配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0215 = (
    "统一 Vue-魔丸 Cookie 配置为 Vue-思齐农场同款紧凑密码框，查看和站点同步按钮都放在输入框内；"
    "运行时优先读取 MoviePilot 的 si-qi.xyz 站点 Cookie，读取失败时才使用已保存值作为备用。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V0212 = (
    "继续微调 Vue-魔丸 物品栏和炼造工坊：不可赠送的物品保留库存信息但不显示赠送控件或技术提示，"
    "炼造配方卡统一为底部操作区并优化三列布局。v0.2.x 小版本升级保留现有配置、Cookie、"
    "执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V028 = (
    "恢复 v0.2.6 经确认的状态页排版与 Vue-农场同款自适应风格；"
    "撤销 v0.2.7 和未发布新版的任务优先重排，同时保留后来增加的接口防报错、"
    "数据校验和后端稳定性修复。v0.2.x 小版本升级保留现有配置、Cookie、"
    "执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V027 = (
    "状态页改为任务优先工作台：第一屏集中显示自动任务、下一触发动作和兑换；"
    "物品栏改为全宽紧凑网格，炼造工坊改为三列配方布局，并继续适配浅色、深色和手机页面。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V021 = (
    "修复真实魔丸页面因省略列表结束标签而解析失败、状态被错误保存为全零并跳过任务的问题，"
    "补充服务器时间与拖拽搬砖状态识别；启动或保存配置时会优先补跑已就绪沙滩，"
    "并将状态页、配置页统一为 Vue-农场同款自适应主题。v0.2.x 小版本升级保留现有配置、"
    "执行历史和动态调度计划，无需重新清配置。"
)
EXPECTED_HISTORY_V022 = (
    "新增与 Vue-农场一致的可隐藏手动 Cookie 输入：填写后优先使用手动 Cookie，"
    "清空后恢复 MoviePilot 站点自动同步；修复插件停止标记在更新后未解除，"
    "导致搬砖等手动任务持续提示“插件正在停止”的问题。v0.2.x 小版本升级保留现有配置、"
    "执行历史和动态调度计划，无需重新清配置。"
)
EXPECTED_HISTORY_V023 = (
    "修复搬砖完成当天剩余次数后仍多请求一次、导致成功记录夹带“已达上限”失败提示的问题；"
    "搬砖已满和沙滩冷却时按真实可执行状态显示文案；热更新传入空配置或同一 v0.2.x "
    "配置代号损坏时，会自动恢复 MoviePilot 已保存配置并保留执行历史和动态调度计划。"
)
EXPECTED_HISTORY_V024 = (
    "配置页自动读取并隐藏显示 MoviePilot 的 si-qi.xyz 站点 Cookie，未手动修改时继续保持自动同步，"
    "避免把自动值固化为旧 Cookie；移除状态页顶部执行按钮，并隐藏炼造上限为 0 和材料不足的重复提示。"
)
EXPECTED_HISTORY_V025 = (
    "修复通过插件管理中心重装或热更新后，Vue 页面 API 仍绑定已停止旧实例、"
    "点击刷新提示“插件正在停止”的问题；旧接口会安全转交给 MoviePilot 当前运行实例，"
    "没有新实例时继续拒绝执行，避免旧版本恢复运行。"
)
EXPECTED_HISTORY_V026 = (
    "状态页直接对齐 Vue-思齐农场 v1.0.3，搬砖与沙滩改为同款动态任务操作卡片，"
    "去除“后端标记”技术文案并改用正常业务状态；修正保留魔丸、随机延迟等数字输入值的"
    "垂直居中。v0.2.x 小版本升级保留现有配置、执行历史和动态调度计划，无需重新清配置。"
)
EXPECTED_HISTORY_V020 = (
    "重写 Vue-魔丸 页面和后端：移植 Vue-农场风格，修复真实配方/沙滩状态解析，"
    "加入手动赠送与赠礼统计；首次从 v0.1.x 更新到完整重写的 v0.2.0 后需手动重启一次 MoviePilot，"
    "重启后会一次性重置旧配置、执行历史和动态调度计划，后续 v0.2.x 更新会保留配置、"
    "执行历史和动态调度计划；"
    "插件不再提供强制 IPv4 设置，站点连接由系统自动选择可用的 IPv4 或 IPv6。"
)
EXPECTED_HISTORY_KEYS = [
    "v0.2.19",
    "v0.2.18",
    "v0.2.17",
    "v0.2.16",
    "v0.2.15",
    "v0.2.14",
    "v0.2.13",
    "v0.2.12",
    "v0.2.11",
    "v0.2.10",
    "v0.2.9",
    "v0.2.8",
    "v0.2.7",
    "v0.2.6",
    "v0.2.5",
    "v0.2.4",
    "v0.2.3",
    "v0.2.2",
    "v0.2.1",
    "v0.2.0",
    "v0.1.18",
    "v0.1.17",
    "v0.1.16",
    "v0.1.15",
    "v0.1.14",
    "v0.1.13",
    "v0.1.12",
    "v0.1.11",
    "v0.1.10",
    "v0.1.9",
    "v0.1.8",
    "v0.1.7",
    "v0.1.6",
    "v0.1.5",
    "v0.1.4",
    "v0.1.3",
    "v0.1.2",
    "v0.1.1",
    "v0.1.0",
]


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


def path_is_link_like(path: Path):
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def normalize_build_input_path(relative_path):
    normalized = Path(relative_path)
    if (
        normalized.is_absolute()
        or not normalized.parts
        or any(part == ".." for part in normalized.parts)
    ):
        raise AssertionError(f"构建输入路径逃逸：{relative_path}")
    return normalized


def stage_build_inputs(
    source_root: Path,
    staged_root: Path,
    *,
    build_inputs=BUILD_INPUT_PATHS,
):
    source_root = Path(source_root)
    staged_root = Path(staged_root)
    if not source_root.is_dir():
        raise AssertionError(f"构建输入根目录不存在：{source_root}")
    if path_is_link_like(source_root):
        raise AssertionError(f"构建输入根目录禁止符号链接或目录联接：{source_root}")
    if staged_root.exists() or path_is_link_like(staged_root):
        raise AssertionError(f"临时构建目录必须不存在：{staged_root}")

    source_root_resolved = source_root.resolve(strict=True)
    validated_inputs = []
    seen_inputs = set()
    for relative_text in build_inputs:
        relative_path = normalize_build_input_path(relative_text)
        relative_posix = relative_path.as_posix()
        if relative_posix in seen_inputs:
            raise AssertionError(f"构建输入白名单包含重复路径：{relative_posix}")
        seen_inputs.add(relative_posix)

        current_path = source_root
        for part in relative_path.parts:
            current_path = current_path / part
            if path_is_link_like(current_path):
                raise AssertionError(
                    f"构建输入禁止符号链接或目录联接：{relative_posix}"
                )

        source_path = source_root / relative_path
        if not source_path.exists():
            raise AssertionError(f"缺少必要构建文件：{relative_posix}")
        if not source_path.is_file():
            raise AssertionError(f"必要构建输入不是普通文件：{relative_posix}")

        resolved_source = source_path.resolve(strict=True)
        try:
            resolved_source.relative_to(source_root_resolved)
        except ValueError as error:
            raise AssertionError(f"构建输入路径逃逸：{relative_posix}") from error
        validated_inputs.append((relative_path, source_path))

    staged_root.mkdir(parents=True)
    staged_root_resolved = staged_root.resolve(strict=True)
    for relative_path, source_path in validated_inputs:
        destination_path = staged_root / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_parent = destination_path.parent.resolve(strict=True)
        try:
            resolved_parent.relative_to(staged_root_resolved)
        except ValueError as error:
            raise AssertionError(
                f"临时构建目标路径逃逸：{relative_path.as_posix()}"
            ) from error
        shutil.copy2(source_path, destination_path)


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
    @staticmethod
    def write_build_input_fixture(root: Path):
        for relative_path in BUILD_INPUT_PATHS:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"fixture:{relative_path}\n", encoding="utf-8")

    @staticmethod
    def replace_directory_with_test_link(link_path: Path, target_path: Path):
        shutil.rmtree(link_path)
        if os.name == "nt":
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", link_path, target_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if result.returncode != 0:
                raise AssertionError(
                    "当前 Windows 测试环境无法创建目录联接。\n"
                    f"stdout:\n{result.stdout}\n"
                    f"stderr:\n{result.stderr}"
                )
            return
        link_path.symlink_to(target_path, target_is_directory=True)

    @staticmethod
    def remove_test_directory_link(link_path: Path):
        if os.name == "nt":
            link_path.rmdir()
            return
        link_path.unlink()

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

    def test_build_input_staging_uses_only_the_explicit_whitelist(self):
        with TemporaryDirectory(prefix="vuepill-staging-whitelist-") as temp_dir:
            temp_root = Path(temp_dir)
            source_dir = temp_root / "source"
            staged_dir = temp_root / "staged"
            source_dir.mkdir()
            self.write_build_input_fixture(source_dir)

            secret_paths = (
                ".env.local",
                ".npmrc",
                "dist/secret.txt",
                "node_modules/secret.txt",
                "tests/secret.txt",
                ".git/config",
                ".playwright-cli/session.json",
                "src/.env.development.local",
                "src/untracked-secret.txt",
            )
            for relative_path in secret_paths:
                secret_path = source_dir / relative_path
                secret_path.parent.mkdir(parents=True, exist_ok=True)
                secret_path.write_text("must-not-copy", encoding="utf-8")

            stage_build_inputs(source_dir, staged_dir)
            staged_snapshot = snapshot_tree(staged_dir)

        self.assertEqual(sorted(BUILD_INPUT_PATHS), sorted(staged_snapshot))
        for secret_path in secret_paths:
            with self.subTest(secret_path=secret_path):
                self.assertNotIn(secret_path, staged_snapshot)

    def test_build_input_staging_rejects_symlink_missing_file_and_escape(self):
        with TemporaryDirectory(prefix="vuepill-staging-guards-") as temp_dir:
            temp_root = Path(temp_dir)
            source_dir = temp_root / "source"
            source_dir.mkdir()
            self.write_build_input_fixture(source_dir)

            outside_secret = temp_root / "outside-secret.txt"
            outside_secret.write_text("must-not-follow", encoding="utf-8")
            outside_utils = temp_root / "outside-utils"
            outside_utils.mkdir()
            for filename in (
                "asyncGuards.js",
                "configValidation.js",
                "request.js",
            ):
                (outside_utils / filename).write_text(
                    f"outside:{filename}\n",
                    encoding="utf-8",
                )
            (outside_utils / ".env.local").write_text(
                "must-not-follow",
                encoding="utf-8",
            )
            linked_input = source_dir / "src" / "utils"
            self.replace_directory_with_test_link(linked_input, outside_utils)

            with self.assertRaisesRegex(
                AssertionError,
                r"符号链接或目录联接.*src/utils",
            ):
                stage_build_inputs(source_dir, temp_root / "staged-symlink")

            self.remove_test_directory_link(linked_input)
            self.write_build_input_fixture(source_dir)
            (source_dir / "vite.config.js").unlink()
            with self.assertRaisesRegex(
                AssertionError,
                r"缺少必要构建文件.*vite\.config\.js",
            ):
                stage_build_inputs(source_dir, temp_root / "staged-missing")

            with self.assertRaisesRegex(AssertionError, r"路径逃逸"):
                stage_build_inputs(
                    source_dir,
                    temp_root / "staged-escape",
                    build_inputs=("../outside-secret.txt",),
                )

    def test_release_versions_are_consistent(self):
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

    def test_market_history_and_readme_describe_the_latest_release(self):
        market = read_json(ROOT / "package.v2.json")["VuePill"]
        history = market["history"]
        self.assertEqual(EXPECTED_HISTORY_KEYS, list(history))
        self.assertEqual(EXPECTED_HISTORY_V0219, history["v0.2.19"])
        for phrase in ("主调度器", "延迟自检", "主动补登记", "保留配置"):
            self.assertIn(phrase, history["v0.2.19"])
        self.assertEqual(EXPECTED_HISTORY_V0218, history["v0.2.18"])
        for phrase in ("后台插件同步", "停止旧实例", "总调度任务", "保留配置"):
            self.assertIn(phrase, history["v0.2.18"])
        self.assertEqual(EXPECTED_HISTORY_V0217, history["v0.2.17"])
        self.assertEqual(EXPECTED_HISTORY_V0216, history["v0.2.16"])
        for phrase in ("容器重启", "动态", "错过", "保留配置"):
            self.assertIn(phrase, history["v0.2.16"])
        self.assertEqual(EXPECTED_HISTORY_V0215, history["v0.2.15"])
        self.assertEqual(EXPECTED_HISTORY_V0214, history["v0.2.14"])
        self.assertEqual(EXPECTED_HISTORY_V0213, history["v0.2.13"])
        self.assertEqual(EXPECTED_HISTORY_V0212, history["v0.2.12"])
        self.assertEqual(EXPECTED_HISTORY_V0211, history["v0.2.11"])
        self.assertEqual(EXPECTED_HISTORY_V0210, history["v0.2.10"])
        self.assertEqual(EXPECTED_HISTORY_V029, history["v0.2.9"])
        self.assertEqual(EXPECTED_HISTORY_V028, history["v0.2.8"])
        self.assertEqual(EXPECTED_HISTORY_V027, history["v0.2.7"])
        self.assertEqual(EXPECTED_HISTORY_V026, history["v0.2.6"])
        self.assertEqual(EXPECTED_HISTORY_V025, history["v0.2.5"])
        self.assertEqual(EXPECTED_HISTORY_V024, history["v0.2.4"])
        self.assertEqual(EXPECTED_HISTORY_V023, history["v0.2.3"])
        self.assertEqual(EXPECTED_HISTORY_V022, history["v0.2.2"])
        self.assertEqual(EXPECTED_HISTORY_V021, history["v0.2.1"])
        self.assertEqual(EXPECTED_HISTORY_V020, history["v0.2.0"])

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required_readme_text = (
            "| `Vue-魔丸` | `v0.2.19` |",
            "主调度器可能先于插件加载完成",
            "延迟自检并主动补登记",
            "后台插件同步会再次初始化插件",
            "停止旧实例时误删全局动态任务",
            "启动时插件清理旧任务会提前创建总调度器",
            "尚未加载完成就漏注册",
            "启动初始化和动态搬砖、沙滩任务",
            "调度器启动较慢",
            "原有搬砖 Cron 和沙滩冷却规则",
            "Cookie 配置改为 `Vue-思齐农场` 同款紧凑密码框",
            "优先读取 MoviePilot 的 `si-qi.xyz` 站点 Cookie",
            "站点读取失败时才使用已保存值作为备用",
            "修正 Vue-魔丸 炼造工坊操作区",
            "配方名称与数量框、炼造按钮合并到同一行",
            "材料独立排列",
            "去掉重复的红色上限提示",
            "微调 Vue-魔丸 炼造工坊三列配方的操作区",
            "数量框和炼造按钮统一靠右对齐",
            "不可赠送的物品保留库存信息但不显示赠送控件",
            "炼造配方卡统一为底部操作区",
            "继续微调 Vue-魔丸 物品栏和炼造工坊",
            "隐藏后端上限提示",
            "紧凑三列",
            "仅允许砖块、木材、塑料袋、瓶子、螺丝、旧电池、破铜片和蚯蚓",
            "真实赠送接口要求使用 `uid`",
            "单件和批量赠送均已修正",
            "物品栏与炼造工坊分别占据整行",
            "批量赠送",
            "后端先完整校验再顺序赠送",
            "部分失败时停止并报告已成功项目",
            "网络响应丢失后重试不会重复赠送",
            "恢复 `v0.2.6` 经确认的状态页排版",
            "保留后来增加的接口防报错、数据校验和后端稳定性修复",
            "任务优先工作台",
            "物品栏改为全宽紧凑网格",
            "炼造工坊改为三列配方布局",
            "现有配置、Cookie、执行历史和动态调度计划",
            "状态页直接对齐 `Vue-思齐农场 v1.0.3`",
            "搬砖与沙滩改为同款动态任务操作卡片",
            "去除“后端标记”技术文案",
            "保留魔丸、随机延迟等数字输入值已垂直居中",
            "插件管理中心重装或热更新后",
            "Vue 页面 API 仍绑定已停止旧实例",
            "旧接口会安全转交给 MoviePilot 当前运行实例",
            "没有新实例时继续拒绝执行",
            "自动读取并隐藏显示 MoviePilot 的 `si-qi.xyz` 站点 Cookie",
            "未手动修改时继续保持自动同步",
            "状态页顶部的“执行”按钮已移除",
            "隐藏炼造上限为 0 和材料不足的重复提示",
            "修复搬砖成功 50 次后又误报“已达上限”为失败",
            "搬砖已满和沙滩冷却时会按真实状态显示",
            "收到空配置或配置代号损坏",
            "恢复 MoviePilot 已保存配置并保留执行历史和动态调度计划",
            "可隐藏的手动 Cookie 输入框",
            "填写后优先使用手动 Cookie",
            "清空后恢复 MoviePilot 站点自动同步",
            "修复更新后一直提示“插件正在停止”",
            "真实页面解析失败后把魔力、魔丸、搬砖、沙滩、库存和配方错误保存为全零",
            "补充服务器时间、拖拽搬砖状态和启动时沙滩补跑识别",
            "状态页和配置页统一使用 Vue-农场同款自适应主题",
            "无需重新清配置",
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
            "仅首次从 `v0.1.x` 更新到本次完整重写的 `v0.2.0` 后需手动重启一次 MoviePilot",
            "重启后会一次性重置旧配置、执行历史和动态调度计划",
            "后续 `v0.2.x` 更新会保留配置、执行历史和动态调度计划",
            "插件不再提供强制 IPv4 设置，站点连接由系统自动选择可用的 IPv4 或 IPv6。",
            "默认关闭",
            "手动刷新插件市场",
            "手动更新 `Vue-魔丸`",
            "不会自动安装或更新插件",
        )
        for token in required_readme_text:
            with self.subTest(token=token):
                self.assertIn(token, readme)

    def test_source_has_editable_cookie_only_on_config_page(self):
        page_source = (PLUGIN_DIR / "src" / "components" / "Page.vue").read_text(
            encoding="utf-8"
        )
        config_source = (
            PLUGIN_DIR / "src" / "components" / "Config.vue"
        ).read_text(encoding="utf-8")
        self.assertIn('v-model="config.cookie"', config_source)
        self.assertIn("showCookie", config_source)
        self.assertIn("cookieAutoFilled", config_source)
        self.assertIn("cookieEdited", config_source)
        self.assertIn("MoviePilot 站点 Cookie 优先", config_source)
        self.assertIn("同步失败时作为备用", config_source)
        self.assertIn("mdi-content-paste", config_source)
        self.assertIn("syncCookie", config_source)
        self.assertIn("/plugin/VuePill/cookie", config_source)
        self.assertNotIn("config.cookie", page_source)
        for forbidden in (
            "auto_cookie",
            "cookieFieldValue",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, f"{page_source}\n{config_source}")

    def test_application_entry_and_dist_have_no_development_api_or_debug_log(self):
        application_source = "\n".join(
            (
                (PLUGIN_DIR / "src" / "App.vue").read_text(encoding="utf-8"),
                (PLUGIN_DIR / "src" / "main.js").read_text(encoding="utf-8"),
                (PLUGIN_DIR / "src" / "utils" / "request.js").read_text(
                    encoding="utf-8"
                ),
            )
        )
        application_dist = (DIST_ASSETS_DIR / "index.js").read_text(
            encoding="utf-8",
            errors="replace",
        )

        targets = {
            "VuePill 应用入口源码": application_source,
            "VuePill 正式入口产物 dist/assets/index.js": application_dist,
        }
        for label, target_text in targets.items():
            with self.subTest(target=label, forbidden="http://localhost"):
                self.assertNotIn("http://localhost", target_text)
            with self.subTest(target=label, forbidden="localhost:3000"):
                self.assertNotIn("localhost:3000", target_text)
            with self.subTest(target=label, forbidden="10.x development API"):
                self.assertNotRegex(
                    target_text,
                    r"https?://10(?:\.\d{1,3}){3}(?::\d+)?",
                )
            with self.subTest(target=label, forbidden="VITE_API_BASE"):
                self.assertNotIn("VITE_API_BASE", target_text)
            with self.subTest(target=label, forbidden="debug console message"):
                self.assertNotIn("VuePill dev shell close event", target_text)

        self.assertNotRegex(application_source, r"console\.log\s*\(")

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
            stage_build_inputs(PLUGIN_DIR, temp_plugin_dir)
            self.assertEqual(
                sorted(BUILD_INPUT_PATHS),
                sorted(snapshot_tree(temp_plugin_dir)),
                "临时工程必须只包含显式构建输入白名单",
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

    def test_dist_contains_current_features_without_legacy_ui(self):
        asset_paths, dist_text = read_dist_text()
        self.assertTrue(asset_paths, "VuePill dist 中没有可检查的 JS/CSS 产物")

        for marker in (
            "siqi-page",
            "siqi-config",
            "gift-item",
            "gift-items",
            "批量赠送",
            "gift-stats",
            "VCronField",
            "config.cookie",
            "站点 Cookie",
            "MoviePilot 站点 Cookie 优先",
            "同步失败时作为备用",
            "cookieAutoFilled",
            "cookieEdited",
            "mdi-eye-outline",
            "mdi-content-paste",
            "/plugin/VuePill/cookie",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, dist_text)

        lowered_dist = dist_text.lower()
        for legacy_marker in ("vp-shell", "vp-page", "#7c5cff"):
            with self.subTest(legacy_marker=legacy_marker):
                self.assertNotIn(legacy_marker, lowered_dist)

        for forbidden_cookie_ui in (
            "站点 Cookie（留空自动同步）",
            "手动 Cookie 优先",
            "清空后恢复自动同步",
            "站点 Cookie：手动填写",
            "cookieFieldValue",
            "auto_cookie",
            "c_secure_pass",
        ):
            with self.subTest(forbidden_cookie_ui=forbidden_cookie_ui):
                self.assertNotIn(forbidden_cookie_ui, dist_text)


if __name__ == "__main__":
    unittest.main()
