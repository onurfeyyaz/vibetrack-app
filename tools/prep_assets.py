#!/usr/bin/env python3
"""Gorselleri hazirlar: ekran goruntuleri (webp), ikonlar, OG kartlari.

    python3 tools/prep_assets.py [SHOTS_DIR]

SHOTS_DIR varsayilan: ~/Projects/XCodeProjects/VibeTrack/build/store-shots
(VibeTrack'te `SIM="iPhone 17 Pro" LANGS="en tr" THEMES="dark light"
scripts/store-capture.sh` ile uretilir; klasorler {en,tr}-{dark,light}).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
VT = Path.home() / "Projects/XCodeProjects/VibeTrack"
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else VT / "build/store-shots"
ICON = VT / "VibeTrack/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
WANT = ["01", "02", "03", "04", "05", "07"]
WIDTHS = (400, 760)


def shots():
    for lang in ("en", "tr"):
        for theme in ("dark", "light"):
            src = SHOTS / f"{lang}-{theme}"
            dst = ROOT / "assets/shots" / lang / theme
            dst.mkdir(parents=True, exist_ok=True)
            for n in WANT:
                found = sorted(src.glob(f"{n}-*.png"))
                if not found:
                    sys.exit(f"eksik: {src}/{n}-*.png")
                im = Image.open(found[0]).convert("RGB")
                for w in WIDTHS:
                    h = round(im.height * w / im.width)
                    im.resize((w, h), Image.LANCZOS).save(dst / f"{found[0].stem}-{w}.webp", "WEBP", quality=80, method=6)
    print("✓ ekranlar")


def icons():
    out = ROOT / "assets/img"
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(ICON).convert("RGBA")
    for s in (64, 180, 512):
        im.resize((s, s), Image.LANCZOS).save(out / f"icon-{s}.png", optimize=True)
    print("✓ ikonlar")


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    im = im.convert("RGBA")
    im.putalpha(m)
    return im


OG = {
    "en": ("149 ways to say", "how you are.", "Mood tracker for iPhone · Free"),
    "tr": ("149 yolla söyle:", "nasılsın?", "iPhone için duygu takibi · Ücretsiz"),
}


def og():
    W, H = 1200, 630
    sans = "/System/Library/Fonts/SFNSRounded.ttf"
    serif = "/System/Library/Fonts/NewYorkItalic.ttf"
    for lang, (l1, l2, sub) in OG.items():
        bg = Image.new("RGB", (W, H), (15, 14, 23))
        glow = Image.new("RGB", (W, H), (15, 14, 23))
        d = ImageDraw.Draw(glow)
        d.ellipse((620, -180, 1320, 520), fill=(124, 92, 255))
        d.ellipse((-200, 330, 520, 900), fill=(255, 122, 154))
        d.ellipse((760, 380, 1300, 860), fill=(64, 200, 224))
        bg = Image.blend(bg, glow.filter(ImageFilter.GaussianBlur(140)), 0.55)
        dr = ImageDraw.Draw(bg)

        icon = rounded(Image.open(ICON).resize((96, 96), Image.LANCZOS), 22)
        bg.paste(icon, (72, 72), icon)
        dr.text((186, 98), "Vibe Track", font=ImageFont.truetype(sans, 40), fill=(255, 255, 255))
        dr.text((72, 230), l1, font=ImageFont.truetype(sans, 76), fill=(255, 255, 255))
        dr.text((72, 322), l2, font=ImageFont.truetype(serif, 84), fill=(196, 182, 255))
        dr.text((72, 496), sub, font=ImageFont.truetype(sans, 32), fill=(200, 196, 220))

        shot = sorted((SHOTS / f"{lang}-dark").glob("01-*.png"))[0]
        ph = Image.open(shot).convert("RGB")
        pw = 300
        ph = ph.resize((pw, round(ph.height * pw / ph.width)), Image.LANCZOS)
        frame = Image.new("RGB", (pw + 20, ph.height + 20), (40, 38, 56))
        frame = rounded(frame, 56)
        ph = rounded(ph, 46)
        frame.paste(ph, (10, 10), ph)
        bg.paste(frame, (830, 70), frame)
        bg.save(ROOT / f"assets/img/og-{lang}.png", optimize=True)
    print("✓ og")


if __name__ == "__main__":
    icons()
    shots()
    og()
