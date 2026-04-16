import base64
from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat

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


def _load_rgb_copy(image_path: Path) -> Image.Image:
    with Image.open(image_path) as image:
        return image.convert("RGB").copy()


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


def _coerce_rgb_tuple(value) -> tuple[int, int, int] | None:
    if value is None:
        return None

    if isinstance(value, (tuple, list)) and len(value) >= 3:
        try:
            return (
                max(0, min(255, int(value[0]))),
                max(0, min(255, int(value[1]))),
                max(0, min(255, int(value[2]))),
            )
        except Exception:
            return None

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.startswith("#"):
            hex_value = raw[1:]
            if len(hex_value) == 3:
                hex_value = "".join(char * 2 for char in hex_value)
            if len(hex_value) == 6:
                try:
                    return (
                        int(hex_value[0:2], 16),
                        int(hex_value[2:4], 16),
                        int(hex_value[4:6], 16),
                    )
                except ValueError:
                    return None
        parts = [segment.strip() for segment in raw.split(",")]
        if len(parts) >= 3 and all(part.lstrip("-").isdigit() for part in parts[:3]):
            return (
                max(0, min(255, int(parts[0]))),
                max(0, min(255, int(parts[1]))),
                max(0, min(255, int(parts[2]))),
            )
    return None


def _resolve_bg_color(primary: Image.Image, bg_color_config) -> tuple[int, int, int]:
    config = bg_color_config or {}
    mode = str(config.get("mode", "auto") or "auto").strip().lower()

    if mode == "custom":
        color = _coerce_rgb_tuple(config.get("custom_color"))
        if color:
            return color
    elif mode in {"config", "fixed", "preset"}:
        color = _coerce_rgb_tuple(config.get("config_color"))
        if color:
            return color
    elif mode == "manual":
        color = _coerce_rgb_tuple(config.get("custom_color")) or _coerce_rgb_tuple(config.get("config_color"))
        if color:
            return color

    stat = ImageStat.Stat(primary.resize((1, 1), Image.Resampling.BILINEAR))
    mean = stat.mean
    return (
        max(0, min(255, int(mean[0]))),
        max(0, min(255, int(mean[1]))),
        max(0, min(255, int(mean[2]))),
    )


def _clamp_ratio(raw_value, default=0.8) -> float:
    try:
        ratio = float(raw_value)
    except Exception:
        ratio = default
    return max(0.0, min(1.0, ratio))


def _normalize_blur(raw_value) -> float:
    try:
        blur = float(raw_value)
    except Exception:
        blur = 50.0
    return max(0.0, blur)


def _scale_from_canvas(canvas_size: Tuple[int, int]) -> float:
    width, height = canvas_size
    if width <= 0 or height <= 0:
        return 1.0
    return min(width / 1920.0, height / 1080.0)


def _resolve_font_size(base_size: int, scale: float, resolution_config) -> int:
    base_size = max(1, int(base_size))
    getter = getattr(resolution_config, "get_font_size", None)
    if callable(getter):
        try:
            return max(1, int(getter(base_size, scale_factor=1.0)))
        except TypeError:
            return max(1, int(getter(base_size)))
        except Exception:
            pass
    return max(1, int(round(base_size * scale)))


def _resolve_font_offsets(font_offset, scale: float) -> tuple[int, int, int]:
    defaults = (0, 40, 40)
    values = list(defaults)
    if isinstance(font_offset, (tuple, list)):
        for index, value in enumerate(font_offset[:3]):
            try:
                values[index] = float(value)
            except Exception:
                values[index] = defaults[index]
    return (
        int(round(values[0] * scale)),
        int(round(values[1] * scale)),
        int(round(values[2] * scale)),
    )


def _build_styled_background(
    base_image: Image.Image,
    blur_size: float,
    color_ratio: float,
    bg_color_config,
) -> Image.Image:
    blur_radius = _normalize_blur(blur_size)
    ratio = _clamp_ratio(color_ratio)

    if blur_radius > 0:
        backdrop = base_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    else:
        backdrop = base_image.copy()

    tint_color = _resolve_bg_color(base_image, bg_color_config)
    tint_layer = Image.new("RGB", base_image.size, tint_color)
    backdrop = Image.blend(backdrop, tint_layer, ratio)

    structure_mix = 0.25 + (ratio * 0.45)
    return Image.blend(base_image, backdrop, structure_mix)


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
        max(1, int(getattr(resolution_config, "width", 1920))),
        max(1, int(getattr(resolution_config, "height", 1080))),
    )
    scale = _scale_from_canvas(canvas_size)
    image_paths = _collect_images(Path(library_dir))
    render_mode = resolve_style5_render_mode(len(image_paths))
    if render_mode["mode"] == "empty":
        raise ValueError("style_5 requires at least one image")
    echo_paths = _resolve_echo_paths(image_paths, render_mode)

    primary = _load_rgb_copy(image_paths[0])
    primary = _enhance_primary(primary)
    fitted_primary = ImageOps.fit(primary, canvas_size, Image.Resampling.LANCZOS)
    background = _build_styled_background(fitted_primary, blur_size * scale, color_ratio, bg_color_config)
    canvas = background.convert("RGBA")

    if render_mode["mode"] == "a2_standard":
        _draw_standard_echo_tiles(canvas, echo_paths)
    elif render_mode["mode"] == "a2_sparse":
        _draw_sparse_echo_tiles(canvas, echo_paths)

    mask = Image.new("L", canvas.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle((0, int(canvas.size[1] * 0.62), canvas.size[0], canvas.size[1]), fill=170)
    mask = mask.filter(ImageFilter.GaussianBlur(max(24, int(round(60 * scale)))))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay.putalpha(mask)
    canvas = Image.alpha_composite(canvas, overlay)

    left_b, left_c, right_b, right_c = _bottom_metrics(canvas)
    anchor = choose_style5_anchor(left_b, left_c, right_b, right_c)

    draw = ImageDraw.Draw(canvas)
    zh_size = _resolve_font_size(int(font_size[0]), scale, resolution_config)
    en_size = _resolve_font_size(int(font_size[1]), scale, resolution_config)
    zh_offset, title_spacing, en_line_spacing = _resolve_font_offsets(font_offset, scale)
    max_width = int(canvas.size[0] * 0.52)
    title_font = _load_font(font_path[0], zh_size)
    measured = int(draw.textlength(title[0], font=title_font))
    zh_size = resolve_style5_title_font_size(zh_size, measured, max_width)
    title_font = _load_font(font_path[0], zh_size)
    en_font = _load_font(font_path[1], en_size)

    side_margin = int(round(120 * scale))
    x = side_margin if anchor == "left" else canvas.size[0] - max_width - side_margin
    eyebrow_y = canvas.size[1] - int(round(270 * scale)) + zh_offset
    title_y = canvas.size[1] - int(round(210 * scale)) + zh_offset
    subtitle_y = title_y + int(round(90 * scale)) + title_spacing + en_line_spacing
    eyebrow = resolve_style5_eyebrow(title[0])
    draw.text((x, eyebrow_y), eyebrow, fill=(230, 230, 230, 210), font=en_font)
    draw.text((x, title_y), title[0], fill=(255, 255, 255, 255), font=title_font)
    if title[1]:
        draw.text((x, subtitle_y), title[1], fill=(230, 230, 230, 220), font=en_font)

    buffer = BytesIO()
    canvas.convert("RGB").save(buffer, format="JPEG", quality=95)
    payload = base64.b64encode(buffer.getvalue()).decode("utf-8")
    logger.info(
        "style_5 rendered in mode=%s echo_count=%s blur=%.2f ratio=%.2f",
        render_mode["mode"],
        len(echo_paths),
        _normalize_blur(blur_size),
        _clamp_ratio(color_ratio),
    )
    return payload
