import importlib.util
import random
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_PATH = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "__init__.py"
STYLE5_STRATEGY_PATH = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "utils" / "style5_cover_strategy.py"
STYLE5_PREVIEW_PATH = REPO_ROOT / "images" / "style_5.jpeg"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _install_stub_modules():
    requests_module = types.ModuleType("requests")
    requests_module.Response = type("Response", (), {})
    requests_module.Session = type("Session", (), {"__init__": lambda self: None})
    requests_module.get = lambda *a, **k: types.SimpleNamespace(raise_for_status=lambda: None, json=lambda: {}, headers={}, content=b"")
    requests_module.request = lambda *a, **k: types.SimpleNamespace(raise_for_status=lambda: None, json=lambda: {}, headers={}, content=b"")
    sys.modules["requests"] = requests_module

    pytz_module = types.ModuleType("pytz")
    pytz_module.timezone = lambda name: None
    sys.modules["pytz"] = pytz_module

    yaml_module = types.ModuleType("yaml")
    yaml_module.safe_load = lambda text: {}
    sys.modules["yaml"] = yaml_module

    app_module = types.ModuleType("app")
    sys.modules["app"] = app_module

    app_core = types.ModuleType("app.core")
    app_core_config = types.ModuleType("app.core.config")
    app_core_config.settings = types.SimpleNamespace(TZ="Asia/Shanghai", USER_AGENT="unittest-agent")
    sys.modules["app.core"] = app_core
    sys.modules["app.core.config"] = app_core_config

    app_helper = types.ModuleType("app.helper")
    app_helper_mediaserver = types.ModuleType("app.helper.mediaserver")
    app_helper_mediaserver.MediaServerHelper = type("MediaServerHelper", (), {})
    sys.modules["app.helper"] = app_helper
    sys.modules["app.helper.mediaserver"] = app_helper_mediaserver

    app_log = types.ModuleType("app.log")
    app_log.logger = types.SimpleNamespace(info=lambda *a, **k: None, warning=lambda *a, **k: None, error=lambda *a, **k: None)
    sys.modules["app.log"] = app_log

    class _PluginBase:
        def __init__(self):
            self._test_data = {}
            self._test_config = {}

        def get_data(self, key):
            return self._test_data.get(key)

        def save_data(self, key, value):
            self._test_data[key] = value

        def update_config(self, payload):
            self._test_config = payload

        def get_data_path(self):
            return Path(tempfile.gettempdir()) / "fnmediacovergenerator-tests"

    app_plugins = types.ModuleType("app.plugins")
    app_plugins._PluginBase = _PluginBase
    sys.modules["app.plugins"] = app_plugins

    app_utils = types.ModuleType("app.utils")
    app_utils_url = types.ModuleType("app.utils.url")
    app_utils_url.UrlUtils = type("UrlUtils", (), {})
    sys.modules["app.utils"] = app_utils
    sys.modules["app.utils.url"] = app_utils_url

    apscheduler = types.ModuleType("apscheduler")
    apscheduler_schedulers = types.ModuleType("apscheduler.schedulers")
    apscheduler_bg = types.ModuleType("apscheduler.schedulers.background")
    apscheduler_bg.BackgroundScheduler = type("BackgroundScheduler", (), {})
    apscheduler_triggers = types.ModuleType("apscheduler.triggers")
    apscheduler_cron = types.ModuleType("apscheduler.triggers.cron")
    apscheduler_cron.CronTrigger = type("CronTrigger", (), {})
    sys.modules["apscheduler"] = apscheduler
    sys.modules["apscheduler.schedulers"] = apscheduler_schedulers
    sys.modules["apscheduler.schedulers.background"] = apscheduler_bg
    sys.modules["apscheduler.triggers"] = apscheduler_triggers
    sys.modules["apscheduler.triggers.cron"] = apscheduler_cron

    app_plugins_root = types.ModuleType("app.plugins.fnmediacovergenerator")
    app_plugins_style = types.ModuleType("app.plugins.fnmediacovergenerator.style")
    app_plugins_utils = types.ModuleType("app.plugins.fnmediacovergenerator.utils")
    sys.modules["app.plugins.fnmediacovergenerator"] = app_plugins_root
    sys.modules["app.plugins.fnmediacovergenerator.style"] = app_plugins_style
    sys.modules["app.plugins.fnmediacovergenerator.utils"] = app_plugins_utils

    for index in range(1, 5):
        module_name = f"app.plugins.fnmediacovergenerator.style.style_static_{index}"
        module = types.ModuleType(module_name)
        setattr(module, f"create_style_static_{index}", lambda *a, **k: f"style{index}")
        sys.modules[module_name] = module

    style5_module = types.ModuleType("app.plugins.fnmediacovergenerator.style.style_static_5")
    style5_module.create_style_static_5 = lambda *a, **k: "style5"
    sys.modules["app.plugins.fnmediacovergenerator.style.style_static_5"] = style5_module

    strategy_module = _load_module(
        "app.plugins.fnmediacovergenerator.utils.style5_cover_strategy",
        STYLE5_STRATEGY_PATH,
    )
    sys.modules["app.plugins.fnmediacovergenerator.utils.style5_cover_strategy"] = strategy_module

    history_selection = types.ModuleType("app.plugins.fnmediacovergenerator.utils.history_selection")
    history_selection.normalize_history_paths = lambda paths: list(paths or [])
    history_selection.resolve_history_delete_targets = lambda paths, root=None: list(paths or [])
    history_selection.retain_history_selection = lambda selected, visible: [item for item in selected if item in set(visible or [])]
    history_selection.toggle_history_selection = lambda selected, path, checked: list(selected or [])
    sys.modules["app.plugins.fnmediacovergenerator.utils.history_selection"] = history_selection

    library_debug = types.ModuleType("app.plugins.fnmediacovergenerator.utils.library_image_debug")
    library_debug.count_non_empty_items = lambda items: len([item for item in (items or []) if str(item or "").strip()])
    library_debug.format_library_image_stats = lambda **kwargs: "stats"
    sys.modules["app.plugins.fnmediacovergenerator.utils.library_image_debug"] = library_debug

    image_manager = types.ModuleType("app.plugins.fnmediacovergenerator.utils.image_manager")

    class ResolutionConfig:
        def __init__(self, value):
            if isinstance(value, tuple):
                self.width, self.height = value
            elif value == "720p":
                self.width, self.height = 1280, 720
            elif value == "480p":
                self.width, self.height = 854, 480
            else:
                self.width, self.height = 1920, 1080

        def get_font_size(self, size, scale_factor=1.0):
            return float(size) * float(scale_factor)

    image_manager.ResolutionConfig = ResolutionConfig
    sys.modules["app.plugins.fnmediacovergenerator.utils.image_manager"] = image_manager

    network_helper = types.ModuleType("app.plugins.fnmediacovergenerator.utils.network_helper")
    network_helper.NetworkHelper = type("NetworkHelper", (), {})
    network_helper.validate_font_file = lambda path: True
    sys.modules["app.plugins.fnmediacovergenerator.utils.network_helper"] = network_helper

    trimemedia_images = types.ModuleType("app.plugins.fnmediacovergenerator.utils.trimemedia_library_images")

    def merge_unique_image_urls(values, limit=None):
        result = []
        seen = set()
        for item in values or []:
            value = str(item or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
            if limit and len(result) >= limit:
                break
        return result

    def prefer_supplemental_image_urls(base_urls, supplemental_urls, limit):
        return merge_unique_image_urls(list(supplemental_urls or []) + list(base_urls or []), limit=limit)

    trimemedia_images.collect_library_item_image_paths = lambda **kwargs: []
    trimemedia_images.merge_unique_image_urls = merge_unique_image_urls
    trimemedia_images.prefer_supplemental_image_urls = prefer_supplemental_image_urls
    sys.modules["app.plugins.fnmediacovergenerator.utils.trimemedia_library_images"] = trimemedia_images


def _load_plugin_module():
    _install_stub_modules()
    return _load_module("fnmediacovergenerator_plugin_under_test", INIT_PATH)


class FnMediaCoverGeneratorStyle5ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_plugin_module()
        cls.PluginClass = cls.module.FnMediaCoverGenerator

    def test_static5_required_count_is_four(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        required = getattr(plugin, "_FnMediaCoverGenerator__get_required_items")()
        self.assertEqual(required, 4)

    def test_generate_image_dispatches_to_style5_factory(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        plugin._resolution_config = self.module.ResolutionConfig("1080p")
        plugin.health_check = lambda: True

        called = {}

        def _fake_create_style_static_5(*args, **kwargs):
            called["args"] = args
            called["kwargs"] = kwargs
            return "style5-payload"

        original = self.module.create_style_static_5
        self.module.create_style_static_5 = _fake_create_style_static_5
        try:
            payload = plugin._generate_image_from_path(
                server_name="server",
                library_name="library",
                library_dir=Path(tempfile.gettempdir()),
                title=("中文", "EN"),
            )
        finally:
            self.module.create_style_static_5 = original

        self.assertEqual(payload, "style5-payload")
        self.assertTrue(called.get("args"))

    def test_mixed_pool_keeps_primary_from_supplemental(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        plugin.get_data = lambda key: {}

        plugin._fetch_trimemedia_library_item_image_urls = lambda **kwargs: [
            "https://supplemental-1.jpg",
            "https://supplemental-2.jpg",
        ]

        original_choice = self.module.random.choice
        self.module.random.choice = lambda values: values[-1]
        try:
            selected = plugin._expand_trimemedia_library_image_urls(
                service=types.SimpleNamespace(name="server"),
                library={
                    "id": "lib1",
                    "name": "library",
                    "server_name": "server",
                    "library_key": "server::lib1",
                    "image_list": [
                        "https://base-1.jpg",
                        "https://base-2.jpg",
                    ],
                },
                runtime={},
                required_items=4,
            )
        finally:
            self.module.random.choice = original_choice

        self.assertGreaterEqual(len(selected), 1)
        self.assertIn(
            selected[0],
            {"https://supplemental-1.jpg", "https://supplemental-2.jpg"},
        )

    def test_expand_does_not_persist_last_primary_before_prepare(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        plugin.get_data = lambda key: {}
        plugin.save_data = lambda key, value: (_ for _ in ()).throw(
            AssertionError("expand stage should not persist style5_last_primary_urls")
        )
        plugin._fetch_trimemedia_library_item_image_urls = lambda **kwargs: [
            "https://supplemental-1.jpg",
        ]

        plugin._expand_trimemedia_library_image_urls(
            service=types.SimpleNamespace(name="server"),
            library={
                "id": "lib1",
                "name": "library",
                "server_name": "server",
                "library_key": "server::lib1",
                "image_list": ["https://base-1.jpg"],
            },
            runtime={},
            required_items=4,
        )

    def test_style5_last_primary_uses_prepare_confirmed_primary(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        plugin._auto_upload = False

        plugin._extract_trimemedia_runtime = lambda *args, **kwargs: {}
        plugin._library_cache_dir = lambda *args, **kwargs: Path(tempfile.gettempdir())
        plugin._expand_trimemedia_library_image_urls = lambda *args, **kwargs: [
            "https://candidate-primary.jpg",
            "https://candidate-2.jpg",
        ]
        plugin._prepare_library_images_from_urls = lambda **kwargs: (
            True,
            "ok",
            "https://actual-primary.jpg",
        )
        plugin._generate_image_from_path = lambda **kwargs: "base64-payload"
        plugin._save_generated_cover = lambda **kwargs: (Path(tempfile.gettempdir()) / "cover.jpg", ".jpg")
        plugin._saved_cover_to_src = lambda path: "src"
        setattr(
            plugin,
            "_FnMediaCoverGenerator__get_title_from_config",
            lambda library_name: ("主标题", "SUBTITLE", None),
        )

        result = plugin._process_library(
            service=types.SimpleNamespace(name="server"),
            library={
                "id": "lib1",
                "name": "library",
                "server_name": "server",
                "library_key": "server::lib1",
                "image_list": [],
            },
        )

        self.assertTrue(result["success"])
        state = plugin.get_data("style5_last_primary_urls")
        self.assertIsInstance(state, dict)
        self.assertEqual(state.get("server::lib1"), "https://actual-primary.jpg")

    def test_prepare_ignores_failed_first_write_for_actual_primary(self):
        plugin = self.PluginClass()
        plugin._cover_style = "static_5"
        plugin._stop_event = types.SimpleNamespace(is_set=lambda: False)
        plugin._is_trimemedia_runtime_ready = lambda runtime: False
        plugin._is_trimemedia_request = lambda url, runtime: False
        plugin.prepare_library_images = lambda library_dir, required_items=9: True

        responses = {
            "https://img-1.jpg": b"image-bytes-1",
            "https://img-2.jpg": b"image-bytes-2",
        }

        def _fake_get(url, timeout=20, headers=None):
            content = responses[url]
            return types.SimpleNamespace(
                raise_for_status=lambda: None,
                headers={"content-type": "image/jpeg"},
                content=content,
                json=lambda: {},
            )

        original_get = self.module.requests.get
        self.module.requests.get = _fake_get
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                library_dir = Path(temp_dir) / "library"
                original_write_bytes = Path.write_bytes
                state = {"calls": 0}

                def _patched_write_bytes(self, data):
                    state["calls"] += 1
                    if self.name == "1.jpg" and state["calls"] == 1:
                        raise OSError("disk full")
                    return original_write_bytes(self, data)

                with mock.patch.object(Path, "write_bytes", _patched_write_bytes):
                    ok, message, actual_primary_url = plugin._prepare_library_images_from_urls(
                        library_dir=library_dir,
                        image_urls=["https://img-1.jpg", "https://img-2.jpg"],
                        required_items=4,
                        runtime={},
                        server_name="server",
                        library_name="library",
                        library_id="lib1",
                    )
        finally:
            self.module.requests.get = original_get

        self.assertTrue(ok)
        self.assertIn("已准备 1 张", message)
        self.assertEqual(actual_primary_url, "https://img-2.jpg")

    def test_style5_preview_image_exists(self):
        self.assertTrue(STYLE5_PREVIEW_PATH.exists())

    def test_style5_preview_prefers_local_data_uri_when_image_exists(self):
        preview_src = getattr(
            self.PluginClass,
            "_FnMediaCoverGenerator__style_preview_src",
        )(5)
        self.assertTrue(preview_src.startswith("data:image/"))
        self.assertNotIn("raw.githubusercontent.com", preview_src)

    def test_fetch_library_item_images_supports_instance_api_and_resolves_relative_url(self):
        plugin = self.PluginClass()

        class _Api:
            host = "https://trimemedia.example.com/v"

            @staticmethod
            def item_list(guid, page, page_size):
                if guid != "library-guid" or page != 1:
                    return []
                return [{"guid": "movie-1", "type": "Movie"}]

            @staticmethod
            def item(guid):
                if guid != "movie-1":
                    return None
                return {"guid": "movie-1", "poster": "/images/poster-1.jpg"}

        service = types.SimpleNamespace(
            instance=types.SimpleNamespace(api=_Api()),
        )

        def _fake_collect_library_item_image_paths(
            library_guid,
            fetch_children,
            fetch_details,
            limit,
        ):
            self.assertEqual(library_guid, "library-guid")
            self.assertEqual(limit, 4)
            children = list(fetch_children("library-guid"))
            self.assertEqual(len(children), 1)
            detail = fetch_details("movie-1")
            self.assertEqual(detail.get("poster"), "/images/poster-1.jpg")
            return [detail.get("poster")]

        original_collect = self.module.collect_library_item_image_paths
        self.module.collect_library_item_image_paths = _fake_collect_library_item_image_paths
        try:
            urls = plugin._fetch_trimemedia_library_item_image_urls(
                service=service,
                library_id="library-guid",
                runtime={},
                target_count=4,
            )
        finally:
            self.module.collect_library_item_image_paths = original_collect

        self.assertEqual(
            urls,
            ["https://trimemedia.example.com/v/images/poster-1.jpg"],
        )


if __name__ == "__main__":
    unittest.main()
