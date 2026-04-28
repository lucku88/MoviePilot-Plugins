import os

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
        bbox = font.getbbox(sample)
        if bbox and bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            return True
    except Exception:
        pass
    try:
        mask = font.getmask(sample)
        if mask.getbbox() is not None:
            return True
    except Exception:
        pass
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
            if font_supports_text(font, text):
                if str(candidate) != str(font_path or ""):
                    logger.warning("文字渲染字体回退 | 文本=%s | 原字体=%s | 回退字体=%s", text, font_path, candidate)
                return font, candidate
            errors.append(f"{candidate}:glyph-missing")
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
    bbox = font.getbbox(text)
    left, top, right, bottom = bbox
    width = max(1, int(right - left))
    height = max(1, int(bottom - top))
    fill_rgba = _to_rgba(fill_color)

    patch = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch)
    draw.text((-left, -top), text, font=font, fill=fill_rgba)
    if patch.getbbox():
        return patch, (left, top)

    mask = font.getmask(text, mode="L")
    mask_bbox = mask.getbbox()
    if mask_bbox is None:
        return None, (left, top)

    alpha = Image.frombytes("L", mask.size, bytes(mask))
    if fill_rgba[3] < 255:
        alpha = alpha.point(lambda value: int(value * fill_rgba[3] / 255))
    glyph = Image.new("RGBA", mask.size, fill_rgba[:3] + (0,))
    glyph.putalpha(alpha)
    logger.warning("文字渲染走掩膜兜底 | 文本=%s | 字体=%s", text, getattr(font, "path", ""))
    return glyph, (left, top)


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
