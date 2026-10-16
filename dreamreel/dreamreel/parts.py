"""Hair styles, extras (glasses, hats...) and moods: small classes a character is assembled from.

    class Crown(dr.Extra):
        description = "A golden crown"
        def build(self, c):
            g = dr.look.plastic("#e8b923", rough=0.25, coat=0.8)
            dr.shapes.cylinder(f"{c.name}.crown", c.hr * 0.7, c.hr * 0.35, g, c.neck,
                               at=c.head_top(), r2=c.hr * 0.8)

    class Confused(dr.Mood):
        brow_tilt, head_tilt, frown = 14, 12, 0.2

Geometry helpers on the character: `c.neck` (parent for anything on the head), `c.body` (for anything
on the torso), `c.hc` (head centre), `c.hr` (head radius), `c.H` (height scale), `c.face_point(x, z)`
(a point on the face surface), `c.head_top()`, `c.neck_z`, `c.body_r`.
"""
import math

from mathutils import Vector

from . import look, shapes as S
from .plugins import Plugin


def _deg(d):
    return math.radians(d)


# ---------------------------------------------------------------------- moods
class Mood(Plugin):
    """An expression: how far the brows tilt and lift, the mouth shape, the eyes and the head tilt."""
    kind = "mood"
    abstract = True
    brow_tilt = 0.0     # degrees; + raises the inner ends (sad, worried), - lowers them (angry)
    brow_lift = 0.0     # fraction of height
    smile = 0.0         # 0-1
    frown = 0.0         # 0-1
    eyes = 1.0          # eye size; < 1 narrows, > 1 widens
    mouth_open = 0.0    # 0-1
    head_tilt = 0.0     # degrees forward (+) or back (-)

    @classmethod
    def define(cls, name, **values):
        """Make a mood without writing a class: dr.Mood.define("confused", brow_tilt=14, head_tilt=12)."""
        return type(name.title().replace("_", ""), (cls,), {"name": name, **values})


for _n, (_t, _l, _s, _f, _e, _m, _h) in {
    "neutral": (0, 0.0, 0.0, 0.0, 1.0, 0.0, 0),
    "happy": (-4, 0.008, 1.0, 0.0, 1.0, 0.0, 0),
    "excited": (-6, 0.016, 1.0, 0.0, 1.12, 0.35, -4),
    "sad": (22, 0.0, 0.0, 0.9, 0.95, 0.0, 10),
    "angry": (-24, -0.012, 0.0, 0.6, 0.95, 0.0, 4),
    "surprised": (4, 0.028, 0.0, 0.0, 1.25, 0.8, -6),
    "worried": (16, 0.006, 0.0, 0.35, 1.05, 0.0, 4),
    "scared": (20, 0.02, 0.0, 0.45, 1.25, 0.4, 6),
    "smug": (-10, 0.0, 0.6, 0.0, 0.85, 0.0, -5),
    "sleepy": (8, -0.006, 0.0, 0.0, 0.45, 0.0, 8),
}.items():
    Mood.define(_n, brow_tilt=_t, brow_lift=_l, smile=_s, frown=_f, eyes=_e, mouth_open=_m, head_tilt=_h)


# ---------------------------------------------------------------------- hair
class Hair(Plugin):
    """A hair style. `build(c, color)` adds meshes parented to `c.neck`."""
    kind = "hair"
    abstract = True
    hairline = 0.6      # how far the cap reaches down the back of the head (higher = longer at the back)
    hairline_z = 0.0    # where the cap starts above the head centre, in head radii

    def cap(self, c, color, segments=40):
        """The basic hair cap that most styles start from."""
        cap = S.sphere(f"{c.name}.hair", c.hr * 1.06, color, c.neck, at=c.hc, segments=segments)
        S.cut_below(cap, (0, 0, self.hairline_z * c.hr), (0, self.hairline, 1))
        return cap

    def build(self, c, color):
        self.cap(c, color)


class NoHair(Hair):
    name = "none"
    label = "Bald"

    def build(self, c, color):
        pass


class Short(Hair):
    hairline, hairline_z = 0.55, 0.05


class Bob(Hair):
    def build(self, c, color):
        self.cap(c, color)
        hr, hc = c.hr, c.hc
        for side in (1, -1):
            S.ellipsoid(f"{c.name}.hair", hr * 0.42, hr * 0.62, hr * 0.62, color, c.neck,
                        at=hc + Vector((side * hr * 0.72, hr * 0.12, -hr * 0.28)))
        S.ellipsoid(f"{c.name}.hair", hr * 0.85, hr * 0.5, hr * 0.62, color, c.neck, at=hc + Vector((0, hr * 0.55, -hr * 0.3)))


class Long(Hair):
    def build(self, c, color):
        self.cap(c, color)
        S.ellipsoid(f"{c.name}.hair", c.hr * 0.95, c.hr * 0.45, c.hr * 1.25, color, c.neck,
                    at=c.hc + Vector((0, c.hr * 0.6, -c.hr * 0.65)))


class Ponytail(Hair):
    def build(self, c, color):
        self.cap(c, color)
        S.ellipsoid(f"{c.name}.hair", c.hr * 0.3, c.hr * 0.3, c.hr * 0.8, color, c.neck,
                    at=c.hc + Vector((0, c.hr * 1.15, -c.hr * 0.25)), rot=(_deg(-25), 0, 0))


class Bun(Hair):
    def build(self, c, color):
        self.cap(c, color)
        S.sphere(f"{c.name}.hair", c.hr * 0.42, color, c.neck, at=c.hc + Vector((0, c.hr * 0.25, c.hr * 1.02)))


class Spiky(Hair):
    hairline, hairline_z = 0.55, 0.05

    def build(self, c, color):
        self.cap(c, color)
        for i in range(7):
            a = _deg(-60 + i * 20)
            S.cylinder(f"{c.name}.spike", c.hr * 0.2, c.hr * 0.5, color, c.neck,
                       at=c.hc + Vector((math.sin(a) * c.hr * 0.6, c.hr * 0.1, c.hr * 0.78)),
                       rot=(_deg(10), math.sin(a) * 0.9, 0), r2=0.0, bevel=0)


class Curly(Hair):
    def build(self, c, color):
        self.cap(c, color)
        hr = c.hr
        for i in range(14):
            a = 2 * math.pi * i / 14
            S.sphere(f"{c.name}.curl", hr * 0.3, color, c.neck,
                     at=c.hc + Vector((math.cos(a) * hr * 0.85, math.sin(a) * hr * 0.6 + hr * 0.25,
                                       hr * 0.55 + 0.15 * hr * math.sin(3 * a))))


class Mohawk(Hair):
    hairline, hairline_z = 0.55, 0.05

    def build(self, c, color):
        cap = self.cap(c, color)
        cap.scale = (0.35, 1.0, 1.0)
        cap.location.z += 0.03 * c.H


# ---------------------------------------------------------------------- extras
class Extra(Plugin):
    """Something worn or added to a character. `build(c)` adds meshes parented to `c.neck` or `c.body`."""
    kind = "extra"
    abstract = True

    def build(self, c):
        raise NotImplementedError


class Glasses(Extra):
    def build(self, c):
        frame = look.plastic("#222222", 0.3, 0.6)
        H = c.H
        for side in (1, -1):
            S.torus(f"{c.name}.glasses", 0.047 * H, 0.007 * H, frame, c.neck,
                    at=c.face_point(side * 0.075 * H, 0.02 * H, -0.02), rot=(_deg(90), 0, 0))
        S.capsule(f"{c.name}.glasses", 0.006 * H, 0.04 * H, frame, c.neck, at=c.face_point(0, 0.03 * H, -0.03),
                  rot=(0, _deg(90), 0))


class Hat(Extra):
    description = "A top hat"

    def build(self, c):
        hr, hc = c.hr, c.hc
        S.cylinder(f"{c.name}.hat", hr * 1.45, 0.02 * c.H, "charcoal", c.neck, at=hc + Vector((0, 0, hr * 0.62)))
        S.cylinder(f"{c.name}.hat", hr * 0.92, hr * 0.75, "charcoal", c.neck, at=hc + Vector((0, 0, hr * 0.62)), r2=hr * 0.88)


class Cap(Extra):
    description = "A baseball cap"

    def build(self, c):
        hr, hc = c.hr, c.hc
        capm = S.sphere(f"{c.name}.cap", hr * 1.08, "red", c.neck, at=hc)
        S.cut_below(capm, (0, 0, hr * 0.2), (0, 0.2, 1))
        S.cylinder(f"{c.name}.cap", hr * 0.6, 0.015 * c.H, "red", c.neck, at=hc + Vector((0, -hr * 0.85, hr * 0.38)),
                   rot=(_deg(-8), 0, 0))


class Scarf(Extra):
    def build(self, c):
        S.torus(f"{c.name}.scarf", c.body_r * 0.72, 0.045 * c.H, "red", c.body, at=(0, 0, c.neck_z - 0.02 * c.H))


class Tie(Extra):
    def build(self, c):
        S.box(f"{c.name}.tie", 0.035 * c.H, 0.012 * c.H, 0.17 * c.H, "red", c.body,
              at=(0, -c.body_r * 0.84, c.neck_z - 0.22 * c.H), rot=(_deg(-12), 0, 0), bevel=0.005 * c.H)


class Bow(Extra):
    description = "A hair bow"

    def build(self, c):
        hr = c.hr
        for side in (1, -1):
            S.ellipsoid(f"{c.name}.bow", hr * 0.28, hr * 0.12, hr * 0.2, "pink", c.neck,
                        at=c.hc + Vector((side * hr * 0.3, -hr * 0.1, hr * 0.98)), rot=(0, _deg(side * 20), 0))


class Beard(Extra):
    def build(self, c):
        hr = c.hr
        S.ellipsoid(f"{c.name}.beard", hr * 0.7, hr * 0.45, hr * 0.45, c.color("hair_color"), c.neck,
                    at=c.hc + Vector((0, -hr * 0.55, -hr * 0.62)))


class Moustache(Extra):
    def build(self, c):
        for side in (1, -1):
            S.ellipsoid(f"{c.name}.moustache", 0.038 * c.H, 0.014 * c.H, 0.014 * c.H, c.color("hair_color"), c.neck,
                        at=c.face_point(side * 0.032 * c.H, -0.045 * c.H, -0.006), rot=(0, _deg(side * 12), 0))


class Headphones(Extra):
    def build(self, c):
        hr, hc = c.hr, c.hc
        S.torus(f"{c.name}.headphones", hr * 1.08, 0.014 * c.H, "charcoal", c.neck, at=hc,
                rot=(_deg(90), 0, _deg(90)), arc=180)
        for side in (1, -1):
            S.cylinder(f"{c.name}.headphones", 0.05 * c.H, 0.04 * c.H, "charcoal", c.neck,
                       at=hc + Vector((side * hr * 1.0, 0, 0)), rot=(0, _deg(90 * side), 0))
