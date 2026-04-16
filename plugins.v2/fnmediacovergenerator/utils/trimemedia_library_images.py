from typing import Any, Callable, Iterable, List, Optional


DIRECTORY_TYPES = {"Directory"}
MEDIA_TYPES = {"Movie", "TV", "Video"}


def _get_value(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        value = getattr(value, "value")
    return str(value).strip()


def _iter_image_candidates(value: Any) -> Iterable[str]:
    if isinstance(value, (list, tuple, set)):
        for item in value:
            normalized = _normalize_text(item)
            if normalized:
                yield normalized
        return
    normalized = _normalize_text(value)
    if normalized:
        yield normalized


def _pick_item_image_path(item: Any) -> str:
    for field in ("posters", "poster"):
        for candidate in _iter_image_candidates(_get_value(item, field)):
            return candidate
    return ""


def merge_unique_image_urls(*groups: Optional[Iterable[Any]], limit: Optional[int] = None) -> List[str]:
    merged: List[str] = []
    seen = set()
    for group in groups:
        for raw in group or []:
            value = _normalize_text(raw)
            if not value or value in seen:
                continue
            seen.add(value)
            merged.append(value)
            if limit is not None and len(merged) >= limit:
                return merged
    return merged


def prefer_supplemental_image_urls(
    base_urls: Optional[Iterable[Any]],
    supplemental_urls: Optional[Iterable[Any]],
    limit: Optional[int] = None,
) -> List[str]:
    preferred = merge_unique_image_urls(supplemental_urls, limit=limit)
    if preferred:
        return preferred
    return merge_unique_image_urls(base_urls, limit=limit)


def collect_library_item_image_paths(
    library_guid: str,
    fetch_children: Callable[[str], Iterable[Any]],
    fetch_details: Callable[[str], Any],
    limit: int,
) -> List[str]:
    queue: List[str] = [_normalize_text(library_guid)] if _normalize_text(library_guid) else []
    visited = set()
    results: List[str] = []
    seen = set()

    while queue and len(results) < limit:
        parent_guid = queue.pop(0)
        if not parent_guid or parent_guid in visited:
            continue
        visited.add(parent_guid)

        for item in fetch_children(parent_guid) or []:
            if len(results) >= limit:
                break
            item_guid = _normalize_text(_get_value(item, "guid"))
            item_type = _normalize_text(_get_value(item, "type"))
            if item_type in DIRECTORY_TYPES:
                if item_guid:
                    queue.append(item_guid)
                continue
            if item_type not in MEDIA_TYPES or not item_guid:
                continue

            detail = fetch_details(item_guid)
            image_path = _pick_item_image_path(detail) or _pick_item_image_path(item)
            if not image_path or image_path in seen:
                continue
            seen.add(image_path)
            results.append(image_path)

    return results
