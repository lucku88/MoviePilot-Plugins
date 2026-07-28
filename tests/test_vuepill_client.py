import importlib.util
import socket
import sys
import types
import unittest
from collections import UserDict
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

    class SSLError(RequestsConnectionError):
        pass

    exceptions_module.RequestException = RequestException
    exceptions_module.Timeout = Timeout
    exceptions_module.ConnectionError = RequestsConnectionError
    exceptions_module.SSLError = SSLError
    requests_module.exceptions = exceptions_module
    sys.modules["requests.exceptions"] = exceptions_module

    adapters_module = types.ModuleType("requests.adapters")

    class HTTPAdapter:
        def __init__(
            self,
            max_retries=0,
            pool_connections=10,
            pool_maxsize=10,
            pool_block=False,
            **kwargs,
        ):
            if hasattr(max_retries, "total"):
                self.max_retries = max_retries
            else:
                self.max_retries = types.SimpleNamespace(total=max_retries)
            self.kwargs = kwargs
            self.proxy_manager = {}
            self.init_poolmanager(
                pool_connections,
                pool_maxsize,
                block=pool_block,
            )

        def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
            self.poolmanager = types.SimpleNamespace(
                connections=connections,
                maxsize=maxsize,
                block=block,
                connection_pool_kw=dict(pool_kwargs),
            )

        def proxy_manager_for(self, proxy, **proxy_kwargs):
            manager = types.SimpleNamespace(
                proxy=proxy,
                proxy_kwargs=dict(proxy_kwargs),
            )
            self.proxy_manager[proxy] = manager
            return manager

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
        url="https://example.test/mowan.php",
    ):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self._json_error = json_error
        self.reason = reason
        self.url = url
        self.json_calls = 0

    def json(self):
        self.json_calls += 1
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
            "logger": logger,
        }
        values.update(overrides)
        return self.module.VuePillSiteClient(**values), logger

    def assert_exception_is_fully_redacted(self, error, *secrets):
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        text = str(error)
        for secret in secrets:
            self.assertNotIn(secret, text)

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

    def test_post_disables_redirects_and_rejects_307_308(self):
        client, _ = self.make_client(retry_times=5)

        for status_code in (307, 308):
            with self.subTest(status_code=status_code):
                redirect = FakeResponse(
                    status_code=status_code,
                    json_data={"message": "redirect refused"},
                    reason="Temporary Redirect",
                )
                session = FakeSession(
                    post_results=[
                        redirect,
                        FakeResponse(json_data={"success": True}),
                    ]
                )
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    f"HTTP {status_code}",
                ):
                    client.post_action(
                        session,
                        "gift_item",
                        payload={"item_name": "stone"},
                        retry_network=True,
                    )
                self.assertEqual(1, len(session.post_calls))
                _, kwargs = session.post_calls[0]
                self.assertIs(kwargs["allow_redirects"], False)
                self.assertEqual(1, redirect.json_calls)

    def test_get_disables_redirects_and_rejects_3xx(self):
        client, _ = self.make_client(retry_times=5)
        redirect = FakeResponse(
            status_code=302,
            json_data={"message": "login redirect"},
            reason="Found",
            url="https://example.test/login.php",
        )
        session = FakeSession(
            get_results=[redirect, FakeResponse(text="<html>game</html>")]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "HTTP 302",
        ):
            client.fetch_page_html(session)

        self.assertEqual(1, len(session.get_calls))
        _, kwargs = session.get_calls[0]
        self.assertIs(kwargs["allow_redirects"], False)
        self.assertEqual(1, redirect.json_calls)

    def test_http_status_must_be_plain_integer_from_100_to_599(self):
        client, _ = self.make_client(retry_times=5)
        invalid_statuses = (True, False, 99, 600, "200", None)

        for status_code in invalid_statuses:
            with self.subTest(status_code=status_code):
                response = FakeResponse(
                    status_code=status_code,
                    json_data={"success": True},
                )
                session = FakeSession(post_results=[response])
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    "status",
                ):
                    client.post_action(session, "sync_game_state")
                self.assertEqual(1, len(session.post_calls))
                self.assertEqual(0, response.json_calls)

    def test_all_non_2xx_statuses_fail_before_success_parsing(self):
        client, _ = self.make_client(retry_times=1)

        for status_code in (100, 199, 300, 399, 400, 499, 501, 505):
            with self.subTest(status_code=status_code):
                response = FakeResponse(
                    status_code=status_code,
                    json_data={"success": True, "message": "not successful"},
                )
                session = FakeSession(post_results=[response])
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    f"HTTP {status_code}",
                ):
                    client.post_action(session, "sync_game_state")
                self.assertEqual(1, response.json_calls)

    def test_each_post_response_json_is_read_only_once(self):
        client, _ = self.make_client(retry_times=2)
        busy = FakeResponse(
            status_code=503,
            json_data={"message": "busy"},
        )
        success = FakeResponse(json_data={"success": True})
        session = FakeSession(post_results=[busy, success])

        with mock.patch.object(self.module.time, "sleep"):
            result = client.post_action(
                session,
                "sync_game_state",
                retry_network=True,
            )

        self.assertIs(result["success"], True)
        self.assertEqual(1, busy.json_calls)
        self.assertEqual(1, success.json_calls)

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

    def test_success_field_must_exist_and_be_plain_bool(self):
        client, _ = self.make_client(retry_times=5)
        invalid_results = (
            {},
            {"success": 0},
            {"success": 1},
            {"success": None},
            {"success": "false"},
            {"success": "true"},
        )

        for result in invalid_results:
            with self.subTest(result=result):
                response = FakeResponse(json_data=result)
                session = FakeSession(
                    post_results=[
                        response,
                        FakeResponse(json_data={"success": True}),
                    ]
                )
                with self.assertRaisesRegex(
                    self.module.VuePillResponseError,
                    "success",
                ):
                    client.post_action(
                        session,
                        "sync_game_state",
                        retry_network=True,
                    )
                self.assertEqual(1, len(session.post_calls))
                self.assertEqual(1, response.json_calls)

    def test_retry_status_matrix_allows_all_5xx(self):
        client, _ = self.make_client(retry_times=2)

        for status_code in (500, 501, 502, 503, 504, 505, 599):
            with self.subTest(status_code=status_code, retryable=True):
                session = FakeSession(
                    post_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "retry"},
                        ),
                        FakeResponse(json_data={"success": True}),
                    ]
                )
                with mock.patch.object(self.module.time, "sleep"):
                    result = client.post_action(
                        session,
                        "sync_game_state",
                        retry_network=True,
                    )
                self.assertIs(result["success"], True)
                self.assertEqual(2, len(session.post_calls))

        for status_code in (307, 308, 400, 429, 499):
            with self.subTest(status_code=status_code, retryable=False):
                session = FakeSession(
                    post_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "do not retry"},
                        ),
                        FakeResponse(json_data={"success": True}),
                    ]
                )
                with self.assertRaises(self.module.VuePillSiteClientError):
                    client.post_action(
                        session,
                        "sync_game_state",
                        retry_network=True,
                    )
                self.assertEqual(1, len(session.post_calls))

    def test_get_retry_status_matrix_allows_all_5xx(self):
        client, _ = self.make_client(retry_times=2)

        for status_code in (500, 501, 502, 503, 504, 505, 599):
            with self.subTest(status_code=status_code, retryable=True):
                session = FakeSession(
                    get_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "retry"},
                        ),
                        FakeResponse(text="<html>game</html>"),
                    ]
                )
                with mock.patch.object(self.module.time, "sleep"):
                    result = client.fetch_page_html(session)
                self.assertEqual("<html>game</html>", result)
                self.assertEqual(2, len(session.get_calls))

        for status_code in (307, 308, 400, 429, 499):
            with self.subTest(status_code=status_code, retryable=False):
                session = FakeSession(
                    get_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "do not retry"},
                        ),
                        FakeResponse(text="<html>game</html>"),
                    ]
                )
                with self.assertRaises(self.module.VuePillSiteClientError):
                    client.fetch_page_html(session)
                self.assertEqual(1, len(session.get_calls))

    def test_safe_post_retries_501_505_599_up_to_retry_times(self):
        client, _ = self.make_client(retry_times=3)

        for status_code in (501, 505, 599):
            with self.subTest(status_code=status_code):
                session = FakeSession(
                    post_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "retry"},
                        )
                        for _ in range(3)
                    ]
                )
                with self.assertRaises(self.module.VuePillRequestError):
                    client.post_action(
                        session,
                        "sync_game_state",
                        retry_network=True,
                    )
                self.assertEqual(3, len(session.post_calls))

    def test_get_retries_501_505_599_up_to_retry_times(self):
        client, _ = self.make_client(retry_times=3)

        for status_code in (501, 505, 599):
            with self.subTest(status_code=status_code):
                session = FakeSession(
                    get_results=[
                        FakeResponse(
                            status_code=status_code,
                            json_data={"message": "retry"},
                        )
                        for _ in range(3)
                    ]
                )
                with self.assertRaises(self.module.VuePillRequestError):
                    client.fetch_page_html(session)
                self.assertEqual(3, len(session.get_calls))

    def test_unsafe_post_actions_do_not_retry_retryable_http_status(self):
        client, _ = self.make_client(retry_times=5)

        for status_code in (500, 501, 505, 599):
            for action in (
                "enter_beach",
                "collect_all_trash",
                "craft_item",
                "exchange_points",
                "gift_item",
                "gift_stats",
            ):
                with self.subTest(action=action, status_code=status_code):
                    session = FakeSession(
                        post_results=[
                            FakeResponse(
                                status_code=status_code,
                                json_data={"message": "retryable status"},
                            ),
                            FakeResponse(json_data={"success": True}),
                        ]
                    )
                    with self.assertRaises(self.module.VuePillRequestError):
                        client.post_action(
                            session,
                            action,
                            retry_network=True,
                        )
                    self.assertEqual(1, len(session.post_calls))

    def test_ssl_and_non_network_runtime_errors_do_not_retry(self):
        client, _ = self.make_client(retry_times=5)
        errors = (
            self.module.requests.exceptions.SSLError(
                "certificate verify failed token=SSL-SECRET"
            ),
            RuntimeError("temporarily unavailable token=RUNTIME-SECRET"),
        )

        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                logger = CapturingLogger()
                client, _ = self.make_client(
                    retry_times=5,
                    logger=logger,
                )
                session = FailingSession(error)
                with self.assertRaises(self.module.VuePillSiteClientError) as raised:
                    client.post_action(
                        session,
                        "sync_game_state",
                        retry_network=True,
                    )
                self.assertEqual(1, len(session.post_calls))
                self.assert_exception_is_fully_redacted(
                    raised.exception,
                    "SSL-SECRET",
                    "RUNTIME-SECRET",
                )
                combined = "\n".join(logger.messages)
                self.assertNotIn("SSL-SECRET", combined)
                self.assertNotIn("RUNTIME-SECRET", combined)

    def test_nested_ssl_error_never_retries_even_with_retryable_status(self):
        client, _ = self.make_client(retry_times=5)
        ssl_error = self.module.requests.exceptions.SSLError(
            "certificate verify failed token=NESTED-SSL-SECRET"
        )
        outer = self.module.VuePillRequestError(
            "request wrapper",
            status_code=503,
        )
        outer.__cause__ = ssl_error
        session = FailingSession(outer)

        with self.assertRaises(self.module.VuePillRequestError) as raised:
            client.post_action(
                session,
                "sync_game_state",
                retry_network=True,
            )

        self.assertEqual(1, len(session.post_calls))
        self.assert_exception_is_fully_redacted(
            raised.exception,
            "NESTED-SSL-SECRET",
        )

    def test_hostile_network_error_attributes_cannot_escape_or_leak(self):
        status_secret = "HOSTILE-STATUS-SECRET"
        errno_secret = "HOSTILE-ERRNO-SECRET"

        class ExplodingHash:
            def __hash__(self):
                raise RuntimeError(f"token={errno_secret}")

        class HostileRequestError(self.module.VuePillRequestError):
            def __init__(self):
                Exception.__init__(self, "hostile request wrapper")

            @property
            def status_code(self):
                raise RuntimeError(f"token={status_secret}")

            @property
            def errno(self):
                return ExplodingHash()

        client, logger = self.make_client(retry_times=5)
        session = FailingSession(HostileRequestError())

        with self.assertRaises(self.module.VuePillRequestError) as raised:
            client.post_action(
                session,
                "sync_game_state",
                retry_network=True,
            )

        self.assertEqual(1, len(session.post_calls))
        self.assert_exception_is_fully_redacted(
            raised.exception,
            status_secret,
            errno_secret,
        )
        combined = "\n".join(logger.messages)
        self.assertNotIn(status_secret, combined)
        self.assertNotIn(errno_secret, combined)

    def test_nested_timeout_chain_retries_but_outward_error_has_no_raw_chain(self):
        cookie_secret = "COOKIE-CHAIN-SECRET"
        token_secret = "TOKEN-CHAIN-SECRET"
        uid_secret = "UID-CHAIN-SECRET"
        logger = CapturingLogger()
        client, _ = self.make_client(
            cookie=f"session={cookie_secret}",
            retry_times=3,
            logger=logger,
        )
        timeout = TimeoutError(
            f"timeout token={token_secret} uid={uid_secret} {cookie_secret}"
        )
        middle = RuntimeError("middle wrapper")
        middle.__cause__ = timeout
        outer = RuntimeError("outer wrapper")
        outer.__context__ = middle
        session = FailingSession(outer)

        with self.assertRaises(self.module.VuePillRequestError) as raised:
            client.post_action(
                session,
                "sync_game_state",
                retry_network=True,
            )

        self.assertEqual(3, len(session.post_calls))
        self.assert_exception_is_fully_redacted(
            raised.exception,
            cookie_secret,
            token_secret,
            uid_secret,
        )
        combined = "\n".join(logger.messages)
        for secret in (cookie_secret, token_secret, uid_secret):
            self.assertNotIn(secret, combined)

    def test_request_error_without_status_retries_nested_timeout(self):
        client, _ = self.make_client(retry_times=3)

        def wrapped_timeout():
            timeout = TimeoutError("timeout token=WRAPPED-TOKEN uid=WRAPPED-UID")
            outer = self.module.VuePillRequestError("request wrapper")
            outer.__cause__ = timeout
            return outer

        session = FakeSession(
            post_results=[
                wrapped_timeout(),
                wrapped_timeout(),
                FakeResponse(json_data={"success": True}),
            ]
        )

        result = client.post_action(
            session,
            "sync_game_state",
            retry_network=True,
        )

        self.assertIs(result["success"], True)
        self.assertEqual(3, len(session.post_calls))

    def test_non_json_error_does_not_survive_in_exception_context(self):
        json_secret = "JSON-TOKEN-SECRET"
        logger = CapturingLogger()
        client, _ = self.make_client(logger=logger)
        response = FakeResponse(
            json_error=ValueError(f"invalid json token={json_secret}"),
        )
        session = FakeSession(post_results=[response])

        with self.assertRaises(self.module.VuePillResponseError) as raised:
            client.post_action(session, "sync_game_state")

        self.assert_exception_is_fully_redacted(raised.exception, json_secret)
        self.assertNotIn(json_secret, "\n".join(logger.messages))

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

        class ActionSubclass(str):
            pass

        for action in (
            "reset_game",
            "update_settings",
            "unknown_action",
            " move_brick ",
            ActionSubclass("move_brick"),
        ):
            with self.subTest(action=action):
                session = FakeSession()
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    "not allowed",
                ):
                    client.post_action(session, action)
                self.assertEqual(0, len(session.post_calls))

    def test_payload_action_key_is_rejected_without_request(self):
        client, _ = self.make_client()
        for key in ("action", "Action", " action "):
            with self.subTest(key=key):
                session = FakeSession()
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    "payload",
                ):
                    client.post_action(
                        session,
                        "move_brick",
                        payload={key: "reset_game"},
                    )
                self.assertEqual([], session.post_calls)

    def test_payload_requires_exact_dict_and_plain_string_keys(self):
        client, _ = self.make_client()

        class DictSubclass(dict):
            pass

        class StringSubclass(str):
            pass

        invalid_payloads = (
            UserDict({}),
            DictSubclass(),
            {b"quantity": 1},
            {1: "value"},
            {StringSubclass("quantity"): 1},
        )
        for payload in invalid_payloads:
            with self.subTest(payload_type=type(payload).__name__):
                session = FakeSession()
                with self.assertRaises(self.module.VuePillSiteClientError):
                    client.post_action(session, "exchange_points", payload=payload)
                self.assertEqual([], session.post_calls)

    def test_each_action_accepts_only_its_known_payload_fields(self):
        valid_payloads = {
            "sync_game_state": {},
            "move_brick": {},
            "enter_beach": {},
            "collect_all_trash": {},
            "craft_item": {"recipe_id": 1, "quantity": 2},
            "exchange_points": {"quantity": 3},
            "gift_item": {
                "item_name": "stone",
                "target_uid": "1001",
                "uid": 1001,
                "recipient_uid": "1002",
                "quantity": 1,
            },
            "gift_stats": {"direction": "sent", "range": "week"},
        }
        client, _ = self.make_client()

        for action, payload in valid_payloads.items():
            with self.subTest(action=action):
                session = FakeSession(
                    post_results=[FakeResponse(json_data={"success": True})]
                )
                result = client.post_action(session, action, payload=payload)
                self.assertIs(result["success"], True)
                _, kwargs = session.post_calls[0]
                self.assertEqual({"action": action, **payload}, kwargs["data"])

        for action in valid_payloads:
            with self.subTest(action=action, field="unexpected"):
                session = FakeSession()
                with self.assertRaisesRegex(
                    self.module.VuePillSiteClientError,
                    "unsupported",
                ):
                    client.post_action(
                        session,
                        action,
                        payload={"unexpected": "value"},
                    )
                self.assertEqual([], session.post_calls)

    def test_payload_values_require_exact_safe_scalar_types(self):
        client, logger = self.make_client()
        safe_values = ("1001", 1001, 1.5, True)

        for value in safe_values:
            with self.subTest(safe_type=type(value).__name__):
                session = FakeSession(
                    post_results=[FakeResponse(json_data={"success": True})]
                )
                client.post_action(
                    session,
                    "gift_item",
                    payload={"target_uid": value},
                )
                _, kwargs = session.post_calls[0]
                self.assertIs(kwargs["data"]["target_uid"], value)

        class StringSubclass(str):
            pass

        class IntSubclass(int):
            pass

        class ExplodingValue:
            def __str__(self):
                raise RuntimeError("VALUE-SECRET")

        invalid_values = (
            None,
            b"1001",
            bytearray(b"1001"),
            [1001],
            (1001,),
            {"uid": 1001},
            float("nan"),
            float("inf"),
            StringSubclass("1001"),
            IntSubclass(1001),
            ExplodingValue(),
        )
        for value in invalid_values:
            with self.subTest(value_type=type(value).__name__):
                session = FakeSession()
                with self.assertRaises(self.module.VuePillSiteClientError) as raised:
                    client.post_action(
                        session,
                        "gift_item",
                        payload={"target_uid": value},
                    )
                self.assertEqual([], session.post_calls)
                combined = "\n".join([str(raised.exception), *logger.messages])
                self.assertNotIn("VALUE-SECRET", combined)
                self.assertIsNone(raised.exception.__cause__)
                self.assertIsNone(raised.exception.__context__)

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

    def test_build_session_uses_standard_adapters_without_source_address(self):
        client, _ = self.make_client()

        session = client.build_session()
        self.addCleanup(session.close)

        for prefix in ("http://", "https://"):
            adapter = session.adapters[prefix]
            self.assertIs(type(adapter), self.module.HTTPAdapter)
            self.assertNotIn(
                "source_address",
                adapter.poolmanager.connection_pool_kw,
            )
            self.assertEqual(0, adapter.max_retries.total)

    def test_build_session_does_not_change_global_address_family_selection(self):
        client, _ = self.make_client()
        sentinel = lambda: socket.AF_UNSPEC
        connection_module = sys.modules["urllib3.util.connection"]

        with mock.patch.object(
            connection_module,
            "allowed_gai_family",
            sentinel,
        ):
            session = client.build_session()
            second_session = client.build_session()
            self.addCleanup(session.close)
            self.addCleanup(second_session.close)

            self.assertIs(sentinel, connection_module.allowed_gai_family)

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

    def test_unquoted_login_form_action_is_rejected(self):
        client, _ = self.make_client()
        session = FakeSession(
            get_results=[
                FakeResponse(
                    text="<form action=/login.php><input type=password></form>"
                )
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "login",
        ):
            client.fetch_page_html(session)

    def test_login_url_is_rejected_even_without_password_input(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            get_results=[
                FakeResponse(
                    text="<html>Please sign in</html>",
                    url="https://example.test/login.php",
                ),
                FakeResponse(text="<html>game</html>"),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "login",
        ):
            client.fetch_page_html(session)

        self.assertEqual(1, len(session.get_calls))

    def test_login_url_cannot_be_overridden_by_game_markers(self):
        client, _ = self.make_client(retry_times=5)
        session = FakeSession(
            get_results=[
                FakeResponse(
                    text=(
                        '<span id="dailyBricks">1</span>'
                        '<div id="brickFactory"></div>'
                    ),
                    url="https://example.test/login.php",
                ),
                FakeResponse(text="<html>game</html>"),
            ]
        )

        with self.assertRaisesRegex(
            self.module.VuePillSiteClientError,
            "login",
        ):
            client.fetch_page_html(session)

        self.assertEqual(1, len(session.get_calls))

    def test_password_change_form_is_not_mistaken_for_login(self):
        client, _ = self.make_client()
        expected = (
            '<form action="/account/change-password">'
            '<input type="password" name="new_password">'
            '<button>Change password</button></form>'
        )
        session = FakeSession(get_results=[FakeResponse(text=expected)])

        html = client.fetch_page_html(session)

        self.assertEqual(expected, html)

    def test_game_markers_override_unrelated_password_form(self):
        client, _ = self.make_client()
        expected = (
            '<span id="dailyBricks">1</span>'
            '<div id="brickFactory"></div>'
            '<form action="/account/change-password">'
            '<input type="password"></form>'
        )
        session = FakeSession(get_results=[FakeResponse(text=expected)])

        html = client.fetch_page_html(session)

        self.assertEqual(expected, html)

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
                            "access_token=ACCESS-SECRET "
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
                    "uid": "UID-SECRET",
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
            site_url="  https://example.test/  ",
            cookie=None,
            user_agent=None,
            timeout="not-a-number",
            retry_times="99",
            retry_delay_ms=-100,
            use_proxy="off",
        )
        minimum_client, _ = self.make_client(
            timeout=0,
            retry_times=0,
            retry_delay_ms="invalid",
            use_proxy="yes",
        )
        unknown_client, _ = self.make_client(
            timeout=float("nan"),
            use_proxy="unexpected",
        )

        self.assertEqual("https://example.test", client.site_url)
        self.assertEqual("", client.cookie)
        self.assertEqual("", client.user_agent)
        self.assertEqual(10.0, client.timeout)
        self.assertEqual(5, client.retry_times)
        self.assertEqual(0, client.retry_delay_ms)
        self.assertIs(client.use_proxy, False)
        self.assertEqual(10.0, minimum_client.timeout)
        self.assertEqual(1, minimum_client.retry_times)
        self.assertEqual(0, minimum_client.retry_delay_ms)
        self.assertIs(minimum_client.use_proxy, True)
        self.assertEqual(10.0, unknown_client.timeout)
        self.assertIs(unknown_client.use_proxy, False)

    def test_site_url_accepts_only_http_https_origin(self):
        for site_url, expected in (
            ("http://example.test", "http://example.test"),
            ("https://example.test/", "https://example.test"),
            ("https://example.test:8443/", "https://example.test:8443"),
        ):
            with self.subTest(site_url=site_url):
                client, _ = self.make_client(site_url=site_url)
                self.assertEqual(expected, client.site_url)

        class ExplodingURL:
            def __str__(self):
                raise RuntimeError("URL-SECRET")

        invalid_urls = (
            None,
            b"https://example.test",
            ExplodingURL(),
            "\x00https://example.test",
            "example.test",
            "ftp://example.test",
            "https://user:URL-SECRET@example.test",
            "https://example.test/path",
            "https://example.test//",
            "https://example.test?",
            "https://example.test?token=URL-SECRET",
            "https://example.test#",
            "https://example.test#fragment",
            "https://example.test\x7f",
            "https:///missing-host",
            "https://example.test:bad-port",
            "https://example.test:/",
        )
        for site_url in invalid_urls:
            with self.subTest(site_url_type=type(site_url).__name__):
                with self.assertRaises(self.module.VuePillConfigurationError) as raised:
                    self.make_client(site_url=site_url)
                self.assert_exception_is_fully_redacted(
                    raised.exception,
                    "URL-SECRET",
                )

    def test_numeric_and_boolean_normalization_rejects_weird_values(self):
        client, _ = self.make_client(
            timeout=True,
            retry_times=3.5,
            retry_delay_ms=1.5,
            use_proxy=2,
        )
        valid_numeric_client, _ = self.make_client(
            timeout="1.5",
            retry_times=4.0,
            retry_delay_ms="25",
            use_proxy=1,
        )

        self.assertEqual(10.0, client.timeout)
        self.assertEqual(1, client.retry_times)
        self.assertEqual(0, client.retry_delay_ms)
        self.assertIs(client.use_proxy, False)
        self.assertEqual(1.5, valid_numeric_client.timeout)
        self.assertEqual(4, valid_numeric_client.retry_times)
        self.assertEqual(25, valid_numeric_client.retry_delay_ms)
        self.assertIs(valid_numeric_client.use_proxy, True)


if __name__ == "__main__":
    unittest.main()
