"""Characters: figures built from a short description, and the verbs that make them act.

    mia = s.cast("mia")                     # from cast/mia.toml
    mia.enter("door").walk_to("table").say("Who ate the last cookie?", mood="angry")

`Character` is the base class; the built-in look is `ToyFigure` (type = "toy"): a jointed vinyl figure
with a separate head, body, arms and legs on pivots. Nothing is skinned, so poses can't tear.

Make a new kind of character by subclassing and overriding any build step:

    class Robot(dr.Character):
        description = "A friendly tin robot"
        params = dr.Character.params + [dr.Param("metal", "color", default="#9aa4ad")]

        def build_head(self):                      # a box head instead of a ball
            ...
        def face_point(self, x, z, inset=0.006):   # the face is flat, so features sit on a plane
            ...

Then use it in a cast file with `type = "robot"`. Build steps, in order: proportions, build_rig,
build_legs, build_body, build_arms, build_head, build_face, build_hair, build_extras. Each step can
use what earlier steps set up (see the attributes listed in `proportions`).

Facing: a character at rotation 0 faces -Y (towards the default camera). Its left hand is at +X.
"""
import math
import random
import re

from mathutils import Vector

from . import keys, look, plugins, shapes
from .keys import hold, key, value_at
from .plugins import Param, Plugin

BODIES = ("bean", "round", "tall", "kid")
SPEEDS = {"slow": 0.65, "normal": 1.0, "fast": 1.45, "run": 2.1}


def _deg(d):
    return math.radians(d)


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def heading_to(dx, dy):
    """Rotation about Z that makes a character face the direction (dx, dy)."""
    return math.atan2(dx, -dy)


class Stride:
    """Where a walking character's root is at any moment of a walk: a path walked at constant speed
    from `start` for `duration` seconds (used to plan footsteps)."""

    def __init__(self, path, start, duration, total):
        self.path, self.start, self.duration, self.total = path, start, duration, total
        self.end = start + duration

    def at(self, t):
        """(position Vector(x, y), heading) at time t."""
        f = min(1.0, max(0.0, (t - self.start) / self.duration)) if self.duration > 0 else 1.0
        d = f * self.total
        for i in range(1, len(self.path)):
            seg = self.path[i] - self.path[i - 1]
            L = seg.length
            if d <= L or i == len(self.path) - 1:
                u = min(1.0, d / L) if L > 1e-9 else 1.0
                return self.path[i - 1] + seg * u, heading_to(seg.x, seg.y)
            d -= L
        return self.path[-1], 0.0


class Character(Plugin):
    kind = "character"
    abstract = True
    params = [
        Param("name", "text", label="Name"),
        Param("height", "number", default=1.0, min=0.7, max=1.3, step=0.05),
        Param("body", "choice", default="bean", choices=BODIES),
        Param("skin", "skin", default="skin2"),
        Param("hair", "hair", default="short"),
        Param("hair_color", "color", default="brown", label="Hair colour"),
        Param("top", "color", default="blue"),
        Param("bottom", "color", default="navy", label="Trousers"),
        Param("shoes", "color", default="charcoal"),
        Param("outfit", "choice", default="shirt", choices=("shirt", "dress")),
        Param("eyes", "choice", default="normal", choices=("small", "normal", "big")),
        Param("extras", "extras", default=[]),
        Param("blush", "bool", default=True),
        Param("nose", "bool", default=True),
        Param("voice", "voice"),
    ]

    drawing = None    # name of a live drawing the studio can show while editing (None: render a portrait)
    default_capabilities = ("walk", "arms", "swing_legs", "face")

    @classmethod
    def describe_extra(cls):
        return {"drawing": cls.drawing, "capabilities": list(cls.default_capabilities)}

    def __init__(self, name, scene=None, **spec):
        self.name = name
        self.scene = scene
        values = self.defaults()
        values.update({k: v for k, v in spec.items() if v is not None})
        values.pop("name", None)
        values.pop("type", None)
        self.spec = values
        self.voice = values.get("voice")
        self.busy = 0.0
        self.mood = "neutral"
        self.sitting = None
        self.rng = random.Random(name)
        self.validate()
        self.proportions()
        self.build()

    # ------------------------------------------------------------------ spec helpers
    @property
    def capabilities(self):
        """What this body can do; gestures and actions check it (see Gesture.needs)."""
        return set(self.default_capabilities)

    def prepare(self, length):
        """Called once the scene is complete, before rendering (creatures plant unplanted feet here)."""

    def get(self, key_, default=None):
        return self.spec.get(key_, default)

    def color(self, key_, default="white"):
        """A colour from the spec (by key), for materials."""
        return self.spec.get(key_) or default

    def validate(self):
        for p in self.params:
            v = self.spec.get(p.name)
            if v is None:
                continue
            if p.type == "choice" and p.choices and v not in p.choices:
                raise ValueError(f"{self.name}: {p.name} {v!r} unknown; use one of {list(p.choices)}")
        if "hair" in self.spec:
            plugins.get("hair", self.spec["hair"])
        for e in self.spec.get("extras", []) or []:
            plugins.get("extra", e)

    # ------------------------------------------------------------------ construction
    def proportions(self):
        """Work out sizes. Sets: H (height scale), hip_z, body_r, body_len, body_cz, neck_z, top_z,
        shoulder_z, hr (head radius), hc (head centre, relative to the neck)."""
        body = self.get("body", "bean")
        self.H = H = float(self.get("height", 1.0)) * (0.75 if body == "kid" else 1.0)
        self.hip_z = 0.29 * H
        self.body_r = {"round": 0.19, "tall": 0.15}.get(body, 0.165) * H
        self.body_len = {"round": 0.08, "tall": 0.2}.get(body, 0.12) * H
        self.body_cz = -0.06 * H + self.body_r + self.body_len / 2
        self.neck_z = self.top_z = self.body_cz + self.body_len / 2 + self.body_r * 0.82
        self.shoulder_z = self.body_cz + self.body_len / 2 + self.body_r * 0.25
        self.hr = self.head_r = (0.21 if body == "kid" else 0.17 if body == "tall" else 0.19) * H
        self.hc = self.head_center = Vector((0, 0, self.hr * 0.62))

    def build(self):
        """Run the build steps. Override a step to change one part; override this to change the order."""
        self.build_rig()
        self.build_legs()
        self.build_body()
        self.build_arms()
        self.build_head()
        self.build_face()
        self.build_hair()
        self.build_extras()

    def build_rig(self):
        """The pivots everything hangs from: root (feet), hips, body, neck. Animation moves these."""
        n = self.name
        self.root = shapes.empty(n)
        self.root.empty_display_size = 0.3
        self.hips = shapes.empty(f"{n}.hips", self.root, (0, 0, self.hip_z))
        self.body = shapes.empty(f"{n}.body", self.hips)
        self.neck = shapes.empty(f"{n}.neck", self.body, (0, 0, self.neck_z))

    def build_legs(self):
        """Sets self.legs = {1: left pivot, -1: right pivot}; legs swing about X."""
        H, n = self.H, self.name
        shoe_h, leg_r = 0.07 * H, 0.055 * H
        self.legs = {}
        for side in (1, -1):
            piv = shapes.empty(f"{n}.leg.{'L' if side > 0 else 'R'}", self.hips, (side * 0.075 * H, 0, 0))
            shapes.capsule(f"{n}.thigh", leg_r, max(0.01, self.hip_z - shoe_h * 0.6 - 2 * leg_r), self.color("bottom"),
                           piv, hang=True)
            shapes.box(f"{n}.shoe", 0.125 * H, 0.18 * H, shoe_h, self.color("shoes"), piv,
                       at=(0, -0.025 * H, -self.hip_z), bevel=0.03 * H)
            self.legs[side] = piv

    def build_body(self):
        H, n, r, length, cz = self.H, self.name, self.body_r, self.body_len, self.body_cz
        top = self.color("top")
        upper = shapes.capsule(f"{n}.top", r, length, top, self.body, at=(0, 0, cz), squash=(1, 0.86))
        shapes.cut_below(upper, (0, 0, 0.03 * H - cz), (0, 0, 1))
        if self.get("outfit") == "dress":
            shapes.cylinder(f"{n}.skirt", r * 1.02, 0.2 * H, top, self.body, at=(0, 0, -0.14 * H), r2=r * 0.8,
                            bevel=0.01 * H)
        else:
            lower = shapes.capsule(f"{n}.pants", r * 0.995, length, self.color("bottom"), self.body, at=(0, 0, cz),
                                   squash=(1, 0.86))
            shapes.cut_below(lower, (0, 0, 0.03 * H - cz), (0, 0, -1))

    def build_arms(self):
        """Sets self.arms = {1: left pivot, -1: right pivot} at the shoulders."""
        H, n = self.H, self.name
        self.arms = {}
        for side in (1, -1):
            piv = shapes.empty(f"{n}.arm.{'L' if side > 0 else 'R'}", self.body, (side * self.body_r * 0.86, 0, self.shoulder_z))
            arm = shapes.capsule(f"{n}.arm", 0.047 * H, 0.15 * H, self.color("top"), piv, rot=(0, _deg(-12 * side), 0),
                                 hang=True)
            shapes.sphere(f"{n}.hand", 0.058 * H, self.color("skin"), arm, at=(0, 0, -0.27 * H))
            self.arms[side] = piv

    def build_head(self):
        shapes.sphere(f"{self.name}.head", self.hr, self.color("skin"), self.neck, at=self.hc)

    def face_point(self, x, z, inset=0.006):
        """A point on the front of the head, `x` across and `z` up from the head centre (neck space)."""
        hr = self.hr
        y = -math.sqrt(max(0.0, hr * hr - x * x - z * z)) + inset * self.H
        return Vector((x, y, z)) + self.hc

    def head_top(self):
        return self.hc + Vector((0, 0, self.hr))

    def build_face(self):
        """Eyes, brows, mouth (with smile/frown shapes), nose and cheeks. Sets self.eyes, self.brows,
        self.mouth (pivot) and self.mouth_mesh; moods and talking animate these."""
        H, n = self.H, self.name
        es = {"small": 0.8, "normal": 1.0, "big": 1.3}.get(self.get("eyes"), 1.0)
        self.eyes = []
        for side in (1, -1):
            piv = shapes.empty(f"{n}.eye", self.neck, self.face_point(side * 0.075 * H, 0.02 * H, 0.004))
            eye = shapes.ellipsoid(f"{n}.eye", 0.03 * H * es, 0.02 * H, 0.043 * H * es,
                                   look.plastic(self.eye_color(), 0.12, 0.9), piv)
            shapes.sphere(f"{n}.glint", 0.011 * H * es, look.plastic("white", emission=1.5), eye,
                          at=(0.01 * H * es, -0.016 * H, 0.016 * H * es))
            self.eyes.append(piv)
        self.brows = {}
        brow_color = self.color("hair_color") if self.get("hair", "short") != "none" else "charcoal"
        for side in (1, -1):
            piv = shapes.empty(f"{n}.brow", self.neck, self.face_point(side * 0.075 * H, 0.085 * H, 0.004))
            shapes.capsule(f"{n}.brow", 0.012 * H, 0.04 * H, brow_color, piv, rot=(0, _deg(90), 0))
            self.brows[side] = piv
        self.mouth = shapes.empty(f"{n}.mouthpivot", self.neck, self.face_point(0, -0.068 * H, 0.004))
        m = shapes.ellipsoid(f"{n}.mouth", 0.042 * H, 0.02 * H, 0.012 * H, look.plastic("#5b1e2c", 0.5, 0.2), self.mouth)
        m.shape_key_add(name="Basis")
        for name, sign in (("smile", 1), ("frown", -1)):
            sk = m.shape_key_add(name=name)
            for v in sk.data:
                t = (v.co.x / (0.042 * H)) ** 2
                v.co.z += sign * 0.022 * H * t - sign * 0.004 * H
        self.mouth_mesh = m
        if self.get("nose", True):
            shapes.sphere(f"{n}.nose", 0.024 * H, self.color("skin"), self.neck, at=self.face_point(0, -0.015 * H, 0.016))
        if self.get("blush", True):
            for side in (1, -1):
                shapes.ellipsoid(f"{n}.blush", 0.034 * H, 0.008 * H, 0.02 * H, look.plastic("#f19aa6", 0.6, 0.1),
                                 self.neck, at=self.face_point(side * 0.115 * H, -0.035 * H, 0.002),
                                 rot=(0, 0, _deg(side * 40)))

    def eye_color(self):
        return "#161414"

    def build_hair(self):
        plugins.get("hair", self.get("hair", "short"))().build(self, self.color("hair_color", "brown"))

    def build_extras(self):
        for e in self.get("extras", []) or []:
            plugins.get("extra", e)().build(self)

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

    def height(self):
        """Top of the head above the feet, in metres (for framing)."""
        return self.top_z + self.head_center.z + self.head_r

    def length(self):
        """Front-to-back size, in metres (for framing long bodies)."""
        return 2 * self.head_r

    def where_at(self, t):
        """Smoothly interpolated (x, y, z) of the feet and the heading at time t (for following)."""
        loc = keys.sample(self.root, "location", t)
        rot = keys.sample(self.root, "rotation_euler", t)
        hz = keys.sample(self.hips, "location", t)[2]
        return Vector(loc), rot[2], hz

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
    def place(self, where, facing=None, at=None, on=None):
        """Put the character somewhere instantly (use at the start of a scene). `on`: the top of a
        table, bench or tray (a set's surfaces) to stand on instead of the floor."""
        t = 0.0 if at is None else at
        z = 0.0
        if on is not None:
            surf = self.scene.set.surfaces.get(on) if self.scene.set else None
            if surf is None:
                known = sorted(self.scene.set.surfaces) if self.scene.set else []
                raise ValueError(f"nothing called {on!r} to stand on. Surfaces: {known}")
            p = Vector(surf[:2])
            z = surf[2]
        else:
            p = self._point(where, t)
        key(self.root, "location", t, (p.x, p.y, z), "cut")
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
        stride, step_t = self.gait_timing(sp, run)
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

        self.animate_steps(Stride(path, ws, dur, total), n_steps, step_t, run)
        self.scene._event("move", self, t, end)
        if facing is not None:
            self._end(end, wait)
            return self.turn_to(facing, at=end, wait=wait)
        mark = self.scene.set.marks.get(where) if isinstance(where, str) and self.scene.set else None
        if mark is not None and mark.facing is not None:
            self._end(end, wait)
            return self.turn_to(math.degrees(mark.facing), at=end, wait=wait)
        return self._end(end, wait)

    def gait_timing(self, speed, run):
        """(stride length in metres, seconds per step) for a speed factor. Bodies override this."""
        H = self.H
        return (0.42 if run else 0.32) * H * min(speed, 1.5) ** 0.3, (0.28 if run else 0.36) / max(0.6, speed) ** 0.6

    def animate_steps(self, path, n_steps, step_t, run):
        """Animate the body while the root travels along `path` (a Stride): legs, arms, bounce.
        The toy swings its rigid legs and arms; other bodies plant feet (see creatures.py)."""
        ws, end, H = path.start, path.end, self.H
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
        """Change expression to a mood (see dr.registry("mood"); add your own with dr.Mood)."""
        m = plugins.get("mood", mood)
        t = self._start(at)
        tilt, lift, smile, frown, eye, mopen, head_tilt = (m.brow_tilt, m.brow_lift, m.smile, m.frown, m.eyes,
                                                          m.mouth_open, m.head_tilt)
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
        self.scene._event("say", self, t0, t0 + dur, line=line, listener=listener, audio=speech,
                          mood=mood or self.mood)
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
                    self.tilt_head_at(t - 0.3)
                t += 0.38
                continue
            groups = re.findall(r"[aeiouy]+", w.lower()) or ["a"]
            for g in groups:
                rnd = 1.0 if g[0] in "ou" else 0.0
                self._mouth_key(t + 0.02, 0.0)
                self._mouth_key(t + 0.09, 0.45 + 0.5 * self.rng.random(), rnd)
                t += 0.19
            if not nod_done and len(groups) > 1:
                self.nod_at(t - 0.3, 5)
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

    def nod_at(self, t, deg=8):
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.15, (cur[0] + _deg(deg), cur[1], cur[2]))
        key(self.neck, "rotation_euler", t + 0.35, tuple(cur))

    def tilt_head_at(self, t, deg=10):
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.2, (cur[0], cur[1] + _deg(deg), cur[2]))
        key(self.neck, "rotation_euler", t + 0.9, tuple(cur))

    # ------------------------------------------------------------------ pose helpers (for gestures)
    def arm_to(self, side, t, rot, ease="smooth"):
        """Key one arm (1 = left, -1 = right) to a rotation (x forward/back, y out to the side, z twist).
        Bodies without arms ignore it, so gestures that also move arms still work on them."""
        if side in self.arms:
            key(self.arms[side], "rotation_euler", t, rot, ease)

    def arms_rest(self, t):
        for s in (1, -1):
            self.arm_to(s, t, (0, 0, 0))

    def arms_up_at(self, t, hold_until=None):
        for s in (1, -1):
            self.arm_to(s, t, (0, _deg(-160 * s), 0))
            if hold_until:
                self.arm_to(s, hold_until, (0, _deg(-150 * s), 0))

    def hop_at(self, t, height, t_up, t_down):
        """Raise the hips by `height` (fraction of the character's height) and settle again."""
        hold(self.hips, "location", t)
        key(self.hips, "location", t + t_up, (0, 0, self.hip_z + height * self.H))
        key(self.hips, "location", t + t_down, (0, 0, self.hip_z))

    def jump_at(self, t, height=0.22):
        hold(self.hips, "location", t)
        z = self.hip_z
        key(self.hips, "location", t + 0.15, (0, 0, z - 0.04 * self.H))
        key(self.hips, "location", t + 0.4, (0, 0, z + height * self.H), "ease_out")
        key(self.hips, "location", t + 0.65, (0, 0, z - 0.03 * self.H), "ease_in")
        key(self.hips, "location", t + 0.8, (0, 0, z))

    def lean_at(self, t, deg_side=0.0, deg_forward=0.0):
        key(self.body, "rotation_euler", t, (_deg(-deg_forward), _deg(deg_side), 0))

    def do(self, gesture, target=None, at=None, wait=True):
        """Play a gesture (see dr.registry("gesture"); add your own with dr.Gesture)."""
        g = plugins.get("gesture", gesture)
        missing = set(g.needs) - self.capabilities
        if missing:
            able = [n for n, cls in plugins.registry("gesture").items() if not set(cls.needs) - self.capabilities]
            raise ValueError(f"{self.name} can't {g.label.lower()} (needs {', '.join(sorted(missing))}). "
                             f"{self.name} can: {', '.join(able)}")
        t = self._start(at)
        for arm in self.arms.values():
            hold(arm, "rotation_euler", t)
        hold(self.body, "rotation_euler", t)
        end = g().perform(self, t, target=target)
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


class ToyFigure(Character):
    name = "toy"
    drawing = "toy"   # the studio has a live drawing for this look
    label = "Toy figure"
    description = "A jointed vinyl toy: big head, stubby limbs, soft plastic"
