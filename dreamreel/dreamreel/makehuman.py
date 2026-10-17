"""Humans from MakeHuman's assets (CC0): a real anatomy for people of any age, sex, build and look.

    # cast/ann.toml
    type = "human"
    gender = 0.0          # 0 female ... 1 male (anything between)
    age = 32              # years, 1 to 90
    muscle = 0.5          # 0 ... 1
    weight = 0.5          # 0 thin ... 1 heavy
    height = 0.5          # 0 short ... 1 tall for their age and sex (or metres: 1.68)
    proportions = 0.5     # 0 uncommon ... 1 idealised
    ethnicity = { african = 0.2, asian = 0.3, caucasian = 0.5 }
    shape = { "nose-scale-horiz" = -0.3, "chin-prominent" = 0.4 }   # any MakeHuman modifier, -1 ... 1
    skin = "#c68e6b"
    eye_color = "brown"   # an eye material (brown, blue, green, ...) or a colour
    hair = "bob01"        # a MakeHuman hair (with the system assets), or none
    eyebrows = "eyebrow001"
    clothes = ["male_casualsuit01"]

MakeHuman (makehumancommunity.org) is a free human modeller. Its base mesh, morph targets, rig,
eyes, eyebrows, hair and clothes are released as CC0: free to use for anything. dreamreel reads
those files directly (its own reader, no MakeHuman code): the body is the base mesh shaped by the
macro targets (age, sex, muscle, weight, height, proportions, ethnicity) and any modifiers you set;
fitted parts (eyes, brows, lashes, teeth, hair, clothes) ride on it; MakeHuman's own skeleton and
weights rig it; and its 34 facial expression units become shape keys that dreamreel's moods drive.

The assets aren't part of dreamreel. Point it at them once:
    dreamreel makehuman --download          # the CC0 system assets, about 280 MB
    dreamreel makehuman --use PATH          # or a MakeHuman checkout / data folder you have
"""
import json
import os

import bpy
import numpy as np
from mathutils import Vector

from . import look, shapes
from .models import ModelCharacter
from .plugins import Param

CONFIG = os.path.join(os.path.expanduser("~"), ".config", "dreamreel", "makehuman.json")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "makehuman")
SYSTEM_ASSETS = ("https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/"
                 "makehuman_system_assets_cc0.zip")
RACES = ("african", "asian", "caucasian")


# ---------------------------------------------------------------------- where the assets are
def _is_data(d):
    return d and os.path.isfile(os.path.join(d, "3dobjs", "base.obj"))


def roots():
    """Folders that hold MakeHuman data (a 'data' folder with 3dobjs/, targets/, ...), most specific
    first: $DREAMREEL_MAKEHUMAN, the folders set up with `dreamreel makehuman`, the download cache."""
    found = []
    cands = [os.environ.get("DREAMREEL_MAKEHUMAN")]
    try:
        with open(CONFIG) as fh:
            cands += json.load(fh).get("paths", [])
    except (OSError, ValueError):
        pass
    cands += [os.path.join(CACHE, "system"), CACHE]
    for c in cands:
        if not c:
            continue
        for d in (c, os.path.join(c, "data"), os.path.join(c, "makehuman", "data")):
            if os.path.isdir(d) and d not in found and (
                    _is_data(d) or any(os.path.isdir(os.path.join(d, k)) for k in ("hair", "eyebrows", "clothes"))):
                found.append(d)
    return found


def find(rel):
    """A MakeHuman asset file by its path in the data folder (e.g. 'eyes/high-poly/high-poly.mhclo')."""
    for d in roots():
        p = os.path.join(d, rel)
        if os.path.exists(p):
            return p
    return None


def available():
    return find("3dobjs/base.obj") is not None and find("targets/macrodetails") is not None


def find_asset(kind, name):
    """A proxy asset (.mhclo) by kind (hair, eyebrows, eyelashes, teeth, clothes, eyes) and name."""
    for d in roots():
        base = os.path.join(d, kind)
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            for f in files:
                if f.endswith(".mhclo") and (os.path.splitext(f)[0].lower() == name.lower()
                                             or os.path.basename(dirpath).lower() == name.lower()):
                    return os.path.join(dirpath, f)
    return None


def asset_names(kind):
    names = set()
    for d in roots():
        base = os.path.join(d, kind)
        if os.path.isdir(base):
            for dirpath, _, files in os.walk(base):
                names |= {os.path.splitext(f)[0] for f in files if f.endswith(".mhclo")}
    return sorted(names)


def use(path):
    """Remember a MakeHuman data folder (or checkout)."""
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    try:
        with open(CONFIG) as fh:
            cfg = json.load(fh)
    except (OSError, ValueError):
        cfg = {}
    paths = [p for p in cfg.get("paths", []) if p != path]
    cfg["paths"] = [os.path.abspath(path)] + paths
    with open(CONFIG, "w") as fh:
        json.dump(cfg, fh, indent=1)


def download(progress=print):
    """Fetch the CC0 system assets (eyebrows, eyelashes, teeth, hair, clothes, skins) into the cache."""
    import urllib.request
    import zipfile
    os.makedirs(CACHE, exist_ok=True)
    zpath = os.path.join(CACHE, "system_assets.zip")
    progress(f"Downloading {SYSTEM_ASSETS} ...")
    urllib.request.urlretrieve(SYSTEM_ASSETS, zpath)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(os.path.join(CACHE, "system"))
    os.remove(zpath)
    progress(f"MakeHuman system assets in {os.path.join(CACHE, 'system')}")


# ---------------------------------------------------------------------- reading the files
_OBJ, _TARGETS = {}, {}


def read_obj(path):
    """Vertices, faces (vertex indices), face UVs and face groups of a Wavefront .obj."""
    if path in _OBJ:
        return _OBJ[path]
    verts, uvs, faces, fuvs, groups = [], [], [], [], []
    group = ""
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                verts.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("vt "):
                uvs.append([float(x) for x in line.split()[1:3]])
            elif line.startswith("g "):
                group = line.split(None, 1)[1].strip()
            elif line.startswith("f "):
                vi, ti = [], []
                for tok in line.split()[1:]:
                    parts = tok.split("/")
                    vi.append(int(parts[0]) - 1)
                    ti.append(int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1)
                faces.append(vi)
                fuvs.append(ti)
                groups.append(group)
    out = (np.array(verts), np.array(uvs) if uvs else None, faces, fuvs, groups)
    _OBJ[path] = out
    return out


def read_target(name):
    """A morph target: (vertex indices, offsets), in MakeHuman's units and axes."""
    if name in _TARGETS:
        return _TARGETS[name]
    path = find(f"targets/{name}.target")
    if path is None:
        _TARGETS[name] = None
        return None
    idx, off = [], []
    with open(path) as fh:
        for line in fh:
            if line[:1].isdigit():
                p = line.split()
                idx.append(int(p[0]))
                off.append([float(p[1]), float(p[2]), float(p[3])])
    _TARGETS[name] = (np.array(idx, dtype=int), np.array(off)) if idx else None
    return _TARGETS[name]


def read_mhclo(path):
    """A fitted asset: each vertex rides on three base-mesh vertices (weights + an offset scaled by
    the distance between reference vertices along each axis)."""
    info = {"scale": {}, "refs": [], "delete": [], "obj": None, "material": None, "z_depth": 50,
            "dir": os.path.dirname(path), "name": os.path.splitext(os.path.basename(path))[0]}
    in_verts = in_delete = False
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            key = p[0]
            if key in ("x_scale", "y_scale", "z_scale"):
                info["scale"][key[0]] = (int(p[1]), int(p[2]), float(p[3]))
            elif key == "obj_file":
                info["obj"] = os.path.join(info["dir"], line.split(None, 1)[1])
            elif key == "material":
                info["material"] = os.path.join(info["dir"], line.split(None, 1)[1])
            elif key == "z_depth":
                info["z_depth"] = int(p[1])
            elif key == "verts":
                in_verts, in_delete = True, False
            elif key == "delete_verts":
                in_verts, in_delete = False, True
            elif in_verts and len(p) >= 9 and p[0].lstrip("-").isdigit():
                info["refs"].append(([int(x) for x in p[:3]], [float(x) for x in p[3:6]],
                                     [float(x) for x in p[6:9]]))
            elif in_verts and len(p) == 1 and p[0].isdigit():
                info["refs"].append(([int(p[0])] * 3, [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
            elif in_delete:                       # "12 - 40 51 60 - 64": single vertices and ranges
                toks = line.replace("-", " - ").split()
                i = 0
                while i < len(toks):
                    if i + 2 < len(toks) and toks[i + 1] == "-":
                        info["delete"] += list(range(int(toks[i]), int(toks[i + 2]) + 1))
                        i += 3
                    else:
                        if toks[i].isdigit():
                            info["delete"].append(int(toks[i]))
                        i += 1
            elif not in_verts and key not in ("name", "uuid", "basemesh", "tag", "version", "license", "author",
                                              "homepage", "max_pole", "special_pose", "offset_scale"):
                in_verts = False
    return info


def fit(info, coords):
    """Where a fitted asset's vertices go on a body (MakeHuman coordinates)."""
    sc = {}
    for axis, k in (("x", 0), ("y", 1), ("z", 2)):
        if axis in info["scale"]:
            a, b, s = info["scale"][axis]
            sc[k] = abs(coords[a][k] - coords[b][k]) / s if s else 1.0
        else:
            sc[k] = 1.0
    out = np.zeros((len(info["refs"]), 3))
    for i, (r, w, o) in enumerate(info["refs"]):
        out[i] = coords[r[0]] * w[0] + coords[r[1]] * w[1] + coords[r[2]] * w[2] + \
            np.array([o[0] * sc[0], o[1] * sc[1], o[2] * sc[2]])
    return out


def read_material(path):
    """The diffuse colour and texture of a MakeHuman .mhmat."""
    out = {"color": None, "texture": None}
    if not path or not os.path.exists(path):
        return out
    with open(path) as fh:
        for line in fh:
            p = line.split()
            if not p:
                continue
            if p[0] == "diffuseColor" and len(p) >= 4:
                out["color"] = tuple(float(x) for x in p[1:4])
            elif p[0] == "diffuseTexture" and len(p) >= 2:
                tex = os.path.join(os.path.dirname(path), line.split(None, 1)[1].strip())
                out["texture"] = tex if os.path.exists(tex) else None
    return out


# ---------------------------------------------------------------------- the body's shape
def _two(v, lo_name, mid_name, hi_name):
    """Weights for a value 0..1 between three named points (0, 0.5, 1)."""
    v = max(0.0, min(1.0, v))
    if v < 0.5:
        return {lo_name: 1 - 2 * v, mid_name: 2 * v}
    return {mid_name: 2 - 2 * v, hi_name: 2 * v - 1}


def age_value(years):
    """MakeHuman's age slider from years: 1 -> 0, 11 -> 0.1875, 25 -> 0.5, 90 -> 1."""
    y = max(1.0, min(90.0, float(years)))
    if y < 11:
        return (y - 1) / 10 * 0.1875
    if y < 25:
        return 0.1875 + (y - 11) / 14 * 0.3125
    return 0.5 + (y - 25) / 65 * 0.5


def macro_weights(gender, age, muscle, weight, height, proportions, races):
    """{target name: weight} for the macro targets: the shape of a person of this age, sex, build,
    height, proportions and ethnic mix (each 0..1; age as MakeHuman's slider)."""
    g = {"female": 1 - gender, "male": gender}
    if age < 0.1875:
        a = {"baby": 1 - age / 0.1875, "child": age / 0.1875}
    elif age < 0.5:
        a = {"child": (0.5 - age) / 0.3125, "young": (age - 0.1875) / 0.3125}
    else:
        a = {"young": (1 - age) / 0.5, "old": (age - 0.5) / 0.5}
    m = _two(muscle, "minmuscle", "averagemuscle", "maxmuscle")
    w = _two(weight, "minweight", "averageweight", "maxweight")
    h = {"minheight": max(0.0, 1 - 2 * height), "maxheight": max(0.0, 2 * height - 1)}
    pr = {"uncommonproportions": max(0.0, 1 - 2 * proportions), "idealproportions": max(0.0, 2 * proportions - 1)}
    out = {}

    def add(name, value):
        if value > 1e-4:
            out[name] = out.get(name, 0.0) + value
    for gn, gw in g.items():
        for an, aw in a.items():
            for rn, rw in races.items():
                add(f"macrodetails/{rn}-{gn}-{an}", gw * aw * rw)
            for mn, mw in m.items():
                for wn, ww in w.items():
                    base = gw * aw * mw * ww
                    add(f"macrodetails/universal-{gn}-{an}-{mn}-{wn}", base)
                    for hn, hw in h.items():
                        add(f"macrodetails/height/{gn}-{an}-{mn}-{wn}-{hn}", base * hw)
                    for pn, pw in pr.items():
                        add(f"macrodetails/proportions/{gn}-{an}-{mn}-{wn}-{pn}", base * pw)
    return out


def modifier_targets(name, value):
    """A MakeHuman modifier ('nose-scale-horiz', -1 ... 1) -> {target: weight}. Two-sided
    modifiers have targets name-min / name-max (e.g. nose-scale-horiz-decr / -incr)."""
    path = find("modifiers/modeling_modifiers.json")
    if path is None:
        return {}
    with open(path) as fh:
        groups = json.load(fh)
    for grp in groups:
        folder = grp["group"]
        for mod in grp.get("modifiers", []):
            if "target" not in mod:                  # macro sliders (age, gender...) are params instead
                continue
            tname, lo, hi = mod["target"], mod.get("min"), mod.get("max")
            if lo is None:
                if name == tname:
                    return {f"{folder}/{tname}": max(0.0, value)}
                continue
            if name not in (tname, f"{tname}-{lo}-{hi}", f"{tname}-{lo}|{hi}"):
                continue
            return {f"{folder}/{tname}-{lo}": -value} if value < 0 else {f"{folder}/{tname}-{hi}": value}
    raise ValueError(f"no MakeHuman modifier called {name!r} (see modifiers/modeling_modifiers.json)")


def shaped(base, weights):
    """The base mesh with targets applied."""
    coords = base.copy()
    for name, w in weights.items():
        t = read_target(name)
        if t is not None:
            coords[t[0]] += t[1] * w
    return coords


def to_blender(p):
    """MakeHuman (decimetres, Y up, facing +Z) -> dreamreel (metres, Z up, facing -Y)."""
    p = np.asarray(p)
    return np.stack([p[..., 0], -p[..., 2], p[..., 1]], axis=-1) * 0.1


# ---------------------------------------------------------------------- the character
MH_ROLES = {"hips": "root", "chest": "spine01", "neck": "neck01", "head": "head"}
for _s, _S in (("l", "L"), ("r", "R")):
    MH_ROLES.update({f"{_s}_arm": f"upperarm01.{_S}", f"{_s}_elbow": f"lowerarm01.{_S}", f"{_s}_wrist": f"wrist.{_S}",
                     f"{_s}_hip": f"upperleg01.{_S}", f"{_s}_knee": f"lowerleg01.{_S}", f"{_s}_ankle": f"foot.{_S}"})

# dreamreel's face controls -> MakeHuman expression units (per side where there are two)
UNITS = {
    "blink": ["eye-left-closure", "eye-right-closure"],
    "squint": ["eye-left-slit", "eye-right-slit"],
    "wide_eyes": ["eye-left-opened-up", "eye-right-opened-up"],
    "brows_up": ["eyebrows-left-up", "eyebrows-right-up"],
    "brows_inner": ["eyebrows-left-inner-up", "eyebrows-right-inner-up"],
    "brows_down": ["eyebrows-left-down", "eyebrows-right-down"],
    "smile": ["mouth-corner-puller", "mouth-elevation"],
    "frown": ["mouth-depression"],
    "open": ["mouth-open"],
    "wide": ["mouth-retraction"],
    "o": ["mouth-pursing", "mouth-protusion"],
    "sneer": ["nose-left-elevation", "nose-right-elevation", "mouth-upward-retraction"],
    "teeth": ["mouth-parling"],
}


class Human(ModelCharacter):
    """A human from MakeHuman's CC0 assets (see makehuman.py)."""
    name = "human"
    label = "Human (MakeHuman)"
    description = "A realistic human of any age, sex, build and look, from MakeHuman's free assets"
    drawing = None
    params = [
        Param("name", "text", label="Name"),
        Param("gender", "number", default=0.5, min=0, max=1, step=0.05, label="Female ... male"),
        Param("age", "number", default=25, min=1, max=90, step=1, label="Age (years)"),
        Param("muscle", "number", default=0.5, min=0, max=1, step=0.05),
        Param("weight", "number", default=0.5, min=0, max=1, step=0.05, label="Weight (thin ... heavy)"),
        Param("height", "number", default=0.5, min=0, max=2.2, step=0.05,
              label="Height (0 ... 1 for their age and sex, or metres)"),
        Param("proportions", "number", default=0.5, min=0, max=1, step=0.05),
        Param("ethnicity", "text", label="Ethnicity (african / asian / caucasian, or a mix)"),
        Param("shape", "text", label="Shape modifiers"),
        Param("skin", "text", default="#d9a07e", label="Skin (a colour or a MakeHuman skin)"),
        Param("eye_color", "text", default="brown", label="Eye colour"),
        Param("hair", "text", default="", label="Hair (a MakeHuman hair)"),
        Param("eyebrows", "text", default="eyebrow001"),
        Param("clothes", "text", label="Clothes (MakeHuman clothes)"),
        Param("voice", "voice"),
    ]
    default_capabilities = ("walk", "arms", "swing_legs", "face")

    def validate(self):
        if not available():
            raise ValueError(f"{self.name}: type = \"human\" needs MakeHuman's assets: run "
                             "`dreamreel makehuman --download` (or --use PATH to a MakeHuman checkout)")

    def proportions(self):
        h = float(self.get("height", 0.5) or 0.5)
        self.metres = h if h > 1.2 else None           # a height in metres, or MakeHuman's slider
        self.H = self.metres or 1.7

    def _races(self):
        e = self.spec.get("ethnicity")
        if not e:
            return {r: 1 / 3 for r in RACES}
        if isinstance(e, str):
            return {r: 1.0 if r == e else 0.0 for r in RACES}
        total = sum(float(e.get(r, 0)) for r in RACES) or 1.0
        return {r: float(e.get(r, 0)) / total for r in RACES}

    def build(self):
        n = self.name
        base, uvs, faces, fuvs, groups = read_obj(find("3dobjs/base.obj"))
        races = self._races()
        slider = float(self.get("height", 0.5) or 0.5)
        weights = macro_weights(float(self.get("gender", 0.5)), age_value(self.get("age", 25)),
                                float(self.get("muscle", 0.5)), float(self.get("weight", 0.5)),
                                0.5 if self.metres else slider, float(self.get("proportions", 0.5)), races)
        for mod, v in (self.spec.get("shape") or {}).items():
            for t, w in modifier_targets(mod, float(v)).items():
                weights[t] = weights.get(t, 0.0) + w
        coords = shaped(base, weights)
        self.mh_coords = coords
        # keep the body (not the helper geometry: tights, skirts, joints), minus what clothes cover
        hidden = set()
        clothes = self.spec.get("clothes") or []
        for name in ([clothes] if isinstance(clothes, str) else clothes):
            p = find_asset("clothes", name)
            if p:
                hidden |= set(read_mhclo(p)["delete"])
        keep = [i for i, g in enumerate(groups) if g == "body" and not any(v in hidden for v in faces[i])]
        used = sorted({v for i in keep for v in faces[i]})
        remap = {old: new for new, old in enumerate(used)}
        whole = sorted({v for i, g in enumerate(groups) if g == "body" for v in faces[i]})   # incl. hidden parts
        pts = to_blender(coords)
        floor = pts[whole, 2].min()
        pts[:, 2] -= floor
        k = 1.0
        if self.metres:
            k = self.metres / (pts[whole, 2].max())
            pts *= k
        self.mh_scale = k
        self.mh_floor = floor
        me = bpy.data.meshes.new(f"{n}.body")
        me.from_pydata([tuple(pts[i]) for i in used], [], [[remap[v] for v in faces[i]] for i in keep])
        if uvs is not None:
            uv = me.uv_layers.new(name="UVMap")
            loop = 0
            for fi in keep:
                for t in fuvs[fi]:
                    uv.data[loop].uv = tuple(uvs[t]) if t >= 0 else (0, 0)
                    loop += 1
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(self._skin())
        body = bpy.data.objects.new(f"{n}.body", me)
        shapes._collection().objects.link(body)
        holder = shapes.empty(f"{n}.model")
        body.parent = holder
        self.body_used, self.body_remap = used, remap
        self.H = float(pts[whole, 2].max())
        # the rig: MakeHuman's skeleton, its joints from the shaped mesh, its weights
        arm = self._rig(pts, holder, body)
        meshes = [body] + self._proxies(pts, coords, arm, holder)
        self._expressions(body, races, k)
        self.rig, self.roles, self.meshes, self.holder = arm, dict(MH_ROLES), [body], holder
        self._drive(arm, self.roles)              # arms hang clear of the body (not the clothes)
        self.meshes = meshes
        self._mh_face(body)

    def _skin(self):
        """A MakeHuman skin (a textured one by name, e.g. young_caucasian_female), or a colour."""
        name = str(self.get("skin", "#d9a07e"))
        path = None
        for d in roots():
            cand = os.path.join(d, "skins", name, f"{name}.mhmat")
            if os.path.exists(cand):
                path = cand
                break
        if path is None:
            return look.skin(name)
        mat = self._mh_material(path, None, "skin")
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        for k, v in (("Subsurface Weight", 0.15), ("Subsurface Scale", 0.01)):
            if k in bsdf.inputs:
                bsdf.inputs[k].default_value = v
        return mat

    # ------------------------------------------------------------------ rig
    def _rig(self, pts, holder, body):
        with open(find("rigs/default.mhskel")) as fh:
            sk = json.load(fh)
        joints = {name: Vector(pts[idx].mean(axis=0)) for name, idx in sk["joints"].items()}
        data = bpy.data.armatures.new(f"{self.name}.rig")
        arm = bpy.data.objects.new(f"{self.name}.rig", data)
        shapes._collection().objects.link(arm)
        arm.parent = holder
        bpy.context.view_layer.objects.active = arm
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        arm.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        eb = {}
        for name, b in sk["bones"].items():
            bone = data.edit_bones.new(name)
            bone.head, bone.tail = joints[b["head"]], joints[b["tail"]]
            if (bone.tail - bone.head).length < 1e-5:
                bone.tail = bone.head + Vector((0, 0, 0.005))
            eb[name] = bone
        for name, b in sk["bones"].items():
            if b.get("parent"):
                eb[name].parent = eb[b["parent"]]
        bpy.ops.object.mode_set(mode="OBJECT")
        with open(find("rigs/" + sk.get("weights_file", "default_weights.mhw"))) as fh:
            wts = json.load(fh)["weights"]
        self.mh_weights = wts
        for bone, pairs in wts.items():
            vg = body.vertex_groups.new(name=bone)
            for v, w in pairs:
                nv = self.body_remap.get(v)
                if nv is not None:
                    vg.add([nv], w, "REPLACE")
        mod = body.modifiers.new("rig", "ARMATURE")
        mod.object = arm
        return arm

    # ------------------------------------------------------------------ fitted parts
    def _proxy_weights(self, info):
        """A fitted asset's skin weights, from the base vertices it rides on."""
        per_vert = {}
        for bone, pairs in self.mh_weights.items():
            for v, w in pairs:
                per_vert.setdefault(v, []).append((bone, w))
        out = []
        for r, w, _ in info["refs"]:
            acc = {}
            for vi, wi in zip(r, w):
                for bone, bw in per_vert.get(vi, []):
                    acc[bone] = acc.get(bone, 0.0) + bw * wi
            out.append(acc)
        return out

    def _proxy(self, path, kind, coords, arm, holder, color=None, material=None):
        info = read_mhclo(path)
        if not info["obj"] or not os.path.exists(info["obj"]):
            return None
        verts, uvs, faces, fuvs, _ = read_obj(info["obj"])
        pts = to_blender(fit(info, coords))
        pts[:, 2] -= self.mh_floor * 1.0
        pts *= self.mh_scale
        me = bpy.data.meshes.new(f"{self.name}.{kind}")
        me.from_pydata([tuple(p) for p in pts], [], faces)
        if uvs is not None:
            uv = me.uv_layers.new(name="UVMap")
            loop = 0
            for fi in range(len(faces)):
                for t in fuvs[fi]:
                    uv.data[loop].uv = tuple(uvs[t]) if t >= 0 else (0, 0)
                    loop += 1
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(material or self._mh_material(info["material"], color, kind))
        obj = bpy.data.objects.new(f"{self.name}.{kind}", me)
        shapes._collection().objects.link(obj)
        obj.parent = holder
        for i, acc in enumerate(self._proxy_weights(info)):
            for bone, w in acc.items():
                vg = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
                vg.add([i], w, "ADD")
        mod = obj.modifiers.new("rig", "ARMATURE")
        mod.object = arm
        obj["mh_info"] = path
        self._fitted.append((obj, info))
        return obj

    def _mh_material(self, path, color, kind):
        m = read_material(path)
        if m["texture"] is None:
            return look.hair(color) if kind in ("hair", "eyebrows", "eyelashes") and color else \
                look.plastic(color or "#808080", 0.6, 0.1)
        mat = bpy.data.materials.new(f"{self.name}.{kind}")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(m["texture"], check_existing=True)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if kind in ("hair", "eyebrows", "eyelashes") or tex.image.depth == 32:
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            if hasattr(mat, "blend_method"):
                mat.blend_method = "HASHED"
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "DITHERED"
        bsdf.inputs["Roughness"].default_value = 0.55 if kind != "eyes" else 0.15
        mat.diffuse_color = (*(m["color"] or (0.5, 0.5, 0.5)), 1)
        return mat

    def _proxies(self, pts, coords, arm, holder):
        self._fitted = []
        out = []
        eyes = find("eyes/high-poly/high-poly.mhclo") or find("eyes/low-poly/low-poly.mhclo")
        if eyes:
            ec = str(self.get("eye_color", "brown") or "brown")
            emat = find(f"eyes/materials/{ec}.mhmat")
            mat = self._mh_material(emat, None, "eyes") if emat else None
            if mat is None:
                mat = look.plastic(ec if not emat else "#6b4423", 0.15, 0.6)
            o = self._proxy(eyes, "eyes", coords, arm, holder, material=mat)
            if o:
                out.append(o)
        hair_col = self.color("hair_color", "#3b2416")
        for kind, name in (("eyebrows", self.get("eyebrows", "eyebrow001")), ("eyelashes", "eyelashes01"),
                           ("teeth", "teeth_base"), ("tongue", "tongue01"), ("hair", self.get("hair", ""))):
            if not name or name == "none":
                continue
            p = find_asset(kind, str(name))
            if p:
                o = self._proxy(p, kind, coords, arm, holder, color=hair_col)
                if o:
                    out.append(o)
        clothes = self.spec.get("clothes") or []
        for name in ([clothes] if isinstance(clothes, str) else clothes):
            p = find_asset("clothes", name)
            if p is None:
                raise ValueError(f"{self.name}: no MakeHuman clothes called {name!r}; installed: "
                                 f"{', '.join(asset_names('clothes')[:30])}")
            o = self._proxy(p, "clothes", coords, arm, holder)
            if o:
                out.append(o)
        return out

    # ------------------------------------------------------------------ the face
    def _expressions(self, body, races, k):
        """MakeHuman's expression units as shape keys on the body and the fitted parts."""
        body.shape_key_add(name="Basis", from_mix=False)
        self.units = {}
        names = sorted({u for us in UNITS.values() for u in us})
        for unit in names:
            delta = np.zeros_like(self.mh_coords)
            found = False
            for race, w in races.items():
                t = read_target(f"expression/units/{race}/{unit}")
                if t is not None and w > 0:
                    delta[t[0]] += t[1] * w
                    found = True
            if not found:
                continue
            d = to_blender(delta) * k
            kb = body.shape_key_add(name=unit, from_mix=False)
            kb.value = 0.0
            for new, old in enumerate(self.body_used):
                if delta[old].any():
                    kb.data[new].co += Vector(d[old])
            self.units[unit] = [kb]
            for obj, info in self._fitted:          # brows, lashes, teeth follow the face
                fd = to_blender(fit(info, self.mh_coords + delta) - fit(info, self.mh_coords)) * k
                if not np.abs(fd).max() > 1e-6:
                    continue
                if obj.data.shape_keys is None:
                    obj.shape_key_add(name="Basis", from_mix=False)
                okb = obj.shape_key_add(name=unit, from_mix=False)
                okb.value = 0.0
                for i, dv in enumerate(fd):
                    okb.data[i].co += Vector(dv)
                self.units[unit].append(okb)

    def _mh_face(self, body):
        """dreamreel's face controls (stand-ins) driving the expression units."""
        from . import face
        n = self.name
        self.eyes = [shapes.empty(f"{n}.eye", self.neck) for _ in (1, -1)]
        self.brows = {s: shapes.empty(f"{n}.brow", self.neck) for s in (1, -1)}
        self.mouth = shapes.empty(f"{n}.mouthpivot", self.neck)
        m = shapes.plane(f"{n}.mouthkeys", 0.001, 0.001, None, self.neck)
        m.hide_render = m.hide_viewport = True
        face.mouth_keys(m, 0.001, 0.001, self.H)
        self.mouth_mesh = m
        lids = shapes.plane(f"{n}.lidkeys", 0.001, 0.001, None, self.neck)
        lids.hide_render = lids.hide_viewport = True
        face.lid_keys(lids, 0.001, 0.001, 1)
        self.scleras, self.irises, self.glints, self.blushes, self.gazes = [lids], [], [], [], []
        self.teeth = {w: shapes.empty(f"{n}.teeth.{w}", self.mouth) for w in ("upper", "lower")}
        for t in self.teeth.values():
            t.scale = (1, 1, 0)
        self.mouth_parts = [m]
        mk, lk = m.data.shape_keys, lids.data.shape_keys
        drive = {
            # unit: [(variable source, data path), ...], expression of v0, v1...
            "blink": ([(self.eyes[0], "scale[2]"), (lk, 'key_blocks["upper"].value')],
                      "max(0, min(1, max(1 - v0, v1 * 0.6)))"),
            "squint": ([(lk, 'key_blocks["lower"].value')], "v0"),
            "wide_eyes": ([(self.eyes[0], "scale[2]")], "max(0, min(1, (v0 - 1) * 2.5))"),
            "brows_up": ([(self.brows[1], "location[2]")], f"max(0, min(1, v0 * {40 / self.H:.4f}))"),
            "brows_down": ([(self.brows[1], "location[2]"), (self.brows[1], "rotation_euler[1]")],
                           f"max(0, min(1, -v0 * {40 / self.H:.4f} - v1 * 1.5))"),
            "brows_inner": ([(self.brows[1], "rotation_euler[1]")], "max(0, min(1, v0 * 2.2))"),
            "smile": ([(mk, 'key_blocks["smile"].value')], "v0"),
            "frown": ([(mk, 'key_blocks["frown"].value')], "v0"),
            "open": ([(self.mouth, "scale[2]")], "max(0, min(1, (v0 - 1) / 2.2))"),
            "wide": ([(mk, 'key_blocks["wide"].value')], "v0"),
            "o": ([(mk, 'key_blocks["o"].value')], "v0"),
            "sneer": ([(mk, 'key_blocks["smirk"].value')], "max(0, -v0)"),
            "teeth": ([(self.teeth["upper"], "scale[2]")], "v0"),
        }
        for role, units in UNITS.items():
            srcs, expr = drive[role]
            for unit in units:
                for kb in self.units.get(unit, []):
                    d = kb.driver_add("value").driver
                    d.type = "SCRIPTED"
                    for i, (src, path) in enumerate(srcs):
                        var = d.variables.new()
                        var.name = f"v{i}"
                        var.targets[0].id_type = "KEY" if path.startswith("key_blocks") else "OBJECT"
                        var.targets[0].id = src
                        var.targets[0].data_path = path
                    d.expression = expr
        # where the face is, for tears, sweat and the camera
        hz = self.hip_z
        head = Vector(self.mh_joint("head"))
        self.face_centre = head
        for side, e in zip((1, -1), self.eyes):
            e.location = Vector(self.mh_joint(f"eye.{'L' if side > 0 else 'R'}")) - Vector((0, 0, hz)) - \
                self.neck.location

    def mh_joint(self, bone):
        b = self.rig.data.bones.get(bone)
        return self.rig.matrix_world @ b.head_local if b else self.rig.matrix_world.translation

    def face_point(self, x, z, inset=0.006):
        return self.hc + Vector((x, -self.hr * 0.9, z))


def register_patterns():
    """Names a cast file can use for MakeHuman assets (for the studio and `dreamreel info`)."""
    return {k: asset_names(k) for k in ("hair", "eyebrows", "clothes")}


