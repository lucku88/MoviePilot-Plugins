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
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import NotificationType


class SQFarm(_PluginBase):
    plugin_name = "SQ种菜"
    plugin_desc = "自动收菜、售出背包作物并补种思齐农场。"
    plugin_icon = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f331.png"
    plugin_version = "0.1.0"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "sqfarm_"
    plugin_order = 66
    auth_level = 2

    _scheduler: Optional[BackgroundScheduler] = None

    _enabled: bool = False
    _notify: bool = True
    _onlyonce: bool = False
    _cron: str = "*/5 * * * *"
    _cookie: str = ""
    _ocr_api_url: str = "http://10.10.10.10:8089/api/tr-run/"
    _prefer_seed: str = "西红柿"
    _wait_window_seconds: int = 90
    _random_delay_max_seconds: int = 5
    _http_timeout: int = 12
    _http_retry_times: int = 3
    _http_retry_delay: int = 1500
    _ocr_retry_times: int = 2
    _force_ipv4: bool = True

    _crop_icon = {
        "萝卜": "🥕",
        "西红柿": "🍅",
        "玉米": "🌽",
        "茄子": "🍆",
        "蘑菇": "🍄",
        "樱桃": "🍒",
    }

    def init_plugin(self, config: dict = None):
        self.stop_service()

        if config:
            self._enabled = bool(config.get("enabled"))
            self._notify = bool(config.get("notify", True))
            self._onlyonce = bool(config.get("onlyonce"))
            self._cron = config.get("cron") or "*/5 * * * *"
            self._cookie = (config.get("cookie") or "").strip()
            self._ocr_api_url = (config.get("ocr_api_url") or self._ocr_api_url).strip()
            self._prefer_seed = (config.get("prefer_seed") or "西红柿").strip()
            self._wait_window_seconds = self._safe_int(config.get("wait_window_seconds"), 90)
            self._random_delay_max_seconds = self._safe_int(config.get("random_delay_max_seconds"), 5)
            self._http_timeout = self._safe_int(config.get("http_timeout"), 12)
            self._http_retry_times = self._safe_int(config.get("http_retry_times"), 3)
            self._http_retry_delay = self._safe_int(config.get("http_retry_delay"), 1500)
            self._ocr_retry_times = self._safe_int(config.get("ocr_retry_times"), 2)
            self._force_ipv4 = bool(config.get("force_ipv4", True))

        if self._enabled or self._onlyonce:
            if self._onlyonce:
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                logger.info("%s 服务启动，立即运行一次", self.plugin_name)
                self._scheduler.add_job(
                    func=self.run_job,
                    trigger="date",
                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                    name=self.plugin_name,
                )
                self._onlyonce = False
                self._update_config()
                if self._scheduler.get_jobs():
                    self._scheduler.print_jobs()
                    self._scheduler.start()

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        if self._enabled and self._cron:
            try:
                return [{
                    "id": "SQFarm",
                    "name": "SQ种菜定时服务",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self.run_job,
                    "kwargs": {},
                }]
            except Exception as err:
                logger.error("SQ种菜 CRON 配置错误：%s", err)
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            self._switch_col("enabled", "启用插件"),
                            self._switch_col("notify", "发送通知"),
                            self._switch_col("onlyonce", "立即运行一次"),
                            self._switch_col("force_ipv4", "优先 IPv4"),
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            self._text_col("cron", "轮询 CRON", "如 */5 * * * *", 4),
                            self._text_col("wait_window_seconds", "到点等待窗口(秒)", "90", 4),
                            self._text_col("random_delay_max_seconds", "随机延迟上限(秒)", "5", 4),
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            self._text_col("http_timeout", "HTTP 超时(秒)", "12", 3),
                            self._text_col("http_retry_times", "网络重试次数", "3", 3),
                            self._text_col("ocr_retry_times", "OCR 重试次数", "2", 3),
                            self._text_col("prefer_seed", "优先种子名称", "西红柿", 3),
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            self._text_col("ocr_api_url", "OCR API 地址", "http://10.10.10.10:8089/api/tr-run/", 12),
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [{
                                    "component": "VTextarea",
                                    "props": {
                                        "model": "cookie",
                                        "label": "SIQI_COOKIE",
                                        "rows": 6,
                                        "placeholder": "填入思齐站点 Cookie，例如 c_secure_pass=...",
                                    },
                                }],
                            }
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [{
                            "component": "VCol",
                            "props": {"cols": 12},
                            "content": [{
                                "component": "VAlert",
                                "props": {
                                    "type": "info",
                                    "variant": "tonal",
                                    "text": "这个插件通过 CRON 轮询，并结合上次 next_run_time 决定是否等待到点执行。OCR API 需要从 MoviePilot 环境内可访问。",
                                },
                            }],
                        }],
                    },
                ],
            }
        ], {
            "enabled": False,
            "notify": True,
            "onlyonce": False,
            "force_ipv4": True,
            "cron": "*/5 * * * *",
            "wait_window_seconds": 90,
            "random_delay_max_seconds": 5,
            "http_timeout": 12,
            "http_retry_times": 3,
            "http_retry_delay": 1500,
            "ocr_retry_times": 2,
            "prefer_seed": "西红柿",
            "ocr_api_url": "http://10.10.10.10:8089/api/tr-run/",
            "cookie": "",
        }

    def get_page(self) -> List[dict]:
        state = self.get_data("state") or {}
        history = self.get_data("history") or []

        if not state and not history:
            return [{
                "component": "div",
                "text": "暂无数据",
                "props": {"class": "text-center"},
            }]

        contents: List[dict] = []

        if state:
            summary_lines = state.get("summary") or []
            contents.append({
                "component": "VCard",
                "props": {"variant": "tonal"},
                "content": [
                    {"component": "VCardTitle", "text": "当前状态"},
                    {"component": "VCardText", "text": f"最近执行：{state.get('time') or '未知'}"},
                    {"component": "VCardText", "text": f"下次可收：{state.get('next_run_time') or '未知'}"},
                    {"component": "VCardText", "text": f"当前魔力：{(state.get('user') or {}).get('bonus', '未知')}"},
                    {"component": "VCardText", "text": f"已收获总数：{(state.get('user') or {}).get('total_harvest', '未知')}"},
                    {"component": "VCardText", "text": "结果：" + (" / ".join(summary_lines) if summary_lines else "无")},
                ],
            })

        for item in history[:10]:
            contents.append({
                "component": "VCard",
                "props": {"variant": "outlined"},
                "content": [
                    {"component": "VCardTitle", "text": item.get("time") or "未知时间"},
                    {"component": "VCardText", "text": item.get("title") or "无标题"},
                    {"component": "VCardText", "text": "\n".join(item.get("lines") or ["无详情"])},
                ],
            })

        return [{
            "component": "div",
            "props": {"class": "grid gap-3 grid-info-card"},
            "content": contents,
        }]

    def run_job(self):
        run_start = time.time()
        logger.info("## 开始执行... %s", self._format_time(datetime.now()))
        try:
            if not self._cookie:
                raise ValueError("未配置 SIQI_COOKIE")

            if self._force_ipv4:
                urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

            rand_delay = random.randint(0, max(0, self._random_delay_max_seconds))
            if rand_delay:
                logger.info("INFO 随机延迟 %s 秒后执行...", rand_delay)
                time.sleep(rand_delay)

            if not self._wait_for_saved_next_time():
                return

            session = self._build_session()
            data = self._fetch_state(session)
            if not data or not data.get("success"):
                raise RuntimeError("获取状态失败，Cookie可能失效")

            now_sec = int(time.time())
            ready_plots = [
                plot for plot in (data.get("user_lands") or [])
                if plot.get("seed_id")
                and (plot.get("is_ready") == 1 or (plot.get("harvest_time") and int(plot.get("harvest_time")) <= now_sec))
            ]
            logger.info("INFO 成熟作物数量：%s", len(ready_plots))

            action_harvest = False
            action_sell = False
            action_plant = False
            harvest_snapshot = []

            if ready_plots:
                action_harvest = True
                harvested = self._harvest_all(session)
                data = self._fetch_state(session)
                if harvested:
                    harvest_snapshot = [
                        {
                            "name": item.get("name"),
                            "qty": int(item.get("quantity") or 0),
                            "unit": int(item.get("unit_reward") or 0),
                            "icon": self._crop_icon.get(item.get("name"), ""),
                        }
                        for item in (data.get("inventory") or [])
                    ]

            inventory = data.get("inventory") or []
            if inventory:
                action_sell = True
                logger.info("INFO 开始售出背包作物，共 %s 类...", len(inventory))
                for item in inventory:
                    try:
                        self._post_action(session, "sell_inventory", {
                            "seed_id": item.get("seed_id"),
                            "quantity": item.get("quantity"),
                        }, retry_network=False)
                    except Exception as err:
                        logger.warning("sell_inventory failed: %s", err)
                logger.info("INFO 售出完成")
                data = self._fetch_state(session)

            empty_count = self._count_empty_plots(data)
            logger.info("INFO 空地数量：%s", empty_count)
            if empty_count > 0:
                best_seed = self._pick_seed(data)
                if best_seed:
                    action_plant = True
                    logger.info("INFO 准备补种：%s", best_seed.get("name"))
                    try:
                        self._post_action(session, "plant_fill_empty", {"seed_id": best_seed.get("id")}, retry_network=False)
                        logger.info("INFO 补种完成：%s", best_seed.get("name"))
                        data = self._fetch_state(session)
                    except Exception as err:
                        logger.warning("plant_fill_empty failed: %s", err)

            next_run = self._compute_next_run(data)
            next_run_text = self._format_time(datetime.fromtimestamp(next_run))
            logger.info("INFO 下次可收时间：%s", next_run_text)

            log_result = self._parse_logs(data.get("user_logs") or [], run_start)
            msg_lines = self._build_result_lines(action_harvest, action_sell, action_plant, harvest_snapshot, log_result, next_run_text)

            state_record = self._build_state_record(data, next_run, msg_lines)
            self.save_data("state", state_record)
            self._append_history("🌱 SQ种菜报告" if len(msg_lines) > 1 else "ℹ️ SQ种菜无动作", msg_lines or ["本次无动作"])

            if self._notify and len(msg_lines) > 1:
                text = "\n".join(msg_lines)
                logger.info("INFO 通知内容：\n%s", text)
                self.post_message(mtype=NotificationType.Plugin, title=f"🌱 {self.plugin_name}报告", text=text)

        except Exception as err:
            detail = self._get_error_detail(err)
            logger.exception("SQ种菜执行失败：%s", detail)
            self._append_history(f"❌ {self.plugin_name}异常", [f"⚠️ {detail}"])
            if self._notify:
                self.post_message(mtype=NotificationType.Plugin, title=f"❌ {self.plugin_name}异常", text=f"⚠️ {detail}")
        finally:
            cost_sec = max(1, round(time.time() - run_start))
            logger.info("## 执行结束... %s  耗时 %s 秒", self._format_time(datetime.now()), cost_sec)

    def stop_service(self):
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as err:
            logger.error("退出插件失败：%s", err)

    def _update_config(self):
        self.update_config({
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "cron": self._cron,
            "cookie": self._cookie,
            "ocr_api_url": self._ocr_api_url,
            "prefer_seed": self._prefer_seed,
            "wait_window_seconds": self._wait_window_seconds,
            "random_delay_max_seconds": self._random_delay_max_seconds,
            "http_timeout": self._http_timeout,
            "http_retry_times": self._http_retry_times,
            "http_retry_delay": self._http_retry_delay,
            "ocr_retry_times": self._ocr_retry_times,
            "force_ipv4": self._force_ipv4,
        })

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _format_time(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _switch_col(model: str, label: str) -> dict:
        return {
            "component": "VCol",
            "props": {"cols": 12, "md": 3},
            "content": [{
                "component": "VSwitch",
                "props": {"model": model, "label": label},
            }],
        }

    @staticmethod
    def _text_col(model: str, label: str, placeholder: str, md: int = 4) -> dict:
        return {
            "component": "VCol",
            "props": {"cols": 12, "md": md},
            "content": [{
                "component": "VTextField",
                "props": {"model": model, "label": label, "placeholder": placeholder},
            }],
        }

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
        session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Cookie": self._cookie,
            "Referer": "https://si-qi.xyz/plant_game.php",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        })
        return session

    def _fetch_state(self, session: requests.Session) -> dict:
        response = self._request_with_retry(
            "fetchState",
            lambda: session.get("https://si-qi.xyz/plant_game.php?action=fetch", timeout=(self._http_timeout, self._http_timeout)),
        )
        response.raise_for_status()
        return response.json()

    def _post_action(self, session: requests.Session, action: str, payload: Optional[dict] = None,
                     retry_network: bool = False) -> dict:
        body = dict(payload or {})
        body["action"] = action

        def run():
            response = session.post(
                "https://si-qi.xyz/plant_game.php",
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

    def _wait_for_saved_next_time(self) -> bool:
        state = self.get_data("state") or {}
        next_run_text = state.get("next_run_time")
        if not next_run_text:
            return True
        try:
            next_run = datetime.strptime(next_run_text, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return True

        now = datetime.now()
        if now >= next_run:
            return True

        remain_seconds = int((next_run - now).total_seconds())
        if remain_seconds > self._wait_window_seconds:
            logger.info("INFO 未到收菜时间，跳过执行")
            logger.info("INFO 下次可运行：%s", next_run_text)
            return False

        logger.info("INFO 距离收菜时间 <= %s 秒，进入等待到点模式...", self._wait_window_seconds)
        while remain_seconds > 0:
            logger.info("INFO 剩余 %s 秒", remain_seconds)
            time.sleep(min(10, remain_seconds))
            remain_seconds = int((next_run - datetime.now()).total_seconds())
        time.sleep(0.3)
        logger.info("INFO 已到收菜时间，开始执行")
        return True

    def _recognize_captcha(self, session: requests.Session, image_content: bytes) -> str:
        best_text = ""
        best_confidence = 0.0
        for idx in range(1, self._ocr_retry_times + 1):
            try:
                response = session.post(
                    self._ocr_api_url,
                    files={"file": ("cap.jpg", image_content, "image/jpeg")},
                    timeout=(10, 30),
                )
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
                image_hash = captcha.get("imagehash")
                img_response = self._request_with_retry(
                    "captchaImage",
                    lambda: session.get(captcha.get("image_url"), timeout=(self._http_timeout, self._http_timeout)),
                )
                img_response.raise_for_status()
                code = self._recognize_captcha(session, img_response.content)
                if not code:
                    logger.warning("captcha OCR failed, retry...")
                    continue

                harvest_res = self._post_action(session, "harvest_all", {
                    "imagehash": image_hash,
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
            if enabled:
                total = int(effective.get(str(land_id)) or effective.get(land_id) or land.get("plot_count") or 0)
            else:
                total = int(land.get("plot_count") or 0)
            planted = len([plot for plot in user_lands if int(plot.get("land_id") or 0) == land_id and plot.get("seed_id")])
            empty += max(0, total - planted)
        return empty

    def _pick_seed(self, data: dict) -> Optional[dict]:
        total_harvest = int((data.get("user_stats") or {}).get("total_harvest") or 0)
        unlocked = [seed for seed in (data.get("seeds") or []) if total_harvest >= int(seed.get("unlock_harvest") or 0)]
        if not unlocked:
            return None
        unlocked.sort(
            key=lambda item: ((float(item.get("base_reward") or 0) - float(item.get("cost") or 0)) / max(float(item.get("grow_time") or 1), 1)),
            reverse=True,
        )
        for seed in unlocked:
            if str(seed.get("name")) == self._prefer_seed:
                return seed
        return unlocked[0]

    @staticmethod
    def _compute_next_run(data: dict) -> int:
        now = int(time.time())
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        future_times = []
        for plot in (data.get("user_lands") or []):
            plant_time = int(plot.get("plant_time") or 0)
            seed = seed_map.get(str(plot.get("seed_id")))
            grow_time = int((seed or {}).get("grow_time") or 0)
            if not plant_time or not grow_time:
                continue
            harvest_ts = plant_time + grow_time
            if harvest_ts > now:
                future_times.append(harvest_ts)
        return min(future_times) if future_times else now + 6 * 3600

    def _build_state_record(self, data: dict, next_run: int, summary_lines: List[str]) -> dict:
        seed_map = {str(seed.get("id")): seed for seed in (data.get("seeds") or [])}
        return {
            "time": self._format_time(datetime.now()),
            "next_run_time": self._format_time(datetime.fromtimestamp(next_run)),
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
                {
                    "name": item.get("name"),
                    "quantity": int(item.get("quantity") or 0),
                    "unit_reward": int(item.get("unit_reward") or 0),
                }
                for item in (data.get("inventory") or [])
            ],
            "logs": [
                {
                    "action": log.get("action"),
                    "seed": log.get("seed_name"),
                    "land": log.get("land_name"),
                    "time": log.get("created_at"),
                    "value": log.get("value"),
                }
                for log in (data.get("user_logs") or [])[:20]
            ],
        }

    def _build_result_lines(self, action_harvest: bool, action_sell: bool, action_plant: bool,
                            harvest_snapshot: List[dict], log_result: dict, next_run_text: str) -> List[str]:
        def format_summary(summary_map: dict) -> str:
            return "  ".join([f"{key}×{value}" for key, value in summary_map.items()])

        harvest_map = {}
        harvest_income = 0
        for item in harvest_snapshot:
            key = f"{item.get('icon', '')}{item.get('name', '')}"
            harvest_map[key] = harvest_map.get(key, 0) + int(item.get("qty") or 0)
            harvest_income += int(item.get("qty") or 0) * int(item.get("unit") or 0)

        lines: List[str] = []
        if action_harvest and harvest_map:
            lines.append(f"✅ 收菜：{format_summary(harvest_map)}")
        if harvest_income > 0:
            lines.append(f"💰 收益：{harvest_income} 魔力")
        elif log_result.get("income", 0) > 0:
            lines.append(f"💰 收益：{log_result.get('income')} 魔力")
        if action_sell and log_result.get("sell"):
            lines.append(f"🧺 售出：{format_summary(log_result.get('sell'))}")
        if action_plant and log_result.get("plant"):
            lines.append(f"🌱 种植：{format_summary(log_result.get('plant'))}")
        lines.append(f"⏰ 下次可收：{next_run_text}")
        return lines

    def _append_history(self, title: str, lines: List[str]):
        history = self.get_data("history") or []
        history.insert(0, {
            "time": self._format_time(datetime.now()),
            "title": title,
            "lines": lines,
        })
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
            icon = item.get("seed_icon") or ""
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
    def _get_error_detail(err: Exception) -> str:
        return str(err) or err.__class__.__name__

