import json
import random
import re
import socket
import time
import traceback
from datetime import datetime, timedelta
from html import unescape
from math import ceil
from typing import Any, Dict, List, Optional, Tuple

import pytz
import requests
import urllib3.util.connection as urllib3_connection
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType


class SQEmoji(_PluginBase):
    plugin_name = "SQ表情"
    plugin_desc = "老虎机、开包、舞台演出、获取执行记录。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3ad.png"
    plugin_version = "0.1.10"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "sqemoji_"
    plugin_order = 69
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_SPIN_CRON = "5 0 * * *"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    SUMMARY_LINE = "━━━━━━━━━━━━━━"
    PRE_REFRESH_SECONDS = 60

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _auto_cookie: bool = True
    _auto_stage: bool = True
    _auto_spin: bool = False
    _auto_open_bags: bool = False
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cookie: str = ""
    _cookie_source: str = "未配置"
    _site_domain: str = DEFAULT_SITE_DOMAIN
    _site_url: str = DEFAULT_SITE_URL
    _user_agent: str = DEFAULT_USER_AGENT
    _schedule_buffer_seconds: int = 5
    _random_delay_max_seconds: int = 5
    _http_timeout: int = 12
    _http_retry_times: int = 3
    _http_retry_delay: int = 1500
    _skip_before_seconds: int = 60
    _auto_stage_effect_key: str = "auto"
    _spin_cron: str = DEFAULT_SPIN_CRON

    _next_run_time: Optional[datetime] = None
    _next_trigger_time: Optional[datetime] = None
    _next_trigger_mode: str = ""
    _bootstrap_pending: bool = False

    def __init__(self):
        super().__init__()

    def init_plugin(self, config: Optional[dict] = None):
        self.stop_service()
        self._siteoper = SiteOper()

        merged = self._default_config()
        if config:
            merged.update(config)
        self._apply_config(merged)
        self._resolve_site_profile()

        if self._auto_cookie:
            self._sync_cookie_from_site(save_config=False, silent=True)
        else:
            self._cookie_source = "手动配置" if self._cookie else "未配置"

        self._load_saved_next_run()
        self._load_saved_next_trigger()
        self._load_saved_next_trigger_mode()
        self._bootstrap_pending = self._enabled and self._has_auto_jobs_enabled() and not self._next_trigger_time

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

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取 SQ表情 配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 SQ表情 配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 SQ表情 状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新 SQ表情 状态"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行 SQ表情"},
            {"path": "/cookie", "endpoint": self._sync_site_cookie_api, "methods": ["GET"], "auth": "bear", "summary": "同步站点 Cookie"},
            {"path": "/spin", "endpoint": self._spin_api, "methods": ["POST"], "auth": "bear", "summary": "手动转动老虎机"},
            {"path": "/open-bag", "endpoint": self._open_bag_api, "methods": ["POST"], "auth": "bear", "summary": "手动开包"},
            {"path": "/accept-open", "endpoint": self._accept_open_api, "methods": ["POST"], "auth": "bear", "summary": "收下开包结果"},
            {"path": "/reroll-open", "endpoint": self._reroll_open_api, "methods": ["POST"], "auth": "bear", "summary": "重开开包结果"},
            {"path": "/upgrade-bag", "endpoint": self._upgrade_bag_api, "methods": ["POST"], "auth": "bear", "summary": "合成表情包"},
            {"path": "/expand-stage-row", "endpoint": self._expand_stage_row_api, "methods": ["POST"], "auth": "bear", "summary": "扩展舞台格子"},
            {"path": "/confirm-stage", "endpoint": self._confirm_stage_api, "methods": ["POST"], "auth": "bear", "summary": "确认演出阵容"},
            {"path": "/recall-stage", "endpoint": self._recall_stage_api, "methods": ["POST"], "auth": "bear", "summary": "收回演出"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        if self._enabled and self._has_auto_jobs_enabled():
            next_run = self._get_next_run_for_service()
            if next_run:
                services.append({
                    "id": "SQEmoji_auto",
                    "name": "SQ表情初始化" if self._bootstrap_pending else "SQ表情智能调度",
                    "trigger": "date",
                    "func": self._bootstrap_worker if self._bootstrap_pending else self._auto_worker,
                    "kwargs": {"run_date": next_run},
                })
        return services

    def stop_service(self):
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as err:
            logger.warning("%s 停止一次性调度失败：%s", self.plugin_name, err)

        try:
            Scheduler().remove_plugin_job(self.__class__.__name__)
        except Exception:
            pass

    def run_job(self, force: bool = False, reason: str = "manual") -> Dict[str, Any]:
        start_time = time.time()
        session: Optional[requests.Session] = None
        state: Dict[str, Any] = {}
        summary_lines: List[str] = []
        logger.info("## 开始执行... %s", self._format_time(self._aware_now()))
        try:
            if not self._enabled and not force:
                return {"success": False, "message": "插件未启用", "status": self._build_status(auto_refresh=False)}

            self._ensure_cookie()
            session = self._build_session()

            if not force and reason == "schedule" and self._is_pre_refresh_trigger():
                emoji_status = self._refresh_state(reason="pre-run-refresh", record_run=False)
                logger.info("%s 已完成运行前 1 分钟预刷新", self.plugin_name)
                return {
                    "success": True,
                    "message": "运行前状态已刷新",
                    "lines": [],
                    "emoji_status": emoji_status,
                    "status": self._build_status(auto_refresh=False),
                }

            if not force and self._should_skip_run():
                return {"success": True, "message": "未到计划触发时间，已跳过", "status": self._build_status(auto_refresh=False)}

            rand_delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if rand_delay:
                time.sleep(rand_delay)

            bundle = self._fetch_bundle(session)
            state = bundle["state"]
            if not state or not state.get("user"):
                raise ValueError("获取表情页失败，Cookie 可能已失效")

            if self._auto_spin:
                state, spin_lines = self._run_auto_spin(session, state)
                summary_lines.extend(spin_lines)
            if self._auto_open_bags:
                state, open_lines = self._run_auto_open_bags(session, state)
                summary_lines.extend(open_lines)
            if self._auto_stage:
                state, stage_lines = self._run_auto_stage(session, state)
                summary_lines.extend(stage_lines)

            final_bundle = self._fetch_bundle(session)
            final_state = final_bundle.get("state") or state
            if self._build_stage_runtime(state).get("has_active") and not self._build_stage_runtime(final_state).get("has_active"):
                final_state = state
            next_run = self._compute_next_run(final_state)
            emoji_status = self._refresh_and_store_status(final_state, next_run, summary_lines)

            if self._notify and summary_lines:
                self._send_report(summary_lines, next_run)

            elapsed = max(1, round(time.time() - start_time))
            message = summary_lines[0] if summary_lines else f"本次没有可执行动作，耗时 {elapsed} 秒"
            return {
                "success": True,
                "message": message,
                "lines": summary_lines,
                "emoji_status": emoji_status,
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            retry_at: Optional[int] = None
            fallback_delay = max(30, self._http_timeout * 2)

            if session is not None:
                try:
                    recovered_bundle = self._fetch_bundle(session)
                    state = recovered_bundle.get("state") or state
                except Exception as refresh_err:
                    logger.warning("%s 异常后刷新状态失败：%s", self.plugin_name, self._get_error_detail(refresh_err))

            partial_lines = list(summary_lines)
            if self._enabled and self._has_auto_jobs_enabled() and (partial_lines or reason in {"schedule", "bootstrap", "onlyonce"}):
                retry_at = int(time.time()) + fallback_delay
            if state:
                computed_next = self._compute_next_run(state)
                if computed_next:
                    retry_at = min(retry_at, computed_next) if retry_at else computed_next
            if partial_lines and retry_at:
                partial_lines.append("\u23f0 \u7f51\u7edc\u6ce2\u52a8\uff0c\u5c06\u5728\u77ed\u5ef6\u8fdf\u540e\u81ea\u52a8\u91cd\u8bd5\u5269\u4f59\u6d41\u7a0b")

            emoji_status = None
            if state:
                try:
                    emoji_status = self._refresh_and_store_status(state, retry_at, partial_lines)
                except Exception as store_err:
                    logger.warning("%s 异常后保存状态失败：%s", self.plugin_name, self._get_error_detail(store_err))
            elif retry_at:
                try:
                    self._schedule_next_run(retry_at, reason="error-retry")
                except Exception as schedule_err:
                    logger.warning("%s 异常后补重试失败：%s", self.plugin_name, self._get_error_detail(schedule_err))

            if partial_lines:
                if not emoji_status:
                    self._append_history(partial_lines, retry_at)
                    self.save_data("last_run", self._format_time(self._aware_now()))
                logger.warning("%s 本轮部分完成后中断：%s", self.plugin_name, detail)
                logger.warning("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
                if self._notify:
                    self._send_report(partial_lines, retry_at)
                return {
                    "success": True,
                    "message": partial_lines[0],
                    "lines": partial_lines,
                    "emoji_status": emoji_status or (self.get_data("emoji_status") or {}),
                    "status": self._build_status(auto_refresh=False),
                }

            logger.error("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            if self._notify:
                self.post_message(
                    title="【🎭SQ表情】 异常",
                    mtype=NotificationType.Plugin,
                    text=detail,
                )
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            logger.info("## 执行结束... %s", self._format_time(self._aware_now()))

    def _manual_worker(self):
        self.run_job(force=True, reason="onlyonce")

    def _bootstrap_worker(self):
        self._bootstrap_pending = False
        self.run_job(force=True, reason="bootstrap")

    def _auto_worker(self):
        self.run_job(force=False, reason="schedule")

    def _get_status(self):
        return self._build_status()

    def _refresh_data(self):
        try:
            emoji_status = self._refresh_state(reason="manual-refresh")
            return {"success": True, "message": "状态已刷新", "emoji_status": emoji_status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

    def _spin_api(self, payload: dict):
        try:
            result = self._manual_spin(payload or {})
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _open_bag_api(self, payload: dict):
        try:
            result = self._manual_open_bag(payload or {})
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _accept_open_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_accept_open()
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _reroll_open_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_reroll_open()
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _upgrade_bag_api(self, payload: dict):
        try:
            result = self._manual_upgrade_bag(payload or {})
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _expand_stage_row_api(self, payload: dict):
        try:
            result = self._manual_expand_stage_row(payload or {})
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _confirm_stage_api(self, payload: dict):
        try:
            result = self._manual_confirm_stage(payload or {})
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _recall_stage_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_recall_stage()
            return {"success": True, **result, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            return {"success": False, "message": self._get_error_detail(err), "status": self._build_status(auto_refresh=False)}

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        emoji_status = self.get_data("emoji_status") or {}
        needs_refresh = not emoji_status or emoji_status.get("schema_version") != self.plugin_version
        if auto_refresh and needs_refresh and self._cookie:
            try:
                emoji_status = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)

        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "auto_cookie": self._auto_cookie,
            "auto_stage": self._auto_stage,
            "auto_spin": self._auto_spin,
            "auto_open_bags": self._auto_open_bags,
            "cookie_source": self._cookie_source,
            "next_run_time": self._format_time(next_run),
            "next_run_ts": int(next_run.timestamp()) if next_run else 0,
            "next_trigger_time": self._format_time(next_trigger),
            "next_trigger_ts": int(next_trigger.timestamp()) if next_trigger else 0,
            "last_run": self.get_data("last_run") or "",
            "emoji_status": emoji_status,
            "history": (self.get_data("history") or [])[:20],
            "config": self._get_config(),
        }

    def _get_config(self, include_options: bool = True) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "auto_stage": self._auto_stage,
            "auto_spin": self._auto_spin,
            "auto_open_bags": self._auto_open_bags,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
            "schedule_buffer_seconds": self._schedule_buffer_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "skip_before_seconds": self._skip_before_seconds,
            "auto_stage_effect_key": self._auto_stage_effect_key,
            "spin_cron": self._spin_cron,
            "effect_options": self._build_effect_options() if include_options else None,
            "capture_tips": [] if include_options else None,
        }

    def _save_config(self, config_payload: dict):
        merged = self._default_config()
        merged.update(self._get_config(include_options=False))
        merged.update(config_payload or {})
        self.init_plugin(merged)
        self._update_config()
        if self._enabled and self._has_auto_jobs_enabled():
            self._reregister_plugin("save-config")
        try:
            status = self._refresh_state(reason="save-config") if self._cookie else self.get_data("emoji_status") or {}
        except Exception as err:
            logger.warning("%s 保存配置后刷新失败：%s", self.plugin_name, err)
            status = self.get_data("emoji_status") or {}
        return {"success": True, "message": "配置已保存", "config": self._get_config(), "emoji_status": status, "status": self._build_status(auto_refresh=False)}

    def _sync_site_cookie_api(self):
        result = self._sync_cookie_from_site(save_config=True, silent=False)
        if result.get("success") and self._enabled and self._has_auto_jobs_enabled():
            self._reregister_plugin("sync-cookie")
        return {**result, "config": self._get_config(), "status": self._build_status(auto_refresh=False)}

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "auto_cookie": True,
            "auto_stage": True,
            "auto_spin": False,
            "auto_open_bags": False,
            "use_proxy": False,
            "force_ipv4": True,
            "cookie": "",
            "schedule_buffer_seconds": 5,
            "random_delay_max_seconds": 5,
            "http_timeout": 12,
            "http_retry_times": 3,
            "http_retry_delay": 1500,
            "skip_before_seconds": 60,
            "auto_stage_effect_key": "auto",
            "spin_cron": self.DEFAULT_SPIN_CRON,
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._auto_cookie = self._to_bool(config.get("auto_cookie", True))
        self._auto_stage = self._to_bool(config.get("auto_stage", True))
        self._auto_spin = self._to_bool(config.get("auto_spin", False))
        self._auto_open_bags = self._to_bool(config.get("auto_open_bags", False))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cookie = (config.get("cookie") or "").strip()
        self._schedule_buffer_seconds = max(0, self._safe_int(config.get("schedule_buffer_seconds"), 5))
        self._random_delay_max_seconds = max(0, self._safe_int(config.get("random_delay_max_seconds"), 5))
        self._http_timeout = max(5, self._safe_int(config.get("http_timeout"), 12))
        self._http_retry_times = max(0, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(0, self._safe_int(config.get("http_retry_delay"), 1500))
        self._skip_before_seconds = max(0, self._safe_int(config.get("skip_before_seconds"), 60))
        auto_stage_effect_key = str(config.get("auto_stage_effect_key") or "auto").strip()
        self._auto_stage_effect_key = auto_stage_effect_key or "auto"
        self._spin_cron = (config.get("spin_cron") or self.DEFAULT_SPIN_CRON).strip() or self.DEFAULT_SPIN_CRON

    def _update_config(self):
        self.update_config({
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "auto_stage": self._auto_stage,
            "auto_spin": self._auto_spin,
            "auto_open_bags": self._auto_open_bags,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
            "schedule_buffer_seconds": self._schedule_buffer_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "skip_before_seconds": self._skip_before_seconds,
            "auto_stage_effect_key": self._auto_stage_effect_key,
            "spin_cron": self._spin_cron,
        })

    def _resolve_site_profile(self):
        self._site_domain = self.DEFAULT_SITE_DOMAIN
        self._site_url = self.DEFAULT_SITE_URL
        self._user_agent = self.DEFAULT_USER_AGENT

    def _sync_cookie_from_site(self, save_config: bool = False, silent: bool = True) -> Dict[str, Any]:
        try:
            if not self._siteoper:
                self._siteoper = SiteOper()
            site = self._siteoper.get_by_domain(self._site_domain)
            if not site:
                return {"success": False, "message": f"未找到站点 {self._site_domain} 的配置"}
            cookie = (getattr(site, "cookie", "") or "").strip()
            if not cookie:
                return {"success": False, "message": f"站点 {self._site_domain} 未配置 Cookie"}
            self._cookie = cookie
            self._cookie_source = f"\u7ad9\u70b9\u540c\u6b65\uff1a{self._site_domain}"
            if save_config:
                self._update_config()
            if not silent:
                logger.info("%s 已同步站点 Cookie：%s", self.plugin_name, self._site_domain)
            return {"success": True, "message": f"已同步 {self._site_domain} 的站点 Cookie"}
        except Exception as err:
            detail = self._get_error_detail(err)
            if not silent:
                logger.warning("%s 同步站点 Cookie 失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _ensure_cookie(self):
        if not self._cookie:
            raise ValueError("未配置 SQ Cookie")

    def _build_session(self) -> requests.Session:
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        retry = Retry(
            total=max(0, self._http_retry_times),
            connect=max(0, self._http_retry_times),
            read=max(0, self._http_retry_times),
            backoff_factor=max(self._http_retry_delay / 1000.0, 0.1),
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": self._user_agent,
            "Cookie": self._cookie,
            "Referer": f"{self._site_url}/siqi_emoji.php",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        })
        if self._use_proxy and getattr(settings, "PROXY", None):
            session.proxies = {"http": settings.PROXY, "https": settings.PROXY}
        return session

    def _fetch_bundle(self, session: requests.Session) -> Dict[str, Any]:
        def run() -> Dict[str, Any]:
            response = session.get(
                f"{self._site_url}/siqi_emoji.php",
                timeout=(self._http_timeout, self._http_timeout),
            )
            response.raise_for_status()
            html = response.text
            state = self._extract_initial_state(html)
            if not state:
                raise ValueError("页面返回成功，但未解析到 SIQI_EMOJI_DATA")
            return {"state": state, "html": html}

        return self._request_with_retry("fetchEmojiPage", run)

    def _extract_initial_state(self, html: str) -> Dict[str, Any]:
        marker = "const SIQI_EMOJI_DATA ="
        index = html.find(marker)
        if index < 0:
            return {}
        start = html.find("{", index)
        if start < 0:
            return {}
        depth = 0
        quote: Optional[str] = None
        escape = False
        end = -1
        for position in range(start, len(html)):
            ch = html[position]
            if quote:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == quote:
                    quote = None
                continue
            if ch in {'"', "'"}:
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = position
                    break
        if end < 0:
            return {}
        try:
            return json.loads(html[start:end + 1])
        except Exception:
            return {}

    def _refresh_state(
        self,
        reason: str = "",
        summary_lines: Optional[List[str]] = None,
        record_run: bool = True,
    ) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        bundle = self._fetch_bundle(session)
        next_run = self._compute_next_run(bundle["state"])
        return self._refresh_and_store_status(bundle["state"], next_run, summary_lines or [], record_run=record_run)

    def _post_action(
        self,
        session: requests.Session,
        action: str,
        payload: Optional[dict] = None,
        retry_network: bool = False,
    ) -> dict:
        body = dict(payload or {})
        body["action"] = action

        def run() -> dict:
            response = session.post(
                f"{self._site_url}/siqi_emoji.php",
                data=body,
                timeout=(self._http_timeout, self._http_timeout),
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
            if data is None:
                return {}
            return {"success": True, "data": data}

        if retry_network:
            return self._request_with_retry(f"postAction:{action}", run)
        return run()

    def _extract_action_state(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(result, dict):
            return None
        data = result.get("data")
        if isinstance(data, dict) and any(key in data for key in ("user", "spin", "bags", "stage", "effects")):
            return data
        return None

    def _run_auto_spin(self, session: requests.Session, state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        spin = state.get("spin") or {}
        remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))
        if remaining <= 0:
            return state, []

        before_bags = self._bag_quantity_map(state)
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_spin_batch"), 10))
        total_spins = 0
        while remaining > 0:
            batch = min(remaining, max_batch)
            used_before = self._safe_int((state.get("spin") or {}).get("used"), 0)
            result = self._post_action(session, "spin_slot", {"count": batch}, retry_network=True)
            if result.get("success"):
                total_spins += batch
                state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
            else:
                recovered = self._recover_spin_state(session, state, before_bags, used_before, batch)
                recovered_state = recovered.get("state") or {}
                recovered_spins = self._safe_int(recovered.get("spins"), 0)
                if recovered_state and recovered_spins > 0:
                    logger.info("%s 老虎机状态已确认，按最新状态计入 %s 次", self.plugin_name, recovered_spins)
                    total_spins += recovered_spins
                    state = recovered_state
                else:
                    raise ValueError(result.get("message") or "老虎机转动失败")
            spin = state.get("spin") or {}
            remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))

        diff_text = self._format_named_counts(self._bag_quantity_diff(before_bags, state))
        if diff_text:
            return state, [f"🎰 老虎机：{diff_text}"]
        return state, [f"🎰 老虎机：已转动 {total_spins} 次"] if total_spins else []

    def _run_auto_open_bags(self, session: requests.Session, state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        lines: List[str] = []
        opened_counts: Dict[str, int] = {}
        accepted_counts: Dict[str, int] = {}
        accepted_batches = 0

        def accept_pending(current_state: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal accepted_batches
            pending = current_state.get("pending_open") or {}
            if not pending:
                return current_state
            item_text = self._format_pending_item_counts(pending)
            if item_text:
                for name, quantity in self._parse_named_counts(item_text).items():
                    accepted_counts[name] = accepted_counts.get(name, 0) + quantity
            accepted_batches += 1
            try:
                result = self._post_action(session, "accept_open", {}, retry_network=True)
            except Exception:
                recovered_state = self._recover_accept_open_state(session)
                if recovered_state is not None:
                    logger.info("%s open-bag accept status confirmed by refreshed state", self.plugin_name)
                    return recovered_state
                raise
            if result.get("success"):
                return self._extract_action_state(result) or self._fetch_bundle(session)["state"]
            recovered_state = self._recover_accept_open_state(session)
            if recovered_state is not None:
                logger.info("%s open-bag accept status confirmed by refreshed state", self.plugin_name)
                return recovered_state
            raise ValueError(result.get("message") or "自动收下开包结果失败")

        state = accept_pending(state)
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_open_bag_batch"), 12))

        while True:
            openable_bag = None
            for bag in self._iter_dicts(state.get("bags") or []):
                if self._safe_int(bag.get("quantity"), 0) > 0:
                    openable_bag = bag
                    break
            if not openable_bag:
                break

            tier = self._safe_int(openable_bag.get("tier"), 0)
            bag_name = self._compact_bag_name(openable_bag.get("name") or f"表情包{tier}")
            quantity = self._safe_int(openable_bag.get("quantity"), 0)
            batch = min(quantity, max_batch)
            result = self._post_action(session, "open_bag", {"tier": tier, "count": batch}, retry_network=True)
            if not result.get("success"):
                raise ValueError(result.get("message") or "自动开包失败")
            opened_counts[bag_name] = opened_counts.get(bag_name, 0) + batch
            state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
            state = accept_pending(state)
            max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_open_bag_batch"), max_batch))

        if opened_counts:
            lines.append(f"📦 开包：{self._format_named_counts(opened_counts)}")
        if accepted_counts:
            lines.append(f"📥 收下：{self._format_named_counts(accepted_counts)}")
        elif accepted_batches:
            lines.append(f"📥 收下：已自动收下 {accepted_batches} 批开包结果")
        return state, lines

    def _run_auto_stage(self, session: requests.Session, state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        lines: List[str] = []
        runtime = self._build_stage_runtime(state)
        if runtime.get("has_active"):
            if self._should_auto_recall_stage(runtime):
                result = self._post_action(session, "recall_stage", {}, retry_network=True)
                if not result.get("success"):
                    raise ValueError(result.get("message") or "收回演出失败")
                recall = result.get("result") or {}
                gain_points = self._safe_int(recall.get("point_gain"), 0)
                gain_magic = self._safe_int(recall.get("magic_gain"), 0)
                lines.append(f"🎁 收演：声誉+{gain_points}，魔力+{gain_magic}")
                state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
            else:
                return state, lines

        runtime = self._build_stage_runtime(state)
        if runtime.get("has_active"):
            return state, lines

        plan = self._build_stage_plan(state)
        placements = plan.get("placements") or []
        if not placements:
            return state, lines

        result = self._post_action(
            session,
            "confirm_stage_cast",
            {"effect_key": plan.get("effect_key") or "basic", "placements": json.dumps(placements, ensure_ascii=False)},
            retry_network=True,
        )
        if not result.get("success"):
            raise ValueError(result.get("message") or "启动演出失败")
        state = self._ensure_stage_state_after_confirm(session, self._extract_action_state(result) or {})
        lines.append(f"🎭 开演：{plan.get('effect_name') or '舞台效果'} / 演员{len(placements)}位")
        return state, lines

    def _manual_spin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        requested = max(1, self._safe_int(payload.get("count"), 1))
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        spin = state.get("spin") or {}
        remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))
        if remaining <= 0:
            raise ValueError("今日老虎机次数已用完")
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_spin_batch"), 10))
        count = min(requested, remaining, max_batch)
        before_bags = self._bag_quantity_map(state)
        result = self._post_action(session, "spin_slot", {"count": count}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "老虎机转动失败")
        after_state = self._ensure_stage_state_after_confirm(session, self._extract_action_state(result) or {})
        diff_text = self._format_named_counts(self._bag_quantity_diff(before_bags, after_state))
        lines = [f"🎰 老虎机：{diff_text or f'已转动 {count} 次'}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or lines[0], "emoji_status": emoji_status}

    def _manual_open_bag(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tier = max(1, self._safe_int(payload.get("tier"), 1))
        requested = max(1, self._safe_int(payload.get("count"), 1))
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        bag = self._find_bag(state, tier)
        if not bag:
            raise ValueError("未找到对应表情包")
        quantity = self._safe_int(bag.get("quantity"), 0)
        if quantity <= 0:
            raise ValueError("当前没有可开启的表情包")
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_open_bag_batch"), 12))
        count = min(requested, quantity, max_batch)
        result = self._post_action(session, "open_bag", {"tier": tier, "count": count}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "开包失败")
        after_state = self._ensure_stage_state_after_confirm(session, self._extract_action_state(result) or {})
        lines = [f"📦 开包：{self._compact_bag_name(bag.get('name') or f'表情包{tier}')}×{count}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "开包成功", "emoji_status": emoji_status}

    def _manual_accept_open(self) -> Dict[str, Any]:
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        pending = state.get("pending_open") or {}
        if not pending:
            raise ValueError("当前没有待处理开包结果")
        item_text = self._format_pending_item_counts(pending)
        result: Dict[str, Any] = {}
        try:
            result = self._post_action(session, "accept_open", {}, retry_network=True)
        except Exception:
            recovered_state = self._recover_accept_open_state(session)
            if recovered_state is None:
                raise
            after_state = recovered_state
        else:
            if result.get("success"):
                after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
            else:
                recovered_state = self._recover_accept_open_state(session)
                if recovered_state is None:
                    raise ValueError(result.get("message") or "收下失败")
                after_state = recovered_state
        lines = [f"📥 收下：{item_text or (pending.get('bag_name') or '开包结果')}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "已收下", "emoji_status": emoji_status}

    def _manual_reroll_open(self) -> Dict[str, Any]:
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        pending = state.get("pending_open") or {}
        if not pending:
            raise ValueError("当前没有待处理开包结果")
        next_cost = self._safe_int(pending.get("next_reroll_cost"), 0)
        result = self._post_action(session, "reroll_open", {}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "重开失败")
        after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
        lines = [f"🔁 重开：消耗 {next_cost} 魔力"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "已重开", "emoji_status": emoji_status}

    def _manual_upgrade_bag(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        rule_key = str(payload.get("rule_key") or "").strip()
        times = max(1, self._safe_int(payload.get("times"), 1))
        if not rule_key:
            raise ValueError("缺少合成规则")
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        rule = self._find_upgrade_rule(state, rule_key)
        if not rule:
            raise ValueError("未找到合成规则")
        max_times = self._max_upgrade_times(state, rule)
        if max_times <= 0:
            raise ValueError("当前材料或魔力不足")
        run_times = min(times, max_times)
        result = self._post_action(session, "upgrade_bag", {"rule_key": rule_key, "times": run_times}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "合成失败")
        after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
        produce = self._safe_int(rule.get("produce"), 1) * run_times
        lines = [f"🧪 合成：{rule.get('to_name') or '高级表情包'}×{produce}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "合成成功", "emoji_status": emoji_status}

    def _manual_expand_stage_row(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row_index = max(1, self._safe_int(payload.get("row_index"), 1))
        session = self._build_session()
        result = self._post_action(session, "expand_stage_row", {"row_index": row_index}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "扩展失败")
        after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
        lines = [f"🧱 扩展：舞台第 {row_index} 行 +1 格"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "扩展成功", "emoji_status": emoji_status}

    def _manual_confirm_stage(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        effect_key = str(payload.get("effect_key") or "basic").strip() or "basic"
        placements_raw = payload.get("placements") or []
        placements: List[Dict[str, Any]] = []
        for item in self._iter_dicts(placements_raw):
            row_index = self._safe_int(item.get("row_index"), 0)
            slot_index = self._safe_int(item.get("slot_index"), 0)
            emoji_code = str(item.get("emoji_code") or "").strip()
            if row_index > 0 and slot_index > 0 and emoji_code:
                placements.append({"row_index": row_index, "slot_index": slot_index, "emoji_code": emoji_code})
        if not placements:
            raise ValueError("缺少有效的演出阵容")
        session = self._build_session()
        result = self._post_action(
            session,
            "confirm_stage_cast",
            {"effect_key": effect_key, "placements": json.dumps(placements, ensure_ascii=False)},
            retry_network=True,
        )
        if not result.get("success"):
            raise ValueError(result.get("message") or "确认演出失败")
        after_state = self._ensure_stage_state_after_confirm(session, self._extract_action_state(result) or {})
        effect = self._find_effect(after_state, effect_key) or {}
        lines = [f"🎭 开演：{effect.get('name') or effect_key} / 演员{len(placements)}位"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "演出已开始", "emoji_status": emoji_status}

    def _manual_recall_stage(self) -> Dict[str, Any]:
        session = self._build_session()
        result = self._post_action(session, "recall_stage", {}, retry_network=True)
        if not result.get("success"):
            raise ValueError(result.get("message") or "收回演出失败")
        recall = result.get("result") or {}
        after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
        lines = [f"🎁 收演：声誉+{self._safe_int(recall.get('point_gain'), 0)}，魔力+{self._safe_int(recall.get('magic_gain'), 0)}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": result.get("message") or "已收回演出", "emoji_status": emoji_status}

    def _send_report(self, lines: List[str], next_run: Optional[int]):
        action_lines = [
            line for line in lines
            if str(line or "").strip()
            and not str(line).startswith("⏰ ")
            and not str(line).startswith("📥 收下：")
        ]
        if not action_lines:
            return
        chunks = [
            self.SUMMARY_LINE,
            *action_lines,
            "",
            self.SUMMARY_LINE,
            f"⏰ 下次运行：{self._format_ts(next_run) or '等待刷新'}",
            self.SUMMARY_LINE,
        ]
        self.post_message(
            title="【🎭SQ表情】 任务报告",
            mtype=NotificationType.Plugin,
            text="\n".join(chunks),
        )

    def _refresh_and_store_status(
        self,
        state: Dict[str, Any],
        next_run: Optional[int],
        summary_lines: List[str],
        record_run: bool = True,
    ) -> Dict[str, Any]:
        self._schedule_next_run(next_run, reason="refresh-state")
        emoji_status = self._build_ui_state(state, next_run, summary_lines)
        self.save_data("emoji_status", emoji_status)
        self.save_data("state", self._build_state_record(state, next_run, summary_lines))
        if record_run:
            self.save_data("last_run", self._format_time(self._aware_now()))
            self._append_history(summary_lines, next_run)
        return emoji_status

    def _build_state_record(self, state: Dict[str, Any], next_run: Optional[int], summary_lines: List[str]) -> Dict[str, Any]:
        return {
            "schema_version": self.plugin_version,
            "time": self._format_time(self._aware_now()),
            "next_run_time": self._format_ts(next_run),
            "next_trigger_time": self._format_time(self._load_saved_next_trigger()),
            "summary": summary_lines,
            "user": state.get("user") or {},
            "spin": state.get("spin") or {},
            "bags": state.get("bags") or [],
            "effects": state.get("effects") or [],
            "stage": state.get("stage") or {},
        }

    def _compute_next_run(self, state: Dict[str, Any]) -> Optional[int]:
        if not self._has_auto_jobs_enabled():
            return 0

        now_ts = int(time.time())
        candidates: List[int] = []

        if self._auto_stage:
            runtime = self._build_stage_runtime(state)
            if runtime.get("has_active"):
                end_ts = self._safe_int(runtime.get("remaining_end_ts"), 0)
                if end_ts > 0:
                    candidates.append(end_ts)
                elif self._safe_int(runtime.get("remaining_seconds"), 0) > 0:
                    candidates.append(now_ts + self._safe_int(runtime.get("remaining_seconds"), 0))
                else:
                    candidates.append(now_ts + 300)
            elif runtime.get("can_start"):
                candidates.append(now_ts + 5)
            else:
                candidates.append(now_ts + 6 * 3600)

        if self._auto_spin or self._auto_open_bags:
            pending = state.get("pending_open") or {}
            if pending:
                candidates.append(now_ts + 5)
            else:
                slot_next = self._get_cron_next_ts(self._spin_cron)
                if slot_next:
                    candidates.append(slot_next)

        candidates = [candidate for candidate in candidates if candidate > 0]
        return min(candidates) if candidates else 0

    def _should_skip_run(self) -> bool:
        next_run = self._load_saved_next_run()
        if not next_run:
            return False
        now = self._aware_now()
        return now + timedelta(seconds=self._skip_before_seconds) < next_run

    def _is_pre_refresh_trigger(self) -> bool:
        return (self._load_saved_next_trigger_mode() or "run") == "refresh"

    def _schedule_next_run(self, next_run_ts: Optional[int], reason: str = ""):
        next_run_ts = self._safe_int(next_run_ts, 0)
        if next_run_ts > 0:
            next_run = self._aware_from_timestamp(next_run_ts)
            now = self._aware_now()
            pre_refresh_time = next_run - timedelta(seconds=self.PRE_REFRESH_SECONDS)
            if pre_refresh_time > now + timedelta(seconds=5):
                next_trigger = pre_refresh_time
                trigger_mode = "refresh"
            else:
                next_trigger = next_run + timedelta(seconds=self._schedule_buffer_seconds)
                trigger_mode = "run"
            self._next_run_time = next_run
            self._next_trigger_time = next_trigger
            self._next_trigger_mode = trigger_mode
            self.save_data("next_run_time", self._format_time(next_run))
            self.save_data("next_trigger_time", self._format_time(next_trigger))
            self.save_data("next_trigger_mode", trigger_mode)
        else:
            self._next_run_time = None
            self._next_trigger_time = None
            self._next_trigger_mode = "run"
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", "")
            self.save_data("next_trigger_mode", "")
        if self._enabled and self._has_auto_jobs_enabled():
            self._bootstrap_pending = False
            self._reregister_plugin(reason or "schedule-next-run")

    def _reregister_plugin(self, reason: str = ""):
        try:
            Scheduler().update_plugin_job(self.__class__.__name__)
        except Exception:
            try:
                Scheduler().reload_plugin_job(self.__class__.__name__)
            except Exception as err:
                logger.warning("%s 重新注册调度失败：%s", self.plugin_name, err)
                return
        logger.info("%s 已重新注册调度：%s", self.plugin_name, reason or "update")

    def _get_next_run_for_service(self) -> Optional[datetime]:
        if self._bootstrap_pending:
            return self._aware_now() + timedelta(seconds=3)
        if self._next_trigger_time:
            return self._next_trigger_time
        return self._load_saved_next_trigger()

    def _load_saved_next_run(self) -> Optional[datetime]:
        if self._next_run_time:
            return self._next_run_time
        self._next_run_time = self._parse_datetime(self.get_data("next_run_time") or ((self.get_data("state") or {}).get("next_run_time")))
        return self._next_run_time

    def _load_saved_next_trigger(self) -> Optional[datetime]:
        if self._next_trigger_time:
            return self._next_trigger_time
        self._next_trigger_time = self._parse_datetime(self.get_data("next_trigger_time") or ((self.get_data("state") or {}).get("next_trigger_time")))
        return self._next_trigger_time

    def _load_saved_next_trigger_mode(self) -> str:
        if self._next_trigger_mode:
            return self._next_trigger_mode
        self._next_trigger_mode = str(self.get_data("next_trigger_mode") or "run").strip() or "run"
        return self._next_trigger_mode

    def _append_history(self, lines: List[str], next_run: Optional[int]):
        if not lines:
            return
        history = list(self.get_data("history") or [])
        history.insert(0, {
            "title": "任务结果",
            "time": self._format_time(self._aware_now()),
            "next_run": self._format_ts(next_run),
            "lines": list(lines),
        })
        self.save_data("history", history[:20])

    def _build_ui_state(self, state: Dict[str, Any], next_run: Optional[int], summary_lines: List[str]) -> Dict[str, Any]:
        return {
            "schema_version": self.plugin_version,
            "title": "表情演出",
            "subtitle": "老虎机、开包、舞台演出、获取执行记录。",
            "cookie_source": self._cookie_source,
            "summary": summary_lines,
            "next_run_time": self._format_ts(next_run),
            "next_run_ts": next_run or 0,
            "next_trigger_time": self._format_time(self._load_saved_next_trigger()),
            "next_trigger_ts": int(self._load_saved_next_trigger().timestamp()) if self._load_saved_next_trigger() else 0,
            "stats": self._build_stats(state),
            "slot_machine": self._build_slot_machine(state),
            "bags": self._build_bags(state),
            "pending_open": self._build_pending_open(state),
            "actor_tabs": self._build_actor_tier_summary(state),
            "actors_by_tier": self._build_actor_inventory(state),
            "effects": self._build_effects(state),
            "stage": self._build_stage_runtime(state),
            "stage_rows": self._build_stage_rows(state),
            "history": (self.get_data("history") or [])[:20],
        }

    def _build_stats(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        user = state.get("user") or {}
        spin = state.get("spin") or {}
        collection = state.get("collection") or {}
        return [
            {"label": "当前魔力", "value": self._safe_int(user.get("magic"), 0), "desc": ""},
            {"label": "演出声誉", "value": self._safe_int(user.get("total_points"), 0), "desc": ""},
            {"label": "演出魔力", "value": self._safe_int(user.get("total_magic_earned"), 0), "desc": ""},
            {
                "label": "今日老虎机",
                "value": f"{self._safe_int(spin.get('used'), 0)}/{self._safe_int(spin.get('limit'), 0)}",
                "desc": f"基础{self._safe_int(spin.get('base'), 0)} + f(hnr*等级) {self._safe_int(spin.get('extra'), 0)}",
            },
            {
                "label": "图鉴进度",
                "value": f"{self._safe_int(collection.get('have_count'), 0)}/{self._safe_int(collection.get('all_count'), 0)}",
                "desc": f"UID #{self._safe_int(user.get('id'), 0)} · {user.get('username') or ''}",
            },
        ]

    def _build_slot_machine(self, state: Dict[str, Any]) -> Dict[str, Any]:
        spin = state.get("spin") or {}
        symbols = state.get("symbols") or []
        if not isinstance(symbols, list) or len(symbols) < 3:
            symbols = ["🤡", "👑", "🎩"]
        limit = self._safe_int(spin.get("limit"), 0)
        used = self._safe_int(spin.get("used"), 0)
        remaining = max(0, limit - used)
        return {
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "base": self._safe_int(spin.get("base"), 0),
            "extra": self._safe_int(spin.get("extra"), 0),
            "max_batch": max(1, self._safe_int((state.get("limits") or {}).get("max_spin_batch"), 10)),
            "reels": [str(symbols[0]), str(symbols[1]), str(symbols[2])],
        }

    def _build_bags(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        rules = {self._safe_int(item.get("from"), 0): item for item in self._iter_dicts(state.get("upgrade_rules") or [])}
        bags: List[Dict[str, Any]] = []
        for bag in self._iter_dicts(state.get("bags") or []):
            tier = self._safe_int(bag.get("tier"), 0)
            quantity = self._safe_int(bag.get("quantity"), 0)
            rule = rules.get(tier)
            max_upgrade = self._max_upgrade_times(state, rule) if rule else 0
            upgrade_tip = ""
            if rule:
                upgrade_tip = (
                    f"每次：{self._safe_int(rule.get('consume'), 0)}{rule.get('from_name') or ''}"
                    f"→{self._safe_int(rule.get('produce'), 0)}{rule.get('to_name') or ''}，"
                    f"{self._safe_int(rule.get('magic_cost'), 0)}魔力，最多{max_upgrade}次"
                )
            bags.append({
                "tier": tier,
                "name": bag.get("name") or f"表情包{tier}",
                "quantity": quantity,
                "bg_color": bag.get("bg_color") or "",
                "badge_color": bag.get("badge_color") or "",
                "bg_image": self._absolute_url(bag.get("bg_image") or ""),
                "reroll_cost": self._safe_int(bag.get("reroll_cost"), 0),
                "can_open": quantity > 0,
                "open_max": max(1, min(quantity, self._safe_int((state.get("limits") or {}).get("max_open_bag_batch"), 12))) if quantity > 0 else 1,
                "upgrade_rule": {
                    "key": rule.get("key"),
                    "from": self._safe_int(rule.get("from"), 0),
                    "to": self._safe_int(rule.get("to"), 0),
                    "consume": self._safe_int(rule.get("consume"), 0),
                    "produce": self._safe_int(rule.get("produce"), 0),
                    "magic_cost": self._safe_int(rule.get("magic_cost"), 0),
                    "from_name": rule.get("from_name") or "",
                    "to_name": rule.get("to_name") or "",
                    "max_times": max_upgrade,
                    "tip": upgrade_tip,
                    "enabled": max_upgrade > 0,
                } if rule else None,
            })
        return bags

    def _build_pending_open(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pending = state.get("pending_open") or {}
        if not pending:
            return {}
        bag_tier = self._safe_int(pending.get("bag_tier"), 1)
        bag = self._find_bag(state, bag_tier) or {}
        items: List[Dict[str, Any]] = []
        for item in self._iter_dicts(pending.get("result_items") or []):
            items.append({
                "emoji": item.get("emoji") or "❓",
                "points": self._safe_int(item.get("points"), 0),
                "magic": self._safe_int(item.get("magic"), 0),
                "owned_count": self._safe_int(item.get("owned_count"), 0),
            })
        return {
            "bag_tier": bag_tier,
            "bag_name": pending.get("bag_name") or bag.get("name") or "",
            "bag_count": self._safe_int(pending.get("bag_count"), 0),
            "reroll_count": self._safe_int(pending.get("reroll_count"), 0),
            "next_reroll_cost": self._safe_int(pending.get("next_reroll_cost"), 0),
            "bg_color": bag.get("bg_color") or "",
            "items": items,
        }

    def _build_actor_tier_summary(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        codex = state.get("codex_by_tier") or {}
        tier_names = state.get("tier_name_map") or {}
        result: List[Dict[str, Any]] = []
        for tier in range(1, 5):
            items = self._iter_dicts(codex.get(str(tier)) or codex.get(tier) or [])
            owned = sum(1 for item in items if item.get("owned"))
            total = len(items)
            result.append({
                "tier": tier,
                "name": tier_names.get(str(tier)) or tier_names.get(tier) or f"{tier}级表情包",
                "owned": owned,
                "total": total,
                "complete": total > 0 and owned >= total,
            })
        return result

    def _build_actor_inventory(self, state: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        result: Dict[str, List[Dict[str, Any]]] = {}
        inventory = state.get("actor_inventory_by_tier") or {}
        for tier in range(1, 5):
            items = []
            for item in self._iter_dicts(inventory.get(str(tier)) or inventory.get(tier) or []):
                quantity = self._safe_int(item.get("quantity"), 0)
                available = self._safe_int(item.get("available"), 0)
                items.append({
                    "code": item.get("code") or "",
                    "emoji": item.get("emoji") or "❓",
                    "tier": tier,
                    "quantity": quantity,
                    "available": available,
                    "locked_quantity": self._safe_int(item.get("locked_quantity"), 0),
                    "points": self._safe_int(item.get("points"), 0),
                    "magic": self._safe_int(item.get("magic"), 0),
                    "can_place": available > 0,
                })
            result[str(tier)] = items
        return result

    def _build_effects(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        selected = str((state.get("stage") or {}).get("selected_effect") or "basic")
        result: List[Dict[str, Any]] = []
        for effect in self._iter_dicts(state.get("effects") or []):
            result.append({
                "key": effect.get("key") or "",
                "name": effect.get("name") or "",
                "point_bonus_pct": round(float(effect.get("point_bonus") or 0) * 100),
                "magic_bonus_pct": round(float(effect.get("magic_bonus") or 0) * 100),
                "duration_seconds": self._safe_int(effect.get("duration_seconds"), 0),
                "duration_text": effect.get("duration_text") or "",
                "unlocked": bool(effect.get("unlocked")),
                "unlock_text": effect.get("unlock_text") or "",
                "active": str(effect.get("key") or "") == selected,
            })
        return result

    def _build_effect_options(self) -> List[Dict[str, Any]]:
        options: List[Dict[str, Any]] = [{"title": "自动选择演出舞台效果", "value": "auto"}]
        state = self.get_data("state") or {}
        effects = list(self._iter_dicts(state.get("effects") or []))
        if not effects:
            emoji_status = self.get_data("emoji_status") or {}
            effects = list(self._iter_dicts(emoji_status.get("effects") or []))
        if not effects and self._cookie:
            try:
                self._refresh_state(reason="config-options", record_run=False)
            except Exception as err:
                logger.warning("%s 刷新舞台效果选项失败：%s", self.plugin_name, self._get_error_detail(err))
            state = self.get_data("state") or {}
            effects = list(self._iter_dicts(state.get("effects") or []))
            if not effects:
                emoji_status = self.get_data("emoji_status") or {}
                effects = list(self._iter_dicts(emoji_status.get("effects") or []))
        seen_keys = {"auto"}
        for effect in effects:
            key = str(effect.get("key") or "").strip()
            if not key or key in seen_keys:
                continue
            if not bool(effect.get("unlocked")):
                continue
            seen_keys.add(key)
            options.append({
                "title": str(effect.get("name") or key),
                "value": key,
            })
        return options

    def _build_stage_runtime(self, state: Dict[str, Any]) -> Dict[str, Any]:
        stage = state.get("stage") or {}
        effect_map = {str(item.get("key") or ""): item for item in self._iter_dicts(state.get("effects") or [])}
        active_slots = self._stage_active_slots(stage)
        has_active = bool(active_slots)
        selected_effect = str(stage.get("selected_effect") or "basic")
        can_start = bool(self._build_stage_plan(state).get("placements")) if not has_active else False
        if not has_active:
            effect = self._find_effect(state, selected_effect) or {}
            return {
                "has_active": False,
                "can_recall": False,
                "can_start": can_start,
                "selected_effect": selected_effect,
                "remaining_seconds": 0,
                "remaining_end_ts": 0,
                "remaining_text": "当前无演出演员",
                "current_effect_name": effect.get("name") or "未开始",
                "expected_points": 0,
                "expected_magic": 0,
                "active_count": 0,
                "current_text": "当前无演出演员",
            }

        first_slot = active_slots[0]
        effect_key = str(first_slot.get("effect_key") or selected_effect)
        effect = effect_map.get(effect_key, {})
        remaining = max(self._safe_int(first_slot.get("remaining_seconds"), 0), 0)
        end_ts = self._extract_slot_end_ts(first_slot, remaining)
        point_gain = 0
        magic_gain = 0
        for slot in active_slots:
            point_gain += ceil(self._safe_int(slot.get("point_bonus"), 0) * (1 + float(effect.get("point_bonus") or 0)))
            magic_gain += ceil(self._safe_int(slot.get("magic_bonus"), 0) * (1 + float(effect.get("magic_bonus") or 0)))
        effect_name = first_slot.get("effect_name") or effect.get("name") or "舞台效果"
        can_recall = remaining <= 0 or (end_ts > 0 and end_ts <= int(time.time()))
        return {
            "has_active": True,
            "can_recall": can_recall,
            "can_start": False,
            "selected_effect": effect_key,
            "remaining_seconds": remaining,
            "remaining_end_ts": end_ts,
            "remaining_text": self._format_duration(remaining) if remaining > 0 else "已到可收回时间",
            "current_effect_name": effect_name,
            "expected_points": point_gain,
            "expected_magic": magic_gain,
            "active_count": len(active_slots),
            "current_text": f"正在演出中，剩余时间：{self._format_duration(remaining) if remaining > 0 else '已完成'}",
        }

    def _build_stage_rows(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        stage = state.get("stage") or {}
        active_map: Dict[Tuple[int, int], Dict[str, Any]] = {}
        for slot in self._stage_active_slots(stage):
            row_index = self._safe_int(slot.get("row_index"), 0)
            slot_index = self._safe_int(slot.get("slot_index"), 0)
            if row_index > 0 and slot_index > 0:
                active_map[(row_index, slot_index)] = slot

        result: List[Dict[str, Any]] = []
        for row in self._iter_dicts(stage.get("rows") or []):
            row_index = self._safe_int(row.get("row_index"), 0)
            slot_count = self._safe_int(row.get("slot_count"), 0)
            row_slots: List[Dict[str, Any]] = []
            for slot_index in range(1, slot_count + 1):
                active = active_map.get((row_index, slot_index)) or {}
                remaining = self._safe_int(active.get("remaining_seconds"), 0)
                row_slots.append({
                    "row_index": row_index,
                    "slot_index": slot_index,
                    "filled": bool(active),
                    "emoji_code": active.get("emoji_code") or "",
                    "emoji": active.get("emoji") or "",
                    "points": self._safe_int(active.get("point_bonus"), 0),
                    "magic": self._safe_int(active.get("magic_bonus"), 0),
                    "remaining_seconds": remaining,
                    "remaining_end_ts": self._extract_slot_end_ts(active, remaining) if active else 0,
                })
            result.append({
                "row_index": row_index,
                "name": row.get("name") or f"第{row_index}舞台",
                "unlock_points": self._safe_int(row.get("unlock_points"), 0),
                "unlocked": bool(row.get("unlocked")),
                "slot_count": slot_count,
                "max_slots": self._safe_int(row.get("max_slots"), slot_count),
                "can_expand": bool(row.get("can_expand")),
                "next_expand_cost": self._safe_int(row.get("next_expand_cost"), 0),
                "slots": row_slots,
            })
        return result

    def _build_stage_plan(self, state: Dict[str, Any], tier_filter: Optional[int] = None, effect_key: Optional[str] = None) -> Dict[str, Any]:
        effect = self._find_effect(state, effect_key) if effect_key else self._choose_best_effect(state)
        actors = self._available_actors(state, tier_filter=tier_filter)
        rows = [row for row in self._iter_dicts((state.get("stage") or {}).get("rows") or []) if row.get("unlocked")]
        placements: List[Dict[str, Any]] = []
        actor_index = 0
        remaining = self._safe_int(actors[0].get("available"), 0) if actors else 0
        for row in rows:
            row_index = self._safe_int(row.get("row_index"), 0)
            slot_count = self._safe_int(row.get("slot_count"), 0)
            for slot_index in range(1, slot_count + 1):
                while actor_index < len(actors) and remaining <= 0:
                    actor_index += 1
                    remaining = self._safe_int(actors[actor_index].get("available"), 0) if actor_index < len(actors) else 0
                if actor_index >= len(actors):
                    break
                placements.append({
                    "row_index": row_index,
                    "slot_index": slot_index,
                    "emoji_code": actors[actor_index].get("code") or "",
                })
                remaining -= 1
        return {
            "effect_key": effect.get("key") or "basic",
            "effect_name": effect.get("name") or "舞台效果",
            "placements": placements,
        }

    def _choose_best_effect(self, state: Dict[str, Any]) -> Dict[str, Any]:
        preferred_key = str(self._auto_stage_effect_key or "auto").strip()
        if preferred_key and preferred_key != "auto":
            preferred = self._find_effect(state, preferred_key)
            if preferred and preferred.get("unlocked"):
                return preferred
        unlocked = [item for item in self._iter_dicts(state.get("effects") or []) if item.get("unlocked")]
        if not unlocked:
            return {"key": "basic", "name": "简陋舞台效果"}
        unlocked.sort(
            key=lambda item: (
                float(item.get("point_bonus") or 0) * 10 + float(item.get("magic_bonus") or 0),
                float(item.get("point_bonus") or 0),
                float(item.get("magic_bonus") or 0),
            ),
            reverse=True,
        )
        return unlocked[0]

    def _available_actors(self, state: Dict[str, Any], tier_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        inventory = state.get("actor_inventory_by_tier") or {}
        actors: List[Dict[str, Any]] = []
        tiers = [tier_filter] if tier_filter else [1, 2, 3, 4]
        for tier in tiers:
            for item in self._iter_dicts(inventory.get(str(tier)) or inventory.get(tier) or []):
                available = self._safe_int(item.get("available"), 0)
                if available <= 0:
                    continue
                actors.append({
                    "code": item.get("code") or "",
                    "emoji": item.get("emoji") or "❓",
                    "tier": self._safe_int(item.get("tier"), tier),
                    "available": available,
                    "points": self._safe_int(item.get("points"), 0),
                    "magic": self._safe_int(item.get("magic"), 0),
                })
        actors.sort(key=lambda item: (item["points"], item["magic"], item["available"], -item["tier"]), reverse=True)
        return actors

    def _find_bag(self, state: Dict[str, Any], tier: int) -> Dict[str, Any]:
        for bag in self._iter_dicts(state.get("bags") or []):
            if self._safe_int(bag.get("tier"), 0) == tier:
                return bag
        return {}

    def _find_effect(self, state: Dict[str, Any], effect_key: Optional[str]) -> Dict[str, Any]:
        effect_key = str(effect_key or "").strip()
        for effect in self._iter_dicts(state.get("effects") or []):
            if str(effect.get("key") or "").strip() == effect_key:
                return effect
        return {}

    def _find_upgrade_rule(self, state: Dict[str, Any], rule_key: str) -> Dict[str, Any]:
        for rule in self._iter_dicts(state.get("upgrade_rules") or []):
            if str(rule.get("key") or "").strip() == rule_key:
                return rule
        return {}

    def _max_upgrade_times(self, state: Dict[str, Any], rule: Optional[Dict[str, Any]]) -> int:
        if not isinstance(rule, dict):
            return 0
        from_tier = self._safe_int(rule.get("from"), 0)
        consume = max(1, self._safe_int(rule.get("consume"), 1))
        magic_cost = max(0, self._safe_int(rule.get("magic_cost"), 0))
        quantity = self._safe_int(self._find_bag(state, from_tier).get("quantity"), 0)
        magic = self._safe_int((state.get("user") or {}).get("magic"), 0)
        by_bag = quantity // consume
        by_magic = by_bag if magic_cost <= 0 else magic // magic_cost
        return max(0, min(by_bag, by_magic))

    def _bag_quantity_map(self, state: Dict[str, Any]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for bag in self._iter_dicts(state.get("bags") or []):
            name = self._compact_bag_name(bag.get("name") or f"表情包{self._safe_int(bag.get('tier'), 0)}")
            result[name] = self._safe_int(bag.get("quantity"), 0)
        return result

    def _bag_quantity_diff(self, before: Dict[str, int], after_state: Dict[str, Any]) -> Dict[str, int]:
        after = self._bag_quantity_map(after_state)
        names = set(before) | set(after)
        diff: Dict[str, int] = {}
        for name in names:
            value = after.get(name, 0) - before.get(name, 0)
            if value > 0:
                diff[name] = value
        return diff

    def _format_pending_item_counts(self, pending: Dict[str, Any]) -> str:
        counts: Dict[str, int] = {}
        for item in self._iter_dicts(pending.get("result_items") or []):
            emoji = str(item.get("emoji") or "❓")
            counts[emoji] = counts.get(emoji, 0) + 1
        return self._format_named_counts(counts)

    @staticmethod
    def _format_named_counts(counts: Dict[str, int]) -> str:
        return "  ".join(f"{name}×{quantity}" for name, quantity in counts.items() if quantity > 0)

    @staticmethod
    def _compact_bag_name(name: Any) -> str:
        text = str(name or "").strip()
        return text[:-3] if text.endswith("表情包") else text

    def _stage_active_slots(self, stage: Dict[str, Any]) -> List[Dict[str, Any]]:
        slots = self._iter_dicts(stage.get("active_slots") or [])
        if slots:
            return slots
        result: List[Dict[str, Any]] = []
        for row in self._iter_dicts(stage.get("rows") or []):
            for slot in self._iter_dicts(row.get("slots") or []):
                if slot.get("emoji_code"):
                    result.append(slot)
        return result

    def _extract_slot_end_ts(self, slot: Dict[str, Any], remaining_seconds: Optional[int] = None) -> int:
        if not slot:
            return 0
        for key in ("end_ts", "ends_at_ts", "ends_at_timestamp"):
            ts = self._safe_int(slot.get(key), 0)
            if ts > 0:
                return ts
        parsed = self._parse_datetime(slot.get("ends_at") or slot.get("end_time"))
        if parsed:
            return int(parsed.timestamp())
        remain = max(0, self._safe_int(remaining_seconds if remaining_seconds is not None else slot.get("remaining_seconds"), 0))
        return int(time.time()) + remain if remain > 0 else 0

    def _next_midnight_ts(self) -> int:
        now = self._aware_now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(tomorrow.timestamp())

    def _get_cron_next_ts(self, cron_expr: str) -> Optional[int]:
        expr = (cron_expr or "").strip()
        if not expr:
            return None
        try:
            timezone = pytz.timezone(settings.TZ)
            now_dt = self._aware_now() + timedelta(seconds=1)
            trigger = CronTrigger.from_crontab(expr, timezone=timezone)
            next_fire = trigger.get_next_fire_time(None, now_dt)
            return int(next_fire.timestamp()) if next_fire else None
        except Exception as err:
            logger.warning("%s CRON 表达式无效：%s | %s", self.plugin_name, expr, err)
            return None

    def _ensure_stage_state_after_confirm(self, session: requests.Session, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate = state if isinstance(state, dict) else {}
        for attempt in range(3):
            if candidate and self._build_stage_runtime(candidate).get("has_active"):
                return candidate
            if attempt >= 2:
                break
            time.sleep(1)
            candidate = self._fetch_bundle(session)["state"]
        return candidate

    def _should_auto_recall_stage(self, runtime: Dict[str, Any]) -> bool:
        remaining = self._safe_int(runtime.get("remaining_seconds"), 0)
        if remaining <= 0:
            return True
        end_ts = self._safe_int(runtime.get("remaining_end_ts"), 0)
        return end_ts > 0 and end_ts <= int(time.time())

    def _has_auto_jobs_enabled(self) -> bool:
        return bool(self._auto_stage or self._auto_spin or self._auto_open_bags)

    def _recover_spin_state(
        self,
        session: requests.Session,
        before_state: Dict[str, Any],
        before_bags: Dict[str, int],
        used_before: int,
        requested_count: int,
    ) -> Dict[str, Any]:
        current_state = self._fetch_bundle(session)["state"] or {}
        used_after = self._safe_int((current_state.get("spin") or {}).get("used"), 0)
        used_delta = max(0, used_after - used_before)
        bag_diff = self._bag_quantity_diff(before_bags, current_state)
        bag_gain = sum(max(0, value) for value in bag_diff.values())
        recovered_spins = used_delta if used_delta > 0 else bag_gain
        if recovered_spins <= 0:
            limit = self._safe_int((current_state.get("spin") or {}).get("limit"), 0)
            if limit > 0 and used_after >= limit and used_before < limit:
                recovered_spins = min(max(0, limit - used_before), max(1, requested_count))
        return {
            "state": current_state,
            "spins": recovered_spins,
            "bag_diff": bag_diff,
        }

    def _recover_accept_open_state(self, session: requests.Session) -> Optional[Dict[str, Any]]:
        current_state = self._fetch_bundle(session)["state"] or {}
        pending = current_state.get("pending_open") or {}
        if pending:
            return None
        return current_state

    def _run_auto_spin(self, session: requests.Session, state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        spin = state.get("spin") or {}
        remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))
        if remaining <= 0:
            return state, []

        before_bags = self._bag_quantity_map(state)
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_spin_batch"), 10))
        total_spins = 0
        while remaining > 0:
            batch = min(remaining, max_batch)
            used_before = self._safe_int((state.get("spin") or {}).get("used"), 0)
            try:
                result = self._post_action(session, "spin_slot", {"count": batch}, retry_network=True)
            except Exception:
                recovered = self._recover_spin_state(session, state, before_bags, used_before, batch)
                recovered_state = recovered.get("state") or {}
                recovered_spins = self._safe_int(recovered.get("spins"), 0)
                if not recovered_state or recovered_spins <= 0:
                    raise
                logger.info("%s 老虎机状态已确认，按最新状态计入 %s 次", self.plugin_name, recovered_spins)
                total_spins += recovered_spins
                state = recovered_state
            else:
                if result.get("success"):
                    total_spins += batch
                    state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
                else:
                    recovered = self._recover_spin_state(session, state, before_bags, used_before, batch)
                    recovered_state = recovered.get("state") or {}
                    recovered_spins = self._safe_int(recovered.get("spins"), 0)
                    if not recovered_state or recovered_spins <= 0:
                        raise ValueError(result.get("message") or "老虎机转动失败")
                    logger.info("%s 老虎机状态已确认，按最新状态计入 %s 次", self.plugin_name, recovered_spins)
                    total_spins += recovered_spins
                    state = recovered_state

            spin = state.get("spin") or {}
            remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))

        diff_text = self._format_named_counts(self._bag_quantity_diff(before_bags, state))
        if diff_text:
            return state, [f"🎰 老虎机：{diff_text}"]
        return state, [f"🎰 老虎机：已转动 {total_spins} 次"] if total_spins else []

    def _manual_spin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        requested = max(1, self._safe_int(payload.get("count"), 1))
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        spin = state.get("spin") or {}
        remaining = max(0, self._safe_int(spin.get("limit"), 0) - self._safe_int(spin.get("used"), 0))
        if remaining <= 0:
            raise ValueError("今日老虎机次数已用完")
        max_batch = max(1, self._safe_int((state.get("limits") or {}).get("max_spin_batch"), 10))
        count = min(requested, remaining, max_batch)
        before_bags = self._bag_quantity_map(state)
        used_before = self._safe_int((state.get("spin") or {}).get("used"), 0)
        try:
            result = self._post_action(session, "spin_slot", {"count": count}, retry_network=True)
        except Exception:
            recovered = self._recover_spin_state(session, state, before_bags, used_before, count)
            after_state = recovered.get("state") or {}
            recovered_spins = self._safe_int(recovered.get("spins"), 0)
            if not after_state or recovered_spins <= 0:
                raise
            logger.info("%s 手动老虎机状态已确认，按最新状态计入 %s 次", self.plugin_name, recovered_spins)
        else:
            if result.get("success"):
                after_state = self._ensure_stage_state_after_confirm(session, self._extract_action_state(result) or {})
            else:
                recovered = self._recover_spin_state(session, state, before_bags, used_before, count)
                after_state = recovered.get("state") or {}
                recovered_spins = self._safe_int(recovered.get("spins"), 0)
                if not after_state or recovered_spins <= 0:
                    raise ValueError(result.get("message") or "老虎机转动失败")
                logger.info("%s 手动老虎机状态已确认，按最新状态计入 %s 次", self.plugin_name, recovered_spins)
        diff_text = self._format_named_counts(self._bag_quantity_diff(before_bags, after_state))
        lines = [f"🎰 老虎机：{diff_text or f'已转动 {count} 次'}"]
        emoji_status = self._refresh_and_store_status(after_state, self._compute_next_run(after_state), lines)
        return {"message": lines[0], "emoji_status": emoji_status}

    @staticmethod
    def _parse_named_counts(text: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for part in re.split(r"\s{2,}", str(text or "").strip()):
            if "×" not in part:
                continue
            name, quantity = part.rsplit("×", 1)
            try:
                counts[name.strip()] = counts.get(name.strip(), 0) + int(quantity.strip())
            except Exception:
                continue
        return counts

    def _request_with_retry(self, label: str, func):
        last_error = None
        max_attempts = max(1, self._http_retry_times)
        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except Exception as err:
                last_error = err
                if attempt >= max_attempts or not self._is_retryable_network_error(err):
                    break
                delay = max(self._http_retry_delay / 1000.0, 0.2) * attempt
                logger.warning("%s %s failed %s/%s: %s", self.plugin_name, label, attempt, max_attempts, self._get_error_detail(err))
                logger.info("%s %s will retry in %.1fs", self.plugin_name, label, delay)
                time.sleep(delay)
        if last_error:
            raise last_error
        return {}

    @staticmethod
    def _is_retryable_network_error(err: Exception) -> bool:
        if isinstance(err, (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError)):
            return True
        message = str(err).lower()
        retryable_tokens = (
            "timed out",
            "timeout",
            "temporarily unavailable",
            "connection reset",
            "failed to establish a new connection",
            "remote end closed connection",
            "name or service not known",
            "read timed out",
        )
        return any(token in message for token in retryable_tokens)

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        try:
            return int(float(value))
        except Exception:
            return default

    @staticmethod
    def _to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _strip_html(text: Any) -> str:
        value = re.sub(r"<[^>]+>", "", str(text or ""))
        return re.sub(r"\s+", " ", unescape(value)).strip()

    @staticmethod
    def _iter_dicts(items: Any) -> List[Dict[str, Any]]:
        return [item for item in (items or []) if isinstance(item, dict)]

    def _absolute_url(self, url: str) -> str:
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self._site_url}{url}" if url.startswith("/") else f"{self._site_url}/{url}"

    @staticmethod
    def _format_time(dt: Optional[datetime]) -> str:
        if not dt:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_ts(self, timestamp: Optional[int]) -> str:
        return self._format_time(self._aware_from_timestamp(timestamp)) if timestamp else ""

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    def _aware_from_timestamp(self, timestamp: int) -> datetime:
        return datetime.fromtimestamp(int(timestamp), tz=pytz.timezone(settings.TZ))

    def _parse_datetime(self, raw: Any) -> Optional[datetime]:
        if not raw:
            return None
        if isinstance(raw, datetime):
            return raw if raw.tzinfo else pytz.timezone(settings.TZ).localize(raw)
        text = str(raw).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                parsed = datetime.strptime(text, fmt)
                return pytz.timezone(settings.TZ).localize(parsed)
            except Exception:
                continue
        return None

    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        total = max(0, int(seconds or 0))
        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts: List[str] = []
        if days:
            parts.append(f"{days}天")
        if hours:
            parts.append(f"{hours}小时")
        if minutes:
            parts.append(f"{minutes}分钟")
        if secs and not days and not hours:
            parts.append(f"{secs}秒")
        if not parts:
            parts.append("0秒")
        return "".join(parts[:2])

    @staticmethod
    def _get_error_detail(err: Exception) -> str:
        parts = []
        response = getattr(err, "response", None)
        if response is not None and getattr(response, "status_code", None):
            parts.append(str(response.status_code))
        if str(err):
            parts.append(str(err))
        return " | ".join(parts) or "未知错误"

