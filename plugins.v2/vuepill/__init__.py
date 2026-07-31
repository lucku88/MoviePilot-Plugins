import inspect
import math
import random
import re
import secrets
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType

from .crafting import (
    compute_magic_pill_plan,
    exchange_batches,
    inventory_to_map,
    max_gift_quantity,
)
from .page_parser import parse_page
from .site_client import VuePillActionError, VuePillSiteClient


LEGACY_MIGRATION_KEY = "v020_initialized"
CONFIG_GENERATION_KEY = "config_generation"
CONFIG_GENERATION = 2
MIGRATION_KEY = LEGACY_MIGRATION_KEY
_DROP_PUBLIC_VALUE = object()
_PROCESS_INSTANCE_ID_ATTRIBUTE = "_moviepilot_vuepill_process_id"
_LEGACY_RESTART_PROCESS_KEY = "legacy_upgrade_restart_process"

# sys survives plugin module reloads and is recreated on MoviePilot restart.
_PROCESS_INSTANCE_ID = getattr(sys, _PROCESS_INSTANCE_ID_ATTRIBUTE, None)
if not isinstance(_PROCESS_INSTANCE_ID, str) or not _PROCESS_INSTANCE_ID:
    _PROCESS_INSTANCE_ID = secrets.token_hex(16)
    setattr(sys, _PROCESS_INSTANCE_ID_ATTRIBUTE, _PROCESS_INSTANCE_ID)


class _SiteResponseAdapter:
    def __init__(self, response, json_filter=None):
        self._response = response
        self._json_filter = json_filter

    @property
    def status_code(self):
        try:
            value = getattr(self._response, "status_code")
        except Exception:
            value = None
        if isinstance(value, int):
            return value
        raise_for_status = getattr(self._response, "raise_for_status", None)
        if callable(raise_for_status):
            raise_for_status()
            return 200
        return value

    def __getattr__(self, name):
        return getattr(self._response, name)

    def json(self):
        value = self._response.json()
        return self._json_filter(value) if self._json_filter else value


class _SiteSessionAdapter:
    def __init__(self, session, json_filter=None):
        self._session = session
        self._json_filter = json_filter

    def get(self, *args, **kwargs):
        return _SiteResponseAdapter(
            self._call("get", *args, **kwargs),
            json_filter=self._json_filter,
        )

    def post(self, *args, **kwargs):
        return _SiteResponseAdapter(
            self._call("post", *args, **kwargs),
            json_filter=self._json_filter,
        )

    def _call(self, method_name: str, *args, **kwargs):
        method = getattr(self._session, method_name)
        try:
            parameters = inspect.signature(method).parameters.values()
            accepts_extra = any(
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in parameters
            )
            if not accepts_extra:
                allowed = {parameter.name for parameter in parameters}
                kwargs = {key: value for key, value in kwargs.items() if key in allowed}
        except (TypeError, ValueError):
            pass
        return method(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._session, name)


def _public_api(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        return self._sanitize_public_response(method(self, *args, **kwargs))

    return wrapped


def _config_public_api(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        return self._sanitize_config_public_response(method(self, *args, **kwargs))

    return wrapped


class _MigrationActivityStopped(RuntimeError):
    pass


class _UpgradeRestartRequired(RuntimeError):
    pass


def _migration_activity(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            self._enter_migration_activity()
        except _MigrationActivityStopped:
            if method.__name__ == "_refresh_state":
                raise
            return self._activity_stopping_response()
        except _UpgradeRestartRequired:
            return self._upgrade_restart_response()
        try:
            return method(self, *args, **kwargs)
        finally:
            self._exit_migration_activity()

    return wrapped


def _exclusive_action(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            self._enter_migration_activity()
        except _MigrationActivityStopped:
            return self._activity_stopping_response()
        except _UpgradeRestartRequired:
            return self._upgrade_restart_response()
        try:
            execution_lock = type(self)._execution_lock
            if not execution_lock.acquire(blocking=False):
                return self._action_busy_response()
            try:
                return method(self, *args, **kwargs)
            finally:
                should_register = False
                try:
                    should_register = self._commit_pending_execution_retry()
                finally:
                    execution_lock.release()
                if should_register:
                    self._reregister_plugin("execution-busy-retry")
        finally:
            self._exit_migration_activity()

    return wrapped


class VuePill(_PluginBase):
    plugin_name = "Vue-魔丸"
    plugin_desc = "动态搬砖、清沙滩、炼造兑换、手动赠送与赠礼统计。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2697.png"
    plugin_version = "0.2.3"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "vuepill_"
    plugin_order = 68
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_BRICK_CRON = "5 0 * * *"
    PRE_REFRESH_SECONDS = 60
    MAX_NETWORK_RETRY_TIMES = 5
    MAX_CONSECUTIVE_ERROR_RETRIES = 5
    MAX_MANUAL_COOKIE_LENGTH = 16384
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    SUMMARY_LINE = "━━━━━━━━━━━━━━"
    LEGACY_MIGRATION_KEY = LEGACY_MIGRATION_KEY
    CONFIG_GENERATION_KEY = CONFIG_GENERATION_KEY
    CONFIG_GENERATION = CONFIG_GENERATION
    MIGRATION_KEY = LEGACY_MIGRATION_KEY
    _BEARER_PATTERN = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+")
    _SENSITIVE_HEADER_PATTERN = re.compile(
        r"(?im)(\b(?:cookie|set-cookie|authorization|proxy-authorization)"
        r"\s*:\s*)[^\r\n]+"
    )
    _SENSITIVE_VALUE_PATTERN = re.compile(
        r"(?i)((?:[\"'])?\b(?:cookie|set-cookie|authorization|"
        r"proxy-authorization|[a-z0-9_-]*(?:token|password|passwd|session|"
        r"secret)[a-z0-9_-]*|sid|api[_-]?key|target[_-]?uid|uid|"
        r"user[_-]?id)\b(?:[\"'])?\s*[:=]\s*)"
        r"(?:\[REDACTED\]|\"[^\"]*\"|'[^']*'|[^;,\s}\]]+)"
    )
    _PUBLIC_SAFE_SENSITIVE_KEYS = {"cookie_source", "cookie_ready"}
    _PUBLIC_SENSITIVE_KEY_FRAGMENTS = (
        "cookie",
        "token",
        "authorization",
        "password",
        "passwd",
        "session",
        "secret",
    )
    _PUBLIC_SENSITIVE_KEYS = {
        "api_key",
        "apikey",
        "auth",
        "credential",
        "credentials",
        "sid",
    }
    _SAFE_UID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
    _SUMMARY_COUNT_FIELDS = {
        "count",
        "events",
        "quantity",
        "total_events",
        "total_quantity",
    }
    _USER_SUMMARY_FIELDS = (
        "uid",
        "name",
        "display_name",
        "count",
        "events",
        "quantity",
        "total_events",
        "total_quantity",
    )
    _ITEM_SUMMARY_FIELDS = (
        "item_name",
        "name",
        "count",
        "events",
        "quantity",
        "total_events",
        "total_quantity",
    )

    ITEM_ICON_MAP = {
        "砖块": "🧱",
        "木材": "🪵",
        "塑料袋": "🛍️",
        "瓶子": "🧴",
        "螺丝": "🔩",
        "旧电池": "🔋",
        "破铜片": "🪙",
        "木工件": "🪚",
        "塑料件": "🪣",
        "简易工具": "🛠️",
        "能量碎片": "⚡",
        "魔丸胚胎": "🥚",
        "魔丸": "⚗️",
        "蚯蚓": "🪱",
    }

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None
    _lifecycle_lock = threading.RLock()
    _plan_lock = threading.RLock()
    _site_credentials_lock = threading.RLock()
    _execution_lock = threading.Lock()
    _migration_barrier = threading.Condition(threading.RLock())
    _migration_activity_local = threading.local()
    _active_migration_activities: int = 0
    _generation_reset_in_progress: bool = False
    _migration_stopping: bool = False
    _plan_revision: int = 0
    _pending_execution_retry: Optional[Tuple[int, str]] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _enable_brick: bool = True
    _enable_beach: bool = True
    _auto_craft: bool = False
    _auto_exchange: bool = False
    _use_proxy: bool = False
    _manual_cookie: str = ""
    _cookie: str = ""
    _cookie_source: str = "未同步"
    _site_domain: str = DEFAULT_SITE_DOMAIN
    _site_url: str = DEFAULT_SITE_URL
    _user_agent: str = DEFAULT_USER_AGENT
    _brick_cron: str = DEFAULT_BRICK_CRON
    _schedule_buffer_seconds: int = 5
    _random_delay_max_seconds: int = 3
    _http_timeout: int = 12
    _http_retry_times: int = MAX_NETWORK_RETRY_TIMES
    _http_retry_delay: int = 1500
    _move_max_loops: int = 80
    _move_delay_min_ms: int = 30
    _move_delay_max_ms: int = 80
    _ready_retry_seconds: int = 60
    _reserve_magic_pill_count: int = 10

    _next_run_time: Optional[datetime] = None
    _next_trigger_time: Optional[datetime] = None
    _next_trigger_mode: str = "run"
    _bootstrap_pending: bool = False

    JS_SAFE_INTEGER_MAX = (1 << 53) - 1
    CONFIG_INTEGER_RULES = {
        "schedule_buffer_seconds": ("冷却缓冲", 0, 3600, 5),
        "random_delay_max_seconds": ("随机延迟", 0, 300, 3),
        "http_timeout": ("请求超时", 5, 120, 12),
        "http_retry_times": (
            "网络重试次数",
            1,
            MAX_NETWORK_RETRY_TIMES,
            MAX_NETWORK_RETRY_TIMES,
        ),
        "http_retry_delay": ("重试间隔", 200, 60000, 1500),
        "move_delay_min_ms": ("搬砖最小延迟", 0, 60000, 30),
        "move_delay_max_ms": ("搬砖最大延迟", 0, 60000, 80),
        "ready_retry_seconds": ("临界状态重试间隔", 10, 3600, 60),
        "reserve_magic_pill_count": ("保留魔丸", 0, JS_SAFE_INTEGER_MAX, 10),
    }
    _CANONICAL_CONFIG_INTEGER_PATTERN = re.compile(r"^(?:0|[1-9]\d*)$")
    _CRON_NUMBER_PATTERN = re.compile(r"^\d+$")
    _CRON_MONTH_NAMES = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    _CRON_DAY_OF_WEEK_NAMES = {
        "mon": 0,
        "tue": 1,
        "wed": 2,
        "thu": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6,
    }
    _CRON_FIELD_RULES = (
        ("分钟", 0, 59, None),
        ("小时", 0, 23, None),
        ("日期", 1, 31, None),
        ("月份", 1, 12, _CRON_MONTH_NAMES),
        ("星期", 0, 7, _CRON_DAY_OF_WEEK_NAMES),
    )
    PUBLIC_MAX_ITEMS = 500
    PUBLIC_MAX_DEPTH = 20
    PUBLIC_MAX_SECRETS = 500
    # Scan beyond the public output bounds so omitted branches can redact echoes.
    PUBLIC_SECRET_SCAN_MAX_ITEMS = 1000
    PUBLIC_SECRET_SCAN_MAX_DEPTH = 64
    PUBLIC_SECRET_SCAN_MAX_NODES = 10000
    PUBLIC_LIMIT_MESSAGE = "响应数据超过安全限制，已省略"

    def __init__(self):
        super().__init__()

    def _enter_migration_activity(self):
        cls = type(self)
        local = cls._migration_activity_local
        depth = getattr(local, "depth", 0)
        if depth:
            local.depth = depth + 1
            return

        with cls._migration_barrier:
            while cls._generation_reset_in_progress:
                cls._migration_barrier.wait()
            if cls._migration_stopping:
                raise _MigrationActivityStopped("插件正在停止，已拒绝新任务")
            if self._upgrade_restart_required():
                raise _UpgradeRestartRequired("插件升级需要重启 MoviePilot")
            cls._active_migration_activities += 1
            local.depth = 1

    def _exit_migration_activity(self):
        cls = type(self)
        local = cls._migration_activity_local
        depth = getattr(local, "depth", 0)
        if depth > 1:
            local.depth = depth - 1
            return
        if depth != 1:
            raise RuntimeError("迁移活动屏障退出顺序无效")

        del local.depth
        with cls._migration_barrier:
            cls._active_migration_activities -= 1
            if cls._active_migration_activities == 0:
                cls._migration_barrier.notify_all()

    def _begin_generation_reset(self):
        cls = type(self)
        if getattr(cls._migration_activity_local, "depth", 0):
            raise RuntimeError("状态活动执行期间不能启动配置迁移")

        with cls._migration_barrier:
            while cls._generation_reset_in_progress:
                cls._migration_barrier.wait()
            cls._generation_reset_in_progress = True
            while cls._active_migration_activities:
                cls._migration_barrier.wait()

    def _end_generation_reset(self):
        cls = type(self)
        with cls._migration_barrier:
            cls._generation_reset_in_progress = False
            cls._migration_barrier.notify_all()

    def _mark_migration_stopping(self):
        cls = type(self)
        with cls._migration_barrier:
            cls._migration_stopping = True

    def _clear_migration_stopping(self):
        cls = type(self)
        with cls._migration_barrier:
            cls._migration_stopping = False
            cls._migration_barrier.notify_all()

    def _wait_for_migration_activities(self):
        cls = type(self)
        with cls._migration_barrier:
            while cls._active_migration_activities:
                cls._migration_barrier.wait()

    def _is_migration_stopping(self) -> bool:
        cls = type(self)
        with cls._migration_barrier:
            return cls._migration_stopping

    def _activity_stopping_response(self) -> Dict[str, Any]:
        return {
            "success": False,
            "message": "插件正在停止，已拒绝新任务",
        }

    def _upgrade_restart_response(self) -> Dict[str, Any]:
        return {
            "success": False,
            "message": "Vue-魔丸升级尚未完成，请重启 MoviePilot 后再执行",
        }

    @contextmanager
    def _explicit_lifecycle(self):
        self._lifecycle_lock.acquire()
        was_stopping = self._is_migration_stopping()
        if was_stopping:
            self._lifecycle_lock.release()
            self._wait_for_migration_activities()
            self._lifecycle_lock.acquire()
            was_stopping = self._is_migration_stopping()
        try:
            yield was_stopping
        finally:
            self._lifecycle_lock.release()

    def init_plugin(self, config: Optional[dict] = None):
        with self._explicit_lifecycle() as was_stopping:
            if was_stopping:
                self._clear_migration_stopping()
            try:
                self._init_plugin_locked(
                    config,
                    preserve_running_onlyonce=True,
                )
            except Exception:
                if was_stopping:
                    self._mark_migration_stopping()
                raise

    def _stored_config_generation(self) -> Optional[int]:
        raw = self.get_data(self.CONFIG_GENERATION_KEY)
        if raw in (None, ""):
            return None
        if isinstance(raw, bool):
            return -1
        if isinstance(raw, int):
            return raw
        if isinstance(raw, str) and re.fullmatch(r"[0-9]+", raw):
            try:
                return int(raw)
            except ValueError:
                return -1
        return -1

    def _has_meaningful_generation_data(self) -> bool:
        keys = (
            "history",
            "state",
            "pill_status",
            "last_run",
            "next_run_time",
            "next_trigger_time",
            "next_trigger_mode",
            "consecutive_error_retries",
            "last_error_retry_detail",
        )
        return any(bool(self.get_data(key)) for key in keys)

    def _stored_legacy_restart_process_id(self) -> Optional[str]:
        raw = self.get_data(_LEGACY_RESTART_PROCESS_KEY)
        if isinstance(raw, str) and raw:
            return raw
        return None

    def _upgrade_restart_required(self) -> bool:
        if self._stored_config_generation() is not None:
            return False
        if self.get_data(self.LEGACY_MIGRATION_KEY):
            return False
        return self._stored_legacy_restart_process_id() == _PROCESS_INSTANCE_ID

    def _finish_legacy_restart_metadata(self):
        self.save_data(self.LEGACY_MIGRATION_KEY, True)
        self.save_data(_LEGACY_RESTART_PROCESS_KEY, None)

    def _config_generation_mode(self, config: Optional[dict]) -> str:
        stored = self._stored_config_generation()
        if stored == self.CONFIG_GENERATION:
            return "current"
        if stored in (None, -1) and self.get_data(self.LEGACY_MIGRATION_KEY):
            return "legacy-current"
        if stored is None:
            restart_process_id = self._stored_legacy_restart_process_id()
            if restart_process_id:
                if restart_process_id == _PROCESS_INSTANCE_ID:
                    return "legacy-restart-pending"
                return "legacy-restart-finalize"
        if (
            stored is None
            and not config
            and not self._has_meaningful_generation_data()
        ):
            return "fresh"
        if stored is None:
            return "legacy-restart-prepare"
        return "reset"

    def _init_plugin_locked(
        self,
        config: Optional[dict] = None,
        preserve_running_onlyonce: bool = False,
    ):
        if not config:
            try:
                persisted_config = self.get_config()
            except Exception:
                persisted_config = None
            if isinstance(persisted_config, dict) and persisted_config:
                config = persisted_config

        generation_mode = self._config_generation_mode(config)
        legacy_restart_finish_pending = bool(
            generation_mode == "current"
            and self._stored_legacy_restart_process_id()
        )
        running_scheduler = bool(
            self._scheduler and self._scheduler.running
        )
        keep_running_scheduler = bool(
            preserve_running_onlyonce
            and generation_mode in {"current", "legacy-current"}
            and not legacy_restart_finish_pending
            and running_scheduler
        )
        if not keep_running_scheduler:
            self._stop_service_locked()

        if generation_mode in {
            "fresh",
            "reset",
            "legacy-restart-finalize",
        }:
            reset_required = generation_mode in {
                "reset",
                "legacy-restart-finalize",
            }
            execution_lock = (
                type(self)._execution_lock if reset_required else None
            )
            migration_started = False
            execution_acquired = False
            try:
                if reset_required:
                    self._begin_generation_reset()
                    migration_started = True
                if execution_lock is not None:
                    execution_lock.acquire()
                    execution_acquired = True
                self._persist_safe_default_config()
                if reset_required:
                    self._reset_generation_data()
                self.save_data(
                    self.CONFIG_GENERATION_KEY,
                    self.CONFIG_GENERATION,
                )
                if generation_mode == "legacy-restart-finalize":
                    self._finish_legacy_restart_metadata()
                else:
                    self.save_data(self.LEGACY_MIGRATION_KEY, True)
            finally:
                if execution_acquired and execution_lock is not None:
                    execution_lock.release()
                if migration_started:
                    self._end_generation_reset()
            return

        if generation_mode in {
            "legacy-restart-prepare",
            "legacy-restart-pending",
        }:
            migration_started = False
            try:
                self._begin_generation_reset()
                migration_started = True
                # 升级重启前只挂起旧实例，不覆盖用户现有配置；真正的重置
                # 在检测到新 MoviePilot 进程后再执行。
                previous_runtime_config = self._get_config(include_options=False)
                self._reset_runtime_site_credentials()
                self._bootstrap_pending = False
                preserved_config = self._merge_public_config(
                    config if config is not None else self._config_store
                )
                try:
                    self._apply_config(preserved_config)
                    if self._update_config() is False:
                        raise RuntimeError("升级等待状态配置写入失败")
                except Exception:
                    self._apply_config(previous_runtime_config)
                    raise
                if generation_mode == "legacy-restart-prepare":
                    self.save_data(
                        _LEGACY_RESTART_PROCESS_KEY,
                        _PROCESS_INSTANCE_ID,
                    )
            finally:
                if migration_started:
                    self._end_generation_reset()
            return

        if legacy_restart_finish_pending:
            self._reset_runtime_site_credentials()
            self._bootstrap_pending = False
            self._apply_config(self._default_config())
            self._finish_legacy_restart_metadata()
            return

        if generation_mode == "legacy-current":
            self.save_data(self.CONFIG_GENERATION_KEY, self.CONFIG_GENERATION)

        self._reset_runtime_site_credentials()
        merged = self._merge_public_config(config)
        self._apply_config(merged)

        self._load_saved_next_run()
        self._load_saved_next_trigger()
        self._bootstrap_pending = (
            self._enabled
            and (self._enable_brick or self._enable_beach)
            and not self._onlyonce
        )

        if keep_running_scheduler:
            requested_onlyonce = self._onlyonce
            self._onlyonce = False
            if requested_onlyonce:
                self._update_config()
            return

        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(
                func=self._manual_worker,
                trigger="date",
                run_date=self._aware_now() + timedelta(seconds=3),
                name=self.plugin_name,
            )
            self._onlyonce = False
            self._update_config()
            self._scheduler.start()
            logger.info("%s 已注册一次性执行任务", self.plugin_name)

    def _persist_safe_default_config(self):
        self._reset_runtime_site_credentials()
        self._bootstrap_pending = False
        self._apply_config(self._default_config())
        if self._update_config() is False:
            raise RuntimeError("默认配置写入失败，配置迁移未完成")

    def _reset_generation_data(self):
        reset_values = {
            "history": [],
            "state": {},
            "pill_status": {},
            "last_run": "",
            "consecutive_error_retries": 0,
            "last_error_retry_detail": "",
        }
        for key, value in reset_values.items():
            self.save_data(key, value)
        self._clear_plan_state()

    def _clear_plan_state(self):
        with self._plan_lock:
            self._next_run_time = None
            self._next_trigger_time = None
            self._next_trigger_mode = "run"
            type(self)._pending_execution_retry = None
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", "")
            self.save_data("next_trigger_mode", "")
            type(self)._plan_revision += 1

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-魔丸配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 Vue-魔丸配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-魔丸状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新 Vue-魔丸状态"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行 Vue-魔丸"},
            {"path": "/move-bricks", "endpoint": self._move_bricks_api, "methods": ["POST"], "auth": "bear", "summary": "立即搬砖"},
            {"path": "/clean-beach", "endpoint": self._clean_beach_api, "methods": ["POST"], "auth": "bear", "summary": "立即清理沙滩"},
            {"path": "/exchange-points", "endpoint": self._exchange_points_api, "methods": ["POST"], "auth": "bear", "summary": "兑换魔力"},
            {"path": "/craft-item", "endpoint": self._craft_item_api, "methods": ["POST"], "auth": "bear", "summary": "炼造指定配方"},
            {"path": "/craft-max-pill", "endpoint": self._craft_max_pill_api, "methods": ["POST"], "auth": "bear", "summary": "一键炼造魔丸"},
            {"path": "/gift-item", "endpoint": self._gift_item_api, "methods": ["POST"], "auth": "bear", "summary": "赠送物品"},
            {"path": "/gift-stats", "endpoint": self._gift_stats_api, "methods": ["POST"], "auth": "bear", "summary": "获取赠礼统计"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        if self._is_migration_stopping():
            return services
        if self._scheduler and self._scheduler.running:
            return services
        if self._enabled:
            next_run = self._get_next_run_for_service()
            if next_run:
                services.append({
                    "id": "VuePill_auto",
                    "name": "Vue-魔丸初始化" if self._bootstrap_pending else "Vue-魔丸智能调度",
                    "trigger": "date",
                    "func": self._bootstrap_worker if self._bootstrap_pending else self._auto_worker,
                    "kwargs": {"run_date": next_run},
                })
        return services

    def stop_service(self):
        with self._lifecycle_lock:
            # 普通任务保持停止；只有明确重新初始化或保存配置才允许恢复。
            self._mark_migration_stopping()
            self._stop_service_locked()
        # manual_worker needs lifecycle for cleanup after its activity exits.
        self._wait_for_migration_activities()

    def _stop_service_locked(self):
        scheduler = self._scheduler
        self._scheduler = None
        try:
            if scheduler:
                scheduler.remove_all_jobs()
                if scheduler.running:
                    scheduler.shutdown(wait=False)
        except Exception as err:
            logger.warning(
                "%s 停止一次性调度失败：%s",
                self.plugin_name,
                self._get_error_detail(err),
            )

        try:
            Scheduler().remove_plugin_job(self.__class__.__name__)
        except Exception:
            pass

    @_migration_activity
    def run_job(self, force: bool = False, reason: str = "manual") -> Dict[str, Any]:
        run_start = time.time()
        base_reason, _ = self._parse_run_reason(reason)
        execution_acquired = False
        logger.info("## 开始执行... %s", self._format_time(self._aware_now()))
        try:
            if not self._enabled and not force:
                return {"success": False, "message": "插件未启用", "status": self._build_status(auto_refresh=False)}

            self._ensure_cookie()

            if not force and base_reason == "schedule" and self._is_pre_refresh_trigger():
                before_refresh = self._capture_refresh_catchup_state()
                pill_status = self._refresh_state(
                    reason="pre-run-refresh",
                    record_run=False,
                    commit_plan=False,
                )
                catchup_result = self._run_after_refresh_if_due(
                    pill_status,
                    run_reason="schedule",
                    refresh_reason="pre-run-refresh",
                    before_refresh=before_refresh,
                )
                if catchup_result:
                    return catchup_result
                self._restore_pre_refresh_plan(before_refresh)
                logger.info("%s 已完成运行前 1 分钟预刷新", self.plugin_name)
                return {
                    "success": True,
                    "message": "运行前状态已刷新",
                    "lines": [],
                    "pill_status": pill_status,
                    "status": self._build_status(auto_refresh=False),
                }

            execution_lock = type(self)._execution_lock
            if not execution_lock.acquire(blocking=False):
                return self._busy_run_result(force=force, reason=reason)
            execution_acquired = True

            rand_delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if rand_delay:
                logger.info("INFO 随机延迟 %s 秒后执行...", rand_delay)
                time.sleep(rand_delay)

            if not force and self._should_skip_run():
                logger.info("INFO 未到计划触发时间，跳过本次运行")
                return {"success": True, "message": "未到计划触发时间，已跳过", "status": self._build_status(auto_refresh=False)}

            session = self._build_session()
            page = self._fetch_page_state(session)

            scheduled_action = self._resolve_scheduled_action(force, reason)
            run_brick = self._enable_brick and scheduled_action in {"all", "brick"}
            run_beach = self._enable_beach and scheduled_action in {"all", "beach"}
            beach_due_action = not force and base_reason == "schedule" and scheduled_action == "beach" and run_beach
            if beach_due_action and not self._is_beach_ready(page.get("beach") or {}):
                page = self._refresh_beach_due_page(session, page)

            brick_result: Dict[str, Any] = {}
            beach_result: Dict[str, Any] = {}
            auto_result: Dict[str, Any] = {}
            beach_flow_attempted = False

            if run_brick and page.get("brick", {}).get("ready"):
                brick_result = self._run_brick_flow(session, page.get("brick") or {})
            elif run_brick:
                brick_result = {"message": page.get("brick", {}).get("status_text") or "今日搬砖已满"}

            if run_beach and self._is_beach_ready(page.get("beach") or {}):
                beach_flow_attempted = True
                beach_result = self._execute_beach_flow(
                    session,
                    page.get("beach") or {},
                )
            elif run_beach:
                beach_result = {"message": page.get("beach", {}).get("status_text") or "沙滩冷却中"}

            final_page = self._fetch_stable_page_state(
                session,
                previous_page=page,
                expect_brick_update=self._safe_int(brick_result.get("moved"), 0) > 0,
                expect_beach_cooldown=bool(beach_result.get("done")),
            )
            brick_result = self._sync_brick_result_with_page(brick_result, page, final_page)
            if (
                beach_due_action
                and not beach_flow_attempted
                and self._is_beach_ready(final_page.get("beach") or {})
            ):
                beach_flow_attempted = True
                beach_result = self._execute_beach_flow(
                    session,
                    final_page.get("beach") or {},
                )
                final_page = self._fetch_stable_page_state(
                    session,
                    previous_page=final_page,
                    expect_beach_cooldown=bool(beach_result.get("done")),
                )
            if beach_result.get("done") and (self._auto_craft or self._auto_exchange):
                auto_result, final_page = self._run_auto_post_beach(session, final_page)
                final_page = self._fetch_stable_page_state(session, previous_page=final_page)
            retry_action = self._get_retry_action(final_page, brick_result, beach_result)
            if beach_due_action and not beach_result.get("done"):
                retry_action = "beach"
            next_run, next_action = self._compute_next_plan(final_page)
            force_run_trigger = False
            if retry_action:
                retry_ts = int(time.time()) + max(10, self._ready_retry_seconds)
                next_run, next_action = self._limit_retry_plan_if_needed(
                    retry_action,
                    retry_ts,
                    next_run,
                    next_action,
                    base_reason,
                )
                force_run_trigger = bool(
                    next_run == retry_ts
                    and next_action in {retry_action, "all"}
                )
            lines, has_action, has_warning = self._build_result_lines(brick_result, beach_result, auto_result)
            if brick_result.get("attempted") and final_page.get("brick", {}).get("ready"):
                remaining = max(
                    0,
                    self._safe_int((final_page.get("brick") or {}).get("daily_limit"), 50)
                    - self._safe_int((final_page.get("brick") or {}).get("daily_bricks"), 0),
                )
                if remaining > 0:
                    lines.append(f"⏳ 搬砖剩余：{remaining} 次，60秒后重试")
                    has_warning = True
            if not has_action and not has_warning:
                lines = ["ℹ️ 本次无可执行动作"]

            self._schedule_next_run(
                next_run,
                base_reason,
                next_action,
                force_run=force_run_trigger,
            )
            pill_status = self._refresh_and_store_status(final_page, next_run, lines, next_action=next_action)
            auto_warning = str(auto_result.get("warning") or "")
            auto_failed = bool(auto_warning)
            history_title = "⚗️ Vue-魔丸运行"
            if auto_failed:
                history_title = (
                    "⚠️ Vue-魔丸部分完成"
                    if has_action or auto_result.get("craft_steps")
                    else "❌ Vue-魔丸失败"
                )
            self._append_history(history_title, lines)

            if self._notify and (has_action or has_warning):
                title = "【⚠️魔丸部分完成】" if auto_failed else "【⚗️魔丸报告 】"
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title=title,
                    text=self._build_notify_text(lines, next_run),
                )

            if not has_warning and not retry_action:
                self._reset_error_retry_count()
            message = lines[0]
            if auto_failed:
                message = next(
                    (line for line in lines if line.startswith("⚠️")),
                    message,
                )
            return {
                "success": not auto_failed,
                "message": message,
                "lines": lines,
                "warning": auto_warning,
                "partial": bool(auto_result.get("partial")),
                "status": self._build_status(auto_refresh=False),
                "pill_status": pill_status,
            }
        except Exception as err:
            error_sensitive_values = self._error_sensitive_values(err)
            detail = self._get_error_detail(err, error_sensitive_values)
            retry_count = self._record_error_retry(detail)
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            safe_traceback = self._sanitize_sensitive_text(
                traceback.format_exc(),
                error_sensitive_values,
            )
            logger.error("%s 异常堆栈：\n%s", self.plugin_name, safe_traceback)
            self._append_history(f"❌ {self.plugin_name}异常", [f"⚠️ {detail}"])
            if self._notify:
                text = f"⚠️ {detail}"
                if retry_count > self.MAX_CONSECUTIVE_ERROR_RETRIES:
                    text += f"\n⛔ 已连续失败 {retry_count} 次，停止短间隔自动重试"
                self.post_message(mtype=NotificationType.Plugin, title=f"【⚠️{self.plugin_name}】 执行异常", text=text)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            should_register = False
            if execution_acquired:
                try:
                    should_register = self._commit_pending_execution_retry()
                finally:
                    type(self)._execution_lock.release()
            if should_register:
                self._reregister_plugin("execution-busy-retry")
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(self._aware_now()), cost_sec)

    def _action_busy_response(self) -> Dict[str, Any]:
        return {
            "success": False,
            "message": "已有任务正在执行，请稍后重试",
            "status": self._build_status(auto_refresh=False),
        }

    def _busy_run_result(self, force: bool, reason: str) -> Dict[str, Any]:
        base_reason, _ = self._parse_run_reason(reason)
        if base_reason in {"schedule", "bootstrap", "save-config"}:
            retry_action = self._resolve_scheduled_action(force, reason)
            retry_ts = int(time.time()) + max(10, self._ready_retry_seconds)
            self._queue_execution_retry(
                retry_ts,
                f"{base_reason}-busy-retry",
                retry_action,
            )
        return self._action_busy_response()

    def _queue_execution_retry(
        self,
        retry_ts: int,
        reason: str,
        retry_action: str,
    ):
        with self._plan_lock:
            pending = type(self)._pending_execution_retry
            if pending:
                retry_ts = min(retry_ts, pending[0])
                retry_action = self._merge_trigger_actions(
                    retry_action,
                    pending[1],
                )
            type(self)._pending_execution_retry = (retry_ts, retry_action)
            should_register = self._commit_next_run_locked(
                retry_ts,
                retry_action,
                force_run=True,
            )
        if should_register:
            self._reregister_plugin(reason)

    def _commit_pending_execution_retry(self) -> bool:
        with self._plan_lock:
            pending = type(self)._pending_execution_retry
            if not pending:
                return False
            type(self)._pending_execution_retry = None
            retry_ts, retry_action = pending
            retry_ts = max(retry_ts, int(time.time()) + 5)
            return self._commit_next_run_locked(
                retry_ts,
                retry_action,
                force_run=True,
            )

    def _manual_worker(self):
        scheduler = self._scheduler
        try:
            return self.run_job(force=True, reason="onlyonce")
        finally:
            with self._lifecycle_lock:
                owns_scheduler_slot = self._scheduler is scheduler
                if owns_scheduler_slot:
                    self._scheduler = None
                if scheduler:
                    try:
                        scheduler.remove_all_jobs()
                    except Exception:
                        pass
                    try:
                        if scheduler.running:
                            scheduler.shutdown(wait=False)
                    except Exception as err:
                        logger.warning(
                            "%s 关闭一次性调度失败：%s",
                            self.plugin_name,
                            self._get_error_detail(err),
                        )

                if owns_scheduler_slot and self._enabled:
                    next_trigger = self._load_saved_next_trigger()
                    self._bootstrap_pending = (
                        (self._enable_brick or self._enable_beach)
                        and not bool(next_trigger)
                    )
                    self._reregister_plugin("onlyonce-complete")

    def _auto_worker(self):
        return self.run_job(force=False, reason="schedule")

    @_migration_activity
    def _bootstrap_worker(self):
        self._bootstrap_pending = False
        if not self._enabled:
            return {"success": False, "message": "插件未启用"}
        try:
            before_refresh = self._capture_refresh_catchup_state()
            status = self._refresh_state(reason="status-init", record_run=False)
            catchup_result = self._run_after_refresh_if_due(
                status,
                run_reason="bootstrap",
                refresh_reason="status-init",
                before_refresh=before_refresh,
            )
            if catchup_result:
                return catchup_result
            return {"success": True, "message": "启动状态已刷新", "pill_status": status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 启动初始化刷新失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _capture_refresh_catchup_state(self) -> Dict[str, Any]:
        now = self._aware_now()
        next_run, next_trigger, trigger_mode, revision = self._load_plan_snapshot()
        _, trigger_action = self._parse_trigger_mode(trigger_mode)
        return {
            "next_run": next_run,
            "next_trigger": next_trigger,
            "next_run_overdue": bool(next_run and next_run <= now),
            "next_trigger_overdue": bool(next_trigger and next_trigger <= now),
            "trigger_mode": trigger_mode,
            "trigger_action": trigger_action,
            "plan_revision": revision,
        }

    def _restore_pre_refresh_plan(self, before_refresh: Dict[str, Any]) -> bool:
        planned_run = before_refresh.get("next_run")
        if not isinstance(planned_run, datetime):
            return False

        should_register = False
        with self._plan_lock:
            if type(self)._plan_revision != before_refresh.get("plan_revision"):
                logger.info("%s 预刷新期间计划已更新，跳过恢复旧计划", self.plugin_name)
                return False
            should_register = self._commit_next_run_locked(
                int(planned_run.timestamp()),
                before_refresh.get("trigger_action") or "all",
                force_run=True,
            )
        if should_register:
            self._reregister_plugin("pre-run-refresh")
        return True

    def _run_after_refresh_if_due(
        self,
        status: Optional[Dict[str, Any]],
        run_reason: str,
        refresh_reason: str,
        before_refresh: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        catchup_action = self._refresh_catchup_action(
            status,
            before_refresh,
            refresh_reason=refresh_reason,
        )
        if not catchup_action:
            return None
        logger.info("%s 刷新后检测到已可执行，立即补跑：%s", self.plugin_name, refresh_reason)
        if catchup_action in {"brick", "beach"}:
            run_reason = f"{run_reason}:{catchup_action}"
        return self.run_job(force=True, reason=run_reason)

    def _should_run_after_refresh(
        self,
        status: Optional[Dict[str, Any]],
        before_refresh: Optional[Dict[str, Any]] = None,
        refresh_reason: str = "",
    ) -> bool:
        return bool(
            self._refresh_catchup_action(
                status,
                before_refresh,
                refresh_reason=refresh_reason,
            )
        )

    def _refresh_catchup_action(
        self,
        status: Optional[Dict[str, Any]],
        before_refresh: Optional[Dict[str, Any]] = None,
        refresh_reason: str = "",
    ) -> str:
        if not self._enabled or not (self._enable_brick or self._enable_beach):
            return ""

        before = before_refresh or {}
        trigger_mode = str(before.get("trigger_mode") or "run")
        if before.get("next_run_overdue") or (before.get("next_trigger_overdue") and trigger_mode.startswith("run")):
            trigger_action = str(before.get("trigger_action") or "")
            return trigger_action if trigger_action in {"brick", "beach"} else "all"

        pill_status = status or {}
        if (
            refresh_reason in {"save-config", "status-init"}
            and self._enable_beach
            and self._is_beach_ready(pill_status.get("beach") or {})
        ):
            return "beach"

        return ""

    def _is_beach_ready(self, beach: Dict[str, Any]) -> bool:
        if not isinstance(beach, dict):
            return False
        return bool(
            beach.get("ready")
            or beach.get("can_clean")
            or beach.get("can_collect")
            or beach.get("has_trash")
            or beach.get("collect_enabled")
            or str(beach.get("action_kind") or "").lower() in {"ready", "run", "clean"}
        )

    @_public_api
    def _refresh_data(self):
        try:
            status = self._refresh_state(reason="manual-refresh")
            return {"success": True, "message": "Vue-魔丸状态已刷新", "pill_status": status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 刷新状态失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    @_public_api
    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

    @_public_api
    @_exclusive_action
    def _move_bricks_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_move_bricks()
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "搬砖完成",
                "lines": result["lines"],
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动搬砖失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    @_public_api
    @_exclusive_action
    def _clean_beach_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_clean_beach()
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "清理沙滩完成",
                "lines": result["lines"],
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动清理沙滩失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    @_public_api
    @_exclusive_action
    def _exchange_points_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_exchange_points(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "兑换完成",
                "lines": result["lines"],
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 兑换魔力失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    @_public_api
    @_exclusive_action
    def _craft_item_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_craft_item(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "炼造完成",
                "lines": result["lines"],
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 炼造配方失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    @_public_api
    @_exclusive_action
    def _craft_max_pill_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_craft_max_pill(payload or {})
            return {
                "success": result.get("success") is not False,
                "message": result["lines"][0] if result["lines"] else "魔丸炼造完成",
                "lines": result["lines"],
                "warning": result.get("warning") or "",
                "crafted": self._safe_int(result.get("crafted"), 0),
                "target": self._safe_int(result.get("target"), 0),
                "partial": bool(result.get("partial")),
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 一键炼造魔丸失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    @_public_api
    @_exclusive_action
    def _gift_item_api(self, payload: Optional[dict] = None):
        target_uid = ""
        try:
            item_name, target_uid, quantity = self._validate_gift_item_payload(payload)
            self._ensure_cookie()

            session = self._build_session()
            page = self._fetch_page_state(session)
            inventory = page.get("inventory") or []
            item = next(
                (
                    row
                    for row in inventory
                    if isinstance(row, dict)
                    and str(row.get("name") or "").strip() == item_name
                ),
                None,
            )
            if not item:
                raise ValueError(f"物品 {item_name} 不存在")
            if item.get("giftable") is not True:
                raise ValueError(f"物品 {item_name} 当前不可赠送")

            max_quantity = max_gift_quantity(
                inventory,
                item_name,
                cap=500,
            )
            if quantity > max_quantity:
                if quantity > 500:
                    raise ValueError("赠送数量不能超过 500")
                raise ValueError(
                    f"赠送数量超过当前库存，最多可赠送 {max_quantity}"
                )

            result = self._post_action(
                session,
                "gift_item",
                {
                    "item_name": item_name,
                    "target_uid": target_uid,
                    "quantity": quantity,
                },
                retry_network=False,
            )
            if not isinstance(result, dict) or result.get("success") is not True:
                raise ValueError(
                    self._safe_result_message(
                        result,
                        "网站拒绝了赠送请求",
                        (target_uid,),
                    )
                )

            refresh_error = ""
            try:
                refreshed_page = self._fetch_page_state(session)
                next_run, next_action = self._compute_next_plan(refreshed_page)
                self._schedule_next_run(next_run, "gift-item", next_action)
                self._refresh_and_store_status(
                    refreshed_page,
                    next_run,
                    [],
                    record_run=False,
                    next_action=next_action,
                )
            except Exception as err:
                refresh_error = self._get_error_detail(err, (target_uid,))
                logger.warning(
                    "%s 赠送成功后刷新状态失败：%s",
                    self.plugin_name,
                    refresh_error,
                )

            history_title = f"🎁赠送：{item_name}×{quantity} / 目标 UID {target_uid}"
            try:
                self._append_history(history_title, [])
            except Exception as err:
                logger.warning(
                    "%s 赠送成功后写入历史失败：%s",
                    self.plugin_name,
                    self._get_error_detail(err, (target_uid,)),
                )

            message = self._safe_result_message(
                result,
                "赠送成功",
                (target_uid,),
            )
            if refresh_error:
                message = f"{message}，但状态刷新失败，请稍后手动刷新"
            return {
                "success": True,
                "message": message,
                "item_name": item_name,
                "quantity": quantity,
                "target_uid": target_uid,
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err, (target_uid,))
            logger.warning("%s 赠送物品失败：%s", self.plugin_name, detail)
            return {
                "success": False,
                "message": detail,
                "status": self._build_status(auto_refresh=False),
            }

    @_public_api
    def _gift_stats_api(self, payload: Optional[dict] = None):
        try:
            direction, range_value = self._validate_gift_stats_payload(payload)
            self._ensure_cookie()

            session = self._build_session()
            result = self._post_action(
                session,
                "gift_stats",
                {"direction": direction, "range": range_value},
                retry_network=False,
            )
            if not isinstance(result, dict) or result.get("success") is not True:
                raise ValueError(
                    self._safe_result_message(
                        result,
                        "网站返回赠礼统计失败",
                    )
                )

            summary = result.get("data")
            if not isinstance(summary, dict):
                summary = result.get("stats")
            if not isinstance(summary, dict):
                summary = result
            (
                result_sensitive_values,
                result_sensitive_scalars,
                result_secrets_complete,
            ) = self._collect_sensitive_public_data(result)
            if not result_secrets_complete:
                raise ValueError(self.PUBLIC_LIMIT_MESSAGE)
            result_sensitive_values = tuple(result_sensitive_values)
            return {
                "success": True,
                "message": self._safe_result_message(result, "统计加载完成"),
                "direction": direction,
                "range": range_value,
                "total_events": self._summary_int(
                    summary.get("total_events"),
                    result_sensitive_values,
                    result_sensitive_scalars,
                ),
                "total_quantity": self._summary_int(
                    summary.get("total_quantity"),
                    result_sensitive_values,
                    result_sensitive_scalars,
                ),
                "users": self._whitelist_summary_rows(
                    summary.get("users"),
                    self._USER_SUMMARY_FIELDS,
                    "uid",
                    result_sensitive_values,
                    result_sensitive_scalars,
                ),
                "items": self._whitelist_summary_rows(
                    summary.get("items"),
                    self._ITEM_SUMMARY_FIELDS,
                    "item_name",
                    result_sensitive_values,
                    result_sensitive_scalars,
                ),
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 获取赠礼统计失败：%s", self.plugin_name, detail)
            return {
                "success": False,
                "message": detail,
                "status": self._build_status(auto_refresh=False),
            }

    def _validate_gift_item_payload(self, payload: Optional[dict]) -> Tuple[str, str, int]:
        if type(payload) is not dict:
            raise ValueError("赠送请求必须是普通字典")
        allowed_fields = {"item_name", "uid", "target_uid", "quantity"}
        if any(type(key) is not str or key not in allowed_fields for key in payload):
            raise ValueError("赠送请求包含不支持的字段")

        item_name = payload.get("item_name")
        if type(item_name) is not str or not item_name.strip():
            raise ValueError("物品名称不能为空")
        item_name = item_name.strip()
        if len(item_name) > 100 or self._contains_control_characters(item_name):
            raise ValueError("物品名称包含不安全字符")

        raw_target = payload.get("target_uid")
        if raw_target is None or (type(raw_target) is str and not raw_target.strip()):
            raw_target = payload.get("uid")
        target_uid = self._normalize_uid(raw_target)
        if "uid" in payload and "target_uid" in payload:
            second_uid = self._normalize_uid(payload.get("uid"))
            if target_uid != second_uid:
                raise ValueError("uid 和 target_uid 不一致")

        quantity = payload.get("quantity")
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("赠送数量必须是正整数")
        return item_name, target_uid, quantity

    def _validate_gift_stats_payload(self, payload: Optional[dict]) -> Tuple[str, str]:
        if type(payload) is not dict:
            raise ValueError("统计请求必须是普通字典")
        if any(
            type(key) is not str or key not in {"direction", "range"}
            for key in payload
        ):
            raise ValueError("统计请求包含不支持的字段")

        direction = payload.get("direction")
        direction = direction.strip().lower() if type(direction) is str else ""
        if direction not in {"out", "in"}:
            raise ValueError("direction 只允许 out 或 in")

        range_value = payload.get("range")
        if type(range_value) is not str:
            raise ValueError("range 必须是字符串")
        range_value = range_value.strip().lower()
        if range_value not in {"30", "all"}:
            raise ValueError('range 只允许 "30" 或 "all"')
        return direction, range_value

    def _normalize_uid(self, value: Any) -> str:
        if type(value) is bool or type(value) not in {str, int}:
            raise ValueError("目标 UID 不能为空且必须是安全字符串")
        uid = str(value).strip()
        if (
            not uid
            or len(uid) > 128
            or not self._SAFE_UID_PATTERN.fullmatch(uid)
        ):
            raise ValueError("目标 UID 不能为空且必须是安全字符串")
        return uid

    @staticmethod
    def _contains_control_characters(value: str) -> bool:
        return any(ord(character) < 32 or ord(character) == 127 for character in value)

    def _safe_result_message(
        self,
        result: Any,
        default: str,
        sensitive_values: Tuple[str, ...] = (),
    ) -> str:
        collected_values, _, collection_complete = (
            self._collect_sensitive_public_data(result)
        )
        if not collection_complete:
            return self.PUBLIC_LIMIT_MESSAGE
        combined_sensitive_values = tuple(sensitive_values) + tuple(
            collected_values
        )
        if isinstance(result, dict):
            for key in ("message", "msg"):
                value = result.get(key)
                if type(value) is str and value.strip():
                    return self._sanitize_sensitive_text(
                        value,
                        combined_sensitive_values,
                    )
        return self._sanitize_sensitive_text(default, combined_sensitive_values)

    def _safe_result_data(self, result: Any) -> Dict[str, Any]:
        if type(result) is not dict:
            return {}
        public_result = self._sanitize_public_response(result)
        return public_result if type(public_result) is dict else {}

    def _whitelist_summary_rows(
        self,
        value: Any,
        allowed_fields: Tuple[str, ...],
        identity_field: str,
        sensitive_values: Tuple[str, ...] = (),
        sensitive_scalar_values: Optional[set] = None,
    ) -> List[Dict[str, Any]]:
        if isinstance(value, dict):
            if any(key in value for key in allowed_fields):
                source_rows = iter((value,))
            else:
                source_rows = (
                    {identity_field: key, "quantity": nested}
                    for key, nested in value.items()
                )
        elif isinstance(value, list):
            source_rows = iter(value)
        else:
            return []

        rows: List[Dict[str, Any]] = []
        for raw_row in self._take_public_items(source_rows):
            if not isinstance(raw_row, dict):
                continue
            row_values, row_scalars, row_complete = (
                self._collect_sensitive_public_data(raw_row)
            )
            if not row_complete:
                continue
            row_sensitive_values = tuple(sensitive_values) + tuple(row_values)
            row_sensitive_scalars = set(sensitive_scalar_values or ())
            row_sensitive_scalars.update(row_scalars)
            row: Dict[str, Any] = {}
            for key in allowed_fields:
                if key not in raw_row:
                    continue
                raw_value = raw_row.get(key)
                if key in self._SUMMARY_COUNT_FIELDS:
                    row[key] = self._summary_int(
                        raw_value,
                        row_sensitive_values,
                        row_sensitive_scalars,
                    )
                elif type(raw_value) in {str, int} and type(raw_value) is not bool:
                    text = str(raw_value).strip()
                    if text and len(text) <= 200 and not self._contains_control_characters(text):
                        row[key] = self._sanitize_sensitive_text(
                            text,
                            row_sensitive_values,
                        )
            if row:
                rows.append(row)
        return rows

    def _summary_int(
        self,
        value: Any,
        sensitive_values: Tuple[str, ...] = (),
        sensitive_scalar_values: Optional[set] = None,
    ) -> int:
        if type(value) is bool:
            return 0
        if type(value) is int:
            marker = self._sensitive_public_scalar_marker(value)
            if (
                marker is not None
                and marker in (sensitive_scalar_values or set())
            ):
                return 0
            return min(self.JS_SAFE_INTEGER_MAX, max(0, value))
        if type(value) is str and value.strip().isdigit():
            if value.strip() in sensitive_values:
                return 0
            try:
                return min(
                    self.JS_SAFE_INTEGER_MAX,
                    max(0, int(value.strip())),
                )
            except (TypeError, ValueError, OverflowError):
                return 0
        return 0

    @_public_api
    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _build_public_exchange(self, exchange: Any) -> Dict[str, Any]:
        public_exchange = dict(exchange) if isinstance(exchange, dict) else {}
        public_exchange["reserve"] = min(
            self.JS_SAFE_INTEGER_MAX,
            max(0, self._safe_int(self._reserve_magic_pill_count, 0)),
        )
        return public_exchange

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        pill_status = self.get_data("pill_status") or {}
        needs_refresh = not pill_status or pill_status.get("schema_version") != self.plugin_version
        if auto_refresh and needs_refresh:
            try:
                pill_status = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning(
                    "%s 初始化状态刷新失败：%s",
                    self.plugin_name,
                    self._get_error_detail(err),
                )

        pill_status = dict(pill_status) if isinstance(pill_status, dict) else {}
        pill_status["exchange"] = self._build_public_exchange(
            pill_status.get("exchange")
        )
        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        cookie_ready, cookie_source = self._cookie_status()
        return self._sanitize_public_response({
            "enabled": self._enabled,
            "notify": self._notify,
            "enable_brick": self._enable_brick,
            "enable_beach": self._enable_beach,
            "cookie_source": cookie_source,
            "cookie_ready": cookie_ready,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(next_trigger) if next_trigger else "",
            "next_trigger_action": self._get_scheduled_action_label(),
            "last_run": self.get_data("last_run") or "",
            "pill_status": pill_status,
            "history": (self.get_data("history") or [])[:10],
            "config": self._get_config(include_cookie=False),
        })

    def _is_pre_refresh_trigger(self) -> bool:
        mode, _ = self._parse_trigger_mode(self._load_saved_next_trigger_mode())
        return mode == "refresh"

    def _resolve_scheduled_action(self, force: bool, reason: str) -> str:
        base_reason, explicit_action = self._parse_run_reason(reason)
        if explicit_action:
            return explicit_action
        if base_reason in {"manual", "manual-api", "onlyonce"}:
            return "all"
        return self._get_scheduled_action()

    @staticmethod
    def _parse_run_reason(reason: str) -> Tuple[str, str]:
        reason_text = str(reason or "manual").strip().lower() or "manual"
        base_reason, separator, action = reason_text.rpartition(":")
        if separator and base_reason and action in {"brick", "beach", "all"}:
            return base_reason, action
        return reason_text, ""

    def _get_scheduled_action(self) -> str:
        _, action = self._parse_trigger_mode(self._load_saved_next_trigger_mode())
        return action

    def _get_scheduled_action_label(self) -> str:
        action = self._get_scheduled_action()
        return {
            "brick": "搬砖",
            "beach": "清沙滩",
            "all": "整轮执行",
        }.get(action, "整轮执行")

    def _parse_trigger_mode(self, raw_mode: Optional[str]) -> Tuple[str, str]:
        mode_text = str(raw_mode or "run").strip().lower() or "run"
        if ":" in mode_text:
            mode, action = mode_text.split(":", 1)
        else:
            mode, action = mode_text, "all"
        if mode not in {"run", "refresh"}:
            mode = "run"
        if action not in {"all", "brick", "beach"}:
            action = "all"
        return mode, action

    def _merge_trigger_actions(self, primary: str, secondary: str) -> str:
        first = primary if primary in {"brick", "beach", "all"} else ""
        second = secondary if secondary in {"brick", "beach", "all"} else ""
        if not first:
            return second or "all"
        if not second or first == second:
            return first
        return "all"

    @_config_public_api
    def _get_config(
        self,
        include_options: bool = True,
        include_cookie: bool = True,
    ) -> Dict[str, Any]:
        config = {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "enable_brick": self._enable_brick,
            "enable_beach": self._enable_beach,
            "auto_craft": self._auto_craft,
            "auto_exchange": self._auto_exchange,
            "use_proxy": self._use_proxy,
            "cookie": self._manual_cookie,
            "brick_cron": self._brick_cron,
            "schedule_buffer_seconds": self._schedule_buffer_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "move_delay_min_ms": self._move_delay_min_ms,
            "move_delay_max_ms": self._move_delay_max_ms,
            "ready_retry_seconds": self._ready_retry_seconds,
            "reserve_magic_pill_count": self._reserve_magic_pill_count,
        }
        if include_options:
            config["capture_tips"] = []
            config["upgrade_restart_required"] = (
                self._upgrade_restart_required()
            )
        if not include_cookie:
            config.pop("cookie", None)
        return config

    @_config_public_api
    def _save_config(self, config_payload: dict):
        activity_entered = False
        with self._explicit_lifecycle() as was_stopping:
            if self._upgrade_restart_required():
                return {
                    "success": False,
                    "message": "Vue-魔丸升级尚未完成，请重启 MoviePilot 后再保存配置",
                }
            current = self._get_config(include_options=False)
            normalized_payload, errors = self._validate_save_config_payload(
                config_payload,
                current,
            )
            if errors:
                return {
                    "success": False,
                    "message": next(iter(errors.values())),
                    "errors": errors,
                }
            before_refresh = self._capture_refresh_catchup_state()
            merged = self._merge_public_config(
                current,
                normalized_payload,
            )
            requested_onlyonce = self._to_bool(merged.get("onlyonce", False))
            if was_stopping:
                self._clear_migration_stopping()
            try:
                self._init_plugin_locked(
                    merged,
                    preserve_running_onlyonce=False,
                )
                onlyonce_queued = bool(
                    requested_onlyonce
                    and self._scheduler
                    and self._scheduler.running
                )
                if not onlyonce_queued:
                    self._update_config()
                    self._enter_migration_activity()
                    activity_entered = True
            except Exception:
                if was_stopping:
                    self._mark_migration_stopping()
                raise

        if onlyonce_queued:
            status = self.get_data("pill_status") or {}
            return {
                "success": True,
                "message": "配置已保存，已排队一次性执行",
                "config": self._get_config(),
                "pill_status": status,
                "status": self._build_status(auto_refresh=False),
            }

        try:
            catchup_result: Optional[Dict[str, Any]] = None
            try:
                status = self._refresh_state(reason="save-config")
                catchup_result = self._run_after_refresh_if_due(
                    status,
                    run_reason="save-config",
                    refresh_reason="save-config",
                    before_refresh=before_refresh,
                )
            except Exception as err:
                logger.warning(
                    "%s 保存配置后刷新失败：%s",
                    self.plugin_name,
                    self._get_error_detail(err),
                )
                status = self.get_data("pill_status") or {}
                if self._enabled and not (self._scheduler and self._scheduler.running):
                    self._reregister_plugin("save-config")
            message = "配置已保存"
            if catchup_result:
                message = "配置已保存，已执行补跑" if catchup_result.get("success", True) else f"配置已保存，补跑失败：{catchup_result.get('message') or '未知原因'}"
            return {
                "success": True,
                "message": message,
                "config": self._get_config(),
                "pill_status": (catchup_result or {}).get("pill_status") or status,
                "status": (catchup_result or {}).get("status") or self._build_status(auto_refresh=False),
            }
        finally:
            if activity_entered:
                self._exit_migration_activity()

    def _sync_site_cookie_api(self):
        result = self._sync_cookie_from_site(save_config=True, silent=False)
        if result.get("success") and self._enabled:
            self._reregister_plugin("sync-cookie")
        return {**result, "config": self._get_config(), "status": self._build_status(auto_refresh=False)}

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "enable_brick": True,
            "enable_beach": True,
            "auto_craft": False,
            "auto_exchange": False,
            "use_proxy": False,
            "cookie": "",
            "brick_cron": self.DEFAULT_BRICK_CRON,
            "schedule_buffer_seconds": 5,
            "random_delay_max_seconds": 3,
            "http_timeout": 12,
            "http_retry_times": self.MAX_NETWORK_RETRY_TIMES,
            "http_retry_delay": 1500,
            "move_delay_min_ms": 30,
            "move_delay_max_ms": 80,
            "ready_retry_seconds": 60,
            "reserve_magic_pill_count": 10,
        }

    def _merge_public_config(self, *configs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = self._default_config()
        allowed_keys = set(merged)
        for config in configs:
            if not isinstance(config, dict):
                continue
            for key in allowed_keys:
                if key in config:
                    merged[key] = config[key]
        return merged

    @classmethod
    def _parse_config_integer(
        cls,
        field: str,
        value: Any,
    ) -> Tuple[Optional[int], str]:
        label, minimum, maximum, _ = cls.CONFIG_INTEGER_RULES[field]
        parsed: Optional[int] = None
        if type(value) is int:
            parsed = value
        elif (
            type(value) is str
            and cls._CANONICAL_CONFIG_INTEGER_PATTERN.fullmatch(value)
        ):
            try:
                parsed = int(value)
            except (TypeError, ValueError, OverflowError):
                parsed = None

        if parsed is None or abs(parsed) > cls.JS_SAFE_INTEGER_MAX:
            return None, f"{label}必须填写规范整数"
        if parsed < minimum or parsed > maximum:
            return None, f"{label}必须在 {minimum} 到 {maximum} 之间"
        return parsed, ""

    @classmethod
    def _parse_cron_value(
        cls,
        value: str,
        minimum: int,
        maximum: int,
        names: Optional[Dict[str, int]],
    ) -> Optional[int]:
        if cls._CRON_NUMBER_PATTERN.fullmatch(value):
            try:
                parsed = int(value)
            except (TypeError, ValueError, OverflowError):
                return None
            return parsed if minimum <= parsed <= maximum else None
        if names and value in names:
            return names[value]
        return None

    @classmethod
    def _validate_cron_item(
        cls,
        item: str,
        minimum: int,
        maximum: int,
        names: Optional[Dict[str, int]],
    ) -> bool:
        step_parts = item.split("/")
        if len(step_parts) > 2 or any(not part for part in step_parts):
            return False

        base = step_parts[0]
        step: Optional[int] = None
        if len(step_parts) == 2:
            if not cls._CRON_NUMBER_PATTERN.fullmatch(step_parts[1]):
                return False
            try:
                step = int(step_parts[1])
            except (TypeError, ValueError, OverflowError):
                return False
            if step <= 0:
                return False

        if base == "*":
            start, end = minimum, maximum
        elif "-" in base:
            range_parts = base.split("-")
            if len(range_parts) != 2 or any(not part for part in range_parts):
                return False
            start = cls._parse_cron_value(
                range_parts[0], minimum, maximum, names
            )
            end = cls._parse_cron_value(
                range_parts[1], minimum, maximum, names
            )
            if start is None or end is None or start > end:
                return False
        else:
            if step is not None:
                return False
            return cls._parse_cron_value(base, minimum, maximum, names) is not None

        return step is None or step <= end - start

    @classmethod
    def _validate_cron_field(
        cls,
        field: str,
        minimum: int,
        maximum: int,
        names: Optional[Dict[str, int]],
    ) -> bool:
        items = field.split(",")
        if not items or any(not item for item in items):
            return False
        if len(items) > 1 and any(item.startswith("*") for item in items):
            return False
        return all(
            cls._validate_cron_item(item, minimum, maximum, names)
            for item in items
        )

    @classmethod
    def _parse_config_cron(cls, value: Any) -> Tuple[Optional[str], str]:
        if not isinstance(value, str) or not value.strip():
            return None, "搬砖 Cron 不能为空"
        if "\r" in value or "\n" in value:
            return None, "搬砖 Cron 不能包含换行"

        fields = re.split(r"[ \t]+", value.strip())
        if len(fields) != 5:
            return None, "搬砖 Cron 必须是 5 段表达式"
        normalized_fields = [field.lower() for field in fields]
        for index, field in enumerate(normalized_fields):
            label, minimum, maximum, names = cls._CRON_FIELD_RULES[index]
            if not cls._validate_cron_field(
                field,
                minimum,
                maximum,
                names,
            ):
                return None, f"搬砖 Cron 的{label}段不合法"

        normalized = " ".join(normalized_fields)
        try:
            CronTrigger.from_crontab(normalized, timezone=settings.TZ)
        except Exception:
            return None, "搬砖 Cron 不是有效表达式"
        return normalized, ""

    def _validate_save_config_payload(
        self,
        payload: Any,
        current: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        if not isinstance(payload, dict):
            return {}, {"config": "配置内容格式不正确"}

        allowed_keys = set(self._default_config())
        normalized = {
            key: payload[key]
            for key in allowed_keys
            if key in payload
        }
        errors: Dict[str, str] = {}
        for field in self.CONFIG_INTEGER_RULES:
            if field not in normalized:
                continue
            parsed, error = self._parse_config_integer(field, normalized[field])
            if error:
                errors[field] = error
            else:
                normalized[field] = parsed

        if "brick_cron" in normalized:
            cron, error = self._parse_config_cron(normalized["brick_cron"])
            if error:
                errors["brick_cron"] = error
            else:
                normalized["brick_cron"] = cron

        if "cookie" in normalized:
            cookie, error = self._parse_config_cookie(normalized["cookie"])
            if error:
                errors["cookie"] = error
            else:
                normalized["cookie"] = cookie

        if not errors:
            merged = self._merge_public_config(current, normalized)
            if merged["move_delay_max_ms"] < merged["move_delay_min_ms"]:
                errors["move_delay_max_ms"] = "搬砖最大延迟不能小于最小延迟"
        return normalized, errors

    def _coerce_stored_config_integer(self, field: str, value: Any) -> int:
        _, minimum, maximum, default = self.CONFIG_INTEGER_RULES[field]
        parsed = self._safe_int(value, default)
        return min(maximum, max(minimum, parsed))

    def _coerce_stored_config_cron(self, value: Any) -> str:
        normalized, error = self._parse_config_cron(value)
        return self.DEFAULT_BRICK_CRON if error else normalized

    @classmethod
    def _parse_config_cookie(cls, value: Any) -> Tuple[Optional[str], str]:
        if not isinstance(value, str):
            return None, "站点 Cookie 必须是文本"
        if "\r" in value or "\n" in value:
            return None, "站点 Cookie 不能包含换行"
        cookie = value.strip()
        if len(cookie) > cls.MAX_MANUAL_COOKIE_LENGTH:
            return None, "站点 Cookie 内容过长"
        if cookie.lower() == "cookie":
            return None, "站点 Cookie 不是有效内容"
        if cls._contains_control_characters(cookie):
            return None, "站点 Cookie 包含不允许的控制字符"
        return cookie, ""

    def _coerce_stored_config_cookie(self, value: Any) -> str:
        cookie, error = self._parse_config_cookie(value)
        return "" if error else cookie

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._enable_brick = self._to_bool(config.get("enable_brick", True))
        self._enable_beach = self._to_bool(config.get("enable_beach", True))
        self._auto_craft = self._to_bool(config.get("auto_craft", False))
        self._auto_exchange = self._to_bool(config.get("auto_exchange", False))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._manual_cookie = self._coerce_stored_config_cookie(
            config.get("cookie", "")
        )
        self._brick_cron = self._coerce_stored_config_cron(config.get("brick_cron"))
        self._schedule_buffer_seconds = self._coerce_stored_config_integer(
            "schedule_buffer_seconds", config.get("schedule_buffer_seconds")
        )
        self._random_delay_max_seconds = self._coerce_stored_config_integer(
            "random_delay_max_seconds", config.get("random_delay_max_seconds")
        )
        self._http_timeout = self._coerce_stored_config_integer(
            "http_timeout", config.get("http_timeout")
        )
        self._http_retry_times = self._coerce_stored_config_integer(
            "http_retry_times", config.get("http_retry_times")
        )
        self._http_retry_delay = self._coerce_stored_config_integer(
            "http_retry_delay", config.get("http_retry_delay")
        )
        self._move_delay_min_ms = self._coerce_stored_config_integer(
            "move_delay_min_ms", config.get("move_delay_min_ms")
        )
        move_delay_max = self._coerce_stored_config_integer(
            "move_delay_max_ms", config.get("move_delay_max_ms")
        )
        self._move_delay_max_ms = max(self._move_delay_min_ms, move_delay_max)
        self._ready_retry_seconds = self._coerce_stored_config_integer(
            "ready_retry_seconds", config.get("ready_retry_seconds")
        )
        self._reserve_magic_pill_count = self._coerce_stored_config_integer(
            "reserve_magic_pill_count", config.get("reserve_magic_pill_count")
        )

    def _update_config(self):
        return self.update_config(self._get_config(include_options=False))

    def _get_error_retry_count(self) -> int:
        return max(0, self._safe_int(self.get_data("consecutive_error_retries"), 0))

    def _record_error_retry(self, detail: str = "") -> int:
        count = self._get_error_retry_count() + 1
        self.save_data("consecutive_error_retries", count)
        if detail:
            self.save_data("last_error_retry_detail", detail)
        return count

    def _reset_error_retry_count(self):
        if self._get_error_retry_count():
            self.save_data("consecutive_error_retries", 0)
            self.save_data("last_error_retry_detail", "")

    def _can_schedule_error_retry(self, count: Optional[int] = None) -> bool:
        retry_count = self._get_error_retry_count() if count is None else max(0, int(count))
        if retry_count <= self.MAX_CONSECUTIVE_ERROR_RETRIES:
            return True
        logger.warning(
            "%s 已连续失败 %s 次，停止短间隔自动重试，等待下一次正常调度",
            self.plugin_name,
            retry_count,
        )
        return False

    def _limit_retry_plan_if_needed(
        self,
        retry_action: str,
        retry_ts: int,
        next_run: Optional[int],
        next_action: str,
        reason: str = "",
    ) -> Tuple[Optional[int], str]:
        retry_count = self._record_error_retry(f"短间隔重试:{retry_action}")
        if not self._can_schedule_error_retry(retry_count):
            return next_run, next_action
        if not next_run or retry_ts < next_run:
            return retry_ts, retry_action
        if retry_ts == next_run:
            return next_run, self._merge_trigger_actions(next_action, retry_action)
        if retry_action == "beach" and next_action not in {"beach", "all"} and reason == "schedule":
            return retry_ts, retry_action
        return next_run, next_action

    @_migration_activity
    def _refresh_state(
        self,
        reason: str = "refresh",
        record_run: bool = True,
        commit_plan: bool = True,
    ) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        data = self._fetch_page_state(session)
        if commit_plan:
            next_run, next_action = self._compute_next_plan(data)
            self._schedule_next_run(next_run, reason, next_action)
        else:
            planned_run, _, trigger_mode, _ = self._load_plan_snapshot()
            next_run = int(planned_run.timestamp()) if planned_run else None
            _, next_action = self._parse_trigger_mode(trigger_mode)
        status = self._refresh_and_store_status(data, next_run, [], record_run=record_run, next_action=next_action)
        self._reset_error_retry_count()
        return status

    def _ensure_cookie(self):
        manual_cookie = self._manual_cookie
        if self._is_valid_cookie_value(manual_cookie):
            with self._site_credentials_lock:
                (
                    self._siteoper,
                    self._cookie,
                    self._cookie_source,
                    self._site_domain,
                    self._site_url,
                    self._user_agent,
                ) = (
                    None,
                    manual_cookie,
                    "手动配置",
                    self.DEFAULT_SITE_DOMAIN,
                    self.DEFAULT_SITE_URL,
                    self.DEFAULT_USER_AGENT,
                )
            return
        self._sync_site_credentials()

    def _reset_runtime_site_credentials(self):
        with self._site_credentials_lock:
            (
                self._siteoper,
                self._cookie,
                self._cookie_source,
                self._site_domain,
                self._site_url,
                self._user_agent,
            ) = (
                None,
                "",
                "未同步",
                self.DEFAULT_SITE_DOMAIN,
                self.DEFAULT_SITE_URL,
                self.DEFAULT_USER_AGENT,
            )

    def _site_credentials_snapshot(self) -> Tuple[Any, str, str, str, str, str]:
        with self._site_credentials_lock:
            return (
                self._siteoper,
                self._cookie,
                self._cookie_source,
                self._site_domain,
                self._site_url,
                self._user_agent,
            )

    @staticmethod
    def _site_value(site: Any, key: str) -> Any:
        if isinstance(site, dict):
            return site.get(key)
        return getattr(site, key, None)

    @staticmethod
    def _is_valid_cookie_value(cookie: Any) -> bool:
        return (
            isinstance(cookie, str)
            and bool(cookie.strip())
            and cookie.strip().lower() != "cookie"
        )

    @staticmethod
    def _cookie_sensitive_values(cookie: Any) -> Tuple[str, ...]:
        if not isinstance(cookie, str) or not cookie.strip():
            return ()
        values = [cookie.strip()]
        for part in cookie.split(";"):
            _, separator, raw_value = part.partition("=")
            if not separator:
                continue
            secret = raw_value.strip().strip("\"'")
            if len(secret) >= 4:
                values.append(secret)
        return tuple(dict.fromkeys(values))

    def _has_valid_cookie(self) -> bool:
        _, cookie, _, _, _, _ = self._site_credentials_snapshot()
        return self._is_valid_cookie_value(cookie)

    def _cookie_status(self) -> Tuple[bool, str]:
        if self._is_valid_cookie_value(self._manual_cookie):
            return True, "手动配置"
        _, cookie, cookie_source, _, _, _ = self._site_credentials_snapshot()
        return self._is_valid_cookie_value(cookie), cookie_source

    def _sync_site_credentials(self):
        with self._site_credentials_lock:
            self._sync_site_credentials_locked()

    def _sync_site_credentials_locked(self):
        siteoper = None
        site = None
        site_found = False
        raw_cookie = None
        raw_site_url = None
        raw_user_agent = None
        try:
            siteoper = SiteOper()
            site = siteoper.get_by_domain(self.DEFAULT_SITE_DOMAIN)
            site_found = bool(site)
            if site_found:
                raw_cookie = self._site_value(site, "cookie")
                raw_site_url = self._site_value(site, "url")
                raw_user_agent = self._site_value(site, "ua")
        except Exception as err:
            sensitive_values = self._cookie_sensitive_values(raw_cookie)
            self._attach_error_sensitive_values(err, sensitive_values)
            detail = self._get_error_detail(err)
            wrapped_error = ValueError(
                f"读取站点 {self.DEFAULT_SITE_DOMAIN} 配置失败：{detail}"
            )
            self._attach_error_sensitive_values(
                wrapped_error,
                sensitive_values,
            )
            self._reset_runtime_site_credentials()
            raise wrapped_error from err

        if not site_found:
            self._reset_runtime_site_credentials()
            raise ValueError(f"未找到站点 {self.DEFAULT_SITE_DOMAIN} 的配置")

        cookie = raw_cookie.strip() if isinstance(raw_cookie, str) else ""
        if not self._is_valid_cookie_value(cookie):
            self._reset_runtime_site_credentials()
            raise ValueError(f"站点 {self.DEFAULT_SITE_DOMAIN} 未配置有效 Cookie")

        site_url = (
            raw_site_url.strip().rstrip("/")
            if isinstance(raw_site_url, str) and raw_site_url.strip()
            else self.DEFAULT_SITE_URL
        )
        user_agent = (
            raw_user_agent.strip()
            if isinstance(raw_user_agent, str) and raw_user_agent.strip()
            else self.DEFAULT_USER_AGENT
        )
        (
            self._siteoper,
            self._cookie,
            self._cookie_source,
            self._site_domain,
            self._site_url,
            self._user_agent,
        ) = (
            siteoper,
            cookie,
            f"站点同步：{self.DEFAULT_SITE_DOMAIN}",
            self.DEFAULT_SITE_DOMAIN,
            site_url,
            user_agent,
        )

    def _sync_cookie_from_site(self, save_config: bool = False, silent: bool = True) -> Dict[str, Any]:
        try:
            self._sync_site_credentials()
            if save_config:
                self._update_config()
            if not silent:
                logger.info("%s 已同步站点 Cookie", self.plugin_name)
            _, _, cookie_source, _, _, _ = self._site_credentials_snapshot()
            return {
                "success": True,
                "message": f"已同步站点 Cookie：{self.DEFAULT_SITE_DOMAIN}",
                "cookie_ready": True,
                "cookie_source": cookie_source,
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 同步站点 Cookie 失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _build_site_client(self) -> VuePillSiteClient:
        _, cookie, _, _, site_url, user_agent = self._site_credentials_snapshot()
        return VuePillSiteClient(
            site_url=site_url,
            cookie=cookie,
            user_agent=user_agent,
            timeout=self._http_timeout,
            retry_times=self._http_retry_times,
            retry_delay_ms=self._http_retry_delay,
            use_proxy=self._use_proxy,
            logger=logger,
        )

    def _build_session(self):
        client = self._build_site_client()
        session = client.build_session()
        try:
            setattr(session, "_vuepill_site_client", client)
        except Exception:
            pass
        return session

    def _site_client_for_session(self, session) -> VuePillSiteClient:
        try:
            client = getattr(session, "_vuepill_site_client", None)
        except Exception:
            client = None
        return client if isinstance(client, VuePillSiteClient) else self._build_site_client()

    def _fetch_page_state(self, session) -> Dict[str, Any]:
        client = self._site_client_for_session(session)
        data = parse_page(client.fetch_page_html(_SiteSessionAdapter(session)))
        if data.get("parse_complete") is not True:
            parse_error = str(data.get("parse_error") or "页面结构不完整").strip()
            raise ValueError(f"魔丸页面解析失败：{parse_error}")
        return data

    def _fetch_stable_page_state(
        self,
        session,
        previous_page: Optional[Dict[str, Any]] = None,
        expect_brick_update: bool = False,
        expect_beach_cooldown: bool = False,
    ) -> Dict[str, Any]:
        page = self._fetch_page_state(session)
        prev_brick = (previous_page or {}).get("brick") or {}
        prev_beach = (previous_page or {}).get("beach") or {}
        prev_daily = self._safe_int(prev_brick.get("daily_bricks"), 0)
        prev_bag = self._safe_int(prev_brick.get("bag_count"), 0)

        for wait_seconds in (0.6, 1.2):
            brick = page.get("brick") or {}
            beach = page.get("beach") or {}
            brick_stale = (
                expect_brick_update
                and self._safe_int(brick.get("daily_bricks"), 0) <= prev_daily
                and self._safe_int(brick.get("bag_count"), 0) <= prev_bag
                and bool(brick.get("ready")) == bool(prev_brick.get("ready"))
            )
            beach_stale = (
                expect_beach_cooldown
                and bool(beach.get("ready"))
                and not self._safe_int(beach.get("next_ready_ts"), 0)
                and bool(prev_beach.get("ready"))
            )
            if not brick_stale and not beach_stale:
                break
            time.sleep(wait_seconds)
            page = self._fetch_page_state(session)

        return page

    def _refresh_beach_due_page(self, session, page: Dict[str, Any]) -> Dict[str, Any]:
        current = page
        try:
            current = self._fetch_stable_page_state(session, previous_page=page)
        except Exception as err:
            logger.warning("%s 沙滩到点重刷状态失败：%s", self.plugin_name, self._get_error_detail(err))
            return current
        if self._is_beach_ready(current.get("beach") or {}):
            return current

        for wait_seconds in (0.8, 1.5):
            time.sleep(wait_seconds)
            try:
                current = self._fetch_page_state(session)
            except Exception as err:
                logger.warning("%s 沙滩到点延迟重刷状态失败：%s", self.plugin_name, self._get_error_detail(err))
                break
            if self._is_beach_ready(current.get("beach") or {}):
                break
        return current

    def _post_action(
        self,
        session,
        action: str,
        payload: Optional[dict] = None,
        retry_network: bool = False,
    ) -> dict:
        try:
            return self._site_client_for_session(session).post_action(
                _SiteSessionAdapter(
                    session,
                    json_filter=self._sanitize_site_action_result,
                ),
                action,
                payload=payload,
                retry_network=retry_network,
            )
        except VuePillActionError as err:
            detail = self._get_error_detail(err)
            prefix = f"Action {action} failed: "
            if detail.startswith(prefix):
                detail = detail[len(prefix):]
            raise ValueError(detail) from None

    def _sanitize_site_action_result(self, result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        safe_result = dict(result)
        for key in ("message", "msg"):
            value = result.get(key)
            if not isinstance(value, str):
                continue
            safe_message = self._safe_result_message(result, value)
            safe_result[key] = re.sub(
                r"(?i)\b(?:cookie|set-cookie|authorization|proxy-authorization|"
                r"[a-z0-9_-]*(?:token|password|passwd|session|secret)[a-z0-9_-]*|"
                r"sid|api[_-]?key|target[_-]?uid|uid|user[_-]?id)\b"
                r"(?=[\"']?\s*[:=])",
                "sensitive",
                safe_message,
            )
        return safe_result

    def _run_brick_flow(self, session, brick_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        total_moved = 0
        last_message = ""
        warning = ""
        next_reset_ts = 0
        attempted = False
        brick_state = brick_state or {}
        daily_limit = max(1, self._safe_int(brick_state.get("daily_limit"), 50))
        daily_bricks = max(0, self._safe_int(brick_state.get("daily_bricks"), 0))
        remaining_quota = max(0, daily_limit - daily_bricks)
        loop_cap = max(1, min(400, (remaining_quota if remaining_quota > 0 else daily_limit) * 8))

        for _ in range(loop_cap):
            attempted = True
            try:
                result = self._post_action(session, "move_brick", retry_network=True)
            except Exception as err:
                warning = self._get_error_detail(err)
                if total_moved > 0:
                    try:
                        latest_page = self._fetch_page_state(session)
                        latest_brick = latest_page.get("brick") or {}
                        latest_limit = max(1, self._safe_int(latest_brick.get("daily_limit"), daily_limit))
                        latest_daily = max(0, self._safe_int(latest_brick.get("daily_bricks"), daily_bricks))
                        next_reset_ts = self._safe_int(latest_brick.get("next_reset_ts"), 0)
                        if latest_brick.get("ready") and latest_daily < latest_limit:
                            delay_ms = random.randint(self._move_delay_min_ms, self._move_delay_max_ms)
                            if delay_ms > 0:
                                time.sleep(delay_ms / 1000.0)
                            continue
                    except Exception:
                        pass
                break

            if result and result.get("success"):
                public_result = self._safe_result_data(result)
                last_message = self._safe_result_message(result, "").strip()
                moved = self._safe_int(public_result.get("bricks_moved"), 0)
                if moved <= 0:
                    if any(token in last_message for token in ("已满", "上限", "不能", "冷却", "结束")):
                        break
                    moved = 1
                total_moved += moved
                if remaining_quota > 0 and total_moved >= remaining_quota:
                    break
                delay_ms = random.randint(self._move_delay_min_ms, self._move_delay_max_ms)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                continue

            public_result = self._safe_result_data(result)
            last_message = self._safe_result_message(result, "今日搬砖已满")
            next_reset_ts = self._safe_int(public_result.get("next_brick_reset_ts"), 0)
            if total_moved > 0:
                try:
                    latest_page = self._fetch_page_state(session)
                    latest_brick = latest_page.get("brick") or {}
                    latest_limit = max(1, self._safe_int(latest_brick.get("daily_limit"), daily_limit))
                    latest_daily = max(0, self._safe_int(latest_brick.get("daily_bricks"), daily_bricks))
                    next_reset_ts = self._safe_int(latest_brick.get("next_reset_ts"), next_reset_ts)
                    if latest_brick.get("ready") and latest_daily < latest_limit:
                        delay_ms = random.randint(self._move_delay_min_ms, self._move_delay_max_ms)
                        if delay_ms > 0:
                            time.sleep(delay_ms / 1000.0)
                        continue
                except Exception:
                    pass
            break

        return {
            "moved": total_moved,
            "message": last_message,
            "warning": warning,
            "next_reset_ts": next_reset_ts,
            "attempted": attempted,
        }

    def _run_beach_flow(self, session) -> Dict[str, Any]:
        try:
            enter = self._post_action(session, "enter_beach", retry_network=False)
        except Exception as err:
            return {
                "items": [],
                "message": "",
                "warning": self._get_error_detail(err),
                "done": False,
                "attempted": True,
            }

        if not enter or not enter.get("success", False):
            message = self._safe_result_message(enter, "沙滩冷却中")
            return {
                "items": [],
                "message": "",
                "warning": message,
                "done": False,
                "attempted": True,
            }

        return self._collect_beach_trash(session)

    def _execute_beach_flow(
        self,
        session,
        beach_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        beach = beach_state if isinstance(beach_state, dict) else {}
        if bool(
            beach.get("can_collect")
            or beach.get("has_trash")
            or beach.get("collect_enabled")
        ):
            return self._collect_beach_trash(session)
        return self._run_beach_flow(session)

    def _collect_beach_trash(self, session) -> Dict[str, Any]:
        try:
            result = self._post_action(session, "collect_all_trash", retry_network=False)
        except Exception as err:
            return {
                "items": [],
                "message": "",
                "warning": self._get_error_detail(err),
                "done": False,
                "attempted": True,
            }

        if result and result.get("success", False):
            public_result = self._safe_result_data(result)
            items = self._normalize_collected_items(public_result)
            return {
                "items": items,
                "message": self._safe_result_message(result, "").strip(),
                "warning": "",
                "done": True,
                "attempted": True,
            }
        return {
            "items": [],
            "message": "",
            "warning": self._safe_result_message(result, "一键收集失败"),
            "done": False,
            "attempted": True,
        }

    def _manual_move_bricks(self) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        page = self._fetch_page_state(session)
        initial_page = page
        if not page.get("brick", {}).get("ready"):
            lines = [f"ℹ️ 搬砖：{page.get('brick', {}).get('status_text') or '今日搬砖已满'}"]
            next_run, next_action = self._compute_next_plan(page)
            pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
            return {"pill_status": pill_status, "lines": lines}

        result = self._run_brick_flow(session, page.get("brick") or {})
        page = self._fetch_stable_page_state(
            session,
            previous_page=page,
            expect_brick_update=self._safe_int(result.get("moved"), 0) > 0,
        )
        result = self._sync_brick_result_with_page(result, initial_page, page)
        next_run, next_action = self._compute_next_plan(page)
        if page.get("brick", {}).get("ready") and (result.get("warning") or result.get("attempted")):
            retry_ts = int(time.time()) + self._ready_retry_seconds
            if not next_run or retry_ts < next_run:
                next_run, next_action = retry_ts, "brick"
            elif retry_ts == next_run:
                next_action = self._merge_trigger_actions(next_action, "brick")
        self._schedule_next_run(next_run, "manual-move", next_action)

        lines = []
        if result.get("moved"):
            lines.append(f"🧱 搬砖：🧱砖块×{result.get('moved')}")
        if result.get("warning"):
            lines.append(f"⚠️ 搬砖失败：{result.get('warning')}")
        elif result.get("message") and not result.get("moved"):
            lines.append(f"ℹ️ 搬砖：{result.get('message')}")
        if result.get("attempted") and page.get("brick", {}).get("ready"):
            remaining = max(
                0,
                self._safe_int((page.get("brick") or {}).get("daily_limit"), 50)
                - self._safe_int((page.get("brick") or {}).get("daily_bricks"), 0),
            )
            if remaining > 0:
                lines.append(f"⏳ 搬砖剩余：{remaining} 次，60秒后重试")
        if not lines:
            lines.append("ℹ️ 本次无可执行动作")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("🧱 手动搬砖", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _sync_brick_result_with_page(
        self,
        brick_result: Optional[Dict[str, Any]],
        before_page: Optional[Dict[str, Any]],
        after_page: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        result = dict(brick_result or {})
        before_brick = (before_page or {}).get("brick") or {}
        after_brick = (after_page or {}).get("brick") or {}
        before_daily = max(0, self._safe_int(before_brick.get("daily_bricks"), 0))
        after_daily = max(0, self._safe_int(after_brick.get("daily_bricks"), before_daily))
        actual_moved = max(0, after_daily - before_daily)
        reported_moved = max(0, self._safe_int(result.get("moved"), 0))
        if actual_moved > reported_moved:
            result["moved"] = actual_moved
        result["next_reset_ts"] = self._safe_int(
            after_brick.get("next_reset_ts"),
            self._safe_int(result.get("next_reset_ts"), 0),
        )
        return result

    def _manual_clean_beach(self) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        page = self._fetch_page_state(session)
        if not self._is_beach_ready(page.get("beach") or {}):
            lines = [f"ℹ️ 沙滩：{page.get('beach', {}).get('status_text') or '沙滩冷却中'}"]
            next_run, next_action = self._compute_next_plan(page)
            pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
            return {"pill_status": pill_status, "lines": lines}

        result = self._execute_beach_flow(session, page.get("beach") or {})
        page = self._fetch_stable_page_state(
            session,
            previous_page=page,
            expect_beach_cooldown=bool(result.get("done")),
        )
        auto_result: Dict[str, Any] = {}
        if result.get("done") and (self._auto_craft or self._auto_exchange):
            auto_result, page = self._run_auto_post_beach(session, page)
            page = self._fetch_stable_page_state(session, previous_page=page)
        next_run, next_action = self._compute_next_plan(page)
        if self._should_retry_beach(page.get("beach") or {}, result):
            retry_ts = int(time.time()) + self._ready_retry_seconds
            if not next_run or retry_ts < next_run:
                next_run, next_action = retry_ts, "beach"
            elif retry_ts == next_run:
                next_action = self._merge_trigger_actions(next_action, "beach")
        self._schedule_next_run(next_run, "manual-beach", next_action)

        lines = []
        items = result.get("items") or []
        if items:
            lines.append(f"🏖️ 沙滩：{self._format_item_lines(items)}")
        if result.get("warning"):
            lines.append(f"⚠️ 清沙滩失败：{result.get('warning')}")
        elif result.get("message") and not items:
            lines.append(f"ℹ️ 沙滩：{result.get('message')}")
        if auto_result.get("lines"):
            lines.extend(auto_result.get("lines") or [])
        if not lines:
            lines.append("ℹ️ 本次无可执行动作")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("🏖️ 手动清沙滩", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _manual_exchange_points(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        page = self._fetch_page_state(session)
        exchange = page.get("exchange") or {}
        max_count = self._safe_int(exchange.get("max_count"), 0)
        magic_pills = self._safe_int(exchange.get("magic_pills"), 0)
        exchangeable = max(0, magic_pills - self._reserve_magic_pill_count)
        if (
            max_count <= 0
            or exchangeable <= 0
            or not exchange.get("enabled")
        ):
            raise ValueError("当前没有可兑换的魔丸")

        quantity = self._safe_int(payload.get("quantity"), 0)
        exchange_quantity = min(
            max(1, quantity or 1),
            max_count,
            exchangeable,
        )
        result = self._post_action(
            session,
            "exchange_points",
            {"quantity": exchange_quantity},
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(self._safe_result_message(result, "兑换失败"))

        page = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-exchange", next_action)

        public_result = self._safe_result_data(result)
        gained = self._safe_int(public_result.get("points_gained"), 0)
        lines = [f"💰 兑换：魔丸×{exchange_quantity}"]
        if gained > 0:
            lines.append(f"✨ 获得：{gained} 魔力")
        elif public_result.get("message"):
            lines.append(f"ℹ️ {public_result.get('message')}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("💰 手动兑换", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _manual_craft_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        recipe_id = self._safe_int(payload.get("recipe_id"), 0)
        session = self._build_session()
        page = self._fetch_page_state(session)
        recipe = next((item for item in (page.get("recipes") or []) if self._safe_int(item.get("craft_id"), 0) == recipe_id), None)
        if not recipe or recipe.get("supported") is False:
            raise ValueError("未识别到对应配方")

        output_item = str(recipe.get("output_item") or recipe.get("title") or "").strip()
        if not output_item:
            raise ValueError("不支持的炼造配方")

        max_count = max(0, self._safe_int(recipe.get("max_count"), 0))
        if max_count <= 0 or not recipe.get("enabled"):
            raise ValueError(f"{output_item} 当前无法炼造")

        quantity = min(max(1, self._safe_int(payload.get("quantity"), 1)), max_count)
        result = self._post_action(
            session,
            "craft_item",
            {"recipe_id": recipe_id, "quantity": quantity},
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(self._safe_result_message(result, "炼造失败"))

        page = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-craft", next_action)

        icon = self.ITEM_ICON_MAP.get(output_item, "📦")
        lines = [f"⚒️ 炼造：{icon}{output_item}×{quantity}"]
        public_result = self._safe_result_data(result)
        if public_result.get("message"):
            lines.append(f"ℹ️ {public_result.get('message')}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("⚒️ 手动炼造", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _manual_craft_max_pill(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        page = self._fetch_page_state(session)
        plan_info = compute_magic_pill_plan(
            page.get("inventory") or [],
            page.get("recipes") or [],
        )
        max_count = self._safe_int(plan_info.get("max_count"), 0)
        if max_count <= 0:
            raise ValueError("当前材料不足，无法炼造魔丸")

        quantity = min(max(1, self._safe_int(payload.get("quantity"), max_count)), max_count)
        craft_result = self._craft_magic_pill_loop(session, page, target=quantity)

        page = craft_result.get("page") or page
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-craft-pill", next_action)

        crafted = self._safe_int(craft_result.get("crafted"), 0)
        target_count = self._safe_int(craft_result.get("target"), quantity)
        complete = bool(craft_result.get("complete"))
        partial = bool(craft_result.get("partial"))
        if complete:
            lines = [f"⚗️ 一键炼造魔丸：{crafted}颗"]
            history_title = "⚗️ 一键炼造魔丸"
        elif partial:
            lines = [f"⚠️ 一键炼造魔丸部分完成：{crafted}/{target_count}颗"]
            history_title = "⚠️ 一键炼造魔丸部分完成"
        else:
            lines = [f"⚠️ 一键炼造魔丸失败：{crafted}/{target_count}颗"]
            history_title = "❌ 一键炼造魔丸失败"
        if craft_result.get("craft_steps"):
            lines.append(f"🧪 步骤：{'  '.join(craft_result.get('craft_steps') or [])}")
        if craft_result.get("warning"):
            lines.append(f"⚠️ 炼造中止：{craft_result.get('warning')}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history(history_title, lines)
        return {
            "success": complete,
            "pill_status": pill_status,
            "lines": lines,
            "warning": craft_result.get("warning") or "",
            "crafted": crafted,
            "target": target_count,
            "partial": partial,
        }

    def _run_auto_post_beach(self, session, page: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        result = {
            "crafted": 0,
            "craft_target": 0,
            "craft_complete": True,
            "partial": False,
            "craft_steps": [],
            "exchanged": 0,
            "points": 0,
            "lines": [],
            "warning": "",
        }
        current_page = page or {}

        if self._auto_craft:
            craft_result = self._auto_craft_magic_pill(session, current_page)
            result["crafted"] += self._safe_int(craft_result.get("crafted"), 0)
            result["craft_target"] = self._safe_int(craft_result.get("target"), 0)
            result["craft_complete"] = bool(craft_result.get("complete"))
            result["partial"] = bool(craft_result.get("partial"))
            result["craft_steps"].extend(craft_result.get("craft_steps") or [])
            result["lines"].extend(craft_result.get("lines") or [])
            current_page = craft_result.get("page") or current_page
            if craft_result.get("warning") or not craft_result.get("success", True):
                result["warning"] = craft_result.get("warning") or "炼造目标未完成"
                outcome = "部分完成" if craft_result.get("partial") else "失败"
                result["lines"].append(
                    f"⚠️ 自动炼造{outcome}：{result['warning']}"
                )
                return result, current_page

        if self._auto_exchange:
            exchange_result = self._auto_exchange_points(session, current_page)
            result["exchanged"] += self._safe_int(exchange_result.get("exchanged"), 0)
            result["points"] += self._safe_int(exchange_result.get("points"), 0)
            result["lines"].extend(exchange_result.get("lines") or [])
            current_page = exchange_result.get("page") or current_page
            if exchange_result.get("warning"):
                result["warning"] = result["warning"] or exchange_result.get("warning")
                result["lines"].append(f"⚠️ 自动兑换失败：{exchange_result.get('warning')}")

        return result, current_page

    def _auto_craft_magic_pill(self, session, page: Dict[str, Any]) -> Dict[str, Any]:
        result = self._craft_magic_pill_loop(session, page)
        crafted = self._safe_int(result.get("crafted"), 0)
        target = self._safe_int(result.get("target"), 0)
        lines: List[str] = []
        if result.get("complete") and crafted > 0:
            lines.append(f"⚗️ 炼造：⚗️魔丸×{crafted}")
        elif result.get("partial"):
            lines.append(f"⚠️ 炼造部分完成：⚗️魔丸×{crafted}/{target}")
        if result.get("warning") and result.get("craft_steps"):
            lines.append(f"🧪 已完成：{'  '.join(result.get('craft_steps') or [])}")
        result["lines"] = lines
        return result

    def _craft_magic_pill_loop(
        self,
        session,
        page: Dict[str, Any],
        target: Optional[int] = None,
    ) -> Dict[str, Any]:
        current_page = page or {}
        first_plan = compute_magic_pill_plan(
            current_page.get("inventory") or [],
            current_page.get("recipes") or [],
            target=target,
        )
        goal = self._safe_int(first_plan.get("max_count"), 0)
        if goal <= 0:
            return {
                "success": True,
                "complete": True,
                "partial": False,
                "target": 0,
                "crafted": 0,
                "craft_steps": [],
                "lines": [],
                "warning": "",
                "page": current_page,
            }

        initial_magic_pills = self._page_magic_pill_count(current_page)
        crafted = 0
        executed_steps: List[str] = []
        warning = ""
        seen_steps = set()
        for _ in range(100):
            if crafted >= goal:
                break
            plan_info = compute_magic_pill_plan(
                current_page.get("inventory") or [],
                current_page.get("recipes") or [],
                target=goal - crafted,
            )
            steps = plan_info.get("steps") or []
            if not steps:
                warning = str(plan_info.get("reason") or "剩余炼造计划不可用")
                break

            step = steps[0]
            recipe_id = self._safe_int(step.get("craft_id"), 0)
            craft_qty = self._safe_int(step.get("count"), 0)
            output_item = str(step.get("output_item") or "").strip()
            stock_marker = tuple(sorted(inventory_to_map(current_page.get("inventory") or []).items()))
            step_marker = (stock_marker, recipe_id, craft_qty, output_item)
            if recipe_id <= 0 or craft_qty <= 0 or not output_item or step_marker in seen_steps:
                warning = "炼造页面未更新，已停止以避免重复提交"
                break
            seen_steps.add(step_marker)

            try:
                action_result = self._post_action(
                    session,
                    "craft_item",
                    {"recipe_id": recipe_id, "quantity": craft_qty},
                    retry_network=False,
                )
            except Exception as err:
                warning = self._get_error_detail(err)
                break
            if not isinstance(action_result, dict) or action_result.get("success") is not True:
                warning = self._safe_result_message(action_result, f"{output_item} 炼造失败")
                break

            executed_steps.append(
                f"{self.ITEM_ICON_MAP.get(output_item, '📦')}{output_item}×{craft_qty}"
            )
            try:
                current_page = self._fetch_page_state(session)
            except Exception as err:
                warning = self._get_error_detail(err)
                break
            crafted = max(
                crafted,
                self._page_magic_pill_count(current_page) - initial_magic_pills,
            )

        complete = crafted >= goal
        partial = 0 < crafted < goal
        if not complete and not warning:
            warning = f"炼造目标未完成，已确认 {crafted}/{goal} 颗"

        return {
            "success": complete,
            "complete": complete,
            "partial": partial,
            "target": goal,
            "crafted": crafted,
            "craft_steps": executed_steps,
            "lines": [],
            "warning": warning,
            "page": current_page,
        }

    def _page_magic_pill_count(self, page: Dict[str, Any]) -> int:
        inventory = inventory_to_map(
            self._get_inventory_items((page or {}).get("inventory"))
        )
        if "魔丸" in inventory:
            return self._safe_int(inventory.get("魔丸"), 0)
        return self._safe_int(((page or {}).get("stats") or {}).get("magic_pills"), 0)

    def _auto_exchange_points(self, session, page: Dict[str, Any]) -> Dict[str, Any]:
        current_page = page or {}
        exchanged = 0
        points = 0
        warning = ""
        seen_counts = set()

        for _ in range(1000):
            exchange = current_page.get("exchange") or {}
            inventory = inventory_to_map(
                self._get_inventory_items(current_page.get("inventory"))
            )
            current_count = self._safe_int(
                inventory.get("魔丸"),
                self._safe_int(exchange.get("magic_pills"), 0),
            )
            batches = exchange_batches(
                current_count,
                self._reserve_magic_pill_count,
                100,
            )
            if not batches or not exchange.get("enabled"):
                break
            if current_count in seen_counts:
                warning = "兑换页面未更新，已停止以保护保留魔丸"
                break
            seen_counts.add(current_count)

            batch = batches[0]
            page_max = self._safe_int(exchange.get("max_count"), 0)
            if page_max > 0:
                batch = min(batch, page_max)
            if batch <= 0:
                break

            try:
                action_result = self._post_action(
                    session,
                    "exchange_points",
                    {"quantity": batch},
                    retry_network=False,
                )
            except Exception as err:
                warning = self._get_error_detail(err)
                break
            if not isinstance(action_result, dict) or action_result.get("success") is not True:
                warning = self._safe_result_message(action_result, "兑换失败")
                break

            exchanged += batch
            public_result = self._safe_result_data(action_result)
            points += self._safe_int(public_result.get("points_gained"), 0)
            try:
                refreshed_page = self._fetch_page_state(session)
            except Exception as err:
                warning = self._get_error_detail(err)
                break
            refreshed_exchange = refreshed_page.get("exchange") or {}
            refreshed_inventory = inventory_to_map(
                self._get_inventory_items(refreshed_page.get("inventory"))
            )
            refreshed_count = self._safe_int(
                refreshed_inventory.get("魔丸"),
                self._safe_int(refreshed_exchange.get("magic_pills"), 0),
            )
            current_page = refreshed_page
            if refreshed_count >= current_count:
                warning = "兑换后库存未减少，已停止以保护保留魔丸"
                break

        lines: List[str] = []
        if exchanged > 0:
            lines.append(f"💰 兑换：⚗️魔丸×{exchanged}")
            if self._reserve_magic_pill_count > 0:
                lines.append(f"🧮 保留：⚗️魔丸≥{self._reserve_magic_pill_count}")
            if points > 0:
                lines.append(f"✨ 获得：{points} 魔力")
        return {
            "exchanged": exchanged,
            "points": points,
            "lines": lines,
            "warning": warning,
            "page": current_page,
        }

    @staticmethod
    def _get_inventory_items(inventory_data: Any) -> List[Dict[str, Any]]:
        if isinstance(inventory_data, list):
            return [item for item in inventory_data if isinstance(item, dict)]
        if isinstance(inventory_data, dict):
            items = inventory_data.get("items")
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []

    def _normalize_collected_items(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        collected = result.get("collected_items") or result.get("items") or {}
        if isinstance(collected, dict):
            for name, count in collected.items():
                qty = self._safe_int(count, 0)
                if qty <= 0:
                    continue
                items.append({
                    "name": str(name),
                    "count": qty,
                    "icon": self.ITEM_ICON_MAP.get(str(name), "📦"),
                })

        extra_magic_pill = max(
            self._safe_int(result.get("magic_pills_found"), 0),
            self._safe_int(result.get("magic_pills_gained"), 0),
            self._safe_int(result.get("pill_count"), 0),
        )
        if extra_magic_pill > 0:
            existing = next((item for item in items if item["name"] == "魔丸"), None)
            if existing:
                existing["count"] += extra_magic_pill
            else:
                items.append({"name": "魔丸", "count": extra_magic_pill, "icon": "⚗️"})
        return items

    def _get_retry_action(self, page: Dict[str, Any], brick_result: Dict[str, Any], beach_result: Dict[str, Any]) -> str:
        brick_retry = page.get("brick", {}).get("ready") and bool(brick_result.get("warning") or brick_result.get("attempted"))
        beach_retry = self._should_retry_beach(
            page.get("beach") or {},
            beach_result,
        )
        if brick_retry and beach_retry:
            return "all"
        if brick_retry:
            return "brick"
        if beach_retry:
            return "beach"
        return ""

    def _should_retry_beach(
        self,
        beach_state: Dict[str, Any],
        beach_result: Dict[str, Any],
    ) -> bool:
        if not beach_result:
            return False
        return bool(
            beach_result.get("attempted") and not beach_result.get("done")
            or beach_state.get("has_trash")
        )

    def _should_skip_run(self) -> bool:
        next_trigger = self._load_saved_next_trigger()
        if not next_trigger:
            return False
        return self._aware_now() < next_trigger

    def _get_next_run_for_service(self) -> Optional[datetime]:
        if self._bootstrap_pending:
            return self._aware_now() + timedelta(seconds=3)
        next_trigger = self._load_saved_next_trigger()
        if not next_trigger:
            return None
        now = self._aware_now()
        return next_trigger if next_trigger > now else now + timedelta(seconds=5)

    def _schedule_next_run(
        self,
        next_run_ts: Optional[int],
        reason: str = "",
        next_action: str = "all",
        force_run: bool = False,
    ):
        with self._plan_lock:
            should_register = self._commit_next_run_locked(
                next_run_ts,
                next_action,
                force_run=force_run,
            )
        if should_register:
            self._reregister_plugin(reason)

    def _commit_next_run_locked(
        self,
        next_run_ts: Optional[int],
        next_action: str,
        force_run: bool = False,
    ) -> bool:
        next_run_ts = self._normalize_timestamp(next_run_ts, 0)
        if next_run_ts and not self._is_reasonable_future_ts(next_run_ts, int(time.time()) - 1):
            next_run_ts = 0
        next_action = next_action if next_action in {"brick", "beach", "all"} else "all"
        if next_run_ts and next_run_ts > 0:
            next_run = self._aware_from_timestamp(next_run_ts)
            now = self._aware_now()
            pre_refresh_time = next_run - timedelta(seconds=self.PRE_REFRESH_SECONDS)
            if force_run:
                next_trigger = next_run + timedelta(seconds=self._schedule_buffer_seconds)
                min_trigger = now + timedelta(seconds=5)
                if next_trigger < min_trigger:
                    next_trigger = min_trigger
                trigger_mode = f"run:{next_action}"
            elif pre_refresh_time > now + timedelta(seconds=5):
                next_trigger = pre_refresh_time
                trigger_mode = f"refresh:{next_action}"
            else:
                next_trigger = next_run + timedelta(seconds=self._schedule_buffer_seconds)
                min_trigger = now + timedelta(seconds=5)
                if next_trigger < min_trigger:
                    next_trigger = min_trigger
                trigger_mode = f"run:{next_action}"
            self._next_run_time = next_run
            self._next_trigger_time = next_trigger
            self._next_trigger_mode = trigger_mode
            self.save_data("next_run_time", self._format_time(next_run))
            self.save_data("next_trigger_time", self._format_time(next_trigger))
            self.save_data("next_trigger_mode", trigger_mode)
            logger.info("INFO 最近可执行时间：%s", self._format_time(next_run))
            logger.info("INFO 计划触发时间：%s", self._format_time(next_trigger))
        else:
            self._next_run_time = None
            self._next_trigger_time = None
            self._next_trigger_mode = "run"
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", "")
            self.save_data("next_trigger_mode", "")
            logger.info("INFO 当前没有已识别的下一次执行时间")

        type(self)._plan_revision += 1
        should_register = self._enabled and not (
            self._scheduler and self._scheduler.running
        )
        if should_register:
            self._bootstrap_pending = not bool(next_run_ts)
        return should_register

    def _reregister_plugin(self, reason: str = ""):
        cls = type(self)
        with cls._migration_barrier:
            if cls._migration_stopping:
                logger.info(
                    "%s 已停止，跳过调度注册：%s",
                    self.plugin_name,
                    reason or "update",
                )
                return
            try:
                Scheduler().update_plugin_job(self.__class__.__name__)
                logger.info("%s 已重新注册调度：%s", self.plugin_name, reason or "update")
            except Exception:
                try:
                    Scheduler().reload_plugin_job(self.__class__.__name__)
                    logger.info("%s 已重新加载调度：%s", self.plugin_name, reason or "reload")
                except Exception as err:
                    logger.warning(
                        "%s 重新注册调度失败：%s",
                        self.plugin_name,
                        self._get_error_detail(err),
                    )

    def _load_saved_next_run(self) -> Optional[datetime]:
        with self._plan_lock:
            return self._load_saved_next_run_locked()

    def _load_saved_next_run_locked(self) -> Optional[datetime]:
        raw = self.get_data("next_run_time")
        if raw is None:
            raw = (self.get_data("state") or {}).get("next_run_time")
        if raw is not None:
            self._next_run_time = self._parse_datetime(raw) if raw else None
        return self._next_run_time

    def _load_saved_next_trigger(self) -> Optional[datetime]:
        with self._plan_lock:
            return self._load_saved_next_trigger_locked()

    def _load_saved_next_trigger_locked(self) -> Optional[datetime]:
        raw = self.get_data("next_trigger_time")
        if raw is None:
            raw = (self.get_data("state") or {}).get("next_trigger_time")
        if raw is not None:
            self._next_trigger_time = self._parse_datetime(raw) if raw else None
        return self._next_trigger_time

    def _load_saved_next_trigger_mode(self) -> str:
        with self._plan_lock:
            return self._load_saved_next_trigger_mode_locked()

    def _load_saved_next_trigger_mode_locked(self) -> str:
        raw = self.get_data("next_trigger_mode")
        if raw is None:
            raw = (self.get_data("state") or {}).get("next_trigger_mode")
        if raw is not None:
            self._next_trigger_mode = str(raw or "run").strip() or "run"
        return self._next_trigger_mode

    def _load_plan_snapshot(
        self,
    ) -> Tuple[Optional[datetime], Optional[datetime], str, int]:
        with self._plan_lock:
            return (
                self._load_saved_next_run_locked(),
                self._load_saved_next_trigger_locked(),
                self._load_saved_next_trigger_mode_locked(),
                type(self)._plan_revision,
            )

    def _compute_next_plan(self, data: dict) -> Tuple[Optional[int], str]:
        candidates: List[Tuple[int, str]] = []
        server_now = self._resolve_server_now(data.get("server_now"))
        if self._enable_brick:
            brick_next = self._get_cron_next_ts(self._brick_cron, server_now)
            if self._is_reasonable_future_ts(brick_next, server_now):
                candidates.append((brick_next, "brick"))
        if self._enable_beach:
            beach_next = self._normalize_timestamp((data.get("beach") or {}).get("next_ready_ts"), 0)
            if self._is_reasonable_future_ts(beach_next, server_now):
                candidates.append((beach_next, "beach"))
        if not candidates:
            return None, "all"
        next_run = min(item[0] for item in candidates)
        actions = [item[1] for item in candidates if item[0] == next_run]
        next_action = "all" if len(actions) > 1 else actions[0]
        return next_run, next_action

    def _get_cron_next_ts(self, cron_expr: str, server_now: Optional[Any] = None) -> Optional[int]:
        expr = (cron_expr or "").strip()
        if not expr:
            return None
        try:
            timezone = pytz.timezone(settings.TZ)
            now_ts = self._resolve_server_now(server_now)
            now_dt = self._aware_from_timestamp(now_ts) + timedelta(seconds=1)
            trigger = CronTrigger.from_crontab(expr, timezone=timezone)
            next_fire = trigger.get_next_fire_time(None, now_dt)
            return int(next_fire.timestamp()) if next_fire else None
        except Exception as err:
            logger.warning(
                "%s CRON 表达式无效：%s | %s",
                self.plugin_name,
                expr,
                self._get_error_detail(err),
            )
            return None

    def _refresh_and_store_status(
        self,
        data: dict,
        next_run: Optional[int],
        summary_lines: List[str],
        record_run: bool = True,
        next_action: str = "all",
    ) -> Dict[str, Any]:
        lines = list(summary_lines or [])
        state = self._sanitize_public_response(
            self._build_state_record(data, next_run, lines, next_action)
        )
        self.save_data("state", state)
        pill_status = self._sanitize_public_response(
            self._build_ui_state(data, next_run, lines, next_action)
        )
        self.save_data("pill_status", pill_status)
        if record_run:
            self.save_data("last_run", self._format_time(self._aware_now()))
        return pill_status

    def _build_state_record(self, data: dict, next_run: Optional[int], summary_lines: List[str], next_action: str = "all") -> dict:
        return {
            "schema_version": self.plugin_version,
            "time": self._format_time(self._aware_now()),
            "next_run_time": self._format_ts(next_run),
            "next_trigger_time": self._format_time(self._load_saved_next_trigger()),
            "next_run_action": next_action,
            "summary": summary_lines,
            "stats": data.get("stats") or {},
            "brick": data.get("brick") or {},
            "beach": data.get("beach") or {},
        }

    def _build_ui_state(self, data: dict, next_run: Optional[int], summary_lines: List[str], next_action: str = "all") -> Dict[str, Any]:
        stats = data.get("stats") or {}
        exchange = self._build_public_exchange(data.get("exchange"))
        brick = data.get("brick") or {}
        beach = data.get("beach") or {}
        inventory = data.get("inventory") or []
        recipes = data.get("recipes") or []
        next_trigger = self._load_saved_next_trigger()
        _, _, cookie_source, _, _, _ = self._site_credentials_snapshot()
        pill_plan = compute_magic_pill_plan(inventory, recipes)
        pill_recipe = next((recipe for recipe in recipes if self._safe_int(recipe.get("craft_id"), 0) == 6), {})

        return {
            "schema_version": self.plugin_version,
            "title": data.get("title") or "搬砖捡破烂炼魔丸",
            "subtitle": data.get("price_text") or "",
            "next_run_time": self._format_ts(next_run),
            "next_trigger_time": self._format_time(next_trigger),
            "next_run_ts": next_run or 0,
            "next_trigger_ts": int(next_trigger.timestamp()) if next_trigger else 0,
            "next_run_action": next_action,
            "next_run_action_label": {
                "brick": "搬砖",
                "beach": "清沙滩",
                "all": "整轮执行",
            }.get(next_action, "整轮执行"),
            "cookie_source": cookie_source,
            "page_note": (
                f"搬砖按 CRON {self._brick_cron} 独立调度，沙滩按冷却时间独立调度。"
                f"{' 清沙滩后会自动炼造魔丸。' if self._auto_craft else ''}"
                f"{' 清沙滩后会自动兑换魔力。' if self._auto_exchange else ''}"
            ),
            "overview": [
                {"label": "魔力", "value": int(stats.get("points") or 0)},
                {"label": "已兑换魔力", "value": int(stats.get("bonus_earned") or 0)},
                {"label": "当前魔丸数", "value": int(stats.get("magic_pills") or 0)},
                {"label": "今日搬砖", "value": f"{int(stats.get('daily_bricks') or 0)}/{int(stats.get('daily_limit') or 50)}"},
            ],
            "exchange": exchange,
            "brick": brick,
            "beach": beach,
            "inventory": {
                "items": inventory,
                "empty": not inventory,
                "empty_text": "物品栏暂无可显示内容",
            },
            "crafting": {
                "magic_pill_max": self._safe_int(pill_plan.get("max_count"), 0),
                "magic_pill_recipe": pill_recipe,
                "magic_pill_requirements": pill_recipe.get("ingredients") or {},
            },
            "recipes": recipes,
            "summary": summary_lines,
            "history": (self.get_data("history") or [])[:10],
            "capture_tips": [],
        }

    def _build_result_lines(
        self,
        brick_result: Dict[str, Any],
        beach_result: Dict[str, Any],
        auto_result: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[str], bool, bool]:
        lines: List[str] = []
        has_action = False
        has_warning = False

        if self._safe_int(brick_result.get("moved"), 0) > 0:
            lines.append(f"🧱 搬砖：🧱砖块×{self._safe_int(brick_result.get('moved'), 0)}")
            has_action = True
        elif brick_result.get("warning"):
            lines.append(f"⚠️ 搬砖失败：{brick_result.get('warning')}")
            has_warning = True

        beach_items = beach_result.get("items") or []
        if beach_items:
            lines.append(f"🏖️ 沙滩：{self._format_item_lines(beach_items)}")
            has_action = True
        elif beach_result.get("warning"):
            lines.append(f"⚠️ 清沙滩失败：{beach_result.get('warning')}")
            has_warning = True

        for line in (auto_result or {}).get("lines") or []:
            lines.append(line)
            if line.startswith(("⚗️", "💰", "✨", "📦")):
                has_action = True
            elif line.startswith("⚠️"):
                has_warning = True

        return lines, has_action, has_warning

    def _build_notify_text(self, lines: List[str], next_run: Optional[int]) -> str:
        prefixes = ("🧱", "🏖️", "⚗️", "💰", "✅", "✨")
        if any(line.startswith("⚠️") for line in lines):
            prefixes += ("⚠️", "🧪")
        report_lines = [line for line in lines if line.startswith(prefixes)]
        if not report_lines:
            report_lines = [line for line in lines if not line.startswith("ℹ️")]
        chunks = [self.SUMMARY_LINE]
        chunks.extend(report_lines)
        chunks.append(self.SUMMARY_LINE)
        chunks.append(f"⏰ 下次运行：{self._format_ts(next_run) if next_run else '等待下一次刷新'}")
        chunks.append(self.SUMMARY_LINE)
        return "\n".join(chunks)

    def _normalize_history_entry(self, title: str, lines: List[str]) -> Tuple[str, List[str]]:
        history_title = title
        history_lines = [line for line in (lines or []) if line]
        if not history_lines:
            return history_title, history_lines

        first_line = history_lines[0]
        if title == "⚗️ Vue-魔丸运行" and first_line.startswith(("🏖️ ", "🧱 ", "💰 ", "⚒️ ", "⚗️ ", "ℹ️ ", "⚠️ ")):
            history_title = first_line
            history_title = history_title.replace("🏖️ 沙滩：", "🏖️沙滩：", 1)
            history_title = history_title.replace("🧱 搬砖：", "🧱搬砖：", 1)
            history_title = history_title.replace("💰 兑换：", "💰兑换：", 1)
            history_title = history_title.replace("⚒️ 炼造：", "⚒️炼造：", 1)
            history_title = history_title.replace("⚗️ 魔丸：", "⚗️魔丸：", 1)
            return history_title, history_lines[1:]

        if title == "🏖️ 手动清沙滩":
            if first_line.startswith("🏖️ 沙滩："):
                return first_line.replace("🏖️ 沙滩：", "🏖️手动沙滩：", 1), history_lines[1:]
            if first_line.startswith("ℹ️ 沙滩："):
                return first_line.replace("ℹ️ 沙滩：", "🏖️手动沙滩：", 1), history_lines[1:]
            if first_line.startswith("⚠️ 清沙滩失败："):
                return first_line.replace("⚠️ 清沙滩失败：", "🏖️手动沙滩失败：", 1), history_lines[1:]

        if title == "🧱 手动搬砖":
            if first_line.startswith("🧱 搬砖："):
                return first_line.replace("🧱 搬砖：", "🧱手动搬砖：", 1), history_lines[1:]
            if first_line.startswith("ℹ️ 搬砖："):
                return first_line.replace("ℹ️ 搬砖：", "🧱手动搬砖：", 1), history_lines[1:]
            if first_line.startswith("⚠️ 搬砖失败："):
                return first_line.replace("⚠️ 搬砖失败：", "🧱手动搬砖失败：", 1), history_lines[1:]

        return history_title, history_lines

    def _append_history(self, title: str, lines: List[str]):
        history = self.get_data("history") or []
        history_title, history_lines = self._normalize_history_entry(title, lines)
        history.insert(0, {"time": self._format_time(self._aware_now()), "title": history_title, "lines": history_lines})
        self.save_data("history", history[:20])

    @staticmethod
    def _to_bool(val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in {"1", "true", "yes", "on"}
        return bool(val)

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        try:
            if isinstance(value, str):
                value = re.sub(r"[^\d-]", "", value)
            return int(value)
        except Exception:
            return default

    def _normalize_timestamp(self, value: Any, default: int = 0) -> int:
        ts = self._safe_int(value, default)
        if ts <= 0:
            return default
        if ts > 10_000_000_000:
            ts //= 1000
        return ts

    def _resolve_server_now(self, raw_value: Any) -> int:
        raw = self._safe_int(raw_value, 0)
        current = int(time.time())
        if raw == 0:
            return current
        if abs(raw) <= 14 * 24 * 3600:
            return current + raw
        return self._normalize_timestamp(raw, current)

    def _is_reasonable_future_ts(self, ts: Any, base_ts: Optional[Any] = None, max_days: int = 400) -> bool:
        value = self._normalize_timestamp(ts, 0)
        base = self._resolve_server_now(base_ts)
        return value > base and value <= base + max_days * 24 * 3600

    def _format_item_lines(self, items: List[Dict[str, Any]]) -> str:
        return "  ".join(
            f"{item.get('icon') or self.ITEM_ICON_MAP.get(item.get('name') or '', '📦')}{item.get('name')}×{self._safe_int(item.get('count'), 0)}"
            for item in items
            if self._safe_int(item.get("count"), 0) > 0
        )

    def _format_time(self, dt: Optional[datetime]) -> str:
        if not dt:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_ts(self, ts: Optional[int]) -> str:
        if not ts:
            return ""
        return self._format_time(self._aware_from_timestamp(int(ts)))

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    def _aware_from_timestamp(self, timestamp: int) -> datetime:
        return datetime.fromtimestamp(self._normalize_timestamp(timestamp, int(time.time())), tz=pytz.timezone(settings.TZ))

    def _parse_datetime(self, raw: Any) -> Optional[datetime]:
        if not raw:
            return None
        if isinstance(raw, datetime):
            return raw if raw.tzinfo else pytz.timezone(settings.TZ).localize(raw)
        try:
            parsed = datetime.strptime(str(raw), "%Y-%m-%d %H:%M:%S")
            return pytz.timezone(settings.TZ).localize(parsed)
        except Exception:
            return None

    def _sanitize_sensitive_text(
        self,
        value: Any,
        sensitive_values: Tuple[str, ...] = (),
    ) -> str:
        try:
            text = str(value)
        except Exception:
            text = type(value).__name__

        secrets: List[str] = []
        secrets.extend(self._cookie_sensitive_values(self._manual_cookie))
        _, cookie, _, _, _, _ = self._site_credentials_snapshot()
        secrets.extend(self._cookie_sensitive_values(cookie))
        secrets.extend(
            secret
            for secret in sensitive_values
            if isinstance(secret, str) and secret
        )
        for secret in sorted(set(secrets), key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = self._SENSITIVE_HEADER_PATTERN.sub(r"\1[REDACTED]", text)
        text = self._BEARER_PATTERN.sub(r"\1[REDACTED]", text)
        return self._SENSITIVE_VALUE_PATTERN.sub(r"\1[REDACTED]", text)

    def _is_sensitive_public_key(self, key: Any) -> bool:
        if not isinstance(key, str):
            return False
        normalized = re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")
        if normalized in self._PUBLIC_SAFE_SENSITIVE_KEYS:
            return False
        if normalized in self._PUBLIC_SENSITIVE_KEYS:
            return True
        return any(
            fragment in normalized
            for fragment in self._PUBLIC_SENSITIVE_KEY_FRAGMENTS
        )

    @classmethod
    def _take_public_items(cls, iterable):
        iterator = iter(iterable)
        for _ in range(cls.PUBLIC_MAX_ITEMS):
            try:
                yield next(iterator)
            except StopIteration:
                return

    @staticmethod
    def _sensitive_public_scalar_marker(value: Any):
        if type(value) is int:
            if value in {0, 1}:
                return None
            return "number", value
        if type(value) is float:
            if not math.isfinite(value) or value in {0.0, 1.0}:
                return None
            return "number", value
        return None

    def _collect_sensitive_public_data(
        self,
        value: Any,
    ) -> Tuple[List[str], set, bool]:
        secrets: List[str] = []
        scalar_values = set()
        known_secrets = set()
        active_containers = set()
        collection_complete = True
        scanned_nodes = 0

        def scan_items(raw_container: Any, iterable):
            nonlocal collection_complete, scanned_nodes
            item_count = len(raw_container)
            if item_count > self.PUBLIC_SECRET_SCAN_MAX_ITEMS:
                collection_complete = False
                return
            iterator = iter(iterable)
            for _ in range(item_count):
                if scanned_nodes >= self.PUBLIC_SECRET_SCAN_MAX_NODES:
                    collection_complete = False
                    return
                try:
                    item = next(iterator)
                except StopIteration:
                    return
                scanned_nodes += 1
                yield item

        def add_scalar(raw_value: Any):
            nonlocal collection_complete
            if type(raw_value) is str:
                texts = (raw_value,)
            elif raw_value is None:
                texts = ("None", "null")
            elif type(raw_value) is bool:
                texts = ()
            elif type(raw_value) is int:
                texts = () if raw_value in {0, 1} else (str(raw_value),)
            elif type(raw_value) is float:
                texts = () if raw_value in {0.0, 1.0} else (str(raw_value),)
            else:
                return
            for text in texts:
                if not text or text in known_secrets:
                    continue
                if len(secrets) >= self.PUBLIC_MAX_SECRETS:
                    collection_complete = False
                    return
                known_secrets.add(text)
                secrets.append(text)
            marker = self._sensitive_public_scalar_marker(raw_value)
            if marker is None or marker in scalar_values:
                return
            if len(scalar_values) >= self.PUBLIC_MAX_SECRETS:
                collection_complete = False
                return
            scalar_values.add(marker)

        def collect_scalars(raw_value: Any, depth: int):
            nonlocal collection_complete
            if not collection_complete:
                return
            if depth > self.PUBLIC_SECRET_SCAN_MAX_DEPTH:
                if (
                    raw_value is None
                    or type(raw_value) in {bool, int, float, str}
                    or (
                        type(raw_value) in {dict, list, tuple}
                        and bool(raw_value)
                    )
                ):
                    collection_complete = False
                return
            if (
                raw_value is None
                or type(raw_value) in {bool, int, float, str}
            ):
                add_scalar(raw_value)
                return
            if type(raw_value) not in {dict, list, tuple}:
                return
            container_id = id(raw_value)
            if container_id in active_containers:
                return
            active_containers.add(container_id)
            try:
                iterable = (
                    raw_value.values()
                    if type(raw_value) is dict
                    else raw_value
                )
                for nested in scan_items(raw_value, iterable):
                    collect_scalars(nested, depth + 1)
                    if not collection_complete:
                        break
            finally:
                active_containers.discard(container_id)

        def walk(raw_value: Any, depth: int):
            nonlocal collection_complete
            if not collection_complete:
                return
            if depth > self.PUBLIC_SECRET_SCAN_MAX_DEPTH:
                if (
                    type(raw_value) in {dict, list, tuple}
                    and bool(raw_value)
                ):
                    collection_complete = False
                return
            if type(raw_value) not in {dict, list, tuple}:
                return
            container_id = id(raw_value)
            if container_id in active_containers:
                return
            active_containers.add(container_id)
            try:
                if type(raw_value) is dict:
                    for key, nested in scan_items(raw_value, raw_value.items()):
                        if type(key) is not str:
                            walk(nested, depth + 1)
                            if not collection_complete:
                                break
                            continue
                        if self._is_sensitive_public_key(key):
                            collect_scalars(nested, depth + 1)
                        else:
                            walk(nested, depth + 1)
                        if not collection_complete:
                            break
                else:
                    for nested in scan_items(raw_value, raw_value):
                        walk(nested, depth + 1)
                        if not collection_complete:
                            break
            finally:
                active_containers.discard(container_id)

        walk(value, 0)
        return secrets, scalar_values, collection_complete

    def _public_value(
        self,
        value: Any,
        sensitive_values: Optional[Tuple[str, ...]] = None,
        sensitive_scalar_values: Optional[set] = None,
        depth: int = 0,
        active_containers: Optional[set] = None,
    ) -> Any:
        if sensitive_values is None or sensitive_scalar_values is None:
            collected_values, collected_scalars, collection_complete = (
                self._collect_sensitive_public_data(value)
            )
            if not collection_complete:
                return _DROP_PUBLIC_VALUE
            if sensitive_values is None:
                sensitive_values = tuple(collected_values)
            if sensitive_scalar_values is None:
                sensitive_scalar_values = collected_scalars
        if active_containers is None:
            active_containers = set()
        if depth > self.PUBLIC_MAX_DEPTH:
            return _DROP_PUBLIC_VALUE
        if value is None or type(value) is bool:
            return value
        if type(value) is str:
            return self._sanitize_sensitive_text(value, sensitive_values)
        if type(value) is int:
            marker = self._sensitive_public_scalar_marker(value)
            if marker is not None and marker in sensitive_scalar_values:
                return _DROP_PUBLIC_VALUE
            if abs(value) <= self.JS_SAFE_INTEGER_MAX:
                return value
            return _DROP_PUBLIC_VALUE
        if type(value) is float:
            marker = self._sensitive_public_scalar_marker(value)
            if marker is not None and marker in sensitive_scalar_values:
                return _DROP_PUBLIC_VALUE
            return value if math.isfinite(value) else _DROP_PUBLIC_VALUE
        if type(value) not in {dict, list, tuple}:
            return _DROP_PUBLIC_VALUE

        container_id = id(value)
        if container_id in active_containers:
            return _DROP_PUBLIC_VALUE
        active_containers.add(container_id)
        try:
            if type(value) is dict:
                public_dict: Dict[str, Any] = {}
                for key, nested in self._take_public_items(value.items()):
                    if type(key) is not str or self._is_sensitive_public_key(key):
                        continue
                    public_nested = self._public_value(
                        nested,
                        sensitive_values,
                        sensitive_scalar_values,
                        depth + 1,
                        active_containers,
                    )
                    if public_nested is not _DROP_PUBLIC_VALUE:
                        public_dict[key] = public_nested
                if depth and value and not public_dict:
                    return _DROP_PUBLIC_VALUE
                return public_dict

            public_items = []
            for nested in self._take_public_items(value):
                public_nested = self._public_value(
                    nested,
                    sensitive_values,
                    sensitive_scalar_values,
                    depth + 1,
                    active_containers,
                )
                if public_nested is not _DROP_PUBLIC_VALUE:
                    public_items.append(public_nested)
            if depth and value and not public_items:
                return _DROP_PUBLIC_VALUE
            return public_items if type(value) is list else tuple(public_items)
        finally:
            active_containers.discard(container_id)

    def _sanitize_public_response(self, value: Any) -> Any:
        sensitive_values, sensitive_scalar_values, collection_complete = (
            self._collect_sensitive_public_data(value)
        )
        if not collection_complete:
            return {
                "success": False,
                "message": self.PUBLIC_LIMIT_MESSAGE,
            }
        public_value = self._public_value(
            value,
            tuple(sensitive_values),
            sensitive_scalar_values,
        )
        return None if public_value is _DROP_PUBLIC_VALUE else public_value

    def _sanitize_config_public_response(self, value: Any) -> Any:
        if not isinstance(value, dict):
            return self._sanitize_public_response(value)

        source = dict(value)
        direct_cookie = source.pop("cookie", None)
        nested_cookie = None
        raw_config = source.get("config")
        if isinstance(raw_config, dict):
            safe_config = dict(raw_config)
            nested_cookie = safe_config.pop("cookie", None)
            source["config"] = safe_config

        cookie_error = None
        raw_errors = source.get("errors")
        if isinstance(raw_errors, dict):
            safe_errors = dict(raw_errors)
            cookie_error = safe_errors.pop("cookie", None)
            source["errors"] = safe_errors

        public_value = self._sanitize_public_response(source)
        if not isinstance(public_value, dict):
            return public_value
        if isinstance(direct_cookie, str):
            public_value["cookie"] = direct_cookie
        if isinstance(nested_cookie, str) and isinstance(public_value.get("config"), dict):
            public_value["config"]["cookie"] = nested_cookie
        if isinstance(cookie_error, str):
            public_value.setdefault("errors", {})["cookie"] = (
                self._sanitize_sensitive_text(cookie_error)
            )
        return public_value

    @staticmethod
    def _attach_error_sensitive_values(
        err: BaseException,
        sensitive_values: Tuple[str, ...],
    ):
        values = tuple(
            value
            for value in sensitive_values
            if isinstance(value, str) and value
        )
        if not values:
            return
        try:
            existing = getattr(err, "_vuepill_sensitive_values", ())
            setattr(
                err,
                "_vuepill_sensitive_values",
                tuple(dict.fromkeys(tuple(existing) + values)),
            )
        except Exception:
            pass

    def _error_sensitive_values(
        self,
        err: BaseException,
        sensitive_values: Tuple[str, ...] = (),
    ) -> Tuple[str, ...]:
        values = [
            value
            for value in sensitive_values
            if isinstance(value, str) and value
        ]
        seen_errors = set()
        current: Optional[BaseException] = err
        while current is not None and len(seen_errors) < 20:
            error_id = id(current)
            if error_id in seen_errors:
                break
            seen_errors.add(error_id)
            try:
                attached = getattr(current, "_vuepill_sensitive_values", ())
                values.extend(
                    value
                    for value in attached
                    if isinstance(value, str) and value
                )
                current = current.__cause__ or current.__context__
            except Exception:
                break
        return tuple(dict.fromkeys(values))

    def _get_error_detail(
        self,
        err: Exception,
        sensitive_values: Tuple[str, ...] = (),
    ) -> str:
        try:
            code = getattr(err, "code", None) or getattr(
                getattr(err, "cause", None),
                "code",
                None,
            )
        except Exception:
            code = None
        try:
            message = str(err)
        except Exception:
            message = type(err).__name__
        detail = " | ".join(
            str(part) for part in (code, message) if part
        ) or "UNKNOWN"
        return self._sanitize_sensitive_text(
            detail,
            self._error_sensitive_values(err, sensitive_values),
        )

