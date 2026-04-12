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
from apscheduler.triggers.cron import CronTrigger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType


class VuePill(_PluginBase):
    plugin_name = "Vue-魔丸"
    plugin_desc = "兑换、搬砖、清沙滩、炼造、获取执行记录。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2697.png"
    plugin_version = "0.1.10"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "vuepill_"
    plugin_order = 68
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_BRICK_CRON = "5 0 * * *"
    PRE_REFRESH_SECONDS = 60
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    SUMMARY_LINE = "━━━━━━━━━━━━━━"

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

    RECIPE_DEFINITIONS = {
        1: {"name": "木工件", "output_item": "木工件", "ingredients": {"砖块": 5, "木材": 1, "塑料袋": 1}},
        2: {"name": "塑料件", "output_item": "塑料件", "ingredients": {"砖块": 5, "塑料袋": 1, "瓶子": 1}},
        3: {"name": "简易工具", "output_item": "简易工具", "ingredients": {"螺丝": 2, "木工件": 2}},
        4: {"name": "能量碎片", "output_item": "能量碎片", "ingredients": {"旧电池": 1, "塑料件": 2}},
        5: {"name": "魔丸胚胎", "output_item": "魔丸胚胎", "ingredients": {"破铜片": 1, "简易工具": 1, "能量碎片": 1}},
        6: {"name": "魔丸", "output_item": "魔丸", "ingredients": {"砖块": 10, "魔丸胚胎": 2}},
    }

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _auto_cookie: bool = True
    _enable_brick: bool = True
    _enable_beach: bool = True
    _auto_craft: bool = False
    _auto_exchange: bool = False
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cookie: str = ""
    _cookie_source: str = "未配置"
    _site_domain: str = DEFAULT_SITE_DOMAIN
    _site_url: str = DEFAULT_SITE_URL
    _user_agent: str = DEFAULT_USER_AGENT
    _brick_cron: str = DEFAULT_BRICK_CRON
    _schedule_buffer_seconds: int = 5
    _random_delay_max_seconds: int = 3
    _http_timeout: int = 12
    _http_retry_times: int = 3
    _http_retry_delay: int = 1500
    _move_max_loops: int = 80
    _move_delay_min_ms: int = 30
    _move_delay_max_ms: int = 80
    _ready_retry_seconds: int = 60
    _reserve_material_count: int = 0
    _reserve_magic_pill_count: int = 0

    _next_run_time: Optional[datetime] = None
    _next_trigger_time: Optional[datetime] = None
    _next_trigger_mode: str = "run"
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
            self._sync_cookie_from_site(silent=True)
        else:
            self._cookie_source = "手动配置" if self._cookie else "未配置"

        self._load_saved_next_run()
        self._load_saved_next_trigger()
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
            {"path": "/cookie", "endpoint": self._sync_site_cookie_api, "methods": ["GET"], "auth": "bear", "summary": "同步站点 Cookie"},
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
                    "id": "VuePill_auto",
                    "name": "Vue-魔丸初始化" if self._bootstrap_pending else "Vue-魔丸智能调度",
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
        run_start = time.time()
        logger.info("## 开始执行... %s", self._format_time(self._aware_now()))
        try:
            if not self._enabled and not force:
                return {"success": False, "message": "插件未启用", "status": self._build_status(auto_refresh=False)}

            self._ensure_cookie()
            if self._force_ipv4:
                urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

            if not force and reason == "schedule" and self._is_pre_refresh_trigger():
                pill_status = self._refresh_state(reason="pre-run-refresh", record_run=False)
                logger.info("%s 已完成运行前 1 分钟预刷新", self.plugin_name)
                return {
                    "success": True,
                    "message": "运行前状态已刷新",
                    "lines": [],
                    "pill_status": pill_status,
                    "status": self._build_status(auto_refresh=False),
                }

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

            brick_result: Dict[str, Any] = {}
            beach_result: Dict[str, Any] = {}
            auto_result: Dict[str, Any] = {}

            if run_brick and page.get("brick", {}).get("ready"):
                brick_result = self._run_brick_flow(session, page.get("brick") or {})
            elif run_brick:
                brick_result = {"message": page.get("brick", {}).get("status_text") or "今日搬砖已满"}

            if run_beach and page.get("beach", {}).get("ready"):
                beach_result = self._run_beach_flow(session)
            elif run_beach:
                beach_result = {"message": page.get("beach", {}).get("status_text") or "沙滩冷却中"}

            final_page = self._fetch_stable_page_state(
                session,
                previous_page=page,
                expect_brick_update=self._safe_int(brick_result.get("moved"), 0) > 0,
                expect_beach_cooldown=bool(beach_result.get("done")),
            )
            if beach_result.get("done") and (self._auto_craft or self._auto_exchange):
                auto_result, final_page = self._run_auto_post_beach(session, final_page)
                final_page = self._fetch_stable_page_state(session, previous_page=final_page)
            retry_action = self._get_retry_action(final_page, brick_result, beach_result)
            next_run, next_action = self._compute_next_plan(final_page)
            if retry_action:
                retry_ts = int(time.time()) + max(10, self._ready_retry_seconds)
                if not next_run or retry_ts < next_run:
                    next_run, next_action = retry_ts, retry_action
                elif retry_ts == next_run:
                    next_action = self._merge_trigger_actions(next_action, retry_action)

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

            self._schedule_next_run(next_run, reason, next_action)
            pill_status = self._refresh_and_store_status(final_page, next_run, lines, next_action=next_action)
            self._append_history("⚗️ Vue-魔丸运行", lines)

            if self._notify and has_action:
                title = "【⚗️魔丸报告 】"
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title=title,
                    text=self._build_notify_text(lines, next_run),
                )

            return {
                "success": True,
                "message": lines[0],
                "status": self._build_status(auto_refresh=False),
                "pill_status": pill_status,
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            logger.error("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
            self._append_history(f"❌ {self.plugin_name}异常", [f"⚠️ {detail}"])
            if self._notify:
                self.post_message(mtype=NotificationType.Plugin, title=f"【⚠️{self.plugin_name}】 执行异常", text=f"⚠️ {detail}")
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(self._aware_now()), cost_sec)

    def _manual_worker(self):
        return self.run_job(force=True, reason="onlyonce")

    def _auto_worker(self):
        return self.run_job(force=False, reason="schedule")

    def _bootstrap_worker(self):
        self._bootstrap_pending = False
        if not self._enabled:
            return {"success": False, "message": "插件未启用"}
        return self.run_job(force=True, reason="bootstrap")

    def _refresh_data(self):
        try:
            status = self._refresh_state(reason="manual-refresh")
            return {"success": True, "message": "Vue-魔丸状态已刷新", "pill_status": status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 刷新状态失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

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

    def _craft_max_pill_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_craft_max_pill(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "魔丸炼造完成",
                "lines": result["lines"],
                "pill_status": result["pill_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 一键炼造魔丸失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        pill_status = self.get_data("pill_status") or {}
        needs_refresh = not pill_status or pill_status.get("schema_version") != self.plugin_version
        if auto_refresh and needs_refresh:
            try:
                pill_status = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)

        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "auto_cookie": self._auto_cookie,
            "enable_brick": self._enable_brick,
            "enable_beach": self._enable_beach,
            "cookie_source": self._cookie_source,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(next_trigger) if next_trigger else "",
            "next_trigger_action": self._get_scheduled_action_label(),
            "last_run": self.get_data("last_run") or "",
            "pill_status": pill_status,
            "history": (self.get_data("history") or [])[:10],
            "config": self._get_config(),
        }

    def _is_pre_refresh_trigger(self) -> bool:
        mode, _ = self._parse_trigger_mode(self._load_saved_next_trigger_mode())
        return mode == "refresh"

    def _resolve_scheduled_action(self, force: bool, reason: str) -> str:
        if force or reason != "schedule":
            return "all"
        return self._get_scheduled_action()

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

    def _get_config(self, include_options: bool = True) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "enable_brick": self._enable_brick,
            "enable_beach": self._enable_beach,
            "auto_craft": self._auto_craft,
            "auto_exchange": self._auto_exchange,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
            "brick_cron": self._brick_cron,
            "schedule_buffer_seconds": self._schedule_buffer_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "move_delay_min_ms": self._move_delay_min_ms,
            "move_delay_max_ms": self._move_delay_max_ms,
            "ready_retry_seconds": self._ready_retry_seconds,
            "reserve_material_count": self._reserve_material_count,
            "reserve_magic_pill_count": self._reserve_magic_pill_count,
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
            status = self.get_data("pill_status") or {}
        return {"success": True, "message": "配置已保存", "config": self._get_config(), "pill_status": status, "status": self._build_status(auto_refresh=False)}

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
            "enable_brick": True,
            "enable_beach": True,
            "auto_craft": False,
            "auto_exchange": False,
            "use_proxy": False,
            "force_ipv4": True,
            "cookie": "",
            "brick_cron": self.DEFAULT_BRICK_CRON,
            "schedule_buffer_seconds": 5,
            "random_delay_max_seconds": 3,
            "http_timeout": 12,
            "http_retry_times": 3,
            "http_retry_delay": 1500,
            "move_delay_min_ms": 30,
            "move_delay_max_ms": 80,
            "ready_retry_seconds": 60,
            "reserve_material_count": 0,
            "reserve_magic_pill_count": 0,
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._auto_cookie = self._to_bool(config.get("auto_cookie", True))
        self._enable_brick = self._to_bool(config.get("enable_brick", True))
        self._enable_beach = self._to_bool(config.get("enable_beach", True))
        self._auto_craft = self._to_bool(config.get("auto_craft", False))
        self._auto_exchange = self._to_bool(config.get("auto_exchange", False))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cookie = (config.get("cookie") or "").strip()
        self._brick_cron = (config.get("brick_cron") or self.DEFAULT_BRICK_CRON).strip() or self.DEFAULT_BRICK_CRON
        self._schedule_buffer_seconds = max(0, self._safe_int(config.get("schedule_buffer_seconds"), 5))
        self._random_delay_max_seconds = max(0, self._safe_int(config.get("random_delay_max_seconds"), 3))
        self._http_timeout = max(5, self._safe_int(config.get("http_timeout"), 12))
        self._http_retry_times = max(1, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(200, self._safe_int(config.get("http_retry_delay"), 1500))
        self._move_delay_min_ms = max(0, self._safe_int(config.get("move_delay_min_ms"), 30))
        self._move_delay_max_ms = max(self._move_delay_min_ms, self._safe_int(config.get("move_delay_max_ms"), 80))
        self._ready_retry_seconds = max(10, self._safe_int(config.get("ready_retry_seconds"), 60))
        self._reserve_material_count = max(0, self._safe_int(config.get("reserve_material_count"), 0))
        self._reserve_magic_pill_count = max(0, self._safe_int(config.get("reserve_magic_pill_count"), 0))

    def _update_config(self):
        self.update_config(self._get_config(include_options=False))

    def _refresh_state(self, reason: str = "refresh", record_run: bool = True) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        data = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(data)
        self._schedule_next_run(next_run, reason, next_action)
        return self._refresh_and_store_status(data, next_run, [], record_run=record_run, next_action=next_action)

    def _ensure_cookie(self):
        if self._auto_cookie:
            result = self._sync_cookie_from_site(save_config=False, silent=True)
            if result.get("success"):
                return
        if self._cookie and self._cookie.strip().lower() != "cookie":
            self._cookie_source = self._cookie_source or "手动配置"
            return
        raise ValueError("未配置有效 Cookie，请手动填写或开启自动同步")

    def _resolve_site_profile(self):
        site_url = self.DEFAULT_SITE_URL
        user_agent = self.DEFAULT_USER_AGENT
        try:
            if self._siteoper:
                site = self._siteoper.get_by_domain(self._site_domain)
                if site:
                    site_url = (getattr(site, "url", None) or site_url).rstrip("/")
                    user_agent = (getattr(site, "ua", None) or user_agent).strip()
        except Exception as err:
            logger.warning("%s 获取站点配置失败：%s", self.plugin_name, err)
        self._site_url = site_url.rstrip("/")
        self._user_agent = user_agent or self.DEFAULT_USER_AGENT

    def _sync_cookie_from_site(self, save_config: bool = False, silent: bool = True) -> Dict[str, Any]:
        try:
            if not self._siteoper:
                self._siteoper = SiteOper()
            site = self._siteoper.get_by_domain(self._site_domain)
            if not site:
                return {"success": False, "message": f"未找到站点 {self._site_domain} 的配置"}

            cookie = (getattr(site, "cookie", None) or "").strip()
            if not cookie or cookie.lower() == "cookie":
                return {"success": False, "message": f"站点 {self._site_domain} 未配置有效 Cookie"}

            self._cookie = cookie
            self._cookie_source = f"站点同步：{self._site_domain}"
            self._site_url = (getattr(site, "url", None) or self.DEFAULT_SITE_URL).rstrip("/")
            self._user_agent = (getattr(site, "ua", None) or self.DEFAULT_USER_AGENT).strip() or self.DEFAULT_USER_AGENT

            if save_config:
                self._update_config()
            if not silent:
                logger.info("%s 已同步站点 Cookie：%s", self.plugin_name, self._mask_cookie(cookie))
            return {"success": True, "message": f"已同步站点 Cookie：{self._site_domain}", "cookie_preview": self._mask_cookie(cookie)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 同步站点 Cookie 失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self._http_retry_times,
            connect=self._http_retry_times,
            read=self._http_retry_times,
            status=self._http_retry_times,
            backoff_factor=max(0.1, self._http_retry_delay / 1000.0),
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.trust_env = self._use_proxy
        session.headers.update({
            "User-Agent": self._user_agent,
            "Cookie": self._cookie,
            "Referer": f"{self._site_url}/mowan.php",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        })
        return session

    def _fetch_page_state(self, session: requests.Session) -> Dict[str, Any]:
        response = self._request_with_retry(
            "fetchMowanPage",
            lambda: session.get(
                f"{self._site_url}/mowan.php",
                params={"_": int(time.time() * 1000)},
                headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
                timeout=(self._http_timeout, self._http_timeout),
            ),
        )
        response.raise_for_status()
        html = response.text
        data = self._parse_page_state(html)
        if not data.get("title") and not data.get("stats"):
            raise ValueError("获取魔丸页面失败，Cookie 可能失效")
        return data

    def _fetch_stable_page_state(
        self,
        session: requests.Session,
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

    def _parse_page_state(self, html: str) -> Dict[str, Any]:
        stats = {
            "points": self._extract_id_int(html, "points"),
            "bonus_earned": self._extract_id_int(html, "bonusEarned"),
            "magic_pills": self._extract_id_int(html, "magicPills"),
            "daily_bricks": self._extract_id_int(html, "dailyBricks"),
        }
        daily_limit = self._extract_int(
            self._first_match(html, r'id="dailyBricks"[^>]*>\s*\d+\s*</span>\s*/\s*(\d+)'),
            50,
        )
        stats["daily_limit"] = daily_limit

        points2 = self._extract_id_int(html, "points2", stats["points"])
        magic_pills2 = self._extract_id_int(html, "magicPills2", stats["magic_pills"])
        pill_price = self._extract_int(self._first_match(html, r"魔丸限时价格：\s*<b>\s*([\d,]+)\s*魔力/颗"), 0)

        server_marker = (
            self._first_match(html, r"server_now\s*[:=]\s*(\d+)")
            or self._first_match(html, r"serverNow\s*[:=]\s*(\d+)")
            or self._first_match(html, r"serverTimeOffset:\s*([-\d]+)")
        )
        server_now = self._resolve_server_now(server_marker)
        next_brick_reset_ts = self._normalize_timestamp(
            self._first_match(html, r"next_brick_reset_ts\s*[:=]\s*(\d+)")
            or self._first_match(html, r"nextBrickResetTs:\s*(\d+)"),
            0,
        )
        last_beach_time = self._normalize_timestamp(
            self._first_match(html, r"last_beach_time\s*[:=]\s*(\d+)")
            or self._first_match(html, r"lastBeachTime:\s*(\d+)"),
            0,
        )
        beach_interval = self._extract_int(self._first_match(html, r"beachInterval:\s*(\d+)"), 7200)

        brick_ready = stats["daily_bricks"] < daily_limit
        brick_next_ts = next_brick_reset_ts if (not brick_ready and self._is_reasonable_future_ts(next_brick_reset_ts, server_now)) else 0
        beach_next_ts = last_beach_time + beach_interval if last_beach_time and self._is_reasonable_future_ts(last_beach_time + beach_interval, server_now) else 0
        beach_ready = not beach_next_ts

        brick = {
            "ready": brick_ready,
            "daily_bricks": stats["daily_bricks"],
            "daily_limit": daily_limit,
            "available_count": self._extract_int(self._extract_id_text(html, "factoryBrickCount"), max(0, daily_limit - stats["daily_bricks"])),
            "bag_count": self._extract_int(self._extract_id_text(html, "bagBrickCount"), 0),
            "status_text": self._extract_id_text(html, "brickStatus") or ("可以搬砖" if brick_ready else "今日搬砖已满"),
            "next_reset_ts": brick_next_ts,
            "next_reset_time": self._format_ts(brick_next_ts),
            "factory_text": self._extract_id_text(html, "factoryBrickCount"),
            "bag_text": self._extract_id_text(html, "bagBrickCount"),
        }

        beach = {
            "ready": beach_ready,
            "status_text": self._extract_id_text(html, "beachStatus") or ("可以进入清理" if beach_ready else "沙滩冷却中"),
            "next_ready_ts": beach_next_ts,
            "next_ready_time": self._format_ts(beach_next_ts),
            "level_text": self._first_match(html, r"发种等级.*?当前：([^）<]+)") or "",
            "hnr_text": self._first_match(html, r"HNR值.*?当前：([^）<]+)") or "",
            "enter_button_text": self._extract_button_text(html, "beachBtn") or "清理沙滩",
            "collect_button_text": self._extract_button_text(html, "collectAllTrashBtn") or "一键收集",
            "collect_enabled": self._button_enabled(html, "collectAllTrashBtn"),
        }

        exchange = {
            "pill_price": pill_price,
            "magic_pills": magic_pills2,
            "points": points2,
            "max_count": self._extract_int(self._first_match(html, r'id="exchangeCount"[^>]*max="(\d+)"'), 0),
            "enabled": self._button_enabled(html, "exchangeBtn"),
            "action_ready": self._button_enabled(html, "exchangeBtn") and magic_pills2 > 0,
            "note": "支持手动兑换魔力；一键炼造魔丸已整合到物品栏。",
        }

        inventory = self._parse_inventory(self._extract_div_inner(html, "inventoryGrid"))
        recipes = self._parse_recipes(self._extract_div_inner(html, "recipeGrid"))

        return {
            "title": self._extract_tag_text(html, "h1") or "搬砖捡破烂炼魔丸",
            "price_text": self._clean_html(self._first_match(html, r"魔丸限时价格：\s*<b>(.*?)</b>")) or "",
            "stats": stats,
            "exchange": exchange,
            "brick": brick,
            "beach": beach,
            "inventory": inventory,
            "recipes": recipes,
            "server_now": server_now,
        }

    def _parse_inventory(self, container_html: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if not container_html:
            return items
        blocks = re.findall(r'(<div class="inventory-item[^"]*">.*?</div>\s*(?=(?:<div class="inventory-item|\s*$)))', container_html, re.S)
        for block in blocks:
            name = self._clean_html(self._first_match(block, r'class="item-name"[^>]*>(.*?)</div>'))
            if not name:
                continue
            count = self._extract_int(self._first_match(block, r'class="item-count"[^>]*>(.*?)</div>'), 0)
            items.append({
                "name": name,
                "icon": self._clean_html(self._first_match(block, r'class="item-icon"[^>]*>(.*?)</span>')) or self.ITEM_ICON_MAP.get(name, "📦"),
                "count": count,
                "giftable": "gift-btn" in block,
                "has_items": "has-items" in block and count > 0,
            })
        return items

    def _parse_recipes(self, container_html: str) -> List[Dict[str, Any]]:
        recipes: List[Dict[str, Any]] = []
        if not container_html:
            return recipes
        blocks = re.findall(r'(<div class="recipe[^"]*">.*?</div>\s*(?=(?:<div class="recipe|\s*$)))', container_html, re.S)
        for block in blocks:
            title_html = self._first_match(block, r'class="recipe-title"[^>]*>(.*?)</div>')
            title_text = self._clean_html(title_html)
            if not title_text:
                continue
            materials = [self._clean_html(val) for val in re.findall(r'class="material-item"[^>]*>(.*?)</span>', block, re.S)]
            craft_id = self._extract_int(self._first_match(block, r"craft\((\d+)\)"), 0)
            recipe_def = self.RECIPE_DEFINITIONS.get(craft_id, {})
            recipes.append({
                "title": re.sub(r"\s*\([^)]*\)\s*$", "", title_text),
                "status": self._clean_html(self._first_match(title_html, r"<span[^>]*>(.*?)</span>")),
                "materials": [item for item in materials if item],
                "can_craft": "can-craft" in block and "disabled" not in block,
                "max_count": self._extract_int(self._first_match(block, r'class="craft-input"[^>]*max="(\d+)"'), 0),
                "craft_id": craft_id,
                "enabled": "disabled" not in block,
                "supported": bool(recipe_def),
                "icon": self.ITEM_ICON_MAP.get(recipe_def.get("output_item") or re.sub(r"\s*\([^)]*\)\s*$", "", title_text), "📦"),
            })
        return recipes

    def _post_action(
        self,
        session: requests.Session,
        action: str,
        payload: Optional[dict] = None,
        retry_network: bool = False,
    ) -> dict:
        form = {"action": action}
        for key, value in (payload or {}).items():
            if value is None:
                continue
            form[key] = value

        def do_request():
            response = session.post(
                f"{self._site_url}/mowan.php",
                data=form,
                timeout=(self._http_timeout, self._http_timeout),
            )
            response.raise_for_status()
            return response.json()

        if retry_network:
            return self._request_with_retry(f"postAction:{action}", do_request)
        return do_request()

    def _request_with_retry(self, label: str, func):
        last_err = None
        for idx in range(1, self._http_retry_times + 1):
            try:
                return func()
            except Exception as err:
                last_err = err
                detail = self._get_error_detail(err)
                logger.warning("%s %s failed %s/%s: %s", self.plugin_name, label, idx, self._http_retry_times, detail)
                if not self._is_retryable_network_error(err) or idx == self._http_retry_times:
                    raise
                wait_ms = self._http_retry_delay * idx + random.randint(0, 500)
                logger.info(
                    "%s %s 将在 %.1f 秒后自动重试（%s/%s）",
                    self.plugin_name,
                    label,
                    wait_ms / 1000.0,
                    idx + 1,
                    self._http_retry_times,
                )
                time.sleep(wait_ms / 1000.0)
        raise last_err

    @staticmethod
    def _is_retryable_network_error(err: Exception) -> bool:
        code = getattr(err, "code", None) or getattr(getattr(err, "cause", None), "code", None)
        status = getattr(getattr(err, "response", None), "status_code", None)
        retryable = {"ETIMEDOUT", "ECONNRESET", "ECONNABORTED", "EAI_AGAIN", "ENOTFOUND", "EHOSTUNREACH", "ECONNREFUSED"}
        if code in retryable or (status is not None and 500 <= int(status) < 600):
            return True
        if isinstance(err, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            return True
        message = str(err).lower()
        return any(
            token in message
            for token in (
                "read timed out",
                "connect timeout",
                "connection timed out",
                "connection aborted",
                "temporarily unavailable",
                "remote disconnected",
            )
        )

    def _run_brick_flow(self, session: requests.Session, brick_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                last_message = (result.get("message") or "").strip()
                moved = self._safe_int(result.get("bricks_moved"), 0)
                if moved <= 0:
                    if any(token in last_message for token in ("已满", "上限", "不能", "冷却", "结束")):
                        break
                    moved = 1
                total_moved += moved
                delay_ms = random.randint(self._move_delay_min_ms, self._move_delay_max_ms)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                continue

            last_message = (result or {}).get("message") or (result or {}).get("msg") or "今日搬砖已满"
            next_reset_ts = self._safe_int((result or {}).get("next_brick_reset_ts"), 0)
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

    def _run_beach_flow(self, session: requests.Session) -> Dict[str, Any]:
        try:
            enter = self._post_action(session, "enter_beach", retry_network=False)
        except Exception as err:
            return {"items": [], "message": "", "warning": self._get_error_detail(err), "done": False}

        if not enter or not enter.get("success", False):
            message = (enter or {}).get("message") or (enter or {}).get("msg") or "沙滩冷却中"
            return {"items": [], "message": message, "warning": "", "done": False}

        try:
            result = self._post_action(session, "collect_all_trash", retry_network=False)
        except Exception as err:
            return {"items": [], "message": "", "warning": self._get_error_detail(err), "done": False}

        if result and result.get("success", False):
            items = self._normalize_collected_items(result)
            return {"items": items, "message": (result.get("message") or "").strip(), "warning": "", "done": True}
        return {
            "items": [],
            "message": (result or {}).get("message") or (result or {}).get("msg") or "一键收集失败",
            "warning": "",
            "done": False,
        }

    def _manual_move_bricks(self) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        page = self._fetch_page_state(session)
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

    def _manual_clean_beach(self) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        page = self._fetch_page_state(session)
        if not page.get("beach", {}).get("ready"):
            lines = [f"ℹ️ 沙滩：{page.get('beach', {}).get('status_text') or '沙滩冷却中'}"]
            next_run, next_action = self._compute_next_plan(page)
            pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
            return {"pill_status": pill_status, "lines": lines}

        result = self._run_beach_flow(session)
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
        if page.get("beach", {}).get("ready") and result.get("warning"):
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
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        page = self._fetch_page_state(session)
        exchange = page.get("exchange") or {}
        max_count = self._safe_int(exchange.get("max_count"), 0)
        magic_pills = self._safe_int(exchange.get("magic_pills"), 0)
        if max_count <= 0 or magic_pills <= 0 or not exchange.get("enabled"):
            raise ValueError("当前没有可兑换的魔丸")

        quantity = self._safe_int(payload.get("quantity"), 0)
        exchange_quantity = min(max(1, quantity or 1), max_count, magic_pills)
        result = self._post_action(
            session,
            "exchange_points",
            {"quantity": exchange_quantity},
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(result.get("message") or result.get("msg") or "兑换失败")

        page = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-exchange", next_action)

        gained = self._safe_int((result or {}).get("points_gained"), 0)
        lines = [f"💰 兑换：魔丸×{exchange_quantity}"]
        if gained > 0:
            lines.append(f"✨ 获得：{gained} 魔力")
        elif (result or {}).get("message"):
            lines.append(f"ℹ️ {(result or {}).get('message')}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("💰 手动兑换", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _manual_craft_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        recipe_id = self._safe_int(payload.get("recipe_id"), 0)
        recipe_def = self.RECIPE_DEFINITIONS.get(recipe_id)
        if not recipe_def:
            raise ValueError("不支持的炼造配方")

        session = self._build_session()
        page = self._fetch_page_state(session)
        recipe = next((item for item in (page.get("recipes") or []) if self._safe_int(item.get("craft_id"), 0) == recipe_id), None)
        if not recipe:
            raise ValueError("未识别到对应配方")

        max_count = max(0, self._safe_int(recipe.get("max_count"), 0))
        if max_count <= 0 or not recipe.get("enabled"):
            raise ValueError(f"{recipe_def['name']} 当前无法炼造")

        quantity = min(max(1, self._safe_int(payload.get("quantity"), 1)), max_count)
        result = self._post_action(
            session,
            "craft_item",
            {"recipe_id": recipe_id, "quantity": quantity},
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(result.get("message") or result.get("msg") or "炼造失败")

        page = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-craft", next_action)

        output_item = recipe_def["output_item"]
        icon = self.ITEM_ICON_MAP.get(output_item, "📦")
        lines = [f"⚒️ 炼造：{icon}{output_item}×{quantity}"]
        if (result or {}).get("message"):
            lines.append(f"ℹ️ {(result or {}).get('message')}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("⚒️ 手动炼造", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _manual_craft_max_pill(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        page = self._fetch_page_state(session)
        plan_info = self._compute_magic_pill_plan(page.get("inventory") or [])
        max_count = self._safe_int(plan_info.get("max_count"), 0)
        if max_count <= 0:
            raise ValueError("当前材料不足，无法炼造魔丸")

        quantity = min(max(1, self._safe_int(payload.get("quantity"), max_count)), max_count)
        if quantity != max_count:
            plan_info = self._compute_magic_pill_plan(page.get("inventory") or [], quantity)

        craft_plan = plan_info.get("plan") or {}
        if not craft_plan or self._safe_int(craft_plan.get(6), 0) <= 0:
            raise ValueError("未生成有效的魔丸炼造计划")

        executed_steps: List[str] = []
        for recipe_id in [1, 2, 3, 4, 5, 6]:
            craft_qty = self._safe_int(craft_plan.get(recipe_id), 0)
            if craft_qty <= 0:
                continue
            recipe_def = self.RECIPE_DEFINITIONS[recipe_id]
            result = self._post_action(
                session,
                "craft_item",
                {"recipe_id": recipe_id, "quantity": craft_qty},
                retry_network=False,
            )
            if result and not result.get("success", True):
                raise ValueError(result.get("message") or result.get("msg") or f"{recipe_def['name']} 炼造失败")
            executed_steps.append(
                f"{self.ITEM_ICON_MAP.get(recipe_def['output_item'], '📦')}{recipe_def['name']}×{craft_qty}"
            )

        page = self._fetch_page_state(session)
        next_run, next_action = self._compute_next_plan(page)
        self._schedule_next_run(next_run, "manual-craft-pill", next_action)

        lines = [f"⚗️ 一键炼造魔丸：{quantity}颗"]
        if executed_steps:
            lines.append(f"🧪 步骤：{'  '.join(executed_steps)}")

        pill_status = self._refresh_and_store_status(page, next_run, lines, next_action=next_action)
        self._append_history("⚗️ 一键炼造魔丸", lines)
        return {"pill_status": pill_status, "lines": lines}

    def _run_auto_post_beach(self, session: requests.Session, page: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        result = {
            "crafted": 0,
            "craft_steps": [],
            "exchanged": 0,
            "points": 0,
            "lines": [],
            "warning": "",
        }
        current_page = page or {}

        if self._auto_craft:
            craft_result = self._auto_craft_magic_pill(session, current_page)
            if craft_result.get("crafted"):
                result["crafted"] += self._safe_int(craft_result.get("crafted"), 0)
                result["craft_steps"].extend(craft_result.get("craft_steps") or [])
                result["lines"].extend(craft_result.get("lines") or [])
                current_page = self._fetch_page_state(session)
            elif craft_result.get("warning"):
                result["warning"] = craft_result.get("warning")
                result["lines"].append(f"⚠️ 自动炼造失败：{craft_result.get('warning')}")

        if self._auto_exchange:
            exchange_result = self._auto_exchange_points(session, current_page)
            if exchange_result.get("exchanged"):
                result["exchanged"] += self._safe_int(exchange_result.get("exchanged"), 0)
                result["points"] += self._safe_int(exchange_result.get("points"), 0)
                result["lines"].extend(exchange_result.get("lines") or [])
                current_page = self._fetch_page_state(session)
            elif exchange_result.get("warning"):
                result["warning"] = result["warning"] or exchange_result.get("warning")
                result["lines"].append(f"⚠️ 自动兑换失败：{exchange_result.get('warning')}")

        return result, current_page

    def _auto_craft_magic_pill(self, session: requests.Session, page: Dict[str, Any]) -> Dict[str, Any]:
        plan_info = self._compute_magic_pill_plan(
            page.get("inventory") or [],
            reserve_material_count=self._reserve_material_count,
        )
        max_count = self._safe_int(plan_info.get("max_count"), 0)
        if max_count <= 0:
            return {}

        craft_plan = plan_info.get("plan") or {}
        executed_steps: List[str] = []
        for recipe_id in [1, 2, 3, 4, 5, 6]:
            craft_qty = self._safe_int(craft_plan.get(recipe_id), 0)
            if craft_qty <= 0:
                continue
            recipe_def = self.RECIPE_DEFINITIONS[recipe_id]
            result = self._post_action(
                session,
                "craft_item",
                {"recipe_id": recipe_id, "quantity": craft_qty},
                retry_network=False,
            )
            if result and not result.get("success", True):
                return {"warning": result.get("message") or result.get("msg") or f"{recipe_def['name']} 炼造失败"}
            executed_steps.append(
                f"{self.ITEM_ICON_MAP.get(recipe_def['output_item'], '📦')}{recipe_def['name']}×{craft_qty}"
            )

        lines = [f"⚗️ 炼造：⚗️魔丸×{max_count}"]
        return {"crafted": max_count, "craft_steps": executed_steps, "lines": lines}

    def _auto_exchange_points(self, session: requests.Session, page: Dict[str, Any]) -> Dict[str, Any]:
        exchange = page.get("exchange") or {}
        max_count = self._safe_int(exchange.get("max_count"), 0)
        magic_pills = self._safe_int(exchange.get("magic_pills"), 0)
        exchangeable = max(0, min(max_count, magic_pills - self._reserve_magic_pill_count))
        if exchangeable <= 0 or not exchange.get("enabled"):
            return {}

        result = self._post_action(
            session,
            "exchange_points",
            {"quantity": exchangeable},
            retry_network=False,
        )
        if result and not result.get("success", True):
            return {"warning": result.get("message") or result.get("msg") or "兑换失败"}

        gained = self._safe_int((result or {}).get("points_gained"), 0)
        lines = [f"💰 兑换：⚗️魔丸×{exchangeable}"]
        if gained > 0:
            lines.append(f"✨ 获得：{gained} 魔力")
        return {"exchanged": exchangeable, "points": gained, "lines": lines}

    def _compute_magic_pill_plan(
        self,
        inventory_items: List[Dict[str, Any]],
        target: Optional[int] = None,
        reserve_material_count: int = 0,
    ) -> Dict[str, Any]:
        inventory_map = self._inventory_to_map(
            inventory_items,
            reserve_material_count=reserve_material_count,
        )
        upper = max(0, sum(max(0, self._safe_int(val, 0)) for val in inventory_map.values()))
        upper = max(upper, inventory_map.get("砖块", 0) // 10, inventory_map.get("魔丸胚胎", 0) // 2)

        if target is not None:
            plan = self._plan_craft_for_item("魔丸", target, inventory_map)
            return {"max_count": target if plan else 0, "plan": plan or {}}

        best_count = 0
        best_plan: Dict[int, int] = {}
        left, right = 0, upper
        while left <= right:
            mid = (left + right) // 2
            plan = self._plan_craft_for_item("魔丸", mid, inventory_map)
            if plan is not None:
                best_count = mid
                best_plan = plan
                left = mid + 1
            else:
                right = mid - 1
        return {"max_count": best_count, "plan": best_plan}

    def _plan_craft_for_item(self, item_name: str, quantity: int, inventory_map: Dict[str, int]) -> Optional[Dict[int, int]]:
        target = max(0, self._safe_int(quantity, 0))
        if target <= 0:
            return {}
        stock = {name: max(0, self._safe_int(count, 0)) for name, count in inventory_map.items()}
        stock["魔丸"] = 0
        plan: Dict[int, int] = {}
        if self._ensure_item_for_plan(item_name, target, stock, plan):
            return plan
        return None

    def _ensure_item_for_plan(self, item_name: str, quantity: int, stock: Dict[str, int], plan: Dict[int, int]) -> bool:
        need = max(0, self._safe_int(quantity, 0))
        if need <= 0:
            return True

        available = max(0, self._safe_int(stock.get(item_name), 0))
        if available >= need:
            stock[item_name] = available - need
            return True
        if available > 0:
            need -= available
            stock[item_name] = 0

        recipe_id, recipe_def = self._get_recipe_by_output(item_name)
        if not recipe_def:
            return False

        for material_name, material_count in recipe_def["ingredients"].items():
            if not self._ensure_item_for_plan(material_name, material_count * need, stock, plan):
                return False

        plan[recipe_id] = self._safe_int(plan.get(recipe_id), 0) + need
        return True

    def _get_recipe_by_output(self, item_name: str) -> Tuple[int, Optional[Dict[str, Any]]]:
        for recipe_id, recipe_def in self.RECIPE_DEFINITIONS.items():
            if recipe_def["output_item"] == item_name:
                return recipe_id, recipe_def
        return 0, None

    def _inventory_to_map(
        self,
        inventory_items: List[Dict[str, Any]],
        reserve_material_count: int = 0,
        reserve_magic_pill_count: int = 0,
    ) -> Dict[str, int]:
        data: Dict[str, int] = {}
        for item in inventory_items or []:
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            count = max(0, self._safe_int(item.get("count"), 0))
            if name == "魔丸":
                count = max(0, count - max(0, reserve_magic_pill_count))
            elif reserve_material_count > 0:
                count = max(0, count - max(0, reserve_material_count))
            data[name] = count
        return data

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

    def _needs_retry_soon(self, page: Dict[str, Any], brick_result: Dict[str, Any], beach_result: Dict[str, Any]) -> bool:
        brick_retry = page.get("brick", {}).get("ready") and bool(brick_result.get("warning") or brick_result.get("attempted"))
        beach_retry = bool(beach_result.get("warning")) and page.get("beach", {}).get("ready")
        return brick_retry or beach_retry

    def _get_retry_action(self, page: Dict[str, Any], brick_result: Dict[str, Any], beach_result: Dict[str, Any]) -> str:
        brick_retry = page.get("brick", {}).get("ready") and bool(brick_result.get("warning") or brick_result.get("attempted"))
        beach_retry = bool(beach_result.get("warning")) and page.get("beach", {}).get("ready")
        if brick_retry and beach_retry:
            return "all"
        if brick_retry:
            return "brick"
        if beach_retry:
            return "beach"
        return ""

    def _should_skip_run(self) -> bool:
        next_trigger = self._load_saved_next_trigger()
        if not next_trigger:
            return False
        return self._aware_now() < next_trigger

    def _get_next_run_for_service(self) -> Optional[datetime]:
        if self._bootstrap_pending:
            return self._aware_now() + timedelta(seconds=3)
        next_trigger = self._next_trigger_time or self._load_saved_next_trigger()
        if not next_trigger:
            return None
        now = self._aware_now()
        return next_trigger if next_trigger > now else now + timedelta(seconds=5)

    def _schedule_next_run(self, next_run_ts: Optional[int], reason: str = "", next_action: str = "all"):
        next_run_ts = self._normalize_timestamp(next_run_ts, 0)
        if next_run_ts and not self._is_reasonable_future_ts(next_run_ts, int(time.time()) - 1):
            next_run_ts = 0
        next_action = next_action if next_action in {"brick", "beach", "all"} else "all"
        if next_run_ts and next_run_ts > 0:
            next_run = self._aware_from_timestamp(next_run_ts)
            now = self._aware_now()
            pre_refresh_time = next_run - timedelta(seconds=self.PRE_REFRESH_SECONDS)
            if pre_refresh_time > now + timedelta(seconds=5):
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

        if self._enabled:
            self._bootstrap_pending = not bool(next_run_ts)
            self._reregister_plugin(reason)

    def _reregister_plugin(self, reason: str = ""):
        try:
            Scheduler().update_plugin_job(self.__class__.__name__)
            logger.info("%s 已重新注册调度：%s", self.plugin_name, reason or "update")
        except Exception:
            try:
                Scheduler().reload_plugin_job(self.__class__.__name__)
                logger.info("%s 已重新加载调度：%s", self.plugin_name, reason or "reload")
            except Exception as err:
                logger.warning("%s 重新注册调度失败：%s", self.plugin_name, err)

    def _load_saved_next_run(self) -> Optional[datetime]:
        if self._next_run_time:
            return self._next_run_time
        raw = self.get_data("next_run_time") or ((self.get_data("state") or {}).get("next_run_time"))
        self._next_run_time = self._parse_datetime(raw)
        return self._next_run_time

    def _load_saved_next_trigger(self) -> Optional[datetime]:
        if self._next_trigger_time:
            return self._next_trigger_time
        raw = self.get_data("next_trigger_time") or ((self.get_data("state") or {}).get("next_trigger_time"))
        self._next_trigger_time = self._parse_datetime(raw)
        return self._next_trigger_time

    def _load_saved_next_trigger_mode(self) -> str:
        if self._next_trigger_mode:
            return self._next_trigger_mode
        self._next_trigger_mode = str(self.get_data("next_trigger_mode") or "run").strip() or "run"
        return self._next_trigger_mode

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
            logger.warning("%s CRON 表达式无效：%s | %s", self.plugin_name, expr, err)
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
        self.save_data("state", self._build_state_record(data, next_run, lines, next_action))
        pill_status = self._build_ui_state(data, next_run, lines, next_action)
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
        exchange = data.get("exchange") or {}
        brick = data.get("brick") or {}
        beach = data.get("beach") or {}
        inventory = data.get("inventory") or []
        recipes = data.get("recipes") or []
        next_trigger = self._load_saved_next_trigger()
        pill_plan = self._compute_magic_pill_plan(inventory)
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
            "cookie_source": self._cookie_source,
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
                "magic_pill_requirements": self.RECIPE_DEFINITIONS[6]["ingredients"],
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
        report_lines = [line for line in lines if line.startswith(("🧱", "🏖️", "⚗️", "💰", "✅", "✨"))]
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

    def _run_brick_flow(self, session: requests.Session, brick_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                last_message = (result.get("message") or "").strip()
                moved = self._safe_int(result.get("bricks_moved"), 0)
                if moved <= 0:
                    if any(token in last_message for token in ("已满", "上限", "不能", "冷却", "结束")):
                        break
                    moved = 1
                total_moved += moved
                delay_ms = random.randint(self._move_delay_min_ms, self._move_delay_max_ms)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                continue

            last_message = (result or {}).get("message") or (result or {}).get("msg") or "今日搬砖已满"
            next_reset_ts = self._safe_int((result or {}).get("next_brick_reset_ts"), 0)
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
            lines.append(f"⚠️ 沙滩失败：{beach_result.get('warning')}")
            has_warning = True

        for line in (auto_result or {}).get("lines") or []:
            lines.append(line)
            if line.startswith(("⚗️", "💰", "⚒️", "✅")):
                has_action = True
            elif line.startswith("⚠️"):
                has_warning = True

        return lines, has_action, has_warning

    def _build_notify_text(self, lines: List[str], next_run: Optional[int]) -> str:
        report_lines = [line for line in lines if line.startswith(("🧱", "🏖️", "⚗️", "💰", "⚒️", "✅"))]
        if not report_lines:
            report_lines = [line for line in lines if not line.startswith(("ℹ️", "⚠️"))]
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
        replacements = [
            ("🏖️ 沙滩：", "🏖️沙滩："),
            ("🧱 搬砖：", "🧱搬砖："),
            ("💰 兑换：", "💰兑换："),
            ("⚒️ 炼造：", "⚒️炼造："),
            ("⚗️ 魔丸：", "⚗️魔丸："),
            ("⚠️ 沙滩失败：", "🏖️沙滩失败："),
            ("⚠️ 搬砖失败：", "🧱搬砖失败："),
            ("ℹ️ 沙滩：", "🏖️沙滩："),
            ("ℹ️ 搬砖：", "🧱搬砖："),
        ]
        manual_replacements = [
            ("🏖️ 沙滩：", "🏖️手动沙滩："),
            ("🧱 搬砖：", "🧱手动搬砖："),
            ("💰 兑换：", "💰手动兑换："),
            ("⚒️ 炼造：", "⚒️手动炼造："),
            ("⚗️ 魔丸：", "⚗️手动魔丸："),
            ("⚠️ 沙滩失败：", "🏖️手动沙滩失败："),
            ("⚠️ 搬砖失败：", "🧱手动搬砖失败："),
            ("ℹ️ 沙滩：", "🏖️手动沙滩："),
            ("ℹ️ 搬砖：", "🧱手动搬砖："),
        ]

        if title == "⚗️ Vue-魔丸运行":
            history_title = first_line
            for src, dest in replacements:
                if history_title.startswith(src):
                    history_title = history_title.replace(src, dest, 1)
                    break
            return history_title, history_lines[1:]

        if title in {"🏖️ 手动清沙滩", "🧱 手动搬砖", "💰 手动兑换", "⚒️ 手动炼造", "⚗️ 一键炼造魔丸"}:
            history_title = first_line
            for src, dest in manual_replacements:
                if history_title.startswith(src):
                    history_title = history_title.replace(src, dest, 1)
                    break
            return history_title, history_lines[1:]

        return history_title, history_lines

    def _extract_id_text(self, html: str, element_id: str) -> str:
        return self._clean_html(self._first_match(html, rf'id="{re.escape(element_id)}"[^>]*>(.*?)</'))

    def _extract_tag_text(self, html: str, tag: str) -> str:
        return self._clean_html(self._first_match(html, rf"<{tag}[^>]*>(.*?)</{tag}>"))

    def _extract_button_text(self, html: str, element_id: str) -> str:
        return self._clean_html(self._first_match(html, rf'id="{re.escape(element_id)}"[^>]*>(.*?)</button>'))

    def _button_enabled(self, html: str, element_id: str) -> bool:
        tag = self._first_match(html, rf'(<button[^>]+id="{re.escape(element_id)}"[^>]*>)')
        if not tag:
            return False
        return "disabled" not in tag.lower()

    def _extract_id_int(self, html: str, element_id: str, default: int = 0) -> int:
        return self._extract_int(self._extract_id_text(html, element_id), default)

    def _extract_div_inner(self, html: str, element_id: str) -> str:
        match = re.search(rf'<div[^>]+id="{re.escape(element_id)}"[^>]*>', html, re.I)
        if not match:
            return ""
        start = match.end()
        depth = 1
        for tag in re.finditer(r"</?div\b", html[start:], re.I):
            token = tag.group(0).lower()
            if token.startswith("</div"):
                depth -= 1
            else:
                depth += 1
            if depth == 0:
                return html[start:start + tag.start()]
        return ""

    @staticmethod
    def _first_match(text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.S | re.I)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _clean_html(text: str) -> str:
        if not text:
            return ""
        stripped = re.sub(r"<[^>]+>", " ", text)
        stripped = unescape(stripped)
        return re.sub(r"\s+", " ", stripped).strip()

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

    def _extract_int(self, value: Any, default: int = 0) -> int:
        return self._safe_int(value, default)

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

    @staticmethod
    def _mask_cookie(cookie: str) -> str:
        if not cookie:
            return ""
        return cookie if len(cookie) <= 18 else f"{cookie[:10]}...{cookie[-6:]}"

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

    @staticmethod
    def _get_error_detail(err: Exception) -> str:
        code = getattr(err, "code", None) or getattr(getattr(err, "cause", None), "code", None)
        message = str(err)
        return " | ".join([str(part) for part in [code, message] if part]) or "UNKNOWN"

