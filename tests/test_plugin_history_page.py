import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "__init__.py"
)
HISTORY_SELECTION_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "history_selection.py"
)
LIBRARY_IMAGE_DEBUG_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "library_image_debug.py"
)
STYLE_CONFIG_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style_config.py"
)
TRIMEMEDIA_IMAGES_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "trimemedia_library_images.py"
)


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _install_plugin_stubs(temp_dir: Path):
    app_module = types.ModuleType("app")
    sys.modules["app"] = app_module

    requests_module = types.ModuleType("requests")
    requests_module.Session = type("Session", (), {})
    requests_module.Response = type("Response", (), {})
    sys.modules["requests"] = requests_module

    pytz_module = types.ModuleType("pytz")
    pytz_module.timezone = lambda value: value
    sys.modules["pytz"] = pytz_module

    yaml_module = types.ModuleType("yaml")
    yaml_module.safe_load = lambda value: {}
    sys.modules["yaml"] = yaml_module

    apscheduler_module = types.ModuleType("apscheduler")
    sys.modules["apscheduler"] = apscheduler_module
    schedulers_module = types.ModuleType("apscheduler.schedulers")
    sys.modules["apscheduler.schedulers"] = schedulers_module
    background_module = types.ModuleType("apscheduler.schedulers.background")

    class BackgroundScheduler:
        def __init__(self, *args, **kwargs):
            self.running = False

        def remove_all_jobs(self):
            return None

        def shutdown(self):
            return None

        def add_job(self, *args, **kwargs):
            return None

        def get_jobs(self):
            return []

        def start(self):
            self.running = True

        def print_jobs(self):
            return None

    background_module.BackgroundScheduler = BackgroundScheduler
    sys.modules["apscheduler.schedulers.background"] = background_module

    triggers_module = types.ModuleType("apscheduler.triggers")
    sys.modules["apscheduler.triggers"] = triggers_module
    cron_module = types.ModuleType("apscheduler.triggers.cron")

    class CronTrigger:
        @staticmethod
        def from_crontab(value):
            return value

    cron_module.CronTrigger = CronTrigger
    sys.modules["apscheduler.triggers.cron"] = cron_module

    core_module = types.ModuleType("app.core")
    sys.modules["app.core"] = core_module
    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(TZ="Asia/Shanghai", GITHUB_PROXY="")
    sys.modules["app.core.config"] = config_module

    helper_module = types.ModuleType("app.helper")
    sys.modules["app.helper"] = helper_module
    mediaserver_module = types.ModuleType("app.helper.mediaserver")

    class MediaServerHelper:
        def get_services(self, *args, **kwargs):
            return {}

    mediaserver_module.MediaServerHelper = MediaServerHelper
    sys.modules["app.helper.mediaserver"] = mediaserver_module

    log_module = types.ModuleType("app.log")

    class _Logger:
        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

        def exception(self, *args, **kwargs):
            return None

    log_module.logger = _Logger()
    sys.modules["app.log"] = log_module

    plugins_module = types.ModuleType("app.plugins")

    class _PluginBase:
        def __init__(self):
            self._data_store = {}
            self._config_store = {}

        def get_data_path(self):
            return temp_dir

        def update_config(self, config):
            self._config_store = dict(config)

        def get_data(self, key):
            return self._data_store.get(key)

        def save_data(self, key, value):
            self._data_store[key] = value

    plugins_module._PluginBase = _PluginBase
    sys.modules["app.plugins"] = plugins_module

    url_module = types.ModuleType("app.utils.url")

    class UrlUtils:
        @staticmethod
        def standardize_base_url(value):
            return value

    url_module.UrlUtils = UrlUtils
    sys.modules["app.utils.url"] = url_module
    sys.modules["app.utils"] = types.ModuleType("app.utils")

    fn_plugin_module = types.ModuleType("app.plugins.fnmediacovergenerator")
    sys.modules["app.plugins.fnmediacovergenerator"] = fn_plugin_module
    style_pkg = types.ModuleType("app.plugins.fnmediacovergenerator.style")
    sys.modules["app.plugins.fnmediacovergenerator.style"] = style_pkg
    utils_pkg = types.ModuleType("app.plugins.fnmediacovergenerator.utils")
    sys.modules["app.plugins.fnmediacovergenerator.utils"] = utils_pkg

    for style_name, export_name in [
        ("style_static_1", "create_style_static_1"),
        ("style_static_2", "create_style_static_2"),
        ("style_static_3", "create_style_static_3"),
        ("style_static_4", "create_style_static_4"),
    ]:
        module_name = f"app.plugins.fnmediacovergenerator.style.{style_name}"
        style_module = types.ModuleType(module_name)
        setattr(style_module, export_name, lambda *args, **kwargs: "")
        sys.modules[module_name] = style_module

    image_manager_module = types.ModuleType("app.plugins.fnmediacovergenerator.utils.image_manager")

    class ResolutionConfig:
        def __init__(self, value):
            self.width = 1920
            self.height = 1080

        def get_font_size(self, value):
            return value

    image_manager_module.ResolutionConfig = ResolutionConfig
    sys.modules["app.plugins.fnmediacovergenerator.utils.image_manager"] = image_manager_module

    network_helper_module = types.ModuleType("app.plugins.fnmediacovergenerator.utils.network_helper")

    class NetworkHelper:
        def __init__(self, *args, **kwargs):
            return None

        def download_file_sync(self, *args, **kwargs):
            return False

    network_helper_module.NetworkHelper = NetworkHelper
    network_helper_module.validate_font_file = lambda path: True
    sys.modules["app.plugins.fnmediacovergenerator.utils.network_helper"] = network_helper_module

    _load_module(
        "app.plugins.fnmediacovergenerator.utils.history_selection",
        HISTORY_SELECTION_PATH,
    )
    _load_module(
        "app.plugins.fnmediacovergenerator.utils.library_image_debug",
        LIBRARY_IMAGE_DEBUG_PATH,
    )
    _load_module(
        "app.plugins.fnmediacovergenerator.utils.style_config",
        STYLE_CONFIG_PATH,
    )
    _load_module(
        "app.plugins.fnmediacovergenerator.utils.trimemedia_library_images",
        TRIMEMEDIA_IMAGES_PATH,
    )


def load_plugin_module(temp_dir: Path):
    _install_plugin_stubs(temp_dir)
    return _load_module("fnmediacovergenerator_plugin", PLUGIN_MODULE_PATH)


def walk_components(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk_components(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk_components(item)


class PluginHistoryPageTests(unittest.TestCase):
    def test_library_item_images_are_preferred_over_media_library_image_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module = load_plugin_module(Path(temp_dir))
            plugin = module.FnMediaCoverGenerator()
            plugin.plugin_name = "飞牛影视媒体库封面生成"
            plugin._fetch_trimemedia_library_item_image_urls = lambda **kwargs: [
                f"https://item/{index}.jpg" for index in range(11)
            ]

            urls = plugin._expand_trimemedia_library_image_urls(
                service=types.SimpleNamespace(name="飞牛影视"),
                library={
                    "server_name": "飞牛影视",
                    "name": "日韩剧",
                    "id": "library-id",
                    "image_list": [f"https://library/{index}.jpg" for index in range(4)],
                },
                runtime={},
                required_items=9,
            )

            self.assertEqual(len(urls), 11)
            self.assertTrue(all(url.startswith("https://item/") for url in urls))

    def test_history_page_uses_uncropped_preview_and_exposes_original_image_link(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            module = load_plugin_module(temp_path)
            plugin = module.FnMediaCoverGenerator()
            plugin._page_tab = "history-tab"
            plugin._covers_output = temp_path / "output"
            plugin._covers_output.mkdir(parents=True, exist_ok=True)
            plugin._covers_page_history_limit = 10
            plugin._selected_servers = []
            plugin._all_libraries = []

            Image.new("RGB", (1920, 1080), (120, 80, 60)).save(
                plugin._covers_output / "demo.png"
            )

            page = plugin.get_page()
            image_components = [
                component
                for component in walk_components(page)
                if component.get("component") == "VImg"
            ]
            self.assertTrue(image_components, "历史页应渲染封面预览图")

            history_image = image_components[0]
            self.assertNotEqual(
                history_image.get("props", {}).get("cover"),
                True,
                "历史页缩略图不应继续使用裁切式 cover 预览",
            )
            self.assertEqual(
                history_image.get("props", {}).get("contain"),
                True,
                "历史页缩略图应完整展示原图",
            )

            original_links = [
                component
                for component in walk_components(page)
                if component.get("component") == "VBtn"
                and component.get("text") == "查看原图"
            ]
            self.assertTrue(original_links, "历史页应提供查看原图入口")
            self.assertTrue(
                original_links[0].get("props", {}).get("href", "").startswith("data:image/"),
                "查看原图按钮应直接指向原始图片数据",
            )


if __name__ == "__main__":
    unittest.main()
