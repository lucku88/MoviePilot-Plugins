import random
import socket
import time
from datetime import datetime, timedelta
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


class SQFarm(_PluginBase):
    plugin_name = "SQ种菜"
    plugin_desc = "思齐农场自动收菜、售卖、补种，支持 Vue 面板、动态调度和站点 Cookie 同步。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f331.png"
    plugin_version = "0.2.0"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "sqfarm_"
    plugin_order = 66
    auth_level = 1

    DEFAULT_SITE_URL = "https://si-qi.xyz"
    DEFAULT_SITE_DOMAIN = "si-qi.xyz"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    DEFAULT_CRON = "*/10 * * * *"

    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper: Optional[SiteOper] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _auto_cookie: bool = True
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cron: str = DEFAULT_CRON
    _site_domain: str = DEFAULT_SITE_DOMAIN
    _site_url: str = DEFAULT_SITE_URL
    _user_agent: str = DEFAULT_USER_AGENT
    _cookie: str = ""
    _cookie_source: str = "未配置"
    _ocr_api_url: str = "http://10.10.10.10:8089/api/tr-run/"
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

        if self._auto_cookie:
            self._sync_cookie_from_site(silent=True)
        else:
            self._cookie_source = "手动配置" if self._cookie else "未配置"

        self._load_saved_next_run()
        self._load_saved_next_trigger()

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
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取 SQFarm 配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 SQFarm 配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 SQFarm 状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新农场数据"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行一次 SQFarm"},
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
        if self._enabled and self._cron:
            try:
                services.append({
                    "id": "SQFarm_poll",
                    "name": "SQ种菜轮询服务",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self._poll_worker,
                    "kwargs": {},
                })
            except Exception as err:
                logger.error("%s CRON 配置错误：%s", self.plugin_name, err)

        if self._enabled:
            next_run = self._get_next_run_for_service()
            if next_run:
                services.append({
                    "id": "SQFarm_auto",
                    "name": "SQ种菜智能调度",
                    "trigger": "date",
                    "func": self._auto_worker,
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
                logger.info("INFO 未到最近收菜时间，跳过本次轮询")
                return {"success": True, "message": "未到最近收菜时间，已跳过", "status": self._build_status(auto_refresh=False)}

            session = self._build_session()
            data = self._fetch_state(session)
            if not data or not data.get("success"):
                raise RuntimeError("获取农场数据失败，Cookie 可能失效")

            now_sec = int(time.time())
            ready_plots = [
                plot for plot in (data.get("user_lands") or [])
                if plot.get("seed_id") and (
                    plot.get("is_ready") == 1
                    or (plot.get("harvest_time") and int(plot.get("harvest_time") or 0) <= now_sec)
                )
            ]
            logger.info("INFO 成熟作物数量：%s", len(ready_plots))

            action_harvest = False
            action_sell = False
            action_plant = False
            sell_success_count = 0
            planted_seed_name = ""
            harvest_snapshot: List[Dict[str, Any]] = []

            if ready_plots:
                harvested = self._harvest_all(session)
                action_harvest = bool(harvested)
                data = self._fetch_state(session)
                if harvested:
                    harvest_snapshot = [
                        {
                            "name": item.get("name"),
                            "qty": int(item.get("quantity") or 0),
                            "unit": int(item.get("unit_reward") or 0),
                            "icon": self._crop_icon.get(item.get("name"), "🌱"),
                        }
                        for item in (data.get("inventory") or [])
                    ]

            inventory = data.get("inventory") or []
            if inventory:
                logger.info("INFO 开始售出背包作物，共 %s 类...", len(inventory))
                for item in inventory:
                    try:
                        result = self._post_action(session, "sell_inventory", {
                            "seed_id": item.get("seed_id"),
                            "quantity": item.get("quantity"),
                        }, retry_network=False)
                        if not result or result.get("success", True):
                            sell_success_count += 1
                    except Exception as err:
                        logger.warning("sell_inventory failed: %s", err)
                action_sell = sell_success_count > 0
                data = self._fetch_state(session)
                logger.info("INFO 售出完成")

            empty_count = self._count_empty_plots(data)
            logger.info("INFO 空地数量：%s", empty_count)
            if empty_count > 0:
                best_seed = self._pick_seed(data)
                if best_seed:
                    logger.info("INFO 准备补种：%s", best_seed.get("name"))
                    try:
                        result = self._post_action(session, "plant_fill_empty", {"seed_id": best_seed.get("id")}, retry_network=False)
                        if result and result.get("success", True):
                            action_plant = True
                            planted_seed_name = best_seed.get("name") or ""
                            logger.info("INFO 补种完成：%s", best_seed.get("name"))
                        data = self._fetch_state(session)
                    except Exception as err:
                        logger.warning("plant_fill_empty failed: %s", err)

            next_run = self._compute_next_run(data)
            if ready_plots and not action_harvest:
                retry_at = int(time.time()) + max(30, self._ready_retry_seconds)
                next_run = min(next_run, retry_at) if next_run else retry_at
                logger.warning("INFO 存在成熟作物但本次未收获成功，延后 %s 秒重试", max(30, self._ready_retry_seconds))
            self._schedule_next_run(next_run, reason)
            log_result = self._parse_logs(data.get("user_logs") or [], run_start)
            next_run_text = self._format_ts(next_run) if next_run else "暂无成熟作物"
            msg_lines = self._build_result_lines(
                action_harvest,
                action_sell,
                action_plant,
                harvest_snapshot,
                log_result,
                next_run_text,
                sell_success_count=sell_success_count,
                planted_seed_name=planted_seed_name,
            )
            has_action_lines = any(line.startswith(("✅", "💰", "🧺", "🌱")) for line in msg_lines)

            state_record = self._build_state_record(data, next_run, msg_lines)
            farm_status = self._build_ui_state(data, next_run, msg_lines)
            self.save_data("state", state_record)
            self.save_data("farm_status", farm_status)
            self.save_data("last_run", self._format_time(self._aware_now()))

            title = "🌱 SQ种菜报告" if has_action_lines else "ℹ️ SQ种菜无动作"
            self._append_history(title, msg_lines or ["本次无动作"])

            if self._notify and has_action_lines:
                self.post_message(mtype=NotificationType.Plugin, title=f"🌱 {self.plugin_name}报告", text="\n".join(msg_lines))

            return {"success": True, "message": msg_lines[0] if msg_lines else "本次无动作", "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.exception("%s 执行失败：%s", self.plugin_name, detail)
            self._append_history(f"❌ {self.plugin_name}异常", [f"⚠️ {detail}"])
            if self._notify:
                self.post_message(mtype=NotificationType.Plugin, title=f"❌ {self.plugin_name}异常", text=f"⚠️ {detail}")
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(self._aware_now()), cost_sec)

    def _manual_worker(self):
        return self.run_job(force=True, reason="onlyonce")

    def _poll_worker(self):
        return self.run_job(force=False, reason="cron")

    def _auto_worker(self):
        return self.run_job(force=True, reason="smart")

    def _refresh_data(self):
        try:
            farm_status = self._refresh_state(reason="manual-refresh")
            return {"success": True, "message": "农场数据已刷新", "farm_status": farm_status, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 刷新数据失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail}

    def _run_now(self):
        return self.run_job(force=True, reason="manual-api")

    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        farm_status = self.get_data("farm_status") or {}
        if auto_refresh and self._enabled and not farm_status:
            try:
                farm_status = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)

        next_run = self._load_saved_next_run()
        next_trigger = self._load_saved_next_trigger()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": self._cron,
            "site_domain": self._site_domain,
            "site_url": self._site_url,
            "auto_cookie": self._auto_cookie,
            "cookie_source": self._cookie_source,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(next_trigger) if next_trigger else "",
            "last_run": self.get_data("last_run") or "",
            "farm_status": farm_status,
            "history": (self.get_data("history") or [])[:10],
            "config": self._get_config(),
        }

    def _get_config(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_cookie": self._auto_cookie,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cron": self._cron,
            "site_domain": self._site_domain,
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

    def _save_config(self, config_payload: dict):
        merged = self._default_config()
        merged.update(self._get_config())
        merged.update(config_payload or {})
        self.init_plugin(merged)
        self._update_config()
        self._reregister_plugin("save_config")
        if self._enabled:
            try:
                self._refresh_state(reason="save-config")
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
            "use_proxy": False,
            "force_ipv4": True,
            "cron": self.DEFAULT_CRON,
            "site_domain": self.DEFAULT_SITE_DOMAIN,
            "cookie": "",
            "ocr_api_url": "http://10.10.10.10:8089/api/tr-run/",
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
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cron = (config.get("cron") or self.DEFAULT_CRON).strip()
        self._site_domain = (config.get("site_domain") or self.DEFAULT_SITE_DOMAIN).strip() or self.DEFAULT_SITE_DOMAIN
        self._cookie = (config.get("cookie") or "").strip()
        self._ocr_api_url = (config.get("ocr_api_url") or "").strip()
        self._prefer_seed = (config.get("prefer_seed") or "西红柿").strip() or "西红柿"
        self._schedule_buffer_seconds = self._safe_int(config.get("schedule_buffer_seconds"), 5)
        self._random_delay_max_seconds = self._safe_int(config.get("random_delay_max_seconds"), 5)
        self._http_timeout = self._safe_int(config.get("http_timeout"), 12)
        self._http_retry_times = max(1, self._safe_int(config.get("http_retry_times"), 3))
        self._http_retry_delay = max(200, self._safe_int(config.get("http_retry_delay"), 1500))
        self._ocr_retry_times = max(1, self._safe_int(config.get("ocr_retry_times"), 2))

    def _update_config(self):
        self.update_config(self._get_config())

    def _refresh_state(self, reason: str = "refresh") -> Dict[str, Any]:
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
        self.save_data("last_run", self._format_time(self._aware_now()))
        return farm_status

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
        return response.json()

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
                if not self._is_retryable_network_error(err) or idx == self._http_retry_times:
                    raise
                wait_ms = self._http_retry_delay * idx + random.randint(0, 500)
                logger.warning("%s failed %s/%s: %s", label, idx, self._http_retry_times, err)
                time.sleep(wait_ms / 1000.0)
        raise last_err

    @staticmethod
    def _is_retryable_network_error(err: Exception) -> bool:
        detail = str(err).upper()
        codes = ["ETIMEDOUT", "ECONNRESET", "ECONNABORTED", "EAI_AGAIN", "ENOTFOUND", "EHOSTUNREACH", "ECONNREFUSED"]
        return any(code in detail for code in codes)

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

    def _harvest_all(self, session: requests.Session) -> bool:
        logger.info("INFO 开始收获...")
        for idx in range(1, 6):
            logger.info("Harvest attempt %s/5", idx)
            try:
                cap_res = self._post_action(session, "get_harvest_all_captcha", {}, retry_network=True)
                if not cap_res or not cap_res.get("success") or not cap_res.get("captcha"):
                    logger.warning("get_harvest_all_captcha failed: %s", (cap_res or {}).get("msg", "UNKNOWN"))
                    continue

                captcha = cap_res["captcha"]
                image_url = captcha.get("image_url")
                if not image_url:
                    continue
                img_response = self._request_with_retry("captchaImage", lambda: session.get(image_url, timeout=(self._http_timeout, self._http_timeout)))
                img_response.raise_for_status()
                code = self._recognize_captcha(session, img_response.content)
                if not code:
                    logger.warning("captcha OCR failed, retry...")
                    continue

                harvest_res = self._post_action(session, "harvest_all", {
                    "imagehash": captcha.get("imagehash"),
                    "imagestring": code,
                }, retry_network=False)
                if harvest_res and harvest_res.get("success"):
                    logger.info("Harvest completed")
                    return True
                logger.warning("harvest_all failed: %s", (harvest_res or {}).get("msg", "UNKNOWN"))
                if not (harvest_res or {}).get("captcha_required"):
                    break
            except Exception as err:
                logger.warning("harvest flow failed: %s", err)
        logger.warning("harvest not completed after retries")
        return False

    def _should_skip_run(self) -> bool:
        next_run = self._load_saved_next_run()
        if not next_run:
            return False
        return self._aware_now() + timedelta(seconds=max(5, self._schedule_buffer_seconds)) < next_run

    def _get_next_run_for_service(self) -> Optional[datetime]:
        next_trigger = self._load_saved_next_trigger()
        now = self._aware_now()
        if next_trigger:
            return next_trigger if next_trigger > now else now + timedelta(seconds=5)
        if not self.get_data("farm_status"):
            return now + timedelta(seconds=8)
        return None

    def _schedule_next_run(self, next_run_ts: Optional[int], reason: str = ""):
        if next_run_ts:
            next_run = self._aware_from_timestamp(next_run_ts)
            next_trigger = next_run + timedelta(seconds=max(0, self._schedule_buffer_seconds))
            if next_trigger < self._aware_now() + timedelta(seconds=5):
                next_trigger = self._aware_now() + timedelta(seconds=5)
            self._next_run_time = next_run
            self._next_trigger_time = next_trigger
            self.save_data("next_run_time", self._format_time(next_run))
            self.save_data("next_trigger_time", self._format_time(next_trigger))
            logger.info("INFO 最近收菜时间：%s", self._format_time(next_run))
            logger.info("INFO 计划触发时间：%s", self._format_time(next_trigger))
        else:
            self._next_run_time = None
            self._next_trigger_time = None
            self.save_data("next_run_time", "")
            self.save_data("next_trigger_time", "")
            logger.info("INFO 当前没有已种植作物，保留 CRON 轮询")

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

    @staticmethod
    def _count_empty_plots(data: dict) -> int:
        lands = data.get("lands") or []
        plot_slot = data.get("plot_slot") or {}
        enabled = bool(plot_slot.get("enabled"))
        effective = plot_slot.get("effective_plot_counts") or {}
        total_harvest = int((data.get("user_stats") or {}).get("total_harvest") or 0)
        unlocked_count = int((data.get("user_stats") or {}).get("unlocked_land_count") or 0)
        user_lands = data.get("user_lands") or []
        empty = 0
        for idx, land in enumerate(lands):
            unlock_need = int(land.get("unlock_harvest") or 0)
            if not (idx < unlocked_count and total_harvest >= unlock_need):
                continue
            land_id = int(land.get("id") or 0)
            total = int(effective.get(str(land_id)) or effective.get(land_id) or land.get("plot_count") or 0) if enabled else int(land.get("plot_count") or 0)
            planted = len([plot for plot in user_lands if int(plot.get("land_id") or 0) == land_id and plot.get("seed_id")])
            empty += max(0, total - planted)
        return empty

    def _pick_seed(self, data: dict) -> Optional[dict]:
        total_harvest = int((data.get("user_stats") or {}).get("total_harvest") or 0)
        unlocked = [seed for seed in (data.get("seeds") or []) if total_harvest >= int(seed.get("unlock_harvest") or 0)]
        if not unlocked:
            return None
        unlocked.sort(key=lambda item: ((float(item.get("base_reward") or 0) - float(item.get("cost") or 0)) / max(float(item.get("grow_time") or 1), 1)), reverse=True)
        for seed in unlocked:
            if str(seed.get("name")) == self._prefer_seed:
                return seed
        return unlocked[0]

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
        return {
            "time": self._format_time(self._aware_now()),
            "next_run_time": self._format_ts(next_run) if next_run else "",
            "next_trigger_time": self._format_time(self._next_trigger_time) if self._next_trigger_time else "",
            "summary": summary_lines,
            "user": {
                "bonus": data.get("user_bonus"),
                "total_harvest": (data.get("user_stats") or {}).get("total_harvest"),
                "total_steal": (data.get("user_stats") or {}).get("total_steal_gain"),
                "farm_likes": (data.get("user_stats") or {}).get("farm_like_total"),
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
        ready_count = len([plot for plot in (data.get("user_lands") or []) if plot.get("is_ready") == 1])
        empty_count = self._count_empty_plots(data)
        growing_count = max(0, len(data.get("user_lands") or []) - ready_count)
        return {
            "title": "思齐种菜赚魔力",
            "last_updated": self._format_time(self._aware_now()),
            "summary": summary_lines,
            "next_run_time": self._format_ts(next_run) if next_run else "暂无成熟作物",
            "next_trigger_time": self._format_time(self._next_trigger_time) if self._next_trigger_time else "等待下一次轮询",
            "cookie_source": self._cookie_source,
            "overview": [
                {"label": "魔力值", "value": int(data.get("user_bonus") or 0), "accent": "amber"},
                {"label": "总种植收获", "value": int(user_stats.get("total_harvest") or 0), "accent": "cyan"},
                {"label": "总偷菜收益", "value": int(user_stats.get("total_steal_gain") or 0), "accent": "green"},
                {"label": "农场被点赞", "value": int(user_stats.get("farm_like_total") or 0), "accent": "indigo"},
            ],
            "highlights": {
                "ready_count": ready_count,
                "growing_count": growing_count,
                "empty_count": empty_count,
                "land_count": int(user_stats.get("unlocked_land_count") or 0),
            },
            "inventory": self._build_inventory_cards(data.get("inventory") or []),
            "seed_shop": self._build_seed_shop(data),
            "land_groups": self._build_land_groups(data),
            "history": (self.get_data("history") or [])[:10],
        }

    def _build_inventory_cards(self, inventory: List[dict]) -> Dict[str, Any]:
        cards = []
        for item in inventory:
            quantity = int(item.get("quantity") or 0)
            unit_reward = int(item.get("unit_reward") or 0)
            name = item.get("name") or "未知作物"
            cards.append({
                "name": name,
                "icon": self._crop_icon.get(name, "🌱"),
                "quantity": quantity,
                "unit_reward": unit_reward,
                "total_reward": quantity * unit_reward,
            })
        return {"empty": not cards, "items": cards, "empty_text": "背包空空如也，快去收菜吧。"}

    def _build_seed_shop(self, data: dict) -> List[Dict[str, Any]]:
        total_harvest = int((data.get("user_stats") or {}).get("total_harvest") or 0)
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
                "preferred": name == self._prefer_seed,
            })
        return cards

    def _build_land_groups(self, data: dict) -> List[Dict[str, Any]]:
        lands = data.get("lands") or []
        user_lands = data.get("user_lands") or []
        plot_slot = data.get("plot_slot") or {}
        effective = plot_slot.get("effective_plot_counts") or {}
        user_stats = data.get("user_stats") or {}
        total_harvest = int(user_stats.get("total_harvest") or 0)
        unlocked_count = int(user_stats.get("unlocked_land_count") or 0)
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        groups: List[Dict[str, Any]] = []

        for idx, land in enumerate(lands):
            land_id = int(land.get("id") or 0)
            total_slots = int(land.get("plot_count") or 0)
            unlock_need = int(land.get("unlock_harvest") or 0)
            land_unlocked = idx < unlocked_count and total_harvest >= unlock_need
            available_slots = int(effective.get(str(land_id)) or effective.get(land_id) or total_slots)
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
                        "slot_index": slot_index,
                        "state": "empty",
                        "title": "空地",
                        "icon": "➕",
                        "badge": "可补种",
                        "description": f"优先种子：{self._prefer_seed}",
                        "remaining_label": "等待补种",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })
                elif slot_index == available_slots + 1 and land_unlocked:
                    expand_cost = land.get("next_plot_cost") or land.get("plot_price") or "待站点开放"
                    slots.append({
                        "slot_index": slot_index,
                        "state": "expand",
                        "title": "扩展坑位",
                        "icon": "🪴",
                        "badge": "可扩展",
                        "description": f"购买 {expand_cost}",
                        "remaining_label": "",
                        "reward_text": "",
                        "harvest_ts": 0,
                    })
                else:
                    slots.append({
                        "slot_index": slot_index,
                        "state": "locked",
                        "title": "未解锁",
                        "icon": "🔒",
                        "badge": "未解锁",
                        "description": "等待扩展",
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
        log_result: dict,
        next_run_text: str,
        sell_success_count: int = 0,
        planted_seed_name: str = "",
    ) -> List[str]:
        def join_summary(summary_map: dict) -> str:
            return "  ".join([f"{key}×{value}" for key, value in summary_map.items()])

        harvest_map: Dict[str, int] = {}
        harvest_income = 0
        for item in harvest_snapshot:
            key = f"{item.get('icon', '')}{item.get('name', '')}"
            harvest_map[key] = harvest_map.get(key, 0) + int(item.get("qty") or 0)
            harvest_income += int(item.get("qty") or 0) * int(item.get("unit") or 0)

        lines: List[str] = []
        if action_harvest and harvest_map:
            lines.append(f"✅ 收菜：{join_summary(harvest_map)}")
        if harvest_income > 0:
            lines.append(f"💰 收益：{harvest_income} 魔力")
        elif log_result.get("income", 0) > 0:
            lines.append(f"💰 收益：{log_result.get('income')} 魔力")
        if action_sell and log_result.get("sell"):
            lines.append(f"🧺 售出：{join_summary(log_result.get('sell'))}")
        elif action_sell and sell_success_count > 0:
            lines.append(f"🧺 售出：已处理 {sell_success_count} 类作物")
        if action_plant and log_result.get("plant"):
            lines.append(f"🌱 补种：{join_summary(log_result.get('plant'))}")
        elif action_plant and planted_seed_name:
            lines.append(f"🌱 补种：{planted_seed_name}")
        if not lines:
            lines.append("ℹ️ 本次没有可执行动作")
        lines.append(f"⏰ 下次可收：{next_run_text}")
        return lines

    def _append_history(self, title: str, lines: List[str]):
        history = self.get_data("history") or []
        history.insert(0, {"time": self._format_time(self._aware_now()), "title": title, "lines": lines})
        self.save_data("history", history[:20])

    def _parse_logs(self, logs: List[dict], since_time: float) -> dict:
        result = {"sell": {}, "plant": {}, "income": 0}
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
            if item.get("action") == "sell":
                result["sell"][key] = result["sell"].get(key, 0) + qty
                result["income"] += int(item.get("value") or 0)
            elif item.get("action") == "plant":
                result["plant"][key] = result["plant"].get(key, 0) + qty
        return result

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
