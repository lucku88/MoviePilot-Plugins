import threading
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

    def test_manual_craft_api_reports_failure_after_completed_intermediate_steps(self):
        stock = self._base_stock()
        action_calls = []
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: self._page(stock)
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}

        def post_action(session, action, payload=None, retry_network=False):
            action_calls.append((payload["recipe_id"], payload["quantity"]))
            if len(action_calls) == 3:
                raise RuntimeError("第三步失败")
            self._apply_craft(stock, payload["recipe_id"], payload["quantity"])
            return {"success": True}

        self.plugin._post_action = post_action

        result = self.plugin._craft_max_pill_api({"quantity": 1})

        self.assertFalse(result["success"])
        self.assertEqual(0, stock["魔丸"])
        self.assertEqual(3, len(action_calls))
        self.assertIn("第三步失败", result.get("warning", ""))
        self.assertTrue(any("步骤" in line for line in result.get("lines", [])))
        history = self.plugin.get_data("history") or []
        self.assertEqual(1, len(history))
        self.assertTrue(history[0]["title"].startswith(("⚠️", "❌")))

    def test_run_job_reports_auto_craft_failure_and_skips_exchange(self):
        stock = self._base_stock()
        action_calls = []
        notifications = []
        self.plugin._enabled = True
        self.plugin._enable_brick = False
        self.plugin._enable_beach = True
        self.plugin._auto_craft = True
        self.plugin._auto_exchange = True
        self.plugin._notify = True
        self.plugin._random_delay_max_seconds = 0
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        fetch_calls = []

        def fetch_page(session):
            page = self._page(stock)
            if not fetch_calls:
                page["beach"]["ready"] = True
            fetch_calls.append(True)
            return page

        self.plugin._fetch_page_state = fetch_page
        self.plugin._fetch_stable_page_state = lambda *args, **kwargs: self._page(
            stock
        )
        self.plugin._run_beach_flow = lambda session: {
            "done": True,
            "items": [{"name": "木材", "count": 1, "icon": "🪵"}],
        }

        def post_action(session, action, payload=None, retry_network=False):
            action_calls.append(action)
            if action == "exchange_points":
                return {"success": True, "points_gained": 1}
            if action_calls.count("craft_item") == 3:
                raise RuntimeError("第三步失败")
            self._apply_craft(stock, payload["recipe_id"], payload["quantity"])
            return {"success": True}

        self.plugin._post_action = post_action
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        self.plugin.post_message = lambda *args, **kwargs: notifications.append(kwargs)

        result = self.plugin.run_job(force=True, reason="manual-api")

        self.assertFalse(result["success"])
        self.assertEqual(0, stock["魔丸"])
        self.assertNotIn("exchange_points", action_calls)
        self.assertIn("第三步失败", result.get("warning", ""))
        self.assertTrue(any("已完成" in line for line in result.get("lines", [])))
        history = self.plugin.get_data("history") or []
        self.assertEqual(1, len(history))
        self.assertTrue(history[0]["title"].startswith(("⚠️", "❌")))
        self.assertEqual(1, len(notifications))
        self.assertIn("⚠️", notifications[0]["title"])
        self.assertIn("第三步失败", notifications[0]["text"])

    def test_manual_craft_api_reports_confirmed_partial_magic_pills(self):
        stock = {
            name: count * 2 if name not in {"魔丸", "木工件", "塑料件", "简易工具", "能量碎片", "魔丸胚胎"} else count
            for name, count in self._base_stock().items()
        }
        final_attempts = []
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: self._page(stock)
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}

        def post_action(session, action, payload=None, retry_network=False):
            recipe_id = payload["recipe_id"]
            quantity = payload["quantity"]
            if recipe_id == 6:
                final_attempts.append(quantity)
                if len(final_attempts) == 1:
                    self._apply_craft(stock, recipe_id, 1)
                    return {"success": True}
                raise RuntimeError("剩余魔丸炼造失败")
            self._apply_craft(stock, recipe_id, quantity)
            return {"success": True}

        self.plugin._post_action = post_action

        result = self.plugin._craft_max_pill_api({"quantity": 2})

        self.assertFalse(result["success"])
        self.assertEqual(1, result.get("crafted"))
        self.assertEqual(2, result.get("target"))
        self.assertEqual(1, stock["魔丸"])
        self.assertIn("部分完成", result["message"])
        self.assertIn("1/2", result["message"])
        self.assertIn("剩余魔丸炼造失败", result.get("warning", ""))
        history = self.plugin.get_data("history") or []
        self.assertEqual(1, len(history))
        self.assertTrue(history[0]["title"].startswith("⚠️"))

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

    def test_concurrent_manual_exchange_allows_one_post_and_keeps_reserve(self):
        stock = {"魔丸": 15}
        post_calls = []
        post_started = threading.Event()
        allow_first_post = threading.Event()
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: self._page(stock)
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        self.plugin._append_history = lambda *args, **kwargs: None

        def post_action(session, action, payload=None, retry_network=False):
            post_calls.append(payload["quantity"])
            if len(post_calls) == 1:
                post_started.set()
                self.assertTrue(allow_first_post.wait(2))
            stock["魔丸"] -= payload["quantity"]
            return {"success": True, "points_gained": payload["quantity"]}

        self.plugin._post_action = post_action
        results = []

        def exchange():
            results.append(self.plugin._exchange_points_api({"quantity": 5}))

        first = threading.Thread(target=exchange)
        second = threading.Thread(target=exchange)
        first.start()
        self.assertTrue(post_started.wait(1))
        second.start()
        second.join(1)
        allow_first_post.set()
        first.join(2)
        second.join(2)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual([5], post_calls)
        self.assertEqual(10, stock["魔丸"])
        self.assertEqual(1, sum(result["success"] is True for result in results))
        busy = next(result for result in results if result["success"] is False)
        self.assertTrue(
            "正在执行" in busy["message"] or "稍后重试" in busy["message"]
        )

    def test_manual_beach_collects_pending_trash_without_reentering(self):
        pending_page = self._page({"木材": 0, "魔丸": 10})
        pending_page["beach"].update(
            {
                "ready": False,
                "can_collect": True,
                "has_trash": True,
                "collect_enabled": True,
                "status_text": "沙滩有垃圾待收集",
            }
        )
        final_page = self._page({"木材": 1, "魔丸": 10})
        action_calls = []
        self.plugin._auto_craft = False
        self.plugin._auto_exchange = False
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: pending_page
        self.plugin._fetch_stable_page_state = lambda *args, **kwargs: final_page

        def post_action(session, action, payload=None, retry_network=False):
            action_calls.append(action)
            return {
                "success": True,
                "collected_items": {"木材": 1},
            }

        self.plugin._post_action = post_action
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        self.plugin._append_history = lambda *args, **kwargs: None

        result = self.plugin._manual_clean_beach()

        self.assertEqual(["collect_all_trash"], action_calls)
        self.assertTrue(any("沙滩" in line for line in result["lines"]))

    def test_manual_beach_failure_keeps_short_retry_when_refresh_misses_trash(self):
        pending_page = self._page({"木材": 0, "魔丸": 10})
        pending_page["beach"].update(
            {
                "ready": False,
                "can_collect": True,
                "has_trash": True,
                "collect_enabled": True,
                "status_text": "沙滩有垃圾待收集",
            }
        )
        future_run = int(self.module.time.time()) + 7200
        final_page = self._page({"木材": 0, "魔丸": 10})
        final_page["beach"].update(
            {
                "ready": False,
                "can_collect": False,
                "has_trash": False,
                "collect_enabled": False,
                "next_ready_ts": future_run,
                "status_text": "沙滩冷却中",
            }
        )
        action_calls = []
        self.plugin._auto_craft = False
        self.plugin._auto_exchange = False
        self.plugin._ready_retry_seconds = 60
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: pending_page
        self.plugin._fetch_stable_page_state = lambda *args, **kwargs: final_page

        def post_action(session, action, payload=None, retry_network=False):
            action_calls.append(action)
            raise RuntimeError("收集失败")

        self.plugin._post_action = post_action
        self.plugin._compute_next_plan = lambda page: (future_run, "beach")
        self.plugin._reregister_plugin = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        self.plugin._append_history = lambda *args, **kwargs: None

        self.plugin._manual_clean_beach()
        next_run = self.plugin._load_saved_next_run()

        self.assertEqual(["collect_all_trash"], action_calls)
        self.assertIsNotNone(next_run)
        self.assertLessEqual(
            next_run.timestamp(),
            self.module.time.time() + self.plugin._ready_retry_seconds + 5,
        )

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

    def test_concurrent_duplicate_gift_allows_only_one_post(self):
        stock = {"木材": 5, "魔丸": 10}
        post_calls = []
        post_started = threading.Event()
        allow_first_post = threading.Event()
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: self._page(stock)
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        self.plugin._append_history = lambda *args, **kwargs: None

        def post_action(session, action, payload=None, retry_network=False):
            post_calls.append((action, dict(payload or {})))
            if len(post_calls) == 1:
                post_started.set()
                self.assertTrue(allow_first_post.wait(2))
            return {"success": True, "message": "赠送成功"}

        self.plugin._post_action = post_action
        results = []
        payload = {"item_name": "木材", "target_uid": "12345", "quantity": 2}

        def gift():
            results.append(self.plugin._gift_item_api(payload))

        first = threading.Thread(target=gift)
        second = threading.Thread(target=gift)
        first.start()
        self.assertTrue(post_started.wait(1))
        second.start()
        second.join(1)
        allow_first_post.set()
        first.join(2)
        second.join(2)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(1, len(post_calls))
        self.assertEqual(1, sum(result["success"] is True for result in results))
        busy = next(result for result in results if result["success"] is False)
        self.assertTrue(
            "正在执行" in busy["message"] or "稍后重试" in busy["message"]
        )


if __name__ == "__main__":
    unittest.main()
