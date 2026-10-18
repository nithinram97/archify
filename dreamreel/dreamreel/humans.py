"""Realistic people: bodies, skin, hair, clothes and an expressive face, from MakeHuman's free assets.

    # cast/asha.toml
    type = "human"
    gender = "female"           # female or male (or a number: 0 female ... 1 male)
    age = 28                    # years
    build = "average"           # slim, average, athletic, heavy
    heritage = "south_asian"    # african, east_asian, european, south_asian, latin, middle_eastern, mixed
    skin_tone = "#8d5a3b"       # optional: any colour; else one that suits the heritage
    hair = "long01"             # afro01, bob01, bob02, braid01, long01, ponytail01, short01-04, none
    hair_color = "black"
    eyes = "brown"              # blue, bluegreen, brown, brownlight, darkblue, green, grey, ice, lightblue
    outfit = "female_casualsuit01"
    shoes = "shoes02"
    face = 0.5                  # how far this face is from the average (0-1): everyone looks different
    height = 1.62               # metres

MakeHuman (makehumancommunity.org) is a free human generator; its body, its shaping targets, skins,
eyes, brows, lashes, hair, clothes and the 52 ARKit face units and 15 visemes contributed by Mika
Suominen are all CC0. dreamreel doesn't bundle them: `dreamreel assets --pack humans` fetches them
(about 700 MB) into ~/.cache/dreamreel/makehuman. dreamreel builds the person itself from the data:
the body shaped for gender, age, build and heritage, a face of its own, hair, eyebrows, eyelashes,
eyes, teeth and tongue, clothes fitted to the body, a skeleton (Mixamo's bone names, so motion
capture clips play on it), and 67 facial shape keys that brows, lashes, eyes and teeth follow too.
"""
import gzip
import json
import os
import random
import re
import urllib.request
import zipfile

import bpy
import numpy as np

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "makehuman")
BASE = os.path.join(CACHE, "base")

# what to fetch: MPFB's data (the base body, its targets and rigs; MakeHuman's CC0 assets travel in
# the MPFB extension, whose code we don't use), and asset packs
DOWNLOADS = {
    "base": ("https://extensions.blender.org/api/v1/extensions/", "mpfb"),
    "system": "https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip",
    "faceunits": "https://files.makehumancommunity.org/functional/faceunits01.zip",
    "visemes": "https://files.makehumancommunity.org/functional/visemes02.zip",
}

ARKIT = ("browDownLeft browDownRight browInnerUp browOuterUpLeft browOuterUpRight cheekPuff cheekSquintLeft "
         "cheekSquintRight eyeBlinkLeft eyeBlinkRight eyeLookDownLeft eyeLookDownRight eyeLookInLeft eyeLookInRight "
         "eyeLookOutLeft eyeLookOutRight eyeLookUpLeft eyeLookUpRight eyeSquintLeft eyeSquintRight eyeWideLeft "
         "eyeWideRight jawForward jawLeft jawOpen jawRight mouthClose mouthDimpleLeft mouthDimpleRight "
         "mouthFrownLeft mouthFrownRight mouthFunnel mouthLeft mouthLowerDownLeft mouthLowerDownRight "
         "mouthPressLeft mouthPressRight mouthPucker mouthRight mouthRollLower mouthRollUpper mouthShrugLower "
         "mouthShrugUpper mouthSmileLeft mouthSmileRight mouthStretchLeft mouthStretchRight mouthUpperUpLeft "
         "mouthUpperUpRight noseSneerLeft noseSneerRight tongueOut").split()
VISEMES = "sil PP FF TH DD kk CH SS nn RR aa E I O U".split()

HERITAGE = {   # MakeHuman's three ancestry blends (african, asian, caucasian), and a skin to start from
    "african": ((1.0, 0.0, 0.0), "african", "#5e3a26"),
    "east_asian": ((0.0, 1.0, 0.0), "asian", "#e0b48f"),
    "european": ((0.0, 0.0, 1.0), "caucasian", "#eec1a0"),
    "south_asian": ((0.2, 0.25, 0.55), "asian", "#a46a45"),
    "latin": ((0.15, 0.2, 0.65), "caucasian", "#c58c63"),
    "middle_eastern": ((0.1, 0.1, 0.8), "caucasian", "#c99a74"),
    "mixed": ((0.34, 0.33, 0.33), "african", "#9a6748"),
}
# clean everyday outfits (some of MakeHuman's have its logo on the shirt); all fit any body
OUTFITS = {"female": ["female_elegantsuit01", "male_casualsuit01", "male_casualsuit05", "male_casualsuit03"],
           "male": ["male_casualsuit01", "male_casualsuit03", "male_casualsuit05"]}
BUILD = {"slim": (0.3, 0.45), "average": (0.5, 0.5), "athletic": (0.45, 0.8), "heavy": (0.85, 0.45),
         "stocky": (0.7, 0.7)}       # (weight, muscle)


def installed():
    return all(os.path.exists(p) for p in (os.path.join(BASE, "3dobjs", "base.obj"),
                                           os.path.join(CACHE, "skins"),
                                           os.path.join(CACHE, "targets", "faceunits")))


def download(progress=print):
    """Fetch MakeHuman's assets (about 700 MB the first time)."""
    os.makedirs(CACHE, exist_ok=True)
    tmp = os.path.join(CACHE, "download.zip")
    ua = {"User-Agent": "dreamreel asset fetcher"}

    def get(url):
        with urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=600) as r, open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)

    if not os.path.exists(os.path.join(BASE, "3dobjs", "base.obj")):
        progress("  MakeHuman's body, targets and rigs (from the MPFB extension, 46 MB)")
        with urllib.request.urlopen(urllib.request.Request(DOWNLOADS["base"][0], headers=ua), timeout=60) as r:
            ext = next(e for e in json.load(r)["data"] if e["id"] == DOWNLOADS["base"][1])
        get(ext["archive_url"])
        with zipfile.ZipFile(tmp) as z:
            for n in z.namelist():
                m = re.match(r"^(?:[^/]+/)?data/((3dobjs|targets|rigs)/.*)$", n)
                if m and not n.endswith("/"):
                    dest = os.path.join(BASE, m.group(1))
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with z.open(n) as src, open(dest, "wb") as out:
                        out.write(src.read())
    for pack, label in (("system", "skins, eyes, hair, clothes (280 MB)"), ("faceunits", "52 face units"),
                        ("visemes", "15 visemes")):
        marker = os.path.join(CACHE, f".{pack}")
        if os.path.exists(marker):
            continue
        progress(f"  MakeHuman {label}")
        get(DOWNLOADS[pack])
        with zipfile.ZipFile(tmp) as z:
            z.extractall(CACHE)
        open(marker, "w").close()
    if os.path.exists(tmp):
        os.remove(tmp)


# ---------------------------------------------------------------------- reading MakeHuman's files
def _read_obj(path):
    """verts (n, 3), uvs (m, 2), faces [(vert indices, uv indices)], the group of each face."""
    vs, uvs, faces, groups, group = [], [], [], [], ""
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                vs.append(line.split()[1:4])
            elif line.startswith("vt "):
                uvs.append(line.split()[1:3])
            elif line.startswith("f "):
                vi, ti = [], []
                for tok in line.split()[1:]:
                    parts = tok.split("/")
                    vi.append(int(parts[0]) - 1)
                    ti.append(int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1)
                faces.append((vi, ti))
                groups.append(group)
            elif line.startswith("g "):
                group = line.split()[1] if len(line.split()) > 1 else ""
    return np.array(vs, dtype=np.float64), np.array(uvs or [[0, 0]], dtype=np.float64), faces, groups


_targets = {}


def _target(path):
    """A shaping target: (vertex indices, offsets)."""
    if path in _targets:
        return _targets[path]
    opener = gzip.open if path.endswith(".gz") else open
    idx, d = [], []
    with opener(path, "rt") as f:
        for line in f:
            p = line.split()
            if len(p) == 4 and not line.startswith("#"):
                idx.append(int(p[0]))
                d.append([float(x) for x in p[1:]])
    _targets[path] = (np.array(idx, dtype=np.int64), np.array(d, dtype=np.float64).reshape(-1, 3))
    return _targets[path]


def _parts(value, edges, names):
    """Weights of the named ends of a slider: e.g. age 0.35 between child (0.1875) and young (0.5)."""
    out = {}
    for (a, b), (lo, hi) in zip(zip(edges, edges[1:]), zip(names, names[1:])):
        if a <= value <= b:
            t = (value - a) / (b - a) if b > a else 0.0
            if lo:
                out[lo] = out.get(lo, 0.0) + 1 - t
            if hi:
                out[hi] = out.get(hi, 0.0) + t
            break
    return {k: v for k, v in out.items() if v > 1e-6}


def age_value(years):
    """MakeHuman's age slider: 0 = 1 year, 0.1875 = 11, 0.5 = 25, 1 = 90."""
    y = max(1.0, min(90.0, float(years)))
    if y < 11:
        return (y - 1) / 10 * 0.1875
    if y < 25:
        return 0.1875 + (y - 11) / 14 * 0.3125
    return 0.5 + (y - 25) / 65 * 0.5


def macro_targets(gender, age, muscle, weight, races, proportions=0.6, height=0.5):
    """[(target path, weight)] for MakeHuman's macro sliders, combined as MakeHuman combines them."""
    T = os.path.join(BASE, "targets", "macrodetails")
    g = _parts(gender, (0, 1), ("female", "male"))
    a = _parts(age, (0, 0.1875, 0.5, 1), ("baby", "child", "young", "old"))
    m = _parts(muscle, (0, 0.5, 1), ("minmuscle", "averagemuscle", "maxmuscle"))
    w = _parts(weight, (0, 0.5, 1), ("minweight", "averageweight", "maxweight"))
    out = []
    for gk, gv in g.items():
        for ak, av in a.items():
            for race, rv in zip(("african", "asian", "caucasian"), races):
                if rv > 0:
                    out.append((os.path.join(T, f"{race}-{gk}-{ak}.target.gz"), rv * gv * av))
            for mk, mv in m.items():
                for wk, wv in w.items():
                    base = gv * av * mv * wv
                    out.append((os.path.join(T, f"universal-{gk}-{ak}-{mk}-{wk}.target.gz"), base))
                    p = _parts(proportions, (0, 0.5, 1), ("uncommonproportions", "", "idealproportions"))
                    for pk, pv in p.items():
                        out.append((os.path.join(T, "proportions", f"{gk}-{ak}-{mk}-{wk}-{pk}.target.gz"), base * pv))
                    h = _parts(height, (0, 0.5, 1), ("minheight", "", "maxheight"))
                    for hk, hv in h.items():
                        out.append((os.path.join(T, "height", f"{gk}-{ak}-{mk}-{wk}-{hk}.target.gz"), base * hv))
    return [(p, x) for p, x in out if x > 1e-4 and os.path.exists(p)]


FACE_PARTS = ("head", "nose", "mouth", "eyes", "chin", "cheek", "forehead", "eyebrows", "ears")


def face_targets(seed, amount):
    """A face of its own: small random pushes of MakeHuman's face sliders, the same for the same name."""
    if amount <= 0:
        return []
    meta = json.load(open(os.path.join(BASE, "targets", "target.json")))
    rng = random.Random(seed)
    out = []
    T = os.path.join(BASE, "targets")
    for part in FACE_PARTS:
        for cat in meta.get(part, {}).get("categories", []):
            opp = cat.get("opposites") or {}
            if rng.random() > 0.55:
                continue
            v = rng.gauss(0, 0.35) * amount
            v = max(-0.9, min(0.9, v))
            side = "positive" if v > 0 else "negative"
            names = [opp.get(f"{side}-unsided")] if opp.get(f"{side}-unsided") else \
                    [opp.get(f"{side}-left"), opp.get(f"{side}-right")]
            for nm in names:
                if not nm:
                    continue
                p = os.path.join(T, part, nm + ".target.gz")
                if os.path.exists(p):
                    out.append((p, abs(v)))
    return out


class Proxy:
    """Something fitted to the body (hair, clothes, eyes, brows...): a MakeHuman .mhclo file. Each of
    its vertices sits on a triangle of the body (three body vertices, weighted) plus an offset."""

    def __init__(self, path):
        self.path = path
        self.dir = os.path.dirname(path)
        self.header, self.delete = {}, set()
        refs, ws, offs = [], [], []
        in_verts = in_delete = False
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if not line:
                    continue
                p = line.split()
                if p[0] == "verts":
                    in_verts, in_delete = True, False
                    continue
                if p[0] == "delete_verts":
                    in_delete = True
                    continue
                if re.match(r"^-?\d", p[0]):
                    if in_delete:
                        i = 0
                        while i < len(p):
                            if i + 2 < len(p) and p[i + 1] == "-":
                                self.delete.update(range(int(p[i]), int(p[i + 2]) + 1))
                                i += 3
                            else:
                                self.delete.add(int(p[i]))
                                i += 1
                    elif in_verts and len(p) == 1:
                        refs.append([int(p[0])] * 3)
                        ws.append([1.0, 0.0, 0.0])
                        offs.append([0.0, 0.0, 0.0])
                    elif in_verts and len(p) >= 9:
                        refs.append([int(x) for x in p[:3]])
                        ws.append([float(x) for x in p[3:6]])
                        offs.append([float(x) for x in p[6:9]])
                    continue
                in_delete = False
                self.header.setdefault(p[0], []).append(p[1:])
        self.refs = np.array(refs, dtype=np.int64)
        self.w = np.array(ws, dtype=np.float64)
        self.off = np.array(offs, dtype=np.float64)
        obj = self.header.get("obj_file", [[None]])[0][0]
        self.obj = os.path.join(self.dir, obj) if obj else None
        mat = self.header.get("material", [[None]])[0][0]
        self.material = os.path.normpath(os.path.join(self.dir, mat)) if mat else None

    def scales(self, V):
        s = []
        for axis, name in enumerate(("x_scale", "y_scale", "z_scale")):
            spec = self.header.get(name)
            if spec:
                a, b, d = int(spec[0][0]), int(spec[0][1]), float(spec[0][2])
                s.append(abs(V[a, axis] - V[b, axis]) / d if d else 1.0)
            else:
                s.append(1.0)
        return np.array(s)

    def fit(self, V):
        """The proxy's vertices for body vertices V."""
        pts = (V[self.refs] * self.w[:, :, None]).sum(axis=1)
        return pts + self.off * self.scales(V)


def read_mhmat(path):
    """A MakeHuman material: {key: value} (textures as full paths)."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    d = os.path.dirname(path)
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", "//")):
                continue
            k, _, v = line.partition(" ")
            v = v.strip()
            if k.endswith("Texture") and v:
                v = os.path.normpath(os.path.join(d, v))
            out.setdefault(k, v)
    return out


def _find(kind, name):
    """A MakeHuman asset by kind (hair, eyebrows, clothes...) and name; None if it isn't there."""
    if not name or str(name).lower() in ("none", "no", "false", ""):
        return None
    folder = os.path.join(CACHE, kind, str(name))
    if os.path.isdir(folder):
        for f in sorted(os.listdir(folder)):
            if f.endswith(".mhclo"):
                return os.path.join(folder, f)
    return None


def catalog():
    """What's installed: {kind: [names]} (for the studio and the docs)."""
    out = {}
    for kind in ("hair", "eyebrows", "eyelashes", "clothes", "skins", "teeth"):
        d = os.path.join(CACHE, kind)
        out[kind] = sorted(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n))) if os.path.isdir(d) else []
    out["eyes"] = sorted(os.path.splitext(n)[0] for n in os.listdir(os.path.join(CACHE, "eyes", "materials"))
                         if n.endswith(".mhmat")) if os.path.isdir(os.path.join(CACHE, "eyes", "materials")) else []
    return out


# ---------------------------------------------------------------------- building a person
def _to_blender(V):
    """MakeHuman's decimetres, y up, facing +z -> Blender metres, z up, facing -y."""
    return np.stack([V[:, 0], -V[:, 2], V[:, 1]], axis=1) * 0.1


class Recipe:
    """Everything that decides how a person looks, from a cast spec."""

    def __init__(self, spec, name):
        g = spec.get("gender", "female")
        self.gender = float(g) if isinstance(g, (int, float)) else (1.0 if str(g).lower().startswith("m") else 0.0)
        self.age = float(spec.get("age", 30))
        weight, muscle = BUILD.get(str(spec.get("build", "average")).lower(), BUILD["average"])
        self.weight = float(spec.get("weight", weight))
        self.muscle = float(spec.get("muscle", muscle))
        h = str(spec.get("heritage", "mixed")).lower().replace(" ", "_").replace("-", "_")
        self.races, self.skin_race, tone = HERITAGE.get(h, HERITAGE["mixed"])
        self.skin_tone = spec.get("skin_tone") or tone
        self.skin = spec.get("skin")
        male = self.gender >= 0.5
        self.hair = spec.get("hair", "short02" if male else "long01")
        self.hair_color = spec.get("hair_color", "#2b1d16")
        self.eyes = spec.get("eyes", "brown")
        self.eyebrows = spec.get("eyebrows", "eyebrow001" if male else "eyebrow010")
        self.eyelashes = spec.get("eyelashes", "eyelashes01" if male else "eyelashes02")
        pick = random.Random(f"{name}/outfit")
        self.outfit = spec.get("outfit") or pick.choice(OUTFITS["male" if male else "female"])
        self.outfit_tint = spec.get("outfit_tint")
        self.shoes = spec.get("shoes", "shoes01" if male else "shoes02")
        self.extra = list(spec.get("wear", []) or [])
        self.face = float(spec.get("face", 0.5))
        self.seed = f"{name}/{spec.get('seed', '')}"

    def skin_file(self):
        if self.skin:
            p = os.path.join(CACHE, "skins", self.skin)
            if os.path.isdir(p):
                return next((os.path.join(p, f) for f in os.listdir(p) if f.endswith(".mhmat")), None)
        stage = "young" if self.age < 35 else "middleage" if self.age < 60 else "old"
        sex = "male" if self.gender >= 0.5 else "female"
        for race in (self.skin_race, "caucasian"):
            p = os.path.join(CACHE, "skins", f"{stage}_{race}_{sex}", f"{stage}_{race}_{sex}.mhmat")
            if os.path.exists(p):
                return p
        return None


def body_shape(recipe):
    """The body's vertices (all of them, helpers too), shaped by the recipe; MakeHuman units."""
    obj = os.path.join(BASE, "3dobjs", "base.obj")
    V, _, _, _ = _cached_base()
    V = V.copy()
    targets = macro_targets(recipe.gender, age_value(recipe.age), recipe.muscle, recipe.weight, recipe.races)
    targets += face_targets(recipe.seed, recipe.face)
    for path, w in targets:
        idx, d = _target(path)
        if len(idx):
            V[idx] += d * w
    del obj
    return V


_base = None


def _cached_base():
    global _base
    if _base is None:
        _base = _read_obj(os.path.join(BASE, "3dobjs", "base.obj"))
    return _base


def _face_units():
    """{shape key name: target path} for the ARKit face units and the visemes that are installed."""
    out = {}
    for n in ARKIT:
        p = os.path.join(CACHE, "targets", "faceunits", f"{n}.target")
        if os.path.exists(p):
            out[n] = p
    for v in VISEMES:
        p = os.path.join(CACHE, "targets", "visemes", f"viseme_{v}.target")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            out[f"viseme_{v}"] = p
    return out


def _mesh(name, verts, faces, uvs=None, face_uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    if uvs is not None and face_uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        flat = []
        for fu in face_uvs:
            for t in fu:
                flat.extend(uvs[t] if t >= 0 else (0.0, 0.0))
        layer.data.foreach_set("uv", flat)
    me.validate(clean_customdata=False)
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    for p in me.polygons:
        p.use_smooth = True
    return obj


def build(spec, name):
    """Make the person in the current scene: (armature, [meshes])."""
    if not installed():
        raise ValueError("MakeHuman's assets aren't downloaded: run `dreamreel assets --pack humans`")
    r = Recipe(spec, name)
    V0, uvs, faces, groups = _cached_base()
    V = body_shape(r)
    proxies = {}
    for role, kind, nm in (("eyes", "eyes", "high-poly"), ("eyebrows", "eyebrows", r.eyebrows),
                           ("eyelashes", "eyelashes", r.eyelashes), ("teeth", "teeth", "teeth_base"),
                           ("tongue", "tongue", "tongue01"), ("hair", "hair", r.hair),
                           ("outfit", "clothes", r.outfit), ("shoes", "clothes", r.shoes)):
        p = _find(kind, nm)
        if p:
            proxies[role] = Proxy(p)
    for i, extra in enumerate(r.extra):
        p = _find("clothes", extra)
        if p:
            proxies[f"wear{i}"] = Proxy(p)
    # the body: its own faces only (not the helpers), minus what clothes cover completely
    hidden = set()
    for role in ("outfit", "shoes") + tuple(k for k in proxies if k.startswith("wear")):
        if role in proxies:
            hidden |= proxies[role].delete
    keep = [i for i, (fv, _) in enumerate(faces) if groups[i] == "body" and not all(v in hidden for v in fv)]
    used = sorted({v for i in keep for v in faces[i][0]})
    remap = {v: k for k, v in enumerate(used)}
    body = _mesh(f"{name}.body", _to_blender(V[used]), [[remap[v] for v in faces[i][0]] for i in keep],
                 uvs, [faces[i][1] for i in keep])
    body.data.materials.append(_skin_material(r, name))
    meshes = [(body, np.array(used), None)]
    for role, px in proxies.items():
        verts, puvs, pfaces, _ = _read_obj(px.obj)
        fitted = px.fit(V)
        o = _mesh(f"{name}.{role}", _to_blender(fitted), [f for f, _ in pfaces], puvs, [t for _, t in pfaces])
        o.data.materials.append(_proxy_material(px, role, r, name))
        meshes.append((o, None, px))
    _face_keys(meshes, V)
    arm = _rig(name, V, meshes)
    return arm, [m for m, _, _ in meshes]


def _face_keys(meshes, V):
    """The 52 ARKit face units and 15 visemes as shape keys on the body, and on every part that
    sits on the face (brows, lashes, eyes, teeth, tongue), so they move together."""
    units = _face_units()
    if not units:
        return
    for obj, used, px in meshes:
        obj.shape_key_add(name="Basis", from_mix=False)
    for name, path in units.items():
        idx, d = _target(path)
        if not len(idx):
            continue
        D = np.zeros_like(V)
        D[idx] = d
        moved = set(idx.tolist())
        for obj, used, px in meshes:
            if px is None:
                co = _to_blender(V[used] + D[used])
                if not np.any(np.abs(D[used]) > 1e-7):
                    continue
            else:
                if not moved.intersection(px.refs[:, 0].tolist()) and not moved.intersection(px.refs[:, 1].tolist()):
                    continue
                co = _to_blender(px.fit(V + D))
            kb = obj.shape_key_add(name=name, from_mix=False)
            kb.value = 0.0
            kb.slider_max = 1.5 if not name.startswith("viseme") else 1.0
            kb.data.foreach_set("co", co.ravel())


def _rig(name, V, meshes):
    """A skeleton with Mixamo's bone names, placed on this body's joints; the skin weighted as
    MakeHuman weights it (parts on the body take the weights of the body under them)."""
    rig = json.load(open(os.path.join(BASE, "rigs", "standard", "rig.mixamo.json")))["bones"]
    wts = json.load(open(os.path.join(BASE, "rigs", "standard", "weights.mixamo.json")))["weights"]
    _, _, faces, groups = _cached_base()
    joint = {}
    for (fv, _), g in zip(faces, groups):
        if g.startswith("joint-"):
            joint.setdefault(g, set()).update(fv)
    B = _to_blender(V)

    def where(spec):
        s = spec["strategy"]
        if s == "CUBE":
            vs = sorted(joint.get(spec["cube_name"], ()))
            if vs:
                return B[vs].mean(axis=0)
        elif s in ("MEAN", "VERTEX"):
            vs = spec.get("vertex_indices") or [spec.get("vertex_index")]
            vs = [v for v in vs if v is not None]
            if vs:
                return B[vs].mean(axis=0)
        return np.array(spec.get("default_position", (0, 0, 0)))

    data = bpy.data.armatures.new(f"{name}.skeleton")
    arm = bpy.data.objects.new(f"{name}.skeleton", data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for bname, b in rig.items():
        e = data.edit_bones.new(bname)
        e.head, e.tail = where(b["head"]), where(b["tail"])
        if (e.tail - e.head).length < 1e-4:
            e.tail = e.head + type(e.head)((0, 0, 0.01))
        e.roll = b.get("roll", 0.0)
        eb[bname] = e
    for bname, b in rig.items():
        if b.get("parent") in eb:
            eb[bname].parent = eb[b["parent"]]
            eb[bname].use_connect = bool(b.get("use_connect")) and (eb[bname].head - eb[b["parent"]].tail).length < 1e-4
    bpy.ops.object.mode_set(mode="OBJECT")
    # weights on the base body
    n = len(V)
    bones = list(wts)
    W = np.zeros((n, len(bones)), dtype=np.float32)
    for j, bname in enumerate(bones):
        for v, w in wts[bname]:
            if v < n:
                W[v, j] = w
    # helper vertices clothes and shoes sit on may have no weights: they take the nearest weighted one's
    from mathutils.kdtree import KDTree
    weighted = np.nonzero(W.sum(axis=1) > 1e-6)[0]
    bare = np.nonzero(W.sum(axis=1) <= 1e-6)[0]
    if len(bare) and len(weighted):
        tree = KDTree(len(weighted))
        for i, v in enumerate(weighted.tolist()):
            tree.insert(V[v], i)
        tree.balance()
        for v in bare.tolist():
            _, i, _ = tree.find(V[v])
            W[v] = W[weighted[i]]
    for obj, used, px in meshes:
        if px is None:
            Wm = W[used]
        else:
            # the triangle's weights can be negative (a point just beyond the triangle): for skinning
            # only the positive parts count, so they can't cancel out to nothing
            pw = np.clip(px.w, 0.0, None)
            pw = np.where(pw.sum(axis=1, keepdims=True) > 1e-6, pw, np.abs(px.w) + 1e-6)
            Wm = (W[px.refs] * pw[:, :, None].astype(np.float32)).sum(axis=1)
        tot = Wm.sum(axis=1, keepdims=True)
        Wm = np.where(tot > 1e-6, Wm / np.maximum(tot, 1e-6), 0)
        for j, bname in enumerate(bones):
            col = Wm[:, j]
            nz = np.nonzero(col > 1e-3)[0]
            if len(nz):
                g = obj.vertex_groups.new(name=bname)
                for v in nz.tolist():
                    g.add([v], float(col[v]), "REPLACE")
        mod = obj.modifiers.new("skeleton", "ARMATURE")
        mod.object = arm
        obj.parent = arm
    return arm


# ---------------------------------------------------------------------- materials
def _image(path, data=False):
    img = bpy.data.images.load(path, check_existing=True)
    if data:
        img.colorspace_settings.name = "Non-Color"
    return img


def _principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    return mat, nt, next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")


def _set(bsdf, k, v):
    s = bsdf.inputs.get(k)
    if s is not None:
        s.default_value = v


def _skin_material(r, name):
    """Skin from a MakeHuman photo skin, recoloured to the skin tone; light scatters under it;
    fine pores; a little oil on the T-zone."""
    from . import look
    mat, nt, bsdf = _principled(f"{name} skin")
    mat["dr_real"] = True
    mat["dr_kind"] = "skin"
    path = r.skin_file()
    mh = read_mhmat(path)
    tone = look.rgb(r.skin_tone)
    tex = None
    if mh.get("diffuseTexture") and os.path.exists(mh["diffuseTexture"]):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _image(mh["diffuseTexture"])
        mean = _mean(tex.image)
        k = nt.nodes.new("ShaderNodeVectorMath")
        k.operation = "MULTIPLY"
        k.inputs[1].default_value = tuple(t / m for t, m in zip(tone, mean))
        nt.links.new(tex.outputs["Color"], k.inputs[0])
        nt.links.new(k.outputs[0], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (*tone, 1)
    _set(bsdf, "Subsurface Weight", 1.0)
    _set(bsdf, "Subsurface Radius", (1.0, 0.35, 0.18))
    _set(bsdf, "Subsurface Scale", 0.004)
    _set(bsdf, "Roughness", 0.48)
    _set(bsdf, "Specular IOR Level", 0.42)
    _set(bsdf, "Coat Weight", 0.05)
    _set(bsdf, "Coat Roughness", 0.3)
    _set(bsdf, "Sheen Weight", 0.05)
    co = nt.nodes.new("ShaderNodeTexCoord")
    pores = nt.nodes.new("ShaderNodeTexVoronoi")
    pores.inputs["Scale"].default_value = 2200.0
    nt.links.new(co.outputs["Object"], pores.inputs["Vector"])
    fine = nt.nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 600.0
    fine.inputs["Detail"].default_value = 6.0
    nt.links.new(co.outputs["Object"], fine.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(pores.outputs["Distance"], add.inputs[0])
    nt.links.new(fine.outputs["Fac"], add.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.0003
    nt.links.new(add.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _mean(img):
    """An image's average colour (linear)."""
    small = img.copy()
    small.scale(32, 32)
    px = np.array(small.pixels[:]).reshape(-1, 4)
    bpy.data.images.remove(small)
    srgb = px[:, :3]
    lin = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
    a = px[:, 3:4]
    m = (lin * a).sum(axis=0) / max(1e-6, a.sum())
    return tuple(max(1e-3, x) for x in m)


def _recolor(nt, tex, want, keep=0.0):
    """A texture in another colour: its brightness (relative to its average, capped so faint
    edges don't glow) times the colour wanted; `keep` mixes back some of its own colour."""
    mean = _mean(tex.image)
    mlum = max(1e-3, 0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tex.outputs["Color"], bw.inputs[0])
    rel = nt.nodes.new("ShaderNodeMath")
    rel.operation = "MULTIPLY"
    rel.use_clamp = False
    rel.inputs[1].default_value = 1.0 / mlum
    nt.links.new(bw.outputs[0], rel.inputs[0])
    cap = nt.nodes.new("ShaderNodeMath")
    cap.operation = "MINIMUM"
    cap.inputs[1].default_value = 1.8
    nt.links.new(rel.outputs[0], cap.inputs[0])
    k = nt.nodes.new("ShaderNodeVectorMath")
    k.operation = "SCALE"
    k.inputs[0].default_value = want
    nt.links.new(cap.outputs[0], k.inputs["Scale"])
    if not keep:
        return k.outputs[0]
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = keep
    nt.links.new(k.outputs[0], mix.inputs[6])
    nt.links.new(tex.outputs["Color"], mix.inputs[7])
    return mix.outputs[2]


def _proxy_material(px, role, r, name):
    """Hair, brows, lashes, eyes, teeth and clothes from their MakeHuman materials, made real:
    alpha-cut hair cards with a sheen, wet eyes, fabric with its normal map."""
    from . import look
    mh = read_mhmat(px.material)
    mat, nt, bsdf = _principled(f"{name} {role}")
    mat["dr_real"] = True
    mat["dr_kind"] = {"eyes": "eye", "eyebrows": "hair", "eyelashes": "hair", "hair": "hair",
                      "teeth": "porcelain", "tongue": "skin"}.get(role, "fabric")
    diff = mh.get("diffuseTexture")
    tex = None
    if diff and os.path.exists(diff):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _image(diff)
        color = tex.outputs["Color"]
        if role in ("hair", "eyebrows", "eyelashes"):
            # brows and lashes are darker than the hair on the head
            dark = {"hair": 0.0, "eyebrows": 0.45, "eyelashes": 0.75}[role]
            want = tuple(h * (1 - dark) + d * dark for h, d in zip(look.rgb(r.hair_color), look.rgb("#1d1714")))
            color = _recolor(nt, tex, want)
        elif role in ("outfit",) and r.outfit_tint:
            color = _recolor(nt, tex, look.rgb(r.outfit_tint), keep=0.25)
        nt.links.new(color, bsdf.inputs["Base Color"])
        if mh.get("transparent", "False").lower() == "true" or role in ("hair", "eyebrows", "eyelashes"):
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "DITHERED"
            if hasattr(mat, "blend_method"):
                try:
                    mat.blend_method = "HASHED"
                except TypeError:
                    pass
            mat.use_backface_culling = False
    nrm = mh.get("normalmapTexture")
    if nrm and os.path.exists(nrm):
        nt_tex = nt.nodes.new("ShaderNodeTexImage")
        nt_tex.image = _image(nrm, data=True)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(nt_tex.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if role == "eyes":
        if r.eyes:
            mh2 = read_mhmat(os.path.join(CACHE, "eyes", "materials", f"{r.eyes}.mhmat"))
            if tex is not None and mh2.get("diffuseTexture") and os.path.exists(mh2["diffuseTexture"]):
                tex.image = _image(mh2["diffuseTexture"])
        _set(bsdf, "Roughness", 0.05)
        _set(bsdf, "Coat Weight", 1.0)
        _set(bsdf, "Coat Roughness", 0.0)
        _set(bsdf, "Subsurface Weight", 0.2)
        _set(bsdf, "Subsurface Scale", 0.002)
    elif role in ("hair", "eyebrows", "eyelashes"):
        _set(bsdf, "Roughness", 0.5)
        _set(bsdf, "Specular IOR Level", 0.22)
        _set(bsdf, "Anisotropic", 0.5)
        _set(bsdf, "Sheen Weight", 0.0)
    elif role == "teeth":
        _set(bsdf, "Roughness", 0.2)
        _set(bsdf, "Subsurface Weight", 0.4)
        _set(bsdf, "Subsurface Scale", 0.002)
    elif role == "tongue":
        _set(bsdf, "Roughness", 0.3)
        _set(bsdf, "Subsurface Weight", 0.6)
        _set(bsdf, "Subsurface Scale", 0.003)
    else:
        _set(bsdf, "Roughness", 0.8)
        _set(bsdf, "Sheen Weight", 0.3)
        _set(bsdf, "Specular IOR Level", 0.35)
    return mat


# ---------------------------------------------------------------------- the character
from .keys import key  # noqa: E402
from .models import ModelCharacter  # noqa: E402
from .plugins import Param  # noqa: E402

# Rhubarb's mouth shapes as visemes (the 15 mouth shapes of speech): {letter: {viseme: weight}}
LETTER_VISEMES = {
    "X": {"sil": 1.0}, "A": {"PP": 1.0}, "B": {"SS": 0.6, "I": 0.4}, "C": {"E": 1.0}, "D": {"aa": 1.0},
    "E": {"O": 0.8, "RR": 0.2}, "F": {"U": 1.0}, "G": {"FF": 1.0}, "H": {"nn": 0.6, "DD": 0.4},
}


class Human(ModelCharacter):
    """A realistic person built from MakeHuman's assets (see the module docs)."""
    name = "human"
    label = "Realistic person"
    description = "A realistic person: any age, build and heritage, real skin, hair and clothes, and a face that acts"
    drawing = None
    params = [
        Param("name", "text", label="Name"),
        Param("gender", "choice", default="female", choices=("female", "male")),
        Param("age", "number", default=30, min=5, max=90, step=1, label="Age (years)"),
        Param("build", "choice", default="average", choices=tuple(BUILD)),
        Param("heritage", "choice", default="south_asian", choices=tuple(HERITAGE)),
        Param("skin_tone", "color", default=None, label="Skin tone (optional)"),
        Param("hair", "choice", default=None, choices=("afro01", "bob01", "bob02", "braid01", "long01", "ponytail01",
                                                          "short01", "short02", "short03", "short04", "none")),
        Param("hair_color", "color", default="#2b1d16", label="Hair colour"),
        Param("eyes", "choice", default="brown", choices=("brown", "brownlight", "blue", "bluegreen", "deepblue",
                                                          "green", "grey", "ice", "lightblue")),
        Param("outfit", "choice", default=None, choices=tuple(sorted(set(OUTFITS["female"] + OUTFITS["male"]
                                                                        + ["female_casualsuit01", "female_sportsuit01",
                                                                           "male_casualsuit02", "male_casualsuit04",
                                                                           "male_casualsuit06", "male_elegantsuit01",
                                                                           "male_worksuit01"])))),
        Param("outfit_tint", "color", default=None, label="Outfit colour (optional)"),
        Param("shoes", "choice", default=None, choices=("shoes01", "shoes02", "shoes03", "shoes04", "shoes05", "shoes06")),
        Param("face", "number", default=0.5, min=0, max=1, step=0.05, label="Face: how distinctive"),
        Param("height", "number", default=None, min=0.8, max=2.2, step=0.01, label="Height (m)"),
        Param("voice", "voice"),
    ]
    default_capabilities = ("walk", "arms", "swing_legs", "face")
    bends = True

    @classmethod
    def stand_in(cls, spec):
        """A toy figure plays the part while MakeHuman's assets aren't downloaded."""
        if installed():
            return None
        male = str(spec.get("gender", "female")).lower().startswith("m")
        toy = {k: spec[k] for k in ("name", "voice") if k in spec}
        toy.update(type="toy", hair="short" if male else "long", height=float(spec.get("height") or (1.76 if male else 1.63)))
        if spec.get("skin_tone"):
            toy["skin"] = spec["skin_tone"]
        return "toy", toy

    def validate(self):
        if not installed():
            raise ValueError(f"{self.name}: realistic people need MakeHuman's assets: `dreamreel assets --pack humans`")

    def proportions(self):
        male = str(self.spec.get("gender", "female")).lower().startswith("m")
        age = float(self.spec.get("age", 30))
        grown = 1.76 if male else 1.63
        default = grown * (min(1.0, 0.47 + 0.53 * (age - 1) / 17) if age < 18 else 1.0)
        self.H = float(self.spec.get("height") or default)

    def _path(self):
        return None

    def _load(self):
        return build(self.spec, self.name)

    # ------------------------------------------------------------------ talking with visemes
    def _viseme_keys(self):
        out = {}
        for mesh in self.meshes:
            ks = mesh.data.shape_keys
            if ks is None:
                continue
            for kb in ks.key_blocks:
                if kb.name.startswith("viseme_"):
                    out.setdefault(kb.name[7:], []).append(kb)
        return out

    def _lipsync_audio(self, t0, speech):
        """Real mouth shapes for the sounds of speech (visemes); with an AI face reading (lipsync =
        "ai" and a booster), the whole face moves with the voice as well."""
        mode = self.scene.voices.lipsync
        if mode == "ai":
            frames = speech.face_frames()
            if frames:
                self._play_face(t0, frames, speech.duration)
                return
        letters = speech.letters() if mode in ("sounds", "ai") else None
        vis = self._viseme_keys()
        if not letters or not vis:
            return super()._lipsync_audio(t0, speech)
        last = None
        self._visemes_at(t0 - 0.06, {"sil": 1.0}, vis)
        for start, letter in letters:
            t = t0 + start
            if last is not None and t - last < 0.035:
                continue
            want = LETTER_VISEMES.get(letter, LETTER_VISEMES["X"])
            self._visemes_at(t, want, vis)
            last = t
        self._visemes_at(t0 + speech.duration + 0.05, {"sil": 1.0}, vis)

    def _visemes_at(self, t, want, vis):
        for name, kbs in vis.items():
            for kb in kbs:
                key(kb, "value", t, float(want.get(name, 0.0)) * (0.0 if name == "sil" else 1.0))

    def _play_face(self, t0, frames, duration):
        """Key the AI's reading of the face (52 ARKit weights per frame) on the face's AI stand-in:
        it adds to the mood, so a sad character stays sad while the voice moves the face."""
        ai = getattr(self, "face_ai", None)
        if ai is None:
            return
        kbs = ai.data.shape_keys.key_blocks
        step = 1.0 / self.scene.fps
        last = -1.0
        for t, weights in frames:
            if t - last < step * 0.99:
                continue
            last = t
            for nm, w in weights.items():
                kb = kbs.get(nm)
                if kb is not None:
                    key(kb, "value", t0 + t, max(0.0, min(1.0, float(w))), "linear")
        for kb in kbs[1:]:
            key(kb, "value", t0 + duration + 0.1, 0.0)
