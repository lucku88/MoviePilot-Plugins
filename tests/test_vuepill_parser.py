import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "vuepill_page.html"
PARSER_PATH = REPO_ROOT / "plugins.v2" / "vuepill" / "page_parser.py"


def _load_parser_module():
    module_name = "vuepill_page_parser_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, PARSER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载页面解析模块: {PARSER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_parse_page():
    return _load_parser_module().parse_page


class VuePillParserTests(unittest.TestCase):
    def assert_actions_disabled(self, data):
        self.assertIs(data["brick"]["ready"], False)
        self.assertIs(data["beach"]["ready"], False)
        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["can_collect"], False)
        self.assertIs(data["beach"]["collect_enabled"], False)
        self.assertIs(data["exchange"]["enabled"], False)
        self.assertIs(data["exchange"]["action_ready"], False)
        for recipe in data.get("recipes") or []:
            self.assertIs(recipe["enabled"], False)
            self.assertIs(recipe["can_craft"], False)
            self.assertIs(recipe["disabled"], True)

    def parse_fixture(self):
        self.assertTrue(PARSER_PATH.exists(), "page_parser.py 尚未创建")
        parse_page = _load_parse_page()
        return parse_page(FIXTURE.read_text(encoding="utf-8"), now_ts=1785100000)

    def movable_brick_html(
        self,
        *,
        daily_bricks="1",
        daily_limit="50",
        factory_count="49",
        brick_status="可以搬砖",
    ):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="dailyBricks">50</span>/50',
            f'id="dailyBricks">{daily_bricks}</span>/{daily_limit}',
        )
        html = html.replace(
            'id="brickFactory" draggable="true" '
            'style="pointer-events:none;opacity:0.5;"',
            'id="brickFactory" draggable="true"',
        )
        html = html.replace(
            'id="factoryBrickCount">可搬: 0块',
            f'id="factoryBrickCount">可搬: {factory_count}块',
        )
        html = html.replace(
            '<span class="countdown">今日已达上限，明日可搬: 10:39:29</span>',
            f'<span>{brick_status}</span>',
        )
        return html

    def test_parse_page_reads_stats_inventory_and_giftable_items(self):
        data = self.parse_fixture()

        self.assertIs(data.get("parse_complete"), True)
        self.assertEqual("", data.get("parse_error"))
        self.assertEqual(73037, data["stats"]["points"])
        self.assertEqual(331000, data["stats"]["bonus_earned"])
        self.assertEqual(57, data["stats"]["magic_pills"])
        self.assertEqual(50, data["stats"]["daily_bricks"])
        self.assertEqual(50, data["stats"]["daily_limit"])
        self.assertEqual(14, len(data["inventory"]))
        self.assertIs(data["inventory"][0]["giftable"], True)
        magic_pill = next(item for item in data["inventory"] if item["name"] == "魔丸")
        self.assertEqual(57, magic_pill["count"])
        self.assertIs(magic_pill["giftable"], False)

    def test_empty_page_is_fail_closed(self):
        parse_page = _load_parse_page()

        data = parse_page("", now_ts=1785100000)

        self.assertIs(data.get("parse_complete"), False)
        self.assertTrue(data.get("parse_error"))
        self.assert_actions_disabled(data)

    def test_optional_li_end_tag_does_not_invalidate_game_page(self):
        parse_page = _load_parse_page()
        html = FIXTURE.read_text(encoding="utf-8")
        html += "<ul><li>浏览器允许省略列表项结束标签</ul>"

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data.get("parse_complete"), True)
        self.assertEqual("", data.get("parse_error"))
        self.assertEqual(73037, data["stats"]["points"])

    def test_missing_brick_factory_nodes_is_fail_closed(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="dailyBricks">50</span>/50',
            'id="dailyBricks">1</span>/50',
        )
        html = html.replace('id="brickFactory"', 'id="missingBrickFactory"')
        html = html.replace(
            'id="factoryBrickCount"',
            'id="missingFactoryBrickCount"',
        )
        html = html.replace(
            '<span class="countdown">今日已达上限，明日可搬: 10:39:29</span>',
            '<span>可以搬砖</span>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["brick"]["ready"], False)
        self.assertIs(data.get("parse_complete"), False)
        self.assert_actions_disabled(data)

    def test_invalid_daily_bricks_is_fail_closed(self):
        parse_page = _load_parse_page()

        valid_data = parse_page(self.movable_brick_html(), now_ts=1785100000)
        self.assertIs(valid_data.get("parse_complete"), True)
        self.assertIs(valid_data["brick"]["ready"], True)

        for invalid_value in ("", "broken", "-1", "49broken"):
            with self.subTest(invalid_value=invalid_value):
                data = parse_page(
                    self.movable_brick_html(daily_bricks=invalid_value),
                    now_ts=1785100000,
                )

                self.assertIs(data.get("parse_complete"), False)
                self.assertIn("dailyBricks", data.get("parse_error") or "")
                self.assert_actions_disabled(data)

    def test_invalid_brick_limit_or_factory_count_is_fail_closed(self):
        parse_page = _load_parse_page()
        cases = {
            "empty_limit": {"daily_limit": ""},
            "broken_limit": {"daily_limit": "broken"},
            "negative_limit": {"daily_limit": "-1"},
            "mixed_limit": {"daily_limit": "50broken"},
            "mixed_factory_count": {"factory_count": "49broken"},
        }

        for case_name, values in cases.items():
            with self.subTest(case_name=case_name):
                data = parse_page(
                    self.movable_brick_html(**values),
                    now_ts=1785100000,
                )

                self.assertIs(data.get("parse_complete"), False)
                self.assertTrue(data.get("parse_error"))
                self.assert_actions_disabled(data)

    def test_brick_requires_explicit_ready_status(self):
        parse_page = _load_parse_page()

        for status_text in ("", "工坊状态未知", "处理中"):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data.get("parse_complete"), True)
                self.assertIs(data["brick"]["ready"], False)

        ready_data = parse_page(
            self.movable_brick_html(brick_status="立即搬"),
            now_ts=1785100000,
        )
        self.assertIs(ready_data["brick"]["ready"], True)

        drag_ready_data = parse_page(
            self.movable_brick_html(brick_status="拖拽砖块到口袋"),
            now_ts=1785100000,
        )
        self.assertIs(drag_ready_data["brick"]["ready"], True)

    def test_server_time_offset_expression_is_used_as_server_now(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '"server_now": 1785100000,',
            "serverTimeOffset: 1785100000 - Math.floor(Date.now() / 1000),",
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            "可进入清理",
        )
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        parse_page = _load_parse_page()

        data = parse_page(html)

        self.assertIs(data.get("parse_complete"), True)
        self.assertEqual(1785100000, data["server_now"])
        self.assertIs(data["beach"]["can_enter"], True)
        self.assertIs(data["beach"]["ready"], True)

    def test_brick_negative_phrases_do_not_match_ready_substrings(self):
        parse_page = _load_parse_page()

        for status_text in (
            "尚未可搬",
            "预计可搬时间未到",
            "尚未可以搬砖",
            "不可以搬砖",
            "不可搬砖",
            "不能搬砖",
            "还不能搬",
            "冷却中",
            "等待",
        ):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data["brick"]["ready"], False)

        for status_text in ("可以搬砖", "可搬砖", "立即搬砖", "立即搬"):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data["brick"]["ready"], True)

    def test_brick_generic_negative_signals_block_ready(self):
        parse_page = _load_parse_page()

        for status_text in (
            "无法立即搬砖",
            "不能立即搬砖",
            "暂无可搬砖任务",
            "没有可搬砖任务",
            "尚未立即搬砖",
            "未到时间，可以搬砖",
            "冷却结束后可以搬砖",
            "等待后可以搬砖",
            "稍后可以搬砖",
        ):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data["brick"]["ready"], False)

        for status_text in ("可以搬砖", "可搬砖", "立即搬砖"):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data["brick"]["ready"], True)

    def test_prohibitive_status_roots_block_brick_ready(self):
        parse_page = _load_parse_page()

        for status_text in (
            "请勿立即搬砖",
            "禁止立即搬砖",
            "严禁立即搬砖",
            "暂停立即搬砖",
            "停止立即搬砖",
            "关闭立即搬砖",
            "禁用立即搬砖",
        ):
            with self.subTest(status_text=status_text):
                data = parse_page(
                    self.movable_brick_html(brick_status=status_text),
                    now_ts=1785100000,
                )

                self.assertIs(data["brick"]["ready"], False)

        ready_data = parse_page(
            self.movable_brick_html(brick_status="立即搬砖"),
            now_ts=1785100000,
        )
        self.assertIs(ready_data["brick"]["ready"], True)

    def test_truncated_inventory_grid_is_fail_closed(self):
        html = FIXTURE.read_text(encoding="utf-8")
        marker = '<div class="inventory-grid" id="inventoryGrid">'
        self.assertIn(marker, html)
        truncated_html = html[: html.index(marker) + len(marker)]
        parse_page = _load_parse_page()

        data = parse_page(truncated_html, now_ts=1785100000)

        self.assertIs(data.get("parse_complete"), False)
        self.assertIn("unclosed", (data.get("parse_error") or "").lower())
        self.assert_actions_disabled(data)

    def test_tree_parser_exception_is_fail_closed(self):
        module = _load_parser_module()
        html = FIXTURE.read_text(encoding="utf-8")

        with mock.patch.object(
            module._TreeParser,
            "feed",
            side_effect=RuntimeError("tree exploded"),
        ):
            data = module.parse_page(html, now_ts=1785100000)

        self.assertIs(data.get("parse_complete"), False)
        self.assertIn("tree exploded", data.get("parse_error") or "")
        self.assert_actions_disabled(data)

    def test_missing_beach_time_evidence_cannot_enter(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace('"server_now"', '"ignored_server_now"')
        html = html.replace('"last_beach_time"', '"ignored_last_beach_time"')
        html = html.replace('"beach_interval"', '"ignored_beach_interval"')
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data.get("parse_complete"), True)
        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)
        self.assertEqual(0, data["beach"]["next_ready_ts"])

    def test_invalid_beach_time_evidence_is_fail_closed(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785090000',
        )
        cases = {
            "missing_server": (
                '"server_now": 1785100000',
                '"ignored_server_now": 1785100000',
            ),
            "missing_last": (
                '"last_beach_time": 1785090000',
                '"ignored_last_beach_time": 1785090000',
            ),
            "missing_interval": (
                '"beach_interval": 7200',
                '"ignored_beach_interval": 7200',
            ),
            "zero_server": ('"server_now": 1785100000', '"server_now": 0'),
            "zero_last": (
                '"last_beach_time": 1785090000',
                '"last_beach_time": 0',
            ),
            "zero_interval": ('"beach_interval": 7200', '"beach_interval": 0'),
            "negative_server": (
                '"server_now": 1785100000',
                '"server_now": -1',
            ),
            "negative_last": (
                '"last_beach_time": 1785090000',
                '"last_beach_time": -1',
            ),
            "negative_interval": (
                '"beach_interval": 7200',
                '"beach_interval": -1',
            ),
            "damaged_interval": (
                '"beach_interval": 7200',
                '"beach_interval": "broken"',
            ),
        }
        parse_page = _load_parse_page()

        for case_name, (original, replacement) in cases.items():
            with self.subTest(case_name=case_name):
                case_html = html.replace(original, replacement)
                self.assertNotEqual(html, case_html)

                data = parse_page(case_html, now_ts=1785100000)

                self.assertIs(data.get("parse_complete"), True)
                self.assertIs(data["beach"]["can_enter"], False)
                self.assertIs(data["beach"]["ready"], False)

    def test_script_number_rejects_garbage_after_numeric_prefix(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785090000',
        )
        parse_page = _load_parse_page()

        for invalid_value in ('"7200broken"', '"7200abc"'):
            with self.subTest(invalid_value=invalid_value):
                case_html = html.replace(
                    '"beach_interval": 7200',
                    f'"beach_interval": {invalid_value}',
                )

                data = parse_page(case_html, now_ts=1785100000)

                self.assertIs(data["beach"]["can_enter"], False)
                self.assertIs(data["beach"]["ready"], False)

        for valid_value in ("7200", '"7200"', '"7,200"'):
            with self.subTest(valid_value=valid_value):
                case_html = html.replace(
                    '"beach_interval": 7200',
                    f'"beach_interval": {valid_value}',
                )

                data = parse_page(case_html, now_ts=1785100000)

                self.assertIs(data["beach"]["can_enter"], True)
                self.assertIs(data["beach"]["ready"], True)

    def test_disabled_beach_with_countdown_is_not_ready(self):
        data = self.parse_fixture()

        self.assertIs(data["beach"]["ready"], False)
        self.assertIs(data["beach"]["collect_enabled"], False)
        self.assertEqual(1785100375, data["beach"]["next_ready_ts"])

    def test_enabled_beach_with_countdown_cannot_enter(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)

    def test_millisecond_timestamps_keep_second_beach_interval(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"server_now": 1785100000',
            '"server_now": 1785100000000',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785096400000',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertEqual(1785100000, data["server_now"])
        self.assertEqual(1785103600, data["beach"]["next_ready_ts"])
        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)

    def test_millisecond_beach_interval_is_normalised(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785099700',
        )
        html = html.replace(
            '"beach_interval": 7200',
            '"beach_interval": 7200000',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertEqual(1785106900, data["beach"]["next_ready_ts"])
        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)

    def test_long_second_beach_interval_stays_in_seconds(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785090000',
        )
        html = html.replace(
            '"beach_interval": 7200',
            '"beach_interval": 60000',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertEqual(1785150000, data["beach"]["next_ready_ts"])
        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)

    def test_script_time_ignores_comments_and_template_values(self):
        html = (
            '<script type="text/template">'
            '{"server_now": 1, "last_beach_time": 1, "beach_interval": 1}'
            '</script>'
            '<script>// const gameData = {"server_now": 2, '
            '"last_beach_time": 2, "beach_interval": 2};</script>'
            + FIXTURE.read_text(encoding="utf-8")
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertEqual(1785100000, data["server_now"])
        self.assertEqual(1785100375, data["beach"]["next_ready_ts"])

    def test_invalid_exchange_magic_pills_is_fail_closed(self):
        parse_page = _load_parse_page()

        for invalid_value in ("", "-1", "57.5", "57broken"):
            with self.subTest(invalid_value=invalid_value):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    'id="magicPills">57</span>',
                    f'id="magicPills">{invalid_value}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data.get("parse_complete"), False)
                self.assertIn("magicPills", data.get("parse_error") or "")
                self.assert_actions_disabled(data)

    def test_invalid_exchange_max_is_fail_closed(self):
        parse_page = _load_parse_page()

        for invalid_value in ("", "-1", "1.5", "57broken"):
            with self.subTest(invalid_value=invalid_value):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    'id="exchangeCount" value="1" min="1" max="57"',
                    'id="exchangeCount" value="1" min="1" '
                    f'max="{invalid_value}"',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data.get("parse_complete"), False)
                self.assertIn("exchangeCount.max", data.get("parse_error") or "")
                self.assert_actions_disabled(data)

    def test_disabled_exchange_input_is_not_actionable(self):
        parse_page = _load_parse_page()
        input_attributes = {
            "disabled": 'disabled=""',
            "aria_disabled": 'aria-disabled="true"',
            "pointer_events": 'style="pointer-events: none"',
        }

        valid_data = parse_page(
            FIXTURE.read_text(encoding="utf-8"),
            now_ts=1785100000,
        )
        self.assertIs(valid_data["exchange"]["enabled"], True)
        self.assertIs(valid_data["exchange"]["action_ready"], True)

        for case_name, attributes in input_attributes.items():
            with self.subTest(case_name=case_name):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    'id="exchangeCount" value="1" min="1" max="57"',
                    'id="exchangeCount" value="1" min="1" max="57" '
                    f'{attributes}',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data.get("parse_complete"), True)
                self.assertIs(data["exchange"]["enabled"], False)
                self.assertIs(data["exchange"]["action_ready"], False)

    def test_existing_trash_keeps_collect_action_available(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area" id="beachArea">'
            '<span class="trash-item">待收瓶子</span></div>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["collect_enabled"], False)
        self.assertIs(data["beach"]["has_trash"], True)
        self.assertIs(data["beach"]["can_collect"], True)

    def test_real_trash_node_overrides_stale_no_trash_status(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area" id="beachArea">'
            '<span class="trash-item">待收瓶子</span></div>',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>暂无待收垃圾</span>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["has_trash"], True)
        self.assertIs(data["beach"]["can_collect"], True)

    def test_negative_trash_status_does_not_report_trash(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>暂无待收垃圾</span>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["has_trash"], False)
        self.assertIs(data["beach"]["can_collect"], False)

    def test_negative_collect_status_never_implies_trash(self):
        parse_page = _load_parse_page()

        for status_text in (
            "当前不可收集",
            "不可收集",
            "暂无待收垃圾",
            "没有垃圾",
            "已清理",
        ):
            with self.subTest(status_text=status_text):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    '<span class="countdown">下次清理: 0:06:15</span>',
                    f'<span>{status_text}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data["beach"]["collect_enabled"], False)
                self.assertIs(data["beach"]["has_trash"], False)
                self.assertIs(data["beach"]["can_collect"], False)

    def test_collect_status_uses_complete_positive_phrases(self):
        parse_page = _load_parse_page()

        for status_text in (
            "尚未可收集",
            "未可收集",
            "尚未可以收集垃圾",
            "不可以收集垃圾",
            "不可收集",
            "不能收集",
            "无法收集",
            "还不能收集",
        ):
            with self.subTest(status_text=status_text):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    '<span class="countdown">下次清理: 0:06:15</span>',
                    f'<span>{status_text}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data["beach"]["has_trash"], False)
                self.assertIs(data["beach"]["can_collect"], False)

        for status_text in (
            "待收垃圾",
            "发现垃圾",
            "可收集垃圾",
            "可以收集垃圾",
            "垃圾待收",
        ):
            with self.subTest(status_text=status_text):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    '<span class="countdown">下次清理: 0:06:15</span>',
                    f'<span>{status_text}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data["beach"]["has_trash"], True)
                self.assertIs(data["beach"]["can_collect"], True)

    def test_beach_generic_negative_signals_block_text_only_trash(self):
        parse_page = _load_parse_page()

        for status_text in (
            "暂无可收集垃圾",
            "没有可收集垃圾",
            "无可收集垃圾",
            "垃圾暂时不能收集",
            "尚未发现垃圾",
            "等待发现垃圾",
            "稍后可以收集垃圾",
        ):
            with self.subTest(status_text=status_text):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    '<span class="countdown">下次清理: 0:06:15</span>',
                    f'<span>{status_text}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data["beach"]["has_trash"], False)
                self.assertIs(data["beach"]["can_collect"], False)

        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area" id="beachArea">'
            '<span class="trash-item">待收瓶子</span></div>',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>没有可收集垃圾</span>',
        )

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["has_trash"], True)
        self.assertIs(data["beach"]["can_collect"], True)

    def test_zero_trash_counts_do_not_imply_trash(self):
        parse_page = _load_parse_page()

        for status_text in (
            "可收集垃圾：0",
            "待收垃圾 0件",
            "零个可收集垃圾",
        ):
            with self.subTest(status_text=status_text):
                html = FIXTURE.read_text(encoding="utf-8").replace(
                    '<span class="countdown">下次清理: 0:06:15</span>',
                    f'<span>{status_text}</span>',
                )

                data = parse_page(html, now_ts=1785100000)

                self.assertIs(data["beach"]["collect_enabled"], False)
                self.assertIs(data["beach"]["has_trash"], False)
                self.assertIs(data["beach"]["can_collect"], False)

        enabled_html = FIXTURE.read_text(encoding="utf-8")
        enabled_html = enabled_html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>可收集垃圾：0</span>',
        )
        enabled_html = enabled_html.replace(
            'id="collectAllTrashBtn" onclick="collectAllTrash()" disabled=""',
            'id="collectAllTrashBtn" onclick="collectAllTrash()"',
        )

        enabled_data = parse_page(enabled_html, now_ts=1785100000)

        self.assertIs(enabled_data["beach"]["collect_enabled"], True)
        self.assertIs(enabled_data["beach"]["has_trash"], False)
        self.assertIs(enabled_data["beach"]["can_collect"], True)

        trash_html = FIXTURE.read_text(encoding="utf-8")
        trash_html = trash_html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area" id="beachArea">'
            '<span class="trash-item">待收瓶子</span></div>',
        )
        trash_html = trash_html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>可收集垃圾：0</span>',
        )

        trash_data = parse_page(trash_html, now_ts=1785100000)

        self.assertIs(trash_data["beach"]["has_trash"], True)
        self.assertIs(trash_data["beach"]["can_collect"], True)

    def test_no_trash_class_and_text_do_not_report_trash(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area no-trash" id="beachArea">'
            '暂无待收垃圾</div>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["has_trash"], False)
        self.assertIs(data["beach"]["can_collect"], False)

    def test_empty_trash_list_container_does_not_report_trash(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<div class="beach-area" id="beachArea"></div>',
            '<div class="beach-area trash-list" id="beachArea"></div>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["has_trash"], False)
        self.assertIs(data["beach"]["can_collect"], False)

    def test_enabled_collect_button_does_not_imply_trash(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>垃圾已清理</span>',
        )
        html = html.replace(
            'id="collectAllTrashBtn" onclick="collectAllTrash()" disabled=""',
            'id="collectAllTrashBtn" onclick="collectAllTrash()"',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["collect_enabled"], True)
        self.assertIs(data["beach"]["has_trash"], False)
        self.assertIs(data["beach"]["can_collect"], True)

    def test_pointer_events_none_disables_beach_buttons(self):
        html = FIXTURE.read_text(encoding="utf-8")
        html = html.replace(
            'id="beachBtn" onclick="enterBeach()" disabled=""',
            'id="beachBtn" onclick="enterBeach()" '
            'style="pointer-events: none"',
        )
        html = html.replace(
            'id="collectAllTrashBtn" onclick="collectAllTrash()" disabled=""',
            'id="collectAllTrashBtn" onclick="collectAllTrash()" '
            'style="pointer-events: none"',
        )
        html = html.replace(
            '<span class="countdown">下次清理: 0:06:15</span>',
            '<span>沙滩可以清理</span>',
        )
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["can_enter"], False)
        self.assertIs(data["beach"]["ready"], False)
        self.assertIs(data["beach"]["collect_enabled"], False)
        self.assertIs(data["beach"]["can_collect"], False)

    def test_enabled_beach_without_countdown_is_ready(self):
        html = FIXTURE.read_text(encoding="utf-8")
        disabled_button = 'id="beachBtn" onclick="enterBeach()" disabled=""'
        countdown = '<span class="countdown">下次清理: 0:06:15</span>'
        self.assertIn(disabled_button, html)
        self.assertIn(countdown, html)
        self.assertIn('"last_beach_time": 1785080000', html)
        html = html.replace(
            disabled_button,
            'id="beachBtn" onclick="enterBeach()"',
        )
        html = html.replace(
            countdown,
            '<span>沙滩可以清理</span>',
        )
        html = html.replace(
            '"last_beach_time": 1785080000',
            '"last_beach_time": 1785090000',
        )
        self.assertTrue(PARSER_PATH.exists(), "page_parser.py 尚未创建")
        parse_page = _load_parse_page()

        data = parse_page(html, now_ts=1785100000)

        self.assertIs(data["beach"]["ready"], True)

    def test_nested_recipe_cards_keep_all_six_ids_and_limits(self):
        data = self.parse_fixture()
        recipes = {row["craft_id"]: row for row in data["recipes"]}

        self.assertEqual({1, 2, 3, 4, 5, 6}, set(recipes))
        self.assertEqual(8, recipes[1]["max_count"])
        self.assertEqual(2, recipes[6]["ingredients"]["魔丸胚胎"])

    def test_recipe_without_matching_quantity_input_is_disabled(self):
        module = _load_parser_module()
        html = '''
        <div id="recipeGrid">
            <div class="recipe can-craft">
                <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                <span class="material-item">🧱砖块: 42/5</span>
                <span class="material-item">🪵木材: 10/1</span>
                <span class="material-item">🛍️塑料袋: 10/1</span>
                <button onclick="craft(1)">炼造</button>
            </div>
        </div>
        '''

        recipe = module.parse_recipes(html, [])[0]

        self.assertIs(recipe["enabled"], False)
        self.assertIs(recipe["can_craft"], False)
        self.assertIs(recipe["disabled"], True)

    def test_recipe_with_wrong_quantity_input_id_is_disabled(self):
        module = _load_parser_module()
        html = '''
        <div id="recipeGrid">
            <div class="recipe can-craft">
                <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                <span class="material-item">🧱砖块: 42/5</span>
                <span class="material-item">🪵木材: 10/1</span>
                <span class="material-item">🛍️塑料袋: 10/1</span>
                <input class="craft-input" max="8" id="craft-99">
                <button onclick="craft(1)">炼造</button>
            </div>
        </div>
        '''

        recipe = module.parse_recipes(html, [])[0]

        self.assertIs(recipe["enabled"], False)
        self.assertIs(recipe["can_craft"], False)
        self.assertIs(recipe["disabled"], True)

    def test_disabled_recipe_quantity_input_is_not_craftable(self):
        module = _load_parser_module()
        disabled_attributes = {
            "disabled": 'disabled=""',
            "aria_disabled": 'aria-disabled="true"',
            "pointer_events": 'style="pointer-events: none"',
        }

        for case_name, attributes in disabled_attributes.items():
            with self.subTest(case_name=case_name):
                html = f'''
                <div id="recipeGrid">
                    <div class="recipe can-craft">
                        <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                        <span class="material-item">🧱砖块: 42/5</span>
                        <span class="material-item">🪵木材: 10/1</span>
                        <span class="material-item">🛍️塑料袋: 10/1</span>
                        <input class="craft-input" max="8" id="craft-1" {attributes}>
                        <button onclick="craft(1)">炼造</button>
                    </div>
                </div>
                '''

                recipe = module.parse_recipes(html, [])[0]

                self.assertIs(recipe["enabled"], False)
                self.assertIs(recipe["can_craft"], False)
                self.assertIs(recipe["disabled"], True)

    def test_recipe_rejects_invalid_max_and_material_numbers(self):
        module = _load_parser_module()
        cases = {
            "max_suffix": {"max_value": "8broken"},
            "max_decimal": {"max_value": "8.5"},
            "available_suffix": {"brick_amount": "42broken/5"},
            "available_decimal": {"brick_amount": "42.5/5"},
            "required_suffix": {"brick_amount": "42/5broken"},
            "required_decimal": {"brick_amount": "42/5.5"},
        }

        for case_name, values in cases.items():
            with self.subTest(case_name=case_name):
                max_value = values.get("max_value", "8")
                brick_amount = values.get("brick_amount", "42/5")
                html = f'''
                <div id="recipeGrid">
                    <div class="recipe can-craft">
                        <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                        <span class="material-item">🧱砖块: {brick_amount}</span>
                        <span class="material-item">🪵木材: 10/1</span>
                        <span class="material-item">🛍️塑料袋: 10/1</span>
                        <input class="craft-input" max="{max_value}" id="craft-1">
                        <button onclick="craft(1)">炼造</button>
                    </div>
                </div>
                '''

                recipe = module.parse_recipes(html, [])[0]

                self.assertIs(recipe["enabled"], False)
                self.assertIs(recipe["can_craft"], False)
                self.assertIs(recipe["disabled"], True)

    def test_partial_known_recipe_is_disabled_without_material_fallback(self):
        module = _load_parser_module()
        html = '''
        <div id="recipeGrid">
            <div class="recipe can-craft">
                <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                <span class="material-item">🧱砖块: 42/5</span>
                <input class="craft-input" max="8" id="craft-1">
                <button onclick="craft(1)">炼造</button>
            </div>
        </div>
        '''

        recipe = module.parse_recipes(html, [])[0]

        self.assertEqual({"砖块": 5}, recipe["ingredients"])
        self.assertIs(recipe["supported"], True)
        self.assertIs(recipe["disabled"], True)
        self.assertIs(recipe["enabled"], False)
        self.assertIs(recipe["can_craft"], False)

    def test_known_recipe_without_materials_does_not_use_compatibility_definition(self):
        module = _load_parser_module()
        html = '''
        <div id="recipeGrid">
            <div class="recipe can-craft">
                <div class="recipe-title">🪚 木工件 <span>(最多可制作 8)</span></div>
                <input class="craft-input" max="8" id="craft-1">
                <button onclick="craft(1)">炼造</button>
            </div>
        </div>
        '''

        recipe = module.parse_recipes(html, [])[0]

        self.assertEqual({}, recipe["ingredients"])
        self.assertIs(recipe["disabled"], True)
        self.assertIs(recipe["enabled"], False)
        self.assertIs(recipe["can_craft"], False)

    def test_unknown_recipe_is_never_craftable(self):
        module = _load_parser_module()
        html = '''
        <div id="recipeGrid">
            <div class="recipe can-craft">
                <div class="recipe-title">🧪 未知药剂 <span>(最多可制作 8)</span></div>
                <span class="material-item">🧱砖块: 42/1</span>
                <input class="craft-input" max="8" id="craft-99">
                <button onclick="craft(99)">炼造</button>
            </div>
        </div>
        '''

        recipe = module.parse_recipes(html, [])[0]

        self.assertEqual(99, recipe["craft_id"])
        self.assertIs(recipe["supported"], False)
        self.assertIs(recipe["disabled"], True)
        self.assertIs(recipe["enabled"], False)
        self.assertIs(recipe["can_craft"], False)

    def test_missing_recipe_cards_use_all_compatibility_definitions(self):
        module = _load_parser_module()

        recipes = {
            row["craft_id"]: row
            for row in module.parse_recipes('<div id="recipeGrid"></div>', [])
        }

        self.assertEqual({1, 2, 3, 4, 5, 6}, set(recipes))
        self.assertEqual(
            {"砖块": 5, "木材": 1, "塑料袋": 1},
            recipes[1]["ingredients"],
        )
        self.assertEqual(2, recipes[6]["ingredients"]["魔丸胚胎"])

    def test_component_parse_exception_disables_all_actions(self):
        html = FIXTURE.read_text(encoding="utf-8")
        for function_name in ("parse_inventory", "parse_recipes"):
            with self.subTest(function_name=function_name):
                module = _load_parser_module()
                with mock.patch.object(
                    module,
                    function_name,
                    side_effect=RuntimeError("parser exploded"),
                ):
                    data = module.parse_page(html, now_ts=1785100000)

                self.assertIs(data.get("parse_complete"), False)
                self.assertIn("parser exploded", data.get("parse_error") or "")
                self.assert_actions_disabled(data)

    def test_public_exports_only_include_parser_entry_points(self):
        module = _load_parser_module()

        self.assertEqual(
            {"parse_page", "parse_inventory", "parse_recipes"},
            set(module.__all__),
        )
        self.assertNotIn("safe_int", module.__all__)


if __name__ == "__main__":
    unittest.main()
