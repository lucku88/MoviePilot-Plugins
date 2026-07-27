"""Small, dependency-free HTML parser for the Vue-魔丸 page.

This module deliberately handles only the page state needed by the first
parser step.  Recipe and detailed beach parsing can be added without making
the public page parser depend on MoviePilot.
"""

from html import unescape
from html.parser import HTMLParser
import math
import re
import time
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_TITLE = "搬砖捡破烂炼魔丸"
DEFAULT_DAILY_LIMIT = 50
DEFAULT_ICON = "📦"

_NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")
_SERVER_NOW_RE = re.compile(
    r"[\"']?(?:server_now|serverNow)[\"']?\s*[:=]\s*[\"']?"
    r"([-+]?\d[\d,]*)",
    re.IGNORECASE,
)
_DAILY_LIMIT_RE = re.compile(r"/\s*([-+]?\d[\d,]*)")

_UNIT_MULTIPLIERS = {
    "万": 10_000,
    "亿": 100_000_000,
    "千": 1_000,
    "百": 100,
    "k": 1_000,
    "m": 1_000_000,
    "b": 1_000_000_000,
}

_ICON_BY_NAME = {
    "砖块": "🧱",
    "木材": "🪵",
    "塑料袋": "🛍️",
    "瓶子": "🧴",
    "螺丝": "🔩",
    "旧电池": "🔋",
    "破铜片": "🪙",
    "木工件": "🪚",
    "塑料件": "🪣",
    "简易工具": "🛠️",
    "能量碎片": "⚡",
    "魔丸胚胎": "🥚",
    "魔丸": "⚗️",
    "蚯蚓": "🪱",
}


class _Node:
    """Minimal HTML tree node used instead of regular-expression nesting."""

    __slots__ = ("tag", "attrs", "content", "parent")

    def __init__(
        self,
        tag: str,
        attrs: Optional[Iterable[Any]] = None,
        parent: Optional["_Node"] = None,
    ) -> None:
        self.tag = tag.lower()
        self.attrs = {
            str(key).lower(): ("" if value is None else str(value))
            for key, value in (attrs or [])
        }
        self.content: List[Any] = []
        self.parent = parent


class _TreeParser(HTMLParser):
    """Build a tolerant, small tree while preserving balanced descendants."""

    _VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("__root__")
        self._stack: List[_Node] = [self.root]

    def _add_node(self, tag: str, attrs: Iterable[Any], push: bool) -> None:
        parent = self._stack[-1]
        node = _Node(tag, attrs, parent)
        parent.content.append(node)
        if push:
            self._stack.append(node)

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        self._add_node(tag, attrs, tag.lower() not in self._VOID_TAGS)

    def handle_startendtag(self, tag: str, attrs: Any) -> None:
        self._add_node(tag, attrs, False)

    def handle_endtag(self, tag: str) -> None:
        wanted = tag.lower()
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == wanted:
                del self._stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self._stack[-1].content.append(data)

    def handle_entityref(self, name: str) -> None:
        self._stack[-1].content.append(unescape("&%s;" % name))

    def handle_charref(self, name: str) -> None:
        self._stack[-1].content.append(unescape("&#%s;" % name))


def safe_int(value: Any, default: int = 0) -> int:
    """Return the first integer in a value, ignoring separators and units."""

    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if math.isfinite(value) else default

    try:
        text = str(value).strip()
    except Exception:
        return default
    match = _NUMBER_RE.search(text)
    if not match:
        return default

    number_text = match.group(0).replace(",", "")
    try:
        number: float = float(number_text)
    except (TypeError, ValueError):
        return default

    suffix = text[match.end() :].lstrip()
    if suffix:
        unit = suffix[0].lower()
        number *= _UNIT_MULTIPLIERS.get(unit, 1)
    return int(number)


def _coerce_html(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    try:
        return str(value)
    except Exception:
        return ""


def _parse_tree(source: str) -> _Node:
    parser = _TreeParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception:
        # HTMLParser is intentionally best-effort for partially rendered pages.
        pass
    return parser.root


def _walk(node: _Node) -> Iterable[_Node]:
    pending: List[_Node] = []
    for part in reversed(node.content):
        if isinstance(part, _Node):
            pending.append(part)
    while pending:
        current = pending.pop()
        yield current
        for part in reversed(current.content):
            if isinstance(part, _Node):
                pending.append(part)


def _walk_inclusive(node: _Node) -> Iterable[_Node]:
    yield node
    yield from _walk(node)


def _node_text(node: Optional[_Node]) -> str:
    if node is None:
        return ""
    parts: List[str] = []
    pending: List[Any] = [node]
    while pending:
        current = pending.pop()
        if isinstance(current, str):
            parts.append(current)
            continue
        for part in reversed(current.content):
            pending.append(part)
    return " ".join("".join(parts).split())


def _class_tokens(node: _Node) -> set:
    return {token.lower() for token in node.attrs.get("class", "").split() if token}


def _has_class(node: _Node, class_name: str) -> bool:
    return class_name.lower() in _class_tokens(node)


def _find_by_id(root: _Node, element_id: str) -> Optional[_Node]:
    wanted = element_id.lower()
    for node in _walk(root):
        if node.attrs.get("id", "").lower() == wanted:
            return node
    return None


def _find_first_tag(root: _Node, tag: str) -> Optional[_Node]:
    wanted = tag.lower()
    for node in _walk_inclusive(root):
        if node.tag == wanted:
            return node
    return None


def _find_first_class(root: _Node, class_name: str) -> Optional[_Node]:
    for node in _walk_inclusive(root):
        if _has_class(node, class_name):
            return node
    return None


def _find_descendant_class(root: _Node, class_name: str) -> Optional[_Node]:
    for node in _walk_inclusive(root):
        if _has_class(node, class_name):
            return node
    return None


def _find_descendant_tag(root: _Node, tag: str) -> Optional[_Node]:
    wanted = tag.lower()
    for node in _walk_inclusive(root):
        if node.tag == wanted:
            return node
    return None


def _normalise_timestamp(value: Any, default: int = 0) -> int:
    parsed = safe_int(value, default)
    if parsed <= 0:
        return default
    if parsed > 10_000_000_000:
        parsed //= 1000
    return parsed


def _server_now(source: str, now_ts: Optional[int]) -> int:
    fallback = (
        _normalise_timestamp(now_ts, 0)
        if now_ts is not None
        else int(time.time())
    )
    match = _SERVER_NOW_RE.search(source)
    if not match:
        return fallback
    return _normalise_timestamp(match.group(1), fallback)


def _default_page(server_now: int) -> Dict[str, Any]:
    return {
        "title": DEFAULT_TITLE,
        "price_text": "",
        "stats": {
            "points": 0,
            "bonus_earned": 0,
            "magic_pills": 0,
            "daily_bricks": 0,
            "daily_limit": DEFAULT_DAILY_LIMIT,
        },
        "brick": {
            "ready": False,
            "daily_bricks": 0,
            "daily_limit": DEFAULT_DAILY_LIMIT,
            "available_count": 0,
            "bag_count": 0,
            "status_text": "",
            "next_reset_ts": 0,
            "next_reset_time": "",
            "factory_text": "",
            "bag_text": "",
        },
        "beach": {
            "ready": False,
            "status_text": "",
            "next_ready_ts": 0,
            "next_ready_time": "",
            "level_text": "",
            "hnr_text": "",
            "enter_button_text": "",
            "collect_button_text": "",
            "collect_enabled": False,
        },
        "exchange": {
            "pill_price": 0,
            "magic_pills": 0,
            "points": 0,
            "max_count": 0,
            "enabled": False,
            "action_ready": False,
            "note": "",
        },
        "inventory": [],
        "recipes": [],
        "server_now": server_now,
    }


def parse_inventory(container_html: str) -> List[Dict[str, Any]]:
    """Parse all inventory items from an inventory grid or its inner HTML."""

    try:
        source = _coerce_html(container_html)
        if not source:
            return []
        root = _parse_tree(source)
        scope = _find_by_id(root, "inventoryGrid") or root
        items: List[Dict[str, Any]] = []
        for item_node in _walk_inclusive(scope):
            if not _has_class(item_node, "inventory-item"):
                continue

            name_node = _find_descendant_class(item_node, "item-name")
            icon_node = _find_descendant_class(item_node, "item-icon")
            count_node = _find_descendant_class(item_node, "item-count")
            name = _node_text(name_node)
            icon = _node_text(icon_node) or _ICON_BY_NAME.get(name, DEFAULT_ICON)
            count = safe_int(_node_text(count_node), 0)
            giftable = any(
                _has_class(node, "gift-btn") for node in _walk_inclusive(item_node)
            )
            has_items = _has_class(item_node, "has-items") and count > 0
            items.append(
                {
                    "name": name,
                    "icon": icon,
                    "count": count,
                    "giftable": bool(giftable),
                    "has_items": bool(has_items),
                }
            )
        return items
    except Exception:
        return []


def parse_recipes(container_html: str, inventory: Any) -> List[Dict[str, Any]]:
    """Recipe parsing is intentionally deferred to a later parser step."""

    return []


def parse_page(html: str, *, now_ts: Optional[int] = None) -> Dict[str, Any]:
    """Parse the supported page state and always return a safe result shape."""

    source = _coerce_html(html)
    server_now = _server_now(source, now_ts)
    result = _default_page(server_now)

    try:
        root = _parse_tree(source)

        title_node = _find_first_tag(root, "h1")
        if title_node is not None and _node_text(title_node):
            result["title"] = _node_text(title_node)

        price_banner = _find_first_class(root, "price-banner")
        if price_banner is not None:
            price_node = _find_descendant_tag(price_banner, "b")
            price_text = _node_text(price_node) or _node_text(price_banner)
            price_text = re.sub(r"^魔丸限时价格\s*[:：]?\s*", "", price_text)
            result["price_text"] = price_text

        stats = result["stats"]
        id_fields = (
            ("points", "points"),
            ("bonus_earned", "bonusEarned"),
            ("magic_pills", "magicPills"),
            ("daily_bricks", "dailyBricks"),
        )
        nodes_by_key: Dict[str, Optional[_Node]] = {}
        for key, element_id in id_fields:
            node = _find_by_id(root, element_id)
            nodes_by_key[key] = node
            stats[key] = safe_int(_node_text(node), 0)

        daily_node = nodes_by_key["daily_bricks"]
        daily_limit = DEFAULT_DAILY_LIMIT
        if daily_node is not None and daily_node.parent is not None:
            match = _DAILY_LIMIT_RE.search(_node_text(daily_node.parent))
            if match:
                daily_limit = safe_int(match.group(1), DEFAULT_DAILY_LIMIT)
        stats["daily_limit"] = daily_limit

        result["brick"]["daily_bricks"] = stats["daily_bricks"]
        result["brick"]["daily_limit"] = daily_limit
        result["exchange"]["magic_pills"] = stats["magic_pills"]
        result["exchange"]["points"] = stats["points"]

        result["inventory"] = parse_inventory(source)
        result["recipes"] = parse_recipes("", result["inventory"])
    except Exception:
        # Keep the already-created skeleton if a malformed page breaks parsing.
        pass

    return result


__all__ = ["safe_int", "parse_page", "parse_inventory", "parse_recipes"]
