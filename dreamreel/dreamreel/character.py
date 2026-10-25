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

from . import acting, keys, look, plugins, shapes
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
        Param("eye_style", "choice", default="whites", choices=("whites", "beads"), label="Eyes look"),
        Param("eye_color", "color", default="#6b4423", label="Eye colour"),
        Param("extras", "extras", default=[]),
        Param("blush", "bool", default=True),
        Param("nose", "bool", default=True),
        Param("braces", "bool", default=False, label="Braces on the teeth"),
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
        self.danglers = []     # (pivot, stiffness, damping, gain): parts that lag and settle (acting.py)
        self.hands = {}        # side -> hand object (what held things follow)
        self.holding = {}      # side -> name of the thing in that hand (handling.py)
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
            self.hands[side] = shapes.sphere(f"{n}.hand", 0.058 * H, self.color("skin"), arm, at=(0, 0, -0.27 * H))
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
        H, n = getattr(self, "face_H", self.H), self.name     # face_H: the scale the features are built at
        L = dict(FACE_LAYOUT, **getattr(self, "face_layout", {}))
        es = {"small": 0.8, "normal": 1.0, "big": 1.3}.get(self.get("eyes"), 1.0)
        self.eyes, self.gazes = [], []
        beads = self.get("eye_style", self.default_eye_style) == "beads"
        for side in (1, -1):
            piv = shapes.empty(f"{n}.eye", self.neck, self.face_point(side * L["eye_x"] * H, L["eye_z"] * H, 0.004))
            if beads:       # one glossy bead (animals, and the classic toy look)
                eye = shapes.ellipsoid(f"{n}.eye", 0.03 * H * es, 0.02 * H, 0.043 * H * es,
                                       look.plastic(self.eye_color(), 0.12, 0.9), piv)
                shapes.sphere(f"{n}.glint", 0.011 * H * es, look.plastic("white", emission=1.5), eye,
                              at=(0.01 * H * es, -0.016 * H, 0.016 * H * es))
            else:           # a white eyeball with a coloured iris, a pupil and a highlight
                shapes.ellipsoid(f"{n}.eye", 0.03 * H * es, 0.02 * H, 0.043 * H * es,
                                 look.plastic("#f7f4ee", 0.3, 0.3), piv)
                gaze = shapes.empty(f"{n}.gaze", piv, (0, -0.0158 * H, -0.002 * H * es))
                shapes.ellipsoid(f"{n}.iris", 0.019 * H * es, 0.0045 * H, 0.023 * H * es,
                                 look.plastic(self.eye_color(), 0.25, 0.5), gaze, segments=24)
                shapes.ellipsoid(f"{n}.pupil", 0.0095 * H * es, 0.003 * H, 0.0115 * H * es,
                                 look.plastic("#0e0c0c", 0.15, 0.8), gaze, at=(0, -0.0028 * H, 0), segments=16)
                shapes.sphere(f"{n}.glint", 0.0055 * H * es, look.plastic("white", emission=1.5), gaze,
                              at=(0.0065 * H * es, -0.0062 * H, 0.008 * H * es), segments=12)
                self.gazes.append(gaze)
            self.eyes.append(piv)
        self.brows = {}
        brow_color = self.color("hair_color") if self.get("hair", "short") != "none" else "charcoal"
        for side in (1, -1):
            piv = shapes.empty(f"{n}.brow", self.neck, self.face_point(side * L["eye_x"] * H, L["brow_z"] * H, 0.004))
            shapes.capsule(f"{n}.brow", 0.012 * H, 0.04 * H, brow_color, piv, rot=(0, _deg(90), 0))
            self.brows[side] = piv
        self.mouth = shapes.empty(f"{n}.mouthpivot", self.neck, self.face_point(0, L["mouth_z"] * H, 0.004))
        m = shapes.ellipsoid(f"{n}.mouth", 0.042 * H, 0.02 * H, 0.012 * H, look.plastic("#5b1e2c", 0.5, 0.2), self.mouth)
        m.shape_key_add(name="Basis")
        for name, sign in (("smile", 1), ("frown", -1)):
            sk = m.shape_key_add(name=name)
            for v in sk.data:
                t = (v.co.x / (0.042 * H)) ** 2
                v.co.z += sign * 0.022 * H * t - sign * 0.004 * H
        self.mouth_mesh = m
        if self.get("nose", True):
            shapes.sphere(f"{n}.nose", 0.024 * H, self.color("skin"), self.neck, at=self.face_point(0, L["nose_z"] * H, 0.016))
        if self.get("blush", True):
            for side in (1, -1):
                shapes.ellipsoid(f"{n}.blush", 0.034 * H, 0.008 * H, 0.02 * H, look.plastic("#f19aa6", 0.6, 0.1),
                                 self.neck, at=self.face_point(side * L["blush_x"] * H, L["blush_z"] * H, 0.002),
                                 rot=(0, 0, _deg(side * 40)))
        from . import face
        face.build(self)

    default_eye_style = "whites"

    def eye_color(self):
        if self.get("eye_style", self.default_eye_style) == "beads":
            return "#161414"
        return self.color("eye_color", "#6b4423")

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
        return getattr(self, "hip_z", 0.0) + self.top_z + self.head_center.z + self.head_r

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

    @property
    def late_side(self):
        """The side of this body that's a touch behind the other in two-handed moves (always the same one)."""
        import zlib
        return 1 if zlib.crc32(self.name.encode()) % 2 else -1

    def contact(self, t0, t1):
        """Mark a stretch where this body is meant to touch others (a blow, a fall, a pile-on), so the
        overlap check leaves it be."""
        self.contacts = getattr(self, "contacts", []) + [(float(t0), float(t1))]

    def touching(self, t):
        return any(t0 <= t <= t1 for t0, t1 in getattr(self, "contacts", []))

    def noted(self, kind, t):
        """Remember a small act (a look, a turn, a feeling) for the checks that read a scene's acting."""
        self.acts = getattr(self, "acts", []) + [(float(t), kind)]

    def turn_to(self, target, at=None, wait=True):
        """Turn the whole body towards a character, mark or direction ("camera", "left", ...)."""
        t = self._start(at)
        self.noted("turn", t)
        p = self.position(t)
        h = self._facing_value(target, p, t)
        hold(self.root, "rotation_euler", t)
        stepped = self.step_turn(t, h)
        if stepped is not None:          # feet that step round, the planted one staying put
            self._reset_head(t, min(stepped, t + 0.35))
            return self._end(stepped, wait)
        dur = 0.25 + 0.3 * abs(_wrap(h - self.heading(t))) / math.pi
        self._key_heading(t + dur, h)
        self._reset_head(t, t + dur * 0.6)
        return self._end(t + dur, wait)

    def walk_time(self, distance, speed="normal", t=None, how=None):
        """How long walk_to takes to cover `distance` metres in a straight line (to plan walking in so
        as to arrive in time)."""
        sp = SPEEDS.get(speed, speed) if not isinstance(speed, (int, float)) else speed
        sp *= acting.effort_of(self, self.busy if t is None else t, how).walk_speed()
        stride, step_t = self.gait_timing(sp, sp >= 1.8)
        return 0.18 + max(2, math.ceil(distance / stride)) * step_t

    def step_turn(self, t, h):
        """Turn to heading `h` from `t` by stepping round; returns when it's done, or None for bodies whose
        feet go round with them (a toy's are part of its legs). Bodies with feet override it."""
        return None

    def look_at(self, target, at=None, wait=False):
        """Turn just the head towards a character or mark (up to 70 degrees); the body stays."""
        t = self._start(at)
        self.noted("look", t)
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
    def walk_to(self, where, speed="normal", facing=None, at=None, wait=True, how=None):
        """Walk to a mark, prop or character (stopping in front of them), going round furniture.

        speed: "slow", "normal", "fast" or "run". facing: what to face on arrival. how: a manner
        ("angrily", "sneakily"...; otherwise the mood decides how they walk).
        """
        if self.sitting:
            self.stand(at=at)
            at = None
        t = self._start(at)
        p0 = self.position(t)
        p1 = self.scene._resolve(where, t, me=self, approach=getattr(self, "_approach", True))
        path = self.scene.set.route(p0, p1) if self.scene.set else [p0, p1]
        sp = SPEEDS.get(speed, speed) if not isinstance(speed, (int, float)) else speed
        self._effort = acting.effort_of(self, t, how)
        sp *= self._effort.walk_speed()
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
        self._footsteps(ws, n_steps, step_t, run)
        self.scene._event("move", self, t, end)
        if facing is not None:
            self._end(end, wait)
            return self.turn_to(facing, at=end, wait=wait)
        mark = self.scene.set.marks.get(where) if isinstance(where, str) and self.scene.set else None
        if mark is not None and mark.facing is not None:
            self._end(end, wait)
            return self.turn_to(math.degrees(mark.facing), at=end, wait=wait)
        return self._end(end, wait)

    def footstep_sound(self, footing):
        """The sound (sounds.py) of one of this character's steps on wood, carpet, concrete, grass or
        snow, or None for silent feet. Bodies override it: a robot clanks, a ghost makes none."""
        return "footstep_" + footing

    def _footsteps(self, t0, n_steps, step_t, run):
        """A footstep as each foot lands."""
        name = self.footstep_sound(self.scene.set.footing() if self.scene.set else "concrete")
        if name is None:
            return
        vol = (0.5 if run else 0.3) * min(1.0, max(0.3, getattr(self, "H", 1.0) / 1.7))
        for k in range(n_steps):
            self.scene.sound(name, at=t0 + (k + 0.5) * step_t, volume=vol, kind="footsteps")

    def gait_timing(self, speed, run):
        """(stride length in metres, seconds per step) for a speed factor. Bodies override this."""
        H = self.H
        return (0.42 if run else 0.32) * H * min(speed, 1.5) ** 0.3, (0.28 if run else 0.36) / max(0.6, speed) ** 0.6

    def animate_steps(self, path, n_steps, step_t, run):
        """Animate the body while the root travels along `path` (a Stride): legs, arms, bounce.
        The toy swings its rigid legs and arms; other bodies plant feet (see creatures.py)."""
        ws, end, H = path.start, path.end, self.H
        if self._library_walk(path, run):
            return
        eff = getattr(self, "_effort", None) or acting.Effort()
        ex = self.scene.exaggeration
        A = _deg(38 if run else 26) * (1 + (eff.swing() - 1) * ex)
        lean = _deg(10 if run else 2) + _deg(5) * eff.time * ex - _deg(4) * max(0.0, -eff.weight)
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
            if 1 not in self.holding:          # an arm carrying something doesn't swing
                key(self.arms[1], "rotation_euler", ti, (sgn * amp * 0.9, 0, 0))
            if -1 not in self.holding:
                key(self.arms[-1], "rotation_euler", ti, (-sgn * amp * 0.9, 0, 0))
            if i < n_steps:
                b = eff.bounce()
                key(self.hips, "location", ti, (0, 0, base - 0.018 * H * (1.6 if run else 1) * b))
                key(self.hips, "location", ti + step_t / 2, (0, 0, base + (0.03 if run else 0.012) * H * b))
        key(self.hips, "location", end, (0, 0, base))
        # follow-through: the body carries on a little when the feet stop, then settles
        settle = 0.08 * ex * (1 + max(0.0, -eff.flow))
        key(self.body, "rotation_euler", end, (-lean - settle, 0, 0))
        key(self.body, "rotation_euler", end + 0.3, (0, 0, 0))

    def _library_walk(self, path, run):
        """Walk with a clip from the motion library if it has one (tagged walk or run): the clip
        closest to the speed needed, looped and played along the path (simple motion matching)."""
        from . import motion
        lib = motion.library(self.scene)
        if not lib.entries or not motion.can_perform(self) or self.holding:
            return False
        clips = lib.tagged("run" if run else "walk") or (lib.tagged("jog") if run else [])
        if not clips:
            return False
        _, _, hip_h = motion._rest(self)
        need = path.total / max(1e-6, path.end - path.start) / hip_h       # hip heights per second
        clip = min(clips, key=lambda cl: abs(math.log(max(1e-3, cl.speed()) / max(1e-3, need))))
        rate = need / max(1e-3, clip.speed())
        motion.walk_cycle(self, clip, path, path.start, path.end, rate)
        for obj in (self.body, *self.arms.values(), *self.legs.values()):
            key(obj, "rotation_euler", path.end + 0.3, (0, 0, 0))
        key(self.hips, "location", path.end + 0.3, (0, 0, self.hip_z))
        return True

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
            for s, leg in self.legs.items():
                key(leg, "rotation_euler", t, (_deg(self.seat_pose[0]), 0, 0), "cut")
                self._reach(("leg", s), t, self.seat_pose[1], "cut")
            self.sitting = seat
            return self
        self.walk_to(seat.front, at=at)
        t = self._start(None)
        self._key_heading(t + 0.3, seat.facing)
        hold(self.root, "location", t + 0.3)
        hold(self.hips, "location", t + 0.3)
        key(self.root, "location", t + 0.75, (seat.at.x, seat.at.y, 0))
        key(self.hips, "location", t + 0.75, (0, 0, seat.height + 0.04 * self.H))
        self._hold_reach(t + 0.3)
        for s, leg in self.legs.items():
            hold(leg, "rotation_euler", t + 0.3)
            key(leg, "rotation_euler", t + 0.75, (_deg(self.seat_pose[0]), 0, 0))
            self._reach(("leg", s), t + 0.75, self.seat_pose[1])
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
        self._hold_reach(t)
        for s, leg in self.legs.items():
            hold(leg, "rotation_euler", t)
            key(leg, "rotation_euler", t + 0.45, (0, 0, 0))
            self._reach(("leg", s), t + 0.45, 1.0)
        self.sitting = None
        return self._end(t + 0.45, wait)

    # ------------------------------------------------------------------ face
    def feel(self, mood, at=None, wait=False, how_much=1.0):
        """Change expression to a mood (see dr.registry("mood"); add your own with dr.Mood).
        how_much: 0.5 a hint of it ... 1 as defined ... 1.5 pushed further (see face.py)."""
        from . import face
        m = plugins.get("mood", mood)
        t = self._start(at)
        amount = float(how_much if how_much is not None else 1.0)
        self._moods = sorted(getattr(self, "_moods", []) + [(t, mood, amount)], key=lambda x: x[0])
        self.noted("feel", t)
        t1 = t + 0.25
        face.apply(self, face.values(m, amount), t, t1)
        self.mood = mood
        return self._end(t1, wait)

    def flash(self, mood, at, hold=0.5, how_much=1.0):
        """A moment of a feeling (the effort of a blow, a wince) that passes back into the mood they were in."""
        from . import face
        self.noted("flash", at)
        before = [(t, m, a) for t, m, a in getattr(self, "_moods", []) if t <= at]
        back, amount = (before[-1][1], before[-1][2]) if before else ("neutral", 1.0)
        face.apply(self, face.values(plugins.get("mood", mood), how_much), at, at + 0.08)
        face.apply(self, face.values(plugins.get("mood", back), amount), at + hold, at + hold + 0.3)

    # ------------------------------------------------------------------ talking
    def say(self, line, mood=None, to=None, at=None, wait=True):
        """Speak a line: mouth, head and subtitles are animated; with a voice set up it's also heard.

        to: who they're talking to (they look at them, and the camera uses it for over-the-shoulder shots).
        """
        t = self._start(at)
        acts = getattr(self, "acts", [])
        if to is not None:
            self.look_at(to, at=t, wait=False)
        if mood:
            self.feel(mood, at=t, wait=False)
        self.acts = acts                 # part of speaking, not acting while speaking (see lint.RadioPlay)
        speech = self.scene.voices.speak(self, line, mood=mood or self.mood)
        t0 = t + 0.15
        if speech is not None:
            dur = speech.duration
            self._lipsync_audio(t0, speech)
        else:
            dur = self._lipsync_text(t0, line)
        listener = self.scene.character(to) if isinstance(to, str) else to
        if listener is None:
            listener = self.scene._nearest(self, t)
        self.scene._event("say", self, t0, t0 + dur, line=line, listener=listener, audio=speech,
                          mood=mood or self.mood)
        return self._end(t0 + dur + 0.3, wait)

    def _mouth_key(self, t, open_amt, round_amt=0.0, wide_amt=0.0):
        """open: the jaw; round: lips pushed forward ("oo"); wide: lips stretched ("ee"). Faces with
        their own shape keys read these (see models.ModelCharacter._face)."""
        rest = self.mouth.get("rest", 0.0)
        o = max(open_amt, rest)
        key(self.mouth, "scale", t, (1 - 0.3 * o - 0.35 * round_amt + 0.3 * wide_amt, 1, 1 + 2.2 * o))
        for prop, v in (("round", round_amt), ("wide", wide_amt)):
            self.mouth[prop] = float(v)
            self.mouth.keyframe_insert(f'["{prop}"]', frame=keys.CLOCK.frame(t))

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

    def _lipsync_audio(self, t0, speech):
        """Mouth shapes from the sounds of the line (lipsync.py), or from its loudness."""
        mode = self.scene.voices.lipsync
        cues = speech.face() if mode == "ai" else None
        if not cues and mode in ("sounds", "ai"):
            cues = speech.shapes()
        if not cues:
            return self._lipsync_envelope(t0, speech)
        hold(self.mouth, "scale", t0 - 0.05)
        last = None
        for start, (o, r, w) in cues:
            t = t0 + start
            if last is not None and t - last < 0.035:     # too quick to see: keep the frames clean
                continue
            self._mouth_key(t, o, r, w)
            last = t
        self._mouth_key(t0 + speech.duration + 0.05, 0.0)

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
    bends = False                 # elbows and knees that bend (see models.py); toys swing straight limbs

    def arm_to(self, side, t, rot, ease="smooth", reach=None, bent=None):
        """Key one arm (1 = left, -1 = right) to a rotation (x forward/back, y out to the side, z twist).
        reach: how far the hand is from the shoulder, as a fraction of the arm's length (1 straight;
        0.45 brings a hand to the face): bodies with real elbows bend them, toys ignore it. Back at
        rest (rotation 0) the arm straightens again. bent: (rotation, reach) to use instead on bodies
        whose elbows bend, whose proportions are real (a hand that reaches the face goes in front of
        it, not beside a toy's big head). Bodies without arms ignore it all, so gestures that also
        move arms still work on them."""
        if bent is not None and self.bends:
            rot, reach = bent
        if side in self.arms:
            key(self.arms[side], "rotation_euler", t, rot, ease)
            if reach is None and not any(rot):
                reach = 1.0
            if reach is not None:
                self._reach(("arm", side), t, reach, ease)

    def _reach(self, limb, t, reach, ease="smooth"):
        """Bend an elbow or a knee so the hand or foot is `reach` of the limb's length away (only
        bodies with jointed limbs, see models.py)."""

    def _hold_reach(self, t):
        """Key every limb's current reach at `t`, so the next bend starts from here."""

    def fist(self, t, amount=1.0, sides=(1, -1), ease="smooth"):
        """Close the hands into fists by `t` (amount 0 opens them again); only bodies with fingers."""

    seat_pose = (-80, 1.0)       # sitting: each leg's swing forward (degrees) and the foot's reach

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
        self.squash_at(t + 0.15, 1.0)          # crouch
        self.squash_at(t + 0.3, -1.0)          # stretch on the way up
        self.squash_at(t + 0.48, 0.0)
        self.squash_at(t + 0.66, 0.8)          # land
        self.squash_at(t + 0.82, 0.0)

    def squash_at(self, t, amount):
        """Squash (amount > 0) or stretch (< 0) the body, keeping its volume (squash and stretch)."""
        k = 0.1 * amount * self.scene.exaggeration
        z = 1.0 - k
        xy = 1.0 / max(0.5, z) ** 0.5
        hold(self.body, "scale", t)
        key(self.body, "scale", t, (xy, xy, z))

    def dangle(self, obj, root, stiffness=1.0, damping=1.0, gain=1.0):
        """Make a part hang from `root` (a point in its parent's space) and lag behind the body's
        movements, then settle (follow-through). Used for long hair, ponytails, floppy ears..."""
        piv = shapes.empty(f"{self.name}.dangle", obj.parent, root)
        obj.location = obj.location - Vector(root)
        obj.parent = piv
        self.danglers.append((piv, stiffness, damping, gain))
        return piv

    def lean_at(self, t, deg_side=0.0, deg_forward=0.0):
        key(self.body, "rotation_euler", t, (_deg(-deg_forward), _deg(deg_side), 0))

    def do(self, gesture, target=None, at=None, wait=True, how=None):
        """Play a gesture (see dr.registry("gesture"); add your own with dr.Gesture). `how`: a manner
        ("angrily", "nervously"...); otherwise the current mood shapes it (see acting.py)."""
        g = plugins.get("gesture", gesture)
        missing = set(g.needs) - self.capabilities
        if gesture in getattr(self, "clip_names", {}):      # an actor's own animation of it
            missing = set()
        if missing:
            able = [n for n, cls in plugins.registry("gesture").items() if not set(cls.needs) - self.capabilities]
            raise ValueError(f"{self.name} can't {g.label.lower()} (needs {', '.join(sorted(missing))}). "
                             f"{self.name} can: {', '.join(able)}")
        t = self._start(at)
        for arm in self.arms.values():
            hold(arm, "rotation_euler", t)
        for leg in (getattr(self, "legs", None) or {}).values():   # a move keys a limb from where it is now,
            hold(leg, "rotation_euler", t)                          # not from its rest pose back at 0 s
        hold(self.hips, "location", t)
        self._hold_reach(t)
        hold(self.body, "rotation_euler", t)
        n_sounds = len(self.scene.sound_fx)
        with keys.recording() as curves:
            end = g().perform(self, t, target=target)
        effort = acting.effort_of(self, t, how)
        if g.keeps_time:
            effort = acting.Steady(effort)
        end = acting.shape(curves, t, end, effort, self.scene.exaggeration)
        if not g.keeps_time:                # moves that must meet someone else's keep their exact timing
            end = acting.overlap(curves, t, end, self.scene.exaggeration)
            if not g.symmetric:
                end = acting.unmirror(curves, t, end, late=self.late_side, exaggeration=self.scene.exaggeration)
        tempo = effort.tempo()          # the gesture's sounds keep time with its retimed moves
        fx = self.scene.sound_fx
        fx[n_sounds:] = [(t + (ts - t) * tempo, f, v, n) for ts, f, v, n in fx[n_sounds:]]
        if g.contact:
            self.contact(t, end)
        self.scene._event("gesture", self, t, end, gesture=gesture, how=how)
        return self._end(end, wait)

    # ------------------------------------------------------------------ motion capture (motion.py)
    def perform(self, motion_name, speed=1.0, mirror=False, in_place=False, at=None, wait=True, how=None,
                start=None, end=None, clip=None):
        """Play a motion-capture clip from the film's motion library (motions/), or a clip given,
        retargeted to this body."""
        from . import motion
        clip = clip or motion.library(self.scene).get(motion_name)
        t = self._start(at)
        eff = acting.effort_of(self, t, how)
        sp = float(speed or 1.0) / max(0.5, eff.tempo())
        t1 = motion.perform(self, clip, t, speed=sp, mirror=bool(mirror), in_place=bool(in_place),
                            start=float(start or 0.0), end=end)
        self.scene._event("perform", self, t, t1, motion=motion_name or clip.name)
        return self._end(t1, wait)

    # ------------------------------------------------------------------ handling things (handling.py)
    def _hand(self, hand=None, holding=None):
        if not self.arms or not self.hands:
            raise ValueError(f"{self.name} has no hands to hold things with")
        if holding is not None:
            side = next((s for s, n in self.holding.items() if n == holding), None)
            if side is None:
                raise ValueError(f"{self.name} isn't holding {holding!r} (holding: {list(self.holding.values()) or 'nothing'})")
            return side
        if hand in ("left", 1):
            return 1
        if hand in ("right", -1):
            return -1
        free = [s for s in (-1, 1) if s in self.hands and s not in self.holding]
        if not free:
            raise ValueError(f"{self.name}'s hands are full ({', '.join(self.holding.values())}): put something down first")
        return free[0]

    def _held(self, thing=None):
        if thing is None:
            if not self.holding:
                raise ValueError(f"{self.name} isn't holding anything")
            return next(iter(self.holding.values()))
        return thing

    def hold(self, thing, hand=None, at=None):
        """Be holding something from this moment: a thing in the set (`cup`) or a new item (`scalpel`)."""
        from . import handling
        t = 0.0 if at is None else at
        side = self._hand(hand)
        th = self.scene.thing(thing, create=True)
        point = handling.carry_point(self, side, t)
        keys.key(self.arms[side], "rotation_euler", t, handling.aim(self, side, t, point), "cut")
        handling.evaluate(self.scene, t)
        hand_at = self.hands[side].matrix_world.translation
        if th.character is None:
            keys.key(th.root, "location", t, tuple(hand_at - Vector((0, 0, 0.02 * self.H))), "cut")
        handling.attach(self.scene, th, self.hands[side], t)
        self.holding[side] = th.name
        th.holder = (self, side)
        return self

    def pick_up(self, thing, hand=None, at=None, wait=True):
        """Walk over if needed, reach, take it, and carry it."""
        from . import handling
        th = self.scene.thing(thing)
        if th.holder is not None and th.holder[0] is not self:
            raise ValueError(f"{th.name} is in {th.holder[0].name}'s hand: use give")
        side = self._hand(hand)
        t = self._start(at)
        p = handling.thing_point(self.scene, th, t)
        _, reach = handling.arm_rest(self)[side]
        if (self.position(t) - p.to_2d()).length > reach + 0.35 * self.H:
            self.walk_to(th.approach or (p.x, p.y), at=t, wait=True)
            t = max(self.busy, t)
        if self.heading(t) is not None:
            self.turn_to((p.x, p.y), at=t, wait=True)
            t = max(self.busy, t)
        eff = acting.effort_of(self, t)
        t1 = t + 0.45 * eff.tempo()
        handling.reach(self, side, t, t1, p + Vector((0, 0, 0.03 * self.H)))
        handling.attach(self.scene, th, self.hands[side], t1)
        t2 = t1 + 0.4 * eff.tempo()
        handling.straighten(self, t1, t2)
        keys.key(self.arms[side], "rotation_euler", t2, handling.aim(self, side, t1, handling.carry_point(self, side, t1)))
        self.holding[side] = th.name
        th.holder = (self, side)
        self.scene._event("handle", self, t, t2, action="picks up", thing=th.name)
        return self._end(t2, wait)

    def grab(self, who, hand=None, at=None, wait=True):
        """Grab a (small) character and carry it."""
        return self.pick_up(who, hand=hand, at=at, wait=wait)

    def put_down(self, thing=None, on=None, at=None, wait=True):
        """Put what's held (or `thing`) down: on a surface (`on = "table"`) or the floor in front."""
        from . import handling
        name = self._held(thing)
        side = self._hand(holding=name)
        th = self.scene.thing(name)
        t = self._start(at)
        if on is not None:
            surf = self.scene.set.surfaces.get(on) if self.scene.set else None
            if surf is None:
                raise ValueError(f"nothing called {on!r} to put things on. Surfaces: {sorted(self.scene.set.surfaces)}")
            if on in self.scene.set.marks:
                self.walk_to(on, at=t, wait=True)
                t = max(self.busy, t)
            here = self.position(t)
            centre = Vector(surf[:2])
            toward = (here - centre)
            w, d = self.scene.set.surface_size.get(on, (0.6, 0.6))
            # near the edge on this side, within reach
            edge = max(0.0, min(w, d) / 2 - 0.12)
            spot = centre + (toward.normalized() * min(edge, toward.length) if toward.length > 1e-3 else Vector())
            point = Vector((spot.x, spot.y, surf[2]))
        else:
            h = self.heading(t)
            fwd = Vector((math.sin(h), -math.cos(h)))
            spot = self.position(t) + fwd * 0.4 * self.H
            point = Vector((spot.x, spot.y, 0.0))
        eff = acting.effort_of(self, t)
        t1 = t + 0.45 * eff.tempo()
        handling.reach(self, side, t, t1, point + Vector((0, 0, 0.04 * self.H)))
        if on is not None:   # put it down where the hand got to, kept on the surface
            handling.evaluate(self.scene, t1)
            hand = self.hands[side].matrix_world.translation
            cx, cy, h = self.scene.set.surfaces[on]
            w, d = self.scene.set.surface_size.get(on, (0.6, 0.6))
            point = Vector((min(cx + w / 2 - 0.05, max(cx - w / 2 + 0.05, hand.x)),
                            min(cy + d / 2 - 0.05, max(cy - d / 2 + 0.05, hand.y)), h))
        handling.release(self.scene, th, t1, at=point, heading=self.heading(t1))
        if th.character is not None:
            th.character.busy = max(th.character.busy, t1)
        t2 = t1 + 0.4 * eff.tempo()
        handling.straighten(self, t1, t2)
        keys.key(self.arms[side], "rotation_euler", t2, (0, 0, 0))
        del self.holding[side]
        self.scene._event("handle", self, t, t2, action="puts down", thing=name)
        return self._end(t2, wait)

    def drop(self, thing=None, at=None, wait=True):
        """Let go: it falls to the floor."""
        from . import handling
        name = self._held(thing)
        side = self._hand(holding=name)
        th = self.scene.thing(name)
        t = self._start(at)
        if th.character is not None:        # a creature lands on its feet
            end = handling.fall(self.scene, th, t)
        else:                               # a thing falls, bounces and tumbles (physics.py)
            from . import physics
            v = physics.velocity(self.scene, th.root, t)
            handling.release(self.scene, th, t)
            end = physics.simulate(self.scene, t, {th: (v, physics.spin_for(v, 0.3) + Vector((1.2, 0.7, 0)))})
        keys.key(self.arms[side], "rotation_euler", t + 0.35, (0, 0, 0))
        del self.holding[side]
        self.scene._event("handle", self, t, end, action="drops", thing=name)
        return self._end(max(t + 0.35, min(end, t + 1.0)), wait)

    def _toward(self, where, t):
        """A point to aim at: a character (their chest), a thing, a mark or place (the floor there)."""
        other = self.scene.character(where) if isinstance(where, str) else (where if isinstance(where, Character) else None)
        if other is not None and other is not self:
            p = other.position(t)
            return Vector((p.x, p.y, other.height() * 0.6)), other
        if isinstance(where, str) and self.scene.set is not None and where in self.scene.set.things:
            from . import handling
            return handling.thing_point(self.scene, self.scene.set.things[where], t), None
        p = self.scene._resolve(where, t)
        return Vector((p.x, p.y, 0.0)), None

    def throw(self, thing=None, to=None, hand=None, at=None, wait=True):
        """Throw what's held (or pick `thing` up first) to someone, who catches it, or to a place, where
        it lands, bounces and rolls."""
        from . import handling, physics
        if thing is not None and thing not in self.holding.values():
            self.pick_up(thing, hand=hand, at=at, wait=True)
            at = None
        name = self._held(thing)
        side = self._hand(holding=name)
        th = self.scene.thing(name)
        t = self._start(at)
        if to is None:
            h = self.heading(t) or 0.0
            here = self.position(t)
            to = (here.x + 2.0 * math.sin(h), here.y - 2.0 * math.cos(h))
        target, other = self._toward(to, t)
        self.turn_to((target.x, target.y), at=t, wait=True)
        t = max(self.busy, t)
        eff = acting.effort_of(self, t)
        _, L = handling.arm_rest(self)[side]
        handling.evaluate(self.scene, t)
        sh = self.arms[side].matrix_world.translation.copy()
        h = self.heading(t) or 0.0
        fwd = Vector((math.sin(h), -math.cos(h), 0))
        up = Vector((0, 0, 1))
        t1 = t + 0.4 * eff.tempo()                  # wind up: the arm goes back and up
        keys.hold(self.arms[side], "rotation_euler", t)
        keys.key(self.arms[side], "rotation_euler", t1, handling.aim(self, side, t, sh - fwd * 0.6 + up * 0.7), "ease_out")
        if self.body is not None:
            keys.hold(self.body, "rotation_euler", t)
            keys.key(self.body, "rotation_euler", t1, (math.radians(8), 0, 0))
        t_rel = t1 + 0.14                           # the throw: fast, let go in front and above
        keys.key(self.arms[side], "rotation_euler", t_rel, handling.aim(self, side, t1, sh + fwd * 0.8 + up * 0.45), "linear")
        t2 = t_rel + 0.18                           # follow through: forward and down
        keys.key(self.arms[side], "rotation_euler", t2, handling.aim(self, side, t1, sh + fwd * 0.9 - up * 0.3), "ease_out")
        if self.body is not None:
            keys.key(self.body, "rotation_euler", t2, (math.radians(-10), 0, 0))
            keys.key(self.body, "rotation_euler", t2 + 0.35, (0, 0, 0))
        keys.key(self.arms[side], "rotation_euler", t2 + 0.45, (0, 0, 0))
        handling.evaluate(self.scene, t_rel)
        p = th.root.matrix_world.translation.copy()
        catcher = other if other is not None and other.arms and other.hands and \
            any(s not in other.holding for s in other.hands) else None
        del self.holding[side]
        if catcher is not None:
            oside = catcher._hand()
            T = physics.flight_time(p, target)
            t_arr = t_rel + T
            catcher.turn_to(self.name, at=max(t, catcher.busy), wait=False)
            q = handling.carry_point(catcher, oside, t_arr) + Vector((0, 0, 0.1 * catcher.H))
            back = (Vector((p.x, p.y, 0)) - Vector((q.x, q.y, 0)))
            q += back.normalized() * 0.15 * catcher.H if back.length > 1e-3 else Vector()
            handling.reach(catcher, oside, max(t_rel, t_arr - 0.45), t_arr, q)
            handling.evaluate(self.scene, t_arr)
            q = catcher.hands[oside].matrix_world.translation - Vector((0, 0, th.grip))
            v = physics.ballistic(p, q, T)
            handling.release(self.scene, th, t_rel)
            physics.fly(th, p, v, t_rel, T)
            handling.attach(self.scene, th, catcher.hands[oside], t_arr)
            handling.straighten(catcher, t_arr, t_arr + 0.4)
            keys.key(catcher.arms[oside], "rotation_euler", t_arr + 0.5,
                     handling.aim(catcher, oside, t_arr, handling.carry_point(catcher, oside, t_arr)))
            catcher.holding[oside] = name
            th.holder = (catcher, oside)
            catcher.busy = max(catcher.busy, t_arr + 0.5)
            end = t_arr
            what = f"throws {name} to {catcher.name}"
        else:
            T = physics.flight_time(p, target) * 1.25        # a lob, so it lands near the spot
            v = physics.ballistic(p, target, T)
            handling.release(self.scene, th, t_rel)
            physics.simulate(self.scene, t_rel, {th: (v, physics.spin_for(v, 0.8))})
            end = t_rel + T
            what = f"throws {name}"
        self.scene._event("handle", self, t, max(t2, end), action=what, thing=name)
        return self._end(t2 + 0.2, wait)

    def knock_over(self, thing, hand=None, at=None, wait=True):
        """Knock something over (or off the table) with a sweep of the arm."""
        from . import handling, physics
        th = self.scene.thing(thing)
        if th.holder is not None or th.character is not None:
            raise ValueError(f"{th.name} isn't standing anywhere to knock over")
        side = self._hand(hand) if hand is not None or any(s not in self.holding for s in self.hands) \
            else next(iter(self.hands))
        t = self._start(at)
        p = handling.thing_point(self.scene, th, t)
        _, reach = handling.arm_rest(self)[side]
        if (self.position(t) - p.to_2d()).length > reach + 0.35 * self.H:
            self.walk_to(th.approach or (p.x, p.y), at=t, wait=True)
            t = max(self.busy, t)
        self.turn_to((p.x, p.y), at=t, wait=True)
        t = max(self.busy, t)
        eff = acting.effort_of(self, t)
        handling.evaluate(self.scene, t)
        sh = self.arms[side].matrix_world.translation.copy()
        mid = p + Vector((0, 0, th.grip))
        t1 = t + 0.35 * eff.tempo()
        handling.reach(self, side, t, t1, mid)
        d = Vector((p.x - sh.x, p.y - sh.y, 0))
        d = d.normalized() if d.length > 1e-3 else Vector((0, 1, 0))
        speed = 1.0 + 0.8 * max(0.0, eff.weight) + 0.5 * max(0.0, -eff.time)
        t2 = t1 + 0.2
        keys.key(self.arms[side], "rotation_euler", t2, handling.aim(self, side, t1, mid + d * 0.35), "ease_out")
        # the hand sweeps through it, high up, so it tips over its base (and maybe off the edge)
        handling.evaluate(self.scene, t1)
        top = max((o.matrix_world @ Vector(c)).z for o in th.root.children_recursive if o.type == "MESH"
                  for c in o.bound_box)
        size = max(0.04, max(max(abs((o.matrix_world @ Vector(c) - p).dot(d)) for c in o.bound_box)
                             for o in th.root.children_recursive if o.type == "MESH"))
        start = Vector((p.x, p.y, p.z + 0.6 * (top - p.z))) - d * (size + 0.05)
        settle = physics.simulate(self.scene, t1, {th: None}, sweep=(start, d * speed, 0.3))
        t3 = t2 + 0.4 * eff.tempo()
        handling.straighten(self, t2, t3)
        keys.key(self.arms[side], "rotation_euler", t3, (0, 0, 0))
        self.scene._event("handle", self, t, max(t3, settle), action="knocks over", thing=th.name)
        return self._end(t3, wait)

    def kick(self, thing, to=None, at=None, wait=True):
        """Kick something on the floor (a ball): towards someone or somewhere, or straight ahead."""
        from . import handling, physics
        th = self.scene.thing(thing)
        if not self.legs:
            raise ValueError(f"{self.name} has no legs to kick with")
        t = self._start(at)
        p = handling.thing_point(self.scene, th, t)
        if to is None:
            d = p.to_2d() - self.position(t)
            d = d.normalized() if d.length > 1e-3 else Vector((0, -1))
            target = Vector((p.x + d.x * 3, p.y + d.y * 3, 0.0))
        else:
            target, _ = self._toward(to, t)
        d = (target - p).to_2d()
        d = d.normalized() if d.length > 1e-3 else Vector((0, -1))
        foot = -1 if -1 in self.legs else next(iter(self.legs))
        side_off = Vector((-d.y, d.x)) * (0.08 * self.H * (1 if foot < 0 else -1))
        spot = p.to_2d() - d * 0.38 * self.H + side_off
        if (self.position(t) - spot).length > 0.08:
            self.walk_to((spot.x, spot.y), at=t, wait=True)
            t = max(self.busy, t)
        self.turn_to((p.x + d.x, p.y + d.y), at=t, wait=True)
        t = max(self.busy, t)
        eff = acting.effort_of(self, t)
        leg = self.legs[foot]
        t1 = t + 0.3 * eff.tempo()            # swing back...
        keys.hold(leg, "rotation_euler", t)
        keys.key(leg, "rotation_euler", t1, (math.radians(35), 0, 0), "ease_out")
        t_hit = t1 + 0.12                     # ...and through
        keys.key(leg, "rotation_euler", t_hit, (math.radians(-45), 0, 0), "linear")
        keys.key(leg, "rotation_euler", t_hit + 0.12, (math.radians(-55), 0, 0), "ease_out")
        keys.key(leg, "rotation_euler", t_hit + 0.45, (0, 0, 0))
        if self.body is not None:
            keys.hold(self.body, "rotation_euler", t)
            keys.key(self.body, "rotation_euler", t1, (math.radians(-6), 0, 0))
            keys.key(self.body, "rotation_euler", t_hit + 0.45, (0, 0, 0))
        handling.evaluate(self.scene, t_hit)
        p = th.root.matrix_world.translation.copy()
        T = physics.flight_time(p, target) * (0.8 + 0.2 * eff.tempo())
        v = physics.ballistic(p, target, T)
        settle = physics.simulate(self.scene, t_hit, {th: (v, physics.spin_for(v, 1.5))})
        self.scene._event("handle", self, t, settle, action="kicks", thing=th.name)
        return self._end(t_hit + 0.45, wait)

    def give(self, to, thing=None, at=None, wait=True):
        """Hand what's held (or `thing`) to someone: walk to them, both reach, they take it."""
        from . import handling
        name = self._held(thing)
        side = self._hand(holding=name)
        other = self.scene.character(to) if isinstance(to, str) else to
        if other is None:
            raise ValueError(f"no one called {to!r} to give it to")
        oside = other._hand()
        th = self.scene.thing(name)
        t = self._start(at)
        self._approach = "close"
        try:
            self.walk_to(other.name, at=t, wait=True)
        finally:
            self._approach = True
        t = max(self.busy, other.busy, t)
        other.turn_to(self.name, at=t, wait=False)
        evalt = t + 0.25
        a = handling.carry_point(self, side, evalt)
        b = handling.carry_point(other, oside, evalt)
        meet = (a + b) / 2
        t1 = evalt + 0.5
        handling.reach(self, side, evalt, t1, meet)
        handling.reach(other, oside, evalt, t1, meet)
        handling.attach(self.scene, th, other.hands[oside], t1)
        t2 = t1 + 0.45
        handling.straighten(self, t1, t2)
        handling.straighten(other, t1, t2)
        keys.key(self.arms[side], "rotation_euler", t2, (0, 0, 0))
        keys.key(other.arms[oside], "rotation_euler", t2,
                 handling.aim(other, oside, t1, handling.carry_point(other, oside, t1)))
        del self.holding[side]
        other.holding[oside] = name
        th.holder = (other, oside)
        self.scene._event("handle", self, t, t2, action="gives", thing=name, listener=other)
        self.scene._end(other, t2, wait=False)
        return self._end(t2, wait)

    # ------------------------------------------------------------------ life
    def _alive(self, length):
        """Blinks, breathing, tears and sweat for the whole scene, added when the scene is finished."""
        from . import face
        face.drops(self, length)
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

    def foot_points(self):
        """Where this body's feet are now, in the world (for the foot-slide check): ankle bones on a
        skeleton, foot targets on a creature; [] if the feet can't slide on their own (a toy's are fixed
        to its legs)."""
        rig, roles = getattr(self, "rig", None), getattr(self, "roles", None) or {}
        if rig is not None and roles:
            return [rig.matrix_world @ rig.pose.bones[roles[r]].head for r in ("l_ankle", "r_ankle")
                    if r in roles and roles[r] in rig.pose.bones]
        feet = getattr(self, "feet", None)
        if isinstance(feet, dict):
            return [o.matrix_world.translation.copy() for o in feet.values()]
        return []

    def sway_parts(self):
        """What drifts while the body is "still": (part, (forward, sideways, twist) in degrees, seconds
        per drift). The trunk shifts its weight slowly, the head a little quicker."""
        return [(self.body, (0.7, 0.9, 1.2), 4.0), (getattr(self, "neck", None), (1.0, 0.8, 1.5), 2.6)]

    def sway(self, amount=1.0):
        """Weight shifts and small drifts of the trunk and head for the whole scene, added on top of the
        acting (noise on the curves, so every move and pose underneath stays as it was): a body is never
        perfectly still. Captured motion plays without it (its controls are off while it plays)."""
        from . import _compat
        if amount <= 0:
            return
        for part, degrees, seconds in self.sway_parts():
            if part is None:
                continue
            if not any(fc.data_path == "rotation_euler" for fc in _compat.fcurves(part)):
                part.keyframe_insert("rotation_euler", frame=1)
            for fc in _compat.fcurves(part):
                if fc.data_path != "rotation_euler" or any(m.type == "NOISE" for m in fc.modifiers):
                    continue
                strength = math.radians(degrees[fc.array_index]) * amount * 1.5
                for blend in ("ADD", "SUBTRACT"):    # two noises against each other: centred on the pose
                    m = fc.modifiers.new("NOISE")
                    m.blend_type, m.strength = blend, strength
                    m.scale = seconds * keys.CLOCK.fps * self.rng.uniform(0.8, 1.25)
                    m.phase = self.rng.uniform(0, 100)


# where the features go, as fractions of the face scale (x across, z up from the head centre)
FACE_LAYOUT = {"eye_x": 0.075, "eye_z": 0.02, "brow_z": 0.085, "mouth_z": -0.068, "nose_z": -0.015,
               "blush_x": 0.115, "blush_z": -0.035}


class ToyFigure(Character):
    name = "toy"
    drawing = "toy"   # the studio has a live drawing for this look
    label = "Toy figure"
    description = "A jointed vinyl toy: big head, stubby limbs, soft plastic"
