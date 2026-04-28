import os
import math

from PIL import Image, ImageDraw, ImageFont

from app.log import logger


ZH_FONT_FALLBACKS = [
    r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    r"/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    r"/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    r"/usr/share/fonts/truetype/arphic/ukai.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"/System/Library/Fonts/PingFang.ttc",
    r"/System/Library/Fonts/Hiragino Sans GB.ttc",
]

EN_FONT_FALLBACKS = [
    r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    r"/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"/System/Library/Fonts/Supplemental/Arial.ttf",
]


def contains_cjk(text):
    for char in str(text or ""):
        code = ord(char)
        if 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF or 0x3040 <= code <= 0x30FF or 0xAC00 <= code <= 0xD7AF:
            return True
    return False


def font_supports_text(font, text):
    sample = str(text or "").strip()
    if not sample:
        return True
    try:
        patch, _ = _build_text_patch(sample, font, (255, 255, 255, 255))
        return bool(patch and patch.getbbox())
    except Exception:
        return False


def resolve_font_path(font_path, text):
    candidates = []
    primary = str(font_path or "").strip()
    if primary:
        candidates.append(primary)
    fallbacks = ZH_FONT_FALLBACKS if contains_cjk(text) else EN_FONT_FALLBACKS
    for candidate in fallbacks:
        if candidate and candidate not in candidates and os.path.exists(candidate):
            candidates.append(candidate)
    return candidates


def load_font_with_fallback(font_path, text, font_size):
    errors = []
    font_size = int(max(1, round(float(font_size))))
    for candidate in resolve_font_path(font_path, text):
        try:
            font = ImageFont.truetype(candidate, font_size)
            return font, candidate
        except Exception as err:
            errors.append(f"{candidate}:{err}")
    logger.warning("文字渲染字体不可用 | 文本=%s | 原字体=%s | 错误=%s", text, font_path, "; ".join(errors[:5]))
    return ImageFont.load_default(), ""


def _to_rgba(fill_color):
    if len(fill_color) == 4:
        return tuple(int(v) for v in fill_color)
    if len(fill_color) == 3:
        return (int(fill_color[0]), int(fill_color[1]), int(fill_color[2]), 255)
    raise ValueError("fill_color 格式不正确")


def _build_text_patch(text, font, fill_color):
    return _build_outline_text_patch(text, font, fill_color)


def _build_outline_text_patch(text, font, fill_color):
    try:
        from fontTools.pens.basePen import BasePen
        from fontTools.ttLib import TTFont
    except Exception as err:
        logger.warning("文字轮廓渲染不可用 | 文本=%s | 错误=%s", text, err)
        return None, (0, 0)

    font_path = str(getattr(font, "path", "") or "").strip()
    if not font_path or not os.path.exists(font_path):
        return None, (0, 0)

    class _FlattenPen(BasePen):
        def __init__(self, glyph_set):
            super().__init__(glyph_set)
            self.contours = []
            self.current = []

        def _moveTo(self, p0):
            self._finish_contour()
            self.current = [p0]

        def _lineTo(self, p1):
            self.current.append(p1)

        def _qCurveToOne(self, p1, p2):
            p0 = self.current[-1]
            for step in range(1, 9):
                t = step / 8.0
                x = (1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
                y = (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
                self.current.append((x, y))

        def _curveToOne(self, p1, p2, p3):
            p0 = self.current[-1]
            for step in range(1, 11):
                t = step / 10.0
                mt = 1 - t
                x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
                y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
                self.current.append((x, y))

        def _closePath(self):
            self._finish_contour()

        def _endPath(self):
            self._finish_contour()

        def _finish_contour(self):
            if len(self.current) >= 3:
                self.contours.append(self.current)
            self.current = []

    try:
        font_number = int(getattr(font, "index", 0) or 0)
        ttfont = TTFont(font_path, fontNumber=font_number)
        cmap = ttfont.getBestCmap() or {}
        glyph_set = ttfont.getGlyphSet()
        hmtx = ttfont["hmtx"].metrics
        units_per_em = float(ttfont["head"].unitsPerEm)
        ascent = float(ttfont["hhea"].ascent)
        descent = float(ttfont["hhea"].descent)
        size = float(getattr(font, "size", 24) or 24)
        scale = size / units_per_em

        contours = []
        cursor = 0.0
        for char in str(text):
            glyph_name = cmap.get(ord(char))
            if not glyph_name:
                cursor += size * 0.35
                continue
            pen = _FlattenPen(glyph_set)
            glyph_set[glyph_name].draw(pen)
            advance_width = hmtx.get(glyph_name, (units_per_em * 0.5, 0))[0]
            for contour in pen.contours:
                points = [
                    (
                        cursor + x * scale,
                        (ascent - y) * scale,
                    )
                    for x, y in contour
                ]
                contours.append(points)
            cursor += advance_width * scale

        if not contours:
            return None, (0, 0)

        width = max(1, int(math.ceil(max(cursor, max(point[0] for contour in contours for point in contour) + 2))))
        height = max(1, int(math.ceil((ascent - descent) * scale + 2)))
        alpha = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(alpha)

        sorted_contours = sorted(contours, key=lambda contour: abs(_polygon_area(contour)), reverse=True)
        for index, contour in enumerate(sorted_contours):
            point = contour[0]
            parent_count = sum(
                1 for parent in sorted_contours[:index]
                if _point_in_polygon(point, parent)
            )
            fill = 0 if parent_count % 2 else 255
            draw.polygon([(int(round(x)), int(round(y))) for x, y in contour], fill=fill)

        fill_rgba = _to_rgba(fill_color)
        if fill_rgba[3] < 255:
            alpha = alpha.point(lambda value: int(value * fill_rgba[3] / 255))
        glyph = Image.new("RGBA", (width, height), fill_rgba[:3] + (0,))
        glyph.putalpha(alpha)
        glyph_bbox = glyph.getbbox()
        if not glyph_bbox:
            return None, (0, 0)
        return glyph.crop(glyph_bbox), (glyph_bbox[0], glyph_bbox[1])
    except Exception as err:
        logger.warning("文字轮廓渲染失败 | 文本=%s | 字体=%s | 错误=%s", text, font_path, err)
        return None, (0, 0)


def _polygon_area(points):
    area = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        area += point[0] * next_point[1] - next_point[0] * point[1]
    return area / 2.0


def _point_in_polygon(point, polygon):
    x, y = point
    inside = False
    previous_x, previous_y = polygon[-1]
    for current_x, current_y in polygon:
        intersects = (current_y > y) != (previous_y > y)
        if intersects:
            x_at_y = (previous_x - current_x) * (y - current_y) / ((previous_y - current_y) or 1e-9) + current_x
            if x < x_at_y:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def draw_text_patch(image, text, position, font, fill_color):
    text = str(text or "")
    if not text:
        return image
    patch, offset = _build_text_patch(text, font, fill_color)
    if patch is None:
        return image
    x = int(round(float(position[0]) + offset[0]))
    y = int(round(float(position[1]) + offset[1]))
    image.paste(patch, (x, y), patch)
    return image
