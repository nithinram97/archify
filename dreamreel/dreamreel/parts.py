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
    """An expression: a setting for each face control (see face.py for what each one does)."""
    kind = "mood"
    abstract = True
    brow_tilt = 0.0     # degrees; + raises the inner ends (sad, worried), - lowers them (angry)
    brow_lift = 0.0     # fraction of height
    brow_squeeze = 0.0  # 0-1, brows pulled together
    smile = 0.0         # 0-1
    frown = 0.0         # 0-1
    eyes = 1.0          # eye size; < 1 narrows, > 1 widens
    pupils = 1.0        # < 1 shrinks the dark of the eye, showing the whites
    lids = 0.0          # 0-1, upper lids down
    squint = 0.0        # 0-1, lower lids up
    lid_slant = 0.0     # -1 angry ... 1 sad
    wide = 0.0          # 0-1, lips stretched wide
    o = 0.0             # 0-1, lips rounded
    smirk = 0.0         # -1-1, one corner up
    mouth_open = 0.0    # 0-1
    teeth = 0.0         # 0-1: upper teeth by 0.5, both (clenched) by 1
    blush = 0.0         # 0-1
    tears = 0.0         # 0-1
    sweat = 0.0         # 0-1
    head_tilt = 0.0     # degrees forward (+) or back (-)

    @classmethod
    def define(cls, name, **values):
        """Make a mood without writing a class: dr.Mood.define("confused", brow_tilt=14, head_tilt=12)."""
        return type(name.title().replace("_", ""), (cls,), {"name": name, **values})


MOODS = {
    "neutral": {},
    "happy": dict(brow_tilt=-4, brow_lift=0.008, smile=1.0, squint=0.25),
    "excited": dict(brow_tilt=-6, brow_lift=0.016, smile=1.0, eyes=1.12, mouth_open=0.35, teeth=0.5, head_tilt=-4),
    "sad": dict(brow_tilt=22, frown=0.9, eyes=0.95, lids=0.25, lid_slant=0.6, head_tilt=10),
    "angry": dict(brow_tilt=-24, brow_lift=-0.012, brow_squeeze=0.5, frown=0.6, eyes=0.95, lid_slant=-0.6, head_tilt=4),
    "surprised": dict(brow_tilt=4, brow_lift=0.028, eyes=1.25, mouth_open=0.8, o=0.6, head_tilt=-6),
    "worried": dict(brow_tilt=16, brow_lift=0.006, brow_squeeze=0.3, frown=0.35, eyes=1.05, wide=0.3, head_tilt=4),
    "scared": dict(brow_tilt=20, brow_lift=0.02, eyes=1.25, pupils=0.8, frown=0.45, wide=0.5, mouth_open=0.4,
                   head_tilt=6),
    "smug": dict(brow_tilt=-10, smile=0.4, smirk=0.7, eyes=0.85, lids=0.35, head_tilt=-5),
    "sleepy": dict(brow_tilt=8, brow_lift=-0.006, lids=0.8, eyes=0.9, head_tilt=8),
    # the extremes (FACS combinations, pushed for animation)
    "gleeful": dict(brow_tilt=-6, brow_lift=0.012, smile=1.0, wide=0.6, teeth=0.5, squint=0.7, eyes=1.0,
                    blush=0.4, head_tilt=-3),
    "crazed": dict(brow_tilt=-16, brow_lift=0.024, smile=1.0, wide=0.85, teeth=1.0, eyes=1.35, pupils=0.42,
                   lid_slant=-0.2, head_tilt=10),
    "furious": dict(brow_tilt=-32, brow_lift=-0.016, brow_squeeze=1.0, frown=0.5, wide=0.75, teeth=1.0,
                    mouth_open=0.25, eyes=1.0, lid_slant=-1.0, lids=0.15, head_tilt=8),
    "determined": dict(brow_tilt=-18, brow_lift=-0.006, brow_squeeze=0.7, wide=0.9, teeth=1.0, mouth_open=0.12,
                       squint=0.7, lid_slant=-0.4, head_tilt=5),
    "terrified": dict(brow_tilt=26, brow_lift=0.032, brow_squeeze=0.4, eyes=1.4, pupils=0.45, frown=0.4, wide=1.0,
                      mouth_open=0.7, teeth=0.6, head_tilt=-4, sweat=0.6),
    "screaming": dict(brow_tilt=22, brow_lift=0.026, eyes=1.15, pupils=0.7, squint=0.3, mouth_open=1.0, wide=0.5,
                      o=0.2, teeth=0.6, head_tilt=-10),
    "shocked": dict(brow_tilt=6, brow_lift=0.038, eyes=1.45, pupils=0.55, mouth_open=0.75, o=0.8, head_tilt=-8),
    "disgusted": dict(brow_tilt=-12, brow_lift=-0.004, brow_squeeze=0.6, frown=0.5, smirk=-0.8, squint=0.8,
                      teeth=0.3, head_tilt=-6),
    "suspicious": dict(brow_tilt=-10, brow_lift=-0.004, lids=0.5, squint=0.3, smirk=0.25, eyes=0.95, head_tilt=4),
    "crying": dict(brow_tilt=28, brow_lift=0.01, brow_squeeze=0.6, frown=1.0, wide=0.6, mouth_open=0.45,
                   teeth=0.4, squint=0.8, lid_slant=0.8, tears=1.0, head_tilt=10),
    "embarrassed": dict(brow_tilt=12, smile=0.45, wide=0.2, eyes=0.9, lids=0.25, blush=1.0, head_tilt=12),
    "nervous": dict(brow_tilt=18, brow_lift=0.01, smile=0.35, wide=0.8, teeth=1.0, eyes=1.1, pupils=0.85,
                    sweat=1.0, head_tilt=4),
    "bored": dict(brow_lift=-0.004, lids=0.6, frown=0.15, eyes=1.0, head_tilt=6),
    "loving": dict(brow_tilt=10, brow_lift=0.01, smile=0.8, squint=0.6, lids=0.3, blush=0.8, head_tilt=10),
    # fighting: the effort of a blow, the pain of taking one, the calm before
    "fierce": dict(brow_tilt=-28, brow_lift=-0.014, brow_squeeze=0.9, wide=0.85, teeth=1.0, mouth_open=0.18,
                   squint=0.6, lid_slant=-0.7, head_tilt=6),
    "pain": dict(brow_tilt=26, brow_lift=0.008, brow_squeeze=1.0, squint=1.0, lids=0.65, wide=0.8, teeth=0.7,
                 mouth_open=0.45, eyes=0.85, head_tilt=-10),
    "focused": dict(brow_tilt=-8, brow_squeeze=0.3, lids=0.2, squint=0.25, eyes=0.95, head_tilt=4),
    "cold": dict(brow_tilt=-6, lids=0.3, smirk=0.25, eyes=0.9, head_tilt=-3),
}
for _n, _v in MOODS.items():
    Mood.define(_n, **_v)


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
        back = S.ellipsoid(f"{c.name}.hair", c.hr * 0.95, c.hr * 0.45, c.hr * 1.25, color, c.neck,
                           at=c.hc + Vector((0, c.hr * 0.6, -c.hr * 0.65)))
        c.dangle(back, c.hc + Vector((0, c.hr * 0.55, c.hr * 0.4)), stiffness=0.8, gain=0.7)


class Ponytail(Hair):
    def build(self, c, color):
        self.cap(c, color)
        tail = S.ellipsoid(f"{c.name}.hair", c.hr * 0.3, c.hr * 0.3, c.hr * 0.8, color, c.neck,
                           at=c.hc + Vector((0, c.hr * 1.15, -c.hr * 0.25)), rot=(_deg(-25), 0, 0))
        c.dangle(tail, c.hc + Vector((0, c.hr * 0.95, c.hr * 0.45)), stiffness=0.6, gain=1.3)


class Bun(Hair):
    def build(self, c, color):
        self.cap(c, color)
        bun = S.sphere(f"{c.name}.hair", c.hr * 0.42, color, c.neck, at=c.hc + Vector((0, c.hr * 0.25, c.hr * 1.02)))
        c.dangle(bun, c.hc + Vector((0, c.hr * 0.2, c.hr * 0.75)), stiffness=2.2, gain=0.5)


class SpaceBuns(Hair):
    name = "space_buns"
    label = "Space buns"
    hairline, hairline_z = 0.62, 0.02

    def build(self, c, color):
        cap = self.cap(c, color)
        hr, hc = c.hr, c.hc
        for side in (1, -1):
            at = hc + Vector((side * hr * 0.58, hr * 0.12, hr * 0.8))
            S.sphere(f"{c.name}.hair", hr * 0.36, color, c.neck, at=at)
            S.capsule(f"{c.name}.hair", hr * 0.06, hr * 0.12, color, c.neck, at=at + Vector((side * hr * 0.03, -hr * 0.05, hr * 0.32)),
                      rot=(_deg(-20), _deg(side * 25), 0))
        return cap


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
