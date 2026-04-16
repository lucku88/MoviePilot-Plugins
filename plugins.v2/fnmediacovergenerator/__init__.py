import base64
import hashlib
import json
import os
import random
import re
import shutil
import threading
import time
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

import pytz
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

try:
    from PIL import Image
except Exception:
    Image = None

from app.core.config import settings
from app.helper.mediaserver import MediaServerHelper
from app.log import logger
from app.plugins import _PluginBase
from app.utils.url import UrlUtils

from app.plugins.fnmediacovergenerator.style.style_static_1 import create_style_static_1
from app.plugins.fnmediacovergenerator.style.style_static_2 import create_style_static_2
from app.plugins.fnmediacovergenerator.style.style_static_3 import create_style_static_3
from app.plugins.fnmediacovergenerator.style.style_static_4 import create_style_static_4
from app.plugins.fnmediacovergenerator.style.style_static_5 import create_style_static_5
from app.plugins.fnmediacovergenerator.utils.style5_cover_strategy import (
    pick_style5_source_urls,
    remember_style5_primary,
    resolve_style5_render_mode,
    select_style5_image_urls,
)
from app.plugins.fnmediacovergenerator.utils.history_selection import (
    normalize_history_paths,
    resolve_history_delete_targets,
    retain_history_selection,
    toggle_history_selection,
)
from app.plugins.fnmediacovergenerator.utils.library_image_debug import (
    count_non_empty_items,
    format_library_image_stats,
)
from app.plugins.fnmediacovergenerator.utils.image_manager import ResolutionConfig
from app.plugins.fnmediacovergenerator.utils.network_helper import NetworkHelper, validate_font_file
from app.plugins.fnmediacovergenerator.utils.trimemedia_library_images import (
    collect_library_item_image_paths,
    merge_unique_image_urls,
    prefer_supplemental_image_urls,
)


TRIMEMEDIA_SIGN_SECRET = "NDzZTVxnRKP8Z0jXg1VAMonaG8akvh"
TRIMEMEDIA_API_KEY = "16CCEB3D-AB42-077D-36A1-F355324E4237"
TRIMEMEDIA_TOKEN_COOKIE = "Trim-MC-token"
TRIMEMEDIA_UPLOAD_MAX_BYTES = 5 * 1024 * 1024
TRIMEMEDIA_SINGLE_POSTER_TYPE = 1
TRIMEMEDIA_PATH_MARKERS = (
    "/api/v1",
    "/library/",
    "/item/",
    "/search/",
    "/user/",
    "/manager/",
    "/mediadb/",
    "/mdb/",
    "/image/",
    "/sys/",
)

DEFAULT_FONT_URLS = {
    "chaohei": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/chaohei.ttf",
    "yasong": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/yasong.ttf",
    "EmblemaOne": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/EmblemaOne.woff2",
    "Melete": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/Melete.otf",
    "Phosphate": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/phosphate.ttf",
    "JosefinSans": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/josefinsans.woff2",
    "LilitaOne": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/lilitaone.woff2",
    "Monoton": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/Monoton.woff2",
    "Plaster": "https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/fonts/Plaster.woff2",
}

DEFAULT_SUBTITLE_MAP = {
    "国漫": "GUOMAN",
    "动画": "Animation",
    "动漫": "Anime",
    "电影": "Films",
    "动画电影": "Animated Films",
    "国产剧": "Chinese Drama",
    "欧美剧": "Western Series",
    "日韩剧": "Japan & Korea Drama",
    "日剧": "Japanese Drama",
    "韩剧": "Korean Drama",
    "电视剧": "TV Series",
    "纪录片": "Documentaries",
    "综艺": "Variety Shows",
    "其他": "Others",
    "短剧": "Short Drama",
    "番剧": "Anime Series",
    "美剧": "US Series",
    "英剧": "UK Series",
    "台剧": "Taiwan Drama",
    "港剧": "Hong Kong Drama",
}


def _safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


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


def _safe_float(value: Any, default: float, minimum: Optional[float] = None, maximum: Optional[float] = None) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = default
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


class FnMediaCoverGenerator(_PluginBase):
    plugin_name = "飞牛影视媒体库封面生成"
    plugin_desc = "生成媒体库静态封面，支持飞牛影视"
    plugin_icon = "https://raw.githubusercontent.com/lucku88/MoviePilot-Plugins/main/icons/fnys.png"
    plugin_version = "0.1.11"
    plugin_author = "lucku88"
    author_url = "https://github.com/lucku88/MoviePilot-Plugins"
    plugin_config_prefix = "fnmediacovergenerator_"
    plugin_order = 13
    auth_level = 1

    _scheduler: Optional[BackgroundScheduler] = None
    _mediaserver_helper: Optional[MediaServerHelper] = None
    _run_lock = threading.Lock()
    _stop_event = threading.Event()

    _enabled = False
    _onlyonce = False
    _auto_upload = True
    _cron = ""
    _selected_servers: List[str] = []
    _include_libraries: List[str] = []
    _all_libraries: List[Dict[str, str]] = []
    _title_config = ""
    _current_config: Dict[str, List[str]] = {}
    _cover_style = "static_1"
    _cover_style_base = "static_1"
    _cover_style_variant = "static"
    _multi_1_blur = True
    _zh_font_preset = "chaohei"
    _en_font_preset = "EmblemaOne"
    _zh_font_custom = ""
    _en_font_custom = ""
    _zh_font_path = ""
    _en_font_path = ""
    _zh_font_size = 170
    _en_font_size = 75
    _zh_font_offset = ""
    _title_spacing = ""
    _en_line_spacing = ""
    _title_scale = 1.0
    _blur_size = 50
    _color_ratio = 0.8
    _resolution = "1080p"
    _custom_width = 1920
    _custom_height = 1080
    _animation_duration = 8
    _animation_scroll = "alternate"
    _animation_fps = 15
    _animation_format = "apng"
    _animation_reduce_colors = "medium"
    _animated_2_image_count = 6
    _animated_2_departure_type = "fly"
    _bg_color_mode = "auto"
    _custom_bg_color = ""
    _covers_history_limit_per_library = 10
    _covers_page_history_limit = 50
    _page_tab = "generate-tab"

    _font_path: Optional[Path] = None
    _covers_path: Optional[Path] = None
    _covers_output: Optional[Path] = None
    _resolution_config: Optional[ResolutionConfig] = None
    _sanitize_log_cache: set = set()

    def __init__(self):
        super().__init__()

    def init_plugin(self, config: dict = None):
        self.stop_service()
        self._mediaserver_helper = MediaServerHelper()

        data_path = self.get_data_path()
        self._font_path = data_path / "fonts"
        self._covers_path = data_path / "input"
        self._covers_output = data_path / "output"
        self._font_path.mkdir(parents=True, exist_ok=True)
        self._covers_path.mkdir(parents=True, exist_ok=True)
        self._covers_output.mkdir(parents=True, exist_ok=True)

        merged = self._default_config()
        if config:
            merged.update(config)
        self._apply_config(merged)
        self._all_libraries = self._collect_library_options()

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
            {"path": "/generate_now", "endpoint": self.api_generate_now, "auth": "bear", "methods": ["POST", "GET"], "summary": "立即生成封面"},
            {"path": "generate_now", "endpoint": self.api_generate_now, "auth": "bear", "methods": ["POST", "GET"], "summary": "立即生成封面"},
            {"path": "/set_cover_style", "endpoint": self.api_set_cover_style, "auth": "bear", "methods": ["POST", "GET"], "summary": "切换风格"},
            {"path": "set_cover_style", "endpoint": self.api_set_cover_style, "auth": "bear", "methods": ["POST", "GET"], "summary": "切换风格"},
            {"path": "/select_style_1", "endpoint": self.api_select_style_1, "auth": "bear", "methods": ["POST"], "summary": "选择风格1"},
            {"path": "select_style_1", "endpoint": self.api_select_style_1, "auth": "bear", "methods": ["POST"], "summary": "选择风格1"},
            {"path": "/select_style_2", "endpoint": self.api_select_style_2, "auth": "bear", "methods": ["POST"], "summary": "选择风格2"},
            {"path": "select_style_2", "endpoint": self.api_select_style_2, "auth": "bear", "methods": ["POST"], "summary": "选择风格2"},
            {"path": "/select_style_3", "endpoint": self.api_select_style_3, "auth": "bear", "methods": ["POST"], "summary": "选择风格3"},
            {"path": "select_style_3", "endpoint": self.api_select_style_3, "auth": "bear", "methods": ["POST"], "summary": "选择风格3"},
            {"path": "/select_style_4", "endpoint": self.api_select_style_4, "auth": "bear", "methods": ["POST"], "summary": "选择风格4"},
            {"path": "select_style_4", "endpoint": self.api_select_style_4, "auth": "bear", "methods": ["POST"], "summary": "选择风格4"},
            {"path": "/select_style_5", "endpoint": self.api_select_style_5, "auth": "bear", "methods": ["POST"], "summary": "选择风格5"},
            {"path": "select_style_5", "endpoint": self.api_select_style_5, "auth": "bear", "methods": ["POST"], "summary": "选择风格5"},
            {"path": "/set_page_tab_generate", "endpoint": self.api_set_page_tab_generate, "auth": "bear", "methods": ["POST"], "summary": "切换到生成页"},
            {"path": "set_page_tab_generate", "endpoint": self.api_set_page_tab_generate, "auth": "bear", "methods": ["POST"], "summary": "切换到生成页"},
            {"path": "/set_page_tab_history", "endpoint": self.api_set_page_tab_history, "auth": "bear", "methods": ["POST"], "summary": "切换到历史页"},
            {"path": "set_page_tab_history", "endpoint": self.api_set_page_tab_history, "auth": "bear", "methods": ["POST"], "summary": "切换到历史页"},
            {"path": "/set_page_tab_clean", "endpoint": self.api_set_page_tab_clean, "auth": "bear", "methods": ["POST"], "summary": "切换到清理页"},
            {"path": "set_page_tab_clean", "endpoint": self.api_set_page_tab_clean, "auth": "bear", "methods": ["POST"], "summary": "切换到清理页"},
            {"path": "/clean_images", "endpoint": self.api_clean_images, "auth": "bear", "methods": ["POST"], "summary": "清理图片缓存"},
            {"path": "clean_images", "endpoint": self.api_clean_images, "auth": "bear", "methods": ["POST"], "summary": "清理图片缓存"},
            {"path": "/clean_fonts", "endpoint": self.api_clean_fonts, "auth": "bear", "methods": ["POST"], "summary": "清理字体缓存"},
            {"path": "clean_fonts", "endpoint": self.api_clean_fonts, "auth": "bear", "methods": ["POST"], "summary": "清理字体缓存"},
            {"path": "/delete_all_saved_covers", "endpoint": self.api_delete_all_saved_covers, "auth": "bear", "methods": ["POST"], "summary": "清空历史封面"},
            {"path": "delete_all_saved_covers", "endpoint": self.api_delete_all_saved_covers, "auth": "bear", "methods": ["POST"], "summary": "清空历史封面"},
            {"path": "/delete_saved_cover", "endpoint": self.api_delete_saved_cover, "auth": "bear", "methods": ["POST", "GET"], "summary": "删除历史封面"},
            {"path": "delete_saved_cover", "endpoint": self.api_delete_saved_cover, "auth": "bear", "methods": ["POST", "GET"], "summary": "删除历史封面"},
        ]

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        server_items = self._collect_server_options()
        self._all_libraries = self._collect_library_options()
        zh_font_items, en_font_items, _, _ = self.__get_font_presets()

        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VCard",
                        "props": {"variant": "outlined"},
                        "content": [
                            {"component": "VCardTitle", "text": "基础设置"},
                            {
                                "component": "VCardText",
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "text": "直接读取 MoviePilot 已配置的飞牛影视媒体服务器，仅生成静态封面并支持自动替换。"
                                        }
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "enabled", "label": "启用插件"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "auto_upload", "label": "自动替换飞牛封面", "hint": "开启后会在静态封面生成完成后自动回写飞牛媒体库。", "persistentHint": True}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSwitch", "props": {"model": "onlyonce", "label": "保存后立即运行一次"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VCronField", "props": {"model": "cron", "label": "定时任务", "placeholder": "5位 Cron"}}]},
                                        ],
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 6}, "content": [{"component": "VSelect", "props": {"model": "selected_servers", "multiple": True, "chips": True, "clearable": True, "label": "飞牛媒体服务器", "items": server_items}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 6}, "content": [{"component": "VSelect", "props": {"model": "include_libraries", "multiple": True, "chips": True, "clearable": True, "label": "媒体库范围", "items": self._all_libraries, "hint": "留空表示处理全部已选飞牛媒体库", "persistentHint": True}}]},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VCard",
                        "props": {"variant": "outlined", "class": "mt-3"},
                        "content": [
                            {"component": "VCardTitle", "text": "封面风格"},
                            {
                                "component": "VCardText",
                                "content": [
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 6}, "content": [{"component": "VSelect", "props": {"model": "cover_style_base", "label": "风格编号", "items": [{"title": "风格1", "value": "static_1"}, {"title": "风格2", "value": "static_2"}, {"title": "风格3", "value": "static_3"}, {"title": "风格4", "value": "static_4"}, {"title": "风格5", "value": "static_5"}]}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 6}, "content": [{"component": "VSwitch", "props": {"model": "multi_1_blur", "label": "九宫格样式启用模糊底图"}}]},
                                        ],
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSelect", "props": {"model": "resolution", "label": "静态分辨率", "items": [{"title": "1080p", "value": "1080p"}, {"title": "720p", "value": "720p"}, {"title": "480p", "value": "480p"}, {"title": "自定义", "value": "custom"}]}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "custom_width", "label": "自定义宽度", "placeholder": "1920"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "custom_height", "label": "自定义高度", "placeholder": "1080"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "covers_page_history_limit", "label": "历史封面显示数量", "placeholder": "50"}}]},
                                        ],
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "blur_size", "label": "背景模糊强度", "placeholder": "50"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "color_ratio", "label": "主色比例", "placeholder": "0.8"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSelect", "props": {"model": "bg_color_mode", "label": "背景颜色模式", "items": [{"title": "自动取色", "value": "auto"}, {"title": "优先标题配置色", "value": "config"}, {"title": "固定颜色", "value": "custom"}]}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "custom_bg_color", "label": "固定背景色", "placeholder": "#1D2433"}}]},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VCard",
                        "props": {"variant": "outlined", "class": "mt-3"},
                        "content": [
                            {"component": "VCardTitle", "text": "字体与标题"},
                            {
                                "component": "VCardText",
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "text": "字体支持预设名、HTTP 下载地址或容器内本地路径。标题映射按 YAML 配置读取，可给单个媒体库单独指定主标题、副标题和背景色；未填写副标题时，会对常见媒体库名自动补默认副标题。"
                                        }
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSelect", "props": {"model": "zh_font_preset", "label": "主标题字体预设", "items": zh_font_items}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VSelect", "props": {"model": "en_font_preset", "label": "副标题字体预设", "items": en_font_items}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "zh_font_custom", "label": "主标题自定义字体", "placeholder": "本地路径或 URL"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 3}, "content": [{"component": "VTextField", "props": {"model": "en_font_custom", "label": "副标题自定义字体", "placeholder": "本地路径或 URL"}}]},
                                        ],
                                    },
                                    {
                                        "component": "VRow",
                                        "content": [
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "zh_font_size", "label": "主标题字号", "placeholder": "170"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "en_font_size", "label": "副标题字号", "placeholder": "75"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "title_scale", "label": "整体标题缩放", "placeholder": "1.0"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "zh_font_offset", "label": "主标题垂直偏移", "placeholder": "0"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "title_spacing", "label": "主副标题间距", "placeholder": "40"}}]},
                                            {"component": "VCol", "props": {"cols": 12, "md": 2}, "content": [{"component": "VTextField", "props": {"model": "en_line_spacing", "label": "副标题行距", "placeholder": "40"}}]},
                                        ],
                                    },
                                    {
                                        "component": "VAceEditor",
                                        "props": {
                                            "modelvalue": "title_config",
                                            "lang": "yaml",
                                            "theme": "monokai",
                                            "style": "height: 18rem",
                                            "label": "媒体库标题映射",
                                            "placeholder": "国漫:\n  - 国漫\n  - GUOMAN\n  - '#22314C'\n动画电影:\n  - 动画电影\n  - Animated Films"
                                        }
                                    },
                                ],
                            },
                        ],
                    },
                ],
            }
        ], self._config_payload()

    def get_page(self) -> List[dict]:
        style_variant, style_index = self.__get_cover_style_parts()
        style_preview_cards = self.__build_page_style_cards(style_variant=style_variant, selected_index=style_index)
        latest_result = self.get_data("latest_result") or {}
        latest_message = latest_result.get("message") or "还没有执行记录"
        latest_time = latest_result.get("finished_at") or self.get_data("last_run") or "-"
        setup_warnings: List[str] = []
        if not self._collect_server_options():
            setup_warnings.append("未检测到已配置的飞牛影视媒体服务器")
        if not self._selected_servers:
            setup_warnings.append("当前未勾选媒体服务器，默认会处理全部飞牛媒体服务器")
        if not self._all_libraries:
            self._all_libraries = self._collect_library_options()
        if self._selected_servers and not self._all_libraries:
            setup_warnings.append("未读取到媒体库列表，请先保存配置后重试")

        history_rows: List[Dict[str, Any]] = []
        if self._page_tab == "history-tab":
            history_items = self.__get_recent_generated_covers(limit=self._covers_page_history_limit)
            for item in history_items:
                delete_api = f"plugin/FnMediaCoverGenerator/delete_saved_cover?file={quote(item['path'])}"
                history_rows.append(
                    {
                        "component": "VCol",
                        "props": {"cols": 12, "sm": 6, "md": 3},
                        "content": [
                            {
                                "component": "VCard",
                                "props": {"variant": "flat", "elevation": 2, "class": "rounded-lg"},
                                "content": [
                                    {"component": "VImg", "props": {"src": item["src"], "aspect-ratio": "16/9", "cover": True}},
                                    {"component": "VCardText", "props": {"class": "py-2"}, "content": [
                                        {"component": "div", "props": {"class": "text-body-2"}, "text": item["name"]},
                                        {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": f"{item['mtime']} / {item['size']}"},
                                        {"component": "VBtn", "props": {"color": "error", "variant": "text", "size": "small", "class": "mt-2 text-none"}, "text": "删除", "events": {"click": {"api": delete_api, "method": "post"}}},
                                    ]},
                                ],
                            }
                        ],
                    }
                )

        return [
            {
                "component": "VCard",
                "content": [
                    {
                        "component": "VTabs",
                        "props": {"grow": True, "modelValue": self._page_tab},
                        "content": [
                            {"component": "VTab", "props": {"value": "generate-tab"}, "text": "封面生成", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/set_page_tab_generate", "method": "post"}}},
                            {"component": "VTab", "props": {"value": "history-tab"}, "text": "历史封面", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/set_page_tab_history", "method": "post"}}},
                            {"component": "VTab", "props": {"value": "clean-tab"}, "text": "清理缓存", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/set_page_tab_clean", "method": "post"}}},
                        ],
                    },
                    {"component": "VDivider"},
                ],
            },
            {
                "component": "VCard",
                "props": {"variant": "outlined", "class": "mt-3"},
                "content": [
                    {
                        "component": "VCardText",
                        "content": [
                            {"component": "div", "props": {"class": "text-subtitle-1 font-weight-medium"}, "text": latest_message},
                            {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-1"}, "text": f"最近执行时间：{latest_time}"},
                            {
                                "component": "VAlert",
                                "props": {"type": "warning", "variant": "tonal", "density": "compact", "class": "mt-3"},
                                "text": "；".join(setup_warnings),
                            } if setup_warnings else {
                                "component": "VAlert",
                                "props": {"type": "info", "variant": "tonal", "density": "compact", "class": "mt-3"},
                                "text": "当前风格会直接作用于飞牛媒体库静态封面。"
                            },
                        ],
                    }
                ],
            },
        ] + (
            [
                {
                    "component": "VCard",
                    "props": {"variant": "outlined", "class": "mt-3"},
                    "content": [
                        {
                            "component": "VCardText",
                            "content": [
                                {
                                    "component": "VRow",
                                    "content": [
                                        {
                                            "component": "VCol",
                                            "props": {"cols": 12, "md": 9},
                                            "content": [
                                                {"component": "VBtn", "props": {"variant": "flat", "color": "primary", "class": "text-none mb-2", "prepend-icon": "mdi-play-circle-outline"}, "text": "立即生成当前风格", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/generate_now", "method": "post"}}},
                                            ],
                                        }
                                    ],
                                },
                                {"component": "VRow", "content": style_preview_cards},
                            ],
                        }
                    ],
                }
            ] if self._page_tab == "generate-tab" else
            [
                {
                    "component": "VCard",
                    "props": {"variant": "outlined", "class": "mt-3"},
                    "content": [
                        {"component": "VCardTitle", "text": f"最近生成的封面（最多 {self._covers_page_history_limit} 张）"},
                        {"component": "VCardText", "content": [
                            {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": "这里保留历史封面预览和单张删除；若要一次性清空全部历史封面，请到“清理缓存”页操作。"}
                        ]},
                        {"component": "VCardText", "content": [{"component": "VRow", "content": history_rows or [{"component": "VAlert", "props": {"type": "info", "variant": "tonal"}, "text": "还没有可展示的历史封面。"}]}]},
                    ],
                }
            ] if self._page_tab == "history-tab" else
            [
                {
                    "component": "VCard",
                    "props": {"variant": "outlined", "class": "mt-3"},
                    "content": [
                        {
                            "component": "VCardText",
                            "props": {"class": "pa-6 d-flex flex-column align-center"},
                            "content": [
                                {"component": "VBtn", "props": {"color": "error", "variant": "flat", "size": "large", "prepend-icon": "mdi-image-remove", "class": "mb-3 text-none"}, "text": "清理图片缓存", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/clean_images", "method": "post"}}},
                                {"component": "VBtn", "props": {"color": "error", "variant": "flat", "size": "large", "prepend-icon": "mdi-format-font", "class": "mb-3 text-none"}, "text": "清理字体缓存", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/clean_fonts", "method": "post"}}},
                                {"component": "VBtn", "props": {"color": "error", "variant": "flat", "size": "large", "prepend-icon": "mdi-delete-sweep", "class": "mb-3 text-none"}, "text": "清空历史封面", "events": {"click": {"api": "plugin/FnMediaCoverGenerator/delete_all_saved_covers", "method": "post"}}},
                                {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": "图片缓存只会清理生成源图；“清空历史封面”会删除插件输出目录里已保存的全部封面历史。"},
                            ],
                        }
                    ],
                }
            ]
        )

    def get_service(self) -> List[Dict[str, Any]]:
        if not self._enabled or not self._cron:
            return []
        try:
            trigger = CronTrigger.from_crontab(self._cron)
        except Exception as err:
            logger.warning("%s Cron 无效：%s", self.plugin_name, err)
            return []
        return [{"id": "FnMediaCoverGenerator", "name": self.plugin_name, "trigger": trigger, "func": self._scheduled_worker, "kwargs": {}}]

    def stop_service(self):
        self._stop_event.set()
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
        except Exception as err:
            logger.warning("%s 停止调度失败：%s", self.plugin_name, err)
        self._scheduler = None
        self._stop_event.clear()

    def api_generate_now(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        style = ""
        if isinstance(data, dict):
            style = str(data.get("style") or "").strip()
        if style:
            self._set_cover_style(style, persist=True)
        return self._execute_run(force=True, reason="manual")

    def api_set_cover_style(self, style: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        style_value = str(style or "").strip()
        if isinstance(data, dict) and data.get("style"):
            style_value = str(data.get("style")).strip()
        if not style_value:
            return {"success": False, "message": "缺少风格参数"}
        self._set_cover_style(style_value, persist=True)
        return {"success": True, "message": f"已切换到 {self._cover_style}"}

    def api_select_style_1(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._select_style_index(1)

    def api_select_style_2(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._select_style_index(2)

    def api_select_style_3(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._select_style_index(3)

    def api_select_style_4(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._select_style_index(4)

    def api_select_style_5(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._select_style_index(5)

    def api_set_page_tab_generate(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._page_tab = "generate-tab"
        self._update_config()
        return {"success": True}

    def api_set_page_tab_history(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._page_tab = "history-tab"
        self._update_config()
        return {"success": True}

    def api_set_page_tab_clean(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._page_tab = "clean-tab"
        self._update_config()
        return {"success": True}

    def api_clean_images(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        removed = self._clean_image_cache()
        return {"success": True, "message": f"已清理 {removed} 个图片缓存项"}

    def api_clean_fonts(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        removed = self._clean_font_cache()
        self._zh_font_path = ""
        self._en_font_path = ""
        self._update_config()
        return {"success": True, "message": f"已清理 {removed} 个字体缓存项"}

    def api_delete_all_saved_covers(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        deleted = self._clear_saved_cover_history()
        self._set_selected_history_files([])
        return {"success": True, "message": f"已清空 {deleted} 张历史封面" if deleted else "没有可清空的历史封面"}

    def api_delete_saved_cover(self, file: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        targets = resolve_history_delete_targets(file=file, data=data)
        if not targets:
            return {"success": False, "message": "缺少文件路径"}
        output_dir = self._covers_output or (self.get_data_path() / "output")
        deleted_paths: List[str] = []
        missing_count = 0
        invalid_count = 0
        for target in targets:
            path = Path(target)
            try:
                path.relative_to(output_dir)
            except Exception:
                invalid_count += 1
                continue
            if not path.exists():
                missing_count += 1
                continue
            path.unlink(missing_ok=True)
            deleted_paths.append(str(path))
        if deleted_paths:
            deleted_set = set(deleted_paths)
            remaining_selected = [item for item in self._get_selected_history_files() if item not in deleted_set]
            self._set_selected_history_files(remaining_selected)
        if not deleted_paths:
            if invalid_count > 0:
                return {"success": False, "message": "只能删除插件输出目录中的文件"}
            return {"success": False, "message": "文件不存在"}
        if len(deleted_paths) == 1:
            message = f"已删除 {Path(deleted_paths[0]).name}"
        else:
            message = f"已删除 {len(deleted_paths)} 张封面"
        if missing_count > 0:
            message += f"，跳过 {missing_count} 个不存在文件"
        if invalid_count > 0:
            message += f"，忽略 {invalid_count} 个非法路径"
        return {"success": True, "message": message}

    def api_toggle_saved_cover_selection(self, file: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        targets = resolve_history_delete_targets(file=file, data=data)
        target = targets[0] if targets else ""
        if not target:
            return {"success": False, "message": "缺少文件路径"}
        visible_paths = [item["path"] for item in self.__get_recent_generated_covers(limit=self._covers_page_history_limit) if item.get("path")]
        if target not in visible_paths:
            return {"success": False, "message": "文件不在当前历史列表中"}
        selected = toggle_history_selection(self._get_selected_history_files(), target)
        selected = retain_history_selection(selected, visible_paths)
        self._set_selected_history_files(selected)
        return {"success": True, "message": f"当前已选 {len(selected)} 张封面"}

    def api_select_all_saved_covers(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        visible_paths = [item["path"] for item in self.__get_recent_generated_covers(limit=self._covers_page_history_limit) if item.get("path")]
        if not visible_paths:
            self._set_selected_history_files([])
            return {"success": False, "message": "当前没有可选的历史封面"}
        self._set_selected_history_files(visible_paths)
        return {"success": True, "message": f"已选中当前页 {len(visible_paths)} 张封面"}

    def api_clear_saved_cover_selection(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._set_selected_history_files([])
        return {"success": True, "message": "已清空历史封面选择"}

    def api_delete_selected_saved_covers(self, _: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        selected = self._prune_selected_history_files()
        if not selected:
            return {"success": False, "message": "请先选择要删除的历史封面"}
        return self.api_delete_saved_cover(data={"files": selected})

    def _default_config(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "onlyonce": False,
            "auto_upload": True,
            "cron": "",
            "selected_servers": [],
            "include_libraries": [],
            "title_config": "",
            "cover_style": "static_1",
            "cover_style_base": "static_1",
            "cover_style_variant": "static",
            "multi_1_blur": True,
            "zh_font_preset": "chaohei",
            "en_font_preset": "EmblemaOne",
            "zh_font_custom": "",
            "en_font_custom": "",
            "zh_font_path": "",
            "en_font_path": "",
            "zh_font_size": 170,
            "en_font_size": 75,
            "zh_font_offset": "",
            "title_spacing": "",
            "en_line_spacing": "",
            "title_scale": 1.0,
            "blur_size": 50,
            "color_ratio": 0.8,
            "resolution": "1080p",
            "custom_width": 1920,
            "custom_height": 1080,
            "animation_duration": 8,
            "animation_scroll": "alternate",
            "animation_fps": 15,
            "animation_format": "apng",
            "animation_reduce_colors": "medium",
            "animated_2_image_count": 6,
            "animated_2_departure_type": "fly",
            "bg_color_mode": "auto",
            "custom_bg_color": "",
            "covers_history_limit_per_library": 10,
            "covers_page_history_limit": 50,
            "page_tab": "generate-tab",
        }

    def _config_payload(self) -> Dict[str, Any]:
        return {
            "enabled": self._enabled,
            "onlyonce": self._onlyonce,
            "auto_upload": self._auto_upload,
            "cron": self._cron,
            "selected_servers": self._selected_servers,
            "include_libraries": self._include_libraries,
            "title_config": self._title_config,
            "cover_style": self._cover_style,
            "cover_style_base": self._cover_style_base,
            "cover_style_variant": "static",
            "multi_1_blur": self._multi_1_blur,
            "zh_font_preset": self._zh_font_preset,
            "en_font_preset": self._en_font_preset,
            "zh_font_custom": self._zh_font_custom,
            "en_font_custom": self._en_font_custom,
            "zh_font_path": str(self._zh_font_path or ""),
            "en_font_path": str(self._en_font_path or ""),
            "zh_font_size": self._zh_font_size,
            "en_font_size": self._en_font_size,
            "zh_font_offset": self._zh_font_offset,
            "title_spacing": self._title_spacing,
            "en_line_spacing": self._en_line_spacing,
            "title_scale": self._title_scale,
            "blur_size": self._blur_size,
            "color_ratio": self._color_ratio,
            "resolution": self._resolution,
            "custom_width": self._custom_width,
            "custom_height": self._custom_height,
            "animation_duration": self._animation_duration,
            "animation_scroll": self._animation_scroll,
            "animation_fps": self._animation_fps,
            "animation_format": self._animation_format,
            "animation_reduce_colors": self._animation_reduce_colors,
            "animated_2_image_count": self._animated_2_image_count,
            "animated_2_departure_type": self._animated_2_departure_type,
            "bg_color_mode": self._bg_color_mode,
            "custom_bg_color": self._custom_bg_color,
            "covers_history_limit_per_library": self._covers_history_limit_per_library,
            "covers_page_history_limit": self._covers_page_history_limit,
            "page_tab": self._page_tab,
        }

    def _apply_config(self, config: Dict[str, Any]):
        cover_style = str(config.get("cover_style") or "static_1").strip()
        cover_style_base = str(config.get("cover_style_base") or "").strip()
        resolved_base, _ = self.__resolve_cover_style_ui(cover_style)
        self._cover_style_base = cover_style_base or resolved_base
        self._cover_style_variant = "static"
        self._cover_style = self.__compose_cover_style(self._cover_style_base, "static")
        self._enabled = _safe_bool(config.get("enabled"), False)
        self._onlyonce = _safe_bool(config.get("onlyonce"), False)
        self._auto_upload = _safe_bool(config.get("auto_upload"), True)
        self._cron = str(config.get("cron") or "").strip()
        self._selected_servers = [item for item in (config.get("selected_servers") or []) if item]
        self._include_libraries = [item for item in (config.get("include_libraries") or []) if item]
        self._title_config = str(config.get("title_config") or "").strip()
        self._current_config = self.__load_title_config(self._title_config)
        self._multi_1_blur = _safe_bool(config.get("multi_1_blur"), True)
        self._zh_font_preset = str(config.get("zh_font_preset") or "chaohei").strip() or "chaohei"
        self._en_font_preset = str(config.get("en_font_preset") or "EmblemaOne").strip() or "EmblemaOne"
        self._zh_font_custom = str(config.get("zh_font_custom") or "").strip()
        self._en_font_custom = str(config.get("en_font_custom") or "").strip()
        self._zh_font_path = str(config.get("zh_font_path") or "").strip()
        self._en_font_path = str(config.get("en_font_path") or "").strip()
        self._zh_font_size = _safe_int(config.get("zh_font_size"), 170, 20, 500)
        self._en_font_size = _safe_int(config.get("en_font_size"), 75, 10, 300)
        self._zh_font_offset = str(config.get("zh_font_offset") or "").strip()
        self._title_spacing = str(config.get("title_spacing") or "").strip()
        self._en_line_spacing = str(config.get("en_line_spacing") or "").strip()
        self._title_scale = _safe_float(config.get("title_scale"), 1.0, 0.2, 4.0)
        self._blur_size = _safe_int(config.get("blur_size"), 50, 1, 100)
        self._color_ratio = _safe_float(config.get("color_ratio"), 0.8, 0.0, 1.0)
        self._resolution = str(config.get("resolution") or "1080p").strip() or "1080p"
        self._custom_width = _safe_int(config.get("custom_width"), 1920, 320, 4096)
        self._custom_height = _safe_int(config.get("custom_height"), 1080, 180, 4096)
        self._animation_duration = _safe_int(config.get("animation_duration"), 8, 2, 60)
        self._animation_scroll = str(config.get("animation_scroll") or "alternate").strip() or "alternate"
        self._animation_fps = _safe_int(config.get("animation_fps"), 15, 1, 60)
        self._animation_format = str(config.get("animation_format") or "apng").strip().lower() or "apng"
        if self._animation_format == "webp":
            self._animation_format = "gif"
        if self._animation_format not in {"apng", "gif"}:
            self._animation_format = "apng"
        self._animation_reduce_colors = str(config.get("animation_reduce_colors") or "medium").strip() or "medium"
        if self._animation_reduce_colors not in {"off", "medium", "strong"}:
            self._animation_reduce_colors = "medium"
        self._animated_2_image_count = _safe_int(config.get("animated_2_image_count"), 6, 3, 9)
        self._animated_2_departure_type = str(config.get("animated_2_departure_type") or "fly").strip() or "fly"
        if self._animated_2_departure_type not in {"fly", "fade", "crossfade"}:
            self._animated_2_departure_type = "fly"
        self._bg_color_mode = str(config.get("bg_color_mode") or "auto").strip() or "auto"
        if self._bg_color_mode not in {"auto", "config", "custom"}:
            self._bg_color_mode = "auto"
        self._custom_bg_color = str(config.get("custom_bg_color") or "").strip()
        self._covers_history_limit_per_library = _safe_int(config.get("covers_history_limit_per_library"), 10, 1, 100)
        self._covers_page_history_limit = _safe_int(config.get("covers_page_history_limit"), 50, 1, 500)
        self._page_tab = str(config.get("page_tab") or "generate-tab").strip() or "generate-tab"
        if self._page_tab not in {"generate-tab", "history-tab", "clean-tab"}:
            self._page_tab = "generate-tab"
        self._resolution_config = self._build_resolution_config()

    def _update_config(self):
        self._cover_style = self.__compose_cover_style(self._cover_style_base, self._cover_style_variant)
        self.update_config(self._config_payload())

    def _run_once_job(self):
        self._execute_run(force=True, reason="onlyonce")

    def _scheduled_worker(self):
        self._execute_run(force=False, reason="schedule")

    def _aware_now(self) -> datetime:
        return datetime.now(tz=pytz.timezone(settings.TZ))

    def _append_history(self, record: Dict[str, Any]):
        history = list(self.get_data("run_history") or [])
        history.insert(0, record)
        self.save_data("run_history", history[:20])

    def _execute_run(self, force: bool = False, reason: str = "manual") -> Dict[str, Any]:
        if not force and not self._enabled:
            return {"success": False, "message": "插件未启用"}
        if not self._run_lock.acquire(blocking=False):
            return {"success": False, "message": "任务正在执行中"}

        self._stop_event.clear()
        self.save_data("running", True)
        self.save_data("last_run", self._aware_now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            self.__get_fonts()
            services = self._get_trimemedia_services()
            if not services:
                return {"success": False, "message": "未找到可用的飞牛媒体服务器"}
            libraries = self._load_target_libraries(services)
            if not libraries:
                return {"success": False, "message": "没有找到可处理的媒体库"}

            generated_count = 0
            uploaded_count = 0
            items: List[Dict[str, Any]] = []
            for library in libraries:
                if self._stop_event.is_set():
                    items.append({"server": library.get("server_name"), "library_name": library.get("name"), "success": False, "uploaded": False, "message": "任务已手动停止"})
                    break
                result = self._process_library(services.get(library["server_name"]), library)
                items.append(result)
                if result.get("success"):
                    generated_count += 1
                if result.get("uploaded"):
                    uploaded_count += 1

            finished_at = self._aware_now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"已处理 {len(items)} 个媒体库，成功生成 {generated_count} 个封面"
            if self._auto_upload:
                message += f"，自动替换成功 {uploaded_count} 个"
            payload = {"success": generated_count > 0, "message": message, "reason": reason, "generated_count": generated_count, "uploaded_count": uploaded_count, "items": items, "finished_at": finished_at}
            self.save_data("latest_result", payload)
            self._append_history({"time": finished_at, "message": message, "generated_count": generated_count, "uploaded_count": uploaded_count, "success": payload["success"]})
            return payload
        except Exception as err:
            logger.exception("%s 执行失败：%s", self.plugin_name, err)
            payload = {"success": False, "message": f"执行失败：{err}"}
            self.save_data("latest_result", payload)
            return payload
        finally:
            self.save_data("running", False)
            self._stop_event.clear()
            self._run_lock.release()

    def _get_trimemedia_services(self) -> Dict[str, Any]:
        helper = self._mediaserver_helper or MediaServerHelper()
        try:
            filters = self._selected_servers or None
            services = helper.get_services(name_filters=filters) or {}
        except Exception as err:
            logger.warning("%s 获取媒体服务器失败：%s", self.plugin_name, err)
            return {}
        available: Dict[str, Any] = {}
        for name, service in services.items():
            if getattr(service, "type", "") != "trimemedia":
                continue
            instance = getattr(service, "instance", None)
            if instance is not None and hasattr(instance, "is_inactive") and callable(getattr(instance, "is_inactive", None)):
                try:
                    if instance.is_inactive() and hasattr(instance, "reconnect"):
                        instance.reconnect()
                except Exception:
                    pass
            available[name] = service
        return available

    def _collect_server_options(self) -> List[Dict[str, str]]:
        helper = self._mediaserver_helper or MediaServerHelper()
        items: List[Dict[str, str]] = []
        try:
            configs = helper.get_configs() or {}
            iterator = configs.values() if isinstance(configs, dict) else configs
            for config in iterator:
                if getattr(config, "type", "") != "trimemedia":
                    continue
                name = getattr(config, "name", "")
                if name:
                    items.append({"title": name, "value": name})
        except Exception as err:
            logger.warning("%s 获取飞牛媒体服务器配置失败：%s", self.plugin_name, err)
        return items

    def _collect_library_options(self) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        services = self._get_trimemedia_services()
        for server_name, service in services.items():
            for library in self._fetch_server_libraries(service):
                library_id = str(library.get("id") or "").strip()
                if not library_id:
                    continue
                items.append({"title": f"{server_name} / {library.get('name') or library_id}", "value": f"{server_name}::{library_id}"})
        return items

    def _load_target_libraries(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        allowed = set(self._include_libraries)
        libraries: List[Dict[str, Any]] = []
        for server_name, service in services.items():
            for library in self._fetch_server_libraries(service):
                library_id = str(library.get("id") or "").strip()
                if not library_id:
                    continue
                library["server_name"] = server_name
                library["library_key"] = f"{server_name}::{library_id}"
                if allowed and library["library_key"] not in allowed:
                    continue
                libraries.append(library)
        return libraries

    def _fetch_server_libraries(self, service: Any) -> List[Dict[str, Any]]:
        instance = getattr(service, "instance", None)
        if instance is None or not hasattr(instance, "get_librarys"):
            return []
        try:
            raw_libraries = instance.get_librarys(hidden=False) or []
        except Exception as err:
            logger.warning("%s 读取飞牛媒体库失败：%s / %s", self.plugin_name, getattr(service, "name", ""), err)
            return []
        libraries: List[Dict[str, Any]] = []
        for library in raw_libraries:
            data = self._normalize_library(library)
            if data.get("id"):
                logger.info(
                    "%s",
                    format_library_image_stats(
                        plugin_name=self.plugin_name,
                        server_name=getattr(service, "name", "") or "",
                        library_name=data.get("name") or "",
                        library_id=data.get("id") or "",
                        returned_count=count_non_empty_items(data.get("image_list") or []),
                        required_items=self.__get_required_items(),
                    ),
                )
                libraries.append(data)
        return libraries

    def _normalize_library(self, library: Any) -> Dict[str, Any]:
        if isinstance(library, dict):
            get_value = lambda key, default=None: library.get(key, default)
        else:
            get_value = lambda key, default=None: getattr(library, key, default)
        image_list = []
        for item in get_value("image_list", []) or []:
            value = str(item or "").strip()
            if value:
                image_list.append(value)
        return {
            "id": str(get_value("id", "") or "").strip(),
            "name": str(get_value("name", "") or "").strip(),
            "type": str(get_value("type", "") or "").strip(),
            "image_list": image_list,
            "link": str(get_value("link", "") or "").strip(),
            "server_type": str(get_value("server_type", "trimemedia") or "trimemedia").strip(),
        }

    def _process_library(self, service: Any, library: Dict[str, Any]) -> Dict[str, Any]:
        server_name = library.get("server_name") or getattr(service, "name", "")
        library_name = library.get("name") or str(library.get("id"))
        runtime = self._extract_trimemedia_runtime(server_name, service, library)
        required_items = self.__get_required_items()
        library_dir = self._library_cache_dir(server_name, library_name, str(library.get("id") or ""))
        image_urls = self._expand_trimemedia_library_image_urls(
            service=service,
            library=library,
            runtime=runtime,
            required_items=required_items,
        )

        ok, message = self._prepare_library_images_from_urls(
            library_dir=library_dir,
            image_urls=image_urls,
            required_items=required_items,
            runtime=runtime,
            server_name=server_name,
            library_name=library_name,
            library_id=str(library.get("id") or ""),
        )
        if not ok:
            return {"server": server_name, "library_name": library_name, "library_id": library.get("id"), "success": False, "uploaded": False, "message": message}

        title_zh, title_en, config_bg_color = self.__get_title_from_config(library_name)
        image_base64 = self._generate_image_from_path(
            server_name=server_name,
            library_name=library_name,
            library_dir=library_dir,
            title=(title_zh, title_en),
            config_bg_color=config_bg_color,
        )
        if not image_base64:
            return {"server": server_name, "library_name": library_name, "library_id": library.get("id"), "success": False, "uploaded": False, "message": "封面生成失败"}

        output_file, output_ext = self._save_generated_cover(
            image_base64=image_base64,
            server_name=server_name,
            library_name=library_name,
            library_id=str(library.get("id") or ""),
        )
        uploaded = False
        upload_message = "仅生成本地封面"
        if self._auto_upload:
            uploaded, upload_message = self._upload_trimemedia_cover(library, output_file, service=service, runtime=runtime, output_ext=output_ext)

        return {
            "server": server_name,
            "library_name": library_name,
            "library_id": library.get("id"),
            "success": True,
            "uploaded": uploaded,
            "message": upload_message if self._auto_upload else "封面生成成功",
            "output_file": str(output_file),
            "preview_url": self._saved_cover_to_src(output_file),
        }

    def _prepare_library_images_from_urls(
        self,
        library_dir: Path,
        image_urls: List[str],
        required_items: int,
        runtime: Dict[str, Any],
        server_name: str = "",
        library_name: str = "",
        library_id: str = "",
    ) -> Tuple[bool, str]:
        if library_dir.exists():
            shutil.rmtree(library_dir, ignore_errors=True)
        library_dir.mkdir(parents=True, exist_ok=True)

        unique_urls: List[str] = []
        seen = set()
        for item in image_urls:
            url = str(item or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            unique_urls.append(url)
        logger.info(
            "%s",
            format_library_image_stats(
                plugin_name=self.plugin_name,
                server_name=server_name,
                library_name=library_name,
                library_id=library_id,
                returned_count=count_non_empty_items(image_urls),
                required_items=required_items,
                deduped_count=len(unique_urls),
            ),
        )
        if not unique_urls:
            return False, "媒体库没有可用的封面源图"
        random.shuffle(unique_urls)

        success_count = 0
        content_hashes = set()
        for url in unique_urls:
            if success_count >= required_items:
                break
            if self._stop_event.is_set():
                return False, "任务已手动停止"
            try:
                if self._is_trimemedia_runtime_ready(runtime) and self._is_trimemedia_request(url, runtime):
                    response = self._trimemedia_http_request(runtime=runtime, method="GET", url=url)
                else:
                    response = requests.get(url, timeout=20, headers={"User-Agent": settings.USER_AGENT})
                response.raise_for_status()
                content_type = str(response.headers.get("content-type") or "").lower()
                if "application/json" in content_type:
                    payload = response.json()
                    raise ValueError(payload.get("msg") or str(payload))
                content = response.content
                content_hash = hashlib.sha1(content).hexdigest()
                if content_hash in content_hashes:
                    continue
                content_hashes.add(content_hash)
                success_count += 1
                (library_dir / f"{success_count}.jpg").write_bytes(content)
            except Exception as err:
                logger.warning("%s 下载媒体库源图失败：%s / %s", self.plugin_name, url, err)
        if success_count <= 0:
            return False, "媒体库源图下载失败"
        if self._cover_style == "static_5":
            render_mode = resolve_style5_render_mode(success_count)
            logger.info(
                "%s style_5 素材缓存保留真实张数 | 服务器=%s | 媒体库=%s | id=%s | 下载成功=%s | 模式=%s",
                self.plugin_name,
                server_name,
                library_name,
                library_id,
                success_count,
                render_mode.get("mode"),
            )
            return True, f"已准备 {success_count} 张不重复封面源图（style_5 保留真实张数）"
        if not self.prepare_library_images(library_dir, required_items=required_items):
            return False, "媒体库源图数量不足，无法补齐封面素材"
        return True, f"已准备 {success_count} 张不重复封面源图"

    def prepare_library_images(self, library_dir: Path, required_items: int = 9) -> bool:
        existing = [item for item in sorted(library_dir.glob("*.jpg"), key=lambda p: p.name) if item.is_file()]
        if not existing:
            return False
        source_images = list(existing)
        last_used: Optional[Path] = None
        for index in range(1, required_items + 1):
            target = library_dir / f"{index}.jpg"
            if target.exists():
                continue
            candidates = [item for item in source_images if item != last_used] or source_images
            selected = random.choice(candidates)
            shutil.copyfile(selected, target)
            last_used = selected
        return True

    def _expand_trimemedia_library_image_urls(
        self,
        service: Any,
        library: Dict[str, Any],
        runtime: Dict[str, Any],
        required_items: int,
    ) -> List[str]:
        base_urls = merge_unique_image_urls(library.get("image_list") or [])
        target_count = min(max(required_items * 4, required_items), 60)
        extra_urls: List[str] = []
        need_item_pool = self._cover_style == "static_5" or len(base_urls) < required_items
        if need_item_pool:
            extra_urls = self._fetch_trimemedia_library_item_image_urls(
                service=service,
                library_id=str(library.get("id") or ""),
                runtime=runtime,
                target_count=target_count,
            )
        if self._cover_style == "static_5":
            primary_urls, source = pick_style5_source_urls(
                base_urls=base_urls,
                supplemental_urls=extra_urls,
            )
            candidate_urls = list(primary_urls)
            if source == "supplemental" and len(primary_urls) < max(1, required_items) and base_urls:
                candidate_urls = merge_unique_image_urls(primary_urls + base_urls, limit=target_count)
                source = "supplemental+base"
            library_key = str(
                library.get("library_key")
                or f"{library.get('server_name') or getattr(service, 'name', '')}::{library.get('id') or ''}"
            ).strip()
            primary_state = self.get_data("style5_last_primary_urls") or {}
            if not isinstance(primary_state, dict):
                primary_state = {}
            last_primary = str(primary_state.get(library_key) or "").strip()
            selected_urls, avoided_last_primary = select_style5_image_urls(
                candidate_urls=candidate_urls,
                required_count=max(1, required_items),
                last_primary_url=last_primary,
            )
            if selected_urls:
                self.save_data(
                    "style5_last_primary_urls",
                    remember_style5_primary(
                        state=primary_state,
                        library_key=library_key,
                        primary_url=selected_urls[0],
                    ),
                )
            render_mode = resolve_style5_render_mode(len(selected_urls))
            logger.info(
                "%s style_5 选图策略 | 服务器=%s | 媒体库=%s | id=%s | key=%s | 来源=%s | 候选=%s | 抽取=%s | 避开上次主图=%s | 模式=%s | 当前风格需要 %s 张",
                self.plugin_name,
                library.get("server_name") or getattr(service, "name", "") or "",
                library.get("name") or "",
                str(library.get("id") or ""),
                library_key,
                source,
                len(candidate_urls),
                len(selected_urls),
                "是" if avoided_last_primary else "否",
                render_mode.get("mode"),
                required_items,
            )
            return selected_urls
        selected_urls = prefer_supplemental_image_urls(
            base_urls=base_urls,
            supplemental_urls=extra_urls,
            limit=target_count,
        )
        logger.info(
            "%s 媒体库条目补图 | 服务器=%s | 媒体库=%s | id=%s | image_list=%s 张 | 条目补充=%s 张 | 最终采用=%s 张 | 来源=%s | 当前风格需要 %s 张",
            self.plugin_name,
            library.get("server_name") or getattr(service, "name", "") or "",
            library.get("name") or "",
            str(library.get("id") or ""),
            len(base_urls),
            len(extra_urls),
            len(selected_urls),
            "条目补图" if extra_urls else "媒体库图",
            required_items,
        )
        return selected_urls

    def _fetch_trimemedia_library_item_image_urls(
        self,
        service: Any,
        library_id: str,
        runtime: Dict[str, Any],
        target_count: int,
    ) -> List[str]:
        instance = getattr(service, "instance", None)
        api = getattr(instance, "_api", None)
        library_guid = str(library_id or "").strip()
        if not library_guid or api is None or not hasattr(api, "item_list") or not hasattr(api, "item"):
            return []

        page_size = max(50, min(200, target_count * 5))
        max_pages = max(1, min(10, (target_count * 6 + page_size - 1) // page_size))

        def fetch_children(parent_guid: str) -> List[Any]:
            collected: List[Any] = []
            for page in range(1, max_pages + 1):
                try:
                    batch = list(api.item_list(guid=parent_guid, page=page, page_size=page_size) or [])
                except Exception as err:
                    logger.warning("%s 读取媒体库条目失败：%s / %s", self.plugin_name, parent_guid, err)
                    break
                if not batch:
                    break
                random.shuffle(batch)
                collected.extend(batch)
                if len(batch) < page_size:
                    break
            return collected

        def fetch_details(item_guid: str) -> Any:
            try:
                return api.item(guid=item_guid)
            except Exception as err:
                logger.warning("%s 读取媒体详情失败：%s / %s", self.plugin_name, item_guid, err)
                return None

        image_paths = collect_library_item_image_paths(
            library_guid=library_guid,
            fetch_children=fetch_children,
            fetch_details=fetch_details,
            limit=target_count,
        )
        random.shuffle(image_paths)
        resolved_urls = merge_unique_image_urls(
            [
                self._resolve_trimemedia_item_image_url(
                    image_path=image_path,
                    runtime=runtime,
                    service=service,
                )
                for image_path in image_paths
            ],
            limit=target_count,
        )
        return resolved_urls

    def _resolve_trimemedia_item_image_url(
        self,
        image_path: str,
        runtime: Dict[str, Any],
        service: Any,
    ) -> str:
        value = str(image_path or "").strip()
        if not value:
            return ""
        if value.startswith("http://") or value.startswith("https://"):
            return value
        host = str(runtime.get("api_host") or "").rstrip("/")
        if not host:
            host = str(getattr(getattr(getattr(service, "instance", None), "_api", None), "host", "") or "").rstrip("/")
        if not host:
            return value
        if not value.startswith("/"):
            value = "/" + value
        return f"{host}{value}"

    def _generate_image_from_path(self, server_name: str, library_name: str, library_dir: Path, title: Tuple[str, str], config_bg_color: Optional[str] = None) -> Any:
        if not self.health_check():
            return False
        title_scale = _safe_float(self._title_scale, 1.0, 0.2, 4.0)
        zh_font_size = float(self._zh_font_size)
        en_font_size = float(self._en_font_size)
        zh_font_size = self._resolution_config.get_font_size(zh_font_size) * title_scale
        en_font_size = self._resolution_config.get_font_size(en_font_size) * title_scale
        font_path = (str(self._zh_font_path), str(self._en_font_path))
        font_size = (float(zh_font_size), float(en_font_size))
        font_offset = (
            _safe_float(self._zh_font_offset, 0.0),
            _safe_float(self._title_spacing, 40.0) * title_scale,
            _safe_float(self._en_line_spacing, 40.0) * title_scale,
        )
        bg_color_config = {"mode": self._bg_color_mode, "custom_color": self._custom_bg_color, "config_color": config_bg_color}
        logger.info("%s 正在生成媒体库封面：%s / %s / %s", self.plugin_name, server_name, library_name, self._cover_style)
        if self._cover_style == "static_1":
            return create_style_static_1(str(library_dir), title, font_path, font_size=font_size, font_offset=font_offset, blur_size=self._blur_size, color_ratio=self._color_ratio, resolution_config=self._resolution_config, bg_color_config=bg_color_config)
        single_image = str(library_dir / "1.jpg")
        if self._cover_style == "static_2":
            return create_style_static_2(single_image, title, font_path, font_size=font_size, font_offset=font_offset, blur_size=self._blur_size, color_ratio=self._color_ratio, resolution_config=self._resolution_config, bg_color_config=bg_color_config)
        if self._cover_style == "static_3":
            return create_style_static_3(library_dir, title, font_path, font_size=font_size, font_offset=font_offset, is_blur=self._multi_1_blur, blur_size=self._blur_size, color_ratio=self._color_ratio, resolution_config=self._resolution_config, bg_color_config=bg_color_config)
        if self._cover_style == "static_4":
            return create_style_static_4(single_image, title, font_path, font_size=font_size, font_offset=font_offset, blur_size=self._blur_size, color_ratio=self._color_ratio, resolution_config=self._resolution_config, bg_color_config=bg_color_config)
        if self._cover_style == "static_5":
            return create_style_static_5(str(library_dir), title, font_path, font_size=font_size, font_offset=font_offset, blur_size=self._blur_size, color_ratio=self._color_ratio, resolution_config=self._resolution_config, bg_color_config=bg_color_config)
        raise ValueError(f"不支持的风格：{self._cover_style}")

    def _save_generated_cover(self, image_base64: str, server_name: str, library_name: str, library_id: str) -> Tuple[Path, str]:
        content = base64.b64decode(image_base64)
        output_ext = self._detect_image_extension(content)
        output_dir = self._covers_output or (self.get_data_path() / "output")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{self.__sanitize_filename(server_name)}_{self.__sanitize_filename(library_name)}_{library_id}_{timestamp}{output_ext}"
        output_path = output_dir / file_name
        output_path.write_bytes(content)
        self._trim_saved_cover_history(server_name, library_name)
        return output_path, output_ext

    def _trim_saved_cover_history(self, server_name: str, library_name: str):
        output_dir = self._covers_output or (self.get_data_path() / "output")
        prefix = f"{self.__sanitize_filename(server_name)}_{self.__sanitize_filename(library_name)}_"
        files = [item for item in output_dir.iterdir() if item.is_file() and item.name.startswith(prefix)]
        files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        for stale in files[self._covers_history_limit_per_library:]:
            stale.unlink(missing_ok=True)

    def _get_selected_history_files(self) -> List[str]:
        return normalize_history_paths(self.get_data("selected_history_files") or [])

    def _set_selected_history_files(self, paths: List[str]):
        self.save_data("selected_history_files", normalize_history_paths(paths))

    def _prune_selected_history_files(self, visible_paths: Optional[List[str]] = None) -> List[str]:
        selected = self._get_selected_history_files()
        visible = visible_paths or [
            item["path"] for item in self.__get_recent_generated_covers(limit=self._covers_page_history_limit) if item.get("path")
        ]
        retained = retain_history_selection(selected, visible)
        if retained != selected:
            self._set_selected_history_files(retained)
        return retained

    def _clear_saved_cover_history(self) -> int:
        output_dir = self._covers_output or (self.get_data_path() / "output")
        if not output_dir.exists():
            return 0
        allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        removed = 0
        for item in output_dir.iterdir():
            if not item.is_file() or item.suffix.lower() not in allowed_ext:
                continue
            item.unlink(missing_ok=True)
            removed += 1
        return removed

    def _library_cache_dir(self, server_name: str, library_name: str, library_id: str) -> Path:
        base = self._covers_path or (self.get_data_path() / "input")
        folder_name = f"{self.__sanitize_filename(server_name)}_{self.__sanitize_filename(library_name)}_{self.__sanitize_filename(library_id)}"
        return base / folder_name

    def _saved_cover_to_src(self, path: Path) -> str:
        if Image is None:
            return ""
        try:
            with Image.open(path) as image:
                if getattr(image, "is_animated", False):
                    image.seek(0)
                thumb = image.convert("RGB")
                thumb.thumbnail((480, 270))
                buffer = BytesIO()
                thumb.save(buffer, format="JPEG", quality=75)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
        except Exception:
            return ""

    def __get_recent_generated_covers(self, limit: int = 20) -> List[Dict[str, Any]]:
        output_dir = self._covers_output or (self.get_data_path() / "output")
        if not output_dir.exists():
            return []
        allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        items: List[Dict[str, Any]] = []
        for item in output_dir.iterdir():
            if not item.is_file() or item.suffix.lower() not in allowed_ext:
                continue
            stat = item.stat()
            items.append({"name": item.name, "path": str(item), "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "mtime_ts": stat.st_mtime, "size": self.__format_size(stat.st_size), "src": self._saved_cover_to_src(item)})
        items.sort(key=lambda row: row["mtime_ts"], reverse=True)
        return items[:max(1, limit)]

    @staticmethod
    def __format_size(size_bytes: int) -> str:
        size = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
            size /= 1024
        return f"{int(size_bytes)} B"

    def _select_style_index(self, index: int) -> Dict[str, Any]:
        self._cover_style_base = f"static_{max(1, min(5, int(index)))}"
        self._cover_style_variant = "static"
        self._cover_style = self.__compose_cover_style(self._cover_style_base, "static")
        self._update_config()
        return {"success": True, "message": f"已切换到 {self._cover_style}"}

    def _set_cover_style(self, cover_style: str, persist: bool = True) -> bool:
        base, _ = self.__resolve_cover_style_ui(cover_style)
        self._cover_style_base = base
        self._cover_style_variant = "static"
        self._cover_style = self.__compose_cover_style(base, "static")
        if persist:
            self._update_config()
        return True

    def __compose_cover_style(self, base_style: str, variant: str) -> str:
        base = base_style if base_style in {"static_1", "static_2", "static_3", "static_4", "static_5"} else "static_1"
        return base

    def __resolve_cover_style_ui(self, cover_style: str) -> Tuple[str, str]:
        if cover_style in {"animated_1", "animated_2", "animated_3", "animated_4", "animated_5"}:
            suffix = cover_style.split("_")[-1]
            return f"static_{suffix}", "static"
        if cover_style in {"static_1", "static_2", "static_3", "static_4", "static_5"}:
            return cover_style, "static"
        return "static_1", "static"

    def __get_cover_style_parts(self) -> Tuple[str, int]:
        try:
            index = int(self._cover_style.split("_")[-1])
        except Exception:
            index = 1
        return "static", max(1, min(5, index))

    def __get_required_items(self) -> int:
        if self._cover_style == "static_1":
            return 3
        if self._cover_style == "static_3":
            return 9
        if self._cover_style == "static_5":
            return 4
        return 1

    def __build_page_style_cards(self, style_variant: str, selected_index: int) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        for index in range(1, 6):
            cards.append(
                {
                    "component": "VCol",
                    "props": {"cols": 12, "sm": 6, "md": 3},
                    "content": [
                        {
                            "component": "VCard",
                            "props": {"variant": "flat", "elevation": 3 if index == selected_index else 1, "color": "primary" if index == selected_index else None, "class": "cursor-pointer"},
                            "events": {"click": {"api": f"plugin/FnMediaCoverGenerator/select_style_{index}", "method": "post"}},
                            "content": [
                                {"component": "VImg", "props": {"src": self.__style_preview_src(index), "aspect-ratio": "16/9", "cover": True}},
                                {"component": "VCardText", "props": {"class": "py-2 text-center"}, "text": f"风格{index}{'（当前）' if index == selected_index else ''} / 静态"},
                            ],
                        }
                    ],
                }
            )
        return cards

    @staticmethod
    def __style_preview_src(index: int) -> str:
        safe_index = max(1, min(5, int(index)))
        return f"https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/images/style_{safe_index}.jpeg"

    def _build_resolution_config(self) -> ResolutionConfig:
        if self._resolution == "custom":
            return ResolutionConfig((self._custom_width, self._custom_height))
        if self._resolution not in {"1080p", "720p", "480p"}:
            self._resolution = "1080p"
        return ResolutionConfig(self._resolution)

    def __font_search_dirs(self) -> List[Path]:
        dirs = []
        if self._font_path:
            dirs.append(Path(self._font_path))
        repo_font_dir = Path(__file__).resolve().parents[2] / "fonts"
        dirs.append(repo_font_dir)
        seen = set()
        unique: List[Path] = []
        for directory in dirs:
            key = str(directory)
            if key in seen:
                continue
            seen.add(key)
            if directory.exists() and directory.is_dir():
                unique.append(directory)
        return unique

    def __find_font_file(self, aliases: List[str], exts: List[str]) -> Optional[str]:
        normalized_aliases = [item.lower() for item in aliases if item]
        compact_aliases = [re.sub(r"[\s_\-]+", "", item) for item in normalized_aliases]
        for directory in self.__font_search_dirs():
            for font_file in sorted(directory.iterdir(), key=lambda item: item.name.lower()):
                if not font_file.is_file() or font_file.suffix.lower() not in exts:
                    continue
                stem = font_file.stem.lower()
                name = font_file.name.lower()
                compact_stem = re.sub(r"[\s_\-]+", "", stem)
                compact_name = re.sub(r"[\s_\-]+", "", name)
                for alias, compact_alias in zip(normalized_aliases, compact_aliases):
                    if alias in stem or alias in name or compact_alias in compact_stem or compact_alias in compact_name:
                        return str(font_file)
        return None

    def __get_font_presets(self) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, Optional[str]], Dict[str, Optional[str]]]:
        zh_specs = [
            {"title": "潮黑", "value": "chaohei", "aliases": ["chaohei", "潮黑", "chao_hei"]},
            {"title": "雅宋", "value": "yasong", "aliases": ["yasong", "雅宋", "ya_song"]},
        ]
        en_specs = [
            {"title": "EmblemaOne", "value": "EmblemaOne", "aliases": ["emblemaone", "emblema_one"]},
            {"title": "Melete", "value": "Melete", "aliases": ["melete"]},
            {"title": "Phosphate", "value": "Phosphate", "aliases": ["phosphate"]},
            {"title": "JosefinSans", "value": "JosefinSans", "aliases": ["josefinsans", "josefin_sans"]},
            {"title": "LilitaOne", "value": "LilitaOne", "aliases": ["lilitaone", "lilita_one"]},
            {"title": "Monoton", "value": "Monoton", "aliases": ["monoton"]},
            {"title": "Plaster", "value": "Plaster", "aliases": ["plaster"]},
        ]
        all_specs = zh_specs + en_specs
        zh_paths: Dict[str, Optional[str]] = {}
        en_paths: Dict[str, Optional[str]] = {}
        for spec in all_specs:
            aliases = list(spec["aliases"])
            aliases.extend([spec["title"].lower(), spec["value"].lower(), re.sub(r"[\s_\-]+", "", spec["value"].lower())])
            zh_paths[spec["value"]] = self.__find_font_file(aliases, [".ttf", ".otf", ".woff2", ".woff"])
            en_paths[spec["value"]] = self.__find_font_file(aliases, [".ttf", ".otf", ".woff2", ".woff"])
        return (
            [{"title": item["title"], "value": item["value"]} for item in zh_specs],
            [{"title": item["title"], "value": item["value"]} for item in en_specs],
            zh_paths,
            en_paths,
        )

    def __get_fonts(self):
        font_dir = Path(self._font_path or (self.get_data_path() / "fonts"))
        font_dir.mkdir(parents=True, exist_ok=True)
        _, _, zh_preset_paths, en_preset_paths = self.__get_font_presets()

        for lang, preset, custom, preset_paths, attr_name, fallback_ext in [
            ("主标题", self._zh_font_preset, self._zh_font_custom, zh_preset_paths, "_zh_font_path", ".ttf"),
            ("副标题", self._en_font_preset, self._en_font_custom, en_preset_paths, "_en_font_path", ".ttf"),
        ]:
            custom = str(custom or "").strip()
            preset = str(preset or "").strip()
            local_path = ""
            url = DEFAULT_FONT_URLS.get(preset, "")
            if custom:
                if re.match(r"^https?://", custom, re.IGNORECASE):
                    url = custom
                else:
                    local_path = custom
            if not local_path:
                local_path = str(preset_paths.get(preset) or "")

            if local_path and validate_font_file(Path(local_path)):
                setattr(self, attr_name, str(local_path))
                continue

            if not url:
                raise RuntimeError(f"{lang}字体未配置")
            extension = self.get_file_extension_from_url(url, fallback_ext=fallback_ext)
            file_name = f"{preset.lower()}_{hashlib.md5(url.encode('utf-8')).hexdigest()[:8]}{extension}"
            target = font_dir / file_name
            if not validate_font_file(target):
                if not self.download_font_safely_with_timeout(url, target):
                    raise RuntimeError(f"{lang}字体下载失败：{url}")
            setattr(self, attr_name, str(target))

    def health_check(self) -> bool:
        if not self._resolution_config:
            self._resolution_config = self._build_resolution_config()
        if not self._zh_font_path or not self._en_font_path:
            self.__get_fonts()
        if not validate_font_file(Path(self._zh_font_path)):
            return False
        if not validate_font_file(Path(self._en_font_path)):
            return False
        return True

    def download_font_safely_with_timeout(self, font_url: str, font_path: Path, timeout: int = 60) -> bool:
        return self.download_font_safely(font_url, font_path, retries=1, timeout=timeout)

    def download_font_safely(self, font_url: str, font_path: Path, retries: int = 2, timeout: int = 30) -> bool:
        network_helper = NetworkHelper(timeout=timeout, max_retries=retries)
        strategies: List[Tuple[str, str]] = []
        if ("github.com" in font_url or "raw.githubusercontent.com" in font_url) and settings.GITHUB_PROXY:
            strategies.append(("proxy", f"{UrlUtils.standardize_base_url(settings.GITHUB_PROXY)}{font_url}"))
        strategies.append(("direct", font_url))

        for _, target_url in strategies:
            temp_path = font_path.with_suffix(".temp")
            try:
                if network_helper.download_file_sync(target_url, temp_path) and validate_font_file(temp_path):
                    temp_path.replace(font_path)
                    return True
            except Exception:
                pass
            finally:
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)
        return False

    def get_file_extension_from_url(self, url: str, fallback_ext: str = ".ttf") -> str:
        try:
            parsed = urlparse(url)
            suffix = Path(parsed.path).suffix
            if suffix:
                return suffix
        except Exception:
            pass
        return fallback_ext

    def __load_title_config(self, yaml_str: str) -> Dict[str, List[str]]:
        if not yaml_str:
            return {}
        try:
            title_config = yaml.safe_load(yaml_str) or {}
        except Exception as err:
            logger.warning("%s 标题映射 YAML 解析失败：%s", self.plugin_name, err)
            return {}
        if not isinstance(title_config, dict):
            return {}
        normalized: Dict[str, List[str]] = {}
        for key, value in title_config.items():
            if isinstance(value, list) and len(value) >= 2 and isinstance(value[0], str) and isinstance(value[1], str):
                rows = [value[0], value[1]]
                if len(value) >= 3 and isinstance(value[2], str):
                    rows.append(value[2])
                normalized[str(key)] = rows
        return normalized

    def __get_default_subtitle(self, library_name: str) -> str:
        normalized_name = re.sub(r"\s+", "", str(library_name or "").strip())
        if not normalized_name:
            return ""
        if normalized_name in DEFAULT_SUBTITLE_MAP:
            return DEFAULT_SUBTITLE_MAP[normalized_name]
        if "动画" in normalized_name and "电影" in normalized_name:
            return "Animated Films"
        if "国漫" in normalized_name:
            return "GUOMAN"
        if "动漫" in normalized_name or "番剧" in normalized_name:
            return "Anime"
        if "欧美" in normalized_name and "剧" in normalized_name:
            return "Western Series"
        if ("日韩" in normalized_name or "日剧" in normalized_name or "韩剧" in normalized_name) and "剧" in normalized_name:
            return "Japan & Korea Drama"
        if "国产" in normalized_name and "剧" in normalized_name:
            return "Chinese Drama"
        if "纪录" in normalized_name:
            return "Documentaries"
        if "综艺" in normalized_name:
            return "Variety Shows"
        if "电影" in normalized_name:
            return "Films"
        if "剧" in normalized_name:
            return "TV Series"
        if re.fullmatch(r"[A-Za-z0-9 _-]+", str(library_name or "").strip()):
            return re.sub(r"[_-]+", " ", str(library_name or "").strip()).title()
        return ""

    def __get_title_from_config(self, library_name: str) -> Tuple[str, str, Optional[str]]:
        zh_title = library_name
        en_title = self.__get_default_subtitle(library_name)
        bg_color = None
        for config_key, config_value in self._current_config.items():
            if str(config_key).strip() != str(library_name).strip():
                continue
            zh_title = config_value[0]
            en_title = config_value[1].strip() if len(config_value) > 1 and isinstance(config_value[1], str) else ""
            if not en_title:
                en_title = self.__get_default_subtitle(zh_title or library_name)
            bg_color = config_value[2] if len(config_value) > 2 else None
            break
        return zh_title, en_title, bg_color

    def __sanitize_filename(self, filename: str) -> str:
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", str(filename or "").strip())
        safe_name = safe_name.strip(" .")
        if not safe_name:
            safe_name = "unknown"
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        return safe_name

    def _clean_image_cache(self) -> int:
        removed = 0
        cache_dir = self._covers_path or (self.get_data_path() / "input")
        if not cache_dir.exists():
            return removed
        for item in cache_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
                removed += 1
            elif item.is_file():
                item.unlink(missing_ok=True)
                removed += 1
        return removed

    def _clean_font_cache(self) -> int:
        removed = 0
        font_dir = self._font_path or (self.get_data_path() / "fonts")
        if not font_dir.exists():
            return removed
        for item in font_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
                removed += 1
        return removed

    def _detect_image_extension(self, content: bytes) -> str:
        if content.startswith(b"\x89PNG"):
            return ".png"
        if content.startswith(b"GIF8"):
            return ".gif"
        if content.startswith(b"RIFF") and b"WEBP" in content[:16]:
            return ".webp"
        if content.startswith(b"\xff\xd8"):
            return ".jpg"
        return ".png"

    def _upload_trimemedia_cover(self, library: Dict[str, Any], output_file: Path, service: Any = None, runtime: Optional[Dict[str, Any]] = None, output_ext: str = ".png") -> Tuple[bool, str]:
        runtime = runtime or self._extract_trimemedia_runtime(library.get("server_name"), service, library)
        if not runtime.get("base_url"):
            return False, "未能识别飞牛地址"
        if not self._is_trimemedia_runtime_ready(runtime):
            return False, "未能从飞牛运行时读取有效鉴权"
        if output_ext.lower() == ".gif":
            return False, "GIF 动图已生成，但飞牛自动替换仅建议 APNG/PNG/WEBP"
        try:
            upload_info = self._trimemedia_upload_temp(runtime, output_file)
            hash_path = self._trimemedia_extract_hash_path(upload_info)
            if not hash_path:
                return False, f"临时图片上传未返回 hash_path：{self._trimemedia_upload_error(upload_info)}"
            payload = {"guid": library.get("id"), "poster_type": TRIMEMEDIA_SINGLE_POSTER_TYPE, "poster": hash_path}
            result = self._trimemedia_request(runtime, "/api/v1/mdb/setPoster", payload)
            code = result.get("code")
            if code not in (0, 200, None):
                return False, f"setPoster 返回异常：{self._trimemedia_upload_error(result)}"
            return True, "自动替换成功"
        except Exception as err:
            return False, f"自动替换失败：{err}"

    def _trimemedia_extract_hash_path(self, upload_info: Any) -> str:
        if not isinstance(upload_info, dict):
            return ""
        for container in [upload_info, upload_info.get("data")]:
            if isinstance(container, dict):
                hash_path = str(container.get("hash_path") or "").strip()
                if hash_path:
                    return hash_path
        return ""

    def _trimemedia_upload_error(self, payload: Any) -> str:
        try:
            return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            return str(payload)

    def _trimemedia_upload_temp(self, runtime: Dict[str, Any], output_file: Path) -> Dict[str, Any]:
        form_data = {"image_type": "poster"}
        signature_candidates = ["{}", json.dumps(form_data, ensure_ascii=False, separators=(",", ":")), ""]
        upload_name, upload_buffer, upload_mime = self._prepare_trimemedia_upload_file(output_file)
        try:
            files = {"file": (upload_name, upload_buffer, upload_mime)}
            last_error = "临时图片上传失败"
            for signature_body in signature_candidates:
                upload_buffer.seek(0)
                response = self._trimemedia_http_request(
                    runtime=runtime,
                    method="POST",
                    path="/api/v1/image/temp/upload",
                    files=files,
                    form_data=form_data,
                    signature_body_text=signature_body,
                )
                data = response.json()
                if data.get("code") in (0, 200, None):
                    return data
                last_error = data.get("msg") or self._trimemedia_upload_error(data)
            raise ValueError(last_error)
        finally:
            upload_buffer.close()

    def _prepare_trimemedia_upload_file(self, output_file: Path) -> Tuple[str, BytesIO, str]:
        suffix = output_file.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        if suffix == ".gif":
            raise ValueError("GIF 不支持自动上传，请改用 APNG")

        payload = output_file.read_bytes()
        if suffix in mime_map and len(payload) <= TRIMEMEDIA_UPLOAD_MAX_BYTES:
            ready = BytesIO(payload)
            ready.seek(0)
            return output_file.name, ready, mime_map[suffix]

        if Image is None:
            raise RuntimeError("Pillow 未安装，无法压缩上传图片")
        with Image.open(output_file) as source:
            is_animated = bool(getattr(source, "is_animated", False))
        if is_animated:
            raise ValueError("动态封面超过 5MB，请降低时长、FPS 或取图数量")

        qualities = (92, 86, 80, 74, 68, 62, 56, 50, 44, 38)
        scales = (1.0, 0.95, 0.9, 0.85, 0.8)
        best_payload = b""
        with Image.open(output_file) as source:
            source_image = source.convert("RGB")
        try:
            for scale in scales:
                candidate = source_image
                if scale != 1.0:
                    candidate = source_image.resize(
                        (max(1, int(source_image.width * scale)), max(1, int(source_image.height * scale))),
                        Image.Resampling.LANCZOS,
                    )
                try:
                    for quality in qualities:
                        buffer = BytesIO()
                        candidate.save(buffer, format="WEBP", quality=quality)
                        best_payload = buffer.getvalue() or best_payload
                        if len(best_payload) <= TRIMEMEDIA_UPLOAD_MAX_BYTES:
                            ready = BytesIO(best_payload)
                            ready.seek(0)
                            return f"{output_file.stem}.webp", ready, "image/webp"
                finally:
                    if candidate is not source_image:
                        candidate.close()
        finally:
            source_image.close()
        raise ValueError("无法将封面压缩到 5MB 内")

    def _trimemedia_request(self, runtime: Dict[str, Any], path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._trimemedia_http_request(runtime=runtime, method="POST", path=path, json_data=payload)
        data = response.json()
        code = data.get("code")
        if code not in (0, 200, None):
            raise ValueError(data.get("msg") or str(data))
        return data

    def _extract_trimemedia_runtime(self, server_name: str, service: Any, library: Dict[str, Any]) -> Dict[str, Any]:
        instance = getattr(service, "instance", None)
        helper = self._mediaserver_helper or MediaServerHelper()
        helper_config = None
        try:
            configs = helper.get_configs() or {}
            if isinstance(configs, dict):
                helper_config = configs.get(server_name)
        except Exception:
            helper_config = None

        service_config = getattr(service, "config", None)
        candidate_objects = [service, instance, service_config, helper_config]
        base_url = ""
        api_host = ""
        headers: Dict[str, str] = {}
        cookies: Dict[str, str] = {}
        token = ""
        apikey = ""

        for obj in candidate_objects:
            if obj is None:
                continue
            attrs = self._collect_object_attrs(obj)
            if not base_url:
                base_url = self._guess_base_url_from_attrs(attrs) or base_url
                if base_url and not api_host:
                    _, api_host = self._resolve_trimemedia_hosts(base_url)
            extra_headers, extra_cookies = self._guess_headers_cookies(attrs)
            headers.update({k: v for k, v in extra_headers.items() if v})
            cookies.update({k: v for k, v in extra_cookies.items() if v})

        if instance is not None:
            api = getattr(instance, "api", None) or getattr(instance, "_api", None)
            if api is not None:
                api_host_value = getattr(api, "host", None) or getattr(api, "_host", None) or ""
                token = getattr(api, "token", None) or getattr(api, "_token", None) or ""
                apikey = getattr(api, "apikey", None) or getattr(api, "_apikey", None) or TRIMEMEDIA_API_KEY
                base_url, api_host = self._resolve_trimemedia_hosts(str(api_host_value))
                session = getattr(api, "_session", None)
                if isinstance(session, requests.Session):
                    cookies.update(session.cookies.get_dict())

        raw_config = None
        for config_obj in [service_config, helper_config]:
            if getattr(config_obj, "config", None):
                raw_config = getattr(config_obj, "config", None)
                break
        config_values, _ = self._trimemedia_credentials_from_config(raw_config)
        if config_values.get("host"):
            config_base, config_api_host = self._resolve_trimemedia_hosts(str(config_values.get("host")))
            base_url = base_url or config_base
            api_host = api_host or config_api_host
        if not token and all(config_values.get(key) for key in ("host", "username", "password")):
            try:
                login_runtime = self._runtime_from_trimemedia_credentials(
                    host=str(config_values.get("host")),
                    username=str(config_values.get("username")),
                    password=str(config_values.get("password")),
                )
                base_url = login_runtime.get("base_url") or base_url
                api_host = login_runtime.get("api_host") or api_host
                headers.update(login_runtime.get("headers") or {})
                cookies.update(login_runtime.get("cookies") or {})
                token = login_runtime.get("token") or token
                apikey = login_runtime.get("apikey") or apikey
            except Exception as err:
                logger.warning("%s 飞牛配置登录失败：%s / %s", self.plugin_name, server_name, err)

        if not base_url and library.get("link"):
            base_url, api_host = self._resolve_trimemedia_hosts(str(library.get("link")))

        cookies = self._trimemedia_cookie_map(cookies, token)
        return {
            "base_url": base_url,
            "api_host": api_host,
            "headers": headers,
            "cookies": cookies,
            "token": token,
            "apikey": apikey or TRIMEMEDIA_API_KEY,
        }

    def _collect_object_attrs(self, obj: Any) -> Dict[str, Any]:
        attrs: Dict[str, Any] = {}
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
        return attrs

    def _trimemedia_credentials_from_config(self, config_data: Any) -> Tuple[Dict[str, str], List[str]]:
        if not isinstance(config_data, dict):
            return {}, []
        host = config_data.get("host") or config_data.get("url") or config_data.get("server")
        username = config_data.get("username") or config_data.get("user")
        password = config_data.get("password") or config_data.get("passwd") or config_data.get("pwd")
        return {
            "host": str(host or "").strip(),
            "username": str(username or "").strip(),
            "password": str(password or "").strip(),
        }, sorted([str(key) for key in config_data.keys()])[:120]

    def _runtime_from_trimemedia_credentials(self, host: str, username: str, password: str) -> Dict[str, Any]:
        api_host = self._probe_trimemedia_api_host(host)
        if not api_host:
            return {}
        base_url, normalized_api_host = self._resolve_trimemedia_hosts(api_host)
        session = requests.Session()
        payload = {"username": username, "password": password, "app_name": "trimemedia-web"}
        response = self._trimemedia_http_request(
            runtime={"base_url": base_url, "api_host": normalized_api_host, "headers": {}, "cookies": {}, "token": "", "apikey": TRIMEMEDIA_API_KEY},
            method="POST",
            path="/api/v1/login",
            json_data=payload,
            session=session,
        )
        data = response.json()
        if int(data.get("code") or -1) != 0:
            raise ValueError(data.get("msg") or str(data))
        token = str((data.get("data") or {}).get("token") or "").strip()
        if not token:
            raise ValueError("飞牛登录成功但未返回 token")
        return {
            "base_url": base_url,
            "api_host": normalized_api_host,
            "headers": {},
            "cookies": self._trimemedia_cookie_map(session.cookies.get_dict(), token),
            "token": token,
            "apikey": TRIMEMEDIA_API_KEY,
        }

    def _resolve_trimemedia_hosts(self, value: str) -> Tuple[str, str]:
        parsed = urlparse(str(value or "").strip())
        if not parsed.scheme or not parsed.netloc:
            return "", ""
        root = f"{parsed.scheme}://{parsed.netloc}"
        path = (parsed.path or "").rstrip("/")
        for marker in TRIMEMEDIA_PATH_MARKERS:
            if marker in path:
                path = path.split(marker, 1)[0].rstrip("/")
                break
        if path.endswith("/v"):
            api_host = f"{root}{path}"
            base_url = f"{root}{path[:-2]}".rstrip("/")
        else:
            base_url = f"{root}{path}".rstrip("/")
            api_host = f"{base_url}/v".rstrip("/")
        return base_url, api_host

    def _probe_trimemedia_api_host(self, host: str) -> str:
        base_url, api_host = self._resolve_trimemedia_hosts(host)
        for candidate in [api_host, base_url]:
            if not candidate:
                continue
            try:
                response = requests.get(f"{candidate}/api/v1/sys/version", headers={"Accept": "application/json", "User-Agent": settings.USER_AGENT}, timeout=20)
                response.raise_for_status()
                data = response.json()
                if int(data.get("code") or -1) == 0:
                    _, normalized_api_host = self._resolve_trimemedia_hosts(candidate)
                    return normalized_api_host
            except Exception:
                continue
        return ""

    def _is_trimemedia_runtime_ready(self, runtime: Optional[Dict[str, Any]]) -> bool:
        return bool(runtime and runtime.get("api_host") and runtime.get("token") and runtime.get("apikey"))

    def _is_trimemedia_request(self, url: str, runtime: Optional[Dict[str, Any]]) -> bool:
        if not runtime or not runtime.get("api_host"):
            return False
        api_host = str(runtime.get("api_host") or "").rstrip("/")
        base_url = str(runtime.get("base_url") or "").rstrip("/")
        return url.startswith(f"{api_host}/api/v1/") or (base_url and url.startswith(f"{base_url}/v/api/v1/"))

    def _trimemedia_cookie_map(self, cookies: Optional[Dict[str, Any]], token: str = "") -> Dict[str, str]:
        normalized: Dict[str, str] = {}
        if isinstance(cookies, dict):
            normalized.update({str(key): str(value) for key, value in cookies.items() if value is not None})
        token = str(token or "").strip()
        if token and not normalized.get(TRIMEMEDIA_TOKEN_COOKIE):
            normalized[TRIMEMEDIA_TOKEN_COOKIE] = token
        return normalized

    def _trimemedia_http_request(self, runtime: Dict[str, Any], method: str, path: Optional[str] = None, url: Optional[str] = None, json_data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, form_data: Optional[Dict[str, Any]] = None, signature_body_text: Optional[str] = None, session: Optional[requests.Session] = None) -> requests.Response:
        api_host = str(runtime.get("api_host") or "").rstrip("/")
        if not url and not (api_host and path):
            raise ValueError("缺少飞牛请求地址")
        full_url = str(url or f"{api_host}{path}")
        parsed = urlparse(full_url)
        api_path = parsed.path or (path or "")
        query_text = parsed.query or ""
        method = method.upper()
        body_text = ""
        if signature_body_text is not None:
            body_text = signature_body_text
        elif method != "GET" and json_data and files is None:
            body_text = json.dumps(json_data, ensure_ascii=False, separators=(",", ":"))

        headers = self._build_trimemedia_headers(runtime=runtime, api_path=api_path, query_text=query_text, body_text=body_text, include_content_type=bool(json_data and files is None))
        cookies = self._trimemedia_cookie_map(runtime.get("cookies"), str(runtime.get("token") or ""))
        requester = session or requests
        kwargs: Dict[str, Any] = {"method": method, "url": full_url, "headers": headers, "cookies": cookies, "timeout": 20}
        if files is not None:
            kwargs["files"] = files
            if form_data is not None and method != "GET":
                kwargs["data"] = form_data
        elif json_data is not None and method != "GET":
            kwargs["data"] = body_text
        elif form_data is not None and method != "GET":
            kwargs["data"] = form_data
        response = requester.request(**kwargs)
        response.raise_for_status()
        return response

    def _build_trimemedia_headers(self, runtime: Dict[str, Any], api_path: str, query_text: str, body_text: str, include_content_type: bool = False) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": settings.USER_AGENT,
            "Referer": str(runtime.get("api_host") or runtime.get("base_url") or ""),
        }
        for key, value in (runtime.get("headers") or {}).items():
            if key.lower() not in {"authorization", "authx", "content-type"}:
                headers[str(key)] = str(value)
        token = str(runtime.get("token") or "").strip()
        if token:
            headers["Authorization"] = token
        headers["authx"] = self._build_trimemedia_authx(api_path=api_path, payload_text=body_text if body_text else query_text, apikey=str(runtime.get("apikey") or TRIMEMEDIA_API_KEY))
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def _build_trimemedia_authx(self, api_path: str, payload_text: str, apikey: str) -> str:
        normalized_path = api_path if api_path.startswith("/v") else f"/v{api_path}"
        nonce = str(random.randint(100000, 999999))
        timestamp = str(int(time.time() * 1000))
        body_hash = hashlib.md5((payload_text or "").encode("utf-8")).hexdigest()
        raw = "_".join([TRIMEMEDIA_SIGN_SECRET, normalized_path, nonce, timestamp, body_hash, apikey])
        sign = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return f"nonce={nonce}&timestamp={timestamp}&sign={sign}"

    def _guess_base_url_from_attrs(self, attrs: Dict[str, Any]) -> str:
        for key in ("base_url", "server", "host", "url", "_host", "_server", "_base_url"):
            value = attrs.get(key)
            if isinstance(value, str) and value.startswith("http"):
                base_url, _ = self._resolve_trimemedia_hosts(value)
                return base_url
        for value in attrs.values():
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                base_url, _ = self._resolve_trimemedia_hosts(value)
                return base_url
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
            if key_lower == "cookie" and isinstance(value, str):
                cookies.update(self._parse_cookie_string(value))
                continue
            if "token" in key_lower and isinstance(value, str) and value:
                headers.setdefault("Authorization", value)
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
