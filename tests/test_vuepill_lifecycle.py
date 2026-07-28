import importlib.util
import json
import sys
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

        def add_job(self, *args, **kwargs):
            self.jobs.append((args, kwargs))

        def remove_all_jobs(self):
            self.jobs.clear()

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
        encoded = json.dumps(value, ensure_ascii=False, default=str)
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
                encoded = json.dumps(value, ensure_ascii=False, default=str)
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
                encoded = json.dumps(response, ensure_ascii=False, default=str)
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
            default=str,
        )
        encoded_result = json.dumps(sync_result, ensure_ascii=False, default=str)
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

    def test_save_onlyonce_does_not_also_register_bootstrap(self):
        self.plugin.save_data("v020_initialized", True)
        registrations = []
        self.plugin._reregister_plugin = lambda reason="": registrations.append(
            reason
        )

        def refresh_state(**kwargs):
            self.plugin._schedule_next_run(None, "save-config", "all")
            return {"inventory": []}

        self.plugin._refresh_state = refresh_state
        self.plugin._run_after_refresh_if_due = lambda *args, **kwargs: None

        self.plugin._save_config({"enabled": True, "onlyonce": True})

        self.assertIsNotNone(self.plugin._scheduler)
        self.assertIs(self.plugin._scheduler.running, True)
        self.assertEqual(1, len(self.plugin._scheduler.jobs))
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
        encoded = json.dumps(result, ensure_ascii=False, default=str)
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
        encoded = json.dumps(result, ensure_ascii=False, default=str)
        for secret in (
            "stats-cookie-secret",
            "user-token-secret",
            "stats-token-secret",
            "nested-token-secret",
            "root-token-secret",
        ):
            self.assertNotIn(secret, encoded)

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
        encoded = json.dumps(result, ensure_ascii=False, default=str)
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
        raw_calls = json.dumps(logger.calls, ensure_ascii=False, default=str)
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
            default=str,
        )
        self.assertIn("执行崩溃", rendered_logs)
        for secret in (
            "traceback-cookie-secret",
            "traceback-token-secret",
        ):
            self.assertNotIn(secret, json.dumps(result, ensure_ascii=False, default=str))
            self.assertNotIn(secret, rendered_logs)
            self.assertNotIn(secret, raw_traceback_call)


if __name__ == "__main__":
    unittest.main()
