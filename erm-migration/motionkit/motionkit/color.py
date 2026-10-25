"""Colours and palettes.

Anywhere the kit asks for a colour you can pass:
  * a hex string: "#ec4f8f" or "ec4f8f"
  * a palette name: "pink", "indigo", "white", ... (see `Palette`)
  * an RGB or RGBA tuple of 0-1 floats (already linear)
"""
from dataclasses import dataclass, field


def hex_to_linear(h):
    """'#rrggbb' -> linear RGB tuple (what Blender's colour sockets expect)."""
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


@dataclass
class Palette:
    """A named set of colours. Pass `palette=` to `Movie` and then refer to colours by name."""
    name: str
    colors: dict = field(default_factory=dict)

    def __getitem__(self, key):
        return self.colors[key]


NEON = Palette("neon", {
    "pink": "#ec4f8f", "indigo": "#6366f1", "cyan": "#7dd3fc", "white": "#f8fafc", "muted": "#94a3b8",
    "night": "#070b16", "gold": "#fbbf24", "green": "#34d399", "red": "#f43f5e", "black": "#000000",
})
CORPORATE = Palette("corporate", {
    "navy": "#00205b", "pink": "#c8326c", "blue": "#0085ca", "purple": "#5f3a8f", "white": "#ffffff",
    "light": "#eef1f7", "muted": "#4a5568", "night": "#00143a", "black": "#000000", "gold": "#d2691e",
})
PALETTES = {"neon": NEON, "corporate": CORPORATE}

_active = NEON


def use_palette(palette):
    """Make `palette` (a Palette or a name from PALETTES) the one colour names resolve against."""
    global _active
    _active = PALETTES[palette] if isinstance(palette, str) else palette


def rgba(color, alpha=1.0):
    """Resolve any colour spec to a linear RGBA tuple."""
    if isinstance(color, (tuple, list)):
        return tuple(color) + ((alpha,) if len(color) == 3 else ())
    if not color.startswith("#") and color in _active.colors:
        color = _active.colors[color]
    if not color.startswith("#"):
        try:
            int(color, 16)
            assert len(color) == 6
        except (ValueError, AssertionError):
            raise ValueError(f"Unknown colour {color!r}: use a hex value or one of {sorted(_active.colors)}") from None
    return (*hex_to_linear(color), alpha)
