"""People: stylized humans, between the toy figures and real people (think animated feature films).

    # cast/maya.toml
    type = "person"
    age = "child"            # child, teen, adult
    build = "average"        # slim, average, sturdy
    skin = "#e8b896"
    hair = "pigtails"
    hair_color = "ginger"
    eye_color = "#3f7fbf"
    top = "white"
    bottom = "navy"
    outfit = "skirt"         # trousers, shorts, skirt, dress
    sleeves = "long"         # long, short, none
    freckles = true
    braces = true

The body is one smooth, skinned mesh grown from a stick figure (Blender's Skin modifier, then
subdivided): torso, neck, arms with elbows, mitten hands with thumbs, legs with knees, shoes. Its
skeleton is driven like an imported model's (models.py), so elbows and knees bend, and every walk,
gesture, motion capture clip and handling verb works. The head is sculpted (cranium, jaw, chin,
cheeks) and carries the full face (face.py): eyes with irises and lids, brows, nose, ears, lashes,
teeth, freckles, and the same moods as everyone else.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import look, plugins, shapes
from .models import ModelCharacter, auto_rig
from .plugins import Param

# proportions (fractions of height), from a big-headed child to an adult
AGES = {
    #          head  neck  shoulder sh_x  elbow wrist hand  hips  hip_x knee  ankle
    "child": (0.215, 0.765, 0.735, 0.100, 0.585, 0.460, 0.385, 0.500, 0.050, 0.265, 0.045),
    "teen":  (0.19, 0.785, 0.755, 0.110, 0.615, 0.470, 0.395, 0.510, 0.055, 0.272, 0.043),
    "adult": (0.165, 0.812, 0.788, 0.118, 0.635, 0.480, 0.400, 0.520, 0.058, 0.280, 0.040),
}
BUILDS = {"slim": 0.85, "average": 1.0, "sturdy": 1.2}


def _skin_mesh(name, nodes, edges, root=0):
    """A smooth body from a stick figure: nodes are (point, (radius_x, radius_y))."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([p for p, _ in nodes], edges, [])
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    mod = obj.modifiers.new("skin", "SKIN")
    mod.branch_smoothing = 0.6
    mod.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, (_, r) in enumerate(nodes):
        sv[i].radius = r
        sv[i].use_root = i == root
    sub = obj.modifiers.new("smooth", "SUBSURF")
    sub.levels = sub.render_levels = 2
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    baked = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(me)
    body = bpy.data.objects.new(name, baked)
    shapes._collection().objects.link(body)
    for p in baked.polygons:
        p.use_smooth = True
    return body


class Person(ModelCharacter):
    """A stylized human: a smooth skinned body, a sculpted head, a full face."""
    name = "person"
    label = "Person"
    description = "A stylized human (animated-film style): child, teen or adult, with a full face"
    drawing = None
    face_layout = {"eye_x": 0.07, "eye_z": -0.005, "brow_z": 0.062, "mouth_z": -0.118, "nose_z": -0.06,
                   "blush_x": 0.1, "blush_z": -0.07}
    params = [
        Param("name", "text", label="Name"),
        Param("age", "choice", default="child", choices=tuple(AGES), label="Age"),
        Param("height", "number", default=None, min=0.5, max=2.0, step=0.05,
              label="Height (m; child 1.0, teen 1.3, adult 1.55 if not set)"),
        Param("build", "choice", default="average", choices=tuple(BUILDS), label="Build"),
        Param("skin", "color", default="#e8b896"),
        Param("hair", "hair", default="short"),
        Param("hair_color", "color", default="brown"),
        Param("eye_color", "color", default="#6b4423", label="Eye colour"),
        Param("eyes", "choice", default="normal", choices=("small", "normal", "big")),
        Param("top", "color", default="teal"),
        Param("bottom", "color", default="navy"),
        Param("shoes", "color", default="charcoal"),
        Param("outfit", "choice", default="trousers", choices=("trousers", "shorts", "skirt", "dress")),
        Param("sleeves", "choice", default="long", choices=("long", "short", "none")),
        Param("nose", "choice", default="button", choices=("button", "round", "pointy")),
        Param("brows", "choice", default="normal", choices=("thin", "normal", "thick")),
        Param("freckles", "bool", default=False),
        Param("blush", "bool", default=False),
        Param("braces", "bool", default=False, label="Braces on the teeth"),
        Param("extras", "extras", default=[]),
        Param("voice", "voice"),
    ]
    default_capabilities = ("walk", "arms", "swing_legs", "face")

    def validate(self):
        for p in self.params:
            v = self.spec.get(p.name)
            if v is not None and p.type == "choice" and p.choices and v not in p.choices:
                raise ValueError(f"{self.name}: {p.name} {v!r} unknown; use one of {list(p.choices)}")
        if "hair" in self.spec:
            plugins.get("hair", self.spec["hair"])

    def proportions(self):
        age = self.get("age", "child")
        self.H = float(self.get("height") or {"child": 1.0, "teen": 1.3, "adult": 1.55}.get(age, 1.0))
        self.P = AGES.get(age, AGES["child"])
        self.girth = BUILDS.get(self.get("build", "average"), 1.0)

    # ------------------------------------------------------------------ the body
    def skeleton(self):
        """Joint positions (world, standing at the origin facing -Y) for the rig and the skin."""
        H = self.H
        head, neck, sh, sh_x, elbow, wrist, hand, hips, hip_x, knee, ankle = self.P
        g = self.girth
        j = {"hips": Vector((0, 0, hips * H)), "chest": Vector((0, 0, hips * H + 0.002 * H)),
             "neck": Vector((0, 0, neck * H))}
        self.chin_z = (1 - head) * H
        self.hr_ = head * H / 2.2                         # cranium radius: the head is ~2.2 of them tall
        self.head_c = Vector((0, -0.006 * H, self.chin_z + 1.2 * self.hr_))
        j["head"] = self.head_c.copy()
        for side, s in ((1, "l"), (-1, "r")):
            x = side * sh_x * H * (0.95 + 0.05 * g)
            j[f"{s}_arm"] = Vector((x, 0.004 * H, sh * H))
            j[f"{s}_elbow"] = Vector((x + side * 0.03 * H, 0.016 * H, elbow * H))
            j[f"{s}_wrist"] = Vector((x + side * 0.052 * H, 0.004 * H, wrist * H))
            j[f"{s}_hand"] = Vector((x + side * 0.06 * H, -0.004 * H, hand * H))
            hx = side * hip_x * H * g
            j[f"{s}_hip"] = Vector((hx, 0, (hips - 0.03) * H))
            j[f"{s}_knee"] = Vector((hx * 0.95, -0.008 * H, knee * H))
            j[f"{s}_ankle"] = Vector((hx * 0.92, 0.004 * H, ankle * H))
            j[f"{s}_toe"] = Vector((hx * 0.92, -0.075 * H, 0.022 * H))
        return j

    def body_mesh(self, j):
        H, g = self.H, self.girth
        head, neck, sh, *_ = self.P
        hips_z = j["hips"].z
        kid = 1.0 + (head - 0.165) * 2.5        # children are rounder
        nodes, edges = [], []

        def node(p, rx, ry=None):
            nodes.append((Vector(p), (rx * H, (ry if ry is not None else rx) * H)))
            return len(nodes) - 1

        def chain(*ids):
            edges.extend(zip(ids, ids[1:]))
        pelvis = node(j["hips"] + Vector((0, 0.004 * H, 0)), 0.078 * g, 0.058 * g)
        waist = node((0, 0.002 * H, hips_z + 0.075 * H), 0.068 * g * kid, 0.052 * g * kid)
        chest = node((0, 0, sh * H - 0.05 * H), 0.082 * g, 0.056 * g)
        collar = node((0, 0.004 * H, sh * H + 0.008 * H), 0.05 * g, 0.04 * g)
        nk = node((0, 0.006 * H, j["neck"].z + 0.012 * H), 0.026, 0.026)
        nk2 = node((0, 0.006 * H, self.chin_z + 0.02 * H), 0.024, 0.024)
        chain(pelvis, waist, chest, collar, nk, nk2)
        for side, s in ((1, "l"), (-1, "r")):
            shoulder = node(j[f"{s}_arm"], 0.03 * g, 0.03 * g)
            chain(collar, shoulder)
            el = node(j[f"{s}_elbow"], 0.023 * g)
            wr = node(j[f"{s}_wrist"], 0.017)
            w, tip = j[f"{s}_wrist"], j[f"{s}_hand"]
            palm = node(w.lerp(tip, 0.42), 0.023, 0.011)
            fingers = node(tip, 0.019, 0.0095)
            thumb = node(w.lerp(tip, 0.35) + Vector((-side * 0.016 * H, -0.016 * H, -0.004 * H)), 0.0085)
            chain(shoulder, el, wr, palm, fingers)
            chain(palm, thumb)
            hip = node(j[f"{s}_hip"], 0.05 * g, 0.048 * g)
            kn = node(j[f"{s}_knee"], 0.033 * g)
            calf = node(j[f"{s}_knee"].lerp(j[f"{s}_ankle"], 0.35) + Vector((0, 0.006 * H, 0)), 0.035 * g, 0.036 * g)
            an = node(j[f"{s}_ankle"], 0.026, 0.028)
            toe = node(j[f"{s}_toe"], 0.03, 0.024)
            chain(pelvis, hip, kn, calf, an, toe)
        body = _skin_mesh(f"{self.name}.body", nodes, edges, root=pelvis)
        self._dress(body, j)
        return body

    def _dress(self, body, j):
        """Colour the body by region: skin, top (with sleeves), bottom (trousers, shorts), shoes."""
        outfit, sleeves = self.get("outfit", "trousers"), self.get("sleeves", "long")
        mats = [look.skin(self.color("skin", "#e8b896")), look.matte(self.color("top", "teal"), 0.7),
                look.matte(self.color("bottom", "navy"), 0.7), look.plastic(self.color("shoes", "charcoal"), 0.45, 0.2)]
        for m in mats:
            body.data.materials.append(m)
        SKIN, TOP, BOTTOM, SHOES = range(4)
        sh_z = j["l_arm"].z
        segs = [("chest", j["chest"], j["neck"])]
        for s in ("l", "r"):
            segs += [(f"{s}_arm", j[f"{s}_arm"], j[f"{s}_elbow"]), (f"{s}_elbow", j[f"{s}_elbow"], j[f"{s}_wrist"]),
                     (f"{s}_wrist", j[f"{s}_wrist"], j[f"{s}_hand"]), (f"{s}_hip", j[f"{s}_hip"], j[f"{s}_knee"]),
                     (f"{s}_knee", j[f"{s}_knee"], j[f"{s}_ankle"]), (f"{s}_ankle", j[f"{s}_ankle"], j[f"{s}_toe"])]

        def nearest(p):
            best, bt = None, 0.0
            bd = 9.0
            for name, a, b in segs:
                ab = b - a
                t = max(0.0, min(1.0, (p - a).dot(ab) / max(1e-9, ab.length_squared)))
                d = (p - (a + ab * t)).length
                if d < bd:
                    best, bt, bd = name, t, d
            return best, bt
        for poly in body.data.polygons:
            p = poly.center
            part, t = nearest(p)
            kind = part.split("_")[-1] if "_" in part else part
            if part == "chest":
                m = SKIN if p.z > sh_z + 0.03 * self.H else (TOP if p.z > j["hips"].z + 0.02 * self.H else BOTTOM)
                if outfit in ("skirt", "dress") and p.z <= j["hips"].z + 0.02 * self.H:
                    m = TOP if outfit == "dress" else BOTTOM
            elif kind == "arm":
                m = TOP if sleeves == "long" or (sleeves == "short" and t < 0.55) else SKIN
            elif kind == "elbow":
                m = TOP if sleeves == "long" and t < 0.92 else SKIN
            elif kind == "wrist":
                m = SKIN
            elif kind == "hip":
                m = BOTTOM if outfit == "trousers" or (outfit == "shorts" and t < 0.6) or t < 0.12 else SKIN
            elif kind == "knee":
                m = BOTTOM if outfit == "trousers" and t < 0.8 else SKIN
                if p.z < j["l_ankle"].z + 0.035 * self.H:
                    m = SHOES
            else:
                m = SHOES
            poly.material_index = m

    def skirt(self, j):
        """A skirt (or the bottom of a dress) that hangs from the hips and moves with them."""
        H, g = self.H, self.girth
        top_r, low = 0.074 * H * g, j["l_knee"].z + 0.04 * H
        length = j["hips"].z + 0.03 * H - low
        color = self.color("top" if self.get("outfit") == "dress" else "bottom", "navy")
        sk = shapes.cylinder(f"{self.name}.skirt", top_r * 1.55, length, look.matte(color, 0.7), self.hips,
                             at=(0, 0.004 * H, low - j["hips"].z), r2=top_r, bevel=0.004 * H)
        return sk

    # ------------------------------------------------------------------ building
    def build(self):
        n, H = self.name, self.H
        j = self.skeleton()
        body = self.body_mesh(j)
        holder = shapes.empty(f"{n}.model")
        body.parent = holder
        bpy.context.view_layer.update()
        arm = auto_rig([body], H, joints=j)
        arm.parent = holder
        bpy.context.view_layer.update()
        roles = {r: r for r in ("hips", "chest", "neck") + tuple(f"{s}_{p}" for s in "lr" for p in
                                                                 ("arm", "elbow", "wrist", "hip", "knee", "ankle"))}
        roles["head"] = "neck"
        self.rig, self.roles, self.meshes, self.holder = arm, roles, [body], holder
        self._drive(arm, roles)
        if self.get("outfit") in ("skirt", "dress"):
            self.skirt(j)
        # the head rides on the neck pivot (exactly where the neck bone turns)
        self.hr = self.head_r = self.hr_
        self.hc = self.head_center = self.head_c - j["neck"]
        self.top_z = self.neck_z = j["neck"].z - self.hip_z
        self.face_H = H * self.hr / 0.19 * 0.97         # the toy face's features, scaled to this head
        self.build_head()
        self.build_face()
        self.build_hair()
        self.build_extras()

    def build_head(self):
        n, hr = self.name, self.hr
        head = self.P[0]
        self._jaw = 0.28 - (head - 0.165) * 3.0       # children: round faces; adults: a jaw
        width = 1.0 + (head - 0.165) * 1.2            # and a little wider
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=hr)
        for v in bm.verts:
            x, y, z = v.co
            if z < 0:     # the face below the eyes: longer, narrower to the jaw, chin a little forward
                d = -z / hr
                taper = 1 - self._jaw * d ** 1.6
                v.co.x = x * taper
                v.co.y = y * (1 - 0.18 * d ** 2) - 0.1 * hr * d ** 2 * (1 if y < 0 else 0)
                v.co.z = z * (1.3 - (head - 0.165) * 3)    # a longer face on adults
            if y < 0:     # a flatter face, fuller cheeks
                f = -v.co.y / hr
                v.co.y *= 0.94
                cheek = math.exp(-((abs(v.co.x) - 0.5 * hr) ** 2 + (v.co.z + 0.45 * hr) ** 2) / (0.09 * hr * hr))
                v.co.y -= 0.06 * hr * cheek * f
            v.co.x *= width
        me = bpy.data.meshes.new(f"{n}.head")
        bm.to_mesh(me)
        bm.free()
        head = bpy.data.objects.new(f"{n}.head", me)
        shapes._collection().objects.link(head)
        head.parent = self.neck
        head.location = self.hc
        head.data.materials.append(look.skin(self.color("skin", "#e8b896")))
        for p in me.polygons:
            p.use_smooth = True
        self.head_mesh = head
        self._head_tree = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        skin = look.skin(self.color("skin", "#e8b896"))
        for side in (1, -1):       # ears
            shapes.ellipsoid(f"{n}.ear", hr * 0.13, hr * 0.2, hr * 0.27, skin, self.neck,
                             at=self.hc + Vector((side * hr * 0.93, hr * 0.08, -hr * 0.12)),
                             rot=(0, 0, math.radians(side * -18)), segments=20)

    def face_point(self, x, z, inset=0.006):
        """A point on the front of the sculpted head (neck space), `x` across and `z` up from its centre."""
        tree = getattr(self, "_head_tree", None)
        if tree is not None:
            hit = tree.ray_cast(Vector((x, -5 * self.hr, z)), Vector((0, 1, 0)))
            if hit[0] is not None:
                return hit[0] + Vector((0, (inset - 0.003) * getattr(self, "face_H", self.H), 0)) + self.hc
        hr = self.hr
        y = -math.sqrt(max(0.0, hr * hr - x * x - z * z)) + inset * self.H
        return Vector((x, y, z)) + self.hc

    def build_face(self):
        super().build_face()
        n, fH = self.name, self.face_H
        skin = look.skin(self.color("skin", "#e8b896"))
        for o in [o for o in self.neck.children if o.name.startswith(f"{n}.nose")]:
            bpy.data.objects.remove(o, do_unlink=True)          # a sculpted nose instead of the toy's ball
        L = self.face_layout
        kind = self.get("nose", "button")
        at = self.face_point(0, L["nose_z"] * fH, 0.012)
        size = {"button": (0.022, 0.026, 0.024), "round": (0.028, 0.03, 0.028), "pointy": (0.018, 0.036, 0.03)}[kind]
        nose = shapes.ellipsoid(f"{n}.nose", size[0] * fH, size[1] * fH, size[2] * fH, skin, self.neck, at=at,
                                rot=(math.radians(-18 if kind == "pointy" else -8), 0, 0), segments=20)
        nose.location.y -= 0.004 * fH
        bridge = shapes.ellipsoid(f"{n}.nose", 0.012 * fH, 0.014 * fH, 0.03 * fH, skin, self.neck,
                                  at=self.face_point(0, (L["nose_z"] + 0.03) * fH, 0.012), segments=16)
        bridge.location.y -= 0.002 * fH
        thick = {"thin": 0.7, "normal": 1.15, "thick": 1.6}[self.get("brows", "normal")]
        for brow in self.brows.values():
            for o in brow.children:
                o.scale = (1.1, 1.0, thick) if thick > 1 else (1.0, 1.0, thick)
        lash = look.plastic("#2a1d18", 0.5, 0.1)
        for side, piv in zip((1, -1), self.eyes):      # lashes flick out at the outer corners
            for k, ang in enumerate((35, 60)):
                shapes.capsule(f"{n}.lash", 0.0022 * fH, 0.012 * fH, lash, piv,
                               at=(side * (0.027 + 0.004 * k) * fH, -0.012 * fH, (0.03 - 0.008 * k) * fH),
                               rot=(0, math.radians(side * ang), 0))
        if self.get("freckles"):
            rng = random.Random(n)
            brown = look.matte("#b07a52", 0.6)
            for _ in range(22):
                side = rng.choice((1, -1))
                x = side * rng.uniform(0.025, 0.11) * fH
                z = (L["nose_z"] + rng.uniform(-0.035, 0.02)) * fH
                shapes.sphere(f"{n}.freckle", rng.uniform(0.0025, 0.004) * fH, brown, self.neck,
                              at=self.face_point(x, z, -0.0005), segments=8)

    def build_hair(self):
        plugins.get("hair", self.get("hair", "short"))().build(self, self.color("hair_color", "brown"))

    def build_extras(self):
        for e in self.get("extras", []) or []:
            plugins.get("extra", e)().build(self)

    def head_top(self):
        return self.hc + Vector((0, 0, self.hr))
