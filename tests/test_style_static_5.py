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
        return Image.open(BytesIO(raw)).convert("RGB")

    def _echo_boxes(self, size):
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

    def _region_diff_score(self, image_a: Image.Image, image_b: Image.Image, box) -> float:
        diff = ImageChops.difference(image_a.crop(box), image_b.crop(box))
        stat = ImageStat.Stat(diff)
        return float(sum(stat.mean))

    def test_create_style_static_5_renders_standard_sparse_and_fallback(self):
        module = load_module()
        payloads = {}
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
            payloads[count] = payload
            decoded_images[count] = self._decode_image(result)
            digests[count] = hashlib.sha256(decoded_images[count].tobytes()).hexdigest()

        self.assertNotEqual(digests[4], digests[1])
        self.assertNotEqual(digests[2], digests[1])
        self.assertNotEqual(digests[4], digests[2])

        echo_1, echo_2, echo_3 = self._echo_boxes(decoded_images[1].size)

        # 2 张图需要真实渲染 1 张 echo，且 fallback 不应有 echo。
        self.assertGreater(self._region_diff_score(decoded_images[2], decoded_images[1], echo_1), 20.0)
        self.assertLess(self._region_diff_score(decoded_images[2], decoded_images[1], echo_2), 5.0)
        self.assertLess(self._region_diff_score(decoded_images[2], decoded_images[1], echo_3), 5.0)

        # 4 张图需要渲染 3 张 echo。
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], echo_1), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], echo_2), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[1], echo_3), 20.0)

        # 4 张图比 2 张图至少应在第 2、3 个 echo 位点有布局差异。
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[2], echo_2), 20.0)
        self.assertGreater(self._region_diff_score(decoded_images[4], decoded_images[2], echo_3), 20.0)


if __name__ == "__main__":
    unittest.main()
