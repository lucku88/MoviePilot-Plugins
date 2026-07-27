"""Standalone HTTP client for VuePill website requests."""

import errno
import math
import re
import socket
import time
from collections.abc import Mapping
from typing import Any, Callable, Iterable, Optional

import requests
import urllib3.util.connection as urllib3_connection
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


def _ipv4_gai_family() -> socket.AddressFamily:
    return socket.AF_INET


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
    MAX_REQUEST_TIMES = 5
    DEFAULT_TIMEOUT = 10.0

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
            "session",
            "session_id",
            "sessionid",
            "sid",
            "token",
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
    _LOGIN_MARKERS = (
        'type="password"',
        "type='password'",
        'name="password"',
        "name='password'",
        "please log in",
        "please login",
        "sign in to continue",
        "\u8bf7\u5148\u767b\u5f55",
        "\u8bf7\u767b\u5f55\u540e",
        "\u672a\u767b\u5f55",
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
        self.cookie = self._to_text(cookie)
        self.user_agent = self._to_text(user_agent)
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
        if self.force_ipv4:
            urllib3_connection.allowed_gai_family = _ipv4_gai_family

        session = requests.Session()
        adapter = HTTPAdapter(
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
            )
            self._raise_for_http_error(response, "fetch_page_html")
            html = getattr(response, "text", None)
            if not isinstance(html, str) or not html.strip():
                raise VuePillResponseError("fetch_page_html returned an empty response")
            if self._looks_like_login_page(html):
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
        action_name = action.strip() if isinstance(action, str) else ""
        if action_name not in self.ALLOWED_ACTIONS:
            raise VuePillActionError("Website action is not allowed")
        if payload is not None and not isinstance(payload, Mapping):
            raise VuePillConfigurationError("Action payload must be a mapping")

        form = {"action": action_name}
        sensitive_values = list(self._cookie_secrets)
        for key, value in (payload or {}).items():
            if key == "action" or value is None:
                continue
            form[key] = value
            if self._is_sensitive_key(key):
                sensitive_values.append(self._to_text(value))

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
            )
            self._raise_for_http_error(
                response,
                action_name,
                sensitive_values=sensitive_values,
            )
            try:
                result = response.json()
            except ValueError:
                raise VuePillResponseError(
                    f"Action {action_name} returned non-JSON data"
                ) from None
            if not isinstance(result, dict):
                raise VuePillResponseError(
                    f"Action {action_name} did not return a JSON object"
                )
            if result.get("success") is False:
                message = result.get("message") or result.get("msg")
                detail = self._sanitize(
                    message or "Website rejected the action",
                    sensitive_values,
                )
                raise VuePillActionError(f"Action {action_name} failed: {detail}")
            return result

        return self._request_with_retry(
            operation=action_name,
            total_attempts=total_attempts,
            request_func=do_request,
            sensitive_values=sensitive_values,
        )

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
            try:
                return request_func()
            except Exception as error:
                retryable = self._is_retryable_network_error(error)
                detail = self._sanitize_error(error, sensitive_values)
                self._log_failure(operation, attempt, attempts, detail)
                if not retryable or attempt >= attempts:
                    if isinstance(error, VuePillSiteClientError):
                        raise
                    raise VuePillRequestError(
                        f"{operation} request failed: {detail}"
                    ) from None
                wait_seconds = (self.retry_delay_ms * attempt) / 1000.0
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
        raise VuePillRequestError(f"{operation} request failed")

    def _raise_for_http_error(
        self,
        response,
        operation: str,
        sensitive_values: Iterable[str] = (),
    ) -> None:
        status_code = self._response_status_code(response)
        if status_code is None:
            raise_for_status = getattr(response, "raise_for_status", None)
            if callable(raise_for_status):
                try:
                    raise_for_status()
                except requests.exceptions.RequestException as error:
                    status_code = self._response_status_code(
                        getattr(error, "response", None)
                    )
                    detail = self._sanitize_error(error, sensitive_values)
                    raise VuePillRequestError(
                        f"{operation} request failed: {detail}",
                        status_code=status_code,
                    ) from None
            return
        if status_code < 400:
            return

        detail = self._response_message(response)
        if not detail:
            detail = getattr(response, "reason", None) or "HTTP error"
        safe_detail = self._sanitize(detail, sensitive_values)
        raise VuePillRequestError(
            f"{operation} request failed (HTTP {status_code}): {safe_detail}",
            status_code=status_code,
        )

    @staticmethod
    def _response_status_code(response) -> Optional[int]:
        if response is None:
            return None
        try:
            value = getattr(response, "status_code", None)
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _response_message(response) -> str:
        try:
            data = response.json()
        except (AttributeError, TypeError, ValueError):
            return ""
        if not isinstance(data, dict):
            return ""
        message = data.get("message") or data.get("msg")
        return str(message).strip() if message is not None else ""

    def _is_retryable_network_error(self, error: Exception) -> bool:
        if isinstance(error, VuePillRequestError):
            status_code = error.status_code
            return status_code is not None and 500 <= status_code < 600
        if isinstance(
            error,
            (VuePillConfigurationError, VuePillResponseError, VuePillActionError),
        ):
            return False
        if isinstance(
            error,
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                TimeoutError,
                ConnectionError,
                ConnectionResetError,
                ConnectionAbortedError,
                BrokenPipeError,
            ),
        ):
            return True

        status_code = self._response_status_code(getattr(error, "response", None))
        if status_code is not None:
            return 500 <= status_code < 600

        for candidate in (error, getattr(error, "__cause__", None)):
            if candidate is None:
                continue
            error_number = getattr(candidate, "errno", None)
            if error_number in self._RETRYABLE_ERRNOS:
                return True
            for attribute in ("code", "winerror"):
                code = getattr(candidate, attribute, None)
                if isinstance(code, str) and code.upper() in self._RETRYABLE_CODES:
                    return True
                if code in self._RETRYABLE_ERRNOS:
                    return True

        message = str(error).lower()
        return any(
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
                "temporarily unavailable",
            )
        )

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

    def _sanitize_error(
        self,
        error: Exception,
        sensitive_values: Iterable[str] = (),
    ) -> str:
        detail = str(error).strip() or error.__class__.__name__
        return self._sanitize(detail, sensitive_values)

    def _sanitize(
        self,
        value: Any,
        sensitive_values: Iterable[str] = (),
    ) -> str:
        text = self._to_text(value)
        secrets = set(self._cookie_secrets)
        secrets.update(
            self._to_text(secret)
            for secret in sensitive_values
            if self._to_text(secret)
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
    def _looks_like_login_page(cls, html: str) -> bool:
        lowered = html.lower()
        if any(marker in lowered for marker in cls._LOGIN_MARKERS):
            return True
        return "<form" in lowered and "login.php" in lowered

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
        site_url = VuePillSiteClient._to_text(value).strip().rstrip("/")
        if not site_url:
            raise VuePillConfigurationError("site_url must not be empty")
        return site_url

    @staticmethod
    def _normalize_positive_float(value: Any, default: float) -> float:
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
        try:
            normalized = int(float(value))
        except (TypeError, ValueError, OverflowError):
            normalized = default
        normalized = max(minimum, normalized)
        if maximum is not None:
            normalized = min(maximum, normalized)
        return normalized

    @staticmethod
    def _normalize_bool(value: Any) -> bool:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "enabled"}:
                return True
            if normalized in {"0", "false", "no", "off", "disabled", ""}:
                return False
            return False
        return bool(value)

    @staticmethod
    def _to_text(value: Any) -> str:
        return "" if value is None else str(value)
