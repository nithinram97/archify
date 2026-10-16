"""Characters: toy figures built from a short description, and the verbs that make them act.

    mia = Character("Mia", height=1.0, skin="skin3", hair="bob", hair_color="black",
                    top="red", bottom="denim", shoes="white", extras=["glasses"])
    mia.enter("door").walk_to("table").say("Who ate the last cookie?", mood="angry")

A character is a jointed vinyl figure (like a collectible toy): separate head, body, arms and legs on
pivots. Nothing is skinned, so poses can't tear or bend wrongly, and the stiffness reads as a style.

Facing: a character at rotation 0 faces -Y (towards the default camera). Its left hand is at +X.
"""
import math
import random
import re

from mathutils import Vector

from . import keys, look, shapes
from .keys import hold, key, value_at

MOODS = {
    #            brow tilt (deg, + = inner end up), brow lift, smile, frown, eye scale, mouth open, head tilt
    "neutral":   (0, 0.0, 0.0, 0.0, 1.0, 0.0, 0),
    "happy":     (-4, 0.008, 1.0, 0.0, 1.0, 0.0, 0),
    "excited":   (-6, 0.016, 1.0, 0.0, 1.12, 0.35, -4),
    "sad":       (22, 0.0, 0.0, 0.9, 0.95, 0.0, 10),
    "angry":     (-24, -0.012, 0.0, 0.6, 0.95, 0.0, 4),
    "surprised": (4, 0.028, 0.0, 0.0, 1.25, 0.8, -6),
    "worried":   (16, 0.006, 0.0, 0.35, 1.05, 0.0, 4),
    "scared":    (20, 0.02, 0.0, 0.45, 1.25, 0.4, 6),
    "smug":      (-10, 0.0, 0.6, 0.0, 0.85, 0.0, -5),
    "sleepy":    (8, -0.006, 0.0, 0.0, 0.45, 0.0, 8),
}

GESTURES = ("wave", "nod", "shake_head", "shrug", "point", "jump", "cheer", "facepalm", "clap", "think",
            "bow", "stomp")

HAIR = ("none", "short", "bob", "long", "spiky", "bun", "curly", "ponytail", "mohawk")
EXTRAS = ("glasses", "hat", "cap", "scarf", "tie", "bow", "beard", "moustache", "headphones")
BODIES = ("bean", "round", "tall", "kid")
SPEEDS = {"slow": 0.65, "normal": 1.0, "fast": 1.45, "run": 2.1}


def _deg(d):
    return math.radians(d)


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def heading_to(dx, dy):
    """Rotation about Z that makes a character face the direction (dx, dy)."""
    return math.atan2(dx, -dy)


class Character:
    def __init__(self, name, height=1.0, body="bean", skin="skin2", hair="short", hair_color="brown",
                 top="blue", bottom="navy", shoes="charcoal", eyes="normal", extras=(), outfit="shirt",
                 blush=True, nose=True, voice=None, scene=None, **_ignored):
        if body not in BODIES:
            raise ValueError(f"{name}: body {body!r} unknown; use one of {BODIES}")
        if hair not in HAIR:
            raise ValueError(f"{name}: hair {hair!r} unknown; use one of {HAIR}")
        for e in extras:
            if e not in EXTRAS:
                raise ValueError(f"{name}: extra {e!r} unknown; use any of {EXTRAS}")
        self.name = name
        self.scene = scene
        self.voice = voice
        self.H = H = height * (0.75 if body == "kid" else 1.0)
        self.spec = dict(body=body, skin=skin, hair=hair, hair_color=hair_color, top=top, bottom=bottom,
                         shoes=shoes, eyes=eyes, extras=list(extras), outfit=outfit)
        self.busy = 0.0
        self.mood = "neutral"
        self.sitting = None
        self.rng = random.Random(name)
        self.hip_z = 0.29 * H
        self.head_r = (0.21 if body == "kid" else 0.17 if body == "tall" else 0.19) * H
        self._build(H, body, skin, hair, hair_color, top, bottom, shoes, eyes, extras, outfit, blush, nose)

    # ------------------------------------------------------------------ construction
    def _build(self, H, body, skin, hair, hair_color, top, bottom, shoes, eyes, extras, outfit, blush, nose):
        n = self.name
        S = shapes
        self.root = S.empty(f"{n}")
        self.root.empty_display_size = 0.3
        self.hips = S.empty(f"{n}.hips", self.root, (0, 0, self.hip_z))

        # legs and shoes
        shoe_h = 0.07 * H
        leg_r = 0.055 * H
        self.legs = {}
        for side in (1, -1):
            piv = S.empty(f"{n}.leg.{'L' if side > 0 else 'R'}", self.hips, (side * 0.075 * H, 0, 0))
            S.capsule(f"{n}.thigh", leg_r, max(0.01, self.hip_z - shoe_h * 0.6 - 2 * leg_r), bottom, piv, hang=True)
            S.box(f"{n}.shoe", 0.125 * H, 0.18 * H, shoe_h, shoes, piv, at=(0, -0.025 * H, -self.hip_z), bevel=0.03 * H)
            self.legs[side] = piv

        # body: a bean, shirt on top and trousers (or a skirt) below
        r = {"round": 0.19, "tall": 0.15}.get(body, 0.165) * H
        length = {"round": 0.08, "tall": 0.2}.get(body, 0.12) * H
        self.body = S.empty(f"{n}.body", self.hips)
        cz = -0.06 * H + r + length / 2
        upper = S.capsule(f"{n}.top", r, length, top, self.body, at=(0, 0, cz), squash=(1, 0.86))
        S.cut_below(upper, (0, 0, 0.03 * H - cz), (0, 0, 1))
        if outfit == "dress":
            S.cylinder(f"{n}.skirt", r * 1.02, 0.2 * H, top, self.body, at=(0, 0, -0.14 * H), r2=r * 0.8, bevel=0.01 * H)
        else:
            lower = S.capsule(f"{n}.pants", r * 0.995, length, bottom, self.body, at=(0, 0, cz), squash=(1, 0.86))
            S.cut_below(lower, (0, 0, 0.03 * H - cz), (0, 0, -1))
        neck_z = cz + length / 2 + r * 0.82
        self.top_z = neck_z

        # arms
        self.arms = {}
        shoulder_z = cz + length / 2 + r * 0.25
        for side in (1, -1):
            piv = S.empty(f"{n}.arm.{'L' if side > 0 else 'R'}", self.body, (side * r * 0.86, 0, shoulder_z))
            arm = S.capsule(f"{n}.arm", 0.047 * H, 0.15 * H, top, piv, rot=(0, _deg(-12 * side), 0), hang=True)
            S.sphere(f"{n}.hand", 0.058 * H, skin, arm, at=(0, 0, -0.27 * H))
            self.arms[side] = piv

        # head
        hr = self.head_r
        self.neck = S.empty(f"{n}.neck", self.body, (0, 0, neck_z))
        hc = Vector((0, 0, hr * 0.62))
        self.head_center = hc
        S.sphere(f"{n}.head", hr, skin, self.neck, at=hc)

        def on_face(x, z, inset=0.006):
            y = -math.sqrt(max(0.0, hr * hr - x * x - z * z)) + inset * H
            return Vector((x, y, z)) + hc

        # eyes
        es = {"small": 0.8, "normal": 1.0, "big": 1.3}.get(eyes, 1.0)
        self.eyes = []
        for side in (1, -1):
            p = on_face(side * 0.075 * H, 0.02 * H, 0.004)
            piv = S.empty(f"{n}.eye", self.neck, p)
            eye = S.ellipsoid(f"{n}.eye", 0.03 * H * es, 0.02 * H, 0.043 * H * es, look.plastic("#161414", 0.12, 0.9), piv)
            S.sphere(f"{n}.glint", 0.011 * H * es, look.plastic("white", emission=1.5), eye,
                     at=(0.01 * H * es, -0.016 * H, 0.016 * H * es))
            self.eyes.append(piv)

        # brows
        self.brows = {}
        for side in (1, -1):
            p = on_face(side * 0.075 * H, 0.085 * H, 0.004)
            piv = S.empty(f"{n}.brow", self.neck, p)
            S.capsule(f"{n}.brow", 0.012 * H, 0.04 * H, hair_color if hair != "none" else "charcoal", piv,
                      rot=(0, _deg(90), 0))
            self.brows[side] = piv

        # mouth with smile and frown shapes
        mp = on_face(0, -0.068 * H, 0.004)
        self.mouth = S.empty(f"{n}.mouthpivot", self.neck, mp)
        m = S.ellipsoid(f"{n}.mouth", 0.042 * H, 0.02 * H, 0.012 * H, look.plastic("#5b1e2c", 0.5, 0.2), self.mouth)
        m.shape_key_add(name="Basis")
        for name, sign in (("smile", 1), ("frown", -1)):
            sk = m.shape_key_add(name=name)
            for v in sk.data:
                t = (v.co.x / (0.042 * H)) ** 2
                v.co.z += sign * 0.022 * H * t - sign * 0.004 * H
        self.mouth_mesh = m
        if nose:
            S.sphere(f"{n}.nose", 0.024 * H, skin, self.neck, at=on_face(0, -0.015 * H, 0.016))
        if blush:
            for side in (1, -1):
                S.ellipsoid(f"{n}.blush", 0.034 * H, 0.008 * H, 0.02 * H, look.plastic("#f19aa6", 0.6, 0.1),
                            self.neck, at=on_face(side * 0.115 * H, -0.035 * H, 0.002), rot=(0, 0, _deg(side * 40)))

        self._hair(hair, hair_color, hc, hr, H)
        self._extras(extras, hair_color, hc, hr, H, on_face, neck_z, r, cz, length, top)

    def _hair(self, style, color, hc, hr, H):
        if style == "none":
            return
        n, S = self.name, shapes
        cap = S.sphere(f"{n}.hair", hr * 1.06, color, self.neck, at=hc, segments=40)
        # keep everything above a plane that is high at the forehead and low at the back
        # the hairline sits above the eyebrows at the front and low at the back
        b, z0 = (0.55, 0.05) if style in ("short", "spiky", "mohawk") else (0.6, 0.0)
        S.cut_below(cap, (0, 0, z0 * hr), (0, b, 1))
        if style == "mohawk":
            cap.scale = (0.35, 1.0, 1.0)
            cap.location.z += 0.03 * H
        if style == "bob":
            for side in (1, -1):
                S.ellipsoid(f"{n}.hair", hr * 0.42, hr * 0.62, hr * 0.62, color, self.neck,
                            at=hc + Vector((side * hr * 0.72, hr * 0.12, -hr * 0.28)))
            S.ellipsoid(f"{n}.hair", hr * 0.85, hr * 0.5, hr * 0.62, color, self.neck,
                        at=hc + Vector((0, hr * 0.55, -hr * 0.3)))
        elif style == "long":
            S.ellipsoid(f"{n}.hair", hr * 0.95, hr * 0.45, hr * 1.25, color, self.neck,
                        at=hc + Vector((0, hr * 0.6, -hr * 0.65)))
        elif style == "ponytail":
            S.ellipsoid(f"{n}.hair", hr * 0.3, hr * 0.3, hr * 0.8, color, self.neck,
                        at=hc + Vector((0, hr * 1.15, -hr * 0.25)), rot=(_deg(-25), 0, 0))
        elif style == "bun":
            S.sphere(f"{n}.hair", hr * 0.42, color, self.neck, at=hc + Vector((0, hr * 0.25, hr * 1.02)))
        elif style == "spiky":
            for i in range(7):
                a = _deg(-60 + i * 20)
                S.cylinder(f"{n}.spike", hr * 0.2, hr * 0.5, color, self.neck,
                           at=hc + Vector((math.sin(a) * hr * 0.6, hr * 0.1, hr * 0.78)),
                           rot=(_deg(10), math.sin(a) * 0.9, 0), r2=0.0, bevel=0)
        elif style == "curly":
            for i in range(14):
                a = 2 * math.pi * i / 14
                S.sphere(f"{n}.curl", hr * 0.3, color, self.neck,
                         at=hc + Vector((math.cos(a) * hr * 0.85, math.sin(a) * hr * 0.6 + hr * 0.25,
                                         hr * 0.55 + 0.15 * hr * math.sin(3 * a))))

    def _extras(self, extras, hair_color, hc, hr, H, on_face, neck_z, r, cz, length, top):
        n, S = self.name, shapes
        for e in extras:
            if e == "glasses":
                frame = look.plastic("#222222", 0.3, 0.6)
                for side in (1, -1):
                    S.torus(f"{n}.glasses", 0.047 * H, 0.007 * H, frame, self.neck,
                            at=on_face(side * 0.075 * H, 0.02 * H, -0.02), rot=(_deg(90), 0, 0))
                S.capsule(f"{n}.glasses", 0.006 * H, 0.04 * H, frame, self.neck,
                          at=on_face(0, 0.03 * H, -0.03), rot=(0, _deg(90), 0))
            elif e == "hat":
                S.cylinder(f"{n}.hat", hr * 1.45, 0.02 * H, "charcoal", self.neck, at=hc + Vector((0, 0, hr * 0.62)))
                S.cylinder(f"{n}.hat", hr * 0.92, hr * 0.75, "charcoal", self.neck, at=hc + Vector((0, 0, hr * 0.62)),
                           r2=hr * 0.88)
            elif e == "cap":
                capm = S.sphere(f"{n}.cap", hr * 1.08, "red", self.neck, at=hc)
                S.cut_below(capm, (0, 0, hr * 0.2), (0, 0.2, 1))
                S.cylinder(f"{n}.cap", hr * 0.6, 0.015 * H, "red", self.neck,
                           at=hc + Vector((0, -hr * 0.85, hr * 0.38)), rot=(_deg(-8), 0, 0))
            elif e == "scarf":
                S.torus(f"{n}.scarf", r * 0.72, 0.045 * H, "red", self.body, at=(0, 0, neck_z - 0.02 * H))
            elif e == "tie":
                S.box(f"{n}.tie", 0.035 * H, 0.012 * H, 0.17 * H, "red", self.body,
                      at=(0, -r * 0.84, neck_z - 0.22 * H), rot=(_deg(-12), 0, 0), bevel=0.005 * H)
            elif e == "bow":
                for side in (1, -1):
                    S.ellipsoid(f"{n}.bow", hr * 0.28, hr * 0.12, hr * 0.2, "pink", self.neck,
                                at=hc + Vector((side * hr * 0.3, -hr * 0.1, hr * 0.98)), rot=(0, _deg(side * 20), 0))
            elif e == "beard":
                S.ellipsoid(f"{n}.beard", hr * 0.7, hr * 0.45, hr * 0.45, hair_color, self.neck,
                            at=hc + Vector((0, -hr * 0.55, -hr * 0.62)))
            elif e == "moustache":
                for side in (1, -1):
                    S.ellipsoid(f"{n}.moustache", 0.038 * H, 0.014 * H, 0.014 * H, hair_color, self.neck,
                                at=on_face(side * 0.032 * H, -0.045 * H, -0.006), rot=(0, _deg(side * 12), 0))
            elif e == "headphones":
                S.torus(f"{n}.headphones", hr * 1.08, 0.014 * H, "charcoal", self.neck, at=hc,
                        rot=(_deg(90), 0, _deg(90)), arc=180)
                for side in (1, -1):
                    S.cylinder(f"{n}.headphones", 0.05 * H, 0.04 * H, "charcoal", self.neck,
                               at=hc + Vector((side * hr * 1.0, 0, 0)), rot=(0, _deg(90 * side), 0))

    # ------------------------------------------------------------------ geometry queries
    def position(self, t):
        """Where the character's feet are at `t` seconds, as (x, y)."""
        loc = value_at(self.root, "location", t)
        return Vector((loc[0], loc[1]))

    def heading(self, t):
        return value_at(self.root, "rotation_euler", t)[2]

    def head_point(self, t):
        """World position of the middle of the face at `t` (for cameras and look-ats)."""
        loc = value_at(self.root, "location", t)
        hz = value_at(self.hips, "location", t)[2]
        return Vector((loc[0], loc[1], loc[2] + hz + self.top_z + self.head_center.z))

    def visible(self, t):
        return value_at(self.root, "scale", t)[0] > 0.01

    def forward(self, t):
        h = self.heading(t)
        return Vector((math.sin(h), -math.cos(h)))

    # ------------------------------------------------------------------ timing
    def _start(self, at):
        return self.scene._start(self, at)

    def _end(self, end, wait=True):
        self.scene._end(self, end, wait)
        return self

    def _point(self, where, t):
        return self.scene._resolve(where, t, me=self)

    # ------------------------------------------------------------------ staging
    def place(self, where, facing=None, at=None):
        """Put the character somewhere instantly (use at the start of a scene)."""
        t = 0.0 if at is None else at
        p = self._point(where, t)
        key(self.root, "location", t, (p.x, p.y, 0), "cut")
        self._key_heading(t, self._facing_value(facing, p, t, where), "cut")
        return self

    def enter(self, where, facing=None, at=None):
        """Appear at `where` (usually a door) at this moment; the character is hidden until then."""
        t = self._start(at)
        if t > 0:
            key(self.root, "scale", 0, 0.0, "cut")
        p = self._point(where, t)
        key(self.root, "location", t, (p.x, p.y, 0), "cut")
        key(self.root, "scale", t, 1.0, "cut")
        self._key_heading(t, self._facing_value(facing, p, t, where), "cut")
        return self._end(t + 0.1)

    def leave(self, at=None):
        """Disappear at this moment (after walking to a door, say)."""
        t = self._start(at)
        hold(self.root, "scale", t, ease="cut")
        key(self.root, "scale", t + 0.05, 0.0, "cut")
        return self._end(t + 0.05)

    def _facing_value(self, facing, p, t, where=None):
        if facing is None:
            mark = self.scene.set.marks.get(where) if isinstance(where, str) and self.scene.set else None
            if mark is not None and mark.facing is not None:
                return mark.facing
            return self.heading(t)
        if isinstance(facing, (int, float)):
            return _deg(facing)
        named = {"camera": 0.0, "front": 0.0, "back": math.pi, "away": math.pi,
                 "left": -math.pi / 2, "right": math.pi / 2}
        if facing in named:  # screen left/right as seen by the default camera
            return named[facing]
        q = self._point(facing, t)
        return heading_to(q.x - p.x, q.y - p.y)

    def _key_heading(self, t, h, ease="smooth"):
        cur = self.heading(t)
        h = cur + _wrap(h - cur)
        key(self.root, "rotation_euler", t, (0, 0, h), ease)
        return h

    def turn_to(self, target, at=None, wait=True):
        """Turn the whole body towards a character, mark or direction ("camera", "left", ...)."""
        t = self._start(at)
        p = self.position(t)
        h = self._facing_value(target, p, t)
        hold(self.root, "rotation_euler", t)
        dur = 0.25 + 0.3 * abs(_wrap(h - self.heading(t))) / math.pi
        self._key_heading(t + dur, h)
        self._reset_head(t, t + dur * 0.6)
        return self._end(t + dur, wait)

    def look_at(self, target, at=None, wait=False):
        """Turn just the head towards a character or mark (up to 70 degrees); the body stays."""
        t = self._start(at)
        p = self.position(t)
        q = self._point(target, t)
        rel = _wrap(heading_to(q.x - p.x, q.y - p.y) - self.heading(t))
        if abs(rel) > _deg(70):
            return self.turn_to(target, at=t, wait=wait)
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.3, (cur[0], cur[1], rel))
        return self._end(t + 0.3, wait)

    def look_forward(self, at=None, wait=False):
        t = self._start(at)
        self._reset_head(t, t + 0.3)
        return self._end(t + 0.3, wait)

    def _reset_head(self, t0, t1):
        hold(self.neck, "rotation_euler", t0)
        cur = value_at(self.neck, "rotation_euler", t0)
        key(self.neck, "rotation_euler", t1, (cur[0], cur[1], 0.0))

    # ------------------------------------------------------------------ moving
    def walk_to(self, where, speed="normal", facing=None, at=None, wait=True):
        """Walk to a mark, prop or character (stopping in front of them), going round furniture.

        speed: "slow", "normal", "fast" or "run". facing: what to face on arrival.
        """
        if self.sitting:
            self.stand(at=at)
            at = None
        t = self._start(at)
        p0 = self.position(t)
        p1 = self.scene._resolve(where, t, me=self, approach=True)
        path = self.scene.set.route(p0, p1) if self.scene.set else [p0, p1]
        sp = SPEEDS.get(speed, speed) if not isinstance(speed, (int, float)) else speed
        run = sp >= 1.8
        H = self.H
        stride = (0.42 if run else 0.32) * H * min(sp, 1.5) ** 0.3
        step_t = (0.28 if run else 0.36) / max(0.6, sp) ** 0.6
        total = sum((path[i + 1] - path[i]).length for i in range(len(path) - 1))
        if total < 0.05:
            if facing is not None:
                return self.turn_to(facing, at=t, wait=wait)
            return self._end(t, wait)
        n_steps = max(2, math.ceil(total / stride))
        dur = n_steps * step_t

        self._reset_head(t, t + 0.25)
        # first turn on the spot, then walk; heading follows the path's corners
        first = path[1] - path[0]
        hold(self.root, "rotation_euler", t)
        h = self._key_heading(t + 0.22, heading_to(first.x, first.y))
        ws = t + 0.18
        hold(self.root, "location", ws, ease="linear")
        dist = 0.0
        for i in range(1, len(path)):
            seg = path[i] - path[i - 1]
            dist += seg.length
            ti = ws + dur * dist / total
            ease = "linear" if i < len(path) - 1 else "ease_out"
            key(self.root, "location", ti, (path[i].x, path[i].y, 0), ease)
            if i < len(path) - 1:
                nxt = path[i + 1] - path[i]
                key(self.root, "rotation_euler", max(ws + 0.25, ti - 0.12), (0, 0, h))
                h = self._key_heading(ti + 0.12, heading_to(nxt.x, nxt.y))
        end = ws + dur

        # legs, arms and bounce, one key per footfall
        A = _deg(38 if run else 26)
        lean = _deg(10 if run else 2)
        base = self.hip_z
        for leg in self.legs.values():
            hold(leg, "rotation_euler", ws)
        for arm in self.arms.values():
            hold(arm, "rotation_euler", ws)
        hold(self.hips, "location", ws)
        hold(self.body, "rotation_euler", ws)
        key(self.body, "rotation_euler", ws + step_t, (-lean, 0, 0))
        for i in range(n_steps + 1):
            ti = ws + i * step_t
            amp = 0.0 if i in (0, n_steps) else A
            sgn = 1 if i % 2 else -1
            key(self.legs[1], "rotation_euler", ti, (-sgn * amp, 0, 0))
            key(self.legs[-1], "rotation_euler", ti, (sgn * amp, 0, 0))
            key(self.arms[1], "rotation_euler", ti, (sgn * amp * 0.9, 0, 0))
            key(self.arms[-1], "rotation_euler", ti, (-sgn * amp * 0.9, 0, 0))
            if i < n_steps:
                key(self.hips, "location", ti, (0, 0, base - 0.018 * H * (1.6 if run else 1)))
                key(self.hips, "location", ti + step_t / 2, (0, 0, base + (0.03 if run else 0.012) * H))
        key(self.hips, "location", end, (0, 0, base))
        key(self.body, "rotation_euler", end, (0, 0, 0))
        self.scene._event("move", self, t, end)
        if facing is not None:
            self._end(end, wait)
            return self.turn_to(facing, at=end, wait=wait)
        mark = self.scene.set.marks.get(where) if isinstance(where, str) and self.scene.set else None
        if mark is not None and mark.facing is not None:
            self._end(end, wait)
            return self.turn_to(math.degrees(mark.facing), at=end, wait=wait)
        return self._end(end, wait)

    def run_to(self, where, **kw):
        return self.walk_to(where, speed="run", **kw)

    def sit(self, on, at=None, wait=True, already=False):
        """Walk to a chair, sofa or bench, turn round and sit down.

        already=True: they are sitting there when the scene starts (no walking)."""
        seat = self.scene.set.seat(on) if self.scene.set else None
        if seat is None:
            seats = sorted(self.scene.set.seats) if self.scene.set else []
            raise ValueError(f"{self.name}.sit({on!r}): no seat called {on!r} in this set; seats: {seats}")
        if already:
            t = 0.0 if at is None else at
            key(self.root, "location", t, (seat.at.x, seat.at.y, 0), "cut")
            self._key_heading(t, seat.facing, "cut")
            key(self.hips, "location", t, (0, 0, seat.height + 0.04 * self.H), "cut")
            for leg in self.legs.values():
                key(leg, "rotation_euler", t, (_deg(-80), 0, 0), "cut")
            self.sitting = seat
            return self
        self.walk_to(seat.front, at=at)
        t = self._start(None)
        self._key_heading(t + 0.3, seat.facing)
        hold(self.root, "location", t + 0.3)
        hold(self.hips, "location", t + 0.3)
        key(self.root, "location", t + 0.75, (seat.at.x, seat.at.y, 0))
        key(self.hips, "location", t + 0.75, (0, 0, seat.height + 0.04 * self.H))
        for leg in self.legs.values():
            hold(leg, "rotation_euler", t + 0.3)
            key(leg, "rotation_euler", t + 0.75, (_deg(-80), 0, 0))
        self.sitting = seat
        self.scene._event("move", self, t, t + 0.75)
        return self._end(t + 0.75, wait)

    def stand(self, at=None, wait=True):
        if not self.sitting:
            return self
        seat = self.sitting
        t = self._start(at)
        hold(self.root, "location", t)
        hold(self.hips, "location", t)
        key(self.root, "location", t + 0.45, (seat.front.x, seat.front.y, 0))
        key(self.hips, "location", t + 0.45, (0, 0, self.hip_z))
        for leg in self.legs.values():
            hold(leg, "rotation_euler", t)
            key(leg, "rotation_euler", t + 0.45, (0, 0, 0))
        self.sitting = None
        return self._end(t + 0.45, wait)

    # ------------------------------------------------------------------ face
    def feel(self, mood, at=None, wait=False):
        """Change expression: neutral, happy, excited, sad, angry, surprised, worried, scared, smug, sleepy."""
        if mood not in MOODS:
            raise ValueError(f"{self.name}.feel({mood!r}): use one of {sorted(MOODS)}")
        t = self._start(at)
        tilt, lift, smile, frown, eye, mopen, head_tilt = MOODS[mood]
        t1 = t + 0.25
        for side, brow in self.brows.items():
            hold(brow, "rotation_euler", t)
            hold(brow, "location", t)
            key(brow, "rotation_euler", t1, (0, _deg(tilt) * side, 0))
            base = brow.get("z0", brow.location.z)
            brow["z0"] = base
            loc = value_at(brow, "location", t)
            key(brow, "location", t1, (loc[0], loc[1], base + lift * self.H))
        for e in self.eyes:
            hold(e, "scale", t)
            key(e, "scale", t1, (eye, 1, eye))
            e["open"] = eye
        sk = self.mouth_mesh.data.shape_keys.key_blocks
        for name, v in (("smile", smile), ("frown", frown)):
            hold(sk[name], "value", t)
            key(sk[name], "value", t1, v)
        hold(self.mouth, "scale", t)
        key(self.mouth, "scale", t1, (1 - 0.3 * mopen, 1, 1 + 2.2 * mopen))
        self.mouth["rest"] = mopen
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t1, (_deg(head_tilt), cur[1], cur[2]))
        self.mood = mood
        return self._end(t1, wait)

    # ------------------------------------------------------------------ talking
    def say(self, line, mood=None, to=None, at=None, wait=True):
        """Speak a line: mouth, head and subtitles are animated; with a voice set up it's also heard.

        to: who they're talking to (they look at them, and the camera uses it for over-the-shoulder shots).
        """
        t = self._start(at)
        if to is not None:
            self.look_at(to, at=t, wait=False)
        if mood:
            self.feel(mood, at=t, wait=False)
        speech = self.scene.voices.speak(self, line)
        t0 = t + 0.15
        if speech is not None:
            dur = speech.duration
            self._lipsync_envelope(t0, speech)
        else:
            dur = self._lipsync_text(t0, line)
        listener = self.scene.character(to) if isinstance(to, str) else to
        if listener is None:
            listener = self.scene._nearest(self, t)
        self.scene._event("say", self, t0, t0 + dur, line=line, listener=listener, audio=speech)
        return self._end(t0 + dur + 0.3, wait)

    def _mouth_key(self, t, open_amt, round_amt=0.0):
        rest = self.mouth.get("rest", 0.0)
        o = max(open_amt, rest)
        key(self.mouth, "scale", t, (1 - 0.3 * o - 0.35 * round_amt, 1, 1 + 2.2 * o))

    def _lipsync_text(self, t0, line):
        """No audio: animate the mouth from the words (one open/close per syllable)."""
        hold(self.mouth, "scale", t0 - 0.05)
        t = t0
        words = re.findall(r"[A-Za-z']+|[.,!?;:]", line)
        nod_done = False
        for w in words:
            if w in ",;:":
                self._mouth_key(t, 0.0)
                t += 0.22
                continue
            if w in ".!?":
                self._mouth_key(t, 0.0)
                if w == "?":
                    self._head_tilt(t - 0.3)
                t += 0.38
                continue
            groups = re.findall(r"[aeiouy]+", w.lower()) or ["a"]
            for g in groups:
                rnd = 1.0 if g[0] in "ou" else 0.0
                self._mouth_key(t + 0.02, 0.0)
                self._mouth_key(t + 0.09, 0.45 + 0.5 * self.rng.random(), rnd)
                t += 0.19
            if not nod_done and len(groups) > 1:
                self._nod(t - 0.3, 5)
                nod_done = True
            t += 0.04
        self._mouth_key(t + 0.05, 0.0)
        return t - t0

    def _lipsync_envelope(self, t0, speech):
        hold(self.mouth, "scale", t0 - 0.05)
        step = 2 / self.scene.fps
        for i, amp in enumerate(speech.envelope(step)):
            self._mouth_key(t0 + i * step, min(1.0, amp * 1.6))
        self._mouth_key(t0 + speech.duration + 0.05, 0.0)

    def _nod(self, t, deg=8):
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.15, (cur[0] + _deg(deg), cur[1], cur[2]))
        key(self.neck, "rotation_euler", t + 0.35, tuple(cur))

    def _head_tilt(self, t, deg=10):
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.2, (cur[0], cur[1] + _deg(deg), cur[2]))
        key(self.neck, "rotation_euler", t + 0.9, tuple(cur))

    # ------------------------------------------------------------------ gestures
    def _arm(self, side, t, rot, ease="smooth"):
        key(self.arms[side], "rotation_euler", t, rot, ease)

    def _arms_rest(self, t):
        for s in (1, -1):
            self._arm(s, t, (0, 0, 0))

    def do(self, gesture, target=None, at=None, wait=True):
        """Play a gesture: wave, nod, shake_head, shrug, point (at target), jump, cheer, facepalm, clap,
        think, bow, stomp."""
        if gesture not in GESTURES:
            raise ValueError(f"{self.name}.do({gesture!r}): use one of {GESTURES}")
        t = self._start(at)
        for s in (1, -1):
            hold(self.arms[s], "rotation_euler", t)
        if gesture == "wave":
            up = _deg(-150)
            self._arm(1, t + 0.3, (0, up, 0))
            for i in range(4):
                self._arm(1, t + 0.45 + i * 0.22, (0, up + _deg(22 if i % 2 else -22), 0))
            self._arm(1, t + 1.5, (0, 0, 0))
            end = t + 1.5
        elif gesture == "nod":
            self._nod(t, 12)
            self._nod(t + 0.35, 10)
            end = t + 0.8
        elif gesture == "shake_head":
            hold(self.neck, "rotation_euler", t)
            cur = value_at(self.neck, "rotation_euler", t)
            for i, d in enumerate((-20, 20, -16, 12, 0)):
                key(self.neck, "rotation_euler", t + 0.18 * (i + 1), (cur[0], cur[1], cur[2] + _deg(d)))
            end = t + 1.0
        elif gesture == "shrug":
            for s in (1, -1):
                self._arm(s, t + 0.25, (_deg(-35), _deg(-55 * s), 0))
                self._arm(s, t + 0.9, (_deg(-35), _deg(-55 * s), 0))
            self._head_tilt(t, 12)
            hold(self.hips, "location", t)
            key(self.hips, "location", t + 0.3, (0, 0, self.hip_z + 0.02 * self.H))
            key(self.hips, "location", t + 0.9, (0, 0, self.hip_z))
            self._arms_rest(t + 1.2)
            end = t + 1.2
        elif gesture == "point":
            if target is not None:
                self.turn_to(target, at=t, wait=False)
            self._arm(1, t + 0.35, (_deg(-90), _deg(-8), 0))
            self._arm(1, t + 1.4, (_deg(-90), _deg(-8), 0))
            self._arm(1, t + 1.8, (0, 0, 0))
            end = t + 1.8
        elif gesture in ("jump", "cheer"):
            hold(self.hips, "location", t)
            z = self.hip_z
            key(self.hips, "location", t + 0.15, (0, 0, z - 0.04 * self.H))
            key(self.hips, "location", t + 0.4, (0, 0, z + 0.22 * self.H), "ease_out")
            key(self.hips, "location", t + 0.65, (0, 0, z - 0.03 * self.H), "ease_in")
            key(self.hips, "location", t + 0.8, (0, 0, z))
            if gesture == "cheer":
                for s in (1, -1):
                    self._arm(s, t + 0.3, (0, _deg(-160 * s), 0))
                    self._arm(s, t + 1.0, (0, _deg(-150 * s), 0))
                self._arms_rest(t + 1.3)
            end = t + (1.3 if gesture == "cheer" else 0.9)
        elif gesture == "facepalm":
            self._arm(1, t + 0.35, (_deg(-150), _deg(30), 0))
            self._arm(1, t + 1.3, (_deg(-150), _deg(30), 0))
            self._nod(t + 0.2, 14)
            self._arm(1, t + 1.7, (0, 0, 0))
            end = t + 1.7
        elif gesture == "clap":
            for i in range(4):
                tc = t + 0.25 + i * 0.25
                for s in (1, -1):
                    self._arm(s, tc, (_deg(-70), _deg(28 * s), 0))
                    self._arm(s, tc + 0.12, (_deg(-70), _deg(10 * s), 0))
            self._arms_rest(t + 1.5)
            end = t + 1.5
        elif gesture == "think":
            self._arm(1, t + 0.4, (_deg(-125), _deg(28), 0))
            self._arm(1, t + 1.8, (_deg(-125), _deg(28), 0))
            self._head_tilt(t + 0.2, 12)
            self._arm(1, t + 2.2, (0, 0, 0))
            end = t + 2.2
        elif gesture == "bow":
            hold(self.body, "rotation_euler", t)
            key(self.body, "rotation_euler", t + 0.4, (_deg(-35), 0, 0))
            key(self.body, "rotation_euler", t + 0.9, (_deg(-35), 0, 0))
            key(self.body, "rotation_euler", t + 1.3, (0, 0, 0))
            end = t + 1.3
        elif gesture == "stomp":
            for i, s in enumerate((1, -1, 1)):
                tl = t + i * 0.3
                hold(self.legs[s], "rotation_euler", tl)
                key(self.legs[s], "rotation_euler", tl + 0.12, (_deg(-30), 0, 0))
                key(self.legs[s], "rotation_euler", tl + 0.24, (0, 0, 0), "ease_in")
            for sd in (1, -1):
                self._arm(sd, t + 0.2, (0, _deg(-25 * sd), 0))
            self._arms_rest(t + 1.0)
            end = t + 1.0
        self.scene._event("gesture", self, t, end, gesture=gesture)
        return self._end(end, wait)

    # ------------------------------------------------------------------ life
    def _alive(self, length):
        """Blinks and breathing for the whole scene, added when the scene is finished."""
        t = self.rng.uniform(0.6, 2.0)
        while t < length - 0.3:
            for e in self.eyes:
                o = value_at(e, "scale", t)[0]
                if o < 0.2:
                    continue
                key(e, "scale", t, (o, 1, o))
                key(e, "scale", t + 0.06, (o, 1, 0.08))
                key(e, "scale", t + 0.14, (o, 1, o))
            t += self.rng.uniform(2.2, 4.8)
        t = 0.0
        while t < length:
            key(self.body, "scale", t, (1, 1, 1))
            key(self.body, "scale", t + 0.9, (1.012, 1.012, 1.02))
            t += 1.9
