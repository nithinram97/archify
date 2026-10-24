"""This film's own additions to dreamreel: a robot character, a dance and a birthday cake.

Every class below registers itself when the film loads, then shows up everywhere: in cast and set
files, in scene beats, and in the studio's menus (with forms built from `params`).
"""
import math

from mathutils import Vector

import dreamreel as dr
from dreamreel import look, shapes
from dreamreel.plugins import Param


class Robot(dr.Character):
    """A friendly tin robot with a box head and a glowing antenna. Use with `type = "robot"`."""
    description = "A friendly tin robot"
    params = [
        Param("name", "text"),
        Param("height", "number", default=1.0, min=0.7, max=1.3, step=0.05),
        Param("metal", "color", default="#a9b4bd"),
        Param("trim", "color", default="teal"),
        Param("glow", "color", default="#7df9ff", label="Eye glow"),
        Param("extras", "extras", default=[]),
        Param("voice", "voice"),
    ]

    def validate(self):
        self.spec.update(hair="none", nose=False, blush=False, body="bean")
        super().validate()

    def color(self, key, default="white"):
        if key in ("skin", "top", "bottom"):
            return self.spec["metal"]
        if key == "shoes":
            return self.spec["trim"]
        if key == "hair_color":
            return "charcoal"
        return super().color(key, default)

    def build_head(self):
        hr, metal = self.hr, look.plastic(self.spec["metal"], rough=0.22, coat=0.7)
        shapes.box(f"{self.name}.head", hr * 1.9, hr * 1.6, hr * 1.7, metal, self.neck,
                   at=self.hc - Vector((0, 0, hr * 0.85)), bevel=hr * 0.22)
        top = self.head_top()
        shapes.cylinder(f"{self.name}.antenna", 0.012 * self.H, hr * 0.55, self.spec["trim"], self.neck, at=top)
        shapes.sphere(f"{self.name}.antenna.ball", hr * 0.14, look.plastic(self.spec["glow"], emission=3.0),
                      self.neck, at=top + Vector((0, 0, hr * 0.6)))
        for side in (1, -1):  # ear bolts
            shapes.cylinder(f"{self.name}.bolt", hr * 0.18, hr * 0.12, self.spec["trim"], self.neck,
                            at=self.hc + Vector((side * hr * 0.95, 0, 0)), rot=(0, math.radians(90 * side), 0))

    def head_top(self):
        return self.hc + Vector((0, 0, self.hr * 0.85))

    def face_point(self, x, z, inset=0.006):
        return Vector((x, -self.hr * 0.8 + inset * self.H, z)) + self.hc

    def eye_color(self):
        return self.spec["glow"]


class Dance(dr.Gesture):
    """Sway side to side with arms up, bouncing on the beat."""
    description = "A happy little dance"

    def perform(self, c, t, target=None):
        beat = 0.35
        for i in range(6):
            tb = t + i * beat
            side = 1 if i % 2 else -1
            c.lean_at(tb + beat / 2, 14 * side)
            c.hop_at(tb, 0.05, beat * 0.4, beat)
            for s in (1, -1):
                c.arm_to(s, tb + beat / 2, (0, math.radians((-150 if s == side else -110) * s), 0))
        end = t + 6 * beat
        c.lean_at(end + 0.2, 0)
        c.arms_rest(end + 0.3)
        return end + 0.3


class Cake(dr.Prop):
    """A layered birthday cake on a little table, with candles."""
    description = "A birthday cake with candles"
    default_place = "center"
    params = dr.Prop.params + [Param("color", "color", default="pink", label="Icing"),
                               Param("candles", "number", default=5, min=0, max=12, step=1)]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.6, 0.6, self.default_place)
        x, y = pos.x, pos.y
        shapes.cylinder(name + ".stand", 0.28, 0.42, "white", at=(x, y, 0), r2=0.22)
        icing = p.get("color", "pink")
        shapes.cylinder(name, 0.24, 0.12, "cream", at=(x, y, 0.42))
        shapes.cylinder(name, 0.245, 0.03, icing, at=(x, y, 0.53))
        shapes.cylinder(name, 0.16, 0.1, "cream", at=(x, y, 0.56))
        shapes.cylinder(name, 0.165, 0.03, icing, at=(x, y, 0.65))
        n = int(p.get("candles", 5))
        for i in range(n):
            a = 2 * math.pi * i / max(1, n)
            cx, cy = x + 0.1 * math.cos(a), y + 0.1 * math.sin(a)
            shapes.cylinder(name + ".candle", 0.012, 0.08, "sky", at=(cx, cy, 0.68), bevel=0)
            shapes.sphere(name + ".flame", 0.014, look.plastic("#ffb347", emission=6), at=(cx, cy, 0.78))
        s.block(pos, 0.6, 0.6)
        s.add_mark(name, (x, y - 0.6), facing="back")
