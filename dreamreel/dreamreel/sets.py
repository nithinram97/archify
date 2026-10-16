"""Sets: rooms and outdoor places built from a short description, with named marks.

You never type coordinates. Furniture goes in named places on a 3 x 3 grid:

    back-left    back      back-right          (back wall)
    left         center    right
    front-left   front     front-right         (towards the camera)

and every prop creates marks that characters can walk to, sit on or look at: a "table" prop makes
the mark "table" (standing in front of it); a "door" makes "door"; chairs make seats "chair",
"chair-2", ... Add your own marks by place name too.

The camera side is the front (-Y). Rooms have no front wall, like a theatre or sitcom set.
"""
import math
import random

import bpy
from mathutils import Vector

from . import look, plugins, shapes
from .plugins import Param, Plugin

ZONES = {
    "back-left": (-1, 1), "back": (0, 1), "back-right": (1, 1),
    "left": (-1, 0), "center": (0, 0), "centre": (0, 0), "right": (1, 0),
    "front-left": (-1, -1), "front": (0, -1), "front-right": (1, -1),
}
SIZES = {"small": (5.0, 3.6), "medium": (6.5, 4.4), "large": (8.5, 5.6)}
FLOORS = {"wood": "wood", "tiles": "cream", "carpet": "beige", "concrete": "#9a9a9a", "grass": "grass",
          "sand": "#e3cf9e", "stone": "#a9a196"}




class Mark:
    def __init__(self, name, at, facing=None):
        self.name = name
        self.at = Vector(at)
        self.facing = facing  # radians, or None to keep the character's heading


class Seat:
    def __init__(self, name, at, facing, height, front):
        self.name, self.at, self.facing, self.height, self.front = name, Vector(at), facing, height, Vector(front)


class Set(Plugin):
    """A place where scenes happen, built from a set file (sets/<name>.toml).

    Subclass it for a new kind of place (`kind = "spaceship"` in the set file):

        class Spaceship(dr.Set):
            params = [dr.Param("hull", "color", default="#c9ccd1")]
            size = (6.0, 4.0)                       # width, depth in metres
            def build_environment(self):
                ...                                 # floor, walls, windows; dr.shapes + dr.look
            def lighting(self, scene, night):       # optional: your own lights
                ...
    """
    kind = "set"
    abstract = True
    params = []
    size = (6.5, 4.4)
    outdoor = False

    @staticmethod
    def create(spec, name="set"):
        """Build the right kind of set for a spec (its `kind`, default "room")."""
        cls = plugins.get("set", spec.get("kind", "room"))
        return cls(spec, name)

    def __init__(self, spec, name="set"):
        self.name = name
        self.spec = dict(self.defaults(), **spec)
        self.kind = self.__class__.name
        self.width, self.depth = self.size
        self.marks = {}
        self.seats = {}
        self.obstacles = []  # (cx, cy, half_w, half_d) footprints characters walk round
        self.props = {}
        self.lights = []     # (location, colour, power) of practical lights (lamps)
        self.walls = []      # hidden in the top-down map
        self.focus = {}      # prop or item name -> its middle (for insert shots)
        self.build_environment()
        for p in self.spec.get("props", []):
            self.add_prop(p)
        for mname, place in self.spec.get("marks", {}).items():
            self.marks[mname] = Mark(mname, self.zone(place))
        for z in ZONES:     # every set has the nine places as marks
            if z != "centre":
                self.marks.setdefault(z, Mark(z, self.zone(z)))

    def build_environment(self):
        """Make the floor, walls, sky... (override in subclasses)."""

    def lighting(self, scene, night):
        """Add lights for this set. Return True if you did, False for dreamreel's default lighting."""
        return False

    # ------------------------------------------------------------------ places
    def zone(self, place, inset=0.9):
        """A named place -> (x, y) on the floor."""
        if isinstance(place, (list, tuple)):
            return Vector(place[:2])
        if place not in ZONES:
            raise ValueError(f"set {self.name}: unknown place {place!r}; use one of {list(ZONES)} or a mark name")
        zx, zy = ZONES[place]
        return Vector((zx * (self.width / 2 - inset) * 0.72, zy * (self.depth / 2 - inset) * 0.8))

    def spot_for(self, p, w, d, default):
        """Where a prop of footprint w x d goes, from its `place` (things on the back row stand
        against the back wall in rooms)."""
        place = p.get("place", default)
        pos = self.zone(place)
        if not self.outdoor:
            zx, zy = ZONES.get(place, (0, 0)) if isinstance(place, str) else (0, 0)
            if p.get("against", zy == 1) and zy == 1:
                pos.y = self.depth / 2 - d / 2 - 0.05
        return pos

    # ------------------------------------------------------------------ props
    def add_prop(self, p):
        kind = p["type"]
        name = p.get("name", kind)
        while name in self.props:
            name = f"{kind}-{len([k for k in self.props if k.startswith(kind)]) + 1}"
        prop = plugins.get("prop", kind)
        self.props[name] = prop
        before = set(bpy.data.objects.keys())
        prop().build(self, name, p)
        self._remember_focus(name, before)
        return name

    def _remember_focus(self, name, before):
        """The middle of whatever was just built, so cameras can frame it (insert shots)."""
        new = [o for o in bpy.data.objects if o.name not in before and o.type == "MESH"]
        if not new:
            return
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in new for c in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        self.focus.setdefault(name, (lo + hi) / 2)

    def block(self, pos, w, d):
        """Characters walk round a w x d footprint centred on pos."""
        self.obstacles.append((pos.x, pos.y, w / 2, d / 2))

    def add_mark(self, name, at, facing=None):
        """A named spot. facing: radians, a mark name, or "camera" / "back" / "left" / "right"."""
        if isinstance(facing, str):
            facing = self.seat_facing({"facing": facing}, Vector(at[:2]))
        self.marks[name] = Mark(name, at, facing)
        return self.marks[name]

    def add_seat(self, name, at, facing, height, front):
        """A place to sit at `at` (x, y), seat height `height`, got into from `front`."""
        self.seats[name] = Seat(name, at, facing, height, front)
        self.marks.setdefault(name, Mark(name, front, facing=facing))
        return self.seats[name]

    def place_item(self, item, pos, h, w):
        """Put a small Item (by name) on a surface of width w at height h centred on pos."""
        rng = random.Random(item)
        x = pos.x + rng.uniform(-w / 3, w / 3)
        before = set(bpy.data.objects.keys())
        plugins.get("item", item)().build(self, x, pos.y, h, rng)
        self._remember_focus(item, before)

    def seat_facing(self, p, pos):
        if "face" in p:
            fx, fy = p["face"]
            return math.atan2(fx, -fy)
        target = p.get("facing", "camera")
        if target == "camera":
            return 0.0
        if target in self.marks:
            q = self.marks[target].at
            return math.atan2(q.x - pos.x, -(q.y - pos.y))
        return {"left": -math.pi / 2, "right": math.pi / 2, "back": math.pi}.get(target, 0.0)

    def tree(self, name, at, scale, rng):
        x, y = at
        shapes.cylinder(name, 0.09 * scale, 1.0 * scale, look.matte("darkwood"), at=(x, y, 0), r2=0.06 * scale)
        for j in range(3):
            shapes.sphere(name, (0.55 - 0.1 * j) * scale, look.plastic(rng.choice(["leaf", "#5aa84f", "#3f8a44"]), 0.6, 0.1),
                          at=(x + rng.uniform(-0.15, 0.15) * scale, y, (1.15 + 0.38 * j) * scale))

    # ------------------------------------------------------------------ walking round things
    def _clear(self, a, b, pad=0.32):
        for cx, cy, hw, hd in self.obstacles:
            hw, hd = hw + pad, hd + pad
            # segment vs axis-aligned box (slab test)
            t0, t1 = 0.0, 1.0
            d = b - a
            ok = True
            for o, dd, lo, hi in ((a.x, d.x, cx - hw, cx + hw), (a.y, d.y, cy - hd, cy + hd)):
                if abs(dd) < 1e-9:
                    if o < lo or o > hi:
                        ok = False
                        break
                    continue
                u0, u1 = (lo - o) / dd, (hi - o) / dd
                if u0 > u1:
                    u0, u1 = u1, u0
                t0, t1 = max(t0, u0), min(t1, u1)
                if t0 > t1:
                    ok = False
                    break
            if ok and t1 - t0 > 1e-3 and not (t1 <= 1e-3 or t0 >= 1 - 1e-3):
                return False
        return True

    def route(self, a, b):
        """A walking path from a to b that goes round furniture (straight if nothing is in the way)."""
        a, b = Vector(a), Vector(b)
        if self._clear(a, b):
            return [a, b]
        corners = []
        for cx, cy, hw, hd in self.obstacles:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    corners.append(Vector((cx + sx * (hw + 0.45), cy + sy * (hd + 0.45))))
        best = None
        for c in corners:
            if self._clear(a, c) and self._clear(c, b):
                L = (c - a).length + (b - c).length
                if best is None or L < best[0]:
                    best = (L, [a, c, b])
        if best is None:
            for c1 in corners:
                for c2 in corners:
                    if self._clear(a, c1) and self._clear(c1, c2) and self._clear(c2, b):
                        L = (c1 - a).length + (c2 - c1).length + (b - c2).length
                        if best is None or L < best[0]:
                            best = (L, [a, c1, c2, b])
        return best[1] if best else [a, b]

    def seat(self, name):
        return self.seats.get(name)




class Room(Set):
    """A room with no front wall (the camera side), like a sitcom set."""
    description = "Indoors: floor, three walls, furniture"
    params = [
        Param("size", "choice", default="medium", choices=tuple(SIZES)),
        Param("walls", "color", default="cream"),
        Param("floor", "choice", default="wood", choices=tuple(FLOORS)),
        Param("trim", "color", default="white", label="Skirting"),
        Param("wallpaper", "color", label="Wallpaper stripes"),
    ]

    def __init__(self, spec, name="set"):
        size = spec.get("size", "medium")
        self.size = SIZES[size] if isinstance(size, str) else tuple(size)
        self.wall_h = spec.get("wall_height", 2.4)
        super().__init__(spec, name)

    def build_environment(self):
        spec = self.spec
        W, D, Hh = self.width, self.depth, self.wall_h
        wall = look.matte(spec.get("walls", "cream"))
        floor = spec.get("floor", "wood")
        shapes.box("floor", W + 0.4, D + 0.4, 0.1, look.matte(FLOORS.get(floor, floor), 0.6), at=(0, 0, -0.1), bevel=0)
        if floor == "wood":
            for i in range(int(W / 0.5) + 1):
                shapes.box("floor.board", 0.012, D, 0.003, look.matte("darkwood", 0.7), at=(-W / 2 + i * 0.5, 0, 0), bevel=0)
        back = shapes.box("wall.back", W + 0.2, 0.12, Hh, wall, at=(0, D / 2 + 0.06, 0), bevel=0)
        left = shapes.box("wall.left", 0.12, D + 0.2, Hh, wall, at=(-W / 2 - 0.06, 0, 0), bevel=0)
        right = shapes.box("wall.right", 0.12, D + 0.2, Hh, wall, at=(W / 2 + 0.06, 0, 0), bevel=0)
        trim = look.matte(spec.get("trim", "white"), 0.5)
        shapes.box("skirting", W, 0.03, 0.1, trim, at=(0, D / 2 - 0.015, 0), bevel=0.005)
        for s in (-1, 1):
            shapes.box("skirting", 0.03, D, 0.1, trim, at=(s * (W / 2 - 0.015), 0, 0), bevel=0.005)
        self.walls = [back, left, right]
        if spec.get("wallpaper"):
            for i in range(int(W / 0.4)):
                shapes.box("stripe", 0.14, 0.005, Hh - 0.1, look.matte(spec["wallpaper"]),
                           at=(-W / 2 + 0.2 + i * 0.4, D / 2 - 0.003, 0.1), bevel=0)


class Outdoor(Set):
    """Open ground with trees and hills."""
    description = "Outdoors: ground, trees, hills, sky"
    outdoor = True
    size = (6.5 * 1.4, 4.4 * 1.6)
    params = [
        Param("ground", "choice", default="grass", choices=tuple(FLOORS)),
        Param("trees", "number", default=6, min=0, max=30, step=1),
        Param("hills", "number", default=3, min=0, max=10, step=1),
        Param("path", "bool", default=True, label="Footpath"),
        Param("seed", "number", default=3, min=0, max=999, step=1, label="Shuffle"),
    ]

    def build_environment(self):
        spec = self.spec
        W, D = self.width, self.depth
        ground = spec.get("ground", "grass")
        shapes.cylinder("ground", max(W, D) * 1.6, 0.1, look.matte(FLOORS.get(ground, ground), 0.9), at=(0, D * 0.3, -0.1),
                        bevel=0, segments=64)
        if spec.get("path", True):
            shapes.box("path", W * 3, 0.7, 0.02, look.matte(FLOORS["stone"], 0.8), at=(0, -0.2, -0.01), bevel=0.01)
        rng = random.Random(spec.get("seed", 3))
        for i in range(int(spec.get("trees", 6))):
            x = rng.uniform(-W * 0.8, W * 0.8)
            y = rng.uniform(D * 0.45, D * 1.2)
            self.tree(f"tree{i}", (x, y), rng.uniform(0.8, 1.4), rng)
        for i in range(int(spec.get("hills", 3))):
            shapes.ellipsoid("hill", rng.uniform(6, 10), rng.uniform(3, 5), rng.uniform(1.5, 3),
                             look.matte(rng.choice(["#86c06a", "#74b05c", "#93c977"]), 0.9),
                             at=(rng.uniform(-W, W), D * 1.6 + rng.uniform(0, 3), -0.3))
