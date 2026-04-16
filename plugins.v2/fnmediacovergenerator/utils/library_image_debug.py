from typing import Any, Iterable, Optional


def count_non_empty_items(items: Optional[Iterable[Any]]) -> int:
    return sum(
        1
        for item in items or []
        if item is not None and str(item).strip()
    )


def format_library_image_stats(
    plugin_name: str,
    server_name: str,
    library_name: str,
    library_id: str,
    returned_count: int,
    required_items: Optional[int] = None,
    deduped_count: Optional[int] = None,
) -> str:
    parts = [
        f"{plugin_name} 媒体库源图统计",
        f"服务器={server_name or '-'}",
        f"媒体库={library_name or '-'}",
        f"id={library_id or '-'}",
        f"飞牛返回 {returned_count} 张",
    ]
    if deduped_count is not None:
        parts.append(f"URL 去重后 {deduped_count} 张")
    if required_items is not None:
        parts.append(f"当前风格需要 {required_items} 张")
    return " | ".join(parts)
