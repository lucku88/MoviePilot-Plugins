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
