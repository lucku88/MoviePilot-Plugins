import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "vuepill_page.html"
PARSER_PATH = REPO_ROOT / "plugins.v2" / "vuepill" / "page_parser.py"


def _load_parse_page():
    module_name = "vuepill_page_parser_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, PARSER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载页面解析模块: {PARSER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.parse_page


class VuePillParserTests(unittest.TestCase):
    def parse_fixture(self):
        self.assertTrue(PARSER_PATH.exists(), "page_parser.py 尚未创建")
        parse_page = _load_parse_page()
        return parse_page(FIXTURE.read_text(encoding="utf-8"), now_ts=1785100000)

    def test_parse_page_reads_stats_inventory_and_giftable_items(self):
        data = self.parse_fixture()

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

    def test_disabled_beach_with_countdown_is_not_ready(self):
        data = self.parse_fixture()

        self.assertIs(data["beach"]["ready"], False)
        self.assertIs(data["beach"]["collect_enabled"], False)
        self.assertLessEqual(data["beach"]["next_ready_ts"], 1785100000)

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


if __name__ == "__main__":
    unittest.main()
