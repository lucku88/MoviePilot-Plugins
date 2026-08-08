import ast
import copy
import importlib.util
import socket
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from tests.test_vue_autocatchup import _install_moviepilot_stubs


REPO_ROOT = Path(__file__).resolve().parents[1]
VUEEMOJI_INIT = REPO_ROOT / "plugins.v2" / "vueemoji" / "__init__.py"


def _load_vueemoji():
    _install_moviepilot_stubs()
    requests_module = sys.modules["requests"]

    class RequestException(Exception):
        pass

    class Timeout(RequestException):
        pass

    class ConnectionError(RequestException):
        pass

    class ChunkedEncodingError(RequestException):
        pass

    requests_module.exceptions = types.SimpleNamespace(
        RequestException=RequestException,
        Timeout=Timeout,
        ConnectionError=ConnectionError,
        ChunkedEncodingError=ChunkedEncodingError,
    )

    module_name = "vueemoji_backend_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, VUEEMOJI_INIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _base_state():
    return {
        "user": {
            "magic": 1000,
            "total_points": 2000,
            "total_magic_earned": 3000,
        },
        "spin": {"used": 1, "limit": 10},
        "limits": {"max_spin_batch": 10, "max_open_bag_batch": 12},
        "bags": [
            {"tier": 1, "name": "新人表情包", "quantity": 5},
            {"tier": 2, "name": "实力表情包", "quantity": 2},
        ],
        "pending_open": {
            "bag_tier": 1,
            "bag_count": 1,
            "reroll_count": 0,
            "next_reroll_cost": 20,
            "result_items": [
                {"emoji": "😀", "points": 1, "magic": 2, "owned_count": 3},
            ],
        },
        "upgrade_rules": [
            {
                "key": "tier-1-to-2",
                "from": 1,
                "to": 2,
                "consume": 3,
                "produce": 1,
                "magic_cost": 30,
            },
        ],
        "effects": [{"key": "basic", "name": "简陋舞台效果", "unlocked": True}],
        "stage": {
            "selected_effect": "basic",
            "rows": [
                {
                    "row_index": 1,
                    "slot_count": 2,
                    "max_slots": 20,
                    "unlocked": True,
                    "slots": [],
                },
            ],
            "active_slots": [],
        },
    }


class VueEmojiBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = VUEEMOJI_INIT.read_text(encoding="utf-8")
        tree = ast.parse(cls.source)
        cls.class_node = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VueEmoji"
        )

    def setUp(self):
        self.module = _load_vueemoji()
        self.plugin = self.module.VueEmoji()
        self.plugin._http_retry_times = 5
        self.plugin._http_retry_delay = 0

    def test_vueemoji_class_has_no_duplicate_methods(self):
        method_names = [
            node.name
            for node in self.class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        duplicates = sorted(
            name for name in set(method_names) if method_names.count(name) > 1
        )

        self.assertEqual([], duplicates)

    def test_source_does_not_force_global_ipv4_resolution(self):
        self.assertNotIn("_force_ipv4", self.source)
        self.assertNotIn("lambda: socket.AF_INET", self.source)

    def test_legacy_force_ipv4_is_ignored_and_not_persisted(self):
        self.plugin._apply_config(
            {**self.plugin._default_config(), "force_ipv4": True}
        )
        captured = {}
        self.plugin.update_config = lambda payload: captured.update(payload)

        self.plugin._update_config()

        self.assertNotIn("force_ipv4", self.plugin._default_config())
        self.assertNotIn("force_ipv4", self.plugin._get_config())
        self.assertNotIn("force_ipv4", captured)

    def test_build_session_preserves_global_address_family_selector(self):
        connection_module = sys.modules["urllib3.util.connection"]
        sentinel = lambda: "system-default"
        connection_module.allowed_gai_family = sentinel
        self.plugin._apply_config(
            {**self.plugin._default_config(), "force_ipv4": True}
        )

        self.plugin._build_session()

        self.assertIs(sentinel, connection_module.allowed_gai_family)

    def test_hot_upgrade_restores_legacy_ipv4_selector_to_system_default(self):
        connection_module = sys.modules["urllib3.util.connection"]
        legacy_selector = eval(
            compile("lambda: socket.AF_INET", str(VUEEMOJI_INIT), "eval"),
            {"socket": socket},
        )
        connection_module.allowed_gai_family = legacy_selector
        connection_module.HAS_IPV6 = True

        self.plugin._restore_legacy_address_family_selector()

        self.assertIsNot(legacy_selector, connection_module.allowed_gai_family)
        self.assertEqual(socket.AF_UNSPEC, connection_module.allowed_gai_family())

    def test_hot_upgrade_preserves_same_shape_selector_from_other_plugin(self):
        connection_module = sys.modules["urllib3.util.connection"]
        foreign_source = REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py"
        foreign_selector = eval(
            compile("lambda: socket.AF_INET", str(foreign_source), "eval"),
            {"socket": socket},
        )
        connection_module.allowed_gai_family = foreign_selector

        self.plugin._restore_legacy_address_family_selector()

        self.assertIs(foreign_selector, connection_module.allowed_gai_family)

    def test_requests_adapter_does_not_repeat_manual_network_retries(self):
        retry_kwargs = {}
        mounted = []

        class RetryCapture:
            def __init__(self, **kwargs):
                retry_kwargs.update(kwargs)

        class AdapterCapture:
            def __init__(self, max_retries=None, **kwargs):
                self.max_retries = max_retries

        class SessionCapture:
            def __init__(self):
                self.headers = {}
                self.proxies = {}
                self.trust_env = False

            def mount(self, prefix, adapter):
                mounted.append((prefix, adapter))

        with (
            mock.patch.object(self.module, "Retry", RetryCapture),
            mock.patch.object(self.module, "HTTPAdapter", AdapterCapture),
            mock.patch.object(self.module.requests, "Session", SessionCapture),
        ):
            self.plugin._build_session()

        self.assertEqual(0, retry_kwargs["total"])
        self.assertEqual(0, retry_kwargs["connect"])
        self.assertEqual(0, retry_kwargs["read"])
        self.assertEqual(["http://", "https://"], [prefix for prefix, _ in mounted])

    def test_manual_network_retry_stops_after_five_total_attempts(self):
        calls = 0

        def fail():
            nonlocal calls
            calls += 1
            raise self.module.requests.exceptions.Timeout("timeout")

        with mock.patch.object(self.module.time, "sleep"):
            with self.assertRaises(self.module.requests.exceptions.Timeout):
                self.plugin._request_with_retry("test", fail)

        self.assertEqual(5, calls)

    def test_action_markers_recognize_every_irreversible_action(self):
        cases = []

        before = _base_state()
        after = copy.deepcopy(before)
        after["spin"]["used"] = 2
        cases.append(("spin_slot", {"count": 1}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["bags"][0]["quantity"] = 4
        cases.append(("open_bag", {"tier": 1, "count": 1}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["pending_open"] = {}
        cases.append(("accept_open", {}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["pending_open"]["reroll_count"] = 1
        after["pending_open"]["result_items"][0]["emoji"] = "😎"
        cases.append(("reroll_open", {}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["bags"][0]["quantity"] = 2
        after["bags"][1]["quantity"] = 3
        cases.append(("upgrade_bag", {"rule_key": "tier-1-to-2", "times": 1}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["stage"]["rows"][0]["slot_count"] = 3
        cases.append(("expand_stage_row", {"row_index": 1}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["stage"]["active_slots"] = [
            {"row_index": 1, "slot_index": 1, "emoji_code": "actor-1"},
        ]
        cases.append(("confirm_stage_cast", {"effect_key": "basic"}, before, after))

        before = copy.deepcopy(after)
        after = _base_state()
        cases.append(("recall_stage", {}, before, after))

        for action, payload, before_state, after_state in cases:
            with self.subTest(action=action):
                marker = self.plugin._capture_action_marker(before_state, action, payload)
                self.assertTrue(self.plugin._action_was_applied(marker, after_state))

    def test_timeout_confirmed_by_state_does_not_post_twice(self):
        before = _base_state()
        after = copy.deepcopy(before)
        after["spin"]["used"] = 2

        with (
            mock.patch.object(
                self.plugin,
                "_post_action",
                side_effect=self.module.requests.exceptions.Timeout("timeout"),
            ) as post_action,
            mock.patch.object(
                self.plugin,
                "_fetch_bundle_once",
                return_value={"state": after, "html": ""},
            ),
        ):
            result = self.plugin._post_action_confirmed(
                object(), "spin_slot", {"count": 1}, before
            )

        self.assertTrue(result["success"])
        self.assertTrue(result["confirmed_after_network_error"])
        self.assertEqual(1, post_action.call_count)

    def test_open_bag_confirmation_handles_removed_empty_tier(self):
        before = _base_state()
        after = copy.deepcopy(before)
        after["bags"] = [bag for bag in after["bags"] if bag["tier"] != 1]

        with (
            mock.patch.object(
                self.plugin,
                "_post_action",
                side_effect=self.module.requests.exceptions.Timeout("timeout"),
            ) as post_action,
            mock.patch.object(
                self.plugin,
                "_fetch_bundle_once",
                return_value={"state": after, "html": ""},
            ),
        ):
            result = self.plugin._post_action_confirmed(
                object(), "open_bag", {"tier": 1, "count": 5}, before
            )

        self.assertTrue(result["success"])
        self.assertEqual(1, post_action.call_count)

    def test_incompatible_state_change_is_ambiguous_and_never_reposted(self):
        cases = []

        before = _base_state()
        after = copy.deepcopy(before)
        after["spin"]["used"] = 0
        cases.append(("spin_slot", {"count": 1}, before, after))

        before = _base_state()
        after = copy.deepcopy(before)
        after["pending_open"]["result_items"][0]["emoji"] = "😎"
        cases.append(("accept_open", {}, before, after))

        for action, payload, before_state, after_state in cases:
            with self.subTest(action=action):
                original_error = self.module.requests.exceptions.Timeout("post timeout")
                with (
                    mock.patch.object(
                        self.plugin,
                        "_post_action",
                        side_effect=original_error,
                    ) as post_action,
                    mock.patch.object(
                        self.plugin,
                        "_fetch_bundle_once",
                        return_value={"state": after_state, "html": ""},
                    ),
                ):
                    with self.assertRaises(self.module.requests.exceptions.Timeout) as caught:
                        self.plugin._post_action_confirmed(
                            object(), action, payload, before_state
                        )

                self.assertIs(original_error, caught.exception)
                self.assertEqual(1, post_action.call_count)

    def test_unchanged_state_allows_at_most_five_post_attempts(self):
        before = _base_state()
        success = {"success": True, "data": before}

        with (
            mock.patch.object(
                self.plugin,
                "_post_action",
                side_effect=[
                    self.module.requests.exceptions.Timeout("timeout-1"),
                    self.module.requests.exceptions.Timeout("timeout-2"),
                    self.module.requests.exceptions.Timeout("timeout-3"),
                    self.module.requests.exceptions.Timeout("timeout-4"),
                    success,
                ],
            ) as post_action,
            mock.patch.object(
                self.plugin,
                "_fetch_bundle_once",
                return_value={"state": before, "html": ""},
            ),
            mock.patch.object(self.module.time, "sleep"),
        ):
            result = self.plugin._post_action_confirmed(
                object(), "open_bag", {"tier": 1, "count": 1}, before
            )

        self.assertTrue(result["success"])
        self.assertEqual(5, post_action.call_count)

    def test_failed_confirmation_read_never_reposts_ambiguous_action(self):
        before = _base_state()
        original_error = self.module.requests.exceptions.Timeout("post timeout")

        with (
            mock.patch.object(
                self.plugin,
                "_post_action",
                side_effect=original_error,
            ) as post_action,
            mock.patch.object(
                self.plugin,
                "_fetch_bundle_once",
                side_effect=self.module.requests.exceptions.ConnectionError("refresh failed"),
            ),
        ):
            with self.assertRaises(self.module.requests.exceptions.Timeout) as caught:
                self.plugin._post_action_confirmed(
                    object(), "recall_stage", {}, before
                )

        self.assertIs(original_error, caught.exception)
        self.assertEqual(1, post_action.call_count)

    def test_confirmed_recall_reconstructs_reward_from_state_delta(self):
        before = _base_state()
        before["stage"]["active_slots"] = [
            {"row_index": 1, "slot_index": 1, "emoji_code": "actor-1"},
        ]
        after = _base_state()
        after["user"]["magic"] = 1065
        after["user"]["total_points"] = 2455
        after["user"]["total_magic_earned"] = 3065

        result = self.plugin._confirmed_action_result(before, after, "recall_stage")

        self.assertEqual(455, result["result"]["point_gain"])
        self.assertEqual(65, result["result"]["magic_gain"])

    def test_extract_operation_logs_from_page_html(self):
        unrelated_logs = """
        <div class=\"log-list\">
          <div class=\"log-item\"><div><b>错误区域</b> <span class=\"muted\">2099-01-01 00:00:00</span></div><div>不能读取这里</div></div>
        </div>
        """
        actor_noise = '<button class="actor-card">😀</button>' * 5000
        html = unrelated_logs + actor_noise + """
        <section class=\"emoji-card\">
          <div data-scroll-key=\"user-log-list\" class=\"log-list\">
            <div class=\"log-item\"><div><b>确认演出</b> <span class=\"muted\">2026-08-08 06:00:14</span></div><div>确认演出：效果[知名舞台效果]，演员60名</div></div>
            <div class=\"log-item\"><div><b>召回结算</b> <span class=\"muted\">2026-08-08 06:00:13</span></div><div>召回60名演员，积分+2036 魔力+642</div></div>
          </div>
        </section>
        """

        logs = self.plugin._extract_operation_logs(html)

        self.assertEqual(
            [
                {
                    "title": "确认演出",
                    "time": "2026-08-08 06:00:14",
                    "detail": "确认演出：效果[知名舞台效果]，演员60名",
                },
                {
                    "title": "召回结算",
                    "time": "2026-08-08 06:00:13",
                    "detail": "召回60名演员，积分+2036 魔力+642",
                },
            ],
            logs,
        )

    def test_extract_operation_logs_requires_the_exact_web_log_container(self):
        html = """
        <div class=\"log-list\">
          <div class=\"log-item\"><div><b>伪日志</b> <span class=\"muted\">2026-08-08 06:00:14</span></div><div>页面其他区域</div></div>
        </div>
        """

        self.assertEqual([], self.plugin._extract_operation_logs(html))

    def test_manual_action_refreshes_web_logs_before_returning_status(self):
        before = _base_state()
        after_action = copy.deepcopy(before)
        after_action["spin"]["used"] = 2
        after_action["bags"][0]["quantity"] = 6
        fresh_logs = [
            {
                "title": "老虎机",
                "time": "2026-08-08 00:35:19",
                "detail": "老虎机：获得实力表情包x1",
            }
        ]
        def refresh_bundle_once(_session):
            self.plugin._operation_logs = fresh_logs
            return {"state": after_action}

        self.plugin._build_session = mock.Mock(return_value=object())
        self.plugin._operation_logs = []
        self.plugin._fetch_bundle = mock.Mock(return_value={"state": before})
        self.plugin._fetch_bundle_once = mock.Mock(side_effect=refresh_bundle_once)
        self.plugin._post_action_confirmed = mock.Mock(
            return_value={"success": True, "data": after_action}
        )
        self.plugin._schedule_next_run = mock.Mock()
        self.plugin._append_history = mock.Mock()

        result = self.plugin._manual_spin({"count": 1})

        self.assertEqual(1, self.plugin._fetch_bundle.call_count)
        self.plugin._fetch_bundle_once.assert_called_once()
        self.assertEqual(fresh_logs, result["emoji_status"]["operation_logs"])

    def test_ui_state_exposes_operation_logs_without_effect_animation_payload(self):
        self.plugin._operation_logs = [
            {"title": "老虎机", "time": "2026-08-08 00:35:19", "detail": "获得新人表情包x1"}
        ]
        state = _base_state()
        state["effects"] = [
            {"key": "famous", "name": "知名舞台效果", "unlocked": True}
        ]

        ui_state = self.plugin._build_ui_state(state, 123, [])

        self.assertEqual(self.plugin._operation_logs, ui_state["operation_logs"])
        self.assertNotIn("animation_class", ui_state["effects"][0])
        self.assertNotIn("preview_emojis", ui_state["effects"][0])
        self.assertNotIn("animation_class", ui_state["stage_rows"][0]["slots"][0])


if __name__ == "__main__":
    unittest.main()
