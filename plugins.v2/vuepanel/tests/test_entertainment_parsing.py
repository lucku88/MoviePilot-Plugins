import importlib.util
import sys
import threading
import types
import unittest
from pathlib import Path


def load_vuepanel_class():
    class DummyScheduler:
        def __init__(self, *args, **kwargs):
            pass

        def add_job(self, *args, **kwargs):
            pass

        def remove_all_jobs(self):
            pass

        def shutdown(self):
            pass

        def start(self):
            pass

        @property
        def running(self):
            return False

    class DummyCronTrigger:
        @classmethod
        def from_crontab(cls, *args, **kwargs):
            return cls()

    class DummyPluginBase:
        def get_data(self, *args, **kwargs):
            return None

        def save_data(self, *args, **kwargs):
            pass

        def update_config(self, *args, **kwargs):
            pass

        def post_message(self, *args, **kwargs):
            pass

    class DummyLogger:
        def info(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

    class DummySchedulerFacade:
        def update_plugin_job(self, *args, **kwargs):
            pass

        def remove_plugin_job(self, *args, **kwargs):
            pass

    request_exception = type("RequestException", (OSError,), {})
    connection_error = type("ConnectionError", (request_exception,), {})
    timeout_error = type("Timeout", (request_exception,), {})
    ssl_error = type("SSLError", (connection_error,), {})

    requests_mod = types.ModuleType("requests")
    requests_mod.Session = type("Session", (), {})
    requests_mod.Response = type("Response", (), {})
    requests_mod.exceptions = types.SimpleNamespace(
        SSLError=ssl_error,
        Timeout=timeout_error,
        ConnectionError=connection_error,
        RequestException=request_exception,
    )

    sys.modules.setdefault("requests", requests_mod)
    adapters_mod = types.ModuleType("requests.adapters")
    adapters_mod.HTTPAdapter = type("HTTPAdapter", (), {})
    sys.modules.setdefault("requests.adapters", adapters_mod)

    urllib3_mod = types.ModuleType("urllib3")
    urllib3_util_mod = types.ModuleType("urllib3.util")
    urllib3_util_mod.Retry = type("Retry", (), {})
    urllib3_mod.util = urllib3_util_mod
    sys.modules.setdefault("urllib3", urllib3_mod)
    sys.modules.setdefault("urllib3.util", urllib3_util_mod)
    urllib3_conn_mod = types.ModuleType("urllib3.util.connection")
    urllib3_conn_mod.allowed_gai_family = None
    urllib3_util_mod.connection = urllib3_conn_mod
    sys.modules.setdefault("urllib3.util.connection", urllib3_conn_mod)

    app_config_mod = types.ModuleType("app.core.config")
    app_config_mod.settings = types.SimpleNamespace(TZ="Asia/Shanghai")
    sys.modules.setdefault("app.core.config", app_config_mod)
    app_log_mod = types.ModuleType("app.log")
    app_log_mod.logger = DummyLogger()
    sys.modules.setdefault("app.log", app_log_mod)
    app_plugins_mod = types.ModuleType("app.plugins")
    app_plugins_mod._PluginBase = DummyPluginBase
    sys.modules.setdefault("app.plugins", app_plugins_mod)
    app_scheduler_mod = types.ModuleType("app.scheduler")
    app_scheduler_mod.Scheduler = DummySchedulerFacade
    sys.modules.setdefault("app.scheduler", app_scheduler_mod)
    app_schemas_mod = types.ModuleType("app.schemas")
    app_schemas_mod.NotificationType = types.SimpleNamespace(Plugin="Plugin")
    sys.modules.setdefault("app.schemas", app_schemas_mod)

    apscheduler_mod = types.ModuleType("apscheduler")
    apscheduler_schedulers_mod = types.ModuleType("apscheduler.schedulers")
    apscheduler_triggers_mod = types.ModuleType("apscheduler.triggers")
    sys.modules.setdefault("apscheduler", apscheduler_mod)
    sys.modules.setdefault("apscheduler.schedulers", apscheduler_schedulers_mod)
    sys.modules.setdefault("apscheduler.triggers", apscheduler_triggers_mod)
    apscheduler_background_mod = types.ModuleType("apscheduler.schedulers.background")
    apscheduler_background_mod.BackgroundScheduler = DummyScheduler
    sys.modules.setdefault("apscheduler.schedulers.background", apscheduler_background_mod)
    apscheduler_cron_mod = types.ModuleType("apscheduler.triggers.cron")
    apscheduler_cron_mod.CronTrigger = DummyCronTrigger
    sys.modules.setdefault("apscheduler.triggers.cron", apscheduler_cron_mod)

    plugin_path = Path(__file__).resolve().parents[1] / "__init__.py"
    spec = importlib.util.spec_from_file_location("vuepanel_under_test", plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VuePanel


class EntertainmentParsingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VuePanel = load_vuepanel_class()

    def test_parse_entertainment_page_keeps_only_available_shout_targets(self):
        html = """
        <form class="live-shout-form" method="post">
          <input name="live_cabinet_action" value="live_cabinet_shout">
          <input name="cabinet_no" value="1">
          <input name="slot_index" value="1">
          <input name="doll_key" value="two_b">
          <input name="slot_owner" value="10867">
          <button type="submit">为TA呐喊</button>
        </form>
        <form class="live-shout-form" method="post">
          <input name="live_cabinet_action" value="live_cabinet_shout">
          <input name="cabinet_no" value="1">
          <input name="slot_index" value="2">
          <input name="doll_key" value="plato">
          <input name="slot_owner" value="10867">
          <button type="submit" disabled>今日已呐喊</button>
        </form>
        <button class="live-emoji-shout-btn" data-cabinet="1" data-used="0" data-limit="1">一键呐喊舞台</button>
        <button class="live-emoji-shout-btn" data-cabinet="2" data-used="1" data-limit="1" disabled>今日已达上限</button>
        """

        parsed = self.VuePanel._parse_siqi_entertainment_page(html)

        self.assertEqual(
            parsed["cabinet_forms"],
            [
                {
                    "cabinet_no": "1",
                    "slot_index": "1",
                    "doll_key": "two_b",
                    "slot_owner": "10867",
                }
            ],
        )
        self.assertEqual(parsed["stage_buttons"], [{"cabinet_no": "1", "used": "0", "limit": "1"}])

    def test_extract_self_magic_reward_from_success_message(self):
        self.assertEqual(self.VuePanel._extract_self_magic_reward("你获得魔力 +34"), 34)
        self.assertEqual(self.VuePanel._extract_self_magic_reward("主人获得魔力 +6，你获得魔力 +7"), 7)
        self.assertEqual(self.VuePanel._extract_self_magic_reward("没有收益"), 0)


class CardNormalizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VuePanel = load_vuepanel_class()

    def test_normalize_cards_drops_deprecated_newapi_cards(self):
        plugin = self.VuePanel()

        normalized = plugin._normalize_cards(
            [
                {
                    "id": "newapi_checkin-default",
                    "title": "New API签到",
                    "module_key": "newapi_checkin",
                    "site_name": "New API 站点",
                    "site_url": "https://api.example.com",
                    "uid": "1001",
                    "cookie": "token=a",
                },
                {
                    "id": "newapi_checkin-copy",
                    "title": "New API签到 副本",
                    "module_key": "newapi_checkin",
                    "site_name": "New API 站点",
                    "site_url": "https://api-copy.example.com",
                    "uid": "2002",
                    "cookie": "token=b",
                },
                {
                    "id": "siqi_sign-default",
                    "title": "思齐签到",
                    "module_key": "siqi_sign",
                    "site_name": "思齐",
                    "site_url": "https://si-qi.xyz",
                    "cookie": "c_secure_pass=ok",
                },
            ]
        )

        self.assertNotIn("newapi_checkin", {item["module_key"] for item in normalized})
        self.assertTrue(any(item["module_key"] == "siqi_sign" for item in normalized))
        self.assertFalse(any(item["title"].startswith("New API") for item in normalized))


class CardRetryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VuePanel = load_vuepanel_class()

    @staticmethod
    def _card():
        return {
            "id": "siqi_sign-default",
            "title": "思齐签到",
            "site_name": "思齐",
        }

    def test_network_failure_retries_three_times_then_succeeds(self):
        plugin = self.VuePanel()
        attempts = []
        waits = []
        execution_flags = []
        request_error = sys.modules["requests"].exceptions.RequestException
        card = self._card()

        def execute_card(execution_card):
            attempts.append(1)
            execution_flags.append(execution_card.get("_disable_http_retries"))
            if len(attempts) < 4:
                raise request_error("temporary connection reset")
            return plugin._success_result("签到成功", "今日签到已完成。")

        plugin._execute_card = execute_card
        plugin._sleep_before_card_retry = waits.append

        result = plugin._execute_card_with_retry(card)

        self.assertTrue(result["success"])
        self.assertEqual(len(attempts), 4)
        self.assertEqual(waits, [30, 30, 30])
        self.assertEqual(execution_flags, [True, True, True, True])
        self.assertNotIn("_disable_http_retries", card)
        self.assertIn("自动重试 3 次后成功", result["detail_lines"])

    def test_network_failure_stops_after_three_retries(self):
        plugin = self.VuePanel()
        attempts = []
        waits = []

        def execute_card(_card):
            attempts.append(1)
            return plugin._error_result("执行失败", "网络连接暂时不可用。")

        plugin._execute_card = execute_card
        plugin._sleep_before_card_retry = waits.append

        result = plugin._execute_card_with_retry(self._card())

        self.assertFalse(result["success"])
        self.assertEqual(len(attempts), 4)
        self.assertEqual(waits, [30, 30, 30])
        self.assertIn("自动重试 3 次后仍未成功", result["detail_lines"])

    def test_permanent_or_completed_results_do_not_retry(self):
        cases = [
            ("缺少 Cookie", "请先填写 Cookie 后再执行。", False),
            ("Cookie 失效", "当前站点返回未登录状态。", False),
            ("今日已完成", "今日任务已经完成。", True),
        ]

        for title, message, success in cases:
            with self.subTest(title=title):
                plugin = self.VuePanel()
                attempts = []
                waits = []

                def execute_card(_card):
                    attempts.append(1)
                    if success:
                        return plugin._success_result(title, message)
                    return plugin._error_result(title, message)

                plugin._execute_card = execute_card
                plugin._sleep_before_card_retry = waits.append

                result = plugin._execute_card_with_retry(self._card())

                self.assertEqual(result["success"], success)
                self.assertEqual(len(attempts), 1)
                self.assertEqual(waits, [])

    def test_certificate_error_does_not_retry(self):
        plugin = self.VuePanel()
        waits = []
        ssl_error = sys.modules["requests"].exceptions.SSLError

        def execute_card(_card):
            raise ssl_error("certificate verify failed: self-signed certificate")

        plugin._execute_card = execute_card
        plugin._sleep_before_card_retry = waits.append

        with self.assertRaises(ssl_error):
            plugin._execute_card_with_retry(self._card())

        self.assertEqual(waits, [])

    def test_invalid_url_request_error_does_not_retry(self):
        plugin = self.VuePanel()
        waits = []
        request_error = sys.modules["requests"].exceptions.RequestException

        def execute_card(_card):
            raise request_error("Invalid URL 'not-a-url': No scheme supplied")

        plugin._execute_card = execute_card
        plugin._sleep_before_card_retry = waits.append

        with self.assertRaises(request_error):
            plugin._execute_card_with_retry(self._card())

        self.assertEqual(waits, [])

    def test_execution_session_disables_request_level_retries(self):
        plugin = self.VuePanel()
        captured = {}
        function_globals = plugin._build_session.__globals__
        requests_module = function_globals["requests"]
        original_retry = function_globals["Retry"]
        original_adapter = function_globals["HTTPAdapter"]
        original_session = requests_module.Session

        class CapturingRetry:
            def __init__(self, **kwargs):
                captured.update(kwargs)

        class DummyAdapter:
            def __init__(self, **_kwargs):
                pass

        class DummySession:
            def __init__(self):
                self.headers = {}
                self.cookies = {}
                self.trust_env = False

            def mount(self, *_args, **_kwargs):
                pass

        function_globals["Retry"] = CapturingRetry
        function_globals["HTTPAdapter"] = DummyAdapter
        requests_module.Session = DummySession
        plugin._http_retry_times = 3
        plugin._use_proxy = False

        try:
            plugin._build_session(
                {
                    "module_key": "siqi_sign",
                    "cookie": "c_secure_pass=ok",
                    "_disable_http_retries": True,
                }
            )
        finally:
            function_globals["Retry"] = original_retry
            function_globals["HTTPAdapter"] = original_adapter
            requests_module.Session = original_session

        self.assertEqual(captured["total"], 0)
        self.assertEqual(captured["connect"], 0)
        self.assertEqual(captured["read"], 0)
        self.assertEqual(captured["status"], 0)

    def test_hnr_network_failure_bubbles_up_for_card_retry(self):
        plugin = self.VuePanel()
        request_error = sys.modules["requests"].exceptions.RequestException

        class DummyResponse:
            text = ""

            @staticmethod
            def raise_for_status():
                pass

        class DummySession:
            @staticmethod
            def get(*_args, **_kwargs):
                return DummyResponse()

            @staticmethod
            def post(*_args, **_kwargs):
                raise request_error("temporary connection reset")

        plugin._http_timeout = 15
        plugin._build_session = lambda _card: DummySession()
        plugin._parse_hnr_page = lambda _html: {
            "rank": "1",
            "claims": [{"reward_type": "magic", "amount": "100", "label": "魔力"}],
        }

        with self.assertRaises(request_error):
            plugin._run_hnr_claim(
                {
                    "module_key": "hnr_claim",
                    "site_url": "https://si-qi.xyz",
                    "cookie": "c_secure_pass=ok",
                }
            )

    def test_run_job_routes_cards_through_retry_wrapper(self):
        plugin = self.VuePanel()
        calls = []
        card = self._card()
        card["notify"] = False

        plugin._random_delay_max_seconds = 0
        plugin._notify = False
        plugin._load_card_states = lambda: {}
        plugin._save_card_states = lambda _states: None
        plugin._build_dashboard = lambda _states: {}
        plugin.save_data = lambda *_args, **_kwargs: None
        plugin._save_schedule_meta = lambda: None
        plugin._append_history = lambda _state: None
        plugin._build_status = lambda auto_refresh=False: {}
        plugin._result_to_state = lambda _card, _result, previous=None, record_run=False: {
            "module_icon": "🪐",
            "title": "思齐签到",
            "status_text": "今日签到已完成。",
            "last_success": True,
            "level": "success",
        }
        plugin._execute_card = lambda _card: self.fail("run_job 不应绕过重试入口")
        plugin._execute_card_with_retry = lambda target: calls.append(target["id"]) or plugin._success_result(
            "签到成功",
            "今日签到已完成。",
        )

        result = plugin.run_job(target_cards=[card])

        self.assertTrue(result["success"])
        self.assertEqual(calls, [card["id"]])

    def test_state_refresh_and_execution_do_not_overlap(self):
        plugin = self.VuePanel()
        card = self._card()
        card["notify"] = False
        plugin._cards = [card]
        plugin._notify = False
        plugin._random_delay_max_seconds = 0
        plugin._load_card_states = lambda: {}
        plugin._save_card_states = lambda _states: None
        plugin._build_dashboard = lambda _states: {}
        plugin._save_schedule_meta = lambda: None
        plugin._append_history = lambda _state: None
        plugin._build_status = lambda auto_refresh=False: {}
        plugin.save_data = lambda *_args, **_kwargs: None
        plugin._result_to_state = lambda target, _result, previous=None, record_run=False: {
            "card_id": target["id"],
            "module_icon": "🪐",
            "title": target["title"],
            "status_text": "今日签到已完成。",
            "last_success": True,
            "level": "success",
        }

        refresh_started = threading.Event()
        allow_refresh_finish = threading.Event()
        run_started = threading.Event()
        errors = []

        def inspect_card(_card):
            refresh_started.set()
            if not allow_refresh_finish.wait(2):
                raise RuntimeError("刷新线程等待超时")
            return plugin._success_result("状态正常", "今日签到已完成。")

        def execute_card(_card):
            run_started.set()
            return plugin._success_result("签到成功", "今日签到已完成。")

        def refresh_state():
            try:
                plugin._refresh_state(reason="status-init")
            except BaseException as error:
                errors.append(error)

        def run_job():
            try:
                plugin.run_job(target_cards=[card])
            except BaseException as error:
                errors.append(error)

        plugin._inspect_card = inspect_card
        plugin._execute_card_with_retry = execute_card
        refresh_thread = threading.Thread(target=refresh_state)
        run_thread = threading.Thread(target=run_job)
        refresh_thread.start()
        self.assertTrue(refresh_started.wait(1))
        run_thread.start()
        overlapped = run_started.wait(0.2)
        allow_refresh_finish.set()
        refresh_thread.join(3)
        run_thread.join(3)

        self.assertFalse(overlapped, "状态刷新未结束前不应开始执行卡片")
        self.assertTrue(run_started.is_set())
        self.assertFalse(refresh_thread.is_alive())
        self.assertFalse(run_thread.is_alive())
        self.assertEqual([], errors)

    def test_catchup_selection_and_execution_are_atomic(self):
        plugin = self.VuePanel()
        catchup_card = self._card()
        scheduled_card = dict(catchup_card, id="hnr_claim-default", title="HNR领取")
        catchup_card["notify"] = False
        scheduled_card["notify"] = False
        plugin._cards = [catchup_card, scheduled_card]
        plugin._notify = False
        plugin._random_delay_max_seconds = 0
        plugin._load_card_states = lambda: {}
        plugin._save_card_states = lambda _states: None
        plugin._build_dashboard = lambda _states: {}
        plugin._refresh_state = lambda reason="": {}
        plugin._save_schedule_meta = lambda: None
        plugin._reregister_plugin = lambda _reason: None
        plugin._log_schedule_snapshot = lambda _reason: None
        plugin._append_history = lambda _state: None
        plugin._build_status = lambda auto_refresh=False: {}
        plugin.save_data = lambda *_args, **_kwargs: None
        plugin._result_to_state = lambda target, _result, previous=None, record_run=False: {
            "card_id": target["id"],
            "module_icon": "🪐",
            "title": target["title"],
            "status_text": "操作完成。",
            "last_success": True,
            "level": "success",
        }

        selection_started = threading.Event()
        allow_catchup_continue = threading.Event()
        scheduled_run_started = threading.Event()
        execution_order = []
        errors = []

        def select_missed(_states):
            selection_started.set()
            if not allow_catchup_continue.wait(2):
                raise RuntimeError("补跑判断线程等待超时")
            return [catchup_card]

        def execute_card(card):
            execution_order.append(card["id"])
            if card["id"] == scheduled_card["id"]:
                scheduled_run_started.set()
            return plugin._success_result("执行成功", "操作完成。")

        def catchup():
            try:
                plugin._refresh_and_catchup_schedule("startup")
            except BaseException as error:
                errors.append(error)

        def scheduled_run():
            try:
                plugin.run_job(target_cards=[scheduled_card])
            except BaseException as error:
                errors.append(error)

        plugin._select_missed_catchup_cards = select_missed
        plugin._execute_card_with_retry = execute_card
        catchup_thread = threading.Thread(target=catchup)
        scheduled_thread = threading.Thread(target=scheduled_run)
        catchup_thread.start()
        self.assertTrue(selection_started.wait(1))
        scheduled_thread.start()
        overlapped = scheduled_run_started.wait(0.2)
        allow_catchup_continue.set()
        catchup_thread.join(3)
        scheduled_thread.join(3)

        self.assertFalse(overlapped, "判断漏跑到执行补跑之间不能插入另一个定时执行")
        self.assertEqual([catchup_card["id"], scheduled_card["id"]], execution_order)
        self.assertFalse(catchup_thread.is_alive())
        self.assertFalse(scheduled_thread.is_alive())
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
