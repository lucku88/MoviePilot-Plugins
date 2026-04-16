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


def _build_rounded_mask(size: Tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def _resolve_echo_paths(image_paths: list[Path], render_mode: dict) -> list[Path]:
    mode = render_mode.get("mode")
    max_echo = max(0, int(render_mode.get("echo_count", 0)))
    if mode == "a1_fallback":
        return []
    if mode not in {"a2_standard", "a2_sparse"}:
        return []
    available_echo = image_paths[1:]
    return available_echo[:max_echo]


def _build_echo_tile(
    image_path: Path,
    size: Tuple[int, int],
    corner: int,
    border_width: int,
) -> tuple[Image.Image, Image.Image]:
    with Image.open(image_path) as echo_image:
        tile = ImageOps.fit(
            echo_image.convert("RGB"),
            size,
            method=Image.Resampling.LANCZOS,
        ).convert("RGBA")
    tile = _enhance_primary(tile.convert("RGB")).convert("RGBA")
    mask = _build_rounded_mask(size, corner)
    clipped = Image.new("RGBA", size, (0, 0, 0, 0))
    clipped.paste(tile, (0, 0), mask)

    border = Image.new("RGBA", size, (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.rounded_rectangle(
        (1, 1, size[0] - 2, size[1] - 2),
        radius=corner,
        outline=(245, 245, 245, 232),
        width=border_width,
    )
    clipped = Image.alpha_composite(clipped, border)
    return clipped, mask


def _draw_standard_echo_tiles(canvas: Image.Image, echo_paths: list[Path]) -> None:
    if not echo_paths:
        return

    width, height = canvas.size
    tile_w = max(160, int(width * 0.13))
    tile_h = max(220, int(height * 0.19))
    gap = max(20, int(width * 0.012))
    top_margin = max(48, int(height * 0.06))
    right_margin = max(40, int(width * 0.03))
    step_y = max(8, int(height * 0.01))
    corner = max(12, int(min(tile_w, tile_h) * 0.09))
    border_width = max(2, int(width * 0.0015))
    shadow_offset = 6

    for index, image_path in enumerate(echo_paths):
        clipped, mask = _build_echo_tile(image_path, (tile_w, tile_h), corner, border_width)
        shadow = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 95))
        shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(4)))
        x = width - right_margin - tile_w - index * (tile_w + gap)
        y = top_margin + index * step_y
        canvas.alpha_composite(shadow, (x + shadow_offset, y + shadow_offset))
        canvas.alpha_composite(clipped, (x, y))


def _draw_sparse_echo_tiles(canvas: Image.Image, echo_paths: list[Path]) -> None:
    if not echo_paths:
        return

    width, height = canvas.size
    tile_w = max(260, int(width * 0.2))
    tile_h = max(340, int(height * 0.32))
    gap = max(20, int(width * 0.012))
    right_margin = max(44, int(width * 0.03))
    bottom_margin = max(44, int(height * 0.04))
    corner = max(18, int(min(tile_w, tile_h) * 0.08))
    border_width = max(3, int(width * 0.0018))
    shadow_offset = 8
    shadow_alpha = 110

    first_x = width - right_margin - tile_w
    first_y = height - bottom_margin - tile_h
    second_x = first_x - tile_w + int(tile_w * 0.22) - gap
    second_y = first_y - int(tile_h * 0.08)
    positions = [(first_x, first_y), (second_x, second_y)]

    for index, image_path in enumerate(echo_paths[:2]):
        clipped, mask = _build_echo_tile(image_path, (tile_w, tile_h), corner, border_width)
        shadow = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, shadow_alpha))
        shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(6)))
        x, y = positions[index]
        canvas.alpha_composite(shadow, (x + shadow_offset, y + shadow_offset))
        canvas.alpha_composite(clipped, (x, y))


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
    echo_paths = _resolve_echo_paths(image_paths, render_mode)

    primary = Image.open(image_paths[0]).convert("RGB")
    primary = _enhance_primary(primary)
    canvas = ImageOps.fit(primary, canvas_size, Image.Resampling.LANCZOS).convert("RGBA")

    if render_mode["mode"] == "a2_standard":
        _draw_standard_echo_tiles(canvas, echo_paths)
    elif render_mode["mode"] == "a2_sparse":
        _draw_sparse_echo_tiles(canvas, echo_paths)

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
    logger.info("style_5 rendered in mode=%s echo_count=%s", render_mode["mode"], len(echo_paths))
    return payload
