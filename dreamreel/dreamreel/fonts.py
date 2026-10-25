"""Text in every script of India, shaped properly.

Blender draws letters one by one, which is fine for English but breaks the scripts of India: vowel
signs land in the wrong place, conjuncts fall apart, Urdu doesn't join. So subtitles and captions
with those scripts are drawn by Pillow, whose text layout (HarfBuzz, through libraqm) shapes them the
way a reader expects, with Google's Noto fonts (SIL Open Font License), downloaded once per script
into ~/.cache/dreamreel/fonts.
"""
import hashlib
import os
import urllib.request

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel")
FONTS = os.path.join(CACHE, "fonts")
NOTO = "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/{f}/hinted/ttf/{f}-{w}.ttf"

# Unicode block -> Noto family
BLOCKS = ((0x0900, 0x097F, "NotoSansDevanagari"), (0x0980, 0x09FF, "NotoSansBengali"),
          (0x0A00, 0x0A7F, "NotoSansGurmukhi"), (0x0A80, 0x0AFF, "NotoSansGujarati"),
          (0x0B00, 0x0B7F, "NotoSansOriya"), (0x0B80, 0x0BFF, "NotoSansTamil"),
          (0x0C00, 0x0C7F, "NotoSansTelugu"), (0x0C80, 0x0CFF, "NotoSansKannada"),
          (0x0D00, 0x0D7F, "NotoSansMalayalam"), (0x0600, 0x06FF, "NotoNastaliqUrdu"),
          (0x0750, 0x077F, "NotoNastaliqUrdu"), (0xA8E0, 0xA8FF, "NotoSansDevanagari"),
          (0x1CD0, 0x1CFF, "NotoSansDevanagari"))
LATIN = "NotoSans"
_warned = set()


def family_of(ch):
    c = ord(ch)
    for lo, hi, fam in BLOCKS:
        if lo <= c <= hi:
            return fam
    return None


def needs_shaping(text):
    """True when the text has a script Blender can't lay out."""
    return any(family_of(ch) for ch in text)


def font(family, weight="Regular"):
    """Path of a Noto font, downloaded once."""
    path = os.path.join(FONTS, f"{family}-{weight}.ttf")
    if not os.path.exists(path):
        os.makedirs(FONTS, exist_ok=True)
        req = urllib.request.Request(NOTO.format(f=family, w=weight), headers={"User-Agent": "dreamreel"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if data[:4] not in (b"\x00\x01\x00\x00", b"true", b"OTTO"):
            raise RuntimeError(f"the {family} font didn't download properly")
        tmp = f"{path}.{os.getpid()}.part"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    return path


def _runs(text):
    """Split text into (family, piece) runs; spaces and punctuation join the run they're in."""
    runs = []
    for ch in text:
        fam = family_of(ch) or (LATIN if ch.isalpha() else None)
        if fam is None and ch.isascii() and not ch.isspace() and not (runs and "Nastaliq" in runs[-1][0]):
            fam = LATIN         # digits and punctuation: not every script's font has them
        if runs and (fam is None or fam == runs[-1][0]):
            runs[-1][1] += ch
        elif fam is None:
            runs.append([LATIN, ch])
        else:
            runs.append([fam, ch])
    return [tuple(r) for r in runs]


def _wrap(text, fits):
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if cur and not fits(cand):
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines or [""]


def text_image(text, W, H, y=0.08, size=0.045, box=True, color=(1, 1, 1, 1)):
    """A transparent W x H picture with the text drawn like a subtitle (centred, `y` up from the
    bottom, in a dark box), or None if Pillow isn't installed. Cached by everything that shapes it."""
    try:
        from PIL import Image, ImageDraw, ImageFont, features
    except ImportError:
        if "pillow" not in _warned:
            _warned.add("pillow")
            print("[dreamreel] subtitles in Indian scripts need Pillow (pip install pillow); "
                  "they'll be drawn without proper shaping")
        return None
    key = hashlib.sha1(repr((text, W, H, y, size, box, tuple(color))).encode()).hexdigest()[:20]
    out = os.path.join(CACHE, "text", f"{key}.png")
    if os.path.exists(out):
        return out
    layout = ImageFont.Layout.RAQM if features.check("raqm") else ImageFont.Layout.BASIC
    px = max(8, int(size * H))
    fonts = {}

    def f(fam):
        if fam not in fonts:
            # Nastaliq sits tall: a little smaller keeps the line height even
            fonts[fam] = ImageFont.truetype(font(fam), int(px * (0.8 if "Nastaliq" in fam else 1.0)),
                                            layout_engine=layout)
        return fonts[fam]

    def width(line):
        return sum(f(fam).getlength(piece) for fam, piece in _runs(line))

    lines = _wrap(text, lambda s: width(s) <= 0.84 * W)
    line_h = int(px * 1.55)
    pad = int(0.012 * H) + int(px * 0.25)
    block_h = line_h * len(lines)
    bottom = H - int(y * H) if y < 0.5 else (H + block_h) // 2
    top = bottom - block_h
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rgba = tuple(int(255 * c) for c in color)
    if box:
        wmax = max(width(line) for line in lines)
        d.rectangle([W / 2 - wmax / 2 - pad, top - pad * 0.6, W / 2 + wmax / 2 + pad, bottom + pad * 0.4],
                    fill=(0, 0, 0, 140))
    for i, line in enumerate(lines):
        runs = _runs(line)
        if any("Nastaliq" in fam for fam, _ in runs) and not any(fam.startswith("NotoSans") and fam != LATIN
                                                                 for fam, _ in runs):
            runs = runs[::-1]       # Urdu reads right to left: its runs go from the right
        x = W / 2 - width(line) / 2
        base = top + i * line_h + int(px * 1.15)
        for fam, piece in runs:
            kw = {"direction": "rtl"} if "Nastaliq" in fam and layout == ImageFont.Layout.RAQM else {}
            d.text((x + 2, base + 2), piece, font=f(fam), fill=(0, 0, 0, 160), anchor="ls", **kw)   # shadow
            d.text((x, base), piece, font=f(fam), fill=rgba, anchor="ls", **kw)
            x += f(fam).getlength(piece, **kw)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = f"{out}.{os.getpid()}.part.png"
    im.save(tmp)
    os.replace(tmp, out)
    return out
