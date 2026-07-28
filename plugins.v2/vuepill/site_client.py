"""Standalone HTTP client for VuePill website requests."""

import errno
import math
import re
import socket
import ssl
import time
from typing import Any, Callable, Iterable, Optional
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter


class VuePillSiteClientError(Exception):
    """Base error raised by the VuePill website client."""


class VuePillConfigurationError(VuePillSiteClientError):
    """Raised when the client receives an unusable configuration value."""


class VuePillRequestError(VuePillSiteClientError):
    """Raised when a website request fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class VuePillResponseError(VuePillSiteClientError):
    """Raised when the website response cannot be safely consumed."""


class VuePillActionError(VuePillSiteClientError):
    """Raised when an action is disallowed or rejected by the website."""


class _NullLogger:
    def warning(self, *args: Any, **kwargs: Any) -> None:
        return None

    def info(self, *args: Any, **kwargs: Any) -> None:
        return None

    def error(self, *args: Any, **kwargs: Any) -> None:
        return None


class _IPv4HTTPAdapter(HTTPAdapter):
    SOURCE_ADDRESS = ("0.0.0.0", 0)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["source_address"] = self.SOURCE_ADDRESS
        return super().init_poolmanager(
            connections,
            maxsize,
            block=block,
            **pool_kwargs,
        )

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        proxy_kwargs["source_address"] = self.SOURCE_ADDRESS
        return super().proxy_manager_for(proxy, **proxy_kwargs)


class _ErrorSnapshot:
    __slots__ = ("category", "type_name", "status_code", "retryable", "text")

    def __init__(self, category, type_name, status_code, retryable, text):
        self.category = category
        self.type_name = type_name
        self.status_code = status_code
        self.retryable = retryable
        self.text = text


class VuePillSiteClient:
    ALLOWED_ACTIONS = frozenset(
        {
            "sync_game_state",
            "move_brick",
            "enter_beach",
            "collect_all_trash",
            "craft_item",
            "exchange_points",
            "gift_item",
            "gift_stats",
        }
    )
    NETWORK_RETRY_ACTIONS = frozenset({"sync_game_state", "move_brick"})
    ACTION_PAYLOAD_FIELDS = {
        "sync_game_state": frozenset(),
        "move_brick": frozenset(),
        "enter_beach": frozenset(),
        "collect_all_trash": frozenset(),
        "craft_item": frozenset({"recipe_id", "quantity"}),
        "exchange_points": frozenset({"quantity"}),
        "gift_item": frozenset(
            {
                "item_name",
                "target_uid",
                "uid",
                "recipient_uid",
                "quantity",
            }
        ),
        "gift_stats": frozenset({"direction", "range"}),
    }
    MAX_REQUEST_TIMES = 5
    DEFAULT_TIMEOUT = 10.0
    RETRYABLE_HTTP_STATUSES = frozenset({500, 502, 503, 504})

    _RETRYABLE_ERRNOS = frozenset(
        value
        for value in (
            getattr(errno, "ECONNRESET", None),
            getattr(errno, "ECONNABORTED", None),
            getattr(errno, "ECONNREFUSED", None),
            getattr(errno, "ETIMEDOUT", None),
            getattr(errno, "EHOSTUNREACH", None),
            getattr(errno, "ENETUNREACH", None),
            getattr(errno, "EPIPE", None),
            getattr(socket, "EAI_AGAIN", None),
            10051,
            10053,
            10054,
            10060,
            10061,
            10065,
        )
        if value is not None
    )
    _RETRYABLE_CODES = frozenset(
        {
            "ETIMEDOUT",
            "ECONNRESET",
            "ECONNABORTED",
            "EAI_AGAIN",
            "ENOTFOUND",
            "EHOSTUNREACH",
            "ENETUNREACH",
            "ECONNREFUSED",
            "EPIPE",
        }
    )
    _SENSITIVE_KEYS = frozenset(
        {
            "access_token",
            "api_key",
            "apikey",
            "auth",
            "auth_token",
            "authorization",
            "cookie",
            "csrf_token",
            "id_token",
            "jwt",
            "password",
            "refresh_token",
            "recipient_uid",
            "session",
            "session_id",
            "sessionid",
            "sid",
            "token",
            "target_uid",
            "uid",
            "user_id",
            "userid",
            "xsrf_token",
        }
    )
    _BEARER_PATTERN = re.compile(
        r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+"
    )
    _HEADER_PATTERN = re.compile(
        r"(?im)(\b(?:cookie|set-cookie|authorization|proxy-authorization)\s*:\s*)[^\r\n]+"
    )
    _KEY_VALUE_PATTERN = re.compile(
        r"(?ix)"
        r"(?P<prefix>[\"']?"
        r"(?:api[_-]?key|auth(?:orization)?|cookie|jwt|password|"
        r"(?:access|auth|csrf|id|refresh|xsrf)[_-]?token|"
        r"session(?:[_-]?id)?|sid|token|uid|user[_-]?id)"
        r"[\"']?\s*(?:=|:)\s*)"
        r"(?:[\"'][^\"']*[\"']|[^&,\s]+)"
    )
    _UID_SPACE_PATTERN = re.compile(
        r"(?i)(\b(?:uid|user[_-]?id)\b\s+)[A-Za-z0-9._-]+"
    )
    _LOGIN_TEXT_MARKERS = (
        "please log in",
        "please login",
        "sign in to continue",
        "\u8bf7\u5148\u767b\u5f55",
        "\u8bf7\u767b\u5f55\u540e",
        "\u672a\u767b\u5f55",
    )
    _GAME_PAGE_MARKERS = (
        'id="dailybricks"',
        "id='dailybricks'",
        'id="brickfactory"',
        "id='brickfactory'",
        'id="inventorygrid"',
        "id='inventorygrid'",
        'id="magicpills"',
        "id='magicpills'",
        'id="beacharea"',
        "id='beacharea'",
    )
    _PASSWORD_INPUT_PATTERN = re.compile(
        r"<input\b[^>]*\btype\s*=\s*([\"']?)password\1",
        re.IGNORECASE,
    )
    _LOGIN_FORM_PATTERN = re.compile(
        r"<form\b[^>]*\baction\s*=\s*(?:"
        r"[\"'][^\"']*(?:login|signin)[^\"']*[\"']|"
        r"[^\s>]*(?:login|signin)[^\s>]*)",
        re.IGNORECASE,
    )
    _INTEGER_TEXT_PATTERN = re.compile(r"^[+-]?\d+$")
    _FLOAT_TEXT_PATTERN = re.compile(
        r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$"
    )

    def __init__(
        self,
        site_url,
        cookie,
        user_agent,
        timeout,
        retry_times,
        retry_delay_ms,
        use_proxy,
        force_ipv4,
        logger,
    ):
        self.site_url = self._normalize_site_url(site_url)
        self.cookie = cookie if type(cookie) is str else ""
        self.user_agent = user_agent if type(user_agent) is str else ""
        self.timeout = self._normalize_positive_float(
            timeout,
            default=self.DEFAULT_TIMEOUT,
        )
        self.retry_times = self._normalize_int(
            retry_times,
            default=1,
            minimum=1,
            maximum=self.MAX_REQUEST_TIMES,
        )
        self.retry_delay_ms = self._normalize_int(
            retry_delay_ms,
            default=0,
            minimum=0,
        )
        self.use_proxy = self._normalize_bool(use_proxy)
        self.force_ipv4 = self._normalize_bool(force_ipv4)
        self.logger = logger or _NullLogger()
        self._cookie_secrets = self._extract_cookie_secrets(self.cookie)

    def build_session(self):
        session = requests.Session()
        adapter_class = _IPv4HTTPAdapter if self.force_ipv4 else HTTPAdapter
        adapter = adapter_class(
            max_retries=0,
            pool_connections=10,
            pool_maxsize=10,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.trust_env = self.use_proxy
        session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Cookie": self.cookie,
                "Referer": self._page_url,
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
            }
        )
        return session

    def fetch_page_html(self, session):
        def do_request():
            response = session.get(
                self._page_url,
                params={"_": int(time.time() * 1000)},
                headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
                timeout=self._request_timeout,
                allow_redirects=False,
            )
            self._raise_for_http_error(response, "fetch_page_html")
            html = getattr(response, "text", None)
            if not isinstance(html, str) or not html.strip():
                raise VuePillResponseError("fetch_page_html returned an empty response")
            response_url = self._safe_response_attribute(response, "url")
            if self._looks_like_login_page(html, response_url):
                raise VuePillResponseError(
                    "fetch_page_html returned an obvious login page"
                )
            return html

        return self._request_with_retry(
            operation="fetch_page_html",
            total_attempts=self.retry_times,
            request_func=do_request,
        )

    def post_action(
        self,
        session,
        action,
        payload=None,
        retry_network=False,
    ):
        action_name = action if type(action) is str else ""
        if action_name not in self.ALLOWED_ACTIONS:
            raise VuePillActionError("Website action is not allowed")
        form, sensitive_values = self._build_action_form(action_name, payload)

        allow_retry = (
            self._normalize_bool(retry_network)
            and action_name in self.NETWORK_RETRY_ACTIONS
        )
        total_attempts = self.retry_times if allow_retry else 1

        def do_request():
            response = session.post(
                self._page_url,
                data=form,
                timeout=self._request_timeout,
                allow_redirects=False,
            )
            self._raise_for_http_error(
                response,
                action_name,
                sensitive_values=sensitive_values,
            )
            json_failed = False
            try:
                result = response.json()
            except Exception:
                json_failed = True
                result = None
            if json_failed:
                raise VuePillResponseError(
                    f"Action {action_name} returned non-JSON data"
                )
            if type(result) is not dict:
                raise VuePillResponseError(
                    f"Action {action_name} did not return a JSON object"
                )
            if "success" not in result or type(result["success"]) is not bool:
                raise VuePillResponseError(
                    f"Action {action_name} returned an invalid success field"
                )
            if result["success"] is False:
                detail = self._site_message(
                    result,
                    default="Website rejected the action",
                    sensitive_values=sensitive_values,
                )
                raise VuePillActionError(f"Action {action_name} failed: {detail}")
            return result

        return self._request_with_retry(
            operation=action_name,
            total_attempts=total_attempts,
            request_func=do_request,
            sensitive_values=sensitive_values,
        )

    def _build_action_form(self, action: str, payload):
        if payload is None:
            payload = {}
        elif type(payload) is not dict:
            raise VuePillConfigurationError("Action payload must be a plain dict")

        allowed_fields = self.ACTION_PAYLOAD_FIELDS[action]
        form = {"action": action}
        sensitive_values = list(self._cookie_secrets)
        for key, value in payload.items():
            if type(key) is not str:
                raise VuePillConfigurationError(
                    "Action payload keys must be plain strings"
                )
            if key.strip().lower() == "action":
                raise VuePillConfigurationError(
                    "Action payload must not contain an action field"
                )
            if key not in allowed_fields:
                raise VuePillConfigurationError(
                    "Action payload contains an unsupported field"
                )
            if not self._is_safe_payload_scalar(value):
                raise VuePillConfigurationError(
                    "Action payload contains an unsafe value"
                )
            form[key] = value
            if self._is_sensitive_key(key):
                sensitive_values.append(self._safe_scalar_text(value))
        return form, tuple(sensitive_values)

    @staticmethod
    def _is_safe_payload_scalar(value: Any) -> bool:
        if type(value) not in {str, int, float, bool}:
            return False
        return type(value) is not float or math.isfinite(value)

    @staticmethod
    def _safe_scalar_text(value: Any) -> str:
        if type(value) is str:
            return value
        if type(value) is bool:
            return "True" if value else "False"
        if type(value) is int:
            return str(value)
        if type(value) is float and math.isfinite(value):
            return repr(value)
        return ""

    @property
    def _page_url(self) -> str:
        return f"{self.site_url}/mowan.php"

    @property
    def _request_timeout(self):
        return self.timeout, self.timeout

    def _request_with_retry(
        self,
        operation: str,
        total_attempts: int,
        request_func: Callable[[], Any],
        sensitive_values: Iterable[str] = (),
    ):
        attempts = self._normalize_int(
            total_attempts,
            default=1,
            minimum=1,
            maximum=self.MAX_REQUEST_TIMES,
        )
        for attempt in range(1, attempts + 1):
            snapshot = None
            try:
                return request_func()
            except Exception as error:
                snapshot = self._snapshot_error(
                    error,
                    operation,
                    sensitive_values,
                )

            self._log_failure(operation, attempt, attempts, snapshot.text)
            if not snapshot.retryable or attempt >= attempts:
                safe_error = self._exception_from_snapshot(snapshot)
                safe_error.__cause__ = None
                safe_error.__context__ = None
                safe_error.__suppress_context__ = True
                raise safe_error
            wait_seconds = (self.retry_delay_ms * attempt) / 1000.0
            if wait_seconds > 0:
                time.sleep(wait_seconds)
        raise VuePillRequestError(f"{operation} request failed")

    def _snapshot_error(
        self,
        error: Exception,
        operation: str,
        sensitive_values: Iterable[str],
    ) -> _ErrorSnapshot:
        if isinstance(error, VuePillConfigurationError):
            category = "configuration"
        elif isinstance(error, VuePillResponseError):
            category = "response"
        elif isinstance(error, VuePillActionError):
            category = "action"
        else:
            category = "request"

        status_code = None
        if isinstance(error, VuePillRequestError):
            status_code = self._valid_status_or_none(
                self._safe_exception_attribute(error, "status_code")
            )
        if status_code is None:
            status_code = self._response_status_code(
                self._safe_exception_attribute(error, "response")
            )

        detail = self._safe_exception_text(error, sensitive_values)
        if not isinstance(error, VuePillSiteClientError):
            detail = f"{operation} request failed: {detail}"
        return _ErrorSnapshot(
            category=category,
            type_name=self._sanitize(type(error).__name__, sensitive_values),
            status_code=status_code,
            retryable=self._is_retryable_network_error(error),
            text=detail,
        )

    @staticmethod
    def _exception_from_snapshot(snapshot: _ErrorSnapshot):
        if snapshot.category == "configuration":
            return VuePillConfigurationError(snapshot.text)
        if snapshot.category == "response":
            return VuePillResponseError(snapshot.text)
        if snapshot.category == "action":
            return VuePillActionError(snapshot.text)
        return VuePillRequestError(snapshot.text, status_code=snapshot.status_code)

    def _raise_for_http_error(
        self,
        response,
        operation: str,
        sensitive_values: Iterable[str] = (),
    ) -> None:
        status_code = self._validated_response_status(response)
        if 200 <= status_code < 300:
            return

        detail = self._response_message(response)
        if not detail:
            reason = self._safe_response_attribute(response, "reason")
            detail = reason if type(reason) is str and reason.strip() else "HTTP error"
        safe_detail = self._sanitize(detail, sensitive_values)
        raise VuePillRequestError(
            f"{operation} request failed (HTTP {status_code}): {safe_detail}",
            status_code=status_code,
        )

    @staticmethod
    def _validated_response_status(response) -> int:
        invalid = False
        try:
            value = getattr(response, "status_code", None)
        except Exception:
            invalid = True
            value = None
        if invalid or type(value) is not int or not 100 <= value <= 599:
            raise VuePillResponseError("Response contains an invalid HTTP status")
        return value

    @staticmethod
    def _valid_status_or_none(value) -> Optional[int]:
        if type(value) is int and 100 <= value <= 599:
            return value
        return None

    @staticmethod
    def _response_status_code(response) -> Optional[int]:
        if response is None:
            return None
        try:
            value = getattr(response, "status_code", None)
            if type(value) is int and 100 <= value <= 599:
                return value
            return None
        except Exception:
            return None

    def _response_message(self, response) -> str:
        json_failed = False
        try:
            data = response.json()
        except Exception:
            json_failed = True
            data = None
        if json_failed or type(data) is not dict:
            return ""
        return self._site_message(data, default="", sensitive_values=())

    def _is_retryable_network_error(self, error: Exception) -> bool:
        if isinstance(
            error,
            (VuePillConfigurationError, VuePillResponseError, VuePillActionError),
        ):
            return False

        chain = tuple(self._iter_exception_chain(error))
        if any(self._is_ssl_error(candidate) for candidate in chain):
            return False

        for candidate in chain:
            status_code = None
            if isinstance(candidate, VuePillRequestError):
                status_code = self._valid_status_or_none(
                    self._safe_exception_attribute(candidate, "status_code")
                )
            if status_code is None:
                status_code = self._response_status_code(
                    self._safe_exception_attribute(candidate, "response")
                )
            if status_code is not None:
                return status_code in self.RETRYABLE_HTTP_STATUSES

        request_timeout = getattr(requests.exceptions, "Timeout", ())
        request_connection = getattr(requests.exceptions, "ConnectionError", ())
        request_exception = getattr(requests.exceptions, "RequestException", ())
        for candidate in chain:
            if isinstance(
                candidate,
                (
                    request_timeout,
                    request_connection,
                    TimeoutError,
                    ConnectionError,
                    ConnectionResetError,
                    ConnectionAbortedError,
                    BrokenPipeError,
                ),
            ):
                return True

            error_number = self._safe_exception_attribute(candidate, "errno")
            if (
                type(error_number) is int
                and error_number in self._RETRYABLE_ERRNOS
            ):
                return True
            for attribute in ("code", "winerror"):
                code = self._safe_exception_attribute(candidate, attribute)
                if type(code) is str and code.upper() in self._RETRYABLE_CODES:
                    return True
                if type(code) is int and code in self._RETRYABLE_ERRNOS:
                    return True
            if isinstance(candidate, (OSError, request_exception)):
                message = self._safe_exception_text(candidate).lower()
                if any(
                    marker in message
                    for marker in (
                        "broken pipe",
                        "connection aborted",
                        "connection refused",
                        "connection reset",
                        "connection timed out",
                        "eai_again",
                        "host unreachable",
                        "name resolution",
                        "network is unreachable",
                        "read timed out",
                        "remote disconnected",
                    )
                ):
                    return True
        return False

    @staticmethod
    def _iter_exception_chain(error: Exception):
        pending = [error]
        seen = set()
        while pending and len(seen) < 32:
            candidate = pending.pop(0)
            identity = id(candidate)
            if identity in seen:
                continue
            seen.add(identity)
            yield candidate
            for attribute in ("__cause__", "__context__"):
                try:
                    nested = getattr(candidate, attribute, None)
                except Exception:
                    nested = None
                if isinstance(nested, BaseException):
                    pending.append(nested)

    @staticmethod
    def _is_ssl_error(error: Exception) -> bool:
        requests_ssl_error = getattr(requests.exceptions, "SSLError", None)
        if requests_ssl_error is not None and isinstance(error, requests_ssl_error):
            return True
        return isinstance(error, (ssl.SSLError, ssl.CertificateError))

    @staticmethod
    def _safe_exception_attribute(error: Exception, attribute: str):
        try:
            return getattr(error, attribute, None)
        except Exception:
            return None

    @staticmethod
    def _safe_response_attribute(response, attribute: str):
        try:
            return getattr(response, attribute, None)
        except Exception:
            return None

    def _log_failure(
        self,
        operation: str,
        attempt: int,
        total_attempts: int,
        detail: str,
    ) -> None:
        try:
            self.logger.warning(
                "action=%s attempt=%s/%s error=%s",
                operation,
                attempt,
                total_attempts,
                detail,
            )
        except Exception:
            return None

    def _safe_exception_text(
        self,
        error: Exception,
        sensitive_values: Iterable[str] = (),
    ) -> str:
        try:
            detail = str(error)
        except Exception:
            detail = type(error).__name__
        if type(detail) is not str or not detail.strip():
            detail = type(error).__name__
        return self._sanitize(detail, sensitive_values)

    def _site_message(
        self,
        data: dict,
        default: str,
        sensitive_values: Iterable[str],
    ) -> str:
        for key in ("message", "msg"):
            value = data.get(key)
            if type(value) is str and value.strip():
                return self._sanitize(value, sensitive_values)
        return default

    def _sanitize(
        self,
        value: Any,
        sensitive_values: Iterable[str] = (),
    ) -> str:
        if type(value) is str:
            text = value
        elif type(value) in {int, float, bool}:
            text = self._safe_scalar_text(value)
        else:
            text = type(value).__name__
        secrets = set(self._cookie_secrets)
        secrets.update(
            secret
            for secret in sensitive_values
            if type(secret) is str and secret
        )
        for secret in sorted(secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = self._HEADER_PATTERN.sub(r"\1[REDACTED]", text)
        text = self._BEARER_PATTERN.sub(r"\1[REDACTED]", text)
        text = self._KEY_VALUE_PATTERN.sub(
            lambda match: f"{match.group('prefix')}[REDACTED]",
            text,
        )
        text = self._UID_SPACE_PATTERN.sub(r"\1[REDACTED]", text)
        return text

    @classmethod
    def _looks_like_login_page(cls, html: str, response_url: Any = "") -> bool:
        lowered = html.lower()
        if type(response_url) is str:
            parse_failed = False
            try:
                path = urlsplit(response_url).path.lower()
            except (TypeError, ValueError):
                parse_failed = True
                path = ""
            if not parse_failed:
                path_parts = {part for part in path.split("/") if part}
                if path_parts.intersection(
                    {"login", "login.php", "signin", "signin.php"}
                ):
                    return True

        if any(marker in lowered for marker in cls._LOGIN_TEXT_MARKERS):
            return True
        game_marker_count = sum(
            marker in lowered for marker in cls._GAME_PAGE_MARKERS
        )
        if game_marker_count >= 2:
            return False
        has_password_input = bool(cls._PASSWORD_INPUT_PATTERN.search(html))
        has_login_form = bool(cls._LOGIN_FORM_PATTERN.search(html))
        return has_password_input and has_login_form

    @classmethod
    def _is_sensitive_key(cls, key: Any) -> bool:
        normalized = cls._to_text(key).strip().lower().replace("-", "_")
        return normalized in cls._SENSITIVE_KEYS

    @staticmethod
    def _extract_cookie_secrets(cookie: str):
        secrets = []
        if cookie:
            secrets.append(cookie)
        for part in cookie.split(";"):
            _, separator, raw_value = part.partition("=")
            if not separator:
                continue
            value = raw_value.strip().strip("\"'")
            if value:
                secrets.append(value)
        return tuple(dict.fromkeys(secrets))

    @staticmethod
    def _normalize_site_url(value: Any) -> str:
        if type(value) is not str:
            raise VuePillConfigurationError("site_url must be an HTTP origin")
        site_url = value.strip()
        parse_failed = False
        try:
            parsed = urlsplit(site_url)
            parsed_port = parsed.port
        except (TypeError, ValueError):
            parse_failed = True
            parsed = None
            parsed_port = None

        invalid = (
            parse_failed
            or not site_url
            or any(
                ord(character) < 32 or ord(character) == 127
                for character in site_url
            )
            or any(character.isspace() for character in site_url)
            or "\\" in site_url
            or "?" in site_url
            or "#" in site_url
            or parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query != ""
            or parsed.fragment != ""
            or parsed.path not in {"", "/"}
            or parsed.netloc.endswith(":")
        )
        if invalid:
            raise VuePillConfigurationError("site_url must be an HTTP origin")
        netloc = parsed.netloc
        if parsed_port is not None and not 1 <= parsed_port <= 65535:
            raise VuePillConfigurationError("site_url must be an HTTP origin")
        return f"{parsed.scheme.lower()}://{netloc}"

    @staticmethod
    def _normalize_positive_float(value: Any, default: float) -> float:
        if type(value) is bool:
            return float(default)
        if type(value) is str:
            stripped = value.strip()
            if not VuePillSiteClient._FLOAT_TEXT_PATTERN.fullmatch(stripped):
                return float(default)
            value = stripped
        elif type(value) not in {int, float}:
            return float(default)
        try:
            normalized = float(value)
        except (TypeError, ValueError, OverflowError):
            return float(default)
        if not math.isfinite(normalized) or normalized <= 0:
            return float(default)
        return normalized

    @staticmethod
    def _normalize_int(
        value: Any,
        default: int,
        minimum: int,
        maximum: Optional[int] = None,
    ) -> int:
        if type(value) is bool:
            normalized = default
        elif type(value) is int:
            normalized = value
        elif type(value) is float:
            if not math.isfinite(value) or not value.is_integer():
                normalized = default
            else:
                normalized = int(value)
        elif type(value) is str:
            stripped = value.strip()
            if VuePillSiteClient._INTEGER_TEXT_PATTERN.fullmatch(stripped):
                try:
                    normalized = int(stripped)
                except (ValueError, OverflowError):
                    normalized = default
            else:
                normalized = default
        else:
            normalized = default
        normalized = max(minimum, normalized)
        if maximum is not None:
            normalized = min(maximum, normalized)
        return normalized

    @staticmethod
    def _normalize_bool(value: Any) -> bool:
        if type(value) is bool:
            return value
        if type(value) is int:
            return value == 1 if value in {0, 1} else False
        if type(value) is str:
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "enabled"}:
                return True
            if normalized in {"0", "false", "no", "off", "disabled", ""}:
                return False
            return False
        return False

    @staticmethod
    def _to_text(value: Any) -> str:
        if type(value) is str:
            return value
        if type(value) in {int, float, bool}:
            return VuePillSiteClient._safe_scalar_text(value)
        return ""
