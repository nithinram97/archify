"""Time and easing.

You always think in **seconds**; the kit converts to frames. Easing names you can use anywhere:

    "smooth"      gentle start and stop (default)
    "linear"      constant speed
    "ease_in"     starts slow, ends fast         "ease_out"    starts fast, ends slow
    "ease_in_out" slow - fast - slow (stronger than smooth)
    "back"        overshoots a little, then settles
    "bounce"      bounces at the end             "elastic"     springy wobble at the end
    "snap"        holds, then jumps (a hard cut / on-off switch)
"""

EASINGS = {
    "smooth": ("BEZIER", "AUTO"),
    "linear": ("LINEAR", "AUTO"),
    "ease_in": ("CUBIC", "EASE_IN"),
    "ease_out": ("CUBIC", "EASE_OUT"),
    "ease_in_out": ("QUINT", "EASE_IN_OUT"),
    "back": ("BACK", "EASE_OUT"),
    "bounce": ("BOUNCE", "EASE_OUT"),
    "elastic": ("ELASTIC", "EASE_OUT"),
    "snap": ("CONSTANT", "AUTO"),
}


def easing(name):
    """Map an easing name to Blender's (interpolation, easing) pair."""
    try:
        return EASINGS[name]
    except KeyError:
        raise ValueError(f"Unknown ease {name!r}; use one of {sorted(EASINGS)}") from None


def smoothstep(a, b, x):
    """0 before a, 1 after b, smooth in between (handy for your own maths)."""
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


class Clock:
    """Converts seconds to frames for one movie. Frame 1 is t = 0."""

    def __init__(self, fps=24):
        self.fps = fps

    def frame(self, seconds):
        return int(round(seconds * self.fps)) + 1

    def seconds(self, frame):
        return (frame - 1) / self.fps


CLOCK = Clock()  # replaced by Movie(fps=...)
