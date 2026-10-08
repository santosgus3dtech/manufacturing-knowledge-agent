from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOCIAL_DIR = Path(__file__).resolve().parent

CANVAS = (1080, 1350)
NAVY = "#142033"
GREEN = "#18864B"
BRIGHT_GREEN = "#36B657"
AMBER = "#DC9300"
WHITE = "#FFFFFF"
MUTED = "#B8C4D2"

FONT_REGULAR = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_SEMIBOLD = Path(r"C:\Windows\Fonts\seguisb.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def rounded_crop(image: Image.Image, radius: int) -> Image.Image:
    result = image.convert("RGBA")
    mask = Image.new("L", result.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, result.width - 1, result.height - 1),
        radius=radius,
        fill=255,
    )
    result.putalpha(mask)
    return result


def paste_shadow(
    canvas: Image.Image,
    item: Image.Image,
    xy: tuple[int, int],
    *,
    blur: int = 22,
    opacity: int = 125,
    offset: tuple[int, int] = (0, 16),
) -> None:
    alpha = item.getchannel("A")
    shadow_mask = alpha.filter(ImageFilter.GaussianBlur(blur))
    shadow = Image.new("RGBA", item.size, (0, 0, 0, opacity))
    shadow.putalpha(shadow_mask.point(lambda value: value * opacity // 255))
    canvas.alpha_composite(shadow, (xy[0] + offset[0], xy[1] + offset[1]))
    canvas.alpha_composite(item, xy)


def draw_brand_mark(layer: Image.Image, xy: tuple[int, int], size: int = 54) -> None:
    x, y = xy
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (x, y, x + size, y + size),
        radius=11,
        fill=(20, 32, 51, 242),
        outline=(255, 255, 255, 50),
        width=1,
    )
    cx = x + size / 2
    top = y + 11
    mid = y + 25
    bottom = y + 44
    left = x + 12
    right = x + 42
    draw.line((cx, top, right, y + 18, cx, mid, left, y + 18, cx, top), fill=WHITE, width=3)
    draw.line((left, y + 18, left, y + 36, cx, bottom, cx, mid), fill=WHITE, width=3)
    draw.line((right, y + 18, right, y + 36, cx, bottom), fill=WHITE, width=3)
    draw.ellipse((x + 38, y + 9, x + 49, y + 20), fill=BRIGHT_GREEN)


def pill(
    layer: Image.Image,
    xy: tuple[int, int],
    label: str,
    *,
    label_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    dot: str | None = None,
    pad_x: int = 18,
    height: int = 44,
) -> int:
    draw = ImageDraw.Draw(layer)
    bbox = draw.textbbox((0, 0), label, font=label_font)
    text_w = bbox[2] - bbox[0]
    dot_space = 19 if dot else 0
    width = text_w + pad_x * 2 + dot_space
    x, y = xy
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=height // 2,
        fill=fill,
        outline=outline,
        width=1,
    )
    text_x = x + pad_x
    if dot:
        draw.ellipse((text_x, y + height // 2 - 4, text_x + 8, y + height // 2 + 4), fill=dot)
        text_x += dot_space
    text_y = y + (height - (bbox[3] - bbox[1])) // 2 - bbox[1] - 1
    draw.text((text_x, text_y), label, font=label_font, fill=WHITE)
    return width


def draw_repo_icon(draw: ImageDraw.ImageDraw, xy: tuple[int, int]) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + 48, y + 48), radius=12, fill=(255, 255, 255, 42))
    draw.line((x + 14, y + 17, x + 24, y + 11, x + 34, y + 17), fill=WHITE, width=3)
    draw.line((x + 14, y + 17, x + 14, y + 31, x + 24, y + 37, x + 34, y + 31, x + 34, y + 17), fill=WHITE, width=3)
    draw.ellipse((x + 20, y + 20, x + 28, y + 28), fill=BRIGHT_GREEN)


def build() -> tuple[Path, Path]:
    background_path = SOCIAL_DIR / "assets" / "industrial-background.png"
    screenshot_path = ROOT / "docs" / "screenshots" / "overview-desktop.png"
    printer_path = ROOT / "frontend" / "public" / "machines" / "northstar-cell.png"

    canvas = cover(Image.open(background_path).convert("RGB"), CANVAS).convert("RGBA")

    # A restrained navy treatment keeps the generated plate on-brand and copy-safe.
    tint = Image.new("RGBA", CANVAS, (8, 17, 29, 46))
    canvas.alpha_composite(tint)
    vignette = Image.new("L", CANVAS, 0)
    vignette_draw = ImageDraw.Draw(vignette)
    for index in range(180):
        alpha = round(index / 179 * 145)
        vignette_draw.rectangle((index, index, 1079 - index, 1349 - index), outline=alpha, width=1)
    vignette = vignette.filter(ImageFilter.GaussianBlur(36))
    dark_edge = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    dark_edge.putalpha(vignette)
    canvas.alpha_composite(dark_edge)

    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Header and product lockup.
    draw_brand_mark(overlay, (66, 58), 56)
    draw.text((140, 60), "MANUFACTURING", font=font(FONT_SEMIBOLD, 24), fill=WHITE)
    draw.text((140, 87), "KNOWLEDGE AGENT", font=font(FONT_SEMIBOLD, 24), fill=WHITE)
    pill(
        overlay,
        (806, 67),
        "OPEN SOURCE",
        label_font=font(FONT_SEMIBOLD, 15),
        fill=(255, 255, 255, 24),
        outline=(255, 255, 255, 52),
        dot=BRIGHT_GREEN,
        height=42,
    )

    # Headline with deliberate, deterministic line breaks.
    headline = font(FONT_BOLD, 72)
    draw.text((66, 157), "IA COM EVIDÊNCIAS", font=headline, fill=WHITE)
    draw.text((66, 238), "PARA IMPRESSÃO", font=headline, fill=WHITE)
    first_width = draw.textlength("PARA IMPRESSÃO ", font=headline)
    draw.text((66 + first_width, 238), "3D", font=headline, fill=BRIGHT_GREEN)

    draw.text(
        (69, 337),
        "RAG + MCP em um workspace operacional.",
        font=font(FONT_REGULAR, 29),
        fill=(232, 238, 244, 255),
    )

    feature_font = font(FONT_SEMIBOLD, 14)
    cursor_x = 68
    for label in ("FONTES INSPECIONÁVEIS", "MÁQUINAS", "ORÇAMENTOS", "AVALIAÇÕES"):
        width = pill(
            overlay,
            (cursor_x, 393),
            label,
            label_font=feature_font,
            fill=(255, 255, 255, 18),
            outline=(255, 255, 255, 42),
            dot=GREEN,
            pad_x=15,
            height=40,
        )
        cursor_x += width + 10

    # GitHub call-to-action.
    cta_box = (66, 461, 1014, 554)
    draw.rounded_rectangle(cta_box, radius=18, fill=(13, 111, 59, 234), outline=(80, 202, 126, 150), width=2)
    draw_repo_icon(draw, (85, 483))
    draw.text((151, 477), "EXPLORE NO GITHUB", font=font(FONT_SEMIBOLD, 16), fill=(208, 244, 220, 255))
    draw.text(
        (151, 504),
        "github.com/santosgus3dtech/manufacturing-knowledge-agent",
        font=font(FONT_SEMIBOLD, 20),
        fill=WHITE,
    )
    draw.text((974, 490), "→", font=font(FONT_SEMIBOLD, 28), fill=WHITE, anchor="mm")

    canvas.alpha_composite(overlay)

    # Use the verified application capture directly; image generation never rewrites the UI.
    screenshot = Image.open(screenshot_path).convert("RGB")
    screenshot = screenshot.resize((900, 600), Image.Resampling.LANCZOS)
    screenshot = rounded_crop(screenshot, 19)
    card = Image.new("RGBA", (912, 612), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle((0, 0, 911, 611), radius=24, fill=(250, 252, 253, 255), outline=(255, 255, 255, 220), width=3)
    card.alpha_composite(screenshot, (6, 6))
    card = card.rotate(-1.35, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, card, (51, 586), blur=30, opacity=165, offset=(0, 20))

    # Small proof label attached to the real screenshot.
    proof = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    proof_draw = ImageDraw.Draw(proof)
    proof_draw.rounded_rectangle((72, 581, 270, 623), radius=20, fill=(20, 32, 51, 245), outline=(255, 255, 255, 60), width=1)
    proof_draw.ellipse((88, 597, 96, 605), fill=BRIGHT_GREEN)
    proof_draw.text((108, 590), "INTERFACE REAL", font=font(FONT_SEMIBOLD, 14), fill=WHITE)
    canvas.alpha_composite(proof)

    # The repository's own transparent printer asset stays recognizable and unchanged.
    printer = Image.open(printer_path).convert("RGBA")
    alpha_bbox = printer.getchannel("A").getbbox()
    if alpha_bbox:
        printer = printer.crop(alpha_bbox)
    target_h = 425
    printer = printer.resize((round(printer.width * target_h / printer.height), target_h), Image.Resampling.LANCZOS)
    paste_shadow(canvas, printer, (682, 853), blur=26, opacity=160, offset=(-8, 18))

    # Footer disclosure and stack — factual, compact, and legible at feed size.
    footer = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    footer_draw = ImageDraw.Draw(footer)
    footer_draw.rectangle((0, 1286, 1080, 1350), fill=(8, 18, 31, 232))
    footer_draw.line((66, 1286, 1014, 1286), fill=(255, 255, 255, 44), width=1)
    footer_draw.ellipse((67, 1310, 77, 1320), fill=AMBER)
    footer_draw.text((91, 1302), "DEMO DE PORTFÓLIO · DADOS SINTÉTICOS", font=font(FONT_SEMIBOLD, 15), fill=MUTED)
    footer_draw.text((1012, 1302), "PYTHON · FASTAPI · REACT · MCP", font=font(FONT_SEMIBOLD, 15), fill=WHITE, anchor="ra")
    canvas.alpha_composite(footer)

    png_path = SOCIAL_DIR / "instagram-manufacturing-knowledge-agent.png"
    jpg_path = SOCIAL_DIR / "instagram-manufacturing-knowledge-agent.jpg"
    canvas.convert("RGB").save(png_path, format="PNG", optimize=True)
    canvas.convert("RGB").save(jpg_path, format="JPEG", quality=95, subsampling=0, optimize=True)
    return png_path, jpg_path


if __name__ == "__main__":
    outputs = build()
    for output in outputs:
        print(output)
