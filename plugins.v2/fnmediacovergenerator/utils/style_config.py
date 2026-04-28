from typing import Any, Tuple


VALID_STATIC_STYLES = {"static_1", "static_2", "static_3", "static_4"}
VALID_ANIMATED_STYLES = {"animated_1", "animated_2", "animated_3", "animated_4"}


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def resolve_static_cover_style_base(cover_style: Any, cover_style_base: Any) -> str:
    base = str(cover_style_base or "").strip()
    if base in VALID_STATIC_STYLES:
        return base

    style = str(cover_style or "").strip()
    if style in VALID_STATIC_STYLES:
        return style
    if style in VALID_ANIMATED_STYLES:
        return f"static_{style.split('_')[-1]}"

    return "static_1"


def sanitize_title_layout_values(
    zh_font_offset: Any,
    title_spacing: Any,
    en_line_spacing: Any,
    title_scale: Any = 1.0,
) -> Tuple[float, float, float]:
    safe_title_scale = _clamp(_safe_float(title_scale, 1.0), 0.2, 4.0)
    safe_zh_font_offset = _clamp(_safe_float(zh_font_offset, 0.0), -240.0, 240.0)
    safe_title_spacing = _clamp(_safe_float(title_spacing, 40.0), -20.0, 220.0) * safe_title_scale
    safe_en_line_spacing = _clamp(_safe_float(en_line_spacing, 40.0), 20.0, 140.0) * safe_title_scale
    return safe_zh_font_offset, safe_title_spacing, safe_en_line_spacing
