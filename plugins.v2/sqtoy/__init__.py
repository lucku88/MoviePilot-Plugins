import json
import random
import re
import socket
import time
import traceback
from datetime import datetime, timedelta
from html import unescape
from typing import Any, Dict, List, Optional, Tuple

import pytz
import requests
import urllib3.util.connection as urllib3_connection
from apscheduler.schedulers.background import BackgroundScheduler
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType


class SQToy(_PluginBase):
    plugin_name = "SQ玩偶"
    plugin_desc = "盲盒、回收、展出、获取执行记录。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f9f8.png"
    plugin_version = "0.1.12"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "sqtoy_"
    plugin_order = 68
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    SUMMARY_LINE = "━━━━━━━━━━━━━━"
    PRE_REFRESH_SECONDS = 60

    QUALITY_ORDER = {"珍稀": 4, "稀有": 4, "特别": 3, "高级": 2, "入门": 1}

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _auto_cookie: bool = True
    _auto_collect: bool = True
    _auto_place: bool = True
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
    _collect_retry: int = 3
    _collect_retry_delay: int = 1200
    _place_loop_limit: int = 10
    _place_retry_delay: int = 1500
    _max_target_try: int = 3

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
        self._bootstrap_pending = self._enabled and not self._next_trigger_time

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
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取 SQ玩偶配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 SQ玩偶配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 SQ玩偶状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新 SQ玩偶状态"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行 SQ玩偶"},
            {"path": "/cookie", "endpoint": self._sync_site_cookie_api, "methods": ["GET"], "auth": "bear", "summary": "同步站点 Cookie"},
            {"path": "/collect-slot", "endpoint": self._collect_slot_api, "methods": ["POST"], "auth": "bear", "summary": "手动收回展位玩偶"},
            {"path": "/place-personal", "endpoint": self._place_personal_api, "methods": ["POST"], "auth": "bear", "summary": "上架到我的展柜"},
            {"path": "/random-target", "endpoint": self._random_target_api, "methods": ["POST"], "auth": "bear", "summary": "随机匹配外展目标"},
            {"path": "/view-target", "endpoint": self._view_target_api, "methods": ["POST"], "auth": "bear", "summary": "查看指定展台"},
            {"path": "/place-target", "endpoint": self._place_target_api, "methods": ["POST"], "auth": "bear", "summary": "抢占他人展位"},
            {"path": "/buy-box", "endpoint": self._buy_box_api, "methods": ["POST"], "auth": "bear", "summary": "购买盲盒"},
            {"path": "/open-box", "endpoint": self._open_box_api, "methods": ["POST"], "auth": "bear", "summary": "开启盲盒"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        if self._enabled:
            next_run = self._get_next_run_for_service()
            if next_run:
                services.append({
                    "id": "SQToy_auto",
                    "name": "SQ玩偶初始化" if self._bootstrap_pending else "SQ玩偶智能调度",
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
        logger.info("## 开始执行... %s", self._format_time(self._aware_now()))
        session: Optional[requests.Session] = None
        state: Dict[str, Any] = {}
        html = ""
        collect_names: List[str] = []
        place_names: List[str] = []
        placed_times: List[Dict[str, Any]] = []
        try:
            if not self._enabled and not force:
                return {"success": False, "message": "插件未启用", "status": self._build_status(auto_refresh=False)}

            self._ensure_cookie()
            if self._force_ipv4:
                urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

            rand_delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if rand_delay:
                logger.info("INFO 随机延迟 %s 秒后执行...", rand_delay)
                time.sleep(rand_delay)

            if not force and reason == "schedule" and self._is_pre_refresh_trigger():
                toy_status = self._refresh_state(reason="pre-run-refresh")
                logger.info("%s 已完成运行前 1 分钟预刷新", self.plugin_name)
                return {
                    "success": True,
                    "message": "运行前状态已刷新",
                    "lines": [],
                    "toy_status": toy_status,
                    "status": self._build_status(auto_refresh=False),
                }

            if not force and self._should_skip_run():
                logger.info("INFO 未到计划触发时间，跳过本次运行")
                return {"success": True, "message": "未到计划触发时间，已跳过", "status": self._build_status(auto_refresh=False)}

            session = self._build_session()
            bundle = self._fetch_bundle(session)
            state = bundle["state"] or {}
            html = bundle["html"] or ""
            if not state or not state.get("user"):
                raise ValueError("获取玩偶页面失败，Cookie 可能失效")

            if self._auto_collect:
                self._collect_personal_slots(session, collect_names)
                self._collect_remote_slots(session, state, collect_names)
                bundle = self._fetch_bundle(session)
                state = bundle["state"] or state
                html = bundle["html"] or html
            if self._auto_place:
                placed_times.extend(self._place_personal_slots(session, state, place_names))
                bundle = self._fetch_bundle(session)
                state = bundle["state"] or state
                html = bundle["html"] or html
                placed_times.extend(self._place_target_slots(session, state, place_names))

            final_bundle = self._fetch_bundle(session)
            final_state = final_bundle["state"] or state
            final_html = final_bundle["html"] or html
            gain_exposure, gain_magic = self._summarize_gains(final_state.get("activity_logs") or [], start_time)
            next_run = self._compute_next_run(final_state, placed_times)
            lines = self._build_summary_lines(collect_names, place_names, gain_exposure, gain_magic)
            toy_status = self._refresh_and_store_status(final_state, final_html, next_run, lines)

            if self._notify and lines:
                self._send_report(lines, next_run)

            return {
                "success": True,
                "message": lines[0] if lines else "本次没有可执行动作",
                "lines": lines,
                "toy_status": toy_status,
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
                    html = recovered_bundle.get("html") or html
                except Exception as refresh_err:
                    logger.warning("%s 异常后刷新状态失败：%s", self.plugin_name, self._get_error_detail(refresh_err))

            gain_exposure = 0
            gain_magic = 0
            if state:
                gain_exposure, gain_magic = self._summarize_gains(state.get("activity_logs") or [], start_time)

            partial_lines = self._build_summary_lines(collect_names, place_names, gain_exposure, gain_magic)
            if self._enabled and (partial_lines or reason in {"schedule", "bootstrap", "onlyonce"}):
                retry_at = int(time.time()) + fallback_delay
            if state:
                computed_next = self._compute_next_run(state, placed_times)
                if computed_next:
                    retry_at = min(retry_at, computed_next) if retry_at else computed_next
            if partial_lines and retry_at:
                partial_lines.append("⚠️ 本轮中途超时/网络波动，剩余动作稍后自动重试")

            toy_status = None
            if state and html:
                try:
                    toy_status = self._refresh_and_store_status(state, html, retry_at, partial_lines)
                except Exception as store_err:
                    logger.warning("%s 异常后保存状态失败：%s", self.plugin_name, self._get_error_detail(store_err))
            elif retry_at:
                try:
                    self._schedule_next_run(retry_at, reason="error-retry")
                except Exception as schedule_err:
                    logger.warning("%s 异常后补重试失败：%s", self.plugin_name, self._get_error_detail(schedule_err))

            if partial_lines:
                if not toy_status:
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
                    "toy_status": toy_status or (self.get_data("toy_status") or {}),
                    "status": self._build_status(auto_refresh=False),
                }

            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            logger.error("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
            if self._notify:
                text = detail
                if retry_at:
                    text += "\n⏰ 已安排稍后自动重试"
                self.post_message(
                    title="【🧸SQ玩偶】 异常",
                    mtype=NotificationType.Plugin,
                    text=text,
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

    def _refresh_data(self):
        try:
            toy_status = self._refresh_state(reason="manual-refresh")
            return {"success": True, "message": "SQ玩偶状态已刷新", "toy_status": toy_status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 刷新状态失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

    def _collect_slot_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_collect_slot(payload or {})
            return {"success": True, "message": result["message"], "toy_status": result["toy_status"], "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动收回失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        return {"success": False, "message": "占位"}

    def _place_personal_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_place_personal(payload or {})
            return {"success": True, "message": result["message"], "toy_status": result["toy_status"], "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 上架自展位失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _random_target_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_random_target()
            return {"success": True, "message": result["message"], "target_panel": result["target_panel"], "toy_status": result["toy_status"], "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 随机匹配失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _view_target_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_view_target(payload or {})
            return {"success": True, "message": result["message"], "target_panel": result["target_panel"], "toy_status": result["toy_status"], "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 查看目标失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _place_target_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_place_target(payload or {})
            return {"success": True, "message": result["message"], "target_panel": result["target_panel"], "toy_status": result["toy_status"], "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 抢占展位失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _buy_box_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_buy_box(payload or {})
            return {
                "success": True,
                "message": result["message"],
                "toy_status": result["toy_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 购买盲盒失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _open_box_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_open_box(payload or {})
            return {
                "success": True,
                "message": result["message"],
                "toy_status": result["toy_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 开启盲盒失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        toy_status = self.get_data("toy_status") or {}
        needs_refresh = not toy_status or toy_status.get("schema_version") != self.plugin_version
        if auto_refresh and needs_refresh:
            try:
                toy_status = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)

        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "auto_cookie": self._auto_cookie,
            "auto_collect": self._auto_collect,
            "auto_place": self._auto_place,
            "cookie_source": self._cookie_source,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(next_trigger) if next_trigger else "",
            "last_run": self.get_data("last_run") or "",
            "toy_status": toy_status,
            "history": (self.get_data("history") or [])[:20],
            "config": self._get_config(),
        }

    def _get_config(self, include_options: bool = True) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
            "auto_collect": self._auto_collect,
            "auto_place": self._auto_place,
            "capture_tips": [] if include_options else None,
        }

    def _save_config(self, config_payload: dict):
        merged = self._default_config()
        merged.update(self._get_config(include_options=False))
        merged.update(config_payload or {})
        self.init_plugin(merged)
        self._update_config()
        self._reregister_plugin("save-config")
        try:
            status = self._refresh_state(reason="save-config")
        except Exception as err:
            logger.warning("%s 保存配置后刷新失败：%s", self.plugin_name, err)
            status = self.get_data("toy_status") or {}
        return {"success": True, "message": "配置已保存", "config": self._get_config(), "toy_status": status, "status": self._build_status(auto_refresh=False)}

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
            "auto_cookie": True,
            "auto_collect": True,
            "auto_place": True,
            "use_proxy": False,
            "force_ipv4": True,
            "cookie": "",
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._auto_cookie = self._to_bool(config.get("auto_cookie", True))
        self._auto_collect = self._to_bool(config.get("auto_collect", True))
        self._auto_place = self._to_bool(config.get("auto_place", config.get("enable_target", True)))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cookie = (config.get("cookie") or "").strip()
        self._schedule_buffer_seconds = max(0, self._safe_int(config.get("schedule_buffer_seconds"), 5))
        self._random_delay_max_seconds = max(0, self._safe_int(config.get("random_delay_max_seconds"), 5))
        self._http_timeout = max(5, self._safe_int(config.get("http_timeout"), 12))
        self._http_retry_times = max(0, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(0, self._safe_int(config.get("http_retry_delay"), 1500))
        self._skip_before_seconds = max(0, self._safe_int(config.get("skip_before_seconds"), 60))
        self._collect_retry = max(1, self._safe_int(config.get("collect_retry"), 3))
        self._collect_retry_delay = max(0, self._safe_int(config.get("collect_retry_delay"), 1200))
        self._place_loop_limit = max(1, self._safe_int(config.get("place_loop_limit"), 10))
        self._place_retry_delay = max(0, self._safe_int(config.get("place_retry_delay"), 1500))
        self._max_target_try = max(1, self._safe_int(config.get("max_target_try"), 3))

    def _update_config(self):
        self.update_config({
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "auto_collect": self._auto_collect,
            "auto_place": self._auto_place,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
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
            self._cookie_source = f"站点同步：{self._site_domain}"
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
            "Referer": f"{self._site_url}/toy_show.php",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        })
        if self._use_proxy and getattr(settings, "PROXY", None):
            session.proxies = {"http": settings.PROXY, "https": settings.PROXY}
        return session

    def _fetch_bundle(self, session: requests.Session) -> Dict[str, Any]:
        response = self._request_with_retry(
            "fetchToyPage",
            lambda: session.get(
                f"{self._site_url}/toy_show.php",
                timeout=(self._http_timeout, self._http_timeout),
            ),
        )
        response.raise_for_status()
        html = response.text
        state = self._extract_initial_state(html)
        if not state:
            raise ValueError("页面返回成功，但未解析到 TOY_SHOW_INITIAL_STATE")
        parsed = self._parse_page_html(html)
        return {"state": state, "html": html, "parsed": parsed}

    def _refresh_state(
        self,
        reason: str = "",
        target_panel: Optional[Dict[str, Any]] = None,
        summary_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self._ensure_cookie()
        session = self._build_session()
        bundle = self._fetch_bundle(session)
        next_run = self._compute_next_run(bundle["state"])
        return self._refresh_and_store_status(
            bundle["state"],
            bundle["html"],
            next_run,
            summary_lines or [],
            target_panel=target_panel,
        )

    def _manual_collect_slot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        owner_id = self._safe_int(payload.get("owner_id"), 0)
        slot_index = self._safe_int(payload.get("slot_index"), -1)
        if owner_id <= 0 or slot_index < 0:
            raise ValueError("缺少有效的 owner_id 或 slot_index")
        session = self._build_session()
        result = self._post_action(session, "collect_slot", {"owner_id": owner_id, "slot_index": slot_index})
        if not result.get("success"):
            raise ValueError(result.get("message") or "收回失败")
        toy_status = self._refresh_state(reason="manual-collect", summary_lines=["✅ 收回：已手动收回展位玩偶"])
        return {"message": "收回成功", "toy_status": toy_status}

    def _manual_place_personal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        owner_id = self._safe_int(payload.get("owner_id"), 0)
        slot_index = self._safe_int(payload.get("slot_index"), -1)
        doll_key = str(payload.get("doll_key") or "").strip()
        doll_name = str(payload.get("doll_name") or "").strip()
        if owner_id <= 0 or slot_index < 0 or not doll_key:
            raise ValueError("缺少有效的展位或玩偶信息")
        session = self._build_session()
        placements = json.dumps([{"owner_id": owner_id, "slot_index": slot_index, "doll_key": doll_key}], ensure_ascii=False)
        result = self._post_action(session, "bulk_place_doll", {"placements": placements})
        if not result.get("success"):
            raise ValueError(result.get("message") or "上架失败")
        toy_status = self._refresh_state(reason="manual-place-personal", summary_lines=[f"🎯 展出：{doll_name or doll_key}"])
        return {"message": "上架成功", "toy_status": toy_status}

    def _manual_random_target(self) -> Dict[str, Any]:
        session = self._build_session()
        result = self._post_action(session, "random_target", {}, retry_network=True)
        target = result.get("target") or {}
        if not result.get("success") or not target:
            raise ValueError(result.get("message") or "没有找到可外展的目标")
        toy_status = self._refresh_state(reason="manual-random-target", target_panel=self._build_target_panel(target))
        return {"message": "已匹配目标展台", "target_panel": toy_status.get("target_panel") or {}, "toy_status": toy_status}

    def _manual_view_target(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw_target = str(payload.get("target_id") or payload.get("owner_id") or payload.get("keyword") or "").strip()
        if not raw_target:
            raise ValueError("请输入用户名或用户 ID，或使用随机匹配")
        session = self._build_session()
        if raw_target.isdigit():
            result = self._post_action(session, "view_target", {"target_id": int(raw_target)}, retry_network=True)
        else:
            result = self._post_action(session, "search_target", {"username": raw_target}, retry_network=True)
        target = result.get("target") or {}
        if not result.get("success") or not target:
            raise ValueError(result.get("message") or "进入目标展台失败")
        toy_status = self._refresh_state(reason="manual-view-target", target_panel=self._build_target_panel(target))
        return {"message": "已加载目标展台", "target_panel": toy_status.get("target_panel") or {}, "toy_status": toy_status}

    def _manual_place_target(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        owner_id = self._safe_int(payload.get("owner_id"), 0)
        slot_index = self._safe_int(payload.get("slot_index"), -1)
        doll_key = str(payload.get("doll_key") or "").strip()
        doll_name = str(payload.get("doll_name") or "").strip()
        if owner_id <= 0 or slot_index < 0 or not doll_key:
            raise ValueError("缺少有效的外展信息")
        session = self._build_session()
        result = self._post_action(session, "place_doll", {"owner_id": owner_id, "slot_index": slot_index, "doll_key": doll_key})
        if not result.get("success"):
            raise ValueError(result.get("message") or "抢占展位失败")
        refreshed = self._post_action(session, "view_target", {"target_id": owner_id}, retry_network=True)
        panel = self._build_target_panel(refreshed.get("target") or {})
        toy_status = self._refresh_state(reason="manual-place-target", target_panel=panel, summary_lines=[f"🎯 展出：{doll_name or doll_key}"])
        return {"message": "抢占成功", "target_panel": toy_status.get("target_panel") or panel, "toy_status": toy_status}

    def _manual_buy_box(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        box_key = str(payload.get("box_key") or "").strip()
        quantity = max(1, self._safe_int(payload.get("quantity"), 1))
        if not box_key:
            raise ValueError("缺少盲盒信息")
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        box_name = self._resolve_box_name(state, box_key)
        result = self._post_action(session, "purchase_box", {"box_key": box_key, "quantity": quantity})
        if not result.get("success"):
            raise ValueError(result.get("message") or "盲盒购买失败")
        summary_lines = [f"📦 购买盲盒：{box_name}×{quantity}"]
        toy_status = self._refresh_state(reason="manual-buy-box", summary_lines=summary_lines)
        return {"message": result.get("message") or "购买成功", "toy_status": toy_status}

    def _manual_open_box(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        box_key = str(payload.get("box_key") or "").strip()
        quantity = max(1, self._safe_int(payload.get("quantity"), 1))
        if not box_key:
            raise ValueError("缺少盲盒信息")
        session = self._build_session()
        state = self._fetch_bundle(session)["state"]
        box_name = self._resolve_box_name(state, box_key)
        result = self._post_action(session, "open_box", {"box_key": box_key, "quantity": quantity})
        if not result.get("success"):
            raise ValueError(result.get("message") or "开启盲盒失败")
        summary_lines = [f"🎁 开盒：{box_name}×{quantity}"]
        drop_text = self._count_items(result.get("drops") or [], name_keys=("name", "doll_name"), qty_keys=("quantity", "count", "added"))
        if drop_text:
            summary_lines.append(f"🪆 获得：{drop_text}")
        toy_status = self._refresh_state(reason="manual-open-box", summary_lines=summary_lines)
        message = result.get("message") or (summary_lines[-1] if len(summary_lines) > 1 else "开启成功")
        return {"message": message, "toy_status": toy_status}

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
                f"{self._site_url}/toy_show.php",
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

    def _collect_personal_slots(self, session: requests.Session, collect_names: List[str]):
        while True:
            latest = self._fetch_bundle(session)["state"]
            ready_slots = sorted(
                [
                    slot
                    for slot in self._iter_dicts(latest.get("personal_slots") or [])
                    if (slot.get("occupant") or {}).get("viewer_is_occupant")
                    and (self._get_personal_remain_sec(slot) is not None and self._get_personal_remain_sec(slot) <= 0)
                ],
                key=lambda item: self._get_personal_remain_sec(item) or 0,
            )
            if not ready_slots:
                break
            collected_count = 0
            for current in ready_slots:
                if self._collect_with_retry(
                    session,
                    current.get("owner_id"),
                    current.get("slot_index"),
                    (current.get("occupant") or {}).get("doll_name"),
                ):
                    collect_names.append((current.get("occupant") or {}).get("doll_name") or "未知玩偶")
                    collected_count += 1
            if collected_count <= 0:
                break

    def _collect_remote_slots(self, session: requests.Session, state: Dict[str, Any], collect_names: List[str]):
        while True:
            latest = self._fetch_bundle(session)["state"]
            remote_list = sorted(
                [
                    item
                    for item in self._iter_dicts(latest.get("remote_deployments") or [])
                    if self._get_remote_remain_sec(item) is not None and self._get_remote_remain_sec(item) <= 0
                ],
                key=lambda item: self._get_remote_remain_sec(item) or 0,
            )
            if not remote_list:
                break
            collected_count = 0
            for remote in remote_list:
                try:
                    target = self._post_action(session, "view_target", {"target_id": remote.get("owner_id")}, retry_network=True).get("target") or {}
                except Exception:
                    continue
                candidate = self._pick_remote_candidate(target.get("slots") or [], remote)
                if not candidate:
                    continue
                occupant = candidate.get("occupant") or {}
                remaining = self._safe_int(occupant.get("time_until_collect"), 1)
                if remaining > 0 and self._safe_int(occupant.get("elapsed_seconds"), 0) < self._safe_int(occupant.get("display_seconds"), 0):
                    continue
                if self._collect_with_retry(session, candidate.get("owner_id"), candidate.get("slot_index"), occupant.get("doll_name")):
                    collect_names.append(occupant.get("doll_name") or "未知玩偶")
                    collected_count += 1
            if collected_count <= 0:
                break

    def _place_personal_slots(self, session: requests.Session, state: Dict[str, Any], place_names: List[str]) -> List[Dict[str, Any]]:
        placed_times: List[Dict[str, Any]] = []
        while True:
            current = self._fetch_bundle(session)["state"]
            idle_slots = [slot for slot in self._iter_dicts(current.get("personal_slots") or []) if not slot.get("occupant")]
            dolls = [dict(item) for item in self._iter_dicts(current.get("doll_inventory") or []) if self._safe_int(item.get("available"), 0) > 0]
            if not idle_slots or not dolls:
                break
            placements = []
            doll_index = 0
            for slot in idle_slots:
                if doll_index >= len(dolls):
                    break
                doll = dolls[doll_index]
                placements.append({
                    "owner_id": slot.get("owner_id"),
                    "slot_index": slot.get("slot_index"),
                    "doll_key": doll.get("doll_key"),
                    "doll_name": doll.get("name"),
                    "display_seconds": self._safe_int(doll.get("display_seconds"), 0),
                })
                doll["available"] = self._safe_int(doll.get("available"), 0) - 1
                if self._safe_int(doll.get("available"), 0) <= 0:
                    doll_index += 1
            if not placements:
                break
            result = self._post_action(
                session,
                "bulk_place_doll",
                {"placements": json.dumps([{"owner_id": p["owner_id"], "slot_index": p["slot_index"], "doll_key": p["doll_key"]} for p in placements], ensure_ascii=False)},
            )
            if not result.get("success"):
                break
            now_ts = int(time.time())
            for item in placements:
                place_names.append(item["doll_name"] or "未知玩偶")
                placed_times.append({"time": now_ts + max(0, item["display_seconds"]), "label": f"本轮放置 自展位 {item['doll_name'] or item['doll_key']}"})
            time.sleep(max(self._place_retry_delay / 1000.0, 0))
        return placed_times

    def _place_target_slots(self, session: requests.Session, state: Dict[str, Any], place_names: List[str]) -> List[Dict[str, Any]]:
        placed_times: List[Dict[str, Any]] = []
        remaining = [dict(item) for item in self._iter_dicts(state.get("doll_inventory") or []) if self._safe_int(item.get("available"), 0) > 0]
        if not remaining:
            return placed_times
        attempt_limit = max(24, len(remaining) * 6, self._max_target_try)
        total_attempts = 0
        no_progress_rounds = 0
        while remaining and total_attempts < attempt_limit and no_progress_rounds < 6:
            total_attempts += 1
            result = self._post_action(session, "random_target", {}, retry_network=True)
            target = result.get("target") or {}
            slots = [
                slot
                for slot in self._iter_dicts(target.get("slots") or [])
                if not slot.get("occupant") and not slot.get("cooldown_active")
            ]
            if not target or not slots:
                no_progress_rounds += 1
                continue
            placements = []
            doll_index = 0
            for slot in slots:
                if doll_index >= len(remaining):
                    break
                doll = remaining[doll_index]
                placements.append({
                    "owner_id": slot.get("owner_id"),
                    "slot_index": slot.get("slot_index"),
                    "doll_key": doll.get("doll_key"),
                    "doll_name": doll.get("name"),
                    "display_seconds": self._safe_int(doll.get("display_seconds"), 0),
                })
                doll["available"] = self._safe_int(doll.get("available"), 0) - 1
                if self._safe_int(doll.get("available"), 0) <= 0:
                    doll_index += 1
            success_count = 0
            now_ts = int(time.time())
            for item in placements:
                placed = self._post_action(session, "place_doll", {"owner_id": item["owner_id"], "slot_index": item["slot_index"], "doll_key": item["doll_key"]})
                if placed.get("success"):
                    success_count += 1
                    place_names.append(item["doll_name"] or "未知玩偶")
                    placed_times.append({"time": now_ts + max(0, item["display_seconds"]), "label": f"本轮放置 外展 {item['doll_name'] or item['doll_key']}"})
            remaining = [item for item in remaining if self._safe_int(item.get("available"), 0) > 0]
            if success_count > 0:
                no_progress_rounds = 0
            else:
                no_progress_rounds += 1
            if success_count and remaining:
                time.sleep(max(self._place_retry_delay / 1000.0, 0))
        return placed_times

    def _pick_remote_candidate(self, slots: List[dict], remote: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        owned = [slot for slot in self._iter_dicts(slots or []) if (slot.get("occupant") or {}).get("viewer_is_occupant")]
        for candidate in owned:
            if candidate.get("slot_index") == remote.get("slot_index"):
                return candidate
        for candidate in owned:
            if (candidate.get("occupant") or {}).get("doll_name") == remote.get("doll_name"):
                return candidate
        return owned[0] if owned else None

    def _collect_with_retry(
        self,
        session: requests.Session,
        owner_id: Any,
        slot_index: Any,
        doll_name: Optional[str],
    ) -> bool:
        owner_id = self._safe_int(owner_id, 0)
        slot_index = self._safe_int(slot_index, -1)
        if owner_id <= 0 or slot_index < 0:
            return False

        for attempt in range(1, self._collect_retry + 1):
            try:
                result = self._post_action(session, "collect_slot", {"owner_id": owner_id, "slot_index": slot_index})
                if result.get("success"):
                    return True
                if self._confirm_collect_success(session, owner_id, slot_index, doll_name):
                    return True
                detail = self._strip_html(result.get("message") or result.get("msg") or "")
                if detail:
                    logger.warning(
                        "%s 回收返回失败（%s/%s）：%s | %s",
                        self.plugin_name,
                        attempt,
                        self._collect_retry,
                        doll_name or "未知玩偶",
                        detail,
                    )
            except Exception as err:
                logger.warning(
                    "%s 回收失败（%s/%s）：%s | %s",
                    self.plugin_name,
                    attempt,
                    self._collect_retry,
                    doll_name or "未知玩偶",
                    self._get_error_detail(err),
                )
                if self._confirm_collect_success(session, owner_id, slot_index, doll_name):
                    return True
            if attempt < self._collect_retry:
                time.sleep(max(self._collect_retry_delay / 1000.0, 0))
        return False

    def _confirm_collect_success(
        self,
        session: requests.Session,
        owner_id: int,
        slot_index: int,
        doll_name: Optional[str],
    ) -> bool:
        try:
            latest = self._fetch_bundle(session)["state"] or {}
        except Exception as err:
            logger.warning(
                "%s 回收状态确认失败：%s | %s",
                self.plugin_name,
                doll_name or "未知玩偶",
                self._get_error_detail(err),
            )
            return False

        personal_slot = next(
            (
                candidate
                for candidate in self._iter_dicts(latest.get("personal_slots") or [])
                if self._safe_int(candidate.get("owner_id"), 0) == owner_id
                and self._safe_int(candidate.get("slot_index"), -1) == slot_index
            ),
            None,
        )
        if personal_slot is not None:
            occupant = personal_slot.get("occupant") or {}
            if not occupant or not occupant.get("viewer_is_occupant"):
                logger.info(
                    "%s 回收状态已确认：%s（按最新状态判定已成功）",
                    self.plugin_name,
                    doll_name or "未知玩偶",
                )
                return True
            return False

        expected_name = str(doll_name or "").strip()
        for item in self._iter_dicts(latest.get("remote_deployments") or []):
            if self._safe_int(item.get("owner_id"), 0) != owner_id:
                continue
            if self._safe_int(item.get("slot_index"), -1) != slot_index:
                continue
            current_name = str(item.get("doll_name") or "").strip()
            if not expected_name or not current_name or current_name == expected_name:
                return False

        logger.info(
            "%s 回收状态已确认：%s（按最新状态判定已成功）",
            self.plugin_name,
            doll_name or "未知玩偶",
        )
        return True

    def _summarize_gains(self, logs: List[dict], since_time: float) -> Tuple[int, int]:
        gain_exposure = 0
        gain_magic = 0
        for item in self._iter_dicts(logs or []):
            created_at = item.get("created_at")
            if not created_at:
                continue
            try:
                log_ts = datetime.strptime(str(created_at).replace("/", "-"), "%Y-%m-%d %H:%M:%S").timestamp()
            except Exception:
                continue
            if log_ts < since_time:
                continue
            message = str(item.get("message") or "")
            if "收获成功" not in message:
                continue
            matched = re.search(r"曝光\+(\d+)\s*魔力\+(\d+)", message)
            if matched:
                gain_exposure += self._safe_int(matched.group(1), 0)
                gain_magic += self._safe_int(matched.group(2), 0)
        return gain_exposure, gain_magic

    def _build_summary_lines(
        self,
        collect_names: List[str],
        place_names: List[str],
        gain_exposure: int,
        gain_magic: int,
    ) -> List[str]:
        lines: List[str] = []
        if collect_names:
            lines.append(f"✅ 收回：{self._count_names(collect_names)}")
        if place_names:
            lines.append(f"🎯 展出：{self._count_names(place_names)}")
        if gain_exposure > 0 or gain_magic > 0:
            lines.append(f"💰 收益：曝光+{gain_exposure} 魔力+{gain_magic}")
        return lines

    def _send_report(self, lines: List[str], next_run: Optional[int]):
        chunks = [self.SUMMARY_LINE, *lines, self.SUMMARY_LINE, f"⏰ 下次运行：{self._format_ts(next_run) or '等待刷新'}", self.SUMMARY_LINE]
        self.post_message(
            title="【🧸SQ玩偶】 任务报告",
            mtype=NotificationType.Plugin,
            text="\n".join(chunks),
        )

    def _refresh_and_store_status(
        self,
        state: Dict[str, Any],
        html: str,
        next_run: Optional[int],
        summary_lines: List[str],
        target_panel: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._schedule_next_run(next_run, reason="refresh-state")
        toy_status = self._build_ui_state(state, html, next_run, summary_lines, target_panel or {})
        stored_status = dict(toy_status)
        stored_status["target_panel"] = {}
        self.save_data("toy_status", stored_status)
        self.save_data("state", self._build_state_record(state, next_run, summary_lines))
        self.save_data("last_run", self._format_time(self._aware_now()))
        self._append_history(summary_lines, next_run)
        return toy_status

    def _build_state_record(self, state: Dict[str, Any], next_run: Optional[int], summary_lines: List[str]) -> Dict[str, Any]:
        return {
            "schema_version": self.plugin_version,
            "time": self._format_time(self._aware_now()),
            "next_run_time": self._format_ts(next_run),
            "next_trigger_time": self._format_time(self._load_saved_next_trigger()),
            "summary": summary_lines,
            "user": state.get("user") or {},
            "profile": state.get("profile") or {},
            "personal_slots": state.get("personal_slots") or [],
            "remote_deployments": state.get("remote_deployments") or [],
            "doll_inventory": state.get("doll_inventory") or [],
            "activity_logs": state.get("activity_logs") or [],
        }

    def _compute_next_run(self, state: Dict[str, Any], placed_times: Optional[List[Dict[str, Any]]] = None) -> Optional[int]:
        now_ts = int(time.time())
        candidates: List[int] = []
        if self._auto_place and self._needs_placement_retry(state):
            candidates.append(now_ts + self._placement_retry_seconds())
        if self._auto_collect:
            for slot in self._iter_dicts(state.get("personal_slots") or []):
                if not (slot.get("occupant") or {}).get("viewer_is_occupant"):
                    continue
                sec = self._get_personal_remain_sec(slot)
                if sec is None:
                    continue
                candidates.append(now_ts + 5 if sec <= 0 else now_ts + sec)
            for remote in self._iter_dicts(state.get("remote_deployments") or []):
                sec = self._get_remote_remain_sec(remote)
                if sec is None:
                    continue
                candidates.append(now_ts + 5 if sec <= 0 else now_ts + sec)
            for item in placed_times or []:
                candidates.append(self._safe_int(item.get("time"), 0))
        if self._auto_place:
            for doll in self._iter_dicts(state.get("doll_inventory") or []):
                if self._safe_int(doll.get("cooling_count"), 0) <= 0:
                    continue
                cooldown_until = self._safe_int(doll.get("cooldown_until"), 0)
                cooldown_remaining = self._safe_int(doll.get("cooldown_remaining"), 0)
                if cooldown_until > 0:
                    candidates.append(cooldown_until)
                elif cooldown_remaining > 0:
                    candidates.append(now_ts + cooldown_remaining)
        candidates = [candidate for candidate in candidates if candidate > 0]
        return min(candidates) if candidates else now_ts + 6 * 3600

    def _placement_retry_seconds(self) -> int:
        return max(45, min(300, self._http_timeout * 3))

    def _needs_placement_retry(self, state: Dict[str, Any]) -> bool:
        if not self._auto_place:
            return False
        available_dolls = any(self._safe_int(item.get("available"), 0) > 0 for item in self._iter_dicts(state.get("doll_inventory") or []))
        if not available_dolls:
            return False
        has_idle_personal_slot = any(not slot.get("occupant") for slot in self._iter_dicts(state.get("personal_slots") or []))
        if has_idle_personal_slot:
            return True
        return True

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
                min_trigger = now + timedelta(seconds=5)
                if next_trigger < min_trigger:
                    next_trigger = min_trigger
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
        if self._enabled:
            self._bootstrap_pending = not bool(next_run_ts)
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
        now = self._aware_now()
        if self._bootstrap_pending:
            return now + timedelta(seconds=3)
        next_trigger = self._next_trigger_time or self._load_saved_next_trigger()
        if not next_trigger:
            return None
        return next_trigger if next_trigger > now else now + timedelta(seconds=5)

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

    def _build_ui_state(
        self,
        state: Dict[str, Any],
        html: str,
        next_run: Optional[int],
        summary_lines: List[str],
        target_panel: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        parsed = self._parse_page_html(html)
        shop_boxes = self._build_shop_boxes(state, parsed.get("shop_boxes") or [])
        doll_map = self._build_doll_map(state, parsed.get("doll_map") or {})
        return {
            "schema_version": self.plugin_version,
            "title": "玩偶抢曝光",
            "subtitle": "盲盒、回收、展出、获取执行记录。",
            "cookie_source": self._cookie_source,
            "summary": summary_lines,
            "next_run_time": self._format_ts(next_run),
            "next_run_ts": next_run or 0,
            "next_trigger_time": self._format_time(self._load_saved_next_trigger()),
            "next_trigger_ts": int(self._load_saved_next_trigger().timestamp()) if self._load_saved_next_trigger() else 0,
            "overview": self._merge_overview(self._build_overview(state), parsed),
            "shop_boxes": shop_boxes,
            "my_boxes": self._build_box_inventory(state, shop_boxes, parsed.get("my_boxes") or []),
            "cabinet": self._build_cabinet_cards(state, doll_map),
            "personal_slots": self._build_personal_slots(state, doll_map),
            "target_panel": target_panel or {},
            "remote_records": self._build_remote_records(state, doll_map),
            "history": (self.get_data("history") or [])[:20],
            "history_logs": self._build_activity_logs(state),
        }

    def _build_shop_boxes(self, state: Dict[str, Any], parsed_boxes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        catalog = state.get("catalog") or []
        if isinstance(catalog, list) and catalog:
            exposure = self._safe_int((state.get("profile") or {}).get("exposure"), 0)
            boxes: List[Dict[str, Any]] = []
            for item in self._iter_dicts(catalog):
                box_key = str(item.get("key") or item.get("box_key") or "").strip()
                unlock_exposure = self._safe_int(item.get("unlock_exposure"), 0)
                locked = exposure < unlock_exposure
                desc = f"售价 {self._safe_int(item.get('price'), 0)} 魔力"
                if unlock_exposure > 0:
                    desc += f" · 解锁需曝光值 {unlock_exposure}"
                boxes.append({
                    "box_key": box_key,
                    "name": str(item.get("name") or box_key),
                    "image": self._absolute_url(item.get("icon") or item.get("image") or ""),
                    "desc": desc,
                    "lock_text": f"购买需要曝光值达 {unlock_exposure}" if locked and unlock_exposure > 0 else "",
                    "locked": locked,
                    "buy_enabled": not locked,
                    "default_quantity": 1,
                })
            return boxes
        return parsed_boxes

    def _build_doll_map(self, state: Dict[str, Any], parsed_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        result = dict(parsed_map or {})
        for box in self._iter_dicts(state.get("catalog") or []):
            box_name = str(box.get("name") or "")
            dolls = box.get("dolls") or {}
            if not isinstance(dolls, dict):
                continue
            for doll in self._iter_dicts(dolls.values()):
                name = str(doll.get("name") or "").strip()
                if not name:
                    continue
                result[name] = {
                    **result.get(name, {}),
                    "image": self._absolute_url(doll.get("icon") or result.get(name, {}).get("image") or ""),
                    "quality": str(doll.get("quality") or result.get(name, {}).get("quality") or ""),
                    "display_text": result.get(name, {}).get("display_text") or f"展出{max(0, round(self._safe_int(doll.get('display_seconds'), 0) / 3600))}小时",
                    "reward_text": result.get(name, {}).get("reward_text") or f"曝光+{self._safe_int(doll.get('exposure_reward'), 0)} 魔力+{self._safe_int(doll.get('magic_reward'), 0)}",
                    "origin": box_name or result.get(name, {}).get("origin") or "",
                }
        return result

    def _build_overview(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        user = state.get("user") or {}
        profile = state.get("profile") or {}
        constants = state.get("constants") or {}
        booth_count = self._safe_int(profile.get("booth_count"), 0)
        booth_cap = self._safe_int(profile.get("booth_cap"), booth_count)
        max_booths = self._safe_int(constants.get("max_booths"), booth_cap or booth_count)
        reward_multiplier = float(profile.get("booth_reward_multiplier") or 1)
        total_bonus = max(0, round((reward_multiplier - 1) * 100))
        return [
            {"label": "当前魔力", "value": self._safe_int(user.get("magic"), 0)},
            {"label": "累计曝光值", "value": self._safe_int(profile.get("exposure"), 0)},
            {"label": "累计收获魔力值", "value": self._safe_int(profile.get("earned_magic"), 0)},
            {
                "label": "我的展柜",
                "value": booth_count,
                "desc": f"上限 {booth_cap}/{max_booths}（不超过100%）",
                "extra": f"玩偶奖励（曝光+魔力）加成： +{total_bonus}%",
            },
        ]

    def _build_box_inventory(
        self,
        state: Dict[str, Any],
        shop_boxes: List[Dict[str, Any]],
        parsed_boxes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        known_map = {str(item.get("box_key") or ""): item for item in shop_boxes}
        for key in ("box_inventory", "my_boxes", "blind_box_inventory", "owned_boxes"):
            inventory = state.get(key)
            if not isinstance(inventory, list) or not inventory:
                continue
            result: List[Dict[str, Any]] = []
            for item in self._iter_dicts(inventory):
                box_key = str(item.get("box_key") or item.get("key") or "")
                meta = known_map.get(box_key, {})
                result.append({
                    "box_key": box_key,
                    "name": item.get("name") or meta.get("name") or box_key,
                    "image": self._absolute_url(item.get("icon") or item.get("image") or meta.get("image") or ""),
                    "count": self._safe_int(item.get("quantity") or item.get("count"), 0),
                    "default_quantity": 1,
                    "open_enabled": self._safe_int(item.get("quantity") or item.get("count"), 0) > 0,
                    "open_tip": "",
                })
            return result
        if parsed_boxes:
            return parsed_boxes
        return []

    def _build_cabinet_cards(self, state: Dict[str, Any], doll_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        for item in self._iter_dicts(state.get("doll_inventory") or []):
            name = str(item.get("name") or "").strip()
            meta = doll_map.get(name, {})
            available = self._safe_int(item.get("available"), 0)
            total = self._safe_int(item.get("quantity"), 0)
            cooling = self._safe_int(item.get("cooling_count"), 0)
            cooldown_until_ts = self._get_future_ts(
                self._safe_int(item.get("cooldown_until"), 0),
                self._safe_int(item.get("cooldown_remaining"), 0),
            )
            cards.append({
                "doll_key": item.get("doll_key") or "",
                "name": name,
                "image": self._absolute_url(item.get("icon") or meta.get("image") or ""),
                "origin": item.get("origin_label") or item.get("box_name") or meta.get("origin") or "",
                "quality": item.get("quality") or meta.get("quality") or "",
                "quality_rank": self.QUALITY_ORDER.get(str(item.get("quality") or meta.get("quality") or ""), 0),
                "display_text": f"展出{max(0, round(self._safe_int(item.get('display_seconds'), 0) / 3600))}小时 · 守候{max(0, round(self._safe_int(item.get('wait_seconds'), 0) / 60))}分钟",
                "reward_text": f"曝光+{self._safe_int(item.get('final_exposure_reward'), 0)} 魔力+{self._safe_int(item.get('final_magic_reward'), 0)}",
                "available": available,
                "total": total,
                "display_count": max(total - available - cooling, 0),
                "cooling_count": cooling,
                "cooldown_text": self._describe_cooldown(item),
                "cooldown_until_ts": cooldown_until_ts,
                "can_place": available > 0,
            })
        return cards

    def _build_personal_slots(self, state: Dict[str, Any], doll_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        viewer_name = self._strip_html((state.get("user") or {}).get("username") or "")
        for slot in self._iter_dicts(state.get("personal_slots") or []):
            cards.append(
                self._build_slot_card(
                    slot=slot,
                    doll_map=doll_map,
                    remaining=self._get_personal_remain_sec(slot),
                    fallback_owner_name=viewer_name,
                    blocked_label="被抢占",
                )
            )
        return cards

    def _build_target_panel(self, target: Dict[str, Any]) -> Dict[str, Any]:
        if not target:
            return {}
        slots = []
        target_name = self._strip_html(target.get("username") or target.get("name") or "")
        for slot in self._iter_dicts(target.get("slots") or []):
            occupant = slot.get("occupant") or {}
            remaining = self._safe_int(occupant.get("time_until_collect"), 0) if occupant else None
            slots.append(
                self._build_slot_card(
                    slot=slot,
                    doll_map={},
                    remaining=remaining,
                    fallback_owner_name=target_name,
                    blocked_label="已被占用",
                    allow_empty=True,
                )
            )
        return {
            "owner_id": self._safe_int(target.get("user_id") or target.get("owner_id"), 0),
            "username": target_name,
            "slots": slots,
            "slot_count": len(slots),
        }

    def _build_slot_card(
        self,
        slot: Dict[str, Any],
        doll_map: Dict[str, Dict[str, Any]],
        remaining: Optional[int],
        fallback_owner_name: str = "",
        blocked_label: str = "已被占用",
        allow_empty: bool = False,
    ) -> Dict[str, Any]:
        occupant = slot.get("occupant") or {}
        name = occupant.get("doll_name") or ""
        meta = doll_map.get(name, {})
        viewer_is_occupant = bool(occupant.get("viewer_is_occupant"))
        empty = not bool(occupant)
        can_collect = bool(viewer_is_occupant) and remaining is not None and remaining <= 0
        action = self._build_slot_action_state(
            empty=empty,
            cooldown_active=bool(slot.get("cooldown_active")),
            viewer_is_occupant=viewer_is_occupant,
            can_collect=can_collect,
            blocked_label=blocked_label,
        )
        owner_name = self._resolve_slot_owner_name(
            slot,
            occupant,
            fallback_owner_name if viewer_is_occupant else "",
        )
        if occupant and not owner_name and not viewer_is_occupant:
            owner_name = "其他用户"
        state_text = self._strip_html(
            occupant.get("status")
            or occupant.get("state_text")
            or slot.get("status")
            or slot.get("state")
            or ("空位" if empty else "正在展出中")
        )
        return {
            "slot_index": self._safe_int(slot.get("slot_index"), 0),
            "owner_id": self._safe_int(slot.get("owner_id"), 0),
            "empty": empty,
            "cooldown_active": bool(slot.get("cooldown_active")),
            "status": str(occupant.get("status") or slot.get("state") or ""),
            "status_text": state_text,
            "doll_name": name,
            "image": self._absolute_url(occupant.get("doll_icon") or meta.get("image") or ""),
            "quality": occupant.get("quality") or meta.get("quality") or "",
            "owner_name": owner_name,
            "remaining_text": self._format_duration(remaining) if remaining is not None and remaining > 0 else ("已可回收" if viewer_is_occupant and not empty else ""),
            "remaining_seconds": remaining if remaining is not None else None,
            "remaining_end_ts": self._get_future_ts(0, remaining),
            "progress": self._calc_slot_progress(slot),
            "reward_text": f"曝光+{self._safe_int(occupant.get('exposure_reward') or occupant.get('final_exposure_reward'), 0)} 魔力+{self._safe_int(occupant.get('magic_reward') or occupant.get('final_magic_reward'), 0)}" if occupant else "",
            "viewer_is_occupant": viewer_is_occupant,
            "can_collect": can_collect,
            "is_other_occupant": bool(occupant) and not viewer_is_occupant,
            "activity_text": self._build_slot_activity_text(empty, viewer_is_occupant, can_collect, bool(slot.get("cooldown_active"))),
            "action_label": action["label"],
            "action_kind": action["kind"],
            "action_disabled": action["disabled"],
            "allow_empty": allow_empty,
        }

    def _build_slot_action_state(
        self,
        empty: bool,
        cooldown_active: bool,
        viewer_is_occupant: bool,
        can_collect: bool,
        blocked_label: str,
    ) -> Dict[str, Any]:
        if empty:
            if cooldown_active:
                return {"label": "冷却中", "kind": "cooldown", "disabled": True}
            return {"label": "", "kind": "empty", "disabled": False}
        if not viewer_is_occupant:
            return {"label": blocked_label, "kind": "blocked", "disabled": True}
        if can_collect:
            return {"label": "收回玩偶", "kind": "ready", "disabled": False}
        return {"label": "提前收回", "kind": "early", "disabled": False}

    def _build_slot_activity_text(self, empty: bool, viewer_is_occupant: bool, can_collect: bool, cooldown_active: bool) -> str:
        if empty:
            return "展位冷却中" if cooldown_active else "空位可上架"
        if viewer_is_occupant and can_collect:
            return "展出完成，可以收回玩偶"
        return "正在展出中，获取曝光中..."

    def _resolve_slot_owner_name(self, slot: Dict[str, Any], occupant: Dict[str, Any], fallback: str = "") -> str:
        candidates = [
            occupant.get("owner_name"),
            occupant.get("owner_username"),
            occupant.get("username"),
            occupant.get("user_name"),
            occupant.get("display_name"),
            slot.get("occupant_owner_name"),
            slot.get("owner_name"),
            slot.get("username"),
            slot.get("name"),
            fallback,
        ]
        for value in candidates:
            text = self._strip_html(value or "")
            if text:
                return text
        return ""

    def _build_remote_records(self, state: Dict[str, Any], doll_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for item in self._iter_dicts(state.get("remote_deployments") or []):
            name = item.get("doll_name") or ""
            meta = doll_map.get(name, {})
            remaining = self._get_remote_remain_sec(item)
            records.append({
                "owner_id": self._safe_int(item.get("owner_id"), 0),
                "owner_name": self._strip_html(item.get("owner_name") or ""),
                "slot_index": self._safe_int(item.get("slot_index"), 0),
                "doll_name": name,
                "image": self._absolute_url(item.get("doll_icon") or meta.get("image") or ""),
                "status": item.get("status") or "",
                "remaining_text": self._format_duration(remaining) if remaining is not None and remaining > 0 else "已可回收",
                "remaining_seconds": remaining if remaining is not None else None,
                "remaining_end_ts": self._get_future_ts(0, remaining),
                "remaining": remaining if remaining is not None else 10**9,
            })
        return sorted(records, key=lambda item: item["remaining"])

    def _build_activity_logs(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for item in self._iter_dicts((state.get("activity_logs") or [])[:20]):
            result.append({
                "message": self._strip_html(item.get("message") or ""),
                "time": item.get("created_at") or "",
            })
        return result

    def _parse_page_html(self, html: str) -> Dict[str, Any]:
        shop_inner = self._extract_div_inner_by_id(html, "toyShopList")
        inventory_inner = self._extract_div_inner_by_id(html, "toyBoxInventory")
        shop_boxes, doll_map = self._parse_shop_boxes(shop_inner)
        return {
            "overview": self._parse_overview_meta(html),
            "shop_boxes": shop_boxes,
            "doll_map": doll_map,
            "my_boxes": self._parse_box_inventory(inventory_inner, shop_boxes),
        }

    def _parse_overview_meta(self, html: str) -> Dict[str, str]:
        return {
            "booth_value": self._extract_text_by_id(html, "toyBoothValue"),
            "booth_cap_desc": self._extract_text_by_id(html, "toyBoothCapDesc"),
            "booth_bonus_desc": self._extract_text_by_id(html, "toyBoothBonusDesc"),
        }

    def _merge_overview(self, overview: List[Dict[str, Any]], parsed: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        result = [dict(item) for item in (overview or [])]
        parsed_overview = parsed.get("overview") if isinstance(parsed, dict) else {}
        if len(result) < 4 or not isinstance(parsed_overview, dict):
            return result
        booth_card = dict(result[3])
        booth_value = self._safe_int(parsed_overview.get("booth_value"), self._safe_int(booth_card.get("value"), 0))
        booth_cap_desc = str(parsed_overview.get("booth_cap_desc") or "").strip()
        booth_bonus_desc = str(parsed_overview.get("booth_bonus_desc") or "").strip()
        if booth_cap_desc:
            booth_card["desc"] = booth_cap_desc
            booth_card["value"] = booth_value
        if booth_bonus_desc:
            booth_card["extra"] = booth_bonus_desc
        result[3] = booth_card
        return result

    def _parse_shop_boxes(self, html: str) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        boxes: List[Dict[str, Any]] = []
        doll_map: Dict[str, Dict[str, Any]] = {}
        for block in self._extract_top_level_div_blocks(html, "toy-box-card"):
            name = self._match_one(block, r"<h3>(.*?)</h3>")
            image = self._match_one(block, r'<div class="toy-box-hero".*?<img[^>]*src="([^"]+)"', flags=re.S)
            desc = self._strip_html(self._match_one(block, r"<div class=\"toy-box-basic\">(.*?)</div>", flags=re.S))
            lock_text = self._strip_html(self._match_one(block, r'<span class="toy-box-lock">(.*?)</span>', flags=re.S))
            box_key = self._match_one(block, r'data-box="([^"]+)"')
            button_disabled = "disabled" in (self._match_one(block, r"<button[^>]*data-box=[^>]*>", flags=re.S) or "")
            quantity = self._safe_int(self._match_one(block, r'<input[^>]*value="(\d+)"'), 1)
            boxes.append({
                "box_key": box_key,
                "name": name,
                "image": self._absolute_url(image),
                "desc": desc,
                "lock_text": lock_text,
                "locked": "locked" in block or button_disabled,
                "buy_enabled": not button_disabled,
                "default_quantity": max(quantity, 1),
            })
            for doll_block in self._extract_top_level_div_blocks(block, "toy-doll-preview"):
                doll_name = self._match_one(doll_block, r"<strong>(.*?)</strong>")
                if not doll_name:
                    continue
                spans = re.findall(r"<span>(.*?)</span>", doll_block, flags=re.S)
                doll_map[doll_name] = {
                    "image": self._absolute_url(self._match_one(doll_block, r'<img[^>]*src="([^"]+)"')),
                    "quality": self._strip_html(spans[0]) if len(spans) > 0 else "",
                    "display_text": self._strip_html(spans[1]) if len(spans) > 1 else "",
                    "reward_text": self._strip_html(spans[2]) if len(spans) > 2 else "",
                    "origin": name,
                }
        return boxes, doll_map

    def _parse_box_inventory(self, html: str, shop_boxes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not html or "toy-empty" in html:
            return []
        known_map = {str(item.get("box_key") or ""): item for item in shop_boxes}
        result: List[Dict[str, Any]] = []
        for class_name in ("toy-box-stock-card", "toy-box-item", "toy-box-owned-card", "toy-box-card"):
            for block in self._extract_top_level_div_blocks(html, class_name):
                name = self._match_one(block, r"<h3>(.*?)</h3>") or self._match_one(block, r"<strong>(.*?)</strong>")
                if not name:
                    continue
                image = self._match_one(block, r'<img[^>]*src="([^"]+)"')
                count = self._safe_int(self._match_one(block, r"(?:数量|拥有|x)\s*[:：]?\s*(\d+)"), 0)
                box_key = self._match_one(block, r'data-box="([^"]+)"')
                known = known_map.get(box_key, {})
                result.append({
                    "box_key": box_key,
                    "name": name,
                    "image": self._absolute_url(image or known.get("image") or ""),
                    "count": count,
                    "default_quantity": 1,
                    "open_enabled": False,
                    "open_tip": "开启盲盒动作还缺少抓包",
                })
            if result:
                break
        return result

    def _extract_initial_state(self, html: str) -> Dict[str, Any]:
        matched = re.search(r"const TOY_SHOW_INITIAL_STATE = (\{[\s\S]*?\});", html)
        if not matched:
            return {}
        try:
            return json.loads(matched.group(1))
        except Exception:
            return {}

    def _extract_div_inner_by_id(self, html: str, element_id: str) -> str:
        matched = re.search(rf'<div\b[^>]*id="{re.escape(element_id)}"[^>]*>', html, flags=re.I)
        return self._extract_div_inner_from_match(html, matched)

    def _extract_text_by_id(self, html: str, element_id: str) -> str:
        matched = re.search(
            rf'<(?P<tag>[a-z0-9]+)\b[^>]*id="{re.escape(element_id)}"[^>]*>(?P<inner>.*?)</(?P=tag)>',
            html,
            flags=re.I | re.S,
        )
        return self._strip_html(matched.group("inner")) if matched else ""

    def _extract_div_inner_from_match(self, html: str, matched: Optional[re.Match]) -> str:
        if not matched:
            return ""
        start = matched.end()
        depth = 1
        cursor = start
        token_re = re.compile(r"<div\b|</div>", flags=re.I)
        while depth > 0:
            token = token_re.search(html, cursor)
            if not token:
                return ""
            if token.group(0).lower().startswith("</div"):
                depth -= 1
            else:
                depth += 1
            cursor = token.end()
        return html[start:token.start()]

    def _extract_top_level_div_blocks(self, html: str, class_name: str) -> List[str]:
        blocks: List[str] = []
        pattern = re.compile(rf'<div\b[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>', flags=re.I)
        cursor = 0
        while True:
            matched = pattern.search(html, cursor)
            if not matched:
                break
            inner = self._extract_div_inner_from_match(html, matched)
            if inner:
                blocks.append(html[matched.start(): matched.end()] + inner + "</div>")
                cursor = matched.end() + len(inner) + 6
            else:
                cursor = matched.end()
        return blocks

    def _get_personal_remain_sec(self, slot: Dict[str, Any]) -> Optional[int]:
        occupant = slot.get("occupant") or {}
        if not occupant.get("viewer_is_occupant"):
            return None
        collect = occupant.get("time_until_collect")
        if collect is not None:
            return self._safe_int(collect, 0)
        elapsed = occupant.get("elapsed_seconds")
        display = occupant.get("display_seconds")
        if elapsed is not None and display is not None:
            return self._safe_int(display, 0) - self._safe_int(elapsed, 0)
        status = str(occupant.get("status") or slot.get("state") or "").lower()
        if status in {"collectable", "collect_ready", "finished", "expired", "overtime"}:
            return 0
        return None

    def _get_remote_remain_sec(self, item: Dict[str, Any]) -> Optional[int]:
        values = [self._safe_int(item.get("time_until_collect"), -1), self._safe_int(item.get("time_until_forced"), -1)]
        valid = [value for value in values if value >= 0]
        if valid:
            return min(valid)
        status = str(item.get("status") or "").lower()
        if status in {"collectable", "collect_ready", "finished", "expired", "overtime"}:
            return 0
        return None

    def _calc_slot_progress(self, slot: Dict[str, Any]) -> int:
        occupant = slot.get("occupant") or {}
        elapsed = self._safe_int(occupant.get("elapsed_seconds"), 0)
        display = self._safe_int(occupant.get("display_seconds"), 0)
        if display <= 0:
            return 0
        return max(0, min(100, round(elapsed * 100 / display)))

    def _describe_cooldown(self, item: Dict[str, Any]) -> str:
        cooling = self._safe_int(item.get("cooling_count"), 0)
        if cooling <= 0:
            return ""
        until = self._safe_int(item.get("cooldown_until"), 0)
        remaining = self._safe_int(item.get("cooldown_remaining"), 0)
        seconds = max(until - int(time.time()), remaining, 0) if until > 0 else max(remaining, 0)
        return f"冷却中 x{cooling} · 最快{self._format_duration(seconds)}" if seconds else f"冷却中 x{cooling}"

    def _request_with_retry(self, label: str, func):
        last_error = None
        max_attempts = max(1, self._http_retry_times)
        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except Exception as err:
                last_error = err
                detail = self._get_error_detail(err)
                if attempt >= max_attempts or not self._is_retryable_network_error(err):
                    raise
                wait_seconds = max(self._http_retry_delay / 1000.0, 0.1) * attempt
                logger.warning("%s %s failed %s/%s: %s", self.plugin_name, label, attempt, max_attempts, detail)
                logger.info("%s %s 将在 %.1f 秒后自动重试（%s/%s）", self.plugin_name, label, wait_seconds, attempt + 1, max_attempts)
                time.sleep(wait_seconds)
        if last_error:
            raise last_error
        return {}

    @staticmethod
    def _is_retryable_network_error(err: Exception) -> bool:
        status = getattr(getattr(err, "response", None), "status_code", None)
        if status is not None and 500 <= int(status) < 600:
            return True
        if isinstance(err, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            return True
        detail = str(err).upper()
        codes = ["ETIMEDOUT", "ECONNRESET", "ECONNABORTED", "EAI_AGAIN", "ENOTFOUND", "EHOSTUNREACH", "ECONNREFUSED"]
        if any(code in detail for code in codes):
            return True
        detail_lower = str(err).lower()
        return any(
            token in detail_lower
            for token in (
                "read timed out",
                "connect timeout",
                "connection timed out",
                "connection aborted",
                "temporarily unavailable",
                "remote disconnected",
            )
        )

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

    def _count_names(self, names: List[str]) -> str:
        counted: Dict[str, int] = {}
        for name in names:
            counted[name] = counted.get(name, 0) + 1
        return "  ".join(f"{key}×{value}" for key, value in counted.items())

    def _count_items(
        self,
        items: List[Dict[str, Any]],
        name_keys: Tuple[str, ...] = ("name",),
        qty_keys: Tuple[str, ...] = ("quantity", "count"),
    ) -> str:
        counted: Dict[str, int] = {}
        for item in self._iter_dicts(items or []):
            name = ""
            for key in name_keys:
                name = str(item.get(key) or "").strip()
                if name:
                    break
            if not name:
                continue
            quantity = 0
            for key in qty_keys:
                quantity = self._safe_int(item.get(key), 0)
                if quantity > 0:
                    break
            counted[name] = counted.get(name, 0) + max(1, quantity)
        return "  ".join(f"{key}×{value}" for key, value in counted.items())

    def _resolve_box_name(self, state: Dict[str, Any], box_key: str) -> str:
        box_key = str(box_key or "").strip()
        if not box_key:
            return "未知盲盒"
        for item in self._iter_dicts(state.get("catalog") or []):
            if str(item.get("key") or item.get("box_key") or "").strip() == box_key:
                return str(item.get("name") or box_key)
        for item in self._iter_dicts(state.get("box_inventory") or []):
            if str(item.get("box_key") or item.get("key") or "").strip() == box_key:
                return str(item.get("name") or box_key)
        return box_key

    @staticmethod
    def _iter_dicts(items: Any) -> List[Dict[str, Any]]:
        return [item for item in (items or []) if isinstance(item, dict)]

    @staticmethod
    def _get_future_ts(until_ts: int, remaining_seconds: Optional[int]) -> int:
        if until_ts and until_ts > 0:
            return until_ts
        if remaining_seconds is None:
            return 0
        remaining = max(0, int(remaining_seconds))
        return int(time.time()) + remaining if remaining > 0 else 0

    def _absolute_url(self, url: str) -> str:
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self._site_url}{url}" if url.startswith("/") else f"{self._site_url}/{url}"

    @staticmethod
    def _match_one(text: str, pattern: str, flags: int = 0) -> str:
        matched = re.search(pattern, text or "", flags=flags)
        return unescape(matched.group(1)).strip() if matched else ""

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
        try:
            parsed = datetime.strptime(str(raw), "%Y-%m-%d %H:%M:%S")
            return pytz.timezone(settings.TZ).localize(parsed)
        except Exception:
            return None

    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        seconds = max(0, int(seconds or 0))
        if seconds <= 0:
            return "0分钟"
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}天")
        if hours:
            parts.append(f"{hours}小时")
        if minutes or not parts:
            parts.append(f"{minutes}分钟")
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
