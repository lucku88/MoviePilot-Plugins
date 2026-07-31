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
DEFAULT_BEACH_INTERVAL = 7200
MAX_BEACH_INTERVAL_SECONDS = 7 * 24 * 60 * 60
DEFAULT_ICON = "📦"

_NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")
_NON_NEGATIVE_INT_PATTERN = r"(?:\d{1,3}(?:,\d{3})+|\d+)"
_NON_NEGATIVE_INT_RE = re.compile(rf"^{_NON_NEGATIVE_INT_PATTERN}$")
_DAILY_LIMIT_RE = re.compile(
    rf"/\s*({_NON_NEGATIVE_INT_PATTERN})\s*$"
)
_CRAFT_ID_RE = re.compile(r"\bcraft\s*\(\s*(\d+)\s*\)", re.IGNORECASE)
_CRAFT_INPUT_ID_RE = re.compile(r"^craft[-_](\d+)$", re.IGNORECASE)
_COOLDOWN_WORDS = ("倒计时", "下次清理", "冷却")
_BRICK_READY_WORDS = (
    "可以搬砖",
    "可搬砖",
    "立即搬砖",
    "立即搬",
    "拖拽砖块到口袋",
    "搬砖到口袋",
)
_BRICK_BLOCKED_WORDS = ("倒计时", "上限", "明日", "明天")
_CONSERVATIVE_NEGATIVE_SIGNALS = (
    "暂无",
    "没有",
    "尚未",
    "不能",
    "不可",
    "无法",
    "未到",
    "冷却",
    "等待",
    "稍后",
    "勿",
    "禁",
    "停",
    "关闭",
    "无",
    "不",
    "未",
)
_TRASH_WORDS = (
    "待收垃圾",
    "待收集垃圾",
    "可以收集垃圾",
    "可收集垃圾",
    "发现垃圾",
    "垃圾待收",
    "垃圾可收集",
)
_NO_TRASH_WORDS = (
    "垃圾已清理",
    "已清理",
    "已收集",
    "清理完成",
    "收集完成",
)
_TRASH_STATUS_PATTERN = "(?:%s)" % "|".join(
    re.escape(word) for word in _TRASH_WORDS
)
_ZERO_TRASH_COUNT_RE = re.compile(
    rf"(?:{_TRASH_STATUS_PATTERN}\s*(?:数量|数目|共|为)?\s*[:：]?\s*"
    r"(?:(?<![\d.])0+(?![\d.])|零)\s*(?:个|件|条|份|项)?"
    r"(?=$|[\s，,。；;！!）)])|"
    r"(?:(?<![\d.])0+(?![\d.])|零)\s*(?:个|件|条|份|项)?\s*"
    rf"{_TRASH_STATUS_PATTERN})"
)
_NO_TRASH_MARKERS = (
    "no-trash",
    "trash-empty",
    "empty-trash",
    "no-garbage",
    "garbage-empty",
    "empty-garbage",
    "no-litter",
    "litter-empty",
    "empty-litter",
)
_TRASH_ITEM_MARKERS = {
    "trash",
    "trash-item",
    "trashitem",
    "garbage",
    "garbage-item",
    "garbageitem",
    "litter",
    "litter-item",
    "litteritem",
}

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

_RECIPE_DEFINITIONS = {
    1: {
        "name": "木工件",
        "output_item": "木工件",
        "ingredients": {"砖块": 5, "木材": 1, "塑料袋": 1},
    },
    2: {
        "name": "塑料件",
        "output_item": "塑料件",
        "ingredients": {"砖块": 5, "塑料袋": 1, "瓶子": 1},
    },
    3: {
        "name": "简易工具",
        "output_item": "简易工具",
        "ingredients": {"螺丝": 2, "木工件": 2},
    },
    4: {
        "name": "能量碎片",
        "output_item": "能量碎片",
        "ingredients": {"旧电池": 1, "塑料件": 2},
    },
    5: {
        "name": "魔丸胚胎",
        "output_item": "魔丸胚胎",
        "ingredients": {"破铜片": 1, "简易工具": 1, "能量碎片": 1},
    },
    6: {
        "name": "魔丸",
        "output_item": "魔丸",
        "ingredients": {"砖块": 10, "魔丸胚胎": 2},
    },
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
    _OPTIONAL_END_TAGS = {
        "colgroup",
        "dd",
        "dt",
        "li",
        "optgroup",
        "option",
        "p",
        "rp",
        "rt",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("__root__")
        self._stack: List[_Node] = [self.root]
        self.errors: List[str] = []

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
                intervening = self._stack[index + 1 :]
                if intervening and not all(
                    node.tag in self._OPTIONAL_END_TAGS
                    for node in intervening
                ):
                    self.errors.append("misnested closing tag: %s" % wanted)
                del self._stack[index:]
                return
        self.errors.append("unexpected closing tag: %s" % wanted)

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


def _strict_non_negative_int(value: Any) -> Optional[int]:
    """Return a complete non-negative integer, without prefix guessing."""

    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    try:
        text = str(value).strip()
    except Exception:
        return None
    if not _NON_NEGATIVE_INT_RE.fullmatch(text):
        return None
    try:
        return int(text.replace(",", ""))
    except ValueError:
        return None


def _strict_brick_count(value: Any, label: str) -> Optional[int]:
    source = _coerce_html(value).strip()
    match = re.fullmatch(
        rf"(?:{re.escape(label)}\s*[:：]?\s*)?"
        rf"({_NON_NEGATIVE_INT_PATTERN})\s*(?:块)?",
        source,
    )
    if match is None:
        return None
    return _strict_non_negative_int(match.group(1))


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
    parser.feed(source)
    parser.close()
    if parser.errors:
        raise ValueError("malformed HTML: %s" % "; ".join(parser.errors[:3]))
    if len(parser._stack) != 1:
        unclosed = " > ".join(node.tag for node in parser._stack[1:])
        raise ValueError("unclosed HTML tags: %s" % unclosed)
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


def _is_disabled(node: Optional[_Node]) -> bool:
    if node is None:
        return True
    if "disabled" in node.attrs:
        return True
    if node.attrs.get("aria-disabled", "").strip().lower() in {"1", "true", "yes"}:
        return True
    return "disabled" in _class_tokens(node)


def _is_pointer_disabled(node: Optional[_Node]) -> bool:
    if _is_disabled(node):
        return True
    if node is None:
        return True
    style = re.sub(r"\s+", "", node.attrs.get("style", "").lower())
    return "pointer-events:none" in style


def _strip_script_comments(source: str) -> str:
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"(?m)(?<!:)//[^\r\n]*", "", without_blocks)


def _script_candidates(source: str) -> List[str]:
    scripts: List[str] = []
    for match in re.finditer(
        r"<script\b([^>]*)>(.*?)</script\s*>",
        source,
        re.IGNORECASE | re.DOTALL,
    ):
        attrs = match.group(1)
        if re.search(r"\btype\s*=\s*[\"'][^\"']*template", attrs, re.IGNORECASE):
            continue
        scripts.append(_strip_script_comments(match.group(2)))

    game_data_blocks: List[str] = []
    for script in scripts:
        game_data_blocks.extend(
            match.group(1)
            for match in re.finditer(
                r"\bgameData\b\s*=\s*(\{.*?\})",
                script,
                re.IGNORECASE | re.DOTALL,
            )
        )
    return game_data_blocks + scripts


def _script_number(source: str, names: Iterable[str]) -> Optional[int]:
    aliases = "|".join(re.escape(name) for name in names if name)
    if not aliases:
        return None
    number_pattern = r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)"
    pattern = re.compile(
        rf"(?<![\w$])(?:[\"'](?:{aliases})[\"']|(?:{aliases}))\s*"
        rf"[:=]\s*(?:(?P<quote>[\"'])[ \t]*(?P<quoted>{number_pattern})"
        rf"[ \t]*(?P=quote)|(?P<plain>{number_pattern}))"
        r"(?=[ \t]*(?:[,;}\]]|\r?\n|$))",
        re.IGNORECASE,
    )
    for candidate in _script_candidates(source):
        match = pattern.search(candidate)
        if match:
            return safe_int(match.group("quoted") or match.group("plain"), 0)
    return None


def _script_server_now(source: str) -> Optional[int]:
    direct = _script_number(source, ("server_now", "serverNow"))
    if direct is not None:
        return direct

    pattern = re.compile(
        r"(?<![\w$])(?:[\"']serverTimeOffset[\"']|serverTimeOffset)\s*"
        r"[:=]\s*(?P<server_now>\d{10,13})\s*-\s*"
        r"Math\.floor\(\s*Date\.now\(\s*\)\s*/\s*1000\s*\)",
        re.IGNORECASE,
    )
    for candidate in _script_candidates(source):
        match = pattern.search(candidate)
        if match:
            return safe_int(match.group("server_now"), 0)
    return None


def _normalise_timestamp(value: Any, default: int = 0) -> int:
    parsed = safe_int(value, default)
    if parsed <= 0:
        return default
    if parsed > 10_000_000_000:
        parsed //= 1000
    return parsed


def _normalise_duration(
    value: Any,
    default: int = DEFAULT_BEACH_INTERVAL,
) -> int:
    parsed = safe_int(value, default)
    if parsed <= 0:
        return default
    if parsed > MAX_BEACH_INTERVAL_SECONDS and parsed % 1000 == 0:
        milliseconds_candidate = parsed // 1000
        if 0 < milliseconds_candidate <= MAX_BEACH_INTERVAL_SECONDS:
            parsed = milliseconds_candidate
    return max(1, parsed)


def _server_now(source: str, now_ts: Optional[int]) -> int:
    fallback = (
        _normalise_timestamp(now_ts, 0)
        if now_ts is not None
        else int(time.time())
    )
    raw_value = _script_server_now(source)
    if raw_value is None:
        return fallback
    return _normalise_timestamp(raw_value, fallback)


def _format_timestamp(value: Any) -> str:
    parsed = _normalise_timestamp(value, 0)
    if parsed <= 0:
        return ""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(parsed))
    except (OverflowError, OSError, ValueError):
        return ""


def _countdown_seconds(text: str) -> int:
    source = _coerce_html(text)
    clock_match = re.search(
        r"(?<!\d)(\d{1,4}):(\d{1,2})(?::(\d{1,2}))?(?!\d)",
        source,
    )
    if clock_match:
        first = safe_int(clock_match.group(1), 0)
        second = safe_int(clock_match.group(2), 0)
        third_text = clock_match.group(3)
        if third_text is None:
            return max(0, first * 60 + second)
        return max(0, first * 3600 + second * 60 + safe_int(third_text, 0))

    chinese_match = re.search(
        r"(?:(\d+)\s*小时)?\s*(?:(\d+)\s*分(?:钟)?)?\s*(?:(\d+)\s*秒)?",
        source,
    )
    if chinese_match and any(chinese_match.groups()):
        return max(
            0,
            safe_int(chinese_match.group(1), 0) * 3600
            + safe_int(chinese_match.group(2), 0) * 60
            + safe_int(chinese_match.group(3), 0),
        )
    return 0


def _current_value_text(source: str, label: str) -> str:
    match = re.search(
        rf"{re.escape(label)}.*?当前\s*[:：]\s*([^）)<\r\n]+)",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    return " ".join(unescape(match.group(1)).split())


def _inventory_count_map(inventory: Any) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    try:
        if isinstance(inventory, dict):
            for name, count in inventory.items():
                counts[str(name)] = max(0, safe_int(count, 0))
            return counts
        if isinstance(inventory, (str, bytes)) or inventory is None:
            return counts
        for item in inventory:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if name:
                counts[name] = max(0, safe_int(item.get("count"), 0))
    except Exception:
        return counts
    return counts


def _material_name(text: str) -> str:
    source = " ".join(_coerce_html(text).split())
    for name in sorted(_ICON_BY_NAME, key=len, reverse=True):
        if name in source:
            return name
    return re.sub(r"^[^\w]+", "", source, flags=re.UNICODE).strip()


def _parse_material_text(text: str) -> Optional[Dict[str, Any]]:
    source = " ".join(_coerce_html(text).split())
    match = re.match(r"^(.*?)\s*[:：]\s*(.*?)$", source)
    if not match:
        return None
    name = _material_name(match.group(1))
    amount_text = match.group(2)
    if not name:
        return None

    available: Optional[int] = None
    required_text = amount_text
    if "/" in amount_text:
        available_text, required_text = amount_text.rsplit("/", 1)
        available = _strict_non_negative_int(available_text)
        if available is None:
            return None
    required = _strict_non_negative_int(required_text)
    if required is None:
        return None
    return {
        "name": name,
        "available": available,
        "required": required,
        "text": source,
    }


def _recipe_craft_id(recipe_node: _Node) -> int:
    for node in _walk_inclusive(recipe_node):
        match = _CRAFT_ID_RE.search(node.attrs.get("onclick", ""))
        if match:
            return safe_int(match.group(1), 0)
    for node in _walk_inclusive(recipe_node):
        match = _CRAFT_INPUT_ID_RE.match(node.attrs.get("id", ""))
        if match:
            return safe_int(match.group(1), 0)
    return 0


def _recipe_action_node(recipe_node: _Node, craft_id: int) -> Optional[_Node]:
    for node in _walk_inclusive(recipe_node):
        match = _CRAFT_ID_RE.search(node.attrs.get("onclick", ""))
        if match and safe_int(match.group(1), 0) == craft_id:
            return node
    return None


def _recipe_input_node(recipe_node: _Node, craft_id: int) -> Optional[_Node]:
    wanted_id = "craft-%s" % craft_id
    for node in _walk_inclusive(recipe_node):
        if node.tag == "input" and node.attrs.get("id", "") == wanted_id:
            return node
    return None


def _recipe_output_parts(
    title_text: str,
    status_text: str,
    recipe_definition: Dict[str, Any],
) -> Dict[str, str]:
    clean_title = " ".join(title_text.split())
    if status_text:
        clean_title = clean_title.replace(status_text, "", 1).strip()
    clean_title = re.sub(r"\s*[（(][^（）()]*[）)]\s*$", "", clean_title).strip()

    output_item = ""
    icon = ""
    for name in sorted(_ICON_BY_NAME, key=len, reverse=True):
        index = clean_title.find(name)
        if index < 0:
            continue
        output_item = name
        prefix = clean_title[:index].strip()
        if prefix:
            icon = prefix.split()[-1]
        break

    if not output_item:
        tokens = clean_title.split(maxsplit=1)
        if len(tokens) == 2 and not re.search(r"[\w\u4e00-\u9fff]", tokens[0]):
            icon, output_item = tokens[0], tokens[1].strip()
        else:
            output_item = clean_title

    if not output_item:
        output_item = str(
            recipe_definition.get("output_item")
            or recipe_definition.get("name")
            or ""
        ).strip()
    if not clean_title:
        clean_title = output_item
    if not icon:
        icon = _ICON_BY_NAME.get(output_item, DEFAULT_ICON)
    return {"title": clean_title, "output_item": output_item, "icon": icon}


def _has_countdown(node: Optional[_Node], text: str) -> bool:
    if any(word in text for word in _COOLDOWN_WORDS):
        return True
    if node is None:
        return False
    return any(
        _has_class(descendant, "countdown")
        for descendant in _walk_inclusive(node)
    )


def _has_conservative_negative_signal(text: str) -> bool:
    source = " ".join(_coerce_html(text).split())
    return any(signal in source for signal in _CONSERVATIVE_NEGATIVE_SIGNALS)


def _has_zero_trash_count(text: str) -> bool:
    source = " ".join(_coerce_html(text).split())
    return bool(_ZERO_TRASH_COUNT_RE.search(source))


def _beach_has_trash(
    beach_area: Optional[_Node],
    status_text: str,
) -> bool:
    area_text = _node_text(beach_area)
    if beach_area is not None:
        for node in _walk_inclusive(beach_area):
            marker = " ".join(
                (
                    node.attrs.get("id", ""),
                    node.attrs.get("class", ""),
                    node.attrs.get("data-type", ""),
                )
            ).lower().replace("_", "-")
            marker_tokens = set(re.split(r"[^a-z0-9-]+", marker))
            if any(
                token in _TRASH_ITEM_MARKERS
                or token.endswith(
                    ("-trash-item", "-garbage-item", "-litter-item")
                )
                for token in marker_tokens
                if token
            ):
                return True

    if _has_conservative_negative_signal(status_text):
        return False
    if _has_conservative_negative_signal(area_text):
        return False
    if any(word in status_text for word in _NO_TRASH_WORDS):
        return False
    if any(word in area_text for word in _NO_TRASH_WORDS):
        return False

    if beach_area is not None:
        for node in _walk_inclusive(beach_area):
            marker = " ".join(
                (
                    node.attrs.get("id", ""),
                    node.attrs.get("class", ""),
                    node.attrs.get("onclick", ""),
                    node.attrs.get("data-type", ""),
                )
            ).lower().replace("_", "-")
            if any(word in marker for word in _NO_TRASH_MARKERS):
                return False
        if _has_zero_trash_count(area_text):
            return False
        if any(word in area_text for word in _TRASH_WORDS):
            return True

    if _has_zero_trash_count(status_text):
        return False
    if any(word in status_text for word in _TRASH_WORDS):
        return True
    return False


def _default_page(server_now: int) -> Dict[str, Any]:
    return {
        "parse_complete": False,
        "parse_error": "",
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
            "can_enter": False,
            "can_collect": False,
            "has_trash": False,
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


def _disable_actions(result: Dict[str, Any]) -> None:
    result["parse_complete"] = False
    brick = result.get("brick") or {}
    brick["ready"] = False

    beach = result.get("beach") or {}
    beach["ready"] = False
    beach["can_enter"] = False
    beach["can_collect"] = False
    beach["collect_enabled"] = False

    exchange = result.get("exchange") or {}
    exchange["enabled"] = False
    exchange["action_ready"] = False

    for recipe in result.get("recipes") or []:
        if not isinstance(recipe, dict):
            continue
        recipe["enabled"] = False
        recipe["can_craft"] = False
        recipe["disabled"] = True


def parse_inventory(
    container_html: str,
    *,
    _raise_errors: bool = False,
) -> List[Dict[str, Any]]:
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
        if _raise_errors:
            raise
        return []


def _compatibility_recipes(inventory: Any) -> List[Dict[str, Any]]:
    inventory_counts = _inventory_count_map(inventory)
    recipes: List[Dict[str, Any]] = []
    for craft_id in sorted(_RECIPE_DEFINITIONS):
        definition = _RECIPE_DEFINITIONS[craft_id]
        output_item = str(definition.get("output_item") or definition["name"])
        icon = _ICON_BY_NAME.get(output_item, DEFAULT_ICON)
        ingredients = {
            str(name): max(0, safe_int(required, 0))
            for name, required in (definition.get("ingredients") or {}).items()
        }
        limits = [
            inventory_counts[name] // max(1, required)
            for name, required in ingredients.items()
            if name in inventory_counts and required > 0
        ]
        max_count = (
            min(limits, default=0) if len(limits) == len(ingredients) else 0
        )
        recipes.append(
            {
                "title": "%s %s" % (icon, output_item),
                "name": output_item,
                "output_item": output_item,
                "icon": icon,
                "status": "",
                "materials": [],
                "ingredients": ingredients,
                "ingredient_details": [
                    {
                        "name": name,
                        "available": inventory_counts.get(name),
                        "required": required,
                        "text": "",
                    }
                    for name, required in ingredients.items()
                ],
                "can_craft": False,
                "max_count": max_count,
                "max": max_count,
                "craft_id": craft_id,
                "disabled": True,
                "enabled": False,
                "supported": True,
            }
        )
    return recipes


def parse_recipes(
    container_html: str,
    inventory: Any,
    *,
    _raise_errors: bool = False,
) -> List[Dict[str, Any]]:
    """Parse balanced recipe cards and keep page values ahead of fallbacks."""

    try:
        source = _coerce_html(container_html)
        if not source:
            return _compatibility_recipes(inventory)
        root = _parse_tree(source)
        scope = _find_by_id(root, "recipeGrid") or root
        inventory_counts = _inventory_count_map(inventory)
        recipes: List[Dict[str, Any]] = []
        seen_ids = set()
        found_recipe_card = False

        for recipe_node in _walk_inclusive(scope):
            if not _has_class(recipe_node, "recipe"):
                continue
            found_recipe_card = True
            craft_id = _recipe_craft_id(recipe_node)
            if craft_id <= 0 or craft_id in seen_ids:
                continue
            seen_ids.add(craft_id)

            recipe_definition = _RECIPE_DEFINITIONS.get(craft_id, {})
            title_node = _find_descendant_class(recipe_node, "recipe-title")
            status_node = (
                _find_descendant_tag(title_node, "span")
                if title_node is not None
                else None
            )
            status_text = _node_text(status_node)
            output_parts = _recipe_output_parts(
                _node_text(title_node),
                status_text,
                recipe_definition,
            )
            icon_node = _find_descendant_class(recipe_node, "recipe-icon")
            if icon_node is not None and _node_text(icon_node):
                output_parts["icon"] = _node_text(icon_node)

            material_nodes = [
                node
                for node in _walk_inclusive(recipe_node)
                if _has_class(node, "material-item")
            ]
            materials = [
                text for text in (_node_text(node) for node in material_nodes) if text
            ]
            ingredient_details = []
            ingredients: Dict[str, int] = {}
            for material_text in materials:
                detail = _parse_material_text(material_text)
                if detail is None:
                    continue
                ingredient_details.append(detail)
                ingredients[detail["name"]] = detail["required"]

            input_node = _recipe_input_node(recipe_node, craft_id)
            max_count = 0
            max_is_explicit = input_node is not None and "max" in input_node.attrs
            max_is_valid = False
            if max_is_explicit:
                explicit_max = _strict_non_negative_int(
                    input_node.attrs.get("max")
                )
                max_is_valid = explicit_max is not None
                max_count = explicit_max if explicit_max is not None else 0
            else:
                status_match = re.search(
                    rf"最多(?:可)?制作\s*({_NON_NEGATIVE_INT_PATTERN})"
                    r"\s*[)）]?\s*$",
                    status_text,
                    re.IGNORECASE,
                )
                if status_match:
                    status_max = _strict_non_negative_int(status_match.group(1))
                    max_count = status_max if status_max is not None else 0

            if not max_is_explicit and max_count <= 0 and ingredient_details:
                page_limits = [
                    safe_int(detail.get("available"), 0)
                    // max(1, safe_int(detail.get("required"), 1))
                    for detail in ingredient_details
                    if detail.get("available") is not None
                    and safe_int(detail.get("required"), 0) > 0
                ]
                if len(page_limits) == len(ingredient_details):
                    max_count = min(page_limits, default=0)

            if not max_is_explicit and max_count <= 0 and ingredients:
                inventory_limits = [
                    inventory_counts[name] // max(1, required)
                    for name, required in ingredients.items()
                    if name in inventory_counts and required > 0
                ]
                if len(inventory_limits) == len(ingredients):
                    max_count = min(inventory_limits, default=0)

            title_text = _node_text(title_node)
            expected_output = str(recipe_definition.get("output_item") or "")
            supported = bool(
                recipe_definition
                and title_text
                and output_parts["output_item"] == expected_output
            )
            expected_ingredients = set(
                (recipe_definition.get("ingredients") or {}).keys()
            )
            ingredients_complete = bool(
                supported
                and materials
                and len(ingredient_details) == len(materials)
                and expected_ingredients.issubset(ingredients)
                and all(required > 0 for required in ingredients.values())
            )
            action_node = _recipe_action_node(recipe_node, craft_id)
            enabled = bool(
                action_node is not None
                and not _is_pointer_disabled(action_node)
                and ingredients_complete
                and input_node is not None
                and not _is_pointer_disabled(input_node)
                and max_is_explicit
                and max_is_valid
                and max_count > 0
            )
            can_craft = bool(
                enabled
                and _has_class(recipe_node, "can-craft")
                and max_count > 0
            )
            recipes.append(
                {
                    "title": output_parts["title"],
                    "name": output_parts["output_item"],
                    "output_item": output_parts["output_item"],
                    "icon": output_parts["icon"],
                    "status": status_text,
                    "materials": materials,
                    "ingredients": ingredients,
                    "ingredient_details": ingredient_details,
                    "can_craft": can_craft,
                    "max_count": max_count,
                    "max": max_count,
                    "craft_id": craft_id,
                    "disabled": not enabled,
                    "enabled": enabled,
                    "supported": supported,
                }
            )
        if not found_recipe_card:
            return _compatibility_recipes(inventory)
        return recipes
    except Exception:
        if _raise_errors:
            raise
        return []


def parse_page(html: str, *, now_ts: Optional[int] = None) -> Dict[str, Any]:
    """Parse the supported page state and always return a safe result shape."""

    source = _coerce_html(html)
    server_now = _server_now(source, now_ts)
    result = _default_page(server_now)
    if not source.strip():
        result["recipes"] = _compatibility_recipes([])
        result["parse_error"] = "empty page"
        _disable_actions(result)
        return result

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
        daily_bricks_value: Optional[int] = None
        magic_pills_value: Optional[int] = None
        for key, element_id in id_fields:
            node = _find_by_id(root, element_id)
            nodes_by_key[key] = node
            node_text = _node_text(node)
            if key == "daily_bricks":
                daily_bricks_value = _strict_non_negative_int(node_text)
                stats[key] = (
                    daily_bricks_value
                    if daily_bricks_value is not None
                    else 0
                )
            elif key == "magic_pills":
                magic_pills_value = _strict_non_negative_int(node_text)
                stats[key] = (
                    magic_pills_value
                    if magic_pills_value is not None
                    else 0
                )
            else:
                stats[key] = safe_int(node_text, 0)

        daily_node = nodes_by_key["daily_bricks"]
        daily_limit_value: Optional[int] = None
        if daily_node is not None and daily_node.parent is not None:
            match = _DAILY_LIMIT_RE.search(_node_text(daily_node.parent))
            if match:
                daily_limit_value = _strict_non_negative_int(match.group(1))
        daily_limit = (
            daily_limit_value
            if daily_limit_value is not None
            else DEFAULT_DAILY_LIMIT
        )
        stats["daily_limit"] = daily_limit

        raw_server_now = _script_server_now(source)
        raw_last_beach = _script_number(
            source,
            ("last_beach_time", "lastBeachTime"),
        )
        raw_beach_interval = _script_number(
            source,
            ("beach_interval", "beachInterval"),
        )
        raw_brick_reset = _script_number(
            source,
            ("next_brick_reset_ts", "nextBrickResetTs"),
        )
        last_beach_time = _normalise_timestamp(raw_last_beach, 0)
        beach_interval = _normalise_duration(
            raw_beach_interval,
            DEFAULT_BEACH_INTERVAL,
        )
        next_brick_reset_ts = _normalise_timestamp(raw_brick_reset, 0)

        factory_node = _find_by_id(root, "brickFactory")
        factory_count_node = _find_by_id(root, "factoryBrickCount")
        bag_count_node = _find_by_id(root, "bagBrickCount")
        brick_status_node = _find_by_id(root, "brickStatus")
        factory_text = _node_text(factory_count_node)
        bag_text = _node_text(bag_count_node)
        brick_status_text = _node_text(brick_status_node)
        available_count_value = _strict_brick_count(factory_text, "可搬")
        invalid_brick_values = []
        if daily_node is not None and daily_bricks_value is None:
            invalid_brick_values.append("dailyBricks")
        if daily_node is not None and daily_limit_value is None:
            invalid_brick_values.append("dailyLimit")
        if factory_count_node is not None and available_count_value is None:
            invalid_brick_values.append("factoryBrickCount")
        brick_state_complete = all(
            node is not None
            for node in (
                daily_node,
                factory_node,
                factory_count_node,
                brick_status_node,
            )
        )
        brick_values_valid = not invalid_brick_values
        available_count = (
            available_count_value
            if available_count_value is not None
            else 0
        )
        bag_count = max(0, safe_int(bag_text, 0))
        brick_status_blocked = bool(
            _has_conservative_negative_signal(brick_status_text)
            or any(
                word in brick_status_text for word in _BRICK_BLOCKED_WORDS
            )
        )
        brick_status_ready = any(
            word in brick_status_text for word in _BRICK_READY_WORDS
        )
        factory_blocked = _is_pointer_disabled(factory_node)
        brick_ready = bool(
            brick_state_complete
            and brick_values_valid
            and stats["daily_bricks"] < daily_limit
            and available_count > 0
            and brick_status_ready
            and not brick_status_blocked
            and not factory_blocked
        )
        result["brick"].update(
            {
                "ready": brick_ready,
                "daily_bricks": stats["daily_bricks"],
                "daily_limit": daily_limit,
                "available_count": available_count,
                "bag_count": bag_count,
                "status_text": brick_status_text
                or ("可以搬砖" if brick_ready else "今日搬砖已满"),
                "next_reset_ts": next_brick_reset_ts,
                "next_reset_time": _format_timestamp(next_brick_reset_ts),
                "factory_text": factory_text,
                "bag_text": bag_text,
            }
        )

        exchange_points_node = _find_by_id(root, "points2")
        exchange_pills_node = _find_by_id(root, "magicPills2")
        exchange_input_node = _find_by_id(root, "exchangeCount")
        exchange_button_node = _find_by_id(root, "exchangeBtn")
        exchange_points = safe_int(
            _node_text(exchange_points_node),
            stats["points"],
        )
        exchange_pills_value = magic_pills_value
        invalid_exchange_values = []
        if nodes_by_key["magic_pills"] is not None and magic_pills_value is None:
            invalid_exchange_values.append("magicPills")
        if exchange_pills_node is not None:
            exchange_pills_value = _strict_non_negative_int(
                _node_text(exchange_pills_node)
            )
            if exchange_pills_value is None:
                invalid_exchange_values.append("magicPills2")
        exchange_pills = (
            exchange_pills_value
            if exchange_pills_value is not None
            else 0
        )
        exchange_state_complete = all(
            node is not None
            for node in (
                nodes_by_key["points"],
                nodes_by_key["magic_pills"],
                exchange_input_node,
                exchange_button_node,
            )
        )
        pill_price = safe_int(result["price_text"], 0)
        if pill_price <= 0:
            price_match = re.search(
                r"1\s*魔丸\s*=\s*([\d,]+)\s*魔力",
                source,
                re.IGNORECASE,
            )
            if price_match:
                pill_price = max(0, safe_int(price_match.group(1), 0))
        exchange_max_value: Optional[int] = None
        if exchange_input_node is not None and "max" in exchange_input_node.attrs:
            exchange_max_value = _strict_non_negative_int(
                exchange_input_node.attrs.get("max")
            )
        if exchange_input_node is not None and exchange_max_value is None:
            invalid_exchange_values.append("exchangeCount.max")
        exchange_max = (
            exchange_max_value if exchange_max_value is not None else 0
        )
        exchange_enabled = bool(
            exchange_state_complete
            and not invalid_exchange_values
            and not _is_pointer_disabled(exchange_input_node)
            and not _is_pointer_disabled(exchange_button_node)
        )
        result["exchange"].update(
            {
                "pill_price": pill_price,
                "magic_pills": exchange_pills,
                "points": exchange_points,
                "max_count": exchange_max,
                "enabled": bool(exchange_enabled),
                "action_ready": bool(
                    exchange_enabled and exchange_pills > 0 and exchange_max > 0
                ),
                "note": "支持手动兑换魔力；一键炼造魔丸已整合到物品栏。",
            }
        )

        beach_area_node = _find_by_id(root, "beachArea")
        beach_status_node = _find_by_id(root, "beachStatus")
        beach_button_node = _find_by_id(root, "beachBtn")
        collect_button_node = _find_by_id(root, "collectAllTrashBtn")
        beach_status_text = _node_text(beach_status_node)
        beach_state_complete = all(
            node is not None
            for node in (
                beach_area_node,
                beach_status_node,
                beach_button_node,
                collect_button_node,
            )
        )
        entry_button_enabled = bool(
            beach_state_complete and not _is_pointer_disabled(beach_button_node)
        )
        collect_enabled = bool(
            beach_state_complete and not _is_pointer_disabled(collect_button_node)
        )
        has_trash = _beach_has_trash(
            beach_area_node,
            beach_status_text,
        )
        countdown_active = _has_countdown(
            beach_status_node,
            beach_status_text,
        )
        has_server_time = bool(
            raw_server_now is not None
            and _normalise_timestamp(raw_server_now, 0) > 0
        )
        has_last_beach_time = bool(
            raw_last_beach is not None and last_beach_time > 0
        )
        has_beach_interval = bool(
            raw_beach_interval is not None
            and _normalise_duration(raw_beach_interval, 0) > 0
        )
        has_beach_time_basis = bool(
            has_server_time
            and has_last_beach_time
            and has_beach_interval
        )
        calculated_beach_ts = (
            last_beach_time + beach_interval
            if has_beach_time_basis
            else 0
        )
        countdown = _countdown_seconds(beach_status_text)
        if has_beach_time_basis and calculated_beach_ts > server_now:
            next_ready_ts = calculated_beach_ts
        elif has_server_time and countdown_active and countdown > 0:
            next_ready_ts = server_now + countdown
        elif has_beach_time_basis:
            next_ready_ts = calculated_beach_ts
        else:
            next_ready_ts = 0
        timestamp_expired = bool(
            has_beach_time_basis
            and calculated_beach_ts <= server_now
        )
        can_enter = bool(
            entry_button_enabled
            and timestamp_expired
            and not countdown_active
        )
        beach_ready = bool(
            can_enter
            and not has_trash
        )
        result["beach"].update(
            {
                "ready": beach_ready,
                "can_enter": bool(can_enter),
                "can_collect": bool(collect_enabled or has_trash),
                "has_trash": bool(has_trash),
                "status_text": beach_status_text
                or ("可以进入清理" if beach_ready else "沙滩冷却中"),
                "next_ready_ts": next_ready_ts,
                "next_ready_time": _format_timestamp(next_ready_ts),
                "level_text": _current_value_text(source, "发种等级"),
                "hnr_text": _current_value_text(source, "HNR值"),
                "enter_button_text": _node_text(beach_button_node) or "清理沙滩",
                "collect_button_text": _node_text(collect_button_node) or "一键收集",
                "collect_enabled": bool(collect_enabled),
            }
        )

        result["inventory"] = parse_inventory(source, _raise_errors=True)
        result["recipes"] = parse_recipes(
            source,
            result["inventory"],
            _raise_errors=True,
        )

        inventory_grid_node = _find_by_id(root, "inventoryGrid")
        required_nodes = {
            "title": title_node,
            "points": nodes_by_key["points"],
            "bonusEarned": nodes_by_key["bonus_earned"],
            "magicPills": nodes_by_key["magic_pills"],
            "dailyBricks": daily_node,
            "brickFactory": factory_node,
            "factoryBrickCount": factory_count_node,
            "bagBrickCount": bag_count_node,
            "brickStatus": brick_status_node,
            "exchangeCount": exchange_input_node,
            "exchangeBtn": exchange_button_node,
            "beachArea": beach_area_node,
            "beachStatus": beach_status_node,
            "beachBtn": beach_button_node,
            "collectAllTrashBtn": collect_button_node,
            "inventoryGrid": inventory_grid_node,
        }
        missing_nodes = [
            name for name, node in required_nodes.items() if node is None
        ]
        validation_errors = []
        if missing_nodes:
            validation_errors.append(
                "missing required nodes: %s" % ", ".join(missing_nodes)
            )
        if invalid_brick_values:
            validation_errors.append(
                "invalid critical values: %s"
                % ", ".join(invalid_brick_values)
            )
        if invalid_exchange_values:
            validation_errors.append(
                "invalid critical values: %s"
                % ", ".join(invalid_exchange_values)
            )
        if validation_errors:
            result["parse_error"] = "; ".join(validation_errors)
            _disable_actions(result)
        else:
            result["parse_complete"] = True
            result["parse_error"] = ""
    except Exception as err:
        result["parse_error"] = "%s: %s" % (type(err).__name__, err)
        _disable_actions(result)

    return result


__all__ = ["parse_page", "parse_inventory", "parse_recipes"]
