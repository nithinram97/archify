"""Nature: terrain, biomes and scenery, laid out by rules instead of by hand.

An outdoor set picks a biome; the biome decides the ground, the shape of the land and what grows
where. The acting area in the middle always stays flat and clear; the land rises and the scenery
thickens towards the distance, and nothing is put where the camera usually stands.

    # sets/canyon.toml
    kind = "outdoor"
    biome = "desert"        # meadow, forest, autumn, beach, desert, snow, mountains, moon
    terrain = "hills"       # flat, rolling, hills, mountains, dunes, craters (the biome chooses otherwise)
    density = 1.5           # how much scenery
    seed = 4                # a different arrangement

Trees, pines, bushes, rocks, flowers, grass and mushrooms are Quaternius's nature models when that
pack is downloaded (`dreamreel assets`), and dreamreel's own shapes otherwise.

Biomes and scenery are classes, so new ones are easy to add:

    class Crystal(dr.Scenery):
        description = "A glowing crystal"
        radius = 0.4
        def build(self, root, name, scale, rng):
            dr.shapes.cylinder(name, 0.2 * scale, 1.2 * scale, dr.look.plastic("#8fe3ff", emission=2),
                               root, r2=0.0, segments=6)

    class CrystalCave(dr.Biome):
        ground = "#3b3550"
        terrain = "hills"
        scatter = [("crystal", 1.0), ("rock", 1.0)]
"""
import math

import bmesh
import bpy
from mathutils import Vector, noise

from . import look, shapes
from .plugins import Plugin


# ---------------------------------------------------------------------- scenery
class Scenery(Plugin):
    """Something that grows or lies about outdoors. `build` makes it round `root` (an empty at its
    base), `radius` is how much room it needs, `blocks` whether people walk round it, `sway` how
    much it moves in the wind. `models` are Quaternius nature models (one is picked) used instead of
    `build` when the pack is downloaded, `height` (toy set, life-size set) how tall they stand."""
    kind = "scenery"
    abstract = True
    radius = 0.6
    blocks = True
    sway = 1.0
    models = ()
    height = (1.0, 1.0)

    def place(self, s, name, at, scale, rng, block=True, z=None):
        x, y = at.x, at.y
        z = s.ground_height(x, y) if z is None and hasattr(s, "ground_height") else (z or 0.0)
        root = shapes.empty(name, at=(x, y, z - 0.03))
        root.rotation_euler.z = rng.uniform(0, 2 * math.pi)
        model = None
        if self.models and getattr(s, "use_models", False):
            h = s.sized(*self.height) * scale * rng.uniform(0.85, 1.15)
            model = s.model(rng.choice(self.models), name, (None, None, h), parent=root, pack="nature")
        if model is None:
            self.build(root, name, scale, rng)
        if self.sway:
            s.sway.append((root, self.sway))
        if self.blocks and block:
            s.block(Vector((x, y)), self.radius * scale * 1.4, self.radius * scale * 1.4)
        return root

    def build(self, root, name, scale, rng):
        raise NotImplementedError


def _leafy(color, rough=0.6):
    return look.plastic(color, rough, 0.1)


class Tree(Scenery):
    description = "A round leafy tree"
    models = tuple(f"CommonTree_{i}" for i in range(1, 6))
    height = (2.6, 5.5)
    palette = ("leaf", "#5aa84f", "#3f8a44")
    trunk = "darkwood"

    def build(self, root, name, scale, rng):
        shapes.cylinder(name, 0.09 * scale, 1.0 * scale, look.matte(self.trunk), root, r2=0.06 * scale,
                        bevel=0, segments=10)
        for j in range(3):
            shapes.sphere(name, (0.55 - 0.1 * j) * scale, _leafy(rng.choice(self.palette)), root,
                          at=(rng.uniform(-0.15, 0.15) * scale, 0, (1.15 + 0.38 * j) * scale), segments=16)


class AutumnTree(Tree):
    description = "A tree in autumn colours"
    models = tuple(f"TwistedTree_{i}" for i in range(1, 6))
    height = (2.6, 5.5)
    palette = ("#e08a2e", "#c9532b", "#e8b33c", "#b5482a")


class Pine(Scenery):
    description = "A pine tree"
    models = tuple(f"Pine_{i}" for i in range(1, 6))
    height = (3.0, 6.5)
    radius = 0.7
    sway = 0.6
    palette = ("#2f6b45", "#3a7a4f", "#2a5e3f")
    snowy = False

    def build(self, root, name, scale, rng):
        shapes.cylinder(name, 0.1 * scale, 0.6 * scale, look.matte("#5a3d28"), root, bevel=0, segments=8)
        green = _leafy(rng.choice(self.palette), 0.7)
        h = rng.uniform(2.2, 3.2) * scale
        for j in range(3):
            r = (0.95 - 0.25 * j) * scale
            z = 0.5 * scale + j * h * 0.26
            shapes.cylinder(name, r, h * 0.42, green, root, at=(0, 0, z), r2=0.0, bevel=0, segments=12)
            if self.snowy:
                shapes.cylinder(name + ".snow", r * 0.55, h * 0.2, look.matte("#f4f7fb", 0.6), root,
                                at=(0, 0, z + h * 0.24), r2=0.0, bevel=0, segments=12)


class SnowyPine(Pine):
    description = "A pine tree with snow on it"
    models = ()
    snowy = True


class Palm(Scenery):
    description = "A palm tree"
    radius = 0.5
    sway = 1.3

    def build(self, root, name, scale, rng):
        bark = look.matte("#a9825a")
        bend = rng.uniform(0.05, 0.12)
        p = Vector((0, 0, 0))
        tilt = 0.0
        for i in range(7):
            seg = shapes.cylinder(name, (0.13 - 0.008 * i) * scale, 0.5 * scale, bark, root, at=p.copy(),
                                  r2=(0.12 - 0.008 * i) * scale, bevel=0, segments=10)
            seg.rotation_euler.y = tilt
            p += Vector((math.sin(tilt), 0, math.cos(tilt))) * 0.48 * scale
            tilt += bend
        leaf = _leafy("#4f9a4a", 0.55)
        for k in range(7):
            a = 2 * math.pi * k / 7 + rng.uniform(-0.2, 0.2)
            lf = shapes.ellipsoid(name + ".leaf", 0.75 * scale, 0.16 * scale, 0.03 * scale, leaf, root,
                                  at=p + Vector((math.cos(a), math.sin(a), -0.35)) * 0.6 * scale, segments=12)
            lf.rotation_euler = (0, 0.55, a)
        for k in range(3):
            a = 2 * math.pi * k / 3
            shapes.sphere(name + ".nut", 0.07 * scale, look.matte("#6b4a2a"), root,
                          at=p + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, -0.12)) * scale, segments=10)


class Cactus(Scenery):
    description = "A tall cactus with arms"
    radius = 0.4
    sway = 0.0

    def build(self, root, name, scale, rng):
        green = look.plastic("#5f9b5a", 0.55, 0.2)
        h = rng.uniform(1.4, 2.4) * scale
        r = 0.16 * scale
        shapes.capsule(name, r, h - 2 * r, green, root, at=(0, 0, h / 2))
        for side in (-1, 1):
            if rng.random() < 0.8:
                z = rng.uniform(0.35, 0.6) * h
                shapes.capsule(name, r * 0.7, 0.25 * scale, green, root, at=(side * 0.25 * scale, 0, z),
                               rot=(0, math.pi / 2, 0))
                shapes.capsule(name, r * 0.7, 0.35 * scale, green, root, at=(side * 0.4 * scale, 0, z + 0.25 * scale))


class Bush(Scenery):
    description = "A round bush"
    models = ("Bush_Common_Flowers",)
    height = (0.75, 1.0)
    radius = 0.5
    sway = 0.6
    palette = ("#4f8f45", "#5aa84f", "#437d3c")

    def build(self, root, name, scale, rng):
        for _ in range(rng.randint(3, 5)):
            r = rng.uniform(0.25, 0.45) * scale
            shapes.sphere(name, r, _leafy(rng.choice(self.palette)), root,
                          at=(rng.uniform(-0.3, 0.3) * scale, rng.uniform(-0.3, 0.3) * scale, r * 0.75), segments=12)


class AutumnBush(Bush):
    description = "A bush in autumn colours"
    models = ("Bush_Common",)
    palette = ("#c9732b", "#b5482a", "#d9a33c")


class Rock(Scenery):
    description = "A rock or boulder"
    models = ("Rock_Medium_1", "Rock_Medium_2", "Rock_Medium_3")
    height = (0.5, 0.7)
    radius = 0.6
    sway = 0.0
    color = "#9a958d"

    def build(self, root, name, scale, rng):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        sx, sy, sz = rng.uniform(0.6, 1.0), rng.uniform(0.5, 0.9), rng.uniform(0.35, 0.6)
        off = rng.uniform(0, 100)
        for v in bm.verts:
            d = 1 + 0.18 * noise.noise(v.co * 1.7 + Vector((off, 0, 0)))
            v.co = Vector((v.co.x * sx * d, v.co.y * sy * d, max(-0.2, v.co.z) * sz * d)) * 0.6 * scale
        obj = shapes._object(name, bm, look.matte(self.color, 0.9), root, (0, 0, 0), (0, 0, 0), smooth=False)
        return obj


class MoonRock(Rock):
    description = "A grey moon rock"
    models = ()
    color = "#8a8a8e"


class Flowers(Scenery):
    description = "A clump of wild flowers"
    models = ("Flower_3_Group", "Flower_4_Group", "Bush_Common_Flowers")
    height = (0.3, 0.4)
    radius = 0.3
    blocks = False
    sway = 0.8

    def build(self, root, name, scale, rng):
        stem = look.matte("#4f8f45")
        color = look.plastic(rng.choice(["#f1c453", "#ef7aa1", "#ffffff", "#9b7fd4", "#e4572e"]), 0.5, 0.1)
        for _ in range(rng.randint(4, 7)):
            x, y = rng.uniform(-0.2, 0.2) * scale, rng.uniform(-0.2, 0.2) * scale
            h = rng.uniform(0.15, 0.3) * scale
            shapes.cylinder(name, 0.008, h, stem, root, at=(x, y, 0), bevel=0, segments=5)
            shapes.sphere(name, 0.035 * scale, color, root, at=(x, y, h), segments=8)


class Grass(Scenery):
    description = "A tuft of long grass"
    models = ("Grass_Common_Tall", "Grass_Wispy_Tall", "Grass_Common_Short")
    height = (0.3, 0.45)
    radius = 0.25
    blocks = False
    sway = 1.5
    color = "#6aa84f"

    def build(self, root, name, scale, rng):
        mat = look.matte(self.color, 0.7)
        for _ in range(rng.randint(5, 8)):
            blade = shapes.cylinder(name, 0.02 * scale, rng.uniform(0.2, 0.4) * scale, mat, root,
                                    at=(rng.uniform(-0.1, 0.1) * scale, rng.uniform(-0.1, 0.1) * scale, 0),
                                    r2=0.0, bevel=0, segments=4)
            blade.rotation_euler = (rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0)


class DryGrass(Grass):
    description = "A tuft of dry grass"
    models = ()
    color = "#c9b06a"


class Mushroom(Scenery):
    description = "A spotted toadstool"
    models = ("Mushroom_Common", "Mushroom_Laetiporus")
    height = (0.2, 0.25)
    radius = 0.2
    blocks = False
    sway = 0.0

    def build(self, root, name, scale, rng):
        shapes.cylinder(name, 0.04 * scale, 0.16 * scale, look.matte("#f3ead8"), root, bevel=0, segments=10)
        cap = shapes.sphere(name, 0.11 * scale, look.plastic("#d9412b", 0.4, 0.3), root, at=(0, 0, 0.16 * scale),
                            segments=14)
        cap.scale.z = 0.55
        for k in range(5):
            a = 2 * math.pi * k / 5
            shapes.sphere(name, 0.018 * scale, look.matte("white"), root,
                          at=(math.cos(a) * 0.07 * scale, math.sin(a) * 0.07 * scale, 0.205 * scale), segments=8)


class DeadTree(Scenery):
    description = "A bare, dead tree"
    models = tuple(f"DeadTree_{i}" for i in range(1, 6))
    height = (2.4, 5.0)
    radius = 0.4
    sway = 0.2

    def build(self, root, name, scale, rng):
        wood = look.matte("#7a6a5a")
        h = rng.uniform(1.6, 2.6) * scale
        shapes.cylinder(name, 0.1 * scale, h, wood, root, r2=0.04 * scale, bevel=0, segments=8)
        for k in range(rng.randint(2, 4)):
            z = rng.uniform(0.4, 0.85) * h
            b = shapes.cylinder(name, 0.04 * scale, rng.uniform(0.5, 0.9) * scale, wood, root, at=(0, 0, z),
                                r2=0.01, bevel=0, segments=6)
            b.rotation_euler = (rng.uniform(0.6, 1.0), 0, rng.uniform(0, 2 * math.pi))


class Snowman(Scenery):
    description = "A snowman"
    radius = 0.4
    sway = 0.0

    def build(self, root, name, scale, rng):
        snow = look.matte("#f4f7fb", 0.6)
        for r, z in ((0.38, 0.32), (0.27, 0.85), (0.19, 1.25)):
            shapes.sphere(name, r * scale, snow, root, at=(0, 0, z * scale), segments=16)
        nose = shapes.cylinder(name, 0.03 * scale, 0.18 * scale, look.plastic("orange"), root,
                               at=(0, -0.17 * scale, 1.27 * scale), r2=0.0, bevel=0, segments=8)
        nose.rotation_euler.x = math.pi / 2
        for sx in (-1, 1):
            shapes.sphere(name, 0.025 * scale, "black", root, at=(sx * 0.07 * scale, -0.17 * scale, 1.33 * scale),
                          segments=8)


class Crater(Scenery):
    description = "A crater (on the moon)"
    radius = 1.5
    blocks = False
    sway = 0.0

    def build(self, root, name, scale, rng):
        shapes.torus(name, 1.2 * scale, 0.25 * scale, look.matte("#9a9a9e", 0.95), root).scale.z = 0.4
        disc = shapes.cylinder(name, 1.15 * scale, 0.02, look.matte("#77777c", 0.95), root, bevel=0, segments=24)
        disc.location.z = -0.01


# ---------------------------------------------------------------------- terrain
TERRAINS = ("flat", "rolling", "hills", "mountains", "dunes", "craters")


class Terrain:
    """The shape of the land: flat in the acting area, rising with distance."""

    def __init__(self, style, seed, flat_w, flat_d, front=6.0):
        self.style = style
        self.seed = seed
        self.hw, self.hd, self.front = flat_w / 2 + 1.5, flat_d / 2 + 1.0, front

    def _outside(self, x, y):
        dx = max(0.0, abs(x) - self.hw)
        dy = max(0.0, y - self.hd, -self.hd - self.front - y)
        return math.hypot(dx, dy)

    def height(self, x, y):
        st = self.style
        if st == "flat":
            return 0.0
        d = self._outside(x, y)
        if d <= 0:
            return 0.0
        o = Vector((x, y, self.seed * 17.0))
        ramp = lambda r: min(1.0, d / r) ** 2 * (3 - 2 * min(1.0, d / r))   # noqa: E731
        far = min(1.0, max(0.0, (d - 20) / 80))       # the land rises towards the horizon
        if st == "rolling":
            return ramp(8) * (1.2 + 1.2 * noise.fractal(o * 0.035, 1.0, 2.0, 3)) + \
                9 * far ** 1.3 * (0.6 + 0.4 * noise.noise(o * 0.02))
        if st == "hills":
            return ramp(10) * (3.5 + 3.5 * noise.fractal(o * 0.03, 1.0, 2.0, 4)) + \
                20 * far ** 1.3 * (0.5 + 0.5 * noise.noise(o * 0.02))
        if st == "dunes":
            ridge = abs(math.sin(x * 0.09 + noise.noise(o * 0.02) * 3.0))
            return ramp(7) * (1.0 + 2.2 * ridge + 0.8 * noise.noise(o * 0.05))
        if st == "craters":
            return ramp(6) * (0.5 + 0.5 * noise.fractal(o * 0.06, 1.0, 2.0, 3))
        if st == "mountains":
            base = ramp(10) * (3.0 + 3.0 * noise.fractal(o * 0.03, 1.0, 2.0, 4))
            far = max(0.0, (d - 14) / 45)
            peaks = 48 * min(1.0, far) ** 1.4 * max(0.0, 0.55 + noise.fractal(o * 0.018, 0.9, 2.1, 5))
            return base + peaks
        return 0.0

    def build(self, color, far_color=None, snow_line=None, rng=None):
        """A ground mesh coloured by height and slope (grass, rock, snow)."""
        n = 110
        X0, X1, Y0, Y1 = -130.0, 130.0, -90.0, 170.0
        bm = bmesh.new()
        grid = []
        for j in range(n + 1):
            row = []
            # finer near the acting area, coarser far away
            v = j / n
            y = Y0 + (Y1 - Y0) * (v ** 1.0)
            for i in range(n + 1):
                u = i / n
                x = X0 + (X1 - X0) * u
                row.append(bm.verts.new((x, y, self.height(x, y) - 0.002)))
            grid.append(row)
        for j in range(n):
            for i in range(n):
                bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        bm.normal_update()
        base, far = look.rgb(color), look.rgb(far_color or color)
        rock, snow = look.rgb("#8f8a84"), look.rgb("#f2f5f8")
        mesh = bpy.data.meshes.new("ground")
        bm.to_mesh(mesh)
        bm.free()
        attr = mesh.color_attributes.new("ground", "FLOAT_COLOR", "POINT")
        for v in mesh.vertices:
            x, y, z = v.co
            d = min(1.0, self._outside(x, y) / 60)
            c = [b + (f - b) * d for b, f in zip(base, far)]
            patch = 0.88 + 0.12 * noise.noise(Vector((x * 0.15, y * 0.15, self.seed)))
            c = [ch * patch for ch in c]
            steep = 1 - v.normal.z
            if steep > 0.25:
                t = min(1.0, (steep - 0.25) * 3)
                c = [a + (b - a) * t for a, b in zip(c, rock)]
            if snow_line is not None and z > snow_line:
                t = min(1.0, (z - snow_line) / 4)
                c = [a + (b - a) * t for a, b in zip(c, snow)]
            attr.data[v.index].color = (*c, 1.0)
        for p in mesh.polygons:
            p.use_smooth = True
        obj = bpy.data.objects.new("ground", mesh)
        bpy.context.scene.collection.objects.link(obj)
        mat = bpy.data.materials.new("ground")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        ca = nt.nodes.new("ShaderNodeVertexColor")
        ca.layer_name = "ground"
        nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.92
        mat.diffuse_color = (*base, 1)
        mesh.materials.append(mat)
        return obj


# ---------------------------------------------------------------------- biomes
class Biome(Plugin):
    """A kind of outdoor place: ground colours, the shape of the land and what grows where.

    `scatter`: (scenery, weight) for the distance and the sides; `near`: small things (flowers, grass)
    allowed close to the acting area; `density`: how many. Override `build_extra` for things like the
    sea, `adjust_light` for a different sky, `animate` for things that move."""
    kind = "biome"
    abstract = True
    ground = "grass"
    far = None
    path = "#a9a196"
    terrain = "rolling"
    snow_line = None
    scatter = [("tree", 1.0)]
    near = []
    density = 1.0

    @classmethod
    def describe_extra(cls):
        return {"terrain": cls.terrain, "scenery": [n for n, _ in cls.scatter + cls.near]}

    def build_extra(self, s, rng):
        pass

    def allowed(self, x, y, s):
        """Whether scenery may go at (x, y) (not in the sea, say)."""
        return True

    def adjust_light(self, light):
        pass

    def animate(self, s, length):
        pass


class Meadow(Biome):
    description = "Grass, round trees, bushes and flowers (the default)"
    ground, far = "#7cb85a", "#93c977"
    scatter = [("tree", 1.0), ("bush", 0.6), ("rock", 0.15)]
    near = [("flowers", 1.0), ("grass", 1.0)]


class Forest(Biome):
    description = "Deep woods: tall trees close together, mushrooms underfoot"
    ground, far = "#5f8f45", "#4a7a3c"
    terrain = "rolling"
    scatter = [("pine", 1.0), ("tree", 0.8), ("bush", 0.7), ("rock", 0.2)]
    near = [("mushroom", 0.6), ("grass", 1.0), ("bush", 0.3)]
    density = 2.4

    def adjust_light(self, light):
        light.sun_energy *= 0.85
        light.wind *= 0.7


class Autumn(Biome):
    description = "Woods in autumn: orange and red leaves"
    ground, far = "#a39a52", "#b08a4a"
    scatter = [("autumn_tree", 1.0), ("autumn_bush", 0.6), ("tree", 0.15), ("rock", 0.15)]
    near = [("dry_grass", 1.0), ("mushroom", 0.3)]
    density = 1.6


class Beach(Biome):
    description = "Sand, palm trees and the sea behind"
    ground, far = "#e8d4a2", "#e3cf9e"
    path = None
    terrain = "flat"
    scatter = [("palm", 1.0), ("rock", 0.3), ("bush", 0.2)]
    near = [("dry_grass", 0.4), ("rock", 0.1)]
    density = 1.2

    def build_extra(self, s, rng):
        y0 = s.depth / 2 + 3.5
        sea = shapes.box("sea", 400, 200, 0.1, look.plastic("#2f8fb5", 0.12, 0.6), at=(0, y0 + 100, -0.35), bevel=0)
        sea.name = "ground.sea"
        s.foam = []
        for i in range(3):
            f = shapes.box(f"ground.foam{i}", 400, 0.25, 0.04, look.plastic("#f4fbff", 0.5, 0.0, emission=0.3),
                           at=(0, y0 + 0.4 + i * 1.6, -0.27), bevel=0)
            s.foam.append(f)
        self.y0 = y0

    def allowed(self, x, y, s):
        return y < s.depth / 2 + 2.0

    def height(self, x, y, s):
        """The beach slopes gently down into the water."""
        y0 = s.depth / 2 + 3.5
        return -0.35 * min(1.0, max(0.0, (y - y0 + 1.5) / 3.0)) if y > y0 - 1.5 else 0.0

    def animate(self, s, length):
        from . import keys
        last = keys.CLOCK.frame(length) + 1
        for i, f in enumerate(getattr(s, "foam", [])):
            y = f.location.y
            for fr in range(1, last + 1, 6):
                t = keys.CLOCK.seconds(fr)
                f.location.y = y - 0.6 * (0.5 + 0.5 * math.sin(t * 0.9 + i * 2.1))
                f.keyframe_insert("location", index=1, frame=fr)


class Desert(Biome):
    description = "Sand dunes, cacti and rocks under a hot sky"
    ground, far = "#e0b97a", "#d9a866"
    path = None
    terrain = "dunes"
    scatter = [("cactus", 1.0), ("rock", 0.8), ("dead_tree", 0.15)]
    near = [("dry_grass", 0.6)]
    density = 0.8

    def adjust_light(self, light):
        from .environment import mix
        light.horizon = mix(light.horizon, "#f2d3a0", 0.35)
        light.sun_energy *= 1.1


class SnowField(Biome):
    name = "snow"
    description = "Deep snow and snowy pines"
    ground, far = "#eef2f6", "#e6ecf2"
    path = "#cfd6de"
    terrain = "hills"
    scatter = [("snowy_pine", 1.0), ("rock", 0.25), ("dead_tree", 0.1)]
    near = [("dry_grass", 1.0), ("snowman", 0.06)]
    density = 1.4

    def adjust_light(self, light):
        light.room *= 1.1


class Mountains(Biome):
    description = "An alpine valley with peaks and snow caps"
    ground, far = "#6f9f55", "#7a9a6a"
    terrain = "mountains"
    snow_line = 24.0
    scatter = [("pine", 1.0), ("rock", 0.6), ("bush", 0.3)]
    near = [("flowers", 0.6), ("grass", 1.0)]
    density = 0.9


class Moon(Biome):
    description = "The surface of the moon: grey dust, craters, a black sky with the Earth in it"
    ground, far = "#a3a3a7", "#8c8c90"
    path = None
    terrain = "craters"
    scatter = [("moon_rock", 1.0), ("crater", 0.8)]
    near = [("crater", 0.3)]
    density = 1.0

    def adjust_light(self, light):
        light.zenith, light.horizon = "#000000", "#05060a"
        light.sky_strength = 0.05
        light.stars = 1.0
        light.sun_softness = 1.0
        light.sun_disc = False
        light.fog = 0.0
        light.wind = 0.0

    def build_extra(self, s, rng):
        earth = shapes.sphere("fx.earth", 14, look.plastic("#3d7dd8", 0.6, 0.0, emission=1.2),
                              at=(40, 230, 40), segments=32)
        earth["dr_fx"] = True
        for k in range(6):
            a, b = rng.uniform(0, 6.28), rng.uniform(-1, 1)
            land = shapes.sphere("fx.earth", rng.uniform(4, 7), look.plastic("#62b06f", 0.6, 0.0, emission=1.2),
                                 at=(40 + 10 * math.cos(a) * math.sqrt(1 - b * b), 220 - 10 * math.sin(a) * 0.3,
                                     40 + 10 * b), segments=16)
            land.scale = (1, 0.4, 0.8)
            land["dr_fx"] = True


# ---------------------------------------------------------------------- laying it out
def scatter(s, biome, rng, density=1.0):
    """Put scenery round an outdoor set by rules: thick in the distance, thinner at the sides,
    a little behind the camera (for reverse shots), a few small things near the acting area, never
    in the acting area itself or where the camera usually stands."""
    from . import plugins
    W, D = s.width, s.depth
    placed = []

    def pick(table):
        total = sum(w for _, w in table)
        r = rng.uniform(0, total)
        for name, w in table:
            r -= w
            if r <= 0:
                return name
        return table[-1][0]

    def free(p, r, small=False):
        if abs(p.x) < W / 2 + 0.6 and -D / 2 - 0.6 < p.y < D / 2 + 0.6:
            return False     # the acting area
        if not small and abs(p.x) < 6.5 and -D / 2 - 14 < p.y < -D / 2:
            return False     # where the camera usually stands (small things are fine: foreground)
        if not biome.allowed(p.x, p.y, s):
            return False
        return all((p - q).length > r + rq for q, rq in placed)

    def put(table, region, count, scale=(0.85, 1.3), grow=True):
        if not table:
            return
        tries = 0
        n = 0
        while n < count and tries < count * 25:
            tries += 1
            x0, x1, y0, y1 = region
            p = Vector((rng.uniform(x0, x1), rng.uniform(y0, y1)))
            kind = pick(table)
            cls = plugins.get("scenery", kind)
            dist = max(0.0, p.y - D / 2, abs(p.x) - W / 2)
            sc = rng.uniform(*scale) * ((1 + dist / 45) if grow else 1.0)
            r = cls.radius * sc
            if not free(p, r, small=not cls.blocks and cls.radius < 0.35):
                continue
            placed.append((p, r))
            cls().place(s, f"{kind}.{n}", p, sc, rng, block=False)
            n += 1

    k = density * biome.density
    put(biome.scatter, (-W / 2 - 40, W / 2 + 40, D / 2 + 0.8, D / 2 + 45), int(70 * k))         # behind
    for side in (-1, 1):                                                                           # the sides
        x0, x1 = sorted((side * (W / 2 + 0.8), side * (W / 2 + 26)))
        put(biome.scatter, (x0, x1, -D / 2 - 20, D / 2 + 1), int(22 * k))
    put(biome.scatter, (-W / 2 - 30, W / 2 + 30, -D / 2 - 45, -D / 2 - 6), int(22 * k))         # behind the camera
    small = biome.near or []
    put(small, (-W / 2 - 2.5, W / 2 + 2.5, -D / 2 - 1, D / 2 + 3), int(14 * density), (0.8, 1.2), grow=False)
    put([t for t in small if not plugins.get("scenery", t[0]).blocks], (-7, 7, -D / 2 - 7, -D / 2 - 0.7),
        int(10 * density), (0.8, 1.2), grow=False)                                              # foreground
    return placed
