# FnMediaCoverGenerator 风格 5（幕光拼贴）实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为 `plugins.v2/fnmediacovergenerator` 新增 `static_5` 幕光拼贴静态封面风格，并完成条目图优先抽图、主图避重复、A2 渲染、配置入口、预览图和回归验证。

**架构：** 先把风格 5 的素材来源、随机抽图、退化模式和排版决策拆成可单测的纯函数模块，再让 `style_static_5.py` 只负责 PIL 渲染。`__init__.py` 只做风格注册、状态持久化和流程接线，避免把新逻辑再次堆进大文件里而不可测。

**技术栈：** Python、Pillow、NumPy、unittest、现有 `fnmediacovergenerator` 工具模块

---

## 文件结构

### 新增文件

- `plugins.v2/fnmediacovergenerator/utils/style5_cover_strategy.py`
  - 负责风格 5 的素材来源选择、随机抽图、退化模式和主图状态更新。
- `plugins.v2/fnmediacovergenerator/utils/style5_layout.py`
  - 负责小眉标文案、文字锚点决策、标题字号缩放等纯排版逻辑。
- `plugins.v2/fnmediacovergenerator/style/style_static_5.py`
  - 负责 `static_5` 的主图增强、辅图带、遮罩、文字绘制和导出。
- `tests/test_style5_cover_strategy.py`
  - 覆盖风格 5 的素材池选择、避开上次主图、退化模式和状态裁剪。
- `tests/test_style5_layout.py`
  - 覆盖小眉标、左右锚点选择和标题字号缩放。
- `tests/test_style_static_5.py`
  - 对 `style_static_5.py` 做渲染烟测，验证 4 图、2 图、1 图三种模式都能输出可解码图像。
- `tests/test_fnmediacovergenerator_style5_contract.py`
  - 验证 `__init__.py` 已接入 `static_5`，且预览资源 `images/style_5.jpeg` 存在。
- `images/style_5.jpeg`
  - 风格 5 的配置页预览图。

### 修改文件

- `plugins.v2/fnmediacovergenerator/__init__.py`
  - 注册 `static_5`、接入新渲染函数、按风格 5 走条目图优先逻辑、保存上次主图 URL、扩展配置页和预览卡。

## 约束与执行顺序

1. 先补纯函数与单测，再碰 `__init__.py`。
2. `style_static_5.py` 不要依赖难以 stub 的运行时对象；能接收 `ResolutionConfig`，但字体加载必须允许空路径回退到默认字体，方便烟测。
3. 风格 5 的来源策略必须是「条目图优先，`image_list` 仅在条目图为空时兜底」，不要再把两者混合。
4. 首版不要复制辅图凑数；有效图不够时，直接减少辅图数量或退化为单主图。

### 任务 1：实现风格 5 素材策略纯函数

**文件：**
- 创建：`plugins.v2/fnmediacovergenerator/utils/style5_cover_strategy.py`
- 测试：`tests/test_style5_cover_strategy.py`

- [ ] **步骤 1：编写失败的测试**

```python
import importlib.util
import random
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_cover_strategy.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style5_cover_strategy",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Style5CoverStrategyTests(unittest.TestCase):
    def test_pick_style5_source_urls_prefers_supplemental_pool(self):
        module = load_module()

        urls, source = module.pick_style5_source_urls(
            base_urls=["https://base-1.jpg", "https://base-2.jpg"],
            supplemental_urls=["https://item-1.jpg", "https://item-2.jpg"],
        )

        self.assertEqual(urls, ["https://item-1.jpg", "https://item-2.jpg"])
        self.assertEqual(source, "supplemental")

    def test_select_style5_image_urls_avoids_last_primary_when_possible(self):
        module = load_module()
        rng = random.Random(7)

        selected, avoided = module.select_style5_image_urls(
            candidate_urls=[
                "https://a.jpg",
                "https://b.jpg",
                "https://c.jpg",
                "https://d.jpg",
            ],
            required_count=4,
            last_primary_url="https://a.jpg",
            rng=rng,
        )

        self.assertEqual(len(selected), 4)
        self.assertNotEqual(selected[0], "https://a.jpg")
        self.assertTrue(avoided)

    def test_resolve_style5_render_mode_degrades_without_duplication(self):
        module = load_module()

        self.assertEqual(
            module.resolve_style5_render_mode(4),
            {"mode": "a2_standard", "primary_count": 1, "echo_count": 3},
        )
        self.assertEqual(
            module.resolve_style5_render_mode(2),
            {"mode": "a2_sparse", "primary_count": 1, "echo_count": 1},
        )
        self.assertEqual(
            module.resolve_style5_render_mode(1),
            {"mode": "a1_fallback", "primary_count": 1, "echo_count": 0},
        )

    def test_remember_style5_primary_keeps_newest_items_only(self):
        module = load_module()

        state = {f"server::{index}": f"https://{index}.jpg" for index in range(205)}
        result = module.remember_style5_primary(
            state=state,
            library_key="server::new",
            primary_url="https://new.jpg",
            limit=200,
        )

        self.assertEqual(len(result), 200)
        self.assertEqual(result["server::new"], "https://new.jpg")
        self.assertNotIn("server::0", result)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_style5_cover_strategy -v`  
预期：FAIL，报错 `style5_cover_strategy.py` 不存在或缺少对应函数。

- [ ] **步骤 3：编写最少实现代码**

```python
from collections import OrderedDict
import random
from typing import Dict, Iterable, List, Optional, Tuple


def _clean_urls(values: Optional[Iterable[str]]) -> List[str]:
    cleaned: List[str] = []
    seen = set()
    for raw in values or []:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        cleaned.append(value)
    return cleaned


def pick_style5_source_urls(
    base_urls: Optional[Iterable[str]],
    supplemental_urls: Optional[Iterable[str]],
) -> Tuple[List[str], str]:
    supplemental = _clean_urls(supplemental_urls)
    if supplemental:
        return supplemental, "supplemental"
    base = _clean_urls(base_urls)
    if base:
        return base, "base"
    return [], "empty"


def select_style5_image_urls(
    candidate_urls: Iterable[str],
    required_count: int,
    last_primary_url: Optional[str] = None,
    rng: Optional[random.Random] = None,
) -> Tuple[List[str], bool]:
    rng = rng or random
    pool = _clean_urls(candidate_urls)
    if not pool:
        return [], False

    primary_candidates = [url for url in pool if url != str(last_primary_url or "").strip()]
    avoided_last_primary = bool(primary_candidates) and bool(last_primary_url)
    primary_pool = primary_candidates or pool
    primary = rng.choice(primary_pool)

    remaining = [url for url in pool if url != primary]
    rng.shuffle(remaining)
    selected = [primary] + remaining[: max(0, required_count - 1)]
    return selected, avoided_last_primary


def resolve_style5_render_mode(image_count: int) -> Dict[str, int | str]:
    if image_count >= 4:
        return {"mode": "a2_standard", "primary_count": 1, "echo_count": 3}
    if image_count == 3:
        return {"mode": "a2_sparse", "primary_count": 1, "echo_count": 2}
    if image_count == 2:
        return {"mode": "a2_sparse", "primary_count": 1, "echo_count": 1}
    if image_count == 1:
        return {"mode": "a1_fallback", "primary_count": 1, "echo_count": 0}
    return {"mode": "empty", "primary_count": 0, "echo_count": 0}


def remember_style5_primary(
    state: Dict[str, str],
    library_key: str,
    primary_url: str,
    limit: int = 200,
) -> Dict[str, str]:
    ordered = OrderedDict((str(k), str(v)) for k, v in (state or {}).items())
    library_key = str(library_key or "").strip()
    primary_url = str(primary_url or "").strip()
    if not library_key or not primary_url:
        return dict(ordered)
    ordered.pop(library_key, None)
    ordered[library_key] = primary_url
    while len(ordered) > max(1, limit):
        ordered.popitem(last=False)
    return dict(ordered)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_style5_cover_strategy -v`  
预期：PASS，输出 `OK`。

- [ ] **步骤 5：Commit**

```bash
git add tests/test_style5_cover_strategy.py plugins.v2/fnmediacovergenerator/utils/style5_cover_strategy.py
git commit -m "feat(飞牛封面): 增加风格5素材策略"
```

### 任务 2：实现风格 5 排版决策纯函数

**文件：**
- 创建：`plugins.v2/fnmediacovergenerator/utils/style5_layout.py`
- 测试：`tests/test_style5_layout.py`

- [ ] **步骤 1：编写失败的测试**

```python
import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_layout.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style5_layout",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Style5LayoutTests(unittest.TestCase):
    def test_resolve_style5_eyebrow_matches_library_name(self):
        module = load_module()

        self.assertEqual(module.resolve_style5_eyebrow("电影"), "Movie Library")
        self.assertEqual(module.resolve_style5_eyebrow("日韩剧"), "Series Collection")
        self.assertEqual(module.resolve_style5_eyebrow("国漫"), "Animation Archive")

    def test_choose_style5_anchor_prefers_darker_and_cleaner_side(self):
        module = load_module()

        anchor = module.choose_style5_anchor(
            left_brightness=0.22,
            left_complexity=0.18,
            right_brightness=0.45,
            right_complexity=0.31,
        )

        self.assertEqual(anchor, "left")

    def test_resolve_style5_title_font_size_respects_lower_bound(self):
        module = load_module()

        self.assertEqual(
            module.resolve_style5_title_font_size(
                base_size=170,
                measured_width=1500,
                max_width=1200,
                min_ratio=0.88,
            ),
            149,
        )
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_style5_layout -v`  
预期：FAIL，报错 `style5_layout.py` 不存在或缺少目标函数。

- [ ] **步骤 3：编写最少实现代码**

```python
import re


def resolve_style5_eyebrow(library_name: str) -> str:
    normalized = re.sub(r"\s+", "", str(library_name or "").strip())
    if "动画" in normalized or "国漫" in normalized or "动漫" in normalized or "番剧" in normalized:
        return "Animation Archive"
    if "剧" in normalized:
        return "Series Collection"
    if "电影" in normalized:
        return "Movie Library"
    return "Featured Collection"


def choose_style5_anchor(
    left_brightness: float,
    left_complexity: float,
    right_brightness: float,
    right_complexity: float,
) -> str:
    left_score = (left_brightness * 0.65) + (left_complexity * 0.35)
    right_score = (right_brightness * 0.65) + (right_complexity * 0.35)
    return "left" if left_score <= right_score else "right"


def resolve_style5_title_font_size(
    base_size: int,
    measured_width: int,
    max_width: int,
    min_ratio: float = 0.88,
) -> int:
    base_size = max(1, int(base_size))
    measured_width = max(1, int(measured_width))
    max_width = max(1, int(max_width))
    if measured_width <= max_width:
        return base_size

    scaled = int(base_size * (max_width / measured_width))
    lower_bound = int(base_size * min_ratio)
    return max(lower_bound, scaled)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_style5_layout -v`  
预期：PASS，输出 `OK`。

- [ ] **步骤 5：Commit**

```bash
git add tests/test_style5_layout.py plugins.v2/fnmediacovergenerator/utils/style5_layout.py
git commit -m "feat(飞牛封面): 增加风格5排版决策"
```

### 任务 3：实现 `style_static_5.py` 并补渲染烟测

**文件：**
- 创建：`plugins.v2/fnmediacovergenerator/style/style_static_5.py`
- 测试：`tests/test_style_static_5.py`

- [ ] **步骤 1：编写失败的烟测**

```python
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

    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style_static_5",
        STYLE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_style_static_5 -v`  
预期：FAIL，报错 `style_static_5.py` 不存在或 `create_style_static_5` 未实现。

- [ ] **步骤 3：编写最少实现代码**

```python
import base64
from io import BytesIO
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from app.log import logger
from app.plugins.fnmediacovergenerator.utils.style5_cover_strategy import resolve_style5_render_mode
from app.plugins.fnmediacovergenerator.utils.style5_layout import (
    choose_style5_anchor,
    resolve_style5_eyebrow,
    resolve_style5_title_font_size,
)


def _load_font(path: str, size: int):
    try:
        if path:
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _collect_images(library_dir: Path) -> list[Path]:
    return [path for path in sorted(library_dir.glob("*.jpg")) if path.is_file()]


def _enhance_primary(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(1.1)
    image = ImageEnhance.Color(image).enhance(1.1)
    return image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))


def _bottom_metrics(image: Image.Image) -> Tuple[float, float, float, float]:
    gray = ImageOps.grayscale(image)
    width, height = gray.size
    box_height = int(height * 0.26)
    left = gray.crop((0, height - box_height, width // 2, height))
    right = gray.crop((width // 2, height - box_height, width, height))
    left_pixels = list(left.getdata())
    right_pixels = list(right.getdata())
    left_brightness = sum(left_pixels) / (255 * len(left_pixels))
    right_brightness = sum(right_pixels) / (255 * len(right_pixels))
    left_complexity = (max(left_pixels) - min(left_pixels)) / 255
    right_complexity = (max(right_pixels) - min(right_pixels)) / 255
    return left_brightness, left_complexity, right_brightness, right_complexity


def create_style_static_5(
    library_dir,
    title,
    font_path,
    font_size=(170, 75),
    font_offset=(0, 40, 40),
    blur_size=50,
    color_ratio=0.8,
    resolution_config=None,
    bg_color_config=None,
):
    canvas_size = (
        getattr(resolution_config, "width", 1920),
        getattr(resolution_config, "height", 1080),
    )
    image_paths = _collect_images(Path(library_dir))
    render_mode = resolve_style5_render_mode(len(image_paths))
    if render_mode["mode"] == "empty":
        raise ValueError("style_5 requires at least one image")

    primary = Image.open(image_paths[0]).convert("RGB")
    primary = _enhance_primary(primary)
    canvas = ImageOps.fit(primary, canvas_size, Image.Resampling.LANCZOS).convert("RGBA")

    mask = Image.new("L", canvas.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle((0, int(canvas.size[1] * 0.62), canvas.size[0], canvas.size[1]), fill=170)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay.putalpha(mask)
    canvas = Image.alpha_composite(canvas, overlay)

    left_b, left_c, right_b, right_c = _bottom_metrics(canvas)
    anchor = choose_style5_anchor(left_b, left_c, right_b, right_c)

    draw = ImageDraw.Draw(canvas)
    zh_size = int(font_size[0])
    max_width = int(canvas.size[0] * 0.52)
    title_font = _load_font(font_path[0], zh_size)
    measured = int(draw.textlength(title[0], font=title_font))
    zh_size = resolve_style5_title_font_size(zh_size, measured, max_width)
    title_font = _load_font(font_path[0], zh_size)
    en_font = _load_font(font_path[1], int(font_size[1]))

    x = 120 if anchor == "left" else canvas.size[0] - max_width - 120
    eyebrow = resolve_style5_eyebrow(title[0])
    draw.text((x, canvas.size[1] - 270), eyebrow, fill=(230, 230, 230, 210), font=en_font)
    draw.text((x, canvas.size[1] - 210), title[0], fill=(255, 255, 255, 255), font=title_font)
    if title[1]:
        draw.text((x, canvas.size[1] - 120), title[1], fill=(230, 230, 230, 220), font=en_font)

    buffer = BytesIO()
    canvas.convert("RGB").save(buffer, format="JPEG", quality=95)
    payload = base64.b64encode(buffer.getvalue()).decode("utf-8")
    logger.info("style_5 rendered in mode=%s", render_mode["mode"])
    return payload
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_style_static_5 -v`  
预期：PASS，输出 `OK`。

- [ ] **步骤 5：Commit**

```bash
git add tests/test_style_static_5.py plugins.v2/fnmediacovergenerator/style/style_static_5.py
git commit -m "feat(飞牛封面): 新增风格5渲染"
```

### 任务 4：接入 `static_5` 到插件流程与配置页

**文件：**
- 修改：`plugins.v2/fnmediacovergenerator/__init__.py`
- 测试：`tests/test_fnmediacovergenerator_style5_contract.py`
- 创建：`images/style_5.jpeg`

- [ ] **步骤 1：编写失败的契约测试**

```python
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_PATH = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "__init__.py"
PREVIEW_PATH = REPO_ROOT / "images" / "style_5.jpeg"


class FnMediaCoverGeneratorStyle5ContractTests(unittest.TestCase):
    def test_init_file_registers_static_5_everywhere(self):
        source = INIT_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "from app.plugins.fnmediacovergenerator.style.style_static_5 import create_style_static_5",
            source,
        )
        self.assertIn('"title": "风格5", "value": "static_5"', source)
        self.assertIn('if self._cover_style == "static_5":', source)
        self.assertIn('range(1, 6)', source)
        self.assertIn('min(5, int(index))', source)
        self.assertIn('style5_last_primary_urls', source)

    def test_style5_preview_exists(self):
        self.assertTrue(PREVIEW_PATH.exists(), PREVIEW_PATH)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_fnmediacovergenerator_style5_contract -v`  
预期：FAIL，提示 `static_5` 相关接线或预览图不存在。

- [ ] **步骤 3：修改插件接线并生成预览图**

```python
# __init__.py 关键改动
from app.plugins.fnmediacovergenerator.style.style_static_5 import create_style_static_5
from app.plugins.fnmediacovergenerator.utils.style5_cover_strategy import (
    pick_style5_source_urls,
    remember_style5_primary,
    resolve_style5_render_mode,
    select_style5_image_urls,
)


def _select_style_index(self, index: int) -> Dict[str, Any]:
    self._cover_style_base = f"static_{max(1, min(5, int(index)))}"
    self._cover_style_variant = "static"
    self._cover_style = self.__compose_cover_style(self._cover_style_base, "static")
    self._update_config()
    return {"success": True, "message": f"已切换到 {self._cover_style}"}


def __compose_cover_style(self, base_style: str, variant: str) -> str:
    base = base_style if base_style in {"static_1", "static_2", "static_3", "static_4", "static_5"} else "static_1"
    return base


def __resolve_cover_style_ui(self, cover_style: str) -> Tuple[str, str]:
    if cover_style in {"static_1", "static_2", "static_3", "static_4", "static_5"}:
        return cover_style, "static"
    return "static_1", "static"


def __get_required_items(self) -> int:
    if self._cover_style == "static_1":
        return 3
    if self._cover_style == "static_3":
        return 9
    if self._cover_style == "static_5":
        return 4
    return 1


def __style_preview_src(index: int) -> str:
    safe_index = max(1, min(5, int(index)))
    return f"https://raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/images/style_{safe_index}.jpeg"
```

```python
# __init__.py 风格 5 需要新增的流程要点
if self._cover_style == "static_5":
    last_primary_map = self.get_data("style5_last_primary_urls") or {}
    library_key = f"{server_name}::{library.get('id')}"
    source_urls, source_name = pick_style5_source_urls(
        base_urls=library.get("image_list") or [],
        supplemental_urls=extra_urls,
    )
    selected_urls, avoided_last_primary = select_style5_image_urls(
        candidate_urls=source_urls,
        required_count=4,
        last_primary_url=last_primary_map.get(library_key),
    )
    logger.info(
        "%s 风格5素材选择 | 服务器=%s | 媒体库=%s | key=%s | 来源=%s | 候选=%s 张 | 实际抽中=%s 张 | 避开上次主图=%s",
        self.plugin_name,
        server_name,
        library_name,
        library_key,
        source_name,
        len(source_urls),
        len(selected_urls),
        "是" if avoided_last_primary else "否",
    )
    last_primary_map = remember_style5_primary(
        state=last_primary_map,
        library_key=library_key,
        primary_url=selected_urls[0] if selected_urls else "",
    )
    self.save_data("style5_last_primary_urls", last_primary_map)
```

```powershell
# 生成 images/style_5.jpeg
@'
import base64
import importlib.util
import sys
import tempfile
import types
from pathlib import Path

from PIL import Image

repo = Path.cwd()
style_path = repo / "plugins.v2" / "fnmediacovergenerator" / "style" / "style_static_5.py"
tmp_dir = Path(tempfile.mkdtemp())

app_module = types.ModuleType("app")
log_module = types.ModuleType("app.log")
log_module.logger = types.SimpleNamespace(
    info=lambda *args, **kwargs: None,
    warning=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
)
sys.modules["app"] = app_module
sys.modules["app.log"] = log_module

spec = importlib.util.spec_from_file_location("style_static_5_preview", style_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

class FakeResolutionConfig:
    width = 1920
    height = 1080

    def get_font_size(self, base_size, scale_factor=1.0):
        return int(base_size * scale_factor)

for index, color in enumerate(((29, 78, 137), (145, 89, 48), (36, 122, 94), (112, 70, 143)), start=1):
    Image.new("RGB", (900, 1350), color).save(tmp_dir / f"{index}.jpg", quality=95)

payload = module.create_style_static_5(
    library_dir=tmp_dir,
    title=("电影", "Films"),
    font_path=("", ""),
    font_size=(170, 72),
    font_offset=(0, 40, 40),
    resolution_config=FakeResolutionConfig(),
    bg_color_config={"mode": "auto", "custom_color": "", "config_color": None},
)

target_dir = repo / "images"
target_dir.mkdir(parents=True, exist_ok=True)
(target_dir / "style_5.jpeg").write_bytes(base64.b64decode(payload))
'@ | python -
```

- [ ] **步骤 4：运行契约测试验证通过**

运行：`python -m unittest tests.test_fnmediacovergenerator_style5_contract -v`  
预期：PASS，输出 `OK`。

- [ ] **步骤 5：Commit**

```bash
git add tests/test_fnmediacovergenerator_style5_contract.py plugins.v2/fnmediacovergenerator/__init__.py images/style_5.jpeg
git commit -m "feat(飞牛封面): 接入风格5入口与预览"
```

### 任务 5：执行回归验证并固定最终状态

**文件：**
- 修改：`plugins.v2/fnmediacovergenerator/__init__.py`
- 修改：`plugins.v2/fnmediacovergenerator/style/style_static_5.py`
- 修改：`plugins.v2/fnmediacovergenerator/utils/style5_cover_strategy.py`
- 修改：`plugins.v2/fnmediacovergenerator/utils/style5_layout.py`
- 修改：`tests/test_style5_cover_strategy.py`
- 修改：`tests/test_style5_layout.py`
- 修改：`tests/test_style_static_5.py`
- 修改：`tests/test_fnmediacovergenerator_style5_contract.py`
- 修改：`images/style_5.jpeg`
- 测试：`tests/test_style5_cover_strategy.py`
- 测试：`tests/test_style5_layout.py`
- 测试：`tests/test_style_static_5.py`
- 测试：`tests/test_fnmediacovergenerator_style5_contract.py`
- 测试：`tests/test_trimemedia_library_images.py`
- 测试：`tests/test_history_selection.py`
- 测试：`tests/test_library_image_debug.py`

- [ ] **步骤 1：运行完整单测集合**

运行：`python -m unittest tests.test_style5_cover_strategy tests.test_style5_layout tests.test_style_static_5 tests.test_fnmediacovergenerator_style5_contract tests.test_trimemedia_library_images tests.test_history_selection tests.test_library_image_debug -v`  
预期：PASS，所有测试输出 `OK`。

- [ ] **步骤 2：手动检查风格 5 的 4 个关键日志**

运行：`rg -n "style5|避开上次主图|来源=|模式=" plugins.v2/fnmediacovergenerator/__init__.py plugins.v2/fnmediacovergenerator/style/style_static_5.py`  
预期：能找到以下 4 类日志：

1. 来源池是 `supplemental` 还是 `base`
2. 是否命中「避开上次主图」
3. 当前模式是 `a2_standard`、`a2_sparse` 或 `a1_fallback`
4. 条目图原始数、去重数、下载有效数

- [ ] **步骤 3：手动 smoke 一次预览资源路径**

运行：`python -c "from pathlib import Path; p = Path('images/style_5.jpeg'); print(p.exists(), p.stat().st_size if p.exists() else 0)"`  
预期：输出 `True` 和大于 `0` 的文件大小。

- [ ] **步骤 4：如回归验证阶段有修正，补最后一个整理 commit**

```bash
git add plugins.v2/fnmediacovergenerator/__init__.py plugins.v2/fnmediacovergenerator/style/style_static_5.py plugins.v2/fnmediacovergenerator/utils/style5_cover_strategy.py plugins.v2/fnmediacovergenerator/utils/style5_layout.py tests/test_style5_cover_strategy.py tests/test_style5_layout.py tests/test_style_static_5.py tests/test_fnmediacovergenerator_style5_contract.py images/style_5.jpeg
git commit -m "test(飞牛封面): 完成风格5回归验证"
```

## 规格覆盖检查

- 规格第 4 节「范围与非目标」由任务 1、任务 3、任务 4 限定；计划中没有把人脸识别、拖拽排版或复制辅图凑数塞进首版。
- 规格第 7 节「数据流设计」由任务 1 和任务 4 覆盖。
- 规格第 8 节「版式与视觉规则」由任务 2 和任务 3 覆盖。
- 规格第 10 节「日志与可观测性」由任务 5 覆盖。
- 规格第 12 节「测试策略」由任务 1、任务 2、任务 3、任务 4、任务 5 的测试步骤共同覆盖。

## 自检结果

1. 本计划没有使用禁止占位符清单中的红旗词。
2. 所有新函数名在任务中前后一致：
   - `pick_style5_source_urls`
   - `select_style5_image_urls`
   - `resolve_style5_render_mode`
   - `remember_style5_primary`
   - `resolve_style5_eyebrow`
   - `choose_style5_anchor`
   - `resolve_style5_title_font_size`
   - `create_style_static_5`
3. 所有测试命令均使用仓库现有的 `python -m unittest` 风格，与当前测试基线一致。
