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
