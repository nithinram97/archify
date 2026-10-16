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

from mathutils import Vector

from . import look, shapes

ZONES = {
    "back-left": (-1, 1), "back": (0, 1), "back-right": (1, 1),
    "left": (-1, 0), "center": (0, 0), "centre": (0, 0), "right": (1, 0),
    "front-left": (-1, -1), "front": (0, -1), "front-right": (1, -1),
}
SIZES = {"small": (5.0, 3.6), "medium": (6.5, 4.4), "large": (8.5, 5.6)}
FLOORS = {"wood": "wood", "tiles": "cream", "carpet": "beige", "concrete": "#9a9a9a", "grass": "grass",
          "sand": "#e3cf9e", "stone": "#a9a196"}


TABLE_ITEMS = ("cookie-jar", "cookie", "plate", "cup", "vase", "laptop", "book")


class Mark:
    def __init__(self, name, at, facing=None):
        self.name = name
        self.at = Vector(at)
        self.facing = facing  # radians, or None to keep the character's heading


class Seat:
    def __init__(self, name, at, facing, height, front):
        self.name, self.at, self.facing, self.height, self.front = name, Vector(at), facing, height, Vector(front)


class Set:
    """A place where scenes happen. Build one from a description dict (what sets/*.toml contains)."""

    def __init__(self, spec, name="set"):
        self.name = name
        self.kind = spec.get("kind", "room")
        size = spec.get("size", "medium")
        self.width, self.depth = SIZES[size] if isinstance(size, str) else size
        self.wall_h = spec.get("wall_height", 2.4)
        self.marks = {}
        self.seats = {}
        self.obstacles = []  # (cx, cy, half_w, half_d) footprints characters walk round
        self.props = {}
        self.spec = spec
        self.lights = []
        if self.kind == "room":
            self._room(spec)
        elif self.kind == "outdoor":
            self._outdoor(spec)
        else:
            raise ValueError(f"set {name}: kind must be 'room' or 'outdoor', not {self.kind!r}")
        for p in spec.get("props", []):
            self.add_prop(p)
        for mname, place in spec.get("marks", {}).items():
            self.marks[mname] = Mark(mname, self.zone(place))
        # default marks every set has
        for z in ZONES:
            if z != "centre":
                self.marks.setdefault(z, Mark(z, self.zone(z)))

    # ------------------------------------------------------------------ places
    def zone(self, place, inset=0.9):
        """A named place -> (x, y) on the floor."""
        if isinstance(place, (list, tuple)):
            return Vector(place[:2])
        if place not in ZONES:
            raise ValueError(f"set {self.name}: unknown place {place!r}; use one of {list(ZONES)} or a mark name")
        zx, zy = ZONES[place]
        return Vector((zx * (self.width / 2 - inset) * 0.72, zy * (self.depth / 2 - inset) * 0.8))

    def _room(self, spec):
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
        if "wallpaper" in spec:  # simple stripes
            for i in range(int(W / 0.4)):
                shapes.box("stripe", 0.14, 0.005, Hh - 0.1, look.matte(spec["wallpaper"]),
                           at=(-W / 2 + 0.2 + i * 0.4, D / 2 - 0.003, 0.1), bevel=0)

    def _outdoor(self, spec):
        W, D = self.width * 1.4, self.depth * 1.6
        self.width, self.depth = W, D
        ground = spec.get("ground", "grass")
        shapes.cylinder("ground", max(W, D) * 1.6, 0.1, look.matte(FLOORS.get(ground, ground), 0.9), at=(0, D * 0.3, -0.1),
                        bevel=0, segments=64)
        if spec.get("path", True):
            shapes.box("path", W * 3, 0.7, 0.02, look.matte(FLOORS["stone"], 0.8), at=(0, -0.2, -0.01), bevel=0.01)
        self.walls = []
        import random
        rng = random.Random(spec.get("seed", 3))
        for i in range(spec.get("trees", 6)):
            x = rng.uniform(-W * 0.8, W * 0.8)
            y = rng.uniform(D * 0.45, D * 1.2)
            self._tree(f"tree{i}", (x, y), rng.uniform(0.8, 1.4), rng)
        for i in range(spec.get("hills", 3)):
            shapes.ellipsoid("hill", rng.uniform(6, 10), rng.uniform(3, 5), rng.uniform(1.5, 3),
                             look.matte(rng.choice(["#86c06a", "#74b05c", "#93c977"]), 0.9),
                             at=(rng.uniform(-W, W), D * 1.6 + rng.uniform(0, 3), -0.3))

    def _tree(self, name, at, scale, rng):
        x, y = at
        shapes.cylinder(name, 0.09 * scale, 1.0 * scale, look.matte("darkwood"), at=(x, y, 0), r2=0.06 * scale)
        for j in range(3):
            shapes.sphere(name, (0.55 - 0.1 * j) * scale, look.plastic(rng.choice(["leaf", "#5aa84f", "#3f8a44"]), 0.6, 0.1),
                          at=(x + rng.uniform(-0.15, 0.15) * scale, y, (1.15 + 0.38 * j) * scale))

    # ------------------------------------------------------------------ props
    def _place(self, p, w, d, default):
        place = p.get("place", default)
        pos = self.zone(place)
        if self.kind == "room":
            zx, zy = ZONES.get(place, (0, 0)) if isinstance(place, str) else (0, 0)
            if p.get("against", zy == 1) and zy == 1:
                pos.y = self.depth / 2 - d / 2 - 0.05
        return pos

    def add_prop(self, p):
        kind = p["type"]
        name = p.get("name", kind)
        while name in self.props:
            name = f"{kind}-{len([k for k in self.props if k.startswith(kind)]) + 1}"
        builder = getattr(self, "_prop_" + kind.replace("-", "_"), None)
        if builder is None:
            raise ValueError(f"set {self.name}: unknown prop type {kind!r}; use one of {PROP_TYPES}")
        self.props[name] = builder(name, p)

    def _block(self, pos, w, d):
        self.obstacles.append((pos.x, pos.y, w / 2, d / 2))

    def _prop_table(self, name, p):
        w, d, h = p.get("width", 1.4), p.get("depth", 0.8), 0.48
        pos = self._place(p, w, d, "center")
        c = p.get("color", "wood")
        top = shapes.box(name, w, d, 0.05, c, at=(pos.x, pos.y, h - 0.05), bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                shapes.box(name + ".leg", 0.06, 0.06, h - 0.05, c, at=(pos.x + sx * (w / 2 - 0.08), pos.y + sy * (d / 2 - 0.08), 0), bevel=0.01)
        self._block(pos, w, d)
        self.marks[name] = Mark(name, (pos.x, pos.y - d / 2 - 0.35), facing=math.pi)
        for side, label in ((-1, "left"), (1, "right")):
            self.marks[f"{name}-{label}"] = Mark(f"{name}-{label}", (pos.x + side * (w / 2 + 0.35), pos.y),
                                                 facing=math.pi / 2 * (1 if side < 0 else -1))
        for i in range(p.get("chairs", 0)):
            side = (-1, 1)[i % 2]
            self.add_prop({"type": "chair", "at": (pos.x + side * (w / 2 + 0.3), pos.y), "face": (-side, 0), "tucked": True,
                           "color": p.get("chair_color", c)})
        for item in p.get("items", []):
            self._table_item(item, pos, h, w)
        return top

    def _table_item(self, item, pos, h, w):
        import random
        rng = random.Random(item)
        x = pos.x + rng.uniform(-w / 3, w / 3)
        if item == "cookie-jar":
            shapes.cylinder("cookie-jar", 0.09, 0.16, look.glass(), at=(x, pos.y, h))
            shapes.cylinder("cookie-jar.lid", 0.095, 0.03, "red", at=(x, pos.y, h + 0.16))
            for i in range(3):
                shapes.cylinder("cookie", 0.05, 0.015, "#c98b4f", at=(x, pos.y, h + 0.01 + i * 0.02))
        elif item == "cookie":
            shapes.cylinder("cookie", 0.05, 0.015, "#c98b4f", at=(x, pos.y - 0.1, h))
        elif item == "plate":
            shapes.cylinder("plate", 0.12, 0.015, "white", at=(x, pos.y, h))
        elif item == "cup":
            shapes.cylinder("cup", 0.045, 0.09, rng.choice(["red", "teal", "yellow"]), at=(x, pos.y, h))
        elif item == "vase":
            shapes.cylinder("vase", 0.06, 0.2, "teal", at=(x, pos.y, h), r2=0.04)
            for i in range(3):
                shapes.sphere("flower", 0.045, rng.choice(["pink", "yellow", "red"]),
                              at=(x + rng.uniform(-0.05, 0.05), pos.y + rng.uniform(-0.05, 0.05), h + 0.26 + 0.04 * i))
        elif item == "laptop":
            shapes.box("laptop", 0.32, 0.22, 0.015, "#c9ccd1", at=(x, pos.y, h))
            shapes.box("laptop", 0.32, 0.015, 0.2, "#c9ccd1", at=(x, pos.y + 0.11, h), rot=(math.radians(-15), 0, 0))
        elif item == "book":
            shapes.box("book", 0.2, 0.14, 0.04, rng.choice(["red", "blue", "green"]), at=(x, pos.y, h), bevel=0.005)
        else:
            raise ValueError(f"unknown table item {item!r}; use one of {TABLE_ITEMS}")

    def _seat_facing(self, p, pos):
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

    def _prop_chair(self, name, p):
        pos = Vector(p["at"]) if "at" in p else self._place(p, 0.45, 0.45, "center")
        f = self._seat_facing(p, pos)
        c = p.get("color", "wood")
        seat_h = 0.3
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        shapes.box(name + ".seat", 0.42, 0.4, 0.04, c, root, at=(0, 0, seat_h - 0.04))
        shapes.box(name + ".back", 0.42, 0.04, 0.45, c, root, at=(0, 0.2, seat_h - 0.02))
        for sx in (-1, 1):
            for sy in (-1, 1):
                shapes.box(name + ".leg", 0.04, 0.04, seat_h - 0.04, c, root, at=(sx * 0.17, sy * 0.16, 0), bevel=0.008)
        fwd = Vector((math.sin(f), -math.cos(f)))
        front = pos + fwd * 0.6
        if p.get("tucked"):  # pushed under a table: get in from the side nearest the camera
            perp = Vector((-fwd.y, fwd.x))
            front = pos + (perp if perp.y < 0 else -perp) * 0.6
        self.seats[name] = Seat(name, pos, f, seat_h, front)
        self.marks.setdefault(name, Mark(name, front, facing=f))
        self._block(pos, 0.4, 0.4)
        return root

    def _prop_sofa(self, name, p):
        w = p.get("width", 1.8)
        pos = self._place(p, w, 0.8, "back")
        f = self._seat_facing(p, pos)
        c = p.get("color", "teal")
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        shapes.box(name, w, 0.8, 0.28, c, root, bevel=0.06)
        shapes.box(name, w, 0.22, 0.7, c, root, at=(0, 0.3, 0), bevel=0.08)
        for s in (-1, 1):
            shapes.box(name, 0.2, 0.8, 0.45, c, root, at=(s * (w / 2 - 0.1), 0, 0), bevel=0.08)
            shapes.box(name + ".cushion", w / 2 - 0.22, 0.6, 0.08, c, root, at=(s * (w / 4 - 0.05), -0.05, 0.28), bevel=0.04)
        fwd = Vector((math.sin(f), -math.cos(f)))
        side = Vector((math.cos(f), math.sin(f)))
        for i, s in enumerate((-1, 1)):
            sname = name if i == 0 else f"{name}-2"
            at = pos + side * s * w * 0.22 - fwd * 0.0
            self.seats[sname] = Seat(sname, at, f, 0.32, at + fwd * 0.65)
        self.marks.setdefault(name, Mark(name, pos + fwd * 0.75, facing=f))
        self._block(pos, w, 0.8)
        return root

    def _prop_door(self, name, p):
        pos = self._place(p, 1.0, 0.1, "back-left")
        c = p.get("color", "#8a5a3c")
        if self.kind == "room":
            pos.y = self.depth / 2
        shapes.box(name + ".frame", 1.0, 0.1, 1.75, look.matte("white", 0.5), at=(pos.x, pos.y - 0.02, 0), bevel=0.01)
        shapes.box(name, 0.86, 0.1, 1.68, c, at=(pos.x, pos.y - 0.05, 0), bevel=0.015)
        shapes.sphere(name + ".knob", 0.035, "#e2b53e", at=(pos.x + 0.32, pos.y - 0.12, 0.85))
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.6), facing=0.0)
        return None

    def _prop_window(self, name, p):
        pos = self._place(p, 1.2, 0.1, "back-right")
        if self.kind == "room":
            pos.y = self.depth / 2
        sky = look.plastic(p.get("view", "sky"), 0.9, 0.0, emission=1.2)
        shapes.box(name + ".view", 1.2, 0.05, 0.9, sky, at=(pos.x, pos.y - 0.02, 0.8), bevel=0)
        frame = look.matte("white", 0.5)
        for dz in (0.8, 1.25, 1.7):
            shapes.box(name + ".frame", 1.3, 0.08, 0.06, frame, at=(pos.x, pos.y - 0.04, dz - 0.03), bevel=0.01)
        for dx in (-0.62, 0, 0.62):
            shapes.box(name + ".frame", 0.06, 0.08, 0.96, frame, at=(pos.x + dx, pos.y - 0.04, 0.77), bevel=0.01)
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None

    def _prop_counter(self, name, p):
        w = p.get("width", 2.2)
        pos = self._place(p, w, 0.6, "back-right")
        c = p.get("color", "white")
        shapes.box(name, w, 0.6, 0.55, c, at=(pos.x, pos.y, 0), bevel=0.02)
        shapes.box(name + ".top", w + 0.05, 0.65, 0.05, p.get("top", "charcoal"), at=(pos.x, pos.y, 0.55), bevel=0.01)
        for i in range(int(w / 0.55)):
            shapes.sphere(name + ".knob", 0.02, "#e2b53e", at=(pos.x - w / 2 + 0.28 + i * 0.55, pos.y - 0.31, 0.42))
        for item in p.get("items", []):
            self._table_item(item, pos, 0.6, w)
        self._block(pos, w, 0.6)
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None

    def _prop_fridge(self, name, p):
        pos = self._place(p, 0.7, 0.65, "back-right")
        c = p.get("color", "#d8eef0")
        shapes.box(name, 0.7, 0.65, 1.55, c, at=(pos.x, pos.y, 0), bevel=0.06)
        shapes.box(name + ".line", 0.7, 0.01, 0.015, "#9fb7ba", at=(pos.x, pos.y - 0.33, 1.0), bevel=0)
        for z in (0.6, 1.2):
            shapes.box(name + ".handle", 0.03, 0.04, 0.22, "#9fb7ba", at=(pos.x + 0.25, pos.y - 0.35, z), bevel=0.01)
        self._block(pos, 0.7, 0.65)
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.75), facing=math.pi)
        return None

    def _prop_bookshelf(self, name, p):
        w = p.get("width", 1.2)
        pos = self._place(p, w, 0.35, "back")
        c = p.get("color", "darkwood")
        shapes.box(name, w, 0.35, 1.6, c, at=(pos.x, pos.y, 0), bevel=0.01)
        import random
        rng = random.Random(name)
        for shelf in range(4):
            z = 0.12 + shelf * 0.38
            shapes.box(name + ".back", w - 0.08, 0.3, 0.33, look.matte("#3d2a1c"), at=(pos.x, pos.y + 0.03, z), bevel=0)
            x = pos.x - w / 2 + 0.08
            while x < pos.x + w / 2 - 0.12:
                bw = rng.uniform(0.04, 0.08)
                bh = rng.uniform(0.22, 0.3)
                shapes.box(name + ".book", bw, 0.24, bh, rng.choice(["red", "blue", "green", "yellow", "cream", "teal"]),
                           at=(x + bw / 2, pos.y - 0.02, z), bevel=0.004)
                x += bw + 0.008
        self._block(pos, w, 0.35)
        return None

    def _prop_plant(self, name, p):
        pos = self._place(p, 0.4, 0.4, "back-right")
        shapes.cylinder(name + ".pot", 0.16, 0.28, p.get("color", "brick"), at=(pos.x, pos.y, 0), r2=0.2)
        import random
        rng = random.Random(name)
        for i in range(7):
            a = 2 * math.pi * i / 7
            shapes.ellipsoid(name + ".leaf", 0.07, 0.07, 0.28, look.plastic("leaf", 0.6, 0.1),
                             at=(pos.x + 0.08 * math.cos(a), pos.y + 0.08 * math.sin(a), 0.45 + rng.uniform(0, 0.15)),
                             rot=(0.5 * math.sin(a), -0.5 * math.cos(a), 0))
        self._block(pos, 0.4, 0.4)
        return None

    def _prop_lamp(self, name, p):
        pos = self._place(p, 0.4, 0.4, "back-left")
        shapes.cylinder(name, 0.15, 0.03, "charcoal", at=(pos.x, pos.y, 0))
        shapes.cylinder(name, 0.02, 1.35, "charcoal", at=(pos.x, pos.y, 0.03), bevel=0)
        shapes.cylinder(name + ".shade", 0.24, 0.3, look.plastic("cream", 0.7, 0.0, emission=0.6), at=(pos.x, pos.y, 1.3), r2=0.14)
        self.lights.append(((pos.x, pos.y, 1.35), "#ffd9a0", 60))
        self._block(pos, 0.3, 0.3)
        return None

    def _prop_rug(self, name, p):
        pos = self._place(p, 2, 1.4, "center")
        shapes.cylinder(name, p.get("width", 1.3), 0.012, look.matte(p.get("color", "#d9775b"), 0.9),
                        at=(pos.x, pos.y, 0.0), bevel=0.004, segments=48).scale.y = 0.6
        return None

    def _prop_bench(self, name, p):
        pos = self._place(p, 1.6, 0.5, "center")
        f = self._seat_facing(p, pos)
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        c = p.get("color", "wood")
        for i in range(3):
            shapes.box(name, 1.6, 0.12, 0.04, c, root, at=(0, -0.14 + i * 0.14, 0.3), bevel=0.01)
        shapes.box(name, 1.6, 0.04, 0.3, c, root, at=(0, 0.2, 0.36), bevel=0.01)
        for s in (-1, 1):
            shapes.box(name, 0.06, 0.45, 0.3, "charcoal", root, at=(s * 0.7, 0, 0), bevel=0.01)
        fwd = Vector((math.sin(f), -math.cos(f)))
        side = Vector((math.cos(f), math.sin(f)))
        for i, s in enumerate((-1, 1)):
            sname = name if i == 0 else f"{name}-2"
            at = pos + side * s * 0.4
            self.seats[sname] = Seat(sname, at, f, 0.32, at + fwd * 0.55)
        self.marks.setdefault(name, Mark(name, pos + fwd * 0.7, facing=f))
        self._block(pos, 1.6, 0.5)
        return root

    def _prop_tree(self, name, p):
        import random
        pos = self._place(p, 1, 1, "back-left")
        self._tree(name, pos, p.get("scale", 1.0), random.Random(name))
        self._block(pos, 0.5, 0.5)
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None

    def _prop_streetlamp(self, name, p):
        pos = self._place(p, 0.3, 0.3, "back-right")
        shapes.cylinder(name, 0.05, 2.2, "charcoal", at=(pos.x, pos.y, 0), bevel=0)
        shapes.sphere(name + ".bulb", 0.14, look.plastic("#fff1c4", 0.5, 0.0, emission=4), at=(pos.x, pos.y, 2.3))
        self.lights.append(((pos.x, pos.y, 2.2), "#ffd9a0", 120))
        self._block(pos, 0.2, 0.2)
        return None

    def _prop_house(self, name, p):
        pos = self._place(p, 3, 3, "back")
        c = p.get("color", "cream")
        shapes.box(name, 3.0, 2.6, 2.2, c, at=(pos.x, pos.y + 1.2, 0), bevel=0.04)
        roof = shapes.cylinder(name + ".roof", 2.2, 3.4, p.get("roof", "brick"), at=(pos.x - 1.7, pos.y + 1.2, 2.2),
                               rot=(0, math.radians(90), 0), segments=3, bevel=0.02)
        roof.scale = (0.75, 1.05, 1)
        roof.rotation_euler = (math.radians(90), 0, math.radians(90))
        roof.location = (pos.x - 1.7, pos.y + 1.2, 2.55)
        shapes.box(name + ".door", 0.7, 0.05, 1.5, "#8a5a3c", at=(pos.x, pos.y - 0.1, 0), bevel=0.01)
        for s in (-1, 1):
            shapes.box(name + ".window", 0.6, 0.05, 0.55, look.plastic("sky", 0.2, 0.3, emission=0.6),
                       at=(pos.x + s * 0.95, pos.y - 0.1, 1.0), bevel=0.01)
        self._block(Vector((pos.x, pos.y + 1.2)), 3.0, 2.6)
        self.marks[name] = Mark(name, (pos.x, pos.y - 0.6), facing=0.0)
        return None

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


PROP_TYPES = sorted(n[len("_prop_"):].replace("_", "-") for n in dir(Set) if n.startswith("_prop_"))
