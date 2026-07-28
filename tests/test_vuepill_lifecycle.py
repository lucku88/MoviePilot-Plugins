import importlib.util
import json
import math
import sys
import threading
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = REPO_ROOT / "plugins.v2" / "vuepill"
PLUGIN_INIT = PLUGIN_DIR / "__init__.py"
PACKAGE_NAME = "vuepill_lifecycle_under_test"


def _install_moviepilot_stubs():
    requests_module = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class Timeout(RequestException):
        pass

    class ConnectionError(RequestException):
        pass

    class SSLError(RequestException):
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
    requests_module.exceptions = types.SimpleNamespace(
        RequestException=RequestException,
        Timeout=Timeout,
        ConnectionError=ConnectionError,
        SSLError=SSLError,
    )
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
            self.jobs = []
            self.shutdown_calls = []

        def add_job(self, *args, **kwargs):
            self.jobs.append((args, kwargs))

        def remove_all_jobs(self):
            self.jobs.clear()

        def shutdown(self, *args, **kwargs):
            self.shutdown_calls.append((args, kwargs))
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


def _load_plugin_module():
    _install_moviepilot_stubs()
    for module_name in list(sys.modules):
        if module_name == PACKAGE_NAME or module_name.startswith(f"{PACKAGE_NAME}."):
            sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        PLUGIN_INIT,
        submodule_search_locations=[str(PLUGIN_DIR)],
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return module


def make_plugin(module):
    plugin = module.VuePill()
    plugin._scheduler = None
    plugin._siteoper = None
    plugin._cookie = ""
    plugin._cookie_source = "未同步"
    return plugin


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, *responses):
        self.headers = {}
        self.responses = list(responses)
        self.post_calls = []

    def post(self, url, data, timeout):
        self.post_calls.append(
            {"url": url, "data": dict(data), "timeout": timeout}
        )
        return FakeResponse(self.responses.pop(0))


class RecordingLogger:
    def __init__(self):
        self.entries = []
        self.calls = []

    def _record(self, level, message, *args):
        self.calls.append((level, message, args))
        try:
            rendered = message % args if args else str(message)
        except Exception:
            rendered = str(message)
        self.entries.append(f"{level}:{rendered}")

    def info(self, message, *args, **kwargs):
        self._record("info", message, *args)

    def warning(self, message, *args, **kwargs):
        self._record("warning", message, *args)

    def error(self, message, *args, **kwargs):
        self._record("error", message, *args)


class VuePillLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_plugin_module()
        self.plugin = make_plugin(self.module)

    def _install_valid_site(self, cookie="sid=site-cookie-secret"):
        class ValidSiteOper:
            def get_by_domain(self, domain):
                return {
                    "cookie": cookie,
                    "url": "https://si-qi.xyz",
                    "ua": "Latest UA",
                }

        self.module.SiteOper = ValidSiteOper

    def _gift_page(self):
        return {
            "inventory": [
                {"name": "木材", "count": 5, "giftable": True},
                {"name": "砖块", "count": 600, "giftable": True},
                {"name": "魔丸", "count": 10, "giftable": False},
            ],
            "stats": {},
            "brick": {},
            "beach": {},
            "exchange": {},
            "recipes": [],
            "server_now": 0,
        }

    def _assert_public_value_has_no_secrets(self, value, secrets):
        sensitive_fragments = (
            "cookie",
            "token",
            "authorization",
            "password",
            "session",
            "secret",
        )

        def assert_safe(nested):
            if isinstance(nested, dict):
                for key, child in nested.items():
                    normalized_key = str(key).strip().lower().replace("-", "_")
                    if normalized_key not in {"cookie_source", "cookie_ready"}:
                        self.assertFalse(
                            any(fragment in normalized_key for fragment in sensitive_fragments),
                            f"敏感字段仍对外可见：{key}",
                        )
                    assert_safe(child)
            elif isinstance(nested, (list, tuple)):
                for child in nested:
                    assert_safe(child)

        assert_safe(value)
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        for secret in secrets:
            self.assertNotIn(secret, encoded)

    def test_first_v020_init_resets_old_state_and_stays_disabled(self):
        old_values = {
            "history": [{"title": "旧记录"}],
            "state": {"old": True},
            "pill_status": {"cookie": "old-secret"},
            "last_run": "2026-01-01 00:00:00",
            "next_run_time": "2026-01-02 00:00:00",
            "next_trigger_time": "2026-01-01 23:59:00",
            "next_trigger_mode": "run:all",
            "consecutive_error_retries": 4,
            "last_error_retry_detail": "old error",
        }
        for key, value in old_values.items():
            self.plugin.save_data(key, value)

        stop_calls = []
        self.plugin.stop_service = lambda: stop_calls.append(True)
        self.plugin.init_plugin(
            {
                "enabled": True,
                "reserve_magic_pill_count": 0,
                "cookie": "manual-secret",
                "auto_cookie": False,
            }
        )

        self.assertEqual([True], stop_calls)
        self.assertIs(self.plugin.get_data("v020_initialized"), True)
        self.assertEqual([], self.plugin.get_data("history"))
        self.assertEqual({}, self.plugin.get_data("state"))
        self.assertEqual({}, self.plugin.get_data("pill_status"))
        self.assertEqual("", self.plugin.get_data("last_run"))
        self.assertEqual("", self.plugin.get_data("next_run_time"))
        self.assertEqual("", self.plugin.get_data("next_trigger_time"))
        self.assertEqual("", self.plugin.get_data("next_trigger_mode"))
        self.assertEqual(0, self.plugin.get_data("consecutive_error_retries"))
        self.assertEqual("", self.plugin.get_data("last_error_retry_detail"))
        self.assertIs(self.plugin._enabled, False)
        self.assertEqual(10, self.plugin._reserve_magic_pill_count)
        self.assertIs(self.plugin._config_store["enabled"], False)
        self.assertEqual(10, self.plugin._config_store["reserve_magic_pill_count"])

    def test_v020_migration_and_save_config_are_serialized_across_instances(self):
        migration_plugin = make_plugin(self.module)
        saving_plugin = make_plugin(self.module)
        shared_data = {}
        shared_config = {}
        migration_plugin._data_store = shared_data
        saving_plugin._data_store = shared_data
        migration_plugin._config_store = shared_config
        saving_plugin._config_store = shared_config

        migration_write_started = threading.Event()
        allow_migration_write = threading.Event()
        saving_write_started = threading.Event()
        errors = []

        def migration_update_config(config):
            migration_write_started.set()
            if not allow_migration_write.wait(2):
                raise RuntimeError("迁移写入等待超时")
            shared_config.clear()
            shared_config.update(config)

        def saving_update_config(config):
            saving_write_started.set()
            shared_config.clear()
            shared_config.update(config)

        migration_plugin.update_config = migration_update_config
        saving_plugin.update_config = saving_update_config
        saving_plugin._refresh_state = lambda **kwargs: {"inventory": []}
        saving_plugin._run_after_refresh_if_due = lambda *args, **kwargs: None
        saving_plugin._reregister_plugin = lambda reason="": None

        def run_in_thread(action):
            try:
                action()
            except BaseException as err:
                errors.append(err)

        migration_thread = threading.Thread(
            target=run_in_thread,
            args=(lambda: migration_plugin.init_plugin({"enabled": True}),),
        )
        saving_thread = threading.Thread(
            target=run_in_thread,
            args=(
                lambda: saving_plugin._save_config(
                    {"enabled": True, "reserve_magic_pill_count": 7}
                ),
            ),
        )

        migration_thread.start()
        self.assertTrue(migration_write_started.wait(1))
        saving_thread.start()
        saving_wrote_before_migration_finished = saving_write_started.wait(0.2)
        allow_migration_write.set()
        migration_thread.join(2)
        saving_thread.join(2)

        self.assertFalse(migration_thread.is_alive())
        self.assertFalse(saving_thread.is_alive())
        self.assertEqual([], errors)
        self.assertFalse(saving_wrote_before_migration_finished)
        self.assertIs(shared_data.get("v020_initialized"), True)
        self.assertIs(shared_config.get("enabled"), True)
        self.assertEqual(7, shared_config.get("reserve_magic_pill_count"))

    def test_failed_default_config_write_leaves_migration_retryable(self):
        self.plugin.save_data("history", [{"title": "旧记录"}])
        original_update_config = self.plugin.update_config
        marker_during_write = []

        def fail_update_config(config):
            marker_during_write.append(
                self.plugin.get_data(self.plugin.MIGRATION_KEY)
            )
            raise RuntimeError("默认配置写入失败")

        self.plugin.update_config = fail_update_config
        with self.assertRaisesRegex(RuntimeError, "默认配置写入失败"):
            self.plugin.init_plugin({"enabled": True})

        self.assertEqual([None], marker_during_write)
        self.assertIsNone(self.plugin.get_data(self.plugin.MIGRATION_KEY))

        self.plugin.save_data("history", [{"title": "失败后的脏数据"}])
        self.plugin.update_config = original_update_config
        self.plugin.init_plugin({"enabled": True})

        self.assertIs(self.plugin.get_data(self.plugin.MIGRATION_KEY), True)
        self.assertEqual([], self.plugin.get_data("history"))
        self.assertIs(self.plugin._enabled, False)
        self.assertIs(self.plugin._config_store["enabled"], False)

    def test_saved_config_after_migration_can_enable_plugin(self):
        self.plugin.save_data("v020_initialized", True)
        self.plugin._refresh_state = lambda **kwargs: {"inventory": []}
        self.plugin._run_after_refresh_if_due = lambda *args, **kwargs: None
        self.plugin._reregister_plugin = lambda reason="": None

        result = self.plugin._save_config(
            {"enabled": True, "enable_beach": True}
        )

        self.assertIs(result["success"], True)
        self.assertIs(result["config"]["enabled"], True)
        self.assertIs(self.plugin._config_store["enabled"], True)

    def test_migration_runs_once_only(self):
        self.plugin.stop_service = lambda: None
        self.plugin.init_plugin({"enabled": True, "reserve_magic_pill_count": 0})
        self.plugin.save_data("history", [{"title": "新记录"}])

        self.plugin.init_plugin(
            {"enabled": True, "reserve_magic_pill_count": 7}
        )

        self.assertEqual([{"title": "新记录"}], self.plugin.get_data("history"))
        self.assertIs(self.plugin._enabled, True)
        self.assertEqual(7, self.plugin._reserve_magic_pill_count)

    def test_defaults_use_safe_v020_values(self):
        defaults = self.plugin._default_config()

        self.assertIs(defaults["enabled"], False)
        self.assertIs(defaults["notify"], True)
        self.assertIs(defaults["onlyonce"], False)
        self.assertIs(defaults["enable_brick"], True)
        self.assertIs(defaults["enable_beach"], True)
        self.assertIs(defaults["auto_craft"], False)
        self.assertIs(defaults["auto_exchange"], False)
        self.assertIs(defaults["use_proxy"], False)
        self.assertIs(defaults["force_ipv4"], True)
        self.assertEqual("5 0 * * *", defaults["brick_cron"])
        self.assertEqual(5, defaults["schedule_buffer_seconds"])
        self.assertEqual(10, defaults["reserve_magic_pill_count"])
        self.assertEqual(3, defaults["random_delay_max_seconds"])
        self.assertEqual(12, defaults["http_timeout"])
        self.assertEqual(5, defaults["http_retry_times"])
        self.assertEqual(1500, defaults["http_retry_delay"])
        self.assertEqual(60, defaults["ready_retry_seconds"])

    def test_public_config_and_api_never_expose_cookie_input(self):
        secret = "sid=manual-cookie-secret; token=manual-token-secret"
        self.plugin.save_data("v020_initialized", True)
        self.plugin._cookie = "sid=runtime-only-secret"
        self.plugin._cookie_source = "站点同步：si-qi.xyz"
        self.plugin._refresh_state = lambda **kwargs: {"inventory": []}
        self.plugin._run_after_refresh_if_due = lambda *args, **kwargs: None
        self.plugin._reregister_plugin = lambda reason="": None

        result = self.plugin._save_config(
            {
                "enabled": False,
                "cookie": secret,
                "auto_cookie": False,
            }
        )

        public_values = [
            self.plugin._default_config(),
            self.plugin._get_config(),
            self.plugin._config_store,
            result,
            self.plugin._build_status(auto_refresh=False),
        ]

        def assert_no_secret_fields(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    self.assertNotIn(
                        str(key).lower(),
                        {"cookie", "auto_cookie", "cookie_preview"},
                    )
                    assert_no_secret_fields(nested)
            elif isinstance(value, (list, tuple)):
                for nested in value:
                    assert_no_secret_fields(nested)

        for value in public_values:
            with self.subTest(value_type=type(value).__name__):
                assert_no_secret_fields(value)
                encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
                self.assertNotIn("manual-cookie-secret", encoded)
                self.assertNotIn("manual-token-secret", encoded)
        self.assertNotEqual(secret, self.plugin._cookie)
        status = self.plugin._build_status(auto_refresh=False)
        self.assertIn("cookie_source", status)
        self.assertIn("cookie_ready", status)

    def test_public_status_filters_nested_sensitive_data_and_keeps_uids(self):
        secrets = (
            "pill-cookie-secret",
            "pill-token-secret",
            "pill-auth-secret",
            "pill-session-secret",
            "history-password-secret",
            "history-dict-cookie-secret",
            "history-dict-token-secret",
            "config-client-secret",
        )
        self.plugin.save_data(
            "pill_status",
            {
                "schema_version": self.plugin.plugin_version,
                "uid": "visible-pill-uid",
                "target_uid": "visible-target-uid",
                "Cookie": "pill-cookie-secret",
                "nested": [
                    {
                        "access_token": "pill-token-secret",
                        "message": "普通中文状态",
                    },
                    (
                        {
                            "authorization": "Bearer pill-auth-secret",
                            "session_id": "pill-session-secret",
                        },
                    ),
                ],
            },
        )
        self.plugin.save_data(
            "history",
            [
                {
                    "uid": "visible-history-uid",
                    "password": "history-password-secret",
                    "message": (
                        "处理失败：{'Cookie':'history-dict-cookie-secret',"
                        "'token':'history-dict-token-secret'}，请稍后重试"
                    ),
                }
            ],
        )
        self.plugin._get_config = lambda include_options=True: {
            "enabled": False,
            "client_secret": "config-client-secret",
            "target_uid": "visible-config-target",
        }

        status = self.plugin._build_status(auto_refresh=False)

        self._assert_public_value_has_no_secrets(status, secrets)
        self.assertEqual("visible-pill-uid", status["pill_status"]["uid"])
        self.assertEqual("visible-target-uid", status["pill_status"]["target_uid"])
        self.assertEqual("visible-history-uid", status["history"][0]["uid"])
        self.assertEqual("visible-config-target", status["config"]["target_uid"])
        self.assertIn("普通中文状态", status["pill_status"]["nested"][0]["message"])
        self.assertIn("处理失败", status["history"][0]["message"])
        self.assertIn("请稍后重试", status["history"][0]["message"])

    def test_sensitive_key_values_redact_sibling_messages_status_and_logs(self):
        public_value = self.plugin._sanitize_public_response(
            {
                "token": "S",
                "message": "server echoed S",
                "nested": {
                    "password": 42,
                    "message": "server echoed code 42",
                },
                "session": float("inf"),
                "float_message": "server echoed inf",
                "authorization": True,
                "bool_message": "server echoed true",
                "client_secret": None,
                "none_message": "server echoed null",
            }
        )

        self.assertNotIn("token", public_value)
        self.assertEqual("server echoed [REDACTED]", public_value["message"])
        self.assertNotIn("password", public_value["nested"])
        self.assertEqual(
            "server echoed code [REDACTED]",
            public_value["nested"]["message"],
        )
        self.assertEqual(
            "server echoed [REDACTED]",
            public_value["float_message"],
        )
        self.assertEqual(
            "server echoed true",
            public_value["bool_message"],
        )
        self.assertEqual(
            "server echoed [REDACTED]",
            public_value["none_message"],
        )

        self.plugin.save_data(
            "pill_status",
            {
                "schema_version": self.plugin.plugin_version,
                "access_token": "STATUS-SECRET",
                "message": "status echoed STATUS-SECRET",
            },
        )
        status = self.plugin._build_status(auto_refresh=False)
        self.assertEqual(
            "status echoed [REDACTED]",
            status["pill_status"]["message"],
        )

        self._install_valid_site("sid=safe-site-cookie")
        logger = RecordingLogger()
        self.module.logger = logger
        session = FakeSession(
            {
                "success": False,
                "token": "LOG-SECRET",
                "message": "server echoed LOG-SECRET",
            }
        )
        self.plugin._build_session = lambda: session
        self.plugin._fetch_page_state = lambda current_session: self._gift_page()

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "target_uid": "12345", "quantity": 1}
        )

        self.assertEqual("server echoed [REDACTED]", result["message"])
        rendered_logs = "\n".join(logger.entries)
        raw_calls = json.dumps(logger.calls, ensure_ascii=False, allow_nan=False)
        self.assertNotIn("LOG-SECRET", rendered_logs)
        self.assertNotIn("LOG-SECRET", raw_calls)

    def test_public_filter_drops_numeric_secret_twins_but_keeps_common_scalars(self):
        public_value = self.plugin._sanitize_public_response(
            {
                "token": 424242,
                "count": 424242,
                "message": "server echoed 424242",
                "nested": {
                    "password": 12.5,
                    "ratio": 12.5,
                },
                "common": {
                    "access_token": 1,
                    "count": 1,
                    "authorization": True,
                    "ready": True,
                    "session": 0,
                    "zero": 0,
                    "secret": False,
                    "enabled": False,
                    "one_text": "普通版本 1",
                    "zero_text": "普通数量 0",
                    "true_text": "普通状态 true",
                    "false_text": "普通状态 false",
                },
            }
        )

        self.assertNotIn("count", public_value)
        self.assertEqual("server echoed [REDACTED]", public_value["message"])
        self.assertNotIn("nested", public_value)
        self.assertEqual(1, public_value["common"]["count"])
        self.assertIs(public_value["common"]["ready"], True)
        self.assertEqual(0, public_value["common"]["zero"])
        self.assertIs(public_value["common"]["enabled"], False)
        self.assertEqual("普通版本 1", public_value["common"]["one_text"])
        self.assertEqual("普通数量 0", public_value["common"]["zero_text"])
        self.assertEqual("普通状态 true", public_value["common"]["true_text"])
        self.assertEqual("普通状态 false", public_value["common"]["false_text"])

    def test_public_filter_fails_closed_when_secret_limit_is_exceeded(self):
        sensitive_rows = [
            {
                "token": f"ZXQ-SENSITIVE-{index * 2:04d}",
                "session": f"ZXQ-SENSITIVE-{index * 2 + 1:04d}",
            }
            for index in range(251)
        ]
        overflow_secret = sensitive_rows[-1]["token"]
        raw_value = {
            "audit": sensitive_rows,
            "message": f"服务端回显 {overflow_secret}",
            "safe": "普通公开字段",
        }

        public_value = self.plugin._sanitize_public_response(raw_value)
        encoded = json.dumps(public_value, ensure_ascii=False, allow_nan=False)

        self.assertEqual(
            {
                "success": False,
                "message": self.plugin.PUBLIC_LIMIT_MESSAGE,
            },
            public_value,
        )
        self.assertNotIn(overflow_secret, encoded)
        self.assertNotIn(f"服务端回显 {overflow_secret}", encoded)

    def test_public_filter_emits_bounded_json_safe_acyclic_values(self):
        class CustomValue:
            pass

        cycle = {}
        cycle["self"] = cycle
        deep = {}
        cursor = deep
        for _ in range(40):
            cursor["next"] = {}
            cursor = cursor["next"]

        max_safe_integer = (1 << 53) - 1
        raw_value = {
            "none": None,
            "bool": True,
            "string": "safe",
            "float": 1.25,
            "safe_integer": max_safe_integer,
            "safe_negative_integer": -max_safe_integer,
            "tuple": ("safe", 2),
            "nan": float("nan"),
            "infinity": float("inf"),
            "unsafe_integer": max_safe_integer + 1,
            "unsafe_negative_integer": -max_safe_integer - 1,
            "set": {"unsafe"},
            "object": CustomValue(),
            7: "non-string-key",
            "cycle": cycle,
            "deep": deep,
            "large_list": list(range(600)),
            "large_dict": {str(index): index for index in range(600)},
        }

        public_value = self.plugin._sanitize_public_response(raw_value)
        encoded = json.dumps(
            public_value,
            ensure_ascii=False,
            allow_nan=False,
        )

        def assert_json_safe(value, depth=0):
            self.assertLessEqual(depth, 25)
            if type(value) is dict:
                self.assertLessEqual(len(value), 500)
                for key, nested in value.items():
                    self.assertIs(type(key), str)
                    assert_json_safe(nested, depth + 1)
            elif type(value) in {list, tuple}:
                self.assertLessEqual(len(value), 500)
                for nested in value:
                    assert_json_safe(nested, depth + 1)
            elif type(value) is float:
                self.assertTrue(math.isfinite(value))
            elif type(value) is int:
                self.assertLessEqual(abs(value), max_safe_integer)
            else:
                self.assertIn(type(value), {type(None), bool, str})

        assert_json_safe(public_value)
        self.assertTrue(encoded)
        self.assertEqual(max_safe_integer, public_value["safe_integer"])
        self.assertEqual(-max_safe_integer, public_value["safe_negative_integer"])
        self.assertEqual(500, len(public_value["large_list"]))
        self.assertEqual(500, len(public_value["large_dict"]))
        for unsafe_key in (
            "nan",
            "infinity",
            "unsafe_integer",
            "unsafe_negative_integer",
            "set",
            "object",
            "cycle",
        ):
            self.assertNotIn(unsafe_key, public_value)
        self.assertNotIn(7, public_value)

    def test_refresh_store_and_api_responses_use_deep_public_filter(self):
        secrets = (
            "stored-cookie-secret",
            "stored-token-secret",
            "api-password-secret",
            "api-session-secret",
            "api-dict-cookie-secret",
            "api-dict-token-secret",
        )
        stored_value = {
            "uid": "stored-visible-uid",
            "target_uid": "stored-visible-target",
            "nested": [
                {"cookie": "stored-cookie-secret"},
                ({"refresh_token": "stored-token-secret"},),
            ],
        }
        self.plugin._build_state_record = lambda *args, **kwargs: stored_value
        self.plugin._build_ui_state = lambda *args, **kwargs: stored_value

        refreshed = self.plugin._refresh_and_store_status({}, None, [])

        for value in (
            refreshed,
            self.plugin.get_data("state"),
            self.plugin.get_data("pill_status"),
        ):
            self._assert_public_value_has_no_secrets(value, secrets)
            self.assertEqual("stored-visible-uid", value["uid"])
            self.assertEqual("stored-visible-target", value["target_uid"])

        api_value = {
            "uid": "api-visible-uid",
            "target_uid": "api-visible-target",
            "password": "api-password-secret",
            "nested": [
                {"session": "api-session-secret"},
                (
                    "接口失败：{'Cookie':'api-dict-cookie-secret',"
                    "'token':'api-dict-token-secret'}，普通中文保留",
                ),
            ],
        }
        action_result = {
            "lines": [api_value["nested"][1][0]],
            "pill_status": api_value,
        }
        self.plugin._build_status = lambda auto_refresh=False: api_value
        self.plugin._refresh_state = lambda **kwargs: api_value
        self.plugin.run_job = lambda *args, **kwargs: {
            "success": True,
            "message": api_value["nested"][1][0],
            "pill_status": api_value,
            "status": api_value,
        }
        self.plugin._manual_move_bricks = lambda: action_result
        self.plugin._manual_clean_beach = lambda: action_result
        self.plugin._manual_exchange_points = lambda payload: action_result
        self.plugin._manual_craft_item = lambda payload: action_result
        self.plugin._manual_craft_max_pill = lambda payload: action_result

        responses = (
            self.plugin._get_status(),
            self.plugin._refresh_data(),
            self.plugin._run_now(),
            self.plugin._move_bricks_api({}),
            self.plugin._clean_beach_api({}),
            self.plugin._exchange_points_api({}),
            self.plugin._craft_item_api({}),
            self.plugin._craft_max_pill_api({}),
            self.plugin._gift_item_api({}),
            self.plugin._gift_stats_api({}),
        )
        for response in responses:
            with self.subTest(response_keys=tuple(response)):
                self._assert_public_value_has_no_secrets(response, secrets)
                encoded = json.dumps(response, ensure_ascii=False, allow_nan=False)
                self.assertIn("api-visible-uid", encoded)
                self.assertIn("api-visible-target", encoded)
                self.assertIn("普通中文保留", encoded)

    def test_ensure_cookie_reads_latest_object_and_dict_site_each_time(self):
        sites = [
            types.SimpleNamespace(
                cookie="sid=first-secret",
                url="https://first.example/",
                ua="First UA",
            ),
            {
                "cookie": "sid=second-secret",
                "url": "https://second.example/",
                "ua": "Second UA",
            },
        ]
        calls = []
        creations = []

        class LatestSiteOper:
            def __init__(self):
                creations.append(True)

            def get_by_domain(self, domain):
                calls.append(domain)
                return sites.pop(0)

        self.module.SiteOper = LatestSiteOper
        self.plugin._cookie = "sid=stale-secret"
        self.plugin._auto_cookie = False

        self.plugin._ensure_cookie()
        self.assertEqual("sid=first-secret", self.plugin._cookie)
        self.assertEqual("https://first.example", self.plugin._site_url)
        self.assertEqual("First UA", self.plugin._user_agent)

        self.plugin._ensure_cookie()
        self.assertEqual("sid=second-secret", self.plugin._cookie)
        self.assertEqual("https://second.example", self.plugin._site_url)
        self.assertEqual("Second UA", self.plugin._user_agent)
        self.assertEqual(["si-qi.xyz", "si-qi.xyz"], calls)
        self.assertEqual(2, len(creations))

    def test_invalid_site_cookie_has_no_manual_fallback_and_blocks_actions(self):
        class MissingSiteOper:
            def get_by_domain(self, domain):
                return None

        self.module.SiteOper = MissingSiteOper
        self.plugin._auto_cookie = False
        self.plugin._build_session = lambda: self.fail(
            "Cookie 同步失败后不应建立网站会话"
        )
        actions = [
            self.plugin._manual_move_bricks,
            self.plugin._manual_clean_beach,
            lambda: self.plugin._manual_exchange_points({}),
            lambda: self.plugin._manual_craft_item({"recipe_id": 1}),
            lambda: self.plugin._manual_craft_max_pill({}),
        ]

        for action in actions:
            with self.subTest(action=action):
                self.plugin._cookie = "sid=stale-manual-secret"
                with self.assertRaisesRegex(ValueError, "未找到站点 si-qi.xyz"):
                    action()
                self.assertEqual("", self.plugin._cookie)

    def test_ensure_cookie_rejects_empty_or_placeholder_cookie(self):
        sites = [
            {"cookie": "", "url": "https://si-qi.xyz", "ua": "UA"},
            {"cookie": "cookie", "url": "https://si-qi.xyz", "ua": "UA"},
        ]

        class InvalidCookieSiteOper:
            def get_by_domain(self, domain):
                return sites.pop(0)

        self.module.SiteOper = InvalidCookieSiteOper
        for _ in range(2):
            self.plugin._cookie = "sid=stale-secret"
            with self.assertRaisesRegex(ValueError, "未配置有效 Cookie"):
                self.plugin._ensure_cookie()
            self.assertEqual("", self.plugin._cookie)

    def test_sync_site_credentials_property_failure_has_no_partial_update(self):
        class BrokenSite:
            @property
            def cookie(self):
                return "sid=new-site-cookie"

            @property
            def url(self):
                raise RuntimeError("读取 URL 失败 token=site-read-secret")

            @property
            def ua(self):
                return "New UA"

        class BrokenSiteOper:
            def get_by_domain(self, domain):
                return BrokenSite()

        self.module.SiteOper = BrokenSiteOper
        self.plugin._siteoper = object()
        self.plugin._cookie = "sid=old-cookie"
        self.plugin._cookie_source = "旧来源"
        self.plugin._site_url = "https://old.example"
        self.plugin._user_agent = "Old UA"

        with self.assertRaisesRegex(ValueError, "读取站点 si-qi.xyz 配置失败") as caught:
            self.plugin._sync_site_credentials()

        self.assertNotIn("site-read-secret", str(caught.exception))
        self.assertIsNone(self.plugin._siteoper)
        self.assertEqual("", self.plugin._cookie)
        self.assertEqual("未同步", self.plugin._cookie_source)
        self.assertEqual(self.plugin.DEFAULT_SITE_URL, self.plugin._site_url)
        self.assertEqual(self.plugin.DEFAULT_USER_AGENT, self.plugin._user_agent)

    def test_site_sync_failure_redacts_cookie_read_before_url_error(self):
        raw_cookie = "theme=blue; account=URL-COOKIE-SECRET"
        logger = RecordingLogger()
        self.module.logger = logger

        class BrokenSite:
            @property
            def cookie(self):
                return raw_cookie

            @property
            def url(self):
                raise RuntimeError(
                    "读取 URL 失败，服务端回显 URL-COOKIE-SECRET"
                )

            @property
            def ua(self):
                return "New UA"

        class BrokenSiteOper:
            def get_by_domain(self, domain):
                return BrokenSite()

        self.module.SiteOper = BrokenSiteOper

        result = self.plugin._sync_cookie_from_site(silent=False)

        self.assertIs(result["success"], False)
        encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
        encoded_logs = json.dumps(logger.calls, ensure_ascii=False, allow_nan=False)
        self.assertNotIn(raw_cookie, encoded_result)
        self.assertNotIn(raw_cookie, encoded_logs)
        self.assertNotIn("URL-COOKIE-SECRET", encoded_result)
        self.assertNotIn("URL-COOKIE-SECRET", encoded_logs)

    def test_concurrent_site_syncs_commit_credentials_in_request_order(self):
        first_read_started = threading.Event()
        allow_first_read = threading.Event()
        second_sync_finished = threading.Event()
        call_lock = threading.Lock()
        call_count = 0
        errors = []

        class SlowFirstSite:
            @property
            def cookie(self):
                first_read_started.set()
                if not allow_first_read.wait(2):
                    raise RuntimeError("首个站点读取等待超时")
                return "sid=first-cookie"

            @property
            def url(self):
                return "https://first.example"

            @property
            def ua(self):
                return "First UA"

        class OrderedSiteOper:
            def get_by_domain(self, domain):
                nonlocal call_count
                with call_lock:
                    call_count += 1
                    current_call = call_count
                if current_call == 1:
                    return SlowFirstSite()
                return {
                    "cookie": "sid=second-cookie",
                    "url": "https://second.example",
                    "ua": "Second UA",
                }

        self.module.SiteOper = OrderedSiteOper

        def run_sync(done_event=None):
            try:
                self.plugin._sync_site_credentials()
            except BaseException as err:
                errors.append(err)
            finally:
                if done_event:
                    done_event.set()

        first_thread = threading.Thread(target=run_sync)
        second_thread = threading.Thread(
            target=run_sync,
            args=(second_sync_finished,),
        )

        first_thread.start()
        self.assertTrue(first_read_started.wait(1))
        second_thread.start()
        second_finished_before_first = second_sync_finished.wait(0.2)
        allow_first_read.set()
        first_thread.join(2)
        second_thread.join(2)

        self.assertFalse(first_thread.is_alive())
        self.assertFalse(second_thread.is_alive())
        self.assertEqual([], errors)
        self.assertFalse(second_finished_before_first)
        self.assertEqual("sid=second-cookie", self.plugin._cookie)
        self.assertEqual("https://second.example", self.plugin._site_url)
        self.assertEqual("Second UA", self.plugin._user_agent)

    def test_synced_cookie_is_never_persisted_or_previewed(self):
        secret = "sid=site-cookie-secret; token=site-token-secret"

        class ValidSiteOper:
            def get_by_domain(self, domain):
                return {
                    "cookie": secret,
                    "url": "https://si-qi.xyz",
                    "ua": "Latest UA",
                }

        self.module.SiteOper = ValidSiteOper
        self.plugin._ensure_cookie()
        self.plugin._update_config()
        sync_result = self.plugin._sync_cookie_from_site(
            save_config=True,
            silent=False,
        )

        encoded_config = json.dumps(
            self.plugin._config_store,
            ensure_ascii=False,
            allow_nan=False,
        )
        encoded_result = json.dumps(sync_result, ensure_ascii=False, allow_nan=False)
        self.assertNotIn("cookie", encoded_config.lower())
        self.assertNotIn(secret, encoded_config)
        self.assertNotIn("preview", encoded_result.lower())
        self.assertNotIn(secret, encoded_result)

    def test_get_api_is_exact_and_has_no_cookie_endpoint(self):
        expected = [
            ("/config", ("GET",)),
            ("/config", ("POST",)),
            ("/status", ("GET",)),
            ("/refresh", ("POST",)),
            ("/run", ("POST",)),
            ("/move-bricks", ("POST",)),
            ("/clean-beach", ("POST",)),
            ("/exchange-points", ("POST",)),
            ("/craft-item", ("POST",)),
            ("/craft-max-pill", ("POST",)),
            ("/gift-item", ("POST",)),
            ("/gift-stats", ("POST",)),
        ]

        api = self.plugin.get_api()
        actual = [(row["path"], tuple(row["methods"])) for row in api]

        self.assertEqual(expected, actual)
        self.assertTrue(all(row["auth"] == "bear" for row in api))
        self.assertFalse(any("cookie" in row["path"].lower() for row in api))

    def test_save_config_registers_bootstrap_at_most_once(self):
        self.plugin.save_data("v020_initialized", True)
        registrations = []
        self.plugin._reregister_plugin = lambda reason="": registrations.append(
            reason
        )

        def refresh_state(**kwargs):
            self.plugin._reregister_plugin("refresh")
            return {"inventory": []}

        self.plugin._refresh_state = refresh_state
        self.plugin._run_after_refresh_if_due = lambda *args, **kwargs: None

        self.plugin._save_config({"enabled": True})

        self.assertEqual(1, len(registrations))

    def test_save_onlyonce_queues_one_run_and_restores_normal_service(self):
        self.plugin.save_data("v020_initialized", True)
        registrations = []
        refresh_calls = []
        run_calls = []
        self.plugin._reregister_plugin = lambda reason="": registrations.append(
            reason
        )

        def refresh_state(**kwargs):
            refresh_calls.append(kwargs)
            return {"beach": {"ready": True}}

        self.plugin._refresh_state = refresh_state
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append(
            (force, reason)
        ) or {"success": True, "message": "执行完成"}

        result = self.plugin._save_config(
            {"enabled": True, "enable_beach": True, "onlyonce": True}
        )

        self.assertIs(result["success"], True)
        self.assertEqual([], refresh_calls)
        self.assertEqual([], run_calls)
        self.assertIsNotNone(self.plugin._scheduler)
        self.assertIs(self.plugin._scheduler.running, True)
        self.assertEqual(1, len(self.plugin._scheduler.jobs))
        self.assertEqual([], registrations)

        temporary_scheduler = self.plugin._scheduler
        self.plugin._next_trigger_time = self.plugin._aware_now() + self.module.timedelta(
            minutes=5
        )
        self.plugin._bootstrap_pending = False
        self.assertEqual([], self.plugin.get_service())

        job_func = temporary_scheduler.jobs[0][1]["func"]
        worker_result = job_func()

        self.assertIs(worker_result["success"], True)
        self.assertEqual([(True, "onlyonce")], run_calls)
        self.assertIsNone(self.plugin._scheduler)
        self.assertIs(temporary_scheduler.running, False)
        self.assertEqual([], temporary_scheduler.jobs)
        self.assertEqual(1, len(temporary_scheduler.shutdown_calls))
        self.assertEqual(1, len(registrations))
        self.assertEqual(1, len(self.plugin.get_service()))

    def test_concurrent_init_cannot_cancel_onlyonce_queued_by_save(self):
        self.plugin.save_data("v020_initialized", True)
        scheduler_started = threading.Event()
        cancellation_attempted = threading.Event()
        allow_start_return = threading.Event()
        schedulers = []
        errors = []
        save_result = {}
        original_scheduler_class = self.module.BackgroundScheduler

        class BlockingScheduler(original_scheduler_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                schedulers.append(self)

            def remove_all_jobs(self):
                cancellation_attempted.set()
                super().remove_all_jobs()

            def start(self):
                self.running = True
                scheduler_started.set()
                if not allow_start_return.wait(2):
                    raise RuntimeError("一次性调度启动等待超时")

        self.module.BackgroundScheduler = BlockingScheduler

        def save_config():
            try:
                save_result.update(
                    self.plugin._save_config(
                        {
                            "enabled": True,
                            "enable_beach": True,
                            "onlyonce": True,
                        }
                    )
                )
            except BaseException as err:
                errors.append(err)

        def reload_plugin():
            try:
                self.plugin.init_plugin(
                    {
                        "enabled": True,
                        "enable_beach": True,
                        "onlyonce": False,
                    }
                )
            except BaseException as err:
                errors.append(err)

        save_thread = threading.Thread(target=save_config)
        reload_thread = threading.Thread(target=reload_plugin)
        save_thread.start()
        self.assertTrue(scheduler_started.wait(1))
        reload_thread.start()
        cancelled_while_save_held_lock = cancellation_attempted.wait(0.5)
        allow_start_return.set()
        save_thread.join(2)
        reload_thread.join(2)

        self.assertFalse(save_thread.is_alive())
        self.assertFalse(reload_thread.is_alive())
        self.assertEqual([], errors)
        self.assertFalse(cancelled_while_save_held_lock)
        self.assertEqual("配置已保存，已排队一次性执行", save_result["message"])
        self.assertEqual(1, len(schedulers))
        self.assertIs(self.plugin._scheduler, schedulers[0])
        self.assertIs(schedulers[0].running, True)
        self.assertEqual(1, len(schedulers[0].jobs))
        self.assertEqual([], schedulers[0].shutdown_calls)

    def test_non_gift_action_uses_raw_secret_for_api_and_log_sanitizing(self):
        self._install_valid_site("sid=safe-site-cookie")
        self.plugin._reserve_magic_pill_count = 0
        logger = RecordingLogger()
        self.module.logger = logger
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: {
            "exchange": {
                "max_count": 1,
                "magic_pills": 1,
                "enabled": True,
            }
        }
        self.plugin._post_action = lambda *args, **kwargs: {
            "success": False,
            "access_token": "ACTION-SECRET",
            "message": "兑换失败，服务端回显 ACTION-SECRET",
        }

        result = self.plugin._exchange_points_api({"quantity": 1})

        self.assertIs(result["success"], False)
        self.assertIn("兑换失败", result["message"])
        encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
        encoded_logs = json.dumps(logger.calls, ensure_ascii=False, allow_nan=False)
        self.assertNotIn("ACTION-SECRET", encoded_result)
        self.assertNotIn("ACTION-SECRET", encoded_logs)

    def test_manual_worker_does_not_clear_a_replacement_scheduler(self):
        old_scheduler = self.module.BackgroundScheduler()
        old_scheduler.start()
        replacement_scheduler = self.module.BackgroundScheduler()
        replacement_scheduler.start()
        self.plugin._scheduler = old_scheduler
        self.plugin._enabled = True
        registrations = []
        self.plugin._reregister_plugin = lambda reason="": registrations.append(
            reason
        )

        def run_job(force=False, reason="manual"):
            self.plugin._scheduler = replacement_scheduler
            return {"success": True, "message": "执行完成"}

        self.plugin.run_job = run_job

        result = self.plugin._manual_worker()

        self.assertIs(result["success"], True)
        self.assertIs(self.plugin._scheduler, replacement_scheduler)
        self.assertIs(replacement_scheduler.running, True)
        self.assertIs(old_scheduler.running, False)
        self.assertEqual(1, len(old_scheduler.shutdown_calls))
        self.assertEqual([], replacement_scheduler.shutdown_calls)
        self.assertEqual([], registrations)

    def test_gift_item_rejects_invalid_quantity_stock_and_item(self):
        self._install_valid_site()
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_page_state = lambda session: self._gift_page()
        action_calls = []
        self.plugin._post_action = lambda *args, **kwargs: action_calls.append(
            (args, kwargs)
        ) or {"success": True}
        cases = [
            ([], "普通字典"),
            ({"item_name": "", "target_uid": "123", "quantity": 1}, "物品名称"),
            ({"item_name": "木材", "target_uid": "", "quantity": 1}, "UID"),
            ({"item_name": "木材", "target_uid": True, "quantity": 1}, "UID"),
            ({"item_name": "木材", "target_uid": "123", "quantity": 0}, "正整数"),
            ({"item_name": "木材", "target_uid": "123", "quantity": -1}, "正整数"),
            ({"item_name": "木材", "target_uid": "123", "quantity": True}, "正整数"),
            (
                {
                    "item_name": "木材",
                    "uid": "123",
                    "target_uid": "456",
                    "quantity": 1,
                },
                "不一致",
            ),
            ({"item_name": "木材", "target_uid": "123", "quantity": 6}, "库存"),
            ({"item_name": "砖块", "target_uid": "123", "quantity": 501}, "500"),
            ({"item_name": "魔丸", "target_uid": "123", "quantity": 1}, "不可赠送"),
            ({"item_name": "不存在", "target_uid": "123", "quantity": 1}, "不存在"),
        ]

        for payload, expected_message in cases:
            with self.subTest(payload=payload):
                result = self.plugin._gift_item_api(payload)
                self.assertIs(result["success"], False)
                self.assertIn(expected_message, result["message"])

        self.assertEqual([], action_calls)

    def test_gift_item_accepts_500_and_rejects_more_than_500(self):
        self._install_valid_site()
        self.plugin._build_session = lambda: object()
        pages = [self._gift_page(), self._gift_page(), self._gift_page()]
        self.plugin._fetch_page_state = lambda session: pages.pop(0)
        action_calls = []
        self.plugin._post_action = lambda *args, **kwargs: action_calls.append(
            (args, kwargs)
        ) or {"success": True, "message": "赠送成功"}
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None
        self.plugin._refresh_and_store_status = lambda *args, **kwargs: {}

        too_many = self.plugin._gift_item_api(
            {"item_name": "砖块", "target_uid": "123", "quantity": 501}
        )
        exact_limit = self.plugin._gift_item_api(
            {"item_name": "砖块", "target_uid": "123", "quantity": 500}
        )

        self.assertIs(too_many["success"], False)
        self.assertIn("500", too_many["message"])
        self.assertIs(exact_limit["success"], True)
        self.assertEqual(1, len(action_calls))
        self.assertEqual(500, action_calls[0][0][2]["quantity"])

    def test_gift_item_stays_successful_when_post_refresh_fails(self):
        self._install_valid_site()
        self.plugin._build_session = lambda: object()
        fetch_calls = []

        def fetch_page(session):
            fetch_calls.append(True)
            if len(fetch_calls) == 1:
                return self._gift_page()
            raise RuntimeError("刷新失败 token=refresh-secret")

        action_calls = []
        self.plugin._fetch_page_state = fetch_page
        self.plugin._post_action = lambda *args, **kwargs: action_calls.append(
            (args, kwargs)
        ) or {"success": True, "message": "赠送成功"}

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "target_uid": "123", "quantity": 1}
        )

        self.assertIs(result["success"], True)
        self.assertEqual(1, len(action_calls))
        self.assertEqual(2, len(fetch_calls))
        self.assertIn("状态刷新失败", result["message"])
        self.assertNotIn("refresh-secret", result["message"])

    def test_gift_item_cookie_failure_blocks_request(self):
        class MissingSiteOper:
            def get_by_domain(self, domain):
                return None

        self.module.SiteOper = MissingSiteOper
        self.plugin._build_session = lambda: self.fail(
            "Cookie 失败后不应建立赠送会话"
        )

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "target_uid": "123", "quantity": 1}
        )

        self.assertIs(result["success"], False)
        self.assertIn("未找到站点 si-qi.xyz", result["message"])

    def test_gift_item_success_posts_once_refreshes_and_returns_no_secrets(self):
        cookie = "sid=site-cookie-secret; token=site-token-secret"
        target_uid = 12345
        self._install_valid_site(cookie)
        session = FakeSession(
            {
                "success": True,
                "message": "赠送成功 token=website-token-secret",
                "token": "website-token-secret",
                "raw": {"cookie": cookie},
            }
        )
        self.plugin._build_session = lambda: session
        pages = [self._gift_page(), self._gift_page()]
        self.plugin._fetch_page_state = lambda current_session: pages.pop(0)
        self.plugin._compute_next_plan = lambda page: (None, "all")
        self.plugin._schedule_next_run = lambda *args, **kwargs: None

        def store_status(page, next_run, lines, **kwargs):
            status = {"inventory": page["inventory"]}
            self.plugin.save_data("pill_status", status)
            return status

        self.plugin._refresh_and_store_status = store_status

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "uid": target_uid, "quantity": 5}
        )

        self.assertIs(result["success"], True)
        self.assertEqual(
            {"success", "message", "item_name", "quantity", "target_uid", "status"},
            set(result),
        )
        self.assertEqual("木材", result["item_name"])
        self.assertEqual(5, result["quantity"])
        self.assertEqual("12345", result["target_uid"])
        self.assertEqual(1, len(session.post_calls))
        self.assertEqual(
            {
                "action": "gift_item",
                "item_name": "木材",
                "target_uid": "12345",
                "quantity": 5,
            },
            session.post_calls[0]["data"],
        )
        self.assertEqual([], pages)
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
        self.assertNotIn("site-cookie-secret", encoded)
        self.assertNotIn("site-token-secret", encoded)
        self.assertNotIn("website-token-secret", encoded)
        self.assertNotIn('"token"', encoded.lower())

    def test_gift_stats_validates_direction_and_string_range(self):
        self._install_valid_site()
        session = FakeSession({"success": True})
        self.plugin._build_session = lambda: session
        cases = [
            ({"direction": "sent", "range": "30"}, "direction"),
            ({"direction": "out", "range": "week"}, "range"),
            ({"direction": "out", "range": 30}, "字符串"),
        ]

        for payload, expected_message in cases:
            with self.subTest(payload=payload):
                result = self.plugin._gift_stats_api(payload)
                self.assertIs(result["success"], False)
                self.assertIn(expected_message, result["message"])

        self.assertEqual([], session.post_calls)

    def test_gift_stats_returns_whitelist_and_does_not_write_history(self):
        cookie = "sid=stats-cookie-secret"
        self._install_valid_site(cookie)
        raw_result = {
            "success": True,
            "message": "统计完成",
            "data": {
                "total_events": 2,
                "total_quantity": 7,
                "users": [
                    {
                        "uid": "10001",
                        "name": "用户甲",
                        "total_quantity": 5,
                        "events": 1,
                        "token": "user-token-secret",
                        "raw": {"cookie": cookie},
                    }
                ],
                "items": [
                    {
                        "item_name": "木材",
                        "quantity": 7,
                        "events": 2,
                        "authorization": "Bearer stats-token-secret",
                    }
                ],
                "token": "nested-token-secret",
            },
            "token": "root-token-secret",
        }
        session = FakeSession(raw_result)
        self.plugin._build_session = lambda: session
        original_history = [{"title": "原记录"}]
        self.plugin.save_data("history", original_history)

        result = self.plugin._gift_stats_api(
            {"direction": "IN", "range": " all "}
        )

        self.assertIs(result["success"], True)
        self.assertEqual(
            {
                "success",
                "message",
                "direction",
                "range",
                "total_events",
                "total_quantity",
                "users",
                "items",
                "status",
            },
            set(result),
        )
        self.assertEqual("in", result["direction"])
        self.assertEqual("all", result["range"])
        self.assertEqual(2, result["total_events"])
        self.assertEqual(7, result["total_quantity"])
        self.assertEqual(
            [
                {
                    "uid": "10001",
                    "name": "用户甲",
                    "total_quantity": 5,
                    "events": 1,
                }
            ],
            result["users"],
        )
        self.assertEqual(
            [{"item_name": "木材", "quantity": 7, "events": 2}],
            result["items"],
        )
        self.assertEqual(original_history, self.plugin.get_data("history"))
        self.assertEqual(1, len(session.post_calls))
        self.assertEqual(
            {"action": "gift_stats", "direction": "in", "range": "all"},
            session.post_calls[0]["data"],
        )
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
        for secret in (
            "stats-cookie-secret",
            "user-token-secret",
            "stats-token-secret",
            "nested-token-secret",
            "root-token-secret",
        ):
            self.assertNotIn(secret, encoded)

    def test_gift_stats_stops_at_500_rows_and_caps_js_safe_integers(self):
        max_safe_integer = (1 << 53) - 1
        huge_integer = max_safe_integer + 1000

        class GuardedUsers(dict):
            def items(self):
                for index in range(500):
                    yield str(index), huge_integer
                raise AssertionError("统计遍历超过 500 行")

        self._install_valid_site()
        raw_result = {
            "success": True,
            "message": "统计完成",
            "data": {
                "total_events": huge_integer,
                "total_quantity": str(huge_integer),
                "users": GuardedUsers(),
                "items": [
                    {
                        "item_name": f"物品-{index}",
                        "quantity": huge_integer,
                        "events": huge_integer,
                    }
                    for index in range(501)
                ],
            },
        }
        session = FakeSession(raw_result)
        self.plugin._build_session = lambda: session

        result = self.plugin._gift_stats_api(
            {"direction": "out", "range": "30"}
        )

        self.assertIs(result["success"], True)
        self.assertEqual(max_safe_integer, result["total_events"])
        self.assertEqual(max_safe_integer, result["total_quantity"])
        self.assertEqual(500, len(result["users"]))
        self.assertEqual(500, len(result["items"]))
        self.assertEqual(max_safe_integer, result["users"][0]["quantity"])
        self.assertEqual(max_safe_integer, result["items"][0]["quantity"])
        self.assertEqual(max_safe_integer, result["items"][0]["events"])
        json.dumps(result, ensure_ascii=False, allow_nan=False)

    def test_gift_api_error_and_logs_are_sanitized(self):
        cookie = "sid=error-cookie-secret; token=error-token-secret"
        target_uid = "98765"
        self._install_valid_site(cookie)
        logger = RecordingLogger()
        self.module.logger = logger
        session = FakeSession(
            {
                "success": False,
                "message": (
                    "Cookie: sid=error-cookie-secret; "
                    "Authorization: Bearer website-bearer-secret; "
                    "token=website-token-secret; uid=98765"
                ),
                "token": "raw-token-secret",
            }
        )
        self.plugin._build_session = lambda: session
        self.plugin._fetch_page_state = lambda current_session: self._gift_page()

        result = self.plugin._gift_item_api(
            {
                "item_name": "木材",
                "target_uid": target_uid,
                "quantity": 1,
            }
        )

        self.assertIs(result["success"], False)
        self.assertEqual(1, len(session.post_calls))
        self.assertTrue(logger.entries)
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
        log_text = "\n".join(logger.entries)
        for secret in (
            "error-cookie-secret",
            "error-token-secret",
            "website-bearer-secret",
            "website-token-secret",
            "raw-token-secret",
            target_uid,
        ):
            self.assertNotIn(secret, encoded)
            self.assertNotIn(secret, log_text)

    def test_quoted_dictionary_api_message_and_logger_are_sanitized(self):
        self._install_valid_site("sid=safe-site-cookie")
        logger = RecordingLogger()
        self.module.logger = logger
        session = FakeSession(
            {
                "success": False,
                "message": (
                    "处理失败：{'Cookie':'single-cookie-secret',"
                    "'token':'single-token-secret'}；"
                    '{"access_token":"double-token-secret"}，请稍后重试'
                ),
            }
        )
        self.plugin._build_session = lambda: session
        self.plugin._fetch_page_state = lambda current_session: self._gift_page()

        result = self.plugin._gift_item_api(
            {"item_name": "木材", "target_uid": "12345", "quantity": 1}
        )

        self.assertIs(result["success"], False)
        self.assertIn("处理失败", result["message"])
        self.assertIn("请稍后重试", result["message"])
        rendered_logs = "\n".join(logger.entries)
        raw_calls = json.dumps(logger.calls, ensure_ascii=False, allow_nan=False)
        for secret in (
            "single-cookie-secret",
            "single-token-secret",
            "double-token-secret",
        ):
            self.assertNotIn(secret, result["message"])
            self.assertNotIn(secret, rendered_logs)
            self.assertNotIn(secret, raw_calls)

    def test_run_job_sanitizes_traceback_before_logging_arguments(self):
        logger = RecordingLogger()
        self.module.logger = logger
        self.plugin._enabled = True
        self.plugin._notify = False
        self.plugin._record_error_retry = lambda detail: 1
        self.plugin._ensure_cookie = lambda: (_ for _ in ()).throw(
            RuntimeError(
                "执行崩溃 Cookie: traceback-cookie-secret; "
                "token=traceback-token-secret"
            )
        )

        result = self.plugin.run_job(force=True, reason="test")

        self.assertIs(result["success"], False)
        traceback_calls = [
            call for call in logger.calls if "异常堆栈" in str(call[1])
        ]
        self.assertEqual(1, len(traceback_calls))
        rendered_logs = "\n".join(logger.entries)
        raw_traceback_call = json.dumps(
            traceback_calls,
            ensure_ascii=False,
            allow_nan=False,
        )
        self.assertIn("执行崩溃", rendered_logs)
        for secret in (
            "traceback-cookie-secret",
            "traceback-token-secret",
        ):
            self.assertNotIn(
                secret,
                json.dumps(result, ensure_ascii=False, allow_nan=False),
            )
            self.assertNotIn(secret, rendered_logs)
            self.assertNotIn(secret, raw_traceback_call)

    def test_run_api_sanitizes_traceback_with_raw_cookie_from_site_getter(self):
        raw_cookie = "theme=blue; account=TRACE-RAW-COOKIE-SECRET"
        logger = RecordingLogger()
        self.module.logger = logger

        class BrokenSite:
            @property
            def cookie(self):
                return raw_cookie

            @property
            def url(self):
                raise RuntimeError(
                    f"读取 URL 失败，服务端直接回显 {raw_cookie}"
                )

            @property
            def ua(self):
                return "New UA"

        class BrokenSiteOper:
            def get_by_domain(self, domain):
                return BrokenSite()

        self.module.SiteOper = BrokenSiteOper
        self.plugin._enabled = True
        self.plugin._notify = False
        self.plugin._record_error_retry = lambda detail: 1

        result = self.plugin._run_now()

        self.assertIs(result["success"], False)
        self.assertIn("读取站点", result["message"])
        traceback_calls = [
            call for call in logger.calls if "异常堆栈" in str(call[1])
        ]
        self.assertEqual(1, len(traceback_calls))
        encoded_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
        rendered_logs = "\n".join(logger.entries)
        raw_log_calls = json.dumps(
            logger.calls,
            ensure_ascii=False,
            allow_nan=False,
        )
        for secret in (raw_cookie, "TRACE-RAW-COOKIE-SECRET"):
            self.assertNotIn(secret, encoded_result)
            self.assertNotIn(secret, rendered_logs)
            self.assertNotIn(secret, raw_log_calls)
        self.assertEqual("", self.plugin._cookie)

    def test_site_getter_cookie_error_persists_only_sanitized_retry_state(self):
        raw_cookie = "theme=blue; account=PERSISTED-RAW-COOKIE-SECRET"
        logger = RecordingLogger()
        self.module.logger = logger

        class BrokenSite:
            @property
            def cookie(self):
                return raw_cookie

            @property
            def url(self):
                raise RuntimeError(
                    f"读取 URL 失败，服务端直接回显 {raw_cookie}"
                )

            @property
            def ua(self):
                return "New UA"

        class BrokenSiteOper:
            def get_by_domain(self, domain):
                return BrokenSite()

        self.module.SiteOper = BrokenSiteOper
        self.plugin._enabled = True
        self.plugin._notify = False

        warning_result = self.plugin._move_bricks_api({})
        run_result = self.plugin._run_now()

        self.assertIs(warning_result["success"], False)
        self.assertIs(run_result["success"], False)
        self.assertEqual(
            1,
            self.plugin.get_data("consecutive_error_retries"),
        )
        self.assertIn(
            "[REDACTED]",
            self.plugin.get_data("last_error_retry_detail"),
        )
        persisted = {
            "last_error_retry_detail": self.plugin.get_data(
                "last_error_retry_detail"
            ),
            "history": self.plugin.get_data("history"),
            "status": self.plugin._build_status(auto_refresh=False),
        }
        public_payloads = {
            "warning_result": warning_result,
            "run_result": run_result,
            "persisted": persisted,
        }
        encoded_payloads = json.dumps(
            public_payloads,
            ensure_ascii=False,
            allow_nan=False,
        )
        rendered_logs = "\n".join(logger.entries)
        raw_log_calls = json.dumps(
            logger.calls,
            ensure_ascii=False,
            allow_nan=False,
        )
        self.assertTrue(any(call[0] == "warning" for call in logger.calls))
        self.assertTrue(any("异常堆栈" in str(call[1]) for call in logger.calls))
        for secret in (raw_cookie, "PERSISTED-RAW-COOKIE-SECRET"):
            self.assertNotIn(secret, encoded_payloads)
            self.assertNotIn(secret, rendered_logs)
            self.assertNotIn(secret, raw_log_calls)


if __name__ == "__main__":
    unittest.main()
