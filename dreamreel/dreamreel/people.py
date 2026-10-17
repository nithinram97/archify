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

import bpy
from mathutils import Vector

from . import look, plugins, shapes
from .models import ModelCharacter, auto_rig
from .plugins import Param

# proportions (fractions of height), from a big-headed child to an adult
AGES = {
    #          head  neck  shoulder sh_x  elbow wrist hand  hips  hip_x knee  ankle
    "child": (0.215, 0.772, 0.745, 0.100, 0.585, 0.460, 0.385, 0.500, 0.050, 0.265, 0.045),
    "teen":  (0.19, 0.785, 0.755, 0.118, 0.615, 0.470, 0.395, 0.510, 0.055, 0.272, 0.043),
    "adult": (0.165, 0.812, 0.788, 0.13, 0.635, 0.480, 0.400, 0.520, 0.058, 0.280, 0.040),
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


def _lip_color(skin):
    """Lips: the skin colour, redder and a little darker."""
    r, g, b = look.rgb(skin)[:3]
    srgb = [max(0.0, min(1.0, c)) ** (1 / 2.2) for c in (r * 0.9, g * 0.62, b * 0.62)]
    return "#%02x%02x%02x" % tuple(int(c * 255) for c in srgb)


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
    def _age_t(self):
        return max(0.0, min(1.0, (0.215 - self.P[0]) / 0.05))

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
            j[f"{s}_toe"] = Vector((hx * 0.92, -(0.1 + 0.015 * self._age_t()) * H, 0.022 * H))
        return j

    def body_mesh(self, j):
        H, g = self.H, self.girth
        head, neck, sh, *_ = self.P
        hips_z = j["hips"].z
        t = max(0.0, min(1.0, (0.215 - head) / 0.05))        # 0 child ... 1 adult
        nodes, edges = [], []

        def R(child, adult):                                  # a radius (fraction of height), by age and build
            return (child + (adult - child) * t) * g

        def node(p, rx, ry=None):
            nodes.append((Vector(p), (rx * H, (ry if ry is not None else rx) * H)))
            return len(nodes) - 1

        def chain(*ids):
            edges.extend(zip(ids, ids[1:]))
        # the trunk: a pelvis (with a seat), a waist, the ribcage (an egg, wide at the top), the collar
        pelvis = node(j["hips"] + Vector((0, 0.008 * H, 0)), R(0.085, 0.09), R(0.066, 0.062))
        waist = node((0, 0.002 * H, hips_z + 0.07 * H), R(0.077, 0.07), R(0.062, 0.05))
        belly = node((0, -0.004 * H, hips_z + 0.12 * H), R(0.082, 0.078), R(0.066, 0.054))
        chest = node((0, -0.004 * H, sh * H - 0.065 * H), R(0.09, 0.098), R(0.066, 0.066))
        collar = node((0, 0.004 * H, sh * H + 0.004 * H), R(0.068, 0.082), R(0.044, 0.046))
        nk = node((0, 0.008 * H, j["neck"].z + 0.012 * H), R(0.033, 0.03), R(0.031, 0.029))
        nk2 = node((0, 0.008 * H, self.chin_z + 0.02 * H), R(0.03, 0.028), R(0.029, 0.027))
        chain(pelvis, waist, belly, chest, collar, nk, nk2)
        foot = (0.13 + 0.02 * t) * H
        for side, s in ((1, "l"), (-1, "r")):
            # arms: a round shoulder, a tapering upper arm, the forearm fuller near the elbow
            sh_j, el_j, wr_j, tip = j[f"{s}_arm"], j[f"{s}_elbow"], j[f"{s}_wrist"], j[f"{s}_hand"]
            shoulder = node(sh_j, R(0.035, 0.037))
            chain(collar, shoulder)
            upper = node(sh_j.lerp(el_j, 0.45), R(0.029, 0.028))
            el = node(el_j, R(0.022, 0.022))
            fore = node(el_j.lerp(wr_j, 0.3) + Vector((0, -0.003 * H, 0)), R(0.025, 0.024), R(0.022, 0.021))
            wr = node(wr_j, 0.016 * g, 0.014 * g)
            chain(shoulder, upper, el, fore, wr)
            # a hand: palm, knuckles, four fingers and a thumb (hanging, palm to the thigh)
            d = (tip - wr_j).normalized()
            palm = node(wr_j.lerp(tip, 0.3), 0.012 * g, 0.026 * g)
            knuck = node(wr_j.lerp(tip, 0.55), 0.01 * g, 0.025 * g)
            chain(wr, palm, knuck)
            for k, (off, length) in enumerate(((-0.018, 0.85), (-0.006, 1.0), (0.006, 0.95), (0.017, 0.78))):
                base = wr_j.lerp(tip, 0.55) + Vector((0, off * H, 0))
                f1 = node(base + d * 0.022 * H * length + Vector((0, off * 0.2 * H, 0)), 0.0068 * g)
                f2 = node(base + d * 0.045 * H * length + Vector((0, off * 0.35 * H, 0)), 0.0055 * g)
                chain(knuck, f1, f2)
            th1 = node(wr_j.lerp(tip, 0.25) + Vector((-side * 0.008 * H, -0.024 * H, 0)), 0.008 * g)
            th2 = node(wr_j.lerp(tip, 0.45) + Vector((-side * 0.01 * H, -0.034 * H, 0)), 0.0065 * g)
            chain(palm, th1, th2)
            # legs: thigh, knee, the calf curving out behind a straight shin, ankle, heel, foot
            hip_j, kn_j, an_j = j[f"{s}_hip"], j[f"{s}_knee"], j[f"{s}_ankle"]
            hip = node(hip_j, R(0.055, 0.058), R(0.055, 0.056))
            thigh = node(hip_j.lerp(kn_j, 0.45) + Vector((0, -0.004 * H, 0)), R(0.048, 0.05))
            kn = node(kn_j, R(0.033, 0.032))
            calf = node(kn_j.lerp(an_j, 0.3) + Vector((0, 0.012 * H, 0)), R(0.035, 0.036), R(0.04, 0.042))
            shin = node(kn_j.lerp(an_j, 0.7) + Vector((0, 0.004 * H, 0)), R(0.025, 0.024))
            an = node(an_j, 0.021 * g, 0.023 * g)
            heel = node(Vector((an_j.x, an_j.y + 0.018 * H, 0.022 * H)), 0.021 * g, 0.022 * g)
            ball = node(Vector((an_j.x, an_j.y - foot * 0.55, 0.022 * H)), 0.031 * g, 0.022 * g)
            toe = node(Vector((an_j.x, an_j.y - foot * 0.8, 0.02 * H)), 0.028 * g, 0.02 * g)
            chain(pelvis, hip, thigh, kn, calf, shin, an, heel)
            chain(an, ball, toe)
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
            if part == "chest" or (kind == "hip" and p.z > j["hips"].z - 0.01 * self.H):   # the trunk: by height
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

    # ------------------------------------------------------------------ the head (see docs/modeling.md)
    def landmarks(self):
        """Where the features go, in cranium radii from its centre: eyes halfway down an adult's head,
        brows halfway down a child's (the face is small under a big cranium)."""
        t = max(0.0, min(1.0, (0.215 - self.P[0]) / 0.05))       # 0 child ... 1 adult
        lerp = lambda a, b: a + (b - a) * t                       # noqa: E731
        eye_z = lerp(-0.30, -0.225)
        nose = lerp(-0.60, -0.74)
        size = {"small": 0.85, "normal": 1.0, "big": 1.15}.get(self.get("eyes"), 1.0)
        return dict(t=t, chin=-lerp(1.12, 1.45), eye_z=eye_z, eye_x=lerp(0.36, 0.34), brow_z=eye_z + lerp(0.25, 0.22),
                    eye_r=lerp(0.235, 0.165) * size, nose=nose, mouth=nose - lerp(0.17, 0.23), jaw=lerp(0.2, 0.3),
                    cheeks=lerp(0.09, 0.035), brow_ridge=lerp(0.02, 0.05))

    def build_head(self):
        """Sculpted like clay: block out the cranium and face, then sockets, brow, cheekbones, cheeks,
        muzzle, chin and nose, then smooth."""
        from .sculpt import Clay
        n, R = self.name, self.hr
        L = self.L = self.landmarks()
        chin, jaw = L["chin"], L["jaw"]

        def block(x, y, z):
            x *= 0.93                                       # the sides of the cranium are flatter
            if z < 0:                                       # the face hangs below it, down to the chin
                d = -z / R
                z = z * -chin
                x *= 1 - jaw * d * d
                y *= (1 - 0.45 * d ** 1.5) if y > 0 else (1 - 0.12 * d * d)
            if y < 0:
                y *= 0.9                                    # a flatter face plane
            return x, y, z
        clay = Clay.sphere(R, detail=5).stretch(block)
        S = clay.surface
        for side in (1, -1):
            x = side * L["eye_x"] * R
            clay.inflate(S(x, L["eye_z"] * R), (0.3 * R, 0.3 * R, 0.25 * R), -0.13 * R)            # eye sockets
            clay.inflate(S(side * 0.3 * R, (L["brow_z"] + 0.05) * R), (0.34 * R, 0.25 * R, 0.13 * R),
                         L["brow_ridge"] * R)                                                        # brow ridge
            clay.inflate(S(side * 0.52 * R, (L["eye_z"] - 0.24) * R), (0.24 * R, 0.24 * R, 0.17 * R), 0.035 * R)  # cheekbones
            clay.inflate(S(side * 0.42 * R, (L["mouth"] + 0.13) * R), 0.32 * R, L["cheeks"] * R)     # cheeks
        clay.inflate(S(0, L["mouth"] * R), (0.42 * R, 0.35 * R, 0.3 * R), 0.055 * R)                # muzzle
        clay.inflate(S(0, (chin + 0.17) * R), (0.22 * R, 0.2 * R, 0.16 * R), 0.05 * R)               # chin
        clay.smooth(2, amount=0.35)
        nose_kind = self.get("nose", "button")
        tip = {"button": 0.13, "round": 0.16, "pointy": 0.15}[nose_kind]
        for k in range(5):                                                                           # bridge
            z = L["eye_z"] + (L["nose"] + 0.12 - L["eye_z"]) * k / 4
            clay.inflate(S(0, z * R), (0.09 * R, 0.1 * R, 0.12 * R), (0.015 + 0.02 * k / 4) * R *
                         (1.6 if nose_kind == "pointy" else 1))
        clay.inflate(S(0, (L["nose"] + 0.1) * R), (0.13 if nose_kind == "round" else 0.11) * R, tip * R)  # tip
        for side in (1, -1):
            clay.inflate(S(side * 0.11 * R, (L["nose"] + 0.07) * R), 0.085 * R, 0.05 * R)               # wings
            clay.inflate(S(side * 0.055 * R, (L["nose"] + 0.02) * R), 0.03 * R, -0.022 * R)             # nostrils
        clay.inflate(S(0, L["mouth"] * R), (0.3 * R, 0.08 * R, 0.05 * R), -0.018 * R)                # mouth line
        clay.smooth(1, amount=0.25)
        skin = look.skin(self.color("skin", "#e8b896"))
        head = clay.object(f"{n}.head", skin, self.neck, at=self.hc)
        self.head_mesh = head
        self._head_tree = clay.tree()
        self.clay = clay
        for side in (1, -1):                                                                         # ears
            ear = Clay.sphere(1.0, detail=3).stretch(lambda x, y, z: (x * 0.06 * R, y * 0.17 * R, z * 0.27 * R))
            ear.inflate((side * 0.06 * R, -0.03 * R, 0), (0.06 * R, 0.1 * R, 0.16 * R), -0.035 * R)
            at = clay.side_point(0.08 * R, ((L["brow_z"] + L["nose"]) / 2) * R, side) + Vector((-side * 0.02 * R, 0, 0))
            o = ear.object(f"{n}.ear", skin, self.neck, at=self.hc + at)
            o.rotation_euler = (math.radians(-12), 0, math.radians(side * 14))

    def face_point(self, x, z, inset=0.006):
        """A point on the front of the sculpted head (neck space), `x` across and `z` up from its centre."""
        tree = getattr(self, "_head_tree", None)
        if tree is not None:
            hit = tree.ray_cast(Vector((x, -5 * self.hr, z)), Vector((0, 1, 0)))
            if hit[0] is not None:
                return hit[0] + Vector((0, inset * getattr(self, "face_H", self.H), 0)) + self.hc
        hr = self.hr
        y = -math.sqrt(max(0.0, hr * hr - x * x - z * z)) + inset * self.H
        return Vector((x, y, z)) + self.hc

    def build_face(self):
        """Eyeballs in the sockets with skin lids, brows on the brow ridge, lips, teeth, freckles."""
        from . import face
        n, R, L = self.name, self.hr, self.L
        skin = look.skin(self.color("skin", "#e8b896"))
        white = look.plastic("#f3efe9", 0.3, 0.35)
        iris_m = look.plastic(self.color("eye_color", "#6b4423"), 0.25, 0.5)
        dark = look.plastic("#120d0c", 0.15, 0.8)
        lash = look.plastic("#22160f", 0.6, 0.0)
        re = L["eye_r"] * R
        self.eyes, self.gazes, self.lid_pivots = [], [], {}
        self.eye_scale = 0.3
        for side in (1, -1):
            surf = self.face_point(side * L["eye_x"] * R, L["eye_z"] * R, 0)
            piv = shapes.empty(f"{n}.eye", self.neck, surf + Vector((0, re * 0.62, 0)))
            shapes.sphere(f"{n}.eyeball", re, white, piv, segments=32)
            look_at = shapes.empty(f"{n}.look", piv)
            gaze = shapes.empty(f"{n}.gaze", look_at, (0, -re * 0.9, 0))
            shapes.ellipsoid(f"{n}.iris", re * 0.5, re * 0.16, re * 0.5, iris_m, gaze, segments=24)
            shapes.ellipsoid(f"{n}.pupil", re * 0.24, re * 0.06, re * 0.24, dark, gaze, at=(0, -re * 0.13, 0),
                             segments=16)
            shapes.sphere(f"{n}.glint", re * 0.075, look.plastic("white", emission=1.5), gaze,
                          at=(side * re * 0.17, -re * 0.19, re * 0.18), segments=10)
            lids = []
            for which, normal in (("upper", 1), ("lower", -1)):
                lp = shapes.empty(f"{n}.lid.{which}", piv)
                lid = shapes.sphere(f"{n}.lid", re * 1.07, skin, lp, segments=32)
                shapes.cut_below(lid, Vector((0, 0, 0)), Vector((0, 0, normal)))
                if which == "upper":                       # the lash line along the lid's edge
                    line = shapes.sphere(f"{n}.lashline", re * 1.085, lash, lp, segments=32)
                    shapes.cut_below(line, Vector((0, 0, 0)), Vector((0, 0, 1)))
                    shapes.cut_below(line, Vector((0, 0, re * 0.13)), Vector((0, 0, -1)))
                    shapes.cut_below(line, Vector((0, re * 0.2, 0)), Vector((0, -1, 0)))
                    for k, ang in enumerate((25, 50, 75)):  # lashes flick out at the outer corner
                        shapes.capsule(f"{n}.lash", re * 0.03, re * (0.16 + 0.04 * k), lash, lp,
                                       at=(side * re * (0.62 + 0.13 * k), -re * (0.75 - 0.2 * k), re * 0.12),
                                       rot=(0, math.radians(side * (50 + 15 * k)), math.radians(side * -ang)))
                lids.append(lp)
            self.lid_pivots[side] = tuple(lids)
            self.eyes.append(piv)
            self.gazes.append(gaze)
        rest = face.lid_angles(face.values(plugins.get("mood", "neutral")), 1)
        for side, (up, low) in self.lid_pivots.items():
            up.rotation_euler = (rest[0], 0, 0)
            low.rotation_euler = (rest[1], 0, 0)
        # brows: tapered, thick by the nose, following the brow ridge
        thick = {"thin": 0.7, "normal": 1.0, "thick": 1.4}[self.get("brows", "normal")]
        brow_m = look.hair(self.spec.get("brow_color") or self.color("hair_color", "brown"))
        self.brows = {}
        for side in (1, -1):
            centre = self.face_point(side * L["eye_x"] * R * 0.95, L["brow_z"] * R, -0.004)
            piv = shapes.empty(f"{n}.brow", self.neck, centre)
            nodes = []
            for k, (u, dz, r) in enumerate(((-0.17, -0.01, 0.05), (-0.04, 0.03, 0.045), (0.09, 0.025, 0.033),
                                            (0.19, -0.03, 0.018))):
                x = side * L["eye_x"] * R * 0.95 + side * u * R
                p = self.face_point(x, (L["brow_z"] + dz) * R, -0.004) - centre
                nodes.append((p, (r * R * thick * 2.0, r * R * 0.6)))
            b = _skin_mesh(f"{n}.brow", nodes, [(0, 1), (1, 2), (2, 3)])
            b.data.materials.append(brow_m)
            b.parent = piv
            self.brows[side] = piv
        # the mouth: a dark line between two lips; it opens, smiles and shows the teeth
        mrx = L["eye_x"] * R * 0.78
        at = self.face_point(0, L["mouth"] * R, 0.0) + Vector((0, -0.024 * R, 0))     # on the muzzle, not in it
        self.mouth = shapes.empty(f"{n}.mouthpivot", self.neck, at)
        lip_m = look.skin(self.spec.get("lips") or _lip_color(self.color("skin", "#e8b896")))
        self.mouth_mesh = shapes.ellipsoid(f"{n}.mouth", mrx, 0.035 * R, 0.032 * R, look.plastic("#4a1a20", 0.5, 0.1),
                                           self.mouth, at=(0, 0.035 * R, 0), segments=24)    # inside, behind the teeth
        upper = shapes.ellipsoid(f"{n}.lip", mrx * 0.92, 0.042 * R, 0.034 * R, lip_m, self.mouth,
                                 at=(0, 0.004 * R, 0.03 * R), segments=24)
        lower = shapes.ellipsoid(f"{n}.lip", mrx * 0.8, 0.046 * R, 0.042 * R, lip_m, self.mouth,
                                 at=(0, 0.006 * R, -0.038 * R), segments=24)
        for lip in (upper, lower):           # lips keep their thickness when the mouth opens
            d = lip.driver_add("scale", 2).driver
            d.type = "SCRIPTED"
            var = d.variables.new()
            var.name = "v"
            var.targets[0].id = self.mouth
            var.targets[0].data_path = "scale[2]"
            d.expression = "1 / max(0.3, v)"
        self.lips = [upper, lower]
        self.teeth_open = 0.75               # showing teeth parts the lips
        face.mouth_parts(self, mrx, 0.1 * R, front=0.006 * R, extra=self.lips, teeth_z=0.2)
        self.irises, self.scleras, self.glints = [], [], []
        self.blushes = []
        if self.get("blush"):
            for side in (1, -1):
                self.blushes.append(shapes.ellipsoid(f"{n}.blush", 0.17 * R, 0.02 * R, 0.1 * R,
                                                     look.plastic("#f19aa6", 0.6, 0.1), self.neck,
                                                     at=self.face_point(side * 0.45 * R, (L["mouth"] + 0.2) * R, 0.0)))
        if self.get("freckles"):
            rng = random.Random(n)
            brown = look.matte("#a8714a", 0.6)
            for _ in range(26):
                side = rng.choice((1, -1))
                x = side * rng.uniform(0.08, 0.5) * R
                z = (L["nose"] + rng.uniform(0.05, 0.3)) * R
                shapes.sphere(f"{n}.freckle", rng.uniform(0.012, 0.02) * R, brown, self.neck,
                              at=self.face_point(x, z, 0.0004), segments=8)

    def build_hair(self):
        from . import hairdo
        hair = look.hair(self.color("hair_color", "brown"))    # not the toys' glossy plastic
        style = self.get("hair", "short")
        if hairdo.supported(style):        # sculpted in locks that follow the head (hairdo.py)
            hairdo.build(self, style, hair)
        else:
            plugins.get("hair", style)().build(self, hair)

    def build_extras(self):
        for e in self.get("extras", []) or []:
            plugins.get("extra", e)().build(self)

    def head_top(self):
        return self.hc + Vector((0, 0, self.hr))
