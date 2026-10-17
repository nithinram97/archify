"""Editing: how scenes join (transitions), effects on the picture (fades, flashes), and the film's edit list.

Transitions happen in the edit, so changing one never re-renders a scene. A scene says how it comes in:

    # scenes/020_gran.toml
    transition = "dissolve"          # cut, fade, dissolve, wipe, iris, clock, push, whip, zoom, flash
    transition_duration = 1.0
    transition_color = "black"       # fade, flash
    transition_direction = "left"    # wipe, push, whip: left, right, up, down; iris: in, out

`film.toml` can override that and do more, with an edit list instead of a plain `scenes` list:

    [[edit]]
    scene = "010_kitchen"
    to = 8.0                          # seconds into the scene: cross-cutting, trims
    [[edit]]
    scene = "020_street"
    to = 6.0
    transition = "whip"
    [[edit]]
    scene = "010_kitchen"
    from = 8.0                        # back to the kitchen where we left it
    audio = "l"                       # l: the previous clip's sound runs on; j: this clip's sound starts early
    audio_seconds = 0.8
    [[edit]]
    split = ["030_her", "040_him"]    # split screen
    layout = "side_by_side"           # or "top_bottom"

Transitions and screen effects are classes, so new ones can be added:

    class Ripple(dr.Transition):
        overlap = True
        def apply(self, ed, a, b, start, frames, **p):
            ed.fade(b, start, start + frames, 0, 1)
            ed.move(b, start, start + frames, offset=(0, 40), to=(0, 0))
"""

from . import look
from .plugins import Param, Plugin


class Clip:
    """A piece of the film on the timeline: a scene (or part of one), a title card or a split screen."""

    def __init__(self, kind, start, length, strips, meta=None, from_s=0.0, channel=2):
        self.kind, self.start, self.length, self.strips = kind, start, length, strips
        self.meta, self.from_s, self.channel = meta, from_s, channel

    @property
    def end(self):
        return self.start + self.length

    @property
    def strip(self):
        return self.strips[0]


class Editor:
    """A thin layer over Blender's video sequencer that transitions and effects use."""

    def __init__(self, scene, fps):
        self.sc = scene
        self.fps = fps
        self.strips = scene.sequence_editor_create().strips
        self.W, self.H = scene.render.resolution_x, scene.render.resolution_y
        self.top = 20         # channels above this are overlays (effects, text)

    def frames(self, seconds):
        return max(1, int(round(seconds * self.fps)))

    def color(self, f0, f1, color, channel=1, alpha=1.0):
        st = self.strips.new_effect(name="color", type="COLOR", channel=channel, frame_start=int(f0),
                                    length=max(1, int(f1 - f0)))
        st.color = look.rgb(color)
        st.blend_type = "ALPHA_OVER"
        st.blend_alpha = alpha
        return st

    def key(self, strip, prop, frame, value, path_obj=None):
        obj = path_obj or strip
        setattr(obj, prop, value)
        obj.keyframe_insert(prop, frame=frame)

    def fade(self, strip, f0, f1, a0, a1):
        """Animate a strip's opacity from a0 at frame f0 to a1 at f1."""
        self.key(strip, "blend_alpha", f0, a0)
        self.key(strip, "blend_alpha", f1, a1)

    def move(self, strip, f0, f1, offset=(0, 0), to=(0, 0), scale=None, scale_to=None):
        """Animate a strip's position (pixels) and optionally its scale."""
        tr = strip.transform
        for f, (x, y) in ((f0, offset), (f1, to)):
            tr.offset_x, tr.offset_y = x, y
            tr.keyframe_insert("offset_x", frame=f)
            tr.keyframe_insert("offset_y", frame=f)
        if scale is not None:
            for f, s in ((f0, scale), (f1, scale_to if scale_to is not None else 1.0)):
                tr.scale_x = tr.scale_y = s
                tr.keyframe_insert("scale_x", frame=f)
                tr.keyframe_insert("scale_y", frame=f)

    def wipe(self, a, b, f0, frames, kind="SINGLE", angle=0.0, direction="OUT", blur=0.08):
        st = self.strips.new_effect(name="wipe", type="WIPE", channel=max(a.channel, b.channel) + 1,
                                    frame_start=int(f0), length=int(frames), input1=a, input2=b)
        st.transition_type = kind
        st.angle = angle
        st.direction = direction
        st.blur_width = blur
        if hasattr(st, "use_default_fade"):   # drive the progress ourselves: linear, exactly over `frames`
            st.use_default_fade = False
            st.effect_fader = 0.0
            st.keyframe_insert("effect_fader", frame=int(f0))
            st.effect_fader = 1.0
            st.keyframe_insert("effect_fader", frame=int(f0 + frames))
            for fc in _strip_fcurves(self.sc, st, "effect_fader"):
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"
        return st

    def text(self, content, f0, f1, channel, y=0.08, size=0.045, box=True, color=(1, 1, 1, 1)):
        from . import fonts
        if fonts.needs_shaping(content):        # Indian scripts: drawn by Pillow, shaped (fonts.py)
            try:
                png = fonts.text_image(content, self.W, self.H, y, size, box, tuple(color))
            except Exception as e:
                print(f"[dreamreel] couldn't draw a subtitle in its script ({e}); drawing it plainly")
                png = None
            if png:
                st = self.strips.new_image(name="text", filepath=png, channel=channel, frame_start=int(f0))
                st.frame_final_duration = max(1, int(f1 - f0))
                st.blend_type = "ALPHA_OVER"
                return st
        st = self.strips.new_effect(name="text", type="TEXT", channel=channel, frame_start=int(f0),
                                    length=max(1, int(f1 - f0)))
        st.text = content
        st.font_size = int(size * self.H)
        st.location = (0.5, y)
        st.anchor_x, st.anchor_y = "CENTER", "BOTTOM" if y < 0.5 else "CENTER"
        st.color = color
        if hasattr(st, "use_shadow"):
            st.use_shadow = True
        if box and hasattr(st, "use_box"):
            st.use_box = True
            st.box_color = (0, 0, 0, 0.55)
            if hasattr(st, "box_margin"):
                st.box_margin = 0.012
        return st


def _strip_fcurves(scene, strip, prop):
    from .timewarp import fcurves_of
    path = f'{strip.path_from_id()}.{prop}'
    return [fc for fc in fcurves_of(scene.animation_data.action if scene.animation_data else None)
            if fc.data_path == path]


# ---------------------------------------------------------------------- transitions
class Transition(Plugin):
    """How one clip gives way to the next. `overlap` transitions play over both clips at once (the next
    one starts `frames` early); the others happen at the join (the end of one, the start of the next)."""
    kind = "transition"
    abstract = True
    overlap = False
    default_duration = 1.0
    uses = ()             # which of colour / direction this transition pays attention to
    params = [Param("duration", "number", min=0.1, max=5, step=0.1, label="Seconds"),
              Param("color", "color", label="Colour"),
              Param("direction", "choice", choices=("left", "right", "up", "down", "in", "out"), label="Direction")]

    @classmethod
    def describe_extra(cls):
        return {"overlap": cls.overlap, "default_duration": cls.default_duration, "uses": list(cls.uses)}

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        """a, b: the outgoing and incoming Clips. start: the frame b starts at."""
        raise NotImplementedError


class Cut(Transition):
    description = "Straight cut (also a smash cut or match cut: the content makes the difference)"
    default_duration = 0.0

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        pass


class Fade(Transition):
    description = "Fade out to a colour (black by default), then fade in"
    uses = ("color",)
    default_duration = 1.2

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        half = max(1, frames // 2)
        ed.color(start - half, start + half, color or "black", channel=1)
        for s in a.strips:
            ed.fade(s, start - half, start, 1.0, 0.0)
        for s in b.strips:
            ed.fade(s, start, start + half, 0.0, 1.0)


class Dissolve(Transition):
    description = "One scene melts into the next"
    overlap = True

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        for s in b.strips:
            ed.fade(s, start, start + frames, 0.0, 1.0)


# Blender's single wipe: angle 90° moves the edge sideways, 0° up or down; OUT/IN picks the way it travels
_WIPE = {"left": (90.0, "OUT"), "right": (90.0, "IN"), "down": (0.0, "OUT"), "up": (0.0, "IN")}


class Wipe(Transition):
    description = "The next scene wipes across the screen (direction: the way the edge travels)"
    uses = ("direction",)
    overlap = True
    default_duration = 0.8

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        import math
        angle, way = _WIPE.get(direction or "left", _WIPE["left"])
        ed.wipe(a.strip, b.strip, start, frames, "SINGLE", math.radians(angle), way)


class Iris(Transition):
    description = "A circle opens on the next scene (direction: in closes it instead)"
    uses = ("direction",)
    overlap = True

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        ed.wipe(a.strip, b.strip, start, frames, "IRIS", 0.0, "IN" if direction == "in" else "OUT", blur=0.02)


class Clock(Transition):
    description = "A clock-hand sweep reveals the next scene (time passing)"
    overlap = True

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        ed.wipe(a.strip, b.strip, start, frames, "CLOCK", 0.0, "OUT", blur=0.02)


def _offset(ed, direction, sign=1):
    return {"left": (-ed.W * sign, 0), "right": (ed.W * sign, 0), "up": (0, ed.H * sign),
            "down": (0, -ed.H * sign)}.get(direction or "left", (-ed.W * sign, 0))


class Push(Transition):
    description = "The next scene pushes the old one off the screen"
    uses = ("direction",)
    overlap = True
    default_duration = 0.7

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        out = _offset(ed, direction)
        inn = (-out[0], -out[1])
        for s in a.strips:
            ed.move(s, start, start + frames, (0, 0), out)
        for s in b.strips:
            ed.move(s, start, start + frames, inn, (0, 0))


class Whip(Transition):
    description = "A fast whip pan from one scene to the next"
    uses = ("direction",)
    overlap = True
    default_duration = 0.3

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        Push().apply(ed, a, b, start, frames, direction=direction)
        mid = start + frames // 2
        for s in b.strips:
            ed.fade(s, start, mid + 1, 0.4, 1.0)


class Zoom(Transition):
    description = "Zoom through into the next scene"
    overlap = True
    default_duration = 0.6

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        for s in a.strips:
            ed.move(s, start, start + frames, (0, 0), (0, 0), scale=1.0, scale_to=2.2)
        for s in b.strips:
            ed.move(s, start, start + frames, (0, 0), (0, 0), scale=0.6, scale_to=1.0)
            ed.fade(s, start, start + frames, 0.0, 1.0)


class Flash(Transition):
    description = "A flash of white (or any colour) at the cut"
    uses = ("color",)
    default_duration = 0.5

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        half = max(1, frames // 2)
        c = ed.color(start - half, start + half, color or "white", channel=ed.top - 1)
        ed.fade(c, start - half, start, 0.0, 1.0)
        ed.fade(c, start, start + half, 1.0, 0.0)


# ---------------------------------------------------------------------- effects on the picture
class ScreenEffect(Plugin):
    """Something done to the whole picture at a moment in a scene: fades, flashes, dips."""
    kind = "screen"
    abstract = True
    default_duration = 1.0
    default_color = "black"

    @classmethod
    def describe_extra(cls):
        return {"default_duration": cls.default_duration, "default_color": cls.default_color}

    def apply(self, ed, f0, frames, color):
        raise NotImplementedError


class FadeOut(ScreenEffect):
    description = "Fade the picture out to a colour (and stay there)"

    def apply(self, ed, f0, frames, color):
        c = ed.color(f0, f0 + frames + ed.frames(30), color, channel=ed.top - 2)
        ed.fade(c, f0, f0 + frames, 0.0, 1.0)
        return c


class FadeIn(ScreenEffect):
    description = "Fade in from a colour"

    def apply(self, ed, f0, frames, color):
        c = ed.color(f0, f0 + frames, color, channel=ed.top - 2)
        ed.fade(c, f0, f0 + frames, 1.0, 0.0)
        return c


class FlashScreen(ScreenEffect):
    name = "flash"
    description = "A flash (an explosion, a camera, a memory)"
    default_duration = 0.4
    default_color = "white"

    def apply(self, ed, f0, frames, color):
        c = ed.color(f0, f0 + frames, color, channel=ed.top - 2)
        ed.fade(c, f0, f0 + max(1, frames // 4), 0.0, 1.0)
        ed.fade(c, f0 + max(1, frames // 4), f0 + frames, 1.0, 0.0)
        return c


class Dip(ScreenEffect):
    description = "Dip to a colour and back (a beat of time passing)"

    def apply(self, ed, f0, frames, color):
        c = ed.color(f0, f0 + frames, color, channel=ed.top - 2)
        ed.fade(c, f0, f0 + frames // 2, 0.0, 1.0)
        ed.fade(c, f0 + frames // 2, f0 + frames, 1.0, 0.0)
        return c


class Blackout(ScreenEffect):
    description = "Cut to a plain colour for a while"

    def apply(self, ed, f0, frames, color):
        return ed.color(f0, f0 + frames, color, channel=ed.top - 2)

