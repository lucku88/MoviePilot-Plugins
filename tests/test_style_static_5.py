import base64
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "style"
    / "style_static_5.py"
)
STRATEGY_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_cover_strategy.py"
)
LAYOUT_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_layout.py"
)


def _register_package(name: str):
    module = sys.modules.get(name)
    if module is not None:
        return module
    module = types.ModuleType(name)
    module.__path__ = []
    sys.modules[name] = module
    return module


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader is not None
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


def load_module():
    app_module = types.ModuleType("app")
    log_module = types.ModuleType("app.log")
    log_module.logger = types.SimpleNamespace(
        info=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
    )
    sys.modules["app"] = app_module
    sys.modules["app.log"] = log_module

    _register_package("app.plugins")
    _register_package("app.plugins.fnmediacovergenerator")
    _register_package("app.plugins.fnmediacovergenerator.utils")

    _load_module(
        "app.plugins.fnmediacovergenerator.utils.style5_cover_strategy",
        STRATEGY_PATH,
    )
    _load_module(
        "app.plugins.fnmediacovergenerator.utils.style5_layout",
        LAYOUT_PATH,
    )

    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style_static_5",
        STYLE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResolutionConfig:
    width = 1920
    height = 1080

    def get_font_size(self, base_size, scale_factor=1.0):
        return int(base_size * scale_factor)


class StyleStatic5Tests(unittest.TestCase):
    def _make_library_dir(self, image_count: int) -> Path:
        root = Path(tempfile.mkdtemp())
        colors = [(29, 78, 137), (145, 89, 48), (36, 122, 94), (112, 70, 143)]
        for index in range(image_count):
            image = Image.new("RGB", (900, 1350), colors[index])
            image.save(root / f"{index + 1}.jpg", quality=95)
        return root

    def test_create_style_static_5_renders_standard_sparse_and_fallback(self):
        module = load_module()

        for count in (4, 2, 1):
            library_dir = self._make_library_dir(count)
            result = module.create_style_static_5(
                library_dir=library_dir,
                title=("日韩剧", "Japan & Korea Drama"),
                font_path=("", ""),
                font_size=(170, 72),
                font_offset=(0, 40, 40),
                resolution_config=FakeResolutionConfig(),
                bg_color_config={"mode": "auto", "custom_color": "", "config_color": None},
            )

            payload = base64.b64decode(result)
            self.assertGreater(len(payload), 1000)


if __name__ == "__main__":
    unittest.main()
