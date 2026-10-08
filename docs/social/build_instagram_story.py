from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from build_instagram_promo import (
    AMBER,
    BRIGHT_GREEN,
    FONT_BOLD,
    FONT_REGULAR,
    FONT_SEMIBOLD,
    GREEN,
    MUTED,
    SOCIAL_DIR,
    WHITE,
    cover,
    draw_brand_mark,
    font,
    paste_shadow,
    pill,
    rounded_crop,
)


ROOT = Path(__file__).resolve().parents[2]
STORY_SIZE = (1080, 1920)


def build_story() -> tuple[Path, Path]:
    background_path = SOCIAL_DIR / "assets" / "industrial-background.png"
    screenshot_path = ROOT / "docs" / "screenshots" / "overview-mobile.png"
    printer_path = ROOT / "frontend" / "public" / "machines" / "atlas-one.png"
    avatar_path = SOCIAL_DIR / "assets" / "github-profile-santosgus3dtech.png"
    github_mark_path = SOCIAL_DIR / "assets" / "github-mark-white.png"

    canvas = cover(Image.open(background_path).convert("RGB"), STORY_SIZE).convert("RGBA")
    canvas.alpha_composite(Image.new("RGBA", STORY_SIZE, (7, 15, 27, 60)))

    # Keep the central story safe area calm while retaining the generated setting.
    glow = Image.new("RGBA", STORY_SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((-240, 560, 980, 1630), fill=(24, 134, 75, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    canvas.alpha_composite(glow)

    overlay = Image.new("RGBA", STORY_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top content starts below the Instagram profile/header overlay safe zone.
    draw_brand_mark(overlay, (66, 252), 56)
    draw.text((140, 254), "MANUFACTURING", font=font(FONT_SEMIBOLD, 24), fill=WHITE)
    draw.text((140, 281), "KNOWLEDGE AGENT", font=font(FONT_SEMIBOLD, 24), fill=WHITE)
    pill(
        overlay,
        (806, 261),
        "OPEN SOURCE",
        label_font=font(FONT_SEMIBOLD, 15),
        fill=(255, 255, 255, 24),
        outline=(255, 255, 255, 52),
        dot=BRIGHT_GREEN,
        height=42,
    )

    headline = font(FONT_BOLD, 72)
    draw.text((66, 365), "EVIDENCE-GROUNDED AI", font=headline, fill=WHITE)
    draw.text((66, 448), "FOR ", font=headline, fill=WHITE)
    prefix_width = draw.textlength("FOR ", font=headline)
    draw.text((66 + prefix_width, 448), "3D", font=headline, fill=BRIGHT_GREEN)
    highlight_width = draw.textlength("3D", font=headline)
    draw.text((66 + prefix_width + highlight_width, 448), " PRINTING", font=headline, fill=WHITE)

    draw.text(
        (69, 548),
        "RAG + MCP in one operational workspace.",
        font=font(FONT_REGULAR, 29),
        fill=(232, 238, 244, 255),
    )

    feature_font = font(FONT_SEMIBOLD, 16)
    cursor_x = 68
    for label in ("INSPECTABLE SOURCES", "MACHINES", "QUOTES", "EVALUATIONS"):
        width = pill(
            overlay,
            (cursor_x, 610),
            label,
            label_font=feature_font,
            fill=(255, 255, 255, 18),
            outline=(255, 255, 255, 42),
            dot=GREEN,
            pad_x=15,
            height=40,
        )
        cursor_x += width + 10

    canvas.alpha_composite(overlay)

    # Preserve a verified crop that shows only the two FDM machines in the mobile UI.
    screenshot = Image.open(screenshot_path).convert("RGB")
    screenshot = screenshot.crop((0, 328, 390, 765))
    screenshot = screenshot.resize((590, 661), Image.Resampling.LANCZOS)
    screenshot = rounded_crop(screenshot, 19)
    card = Image.new("RGBA", (602, 673), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        (0, 0, 601, 672),
        radius=24,
        fill=(250, 252, 253, 255),
        outline=(255, 255, 255, 220),
        width=3,
    )
    card.alpha_composite(screenshot, (6, 6))
    card = card.rotate(-1.15, resample=Image.Resampling.BICUBIC, expand=True)
    paste_shadow(canvas, card, (64, 842), blur=30, opacity=170, offset=(0, 22))

    proof = Image.new("RGBA", STORY_SIZE, (0, 0, 0, 0))
    proof_draw = ImageDraw.Draw(proof)
    proof_draw.rounded_rectangle(
        (72, 835, 248, 877),
        radius=20,
        fill=(20, 32, 51, 245),
        outline=(255, 255, 255, 60),
        width=1,
    )
    proof_draw.ellipse((88, 851, 96, 859), fill=BRIGHT_GREEN)
    proof_draw.text((108, 844), "FDM DASHBOARD", font=font(FONT_SEMIBOLD, 14), fill=WHITE)
    canvas.alpha_composite(proof)

    printer = Image.open(printer_path).convert("RGBA")
    alpha_bbox = printer.getchannel("A").getbbox()
    if alpha_bbox:
        printer = printer.crop(alpha_bbox)
    target_h = 520
    printer = printer.resize(
        (round(printer.width * target_h / printer.height), target_h),
        Image.Resampling.LANCZOS,
    )
    paste_shadow(canvas, printer, (560, 1020), blur=28, opacity=165, offset=(-8, 19))

    # CTA and disclosure end above the reply/link controls at the bottom of Stories.
    cta = Image.new("RGBA", STORY_SIZE, (0, 0, 0, 0))
    cta_draw = ImageDraw.Draw(cta)
    cta_draw.rounded_rectangle(
        (66, 678, 1014, 786),
        radius=20,
        fill=(13, 111, 59, 238),
        outline=(80, 202, 126, 155),
        width=2,
    )
    github_mark = Image.open(github_mark_path).convert("RGBA").resize((44, 44), Image.Resampling.LANCZOS)
    cta.alpha_composite(github_mark, (84, 710))

    avatar = Image.open(avatar_path).convert("RGB").resize((62, 62), Image.Resampling.LANCZOS)
    avatar_mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(avatar_mask).ellipse((0, 0, 61, 61), fill=255)
    avatar_rgba = avatar.convert("RGBA")
    avatar_rgba.putalpha(avatar_mask)
    avatar_lockup = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    avatar_draw = ImageDraw.Draw(avatar_lockup)
    avatar_draw.ellipse((0, 0, 69, 69), fill=(255, 255, 255, 235))
    avatar_draw.ellipse((3, 3, 66, 66), fill=(24, 134, 75, 255))
    avatar_lockup.alpha_composite(avatar_rgba, (4, 4))
    cta.alpha_composite(avatar_lockup, (132, 697))

    cta_draw.text(
        (218, 695),
        "@SANTOSGUS3DTECH · EXPLORE ON GITHUB",
        font=font(FONT_SEMIBOLD, 15),
        fill=(208, 244, 220, 255),
    )
    cta_draw.text(
        (218, 724),
        "github.com/santosgus3dtech/manufacturing-knowledge-agent",
        font=font(FONT_SEMIBOLD, 19),
        fill=WHITE,
    )
    cta_draw.text((974, 716), "→", font=font(FONT_SEMIBOLD, 28), fill=WHITE, anchor="mm")
    cta_draw.line((66, 1628, 1014, 1628), fill=(255, 255, 255, 44), width=1)
    cta_draw.ellipse((67, 1652, 77, 1662), fill=AMBER)
    cta_draw.text(
        (91, 1644),
        "PORTFOLIO DEMO · SYNTHETIC DATA",
        font=font(FONT_SEMIBOLD, 15),
        fill=MUTED,
    )
    cta_draw.text(
        (1012, 1644),
        "PYTHON · FASTAPI · REACT · MCP",
        font=font(FONT_SEMIBOLD, 15),
        fill=WHITE,
        anchor="ra",
    )
    canvas.alpha_composite(cta)

    png_path = SOCIAL_DIR / "instagram-story-manufacturing-knowledge-agent.png"
    jpg_path = SOCIAL_DIR / "instagram-story-manufacturing-knowledge-agent.jpg"
    canvas.convert("RGB").save(png_path, format="PNG", optimize=True)
    canvas.convert("RGB").save(jpg_path, format="JPEG", quality=95, subsampling=0, optimize=True)
    return png_path, jpg_path


if __name__ == "__main__":
    outputs = build_story()
    for output in outputs:
        print(output)
