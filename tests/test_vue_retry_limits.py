import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INITS = {
    "vuefarm": REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py",
    "vuepill": REPO_ROOT / "plugins.v2" / "vuepill" / "__init__.py",
    "vuetoy": REPO_ROOT / "plugins.v2" / "vuetoy" / "__init__.py",
    "vueemoji": REPO_ROOT / "plugins.v2" / "vueemoji" / "__init__.py",
}


def _install_moviepilot_stubs():
    requests_module = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class Timeout(RequestException):
        pass

    class ConnectionError(RequestException):
        pass

    class Session:
        def __init__(self):
            self.headers = {}
            self.trust_env = False
            self.proxies = {}

        def mount(self, *args, **kwargs):
            return None

    requests_module.Session = Session
    requests_module.Response = type("Response", (), {})
    requests_module.RequestException = RequestException
    requests_module.Timeout = Timeout
    requests_module.ConnectionError = ConnectionError
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
            self.kwargs = kwargs

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
            self.messages = []

        def get_data(self, key):
            return self._data_store.get(key)

        def save_data(self, key, value):
            self._data_store[key] = value

        def update_config(self, config):
            self._config_store = dict(config)

        def post_message(self, *args, **kwargs):
            self.messages.append((args, kwargs))

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
    module_name = f"{key}_retry_limit_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, PLUGIN_INITS[key])
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class VueRetryLimitTests(unittest.TestCase):
    def test_http_retry_defaults_to_five_for_all_vue_game_plugins(self):
        for key, class_name in [
            ("vuefarm", "VueFarm"),
            ("vuepill", "VuePill"),
            ("vuetoy", "VueToy"),
            ("vueemoji", "VueEmoji"),
        ]:
            with self.subTest(plugin=key):
                module = _load_plugin(key)
                plugin = getattr(module, class_name)()
                plugin._apply_config(plugin._default_config())
                self.assertEqual(5, plugin._http_retry_times)

    def test_vuefarm_stops_short_error_retry_after_five_consecutive_failures(self):
        module = _load_plugin("vuefarm")
        plugin = module.VueFarm()
        plugin._enabled = True
        plugin._notify = False
        plugin._ready_retry_seconds = 60
        plugin._random_delay_max_seconds = 0
        plugin._force_ipv4 = False
        plugin._cookie = "sid=ok"
        plugin.save_data("consecutive_error_retries", 5)
        scheduled = []
        plugin._ensure_cookie = lambda: None
        plugin._build_session = lambda: object()
        plugin._fetch_state = lambda session: (_ for _ in ()).throw(RuntimeError("network down"))
        plugin._schedule_next_run = lambda next_run, reason="": scheduled.append((next_run, reason))

        result = plugin.run_job(force=True, reason="bootstrap")

        self.assertFalse(result["success"])
        self.assertEqual([], scheduled)
        self.assertEqual(6, plugin.get_data("consecutive_error_retries"))

    def test_vuetoy_stops_short_error_retry_after_five_consecutive_failures(self):
        module = _load_plugin("vuetoy")
        plugin = module.VueToy()
        plugin._enabled = True
        plugin._notify = False
        plugin._http_timeout = 12
        plugin._random_delay_max_seconds = 0
        plugin._force_ipv4 = False
        plugin._cookie = "sid=ok"
        plugin.save_data("consecutive_error_retries", 5)
        scheduled = []
        plugin._ensure_cookie = lambda: None
        plugin._build_session = lambda: object()
        plugin._fetch_bundle = lambda session: (_ for _ in ()).throw(RuntimeError("network down"))
        plugin._schedule_next_run = lambda next_run, reason="": scheduled.append((next_run, reason))

        result = plugin.run_job(force=False, reason="schedule")

        self.assertFalse(result["success"])
        self.assertEqual([], scheduled)
        self.assertEqual(6, plugin.get_data("consecutive_error_retries"))

    def test_vueemoji_stops_short_error_retry_after_five_consecutive_failures(self):
        module = _load_plugin("vueemoji")
        plugin = module.VueEmoji()
        plugin._enabled = True
        plugin._notify = False
        plugin._auto_stage = True
        plugin._auto_spin = False
        plugin._auto_open_bags = False
        plugin._http_timeout = 12
        plugin._random_delay_max_seconds = 0
        plugin._force_ipv4 = False
        plugin._cookie = "sid=ok"
        plugin.save_data("consecutive_error_retries", 5)
        scheduled = []
        plugin._ensure_cookie = lambda: None
        plugin._build_session = lambda: object()
        plugin._fetch_bundle = lambda session: (_ for _ in ()).throw(RuntimeError("页面返回成功，但未解析到 SIQI_EMOJI_DATA"))
        plugin._schedule_next_run = lambda next_run, reason="": scheduled.append((next_run, reason))

        result = plugin.run_job(force=False, reason="schedule")

        self.assertFalse(result["success"])
        self.assertEqual([], scheduled)
        self.assertEqual(6, plugin.get_data("consecutive_error_retries"))

    def test_vuepill_limits_short_action_retry_after_five_warnings(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._notify = False
        plugin._ready_retry_seconds = 60
        plugin.save_data("consecutive_error_retries", 5)
        now = int(time.time())
        next_run, next_action = plugin._limit_retry_plan_if_needed(
            retry_action="beach",
            retry_ts=now + 60,
            next_run=now + 24 * 3600,
            next_action="brick",
            reason="schedule",
        )

        self.assertEqual(now + 24 * 3600, next_run)
        self.assertEqual("brick", next_action)
        self.assertEqual(6, plugin.get_data("consecutive_error_retries"))

