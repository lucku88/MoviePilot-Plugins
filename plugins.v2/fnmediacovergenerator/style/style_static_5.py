import base64
from io import BytesIO
from pathlib import Path
from typing import Tuple

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
