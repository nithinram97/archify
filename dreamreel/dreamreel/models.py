"""Your own characters: import a 3D model (glTF/GLB, FBX, OBJ) and it acts like any dreamreel character.

    # cast/hero.toml
    type = "model"
    file = "models/hero.glb"     # in the film's models/ folder
    height = 1.0                 # metres, to match the cast (toy figures are about 1 m)
    turn = 0                     # degrees, if the model doesn't face the front (-Y) after import

Rigged models (Mixamo, Ready Player Me, VRoid, Quaternius...) keep their skeleton: dreamreel finds the
hips, spine, neck, shoulders, elbows, wrists, legs, knees and ankles by name, or, when the names mean
nothing, by shape (legs are the chains that reach the floor, arms the ones that reach out sideways,
the head the highest). Unrigged models in a T or A pose are rigged automatically: joints are found
from the mesh's silhouette and the skin is weighted to the nearest bones.

Then the skeleton is driven by dreamreel's usual pivots (hips, body, neck, an arm pivot at each
shoulder and a leg pivot at each hip, with IK for elbows and knees), so every gesture, walk, motion
capture clip and handling verb works on it. If the model has facial shape keys (blink, smile,
jawOpen, ARKit, VRM...), moods, blinks and talking drive them.

Check the licence of any model you use.
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from . import shapes
from .character import Character
from .plugins import Param

FORMATS = (".glb", ".gltf", ".fbx", ".obj")


def files(root):
    """The model files in a film's models/ folder (paths relative to the film)."""
    found = []
    base = os.path.join(root, "models")
    for d, _, names in os.walk(base):
        for f in sorted(names):
            if os.path.splitext(f)[1].lower() in FORMATS:
                found.append(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/"))
    return sorted(found)


# ---------------------------------------------------------------------- importing
def import_file(path):
    """Import a model file into the scene; returns the new objects."""
    import addon_utils
    ext = os.path.splitext(path)[1].lower()
    if ext not in FORMATS:
        raise ValueError(f"{path}: models are {', '.join(FORMATS)}")
    if not os.path.exists(path):
        raise ValueError(f"no model file at {path}")
    before = set(bpy.data.objects)
    acts = set(bpy.data.actions)
    if ext in (".glb", ".gltf"):
        addon_utils.enable("io_scene_gltf2", default_set=True)
        bpy.ops.import_scene.gltf(filepath=path, bone_heuristic="TEMPERANCE")   # bones point at their children
    elif ext == ".fbx":
        addon_utils.enable("io_scene_fbx", default_set=True)
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=True)
    else:
        bpy.ops.wm.obj_import(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:      # the model's own animations would fight dreamreel's
        if o.animation_data:
            o.animation_data.action = None
    for a in set(bpy.data.actions) - acts:
        bpy.data.actions.remove(a)
    return new


def keep_character(objs):
    """The skeleton and the meshes that make up the character; everything else imported goes."""
    arm = next((o for o in objs if o.type == "ARMATURE"), None)
    meshes = [o for o in objs if o.type == "MESH"]
    if arm is not None:
        rigged = [m for m in meshes if any(md.type == "ARMATURE" and md.object == arm for md in m.modifiers)
                  or m.parent is arm]
        meshes = rigged or meshes
    bpy.context.view_layer.update()
    keep = set(meshes) | ({arm} if arm else set())
    for o in keep:                # free them from imported parents, keeping where they are
        mw = o.matrix_world.copy()
        if o.parent is not None and o.parent not in keep:
            o.parent = None
            o.matrix_world = mw
    for o in objs:
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    return arm, meshes


def world_points(meshes, dense=0):
    """Points on the meshes in world space: the vertices, or `dense` points spread evenly over the
    surface (so low-poly models still have points everywhere)."""
    import random
    pts = []
    dg = bpy.context.evaluated_depsgraph_get()
    tris = []
    for m in meshes:
        ev = m.evaluated_get(dg)
        me = ev.to_mesh()
        mw = m.matrix_world
        if not dense:
            pts += [mw @ v.co for v in me.vertices]
        else:
            me.calc_loop_triangles()
            vs = [mw @ v.co for v in me.vertices]
            for lt in me.loop_triangles:
                a, b, c = (vs[i] for i in lt.vertices)
                tris.append((a, b, c, ((b - a).cross(c - a)).length / 2))
        ev.to_mesh_clear()
    if dense and tris:
        rng = random.Random(1)
        total = sum(t[3] for t in tris) or 1.0
        for a, b, c, area in tris:
            n = area / total * dense
            k = int(n) + (1 if rng.random() < n - int(n) else 0)
            pts.append((a + b + c) / 3)
            for _ in range(k):
                u, v = rng.random(), rng.random()
                if u + v > 1:
                    u, v = 1 - u, 1 - v
                pts.append(a + (b - a) * u + (c - a) * v)
    return pts


# ---------------------------------------------------------------------- finding the joints
def _chain_up(bone):
    out = []
    while bone is not None:
        out.append(bone)
        bone = bone.parent
    return out


def bone_roles(arm, height):
    """{role: bone name} for an armature: by joint names if they're recognisable, else by shape."""
    from . import motion
    names = [b.name for b in arm.data.bones]
    try:
        roles = motion.find_roles(names)
        if all(r in roles for r in ("l_elbow", "r_elbow", "l_knee", "r_knee")):
            return roles
    except ValueError:
        pass
    return _roles_by_shape(arm, height)


def _roles_by_shape(arm, height):
    """Roles from the skeleton's shape, using joint positions (bone heads) only: bone tails mean
    nothing in many exported rigs."""
    mw = arm.matrix_world
    bones = arm.data.bones
    head = {b.name: mw @ b.head_local for b in bones}
    leaves = [b for b in bones if not b.children]
    floor = min(p.z for p in head.values())
    low = [b for b in leaves if head[b.name].z - floor < 0.15 * height]

    def pick(cands, side, key):
        c = [b for b in cands if (head[b.name].x > 0) == (side > 0) and abs(head[b.name].x) > 0.01 * height]
        return max(c, key=key) if c else None
    l_foot = pick(low, 1, lambda b: -head[b.name].z)
    r_foot = pick(low, -1, lambda b: -head[b.name].z)
    if l_foot is None or r_foot is None:
        raise ValueError("can't find two legs in the model's skeleton")
    l_chain, r_chain = _chain_up(l_foot), _chain_up(r_foot)
    common = next(b for b in l_chain if b in r_chain)
    hips = common
    legs_l = l_chain[:l_chain.index(common)][::-1]      # from the hip down
    legs_r = r_chain[:r_chain.index(common)][::-1]
    rest = [b for b in leaves if b not in legs_l and b not in legs_r]
    top = max(rest, key=lambda b: head[b.name].z - 2 * abs(head[b.name].x))
    up_chain = _chain_up(top)
    reach = [b for b in rest if b not in up_chain and head[b.name].z > head[hips.name].z]
    l_hand = pick(reach, 1, lambda b: abs(head[b.name].x))
    r_hand = pick(reach, -1, lambda b: abs(head[b.name].x))
    if l_hand is None or r_hand is None:
        raise ValueError("can't find two arms in the model's skeleton")

    def limb(chain, fracs):
        """Bones along a limb at fractions of its length (from the shoulder or hip)."""
        pts = [head[b.name] for b in chain]
        d = [0.0]
        for a, b in zip(pts, pts[1:]):
            d.append(d[-1] + (b - a).length)
        total = d[-1] or 1.0
        return [chain[min(range(len(chain)), key=lambda k: abs(d[k] - f * total))] for f in fracs]

    roles = {"hips": hips.name}
    spine = up_chain[:up_chain.index(hips)][::-1] if hips in up_chain else up_chain[::-1]
    for side, hand, legs in ((1, l_hand, legs_l), (-1, r_hand, legs_r)):
        s = "l" if side > 0 else "r"
        arm_chain = _chain_up(hand)
        branch = next((b for b in arm_chain if b in spine), None)
        chain = arm_chain[:arm_chain.index(branch)][::-1] if branch else arm_chain[::-1]
        if len(chain) > 3 and (head[chain[1].name] - head[chain[0].name]).length < 0.1 * height:
            chain = chain[1:]                                       # a collar bone
        upper, elbow, wrist = limb(chain, (0.0, 0.5, 1.0))
        roles.update({f"{s}_arm": upper.name, f"{s}_elbow": elbow.name, f"{s}_wrist": wrist.name})
        if len(legs) > 3 and (head[legs[1].name] - head[legs[0].name]).length < 0.06 * height:
            legs = legs[1:]                                         # a short hip joint
        ankle = min(legs, key=lambda b: abs(head[b.name].z - floor - 0.06 * height))
        legs = legs[:legs.index(ankle) + 1]
        thigh, knee = limb(legs, (0.0, 0.5))
        roles.update({f"{s}_hip": thigh.name, f"{s}_knee": knee.name, f"{s}_ankle": ankle.name})
        if branch is not None:
            roles.setdefault("chest", branch.name)
    sh_z = max(head[roles["l_arm"]].z, head[roles["r_arm"]].z)
    neck = next((b for b in spine if head[b.name].z > sh_z + 0.02 * height), spine[-1] if spine else hips)
    roles["neck"] = neck.name
    roles["head"] = top.name
    roles.setdefault("chest", spine[-1].name if spine else hips.name)
    return roles


# ---------------------------------------------------------------------- automatic rigging
def silhouette_joints(pts, height):
    """Joint positions of a standing T/A-pose figure from its points (facing -Y, z up, feet at 0)."""
    H = height
    xs = [p.x for p in pts]
    cx = (max(xs) + min(xs)) / 2

    def slab(z0, z1):
        return [p for p in pts if z0 <= p.z < z1]
    # the crotch: going up from the knees, the first level where the legs join in the middle
    crotch = 0.45 * H
    for k in range(25, 62):
        z = k / 100 * H
        s = slab(z - 0.005 * H, z + 0.005 * H)
        if s and any(abs(p.x - cx) < 0.006 * H for p in s):
            crotch = z
            break
    hip_z = crotch + 0.04 * H
    feet = slab(0, 0.06 * H)
    lf = [p for p in feet if p.x > cx] or feet
    rf = [p for p in feet if p.x <= cx] or feet
    ank_l = Vector((sum(p.x for p in lf) / len(lf), sum(p.y for p in lf) / len(lf), 0.06 * H))
    ank_r = Vector((sum(p.x for p in rf) / len(rf), sum(p.y for p in rf) / len(rf), 0.06 * H))
    thighs = [p for p in slab(hip_z - 0.12 * H, hip_z - 0.06 * H) if abs(p.x - cx) < 0.14 * H]
    hx = (sorted(abs(p.x - cx) for p in thighs)[len(thighs) // 2] if thighs else 0.08 * H)
    # torso width just above the hips (arms in an A pose hang further out than this)
    waist = [abs(p.x - cx) for p in slab(hip_z + 0.06 * H, hip_z + 0.12 * H) if abs(p.x - cx) < 0.22 * H]
    half = sorted(waist)[int(len(waist) * 0.85)] if waist else 0.12 * H
    # arms: the points furthest out on each side
    far_l = max(pts, key=lambda p: p.x)
    far_r = min(pts, key=lambda p: p.x)
    # shoulders: the top of the torso, where the neck narrows
    widths = []
    for k in range(int(hip_z / H * 100) + 10, 98):
        z = k / 100 * H
        s = [abs(p.x - cx) for p in slab(z - 0.01 * H, z + 0.01 * H) if abs(p.x - cx) < half * 1.6]
        if s:
            widths.append((z, max(s)))
    neck_z = max(widths, key=lambda w: w[0])[0] * 0.86 if widths else 0.85 * H
    if widths:
        upper_w = [w for w in widths if w[0] > hip_z + 0.2 * H]
        if upper_w:
            neck_z = min(upper_w, key=lambda w: w[1])[0]
    shoulder_z = max(hip_z + 0.15 * H, neck_z - 0.06 * H)
    # the shoulder joints sit inside the top of the torso at that height (wider than the waist)
    top_w = [abs(p.x - cx) for p in slab(shoulder_z - 0.01 * H, shoulder_z + 0.01 * H)]
    sh_x = max(half * 0.95, (max(top_w) if top_w else 0) * 0.7)
    sh_x = min(sh_x, 0.14 * H)
    sh_l = Vector((cx + sh_x, 0, shoulder_z))
    sh_r = Vector((cx - sh_x, 0, shoulder_z))
    wr_l = sh_l.lerp(Vector((far_l.x, far_l.y, far_l.z)), 0.86)
    wr_r = sh_r.lerp(Vector((far_r.x, far_r.y, far_r.z)), 0.86)
    top = max(p.z for p in pts)
    j = {
        "hips": Vector((cx, 0, hip_z)), "chest": Vector((cx, 0, (hip_z + shoulder_z) / 2 + 0.05 * H)),
        "neck": Vector((cx, 0, neck_z)), "head": Vector((cx, 0, top)),
        "l_hip": Vector((cx + hx, 0, hip_z - 0.03 * H)), "r_hip": Vector((cx - hx, 0, hip_z - 0.03 * H)),
        "l_ankle": ank_l, "r_ankle": ank_r,
        "l_arm": sh_l, "r_arm": sh_r, "l_wrist": wr_l, "r_wrist": wr_r,
    }
    for s in ("l", "r"):
        j[f"{s}_knee"] = j[f"{s}_hip"].lerp(j[f"{s}_ankle"], 0.5) + Vector((0, -0.01 * H, 0))
        j[f"{s}_elbow"] = j[f"{s}_arm"].lerp(j[f"{s}_wrist"], 0.5) + Vector((0, 0.01 * H, 0))
        j[f"{s}_toe"] = j[f"{s}_ankle"] + Vector((0, -0.08 * H, -0.04 * H))
        j[f"{s}_hand"] = j[f"{s}_wrist"] + (j[f"{s}_wrist"] - j[f"{s}_elbow"]).normalized() * 0.07 * H
    return j


def _torso_half(pts, cx, z0, z1, H):
    """The widest the trunk (centred at x = cx) gets between two heights, not counting arms held away."""
    widest = 0.0
    steps = 5
    for k in range(steps):
        z = z0 + (z1 - z0) * k / (steps - 1)
        for sign in (1, -1):
            xs = sorted(sign * (p.x - cx) for p in pts if abs(p.z - z) < 0.01 * H and sign * (p.x - cx) >= 0)
            edge = 0.0
            for x in xs:              # out from the middle until the first gap
                if x - edge > 0.03 * H:
                    break
                edge = x
            widest = max(widest, edge)
    return widest


BONES = [  # name, head joint, tail joint, parent
    ("hips", "hips", "chest", None), ("chest", "chest", "neck", "hips"), ("neck", "neck", "head", "chest"),
] + [b for s in ("l", "r") for b in (
    (f"{s}_arm", f"{s}_arm", f"{s}_elbow", "chest"), (f"{s}_elbow", f"{s}_elbow", f"{s}_wrist", f"{s}_arm"),
    (f"{s}_wrist", f"{s}_wrist", f"{s}_hand", f"{s}_elbow"),
    (f"{s}_hip", f"{s}_hip", f"{s}_knee", "hips"), (f"{s}_knee", f"{s}_knee", f"{s}_ankle", f"{s}_hip"),
    (f"{s}_ankle", f"{s}_ankle", f"{s}_toe", f"{s}_knee"))]


def auto_rig(meshes, height, joints=None):
    """Build a skeleton for an unrigged figure and weight its skin to the nearest bones."""
    pts = world_points(meshes, dense=60000)
    j = joints or silhouette_joints(pts, height)
    data = bpy.data.armatures.new("autorig")
    arm = bpy.data.objects.new("autorig", data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for name, a, b, parent in BONES:
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = j[a], j[b]
        if (bone.tail - bone.head).length < 1e-4:
            bone.tail = bone.head + Vector((0, 0, 0.01))
        if parent:
            bone.parent = eb[parent]
        eb[name] = bone
    for s in ("l", "r"):          # bend directions for IK: elbows back, knees forward
        eb[f"{s}_elbow"].roll = 0.0
    bpy.ops.object.mode_set(mode="OBJECT")
    segs = [(name, j[a], j[b]) for name, a, b, _ in BONES]
    for m in meshes:
        _weight(m, segs)
        mod = m.modifiers.new("autorig", "ARMATURE")
        mod.object = arm
        mw = m.matrix_world.copy()
        m.parent = arm
        m.matrix_world = mw
    return arm


def _weight(mesh, segs):
    """Each vertex follows its nearest bones (smoothly between the two nearest)."""
    for name, _, _ in segs:
        if name not in mesh.vertex_groups:
            mesh.vertex_groups.new(name=name)
    mw = mesh.matrix_world

    def dist(p, a, b):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(1e-9, ab.length_squared)))
        return (p - (a + ab * t)).length
    for v in mesh.data.vertices:
        p = mw @ v.co
        ds = sorted((dist(p, a, b), name) for name, a, b in segs)
        d0, n0 = ds[0]
        d1, n1 = ds[1]
        w0 = 1.0 / max(1e-4, d0) ** 4
        w1 = 1.0 / max(1e-4, d1) ** 4 if d1 < d0 * 1.6 else 0.0
        tot = w0 + w1
        mesh.vertex_groups[n0].add([v.index], w0 / tot, "REPLACE")
        if w1:
            mesh.vertex_groups[n1].add([v.index], w1 / tot, "REPLACE")


# ---------------------------------------------------------------------- the character
FACE_KEYS = {
    "blink": ("eyeblink", "blink", "eyesclosed", "eyeclose", "fcleyeclose", "eyesclose"),
    "smile": ("mouthsmile", "smile", "joy", "happy", "fclalljoy"),
    "frown": ("mouthfrown", "frown", "sorrow", "sad", "fclallsorrow"),
    "open": ("jawopen", "mouthopen", "visemeaa", "fclmtha", "aa", "a"),
    "brows_up": ("browinnerup", "browsup", "browup", "surprised", "fclallsurprised"),
    "brows_down": ("browdown", "angry", "fclallangry"),
}


class ModelCharacter(Character):
    """A character from a 3D model file, rigged or not (see models.py)."""
    name = "model"
    label = "Your own model"
    description = "A 3D model you bring (glTF, FBX, OBJ), rigged or rigged automatically"
    drawing = "model"
    params = [
        Param("name", "text", label="Name"),
        Param("file", "model", required=True, label="Model file (in models/)"),
        Param("height", "number", default=1.0, min=0.3, max=3.0, step=0.05, label="Height (m)"),
        Param("turn", "number", default=0, min=-180, max=180, step=90, label="Turn (degrees)"),
        Param("voice", "voice"),
    ]
    default_capabilities = ("walk", "arms", "swing_legs", "face")

    def validate(self):
        f = self.spec.get("file")
        if not f:
            raise ValueError(f"{self.name}: a model character needs file = \"models/...\"")

    def _path(self):
        f = self.spec["file"]
        if os.path.isabs(f) or os.path.exists(f):
            return f
        from . import project
        p = project.current()
        if p is not None:
            for cand in (os.path.join(p.root, f), os.path.join(p.root, "models", f)):
                if os.path.exists(cand):
                    return cand
        return f

    def proportions(self):
        self.H = float(self.spec.get("height") or 1.0)

    def build(self):
        n, H = self.name, self.H
        objs = import_file(self._path())
        arm, meshes = keep_character(objs)
        if not meshes:
            raise ValueError(f"{self.name}: no mesh in {self.spec['file']}")
        # stand it up: feet on the ground, centred, facing the front, at the height asked for
        holder = shapes.empty(f"{n}.model")
        bpy.context.view_layer.update()
        for o in [arm] + meshes if arm else meshes:
            if o.parent is None or o.parent not in meshes + [arm]:
                mw = o.matrix_world.copy()
                o.parent = holder
                o.matrix_world = mw
        pts = world_points(meshes)
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        k = H / max(1e-6, hi.z - lo.z)
        holder.matrix_world = (Matrix.Rotation(math.radians(float(self.spec.get("turn") or 0)), 4, "Z")
                               @ Matrix.Scale(k, 4)
                               @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
        bpy.context.view_layer.update()
        if arm is None:
            arm = auto_rig(meshes, H)
            arm.parent = holder
            arm.matrix_parent_inverse = holder.matrix_world.inverted()
            bpy.context.view_layer.update()
            roles = {r: r for r in ("hips", "chest", "neck") + tuple(f"{s}_{p}" for s in "lr" for p in
                                                                         ("arm", "elbow", "wrist", "hip", "knee", "ankle"))}
            roles["head"] = "neck"
        else:
            roles = bone_roles(arm, H)
        self.rig, self.roles, self.meshes, self.holder = arm, roles, meshes, holder
        self._drive(arm, roles)
        self._face(meshes)

    def _joint(self, role, tail=False):
        b = self.rig.data.bones[self.roles[role]]
        return self.rig.matrix_world @ (b.tail_local if tail else b.head_local)

    def _drive(self, arm, roles):
        """dreamreel's pivots, and the skeleton following them."""
        n, H = self.name, self.H
        J = self._joint
        hip_z = (J("l_hip").z + J("r_hip").z) / 2
        self.hip_z = hip_z
        neck = J("neck")
        top = max(max(p.z for p in world_points(self.meshes)), neck.z + 0.05 * H)
        self.head_r = self.hr = max(0.04 * H, (top - neck.z) / 2)
        self.top_z = self.neck_z = neck.z - hip_z
        self.head_center = self.hc = Vector((0, 0, self.hr))
        self.body_r = max(abs(J("l_arm").x), abs(J("r_arm").x))
        self.shoulder_z = J("l_arm").z - hip_z
        self.root = shapes.empty(n)
        self.root.empty_display_size = 0.3
        self.hips = shapes.empty(f"{n}.hips", self.root, (0, 0, hip_z))
        self.body = shapes.empty(f"{n}.body", self.hips)
        self.neck = shapes.empty(f"{n}.neck", self.body, (0, 0, neck.z - hip_z))
        # the model rides on the hips (so it bobs and jumps with them)
        self.holder.parent = self.hips
        self.holder.matrix_parent_inverse = Matrix.Translation((0, 0, -hip_z))
        pb = arm.pose.bones
        hips_bone = pb[roles["hips"]]
        spine = []
        b = pb[roles["neck"]].parent
        while b is not None and b != hips_bone:
            spine.append(b)
            b = b.parent
        for bone in spine[::-1] or [hips_bone]:
            c = bone.constraints.new("COPY_ROTATION")
            c.target, c.mix_mode = self.body, "ADD"
            c.owner_space, c.target_space = "POSE", "LOCAL"
            c.influence = 1.0 / max(1, len(spine))
        c = pb[roles["neck"]].constraints.new("COPY_ROTATION")
        c.target, c.mix_mode, c.owner_space, c.target_space = self.neck, "ADD", "POSE", "LOCAL"
        # limbs: a pivot at each shoulder and hip; the hand or foot reaches for a target the pivot swings
        self.arms, self.legs, self.hands, self.iks = {}, {}, {}, []
        pts = world_points(self.meshes, dense=20000)
        cx = (J("l_arm").x + J("r_arm").x) / 2
        for side, s in ((1, "l"), (-1, "r")):
            sh = J(f"{s}_arm")
            reach = (J(f"{s}_elbow") - sh).length + (J(f"{s}_wrist") - J(f"{s}_elbow")).length
            piv = shapes.empty(f"{n}.arm.{s.upper()}", self.body, (sh.x, sh.y, sh.z - hip_z))
            # hanging arms clear the body: out to the side by as much as the torso is wider than the shoulders
            out = max(0.0, _torso_half(pts, cx, sh.z - reach, sh.z - 0.3 * reach, H) + 0.045 * H - abs(sh.x - cx))
            out = min(out, 0.5 * reach)
            tgt = shapes.empty(f"{n}.hand.target.{s}", piv,
                               (side * out, 0, -math.sqrt(max(0.0, (reach * 0.97) ** 2 - out ** 2))))
            pole = shapes.empty(f"{n}.elbow.pole.{s}", piv, (side * 0.05 * H, 0.6 * reach, -reach * 0.5))
            self._ik(pb[roles[f"{s}_elbow"]], pb[roles[f"{s}_arm"]], tgt, pole)
            hand = shapes.empty(f"{n}.hand.{s}")
            hand.parent = arm
            hand.parent_type = "BONE"
            hand.parent_bone = roles[f"{s}_wrist"]
            # in the palm: a little past the wrist, along the forearm (bone tails can point anywhere)
            wb = arm.data.bones[roles[f"{s}_wrist"]]
            fore = wb.head_local - arm.data.bones[roles[f"{s}_elbow"]].head_local
            palm = wb.head_local + fore.normalized() * min(0.3 * fore.length, 0.05 * H / arm.matrix_world.to_scale().x)
            hand.location = wb.matrix_local.inverted() @ palm - Vector((0, wb.length, 0))
            self.arms[side], self.hands[side] = piv, hand
            hp = J(f"{s}_hip")
            ank = J(f"{s}_ankle")
            leg_len = (J(f"{s}_knee") - hp).length + (ank - J(f"{s}_knee")).length
            lp = shapes.empty(f"{n}.leg.{s.upper()}", self.hips, (hp.x, hp.y, hp.z - hip_z))
            ft = shapes.empty(f"{n}.foot.target.{s}", lp, (ank.x - hp.x, ank.y - hp.y, -min(leg_len * 0.98, hp.z - ank.z)))
            kp = shapes.empty(f"{n}.knee.pole.{s}", lp, (0, -0.6 * leg_len, -leg_len * 0.5))
            self._ik(pb[roles[f"{s}_knee"]], pb[roles[f"{s}_hip"]], ft, kp)
            self.legs[side] = lp
        self._calibrate()
        bpy.context.view_layer.update()
        # rest directions for motion capture (arms hang down, legs straight down)
        from . import handling
        self._arm_rest = None
        handling.arm_rest(self)
        self._mrest = (self._arm_rest, {s: (Vector((0, 0, -1)), 1.0) for s in self.legs}, hip_z)

    def _ik(self, lower, upper, target, pole):
        chain = 1
        b = lower
        while b is not None and b != upper:
            chain += 1
            b = b.parent
        ik = lower.constraints.new("IK")
        ik.target, ik.pole_target = target, pole
        ik.chain_count = chain if b is not None else 2
        ik.use_stretch = False
        self.iks.append((ik, lower))

    def _calibrate(self):
        """Pick each IK's pole angle so the elbow or knee bends the way it should."""
        for ik, lower in self.iks:
            best = (0.0, 1e9)
            pole = ik.pole_target.matrix_world.translation
            for angle in (-90, 90, 0, 180):
                ik.pole_angle = math.radians(angle)
                bpy.context.view_layer.update()
                mid = self.rig.matrix_world @ lower.head
                hi = self.rig.matrix_world @ lower.parent.head if lower.parent else mid
                lo = self.rig.matrix_world @ lower.tail
                line = lo - hi
                foot = hi + line * max(0.0, min(1.0, (mid - hi).dot(line) / max(1e-9, line.length_squared)))
                bend = mid - foot
                want = pole - foot
                err = -bend.normalized().dot(want.normalized()) if bend.length > 1e-5 and want.length > 1e-5 else 0.0
                if err < best[1]:
                    best = (angle, err)
            ik.pole_angle = math.radians(best[0])

    def _face(self, meshes):
        """dreamreel's face controls (eyes, brows, mouth) as invisible stand-ins, wired to the model's
        own facial shape keys if it has any."""
        n = self.name
        self.eyes = [shapes.empty(f"{n}.eye", self.neck) for _ in (1, -1)]
        self.brows = {s: shapes.empty(f"{n}.brow", self.neck) for s in (1, -1)}
        self.mouth = shapes.empty(f"{n}.mouthpivot", self.neck)
        m = shapes.plane(f"{n}.mouthkeys", 0.001, 0.001, None, self.neck)
        m.hide_render = True
        m.hide_viewport = True
        m.shape_key_add(name="Basis")
        m.shape_key_add(name="smile")
        m.shape_key_add(name="frown")
        self.mouth_mesh = m
        self.face_keys = {}
        for mesh in meshes:
            keys_ = mesh.data.shape_keys
            if keys_ is None:
                continue
            for kb in keys_.key_blocks[1:]:
                norm = "".join(ch for ch in kb.name.lower() if ch.isalnum())
                for role, cands in FACE_KEYS.items():
                    if any(norm == c or (len(c) > 2 and c in norm) for c in cands):
                        self.face_keys.setdefault(role, []).append(kb)
        drive = {
            "blink": (self.eyes[0], "scale", 2, "max(0, min(1, 1 - v))"),
            "open": (self.mouth, "scale", 2, "max(0, min(1, (v - 1) / 2.2))"),
            "smile": (m.data.shape_keys, 'key_blocks["smile"].value', None, "v"),
            "frown": (m.data.shape_keys, 'key_blocks["frown"].value', None, "v"),
            "brows_up": (self.brows[1], "location", 2, "max(0, min(1, v * 40))"),
            "brows_down": (self.brows[1], "location", 2, "max(0, min(1, -v * 40))"),
        }
        for role, kbs in self.face_keys.items():
            src, path, index, expr = drive[role]
            for kb in kbs:
                fc = kb.driver_add("value")
                d = fc.driver
                d.type = "SCRIPTED"
                var = d.variables.new()
                var.name = "v"
                var.type = "SINGLE_PROP"
                var.targets[0].id_type = "KEY" if path.startswith("key_blocks") else "OBJECT"
                var.targets[0].id = src
                var.targets[0].data_path = f"{path}[{index}]" if index is not None else path
                d.expression = expr

    # the toy's build steps don't apply
    def build_rig(self):
        pass
