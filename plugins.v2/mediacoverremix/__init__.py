import base64
import io
import json
import math
import random
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    RESAMPLING = getattr(Image, "Resampling", Image)
except Exception:
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageFont = None

    class _FallbackResampling:
        LANCZOS = 1

    RESAMPLING = _FallbackResampling()

from app.core.config import settings
from app.helper.mediaserver import MediaServerHelper
from app.log import logger
from app.plugins import _PluginBase


def _safe_int(value: Any, default: int, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        result = default
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


def _safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _safe_json(value: Any, default: Any) -> Any:
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


class MediaCoverRemix(_PluginBase):
    plugin_name = "媒体库封面生成魔改"
    plugin_desc = "读取 MoviePilot 已配置的飞牛影视媒体库，生成拼贴风格封面并尝试自动替换。"
    plugin_icon = "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/icons/emby.png"
    plugin_version = "0.1.0"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins/"
    plugin_config_prefix = "mediacoverremix_"
    plugin_order = 12
    auth_level = 1

    _scheduler: Optional[BackgroundScheduler] = None
    _mediaserver_helper: Optional[MediaServerHelper] = None
    _run_lock = threading.Lock()
    _stop_event = threading.Event()

    _enabled = False
    _notify = False
    _onlyonce = False
    _auto_upload = True
    _cron = ""
    _moviepilot_url = ""
    _moviepilot_api_token = ""
    _selected_servers: List[str] = []
    _include_libraries: List[str] = []
    _title_rules: List[Dict[str, str]] = []
    _image_count = 4
    _history_limit = 30
    _http_timeout = 20
    _poster_width = 1600
    _poster_height = 900
    _custom_bg_color = ""

    def __init__(self):
        super().__init__()

    def init_plugin(self, config: Optional[dict] = None):
        self.stop_service()
        self._mediaserver_helper = MediaServerHelper()

        merged = self._default_config()
        if config:
            merged.update(config)
        self._apply_config(merged)

        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            self._scheduler.add_job(
                func=self._run_once_job,
                trigger="date",
                run_date=self._aware_now() + timedelta(seconds=3),
                name=self.plugin_name,
            )
            self._onlyonce = False
            self._update_config()
            self._scheduler.start()

    def get_state(self) -> bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/config", "endpoint": self._get_config, "methods": ["GET"], "auth": "bear", "summary": "获取封面生成配置"},
            {"path": "/config", "endpoint": self._save_config, "methods": ["POST"], "auth": "bear", "summary": "保存封面生成配置"},
            {"path": "/status", "endpoint": self._get_status, "methods": ["GET"], "auth": "bear", "summary": "获取封面生成状态"},
            {"path": "/run", "endpoint": self._run_now, "methods": ["POST"], "auth": "bear", "summary": "立即执行封面生成"},
            {"path": "/refresh", "endpoint": self._refresh_status, "methods": ["POST"], "auth": "bear", "summary": "刷新媒体库缓存"},
            {"path": "/inspect", "endpoint": self._inspect_runtime, "methods": ["GET"], "auth": "bear", "summary": "查看飞牛服务探测结果"},
            {"path": "/stop", "endpoint": self._stop_now, "methods": ["POST"], "auth": "bear", "summary": "停止当前任务"},
        ]

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        return None, self._get_config()

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        return "vue", "dist/assets/assets"

    def get_page(self) -> List[dict]:
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        if not self._enabled or not self._cron:
            return []
        try:
            trigger = CronTrigger.from_crontab(self._cron)
        except Exception as err:
            logger.warning("%s Cron 无效：%s", self.plugin_name, err)
            return []
        return [{
            "id": "MediaCoverRemix",
            "name": "媒体库封面生成服务",
            "trigger": trigger,
            "func": self._scheduled_worker,
            "kwargs": {},
        }]

    def stop_service(self):
        self._stop_event.set()
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
        except Exception as err:
            logger.warning("%s 停止一次性调度失败：%s", self.plugin_name, err)
        self._scheduler = None
        self._stop_event.clear()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "notify": False,
            "onlyonce": False,
            "auto_upload": True,
            "cron": "",
            "moviepilot_url": "",
            "moviepilot_api_token": "",
            "selected_servers": [],
            "include_libraries": [],
            "title_rules": [],
            "image_count": 4,
            "history_limit": 30,
            "http_timeout": 20,
            "poster_width": 1600,
            "poster_height": 900,
            "custom_bg_color": "",
        }

    def _apply_config(self, config: Dict[str, Any]):
        self._enabled = _safe_bool(config.get("enabled"), False)
        self._notify = _safe_bool(config.get("notify"), False)
        self._onlyonce = _safe_bool(config.get("onlyonce"), False)
        self._auto_upload = _safe_bool(config.get("auto_upload"), True)
        self._cron = (config.get("cron") or "").strip()
        self._moviepilot_url = (config.get("moviepilot_url") or "").strip().rstrip("/")
        self._moviepilot_api_token = (config.get("moviepilot_api_token") or "").strip()
        self._selected_servers = [item for item in (config.get("selected_servers") or []) if item]
        self._include_libraries = [item for item in (config.get("include_libraries") or []) if item]
        self._title_rules = _safe_json(config.get("title_rules"), [])
        self._image_count = _safe_int(config.get("image_count"), 4, 1, 9)
        self._history_limit = _safe_int(config.get("history_limit"), 30, 5, 200)
        self._http_timeout = _safe_int(config.get("http_timeout"), 20, 5, 120)
        self._poster_width = _safe_int(config.get("poster_width"), 1600, 640, 2400)
        self._poster_height = _safe_int(config.get("poster_height"), 900, 360, 1800)
        self._custom_bg_color = (config.get("custom_bg_color") or "").strip()

    def _update_config(self):
        self.update_config({
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_upload": self._auto_upload,
            "cron": self._cron,
            "moviepilot_url": self._moviepilot_url,
            "moviepilot_api_token": self._moviepilot_api_token,
            "selected_servers": self._selected_servers,
            "include_libraries": self._include_libraries,
            "title_rules": self._title_rules,
            "image_count": self._image_count,
            "history_limit": self._history_limit,
            "http_timeout": self._http_timeout,
            "poster_width": self._poster_width,
            "poster_height": self._poster_height,
            "custom_bg_color": self._custom_bg_color,
        })

    def _get_config(self) -> Dict[str, Any]:
        library_options = self._collect_library_options()
        return {
            "enabled": self._enabled,
            "notify": self._notify,
            "onlyonce": self._onlyonce,
            "auto_upload": self._auto_upload,
            "cron": self._cron,
            "moviepilot_url": self._moviepilot_url,
            "moviepilot_api_token": self._moviepilot_api_token,
            "selected_servers": self._selected_servers,
            "include_libraries": self._include_libraries,
            "title_rules": self._title_rules,
            "image_count": self._image_count,
            "history_limit": self._history_limit,
            "http_timeout": self._http_timeout,
            "poster_width": self._poster_width,
            "poster_height": self._poster_height,
            "custom_bg_color": self._custom_bg_color,
            "server_options": self._collect_server_options(),
            "library_options": library_options,
            "rule_template": [{"match": "国产剧", "title": "国剧", "subtitle": "Chinese Drama"}],
            "notes": [
                "优先读取 MoviePilot 已配置的媒体服务器，当前重点支持飞牛影视 trimemedia。",
                "海报生成基于媒体库返回的 image_list 拼贴，不依赖 Jellyfin/Emby 的项目明细接口。",
                "自动替换会优先尝试从 MoviePilot 媒体服务器配置中提取飞牛鉴权，再调用 /image/temp/upload 和 /mdb/setPoster。",
            ],
        }

    def _save_config(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = self._default_config()
        payload.update(self._get_config())
        payload.update(data or {})
        payload.pop("server_options", None)
        payload.pop("library_options", None)
        payload.pop("rule_template", None)
        payload.pop("notes", None)
        self._apply_config(payload)
        self._update_config()
        return {"success": True, "message": "配置已保存", "config": self._get_config()}

    def _get_status(self) -> Dict[str, Any]:
        return self._build_status(refresh_libraries=False)

    def _refresh_status(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._build_status(refresh_libraries=True)

    def _run_now(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        reason = "manual"
        if isinstance(data, dict) and data.get("reason"):
            reason = str(data.get("reason"))
        return self._execute_run(force=True, reason=reason)

    def _stop_now(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._stop_event.set()
        return {"success": True, "message": "已发送停止信号"}

    def _run_once_job(self):
        self._execute_run(force=True, reason="onlyonce")

    def _scheduled_worker(self):
        self._execute_run(force=False, reason="schedule")

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    def _build_status(self, refresh_libraries: bool = False) -> Dict[str, Any]:
        history = list(self.get_data("history") or [])
        latest = self.get_data("latest_result") or {}
        inspect = self.get_data("inspect_result") or {}
        library_options = self._collect_library_options(force_refresh=refresh_libraries)
        return {
            "enabled": self._enabled,
            "running": _safe_bool(self.get_data("running"), False),
            "last_run": self.get_data("last_run"),
            "latest_result": latest,
            "history": history[: self._history_limit],
            "inspect": inspect,
            "library_options": library_options,
            "output_dir": str(self._output_dir()),
        }

    def _append_history(self, record: Dict[str, Any]):
        history = list(self.get_data("history") or [])
        history.insert(0, record)
        history = history[: self._history_limit]
        self.save_data("history", history)

    def _collect_server_options(self) -> List[Dict[str, str]]:
        options: List[Dict[str, str]] = []
        helper = self._mediaserver_helper or MediaServerHelper()
        try:
            configs = helper.get_configs() or {}
            iterator = configs.values() if isinstance(configs, dict) else configs
            for item in iterator:
                name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
                server_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
                if not name:
                    continue
                options.append({"title": f"{name} ({server_type or 'unknown'})", "value": name})
        except Exception as err:
            logger.warning("%s 获取媒体服务器配置失败：%s", self.plugin_name, err)
        if options:
            return options
        for item in self._fetch_moviepilot_clients():
            name = item.get("name")
            if name:
                options.append({"title": f"{name} ({item.get('type') or 'unknown'})", "value": name})
        return options

    def _collect_library_options(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        cache_key = "library_cache"
        if not force_refresh:
            cached = self.get_data(cache_key) or []
            if cached:
                return cached
        options: List[Dict[str, str]] = []
        selected = self._selected_servers or [item["value"] for item in self._collect_server_options()]
        for server_name in selected:
            for library in self._fetch_server_libraries(server_name):
                library_id = str(library.get("id") or "")
                if not library_id:
                    continue
                value = self._library_key(server_name, library_id)
                label = f"{server_name} / {library.get('name') or library_id}"
                library_type = library.get("type") or library.get("server_type") or "未知"
                options.append({"title": f"{label} ({library_type})", "value": value})
        self.save_data(cache_key, options)
        return options

    def _library_key(self, server_name: str, library_id: str) -> str:
        return f"{server_name}::{library_id}"

    def _execute_run(self, force: bool = False, reason: str = "manual") -> Dict[str, Any]:
        if not force and not self._enabled:
            return {"success": False, "message": "插件未启用", "status": self._build_status()}
        if not self._run_lock.acquire(blocking=False):
            return {"success": False, "message": "任务正在执行中", "status": self._build_status()}

        self._stop_event.clear()
        self.save_data("running", True)
        self.save_data("last_run", self._aware_now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            libraries = self._load_target_libraries()
            if not libraries:
                message = "没有找到可处理的媒体库，请先选择服务器或刷新媒体库缓存"
                result = {"success": False, "message": message, "items": []}
                self.save_data("latest_result", result)
                return {**result, "status": self._build_status()}

            items: List[Dict[str, Any]] = []
            success_count = 0
            upload_count = 0
            for library in libraries:
                if self._stop_event.is_set():
                    items.append({
                        "server": library.get("server_name"),
                        "library_id": library.get("id"),
                        "library_name": library.get("name"),
                        "success": False,
                        "uploaded": False,
                        "message": "任务已手动停止",
                    })
                    break
                item_result = self._process_library(library)
                items.append(item_result)
                if item_result.get("success"):
                    success_count += 1
                if item_result.get("uploaded"):
                    upload_count += 1

            message = f"已处理 {len(items)} 个媒体库，成功生成 {success_count} 个封面"
            if self._auto_upload:
                message += f"，自动替换成功 {upload_count} 个"
            result = {
                "success": success_count > 0,
                "message": message,
                "reason": reason,
                "items": items,
                "generated_count": success_count,
                "uploaded_count": upload_count,
                "finished_at": self._aware_now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.save_data("latest_result", result)
            self._append_history({
                "time": result["finished_at"],
                "reason": reason,
                "message": message,
                "generated_count": success_count,
                "uploaded_count": upload_count,
                "success": result["success"],
            })
            return {**result, "status": self._build_status()}
        except Exception as err:
            logger.exception("%s 执行失败：%s", self.plugin_name, err)
            result = {
                "success": False,
                "message": f"执行失败：{err}",
                "reason": reason,
                "items": [],
                "finished_at": self._aware_now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.save_data("latest_result", result)
            self._append_history({
                "time": result["finished_at"],
                "reason": reason,
                "message": result["message"],
                "generated_count": 0,
                "uploaded_count": 0,
                "success": False,
            })
            return {**result, "status": self._build_status()}
        finally:
            self.save_data("running", False)
            self._run_lock.release()
            self._stop_event.clear()

    def _load_target_libraries(self) -> List[Dict[str, Any]]:
        selected_servers = self._selected_servers or [item["value"] for item in self._collect_server_options()]
        allowed = set(self._include_libraries)
        libraries: List[Dict[str, Any]] = []
        for server_name in selected_servers:
            for library in self._fetch_server_libraries(server_name):
                library_id = str(library.get("id") or "")
                if not library_id:
                    continue
                library["server_name"] = server_name
                library["library_key"] = self._library_key(server_name, library_id)
                if allowed and library["library_key"] not in allowed:
                    continue
                libraries.append(library)
        return libraries

    def _moviepilot_base_url(self) -> str:
        if self._moviepilot_url:
            return self._moviepilot_url
        return "http://127.0.0.1:3000"

    def _moviepilot_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._moviepilot_api_token:
            headers["X-API-KEY"] = self._moviepilot_api_token
        return headers

    def _moviepilot_request(self, path: str, method: str = "GET", json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self._moviepilot_base_url()}{path}"
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=self._moviepilot_headers(),
            json=json_data,
            timeout=self._http_timeout,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_moviepilot_clients(self) -> List[Dict[str, Any]]:
        try:
            result = self._moviepilot_request("/api/v1/mediaserver/clients")
        except Exception as err:
            logger.warning("%s 读取 MoviePilot 媒体服务器列表失败：%s", self.plugin_name, err)
            return []
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        if isinstance(result, dict):
            return [result]
        return []

    def _fetch_server_libraries(self, server_name: str) -> List[Dict[str, Any]]:
        try:
            encoded = requests.utils.quote(server_name)
            result = self._moviepilot_request(f"/api/v1/mediaserver/library?server={encoded}")
        except Exception as err:
            logger.warning("%s 读取媒体库失败：%s / %s", self.plugin_name, server_name, err)
            return []
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        return []

    def _process_library(self, library: Dict[str, Any]) -> Dict[str, Any]:
        image_urls = [item for item in (library.get("image_list") or []) if item][: self._image_count]
        if not image_urls:
            return {
                "server": library.get("server_name"),
                "library_id": library.get("id"),
                "library_name": library.get("name"),
                "success": False,
                "uploaded": False,
                "message": "媒体库没有可用的 image_list",
            }

        output_file = self._output_dir() / f"{self._slugify(library.get('server_name'))}_{self._slugify(library.get('name'))}_{library.get('id')}.png"
        generated, generate_message = self._generate_cover(
            library_name=library.get("name") or str(library.get("id")),
            library_type=library.get("type") or library.get("server_type") or "",
            image_urls=image_urls,
            output_file=output_file,
        )
        uploaded = False
        upload_message = "未启用自动替换"
        if generated and self._auto_upload:
            uploaded, upload_message = self._upload_trimemedia_cover(library, output_file)

        result = {
            "server": library.get("server_name"),
            "library_id": library.get("id"),
            "library_name": library.get("name"),
            "success": generated,
            "uploaded": uploaded,
            "message": upload_message if generated else generate_message,
            "output_file": str(output_file),
            "output_name": output_file.name,
            "preview_url": self._to_preview_payload(output_file),
        }
        return result

    def _generate_cover(self, library_name: str, library_type: str, image_urls: List[str], output_file: Path) -> Tuple[bool, str]:
        self._ensure_pillow()
        images, errors = self._download_images(image_urls)
        if not images:
            detail = "; ".join(errors[:3]) if errors else "未下载到任何源图"
            return False, f"封面生成失败：{detail}"
        width = self._poster_width
        height = self._poster_height
        primary = images[0].copy().convert("RGB")
        background = self._build_background(primary, width, height)
        canvas = background.convert("RGBA")

        layout = self._compute_layout(len(images), width, height)
        for image, box in zip(images, layout):
            poster = self._fit_cover(image, box[2], box[3]).convert("RGBA")
            poster = self._rounded_image(poster, 28)
            shadow = self._make_shadow(box[2], box[3], 28)
            canvas.alpha_composite(shadow, (box[0] + 12, box[1] + 14))
            canvas.alpha_composite(poster, (box[0], box[1]))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [(60, height - 250), (width - 60, height - 60)],
            radius=34,
            fill=(12, 18, 32, 150),
        )
        canvas = Image.alpha_composite(canvas, overlay)

        title, subtitle = self._resolve_titles(library_name, library_type)
        title_font = self._load_font("ch.ttf", int(height * 0.095))
        sub_font = self._load_font("en.otf", int(height * 0.04))
        draw = ImageDraw.Draw(canvas)
        draw.text((100, height - 215), title, font=title_font, fill=(255, 255, 255, 245))
        if subtitle:
            draw.text((106, height - 126), subtitle, font=sub_font, fill=(227, 234, 247, 228))

        output_file.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(output_file, format="PNG", optimize=True)
        return True, "封面生成成功"

    def _ensure_pillow(self):
        if not all([Image, ImageDraw, ImageFilter, ImageFont]):
            raise RuntimeError("Pillow 未安装，无法生成媒体库封面")

    def _download_images(self, image_urls: List[str]) -> Tuple[List[Image.Image], List[str]]:
        images: List[Image.Image] = []
        errors: List[str] = []
        for url in image_urls:
            if self._stop_event.is_set():
                break
            try:
                response = requests.get(url, timeout=self._http_timeout)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                images.append(image)
            except Exception as err:
                logger.warning("%s 下载封面源图失败：%s / %s", self.plugin_name, url, err)
                errors.append(f"{url} -> {err}")
        return images, errors

    def _build_background(self, image: Image.Image, width: int, height: int) -> Image.Image:
        seed = image.resize((width, height), RESAMPLING.LANCZOS).filter(ImageFilter.GaussianBlur(30))
        seed = seed.convert("RGBA")
        dark = Image.new("RGBA", (width, height), (8, 12, 24, 175))
        seed = Image.alpha_composite(seed, dark)
        if self._custom_bg_color:
            custom = self._parse_hex_color(self._custom_bg_color)
            if custom:
                tint = Image.new("RGBA", (width, height), (*custom, 110))
                seed = Image.alpha_composite(seed, tint)
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        for idx in range(height):
            ratio = idx / max(height - 1, 1)
            alpha = int(110 * ratio)
            draw.line((0, idx, width, idx), fill=(4, 6, 14, alpha), width=1)
        return Image.alpha_composite(seed, gradient).convert("RGB")

    def _compute_layout(self, count: int, width: int, height: int) -> List[Tuple[int, int, int, int]]:
        count = max(1, min(count, 6))
        top = 78
        gap = 28
        card_w = 248
        card_h = 372
        total_w = count * card_w + (count - 1) * gap
        start_x = max(76, int((width - total_w) / 2))
        if total_w > width - 120:
            scale = (width - 120 - (count - 1) * gap) / max(count * card_w, 1)
            card_w = int(card_w * scale)
            card_h = int(card_h * scale)
            total_w = count * card_w + (count - 1) * gap
            start_x = max(60, int((width - total_w) / 2))
        boxes: List[Tuple[int, int, int, int]] = []
        for index in range(count):
            offset = int(abs((count - 1) / 2 - index) * 12)
            boxes.append((start_x + index * (card_w + gap), top + offset, card_w, card_h))
        return boxes

    def _fit_cover(self, image: Image.Image, target_w: int, target_h: int) -> Image.Image:
        src_w, src_h = image.size
        if src_w <= 0 or src_h <= 0:
            return Image.new("RGB", (target_w, target_h), (48, 54, 72))
        scale = max(target_w / src_w, target_h / src_h)
        resized = image.resize((int(src_w * scale), int(src_h * scale)), RESAMPLING.LANCZOS)
        left = max(0, int((resized.width - target_w) / 2))
        top = max(0, int((resized.height - target_h) / 2))
        return resized.crop((left, top, left + target_w, top + target_h))

    def _rounded_image(self, image: Image.Image, radius: int) -> Image.Image:
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
        rounded.paste(image, (0, 0))
        rounded.putalpha(mask)
        return rounded

    def _make_shadow(self, width: int, height: int, radius: int) -> Image.Image:
        shadow = Image.new("RGBA", (width + 24, height + 28), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        draw.rounded_rectangle([(8, 8), (width + 4, height + 6)], radius=radius, fill=(0, 0, 0, 120))
        return shadow.filter(ImageFilter.GaussianBlur(14))

    def _resolve_titles(self, library_name: str, library_type: str) -> Tuple[str, str]:
        title = library_name
        subtitle = library_type or ""
        for rule in self._title_rules:
            if not isinstance(rule, dict):
                continue
            match = (rule.get("match") or "").strip()
            if match and match in library_name:
                title = (rule.get("title") or title).strip() or title
                subtitle = (rule.get("subtitle") or subtitle).strip() or subtitle
                break
        if subtitle and not re.search(r"[A-Za-z]", subtitle):
            subtitle = subtitle.upper() if len(subtitle) <= 6 else subtitle
        return title, subtitle

    def _font_dir(self) -> Path:
        return Path(__file__).parent / "assets" / "fonts"

    def _load_font(self, filename: str, size: int) -> ImageFont.FreeTypeFont:
        font_path = self._font_dir() / filename
        try:
            return ImageFont.truetype(str(font_path), size=size)
        except Exception:
            return ImageFont.load_default()

    def _parse_hex_color(self, value: str) -> Optional[Tuple[int, int, int]]:
        match = re.fullmatch(r"#?([0-9a-fA-F]{6})", value.strip())
        if not match:
            return None
        raw = match.group(1)
        return tuple(int(raw[idx: idx + 2], 16) for idx in range(0, 6, 2))

    def _output_dir(self) -> Path:
        try:
            base = Path(self.get_data_path())
        except Exception:
            base = Path(__file__).parent / "data"
        output = base / "covers"
        output.mkdir(parents=True, exist_ok=True)
        return output

    def _slugify(self, value: Any) -> str:
        text = str(value or "").strip().lower()
        text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
        return text.strip("-") or "library"

    def _to_preview_payload(self, path: Path) -> str:
        try:
            self._ensure_pillow()
            image = Image.open(path).convert("RGB")
            image.thumbnail((420, 236), RESAMPLING.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=82)
            content = buffer.getvalue()
        except Exception:
            return ""
        encoded = base64.b64encode(content).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"

    def _inspect_runtime(self) -> Dict[str, Any]:
        helper = self._mediaserver_helper or MediaServerHelper()
        result: Dict[str, Any] = {
            "moviepilot_url": self._moviepilot_base_url(),
            "selected_servers": self._selected_servers,
            "configs": [],
            "services": [],
        }
        try:
            configs = helper.get_configs() or {}
            iterator = configs.items() if isinstance(configs, dict) else enumerate(configs)
            for key, item in iterator:
                info = self._object_summary(item)
                info["key"] = str(key)
                result["configs"].append(info)
        except Exception as err:
            result["configs_error"] = str(err)

        try:
            filters = self._selected_servers or None
            services = helper.get_services(name_filters=filters) or {}
            for name, service in services.items():
                instance = getattr(service, "instance", None)
                info = {
                    "name": name,
                    "service": self._object_summary(service),
                    "instance": self._object_summary(instance),
                    "request_probe": self._extract_trimemedia_runtime(name, service, {}),
                }
                result["services"].append(info)
        except Exception as err:
            result["services_error"] = str(err)

        self.save_data("inspect_result", result)
        return result

    def _object_summary(self, obj: Any) -> Dict[str, Any]:
        if obj is None:
            return {"type": "None"}
        summary: Dict[str, Any] = {"type": obj.__class__.__name__}
        plain: Dict[str, Any] = {}
        methods: List[str] = []
        for name in dir(obj):
            if name.startswith("__"):
                continue
            try:
                value = getattr(obj, name)
            except Exception:
                continue
            if callable(value):
                if not name.startswith("_"):
                    methods.append(name)
                continue
            if name.lower() in {"password", "passwd", "secret"}:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                plain[name] = value
            elif isinstance(value, dict):
                plain[name] = {str(k): self._mask_sensitive(v) for k, v in list(value.items())[:12]}
            elif isinstance(value, (list, tuple)):
                plain[name] = [self._mask_sensitive(v) for v in list(value)[:12]]
        summary["attrs"] = plain
        summary["methods"] = methods[:60]
        return summary

    def _mask_sensitive(self, value: Any) -> Any:
        if isinstance(value, str):
            low = value.lower()
            if "token" in low or "cookie" in low or len(value) > 80:
                return f"{value[:12]}...{value[-6:]}" if len(value) > 24 else "***"
        return value

    def _upload_trimemedia_cover(self, library: Dict[str, Any], output_file: Path) -> Tuple[bool, str]:
        helper = self._mediaserver_helper or MediaServerHelper()
        try:
            services = helper.get_services(name_filters=[library.get("server_name")]) or {}
            service = services.get(library.get("server_name"))
        except Exception as err:
            return False, f"获取媒体服务器实例失败：{err}"
        if not service:
            return False, "未找到对应的媒体服务器实例"

        runtime = self._extract_trimemedia_runtime(library.get("server_name"), service, library)
        if not runtime.get("base_url"):
            return False, "未能识别飞牛地址"

        headers = dict(runtime.get("headers") or {})
        cookies = dict(runtime.get("cookies") or {})
        base_url = str(runtime.get("base_url")).rstrip("/")
        try:
            poster_info = self._trimemedia_request(base_url, "/v/api/v1/mdb/getPoster", headers, cookies, {"guid": library.get("id")})
            poster_type = (poster_info.get("data") or {}).get("poster_type") or "single"
            upload_info = self._trimemedia_upload_temp(base_url, headers, cookies, output_file)
            hash_path = ((upload_info.get("data") or {}).get("hash_path")) or ""
            if not hash_path:
                return False, "临时图片上传后未返回 hash_path"
            payload = {"guid": library.get("id"), "poster_type": poster_type, "poster": hash_path}
            result = self._trimemedia_request(base_url, "/v/api/v1/mdb/setPoster", headers, cookies, payload)
            code = result.get("code")
            if code not in (0, 200, None):
                return False, f"setPoster 返回异常：{result}"
            return True, "自动替换成功"
        except Exception as err:
            return False, f"自动替换失败：{err}"

    def _trimemedia_upload_temp(self, base_url: str, headers: Dict[str, str], cookies: Dict[str, str], output_file: Path) -> Dict[str, Any]:
        with output_file.open("rb") as handle:
            files = {"file": (output_file.name, handle, "image/png")}
            response = requests.post(
                f"{base_url}/v/api/v1/image/temp/upload",
                headers={k: v for k, v in headers.items() if k.lower() != "content-type"},
                cookies=cookies,
                files=files,
                timeout=self._http_timeout,
            )
        response.raise_for_status()
        return response.json()

    def _trimemedia_request(
        self,
        base_url: str,
        path: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{base_url}{path}",
            headers={**headers, "Content-Type": "application/json"},
            cookies=cookies,
            json=payload,
            timeout=self._http_timeout,
        )
        response.raise_for_status()
        data = response.json()
        code = data.get("code")
        if code not in (0, 200, None):
            raise ValueError(data.get("msg") or str(data))
        return data

    def _extract_trimemedia_runtime(self, server_name: str, service: Any, library: Dict[str, Any]) -> Dict[str, Any]:
        instance = getattr(service, "instance", None)
        candidate_objects = [service, instance]
        config = None
        helper = self._mediaserver_helper or MediaServerHelper()
        try:
            configs = helper.get_configs() or {}
            if isinstance(configs, dict):
                config = configs.get(server_name)
        except Exception:
            config = None
        if config is not None:
            candidate_objects.append(config)

        base_url = ""
        headers: Dict[str, str] = {}
        cookies: Dict[str, str] = {}
        attrs_dump: List[Dict[str, Any]] = []

        for obj in candidate_objects:
            if obj is None:
                continue
            attrs = {}
            for name in dir(obj):
                if name.startswith("__"):
                    continue
                try:
                    value = getattr(obj, name)
                except Exception:
                    continue
                if callable(value):
                    continue
                attrs[name] = value
            attrs_dump.append({
                "type": obj.__class__.__name__,
                "keys": sorted(list(attrs.keys()))[:120],
            })
            if not base_url:
                base_url = self._guess_base_url_from_attrs(attrs) or base_url
            extra_headers, extra_cookies = self._guess_headers_cookies(attrs)
            headers.update({k: v for k, v in extra_headers.items() if v})
            cookies.update({k: v for k, v in extra_cookies.items() if v})

        if not base_url and library.get("link"):
            parsed = urlparse(str(library.get("link")))
            if parsed.scheme and parsed.netloc:
                base_url = f"{parsed.scheme}://{parsed.netloc}"

        return {
            "base_url": base_url,
            "headers": headers,
            "cookies": cookies,
            "attrs_dump": attrs_dump,
        }

    def _guess_base_url_from_attrs(self, attrs: Dict[str, Any]) -> str:
        for key in ("base_url", "server", "host", "url", "_host", "_server", "_base_url"):
            value = attrs.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value.rstrip("/")
        for key, value in attrs.items():
            if not isinstance(value, str):
                continue
            if value.startswith("http://") or value.startswith("https://"):
                return value.rstrip("/")
        return ""

    def _guess_headers_cookies(self, attrs: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
        headers: Dict[str, str] = {}
        cookies: Dict[str, str] = {}
        for key, value in attrs.items():
            key_lower = key.lower()
            if isinstance(value, requests.Session):
                headers.update({str(k): str(v) for k, v in value.headers.items()})
                cookies.update(value.cookies.get_dict())
                continue
            if key_lower in {"headers", "_headers"} and isinstance(value, dict):
                headers.update({str(k): str(v) for k, v in value.items()})
                continue
            if key_lower in {"cookies", "_cookies"}:
                if isinstance(value, dict):
                    cookies.update({str(k): str(v) for k, v in value.items()})
                elif isinstance(value, str):
                    cookies.update(self._parse_cookie_string(value))
                continue
            if "cookie" == key_lower and isinstance(value, str):
                cookies.update(self._parse_cookie_string(value))
                continue
            if "token" in key_lower and isinstance(value, str) and value:
                headers.setdefault("Authorization", value if value.lower().startswith("bearer ") else f"Bearer {value}")
            if key_lower in {"authorization", "auth"} and isinstance(value, str) and value:
                headers.setdefault("Authorization", value)
        return headers, cookies

    def _parse_cookie_string(self, cookie_value: str) -> Dict[str, str]:
        cookies: Dict[str, str] = {}
        for chunk in str(cookie_value or "").split(";"):
            if "=" not in chunk:
                continue
            name, value = chunk.split("=", 1)
            cookies[name.strip()] = value.strip()
        return cookies
