"""The motion library: motion-capture clips played by any dreamreel character.

Put clips in the film's `motions/` folder (BVH files; FBX and glTF too, read with Blender's importers).
dreamreel can't ship third-party motion capture, so the library is what you add: the CMU Graphics Lab
Motion Capture Database offers BVH files, Mixamo offers FBX (check each source's licence). Then:

    [[beats]]
    who = "mia"
    do = "perform"
    motion = "cartwheel"       # the file name, or a name from motions/library.toml
    speed = 1.0
    mirror = false             # left becomes right

Clips are *retargeted*: dreamreel finds the hips, spine, head, shoulders, elbows, wrists, hips, knees
and ankles in the clip (whatever the source names them: CMU, Mixamo, SMPL...), and turns their
movement into the character's own pose: arm and leg directions, lean, head, hip height and travel,
scaled to the character's size. Toy figures and creatures with two legs and arms can perform clips, and
so can people from the 3D packs, on their own rigs (actors.ClipActor.perform).

Walking uses the library too: if there are clips tagged `walk` or `run`, walk_to picks the one closest
to the speed asked for, finds a clean loop in it (two moments with the same pose a stride or two apart)
and plays it along the path. This is a simple form of motion matching (Clavet and Buttner, Ubisoft,
2015): the clip is chosen to fit the moment.

    # motions/library.toml (optional)
    [cartwheel]
    file = "49_07.bvh"
    start = 1.0                # seconds
    end = 4.5
    tags = ["acrobatics"]
"""
import math
import os
import re
import tomllib

from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------------- reading BVH
Y_UP_TO_Z_UP = Matrix.Rotation(math.radians(90), 4, "X")


class _Joint:
    def __init__(self, name, parent):
        self.name, self.parent = name, parent
        self.offset = Vector()
        self.channels = []
        self.children = []
        self.index = 0          # first channel in a frame row


def read_bvh(path):
    """(joints in order, frame time, frames as lists of floats)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        tokens = f.read().split()
    i = 0
    joints, stack = [], []
    current = None
    chan = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("ROOT", "JOINT"):
            current = _Joint(tokens[i + 1], stack[-1] if stack else None)
            if current.parent:
                current.parent.children.append(current)
            joints.append(current)
            i += 2
        elif tok == "End":
            current = _Joint(None, stack[-1])    # end site: an offset only
            i += 2
        elif tok == "{":
            stack.append(current)
            i += 1
        elif tok == "}":
            stack.pop()
            i += 1
        elif tok == "OFFSET":
            current.offset = Vector((float(tokens[i + 1]), float(tokens[i + 2]), float(tokens[i + 3])))
            i += 4
        elif tok == "CHANNELS":
            n = int(tokens[i + 1])
            current.channels = tokens[i + 2:i + 2 + n]
            current.index = chan
            chan += n
            i += 2 + n
        elif tok == "MOTION":
            break
        else:
            i += 1
    n_frames = int(tokens[tokens.index("Frames:", i) + 1])
    dt = float(tokens[tokens.index("Time:", i) + 1])
    j = tokens.index("Time:", i) + 2
    values = [float(v) for v in tokens[j:j + n_frames * chan]]
    frames = [values[k * chan:(k + 1) * chan] for k in range(n_frames)]
    return joints, dt, frames


def _local(joint, row):
    loc = joint.offset.copy()
    rot = Matrix.Identity(4)
    for k, name in enumerate(joint.channels):
        v = row[joint.index + k]
        axis = name[0].upper()
        if name.endswith("position"):
            loc["XYZ".index(axis)] = v if joint.parent is None else loc["XYZ".index(axis)] + v
        else:
            rot = rot @ Matrix.Rotation(math.radians(v), 4, axis)
    return Matrix.Translation(loc) @ rot


def bvh_positions(path):
    """World positions (z up) of every joint in every frame: ({name: [Vector per frame]}, fps)."""
    joints, dt, frames = read_bvh(path)
    out = {j.name: [] for j in joints}
    for row in frames:
        world = {}
        for j in joints:
            m = _local(j, row)
            world[j] = (world[j.parent] @ m) if j.parent is not None else m
            out[j.name].append((Y_UP_TO_Z_UP @ world[j]).translation.copy())
    return out, 1.0 / dt


# ---------------------------------------------------------------------- reading ASF/AMC (the CMU database's own format)
def _asf_rot(angles, order="XYZ"):
    m = Matrix.Identity(3)
    for ax, a in zip(order, angles):      # rotations applied in order: the first one first
        m = Matrix.Rotation(math.radians(a), 3, ax) @ m
    return m


def read_asf(path):
    """A skeleton: {bone: dict(direction, length, axis matrix, dof, parent)}, root order, length unit."""
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = [l.strip() for l in f]
    bones, section, cur, unit = {}, None, None, 1.0
    hierarchy, root_order = [], ["TX", "TY", "TZ", "RX", "RY", "RZ"]
    for l in lines:
        if not l or l.startswith("#"):
            continue
        if l.startswith(":"):
            section = l.split()[0][1:]
            continue
        w = l.split()
        if section == "units" and w[0] == "length":
            unit = float(w[1])
        elif section == "root" and w[0] == "order":
            root_order = [x.upper() for x in w[1:]]
        elif section == "bonedata":
            if w[0] == "begin":
                cur = {"dof": [], "direction": Vector((0, 0, 0)), "length": 0.0, "axis": Matrix.Identity(3)}
            elif w[0] == "end":
                bones[cur["name"]] = cur
            elif w[0] == "name":
                cur["name"] = w[1]
            elif w[0] == "direction":
                cur["direction"] = Vector(tuple(float(x) for x in w[1:4]))
            elif w[0] == "length":
                cur["length"] = float(w[1])
            elif w[0] == "axis":
                cur["axis"] = _asf_rot([float(x) for x in w[1:4]], w[4].upper() if len(w) > 4 else "XYZ")
            elif w[0] == "dof":
                cur["dof"] = [x.upper() for x in w[1:]]
        elif section == "hierarchy" and w[0] not in ("begin", "end"):
            hierarchy.append(w)
    for w in hierarchy:
        for child in w[1:]:
            if child in bones:
                bones[child]["parent"] = w[0]
    return bones, root_order, unit


def read_amc(path, bones, root_order):
    """Frames of {bone: [values]} (root: its order's values)."""
    frames, cur = [], None
    with open(path, encoding="utf-8", errors="replace") as f:
        for l in f:
            l = l.strip()
            if not l or l.startswith(("#", ":")):
                continue
            w = l.split()
            if len(w) == 1 and w[0].isdigit():
                cur = {}
                frames.append(cur)
            elif cur is not None:
                cur[w[0]] = [float(x) for x in w[1:]]
    return frames


def asf_amc_positions(asf, amc, fps=120.0):
    """World positions (metres, z up) of the start of every bone, and the root, in every frame."""
    bones, root_order, unit = read_asf(asf)
    frames = read_amc(amc, bones, root_order)
    scale = 0.0254 / unit                               # ASF lengths are inches times `unit`
    order = []                                          # parents before children
    pending = list(bones)
    while pending:
        for b in list(pending):
            par = bones[b].get("parent", "root")
            if par == "root" or par in order:
                order.append(b)
                pending.remove(b)
    out = {"root": []}
    out.update({b: [] for b in bones})
    for fr in frames:
        rv = fr.get("root", [0] * 6)
        vals = dict(zip(root_order, rv))
        pos = Vector((vals.get("TX", 0), vals.get("TY", 0), vals.get("TZ", 0)))
        rot = _asf_rot([vals.get("RX", 0), vals.get("RY", 0), vals.get("RZ", 0)], "XYZ")
        world_rot, start = {"root": rot}, {"root": pos}
        for b in order:
            bd = bones[b]
            par = bd.get("parent", "root")
            angles = dict(zip(bd["dof"], fr.get(b, [])))
            m = _asf_rot([angles.get("RX", 0), angles.get("RY", 0), angles.get("RZ", 0)], "XYZ")
            C = bd["axis"]
            R = world_rot[par] @ C @ m @ C.inverted()
            world_rot[b] = R
            s = start[par] if par == "root" else start[par] + world_rot[par] @ (bones[par]["direction"] * bones[par]["length"])
            start[b] = s
        for b, s in start.items():
            out[b].append((Y_UP_TO_Z_UP.to_3x3() @ s) * scale)
    return out, fps


ASF_ROLES = {"hips": "root", "chest": "thorax", "neck": "lowerneck", "head": "head",
             "l_arm": "lhumerus", "l_elbow": "lradius", "l_wrist": "lwrist", "l_hip": "lfemur", "l_knee": "ltibia",
             "l_ankle": "lfoot", "r_arm": "rhumerus", "r_elbow": "rradius", "r_wrist": "rwrist", "r_hip": "rfemur",
             "r_knee": "rtibia", "r_ankle": "rfoot"}


# ---------------------------------------------------------------------- joint roles
def _norm(name):
    n = re.sub(r"^(mixamorig\d*|bip0?1|def|characters?\d*)[:_ ]*", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", n)


ROLES = {
    "hips": ["hips", "pelvis", "hip", "root"],
    "chest": ["upperchest", "chest", "spine3", "spine2", "spine1", "spine"],
    "neck": ["neck", "neck1", "lowerneck", "upperneck"],
    "head": ["head"],
}
for _s, _l in (("l", "left"), ("r", "right")):
    ROLES.update({
        f"{_s}_arm": [f"{_l}arm", f"{_l}upperarm", f"{_s}upperarm", f"upperarm{_s}", f"{_l}shoulder"],
        f"{_s}_elbow": [f"{_l}forearm", f"{_l}lowerarm", f"{_s}forearm", f"lowerarm{_s}", f"{_l}elbow"],
        f"{_s}_wrist": [f"{_l}hand", f"{_s}hand", f"hand{_s}", f"{_l}wrist"],
        f"{_s}_hip": [f"{_l}upleg", f"{_l}upperleg", f"{_s}thigh", f"thigh{_s}", f"{_l}hip"],
        f"{_s}_knee": [f"{_l}leg", f"{_l}lowerleg", f"{_s}calf", f"calf{_s}", f"{_l}knee"],
        f"{_s}_ankle": [f"{_l}foot", f"{_s}foot", f"foot{_s}", f"{_l}ankle"],
    })


def find_roles(names):
    """Which joint plays which role: {role: joint name}."""
    norm = {_norm(n): n for n in names if n}
    found = {}
    for role, cands in ROLES.items():
        for c in cands:
            if c in norm and norm[c] not in found.values():
                found[role] = norm[c]
                break
    missing = [r for r in ("hips", "l_arm", "l_wrist", "r_arm", "r_wrist", "l_hip", "l_ankle", "r_hip", "r_ankle")
               if r not in found]
    if missing:
        raise ValueError(f"can't find {', '.join(missing)} in the clip's skeleton (joints: {', '.join(sorted(norm.values())[:30])})")
    found.setdefault("chest", found.get("neck", found["hips"]))
    found.setdefault("neck", found["chest"])
    found.setdefault("head", found["neck"])
    return found


# ---------------------------------------------------------------------- clips
class Clip:
    """A motion: the world positions of each role over time, measured in source units, z up."""

    def __init__(self, name, roles, fps, tags=(), source=None):
        self.name, self.fps, self.tags, self.source = name, fps, set(tags), source
        self.roles = roles                      # {role: [Vector per frame]}
        self.n = len(roles["hips"])
        # how tall the source is: hip height standing (the median over the clip, robust to jumps)
        heights = sorted(((roles["l_hip"][i].z + roles["r_hip"][i].z) / 2 - min(roles["l_ankle"][i].z,
                                                                               roles["r_ankle"][i].z))
                         for i in range(self.n))
        self.hip_height = max(1e-6, heights[len(heights) // 2])
        self.floor = min(min(roles["l_ankle"][i].z, roles["r_ankle"][i].z) for i in range(self.n))
        # how long the legs are: the same whatever the pose (a clip spent mostly on the floor has a
        # tiny standing hip height, but not short legs)
        legs = sorted((roles["l_hip"][i] - roles["l_knee"][i]).length + (roles["l_knee"][i] - roles["l_ankle"][i]).length
                      for i in range(0, self.n, max(1, self.n // 50)))
        self.leg_length = max(1e-6, legs[len(legs) // 2])
        self.loop = None                        # (first, last) frame of a clean cycle, for walks

    @property
    def length(self):
        return (self.n - 1) / self.fps

    def trim(self, start=None, end=None):
        a = int(round((start or 0.0) * self.fps))
        b = int(round(end * self.fps)) + 1 if end is not None else self.n
        self.roles = {r: v[a:b] for r, v in self.roles.items()}
        self.n = len(self.roles["hips"])
        return self

    def at(self, t):
        """{role: Vector} at t seconds (interpolated)."""
        f = max(0.0, min(self.n - 1.0, t * self.fps))
        i = int(f)
        j = min(self.n - 1, i + 1)
        u = f - i
        return {r: v[i].lerp(v[j], u) for r, v in self.roles.items()}

    # facing: the hips' right-to-left line turned to point forward
    def heading(self, pose):
        right = pose["r_hip"] - pose["l_hip"]
        right.z = 0
        if right.length < 1e-6:
            return 0.0
        fwd = Vector((0, 0, 1)).cross(right.normalized())
        return math.atan2(fwd.x, -fwd.y)

    def speed(self):
        """Average travel speed in hip-heights per second."""
        a, b = self.roles["hips"][0], self.roles["hips"][-1]
        return (Vector((b.x - a.x, b.y - a.y)).length / self.hip_height) / max(1e-6, self.length)

    def find_loop(self, min_s=0.7, max_s=2.6):
        """Two frames with the same pose (feet and arms relative to the hips) a stride or two apart."""
        if self.loop is not None:
            return self.loop

        def feature(i):
            p = {r: v[i] for r, v in self.roles.items()}
            h = self.heading(p)
            R = Matrix.Rotation(-h, 3, "Z")
            hips = p["hips"]
            return [R @ (p[r] - hips) / self.hip_height for r in ("l_ankle", "r_ankle", "l_wrist", "r_wrist")]

        step = max(1, int(self.fps / 30))
        feats = {i: feature(i) for i in range(0, self.n, step)}
        best = (1e9, 0, self.n - 1)
        lo, hi = int(min_s * self.fps), int(max_s * self.fps)
        for i in range(0, max(1, self.n // 2), step):
            for j in range(i + lo, min(self.n, i + hi), step):
                if j not in feats:
                    continue
                d = sum((a - b).length for a, b in zip(feats[i], feats[j]))
                if d < best[0]:
                    best = (d, i, j)
        self.loop = (best[1], best[2])
        return self.loop


def load(path, name=None, tags=None):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bvh":
        positions, fps = bvh_positions(path)
    elif ext == ".amc":                                   # the CMU database: the skeleton is the subject's .asf
        asf = os.path.join(os.path.dirname(path), os.path.basename(path).split("_")[0] + ".asf")
        positions, fps = asf_amc_positions(asf, path)
        stem = os.path.splitext(os.path.basename(path))[0]
        return Clip(name or stem, {r: positions[j] for r, j in ASF_ROLES.items()}, fps, tags or set(), source=path)
    elif ext in (".fbx", ".glb", ".gltf"):
        positions, fps = _import_with_blender(path)
    else:
        raise ValueError(f"{path}: motion files are .bvh, .fbx, .glb or .gltf")
    roles = find_roles(list(positions))
    stem = os.path.splitext(os.path.basename(path))[0]
    if tags is None:
        words = set(re.split(r"[^a-z]+", stem.lower()))
        tags = {w for w in ("walk", "run", "jog", "jump", "dance", "sneak", "skip") if w in words or w + "s" in words}
    return Clip(name or stem, {r: positions[j] for r, j in roles.items()}, fps, tags, source=path)


def _import_with_blender(path):
    """Read FBX/glTF with Blender's importer, sample the armature's bones, then remove what it made."""
    import addon_utils
    import bpy
    before = set(bpy.data.objects)
    actions_before = set(bpy.data.actions)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".fbx":
        addon_utils.enable("io_scene_fbx", default_set=True)
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=True)
    else:
        addon_utils.enable("io_scene_gltf2", default_set=True)
        bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next((o for o in new if o.type == "ARMATURE"), None)
    try:
        if arm is None or not arm.animation_data or not arm.animation_data.action:
            raise ValueError(f"{path}: no animated skeleton found")
        a, b = arm.animation_data.action.frame_range
        sc = bpy.context.scene
        positions = {pb.name: [] for pb in arm.pose.bones}
        for f in range(int(a), int(b) + 1):
            sc.frame_set(f)
            for pb in arm.pose.bones:
                positions[pb.name].append((arm.matrix_world @ pb.head).copy())
        fps = sc.render.fps / sc.render.fps_base
    finally:
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        for act in set(bpy.data.actions) - actions_before:
            bpy.data.actions.remove(act)
    return positions, fps


# ---------------------------------------------------------------------- the library
class Library:
    """The film's motions/ folder (and library.toml), loaded on demand."""

    def __init__(self, root):
        self.root = root
        self.dir = os.path.join(root, "motions") if root else None
        self._clips = {}
        self.entries = self._scan()

    def _scan(self):
        entries = {}
        if not self.dir or not os.path.isdir(self.dir):
            return entries
        for f in sorted(os.listdir(self.dir)):
            if f.lower().endswith((".bvh", ".fbx", ".glb", ".gltf")):
                entries[os.path.splitext(f)[0]] = {"file": f}
        toml = os.path.join(self.dir, "library.toml")
        if os.path.exists(toml):
            with open(toml, "rb") as fh:
                for name, e in tomllib.load(fh).items():
                    entries[name] = dict(e)
        return entries

    def names(self):
        return sorted(self.entries)

    def get(self, name):
        if name in self._clips:
            return self._clips[name]
        e = self.entries.get(name)
        if e is None:
            raise ValueError(f"no motion called {name!r}. Motions: {', '.join(self.names()) or 'none yet'} "
                             f"(put .bvh/.fbx files in motions/)")
        clip = load(os.path.join(self.dir, e["file"]), name=name, tags=e.get("tags"))
        if e.get("start") is not None or e.get("end") is not None:
            clip.trim(e.get("start"), e.get("end"))
        self._clips[name] = clip
        return clip

    def tagged(self, tag):
        out = []
        for name, e in self.entries.items():
            tags = set(e.get("tags") or [])
            if not tags:
                tags = self.get(name).tags
            if tag in tags:
                out.append(self.get(name))
        return out


def library(scene):
    lib = getattr(scene, "_motions", None)
    if lib is None:
        root = scene.project.root if scene.project else None
        lib = scene._motions = Library(root)
    return lib


# ---------------------------------------------------------------------- retargeting
def _rest(c):
    """Rest directions of a character's limbs (in their pivots' frames) and its hip height."""
    if getattr(c, "_mrest", None) is not None:
        return c._mrest
    import bpy
    from . import handling
    bpy.context.view_layer.update()
    arms = handling.arm_rest(c) if c.arms and c.hands else {}
    legs = {}
    for side, piv in getattr(c, "legs", {}).items():
        foot = max((o for o in piv.children_recursive if o.type == "MESH"),
                   key=lambda o: -(o.matrix_world.translation.z), default=None)
        if foot is not None:
            d = piv.matrix_world.inverted() @ foot.matrix_world.translation
            legs[side] = (d.normalized(), d.length)
    if legs:
        hip_h = max(p.matrix_world.translation.z for p in c.legs.values())
    else:
        hip_h = c.leg_len if getattr(c, "leg_len", None) else 0.4 * c.H
    c._mrest = (arms, legs, hip_h)
    return c._mrest


def can_perform(c):
    return bool(c.arms) and (bool(getattr(c, "legs", None)) or bool(getattr(c, "feet", None))) and \
        len(getattr(c, "feet", {}) or getattr(c, "legs", {})) == 2


def pose(c, clip, p, h0, mirror=False):
    """Turn one clip pose into the character's pose: {object: rotation or location} plus the clip's
    hips (travel) and heading relative to `h0` (the clip's own starting heading)."""
    arms, legs, hip_h = _rest(c)
    scale = hip_h / clip.hip_height
    h = clip.heading(p)
    if mirror:   # swap left and right (and reflect across the centre line, below)
        p = {(("r_" if r[0] == "l" else "l_") + r[2:]) if r[:2] in ("l_", "r_") else r: v for r, v in p.items()}
    R = Matrix.Rotation(-h, 3, "Z")
    hips = p["hips"]

    def local(role, origin="hips"):
        v = R @ (p[role] - p[origin])
        return Vector((-v.x, v.y, v.z)) if mirror else v

    out = {}
    spine = local("chest")
    torso = Vector((0, 0, 1)).rotation_difference(spine.normalized()) if spine.length > 1e-6 else None
    if torso is not None and c.body is not None:
        out[(c.body, "rotation_euler")] = torso.to_euler("XYZ")
    tinv = torso.inverted() if torso is not None else None
    head = local("head", "neck")
    neck_of = getattr(c, "neck", None)
    if head.length > 1e-6 and neck_of is not None and not hasattr(c, "skel"):
        hl = (tinv @ head) if tinv else head
        out[(neck_of, "rotation_euler")] = Vector((0, 0, 1)).rotation_difference(hl.normalized()).to_euler("XYZ")
    for side, role in ((1, "l"), (-1, "r")):
        if side in arms:
            rest, _ = arms[side]
            d = local(f"{role}_wrist", f"{role}_arm")
            d = (tinv @ d) if tinv else d
            out[(c.arms[side], "rotation_euler")] = rest.rotation_difference(d.normalized()).to_euler("XYZ")
        if side in legs:
            rest, _ = legs[side]
            d = local(f"{role}_ankle", f"{role}_hip")
            out[(c.legs[side], "rotation_euler")] = rest.rotation_difference(d.normalized()).to_euler("XYZ")
    rise = (hips.z - clip.floor - clip.hip_height) * scale
    out[(c.hips, "location")] = Vector((0, 0, getattr(c, "hip_z", 0.0) + rise))
    feet = {}
    if getattr(c, "feet", None) and not legs:
        for leg in c.feet:
            role = "l" if leg.endswith("L") or leg.endswith(".L") else "r"
            feet[leg] = local(f"{role}_ankle") * scale
    return out, Vector((hips.x, hips.y)) * scale, h, feet


def perform(c, clip, t0, speed=1.0, mirror=False, in_place=False, blend=0.25, start=0.0, end=None):
    """Play `clip` on character `c` from t0. Returns when it ends (seconds). Bodies with a skeleton of
    their own play it bone by bone (ModelCharacter.perform_clip); others through dreamreel's pivots."""
    if hasattr(c, "perform_clip"):
        return c.perform_clip(clip, t0, speed, mirror, in_place, blend, start, end)
    return perform_pivots(c, clip, t0, speed, mirror, in_place, blend, start, end)


def perform_pivots(c, clip, t0, speed=1.0, mirror=False, in_place=False, blend=0.25, start=0.0, end=None):
    """Play `clip` through dreamreel's pivots: limb directions, the torso's lean, the hips' height."""
    from . import keys
    from .keys import key, value_at
    if not can_perform(c):
        raise ValueError(f"{c.name} hasn't got a body that can perform motion capture (two arms and two legs)")
    end = clip.length if end is None else min(end, clip.length)
    dur = (end - start) / max(0.05, speed)
    fps = keys.CLOCK.fps
    nf = max(2, int(round(dur * fps)))
    loc0 = Vector(value_at(c.root, "location", t0))
    H0 = value_at(c.root, "rotation_euler", t0)[2]
    p_first = clip.at(start)
    _, hips0, hs0, _ = pose(c, clip, p_first, 0.0, mirror)
    rest_vals = {}
    for i in range(nf + 1):
        tc = start + i / fps * speed
        objs, hips, hs, feet = pose(c, clip, clip.at(tc), hs0, mirror)
        t = t0 + i / fps
        w = min(1.0, i / max(1, blend * fps), (nf - i) / max(1, blend * fps) + 1e9)
        for (obj, prop), val in objs.items():
            if (obj, prop) not in rest_vals:
                rest_vals[(obj, prop)] = Vector(value_at(obj, prop, t0))
            v = Vector(val) if not isinstance(val, Euler) else Vector(val[:])
            v = rest_vals[(obj, prop)].lerp(v, w)
            key(obj, prop, t, tuple(v), "linear")
        dh = hs - hs0
        if mirror:
            dh = -dh
        heading = H0 + dh
        if in_place:
            pos = loc0.copy()
        else:
            d = Matrix.Rotation(-hs0, 3, "Z") @ Vector((hips.x - hips0.x, hips.y - hips0.y, 0))
            if mirror:
                d.x = -d.x
            d = Matrix.Rotation(H0, 3, "Z") @ d
            pos = loc0 + Vector((d.x, d.y, 0))
        key(c.root, "location", t, tuple(pos), "linear")
        key(c.root, "rotation_euler", t, (0, 0, heading), "linear")
        for leg, off in feet.items():
            wpos = Matrix.Rotation(heading, 3, "Z") @ off
            key(c.feet[leg], "location", t, (pos.x + wpos.x, pos.y + wpos.y, max(0.0, wpos.z + loc0.z)), "linear")
    t_end = t0 + nf / fps
    # settle back to the rest pose
    for (obj, prop), v in rest_vals.items():
        if prop == "rotation_euler" and obj is not c.root:
            key(obj, prop, t_end + blend, (0, 0, 0))
        elif obj is c.hips:
            key(obj, prop, t_end + blend, tuple(v))
    if getattr(c, "feet", None) and hasattr(c, "plant_feet"):
        c.plant_feet(t_end + blend, ease="smooth")
    return t_end + blend


def walk_cycle(c, clip, path, ws, end, rate):
    """Pose a character along a walk with a looping clip (its travel replaced by the path)."""
    from . import keys
    from .keys import key
    i0, i1 = clip.find_loop()
    cyc = (i1 - i0) / clip.fps
    fps = keys.CLOCK.fps
    p_start = clip.at(i0 / clip.fps)
    _, _, hs0, _ = pose(c, clip, p_start, 0.0)
    t = ws
    while t <= end + 1e-6:
        tc = i0 / clip.fps + ((t - ws) * rate) % cyc
        objs, _, _, feet = pose(c, clip, clip.at(tc), hs0)
        for (obj, prop), val in objs.items():
            key(obj, prop, t, tuple(val), "linear")
        t += 1.0 / fps
