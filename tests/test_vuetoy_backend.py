import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from tests.test_vue_autocatchup import _install_moviepilot_stubs


REPO_ROOT = Path(__file__).resolve().parents[1]
VUETOY_INIT = REPO_ROOT / "plugins.v2" / "vuetoy" / "__init__.py"


def _load_vuetoy():
    _install_moviepilot_stubs()
    module_name = "vuetoy_backend_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, VUETOY_INIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _toy_state(personal_remaining=7200, available=1):
    return {
        "user": {"magic": 1000},
        "profile": {"exposure": 2000, "earned_magic": 3000},
        "personal_slots": [
            {
                "owner_id": 10,
                "slot_index": 1,
                "occupant": {
                    "viewer_is_occupant": True,
                    "doll_name": "阿鲁卡多",
                    "time_until_collect": personal_remaining,
                },
            }
        ],
        "remote_deployments": [],
        "doll_inventory": [
            {
                "doll_key": "alucard",
                "name": "阿鲁卡多",
                "available": available,
                "quantity": max(available, 1),
                "display_seconds": 3600,
            }
        ],
    }


class VueToyBackendTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_vuetoy()
        self.plugin = self.module.VueToy()
        self.plugin._enabled = True
        self.plugin._notify = False
        self.plugin._auto_collect = True
        self.plugin._auto_place = True
        self.plugin._random_delay_max_seconds = 0

    def test_stale_status_api_forwards_to_current_running_instance(self):
        stale_plugin = self.plugin
        current_plugin = self.module.VueToy()

        def stale_status():
            return {"source": "stale"}

        def current_status():
            return {"source": "current"}

        stale_status.__name__ = "_get_status"
        current_status.__name__ = "_get_status"
        stale_plugin._get_status = stale_status
        current_plugin._get_status = current_status

        plugin_module = types.ModuleType("app.core.plugin")
        manager = types.SimpleNamespace(running_plugins={"VueToy": current_plugin})
        plugin_module.PluginManager = lambda: manager

        endpoint = next(route["endpoint"] for route in stale_plugin.get_api() if route["path"] == "/status")
        with mock.patch.dict(sys.modules, {"app.core.plugin": plugin_module}, clear=False):
            result = endpoint()

        self.assertEqual("current", result["source"])

    def test_stale_config_api_forwards_payload_to_current_running_instance(self):
        stale_plugin = self.plugin
        current_plugin = self.module.VueToy()

        def stale_save(payload):
            return {"source": "stale", "payload": payload}

        def current_save(payload):
            return {"source": "current", "payload": payload}

        stale_save.__name__ = "_save_config"
        current_save.__name__ = "_save_config"
        stale_plugin._save_config = stale_save
        current_plugin._save_config = current_save

        plugin_module = types.ModuleType("app.core.plugin")
        manager = types.SimpleNamespace(running_plugins={"VueToy": current_plugin})
        plugin_module.PluginManager = lambda: manager

        endpoint = next(
            route["endpoint"]
            for route in stale_plugin.get_api()
            if route["path"] == "/config" and "POST" in route["methods"]
        )
        payload = {"enabled": True, "self_slot_guard_hours": 2}
        with mock.patch.dict(sys.modules, {"app.core.plugin": plugin_module}, clear=False):
            result = endpoint(payload)

        self.assertEqual("current", result["source"])
        self.assertEqual(payload, result["payload"])

    def test_remote_placement_pauses_inside_default_one_hour_guard(self):
        state = _toy_state(personal_remaining=3599, available=1)

        self.assertTrue(self.plugin._should_pause_remote_placement(state))

    def test_remote_placement_does_not_pause_before_guard_window(self):
        state = _toy_state(personal_remaining=3601, available=1)

        self.assertFalse(self.plugin._should_pause_remote_placement(state))

    def test_remote_placement_does_not_pause_without_available_doll(self):
        state = _toy_state(personal_remaining=1200, available=0)

        self.assertFalse(self.plugin._should_pause_remote_placement(state))

    def test_remote_placement_guard_requires_auto_collect(self):
        self.plugin._auto_collect = False
        state = _toy_state(personal_remaining=1200, available=1)

        self.assertFalse(self.plugin._should_pause_remote_placement(state))

    def test_remote_target_search_is_limited_to_three_targets_per_run(self):
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append(action)
            return {"success": False, "message": "没有空展位"}

        self.plugin._post_action = post_action
        # 旧配置即使保存过更大的值，新版也必须硬限制为每轮最多 3 个目标。
        self.plugin._max_target_try = 99

        placed = self.plugin._place_target_slots(object(), _toy_state(), [])

        self.assertEqual([], placed)
        self.assertEqual(3, calls.count("random_target"))

    def test_failed_external_search_waits_ten_minutes_before_retry(self):
        self.assertEqual(600, self.plugin._placement_retry_seconds())

    def test_guarded_external_search_follows_personal_collect_time(self):
        state = _toy_state(personal_remaining=1800, available=1)
        with mock.patch.object(self.module.time, "time", return_value=1000):
            next_run = self.plugin._compute_next_run(state)

        self.assertEqual(2800, next_run)

    def test_requests_adapter_does_not_repeat_plugin_network_retries(self):
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

    def test_public_config_uses_automatic_cookie_and_dual_stack_network(self):
        config = self.plugin._get_config()

        self.assertNotIn("auto_cookie", config)
        self.assertNotIn("force_ipv4", config)
        self.assertEqual(1, config["self_slot_guard_hours"])

    def test_status_response_does_not_expose_cookie_to_status_page(self):
        self.plugin._cookie = "session=private-value"

        status = self.plugin._build_status(auto_refresh=False)

        self.assertNotIn("cookie", status["config"])
        self.assertEqual("session=private-value", self.plugin._get_config()["cookie"])

    def test_source_does_not_patch_global_ipv4_resolution(self):
        source = VUETOY_INIT.read_text(encoding="utf-8")

        self.assertNotIn("allowed_gai_family", source)
        self.assertNotIn("socket.AF_INET", source)

    def test_overview_reports_owned_personal_slots_instead_of_zero_booth_count(self):
        state = _toy_state()
        state["personal_slots"] = [
            {"occupant": {"viewer_is_occupant": True}},
            {"occupant": {"viewer_is_occupant": True}},
            {"occupant": {"viewer_is_occupant": False}},
        ]

        overview = self.plugin._merge_overview(
            self.plugin._build_overview(state),
            {"overview": {"booth_value": 0}},
        )

        self.assertEqual("2/3", overview[-1]["value"])

    def test_ensure_cookie_prefers_moviepilot_site_cookie(self):
        self.plugin._cookie = ""
        self.plugin._sync_cookie_from_site = lambda save_config=False, silent=True: {
            "success": True,
            "message": "已同步",
        }

        self.plugin._ensure_cookie()


if __name__ == "__main__":
    unittest.main()
