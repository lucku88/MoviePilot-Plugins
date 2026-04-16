from typing import Any, Dict, Iterable, List, Optional


def normalize_history_paths(paths: Optional[Iterable[Any]]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for raw in paths or []:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def toggle_history_selection(selected_paths: Optional[Iterable[Any]], target_path: str) -> List[str]:
    normalized = normalize_history_paths(selected_paths)
    target = str(target_path or "").strip()
    if not target:
        return normalized
    if target in normalized:
        return [item for item in normalized if item != target]
    return normalized + [target]


def retain_history_selection(
    selected_paths: Optional[Iterable[Any]],
    visible_paths: Optional[Iterable[Any]],
) -> List[str]:
    visible = set(normalize_history_paths(visible_paths))
    return [item for item in normalize_history_paths(selected_paths) if item in visible]


def resolve_history_delete_targets(
    file: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> List[str]:
    targets: List[str] = []
    if file:
        targets.append(file)
    if isinstance(data, dict):
        if data.get("file"):
            targets.append(data.get("file"))
        files = data.get("files")
        if isinstance(files, (list, tuple, set)):
            targets.extend(files)
    return normalize_history_paths(targets)
