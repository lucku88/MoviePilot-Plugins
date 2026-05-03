import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INITS = {
    "vuepill": REPO_ROOT / "plugins.v2" / "vuepill" / "__init__.py",
    "vuetoy": REPO_ROOT / "plugins.v2" / "vuetoy" / "__init__.py",
    "vueemoji": REPO_ROOT / "plugins.v2" / "vueemoji" / "__init__.py",
}


def _install_moviepilot_stubs():
    requests_module = types.ModuleType("requests")

    class Session:
        def __init__(self):
            self.headers = {}
            self.trust_env = False
            self.proxies = {}

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

    triggers_module = types.ModuleType("apscheduler.triggers")
    sys.modules["apscheduler.triggers"] = triggers_module
    cron_module = types.ModuleType("apscheduler.triggers.cron")

    class CronTrigger:
        @classmethod
        def from_crontab(cls, *args, **kwargs):
            return cls()

        def get_next_fire_time(self, *args, **kwargs):
            return None

    cron_module.CronTrigger = CronTrigger
    sys.modules["apscheduler.triggers.cron"] = cron_module

    app_module = types.ModuleType("app")
    sys.modules["app"] = app_module

    core_module = types.ModuleType("app.core")
    sys.modules["app.core"] = core_module
    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(TZ="Asia/Shanghai", PROXY="")
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


def _load_plugin(key: str):
    _install_moviepilot_stubs()
    module_name = f"{key}_autocatchup_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, PLUGIN_INITS[key])
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class VueAutoCatchupTests(unittest.TestCase):
    def _patch_save_dependencies(self, plugin):
        plugin.init_plugin = lambda config: setattr(plugin, "_enabled", bool(config.get("enabled", True)))
        plugin._update_config = lambda: None
        plugin._reregister_plugin = lambda reason="": None

    def test_vuepill_save_config_runs_after_refresh_when_beach_ready(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._enable_beach = True
        plugin._enable_brick = True
        self._patch_save_dependencies(plugin)
        run_calls = []
        plugin._refresh_state = lambda reason, record_run=True: {"beach": {"ready": True}, "next_run_ts": 0}
        plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "pill_status": {"ran": True},
            "status": {"ran": True},
        }

        result = plugin._save_config({"enabled": True})

        self.assertEqual([(True, "save-config")], run_calls)
        self.assertEqual("配置已保存，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["pill_status"])

    def test_vuepill_save_config_does_not_run_for_brick_ready_without_overdue(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._enable_beach = True
        plugin._enable_brick = True
        self._patch_save_dependencies(plugin)
        run_calls = []
        plugin._refresh_state = lambda reason, record_run=True: {"brick": {"ready": True}, "beach": {"ready": False}}
        plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "不应执行",
        }

        result = plugin._save_config({"enabled": True})

        self.assertEqual([], run_calls)
        self.assertEqual("配置已保存", result["message"])

    def test_vuetoy_bootstrap_runs_after_refresh_when_personal_collectable(self):
        module = _load_plugin("vuetoy")
        plugin = module.VueToy()
        plugin._enabled = True
        plugin._auto_collect = True
        plugin._auto_place = True
        events = []
        plugin._refresh_state = lambda reason="": events.append(("refresh", reason)) or {
            "personal_slots": [{"viewer_is_occupant": True, "can_collect": True, "remaining_seconds": 0}],
            "cabinet": [],
            "remote_records": [],
        }
        plugin.run_job = lambda force=False, reason="manual": events.append(("run", force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "toy_status": {"ran": True},
        }

        result = plugin._bootstrap_worker()

        self.assertEqual([("refresh", "status-init"), ("run", True, "bootstrap")], events)
        self.assertEqual("补跑完成", result["message"])

    def test_vuetoy_bootstrap_does_not_run_for_available_dolls_without_personal_slot(self):
        module = _load_plugin("vuetoy")
        plugin = module.VueToy()
        plugin._enabled = True
        plugin._auto_collect = True
        plugin._auto_place = True
        run_calls = []
        plugin._refresh_state = lambda reason="": {
            "personal_slots": [{"empty": False, "viewer_is_occupant": False, "action_kind": "blocked"}],
            "cabinet": [{"can_place": True, "available": 3}],
            "remote_records": [],
        }
        plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "不应执行",
        }

        result = plugin._bootstrap_worker()

        self.assertEqual([], run_calls)
        self.assertEqual("启动状态已刷新", result["message"])

    def test_vueemoji_save_config_runs_after_refresh_when_pending_open_exists(self):
        module = _load_plugin("vueemoji")
        plugin = module.VueEmoji()
        plugin._enabled = True
        plugin._auto_stage = True
        plugin._auto_open_bags = True
        plugin._auto_spin = True
        plugin._cookie = "cookie=value"
        self._patch_save_dependencies(plugin)
        run_calls = []
        plugin._has_auto_jobs_enabled = lambda: True
        plugin._refresh_state = lambda reason="", record_run=True: {
            "pending_open": {"bag_tier": 1, "items": [{"emoji": "🎭"}]},
            "bags": [],
            "stage": {"can_start": False, "can_recall": False},
        }
        plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "emoji_status": {"ran": True},
            "status": {"ran": True},
        }

        result = plugin._save_config({"enabled": True, "auto_open_bags": True})

        self.assertEqual([(True, "save-config")], run_calls)
        self.assertEqual("配置已保存，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["emoji_status"])

    def test_vueemoji_pre_refresh_runs_only_when_saved_run_is_overdue(self):
        module = _load_plugin("vueemoji")
        plugin = module.VueEmoji()
        plugin._enabled = True
        plugin._auto_stage = True
        plugin._auto_open_bags = True
        plugin._auto_spin = True
        plugin._cookie = "cookie=value"
        now = plugin._aware_now()
        plugin._next_run_time = now - module.timedelta(seconds=30)
        plugin._next_trigger_time = now - module.timedelta(seconds=90)
        plugin._next_trigger_mode = "refresh"
        run_calls = []
        plugin._refresh_state = lambda reason="", record_run=True: {
            "pending_open": {},
            "bags": [],
            "stage": {"can_start": False, "can_recall": False},
        }
        original_run_job = plugin.run_job

        def run_job(force=False, reason="manual"):
            if force:
                run_calls.append((force, reason))
                return {"success": True, "message": "补跑完成", "emoji_status": {"ran": True}}
            return original_run_job(force=force, reason=reason)

        plugin.run_job = run_job

        result = plugin.run_job(force=False, reason="schedule")

        self.assertEqual([(True, "schedule")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_vueemoji_pre_refresh_does_not_run_before_saved_run_time(self):
        module = _load_plugin("vueemoji")
        plugin = module.VueEmoji()
        plugin._enabled = True
        plugin._auto_stage = True
        plugin._auto_open_bags = True
        plugin._auto_spin = True
        plugin._cookie = "cookie=value"
        now = plugin._aware_now()
        plugin._next_run_time = now + module.timedelta(seconds=60)
        plugin._next_trigger_time = now - module.timedelta(seconds=5)
        plugin._next_trigger_mode = "refresh"
        run_calls = []
        plugin._refresh_state = lambda reason="", record_run=True: {
            "pending_open": {},
            "bags": [],
            "stage": {"can_start": False, "can_recall": False},
        }
        original_run_job = plugin.run_job

        def run_job(force=False, reason="manual"):
            if force:
                run_calls.append((force, reason))
                return {"success": True, "message": "不应执行"}
            return original_run_job(force=force, reason=reason)

        plugin.run_job = run_job

        result = plugin.run_job(force=False, reason="schedule")

        self.assertEqual([], run_calls)
        self.assertEqual("运行前状态已刷新", result["message"])


if __name__ == "__main__":
    unittest.main()
