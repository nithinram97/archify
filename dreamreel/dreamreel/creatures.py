"""Creatures: any body, from a body plan.

A creature is a skeleton of joints (each with a radius) that becomes a smooth, skinned body, plus a head
with a face, ears, horns, wings, fins and tails as attached parts. Legs reach for foot targets on the ground
(inverse kinematics), and a footstep planner places those targets as the creature moves, so the same
code walks a biped, gallops a horse, scuttles a spider and keeps feet planted while turning.

    cast/rex.toml                         cast/ghost.toml
    type = "creature"                     type = "creature"
    body = "quadruped"                    body = "blob"
    color = "#4f9a4a"                     color = "white"
    wings = true                          float = true
    horns = "ram"

Body plans are classes (`dr.BodyPlan`): biped, quadruped, bird, fish, serpent, bug, spider and blob are
built in. A new plan describes its skeleton, legs and gait:

    class Centaur(dr.BodyPlan):
        capabilities = {"walk", "arms", "tail"}
        def skeleton(self, c):
            k = dr.Skeleton()
            ...                              # k.joint(name, (x, y, z), radius, parent), k.leg(...)
            return k

Coordinates: creature-local metres, facing -Y, z up, feet on z = 0.
"""
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

from . import look, plugins, shapes
from .character import Character, _deg, _wrap, heading_to
from .keys import hold, key, value_at
from .plugins import Param, Plugin


# ---------------------------------------------------------------------- skeleton description
class Joint:
    def __init__(self, name, at, radius, parent=None, deform=True):
        self.name, self.at, self.radius, self.parent, self.deform = name, Vector(at), radius, parent, deform


class LegSpec:
    """A leg: three joints (hip, knee, foot). `bend` is the direction the knee points (for the pole)."""

    def __init__(self, name, hip, knee, foot, bend=(0, -1, 0), group="legs"):
        self.name, self.hip, self.knee, self.foot, self.bend, self.group = name, hip, knee, foot, Vector(bend), group


class Skeleton:
    """What a body plan returns: joints (a tree), legs, and which joints are head, chest, spine, tail, wings."""

    def __init__(self):
        self.joints = {}
        self.legs = []
        self.head = None          # joint the head attaches to (the head turns about it)
        self.head_offset = Vector((0, 0, 0))   # head centre relative to that joint
        self.head_r = 0.1
        self.chest = None         # joint arms attach to (bipeds)
        self.shoulders = []       # (side, position) for rigid arms
        self.spine = []           # joints that sway when swimming or slithering, head to tail
        self.tail = []            # joints of the tail, base to tip
        self.wings = []           # (side, [joint names root to tip])
        self.squash = (1.0, 1.0, 1.0)   # scale the finished body mesh (e.g. flatten a fish sideways)

    def joint(self, name, at, radius, parent=None, deform=True):
        self.joints[name] = Joint(name, at, radius, parent, deform)
        return name

    def leg(self, name, hip, knee, foot, bend=(0, -1, 0), group="legs"):
        self.legs.append(LegSpec(name, hip, knee, foot, bend, group))

    def at(self, name):
        return self.joints[name].at


# ---------------------------------------------------------------------- body plans
class BodyPlan(Plugin):
    """A kind of body: its skeleton, how it moves and what it can do."""
    kind = "body"
    abstract = True
    capabilities = {"walk"}
    locomotion = "walk"         # walk, swim, slither, hop
    default_head = "round"
    default_colors = ("chestnut", "cream")

    @classmethod
    def describe_extra(cls):
        return {"capabilities": sorted(cls.capabilities), "locomotion": cls.locomotion}

    def skeleton(self, c):
        raise NotImplementedError

    def gait(self, c, run):
        """{leg name: phase in the stride cycle (0-1)}, duty factor (share of the cycle a foot is down)."""
        legs = c.skel.legs
        return {leg.name: (i % 2) * 0.5 for i, leg in enumerate(legs)}, (0.38 if run else 0.62)

    def stride(self, c, speed, run):
        """(metres per step, seconds per step)."""
        L = c.leg_len
        return L * (1.1 if run else 0.75) * min(speed, 1.5) ** 0.3, (0.24 if run else 0.34) / max(0.6, speed) ** 0.6


def _p(c, name, default=1.0):
    return float(c.get(name, default) or default)


class Biped(BodyPlan):
    """Two legs, two arms: goblins, aliens, monsters, apes, robots."""
    description = "Two legs and two arms (goblins, aliens, monsters, apes)"
    capabilities = {"walk", "arms"}

    def skeleton(self, c):
        S, G, LL = c.size, _p(c, "girth"), _p(c, "legs_length")
        k = Skeleton()
        hip_h = 0.36 * S * LL
        r = 0.14 * S * G
        k.joint("pelvis", (0, 0, hip_h), r * 1.05)
        k.joint("spine", (0, 0, hip_h + 0.16 * S), r, "pelvis")
        k.joint("chest", (0, 0, hip_h + 0.3 * S), r * 1.0, "spine")
        k.joint("neck", (0, 0, hip_h + 0.42 * S * _p(c, "neck")), r * 0.45, "chest")
        k.head, k.chest = "neck", "chest"
        k.head_r = 0.17 * S
        k.head_offset = Vector((0, 0, k.head_r * 0.8))
        for side, nm in ((1, "L"), (-1, "R")):
            x = side * r * 0.55
            k.joint(f"hip.{nm}", (x, 0, hip_h - r * 0.2), r * 0.5, "pelvis")
            k.joint(f"knee.{nm}", (x, -0.05 * S, hip_h * 0.52), 0.05 * S * G, f"hip.{nm}")
            k.joint(f"foot.{nm}", (x, -0.02 * S, 0.045 * S), 0.055 * S, f"knee.{nm}")
            k.leg(f"leg.{nm}", f"hip.{nm}", f"knee.{nm}", f"foot.{nm}", bend=(0, -1, 0))
            k.shoulders.append((side, Vector((side * r * 0.95, 0, hip_h + 0.3 * S))))
        if _p(c, "tail", 0) > 0:
            _tail(k, "pelvis", (0, r * 0.8, hip_h), S * _p(c, "tail", 0), r * 0.4, up=0.02)
        return k


class Quadruped(BodyPlan):
    """Four legs: dogs, cats, horses, lions, dinosaurs; with wings, a dragon."""
    description = "Four legs (dogs, cats, horses, dragons with wings)"
    capabilities = {"walk", "tail", "rear"}
    default_head = "snout"

    def skeleton(self, c):
        S, G, L, LL, N = c.size, _p(c, "girth"), _p(c, "length"), _p(c, "legs_length"), _p(c, "neck")
        k = Skeleton()
        leg_h = 0.4 * S * LL
        r = 0.14 * S * G
        z = leg_h + r * 0.35
        hy, cy = 0.27 * S * L, -0.27 * S * L
        k.joint("pelvis", (0, hy, z), r * 1.02)
        k.joint("spine", (0, 0, z + 0.02 * S), r * 0.95, "pelvis")
        k.joint("chest", (0, cy, z + 0.03 * S), r * 1.08, "spine")
        k.joint("neck", (0, cy - 0.1 * S * N, z + 0.16 * S * N), r * 0.6, "chest")
        k.joint("head", (0, cy - 0.16 * S * N - 0.03 * S, z + 0.3 * S * N), r * 0.45, "neck")
        k.head, k.head_r = "head", 0.13 * S
        k.head_offset = Vector((0, -k.head_r * 0.2, k.head_r * 0.3))
        k.spine = ["chest", "spine", "pelvis"]
        for name, y, parent, front in (("LF", cy, "chest", True), ("RF", cy, "chest", True),
                                       ("LH", hy, "pelvis", False), ("RH", hy, "pelvis", False)):
            side = 1 if name[0] == "L" else -1
            x = side * r * 0.62
            bend = (0, 1, 0) if front else (0, -1, 0)
            k.joint(f"hip.{name}", (x, y, z - r * 0.35), r * 0.48, parent)
            k.joint(f"knee.{name}", (x, y + bend[1] * 0.05 * S, leg_h * 0.5), 0.05 * S * G, f"hip.{name}")
            k.joint(f"foot.{name}", (x, y - 0.01 * S, 0.05 * S), 0.055 * S * G, f"knee.{name}")
            k.leg(f"leg.{name}", f"hip.{name}", f"knee.{name}", f"foot.{name}", bend=bend)
        if _p(c, "tail", 1.0) > 0:
            _tail(k, "pelvis", (0, hy + r * 0.8, z + 0.02 * S), 0.5 * S * _p(c, "tail", 1.0), r * 0.35, up=0.08)
        if c.get("wings"):
            _wings(k, "chest", (r * 0.7, cy + 0.08 * S, z + r * 0.6), 0.5 * S)
        return k

    def gait(self, c, run):
        if run:   # gallop
            return {"leg.LH": 0.0, "leg.RH": 0.1, "leg.LF": 0.5, "leg.RF": 0.6}, 0.35
        if c.speed_now >= 1.3:  # trot: diagonal pairs together
            return {"leg.LF": 0.0, "leg.RH": 0.0, "leg.RF": 0.5, "leg.LH": 0.5}, 0.5
        return {"leg.LH": 0.0, "leg.LF": 0.25, "leg.RH": 0.5, "leg.RF": 0.75}, 0.7   # walk


class Bird(BodyPlan):
    """Two thin legs, wings, a beak and tail feathers."""
    description = "Two legs and wings (birds, chickens, penguins)"
    capabilities = {"walk", "wings", "fly", "tail"}
    default_head = "beak"
    default_colors = ("sky", "white")

    def skeleton(self, c):
        S, G, LL = c.size, _p(c, "girth"), _p(c, "legs_length")
        k = Skeleton()
        hip_h = 0.22 * S * LL
        r = 0.16 * S * G
        k.joint("pelvis", (0, 0.06 * S, hip_h + r * 0.6), r)
        k.joint("chest", (0, -0.1 * S, hip_h + r * 0.9), r * 1.05, "pelvis")
        k.joint("neck", (0, -0.16 * S, hip_h + r * 1.7 + 0.08 * S * _p(c, "neck")), r * 0.45, "chest")
        k.head, k.head_r = "neck", 0.13 * S
        k.head_offset = Vector((0, -k.head_r * 0.2, k.head_r * 0.7))
        k.joint("tail", (0, 0.3 * S, hip_h + r * 0.9), r * 0.3, "pelvis")
        k.tail = ["tail"]
        for side, nm in ((1, "L"), (-1, "R")):
            x = side * r * 0.4
            k.joint(f"hip.{nm}", (x, 0.04 * S, hip_h + r * 0.2), r * 0.35, "pelvis")
            k.joint(f"knee.{nm}", (x, 0.07 * S, hip_h * 0.5), 0.022 * S, f"hip.{nm}")
            k.joint(f"foot.{nm}", (x, 0.02 * S, 0.025 * S), 0.03 * S, f"knee.{nm}")
            k.leg(f"leg.{nm}", f"hip.{nm}", f"knee.{nm}", f"foot.{nm}", bend=(0, 1, 0))
        _wings(k, "chest", (r * 0.85, -0.08 * S, hip_h + r * 1.1), 0.45 * S, feathers=True)
        return k

    def stride(self, c, speed, run):
        return c.leg_len * (0.9 if run else 0.6), (0.18 if run else 0.24) / max(0.6, speed) ** 0.6


class Fish(BodyPlan):
    """A body that swims: fins and a tail fin."""
    description = "Swims (fish, sharks, whales)"
    capabilities = {"swim", "tail"}
    locomotion = "swim"
    default_head = "fish"
    default_colors = ("orange", "cream")

    def skeleton(self, c):
        S, G, L = c.size, _p(c, "girth"), _p(c, "length")
        k = Skeleton()
        z = 0.7 * S
        k.joint("nose", (0, -0.32 * S * L, z), 0.07 * S * G)
        k.joint("body1", (0, -0.15 * S * L, z), 0.16 * S * G, "nose")
        k.joint("body2", (0, 0.05 * S * L, z), 0.14 * S * G, "body1")
        k.joint("body3", (0, 0.22 * S * L, z), 0.08 * S * G, "body2")
        k.joint("tail", (0, 0.36 * S * L, z), 0.03 * S * G, "body3")
        k.head, k.head_r = "nose", 0.11 * S * G
        k.head_offset = Vector((0, 0.02 * S, 0))
        k.spine = ["body1", "body2", "body3", "tail"]
        k.tail = ["tail"]
        k.squash = (0.62, 1.0, 1.0)
        return k

    def stride(self, c, speed, run):
        return 0.35 * c.size * _p(c, "length") * (1.5 if run else 1.0), 0.4 / max(0.6, speed) ** 0.5


class Serpent(BodyPlan):
    """A long body that slithers: snakes, worms, eels, sea serpents."""
    description = "Slithers (snakes, worms, eels)"
    capabilities = {"slither", "tail"}
    locomotion = "slither"
    default_head = "snout"
    default_colors = ("green", "yellow")

    def skeleton(self, c):
        S, G, L = c.size, _p(c, "girth"), _p(c, "length")
        k = Skeleton()
        n = 9
        r = 0.06 * S * G
        prev = None
        for i in range(n):
            t = i / (n - 1)
            rad = r * (1.0 - 0.75 * t ** 1.5) * (0.85 if i == 0 else 1.0)
            name = f"s{i}"
            k.joint(name, (0, -0.4 * S * L + t * 1.3 * S * L, rad), rad, prev)
            prev = name
        k.joint("neck", (0, -0.47 * S * L, r * 2.2), r * 0.8, "s0")
        k.head, k.head_r = "neck", 0.08 * S * G
        k.head_offset = Vector((0, -k.head_r * 0.4, 0))
        k.spine = [f"s{i}" for i in range(1, n)]
        k.tail = k.spine[-3:]
        return k

    def stride(self, c, speed, run):
        return 0.3 * c.size * _p(c, "length"), 0.45 / max(0.6, speed) ** 0.5


class Bug(BodyPlan):
    """Six thin legs (or `leg_pairs` of them): ants, beetles, crabs-ish."""
    description = "Six legs (insects; set leg pairs for more)"
    capabilities = {"walk"}
    default_head = "bug"
    default_colors = ("charcoal", "brown")
    pairs = 3

    def skeleton(self, c):
        S, G, L = c.size, _p(c, "girth"), _p(c, "length")
        n = int(c.get("leg_pairs") or self.pairs)
        k = Skeleton()
        h = 0.18 * S * _p(c, "legs_length")
        k.joint("thorax", (0, -0.05 * S * L, h), 0.1 * S * G)
        k.joint("abdomen", (0, 0.22 * S * L, h + 0.02 * S), 0.16 * S * G, "thorax")
        k.joint("neck", (0, -0.16 * S * L, h + 0.02 * S), 0.06 * S * G, "thorax")
        k.head, k.head_r = "neck", 0.09 * S * G
        k.head_offset = Vector((0, -k.head_r * 0.5, 0.01 * S))
        for p in range(n):
            y = -0.05 * S * L + (p - (n - 1) / 2) * 0.09 * S * L
            for side, nm in ((1, "L"), (-1, "R")):
                tag = f"{nm}{p}"
                k.joint(f"hip.{tag}", (side * 0.07 * S, y, h), 0.025 * S, "thorax")
                k.joint(f"knee.{tag}", (side * 0.2 * S, y, h + 0.1 * S), 0.02 * S, f"hip.{tag}")
                k.joint(f"foot.{tag}", (side * 0.32 * S, y * 1.3, 0.015 * S), 0.015 * S, f"knee.{tag}")
                k.leg(f"leg.{tag}", f"hip.{tag}", f"knee.{tag}", f"foot.{tag}", bend=(side, 0, 1))
        return k

    def gait(self, c, run):
        phases = {}
        for leg in c.skel.legs:
            tag = leg.name.split(".")[1]
            side, p = tag[0], int(tag[1:])
            phases[leg.name] = ((p + (0 if side == "L" else 1)) % 2) * 0.5
        return phases, 0.5

    def stride(self, c, speed, run):
        return 0.12 * c.size * (1.5 if run else 1.0), 0.16 / max(0.6, speed) ** 0.5


class Spider(Bug):
    """Eight long legs."""
    description = "Eight long legs (spiders)"
    pairs = 4
    default_colors = ("black", "charcoal")


class Blob(BodyPlan):
    """No legs: slimes, ghosts, jelly monsters. Moves by hopping (or floats with `float = true`)."""
    description = "No legs: hops or floats (slimes, ghosts)"
    capabilities = {"hop"}
    locomotion = "hop"
    default_head = "none"
    default_colors = ("mint", "white")

    def skeleton(self, c):
        S, G = c.size, _p(c, "girth")
        k = Skeleton()
        lift = 0.35 * S if c.get("float") else 0.0
        k.joint("base", (0, 0, 0.12 * S * G + lift), 0.2 * S * G)
        k.joint("top", (0, 0, 0.42 * S * G + lift), 0.17 * S * G, "base")
        k.head, k.head_r = "top", 0.17 * S * G
        k.head_offset = Vector((0, 0, 0))
        if c.get("float"):
            k.joint("wisp", (0, 0.08 * S, lift * 0.25), 0.05 * S, "base")
            k.tail = ["wisp"]
        return k

    def stride(self, c, speed, run):
        return 0.25 * c.size, 0.45 / max(0.6, speed) ** 0.5


def _tail(k, parent, start, length, radius, up=0.05, n=4):
    prev = parent
    x, y, z = start
    for i in range(n):
        t = (i + 1) / n
        name = f"tail{i}"
        k.joint(name, (x, y + length * t, z + up * length * math.sin(t * 2.0)), radius * (1 - 0.7 * t), prev)
        k.tail.append(name)
        prev = name


def _wings(k, parent, shoulder, span, feathers=False):
    sx, sy, sz = shoulder
    for side, nm in ((1, "L"), (-1, "R")):
        a = k.joint(f"wing1.{nm}", (side * (sx + span * 0.12), sy + span * 0.1, sz + span * 0.04), 0.02, parent, deform=False)
        b = k.joint(f"wing2.{nm}", (side * (sx + span * 0.2), sy + span * 0.45, sz + span * 0.02), 0.015, a, deform=False)
        k.wings.append((side, [a, b]))
    k.feathers = feathers


# ---------------------------------------------------------------------- the creature
HEADS = ("round", "snout", "beak", "fish", "bug", "none")
EARS = ("none", "pointy", "round", "floppy", "long")
HORNS = ("none", "small", "ram", "unicorn")


class Creature(Character):
    """Any body, from a body plan; with a face that talks and feels like everyone else's."""
    label = "Creature"
    description = "Any body: animals, monsters, bugs, birds, fish, slimes"
    default_capabilities = ("face",)   # plus the body plan's (see `capabilities`)
    params = [
        Param("name", "text"),
        Param("body", "body", default="quadruped", label="Body plan"),
        Param("size", "number", default=1.0, min=0.2, max=5, step=0.1),
        Param("length", "number", default=1.0, min=0.5, max=2.5, step=0.1, label="Body length"),
        Param("legs_length", "number", default=1.0, min=0.4, max=2.5, step=0.1, label="Leg length"),
        Param("neck", "number", default=1.0, min=0.3, max=3, step=0.1, label="Neck length"),
        Param("tail", "number", default=None, min=0, max=3, step=0.1, label="Tail length"),
        Param("girth", "number", default=1.0, min=0.5, max=2, step=0.1, label="Chunkiness"),
        Param("leg_pairs", "number", default=None, min=2, max=6, step=1, label="Leg pairs (bugs)"),
        Param("color", "color", default=None, label="Colour"),
        Param("belly", "color", default=None, label="Belly colour"),
        Param("pattern", "choice", default="none", choices=("none", "spots", "stripes")),
        Param("pattern_color", "color", default="charcoal", label="Pattern colour"),
        Param("head", "choice", default=None, choices=HEADS, label="Head"),
        Param("ears", "choice", default="none", choices=EARS),
        Param("horns", "choice", default="none", choices=HORNS),
        Param("wings", "bool", default=False),
        Param("float", "bool", default=False, label="Floats (blobs)"),
        Param("eyes", "choice", default="normal", choices=("small", "normal", "big")),
        Param("hair", "hair", default="none", label="Hair / mane"),
        Param("hair_color", "color", default="brown", label="Hair colour"),
        Param("extras", "extras", default=[]),
        Param("voice", "voice"),
    ]

    # ------------------------------------------------------------------ setup
    def validate(self):
        self.plan = plugins.get("body", self.spec.get("body") or "quadruped")()
        main, belly = self.plan.default_colors
        self.spec.setdefault("color", main)
        if not self.spec.get("color"):
            self.spec["color"] = main
        if not self.spec.get("belly"):
            self.spec["belly"] = belly
        if not self.spec.get("head"):
            self.spec["head"] = self.plan.default_head
        self.spec.update(nose=False, blush=self.spec.get("blush", False))
        super().validate()

    @property
    def capabilities(self):
        caps = set(self.plan.capabilities) | {"face"}
        if self.get("wings"):
            caps |= {"wings", "fly"}
        if self.skel.tail:
            caps.add("tail")
        return caps

    def color(self, key_, default="white"):
        if key_ in ("skin", "top", "bottom", "shoes"):
            return self.spec["color"]
        return super().color(key_, default)

    def proportions(self):
        self.size = float(self.get("size", 1.0) or 1.0)
        self.speed_now = 1.0
        self.skel = self.plan.skeleton(self)
        k = self.skel
        self.hr = self.head_r = k.head_r
        self.H = self.hr / 0.19            # the shared face code is sized from H
        self.hip_z = 0.0
        self.hc = self.head_center = k.head_offset.copy()
        legs = [(k.at(l.hip) - k.at(l.knee)).length + (k.at(l.knee) - k.at(l.foot)).length for l in k.legs]
        self.leg_len = max(legs) if legs else 0.3 * self.size
        head_world = k.at(k.head) + k.head_offset
        self.top_z = k.at(k.head).z
        self.neck_z = self.top_z
        self.body_r = max(j.radius for j in k.joints.values())
        self.head_rest = head_world

    def build(self):
        self.build_rig()
        self.build_legs()
        self.build_body()
        self.build_arms()
        self.build_head()
        self.build_face()
        self.build_hair()
        self.build_extras()
        self.build_features()

    # ------------------------------------------------------------------ rig
    def build_rig(self):
        n, k = self.name, self.skel
        self.root = shapes.empty(n)
        self.root.empty_display_size = 0.3
        self.hips = shapes.empty(f"{n}.hips", self.root)
        self.body = shapes.empty(f"{n}.body", self.hips)
        arm = bpy.data.armatures.new(f"{n}.rig")
        self.rig = bpy.data.objects.new(f"{n}.rig", arm)
        bpy.context.scene.collection.objects.link(self.rig)
        self.rig.parent = self.body
        bpy.context.view_layer.objects.active = self.rig
        bpy.ops.object.mode_set(mode="EDIT")
        roots = [j for j in k.joints.values() if j.parent is None]
        eb = {}
        for j in roots:
            b = arm.edit_bones.new(j.name)
            b.head = j.at
            b.tail = j.at + Vector((0, 0, max(0.02, j.radius * 0.5)))
            eb[j.name] = b
        for j in k.joints.values():           # joints are added parents-first
            if j.parent is None:
                continue
            b = arm.edit_bones.new(j.name)
            b.head = k.at(j.parent)
            b.tail = j.at if (j.at - k.at(j.parent)).length > 1e-4 else j.at + Vector((0, 0, 0.01))
            b.parent = eb[j.parent]
            b.use_connect = False
            b.use_deform = j.deform
            eb[j.name] = b
        bpy.ops.object.mode_set(mode="OBJECT")
        for pb in self.rig.pose.bones:
            pb.rotation_mode = "QUATERNION"
        self.rig.show_in_front = False

    def bone_world_rest(self, name):
        b = self.rig.data.bones[name]
        return b.matrix_local

    def attach(self, obj, bone):
        """Make obj follow a bone while keeping where it is now (creature-local rest coordinates)."""
        b = self.rig.data.bones[bone]
        tail = b.matrix_local @ Matrix.Translation((0, b.length, 0))
        obj.parent = self.rig
        obj.parent_type = "BONE"
        obj.parent_bone = bone
        obj.matrix_parent_inverse = tail.inverted()
        return obj

    def turn_bone(self, name, t, rot, ease="smooth"):
        """Key a bone's rotation, given as a Quaternion (or (x, y, z) Euler degrees) in creature space."""
        if not isinstance(rot, Quaternion):
            from mathutils import Euler
            rot = Euler(tuple(_deg(a) for a in rot), "XYZ").to_quaternion()
        pb = self.rig.pose.bones[name]
        rest = self.rig.data.bones[name].matrix_local.to_quaternion()
        local = rest.inverted() @ rot @ rest
        key(pb, "rotation_quaternion", t, tuple(local), ease)

    def wave(self, bones, t0, t1, period, amp_deg, axis="Z", phase_step=0.9, grow=1.0):
        """Sway a chain of bones in a travelling wave (tails, fish, snakes), then settle."""
        if not bones:
            return
        ax = {"X": Vector((1, 0, 0)), "Y": Vector((0, 1, 0)), "Z": Vector((0, 0, 1))}[axis]
        for b in bones:
            hold(self.rig.pose.bones[b], "rotation_quaternion", t0)
        steps = max(2, int((t1 - t0) / (period / 8)))
        for s in range(1, steps + 1):
            t = t0 + (t1 - t0) * s / steps
            fade = min(1.0, (t - t0) / max(0.01, period * 0.5), (t1 - t) / max(0.01, period * 0.5) + 0.0)
            for i, b in enumerate(bones):
                a = amp_deg * (1 + grow * i / max(1, len(bones) - 1)) / (1 + grow) * fade
                ang = _deg(a) * math.sin(2 * math.pi * (t - t0) / period - phase_step * i)
                self.turn_bone(b, t, Quaternion(ax, ang))
        for b in bones:
            self.turn_bone(b, t1 + 0.15, Quaternion())

    # ------------------------------------------------------------------ legs
    def build_legs(self):
        n, k = self.name, self.skel
        self.feet = {}      # leg name -> foot target empty (world space)
        self.foot_home = {}  # leg name -> rest (x, y, z) relative to the root
        self.legs, self.arms = {}, {}
        for leg in k.legs:
            target = shapes.empty(f"{n}.{leg.name}.target")
            target.location = k.at(leg.foot)
            self.feet[leg.name] = target
            self.foot_home[leg.name] = k.at(leg.foot).copy()
            pole = shapes.empty(f"{n}.{leg.name}.pole", self.body, k.at(leg.knee) + leg.bend * self.leg_len * 2)
            pb = self.rig.pose.bones[leg.foot]
            ik = pb.constraints.new("IK")
            ik.name = "IK"
            ik.target = target
            ik.pole_target = pole
            ik.pole_angle = _deg(-90)
            ik.chain_count = 2
            ik.use_stretch = False
            leg.ik = ik
        self.calibrate_poles()

    def calibrate_poles(self):
        """Blender's IK pole angle depends on each bone's orientation, so try the four usual angles and
        keep, per leg, the one that leaves the knee where the skeleton put it."""
        k = self.skel
        if not k.legs:
            return
        best = {leg.name: (None, 1e9) for leg in k.legs}
        for angle in (-90, 90, 0, 180):
            for leg in k.legs:
                leg.ik.pole_angle = _deg(angle)
            bpy.context.view_layer.update()
            for leg in k.legs:
                knee = self.rig.pose.bones[leg.knee].tail
                err = (knee - k.at(leg.knee)).length
                if err < best[leg.name][1]:
                    best[leg.name] = (angle, err)
        for leg in k.legs:
            leg.ik.pole_angle = _deg(best[leg.name][0])

    # ------------------------------------------------------------------ body mesh
    def build_body(self):
        k, n = self.skel, self.name
        names = list(k.joints)
        index = {nm: i for i, nm in enumerate(names)}
        verts = [k.joints[nm].at for nm in names]
        edges = [(index[j.parent], index[j.name]) for j in k.joints.values() if j.parent and j.deform]
        me = bpy.data.meshes.new(f"{n}.skin")
        me.from_pydata([tuple(v) for v in verts], edges, [])
        ob = bpy.data.objects.new(f"{n}.body", me)
        bpy.context.scene.collection.objects.link(ob)
        ob.modifiers.new("skin", "SKIN")
        used = {i for e in edges for i in e} | {index[j.name] for j in k.joints.values() if j.parent is None}
        for i, nm in enumerate(names):
            r = k.joints[nm].radius if i in used else 0.001
            me.skin_vertices[0].data[i].radius = (r, r)
        me.skin_vertices[0].data[index[next(j.name for j in k.joints.values() if j.parent is None)]].use_root = True
        sub = ob.modifiers.new("smooth", "SUBSURF")
        sub.levels = 2
        dg = bpy.context.evaluated_depsgraph_get()
        baked = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.clear()
        ob.data = baked
        bpy.data.meshes.remove(me)
        sx, sy, sz = k.squash
        if (sx, sy, sz) != (1, 1, 1):
            spine_x = 0.0
            for v in baked.vertices:
                v.co.x = spine_x + (v.co.x - spine_x) * sx
                v.co.z = v.co.z if sz == 1 else v.co.z * sz
        for p in baked.polygons:
            p.use_smooth = True
        mod = ob.modifiers.new("smooth", "SUBSURF")
        mod.levels = 1
        mod.render_levels = 1
        baked.materials.append(self.skin_material())
        self.skin_weights(ob)
        self.paint_belly(ob)
        ob.parent = self.rig
        am = ob.modifiers.new("rig", "ARMATURE")
        am.object = self.rig
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
        self.body_mesh = ob

    def skin_weights(self, ob):
        """Weight each vertex to the nearest bones (smoothly between two)."""
        segs = []
        for b in self.rig.data.bones:
            if b.use_deform and b.parent is not None:
                segs.append((b.name, b.head_local.copy(), b.tail_local.copy()))
        if not segs:
            segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in self.rig.data.bones]
        groups = {nm: ob.vertex_groups.new(name=nm) for nm, _, _ in segs}

        def dist(p, a, b):
            ab = b - a
            L = ab.length_squared
            t = 0.0 if L < 1e-12 else max(0.0, min(1.0, (p - a).dot(ab) / L))
            return (p - (a + ab * t)).length

        for v in ob.data.vertices:
            ds = sorted((dist(v.co, a, b), nm) for nm, a, b in segs)
            (d1, n1) = ds[0]
            if len(ds) > 1 and ds[1][0] < d1 * 1.5 + 0.01:
                d2, n2 = ds[1]
                w1, w2 = 1 / (d1 + 1e-4) ** 3, 1 / (d2 + 1e-4) ** 3
                s = w1 + w2
                groups[n1].add([v.index], w1 / s, "REPLACE")
                groups[n2].add([v.index], w2 / s, "REPLACE")
            else:
                groups[n1].add([v.index], 1.0, "REPLACE")

    TORSO = ("pelvis", "spine", "chest", "neck", "head", "body", "nose", "thorax", "abdomen", "base", "top", "s")

    def paint_belly(self, ob):
        """A 0-1 'belly' value per vertex: the underside (or, for bipeds, the front) of the torso."""
        attr = ob.data.attributes.new("belly", "FLOAT", "POINT")
        front = "arms" in self.plan.capabilities
        torso = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in self.rig.data.bones
                 if b.name.split(".")[0].rstrip("0123456789") in self.TORSO or b.name in self.TORSO]
        if not torso:
            return
        for v in ob.data.vertices:
            best = None
            for nm, a, b in torso:
                ab = b - a
                L = ab.length_squared
                t = 0.0 if L < 1e-12 else max(0.0, min(1.0, (v.co - a).dot(ab) / L))
                p = a + ab * t
                d = (v.co - p).length
                if best is None or d < best[0]:
                    best = (d, p, nm)
            d, p, nm = best
            r = max(0.01, self.skel.joints[nm].radius if nm in self.skel.joints else self.body_r)
            if d > r * 1.6:      # a leg or tail, not the torso
                attr.data[v.index].value = 0.0
                continue
            depth = (p.y - v.co.y) if front else (p.z - v.co.z)
            f = max(0.0, min(1.0, (depth / r - 0.25) / 0.45))
            attr.data[v.index].value = f * f * (3 - 2 * f)

    def skin_material(self):
        """Main colour with a lighter belly, optionally spots or stripes."""
        main, belly = self.spec["color"], self.spec["belly"]
        pattern = self.get("pattern", "none")
        mat = bpy.data.materials.new(f"{self.name}.skin")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        bsdf.inputs["Roughness"].default_value = 0.5
        if bsdf.inputs.get("Coat Weight"):
            bsdf.inputs["Coat Weight"].default_value = 0.2
        mat.diffuse_color = look.rgba(main)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        belly_attr = nt.nodes.new("ShaderNodeAttribute")
        belly_attr.attribute_name = "belly"
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        sock = lambda socks, ident: next(s for s in socks if s.identifier == ident)  # noqa: E731
        sock(mix.inputs, "A_Color").default_value = look.rgba(main)
        sock(mix.inputs, "B_Color").default_value = look.rgba(belly)
        nt.links.new(belly_attr.outputs["Fac"], sock(mix.inputs, "Factor_Float"))
        color_out = sock(mix.outputs, "Result_Color")
        if pattern in ("spots", "stripes"):
            if pattern == "spots":
                tex = nt.nodes.new("ShaderNodeTexVoronoi")
                tex.inputs["Scale"].default_value = 9.0 / max(0.3, self.size)
                nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
                ramp = nt.nodes.new("ShaderNodeMapRange")
                ramp.inputs["From Min"].default_value = 0.22
                ramp.inputs["From Max"].default_value = 0.18
                nt.links.new(tex.outputs["Distance"], ramp.inputs["Value"])
            else:
                tex = nt.nodes.new("ShaderNodeTexWave")
                tex.inputs["Scale"].default_value = 3.0 / max(0.3, self.size)
                tex.wave_type = "BANDS"
                tex.bands_direction = "Y"
                nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
                ramp = nt.nodes.new("ShaderNodeMapRange")
                ramp.inputs["From Min"].default_value = 0.55
                ramp.inputs["From Max"].default_value = 0.6
                nt.links.new(tex.outputs["Fac"], ramp.inputs["Value"])
            mix2 = nt.nodes.new("ShaderNodeMix")
            mix2.data_type = "RGBA"
            nt.links.new(color_out, sock(mix2.inputs, "A_Color"))
            sock(mix2.inputs, "B_Color").default_value = look.rgba(self.get("pattern_color", "charcoal"))
            nt.links.new(ramp.outputs["Result"], sock(mix2.inputs, "Factor_Float"))
            color_out = sock(mix2.outputs, "Result_Color")
        nt.links.new(color_out, bsdf.inputs["Base Color"])
        return mat

    # ------------------------------------------------------------------ arms (bipeds)
    def build_arms(self):
        k = self.skel
        self.arms = {}
        if "arms" not in self.plan.capabilities or not k.chest:
            return
        n, S = self.name, self.size
        anchor = shapes.empty(f"{n}.chest")
        self.attach(anchor, k.chest)
        for side, at in k.shoulders:
            piv = shapes.empty(f"{n}.arm.{'L' if side > 0 else 'R'}", anchor, at)
            arm = shapes.capsule(f"{n}.arm", 0.05 * S, 0.2 * S * float(self.get("legs_length", 1) or 1), self.color("skin"),
                                 piv, rot=(0, _deg(-12 * side), 0), hang=True)
            shapes.sphere(f"{n}.hand", 0.065 * S, self.color("skin"), arm, at=(0, 0, -(0.2 * S + 0.1 * S)))
            self.arms[side] = piv

    # ------------------------------------------------------------------ head and features
    def build_head(self):
        k, n, hr, hc = self.skel, self.name, self.hr, self.hc
        self.neck = shapes.empty(f"{n}.neck")
        self.neck.location = k.at(k.head)
        self.attach(self.neck, k.head)
        kind = self.get("head")
        col = self.color("skin")
        if kind in ("round", "snout", "bug", "beak"):
            shapes.sphere(f"{n}.head", hr, col, self.neck, at=hc)
        if kind == "snout":
            shapes.ellipsoid(f"{n}.snout", hr * 0.5, hr * 0.72, hr * 0.42, col, self.neck,
                             at=hc + Vector((0, -hr * 0.95, -hr * 0.42)))
            shapes.sphere(f"{n}.nose", hr * 0.14, look.plastic("#1c1a1a", 0.2, 0.8), self.neck,
                          at=hc + Vector((0, -hr * 1.62, -hr * 0.3)))
        elif kind == "beak":
            shapes.cylinder(f"{n}.beak", hr * 0.32, hr * 0.75, look.plastic("orange", 0.4, 0.3), self.neck,
                            at=hc + Vector((0, -hr * 0.8, -hr * 0.15)), rot=(_deg(90), 0, 0), r2=0.0, bevel=0)
        elif kind == "fish":
            pass   # the body is the head
        elif kind == "bug":
            for side in (1, -1):
                shapes.cylinder(f"{n}.antenna", hr * 0.05, hr * 1.4, "charcoal", self.neck,
                                at=hc + Vector((side * hr * 0.35, -hr * 0.5, hr * 0.6)),
                                rot=(_deg(-35), _deg(25 * side), 0), bevel=0)

    def face_point(self, x, z, inset=0.006):
        hr = self.hr
        y = -math.sqrt(max(0.0, hr * hr - x * x - z * z)) + inset * self.H
        return Vector((x, y, z)) + self.hc

    def build_face(self):
        super().build_face()
        kind, hr, hc = self.get("head"), self.hr, self.hc
        if kind == "snout":
            self.mouth.location = hc + Vector((0, -hr * 1.42, -hr * 0.62))
        elif kind == "beak":
            self.mouth.location = hc + Vector((0, -hr * 0.6, -hr * 0.45))
            self.mouth.scale = (0.6, 1, 1)
        if kind in ("bug",):
            for e in self.eyes:
                e.scale = (1.5, 1.2, 1.5)

    def build_features(self):
        n, hr, hc, col = self.name, self.hr, self.hc, self.color("skin")
        ears = self.get("ears", "none")
        for side in (1, -1):
            if ears == "pointy":
                shapes.cylinder(f"{n}.ear", hr * 0.28, hr * 0.6, col, self.neck,
                                at=hc + Vector((side * hr * 0.5, hr * 0.1, hr * 0.7)), rot=(0, _deg(25 * side), 0), r2=0.0, bevel=0)
            elif ears == "round":
                shapes.ellipsoid(f"{n}.ear", hr * 0.3, hr * 0.1, hr * 0.3, col, self.neck,
                                 at=hc + Vector((side * hr * 0.7, hr * 0.1, hr * 0.7)))
            elif ears == "floppy":
                shapes.ellipsoid(f"{n}.ear", hr * 0.18, hr * 0.12, hr * 0.5, col, self.neck,
                                 at=hc + Vector((side * hr * 1.0, hr * 0.1, -hr * 0.1)), rot=(0, _deg(-15 * side), 0))
            elif ears == "long":
                shapes.ellipsoid(f"{n}.ear", hr * 0.18, hr * 0.08, hr * 0.85, col, self.neck,
                                 at=hc + Vector((side * hr * 0.35, hr * 0.15, hr * 1.4)), rot=(0, _deg(10 * side), 0))
        horns = self.get("horns", "none")
        horn = look.plastic("cream", 0.4, 0.3)
        if horns == "small":
            for side in (1, -1):
                shapes.cylinder(f"{n}.horn", hr * 0.12, hr * 0.45, horn, self.neck,
                                at=hc + Vector((side * hr * 0.4, -hr * 0.1, hr * 0.8)), rot=(_deg(-20), _deg(15 * side), 0), r2=0.0, bevel=0)
        elif horns == "ram":
            for side in (1, -1):
                shapes.torus(f"{n}.horn", hr * 0.38, hr * 0.12, horn, self.neck,
                             at=hc + Vector((side * hr * 0.85, hr * 0.1, hr * 0.35)), rot=(0, _deg(90), 0), arc=300)
        elif horns == "unicorn":
            shapes.cylinder(f"{n}.horn", hr * 0.12, hr * 1.0, look.plastic("gold", 0.3, 0.6), self.neck,
                            at=hc + Vector((0, -hr * 0.6, hr * 0.7)), rot=(_deg(-35), 0, 0), r2=0.0, bevel=0)
        self.build_wings()
        self.build_fins()

    def build_wings(self):
        k, n = self.skel, self.name
        feathers = getattr(k, "feathers", False)
        mat = look.plastic(self.spec["color"] if feathers else self.spec.get("belly"), 0.6, 0.1)
        for side, bones in k.wings:
            for i, b in enumerate(bones):
                bone = self.rig.data.bones[b]
                a, z = bone.head_local, bone.tail_local
                w = self.size * (0.16 if i == 0 else 0.2)
                me = bpy.data.meshes.new(f"{n}.wing")
                me.from_pydata([tuple(a), tuple(z), tuple(z + Vector((side * w * 1.2, w * 0.3, -0.01))),
                                tuple(a + Vector((side * w, -w * 0.2, -0.01)))], [], [(0, 1, 2, 3)])
                ob = bpy.data.objects.new(f"{n}.wing", me)
                bpy.context.scene.collection.objects.link(ob)
                me.materials.append(mat)
                shapes.solidify(ob, 0.01 * self.size)
                self.attach(ob, b)
        self.wing_bones = [b for _, bones in k.wings for b in bones[:1]]

    def build_fins(self):
        k, n, S = self.skel, self.name, self.size
        if self.plan.locomotion != "swim":
            if self.plan.name == "bird" and k.tail:
                fan = shapes.ellipsoid(f"{n}.tailfeathers", 0.1 * S, 0.16 * S, 0.02 * S, self.spec["color"], None,
                                       at=k.at(k.tail[-1]) + Vector((0, 0.08 * S, 0.02 * S)), rot=(_deg(-20), 0, 0))
                self.attach(fan, k.tail[-1])
            return
        fin = look.plastic(self.spec["color"], 0.4, 0.3)
        tail = k.tail[-1]
        t = k.at(tail)
        me = bpy.data.meshes.new(f"{n}.tailfin")
        me.from_pydata([tuple(t), tuple(t + Vector((0, 0.18 * S, 0.14 * S))), tuple(t + Vector((0, 0.12 * S, 0))),
                        tuple(t + Vector((0, 0.18 * S, -0.14 * S)))], [], [(0, 1, 2), (0, 2, 3)])
        ob = bpy.data.objects.new(f"{n}.tailfin", me)
        bpy.context.scene.collection.objects.link(ob)
        me.materials.append(fin)
        shapes.solidify(ob, 0.012 * S)
        self.attach(ob, tail)
        top = k.at("body1") + Vector((0, 0.06 * S, k.joints["body1"].radius * 0.8))
        dorsal = shapes.cylinder(f"{n}.dorsal", 0.09 * S, 0.12 * S, fin, None, at=top, r2=0.0, bevel=0)
        dorsal.scale = (0.15, 1, 1)
        self.attach(dorsal, "body1")
        for side in (1, -1):
            f = shapes.ellipsoid(f"{n}.fin", 0.07 * S, 0.035 * S, 0.012 * S, fin, None,
                                 at=k.at("body1") + Vector((side * 0.11 * S, 0.02 * S, -0.04 * S)), rot=(0, _deg(-30 * side), 0))
            self.attach(f, "body1")

    # ------------------------------------------------------------------ queries
    def head_point(self, t):
        loc = value_at(self.root, "location", t)
        hz = value_at(self.hips, "location", t)[2]
        h = self.heading(t)
        r = self.head_rest
        x = r.x * math.cos(h) - r.y * math.sin(h)
        y = r.x * math.sin(h) + r.y * math.cos(h)
        return Vector((loc[0] + x, loc[1] + y, loc[2] + hz + r.z))

    def height(self):
        return self.head_rest.z + self.hr

    def length(self):
        ys = [j.at.y for j in self.skel.joints.values()]
        return max(ys) - min(ys) + 2 * self.hr

    def home_at(self, leg, pos, heading, z=0.0):
        """Where a leg's foot rests when the creature stands at pos (x, y) facing heading."""
        hx, hy, hz = self.foot_home[leg]
        c, s = math.cos(heading), math.sin(heading)
        return Vector((pos.x + hx * c - hy * s, pos.y + hx * s + hy * c, hz + z))

    # ------------------------------------------------------------------ feet
    def plant_feet(self, t, ease="cut", where=None):
        """Put every foot at its rest spot under the creature as it stands at time t (or at
        `where` = (x, y, z, heading) if given, e.g. where it is about to land)."""
        if where is None:
            loc = value_at(self.root, "location", t)
            where = (loc[0], loc[1], loc[2], self.heading(t))
        x, y, z, h = where
        for leg, target in self.feet.items():
            key(target, "location", t, tuple(self.home_at(leg, Vector((x, y)), h, z)), ease)

    def step_feet_home(self, t0, t1):
        """Little steps so the feet end under the body at t1 (after turning on the spot)."""
        if not self.feet:
            return
        loc = value_at(self.root, "location", t1)
        p, h = Vector((loc[0], loc[1])), value_at(self.root, "rotation_euler", t1)[2]
        phases, _ = self.plan.gait(self, False)
        span = max(0.2, t1 - t0)
        for leg, target in self.feet.items():
            start = t0 + span * 0.6 * phases.get(leg, 0)
            land = min(t1 + 0.1, start + min(0.3, span * 0.6))
            cur = Vector(hold(target, "location", start))
            new = self.home_at(leg, p, h, loc[2])
            if (new - cur).length < 0.01:
                continue
            mid = (cur + new) / 2 + Vector((0, 0, 0.06 * self.leg_len + 0.02))
            key(target, "location", (start + land) / 2, tuple(mid))
            key(target, "location", land, tuple(new))

    def gait_timing(self, speed, run):
        self.speed_now = speed
        return self.plan.stride(self, speed, run)

    def animate_steps(self, path, n_steps, step_t, run):
        loco = self.plan.locomotion
        ws, end = path.start, path.end
        T = 2 * step_t
        if loco in ("swim", "slither"):
            amp = 18 if loco == "slither" else 12
            self.wave(self.skel.spine, ws, end, period=T * 1.2, amp_deg=amp, axis="Z", phase_step=1.1)
            return
        if loco == "hop":
            base = 0.0
            hold(self.hips, "location", ws)
            hold(self.body, "scale", ws)
            for i in range(n_steps):
                t = ws + i * step_t
                key(self.hips, "location", t, (0, 0, base))
                key(self.body, "scale", t, (1.12, 1.12, 0.82))
                key(self.hips, "location", t + step_t * 0.5, (0, 0, base + 0.18 * self.size), "ease_out")
                key(self.body, "scale", t + step_t * 0.3, (0.92, 0.92, 1.15))
            key(self.hips, "location", end, (0, 0, base))
            key(self.body, "scale", end, (1.1, 1.1, 0.85))
            key(self.body, "scale", end + 0.15, (1, 1, 1))
            return
        phases, duty = self.plan.gait(self, run)
        swing = (1 - duty) * T
        lift = (0.12 if run else 0.08) * self.leg_len + 0.01
        for leg, target in self.feet.items():
            phi = phases.get(leg, 0.0)
            ts = ws + phi * T
            hold(target, "location", ws)
            last = None
            while ts < end - 0.04:
                tl = min(ts + swing, end)
                aim = min(tl + duty * T * 0.5, end)
                pos, hdg = path.at(aim)
                land = self.home_at(leg, pos, hdg)
                cur = Vector(value_at(target, "location", ts))
                key(target, "location", ts, tuple(cur))
                mid = (cur + land) / 2 + Vector((0, 0, lift))
                key(target, "location", (ts + tl) / 2, tuple(mid))
                key(target, "location", tl, tuple(land))
                last = tl
                ts += T
            pos, hdg = path.at(end)
            final = self.home_at(leg, pos, hdg)
            cur = Vector(value_at(target, "location", end + 0.01))
            if (final - cur).length > 0.02:
                t0 = max(end, (last or end)) + 0.02 + phi * 0.15
                key(target, "location", t0, tuple(cur))
                key(target, "location", t0 + 0.12, tuple((cur + final) / 2 + Vector((0, 0, lift))))
                key(target, "location", t0 + 0.24, tuple(final))
        # a little bounce in the body, and the tail sways
        hold(self.hips, "location", ws)
        bob = 0.015 * self.leg_len * (2 if run else 1)
        t = ws
        while t < end:
            key(self.hips, "location", t, (0, 0, -bob))
            key(self.hips, "location", t + step_t / 2, (0, 0, bob * 0.5))
            t += step_t
        key(self.hips, "location", end, (0, 0, 0))
        if self.skel.tail:
            self.wave(self.skel.tail, ws, end, period=T, amp_deg=10, axis="Z")

    # ------------------------------------------------------------------ verbs that need feet
    def place(self, where, facing=None, at=None):
        super().place(where, facing=facing, at=at)
        self.plant_feet(0.0 if at is None else at)
        return self

    def enter(self, where, facing=None, at=None):
        super().enter(where, facing=facing, at=at)
        self.plant_feet(self.busy - 0.1)
        return self

    def turn_to(self, target, at=None, wait=True):
        t = self._start(at)
        super().turn_to(target, at=t, wait=wait)
        self.step_feet_home(t, self.busy)
        return self

    def sit(self, on, at=None, wait=True, already=False):
        """Bipeds sit on the seat; other bodies lie down there."""
        if "arms" in self.capabilities or not self.feet:
            return super().sit(on, at=at, wait=wait, already=already)
        seat = self.scene.set.seat(on) if self.scene.set else None
        if seat is None:
            raise ValueError(f"{self.name}: no seat called {on!r}")
        if already:
            t = 0.0 if at is None else at
            self.place(seat.front, facing=math.degrees(seat.facing), at=t)
        else:
            self.walk_to(seat.front, at=at)
            self.turn_to(math.degrees(seat.facing))
        return self.lie_down(wait=wait)

    def lie_down(self, at=None, wait=True):
        t = self._start(at)
        hold(self.hips, "location", t)
        key(self.hips, "location", t + 0.6, (0, 0, -self.leg_len * 0.45))
        self.sitting = "lying"
        return self._end(t + 0.6, wait)

    def stand(self, at=None, wait=True):
        if self.sitting == "lying":
            t = self._start(at)
            hold(self.hips, "location", t)
            key(self.hips, "location", t + 0.5, (0, 0, 0))
            self.sitting = None
            return self._end(t + 0.5, wait)
        return super().stand(at=at, wait=wait)

    def fly_to(self, where, height=1.5, land=True, at=None, wait=True):
        """Take off, fly to a spot at `height` metres, and land (needs wings)."""
        if "fly" not in self.capabilities:
            raise ValueError(f"{self.name} can't fly (no wings)")
        t = self._start(at)
        p0 = self.position(t)
        p1 = self.scene._resolve(where, t, me=self, approach=True)
        d = (p1 - p0).length
        dur = max(1.2, d / (1.6 * max(0.5, self.size)))
        h = heading_to(p1.x - p0.x, p1.y - p0.y)
        hold(self.root, "rotation_euler", t)
        self._key_heading(t + 0.3, h)
        loc0 = value_at(self.root, "location", t)
        hold(self.root, "location", t)
        up = t + 0.6
        key(self.root, "location", up, (p0.x, p0.y, height), "ease_out")
        key(self.root, "location", up + dur, (p1.x, p1.y, height if land else height), "smooth")
        end = up + dur
        if land:
            key(self.root, "location", end + 0.6, (p1.x, p1.y, loc0[2]), "ease_in")
            end += 0.6
        for leg in self.skel.legs:   # legs hang while flying
            hold(leg.ik, "influence", t + 0.2)
            key(leg.ik, "influence", t + 0.5, 0.0)
            if land:
                key(leg.ik, "influence", end - 0.15, 0.0)
                key(leg.ik, "influence", end, 1.0)
        if land:
            self.plant_feet(end - 0.15, where=(p1.x, p1.y, loc0[2], h))
        self.flap(t + 0.1, end)
        self.scene._event("move", self, t, end)
        return self._end(end + 0.1, wait)

    def flap(self, t0, t1, beat=0.35, amp=55):
        for side, bones in self.skel.wings:
            root = bones[0]
            hold(self.rig.pose.bones[root], "rotation_quaternion", t0)
            t = t0
            i = 0
            spread = Quaternion((0, 0, 1), _deg(-70 * side))
            while t < t1:
                ang = _deg(amp if i % 2 == 0 else -amp * 0.6) * side
                self.turn_bone(root, t, Quaternion((0, 1, 0), -ang) @ spread)
                t += beat / 2
                i += 1
            self.turn_bone(root, t1 + 0.2, Quaternion())

    def prepare(self, length):
        """Feet that were never planted stand under the creature."""
        for target in self.feet.values():
            if not (target.animation_data and target.animation_data.action):
                self.plant_feet(0.0)
                break
