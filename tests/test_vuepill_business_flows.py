import unittest

from tests.test_vuepill_lifecycle import _load_plugin_module, make_plugin


class VuePillBusinessFlowTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_plugin_module()
        self.plugin = make_plugin(self.module)
        self.plugin._reserve_magic_pill_count = 10
        self.recipes = [
            {
                "craft_id": 1,
                "output_item": "木工件",
                "ingredients": {"砖块": 5, "木材": 1, "塑料袋": 1},
            },
            {
                "craft_id": 2,
                "output_item": "塑料件",
                "ingredients": {"砖块": 5, "塑料袋": 1, "瓶子": 1},
            },
            {
                "craft_id": 3,
                "output_item": "简易工具",
                "ingredients": {"螺丝": 2, "木工件": 2},
            },
            {
                "craft_id": 4,
                "output_item": "能量碎片",
                "ingredients": {"旧电池": 1, "塑料件": 2},
            },
            {
                "craft_id": 5,
                "output_item": "魔丸胚胎",
                "ingredients": {"破铜片": 1, "简易工具": 1, "能量碎片": 1},
            },
            {
                "craft_id": 6,
                "output_item": "魔丸",
                "ingredients": {"砖块": 10, "魔丸胚胎": 2},
            },
        ]

    @staticmethod
    def _base_stock():
        return {
            "砖块": 50,
            "木材": 4,
            "塑料袋": 8,
            "瓶子": 4,
            "螺丝": 4,
            "旧电池": 2,
            "破铜片": 2,
            "木工件": 0,
            "塑料件": 0,
            "简易工具": 0,
            "能量碎片": 0,
            "魔丸胚胎": 0,
            "魔丸": 0,
        }

    def _page(self, stock):
        pills = stock.get("魔丸", 0)
        return {
            "title": "搬砖捡破烂炼魔丸",
            "server_now": 1785100000,
            "stats": {"magic_pills": pills},
            "brick": {"ready": False},
            "beach": {"ready": False},
            "exchange": {
                "enabled": pills > 0,
                "max_count": pills,
                "magic_pills": pills,
            },
            "inventory": [
                {"name": name, "count": count, "giftable": name != "魔丸"}
                for name, count in stock.items()
            ],
            "recipes": [dict(recipe) for recipe in self.recipes],
        }

    def _apply_craft(self, stock, recipe_id, quantity):
        recipe = next(row for row in self.recipes if row["craft_id"] == recipe_id)
        for item_name, required in recipe["ingredients"].items():
            stock[item_name] -= required * quantity
        stock[recipe["output_item"]] += quantity

    def test_auto_craft_refreshes_and_replans_after_every_success(self):
        stock = self._base_stock()
        action_calls = []
        fetch_calls = []

        def post_action(session, action, payload=None, retry_network=False):
            self.assertEqual("craft_item", action)
            self.assertFalse(retry_network)
            action_calls.append((payload["recipe_id"], payload["quantity"]))
            self._apply_craft(stock, payload["recipe_id"], payload["quantity"])
            return {"success": True}

        self.plugin._post_action = post_action
        self.plugin._fetch_page_state = lambda session: fetch_calls.append(
            True
        ) or self._page(stock)

        result = self.plugin._auto_craft_magic_pill(object(), self._page(stock))

        self.assertEqual(
            {1: 4, 2: 4, 3: 2, 4: 2, 5: 2, 6: 1},
            dict(action_calls),
        )
        self.assertEqual(6, len(action_calls))
        self.assertEqual(6, len(fetch_calls))
        self.assertEqual(1, result["crafted"])
        self.assertEqual(1, stock["魔丸"])

    def test_auto_craft_keeps_completed_steps_and_stops_on_partial_failure(self):
        stock = self._base_stock()
        action_calls = []
        fetch_calls = []

        def post_action(session, action, payload=None, retry_network=False):
            action_calls.append((payload["recipe_id"], payload["quantity"]))
            if len(action_calls) == 3:
                raise RuntimeError("第三步失败")
            self._apply_craft(stock, payload["recipe_id"], payload["quantity"])
            return {"success": True}

        self.plugin._post_action = post_action
        self.plugin._fetch_page_state = lambda session: fetch_calls.append(
            True
        ) or self._page(stock)

        result = self.plugin._auto_craft_magic_pill(object(), self._page(stock))

        self.assertEqual(3, len(action_calls))
        self.assertEqual(2, len(fetch_calls))
        self.assertEqual(2, len(result["craft_steps"]))
        self.assertTrue(any("已完成" in line for line in result["lines"]))
        self.assertIn("第三步失败", result["warning"])

    def test_auto_exchange_rechecks_inventory_between_safe_batches(self):
        stock = {"魔丸": 257}
        action_calls = []
        fetch_calls = []

        def post_action(session, action, payload=None, retry_network=False):
            self.assertEqual("exchange_points", action)
            self.assertFalse(retry_network)
            quantity = payload["quantity"]
            action_calls.append(quantity)
            stock["魔丸"] -= quantity
            return {"success": True, "points_gained": quantity * 2}

        self.plugin._post_action = post_action
        self.plugin._fetch_page_state = lambda session: fetch_calls.append(
            True
        ) or self._page(stock)

        result = self.plugin._auto_exchange_points(object(), self._page(stock))

        self.assertEqual([100, 100, 47], action_calls)
        self.assertEqual(3, len(fetch_calls))
        self.assertEqual(247, result["exchanged"])
        self.assertEqual(10, stock["魔丸"])

    def test_gift_success_appends_one_history_entry_after_single_post(self):
        stock = {"木材": 5, "魔丸": 10}
        pages = [self._page(stock), self._page(stock)]
        action_calls = []
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: pages.pop(0)
        self.plugin._post_action = lambda *args, **kwargs: action_calls.append(
            (args, kwargs)
        ) or {"success": True, "message": "赠送成功"}
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "target_uid": "12345", "quantity": 2}
        )

        self.assertTrue(result["success"])
        self.assertEqual(1, len(action_calls))
        self.assertFalse(action_calls[0][1]["retry_network"])
        history = self.plugin.get_data("history") or []
        self.assertEqual(1, len(history))
        self.assertEqual("🎁赠送：木材×2 / 目标 UID 12345", history[0]["title"])


if __name__ == "__main__":
    unittest.main()
