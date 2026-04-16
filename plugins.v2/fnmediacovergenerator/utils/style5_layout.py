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
