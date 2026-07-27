import copy
import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CRAFTING_PATH = REPO_ROOT / "plugins.v2" / "vuepill" / "crafting.py"
PARSER_PATH = REPO_ROOT / "plugins.v2" / "vuepill" / "page_parser.py"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "vuepill_page.html"


def _load_module(module_name, path):
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_crafting_module():
    return _load_module("vuepill_crafting_under_test", CRAFTING_PATH)


def _parse_fixture():
    parser = _load_module("vuepill_page_parser_for_crafting_test", PARSER_PATH)
    return parser.parse_page(
        FIXTURE_PATH.read_text(encoding="utf-8"),
        now_ts=1785100000,
    )


def _dynamic_recipes():
    ids = {
        "木工件": 410,
        "塑料件": 275,
        "简易工具": 903,
        "能量碎片": 118,
        "魔丸胚胎": 664,
        "魔丸": 52,
    }
    recipes = []
    for recipe in reversed(_parse_fixture()["recipes"]):
        copied = copy.deepcopy(recipe)
        copied["craft_id"] = ids[copied["output_item"]]
        recipes.append(copied)
    return recipes, ids


def _base_inventory(pill_count=1):
    return {
        "砖块": 50 * pill_count,
        "木材": 4 * pill_count,
        "塑料袋": 8 * pill_count,
        "瓶子": 4 * pill_count,
        "螺丝": 4 * pill_count,
        "旧电池": 2 * pill_count,
        "破铜片": 2 * pill_count,
        "木工件": 0,
        "塑料件": 0,
        "简易工具": 0,
        "能量碎片": 0,
        "魔丸胚胎": 0,
        "魔丸": 0,
    }


def _full_plan(ids, pill_count=1):
    return {
        ids["木工件"]: 4 * pill_count,
        ids["塑料件"]: 4 * pill_count,
        ids["简易工具"]: 2 * pill_count,
        ids["能量碎片"]: 2 * pill_count,
        ids["魔丸胚胎"]: 2 * pill_count,
        ids["魔丸"]: pill_count,
    }


class VuePillCraftingTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CRAFTING_PATH.exists(), "crafting.py 尚未创建")
        self.module = _load_crafting_module()
        self.recipes, self.ids = _dynamic_recipes()

    def test_public_exports_only_include_four_calculation_functions(self):
        self.assertEqual(
            {
                "inventory_to_map",
                "compute_magic_pill_plan",
                "exchange_batches",
                "max_gift_quantity",
            },
            set(self.module.__all__),
        )

    def test_inventory_to_map_sums_duplicates_and_applies_magic_pill_reserve(self):
        items = [
            {"name": "木材", "count": "3"},
            {"name": "木材", "count": 4},
            {"name": "魔丸", "count": "12"},
            {"name": "魔丸", "count": 3},
            {"name": "破铜片", "count": -2},
            {"name": "螺丝", "count": "not-a-number"},
            {"name": "旧电池", "count": 1.5},
            {"name": "", "count": 99},
            "不是物品字典",
        ]
        original = copy.deepcopy(items)

        result = self.module.inventory_to_map(
            items,
            reserve_magic_pill_count="10",
        )

        self.assertEqual(
            {
                "木材": 7,
                "魔丸": 5,
                "破铜片": 0,
                "螺丝": 0,
                "旧电池": 0,
            },
            result,
        )
        self.assertEqual(original, items)

    def test_inventory_to_map_invalid_inputs_fail_closed(self):
        self.assertEqual({}, self.module.inventory_to_map(None))
        self.assertEqual({}, self.module.inventory_to_map("not-items"))
        self.assertEqual(
            {"魔丸": 2},
            self.module.inventory_to_map(
                [{"name": "魔丸", "count": 2}],
                reserve_magic_pill_count=-10,
            ),
        )

    def test_dynamic_recipe_ids_follow_real_fixture_math_and_dependency_order(self):
        inventory = _base_inventory(1)
        original_inventory = copy.deepcopy(inventory)
        original_recipes = copy.deepcopy(self.recipes)

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=1,
        )

        self.assertEqual(1, result["max_count"])
        self.assertEqual(_full_plan(self.ids, 1), result["plan"])
        self.assertEqual(
            [
                self.ids["木工件"],
                self.ids["简易工具"],
                self.ids["塑料件"],
                self.ids["能量碎片"],
                self.ids["魔丸胚胎"],
                self.ids["魔丸"],
            ],
            [step["craft_id"] for step in result["steps"]],
        )
        self.assertEqual({}, result["missing"])
        self.assertEqual("", result["reason"])
        self.assertEqual(original_inventory, inventory)
        self.assertEqual(original_recipes, self.recipes)

    def test_shared_intermediate_steps_are_topologically_sorted(self):
        recipes = [
            {
                "craft_id": 50,
                "output_item": "魔丸",
                "ingredients": {"分支甲": 1, "分支乙": 1},
            },
            {
                "craft_id": 20,
                "output_item": "分支乙",
                "ingredients": {"共享件": 1},
            },
            {
                "craft_id": 40,
                "output_item": "深层件",
                "ingredients": {"基础材料": 1},
            },
            {
                "craft_id": 10,
                "output_item": "分支甲",
                "ingredients": {"共享件": 1},
            },
            {
                "craft_id": 30,
                "output_item": "共享件",
                "ingredients": {"深层件": 1},
            },
        ]
        inventory = {"深层件": 1, "基础材料": 1}
        original_inventory = copy.deepcopy(inventory)
        original_recipes = copy.deepcopy(recipes)

        result = self.module.compute_magic_pill_plan(
            inventory,
            recipes,
            target=1,
        )

        expected_order = [40, 30, 10, 20, 50]
        step_ids = [step["craft_id"] for step in result["steps"]]
        self.assertEqual(expected_order, step_ids)
        self.assertEqual(expected_order, list(result["plan"]))
        self.assertEqual({30: 2, 10: 1, 40: 1, 20: 1, 50: 1}, result["plan"])

        recipes_by_output = {recipe["output_item"]: recipe for recipe in recipes}
        positions = {craft_id: index for index, craft_id in enumerate(step_ids)}
        for recipe in recipes:
            craft_id = recipe["craft_id"]
            if craft_id not in result["plan"]:
                continue
            for ingredient_name in recipe["ingredients"]:
                dependency = recipes_by_output.get(ingredient_name)
                if dependency and dependency["craft_id"] in result["plan"]:
                    self.assertLess(
                        positions[dependency["craft_id"]],
                        positions[craft_id],
                    )

        self.assertEqual(original_inventory, inventory)
        self.assertEqual(original_recipes, recipes)

    def test_recipe_iterables_are_supported(self):
        recipe_iterator = (recipe for recipe in copy.deepcopy(self.recipes))

        result = self.module.compute_magic_pill_plan(
            _base_inventory(1),
            recipe_iterator,
            target=1,
        )

        self.assertEqual(1, result["max_count"])
        self.assertEqual(_full_plan(self.ids, 1), result["plan"])

    def test_existing_lower_intermediates_reduce_prerequisite_steps(self):
        inventory = _base_inventory(1)
        inventory["木工件"] = 2
        inventory["塑料件"] = 2

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=1,
        )

        self.assertEqual(
            {
                self.ids["木工件"]: 2,
                self.ids["塑料件"]: 2,
                self.ids["简易工具"]: 2,
                self.ids["能量碎片"]: 2,
                self.ids["魔丸胚胎"]: 2,
                self.ids["魔丸"]: 1,
            },
            result["plan"],
        )

    def test_existing_upper_intermediates_are_consumed_before_crafting(self):
        inventory = _base_inventory(1)
        inventory["魔丸胚胎"] = 1
        inventory["简易工具"] = 1
        inventory["能量碎片"] = 1

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=1,
        )

        self.assertEqual(
            {
                self.ids["魔丸胚胎"]: 1,
                self.ids["魔丸"]: 1,
            },
            result["plan"],
        )

    def test_existing_magic_pills_do_not_reduce_requested_new_target(self):
        inventory = _base_inventory(1)
        inventory["魔丸"] = 500

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=2,
        )

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertTrue(result["missing"])

    def test_target_none_computes_maximum_new_magic_pills(self):
        inventory = _base_inventory(3)
        inventory["魔丸"] = 999

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=None,
        )

        self.assertEqual(3, result["max_count"])
        self.assertEqual(_full_plan(self.ids, 3), result["plan"])

    def test_non_positive_target_returns_empty_plan(self):
        for target in (0, -1):
            with self.subTest(target=target):
                result = self.module.compute_magic_pill_plan(
                    _base_inventory(1),
                    self.recipes,
                    target=target,
                )

                self.assertEqual(0, result["max_count"])
                self.assertEqual({}, result["plan"])
                self.assertEqual([], result["steps"])
                self.assertEqual({}, result["missing"])

    def test_invalid_target_numbers_fail_closed(self):
        for target in (True, 1.5, "not-a-number"):
            with self.subTest(target=target):
                result = self.module.compute_magic_pill_plan(
                    _base_inventory(1),
                    self.recipes,
                    target=target,
                )

                self.assertEqual(0, result["max_count"])
                self.assertEqual({}, result["plan"])
                self.assertTrue(result["reason"])

    def test_insufficient_materials_fail_closed_without_mutating_inputs(self):
        inventory = _base_inventory(1)
        inventory["砖块"] = "invalid"
        original_inventory = copy.deepcopy(inventory)
        original_recipes = copy.deepcopy(self.recipes)

        result = self.module.compute_magic_pill_plan(
            inventory,
            self.recipes,
            target=1,
        )

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertGreater(result["missing"].get("砖块", 0), 0)
        self.assertTrue(result["reason"])
        self.assertEqual(original_inventory, inventory)
        self.assertEqual(original_recipes, self.recipes)

    def test_missing_dependency_recipe_fails_closed(self):
        recipes = [
            recipe
            for recipe in self.recipes
            if recipe["output_item"] != "魔丸胚胎"
        ]

        result = self.module.compute_magic_pill_plan(
            _base_inventory(1),
            recipes,
            target=1,
        )

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertEqual(2, result["missing"].get("魔丸胚胎"))
        self.assertTrue(result["reason"])

    def test_circular_dependencies_fail_closed(self):
        recipes = [
            {
                "craft_id": 81,
                "output_item": "魔丸",
                "ingredients": {"魔丸胚胎": 1},
            },
            {
                "craft_id": 82,
                "output_item": "魔丸胚胎",
                "ingredients": {"魔丸": 1},
            },
        ]

        result = self.module.compute_magic_pill_plan({}, recipes, target=1)

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertIn("循环", result["reason"])

    def test_duplicate_output_items_fail_closed(self):
        recipes = copy.deepcopy(self.recipes)
        duplicate = copy.deepcopy(recipes[0])
        duplicate["craft_id"] = 9999
        recipes.append(duplicate)

        result = self.module.compute_magic_pill_plan(
            _base_inventory(1),
            recipes,
            target=1,
        )

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertIn("重复产物", result["reason"])

    def test_duplicate_craft_ids_fail_closed(self):
        recipes = copy.deepcopy(self.recipes)
        recipes[0]["craft_id"] = recipes[1]["craft_id"]

        result = self.module.compute_magic_pill_plan(
            _base_inventory(1),
            recipes,
            target=1,
        )

        self.assertEqual(0, result["max_count"])
        self.assertEqual({}, result["plan"])
        self.assertIn("重复配方", result["reason"])

    def test_invalid_ingredient_quantities_fail_closed(self):
        for invalid_quantity in (0, -1, True, 1.5, "2", None):
            with self.subTest(invalid_quantity=invalid_quantity):
                recipes = copy.deepcopy(self.recipes)
                magic_recipe = next(
                    recipe
                    for recipe in recipes
                    if recipe["output_item"] == "魔丸"
                )
                magic_recipe["ingredients"]["砖块"] = invalid_quantity

                result = self.module.compute_magic_pill_plan(
                    _base_inventory(1),
                    recipes,
                    target=1,
                )

                self.assertEqual(0, result["max_count"])
                self.assertEqual({}, result["plan"])
                self.assertIn("材料数量", result["reason"])

    def test_exchange_batches_honors_reserve_and_request_limit(self):
        batches = self.module.exchange_batches(
            current=257,
            reserve=10,
            max_per_request=100,
        )

        self.assertEqual([100, 100, 47], batches)
        self.assertEqual(247, sum(batches))
        self.assertEqual(10, 257 - sum(batches))
        self.assertTrue(all(0 < batch <= 100 for batch in batches))
        self.assertEqual([], self.module.exchange_batches(10, 10, 100))
        self.assertEqual([], self.module.exchange_batches(9, 10, 100))

    def test_exchange_batches_invalid_values_fail_closed(self):
        invalid_cases = (
            (-1, 0, 100),
            (10, -1, 100),
            (10, 0, 0),
            (10, 0, -1),
            ("invalid", 0, 100),
            (10, 0, 1.5),
            (True, 0, 100),
        )
        for current, reserve, maximum in invalid_cases:
            with self.subTest(
                current=current,
                reserve=reserve,
                maximum=maximum,
            ):
                self.assertEqual(
                    [],
                    self.module.exchange_batches(current, reserve, maximum),
                )

    def test_max_gift_quantity_caps_stock_and_handles_missing_items(self):
        inventory = {"木材": 700, "螺丝": 40}

        self.assertEqual(
            500,
            self.module.max_gift_quantity(inventory, "木材"),
        )
        self.assertEqual(
            100,
            self.module.max_gift_quantity(inventory, "木材", cap=100),
        )
        self.assertEqual(
            40,
            self.module.max_gift_quantity(inventory, "螺丝"),
        )
        self.assertEqual(
            0,
            self.module.max_gift_quantity(inventory, "不存在"),
        )

    def test_max_gift_quantity_invalid_values_fail_closed(self):
        self.assertEqual(
            0,
            self.module.max_gift_quantity({"木材": -1}, "木材"),
        )
        self.assertEqual(
            0,
            self.module.max_gift_quantity({"木材": "invalid"}, "木材"),
        )
        self.assertEqual(
            0,
            self.module.max_gift_quantity({"木材": 10}, "木材", cap=-1),
        )
        self.assertEqual(
            0,
            self.module.max_gift_quantity({"木材": 10}, "木材", cap="invalid"),
        )
        self.assertEqual(
            0,
            self.module.max_gift_quantity(None, "木材"),
        )


if __name__ == "__main__":
    unittest.main()
