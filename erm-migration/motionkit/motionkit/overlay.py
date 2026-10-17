"""Screen-space layer: captions, titles, logos, fades. It rides on the camera, so it never moves
with the 3D scene and nothing in the scene can cover it.

Positions are fractions of the frame: x from -0.5 (left edge) to 0.5 (right edge), y from -0.5
(bottom) to 0.5 (top). Sizes are fractions of the frame height (0.05 = 5% of the height).

    movie.overlay.caption("Everything you rely on", eyebrow="New", at=2, until=5)
    movie.overlay.title("ERM 2.0", subtitle="Coming soon", at=8)
    movie.overlay.fade_from_black(at=0, duration=1)
"""
import math

import bpy

from .assets import Text3D, _plane_object
from .item import Item
from .keys import socket_key
from .materials import GlowMaterial

DIST = 5.0  # distance of the overlay plane in front of the lens


class Overlay:
    def __init__(self, camera, size):
        self.camera = camera
        self.aspect = size[0] / size[1]
        self.root = bpy.data.objects.new("overlay", None)
        bpy.context.scene.collection.objects.link(self.root)
        self.root.parent = camera.obj
        self._fader = None

    @property
    def width(self):
        return DIST * 36 / self.camera.obj.data.lens

    @property
    def height(self):
        return self.width / self.aspect

    def _place(self, ob, x, y, z=0.0):
        ob.parent = self.root
        ob.rotation_euler = (0, 0, 0)
        ob.location = (x * self.width, y * self.height, -DIST + z)
        return ob

    def _timed(self, item, at, until, fade):
        if at is not None:
            item.fade_in(at, fade)
            if until is not None:
                item.fade_out(until - fade, fade)
        return item

    # ------------------------------------------------------------------ text
    def text(self, text, x=0.0, y=0.0, size=0.05, color="white", glow=1.0, at=None, until=None, fade=0.4,
             font=None, align="center", spacing=1.0, rise=True):
        """Flat text on screen. Fades in at `at`, out at `until` (both optional)."""
        t = Text3D(text, size * self.height, color, glow, depth=0, font=font, align=align, spacing=spacing)
        self._place(t.obj, x, y)
        t._loc, t._rot = t.obj.location.copy(), t.obj.rotation_euler.copy()
        if at is not None and rise:
            t.slide_in(at, fade + 0.3, (0, -0.02 * self.height * 10, 0), 1.0, fade=False)
        return self._timed(t, at, until, fade)

    def caption(self, text, eyebrow=None, at=None, until=None, color="white", accent="pink"):
        """A subtitle-style line near the bottom, with an optional small label above it."""
        main = self.text(text, 0, -0.36, 0.05, color, 1.0, at, until)
        if eyebrow:
            self.text(eyebrow.upper(), 0, -0.29, 0.028, accent, 1.0, None if at is None else at + 0.15, until,
                      spacing=1.4, rise=False)
        return main

    def title(self, text, subtitle=None, at=None, until=None, color="white", accent="pink", size=0.14):
        """A big centred title, with an optional subtitle under it."""
        t = self.text(text, 0, 0.04, size, color, 2.0, at, until)
        if subtitle:
            self.text(subtitle, 0, -0.1, 0.035, accent, 1.2, None if at is None else at + 0.4, until, spacing=1.2)
        return t

    def lower_third(self, name, role=None, at=None, until=None, accent="pink"):
        """Name and role at the bottom left, with an accent bar (introducing a person or a feature)."""
        bar = self.box(-0.46, -0.33, 0.006, 0.09, accent, at=at, until=until)
        self.text(name, -0.445, -0.31, 0.04, "white", 1.0, at, until, align="left")
        if role:
            self.text(role, -0.445, -0.355, 0.026, "muted", 1.0, at, until, align="left")
        return bar

    # ------------------------------------------------------------------ pictures and boxes
    def box(self, x, y, w, h, color="black", opacity=1.0, at=None, until=None, fade=0.4):
        """A filled rectangle (fractions of the frame), e.g. a backing panel behind text."""
        mat = GlowMaterial(color, 1.0, opacity)
        ob = _plane_object("overlay box", w * self.width, h * self.height, mat)
        ob.rotation_euler = (math.radians(-90), 0, 0)
        ob = self._place(ob, x, y, -0.002)
        ob.rotation_euler = (math.radians(-90), 0, 0)
        return self._timed(Item(ob, [mat]), at, until, fade)

    def image(self, path, x=0.0, y=0.0, height=0.2, at=None, until=None, fade=0.4):
        """A picture or logo on screen, `height` as a fraction of the frame height."""
        mat = GlowMaterial("white", 1.0, 1.0, image=path)
        h = height * self.height
        ob = _plane_object("overlay image", h * mat.aspect, h, mat)
        ob = self._place(ob, x, y)
        ob.rotation_euler = (math.radians(-90), 0, 0)
        return self._timed(Item(ob, [mat]), at, until, fade)

    def letterbox(self, amount=0.1, color="black"):
        """Cinematic black bars, `amount` of the frame height each."""
        for sign in (1, -1):
            self.box(0, sign * (0.5 - amount / 2), 1.2, amount, color).obj.location.z = -DIST + 0.02

    # ------------------------------------------------------------------ fades
    def _full(self, color, z):
        mat = GlowMaterial(color, 1.0, 0.0)
        ob = _plane_object("overlay fill", self.width * 1.4, self.height * 1.4, mat)
        ob = self._place(ob, 0, 0, z)
        ob.rotation_euler = (math.radians(-90), 0, 0)
        return mat

    def fade_from_black(self, at=0.0, duration=1.0):
        """Start in black and fade the picture up."""
        m = self._full("black", 0.03)
        socket_key(m.alpha, at, 1.0)
        socket_key(m.alpha, at + duration, 0.0)

    def fade_to_black(self, at, duration=1.0):
        """Fade the picture down to black, finishing at `at + duration`."""
        m = self._full("black", 0.03)
        socket_key(m.alpha, at, 0.0)
        socket_key(m.alpha, at + duration, 1.0)

    def dip(self, at, color="black", duration=0.8):
        """Fade to a colour and back, peaking at `at` (hides a cut)."""
        m = self._full(color, 0.025)
        socket_key(m.alpha, at - duration / 2, 0.0)
        socket_key(m.alpha, at, 1.0)
        socket_key(m.alpha, at + duration / 2, 0.0)

    def flash(self, at, color="white", strength=0.9, duration=0.4):
        """A bright flash peaking at `at` (punctuates a reveal or hides a cut)."""
        m = self._full(color, 0.028)
        m.strength.default_value = 2.0
        socket_key(m.alpha, at - duration * 0.3, 0.0)
        socket_key(m.alpha, at, strength)
        socket_key(m.alpha, at + duration * 0.7, 0.0)
