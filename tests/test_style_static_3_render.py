import base64
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "style"
    / "style_static_3.py"
)
COLOR_HELPER_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "color_helper.py"
)


def _install_app_stubs():
    app_module = types.ModuleType("app")
    log_module = types.ModuleType("app.log")

    class _Logger:
        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

    log_module.logger = _Logger()
    sys.modules["app"] = app_module
    sys.modules["app.log"] = log_module
    sys.modules["app.plugins"] = types.ModuleType("app.plugins")
    sys.modules["app.plugins.fnmediacovergenerator"] = types.ModuleType(
        "app.plugins.fnmediacovergenerator"
    )
    sys.modules["app.plugins.fnmediacovergenerator.style"] = types.ModuleType(
        "app.plugins.fnmediacovergenerator.style"
    )
    sys.modules["app.plugins.fnmediacovergenerator.utils"] = types.ModuleType(
        "app.plugins.fnmediacovergenerator.utils"
    )


def load_style_module():
    _install_app_stubs()

    helper_spec = importlib.util.spec_from_file_location(
        "app.plugins.fnmediacovergenerator.utils.color_helper",
        COLOR_HELPER_PATH,
    )
    helper_module = importlib.util.module_from_spec(helper_spec)
    assert helper_spec.loader is not None
    sys.modules[helper_spec.name] = helper_module
    helper_spec.loader.exec_module(helper_module)

    style_spec = importlib.util.spec_from_file_location(
        "app.plugins.fnmediacovergenerator.style.style_static_3",
        STYLE_MODULE_PATH,
    )
    style_module = importlib.util.module_from_spec(style_spec)
    assert style_spec.loader is not None
    sys.modules[style_spec.name] = style_module
    style_spec.loader.exec_module(style_module)
    return style_module


def find_font_path():
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise unittest.SkipTest("未找到可用于样式渲染测试的字体文件")


class StyleStatic3RenderTests(unittest.TestCase):
    def test_style_static_3_keeps_titles_visible_with_legacy_large_offsets(self):
        module = load_style_module()
        font_path = find_font_path()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for index in range(1, 10):
                color = (90 + index * 10, 120 + index * 8, 160 + index * 6)
                Image.new("RGB", (800, 1200), color).save(temp_path / f"{index}.jpg")

            result = module.create_style_static_3(
                temp_path,
                ("LIBRARY", "SUBTITLE"),
                (font_path, font_path),
                font_size=(170, 75),
                font_offset=(120, 500, 40),
                is_blur=True,
            )

            self.assertIsInstance(result, str)
            image = Image.open(io.BytesIO(base64.b64decode(result))).convert("RGB")
            left_half = np.array(image.crop((0, 0, image.width // 2, image.height)))
            bright_pixels = int(
                ((left_half[:, :, 0] > 230) & (left_half[:, :, 1] > 230) & (left_half[:, :, 2] > 230)).sum()
            )

            self.assertGreater(
                bright_pixels,
                1000,
                "legacy 大偏移下标题文字不应整体消失",
            )

    def test_style_static_3_places_title_block_inside_safe_left_margin(self):
        module = load_style_module()
        font_path = find_font_path()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for index in range(1, 10):
                color = (90 + index * 10, 120 + index * 8, 160 + index * 6)
                Image.new("RGB", (800, 1200), color).save(temp_path / f"{index}.jpg")

            result = module.create_style_static_3(
                temp_path,
                ("LIBRARY", "Japan & Korea Drama"),
                (font_path, font_path),
                font_size=(170, 75),
                font_offset=(0, 40, 40),
                is_blur=True,
            )

            self.assertIsInstance(result, str)
            image = Image.open(io.BytesIO(base64.b64decode(result))).convert("RGB")
            image_array = np.array(image)
            bright_mask = (
                (image_array[:, :, 0] > 230)
                & (image_array[:, :, 1] > 230)
                & (image_array[:, :, 2] > 230)
            )
            _, bright_x = np.where(bright_mask)

            self.assertGreater(len(bright_x), 1000)
            self.assertGreaterEqual(
                int(bright_x.min()),
                150,
                "风格3标题块应整体右移到飞牛展示安全区内",
            )


if __name__ == "__main__":
    unittest.main()
