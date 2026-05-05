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
