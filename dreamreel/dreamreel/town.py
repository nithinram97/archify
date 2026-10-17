"""Towns: a street of buildings made by rules (heights, colours, windows, shops), pavements, a road,
street lamps and parked cars.

    # sets/main_street.toml
    kind = "street"
    style = "town"          # town (pastel, 2-4 floors), city (tall, grey and glass), old_town (brick)
    shops = 0.5             # share of buildings with a shop at street level
    cars = 4
    seed = 2

The acting area is the pavement in front of the buildings; the road runs between it and the camera,
and the other side of the street is there for reverse shots. Marks: door, shop, crossing, kerb,
lamp (and the usual nine places).

City and old town streets are Quaternius's brick buildings when its city pack is downloaded
(`dreamreel assets`); the town style, and every style without the pack, is made here.

Building styles are a class attribute, so a film can add its own:

    class Street(dr.get("set", "street")):
        STYLES = dict(dr.get("set", "street").STYLES, neon={...})
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from . import look, shapes
from .plugins import Param
from .sets import COMMON, Set


class Parts:
    """Many boxes in one object (one per building), so a street stays light to render."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.mats = []

    def box(self, x, y, z, w, d, h, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        idx = self.mats.index(mat)
        res = bmesh.ops.create_cube(self.bm, size=1.0)
        vs = res["verts"]
        for v in vs:
            v.co = Vector((x + v.co.x * w, y + v.co.y * d, z + (v.co.z + 0.5) * h))
        for f in {f for v in vs for f in v.link_faces}:
            f.material_index = idx

    def done(self):
        mesh = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for m in self.mats:
            mesh.materials.append(m)
        obj = bpy.data.objects.new(self.name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj


class Street(Set):
    """A street of buildings with a pavement, a road and the other side of the street."""
    description = "A town street: buildings, shops, pavement, road, lamps and cars"
    outdoor = True
    size = (10.0, 4.0)
    STYLES = {
        "town": {"walls": ["#f3e6cc", "#f2c6b4", "#cfe3d4", "#f6dfa4", "#c9d8ea", "#e9d0e6"], "floors": (2, 4),
                 "trim": "#ffffff", "roof": "#b4553b"},
        "city": {"walls": ["#9aa3ad", "#c4c9cf", "#7d8691", "#b8b0a4", "#5f6872"], "floors": (5, 12),
                 "trim": "#4a5058", "roof": "#3a3a40"},
        "old_town": {"walls": ["#b4553b", "#a5684a", "#c27b56", "#9a5a44", "#d9b48a"], "floors": (2, 4),
                     "trim": "#f3e6cc", "roof": "#5a3825"},
    }
    AWNINGS = ["#e4572e", "#2a9d8f", "#3d7dd8", "#f1c453", "#7b5ea7"]
    params = COMMON + [
        Param("style", "choice", default="town", choices=("town", "city", "old_town")),
        Param("shops", "number", default=0.5, min=0, max=1, step=0.1, label="Shops"),
        Param("cars", "number", default=4, min=0, max=12, step=1),
        Param("lamps", "bool", default=True, label="Street lamps"),
        Param("trees", "bool", default=True, label="Street trees"),
        Param("seed", "number", default=2, min=0, max=999, step=1, label="Shuffle"),
    ]

    def build_environment(self):
        spec = self.spec
        style = self.STYLES.get(spec.get("style", "town"), self.STYLES["town"])
        rng = random.Random(int(spec.get("seed", 2)))
        W, D = self.width, self.depth
        back, kerb = D / 2, -D / 2
        road = 5.5
        far_kerb = kerb - road
        far_front = far_kerb - 2.5
        L = 140.0
        # ground: pavements, kerbs and the road
        shapes.box("ground", L * 2, 400, 0.1, look.matte("#6f6f72", 0.9), at=(0, 0, -0.25), bevel=0)
        shapes.box("ground.pavement", L * 2, back - kerb, 0.12, look.matte("#c9c5bd", 0.85),
                   at=(0, (back + kerb) / 2, -0.12), bevel=0)
        shapes.box("ground.pavement", L * 2, 2.5, 0.12, look.matte("#c9c5bd", 0.85), at=(0, far_kerb - 1.25, -0.12),
                   bevel=0)
        for y in (kerb, far_kerb):
            shapes.box("ground.kerb", L * 2, 0.18, 0.13, look.matte("#a9a59d", 0.8), at=(0, y, -0.13), bevel=0.01)
        shapes.box("ground.road", L * 2, road, 0.1, look.matte("#47474c", 0.9), at=(0, kerb - road / 2, -0.2), bevel=0)
        paint = look.matte("#f4f1ea", 0.6)
        lines = Parts("ground.lines")
        for x in range(-int(L), int(L), 4):
            lines.box(x, kerb - road / 2, -0.1, 1.6, 0.1, 0.005, paint)
        cross_x = W / 2 + 3.5
        for k in range(6):
            lines.box(cross_x, kerb - 0.45 - k * 0.85, -0.1, 2.2, 0.42, 0.006, paint)
        lines.done()
        # buildings on both sides
        self.doors = []
        self._row(rng, style, back, +1, L)
        self._row(rng, style, far_front, -1, L)
        # street lamps, trees and cars
        for i, x in enumerate(range(-35, 36, 7)):
            if spec.get("lamps", True):
                self._lamp(f"lamp{i}", x + 3.5, kerb + 0.3, near=abs(x + 3.5) < 15)
            if spec.get("trees", True) and abs(x) > 2:
                self.tree(f"streettree{i}", (x, kerb + 0.5), 0.6, rng)
        n = int(spec.get("cars", 4))
        xs = [x for x in range(-30, 31, 4) if abs(x) > 9]       # none parked in front of the camera
        rng.shuffle(xs)
        colors = ["red", "blue", "yellow", "teal", "white", "charcoal", "orange", "mint"]
        for i, x in enumerate(sorted(xs[:n])):
            far = i % 2 == 1
            self.add_prop({"type": "car", "name": f"car{i + 1}" if i else "car", "color": rng.choice(colors),
                           "at": (x + rng.uniform(-0.6, 0.6), (far_kerb + 0.75) if far else (kerb - 0.75)),
                           "facing": "right" if far else "left"})
        # marks
        door = min(self.doors, key=lambda d: abs(d[0])) if self.doors else (0.0, False)
        self.add_mark("door", (door[0], back - 0.5), facing="back")
        shop = min((d for d in self.doors if d[1]), key=lambda d: abs(d[0]), default=None)
        if shop:
            self.add_mark("shop", (shop[0] + 1.0, back - 0.7), facing="back")
        self.add_mark("crossing", (cross_x, kerb - 0.2), facing="camera")
        self.add_mark("kerb", (0.0, kerb + 0.35), facing="camera")
        self.add_mark("lamp", (3.5 + 0.5, kerb + 0.3))
        self.add_mark("across", (0.0, far_kerb - 1.0), facing="back")

    # -------------------------------------------------------------- pieces
    KIT = ("Building_Small_1", "Building_Medium_2_001", "Building_Large_2")    # Quaternius's city kit

    def _kit_row(self, rng, y0, side, L):
        """A row of Quaternius's brick buildings (city and old town streets), alternated and mirrored
        so the row doesn't repeat; False if the city pack isn't downloaded."""
        from . import quaternius
        if not self.use_models or quaternius.mesh("city", self.KIT[0]) is None:
            return False
        k = self.sized(0.6, 1.0)
        x = -L / 2 + rng.uniform(0, 3)
        i = 0
        while x < L / 2:
            name = rng.choice(self.KIT)
            m = quaternius.mesh("city", name)
            w = (max(v.co.x for v in m.vertices) - min(v.co.x for v in m.vertices)) * k
            depth = (max(v.co.y for v in m.vertices) - min(v.co.y for v in m.vertices)) * k
            cx, cy = x + w / 2, y0 + side * depth / 2
            obj = self.model(name, f"building{side}.{i}", (None, None, None), (cx, cy, 0),
                             0.0 if side > 0 else math.pi, pack="city")
            obj.scale = (k * rng.choice((1, -1)), k, k)
            obj["dr_building"] = True
            if side > 0:
                self.doors.append((cx, False))
                if abs(cx) < 30:
                    self.block(Vector((cx, cy)), w, depth)
            x += w + rng.uniform(0, 0.3) * k
            i += 1
        return True

    def _row(self, rng, style, y0, side, L):
        """A row of buildings with their fronts at y0, facing towards the street (side +1: the far
        side of the camera, -1: the near side, seen in reverse shots)."""
        if self.spec.get("style", "town") in ("city", "old_town") and self._kit_row(rng, y0, side, L):
            return
        x = -L / 2 + rng.uniform(0, 3)
        trim = look.matte(style["trim"], 0.6)
        glass = [look.plastic("#4f6b80", 0.12, 0.6, emission=0.0).copy() for _ in range(8)]
        for g in glass:
            bsdf = g.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Emission Color"].default_value = (*look.rgb("#ffd890"), 1)
            self.glows.append((g, "lit", 0.9))
        i = 0
        while x < L / 2:
            w = rng.choice((3.0, 3.6, 4.2, 4.8))
            floors = rng.randint(*style["floors"])
            FH = 2.0                                    # floor height, at the toy figures' scale
            h = floors * FH + 0.4
            near = abs(x + w / 2) < 18
            p = Parts(f"building{side}.{i}")
            wall = look.matte(rng.choice(style["walls"]), 0.85)
            depth = 6.0
            cy = y0 + side * depth / 2
            p.box(x + w / 2, cy, 0, w - 0.05, depth, h, wall)
            p.box(x + w / 2, y0 - side * 0.05, h - 0.05, w + 0.1, 0.3, 0.35, trim)            # cornice
            shop = rng.random() < self.spec.get("shops", 0.5)
            front = y0 - side * 0.02
            cols = max(1, int((w - 0.6) / 1.1))
            for fl in range(1, floors):
                z = fl * FH + 0.4
                for c in range(cols):
                    wx = x + w / 2 + (c - (cols - 1) / 2) * 1.1
                    p.box(wx, front, z + 0.45, 0.62, 0.06, 0.95, rng.choice(glass))
                    if near:
                        p.box(wx, front - side * 0.03, z + 0.4, 0.74, 0.1, 0.06, trim)         # sill
            # street level: a door, and a shop window with an awning
            dx = x + w / 2 + (rng.choice((-1, 1)) * (w / 2 - 0.65) if shop else 0)
            p.box(dx, front, 0, 0.86, 0.08, 1.68, look.matte(rng.choice(["#6e4a2f", "#26375f", "#2a9d8f", "#7a2e2e"])))
            p.box(dx, front - side * 0.02, 1.68, 1.0, 0.1, 0.08, trim)
            if shop:
                sx = x + w / 2 - (dx - (x + w / 2)) * 0.5
                p.box(sx, front, 0.35, w * 0.5, 0.07, 1.3, rng.choice(glass))
                aw = look.matte(rng.choice(self.AWNINGS), 0.7)
                p.box(sx, front - side * 0.35, 1.85, w * 0.56, 0.7, 0.1, aw)
            else:
                for c in range(cols):
                    wx = x + w / 2 + (c - (cols - 1) / 2) * 1.1
                    if abs(wx - dx) > 0.75:
                        p.box(wx, front, 0.6, 0.62, 0.06, 0.95, rng.choice(glass))
            p.box(x + w / 2, front - side * 0.02, 2.2, w - 0.1, 0.08, 0.1, trim)                # floor line
            obj = p.done()
            obj["dr_building"] = True
            if side > 0:
                self.doors.append((dx, shop))
                if abs(x + w / 2) < 30:
                    self.block(Vector((x + w / 2, cy)), w, depth)
            x += w
            i += 1

    def _lamp(self, name, x, y, near=True):
        shapes.cylinder(name, 0.05, 2.4, "charcoal", at=(x, y, 0), bevel=0, segments=10)
        arm = shapes.cylinder(name, 0.025, 0.45, "charcoal", at=(x, y, 2.37), bevel=0, segments=8)
        arm.rotation_euler.x = math.pi / 2
        shapes.sphere(name + ".bulb", 0.13, look.plastic("#fff1c4", 0.5, 0.0, emission=4), at=(x, y - 0.45, 2.33),
                      segments=16)
        if near:
            self.lights.append(((x, y - 0.45, 2.25), "#ffd9a0", 160))
        self.block(Vector((x, y)), 0.2, 0.2)

    def ground_height(self, x, y):
        return 0.0
