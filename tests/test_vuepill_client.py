import importlib.util
import socket
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT_PATH = REPO_ROOT / "plugins.v2" / "vuepill" / "site_client.py"
MISSING = object()


def _install_http_dependency_stubs():
    try:
        import requests  # noqa: F401
        import urllib3.util.connection  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    requests_module = types.ModuleType("requests")
    exceptions_module = types.ModuleType("requests.exceptions")

    class RequestException(Exception):
        pass

    class Timeout(RequestException):
        pass

    class RequestsConnectionError(RequestException):
        pass

    exceptions_module.RequestException = RequestException
    exceptions_module.Timeout = Timeout
    exceptions_module.ConnectionError = RequestsConnectionError
    requests_module.exceptions = exceptions_module
    sys.modules["requests.exceptions"] = exceptions_module

    adapters_module = types.ModuleType("requests.adapters")

    class HTTPAdapter:
        def __init__(self, max_retries=0, **kwargs):
            if hasattr(max_retries, "total"):
                self.max_retries = max_retries
            else:
                self.max_retries = types.SimpleNamespace(total=max_retries)
            self.kwargs = kwargs

    adapters_module.HTTPAdapter = HTTPAdapter
    sys.modules["requests.adapters"] = adapters_module

    class Session:
        def __init__(self):
            self.headers = {}
            self.adapters = {}
            self.trust_env = False

        def mount(self, prefix, adapter):
            self.adapters[prefix] = adapter

        def close(self):
            return None

    requests_module.Session = Session
    sys.modules["requests"] = requests_module

    urllib3_module = types.ModuleType("urllib3")
    urllib3_module.__path__ = []
    urllib3_util_module = types.ModuleType("urllib3.util")
    urllib3_util_module.__path__ = []
    urllib3_connection_module = types.ModuleType("urllib3.util.connection")
    urllib3_connection_module.allowed_gai_family = lambda: socket.AF_UNSPEC
    urllib3_util_module.connection = urllib3_connection_module
    urllib3_module.util = urllib3_util_module
    sys.modules["urllib3"] = urllib3_module
    sys.modules["urllib3.util"] = urllib3_util_module
    sys.modules["urllib3.util.connection"] = urllib3_connection_module


_install_http_dependency_stubs()


def _load_client_module():
    module_name = "vuepill_site_client_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, CLIENT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load site client: {CLIENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(
        self,
        *,
        status_code=200,
        text="",
        json_data=MISSING,
        json_error=None,
        reason="",
    ):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self._json_error = json_error
        self.reason = reason

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        if self._json_data is MISSING:
            return {"success": True}
        return self._json_data


class FakeSession:
    def __init__(self, *, get_results=None, post_results=None):
        self.get_results = list(get_results or [])
        self.post_results = list(post_results or [])
        self.get_calls = []
        self.post_calls = []

    @staticmethod
    def _take(results):
        if not results:
            raise AssertionError("Unexpected request")
        result = results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self._take(self.get_results)

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self._take(self.post_results)


class FailingSession:
    def __init__(self, error):
        self.error = error
        self.get_calls = []
        self.post_calls = []

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        raise self.error

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        raise self.error


class CapturingLogger:
    def __init__(self):
        self.messages = []

    def _record(self, message, *args):
        if args:
            try:
                message = message % args
            except (TypeError, ValueError):
                message = " ".join([str(message), *(str(arg) for arg in args)])
        self.messages.append(str(message))

    def warning(self, message, *args):
        self._record(message, *args)

    def info(self, message, *args):
        self._record(message, *args)

    def error(self, message, *args):
        self._record(message, *args)


class VuePillSiteClientTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_client_module()

    def make_client(self, **overrides):
        logger = overrides.pop("logger", CapturingLogger())
        values = {
            "site_url": "https://example.test/",
            "cookie": "session=COOKIE-VALUE",
            "user_agent": "VuePill-Test/1.0",
            "timeout": 12,
            "retry_times": 5,
            "retry_delay_ms": 0,
            "use_proxy": False,
            "force_ipv4": False,
            "logger": logger,
        }
        values.update(overrides)
        return self.module.VuePillSiteClient(**values), logger

    def test_site_client_module_exists(self):
        self.assertTrue(CLIENT_PATH.exists(), "site_client.py has not been created")

    def test_move_brick_retries_timeout_error_five_total_attempts(self):
        client, _ = self.make_client(retry_times=5, retry_delay_ms=10)
        session = FailingSession(TimeoutError("read timed out"))

        with mock.patch.object(self.module.time, "sleep") as sleep_mock:
            with self.assertRaises(self.module.VuePillSiteClientError):
                client.post_action(session, "move_brick", retry_network=True)

        self.assertEqual(5, len(session.post_calls))
        self.assertEqual(
            [mock.call(0.01), mock.call(0.02), mock.call(0.03), mock.call(0.04)],
            sleep_mock.call_args_list,
        )

    def test_gift_item_never_retries_even_when_requested(self):
        for retry_network in (False, True):
            with self.subTest(retry_network=retry_network):
                client, _ = self.make_client(retry_times=5)
                session = FailingSession(TimeoutError("read timed out"))

                with mock.patch.object(self.module.time, "sleep") as sleep_mock:
                    with self.assertRaises(self.module.VuePillSiteClientError):
                        client.post_action(
                            session,
                            "gift_item",
                            retry_network=retry_network,
                        )

                self.assertEqual(1, len(session.post_calls))
                sleep_mock.assert_not_called()

    def test_irreversible_post_actions_are_forced_to_one_attempt(self):
        for action in (
            "craft_item",
            "exchange_points",
            "enter_beach",
            "collect_all_trash",
            "gift_stats",
        ):
            with self.subTest(action=action):
                client, _ = self.make_client(retry_times=5)
                session = FailingSession(TimeoutError("connection reset"))

                with self.assertRaises(self.module.VuePillSiteClientError):
                    client.post_action(session, action, retry_network=True)

                self.assertEqual(1, len(session.post_calls))

    def test_post_defaults_to_one_attempt_for_retryable_action(self):
        client, _ = self.make_client(retry_times=5)
        session = FailingSession(TimeoutError("read timed out"))

        with self.assertRaises(self.module.VuePillSiteClientError):
            client.post_action(session, "move_brick")

        self.assertEqual(1, len(session.post_calls))

    def test_get_page_retries_at_most_five_times(self):
        client, _ = self.make_client(retry_times=5)
        session = FailingSession(TimeoutError("connection timed out"))

        with mock.patch.object(self.module.time, "sleep"):
            with self.assertRaises(self.module.VuePillSiteClientError):
                client.fetch_page_html(session)

        self.assertEqual(5, len(session.get_calls))

    def test_connection_reset_and_requests_connection_error_are_retryable(self):
        windows_reset = OSError("socket operation failed")
        windows_reset.winerror = 10054
        errors = (
            ConnectionResetError("connection reset by peer"),
            ConnectionError("connection closed"),
            self.module.requests.exceptions.ConnectionError("remote disconnected"),
            windows_reset,
        )

        for error in errors:
            with self.subTest(error=error.__class__.__name__):
                client, _ = self.make_client(retry_times=5)
                session = FailingSession(error)
                with mock.patch.object(self.module.time, "sleep"):
                    with self.assertRaises(self.module.VuePillSiteClientError):
                        client.post_action(
                            session,
                            "sync_game_state",
                            retry_network=True,
                        )
                self.assertEqual(5, len(session.post_calls))

    def test_retry_times_above_five_is_clamped_to_five(self):
        client, _ = self.make_client(retry_times=99)
        session = FailingSession(TimeoutError("connection timed out"))

        with mock.patch.object(self.module.time, "sleep"):
            with self.assertRaises(self.module.VuePillSiteClientError):
                client.post_action(session, "sync_game_state", retry_network=True)

        self.assertEqual(5, client.retry_times)
        self.assertEqual(5, len(session.post_calls))

    def test_http_5xx_retries_for_safe_post_action(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            post_results=[
                FakeResponse(
                    status_code=503,
                    json_data={"message": "temporarily unavailable"},
                    reason="Service Unavailable",
                ),
                FakeResponse(json_data={"success": True, "moved": 1}),
            ]
        )

        with mock.patch.object(self.module.time, "sleep"):
            result = client.post_action(
                session,
                "move_brick",
                retry_network=True,
            )

        self.assertEqual({"success": True, "moved": 1}, result)
        self.assertEqual(2, len(session.post_calls))

    def test_http_4xx_does_not_retry(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            post_results=[
                FakeResponse(
                    status_code=429,
                    json_data={"message": "too many requests"},
                    reason="Too Many Requests",
                ),
                FakeResponse(json_data={"success": True}),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "HTTP 429",
        ):
            client.post_action(session, "move_brick", retry_network=True)

        self.assertEqual(1, len(session.post_calls))

    def test_non_json_response_does_not_retry(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            post_results=[
                FakeResponse(json_error=ValueError("invalid json")),
                FakeResponse(json_data={"success": True}),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "non-JSON",
        ):
            client.post_action(session, "move_brick", retry_network=True)

        self.assertEqual(1, len(session.post_calls))

    def test_business_rejection_does_not_retry_and_uses_site_message(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            post_results=[
                FakeResponse(
                    json_data={"success": False, "message": "daily limit reached"}
                ),
                FakeResponse(json_data={"success": True}),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "daily limit reached",
        ):
            client.post_action(session, "move_brick", retry_network=True)

        self.assertEqual(1, len(session.post_calls))

    def test_list_json_response_is_rejected(self):
        client, _ = self.make_client()
        session = FakeSession(post_results=[FakeResponse(json_data=[{"success": True}])])

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "JSON object",
        ):
            client.post_action(session, "sync_game_state")

        self.assertEqual(1, len(session.post_calls))

    def test_all_eight_allowed_actions_are_accepted(self):
        allowed = (
            "sync_game_state",
            "move_brick",
            "enter_beach",
            "collect_all_trash",
            "craft_item",
            "exchange_points",
            "gift_item",
            "gift_stats",
        )
        client, _ = self.make_client()

        for action in allowed:
            with self.subTest(action=action):
                session = FakeSession(
                    post_results=[FakeResponse(json_data={"success": True})]
                )
                result = client.post_action(session, action)
                self.assertTrue(result["success"])
                self.assertEqual(1, len(session.post_calls))

    def test_reset_settings_and_unknown_actions_are_rejected(self):
        client, _ = self.make_client()

        for action in ("reset_game", "update_settings", "unknown_action"):
            with self.subTest(action=action):
                session = FakeSession()
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    "not allowed",
                ):
                    client.post_action(session, action)
                self.assertEqual(0, len(session.post_calls))

    def test_payload_cannot_override_action_and_none_values_are_ignored(self):
        client, _ = self.make_client()
        session = FakeSession(
            post_results=[FakeResponse(json_data={"success": True})]
        )

        client.post_action(
            session,
            "move_brick",
            payload={"action": "reset_game", "quantity": 3, "note": None},
        )

        _, kwargs = session.post_calls[0]
        self.assertEqual({"action": "move_brick", "quantity": 3}, kwargs["data"])

    def test_build_session_sets_headers_proxy_and_zero_adapter_retries(self):
        client, _ = self.make_client(use_proxy=True)

        session = client.build_session()
        self.addCleanup(session.close)

        self.assertEqual("VuePill-Test/1.0", session.headers["User-Agent"])
        self.assertEqual("session=COOKIE-VALUE", session.headers["Cookie"])
        self.assertEqual(
            "https://example.test/mowan.php",
            session.headers["Referer"],
        )
        self.assertEqual("XMLHttpRequest", session.headers["X-Requested-With"])
        self.assertEqual("keep-alive", session.headers["Connection"])
        self.assertIs(session.trust_env, True)
        self.assertEqual(0, session.adapters["http://"].max_retries.total)
        self.assertEqual(0, session.adapters["https://"].max_retries.total)

    def test_force_ipv4_false_does_not_change_global_urllib3_state(self):
        client, _ = self.make_client(force_ipv4=False)
        sentinel = lambda: socket.AF_UNSPEC

        with mock.patch.object(
            self.module.urllib3_connection,
            "allowed_gai_family",
            sentinel,
        ):
            session = client.build_session()
            self.addCleanup(session.close)
            self.assertIs(
                sentinel,
                self.module.urllib3_connection.allowed_gai_family,
            )

    def test_force_ipv4_true_uses_project_urllib3_override(self):
        client, _ = self.make_client(force_ipv4=True)
        sentinel = lambda: socket.AF_UNSPEC

        with mock.patch.object(
            self.module.urllib3_connection,
            "allowed_gai_family",
            sentinel,
        ):
            session = client.build_session()
            self.addCleanup(session.close)
            self.assertEqual(
                socket.AF_INET,
                self.module.urllib3_connection.allowed_gai_family(),
            )

    def test_fetch_page_uses_timestamp_no_cache_and_returns_text(self):
        client, _ = self.make_client(timeout=12)
        session = FakeSession(get_results=[FakeResponse(text="<html>game</html>")])

        with mock.patch.object(self.module.time, "time", return_value=123.456):
            html = client.fetch_page_html(session)

        self.assertEqual("<html>game</html>", html)
        url, kwargs = session.get_calls[0]
        self.assertEqual("https://example.test/mowan.php", url)
        self.assertEqual({"_": 123456}, kwargs["params"])
        self.assertEqual(
            {"Cache-Control": "no-cache", "Pragma": "no-cache"},
            kwargs["headers"],
        )
        self.assertEqual((12.0, 12.0), kwargs["timeout"])

    def test_empty_page_is_rejected_without_retry(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            get_results=[FakeResponse(text="   "), FakeResponse(text="<html>game</html>")]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "empty",
        ):
            client.fetch_page_html(session)

        self.assertEqual(1, len(session.get_calls))

    def test_obvious_login_page_is_rejected_without_retry(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            get_results=[
                FakeResponse(text='<form action="/login.php"><input type="password"></form>'),
                FakeResponse(text="<html>game</html>"),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "login",
        ):
            client.fetch_page_html(session)

        self.assertEqual(1, len(session.get_calls))

    def test_normal_game_page_with_login_link_is_not_rejected(self):
        client, _ = self.make_client()
        expected = '<html><a href="/login.php">Login</a><div id="game">ready</div></html>'
        session = FakeSession(get_results=[FakeResponse(text=expected)])

        html = client.fetch_page_html(session)

        self.assertEqual(expected, html)

    def test_cookie_token_and_uid_are_redacted_from_errors_and_logs(self):
        logger = CapturingLogger()
        client, _ = self.make_client(
            cookie="session=COOKIE-SECRET; auth=COOKIE-TWO",
            logger=logger,
            retry_times=1,
        )
        session = FakeSession(
            post_results=[
                FakeResponse(
                    json_data={
                        "success": False,
                        "message": (
                            "cookie=session=COOKIE-SECRET; auth=COOKIE-TWO "
                            "token=TOKEN-SECRET uid=UID-SECRET "
                            "credential=ACCESS-SECRET "
                            "Authorization: Bearer BEARER-SECRET"
                        ),
                    }
                )
            ]
        )

        with self.assertRaises(self.module.VuePillSiteClientError) as raised:
            client.post_action(
                session,
                "gift_item",
                payload={
                    "token": "TOKEN-SECRET",
                    "uid": "UID-SECRET",
                    "access_token": "ACCESS-SECRET",
                },
            )

        combined = "\n".join([str(raised.exception), *logger.messages])
        for secret in (
            "COOKIE-SECRET",
            "COOKIE-TWO",
            "TOKEN-SECRET",
            "UID-SECRET",
            "ACCESS-SECRET",
            "BEARER-SECRET",
        ):
            self.assertNotIn(secret, combined)
        self.assertIn("[REDACTED]", combined)

    def test_http_error_prefers_site_msg_but_redacts_it(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            post_results=[
                FakeResponse(
                    status_code=403,
                    json_data={"msg": "token=TOKEN-SECRET denied"},
                    reason="Forbidden",
                )
            ]
        )

        with self.assertRaises(self.module.VuePillSiteClientError) as raised:
            client.post_action(session, "sync_game_state", retry_network=True)

        self.assertIn("denied", str(raised.exception))
        self.assertNotIn("TOKEN-SECRET", str(raised.exception))
        self.assertEqual(1, len(session.post_calls))

    def test_invalid_configuration_values_are_safely_normalized(self):
        client, _ = self.make_client(
            site_url="  https://example.test///  ",
            cookie=None,
            user_agent=None,
            timeout="not-a-number",
            retry_times="99",
            retry_delay_ms=-100,
            use_proxy="off",
            force_ipv4="no",
        )
        minimum_client, _ = self.make_client(
            timeout=0,
            retry_times=0,
            retry_delay_ms="invalid",
            use_proxy="yes",
            force_ipv4="1",
        )
        unknown_client, _ = self.make_client(
            timeout=float("nan"),
            use_proxy="unexpected",
            force_ipv4="unexpected",
        )

        self.assertEqual("https://example.test", client.site_url)
        self.assertEqual("", client.cookie)
        self.assertEqual("", client.user_agent)
        self.assertEqual(10.0, client.timeout)
        self.assertEqual(5, client.retry_times)
        self.assertEqual(0, client.retry_delay_ms)
        self.assertIs(client.use_proxy, False)
        self.assertIs(client.force_ipv4, False)
        self.assertEqual(10.0, minimum_client.timeout)
        self.assertEqual(1, minimum_client.retry_times)
        self.assertEqual(0, minimum_client.retry_delay_ms)
        self.assertIs(minimum_client.use_proxy, True)
        self.assertIs(minimum_client.force_ipv4, True)
        self.assertEqual(10.0, unknown_client.timeout)
        self.assertIs(unknown_client.use_proxy, False)
        self.assertIs(unknown_client.force_ipv4, False)


if __name__ == "__main__":
    unittest.main()
