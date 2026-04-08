import json
import random
import re
import socket
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urljoin, urlparse

import pytz
import requests
import urllib3.util.connection as urllib3_connection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.core.config import settings
from app.db.site_oper import SiteOper
from app.helper.browser import PlaywrightHelper
from app.helper.cloudflare import under_challenge
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType


class PrivateCheckin(_PluginBase):
    plugin_name = "自用签到"
    plugin_desc = (
        "支持自定义浏览器签到页与 GET/POST 接口签到，"
        "浏览器型任务默认优先使用 Playwright 过 CF。"
    )
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2705.png"
    plugin_version = "0.3.0"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "privatecheckin_"
    plugin_order = 68
    auth_level = 1

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    DEFAULT_CRON = "0 9 * * *"
    DEFAULT_SUCCESS_KEYWORDS = (
        "签到成功|今日已签到|已经签到|已签到|签到已得|\"success\":true|\"status\":\"success\"|already signed|already attended|check-in completed"
    )
    DEFAULT_FAILURE_KEYWORDS = "Cookie已失效|未登录|请先登录|重新登录|login required"
    TASK_TYPE_LABELS = {
        "generic_attendance": "浏览器自动签到页",
        "request_get": "GET 接口签到",
        "request_post_form": "POST 表单签到",
        "request_post_json": "POST JSON 签到",
        "siqi_attendance": "思齐签到",
        "siqi_hnr_claim": "思齐 HNR 领取",
        "new_api_checkin": "New API 签到",
    }
    EXPOSED_TASK_TYPE_VALUES = [
        "generic_attendance",
        "request_get",
        "request_post_form",
        "request_post_json",
    ]
    CF_MODE_LABELS = {
        "auto": "智能兜底",
        "request": "仅请求",
        "playwright": "仅 Playwright",
        "flaresolverr": "仅 FlareSolverr",
    }

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cron: str = DEFAULT_CRON
    _max_workers: int = 2
    _random_delay_max_seconds: int = 5
    _http_timeout: int = 18
    _http_retry_times: int = 3
    _http_retry_delay: int = 1500
    _flaresolverr_url: str = ""
    _tasks: List[Dict[str, Any]] = []

    def __init__(self):
        super().__init__()

    def init_plugin(self, config: Optional[dict] = None):
        self.stop_service()
        self._siteoper = SiteOper()

        merged = self._default_config()
        if config:
            merged.update(config)
        self._apply_config(merged)

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
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取自用签到配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存自用签到配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取自用签到状态"},
            {"path": "/run", "endpoint": self._run_api, "methods": ["POST"], "auth": "bear", "summary": "执行全部或单个签到任务"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        if self._enabled and self._cron:
            try:
                services.append({
                    "id": "PrivateCheckin",
                    "name": "自用签到定时任务",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self._auto_worker,
                    "kwargs": {},
                })
            except Exception as err:
                logger.warning("%s Cron 配置无效：%s", self.plugin_name, err)
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

    def _manual_worker(self):
        self.run_job(force=True, reason="onlyonce")

    def _auto_worker(self):
        self.run_job(force=False, reason="cron")

    def run_job(self, force: bool = False, task_id: str = "", reason: str = "manual") -> Dict[str, Any]:
        started = time.time()
        logger.info("## %s 开始执行... %s", self.plugin_name, self._format_time(self._aware_now()))
        try:
            if not self._enabled and not force:
                return {"success": False, "message": "插件未启用", "status": self._build_status()}

            tasks = self._select_tasks(task_id=task_id, force=force)
            if not tasks:
                return {"success": False, "message": "没有可执行的任务", "status": self._build_status()}

            if self._force_ipv4:
                urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

            delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if delay:
                logger.info("%s 随机延迟 %s 秒后执行", self.plugin_name, delay)
                time.sleep(delay)

            results: List[Dict[str, Any]] = []
            worker_count = max(1, min(self._max_workers, len(tasks)))
            if worker_count == 1:
                for task in tasks:
                    results.append(self._execute_task(task))
            else:
                with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="privatecheckin") as executor:
                    futures = {executor.submit(self._execute_task, task): task for task in tasks}
                    for future in as_completed(futures):
                        try:
                            results.append(future.result())
                        except Exception as err:
                            task = futures[future]
                            logger.error("%s 任务执行异常：%s", task.get("name"), err)
                            results.append(self._build_result(task=task, success=False, message=f"执行异常：{err}", method="internal"))

            results.sort(key=lambda item: item.get("name", ""))
            self._record_results(results=results, reason=reason)

            summary_lines = []
            success_count = 0
            for result in results:
                prefix = "成功" if result.get("success") else "失败"
                if result.get("success"):
                    success_count += 1
                summary_lines.append(f"[{prefix}] {result.get('name')} - {result.get('message')}")

            summary_title = f"已完成 {len(results)} 个任务，成功 {success_count} 个"
            if self._notify and summary_lines:
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title=f"【{self.plugin_name}】 {summary_title}",
                    text="\n".join(summary_lines),
                )

            return {
                "success": success_count == len(results),
                "message": summary_title,
                "results": results,
                "status": self._build_status(),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            traceback.print_exc()
            if self._notify:
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title=f"【{self.plugin_name}】 执行异常",
                    text=detail,
                )
            return {"success": False, "message": detail, "status": self._build_status()}
        finally:
            cost_sec = max(1, round(time.time() - started))
            logger.info("## %s 执行结束... %s  耗时 %s 秒", self.plugin_name, self._format_time(self._aware_now()), cost_sec)

    def _get_status(self) -> Dict[str, Any]:
        return self._build_status()

    def _run_api(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        task_id = (payload.get("task_id") or "").strip()
        force = bool(task_id) or self._to_bool(payload.get("force", True))
        return self.run_job(force=force, task_id=task_id, reason="api")

    def _get_config(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cron": self._cron,
            "max_workers": self._max_workers,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "flaresolverr_url": self._flaresolverr_url,
            "tasks": [self._export_task(task) for task in self._tasks],
            "task_type_options": [
                {"title": self.TASK_TYPE_LABELS.get(value, value), "value": value}
                for value in self.EXPOSED_TASK_TYPE_VALUES
            ],
            "cf_mode_options": [{"title": label, "value": value} for value, label in self.CF_MODE_LABELS.items()],
        }

    def _save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        merged = self._default_config()
        if config:
            merged.update(config)
        self.init_plugin(merged)
        self._update_config()
        self._reregister_plugin("save_config")
        return {"success": True, "message": "配置已保存", "config": self._get_config(), "status": self._build_status()}

    def _update_config(self):
        self.update_config(
            {
                "enabled": self._enabled,
                "notify": self._notify,
                "onlyonce": self._onlyonce,
                "use_proxy": self._use_proxy,
                "force_ipv4": self._force_ipv4,
                "cron": self._cron,
                "max_workers": self._max_workers,
                "random_delay_max_seconds": self._random_delay_max_seconds,
                "http_timeout": self._http_timeout,
                "http_retry_times": self._http_retry_times,
                "http_retry_delay": self._http_retry_delay,
                "flaresolverr_url": self._flaresolverr_url,
                "tasks": [self._export_task(task) for task in self._tasks],
            }
        )

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "use_proxy": False,
            "force_ipv4": True,
            "cron": self.DEFAULT_CRON,
            "max_workers": 2,
            "random_delay_max_seconds": 5,
            "http_timeout": 18,
            "http_retry_times": 3,
            "http_retry_delay": 1500,
            "flaresolverr_url": "",
            "tasks": [],
        }

    def _default_tasks(self) -> List[Dict[str, Any]]:
        return []

    def _task_template(self) -> Dict[str, Any]:
        return {
            "id": "",
            "name": "",
            "enabled": True,
            "task_type": "generic_attendance",
            "site_url": "",
            "target_url": "",
            "use_moviepilot_cookie": False,
            "moviepilot_domain": "",
            "cookie": "",
            "user_agent": "",
            "cf_mode": "playwright",
            "success_keywords": self.DEFAULT_SUCCESS_KEYWORDS,
            "failure_keywords": self.DEFAULT_FAILURE_KEYWORDS,
            "request_body": "",
            "request_headers": "",
            "allow_logged_in_as_success": True,
            "use_proxy": False,
            "force_ipv4": True,
            "new_api_uid": "",
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cron = (config.get("cron") or self.DEFAULT_CRON).strip() or self.DEFAULT_CRON
        self._max_workers = max(1, self._safe_int(config.get("max_workers"), 2))
        self._random_delay_max_seconds = max(0, self._safe_int(config.get("random_delay_max_seconds"), 5))
        self._http_timeout = max(5, self._safe_int(config.get("http_timeout"), 18))
        self._http_retry_times = max(1, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(0, self._safe_int(config.get("http_retry_delay"), 1500))
        self._flaresolverr_url = self._normalize_flaresolverr_url(config.get("flaresolverr_url"))

        tasks = config.get("tasks") or []
        normalized_tasks = []
        seen_ids = set()
        for raw_task in tasks:
            task = self._normalize_task(raw_task or {})
            if task["id"] in seen_ids:
                task["id"] = f"{task['id']}-{uuid.uuid4().hex[:4]}"
            seen_ids.add(task["id"])
            normalized_tasks.append(task)

        self._tasks = normalized_tasks

    def _normalize_task(self, raw_task: Dict[str, Any]) -> Dict[str, Any]:
        task = self._task_template()
        task.update(raw_task or {})
        task["id"] = (task.get("id") or f"task-{uuid.uuid4().hex[:8]}").strip()
        task["name"] = (task.get("name") or "未命名任务").strip() or "未命名任务"
        task["task_type"] = task.get("task_type") if task.get("task_type") in self.TASK_TYPE_LABELS else "generic_attendance"
        task["enabled"] = self._to_bool(task.get("enabled", True))
        task["use_moviepilot_cookie"] = self._to_bool(task.get("use_moviepilot_cookie", False))
        task["allow_logged_in_as_success"] = self._to_bool(task.get("allow_logged_in_as_success", True))
        task["use_proxy"] = self._to_bool(task.get("use_proxy", self._use_proxy))
        task["force_ipv4"] = self._to_bool(task.get("force_ipv4", self._force_ipv4))
        task["cf_mode"] = task.get("cf_mode") if task.get("cf_mode") in self.CF_MODE_LABELS else "playwright"
        task["site_url"] = self._normalize_url(task.get("site_url") or self._guess_site_url(task.get("target_url")))
        task["target_url"] = self._normalize_url(task.get("target_url") or self._default_target_url(task))
        task["moviepilot_domain"] = (task.get("moviepilot_domain") or self._guess_domain(task["site_url"] or task["target_url"]) or "").strip().lower()
        task["cookie"] = (task.get("cookie") or "").strip()
        task["user_agent"] = (task.get("user_agent") or "").strip()
        task["success_keywords"] = (task.get("success_keywords") or self.DEFAULT_SUCCESS_KEYWORDS).strip()
        task["failure_keywords"] = (task.get("failure_keywords") or self.DEFAULT_FAILURE_KEYWORDS).strip()
        task["request_body"] = (task.get("request_body") or "").strip()
        task["request_headers"] = (task.get("request_headers") or "").strip()
        task["new_api_uid"] = (task.get("new_api_uid") or "").strip()
        return task

    def _export_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": task.get("id"),
            "name": task.get("name"),
            "enabled": bool(task.get("enabled")),
            "task_type": task.get("task_type"),
            "site_url": task.get("site_url") or "",
            "target_url": task.get("target_url") or "",
            "use_moviepilot_cookie": bool(task.get("use_moviepilot_cookie")),
            "moviepilot_domain": task.get("moviepilot_domain") or "",
            "cookie": task.get("cookie") or "",
            "user_agent": task.get("user_agent") or "",
            "cf_mode": task.get("cf_mode") or "playwright",
            "success_keywords": task.get("success_keywords") or "",
            "failure_keywords": task.get("failure_keywords") or "",
            "request_body": task.get("request_body") or "",
            "request_headers": task.get("request_headers") or "",
            "allow_logged_in_as_success": bool(task.get("allow_logged_in_as_success")),
            "use_proxy": bool(task.get("use_proxy")),
            "force_ipv4": bool(task.get("force_ipv4")),
            "new_api_uid": task.get("new_api_uid") or "",
        }

    def _select_tasks(self, task_id: str = "", force: bool = False) -> List[Dict[str, Any]]:
        if task_id:
            task = next((item for item in self._tasks if item.get("id") == task_id), None)
            return [task] if task else []
        return [task for task in self._tasks if task.get("enabled")]

    def _build_status(self) -> Dict[str, Any]:
        task_state_map = self.get_data("task_state") or {}
        history = self.get_data("history") or []
        last_summary = self.get_data("last_summary") or []

        tasks = []
        enabled_count = 0
        success_total = 0
        fail_total = 0
        for task in self._tasks:
            state = task_state_map.get(task.get("id"), {})
            if task.get("enabled"):
                enabled_count += 1
            success_total += int(state.get("success_count") or 0)
            fail_total += int(state.get("fail_count") or 0)
            tasks.append(
                {
                    **self._export_task(task),
                    "task_type_label": self.TASK_TYPE_LABELS.get(task.get("task_type"), task.get("task_type")),
                    "cf_mode_label": self.CF_MODE_LABELS.get(task.get("cf_mode"), task.get("cf_mode")),
                    "cookie_preview": self._mask_cookie(task.get("cookie") or ""),
                    "last_run": state.get("last_run") or "",
                    "last_result": state.get("last_result") or "",
                    "last_message": state.get("last_message") or "",
                    "last_detail": state.get("last_detail") or "",
                    "last_method": state.get("last_method") or "",
                    "cookie_source": state.get("cookie_source") or "",
                    "last_duration_sec": state.get("last_duration_sec") or 0,
                    "success_count": int(state.get("success_count") or 0),
                    "fail_count": int(state.get("fail_count") or 0),
                    "recent": state.get("recent") or [],
                }
            )

        next_run = self._get_next_run_time()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": self._cron,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "flaresolverr_enabled": bool(self._flaresolverr_url),
            "flaresolverr_url": self._flaresolverr_url,
            "task_count": len(tasks),
            "enabled_task_count": enabled_count,
            "total_success_count": success_total,
            "total_fail_count": fail_total,
            "last_run": self.get_data("last_run") or "",
            "next_run_time": self._format_time(next_run) if next_run else "",
            "summary": last_summary,
            "tasks": tasks,
            "history": history[:30],
            "guides": [
                "浏览器自动签到页默认建议使用 Playwright，适合 attendance.php 这类打开页面即自动签到或领取的站点。",
                "GET / POST 表单 / POST JSON 这三类接口任务通过 requests 执行，适合 AJAX 或 API 型签到。",
                "智能兜底会优先尝试 Playwright，再回退 requests，最后才尝试 FlareSolverr。",
                "MoviePilot V2 容器已自带 Playwright；只有强 CF 仍过不去时，再额外部署 FlareSolverr。",
                "任务支持优先读取 MoviePilot 站点 Cookie；如果站点不在站点管理里，直接填写浏览器 Cookie 或请求头即可。",
            ],
        }

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        try:
            runtime = self._resolve_runtime(task)
            task_type = task.get("task_type")
            if task_type == "siqi_attendance":
                success, message, method, detail = self._run_siqi_attendance(task, runtime)
            elif task_type == "siqi_hnr_claim":
                success, message, method, detail = self._run_siqi_hnr_claim(task, runtime)
            elif task_type == "new_api_checkin":
                success, message, method, detail = self._run_new_api_checkin(task, runtime)
            elif task_type in ["request_get", "request_post_form", "request_post_json"]:
                success, message, method, detail = self._run_request_task(task, runtime)
            else:
                success, message, method, detail = self._run_generic_attendance(task, runtime)

            result = self._build_result(task=task, success=success, message=message, method=method, detail=detail)
            result["cookie_source"] = runtime.get("cookie_source") or ""
            result["last_duration_sec"] = max(1, round(time.time() - start_time))
            return result
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 执行失败：%s", task.get("name"), detail)
            traceback.print_exc()
            result = self._build_result(task=task, success=False, message=detail, method="internal")
            result["last_duration_sec"] = max(1, round(time.time() - start_time))
            return result

    def _build_result(
        self,
        task: Dict[str, Any],
        success: bool,
        message: str,
        method: str,
        detail: str = "",
    ) -> Dict[str, Any]:
        now = self._format_time(self._aware_now())
        return {
            "task_id": task.get("id"),
            "name": task.get("name"),
            "success": bool(success),
            "message": (message or "").strip(),
            "detail": (detail or "").strip(),
            "method": method,
            "task_type": task.get("task_type"),
            "task_type_label": self.TASK_TYPE_LABELS.get(task.get("task_type"), task.get("task_type")),
            "time": now,
            "status": "success" if success else "error",
        }

    def _resolve_runtime(self, task: Dict[str, Any]) -> Dict[str, Any]:
        runtime = dict(task)
        runtime["site_url"] = self._normalize_url(runtime.get("site_url") or self._guess_site_url(runtime.get("target_url")))
        runtime["target_url"] = self._normalize_url(runtime.get("target_url") or self._default_target_url(runtime))
        runtime["user_agent"] = runtime.get("user_agent") or self.DEFAULT_USER_AGENT
        runtime["cookie_source"] = "手动配置" if runtime.get("cookie") else "未配置"
        runtime["proxy_dict"] = getattr(settings, "PROXY", None) if runtime.get("use_proxy") else None
        runtime["proxy_server"] = getattr(settings, "PROXY_SERVER", None) if runtime.get("use_proxy") else None

        if runtime.get("use_moviepilot_cookie"):
            domain = runtime.get("moviepilot_domain") or self._guess_domain(runtime.get("site_url") or runtime.get("target_url"))
            if domain:
                site = self._get_site_by_domain(domain)
                cookie = (getattr(site, "cookie", None) or "").strip() if site else ""
                if cookie and cookie.lower() != "cookie":
                    runtime["cookie"] = cookie
                    runtime["cookie_source"] = f"站点同步：{domain}"
                    site_url = (getattr(site, "url", None) or runtime.get("site_url") or "").strip()
                    if site_url:
                        runtime["site_url"] = self._normalize_url(site_url)
                    runtime["user_agent"] = (getattr(site, "ua", None) or runtime.get("user_agent") or self.DEFAULT_USER_AGENT).strip() or self.DEFAULT_USER_AGENT

        if runtime.get("force_ipv4"):
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

        if runtime.get("task_type") == "new_api_checkin":
            if not runtime.get("cookie"):
                raise ValueError("未配置 New API Cookie")
            if not runtime.get("new_api_uid"):
                raise ValueError("未填写 New API UID")
            if not runtime.get("site_url"):
                raise ValueError("未配置 New API 站点地址")
            return runtime

        if not runtime.get("target_url"):
            raise ValueError("未配置任务目标地址")
        if runtime.get("task_type") in ["siqi_attendance", "siqi_hnr_claim"] and not runtime.get("cookie"):
            raise ValueError("未配置有效 Cookie，请手动填写或开启 MoviePilot 站点 Cookie")
        return runtime

    def _run_generic_attendance(self, task: Dict[str, Any], runtime: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        target_url = runtime.get("target_url")
        logger.info("%s 正在访问签到页：%s", task.get("name"), target_url)
        page = self._fetch_page_with_cf(task=task, runtime=runtime, url=target_url)

        if not page.get("success"):
            return False, page.get("message") or "无法打开页面", page.get("method") or "request", page.get("detail") or ""

        html = page.get("text") or ""
        if self._looks_logged_out(html):
            return False, "Cookie 已失效或未登录", page.get("method") or "request", ""

        if self._match_keywords(html, task.get("failure_keywords")) and not self._match_keywords(html, task.get("success_keywords")):
            return False, "页面命中失败关键字", page.get("method") or "request", ""

        if self._match_keywords(html, task.get("success_keywords")):
            return True, "签到成功", page.get("method") or "request", ""

        if self._to_bool(task.get("allow_logged_in_as_success", True)):
            return True, "已访问签到页，未捕获明确成功关键字，按已登录通过处理", page.get("method") or "request", ""

        return False, "未命中成功关键字", page.get("method") or "request", ""

    def _run_request_task(self, task: Dict[str, Any], runtime: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        task_type = task.get("task_type")
        target_url = runtime.get("target_url")
        headers = self._parse_request_headers(task.get("request_headers"))
        session = self._build_session(
            runtime=runtime,
            extra_headers=headers,
            allow_post_retry=task_type in ["request_post_form", "request_post_json"],
        )

        logger.info("%s 正在执行接口签到：%s", task.get("name"), target_url)
        if task_type == "request_get":
            params = self._parse_key_value_payload(task.get("request_body"))
            response = session.get(
                target_url,
                params=params or None,
                timeout=(self._http_timeout, self._http_timeout),
            )
        elif task_type == "request_post_form":
            payload = self._parse_key_value_payload(task.get("request_body"))
            response = session.post(
                target_url,
                data=payload,
                timeout=(self._http_timeout, self._http_timeout),
            )
        else:
            payload = self._parse_json_payload(task.get("request_body"))
            response = session.post(
                target_url,
                json=payload,
                timeout=(self._http_timeout, self._http_timeout),
            )

        response_text = response.text or ""
        if self._looks_logged_out(response_text):
            return False, "Cookie 已失效或未登录", "request", ""
        if response.status_code >= 400:
            return False, f"请求失败，HTTP {response.status_code}", "request", ""
        if self._match_keywords(response_text, task.get("failure_keywords")) and not self._match_keywords(
            response_text, task.get("success_keywords")
        ):
            return False, "响应命中失败关键字", "request", ""
        if self._match_keywords(response_text, task.get("success_keywords")):
            return True, "请求成功，命中成功关键字", "request", ""

        response_json = self._safe_json(response)
        if isinstance(response_json, dict) and response_json:
            success, message = self._detect_json_success(response_json)
            if success is True:
                return True, message or "接口返回成功", "request", ""
            if success is False:
                return False, message or "接口返回失败", "request", ""

        return False, "未命中成功关键字，请补充成功关键字/正则", "request", ""

    def _run_siqi_attendance(self, task: Dict[str, Any], runtime: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        url = runtime.get("target_url") or urljoin(runtime.get("site_url", "") + "/", "attendance.php")
        session = self._build_session(runtime=runtime, allow_post_retry=False)

        resp = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        html = resp.text
        if self._looks_logged_out(html):
            return False, "Cookie 已失效，请更新思齐 Cookie", "request", ""
        if self._is_cloudflare_blocked(html, resp.status_code):
            return False, "命中 Cloudflare 防护，请改用浏览器仿真或检查 Cookie", "request", ""

        if "签到成功" in html or "今日已签到" in html:
            count, consecutive, gain = self._extract_siqi_sign_info(html)
            return True, f"签到成功，第 {count} 次，连续 {consecutive} 天，获得 {gain} 魔力", "request", ""

        imagehash_match = re.search(r'name="imagehash"\s+value="([a-f0-9]+)"', html)
        if not imagehash_match:
            return False, "未找到 imagehash 字段", "request", ""
        imagehash = imagehash_match.group(1)

        captcha_match = re.search(r"captchaString\s*=\s*'([^']+)'", html)
        if not captcha_match:
            return False, "未找到验证码值", "request", ""
        captcha = captcha_match.group(1)

        form_action = url
        form_match = re.search(r'<form[^>]*action=["\']([^"\']*)', html, re.IGNORECASE)
        if form_match and form_match.group(1):
            action = form_match.group(1).strip()
            form_action = urljoin(url, action)

        post_resp = session.post(
            form_action,
            data={"imagestring": captcha, "imagehash": imagehash},
            headers={"Referer": url},
            timeout=(self._http_timeout, self._http_timeout),
        )
        if post_resp.status_code >= 400:
            return False, f"提交签到失败，HTTP {post_resp.status_code}", "request", ""

        verify_resp = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        verify_html = verify_resp.text
        if "签到成功" in verify_html or "今日已签到" in verify_html:
            count, consecutive, gain = self._extract_siqi_sign_info(verify_html)
            return True, f"签到成功，第 {count} 次，连续 {consecutive} 天，获得 {gain} 魔力", "request", ""

        return False, "签到后未检测到成功信息", "request", ""

    def _run_siqi_hnr_claim(self, task: Dict[str, Any], runtime: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        reward_names = {
            "reward_10": "前10名奖励",
            "reward_20": "前20名奖励",
            "reward_30": "前30名奖励",
            "reward_50": "前50名奖励",
            "reward_100": "前100名奖励",
            "reward_200": "前200名奖励",
            "welfare": "福利奖励",
        }

        list_url = runtime.get("target_url") or urljoin(runtime.get("site_url", "") + "/", "hnrview.php")
        claim_url = urljoin(runtime.get("site_url", "") + "/", "hnr_claim_reward.php")
        session = self._build_session(runtime=runtime, allow_post_retry=False)

        resp = session.get(list_url, timeout=(self._http_timeout, self._http_timeout))
        html = resp.text
        if self._looks_logged_out(html):
            return False, "Cookie 已失效，请更新思齐 Cookie", "request", ""

        rank_match = re.search(r"当前排名：\s*<span[^>]*>\s*(\d+)", html)
        rank = rank_match.group(1) if rank_match else "未知"

        next_time_match = re.search(r"下次领取:\s*([\d\-: ]+)", html)
        if next_time_match:
            return True, f"今日已领取，下次可领取时间：{next_time_match.group(1).strip()}，当前排名 {rank}", "request", ""

        claims = re.findall(r'claimReward\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*(\d+)\s*\)', html)
        if not claims:
            return True, f"今日无可领奖励，当前排名 {rank}", "request", ""

        success_count = 0
        claimed = []
        failed = []
        total_earned = 0

        for reward_type, amount in claims:
            post_resp = session.post(
                claim_url,
                data={"reward_type": reward_type, "amount": amount},
                headers={"Referer": list_url},
                allow_redirects=False,
                timeout=(self._http_timeout, self._http_timeout),
            )
            if post_resp.status_code == 302:
                location = post_resp.headers.get("Location", "")
                if "success=reward_claimed" in location:
                    success_count += 1
                    claimed.append(f"{reward_names.get(reward_type, reward_type)}(+{amount})")
                    total_earned += int(amount)
                else:
                    failed.append(f"{reward_type}(重定向未命中成功标记)")
            elif post_resp.status_code == 200 and ("成功" in post_resp.text or "领取成功" in post_resp.text):
                success_count += 1
                claimed.append(f"{reward_names.get(reward_type, reward_type)}(+{amount})")
                total_earned += int(amount)
            else:
                failed.append(f"{reward_type}(HTTP {post_resp.status_code})")

        if success_count > 0:
            detail = f"成功领取 {success_count} 个奖励"
            if claimed:
                detail += " (" + ", ".join(claimed) + ")"
            if total_earned > 0:
                detail += f"，共获得 {total_earned} 魔力"
            if failed:
                detail += f"；失败: {', '.join(failed)}"
            return True, f"{detail}，当前排名 {rank}", "request", ""

        msg = f"所有奖励领取失败，当前排名 {rank}"
        if failed:
            msg += f"；失败: {', '.join(failed)}"
        return False, msg, "request", ""

    def _run_new_api_checkin(self, task: Dict[str, Any], runtime: Dict[str, Any]) -> Tuple[bool, str, str, str]:
        base_url = (runtime.get("site_url") or "").rstrip("/")
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": base_url,
            "referer": f"{base_url}/console/personal",
            "new-api-user": runtime.get("new_api_uid"),
        }
        session = self._build_session(runtime=runtime, extra_headers=headers, allow_post_retry=True)
        month = self._aware_now().strftime("%Y-%m")

        status_resp = session.get(
            f"{base_url}/api/user/checkin?month={month}",
            timeout=(self._http_timeout, self._http_timeout),
        )
        status_data = self._safe_json(status_resp)
        if not status_data.get("success"):
            msg = status_data.get("message") or f"HTTP {status_resp.status_code}"
            return False, f"查询失败 {msg}", "request", ""

        stats = (status_data.get("data") or {}).get("stats") or {}
        if stats.get("checked_in_today"):
            return True, f"今日已签到 | {self._format_new_api_stats(stats)}", "request", ""

        sign_data = {}
        sign_resp = None
        for attempt in range(1, 4):
            sign_resp = session.post(
                f"{base_url}/api/user/checkin",
                timeout=(self._http_timeout, self._http_timeout),
            )
            sign_data = self._safe_json(sign_resp)
            if sign_data.get("success"):
                break
            if attempt < 3:
                time.sleep(5)

        if not sign_data.get("success"):
            message = sign_data.get("message") or (f"HTTP {sign_resp.status_code}" if sign_resp is not None else "未知错误")
            return False, f"签到失败 {message}", "request", ""

        reward_text = self._format_new_api_money(((sign_data.get("data") or {}).get("quota_awarded") or 0))
        refresh_resp = session.get(
            f"{base_url}/api/user/checkin?month={month}",
            timeout=(self._http_timeout, self._http_timeout),
        )
        refresh_data = self._safe_json(refresh_resp)
        if refresh_data.get("success"):
            stats = (refresh_data.get("data") or {}).get("stats") or stats

        return True, f"签到成功 {reward_text} | {self._format_new_api_stats(stats)}", "request", ""

    def _fetch_page_with_cf(self, task: Dict[str, Any], runtime: Dict[str, Any], url: str) -> Dict[str, Any]:
        mode = task.get("cf_mode") or "auto"
        strategies = {
            "request": ["request"],
            "playwright": ["playwright"],
            "flaresolverr": ["flaresolverr"],
            "auto": ["playwright", "request", "flaresolverr"],
        }.get(mode, ["playwright", "request", "flaresolverr"])

        last_result = {"success": False, "message": "未执行", "method": ""}
        for strategy in strategies:
            if strategy == "flaresolverr" and not self._flaresolverr_url:
                continue
            try:
                if strategy == "playwright":
                    result = self._fetch_page_by_playwright(runtime=runtime, url=url)
                elif strategy == "flaresolverr":
                    result = self._fetch_page_by_flaresolverr(runtime=runtime, url=url)
                else:
                    result = self._fetch_page_by_request(runtime=runtime, url=url)
            except Exception as err:
                result = {
                    "success": False,
                    "message": f"{self.CF_MODE_LABELS.get(strategy, strategy)} 访问异常：{err}",
                    "detail": self._get_error_detail(err),
                    "method": strategy,
                }

            last_result = result
            html = result.get("text") or ""
            if result.get("success") and not self._is_cloudflare_blocked(html, result.get("status_code")):
                return result

        if not last_result.get("message"):
            last_result["message"] = "无法通过站点访问"
        return last_result

    def _fetch_page_by_request(self, runtime: Dict[str, Any], url: str) -> Dict[str, Any]:
        session = self._build_session(runtime=runtime, allow_post_retry=False)
        resp = session.get(url, timeout=(self._http_timeout, self._http_timeout), allow_redirects=True)
        html = resp.text or ""
        if self._is_cloudflare_blocked(html, resp.status_code):
            return {
                "success": False,
                "message": "请求模式命中 Cloudflare",
                "detail": "",
                "method": "request",
                "status_code": resp.status_code,
                "text": html,
            }
        if resp.status_code >= 400:
            return {
                "success": False,
                "message": f"HTTP {resp.status_code}",
                "detail": "",
                "method": "request",
                "status_code": resp.status_code,
                "text": html,
            }
        return {
            "success": True,
            "message": "访问成功",
            "detail": "",
            "method": "request",
            "status_code": resp.status_code,
            "text": html,
        }

    def _fetch_page_by_playwright(self, runtime: Dict[str, Any], url: str) -> Dict[str, Any]:
        html = PlaywrightHelper().get_page_source(
            url=url,
            cookies=runtime.get("cookie"),
            ua=runtime.get("user_agent"),
            proxies=runtime.get("proxy_server"),
        ) or ""
        if not html:
            return {"success": False, "message": "Playwright 返回空页面", "detail": "", "method": "playwright", "status_code": 0, "text": ""}
        if self._is_cloudflare_blocked(html, 200):
            return {
                "success": False,
                "message": "Playwright 仍命中 Cloudflare",
                "detail": "",
                "method": "playwright",
                "status_code": 200,
                "text": html,
            }
        return {
            "success": True,
            "message": "访问成功",
            "detail": "",
            "method": "playwright",
            "status_code": 200,
            "text": html,
        }

    def _fetch_page_by_flaresolverr(self, runtime: Dict[str, Any], url: str) -> Dict[str, Any]:
        endpoint = self._flaresolverr_url
        if not endpoint:
            return {"success": False, "message": "未配置 FlareSolverr 地址", "detail": "", "method": "flaresolverr", "status_code": 0, "text": ""}

        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": max(self._http_timeout, 20) * 1000,
            "headers": {"User-Agent": runtime.get("user_agent") or self.DEFAULT_USER_AGENT},
            "cookies": self._cookie_string_to_flaresolverr(runtime.get("cookie")),
        }
        resp = requests.post(endpoint, json=payload, timeout=(10, max(self._http_timeout, 20)))
        if resp.status_code >= 400:
            return {
                "success": False,
                "message": f"FlareSolverr HTTP {resp.status_code}",
                "detail": "",
                "method": "flaresolverr",
                "status_code": resp.status_code,
                "text": "",
            }
        data = self._safe_json(resp)
        if data.get("status") != "ok":
            return {
                "success": False,
                "message": data.get("message") or "FlareSolverr 返回失败",
                "detail": "",
                "method": "flaresolverr",
                "status_code": resp.status_code,
                "text": "",
            }
        solution = data.get("solution") or {}
        html = solution.get("response") or ""
        if self._is_cloudflare_blocked(html, 200):
            return {
                "success": False,
                "message": "FlareSolverr 仍命中 Cloudflare",
                "detail": "",
                "method": "flaresolverr",
                "status_code": 200,
                "text": html,
            }
        merged_cookie = self._merge_cookie_strings(runtime.get("cookie"), self._flaresolverr_cookies_to_string(solution.get("cookies") or []))
        if merged_cookie:
            runtime["cookie"] = merged_cookie
        return {
            "success": True,
            "message": "访问成功",
            "detail": "",
            "method": "flaresolverr",
            "status_code": 200,
            "text": html,
        }

    def _build_session(
        self,
        runtime: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
        allow_post_retry: bool = False,
    ) -> requests.Session:
        session = requests.Session()
        retry_methods = ["HEAD", "GET", "OPTIONS"]
        if allow_post_retry:
            retry_methods.append("POST")
        retry_strategy = Retry(
            total=self._http_retry_times,
            connect=self._http_retry_times,
            read=self._http_retry_times,
            status=self._http_retry_times,
            backoff_factor=max(0.1, self._http_retry_delay / 1000.0),
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(retry_methods),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.trust_env = bool(runtime.get("use_proxy"))

        headers = {
            "User-Agent": runtime.get("user_agent") or self.DEFAULT_USER_AGENT,
            "Connection": "keep-alive",
        }
        if runtime.get("cookie"):
            headers["Cookie"] = runtime.get("cookie")
        if extra_headers:
            headers.update(extra_headers)
        session.headers.update(headers)

        if runtime.get("proxy_dict"):
            session.proxies.update(runtime.get("proxy_dict"))
        return session

    def _record_results(self, results: List[Dict[str, Any]], reason: str = ""):
        now = self._format_time(self._aware_now())
        self.save_data("last_run", now)

        task_state_map = self.get_data("task_state") or {}
        history = self.get_data("history") or []
        summary = []

        for result in results:
            task_id = result.get("task_id")
            state = task_state_map.get(task_id, {})
            success = bool(result.get("success"))
            recent = list(state.get("recent") or [])
            recent.insert(
                0,
                {
                    "time": result.get("time"),
                    "success": success,
                    "message": result.get("message"),
                    "method": result.get("method"),
                },
            )
            state.update(
                {
                    "last_run": result.get("time"),
                    "last_result": "success" if success else "error",
                    "last_message": result.get("message"),
                    "last_detail": result.get("detail"),
                    "last_method": result.get("method"),
                    "cookie_source": result.get("cookie_source") or state.get("cookie_source") or "",
                    "last_duration_sec": result.get("last_duration_sec") or 0,
                    "success_count": int(state.get("success_count") or 0) + (1 if success else 0),
                    "fail_count": int(state.get("fail_count") or 0) + (0 if success else 1),
                    "recent": recent[:6],
                }
            )
            task_state_map[task_id] = state

            history.insert(
                0,
                {
                    "task_id": result.get("task_id"),
                    "name": result.get("name"),
                    "time": result.get("time"),
                    "success": success,
                    "message": result.get("message"),
                    "method": result.get("method"),
                    "reason": reason,
                },
            )
            summary.append(
                f"[{'成功' if success else '失败'}] {result.get('name')} - {result.get('message')}"
            )

        self.save_data("task_state", task_state_map)
        self.save_data("history", history[:100])
        self.save_data("last_summary", summary[:20])

    def _reregister_plugin(self, reason: str = ""):
        try:
            Scheduler().update_plugin_job(self.__class__.__name__)
            if reason:
                logger.info("%s 已刷新调度：%s", self.plugin_name, reason)
        except Exception as err:
            logger.warning("%s 刷新调度失败：%s", self.plugin_name, err)

    def _get_next_run_time(self) -> Optional[datetime]:
        if not self._enabled or not self._cron:
            return None
        try:
            trigger = CronTrigger.from_crontab(self._cron, timezone=pytz.timezone(settings.TZ))
            return trigger.get_next_fire_time(None, self._aware_now())
        except Exception:
            return None

    def _extract_siqi_sign_info(self, html: str) -> Tuple[str, str, str]:
        sign_count = re.search(r"第\s*<b>\s*(\d+)\s*</b>\s*次签到", html)
        consecutive = re.search(r"连续签到\s*<b>\s*(\d+)\s*</b>\s*天", html)
        gained = re.search(r"本次签到获得\s*<b>\s*(\d+)\s*</b>\s*个魔力值", html)
        return (
            sign_count.group(1) if sign_count else "?",
            consecutive.group(1) if consecutive else "?",
            gained.group(1) if gained else "?",
        )

    def _format_new_api_money(self, raw: Any) -> str:
        value = float(raw or 0) / 500000
        if value.is_integer():
            return f"${int(value)}"
        return f"${value:.2f}".rstrip("0").rstrip(".")

    def _format_new_api_stats(self, stats: Dict[str, Any]) -> str:
        if not stats:
            return "累计签到未知 | 本月未知 | 累计未知"
        total_checkins = stats.get("total_checkins") or stats.get("checkin_count") or "未知"
        total_quota = stats.get("total_quota") or 0
        month_quota = 0
        records = stats.get("records") or []
        if isinstance(records, list):
            month_quota = sum(float(item.get("quota_awarded") or 0) for item in records)
        return f"累计签到{total_checkins}天 | 本月{self._format_new_api_money(month_quota)} | 累计{self._format_new_api_money(total_quota)}"

    def _is_cloudflare_blocked(self, html: str, status_code: Optional[int] = None) -> bool:
        text = html or ""
        try:
            if under_challenge(text):
                return True
        except Exception:
            pass
        lowered = text.lower()
        markers = [
            "cf-browser-verification",
            "checking your browser",
            "just a moment",
            "attention required",
            "cloudflare ray id",
        ]
        if any(marker in lowered for marker in markers):
            return True
        return bool(status_code in [403, 503] and "cloudflare" in lowered)

    def _looks_logged_out(self, html: str) -> bool:
        text = html or ""
        lowered = text.lower()
        if "未登录" in text or "cookie已失效" in text or "cookie 已失效" in text:
            return True
        if ("登录" in text and "注册" in text and "退出" not in text and "登出" not in text):
            return True
        if re.search(r"\blogin\b", lowered) and "logout" not in lowered and "sign out" not in lowered:
            return True
        if re.search(r"\bsign in\b", lowered) and "sign out" not in lowered:
            return True
        return False

    def _match_keywords(self, html: str, pattern_text: str) -> bool:
        if not html or not pattern_text:
            return False
        patterns = [item.strip() for item in re.split(r"[\n|]+", pattern_text) if item.strip()]
        for pattern in patterns:
            try:
                if re.search(pattern, html, re.IGNORECASE):
                    return True
            except re.error:
                if pattern.lower() in html.lower():
                    return True
        return False

    def _cookie_string_to_flaresolverr(self, cookie_str: str) -> List[Dict[str, Any]]:
        cookies = []
        for part in (cookie_str or "").split(";"):
            segment = part.strip()
            if not segment or "=" not in segment:
                continue
            name, value = segment.split("=", 1)
            cookies.append({"name": name.strip(), "value": value.strip()})
        return cookies

    def _flaresolverr_cookies_to_string(self, cookies: List[Dict[str, Any]]) -> str:
        items = []
        for cookie in cookies or []:
            name = (cookie.get("name") or "").strip()
            value = (cookie.get("value") or "").strip()
            if name:
                items.append(f"{name}={value}")
        return "; ".join(items)

    def _merge_cookie_strings(self, base_cookie: str, extra_cookie: str) -> str:
        merged = {}
        for cookie_str in [base_cookie, extra_cookie]:
            for part in (cookie_str or "").split(";"):
                segment = part.strip()
                if not segment or "=" not in segment:
                    continue
                name, value = segment.split("=", 1)
                merged[name.strip()] = value.strip()
        return "; ".join(f"{name}={value}" for name, value in merged.items())

    def _normalize_flaresolverr_url(self, value: Any) -> str:
        url = (value or "").strip()
        if not url:
            return ""
        if not re.search(r"/v1/?$", url):
            url = url.rstrip("/") + "/v1"
        return url

    def _default_target_url(self, task: Dict[str, Any]) -> str:
        base_url = self._normalize_url(task.get("site_url"))
        task_type = task.get("task_type")
        if not base_url:
            return ""
        if task_type in ["request_get", "request_post_form", "request_post_json"]:
            return ""
        if task_type == "siqi_hnr_claim":
            return urljoin(base_url + "/", "hnrview.php")
        if task_type == "new_api_checkin":
            return urljoin(base_url + "/", "console/personal")
        return urljoin(base_url + "/", "attendance.php")

    @staticmethod
    def _parse_request_headers(raw_headers: str) -> Dict[str, str]:
        text = (raw_headers or "").strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("请求头 JSON 必须是对象")
            return {str(key): "" if value is None else str(value) for key, value in parsed.items()}
        except json.JSONDecodeError:
            headers: Dict[str, str] = {}
            for line in re.split(r"[\r\n]+", text):
                segment = line.strip()
                if not segment:
                    continue
                if ":" not in segment:
                    raise ValueError("请求头格式错误，应为 JSON 或每行 Header: Value")
                name, value = segment.split(":", 1)
                headers[name.strip()] = value.strip()
            return headers

    @staticmethod
    def _parse_key_value_payload(raw_payload: str) -> Dict[str, str]:
        text = (raw_payload or "").strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return {str(key): "" if value is None else str(value) for key, value in parsed.items()}
        except json.JSONDecodeError:
            pass

        merged: Dict[str, str] = {}
        normalized = text.replace("\r", "\n").replace("&", "\n")
        for line in normalized.split("\n"):
            segment = line.strip()
            if not segment:
                continue
            if "=" in segment:
                key, value = segment.split("=", 1)
                merged[key.strip()] = value.strip()
        if merged:
            return merged

        return {key: value for key, value in parse_qsl(text, keep_blank_values=True)}

    @staticmethod
    def _parse_json_payload(raw_payload: str) -> Any:
        text = (raw_payload or "").strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            raise ValueError(f"JSON 请求体格式错误：{err}") from err

    @staticmethod
    def _detect_json_success(data: Dict[str, Any]) -> Tuple[Optional[bool], str]:
        message = (
            data.get("message")
            or data.get("msg")
            or data.get("detail")
            or data.get("error")
            or data.get("errMsg")
            or ""
        )
        if data.get("success") is True:
            return True, str(message or "接口返回 success=true")
        if data.get("success") is False:
            return False, str(message or "接口返回 success=false")

        status = str(data.get("status") or "").strip().lower()
        if status in ["ok", "success", "passed"]:
            return True, str(message or f"接口返回 status={status}")
        if status in ["error", "failed", "forbidden"]:
            return False, str(message or f"接口返回 status={status}")

        code = data.get("code")
        if code in [0, 200]:
            return True, str(message or f"接口返回 code={code}")
        if isinstance(code, int) and code >= 400:
            return False, str(message or f"接口返回 code={code}")

        return None, str(message)

    def _guess_site_url(self, value: Any) -> str:
        url = self._normalize_url(value)
        if not url:
            return ""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return f"{parsed.scheme}://{parsed.netloc}"

    def _guess_domain(self, value: Any) -> str:
        url = self._normalize_url(value)
        if not url:
            return ""
        return (urlparse(url).hostname or "").lower()

    def _normalize_url(self, value: Any) -> str:
        url = (value or "").strip()
        if not url:
            return ""
        if not re.match(r"^https?://", url, re.IGNORECASE):
            url = "https://" + url.lstrip("/")
        return url.rstrip("/")

    def _get_site_by_domain(self, domain: str):
        try:
            if not self._siteoper:
                self._siteoper = SiteOper()
            return self._siteoper.get_by_domain(domain)
        except Exception as err:
            logger.warning("%s 获取站点 %s 配置失败：%s", self.plugin_name, domain, err)
            return None

    def _safe_json(self, response: requests.Response) -> Dict[str, Any]:
        try:
            return response.json() if response is not None else {}
        except Exception:
            return {}

    @staticmethod
    def _to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ["1", "true", "yes", "on"]
        return bool(value)

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _mask_cookie(cookie: str) -> str:
        if not cookie:
            return ""
        return cookie if len(cookie) <= 18 else f"{cookie[:10]}...{cookie[-6:]}"

    @staticmethod
    def _get_error_detail(err: Exception) -> str:
        return str(err) or err.__class__.__name__

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    @staticmethod
    def _format_time(value: Optional[datetime]) -> str:
        if not value:
            return ""
        return value.strftime("%Y-%m-%d %H:%M:%S")
