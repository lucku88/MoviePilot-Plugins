import base64
import hashlib
import importlib.util
from io import BytesIO
import sys
import tempfile
import types
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


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


class Fake720ResolutionConfig:
    width = 1280
    height = 720

    def get_font_size(self, base_size, scale_factor=1.0):
        ratio = self.height / 1080
        return int(base_size * ratio * scale_factor)


class StyleStatic5Tests(unittest.TestCase):
    def _make_library_dir(self, image_count: int) -> Path:
        root = Path(tempfile.mkdtemp())
        colors = [(29, 78, 137), (145, 89, 48), (36, 122, 94), (112, 70, 143)]
        for index in range(image_count):
            image = Image.new("RGB", (900, 1350), colors[index])
            image.save(root / f"{index + 1}.jpg", quality=95)
        return root

    def _decode_image(self, payload: str) -> Image.Image:
        raw = base64.b64decode(payload)
        with Image.open(BytesIO(raw)) as image:
            return image.convert("RGB").copy()

    def _standard_echo_boxes(self, size):
        width, height = size
        tile_w = max(160, int(width * 0.13))
        tile_h = max(220, int(height * 0.19))
        gap = max(20, int(width * 0.012))
        top_margin = max(48, int(height * 0.06))
        right_margin = max(40, int(width * 0.03))
        step_y = max(8, int(height * 0.01))
        inset = max(6, int(min(tile_w, tile_h) * 0.1))

        boxes = []
        for index in range(3):
            x = width - right_margin - tile_w - index * (tile_w + gap)
            y = top_margin + index * step_y
            boxes.append((x + inset, y + inset, x + tile_w - inset, y + tile_h - inset))
        return boxes

    def _sparse_echo_boxes(self, size):
        width, height = size
        tile_w = max(260, int(width * 0.2))
        tile_h = max(340, int(height * 0.32))
        gap = max(20, int(width * 0.012))
        right_margin = max(44, int(width * 0.03))
        bottom_margin = max(44, int(height * 0.04))
        inset = max(10, int(min(tile_w, tile_h) * 0.1))

        first_x = width - right_margin - tile_w
        first_y = height - bottom_margin - tile_h
        second_x = first_x - tile_w + int(tile_w * 0.22) - gap
        second_y = first_y - int(tile_h * 0.08)
        return [
            (first_x + inset, first_y + inset, first_x + tile_w - inset, first_y + tile_h - inset),
            (second_x + inset, second_y + inset, second_x + tile_w - inset, second_y + tile_h - inset),
        ]

    def _region_diff_score(self, image_a: Image.Image, image_b: Image.Image, box) -> float:
        diff = ImageChops.difference(image_a.crop(box), image_b.crop(box))
        stat = ImageStat.Stat(diff)
        return float(sum(stat.mean))

    def test_create_style_static_5_renders_standard_sparse_and_fallback(self):
        module = load_module()
        decoded_images = {}
        digests = {}

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
            decoded_images[count] = self._decode_image(result)
            digests[count] = hashlib.sha256(decoded_images[count].tobytes()).hexdigest()

        self.assertNotEqual(digests[4], digests[1])
        self.assertNotEqual(digests[2], digests[1])
        self.assertNotEqual(digests[4], digests[2])

        std_1, std_2, std_3 = self._standard_echo_boxes(decoded_images[1].size)
        sparse_1, sparse_2 = self._sparse_echo_boxes(decoded_images[1].size)

        # a2_standard：右上三连区域应明显变化，右下大卡区域应基本不受影响。
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], std_1), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], std_2), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], std_3), 20.0)
        self.assertLess(self._region_diff_score(decoded_images[4], decoded_images[1], sparse_1), 8.0)
        self.assertLess(self._region_diff_score(decoded_images[4], decoded_images[1], sparse_2), 8.0)

        # a2_sparse：右下大卡区域应明显变化，右上三连区域应基本不受影响。
        self.assertGreater(self._region_diff_score(decoded_images[2], decoded_images[1], sparse_1), 20.0)
        self.assertLess(self._region_diff_score(decoded_images[2], decoded_images[1], std_1), 8.0)
        self.assertLess(self._region_diff_score(decoded_images[2], decoded_images[1], std_2), 8.0)
        self.assertLess(self._region_diff_score(decoded_images[2], decoded_images[1], std_3), 8.0)

        # standard vs sparse：两套布局核心区域都应体现明显差异。
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[2], std_2), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[2], sparse_1), 20.0)

    def test_create_style_static_5_consumes_params_and_scales_with_resolution(self):
        module = load_module()
        library_dir = self._make_library_dir(1)

        base_result = module.create_style_static_5(
            library_dir=library_dir,
            title=("日韩剧", "Japan & Korea Drama"),
            font_path=("", ""),
            font_size=(170, 72),
            font_offset=(0, 40, 40),
            blur_size=0,
            color_ratio=0,
            resolution_config=FakeResolutionConfig(),
            bg_color_config={"mode": "custom", "custom_color": "#111111", "config_color": None},
        )
        shifted_result = module.create_style_static_5(
            library_dir=library_dir,
            title=("日韩剧", "Japan & Korea Drama"),
            font_path=("", ""),
            font_size=(170, 72),
            font_offset=(140, 40, 40),
            blur_size=0,
            color_ratio=0,
            resolution_config=FakeResolutionConfig(),
            bg_color_config={"mode": "custom", "custom_color": "#111111", "config_color": None},
        )
        self.assertNotEqual(base_result, shifted_result)

        red_tint_result = module.create_style_static_5(
            library_dir=library_dir,
            title=("日韩剧", "Japan & Korea Drama"),
            font_path=("", ""),
            font_size=(170, 72),
            font_offset=(0, 40, 40),
            blur_size=80,
            color_ratio=1.0,
            resolution_config=FakeResolutionConfig(),
            bg_color_config={"mode": "custom", "custom_color": "#d94646", "config_color": None},
        )
        blue_tint_result = module.create_style_static_5(
            library_dir=library_dir,
            title=("日韩剧", "Japan & Korea Drama"),
            font_path=("", ""),
            font_size=(170, 72),
            font_offset=(0, 40, 40),
            blur_size=80,
            color_ratio=1.0,
            resolution_config=FakeResolutionConfig(),
            bg_color_config={"mode": "custom", "custom_color": "#2563eb", "config_color": None},
        )
        self.assertNotEqual(red_tint_result, blue_tint_result)

        resized_result = module.create_style_static_5(
            library_dir=library_dir,
            title=("日韩剧", "Japan & Korea Drama"),
            font_path=("", ""),
            font_size=(170, 72),
            font_offset=(0, 40, 40),
            blur_size=50,
            color_ratio=0.8,
            resolution_config=Fake720ResolutionConfig(),
            bg_color_config={"mode": "auto", "custom_color": "", "config_color": None},
        )
        resized_image = self._decode_image(resized_result)
        self.assertEqual(resized_image.size, (1280, 720))


if __name__ == "__main__":
    unittest.main()
