import base64
import importlib.util
import io
from unittest import mock
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
TEXT_RENDERING_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "style"
    / "text_rendering.py"
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

    text_spec = importlib.util.spec_from_file_location(
        "app.plugins.fnmediacovergenerator.style.text_rendering",
        TEXT_RENDERING_PATH,
    )
    text_module = importlib.util.module_from_spec(text_spec)
    assert text_spec.loader is not None
    sys.modules[text_spec.name] = text_module
    text_spec.loader.exec_module(text_module)

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


def find_font_pair_without_and_with_cjk():
    latin_candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    cjk_candidates = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
    ]
    latin_font = next((str(path) for path in latin_candidates if path.exists()), "")
    cjk_font = next((str(path) for path in cjk_candidates if path.exists()), "")
    if not latin_font or not cjk_font:
        raise unittest.SkipTest("未找到可用于字体回退验证的中英文字体组合")
    return latin_font, cjk_font


class StyleStatic3RenderTests(unittest.TestCase):
    def test_font_support_probe_uses_bbox_when_mask_bbox_is_empty(self):
        module = load_style_module()

        class EmptyMask:
            def getbbox(self):
                return None

        class BBoxOnlyFont:
            def getbbox(self, text):
                return (0, 0, 120, 36)

            def getmask(self, text, mode=""):
                return EmptyMask()

        self.assertTrue(
            module._font_supports_text(BBoxOnlyFont(), "GUOMAN"),
            "容器内 getmask 可能误报空字形，应允许 getbbox 成功的字体继续渲染",
        )

    def test_font_loader_falls_back_when_primary_font_cannot_render_cjk(self):
        module = load_style_module()
        _, cjk_font = find_font_pair_without_and_with_cjk()

        original_fallbacks = list(module.ZH_FONT_FALLBACKS)
        module.ZH_FONT_FALLBACKS = [cjk_font]
        try:
            font, used_path = module._load_font_with_fallback(
                "Z:/non-existent-font.ttf",
                "影视",
                36,
            )
        finally:
            module.ZH_FONT_FALLBACKS = original_fallbacks

        self.assertTrue(module._font_supports_text(font, "影视"))
        self.assertEqual(
            used_path,
            cjk_font,
            "首选字体不支持中文时应回退到可渲染的中文字体",
        )

    def test_draw_text_on_image_still_renders_when_pil_text_draw_is_noop(self):
        module = load_style_module()
        font_path = find_font_path()
        image = Image.new("RGBA", (420, 180), (20, 20, 20, 255))

        with mock.patch("PIL.ImageDraw.ImageDraw.text", autospec=True, side_effect=lambda *args, **kwargs: None):
            rendered = module.draw_text_on_image(
                image,
                "国产剧",
                (30, 40),
                font_path,
                "unused.ttf",
                72,
                fill_color=(255, 255, 255, 255),
                shadow=False,
            )

        pixels = np.array(rendered.convert("RGB"))
        bright_pixels = int(
            ((pixels[:, :, 0] > 220) & (pixels[:, :, 1] > 220) & (pixels[:, :, 2] > 220)).sum()
        )
        self.assertGreater(
            bright_pixels,
            500,
            "即使 Pillow 的 draw.text 未实际落字，也应通过兜底路径渲染出标题像素",
        )

    @staticmethod
    def _render_style_static_3(module, font_path, resolution_config=None):
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
                resolution_config=resolution_config,
            )

            return Image.open(io.BytesIO(base64.b64decode(result))).convert("RGB")

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
                300,
                "legacy 大偏移下标题文字不应整体消失",
            )

    def test_style_static_3_places_title_block_inside_safe_left_margin_for_1080p(self):
        module = load_style_module()
        font_path = find_font_path()
        image = self._render_style_static_3(module, font_path)
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
            "1080p 下风格3标题块应整体右移到飞牛展示安全区内",
        )

    def test_style_static_3_places_title_block_inside_safe_left_margin_for_480p(self):
        module = load_style_module()
        font_path = find_font_path()

        class ResolutionConfig:
            width = 853
            height = 480

        image = self._render_style_static_3(module, font_path, resolution_config=ResolutionConfig())
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
            140,
            "480p 下风格3标题块不应因缩放再次贴回最左侧",
        )


if __name__ == "__main__":
    unittest.main()
