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
        self.sway = []       # (object, how much) that move in the wind: trees, plants
        self.glows = []      # (material, kind, strength): windows that show the sky, lit windows at night
        self.windows = []    # (x, y, z) of windows in rooms: daylight comes in through them
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
        """Add lights for this set. Return True if you did, False for dreamreel's default lighting.
        `scene.environment.light` says what the light is like (time of day and weather)."""
        return False

    def adjust_light(self, light):
        """Change the light before it is built (the moon has a black sky)."""

    def animate(self, length):
        """Move things in the set once the scene's length is known (waves)."""

    def apply_light(self, light):
        """Match the set to the time of day: windows show the sky, town windows light up at night."""
        rng = random.Random(self.name)
        for mat, kind, strength in self.glows:
            bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
            if bsdf is None:
                continue
            if kind == "sky":
                color = (*look.rgb(light.horizon), 1)
                bsdf.inputs["Base Color"].default_value = color
                bsdf.inputs["Emission Color"].default_value = color
                bsdf.inputs["Emission Strength"].default_value = strength * max(0.25, light.sky_strength)
                mat.diffuse_color = color
            elif kind == "lit":
                on = rng.random() < light.lit_windows
                bsdf.inputs["Emission Strength"].default_value = strength if on else 0.0
                if on:
                    mat.diffuse_color = (*look.rgb("#ffd890"), 1)

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

    def tree(self, name, at, scale, rng, kind="tree", **kw):
        """A tree (or any scenery: pine, palm, cactus, rock, bush...) at (x, y)."""
        return plugins.get("scenery", kind)().place(self, name, Vector(at[:2]), scale, rng, **kw)

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




# A furnished room: what goes where. Your own props come first; these fill the places still free.
FURNISH = {
    "living_room": [{"type": "window", "place": "back-left"}, {"type": "sofa", "place": "back"},
                    {"type": "painting", "place": "back"}, {"type": "lamp", "place": "back-right"},
                    {"type": "rug", "place": "center"}, {"type": "tv", "place": "left", "facing": "right"},
                    {"type": "plant", "place": "right"}, {"type": "door", "place": "back-right"}],
    "kitchen": [{"type": "door", "place": "back-left"}, {"type": "fridge", "place": "back"},
                {"type": "counter", "place": "back-right", "items": ["cup", "plate"]},
                {"type": "window", "place": "back-right"}, {"type": "clock", "place": "back"},
                {"type": "table", "place": "center", "chairs": 2, "items": ["plate"]}, {"type": "plant", "place": "left"}],
    "bedroom": [{"type": "bed", "place": "back"}, {"type": "wardrobe", "place": "back-left"},
                {"type": "window", "place": "back-right"}, {"type": "lamp", "place": "right"},
                {"type": "rug", "place": "front"}, {"type": "desk", "place": "left", "items": ["book"]},
                {"type": "painting", "place": "back", "height": 1.75}],
    "office": [{"type": "window", "place": "back-left"}, {"type": "bookshelf", "place": "back"},
               {"type": "plant", "place": "back-right"}, {"type": "desk", "place": "left", "items": ["laptop"]},
               {"type": "desk", "place": "right", "items": ["laptop", "cup"]}, {"type": "clock", "place": "back"},
               {"type": "door", "place": "back-right"}],
    "classroom": [{"type": "blackboard", "place": "back"}, {"type": "desk", "place": "back-left", "facing": "camera",
                                                               "items": ["book"]},
                  {"type": "desk", "place": "left", "items": ["book"]}, {"type": "desk", "place": "center"},
                  {"type": "desk", "place": "right", "items": ["book"]}, {"type": "bookshelf", "place": "back-right"},
                  {"type": "clock", "place": "back-right"}, {"type": "door", "place": "back-left"}],
    "cafe": [{"type": "counter", "place": "back", "items": ["cup", "cup", "plate"]}, {"type": "window", "place": "back-left"},
             {"type": "plant", "place": "back-right"}, {"type": "table", "place": "left", "width": 0.9, "chairs": 2,
                                                          "items": ["cup"]},
             {"type": "table", "place": "right", "width": 0.9, "chairs": 2, "items": ["cup"]},
             {"type": "painting", "place": "back-right"}, {"type": "lamp", "place": "front-left"}],
}


def furnish(kind, own):
    """The props of a furnished room: yours, plus the room type's furniture wherever a place is free."""
    from . import plugins as _plugins
    own = list(own or [])
    taken_floor = {p.get("place", _plugins.get("prop", p["type"]).default_place) for p in own
                   if not getattr(_plugins.get("prop", p["type"]), "wall", False)}
    have = {p["type"] for p in own}
    out = list(own)
    for p in FURNISH[kind]:
        cls = _plugins.get("prop", p["type"])
        wall = getattr(cls, "wall", False)
        if p["type"] in have and p["type"] in ("door", "window", "sofa", "bed", "counter", "fridge", "tv",
                                                "blackboard", "clock", "bookshelf", "wardrobe"):
            continue
        if not wall and p["place"] in taken_floor:
            continue
        if not wall:
            taken_floor.add(p["place"])
        out.append(dict(p))
    return out


class Room(Set):
    """A room with no front wall (the camera side), like a sitcom set."""
    description = "Indoors: floor, three walls, furniture (or furnished for you)"
    params = [
        Param("furnish", "choice", default=None, choices=tuple(FURNISH), label="Furnish as"),
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
        if spec.get("furnish"):
            spec = dict(spec, props=furnish(spec["furnish"], spec.get("props")))
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
    """Outdoors: a biome (meadow, forest, beach, desert, snow, mountains, moon...) with its terrain and
    scenery laid out by rules round a flat acting area. See nature.py."""
    description = "Outdoors: any landscape, from a meadow to the moon"
    outdoor = True
    size = (6.5 * 1.4, 4.4 * 1.6)
    params = [
        Param("biome", "biome", default="meadow", label="Landscape"),
        Param("terrain", "choice", default=None, choices=("flat", "rolling", "hills", "mountains", "dunes", "craters"),
              label="Land"),
        Param("density", "number", default=None, min=0, max=3, step=0.1, label="How much scenery"),
        Param("ground", "color", label="Ground colour"),
        Param("path", "bool", default=True, label="Footpath"),
        Param("seed", "number", default=3, min=0, max=999, step=1, label="Shuffle"),
    ]

    def __init__(self, spec, name="set"):
        self.foam = []
        super().__init__(spec, name)

    def build_environment(self):
        from . import nature
        spec = self.spec
        W, D = self.width, self.depth
        self.biome = plugins.get("biome", spec.get("biome") or "meadow")()
        seed = int(spec.get("seed", 3))
        rng = random.Random(seed)
        style = spec.get("terrain")
        if style is None and "hills" in spec:          # older set files: hills = 0 meant flat
            style = "rolling" if spec["hills"] else "flat"
        self.terrain = nature.Terrain(style or self.biome.terrain, seed, W, D)
        ground = spec.get("ground") or self.biome.ground
        ground = FLOORS.get(ground, ground)
        far = self.biome.far if not spec.get("ground") else None
        self.terrain.extra = getattr(self.biome, "height", None)
        if self.terrain.extra is not None:
            base = self.terrain.height
            self.terrain.height = lambda x, y: base(x, y) + self.biome.height(x, y, self)
        self.terrain.build(ground, far, self.biome.snow_line)
        if spec.get("path", True) and self.biome.path:
            shapes.box("ground.path", W + 3.0, 0.7, 0.02, look.matte(self.biome.path, 0.8), at=(0, -0.2, -0.01),
                       bevel=0.01)
        self.biome.build_extra(self, rng)
        density = spec.get("density")
        if density is None:
            density = spec["trees"] / 6 if "trees" in spec else 1.0
        from . import nature as _n
        _n.scatter(self, self.biome, rng, float(density))

    def ground_height(self, x, y):
        return self.terrain.height(x, y)

    def adjust_light(self, light):
        self.biome.adjust_light(light)

    def animate(self, length):
        self.biome.animate(self, length)
