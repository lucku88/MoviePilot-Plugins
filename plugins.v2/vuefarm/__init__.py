import random
import re
import socket
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

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


class VueFarm(_PluginBase):
    plugin_name = "Vue-农场"
    plugin_desc = "收菜、种植、出售、获取执行记录。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f331.png"
    plugin_version = "0.1.9"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "vuefarm_"
    plugin_order = 68
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    DEFAULT_CRON = "*/10 * * * *"
    PRE_REFRESH_SECONDS = 60
    IDLE_REFRESH_SECONDS = 12 * 60 * 60
    MIN_TRIGGER_SECONDS = 5

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _auto_cookie: bool = True
    _enable_sell: bool = True
    _enable_plant: bool = True
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cron: str = DEFAULT_CRON
    _site_domain: str = DEFAULT_SITE_DOMAIN
    _site_url: str = DEFAULT_SITE_URL
    _user_agent: str = DEFAULT_USER_AGENT
    _cookie: str = ""
    _cookie_source: str = "未配置"
    _ocr_api_url: str = "http://ip:8089/api/tr-run/"
    _prefer_seed: str = "西红柿"
    _schedule_buffer_seconds: int = 5
    _random_delay_max_seconds: int = 5
    _http_timeout: int = 12
    _http_retry_times: int = 3
    _http_retry_delay: int = 1500
    _ocr_retry_times: int = 2
    _ready_retry_seconds: int = 60

    _next_run_time: Optional[datetime] = None
    _next_trigger_time: Optional[datetime] = None
    _next_trigger_mode: str = "run"
    _bootstrap_pending: bool = False
    _page_stat_cache: Optional[Dict[str, int]] = None
    _page_stat_cache_at: float = 0.0

    _crop_icon = {
        "萝卜": "🥕",
        "西红柿": "🍅",
        "玉米": "🌽",
        "茄子": "🍆",
        "蘑菇": "🍄",
        "樱桃": "🍒",
    }

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
        self._page_stat_cache = None
        self._page_stat_cache_at = 0.0

        if self._auto_cookie:
            self._sync_cookie_from_site(silent=True)
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
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-农场配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 Vue-农场配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-农场状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新农场数据"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行一次 Vue-农场"},
            {"path": "/harvest-plot", "endpoint": self._harvest_plot_api, "methods": ["POST"], "auth": "bear", "summary": "手动收菜"},
            {"path": "/plant-plot", "endpoint": self._plant_plot_api, "methods": ["POST"], "auth": "bear", "summary": "手动种植"},
            {"path": "/harvest-all", "endpoint": self._harvest_all_api, "methods": ["POST"], "auth": "bear", "summary": "一键收获"},
            {"path": "/plant-empty", "endpoint": self._plant_empty_api, "methods": ["POST"], "auth": "bear", "summary": "一键种植空地"},
            {"path": "/sell-inventory", "endpoint": self._sell_inventory_api, "methods": ["POST"], "auth": "bear", "summary": "售出背包作物"},
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
                job_func = self._bootstrap_worker if self._bootstrap_pending else (
                    self._refresh_worker if self._load_saved_next_trigger_mode() == "refresh" else self._auto_worker
                )
                services.append({
                    "id": "VueFarm_auto",
                    "name": "Vue-农场初始化" if self._bootstrap_pending else "Vue-农场智能调度",
                    "trigger": "date",
                    "func": job_func,
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

            rand_delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if rand_delay:
                logger.info("INFO 随机延迟 %s 秒后执行...", rand_delay)
                time.sleep(rand_delay)

            if not force and self._should_skip_run():
                logger.info("INFO 未到最近收菜时间，跳过本次运行")
                return {"success": True, "message": "未到最近收菜时间，已跳过", "status": self._build_status(auto_refresh=False)}

            session = self._build_session()
            data = self._fetch_state(session)
            if not data or not data.get("success"):
                raise RuntimeError("获取农场数据失败，Cookie 可能失效")

            ready_plots = self._collect_ready_plots(data)
            logger.info("INFO 成熟作物数量：%s", len(ready_plots))

            action_harvest = False
            action_sell = False
            action_plant = False
            sell_success_count = 0
            planted_seed_name = ""
            harvest_failure_detail = ""
            harvest_note_detail = ""
            harvest_success_count = 0
            harvest_snapshot: List[Dict[str, Any]] = []
            sell_snapshot: List[Dict[str, Any]] = []
            sell_income_actual = 0
            plant_snapshot: List[Dict[str, Any]] = []
            plant_cost_actual = 0
            sell_amount_estimate = 0
            plant_cost_estimate = 0
            plant_next_run_fallback = 0

            if ready_plots:
                harvest_result = self._harvest_ready_plots(session, data)
                action_harvest = bool(harvest_result.get("success"))
                harvest_failure_detail = harvest_result.get("detail") or ""
                harvest_note_detail = harvest_result.get("note") or ""
                harvest_success_count = int(harvest_result.get("harvested_count") or 0)
                data = harvest_result.get("data") or self._fetch_state(session)
                if action_harvest:
                    harvest_snapshot = list(harvest_result.get("harvest_items") or [])

            inventory = data.get("inventory") or []
            if self._enable_sell and inventory:
                sell_amount_estimate = sum(
                    int(item.get("quantity") or 0) * int(item.get("unit_reward") or 0)
                    for item in inventory
                )
                logger.info("INFO 开始售出背包作物，共 %s 类...", len(inventory))
                for item in inventory:
                    try:
                        result = self._post_action(session, "sell_inventory", {
                            "seed_id": item.get("seed_id"),
                            "quantity": item.get("quantity"),
                        }, retry_network=False)
                        if not result or result.get("success", True):
                            sell_success_count += 1
                            sell_qty = self._safe_int(item.get("quantity"), 0)
                            sell_income_actual += self._safe_int(
                                (result or {}).get("gain"),
                                sell_qty * self._safe_int(item.get("unit_reward"), 0),
                            )
                            sell_snapshot.append(self._normalize_sell_item(result or {}, item, sell_qty))
                    except Exception as err:
                        logger.warning("sell_inventory failed: %s", err)
                action_sell = sell_success_count > 0
                data = self._fetch_state(session)
                logger.info("INFO 售出完成")

            empty_count = self._count_empty_plots(data)
            logger.info("INFO 空地数量：%s", empty_count)
            if self._enable_plant and empty_count > 0:
                best_seed = self._pick_seed(data)
                if best_seed:
                    logger.info("INFO 准备种植：%s", best_seed.get("name"))
                    try:
                        result = self._post_action(session, "plant_fill_empty", {"seed_id": best_seed.get("id")}, retry_network=False)
                        if result and result.get("success", True):
                            action_plant = True
                            planted_seed_name = best_seed.get("name") or ""
                            plant_snapshot.append(self._normalize_plant_item(result or {}, best_seed, empty_count))
                            plant_cost_actual = self._safe_int(
                                (result or {}).get("total_cost"),
                                int(best_seed.get("cost") or 0) * self._safe_int((result or {}).get("planted"), empty_count),
                            )
                            plant_cost_estimate = int(best_seed.get("cost") or 0) * empty_count
                            plant_next_run_fallback = int(time.time()) + int(best_seed.get("grow_time") or 0)
                            logger.info("INFO 种植完成：%s", best_seed.get("name"))
                        data = self._refetch_state_until(
                            session,
                            predicate=lambda latest: bool(self._compute_next_run(latest)),
                            attempts=3,
                            delay_seconds=1.0,
                            default=data,
                        )
                    except Exception as err:
                        logger.warning("plant_fill_empty failed: %s", err)

            next_run = self._compute_next_run(data)
            if action_plant and plant_next_run_fallback and not next_run:
                next_run = plant_next_run_fallback
            remaining_ready_plots = self._collect_ready_plots(data)
            if remaining_ready_plots:
                retry_at = int(time.time()) + max(30, self._ready_retry_seconds)
                next_run = min(next_run, retry_at) if next_run else retry_at
                logger.warning("INFO 存在成熟作物但本次未收获成功，延后 %s 秒重试", max(30, self._ready_retry_seconds))
                if not harvest_failure_detail:
                    harvest_failure_detail = f"仍有 {len(remaining_ready_plots)} 块成熟田未收获，将稍后重试"
            self._schedule_next_run(next_run, reason)
            log_result = self._parse_logs(data.get("user_logs") or [], run_start, data.get("seeds") or [])
            next_run_text = self._format_ts(next_run) if next_run else "暂无成熟作物"
            msg_lines = self._build_result_lines(
                action_harvest,
                action_sell,
                action_plant,
                harvest_snapshot,
                sell_snapshot,
                plant_snapshot,
                log_result,
                next_run_text,
                harvest_success_count=harvest_success_count,
                sell_success_count=sell_success_count,
                planted_seed_name=planted_seed_name,
                harvest_failure_detail=harvest_failure_detail,
                harvest_note_detail=harvest_note_detail,
                sell_income_actual=sell_income_actual,
                plant_cost_actual=plant_cost_actual,
                sell_amount_fallback=sell_amount_estimate,
                plant_cost_fallback=plant_cost_estimate,
            )
            has_action_lines = any(line.startswith(("✅", "💰", "🧺", "🌱")) for line in msg_lines)
            has_warning_lines = any(line.startswith("⚠️") for line in msg_lines)

            state_record = self._build_state_record(data, next_run, msg_lines)
            farm_status = self._build_ui_state(data, next_run, msg_lines)
            self.save_data("state", state_record)
            self.save_data("farm_status", farm_status)
            self.save_data("last_run", self._format_time(self._aware_now()))

            history_title = "🌱 Vue-农场运行"
            if has_warning_lines and not has_action_lines:
                history_title = "⚠️ Vue-农场异常"
            self._append_history(history_title, msg_lines or ["ℹ️本次无动作"])

            if self._notify and has_action_lines:
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title="【🌱农场报告 】",
                    text=self._build_notify_text(msg_lines),
                )
            elif self._notify and has_warning_lines:
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title="【⚠️农场异常】",
                    text="\n".join(msg_lines),
                )

            return {"success": True, "message": msg_lines[0] if msg_lines else "本次无动作", "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            retry_scheduled = False
            if self._enabled and reason in {"smart", "bootstrap", "onlyonce"}:
                retry_delay = max(30, self._ready_retry_seconds)
                retry_at = int(time.time()) + retry_delay
                try:
                    self._schedule_next_run(retry_at, f"{reason}-error-retry")
                    retry_scheduled = True
                    logger.warning("%s 本次执行异常，已安排 %s 秒后自动重试：%s", self.plugin_name, retry_delay, self._format_ts(retry_at))
                except Exception as schedule_err:
                    logger.warning("%s 异常后补重试失败：%s", self.plugin_name, schedule_err)
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            logger.error("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
            self._append_history("❌ Vue-农场异常", [f"⚠️ {detail}"])
            if self._notify:
                text = f"⚠️ {detail}"
                if retry_scheduled:
                    text += "\n⏰ 已安排稍后自动重试"
                self.post_message(mtype=NotificationType.Plugin, title="【⚠️农场异常】", text=text)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(self._aware_now()), cost_sec)

    def _manual_worker(self):
        return self.run_job(force=True, reason="onlyonce")

    def _auto_worker(self):
        return self.run_job(force=True, reason="smart")

    def _refresh_worker(self):
        if not self._enabled:
            return {"success": False, "message": "插件未启用"}
        try:
            farm_status = self._refresh_state(reason="scheduled-refresh", record_run=False)
            return {"success": True, "message": "农场状态已预刷新", "farm_status": farm_status}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 计划刷新失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _bootstrap_worker(self):
        self._bootstrap_pending = False
        now = self._aware_now()
        if not self._enabled:
            return {"success": False, "message": "插件未启用"}
        try:
            farm_status = self._refresh_state(reason="bootstrap", record_run=False)
            return {"success": True, "message": "已初始化农场状态", "farm_status": farm_status}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 初始化状态失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _refresh_data(self):
        try:
            farm_status = self._refresh_state(reason="manual-refresh", record_run=False)
            return {"success": True, "message": "农场数据已刷新", "farm_status": farm_status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 刷新数据失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

    def _harvest_plot_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_harvest_plot(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "手动收菜完成",
                "lines": result["lines"],
                "farm_status": result["farm_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动收菜失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _plant_plot_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_plant_plot(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "手动种植完成",
                "lines": result["lines"],
                "farm_status": result["farm_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动种植失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _harvest_all_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_harvest_all(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "一键收获完成",
                "lines": result["lines"],
                "farm_status": result["farm_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 一键收获失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _plant_empty_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_plant_empty(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "一键种植完成",
                "lines": result["lines"],
                "farm_status": result["farm_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 一键种植失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _sell_inventory_api(self, payload: Optional[dict] = None):
        try:
            result = self._manual_sell_inventory(payload or {})
            return {
                "success": True,
                "message": result["lines"][0] if result["lines"] else "售出完成",
                "lines": result["lines"],
                "farm_status": result["farm_status"],
                "status": self._build_status(auto_refresh=False),
            }
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 手动售出失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        farm_status = self.get_data("farm_status") or {}
        needs_refresh = (
            not farm_status
            or farm_status.get("schema_version") != self.plugin_version
            or (self._enabled and not self._load_saved_next_trigger())
        )
        if auto_refresh and self._enabled and needs_refresh:
            try:
                farm_status = self._refresh_state(reason="status-init", record_run=False)
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)

        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "site_url": self._site_url,
            "auto_cookie": self._auto_cookie,
            "enable_sell": self._enable_sell,
            "enable_plant": self._enable_plant,
            "cookie_source": self._cookie_source,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(next_trigger) if next_trigger else "",
            "next_trigger_mode": self._load_saved_next_trigger_mode(),
            "last_run": self.get_data("last_run") or "",
            "farm_status": farm_status,
            "history": self._get_clean_history(persist=True)[:10],
            "config": self._get_config(),
        }

    def _get_config(self, include_options: bool = True) -> Dict[str, Any]:
        config = {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "enable_sell": self._enable_sell,
            "enable_plant": self._enable_plant,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cookie": self._cookie,
            "ocr_api_url": self._ocr_api_url,
            "prefer_seed": self._prefer_seed,
            "schedule_buffer_seconds": self._schedule_buffer_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "ocr_retry_times": self._ocr_retry_times,
        }
        if include_options:
            config["seed_options"] = self._get_seed_options()
        return config

    def _save_config(self, config_payload: dict):
        merged = self._default_config()
        merged.update(self._get_config(include_options=False))
        merged.update(config_payload or {})
        self.init_plugin(merged)
        self._update_config()
        self._reregister_plugin("save_config")
        if self._enabled:
            try:
                self._refresh_state(reason="save-config", record_run=False)
            except Exception as err:
                logger.warning("%s 保存配置后刷新失败：%s", self.plugin_name, err)
        return {"success": True, "message": "配置已保存", "config": self._get_config(), "status": self._build_status(auto_refresh=False)}

    def _sync_site_cookie_api(self):
        result = self._sync_cookie_from_site(save_config=True, silent=False)
        if result.get("success") and self._enabled:
            self._reregister_plugin("sync_cookie")
        return {**result, "config": self._get_config(), "status": self._build_status(auto_refresh=False)}

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "auto_cookie": True,
            "enable_sell": True,
            "enable_plant": True,
            "use_proxy": False,
            "force_ipv4": True,
            "cookie": "",
            "ocr_api_url": "http://ip:8089/api/tr-run/",
            "prefer_seed": "西红柿",
            "schedule_buffer_seconds": 5,
            "random_delay_max_seconds": 5,
            "http_timeout": 12,
            "http_retry_times": 3,
            "http_retry_delay": 1500,
            "ocr_retry_times": 2,
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._auto_cookie = self._to_bool(config.get("auto_cookie", True))
        self._enable_sell = self._to_bool(config.get("enable_sell", True))
        self._enable_plant = self._to_bool(config.get("enable_plant", True))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cron = self.DEFAULT_CRON
        self._site_domain = self.DEFAULT_SITE_DOMAIN
        self._cookie = (config.get("cookie") or "").strip()
        self._ocr_api_url = (config.get("ocr_api_url") or "").strip()
        self._prefer_seed = (config.get("prefer_seed") or "西红柿").strip() or "西红柿"
        self._schedule_buffer_seconds = self._safe_int(config.get("schedule_buffer_seconds"), 5)
        self._random_delay_max_seconds = self._safe_int(config.get("random_delay_max_seconds"), 5)
        self._http_timeout = self._safe_int(config.get("http_timeout"), 12)
        self._http_retry_times = max(1, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(200, self._safe_int(config.get("http_retry_delay"), 1500))
        self._ocr_retry_times = max(1, self._safe_int(config.get("ocr_retry_times"), 2))

    def _normalize_seed_name(self, value: Any) -> str:
        text = re.sub(r"\s+", "", str(value or "").strip())
        if not text:
            return ""

        text = re.sub(r"[^\w\u4e00-\u9fff]", "", text)
        lowered = text.lower()
        alias_map = {
            "tomato": "西红柿",
            "corn": "玉米",
            "radish": "萝卜",
            "eggplant": "茄子",
            "mushroom": "蘑菇",
            "cherry": "樱桃",
        }
        if lowered in alias_map:
            return alias_map[lowered]

        for suffix in ("种子", "作物", "果实", "种植", "农作物"):
            if text.endswith(suffix) and len(text) > len(suffix):
                text = text[: -len(suffix)]
                break

        for crop_name in sorted(self._crop_icon.keys(), key=len, reverse=True):
            crop_key = re.sub(r"\s+", "", str(crop_name or "").strip())
            if crop_key and (crop_key in text or text in crop_key):
                return crop_key
        return text

    def _seed_matches_preference(self, seed_name: Any, preference: Any) -> bool:
        seed_key = self._normalize_seed_name(seed_name)
        prefer_key = self._normalize_seed_name(preference)
        return bool(seed_key and prefer_key and seed_key == prefer_key)

    def _update_config(self):
        self.update_config(self._get_config(include_options=False))

    def _refresh_state(self, reason: str = "refresh", record_run: bool = False) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        session = self._build_session()
        data = self._fetch_state(session)
        next_run = self._compute_next_run(data)
        self._schedule_next_run(next_run, reason)
        self.save_data("state", self._build_state_record(data, next_run, []))
        farm_status = self._build_ui_state(data, next_run, [])
        self.save_data("farm_status", farm_status)
        if record_run:
            self.save_data("last_run", self._format_time(self._aware_now()))
        return farm_status

    def _get_seed_options(self) -> List[str]:
        farm_status = self.get_data("farm_status") or {}
        seed_shop = farm_status.get("seed_shop") or []
        options = [seed.get("name") for seed in seed_shop if seed.get("unlocked") and seed.get("name")]
        if options:
            return options
        return list(self._crop_icon.keys())

    def _get_land_slot_meta(self, data: dict, land: dict, idx: int) -> Dict[str, int]:
        plot_slot = data.get("plot_slot") or {}
        effective = plot_slot.get("effective_plot_counts") or {}
        max_counts = plot_slot.get("max_plot_counts") or plot_slot.get("plot_counts") or {}
        user_stats = data.get("user_stats") or {}
        total_harvest = int(user_stats.get("total_harvest") or 0)
        unlocked_count = int(user_stats.get("unlocked_land_count") or 0)
        land_id = int(land.get("id") or 0)
        unlock_need = int(land.get("unlock_harvest") or 0)
        plot_indexes = [
            int(plot.get("plot_index") or 0) + 1
            for plot in (data.get("user_lands") or [])
            if int(plot.get("land_id") or 0) == land_id
        ]
        base_total = int(land.get("plot_count") or 0)
        max_total = int(max_counts.get(str(land_id)) or max_counts.get(land_id) or 0)
        effective_total = int(effective.get(str(land_id)) or effective.get(land_id) or 0)
        planted_max = max(plot_indexes) if plot_indexes else 0
        total_slots = max(10, base_total, max_total, effective_total, planted_max)
        land_unlocked = (
            (idx < unlocked_count and total_harvest >= unlock_need)
            or effective_total > 0
            or planted_max > 0
        )
        available_slots = max(effective_total, planted_max)
        if land_unlocked and available_slots <= 0:
            available_slots = min(total_slots, base_total or total_slots)
        available_slots = min(max(available_slots, 0), total_slots)
        return {
            "land_id": land_id,
            "unlock_need": unlock_need,
            "total_slots": total_slots,
            "available_slots": available_slots,
            "land_unlocked": land_unlocked,
        }

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
            "Referer": f"{self._site_url}/plant_game.php",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        })
        return session

    def _fetch_state(self, session: requests.Session) -> dict:
        response = self._request_with_retry(
            "fetchState",
            lambda: session.get(f"{self._site_url}/plant_game.php?action=fetch", timeout=(self._http_timeout, self._http_timeout)),
        )
        response.raise_for_status()
        data = response.json()
        return self._enrich_state_with_page_stats(session, data)

    def _enrich_state_with_page_stats(self, session: requests.Session, data: dict) -> dict:
        if not isinstance(data, dict):
            return data
        if self._has_stat_key(data, "user_steal_gain", "total_steal_gain", "total_steal", "steal_gain_total", "steal_gain") and self._has_stat_key(
            data,
            "farm_like_total",
            "user_farm_like_total",
            "farm_like_count",
            "farm_likes",
            "like_total",
        ):
            return data

        try:
            page_stats = self._fetch_page_stats(session)
        except Exception as err:
            logger.warning("%s 页面统计兜底失败：%s", self.plugin_name, err)
            return data

        if not page_stats:
            return data

        user_stats = data.setdefault("user_stats", {})
        if "user_bonus" in page_stats and not data.get("user_bonus"):
            data["user_bonus"] = page_stats["user_bonus"]
        if "total_harvest" in page_stats and not user_stats.get("total_harvest"):
            user_stats["total_harvest"] = page_stats["total_harvest"]
        if "user_steal_gain" in page_stats:
            data["user_steal_gain"] = page_stats["user_steal_gain"]
            user_stats["total_steal_gain"] = page_stats["user_steal_gain"]
        if "user_farm_like_total" in page_stats:
            data["user_farm_like_total"] = page_stats["user_farm_like_total"]
            user_stats["farm_like_total"] = page_stats["user_farm_like_total"]
        return data

    def _fetch_page_stats(self, session: requests.Session) -> Dict[str, int]:
        now = time.time()
        if self._page_stat_cache and (now - self._page_stat_cache_at) < 30:
            return dict(self._page_stat_cache)

        response = self._request_with_retry(
            "fetchPageStats",
            lambda: session.get(f"{self._site_url}/plant_game.php", timeout=(self._http_timeout, self._http_timeout)),
        )
        response.raise_for_status()
        stats = self._parse_page_stats(response.text)
        if stats:
            self._page_stat_cache = dict(stats)
            self._page_stat_cache_at = now
        return stats

    def _parse_page_stats(self, html: str) -> Dict[str, int]:
        if not html:
            return {}

        def pick(stat_id: str) -> Optional[int]:
            matched = re.search(rf'id="{re.escape(stat_id)}"[^>]*>\s*([\d,]+)\s*<', html, re.IGNORECASE)
            if not matched:
                return None
            return self._safe_int(str(matched.group(1)).replace(",", ""), 0)

        stats: Dict[str, int] = {}
        mapping = {
            "user-bonus": "user_bonus",
            "user-harvest": "total_harvest",
            "user-steal-gain": "user_steal_gain",
            "user-farm-like-total": "user_farm_like_total",
        }
        for element_id, key in mapping.items():
            value = pick(element_id)
            if value is not None:
                stats[key] = value
        return stats

    def _post_action(self, session: requests.Session, action: str, payload: Optional[dict] = None, retry_network: bool = False) -> dict:
        body = dict(payload or {})
        body["action"] = action

        def run():
            response = session.post(
                f"{self._site_url}/plant_game.php",
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=(self._http_timeout, self._http_timeout),
            )
            response.raise_for_status()
            return response

        response = self._request_with_retry(f"postAction:{action}", run) if retry_network else run()
        return response.json()

    def _request_with_retry(self, label: str, func):
        last_err = None
        for idx in range(1, self._http_retry_times + 1):
            try:
                return func()
            except Exception as err:
                last_err = err
                detail = self._get_error_detail(err)
                if not self._is_retryable_network_error(err) or idx == self._http_retry_times:
                    raise
                wait_ms = self._http_retry_delay * idx + random.randint(0, 500)
                logger.warning("%s %s failed %s/%s: %s", self.plugin_name, label, idx, self._http_retry_times, detail)
                logger.info("%s %s 将在 %.1f 秒后自动重试（%s/%s）", self.plugin_name, label, wait_ms / 1000.0, idx + 1, self._http_retry_times)
                time.sleep(wait_ms / 1000.0)
        raise last_err

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

    def _recognize_captcha(self, session: requests.Session, image_content: bytes) -> str:
        if not self._ocr_api_url:
            raise ValueError("未配置 OCR API 地址")

        best_text = ""
        best_confidence = 0.0
        for idx in range(1, self._ocr_retry_times + 1):
            try:
                response = session.post(self._ocr_api_url, files={"file": ("cap.jpg", image_content, "image/jpeg")}, timeout=(10, 30))
                response.raise_for_status()
                data = response.json()
                raw_lines = ((data or {}).get("data") or {}).get("raw_out") or []
                text = ""
                confidence = 0.0
                for line in raw_lines:
                    if isinstance(line, list) and len(line) >= 2:
                        if isinstance(line[1], str):
                            text += line[1]
                        if len(line) >= 3 and isinstance(line[2], (int, float)):
                            confidence = max(confidence, float(line[2]))
                text = "".join(ch for ch in text.upper() if ch.isalnum())
                if 4 <= len(text) <= 8 and confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
            except Exception as err:
                logger.warning("OCR 第 %s 次尝试异常: %s", idx, err)
        logger.info("INFO OCR 最终结果: %s (置信度: %s)", best_text or "EMPTY", best_confidence)
        return best_text

    def _harvest_all(self, session: requests.Session) -> Dict[str, Any]:
        logger.info("INFO 开始收获...")
        last_detail = "未知原因"
        for idx in range(1, 6):
            logger.info("Harvest attempt %s/5", idx)
            try:
                cap_res = self._post_action(session, "get_harvest_all_captcha", {}, retry_network=True)
                if not cap_res or not cap_res.get("success") or not cap_res.get("captcha"):
                    last_detail = f"验证码接口失败：{(cap_res or {}).get('msg', 'UNKNOWN')}"
                    logger.warning("get_harvest_all_captcha failed: %s", (cap_res or {}).get("msg", "UNKNOWN"))
                    continue

                captcha = cap_res["captcha"]
                image_url = captcha.get("image_url")
                if not image_url:
                    last_detail = "验证码图片地址为空"
                    continue
                image_url = urljoin(f"{self._site_url}/", str(image_url))
                img_response = self._request_with_retry("captchaImage", lambda: session.get(image_url, timeout=(self._http_timeout, self._http_timeout)))
                img_response.raise_for_status()
                code = self._recognize_captcha(session, img_response.content)
                if not code:
                    last_detail = "OCR 未识别出有效验证码"
                    logger.warning("captcha OCR failed, retry...")
                    continue

                harvest_res = self._post_action(session, "harvest_all", {
                    "imagehash": captcha.get("imagehash"),
                    "imagestring": code,
                }, retry_network=False)
                if harvest_res and harvest_res.get("success"):
                    logger.info("Harvest completed")
                    return {
                        "success": True,
                        "detail": "",
                        "reward": self._safe_int(harvest_res.get("reward"), 0),
                        "items": self._normalize_harvest_items(harvest_res.get("inventory")),
                    }
                last_detail = f"提交收菜失败：{(harvest_res or {}).get('msg', 'UNKNOWN')}"
                logger.warning("harvest_all failed: %s", (harvest_res or {}).get("msg", "UNKNOWN"))
                if not (harvest_res or {}).get("captcha_required"):
                    break
            except Exception as err:
                last_detail = self._get_error_detail(err)
                logger.warning("harvest flow failed: %s", err)
        logger.warning("harvest not completed after retries")
        return {"success": False, "detail": last_detail, "reward": 0, "items": []}

    def _collect_ready_plots(self, data: dict) -> List[dict]:
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        now_sec = int(time.time())
        ready_plots: List[dict] = []
        for plot in (data.get("user_lands") or []):
            if not plot.get("seed_id"):
                continue
            seed = seed_map.get(str(plot.get("seed_id"))) or {}
            harvest_ts = self._plot_harvest_time(plot, seed)
            if plot.get("is_ready") == 1 or (harvest_ts and harvest_ts <= now_sec):
                ready_plots.append(plot)
        return ready_plots

    def _refetch_state_until(
        self,
        session: requests.Session,
        predicate=None,
        attempts: int = 3,
        delay_seconds: float = 1.0,
        default: Optional[dict] = None,
    ) -> Optional[dict]:
        latest = default
        total_attempts = max(1, attempts)
        for idx in range(total_attempts):
            try:
                data = self._fetch_state(session)
                latest = data
                if predicate is None or predicate(data):
                    return data
            except Exception as err:
                logger.warning("state refetch %s/%s failed: %s", idx + 1, total_attempts, err)
            if idx < total_attempts - 1:
                time.sleep(max(0.1, delay_seconds))
        return latest

    def _harvest_single_plot(self, session: requests.Session, land_id: int, plot_index: int) -> Dict[str, Any]:
        result = self._post_action(
            session,
            "harvest",
            {"land_id": land_id, "plot_index": plot_index},
            retry_network=False,
        )
        if result and result.get("success", True):
            return {
                "success": True,
                "result": result,
                "items": self._normalize_harvest_items((result or {}).get("inventory"), default_added=1),
            }
        return {"success": False, "detail": (result or {}).get("msg") or "收菜失败", "result": result or {}}

    def _harvest_ready_plots(self, session: requests.Session, data: dict) -> Dict[str, Any]:
        ready_before = self._collect_ready_plots(data)
        if not ready_before:
            return {"success": False, "detail": "当前没有可收获田块", "note": "", "data": data, "harvested_count": 0, "harvest_items": []}

        batch_result = self._harvest_all(session)
        latest_data = self._refetch_state_until(session, attempts=2, delay_seconds=0.6, default=data) or data
        remaining_ready = self._collect_ready_plots(latest_data)
        harvested_items: List[Dict[str, Any]] = list(batch_result.get("items") or [])

        if batch_result.get("success") and not remaining_ready:
            return {
                "success": True,
                "detail": "",
                "note": "",
                "data": latest_data,
                "harvested_count": sum(int(item.get("qty") or 0) for item in harvested_items) or len(ready_before),
                "harvest_items": harvested_items,
            }

        fallback_success = 0
        fallback_failures: List[str] = []
        if remaining_ready:
            for plot in remaining_ready:
                land_id = int(plot.get("land_id") or 0)
                plot_index = int(plot.get("plot_index") or 0)
                try:
                    single_result = self._harvest_single_plot(session, land_id, plot_index)
                    if single_result.get("success"):
                        fallback_success += 1
                        harvested_items.extend(single_result.get("items") or [])
                    else:
                        fallback_failures.append(
                            f"{land_id}-{plot_index + 1}:{single_result.get('detail') or '收菜失败'}"
                        )
                except Exception as err:
                    fallback_failures.append(f"{land_id}-{plot_index + 1}:{self._get_error_detail(err)}")

        latest_data = self._refetch_state_until(session, attempts=2, delay_seconds=0.6, default=latest_data) or latest_data
        remaining_after = self._collect_ready_plots(latest_data)
        harvested_count = max(0, len(ready_before) - len(remaining_after))

        note = ""
        if remaining_ready:
            if batch_result.get("success"):
                note = "已对剩余成熟田执行逐坑位收菜兜底。"
            elif fallback_success > 0:
                note = f"批量收菜失败，已自动切换逐坑位收菜，成功 {fallback_success} 块。"

        detail = ""
        batch_detail = batch_result.get("detail") or ""
        if remaining_after:
            detail = f"仍有 {len(remaining_after)} 块成熟田未收获"
            if fallback_failures:
                detail = f"{detail}；逐坑位失败：{' / '.join(fallback_failures[:3])}"
            elif batch_detail:
                detail = f"{detail}；批量原因：{batch_detail}"
        elif not harvested_count:
            detail = batch_detail or "收菜失败"
            if fallback_failures:
                detail = f"{detail}；逐坑位失败：{' / '.join(fallback_failures[:3])}"

        return {
            "success": harvested_count > 0,
            "detail": detail,
            "note": note,
            "data": latest_data,
            "harvested_count": harvested_count,
            "harvest_items": harvested_items,
        }

    def _should_skip_run(self) -> bool:
        next_run = self._load_saved_next_run()
        if not next_run:
            return False
        return self._aware_now() + timedelta(seconds=max(5, self._schedule_buffer_seconds)) < next_run

    def _get_next_run_for_service(self) -> Optional[datetime]:
        next_trigger = self._load_saved_next_trigger()
        now = self._aware_now()
        if next_trigger:
            return next_trigger if next_trigger > now else now + timedelta(seconds=self.MIN_TRIGGER_SECONDS)
        if self._bootstrap_pending:
            return now + timedelta(seconds=8)
        return None

    def _schedule_next_run(self, next_run_ts: Optional[int], reason: str = ""):
        self._bootstrap_pending = False
        now = self._aware_now()
        if next_run_ts:
            next_run = self._aware_from_timestamp(next_run_ts)
            trigger_run_at = next_run + timedelta(seconds=max(0, self._schedule_buffer_seconds))
            pre_refresh_at = trigger_run_at - timedelta(seconds=self.PRE_REFRESH_SECONDS)
            if pre_refresh_at > now + timedelta(seconds=self.MIN_TRIGGER_SECONDS):
                next_trigger = pre_refresh_at
                trigger_mode = "refresh"
            else:
                next_trigger = trigger_run_at
                if next_trigger < now + timedelta(seconds=self.MIN_TRIGGER_SECONDS):
                    next_trigger = now + timedelta(seconds=self.MIN_TRIGGER_SECONDS)
                trigger_mode = "run"
            self._next_run_time = next_run
            self._next_trigger_time = next_trigger
            self._next_trigger_mode = trigger_mode
            self.save_data("next_run_time", self._format_time(next_run))
            self.save_data("next_trigger_time", self._format_time(next_trigger))
            self.save_data("next_trigger_mode", trigger_mode)
            logger.info("INFO 最近收菜时间：%s", self._format_time(next_run))
            logger.info("INFO 计划触发时间：%s", self._format_time(next_trigger))
        else:
            self._next_run_time = None
            self._next_trigger_time = now + timedelta(seconds=self.IDLE_REFRESH_SECONDS)
            self._next_trigger_mode = "refresh"
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", self._format_time(self._next_trigger_time))
            self.save_data("next_trigger_mode", "refresh")
            logger.info("INFO 当前没有已识别的收菜时间，不注册下一次自动运行")

        if self._enabled:
            self._reregister_plugin(reason or "schedule_next_run")

    def _reregister_plugin(self, reason: str = ""):
        try:
            Scheduler().update_plugin_job(self.__class__.__name__)
            if reason:
                logger.info("%s 已刷新调度：%s", self.plugin_name, reason)
        except Exception as err:
            logger.warning("%s 刷新调度失败：%s", self.plugin_name, err)

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
        raw = self.get_data("next_trigger_mode") or ((self.get_data("state") or {}).get("next_trigger_mode")) or self._next_trigger_mode or "run"
        self._next_trigger_mode = str(raw or "run")
        return self._next_trigger_mode

    def _get_next_run_for_service(self) -> Optional[datetime]:
        next_trigger = self._load_saved_next_trigger()
        now = self._aware_now()
        if next_trigger:
            return next_trigger if next_trigger > now else now + timedelta(seconds=self.MIN_TRIGGER_SECONDS)
        if self._bootstrap_pending:
            return now + timedelta(seconds=8)
        return None

    def _schedule_next_run(self, next_run_ts: Optional[int], reason: str = ""):
        self._bootstrap_pending = False
        now = self._aware_now()
        if next_run_ts:
            next_run = self._aware_from_timestamp(next_run_ts)
            trigger_run_at = next_run + timedelta(seconds=max(0, self._schedule_buffer_seconds))
            pre_refresh_at = trigger_run_at - timedelta(seconds=self.PRE_REFRESH_SECONDS)
            if pre_refresh_at > now + timedelta(seconds=self.MIN_TRIGGER_SECONDS):
                next_trigger = pre_refresh_at
                trigger_mode = "refresh"
            else:
                next_trigger = trigger_run_at
                if next_trigger < now + timedelta(seconds=self.MIN_TRIGGER_SECONDS):
                    next_trigger = now + timedelta(seconds=self.MIN_TRIGGER_SECONDS)
                trigger_mode = "run"
            self._next_run_time = next_run
            self._next_trigger_time = next_trigger
            self._next_trigger_mode = trigger_mode
            self.save_data("next_run_time", self._format_time(next_run))
            self.save_data("next_trigger_time", self._format_time(next_trigger))
            self.save_data("next_trigger_mode", trigger_mode)
            logger.info("INFO 最近收菜时间：%s", self._format_time(next_run))
            logger.info("INFO 计划触发时间：%s (%s)", self._format_time(next_trigger), trigger_mode)
        else:
            self._next_run_time = None
            self._next_trigger_time = now + timedelta(seconds=self.IDLE_REFRESH_SECONDS)
            self._next_trigger_mode = "refresh"
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", self._format_time(self._next_trigger_time))
            self.save_data("next_trigger_mode", "refresh")
            logger.info("INFO 当前没有已识别的收菜时间，%s 小时后自动刷新状态", int(self.IDLE_REFRESH_SECONDS / 3600))

        if self._enabled:
            self._reregister_plugin(reason or "schedule_next_run")

    def _count_empty_plots(self, data: dict) -> int:
        lands = data.get("lands") or []
        user_lands = data.get("user_lands") or []
        empty = 0
        for idx, land in enumerate(lands):
            meta = self._get_land_slot_meta(data, land, idx)
            if not meta.get("land_unlocked"):
                continue
            land_id = int(meta.get("land_id") or 0)
            planted = len([plot for plot in user_lands if int(plot.get("land_id") or 0) == land_id and plot.get("seed_id")])
            empty += max(0, int(meta.get("available_slots") or 0) - planted)
        return empty

    def _pick_seed(self, data: dict) -> Optional[dict]:
        unlocked = self._get_unlocked_seeds(data)
        if not unlocked:
            return None
        preference = str(self._prefer_seed or "").strip()
        for seed in unlocked:
            if self._seed_matches_preference(seed.get("name"), preference):
                self._prefer_seed = str(seed.get("name") or self._prefer_seed).strip() or self._prefer_seed
                logger.info("%s 自动种植命中优先种子：%s", self.plugin_name, self._prefer_seed)
                return seed
        if preference:
            logger.warning(
                "%s 优先种子未匹配成功：%s，可用种子：%s",
                self.plugin_name,
                preference,
                ", ".join(str(seed.get("name") or "") for seed in unlocked) or "无",
            )
        unlocked.sort(key=lambda item: ((float(item.get("base_reward") or 0) - float(item.get("cost") or 0)) / max(float(item.get("grow_time") or 1), 1)), reverse=True)
        return unlocked[0]

    def _get_unlocked_seeds(self, data: dict) -> List[dict]:
        total_harvest = self._get_stat_number(data, "total_harvest")
        return [seed for seed in (data.get("seeds") or []) if total_harvest >= int(seed.get("unlock_harvest") or 0)]

    def _find_slot_context(self, data: dict, land_id: int, slot_index: int) -> Dict[str, Any]:
        lands = data.get("lands") or []
        user_lands = data.get("user_lands") or []
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}

        for idx, land in enumerate(lands):
            current_land_id = int(land.get("id") or 0)
            if current_land_id != land_id:
                continue
            meta = self._get_land_slot_meta(data, land, idx)
            plot = next(
                (
                    item for item in user_lands
                    if int(item.get("land_id") or 0) == land_id
                    and int(item.get("plot_index") or 0) + 1 == slot_index
                    and item.get("seed_id")
                ),
                None,
            )
            seed = seed_map.get(str((plot or {}).get("seed_id"))) or {}
            harvest_ts = self._plot_harvest_time(plot, seed) if plot else 0
            ready = bool(plot and (plot.get("is_ready") == 1 or (harvest_ts and harvest_ts <= int(time.time()))))
            is_open_slot = meta.get("land_unlocked") and slot_index <= int(meta.get("available_slots") or 0)
            return {
                "land": land,
                "land_name": land.get("name") or land.get("land_name") or f"农场 {idx + 1}",
                "land_unlocked": meta.get("land_unlocked"),
                "available_slots": int(meta.get("available_slots") or 0),
                "is_open_slot": is_open_slot,
                "plot": plot,
                "seed": seed,
                "harvest_ts": harvest_ts,
                "ready": ready,
                "empty": bool(is_open_slot and not plot),
            }
        return {}

    def _refresh_and_store_farm_state(self, data: dict, reason: str, summary_lines: Optional[List[str]] = None) -> Dict[str, Any]:
        next_run = self._compute_next_run(data)
        self._schedule_next_run(next_run, reason)
        lines = list(summary_lines or [])
        self.save_data("state", self._build_state_record(data, next_run, lines))
        farm_status = self._build_ui_state(data, next_run, lines)
        self.save_data("farm_status", farm_status)
        self.save_data("last_run", self._format_time(self._aware_now()))
        return farm_status

    def _resolve_seed(self, data: dict, seed_id: Any = None, seed_name: str = "") -> Optional[dict]:
        unlocked = self._get_unlocked_seeds(data)
        if seed_id:
            for seed in unlocked:
                if int(seed.get("id") or 0) == int(seed_id):
                    return seed
        if seed_name:
            for seed in unlocked:
                if self._seed_matches_preference(seed.get("name"), seed_name):
                    return seed
        return self._pick_seed(data)

    def _manual_harvest_plot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        land_id = self._safe_int(payload.get("land_id"), 0)
        slot_index = self._safe_int(payload.get("slot_index"), 0)
        if land_id <= 0 or slot_index <= 0:
            raise ValueError("田块参数不完整")

        session = self._build_session()
        data = self._fetch_state(session)
        slot = self._find_slot_context(data, land_id, slot_index)
        if not slot:
            raise ValueError("未找到指定田块")
        if not slot.get("plot"):
            raise ValueError("这块田当前没有作物")
        if not slot.get("ready"):
            raise ValueError("这块田还没成熟")

        result = self._harvest_single_plot(session, land_id, slot_index - 1)
        if not result.get("success"):
            raise ValueError(result.get("detail") or "收菜失败")

        data = self._fetch_state(session)
        inventory = (result.get("result") or {}).get("inventory") or {}
        reward = self._safe_int((result.get("result") or {}).get("reward"), 0)
        seed_name = inventory.get("name") or (slot.get("seed") or {}).get("name") or "作物"
        seed_icon = inventory.get("icon") or self._crop_icon.get(seed_name, "🌱")
        lines = [
            f"✅ 收菜：{seed_icon}{seed_name} -> {slot.get('land_name')} #{slot_index}",
        ]
        if reward > 0:
            lines.append(f"💰 获得：{reward} 魔力")
        farm_status = self._refresh_and_store_farm_state(data, "manual-plot-harvest", lines)
        self._append_history("🖱️ 手动收菜", lines)
        return {"farm_status": farm_status, "lines": lines}

    def _manual_plant_plot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
        land_id = self._safe_int(payload.get("land_id"), 0)
        slot_index = self._safe_int(payload.get("slot_index"), 0)
        seed_id = self._safe_int(payload.get("seed_id"), 0)
        if land_id <= 0 or slot_index <= 0:
            raise ValueError("田块参数不完整")

        session = self._build_session()
        data = self._fetch_state(session)
        slot = self._find_slot_context(data, land_id, slot_index)
        if not slot:
            raise ValueError("未找到指定田块")
        if not slot.get("land_unlocked"):
            raise ValueError("这块田还未解锁")
        if not slot.get("empty"):
            raise ValueError("这块田当前不可种植")

        seed = self._resolve_seed(data, seed_id=seed_id)
        if not seed:
            raise ValueError("未找到可用种子")

        result = self._post_action(
            session,
            "plant",
            {
                "land_id": land_id,
                "plot_index": slot_index - 1,
                "seed_id": seed.get("id"),
            },
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(result.get("msg") or "种植失败")

        data = self._refetch_state_until(
            session,
            predicate=lambda latest: bool(self._compute_next_run(latest)),
            attempts=3,
            delay_seconds=1.0,
            default=data,
        ) or data
        lines = [
            f"🌱 手动种植：{self._crop_icon.get(seed.get('name'), '🌱')}{seed.get('name')} -> {slot.get('land_name')} #{slot_index}",
        ]
        farm_status = self._refresh_and_store_farm_state(data, "manual-plot-plant", lines)
        self._append_history("🖱️ 手动种植", lines)
        return {"farm_status": farm_status, "lines": lines}

    def _manual_harvest_all(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

        session = self._build_session()
        data = self._fetch_state(session)
        ready_plots = self._collect_ready_plots(data)
        if not ready_plots:
            raise ValueError("当前没有可收获田块")

        result = self._harvest_ready_plots(session, data)
        if not result.get("success"):
            raise ValueError(result.get("detail") or "收菜失败")

        data = result.get("data") or self._fetch_state(session)
        processed_count = int(result.get("harvested_count") or len(ready_plots))
        lines = [f"✅ 一键收获：已处理 {processed_count} 块成熟田"]
        if result.get("note"):
            lines.append(f"ℹ️ {result.get('note')}")
        if result.get("detail"):
            lines.append(f"⚠️ {result.get('detail')}")
        farm_status = self._refresh_and_store_farm_state(data, "manual-harvest-all", lines)
        self._append_history("🧺 一键收获", lines)
        return {"farm_status": farm_status, "lines": lines}

    def _manual_plant_empty(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

        seed_id = self._safe_int(payload.get("seed_id"), 0)
        session = self._build_session()
        data = self._fetch_state(session)
        empty_count = self._count_empty_plots(data)
        if empty_count <= 0:
            raise ValueError("当前没有可种植空地")

        seed = self._resolve_seed(data, seed_id=seed_id)
        if not seed:
            raise ValueError("未找到可用种子")

        result = self._post_action(session, "plant_fill_empty", {"seed_id": seed.get("id")}, retry_network=False)
        if result and not result.get("success", True):
            raise ValueError(result.get("msg") or "种植失败")

        data = self._refetch_state_until(
            session,
            predicate=lambda latest: bool(self._compute_next_run(latest)),
            attempts=3,
            delay_seconds=1.0,
            default=data,
        ) or data
        planted_count = self._safe_int((result or {}).get("planted"), empty_count)
        lines = [
            f"🌱 一键种植：{self._crop_icon.get(seed.get('name'), '🌱')}{seed.get('name')} ×{planted_count}",
        ]
        farm_status = self._refresh_and_store_farm_state(data, "manual-plant-empty", lines)
        self._append_history("🌱 一键种植", lines)
        return {"farm_status": farm_status, "lines": lines}

    def _manual_sell_inventory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_cookie()
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

        seed_id = self._safe_int(payload.get("seed_id"), 0)
        quantity = self._safe_int(payload.get("quantity"), 0)
        if seed_id <= 0 or quantity <= 0:
            raise ValueError("售出参数不完整")

        session = self._build_session()
        data = self._fetch_state(session)
        inventory_item = next(
            (
                item for item in (data.get("inventory") or [])
                if int(item.get("seed_id") or 0) == seed_id and int(item.get("quantity") or 0) > 0
            ),
            None,
        )
        if not inventory_item:
            raise ValueError("背包中没有该作物")

        available_quantity = int(inventory_item.get("quantity") or 0)
        sell_quantity = min(max(1, quantity), available_quantity)
        result = self._post_action(
            session,
            "sell_inventory",
            {"seed_id": seed_id, "quantity": sell_quantity},
            retry_network=False,
        )
        if result and not result.get("success", True):
            raise ValueError(result.get("msg") or "售出失败")

        inventory = result.get("inventory") or {}
        seed_name = inventory.get("name") or inventory_item.get("name") or "作物"
        seed_icon = inventory.get("icon") or self._crop_icon.get(seed_name, "🌱")
        gain = self._safe_int(result.get("gain"), sell_quantity * self._safe_int(inventory_item.get("unit_reward"), 0))
        data = self._refetch_state_until(session, attempts=2, delay_seconds=0.5, default=data) or data
        lines = [
            f"🧺 售出：{seed_icon}{seed_name}×{sell_quantity}",
            f"💰 获得：{gain} 魔力",
        ]
        farm_status = self._refresh_and_store_farm_state(data, "manual-sell-inventory", lines)
        self._append_history("🧺 手动售出", lines)
        return {"farm_status": farm_status, "lines": lines}

    def _compute_next_run(self, data: dict) -> Optional[int]:
        now = int(time.time())
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        future_times: List[int] = []
        for plot in (data.get("user_lands") or []):
            if not plot.get("seed_id"):
                continue
            seed = seed_map.get(str(plot.get("seed_id")))
            plant_time = int(plot.get("plant_time") or 0)
            grow_time = int((seed or {}).get("grow_time") or 0)
            harvest_ts = int(plot.get("harvest_time") or 0) or (plant_time + grow_time if plant_time and grow_time else 0)
            if harvest_ts > now:
                future_times.append(harvest_ts)
        return min(future_times) if future_times else None

    def _build_state_record(self, data: dict, next_run: Optional[int], summary_lines: List[str]) -> dict:
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        total_harvest = self._get_stat_number(data, "total_harvest")
        total_steal_gain = self._get_stat_number(
            data,
            "total_steal_gain",
            "user_steal_gain",
            "total_steal",
            "steal_gain_total",
            "steal_gain",
        )
        farm_like_total = self._get_stat_number(
            data,
            "farm_like_total",
            "user_farm_like_total",
            "farm_like_count",
            "farm_likes",
            "like_total",
        )
        return {
            "time": self._format_time(self._aware_now()),
            "next_run_ts": int(next_run or 0),
            "next_run_time": self._format_ts(next_run) if next_run else "",
            "next_trigger_ts": int(self._next_trigger_time.timestamp()) if self._next_trigger_time else 0,
            "next_trigger_mode": self._next_trigger_mode,
            "next_trigger_time": self._format_time(self._next_trigger_time) if self._next_trigger_time else "",
            "summary": summary_lines,
            "user": {
                "bonus": data.get("user_bonus"),
                "total_harvest": total_harvest,
                "total_steal": total_steal_gain,
                "farm_likes": farm_like_total,
            },
            "plots": [
                {
                    "land_id": int(plot.get("land_id") or 0),
                    "plot_index": int(plot.get("plot_index") or 0) + 1,
                    "seed_name": (seed_map.get(str(plot.get("seed_id"))) or {}).get("name"),
                    "ready": plot.get("is_ready") == 1,
                }
                for plot in (data.get("user_lands") or [])
            ],
            "inventory": [
                {"name": item.get("name"), "quantity": int(item.get("quantity") or 0), "unit_reward": int(item.get("unit_reward") or 0)}
                for item in (data.get("inventory") or [])
            ],
            "logs": [
                {"action": log.get("action"), "seed": log.get("seed_name"), "land": log.get("land_name"), "time": log.get("created_at"), "value": log.get("value")}
                for log in (data.get("user_logs") or [])[:20]
            ],
        }

    def _build_ui_state(self, data: dict, next_run: Optional[int], summary_lines: List[str]) -> Dict[str, Any]:
        user_stats = data.get("user_stats") or {}
        total_harvest = self._get_stat_number(data, "total_harvest")
        total_steal_gain = self._get_stat_number(
            data,
            "total_steal_gain",
            "user_steal_gain",
            "total_steal",
            "steal_gain_total",
            "steal_gain",
        )
        farm_like_total = self._get_stat_number(
            data,
            "farm_like_total",
            "user_farm_like_total",
            "farm_like_count",
            "farm_likes",
            "like_total",
        )
        unlocked_land_count = self._get_stat_number(data, "unlocked_land_count")
        ready_count = len(self._collect_ready_plots(data))
        empty_count = self._count_empty_plots(data)
        growing_count = max(0, len(data.get("user_lands") or []) - ready_count)
        return {
            "title": "种菜赚魔力",
            "schema_version": self.plugin_version,
            "last_updated": self._format_time(self._aware_now()),
            "summary": summary_lines,
            "next_run_ts": int(next_run or 0),
            "next_run_time": self._format_ts(next_run) if next_run else "暂无成熟作物",
            "next_trigger_ts": int(self._next_trigger_time.timestamp()) if self._next_trigger_time else 0,
            "next_trigger_time": self._format_time(self._next_trigger_time) if self._next_trigger_time else "等待下一次运行",
            "cookie_source": self._cookie_source,
            "page_note": "状态页仅展示当前农场信息。插件会先动态识别最近可收时间并记录下一次运行；如果当前还没有可收时间，会自动运行一次获取农场信息。",
            "overview": [
                {"label": "魔力值", "value": int(data.get("user_bonus") or 0), "accent": "amber"},
                {"label": "总种植收获", "value": total_harvest, "accent": "cyan"},
                {"label": "总偷菜收益", "value": total_steal_gain, "accent": "green"},
                {"label": "农场被点赞", "value": farm_like_total, "accent": "indigo"},
            ],
            "highlights": {
                "ready_count": ready_count,
                "growing_count": growing_count,
                "empty_count": empty_count,
                "land_count": unlocked_land_count,
            },
            "inventory": self._build_inventory_cards(data.get("inventory") or []),
            "seed_shop": self._build_seed_shop(data),
            "land_groups": self._build_land_groups(data),
            "history": self._get_clean_history(persist=True)[:10],
        }

    def _build_inventory_cards(self, inventory: List[dict]) -> Dict[str, Any]:
        cards = []
        for item in inventory:
            seed_id = int(item.get("seed_id") or 0)
            quantity = int(item.get("quantity") or 0)
            unit_reward = int(item.get("unit_reward") or 0)
            base_unit_reward = int(item.get("base_unit_reward") or unit_reward or 0)
            name = item.get("name") or "未知作物"
            sell_bonus_percent = 0
            if base_unit_reward > 0:
                sell_bonus_percent = round((unit_reward - base_unit_reward) * 100 / base_unit_reward)
            cards.append({
                "seed_id": seed_id,
                "name": name,
                "icon": self._crop_icon.get(name, "🌱"),
                "quantity": quantity,
                "base_unit_reward": base_unit_reward,
                "unit_reward": unit_reward,
                "sell_bonus_percent": sell_bonus_percent,
            })
        return {"empty": not cards, "items": cards, "empty_text": "背包空空如也，快去收菜吧。"}

    def _build_seed_shop(self, data: dict) -> List[Dict[str, Any]]:
        total_harvest = self._get_stat_number(data, "total_harvest")
        cards = []
        for seed in sorted(data.get("seeds") or [], key=lambda item: int(item.get("unlock_harvest") or 0)):
            grow_time = int(seed.get("grow_time") or 0)
            unlock_need = int(seed.get("unlock_harvest") or 0)
            name = seed.get("name") or "未知种子"
            cards.append({
                "id": int(seed.get("id") or 0),
                "name": name,
                "icon": self._crop_icon.get(name, "🌱"),
                "cost": int(seed.get("cost") or 0),
                "reward": int(seed.get("base_reward") or 0),
                "grow_text": self._format_duration(grow_time),
                "unlock_text": f"解锁：总收获 {unlock_need}",
                "unlocked": total_harvest >= unlock_need,
                "preferred": self._seed_matches_preference(name, self._prefer_seed),
            })
        return cards

    def _build_land_groups(self, data: dict) -> List[Dict[str, Any]]:
        lands = data.get("lands") or []
        user_lands = data.get("user_lands") or []
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        groups: List[Dict[str, Any]] = []

        for idx, land in enumerate(lands):
            meta = self._get_land_slot_meta(data, land, idx)
            land_id = int(meta.get("land_id") or 0)
            total_slots = int(meta.get("total_slots") or 0)
            unlock_need = int(meta.get("unlock_need") or 0)
            land_unlocked = bool(meta.get("land_unlocked"))
            available_slots = int(meta.get("available_slots") or 0)
            land_name = land.get("name") or land.get("land_name") or f"农场 {idx + 1}"
            plot_map = {
                int(plot.get("plot_index") or 0) + 1: plot
                for plot in user_lands
                if int(plot.get("land_id") or 0) == land_id and plot.get("seed_id")
            }
            slots: List[Dict[str, Any]] = []
            for slot_index in range(1, total_slots + 1):
                if not land_unlocked:
                    slots.append({
                        "land_id": land_id,
                        "land_name": land_name,
                        "slot_index": slot_index,
                        "state": "locked",
                        "title": "未解锁",
                        "icon": "🔒",
                        "badge": "未解锁",
                        "description": f"总收获达到 {unlock_need} 后解锁",
                        "remaining_label": "",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })
                    continue

                plot = plot_map.get(slot_index)
                if plot:
                    seed = seed_map.get(str(plot.get("seed_id"))) or {}
                    harvest_ts = self._plot_harvest_time(plot, seed)
                    ready = plot.get("is_ready") == 1 or (harvest_ts and harvest_ts <= int(time.time()))
                    slots.append({
                        "land_id": land_id,
                        "land_name": land_name,
                        "slot_index": slot_index,
                        "state": "ready" if ready else "growing",
                        "title": seed.get("name") or "已种植",
                        "icon": self._crop_icon.get(seed.get("name"), "🌱"),
                        "badge": "可收获" if ready else "成长中",
                        "description": f"收获 +{int(seed.get('base_reward') or 0)} 魔力",
                        "remaining_label": "现在可收" if ready else self._format_duration(max(0, harvest_ts - int(time.time()))),
                        "reward_text": f"成长 {self._format_duration(int(seed.get('grow_time') or 0))}",
                        "harvest_ts": harvest_ts,
                    })
                elif slot_index <= available_slots:
                    slots.append({
                        "land_id": land_id,
                        "land_name": land_name,
                        "slot_index": slot_index,
                        "state": "empty",
                        "title": "空地",
                        "icon": "➕",
                        "badge": "可种植",
                        "description": f"优先种子：{self._prefer_seed}",
                        "remaining_label": "等待种植",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })
                elif slot_index == available_slots + 1 and land_unlocked:
                    expand_cost = land.get("next_plot_cost") or land.get("plot_price") or "待站点开放"
                    slots.append({
                        "land_id": land_id,
                        "land_name": land_name,
                        "slot_index": slot_index,
                        "state": "locked",
                        "title": "未解锁",
                        "icon": "🔒",
                        "badge": "未解锁",
                        "description": f"购买 {expand_cost}",
                        "remaining_label": "",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })
                else:
                    slots.append({
                        "land_id": land_id,
                        "land_name": land_name,
                        "slot_index": slot_index,
                        "state": "locked",
                        "title": "未解锁",
                        "icon": "🔒",
                        "badge": "未解锁",
                        "description": "",
                        "remaining_label": "",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })

            groups.append({
                "id": land_id,
                "name": land_name,
                "subtitle": f"坑位：{min(available_slots, total_slots)}/{total_slots}" if land_unlocked else f"解锁条件：总收获 {unlock_need}",
                "slots": slots,
            })
        return groups

    def _plot_harvest_time(self, plot: dict, seed: dict) -> int:
        harvest_ts = int(plot.get("harvest_time") or 0)
        if harvest_ts:
            return harvest_ts
        plant_time = int(plot.get("plant_time") or 0)
        grow_time = int(seed.get("grow_time") or 0)
        if plant_time and grow_time:
            return plant_time + grow_time
        return 0

    def _build_result_lines(
        self,
        action_harvest: bool,
        action_sell: bool,
        action_plant: bool,
        harvest_snapshot: List[dict],
        sell_snapshot: List[dict],
        plant_snapshot: List[dict],
        log_result: dict,
        next_run_text: str,
        harvest_success_count: int = 0,
        sell_success_count: int = 0,
        planted_seed_name: str = "",
        harvest_failure_detail: str = "",
        harvest_note_detail: str = "",
        sell_income_actual: int = 0,
        plant_cost_actual: int = 0,
        sell_amount_fallback: int = 0,
        plant_cost_fallback: int = 0,
    ) -> List[str]:
        def join_summary(summary_map: dict) -> str:
            return "  ".join([f"{key}×{value}" for key, value in summary_map.items()])

        harvest_map: Dict[str, int] = {}
        for item in harvest_snapshot:
            key = f"{item.get('icon', '')}{item.get('name', '')}"
            harvest_map[key] = harvest_map.get(key, 0) + int(item.get("qty") or 0)

        sell_map: Dict[str, int] = {}
        for item in sell_snapshot:
            key = f"{item.get('icon', '')}{item.get('name', '')}"
            sell_map[key] = sell_map.get(key, 0) + int(item.get("qty") or 0)

        plant_map: Dict[str, int] = {}
        for item in plant_snapshot:
            key = f"{item.get('icon', '')}{item.get('name', '')}"
            plant_map[key] = plant_map.get(key, 0) + int(item.get("qty") or 0)

        sell_income = int(sell_income_actual or 0) or int(log_result.get("sell_income") or 0) or int(sell_amount_fallback or 0)
        plant_cost = int(plant_cost_actual or 0) or int(log_result.get("plant_cost") or 0) or int(plant_cost_fallback or 0)

        lines: List[str] = []
        if action_harvest and harvest_map:
            lines.append(f"✅收菜：{join_summary(harvest_map)}")
        elif action_harvest and log_result.get("harvest"):
            lines.append(f"✅收菜：{join_summary(log_result.get('harvest'))}")
        elif action_harvest and harvest_success_count > 0:
            lines.append(f"✅收菜：已处理 {harvest_success_count} 块成熟田")
        if action_sell and sell_map:
            lines.append(f"🧺售出：{join_summary(sell_map)}")
        elif action_sell and log_result.get("sell"):
            lines.append(f"🧺售出：{join_summary(log_result.get('sell'))}")
        elif action_sell and sell_success_count > 0:
            lines.append(f"🧺售出：已处理 {sell_success_count} 类作物")
        if action_plant and plant_map:
            lines.append(f"🌱种植：{join_summary(plant_map)}")
        elif action_plant and log_result.get("plant"):
            lines.append(f"🌱种植：{join_summary(log_result.get('plant'))}")
        elif action_plant and planted_seed_name:
            lines.append(f"🌱种植：{planted_seed_name}")
        if action_sell or action_plant:
            lines.append(f"💰收益：{sell_income - plant_cost} 魔力")
        if harvest_note_detail:
            lines.append(f"ℹ️{harvest_note_detail}")
        if harvest_failure_detail:
            lines.append(f"⚠️收菜失败：{harvest_failure_detail}")
        if not lines:
            lines.append("ℹ️本次没有可执行动作")
        lines.append(f"⏰下次可收：{next_run_text}")
        return lines

    def _normalize_harvest_items(self, inventory: Any, default_added: int = 0) -> List[Dict[str, Any]]:
        if not inventory:
            return []
        items = inventory if isinstance(inventory, list) else [inventory]
        normalized: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "作物")
            added = self._safe_int(item.get("added"), 0)
            if added <= 0:
                added = self._safe_int(item.get("quantity"), 0) or default_added or 1
            normalized.append({
                "name": name,
                "qty": added,
                "unit": self._safe_int(item.get("unit_reward"), 0),
                "icon": item.get("icon") or self._crop_icon.get(name, "🌱"),
            })
        return normalized

    def _normalize_sell_item(self, result: Dict[str, Any], fallback_item: Dict[str, Any], sold_quantity: int) -> Dict[str, Any]:
        inventory = (result or {}).get("inventory") or {}
        name = inventory.get("name") or fallback_item.get("name") or "作物"
        return {
            "name": name,
            "qty": max(1, self._safe_int(sold_quantity, 1)),
            "unit": self._safe_int(inventory.get("unit_reward"), self._safe_int(fallback_item.get("unit_reward"), 0)),
            "icon": inventory.get("icon") or fallback_item.get("icon") or self._crop_icon.get(name, "🌱"),
        }

    def _normalize_plant_item(self, result: Dict[str, Any], fallback_seed: Dict[str, Any], default_planted: int = 0) -> Dict[str, Any]:
        name = str(fallback_seed.get("name") or "作物")
        planted = self._safe_int((result or {}).get("planted"), 0) or max(1, default_planted or 1)
        return {
            "name": name,
            "qty": planted,
            "unit": self._safe_int(fallback_seed.get("cost"), 0),
            "icon": fallback_seed.get("icon") or self._crop_icon.get(name, "🌱"),
        }

    @staticmethod
    def _build_notify_text(lines: List[str]) -> str:
        action_lines = [line for line in lines if line.startswith(("✅", "🧺", "🌱", "💰"))]
        time_line = next((line for line in lines if line.startswith("⏰")), "")
        chunks = ["━━━━━━━━━━━━━━"]
        if action_lines:
            chunks.extend(action_lines)
            chunks.append("━━━━━━━━━━━━━━")
        if time_line:
            chunks.append(time_line.replace("⏰下次可收：", "⏰ 下次运行：", 1))
            chunks.append("━━━━━━━━━━━━━━")
        return "\n".join(chunks)

    def _normalize_history_line(self, line: str) -> str:
        text = str(line or "").strip()
        replacements = [
            ("✅ 手动收菜：", "✅收菜："),
            ("✅ 一键收获：", "✅收菜："),
            ("✅ 收菜：", "✅收菜："),
            ("✅收菜：", "✅收菜："),
            ("🧺 手动售出：", "🧺售出："),
            ("🧺 售出：", "🧺售出："),
            ("🧺售出：", "🧺售出："),
            ("🌱 手动种植：", "🌱种植："),
            ("🌱 一键种植：", "🌱种植："),
            ("🌱 种植：", "🌱种植："),
            ("🌱种植：", "🌱种植："),
            ("💰 手动收益：", "💰收益："),
            ("💰 获得：", "💰收益："),
            ("💰 收益：", "💰收益："),
            ("💰收益：", "💰收益："),
            ("⚠️ 手动收菜失败：", "⚠️收菜失败："),
            ("⚠️ 收菜失败：", "⚠️收菜失败："),
            ("⚠️收菜失败：", "⚠️收菜失败："),
            ("ℹ️ 手动无动作", "ℹ️本次无动作"),
            ("ℹ️ 本次没有可执行动作", "ℹ️本次无动作"),
            ("ℹ️本次没有可执行动作", "ℹ️本次无动作"),
        ]
        for src, dest in replacements:
            if text.startswith(src):
                return text.replace(src, dest, 1)
        return text

    @staticmethod
    def _is_report_history_title(title: str) -> bool:
        compact = re.sub(r"\s+", "", str(title or ""))
        return compact in {
            "🌱Vue-农场运行",
            "⚠️Vue-农场异常",
            "❌Vue-农场异常",
            "【🌱Vue-农场】任务报告",
            "【🌱农场报告】",
            "【⚠️农场异常】",
        }

    def _normalize_history_entry(self, title: str, lines: List[str]) -> Tuple[str, List[str]]:
        history_title = self._normalize_history_line(title)
        history_lines = [normalized for normalized in (self._normalize_history_line(line) for line in (lines or [])) if normalized]

        if self._is_report_history_title(history_title):
            if not history_lines:
                return "", []
            return history_lines[0], history_lines[1:]

        return history_title, history_lines

    def _get_clean_history(self, persist: bool = False) -> List[Dict[str, Any]]:
        raw_history = list(self.get_data("history") or [])
        cleaned_history: List[Dict[str, Any]] = []
        changed = False
        for item in raw_history:
            if not isinstance(item, dict):
                changed = True
                continue

            raw_title = str(item.get("title") or "").strip()
            raw_lines = [str(line or "").strip() for line in (item.get("lines") or []) if str(line or "").strip()]
            title, lines = self._normalize_history_entry(raw_title, raw_lines)
            if title != raw_title or lines != raw_lines:
                changed = True
            if not title and not lines:
                changed = True
                continue

            normalized_item = dict(item)
            normalized_item["title"] = title
            normalized_item["lines"] = lines
            cleaned_history.append(normalized_item)

        cleaned_history = cleaned_history[:20]
        if persist and (changed or len(cleaned_history) != len(raw_history[:20])):
            self.save_data("history", cleaned_history)
        return cleaned_history

    def _append_history(self, title: str, lines: List[str]):
        history = self._get_clean_history()
        history_title, history_lines = self._normalize_history_entry(title, lines)
        history.insert(0, {"time": self._format_time(self._aware_now()), "title": history_title, "lines": history_lines})
        self.save_data("history", history[:20])

    def _parse_logs(self, logs: List[dict], since_time: float, seeds: Optional[List[dict]] = None) -> dict:
        seed_cost_map = {str(seed.get("name") or ""): int(seed.get("cost") or 0) for seed in (seeds or [])}
        result = {"harvest": {}, "sell": {}, "plant": {}, "harvest_income": 0, "sell_income": 0, "plant_cost": 0}
        for item in logs:
            created_at = item.get("created_at")
            if not created_at:
                continue
            try:
                log_time = datetime.strptime(created_at.replace("/", "-"), "%Y-%m-%d %H:%M:%S").timestamp()
            except Exception:
                continue
            if log_time < since_time:
                continue
            icon = item.get("seed_icon") or self._crop_icon.get(item.get("seed_name"), "")
            name = item.get("seed_name") or ""
            qty = int(item.get("quantity") or 1)
            key = f"{icon}{name}"
            if item.get("action") == "harvest":
                result["harvest"][key] = result["harvest"].get(key, 0) + qty
                result["harvest_income"] += int(item.get("value") or 0)
            elif item.get("action") == "sell":
                result["sell"][key] = result["sell"].get(key, 0) + qty
                result["sell_income"] += int(item.get("value") or 0)
            elif item.get("action") == "plant":
                result["plant"][key] = result["plant"].get(key, 0) + qty
                result["plant_cost"] += qty * seed_cost_map.get(name, 0)
        return result

    def _get_stat_number(self, data: dict, *keys: str) -> int:
        sources = [
            data.get("user_stats") or {},
            data.get("user") or {},
            data.get("profile") or {},
            data,
        ]
        for key in keys:
            for source in sources:
                if isinstance(source, dict) and key in source and source.get(key) is not None:
                    return self._safe_int(source.get(key), 0)
        return 0

    def _has_stat_key(self, data: dict, *keys: str) -> bool:
        sources = [
            data.get("user_stats") or {},
            data.get("user") or {},
            data.get("profile") or {},
            data,
        ]
        for key in keys:
            for source in sources:
                if isinstance(source, dict) and key in source and source.get(key) is not None:
                    return True
        return False

    @staticmethod
    def _to_bool(val: Any) -> bool:
        return val if isinstance(val, bool) else (val.lower() == "true" if isinstance(val, str) else bool(val))

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _format_time(dt: Optional[datetime]) -> str:
        if not dt:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_ts(self, ts: Optional[int]) -> str:
        return self._format_time(self._aware_from_timestamp(ts)) if ts else ""

    @staticmethod
    def _mask_cookie(cookie: str) -> str:
        if not cookie:
            return ""
        return cookie if len(cookie) <= 18 else f"{cookie[:10]}...{cookie[-6:]}"

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    def _aware_from_timestamp(self, timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings.TZ))

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
    def _format_duration(seconds: int) -> str:
        seconds = max(0, int(seconds or 0))
        if seconds <= 0:
            return "0秒"
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}天")
        if hours:
            parts.append(f"{hours}小时")
        if minutes:
            parts.append(f"{minutes}分钟")
        if secs and not parts:
            parts.append(f"{secs}秒")
        return "".join(parts[:2])

    @staticmethod
    def _get_error_detail(err: Exception) -> str:
        return str(err) or err.__class__.__name__
