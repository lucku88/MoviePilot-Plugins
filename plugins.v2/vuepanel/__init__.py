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
from apscheduler.triggers.cron import CronTrigger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase
from app.scheduler import Scheduler
from app.schemas import NotificationType


class VuePanel(_PluginBase):
    plugin_name = "Vue-面板"
    plugin_desc = "按网站 / 功能模块组织签到与领取卡片，支持思齐签到、HNR领取与 New API 多站点签到。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4ca.png"
    plugin_version = "0.1.3"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "vuepanel_"
    plugin_order = 69
    auth_level = 1

    DEFAULT_CRON = "5 8 * * *"
    DEFAULT_TIMEOUT = 15
    DEFAULT_RETRY_TIMES = 3
    DEFAULT_RANDOM_DELAY = 5
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
    HISTORY_LIMIT = 30

    MODULES: List[Dict[str, str]] = [
        {
            "key": "siqi_sign",
            "label": "思齐签到",
            "icon": "🪪",
            "description": "访问 /attendance.php 完成签到。",
            "default_site_name": "思齐主站",
            "default_site_url": "https://si-qi.xyz",
            "singleton": True,
            "tone": "emerald",
        },
        {
            "key": "hnr_claim",
            "label": "HNR领取",
            "icon": "🎁",
            "description": "访问 /hnrview.php 领取 HNR 奖励。",
            "default_site_name": "思齐主站",
            "default_site_url": "https://si-qi.xyz",
            "singleton": True,
            "tone": "amber",
        },
        {
            "key": "newapi_checkin",
            "label": "New API签到",
            "icon": "🤖",
            "description": "调用 /api/user/checkin 执行签到，支持多站点独立配置。",
            "default_site_name": "New API 站点",
            "default_site_url": "https://open.xingyungept.cn",
            "singleton": False,
            "tone": "azure",
        },
    ]

    TONES: List[Dict[str, str]] = [
        {"key": "emerald", "label": "薄荷绿"},
        {"key": "azure", "label": "海湾蓝"},
        {"key": "amber", "label": "琥珀橙"},
        {"key": "rose", "label": "莓果红"},
        {"key": "violet", "label": "雾紫"},
        {"key": "slate", "label": "石墨灰"},
    ]

    _scheduler: Optional[BackgroundScheduler] = None
    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _use_proxy: bool = False
    _force_ipv4: bool = True
    _cron: str = DEFAULT_CRON
    _http_timeout: int = DEFAULT_TIMEOUT
    _http_retry_times: int = DEFAULT_RETRY_TIMES
    _random_delay_max_seconds: int = DEFAULT_RANDOM_DELAY
    _cards: List[Dict[str, Any]] = []

    def __init__(self):
        super().__init__()

    def init_plugin(self, config: Optional[dict] = None):
        self.stop_service()

        merged = self._default_config()
        if config:
            merged.update(config)
        if config and "cards" in config:
            merged["cards"] = config.get("cards") or []

        self._apply_config(merged)
        self._save_schedule_meta()

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
            {"path": "/config", "endpoint": self._get_config_api, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-面板配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存 Vue-面板配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取 Vue-面板状态"},
            {"path": "/refresh", "endpoint": self._refresh_data, "methods": ["POST"], "auth": "bear", "summary": "刷新所有卡片状态"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "执行启用卡片"},
            {"path": "/card/run", "endpoint": self._run_card_api, "methods": ["POST"], "auth": "bear", "summary": "执行单个卡片"},
            {"path": "/card/refresh", "endpoint": self._refresh_card_api, "methods": ["POST"], "auth": "bear", "summary": "刷新单个卡片"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        if not self._enabled:
            return []
        services: List[Dict[str, Any]] = []
        for card in self._cards:
            trigger = self._get_card_trigger(card)
            if not trigger:
                continue
            services.append(
                {
                    "id": f"VuePanel_{self._safe_card_id(card['id'])}",
                    "name": f"{self.plugin_name}-{card.get('title') or card.get('site_name') or card['id']}",
                    "trigger": trigger,
                    "func": self._scheduled_card_worker,
                    "kwargs": {"card_id": card["id"]},
                }
            )
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
        return self.run_job(force=True, reason="onlyonce")

    def _scheduled_worker(self):
        return self.run_job(force=False, reason="scheduled")

    def _scheduled_card_worker(self, card_id: str):
        return self.run_job(force=False, reason="scheduled-card", card_id=card_id)

    def _get_config_api(self):
        return self._get_config()

    def _get_status(self):
        return self._build_status(auto_refresh=True)

    def _refresh_data(self, payload: Optional[dict] = None):
        card_id = str((payload or {}).get("card_id") or "").strip()
        try:
            dashboard = self._refresh_state(reason="manual-refresh", card_id=card_id)
            message = "卡片状态已刷新" if card_id else "全部卡片状态已刷新"
            return {"success": True, "message": message, "dashboard": dashboard, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.warning("%s 刷新状态失败：%s", self.plugin_name, detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}

    def _refresh_card_api(self, payload: Optional[dict] = None):
        return self._refresh_data(payload)

    def _run_now(self, payload: Optional[dict] = None):
        card_id = str((payload or {}).get("card_id") or "").strip()
        return self.run_job(force=True, reason="manual", card_id=card_id)

    def _run_card_api(self, payload: Optional[dict] = None):
        payload = payload or {}
        card_id = str(payload.get("card_id") or "").strip()
        if not card_id:
            return {"success": False, "message": "缺少 card_id", "status": self._build_status(auto_refresh=False)}
        return self.run_job(force=True, reason="manual-card", card_id=card_id)

    def run_job(self, force: bool = False, reason: str = "manual", card_id: str = "") -> Dict[str, Any]:
        run_start = time.time()
        logger.info("## 开始执行... %s", self._format_time(self._aware_now()))
        try:
            targets = self._select_cards_for_run(card_id=card_id, force=force, reason=reason)
            if not targets:
                return {"success": False, "message": "暂无可执行卡片", "status": self._build_status(auto_refresh=False)}

            if self._force_ipv4:
                urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

            delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if delay:
                logger.info("%s 随机延迟 %s 秒后执行", self.plugin_name, delay)
                time.sleep(delay)

            states = self._load_card_states()
            notify_lines: List[str] = []
            summary_lines: List[str] = []
            success_count = 0
            error_count = 0

            for card in targets:
                result = self._execute_card(card)
                state = self._result_to_state(card, result, previous=states.get(card["id"]), record_run=True)
                states[card["id"]] = state
                summary_lines.append(f"{state['module_icon']} {state['title']}：{state['status_text']}")
                if state.get("last_success"):
                    success_count += 1
                elif state.get("level") == "error":
                    error_count += 1
                self._append_history(state)
                if self._notify and card.get("notify"):
                    notify_lines.append(f"{state['module_icon']} {state['title']}：{state['status_text']}")

            self._save_card_states(states)
            dashboard = self._build_dashboard(states)
            self.save_data("dashboard_status", dashboard)
            self.save_data("last_run", self._format_time(self._aware_now()))
            self._save_schedule_meta()

            if self._notify and notify_lines:
                title = "【📊面板报告】" if error_count == 0 else "【⚠️面板报告】"
                self.post_message(
                    mtype=NotificationType.Plugin,
                    title=title,
                    text="\n".join(notify_lines[:12]),
                )

            message = f"已执行 {len(targets)} 个卡片，成功 {success_count}，异常 {error_count}"
            if card_id and summary_lines:
                message = summary_lines[0]
            return {"success": error_count == 0, "message": message, "summary": summary_lines, "dashboard": dashboard, "status": self._build_status(auto_refresh=False)}
        except Exception as err:
            detail = self._get_error_detail(err)
            logger.error("%s 执行失败：%s", self.plugin_name, detail)
            logger.error("%s 异常堆栈：\n%s", self.plugin_name, traceback.format_exc())
            if self._notify:
                self.post_message(mtype=NotificationType.Plugin, title="【⚠️面板异常】", text=detail)
            return {"success": False, "message": detail, "status": self._build_status(auto_refresh=False)}
        finally:
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(self._aware_now()), cost_sec)

    def _build_status(self, auto_refresh: bool = True) -> Dict[str, Any]:
        dashboard = self.get_data("dashboard_status") or {}
        if auto_refresh and (
            not dashboard
            or dashboard.get("schema_version") != self.plugin_version
            or dashboard.get("cards_version") != self._cards_fingerprint()
        ):
            try:
                dashboard = self._refresh_state(reason="status-init")
            except Exception as err:
                logger.warning("%s 初始化状态刷新失败：%s", self.plugin_name, err)
                dashboard = self._build_dashboard(self._load_card_states())

        next_run = self._load_next_run_time()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "cron": self._cron,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "next_run_time": self._format_time(next_run) if next_run else "",
            "next_trigger_time": self._format_time(self._load_next_trigger_time()) if self._load_next_trigger_time() else "",
            "next_trigger_mode": self._load_next_trigger_mode(),
            "last_run": self.get_data("last_run") or "",
            "dashboard": dashboard,
            "history": (self.get_data("history") or [])[:12],
            "config": self._get_config(),
        }

    def _get_config(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "use_proxy": self._use_proxy,
            "force_ipv4": self._force_ipv4,
            "cron": self._cron,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "cards": list(self._cards),
            "module_options": list(self.MODULES),
            "tone_options": list(self.TONES),
        }

    def _save_config(self, config_payload: dict):
        merged = self._default_config()
        merged.update(self._get_config())
        merged.update(config_payload or {})
        if "cards" not in (config_payload or {}):
            merged["cards"] = self._cards

        self.init_plugin(merged)
        self._update_config()
        self._reregister_plugin("save_config")

        try:
            dashboard = self._refresh_state(reason="save-config")
        except Exception as err:
            logger.warning("%s 保存配置后刷新失败：%s", self.plugin_name, err)
            dashboard = self._build_dashboard(self._load_card_states())

        return {"success": True, "message": "配置已保存", "config": self._get_config(), "dashboard": dashboard, "status": self._build_status(auto_refresh=False)}

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "use_proxy": False,
            "force_ipv4": True,
            "cron": self.DEFAULT_CRON,
            "http_timeout": self.DEFAULT_TIMEOUT,
            "http_retry_times": self.DEFAULT_RETRY_TIMES,
            "random_delay_max_seconds": self.DEFAULT_RANDOM_DELAY,
            "cards": self._default_cards(),
        }

    def _default_cards(self) -> List[Dict[str, Any]]:
        return [
            self._fixed_card_template("siqi_sign", note="填写 Cookie 后即可启用。"),
            self._fixed_card_template("hnr_claim", note="和思齐签到共用同站 Cookie。"),
            self._newapi_card_template(),
        ]

    def _fixed_card_template(self, module_key: str, note: str = "") -> Dict[str, Any]:
        module_meta = self._module_meta(module_key)
        return self._normalize_card(
            {
                "id": f"{module_key}-default",
                "title": module_meta["label"],
                "module_key": module_key,
                "site_name": module_meta["default_site_name"],
                "site_url": module_meta["default_site_url"],
                "enabled": False,
                "auto_run": True,
                "cron": self.DEFAULT_CRON,
                "show_status": True,
                "notify": True,
                "tone": module_meta.get("tone") or "azure",
                "cookie": "",
                "uid": "",
                "note": note,
            },
            fallback_id=f"{module_key}-default",
        )

    def _newapi_card_template(self) -> Dict[str, Any]:
        module_meta = self._module_meta("newapi_checkin")
        return self._normalize_card(
            {
                "id": "newapi-checkin-default",
                "title": module_meta["label"],
                "module_key": "newapi_checkin",
                "site_name": "Open 站点",
                "site_url": module_meta["default_site_url"],
                "enabled": False,
                "auto_run": True,
                "cron": self.DEFAULT_CRON,
                "show_status": True,
                "notify": True,
                "tone": module_meta.get("tone") or "azure",
                "cookie": "",
                "uid": "225",
                "note": "可在 New API 模块内继续新增不同站点。",
            },
            fallback_id="newapi-checkin-default",
        )

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = self._to_bool(config.get("enabled", False))
        self._notify = self._to_bool(config.get("notify", True))
        self._onlyonce = self._to_bool(config.get("onlyonce", False))
        self._use_proxy = self._to_bool(config.get("use_proxy", False))
        self._force_ipv4 = self._to_bool(config.get("force_ipv4", True))
        self._cron = str(config.get("cron") or self.DEFAULT_CRON).strip() or self.DEFAULT_CRON
        self._http_timeout = max(3, self._safe_int(config.get("http_timeout"), self.DEFAULT_TIMEOUT))
        self._http_retry_times = max(1, self._safe_int(config.get("http_retry_times"), self.DEFAULT_RETRY_TIMES))
        self._random_delay_max_seconds = max(0, self._safe_int(config.get("random_delay_max_seconds"), self.DEFAULT_RANDOM_DELAY))
        self._cards = self._normalize_cards(config.get("cards"))

    def _update_config(self):
        self.update_config(
            {
                "enabled": self._enabled,
                "notify": self._notify,
                "onlyonce": self._onlyonce,
                "use_proxy": self._use_proxy,
                "force_ipv4": self._force_ipv4,
                "cron": self._cron,
                "http_timeout": self._http_timeout,
                "http_retry_times": self._http_retry_times,
                "random_delay_max_seconds": self._random_delay_max_seconds,
                "cards": self._cards,
            }
        )

    def _refresh_state(self, reason: str = "refresh", card_id: str = "") -> Dict[str, Any]:
        if self._force_ipv4:
            urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

        states = self._load_card_states()
        targets = self._select_cards_for_refresh(card_id=card_id)
        for card in targets:
            result = self._inspect_card(card)
            states[card["id"]] = self._result_to_state(card, result, previous=states.get(card["id"]), record_run=False)

        self._save_card_states(states)
        dashboard = self._build_dashboard(states)
        self.save_data("dashboard_status", dashboard)
        self._save_schedule_meta()
        logger.info("%s 已刷新状态：%s", self.plugin_name, reason)
        return dashboard

    def _inspect_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        if not card.get("cookie"):
            return self._warning_result("待配置 Cookie", "尚未填写 Cookie，当前卡片仅保留配置。")
        if card.get("module_key") == "newapi_checkin" and not card.get("uid"):
            return self._warning_result("待配置 UID", "New API 签到需要填写 UID。")

        module_key = card.get("module_key")
        if module_key == "siqi_sign":
            return self._inspect_siqi_sign(card)
        if module_key == "hnr_claim":
            return self._inspect_hnr_claim(card)
        if module_key == "newapi_checkin":
            return self._inspect_newapi_checkin(card)
        return self._error_result("未知功能模块", f"不支持的模块类型：{module_key}")

    def _execute_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        if not card.get("cookie"):
            return self._error_result("缺少 Cookie", "请先填写 Cookie 后再执行。")
        if card.get("module_key") == "newapi_checkin" and not card.get("uid"):
            return self._error_result("缺少 UID", "New API 签到卡片需要单独填写 UID。")

        module_key = card.get("module_key")
        if module_key == "siqi_sign":
            return self._run_siqi_sign(card)
        if module_key == "hnr_claim":
            return self._run_hnr_claim(card)
        if module_key == "newapi_checkin":
            return self._run_newapi_checkin(card)
        return self._error_result("未知功能模块", f"不支持的模块类型：{module_key}")

    def _inspect_siqi_sign(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        url = urljoin(card["site_url"], "/attendance.php")
        response = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        response.raise_for_status()
        info = self._parse_siqi_page(response.text, url)
        if info.get("invalid_cookie"):
            return self._error_result("Cookie 失效", "当前站点返回未登录状态，请更新 Cookie。")
        if info.get("signed"):
            return self._siqi_success_result(info, changed=False)
        if info.get("captcha") and info.get("imagehash"):
            return self._warning_result(
                "待执行签到",
                f"今日尚未签到，验证码 {info.get('captcha')} 已识别，可直接执行。",
                metrics=self._siqi_metrics(info),
                detail_lines=[f"站点：{card['site_url']}"],
            )
        return self._warning_result("待执行签到", "今日尚未签到，但页面未识别到验证码。", metrics=self._siqi_metrics(info))

    def _run_siqi_sign(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        url = urljoin(card["site_url"], "/attendance.php")
        response = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        response.raise_for_status()
        info = self._parse_siqi_page(response.text, url)
        if info.get("invalid_cookie"):
            return self._error_result("Cookie 失效", "当前站点返回未登录状态，请更新 Cookie。")
        if info.get("signed"):
            return self._siqi_success_result(info, changed=False)
        if not info.get("imagehash") or not info.get("captcha"):
            return self._error_result("页面解析失败", "未识别到签到验证码，无法自动提交。")

        payload = {"imagestring": info["captcha"], "imagehash": info["imagehash"]}
        submit_url = info.get("form_action") or url
        post_resp = session.post(
            submit_url,
            data=payload,
            headers={"Referer": url},
            timeout=(self._http_timeout, self._http_timeout),
        )
        post_resp.raise_for_status()

        verify_resp = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        verify_resp.raise_for_status()
        verify_info = self._parse_siqi_page(verify_resp.text, url)
        if verify_info.get("signed"):
            return self._siqi_success_result(verify_info, changed=True)
        return self._error_result("签到失败", "提交后未检测到签到成功信息，请检查页面结构或 Cookie。")

    def _inspect_hnr_claim(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        url = urljoin(card["site_url"], "/hnrview.php")
        response = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        response.raise_for_status()
        info = self._parse_hnr_page(response.text)
        if info.get("invalid_cookie"):
            return self._error_result("Cookie 失效", "当前站点返回未登录状态，请更新 Cookie。")
        rank = info.get("rank") or "未知"
        if info.get("next_time"):
            return self._success_result(
                "已领取",
                f"今日奖励已领取，下次可领取时间：{info['next_time']}。",
                metrics=[
                    {"label": "排名", "value": str(rank)},
                    {"label": "剩余奖励", "value": "0"},
                ],
                detail_lines=[f"站点：{card['site_url']}"],
            )

        claims = info.get("claims") or []
        if not claims:
            return self._info_result(
                "暂无奖励",
                f"当前没有可领取奖励，排名 {rank}。",
                metrics=[
                    {"label": "排名", "value": str(rank)},
                    {"label": "奖励数", "value": "0"},
                ],
            )

        total = sum(int(item.get("amount") or 0) for item in claims)
        return self._warning_result(
            "待领取",
            f"当前可领取 {len(claims)} 项奖励，共 {total} 魔力。",
            metrics=[
                {"label": "排名", "value": str(rank)},
                {"label": "奖励数", "value": str(len(claims))},
                {"label": "总额", "value": str(total)},
            ],
            detail_lines=[f"可领取：{', '.join(item.get('label') or item.get('reward_type') for item in claims)}"],
        )

    def _run_hnr_claim(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        list_url = urljoin(card["site_url"], "/hnrview.php")
        response = session.get(list_url, timeout=(self._http_timeout, self._http_timeout))
        response.raise_for_status()
        info = self._parse_hnr_page(response.text)
        if info.get("invalid_cookie"):
            return self._error_result("Cookie 失效", "当前站点返回未登录状态，请更新 Cookie。")
        if info.get("next_time"):
            return self._success_result(
                "已领取",
                f"今日奖励已领取，下次可领取时间：{info['next_time']}。",
                metrics=[
                    {"label": "排名", "value": str(info.get("rank") or "未知")},
                    {"label": "奖励数", "value": "0"},
                ],
            )

        claims = info.get("claims") or []
        if not claims:
            return self._info_result(
                "暂无奖励",
                f"当前没有可领取奖励，排名 {info.get('rank') or '未知'}。",
                metrics=[
                    {"label": "排名", "value": str(info.get("rank") or "未知")},
                    {"label": "奖励数", "value": "0"},
                ],
            )

        claim_url = urljoin(card["site_url"], "/hnr_claim_reward.php")
        claimed: List[str] = []
        failed: List[str] = []
        total_amount = 0

        for item in claims:
            reward_type = item.get("reward_type")
            amount = str(item.get("amount") or "0")
            name = item.get("label") or reward_type or "奖励"
            try:
                post_resp = session.post(
                    claim_url,
                    data={"reward_type": reward_type, "amount": amount},
                    headers={"Referer": list_url},
                    allow_redirects=False,
                    timeout=(self._http_timeout, self._http_timeout),
                )
                success = False
                if post_resp.status_code == 302:
                    success = "success=reward_claimed" in str(post_resp.headers.get("Location") or "")
                elif post_resp.status_code == 200:
                    success = "成功" in post_resp.text or "领取成功" in post_resp.text
                if success:
                    claimed.append(f"{name}(+{amount})")
                    total_amount += self._safe_int(amount, 0)
                else:
                    failed.append(name)
            except Exception:
                failed.append(name)

        level = "success" if claimed and not failed else ("warning" if claimed else "error")
        status_title = "领取完成" if claimed else "领取失败"
        status_text = (
            f"成功领取 {len(claimed)} 项奖励，共 {total_amount} 魔力。"
            if claimed
            else f"全部奖励领取失败，当前排名 {info.get('rank') or '未知'}。"
        )
        detail_lines: List[str] = []
        if claimed:
            detail_lines.append(f"已领取：{', '.join(claimed)}")
        if failed:
            detail_lines.append(f"失败：{', '.join(failed)}")
        return self._build_result(
            success=bool(claimed),
            level=level,
            status_title=status_title,
            status_text=status_text,
            metrics=[
                {"label": "排名", "value": str(info.get("rank") or "未知")},
                {"label": "成功数", "value": str(len(claimed))},
                {"label": "总额", "value": str(total_amount)},
            ],
            detail_lines=detail_lines,
        )

    def _inspect_newapi_checkin(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        status = self._request_newapi_status(session, card)
        if not status.get("success"):
            return self._error_result("状态读取失败", status.get("message") or "接口未返回 success。")

        stats = status.get("stats") or {}
        checked = bool(stats.get("checked_in_today"))
        return self._build_result(
            success=True,
            level="success" if checked else "warning",
            status_title="今日已签到" if checked else "今日未签到",
            status_text=f"{'今日已签到' if checked else '今日未签到'} | {self._format_newapi_stats(stats)}",
            metrics=self._newapi_metrics(stats),
            detail_lines=[f"站点：{card['site_url']}", f"UID：{card['uid']}"],
        )

    def _run_newapi_checkin(self, card: Dict[str, Any]) -> Dict[str, Any]:
        session = self._build_session(card)
        status = self._request_newapi_status(session, card)
        if not status.get("success"):
            return self._error_result("状态读取失败", status.get("message") or "接口未返回 success。")

        stats = status.get("stats") or {}
        if stats.get("checked_in_today"):
            return self._build_result(
                success=True,
                level="success",
                status_title="今日已签到",
                status_text=f"今日已签到 | {self._format_newapi_stats(stats)}",
                metrics=self._newapi_metrics(stats),
                detail_lines=[f"站点：{card['site_url']}", f"UID：{card['uid']}"],
            )

        sign_result: Dict[str, Any] = {}
        delay_seconds = max(1, min(5, self._http_timeout // 3 or 1))
        for attempt in range(1, self._http_retry_times + 1):
            sign_result = self._request_newapi_checkin(session, card)
            if sign_result.get("success"):
                break
            if attempt < self._http_retry_times:
                time.sleep(delay_seconds)

        if not sign_result.get("success"):
            return self._error_result("签到失败", sign_result.get("message") or "接口未返回 success。")

        refresh = self._request_newapi_status(session, card)
        refresh_stats = refresh.get("stats") or stats
        reward_text = self._format_newapi_money((sign_result.get("data") or {}).get("quota_awarded"))
        return self._build_result(
            success=True,
            level="success",
            status_title="签到成功",
            status_text=f"签到成功 {reward_text} | {self._format_newapi_stats(refresh_stats)}",
            metrics=self._newapi_metrics(refresh_stats),
            detail_lines=[f"站点：{card['site_url']}", f"UID：{card['uid']}", f"奖励：{reward_text}"],
        )

    def _request_newapi_status(self, session: requests.Session, card: Dict[str, Any]) -> Dict[str, Any]:
        month = datetime.now().strftime("%Y-%m")
        url = urljoin(card["site_url"], f"/api/user/checkin?month={month}")
        response = session.get(url, timeout=(self._http_timeout, self._http_timeout))
        payload = self._safe_json(response)
        if not isinstance(payload, dict):
            return {"success": False, "message": f"HTTP {response.status_code}"}
        if not payload.get("success"):
            message = payload.get("message") or f"HTTP {response.status_code}"
            return {"success": False, "message": message}
        return {"success": True, "stats": ((payload.get("data") or {}).get("stats") or {}), "raw": payload}

    def _request_newapi_checkin(self, session: requests.Session, card: Dict[str, Any]) -> Dict[str, Any]:
        url = urljoin(card["site_url"], "/api/user/checkin")
        response = session.post(url, timeout=(self._http_timeout, self._http_timeout))
        payload = self._safe_json(response)
        if not isinstance(payload, dict):
            return {"success": False, "message": f"HTTP {response.status_code}"}
        if not payload.get("success"):
            return {"success": False, "message": payload.get("message") or f"HTTP {response.status_code}", "data": payload.get("data")}
        return {"success": True, "message": payload.get("message") or "success", "data": payload.get("data") or {}}

    def _parse_siqi_page(self, html: str, url: str) -> Dict[str, Any]:
        imagehash_match = re.search(r'name="imagehash"\s+value="([a-f0-9]+)"', html, re.IGNORECASE)
        captcha_match = re.search(r"captchaString\s*=\s*'([^']+)'", html)
        form_match = re.search(r'<form[^>]*action=["\']([^"\']*)', html, re.IGNORECASE)
        return {
            "invalid_cookie": ("未登录" in html) or ("登录" in html and "注册" in html),
            "signed": "签到成功" in html,
            "imagehash": imagehash_match.group(1) if imagehash_match else "",
            "captcha": captcha_match.group(1) if captcha_match else "",
            "form_action": urljoin(url, form_match.group(1)) if form_match and form_match.group(1) else url,
            "sign_count": self._pick_first_group(html, r"第\s*<b>\s*(\d+)\s*</b>\s*次签到"),
            "consecutive_days": self._pick_first_group(html, r"连续签到\s*<b>\s*(\d+)\s*</b>\s*天"),
            "reward_amount": self._pick_first_group(html, r"本次签到获得\s*<b>\s*(\d+)\s*</b>\s*个魔力"),
        }

    def _siqi_success_result(self, info: Dict[str, Any], changed: bool) -> Dict[str, Any]:
        count = info.get("sign_count") or "?"
        cons = info.get("consecutive_days") or "?"
        reward = info.get("reward_amount") or "?"
        status = f"签到成功，第 {count} 次，连续 {cons} 天，获得 {reward} 魔力。"
        if not changed:
            status = f"今日已签到，第 {count} 次，连续 {cons} 天，获得 {reward} 魔力。"
        return self._success_result(
            "签到完成" if changed else "今日已签到",
            status,
            metrics=self._siqi_metrics(info),
        )

    def _siqi_metrics(self, info: Dict[str, Any]) -> List[Dict[str, str]]:
        return [
            {"label": "累计次数", "value": str(info.get("sign_count") or "?")},
            {"label": "连续天数", "value": str(info.get("consecutive_days") or "?")},
            {"label": "本次奖励", "value": str(info.get("reward_amount") or "?")},
        ]

    def _parse_hnr_page(self, html: str) -> Dict[str, Any]:
        reward_names = {
            "reward_10": "前10名奖励",
            "reward_20": "前20名奖励",
            "reward_30": "前30名奖励",
            "reward_50": "前50名奖励",
            "reward_100": "前100名奖励",
            "reward_200": "前200名奖励",
            "welfare": "福利奖励",
        }
        claims = []
        for reward_type, amount in re.findall(r"claimReward\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(\d+)\s*\)", html):
            claims.append(
                {
                    "reward_type": reward_type,
                    "amount": int(amount),
                    "label": reward_names.get(reward_type, reward_type),
                }
            )
        return {
            "invalid_cookie": ("未登录" in html) or ("登录" in html and "注册" in html),
            "rank": self._pick_first_group(html, r"当前排名[：:]\s*<span[^>]*>\s*(\d+)"),
            "next_time": self._pick_first_group(html, r"下次领取[：:]\s*([\d:\- ]+)"),
            "claims": claims,
        }

    def _build_dashboard(self, states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        site_map: Dict[str, Dict[str, Any]] = {}
        success_count = 0
        error_count = 0
        auto_count = 0

        for card in self._cards:
            module_meta = self._module_meta(card["module_key"])
            state = dict(states.get(card["id"]) or self._placeholder_state(card))
            state.update(
                {
                    "title": card["title"],
                    "site_name": card["site_name"],
                    "site_url": card["site_url"],
                    "module_name": module_meta["label"],
                    "module_icon": module_meta["icon"],
                    "enabled": card["enabled"],
                    "auto_run": card["auto_run"],
                    "cron": self._get_card_cron(card),
                    "next_run_time": self._format_time(self._get_card_next_run(card)) if self._card_schedule_enabled(card) else "",
                    "notify": card["notify"],
                    "tone": card["tone"],
                    "note": card.get("note") or "",
                    "uid": card.get("uid") or "",
                    "cookie_configured": bool(card.get("cookie")),
                }
            )
            state["tags"] = self._build_card_tags(card)
            if state.get("last_success"):
                success_count += 1
            if state.get("level") == "error":
                error_count += 1
            if card.get("auto_run"):
                auto_count += 1
            site_key = self._site_group_key(card)
            if site_key not in site_map:
                site_map[site_key] = {
                    "site_key": site_key,
                    "site_name": card["site_name"],
                    "site_url": card["site_url"],
                    "subtitle": "",
                    "modules": {},
                }
            module_key = card["module_key"]
            site_group = site_map[site_key]
            if module_key not in site_group["modules"]:
                module_meta = self._module_meta(module_key)
                site_group["modules"][module_key] = {
                    "module_key": module_key,
                    "module_name": module_meta["label"],
                    "module_icon": module_meta["icon"],
                    "cards": [],
                }
            site_group["modules"][module_key]["cards"].append(state)

        groups: List[Dict[str, Any]] = []
        for item in site_map.values():
            modules = list(item["modules"].values())
            card_total = sum(len(group["cards"]) for group in modules)
            item["subtitle"] = f"{card_total} 张状态卡片"
            item["modules"] = modules
            groups.append(item)

        groups.sort(key=lambda item: f"{item['site_name']}|{item['site_url']}".lower())
        module_sections = self._build_module_sections(groups)

        overview = [
            {"label": "模块数量", "value": str(len(module_sections))},
            {"label": "配置卡片", "value": str(len(self._cards))},
            {"label": "自动执行", "value": str(auto_count)},
            {"label": "成功状态", "value": str(success_count)},
            {"label": "异常状态", "value": str(error_count)},
        ]

        return {
            "schema_version": self.plugin_version,
            "cards_version": self._cards_fingerprint(),
            "title": "模块状态页",
            "subtitle": "按模块拆分状态、调度与最近执行记录，固定任务和多站点任务各自独立展示。",
            "next_run_time": self._format_time(self._load_next_run_time()) if self._enabled else "",
            "next_trigger_time": self._format_time(self._load_next_trigger_time()) if self._enabled else "",
            "next_trigger_mode": self._load_next_trigger_mode(),
            "overview": overview,
            "groups": groups,
            "module_sections": module_sections,
            "hidden_count": "0",
            "history": [],
            "module_options": list(self.MODULES),
            "tone_options": list(self.TONES),
        }

    def _build_module_sections(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        history_map = self._build_module_history_map(self.get_data("history") or [])
        bucket: Dict[str, Dict[str, Any]] = {}
        for module_meta in self.MODULES:
            bucket[module_meta["key"]] = {
                "module_key": module_meta["key"],
                "module_name": module_meta["label"],
                "module_icon": module_meta["icon"],
                "singleton": bool(module_meta.get("singleton")),
                "tone": module_meta.get("tone") or "azure",
                "cards": [],
                "history": list(history_map.get(module_meta["key"]) or []),
                "stats": [],
                "latest_run": "",
            }

        for group in groups:
            for module in group.get("modules") or []:
                target = bucket.get(module.get("module_key") or "")
                if not target:
                    continue
                cards = list(module.get("cards") or [])
                cards.sort(key=lambda item: f"{item.get('site_name') or ''}|{item.get('title') or ''}".lower())
                target["cards"].extend(cards)

        sections: List[Dict[str, Any]] = []
        for section in bucket.values():
            cards = list(section.get("cards") or [])
            history = list(section.get("history") or [])[:8]
            if not cards and not history:
                continue
            enabled_count = sum(1 for card in cards if card.get("enabled"))
            auto_count = sum(1 for card in cards if card.get("auto_run"))
            error_count = sum(1 for card in cards if card.get("level") == "error")
            latest_values = [str(card.get("last_run") or "") for card in cards if card.get("last_run")]
            latest_values.extend(str(item.get("time") or "") for item in history if item.get("time"))
            section["latest_run"] = max(latest_values) if latest_values else ""
            section["history"] = history
            section["stats"] = [
                {"label": "卡片", "value": str(len(cards))},
                {"label": "启用", "value": str(enabled_count)},
                {"label": "定时", "value": str(auto_count)},
                {"label": "异常", "value": str(error_count)},
            ]
            sections.append(section)
        return sections

    def _placeholder_state(self, card: Dict[str, Any]) -> Dict[str, Any]:
        module_meta = self._module_meta(card["module_key"])
        if not card.get("enabled"):
            level = "info"
            title = "已停用"
            text = "卡片已停用，不参与自动执行。"
        elif not card.get("cookie"):
            level = "warning"
            title = "待配置 Cookie"
            text = "请先填写 Cookie。"
        elif card["module_key"] == "newapi_checkin" and not card.get("uid"):
            level = "warning"
            title = "待配置 UID"
            text = "New API 签到卡片需要填写 UID。"
        else:
            level = "info"
            title = "等待刷新"
            text = "可先执行“刷新状态”拉取当前站点信息。"
        return {
            "card_id": card["id"],
            "title": card["title"],
            "site_name": card["site_name"],
            "site_url": card["site_url"],
            "module_key": card["module_key"],
            "module_name": module_meta["label"],
            "module_icon": module_meta["icon"],
            "tone": card["tone"],
            "tone_label": self._tone_label(card["tone"]),
            "enabled": card["enabled"],
            "auto_run": card["auto_run"],
            "cron": self._get_card_cron(card),
            "next_run_time": self._format_time(self._get_card_next_run(card)) if self._card_schedule_enabled(card) else "",
            "show_status": card["show_status"],
            "notify": card["notify"],
            "level": level,
            "status_title": title,
            "status_text": text,
            "detail_lines": [card.get("note") or ""] if card.get("note") else [],
            "metrics": [],
            "tags": self._build_card_tags(card),
            "last_success": False,
            "last_run": "",
            "last_checked": "",
            "uid": card.get("uid") or "",
            "cookie_configured": bool(card.get("cookie")),
            "note": card.get("note") or "",
        }

    def _result_to_state(
        self,
        card: Dict[str, Any],
        result: Dict[str, Any],
        previous: Optional[Dict[str, Any]] = None,
        record_run: bool = False,
    ) -> Dict[str, Any]:
        module_meta = self._module_meta(card["module_key"])
        now_text = self._format_time(self._aware_now())
        prev = previous or {}
        return {
            "card_id": card["id"],
            "title": card["title"],
            "site_name": card["site_name"],
            "site_url": card["site_url"],
            "module_key": card["module_key"],
            "module_name": module_meta["label"],
            "module_icon": module_meta["icon"],
            "tone": card["tone"],
            "tone_label": self._tone_label(card["tone"]),
            "enabled": card["enabled"],
            "auto_run": card["auto_run"],
            "cron": self._get_card_cron(card),
            "next_run_time": self._format_time(self._get_card_next_run(card)) if self._card_schedule_enabled(card) else "",
            "show_status": card["show_status"],
            "notify": card["notify"],
            "level": result.get("level") or "info",
            "status_title": result.get("status_title") or "状态未知",
            "status_text": result.get("status_text") or "未返回状态描述",
            "detail_lines": [line for line in (result.get("detail_lines") or []) if line],
            "metrics": result.get("metrics") or [],
            "tags": self._build_card_tags(card),
            "last_success": bool(result.get("success")),
            "last_run": now_text if record_run else str(prev.get("last_run") or ""),
            "last_checked": now_text,
            "uid": card.get("uid") or "",
            "cookie_configured": bool(card.get("cookie")),
            "note": card.get("note") or "",
        }

    def _append_history(self, state: Dict[str, Any]):
        history = self.get_data("history") or []
        lines = [state.get("status_text") or ""]
        lines.extend(state.get("detail_lines") or [])
        history.insert(
            0,
            {
                "time": self._format_time(self._aware_now()),
                "title": state.get("title") or state.get("site_name") or "",
                "level": state.get("level") or "info",
                "lines": [line for line in lines if line],
                "card_id": state.get("card_id") or "",
                "module_key": state.get("module_key") or "",
                "module_name": state.get("module_name") or "",
                "module_icon": state.get("module_icon") or "",
                "site_name": state.get("site_name") or "",
                "site_url": state.get("site_url") or "",
            },
        )
        self.save_data("history", history[: self.HISTORY_LIMIT])

    def _load_card_states(self) -> Dict[str, Dict[str, Any]]:
        data = self.get_data("card_states") or {}
        return data if isinstance(data, dict) else {}

    def _save_card_states(self, states: Dict[str, Dict[str, Any]]):
        current_ids = {card["id"] for card in self._cards}
        filtered = {card_id: state for card_id, state in states.items() if card_id in current_ids}
        self.save_data("card_states", filtered)

    def _select_cards_for_refresh(self, card_id: str = "") -> List[Dict[str, Any]]:
        if card_id:
            match = next((card for card in self._cards if card["id"] == card_id), None)
            return [match] if match else []
        return list(self._cards)

    def _select_cards_for_run(self, card_id: str = "", force: bool = False, reason: str = "manual") -> List[Dict[str, Any]]:
        if card_id:
            match = next((card for card in self._cards if card["id"] == card_id), None)
            if not match:
                return []
            if force:
                return [match]
            if not self._enabled or not match.get("enabled"):
                return []
            if reason == "scheduled-card" and not self._card_schedule_enabled(match):
                return []
            return [match]

        cards = [card for card in self._cards if card.get("enabled")]
        if not force and not self._enabled:
            return []
        if reason in {"scheduled", "scheduled-card"}:
            cards = [card for card in cards if card.get("auto_run")]
        return cards

    def _normalize_cards(self, cards: Any) -> List[Dict[str, Any]]:
        source = cards if isinstance(cards, list) and cards else []
        fixed_cards: Dict[str, Dict[str, Any]] = {}
        newapi_cards: List[Dict[str, Any]] = []
        seen_ids: set = set()

        for index, item in enumerate(source):
            if not isinstance(item, dict):
                continue
            card = self._normalize_card(item, fallback_id=f"card-{index + 1}")
            module_key = card.get("module_key") or ""
            if self._module_is_singleton(module_key):
                if module_key not in fixed_cards:
                    fixed_cards[module_key] = card
                continue
            while card["id"] in seen_ids:
                card["id"] = f"{card['id']}-{index + 1}"
            seen_ids.add(card["id"])
            newapi_cards.append(card)

        normalized: List[Dict[str, Any]] = []
        for module_key in ["siqi_sign", "hnr_claim"]:
            normalized.append(fixed_cards.get(module_key) or self._fixed_card_template(module_key))

        normalized.extend(newapi_cards or [self._newapi_card_template()])
        return normalized

    def _normalize_card(self, item: Dict[str, Any], fallback_id: str) -> Dict[str, Any]:
        module_key = str(item.get("module_key") or item.get("module") or "siqi_sign").strip() or "siqi_sign"
        module_meta = self._module_meta(module_key)
        is_singleton = self._module_is_singleton(module_key)
        site_url = self._normalize_site_url(item.get("site_url") or module_meta["default_site_url"])
        site_name = str(item.get("site_name") or module_meta["default_site_name"]).strip() or module_meta["default_site_name"]
        title = str(item.get("title") or module_meta["label"]).strip() or module_meta["label"]
        tone = str(item.get("tone") or module_meta.get("tone") or "azure").strip().lower()
        if tone not in {item["key"] for item in self.TONES}:
            tone = str(module_meta.get("tone") or "azure")
        if is_singleton:
            site_url = self._normalize_site_url(module_meta["default_site_url"])
            site_name = str(module_meta["default_site_name"]).strip()
            title = module_meta["label"]
        return {
            "id": self._safe_card_id(module_key if is_singleton else (item.get("id") or fallback_id)),
            "title": title,
            "module_key": module_key,
            "site_name": site_name,
            "site_url": site_url,
            "enabled": self._to_bool(item.get("enabled", False)),
            "auto_run": self._to_bool(item.get("auto_run", True)),
            "cron": str(item.get("cron") or item.get("schedule_cron") or self._cron or self.DEFAULT_CRON).strip() or self.DEFAULT_CRON,
            "show_status": True,
            "notify": self._to_bool(item.get("notify", True)),
            "tone": tone,
            "cookie": str(item.get("cookie") or "").strip(),
            "uid": "" if is_singleton else str(item.get("uid") or "").strip(),
            "note": str(item.get("note") or "").strip(),
        }

    def _build_session(self, card: Dict[str, Any]) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self._http_retry_times,
            connect=self._http_retry_times,
            read=self._http_retry_times,
            status=self._http_retry_times,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(["HEAD", "GET", "POST", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.trust_env = self._use_proxy

        headers: Dict[str, str] = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Connection": "keep-alive",
            "Cookie": card.get("cookie") or "",
        }
        if card.get("module_key") == "newapi_checkin":
            headers.update(
                {
                    "Accept": "application/json, text/plain, */*",
                    "Origin": card["site_url"],
                    "Referer": f"{card['site_url'].rstrip('/')}/console/personal",
                    "new-api-user": str(card.get("uid") or ""),
                }
            )
        session.headers.update(headers)
        session.cookies.update(self._parse_cookie(card.get("cookie") or ""))
        return session

    def _save_schedule_meta(self):
        next_run = self._get_next_run_time()
        next_run_text = self._format_time(next_run) if next_run else ""
        self.save_data("next_run_time", next_run_text)
        self.save_data("next_trigger_time", next_run_text)
        self.save_data("next_trigger_mode", "card-cron" if next_run else "")

    def _load_next_run_time(self) -> Optional[datetime]:
        raw = self.get_data("next_run_time")
        return self._parse_datetime(raw)

    def _load_next_trigger_time(self) -> Optional[datetime]:
        raw = self.get_data("next_trigger_time")
        return self._parse_datetime(raw)

    def _load_next_trigger_mode(self) -> str:
        return str(self.get_data("next_trigger_mode") or "")

    def _get_next_run_time(self) -> Optional[datetime]:
        if not self._enabled:
            return None
        next_runs = [self._get_card_next_run(card) for card in self._cards if self._card_schedule_enabled(card)]
        next_runs = [item for item in next_runs if item]
        return min(next_runs) if next_runs else None

    def _reregister_plugin(self, reason: str = ""):
        try:
            Scheduler().update_plugin_job(self.__class__.__name__)
            if reason:
                logger.info("%s 已刷新调度：%s", self.plugin_name, reason)
        except Exception as err:
            logger.warning("%s 刷新调度失败：%s", self.plugin_name, err)

    def _module_meta(self, module_key: str) -> Dict[str, str]:
        for item in self.MODULES:
            if item["key"] == module_key:
                return item
        return self.MODULES[0]

    def _module_is_singleton(self, module_key: str) -> bool:
        return bool(self._module_meta(module_key).get("singleton"))

    def _tone_label(self, tone_key: str) -> str:
        for item in self.TONES:
            if item["key"] == tone_key:
                return item["label"]
        return self.TONES[0]["label"]

    def _build_card_tags(self, card: Dict[str, Any]) -> List[str]:
        tags = []
        tags.append("已启用" if card.get("enabled") else "已停用")
        if card.get("auto_run"):
            tags.append("定时运行" if self._has_valid_card_cron(card) else "Cron 无效")
        else:
            tags.append("仅手动执行")
        if card.get("cookie"):
            tags.append("Cookie 已配置")
        if card.get("notify"):
            tags.append("发送通知")
        if card.get("module_key") == "newapi_checkin" and card.get("uid"):
            tags.append(f"UID {card['uid']}")
        return tags

    def _site_group_key(self, card: Dict[str, Any]) -> str:
        return f"{card.get('site_name') or ''}|{card.get('site_url') or ''}".lower()

    def _cards_fingerprint(self) -> str:
        values = []
        for card in self._cards:
            values.append(
                "|".join(
                    [
                        str(card.get("id") or ""),
                        str(card.get("title") or ""),
                        str(card.get("module_key") or ""),
                        str(card.get("site_name") or ""),
                        str(card.get("site_url") or ""),
                        str(card.get("enabled") or False),
                        str(card.get("auto_run") or False),
                        str(card.get("cron") or ""),
                        str(card.get("show_status") or False),
                        str(card.get("notify") or False),
                        str(card.get("tone") or ""),
                        str(bool(card.get("cookie"))),
                        str(card.get("uid") or ""),
                    ]
                )
            )
        return "||".join(values)

    def _build_module_history_map(self, history_items: Any) -> Dict[str, List[Dict[str, Any]]]:
        bucket: Dict[str, List[Dict[str, Any]]] = {item["key"]: [] for item in self.MODULES}
        if not isinstance(history_items, list):
            return bucket
        for item in history_items:
            if not isinstance(item, dict):
                continue
            module_key = str(item.get("module_key") or "").strip()
            if module_key not in bucket:
                title = str(item.get("title") or "")
                if "🎁" in title or "HNR" in title:
                    module_key = "hnr_claim"
                elif "🪪" in title or "思齐" in title:
                    module_key = "siqi_sign"
                elif "🤖" in title:
                    module_key = "newapi_checkin"
            if module_key not in bucket:
                continue
            bucket[module_key].append(item)
        return bucket

    def _get_card_cron(self, card: Dict[str, Any]) -> str:
        return str(card.get("cron") or "").strip()

    def _get_card_trigger(self, card: Dict[str, Any]) -> Optional[CronTrigger]:
        if not self._card_schedule_enabled(card):
            return None
        return self._parse_card_cron(self._get_card_cron(card), title=str(card.get("title") or card.get("id") or ""))

    def _has_valid_card_cron(self, card: Dict[str, Any]) -> bool:
        return bool(self._parse_card_cron(self._get_card_cron(card)))

    def _card_schedule_enabled(self, card: Dict[str, Any]) -> bool:
        return bool(self._enabled and card.get("enabled") and card.get("auto_run") and self._get_card_cron(card))

    def _get_card_next_run(self, card: Dict[str, Any]) -> Optional[datetime]:
        trigger = self._parse_card_cron(self._get_card_cron(card))
        if not trigger:
            return None
        try:
            return trigger.get_next_fire_time(None, self._aware_now())
        except Exception:
            return None

    def _parse_card_cron(self, cron_text: str, title: str = "") -> Optional[CronTrigger]:
        if not cron_text:
            return None
        try:
            return CronTrigger.from_crontab(cron_text, timezone=pytz.timezone(settings.TZ))
        except Exception as err:
            if title:
                logger.warning("%s 卡片 Cron 无效：%s -> %s", self.plugin_name, title, err)
            return None

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except Exception:
            return None

    @staticmethod
    def _parse_cookie(cookie_str: str) -> Dict[str, str]:
        cookies: Dict[str, str] = {}
        for item in str(cookie_str or "").split(";"):
            chunk = item.strip()
            if not chunk or "=" not in chunk:
                continue
            name, value = chunk.split("=", 1)
            cookies[name.strip()] = value.strip()
        return cookies

    @staticmethod
    def _pick_first_group(text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _normalize_site_url(url: Any) -> str:
        text = str(url or "").strip()
        if not text:
            return ""
        if not text.startswith("http://") and not text.startswith("https://"):
            text = f"https://{text.lstrip('/')}"
        return text.rstrip("/")

    @staticmethod
    def _safe_card_id(value: Any) -> str:
        text = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").strip()).strip("-").lower()
        return text or "card"

    @staticmethod
    def _format_newapi_money(raw: Any) -> str:
        value = float(raw or 0) / 500000
        text = f"{value:.2f}".rstrip("0").rstrip(".")
        return f"${text}"

    def _format_newapi_stats(self, stats: Dict[str, Any]) -> str:
        total_checkins = stats.get("total_checkins") or stats.get("checkin_count") or "未知"
        total_quota = self._format_newapi_money(stats.get("total_quota") or 0)
        month_quota = 0
        for item in stats.get("records") or []:
            month_quota += float(item.get("quota_awarded") or 0)
        month_quota_text = self._format_newapi_money(month_quota)
        return f"累计签到 {total_checkins} 天 | 本月 {month_quota_text} | 累计 {total_quota}"

    def _newapi_metrics(self, stats: Dict[str, Any]) -> List[Dict[str, str]]:
        total_checkins = stats.get("total_checkins") or stats.get("checkin_count") or "未知"
        total_quota = self._format_newapi_money(stats.get("total_quota") or 0)
        month_quota = 0
        for item in stats.get("records") or []:
            month_quota += float(item.get("quota_awarded") or 0)
        return [
            {"label": "累计签到", "value": str(total_checkins)},
            {"label": "本月额度", "value": self._format_newapi_money(month_quota)},
            {"label": "累计额度", "value": total_quota},
        ]

    def _success_result(
        self,
        status_title: str,
        status_text: str,
        metrics: Optional[List[Dict[str, str]]] = None,
        detail_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return self._build_result(True, "success", status_title, status_text, metrics, detail_lines)

    def _warning_result(
        self,
        status_title: str,
        status_text: str,
        metrics: Optional[List[Dict[str, str]]] = None,
        detail_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return self._build_result(False, "warning", status_title, status_text, metrics, detail_lines)

    def _info_result(
        self,
        status_title: str,
        status_text: str,
        metrics: Optional[List[Dict[str, str]]] = None,
        detail_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return self._build_result(True, "info", status_title, status_text, metrics, detail_lines)

    def _error_result(
        self,
        status_title: str,
        status_text: str,
        metrics: Optional[List[Dict[str, str]]] = None,
        detail_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return self._build_result(False, "error", status_title, status_text, metrics, detail_lines)

    @staticmethod
    def _build_result(
        success: bool,
        level: str,
        status_title: str,
        status_text: str,
        metrics: Optional[List[Dict[str, str]]] = None,
        detail_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "success": success,
            "level": level,
            "status_title": status_title,
            "status_text": status_text,
            "metrics": metrics or [],
            "detail_lines": [line for line in (detail_lines or []) if line],
        }

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

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

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
        return str(err) or err.__class__.__name__
