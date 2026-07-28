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
    for loaded_name in list(sys.modules):
        if loaded_name == module_name or loaded_name.startswith(f"{module_name}."):
            sys.modules.pop(loaded_name, None)
    if key == "vuepill":
        spec = importlib.util.spec_from_file_location(
            module_name,
            PLUGIN_INITS[key],
            submodule_search_locations=[str(PLUGIN_INITS[key].parent)],
        )
    else:
        spec = importlib.util.spec_from_file_location(module_name, PLUGIN_INITS[key])
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class VueAutoCatchupTests(unittest.TestCase):
    def _patch_save_dependencies(self, plugin):
        if hasattr(plugin, "MIGRATION_KEY"):
            plugin.save_data(plugin.MIGRATION_KEY, True)
        else:
            plugin.init_plugin = lambda config: setattr(
                plugin,
                "_enabled",
                bool(config.get("enabled", True)),
            )
        plugin._update_config = lambda: None
        plugin._reregister_plugin = lambda reason="": None

    def _ready_vuepill_for_scheduled_action(self, plugin, module, action="beach"):
        plugin._enabled = True
        plugin._notify = False
        plugin._random_delay_max_seconds = 0
        plugin._ready_retry_seconds = 60
        plugin._next_trigger_time = plugin._aware_now() - module.timedelta(seconds=1)
        plugin._next_trigger_mode = f"run:{action}"
        plugin._ensure_cookie = lambda: None
        plugin._build_session = lambda: object()
        plugin._reregister_plugin = lambda reason="": None

    def _vuepill_page(self, beach_ready=False, beach_next_ts=0, brick_ready=False, brick_next_ts=0):
        return {
            "title": "搬砖捡破烂炼魔丸",
            "server_now": int(time.time()),
            "stats": {
                "points": 0,
                "bonus_earned": 0,
                "magic_pills": 0,
                "daily_bricks": 50 if not brick_ready else 0,
                "daily_limit": 50,
            },
            "exchange": {},
            "brick": {
                "ready": brick_ready,
                "daily_bricks": 50 if not brick_ready else 0,
                "daily_limit": 50,
                "next_reset_ts": brick_next_ts,
                "status_text": "可以搬砖" if brick_ready else "今日搬砖已满",
            },
            "beach": {
                "ready": beach_ready,
                "status_text": "可以进入清理" if beach_ready else "沙滩冷却中",
                "next_ready_ts": beach_next_ts,
            },
            "inventory": [],
            "recipes": [],
        }

    def test_save_refresh_runs_when_beach_is_ready(self):
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

    def test_bootstrap_refresh_runs_when_saved_plan_is_overdue(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._enable_brick = True
        plugin._enable_beach = False
        plugin._next_run_time = plugin._aware_now() - module.timedelta(seconds=30)
        plugin._next_trigger_time = plugin._aware_now() - module.timedelta(seconds=90)
        plugin._next_trigger_mode = "run:brick"
        refresh_calls = []
        run_calls = []
        plugin._refresh_state = lambda reason, record_run=True: refresh_calls.append(
            (reason, record_run)
        ) or {"brick": {"ready": True}, "beach": {"ready": False}}
        plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "pill_status": {"ran": True},
        }

        result = plugin._bootstrap_worker()

        self.assertEqual([("status-init", False)], refresh_calls)
        self.assertEqual([(True, "bootstrap")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_pre_refresh_does_not_run_before_formal_time(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._enable_beach = True
        plugin._enable_brick = False
        plugin._notify = False
        plugin._next_run_time = plugin._aware_now() + module.timedelta(seconds=30)
        plugin._next_trigger_time = plugin._aware_now() - module.timedelta(seconds=1)
        plugin._next_trigger_mode = "refresh:beach"
        plugin._ensure_cookie = lambda: None
        plugin._refresh_state = lambda reason, record_run=True: {"beach": {"ready": True}}
        run_calls = []
        original_run_job = plugin.run_job

        def run_job(force=False, reason="manual"):
            if force:
                run_calls.append((force, reason))
                return {"success": True, "message": "不应提前执行"}
            return original_run_job(force=force, reason=reason)

        plugin.run_job = run_job

        result = plugin.run_job(force=False, reason="schedule")

        self.assertEqual([], run_calls)
        self.assertEqual("运行前状态已刷新", result["message"])

    def test_run_beach_rechecks_ready_after_first_page_is_cooling(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        self._ready_vuepill_for_scheduled_action(plugin, module, action="beach")
        plugin._enable_beach = True
        plugin._enable_brick = False
        initial_page = self._vuepill_page(beach_ready=False, beach_next_ts=int(time.time()) + 1)
        ready_page = self._vuepill_page(beach_ready=True)
        cooldown_page = self._vuepill_page(
            beach_ready=False,
            beach_next_ts=int(time.time()) + 7200,
        )
        beach_calls = []
        stable_pages = [ready_page, cooldown_page]
        plugin._fetch_page_state = lambda session: initial_page
        plugin._fetch_stable_page_state = lambda *args, **kwargs: stable_pages.pop(0)
        plugin._run_beach_flow = lambda session: beach_calls.append("beach") or {
            "done": True,
            "items": [{"name": "木材", "count": 1, "icon": "🪵"}],
        }
        plugin._compute_next_plan = lambda page: (int(time.time()) + 7200, "beach")
        plugin._schedule_next_run = lambda *args, **kwargs: None
        plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        plugin._append_history = lambda *args, **kwargs: None

        result = plugin.run_job(force=False, reason="schedule")

        self.assertEqual(["beach"], beach_calls)
        self.assertEqual([], stable_pages)
        self.assertIn("沙滩", result["message"])
        self.assertNotEqual("ℹ️ 本次无可执行动作", result["message"])

    def test_run_beach_stays_short_retry_when_every_refresh_is_not_ready(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        self._ready_vuepill_for_scheduled_action(plugin, module, action="beach")
        plugin._enable_beach = True
        plugin._enable_brick = True
        future_brick = int(time.time()) + 24 * 3600
        not_ready_page = self._vuepill_page(
            beach_ready=False,
            beach_next_ts=0,
            brick_ready=False,
            brick_next_ts=future_brick,
        )
        beach_calls = []
        plugin._fetch_page_state = lambda session: not_ready_page
        plugin._refresh_beach_due_page = lambda session, page: not_ready_page
        plugin._fetch_stable_page_state = lambda *args, **kwargs: not_ready_page
        plugin._run_beach_flow = lambda session: beach_calls.append("beach") or {"done": True, "items": []}
        plugin._compute_next_plan = lambda page: (future_brick, "brick")

        plugin.run_job(force=False, reason="schedule")
        next_run = plugin._load_saved_next_run()

        self.assertIsNotNone(next_run)
        self.assertEqual([], beach_calls)
        self.assertLessEqual(next_run.timestamp(), time.time() + plugin._ready_retry_seconds + 5)
        self.assertEqual("run:beach", plugin.get_data("next_trigger_mode"))

    def test_run_beach_does_not_repeat_failed_irreversible_flow(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        self._ready_vuepill_for_scheduled_action(plugin, module, action="beach")
        plugin._enable_beach = True
        plugin._enable_brick = False
        ready_page = self._vuepill_page(beach_ready=True)
        beach_calls = []
        plugin._fetch_page_state = lambda session: ready_page
        plugin._fetch_stable_page_state = lambda *args, **kwargs: ready_page
        plugin._run_beach_flow = lambda session: beach_calls.append("beach") or {
            "done": False,
            "items": [],
            "warning": "收集失败",
        }
        plugin._compute_next_plan = lambda page: (int(time.time()) + 7200, "beach")
        plugin._append_history = lambda *args, **kwargs: None

        plugin.run_job(force=False, reason="schedule")

        self.assertEqual(["beach"], beach_calls)
        self.assertEqual(1, plugin.get_data("consecutive_error_retries"))
        self.assertEqual("run:beach", plugin.get_data("next_trigger_mode"))

    def test_run_brick_never_cleans_ready_beach(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        self._ready_vuepill_for_scheduled_action(plugin, module, action="brick")
        plugin._enable_beach = True
        plugin._enable_brick = True
        page = self._vuepill_page(beach_ready=True, brick_ready=False)
        beach_calls = []
        plugin._fetch_page_state = lambda session: page
        plugin._fetch_stable_page_state = lambda *args, **kwargs: page
        plugin._run_beach_flow = lambda session: beach_calls.append("beach") or {"done": True, "items": []}
        plugin._compute_next_plan = lambda current_page: (int(time.time()) + 7200, "beach")
        plugin._schedule_next_run = lambda *args, **kwargs: None
        plugin._refresh_and_store_status = lambda *args, **kwargs: {}
        plugin._append_history = lambda *args, **kwargs: None

        plugin.run_job(force=False, reason="schedule")

        self.assertEqual([], beach_calls)

    def test_today_brick_quota_does_not_trigger_on_every_restart(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._enable_brick = True
        plugin._enable_beach = False
        plugin._next_run_time = plugin._aware_now() + module.timedelta(hours=12)
        plugin._next_trigger_time = plugin._aware_now() + module.timedelta(hours=11)
        plugin._next_trigger_mode = "refresh:brick"
        run_calls = []
        plugin._refresh_state = lambda reason, record_run=True: {
            "brick": {"ready": True, "daily_bricks": 1, "daily_limit": 50},
            "beach": {"ready": False},
        }
        plugin.run_job = lambda force=False, reason="manual": run_calls.append(
            (force, reason)
        ) or {"success": True, "message": "不应执行"}

        result = plugin._bootstrap_worker()

        self.assertEqual([], run_calls)
        self.assertEqual("启动状态已刷新", result["message"])

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
