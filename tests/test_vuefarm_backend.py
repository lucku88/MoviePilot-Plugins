import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VUEFARM_INIT = REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py"


def _install_moviepilot_stubs():
    requests_module = types.ModuleType("requests")

    class Session:
        def __init__(self):
            self.headers = {}
            self.trust_env = False

        def mount(self, *args, **kwargs):
            return None

    requests_module.Session = Session
    requests_module.Response = type("Response", (), {})
    sys.modules["requests"] = requests_module

    adapters_module = types.ModuleType("requests.adapters")

    class HTTPAdapter:
        def __init__(self, *args, **kwargs):
            return None

    adapters_module.HTTPAdapter = HTTPAdapter
    sys.modules["requests.adapters"] = adapters_module

    urllib3_module = types.ModuleType("urllib3")
    sys.modules["urllib3"] = urllib3_module
    urllib3_util_module = types.ModuleType("urllib3.util")

    class Retry:
        def __init__(self, *args, **kwargs):
            return None

    urllib3_util_module.Retry = Retry
    sys.modules["urllib3.util"] = urllib3_util_module
    urllib3_connection_module = types.ModuleType("urllib3.util.connection")
    urllib3_connection_module.allowed_gai_family = lambda: None
    sys.modules["urllib3.util.connection"] = urllib3_connection_module

    app_module = types.ModuleType("app")
    sys.modules["app"] = app_module

    core_module = types.ModuleType("app.core")
    sys.modules["app.core"] = core_module
    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(TZ="Asia/Shanghai")
    sys.modules["app.core.config"] = config_module

    db_module = types.ModuleType("app.db")
    sys.modules["app.db"] = db_module
    site_oper_module = types.ModuleType("app.db.site_oper")

    class SiteOper:
        def get_by_domain(self, *args, **kwargs):
            return None

    site_oper_module.SiteOper = SiteOper
    sys.modules["app.db.site_oper"] = site_oper_module

    log_module = types.ModuleType("app.log")

    class Logger:
        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

    log_module.logger = Logger()
    sys.modules["app.log"] = log_module

    plugins_module = types.ModuleType("app.plugins")

    class PluginBase:
        def __init__(self):
            self._data_store = {}
            self._config_store = {}

        def get_data(self, key):
            return self._data_store.get(key)

        def save_data(self, key, value):
            self._data_store[key] = value

        def update_config(self, config):
            self._config_store = dict(config)

        def post_message(self, *args, **kwargs):
            return None

    plugins_module._PluginBase = PluginBase
    sys.modules["app.plugins"] = plugins_module

    scheduler_module = types.ModuleType("app.scheduler")

    class Scheduler:
        def update_plugin_job(self, *args, **kwargs):
            return None

        def reload_plugin_job(self, *args, **kwargs):
            return None

        def remove_plugin_job(self, *args, **kwargs):
            return None

    scheduler_module.Scheduler = Scheduler
    sys.modules["app.scheduler"] = scheduler_module

    schemas_module = types.ModuleType("app.schemas")
    schemas_module.NotificationType = types.SimpleNamespace(Plugin="Plugin")
    sys.modules["app.schemas"] = schemas_module

    apscheduler_module = types.ModuleType("apscheduler")
    sys.modules["apscheduler"] = apscheduler_module
    schedulers_module = types.ModuleType("apscheduler.schedulers")
    sys.modules["apscheduler.schedulers"] = schedulers_module
    background_module = types.ModuleType("apscheduler.schedulers.background")

    class BackgroundScheduler:
        def __init__(self, *args, **kwargs):
            self.running = False

        def add_job(self, *args, **kwargs):
            return None

        def remove_all_jobs(self):
            return None

        def shutdown(self):
            self.running = False

        def start(self):
            self.running = True

    background_module.BackgroundScheduler = BackgroundScheduler
    sys.modules["apscheduler.schedulers.background"] = background_module


def _load_vuefarm():
    _install_moviepilot_stubs()
    module_name = "vuefarm_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, VUEFARM_INIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _ready_farm_data(count=20):
    return {
        "success": True,
        "user_bonus": 0,
        "user_stats": {"total_harvest": "500000"},
        "seeds": [
            {
                "id": "4",
                "name": "茄子",
                "icon": "🍆",
                "cost": "3600",
                "grow_time": "259200",
                "base_reward": "4230",
                "unlock_harvest": "500000",
            }
        ],
        "lands": [],
        "user_lands": [
            {
                "land_id": str((idx // 10) + 1),
                "plot_index": str(idx % 10),
                "seed_id": "4",
                "plant_time": str(int(time.time()) - 259300),
                "harvest_time": str(int(time.time()) - 100),
                "is_ready": 1,
            }
            for idx in range(count)
        ],
        "inventory": [],
        "user_logs": [],
    }


class VueFarmBackendTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_vuefarm()
        self.plugin = self.module.VueFarm()
        self.plugin._enabled = True
        self.plugin._notify = False
        self.plugin._force_ipv4 = False
        self.plugin._random_delay_max_seconds = 0

    def test_single_plot_fallback_counts_each_success_once_not_cumulative_inventory(self):
        ready_data = _ready_farm_data(20)
        empty_data = {**ready_data, "user_lands": []}

        self.plugin._enable_ocr_harvest = True
        self.plugin._harvest_all = lambda session: {
            "success": False,
            "detail": "OCR 未识别出有效验证码",
            "reward": 0,
            "items": [],
        }

        refetch_calls = {"count": 0}

        def refetch_state(*args, **kwargs):
            refetch_calls["count"] += 1
            return ready_data if refetch_calls["count"] == 1 else empty_data

        harvest_calls = {"count": 0}

        def post_action(session, action, payload, retry_network=False):
            self.assertEqual("harvest", action)
            harvest_calls["count"] += 1
            return {
                "success": True,
                "inventory": {
                    "seed_id": 4,
                    "name": "茄子",
                    "icon": "🍆",
                    "quantity": harvest_calls["count"],
                    "unit_reward": 4230,
                },
            }

        self.plugin._refetch_state_until = refetch_state
        self.plugin._post_action = post_action

        result = self.plugin._harvest_ready_plots(object(), ready_data)
        lines = self.plugin._build_result_lines(
            True,
            False,
            False,
            result["harvest_items"],
            [],
            [],
            {},
            "暂无成熟作物",
            harvest_success_count=result["harvested_count"],
            harvest_note_detail=result["note"],
        )

        self.assertTrue(result["success"])
        self.assertEqual(20, result["harvested_count"])
        self.assertIn("✅收菜：🍆茄子×20", lines)
        self.assertNotIn("✅收菜：🍆茄子×210", lines)

    def test_prefer_mushroom_when_total_harvest_contains_commas(self):
        data = {
            "success": True,
            "user_stats": {"total_harvest": "5,000,000"},
            "seeds": [
                {
                    "id": "4",
                    "name": "茄子",
                    "icon": "🍆",
                    "cost": "3600",
                    "grow_time": "259200",
                    "base_reward": "4230",
                    "unlock_harvest": "500000",
                },
                {
                    "id": "5",
                    "name": "蘑菇",
                    "icon": "🍄",
                    "cost": "8400",
                    "grow_time": "604800",
                    "base_reward": "10080",
                    "unlock_harvest": "5000000",
                },
            ],
        }
        self.plugin._prefer_seed = "蘑菇"

        picked = self.plugin._pick_seed(data)

        self.assertIsNotNone(picked)
        self.assertEqual("蘑菇", picked["name"])

    def test_prefer_mushroom_when_seed_reports_unlocked_before_stats_refresh(self):
        data = {
            "success": True,
            "user_stats": {"total_harvest": "4,999,999"},
            "seeds": [
                {
                    "id": "4",
                    "name": "茄子",
                    "icon": "🍆",
                    "cost": "3600",
                    "grow_time": "259200",
                    "base_reward": "4230",
                    "unlock_harvest": "500000",
                    "unlocked": True,
                },
                {
                    "id": "5",
                    "name": "蘑菇",
                    "icon": "🍄",
                    "cost": "8400",
                    "grow_time": "604800",
                    "base_reward": "10080",
                    "unlock_harvest": "5000000",
                    "unlocked": True,
                },
            ],
        }
        self.plugin._prefer_seed = "蘑菇"

        picked = self.plugin._pick_seed(data)
        seed_shop = self.plugin._build_seed_shop(data)

        self.assertIsNotNone(picked)
        self.assertEqual("蘑菇", picked["name"])
        self.assertTrue(next(seed for seed in seed_shop if seed["name"] == "蘑菇")["unlocked"])

    def test_ocr_batch_disabled_harvests_individually_and_rechecks_remaining(self):
        ready_data = _ready_farm_data(3)
        remaining_one = {**ready_data, "user_lands": [ready_data["user_lands"][-1]]}
        empty_data = {**ready_data, "user_lands": []}
        refetches = iter([remaining_one, empty_data])
        harvest_calls = []

        self.plugin._enable_ocr_harvest = False
        self.plugin._harvest_all = lambda session: self.fail("OCR 批量收菜关闭时不应调用批量接口")
        self.plugin._refetch_state_until = lambda *args, **kwargs: next(refetches)

        def harvest_single(session, land_id, plot_index):
            harvest_calls.append((land_id, plot_index))
            return {
                "success": True,
                "items": [{"name": "茄子", "qty": 1, "unit": 4230, "icon": "🍆"}],
            }

        self.plugin._harvest_single_plot = harvest_single

        result = self.plugin._harvest_ready_plots(object(), ready_data)

        self.assertTrue(result["success"])
        self.assertEqual(3, result["harvested_count"])
        self.assertEqual(
            [(1, 0), (1, 1), (1, 2), (1, 2)],
            harvest_calls,
        )
        self.assertIn("逐坑位收菜", result["note"])
        self.assertIn("成功 3 块", result["note"])

    def test_ocr_batch_enabled_without_api_harvests_individually(self):
        ready_data = _ready_farm_data(2)
        empty_data = {**ready_data, "user_lands": []}
        harvest_calls = []

        self.plugin._enable_ocr_harvest = True
        self.plugin._ocr_api_url = ""
        self.plugin._harvest_all = lambda session: self.fail("未配置 OCR API 时不应调用批量接口")
        self.plugin._refetch_state_until = lambda *args, **kwargs: empty_data
        self.plugin._harvest_single_plot = lambda session, land_id, plot_index: harvest_calls.append((land_id, plot_index)) or {
            "success": True,
            "items": [{"name": "茄子", "qty": 1, "unit": 4230, "icon": "🍆"}],
        }

        result = self.plugin._harvest_ready_plots(object(), ready_data)

        self.assertTrue(result["success"])
        self.assertEqual(2, result["harvested_count"])
        self.assertEqual([(1, 0), (1, 1)], harvest_calls)
        self.assertIn("未配置 OCR API", result["note"])

    def test_batch_harvest_stops_after_three_failed_captcha_attempts(self):
        class FakeResponse:
            content = b"captcha"

            def raise_for_status(self):
                return None

        class FakeSession:
            def get(self, *args, **kwargs):
                return FakeResponse()

        captcha_calls = {"count": 0}

        def post_action(session, action, payload, retry_network=False):
            if action == "get_harvest_all_captcha":
                captcha_calls["count"] += 1
                return {"success": True, "captcha": {"image_url": "/cap.jpg", "imagehash": "hash"}}
            self.fail(f"验证码识别失败时不应提交收菜：{action}")

        self.plugin._post_action = post_action
        self.plugin._recognize_captcha = lambda session, image_content: ""

        result = self.plugin._harvest_all(FakeSession())

        self.assertFalse(result["success"])
        self.assertEqual(3, captcha_calls["count"])
        self.assertIn("OCR", result["detail"])

    def test_bootstrap_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
        }

        result = self.plugin._bootstrap_worker()

        self.assertEqual([(True, "bootstrap")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_scheduled_refresh_runs_full_job_when_next_run_is_overdue(self):
        overdue_ts = int(time.time()) - 60
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {
            "highlights": {"ready_count": 0},
            "next_run_ts": overdue_ts,
        }
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
        }

        result = self.plugin._refresh_worker()

        self.assertEqual([(True, "smart")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_save_config_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._enabled = True
        self.plugin.init_plugin = lambda config: setattr(self.plugin, "_enabled", True)
        self.plugin._update_config = lambda: None
        self.plugin._reregister_plugin = lambda reason="": None
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "status": {"ran": True},
        }

        result = self.plugin._save_config({"enabled": True})

        self.assertEqual([(True, "save-config")], run_calls)
        self.assertEqual("配置已保存，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["status"])

    def test_manual_refresh_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "status": {"ran": True},
        }

        result = self.plugin._refresh_data()

        self.assertEqual([(True, "manual-refresh")], run_calls)
        self.assertEqual("农场数据已刷新，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["status"])

    def test_status_refresh_with_ready_string_registers_immediate_run(self):
        data = _ready_farm_data(18)
        for plot in data["user_lands"]:
            plot["is_ready"] = "1"
            plot["plant_time"] = None
            plot["harvest_time"] = None

        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_state = lambda session: data
        self.plugin._reregister_plugin = lambda reason="": None

        before_ts = int(time.time())
        farm_status = self.plugin._refresh_state(reason="status-init", record_run=False)

        self.assertEqual(18, farm_status["highlights"]["ready_count"])
        self.assertEqual("run", self.plugin.get_data("next_trigger_mode"))
        next_trigger = self.plugin._parse_datetime(self.plugin.get_data("next_trigger_time"))
        self.assertIsNotNone(next_trigger)
        self.assertLessEqual(int(next_trigger.timestamp()), before_ts + self.plugin.MIN_TRIGGER_SECONDS + 2)

    def test_refresh_only_when_not_ready_or_overdue(self):
        run_calls = []
        future_ts = int(time.time()) + 3600
        self.plugin._refresh_state = lambda reason, record_run=False: {
            "highlights": {"ready_count": 0},
            "next_run_ts": future_ts,
            "next_trigger_ts": future_ts,
        }
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "不应执行",
        }

        result = self.plugin._refresh_worker()

        self.assertEqual([], run_calls)
        self.assertEqual("农场状态已预刷新", result["message"])


if __name__ == "__main__":
    unittest.main()
