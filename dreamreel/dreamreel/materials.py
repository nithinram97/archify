"""Real materials: in the realistic look, everything looks like what it is made of.

Floors, walls, furniture, buildings, roads, grass, bark, rocks, cars, clothes, animals' fur and
people's skin each get the surface of the real thing: a photo-scanned texture (its colour, how
rough or shiny it is from place to place, and its relief), at its real size. Textures come from
ambientCG and Poly Haven, both CC0 (free for any use, no credit needed); they are downloaded the
first time a material needs them and kept in ~/.cache/dreamreel/materials (`dreamreel assets
--pack materials` fetches them all at once). Without them (offline), surfaces get a procedural
finish instead.

What a surface is made of is worked out from names (a Quaternius "Wood" material, a set's
"floor", a person's "Casual_Legs", a "car"), so imported models and packs come out right too. A
texture keeps the colour the film gave the thing: a teal cup stays teal, only now it is glazed
porcelain. Each object gets the pattern at a different place, so a row of benches isn't a row of
copies, and patterns are pinned to the object, so they don't slide as a character moves.
"""
import json
import math
import os
import re
import urllib.request
import zipfile

import bpy
from mathutils import Vector

from . import look

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "materials")
RES = os.environ.get("DREAMREEL_TEXTURES", "1K")       # 1K, 2K or 4K
UA = {"User-Agent": "dreamreel material fetcher"}

# kind: where its texture comes from and how it is used.
#   src     ("acg", id) ambientCG, ("ph", id) Poly Haven, or None for a procedural surface
#   size    metres one tile covers (default: the library's own measurement)
#   color   "tint": the film's colour, with the texture's light and dark; "natural": the texture's
#           own colour, nudged towards the film's; "keep": the texture's colour
#   bump    how strongly the relief shows; rough: (low, high) roughness range; metal: metallic
KINDS = {
    "wood_floor": dict(src=("acg", "WoodFloor051"), color="natural", bump=0.35, size=2.0),
    "wood": dict(src=("acg", "Wood049"), color="natural", bump=0.2, size=1.2),
    "painted_wood": dict(src=("acg", "Wood049"), color="paint", bump=0.12, rough=(0.3, 0.5), size=1.2),
    "plaster": dict(src=("acg", "PaintedPlaster017"), color="tint", bump=0.3, size=2.0),
    "brick": dict(src=("acg", "Bricks059"), color="natural", bump=0.9),
    "brick_pale": dict(src=("acg", "Bricks060"), color="natural", bump=0.9),
    "concrete": dict(src=("acg", "Concrete036"), color="natural", bump=0.4),
    "asphalt": dict(src=("acg", "Asphalt031"), color="natural", bump=0.5, size=3.0),
    "paving": dict(src=("acg", "PavingStones070"), color="natural", bump=0.8),
    "roof": dict(src=("acg", "RoofingTiles006"), color="natural", bump=0.9),
    "tiles": dict(src=("acg", "Tiles107"), color="tint", bump=0.5, rough=(0.08, 0.3)),
    "granite": dict(src=("acg", "Granite005A"), color="natural", bump=0.1, rough=(0.1, 0.25)),
    "metal": dict(src=("acg", "Metal009"), color="tint", bump=0.1, metal=1.0, rough=(0.2, 0.45)),
    "chrome": dict(src=("acg", "Metal012"), color="keep", bump=0.05, metal=1.0, rough=(0.03, 0.15)),
    "painted_metal": dict(src=("acg", "SurfaceImperfections003"), color="tint", bump=0.05, rough=(0.3, 0.55), size=1.0,
                          detail_only=True),
    "fabric": dict(src=("acg", "Fabric030"), color="tint", bump=0.6, rough=(0.75, 0.95), size=0.4),
    "cotton": dict(src=("ph", "cotton_jersey"), color="tint", bump=0.5, rough=(0.8, 0.95), size=0.5),
    "denim": dict(src=("ph", "denim_fabric_03"), color="tint", bump=0.6, rough=(0.75, 0.95), size=0.5),
    "linen": dict(src=("ph", "rough_linen"), color="tint", bump=0.5, rough=(0.75, 0.95), size=0.5),
    "corduroy": dict(src=("ph", "ribbed_corduroy"), color="tint", bump=0.6, rough=(0.8, 0.95), size=0.5),
    "leather": dict(src=("ph", "brown_leather"), color="tint", bump=0.4, rough=(0.3, 0.6), size=0.6),
    "carpet": dict(src=("acg", "Carpet016"), color="tint", bump=0.8, rough=(0.85, 1.0), size=1.0),
    "grass": dict(src=("acg", "Grass004"), color="natural", bump=0.6, size=2.0, rough=(0.75, 1.0)),
    "ground": dict(src=("acg", "Ground037"), color="natural", bump=0.6, size=3.0, rough=(0.75, 1.0)),
    "gravel": dict(src=("acg", "Gravel023"), color="natural", bump=0.8, size=1.5, rough=(0.7, 1.0)),
    "sand": dict(src=("acg", "Ground054"), color="natural", bump=0.6, size=2.0, rough=(0.75, 1.0)),
    "rock": dict(src=("acg", "Rock030"), color="natural", bump=1.0, size=2.0),
    "bark": dict(src=("acg", "Bark014"), color="natural", bump=1.0, size=1.0),
    "leaves": dict(src=("acg", "ScatteredLeaves009"), color="tint", bump=0.8, size=0.8, foliage=True),
    "porcelain": dict(src=("acg", "Porcelain001"), color="tint", bump=0.05, rough=(0.04, 0.12), size=0.4),
    "paper": dict(src=("acg", "Paper001"), color="tint", bump=0.2, rough=(0.7, 0.9), size=0.4),
    "cardboard": dict(src=("acg", "Cardboard002"), color="natural", bump=0.3, size=0.6),
    "wicker": dict(src=("acg", "Wicker004"), color="natural", bump=0.9, size=0.4),
    "fur": dict(src=("ph", "polar_fleece"), color="tint", bump=0.7, rough=(0.6, 0.85), size=0.25, fur=True),
    # procedural surfaces
    "skin": dict(src=None), "hair": dict(src=None), "eye": dict(src=None), "glass": dict(src=None),
    "car_paint": dict(src=None), "rubber": dict(src=None), "baked": dict(src=None), "wax": dict(src=None),
    "petals": dict(src=None), "frosting": dict(src=None), "plastic": dict(src=None),
}

# what a surface is made of, from its material's name (first match wins)
BY_MATERIAL = [
    (r"headlight|taillight|bulb|flame|glow|emiss|screen|fakeinterior|interior|sky|outline|fog", None),
    (r"glass|window(s)?$|windshield|lens", "glass"),
    (r"skin|face|body_skin", "skin"),
    (r"hair|eyebrow|\bbrows?\b|beard|mustache|lash", "hair"),
    (r"eye|pupil|iris|sclera", "eye"),
    (r"bark|trunk", "bark"),
    (r"lea(f|ves)|foliage|plant_green|needles|bush", "leaves"),
    (r"grass", "grass"),
    (r"flower|petal", "petals"),
    (r"rock|stone|boulder|cliff", "rock"),
    (r"wood_dark|darkwood", "wood"),
    (r"floorboard|parquet|woodfloor", "wood_floor"),
    (r"wood|plank|log", "wood"),
    (r"brick.*pale|pale.*brick|whitebrick", "brick_pale"),
    (r"brick", "brick"),
    (r"trim_metalconcrete|concrete|cement", "concrete"),
    (r"asphalt|tarmac|road", "asphalt"),
    (r"pav(ing|ement)|sidewalk|cobble", "paving"),
    (r"roof", "roof"),
    (r"trim_dark|trim_green|railing|painted_metal", "painted_metal"),
    (r"trim", "painted_wood"),
    (r"kitchentop|countertop|worktop|granite", "granite"),
    (r"marble", "granite"),
    (r"kitchen|cabinet|cupboard", "painted_wood"),
    (r"tile", "tiles"),
    (r"chrome|silver|steel|alumin|iron|metal", "metal"),
    (r"gold|brass|copper", "metal"),
    (r"cushion|cushin|sofa|fabric|cloth|curtain|pillow|blanket|towel", "fabric"),
    (r"carpet|rug", "carpet"),
    (r"leather", "leather"),
    (r"denim|jean", "denim"),
    (r"rubber|tyre|tire", "rubber"),
    (r"ground|dirt|soil|mud", "ground"),
    (r"gravel", "gravel"),
    (r"sand", "sand"),
    (r"paper|book", "paper"),
    (r"ceramic|porcelain|plate|cup|mug", "porcelain"),
]
# ... else from the object's name
BY_OBJECT = [
    (r"\.(glint|blush|tear|sweat|lips|mouthkeys|lidkeys|eyeline)|^fx\.|bulb|flame|\.view$|sky|stars|disc", None),
    (r"\.road|^road", "asphalt"),
    (r"\.path|^path|pavement|sidewalk|kerb|curb", "paving"),
    (r"^floor", "wood_floor"),
    (r"^ground|terrain", "grass"),
    (r"^skirting|^door|^window|^shelf|^bookshelf|^wardrobe|^counter|^fridge.door", "painted_wood"),
    (r"^wall|ceiling", "plaster"),
    (r"^(table|chair|desk|bed|bench|stool|crate|barrel|frame|easel)", "wood"),
    (r"^(plate|cup|mug|bowl|vase|teapot)", "porcelain"),
    (r"^(cookie|bread|cake|pie|biscuit|bun|toast|pizza)", "baked"),
    (r"candle", "wax"),
    (r"^(book|letter|paper|newspaper|poster|painting)", "paper"),
    (r"^(box|parcel|carton)", "cardboard"),
    (r"^(streetlamp|lamp|pole|sign|fence|gate|railing|bin|bike|tool|scalpel|laptop|tv|television|fridge|clock)", "painted_metal"),
    (r"^(rug|carpet|mat)", "carpet"),
    (r"^(sofa|cushion|pillow|curtain|blanket)", "fabric"),
    (r"^(rock|stone|boulder|cliff)", "rock"),
    (r"^(tree|streettree|log)", "bark"),
    (r"^(house|building)", "plaster"),
    (r"^(plant|pot|planter)", "plaster"),
    (r"^(ball)", "rubber"),
    (r"^(jar|bottle|beaker)", "glass"),
]
# a character's or a vehicle's parts: what clothes, bodies and car bodies are made of
CHARACTER_PARTS = [
    (r"\.(glint|blush|tear|sweat|lips|mouth|mouthkeys|lidkeys|mouthpivot)", None),
    (r"\.(eye|white|pupil|iris|gaze|eyeline)", "eye"),
    (r"\.(teeth|braces)", "porcelain"),
    (r"\.(brow|lash)", "hair"),
]
CLOTHES = [
    (r"legs|pants|trouser|jean|short|skirt", "denim"),
    (r"feet|shoe|boot|sandal", "leather"),
    (r"hat|cap|head", "cotton"),
    (r"body|shirt|top|torso|dress|jacket|coat|hood|sweater|arm|sleeve", "cotton"),
]


def _norm(s):
    return re.sub(r"\.\d+$", "", s or "").lower()


def classify(obj, mat, owner=None):
    """What a surface is made of: a KINDS key, or None to leave it as it is. `owner` is the
    character class name ("Animal", "Person", "ToyFigure", ...) or "car" for vehicles."""
    m, o = _norm(mat.name), _norm(obj.name)
    if "dr_material" in mat:                 # set by a model or a film: what it's made of
        return mat["dr_material"] or None
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if mat.use_nodes else None
    if bsdf is None:
        return None
    em = bsdf.inputs.get("Emission Strength")
    if em is not None and em.default_value > 0.05 and not bsdf.inputs["Emission Color"].is_linked:
        return None
    tr = bsdf.inputs.get("Transmission Weight")
    if tr is not None and tr.default_value > 0.5:
        return "glass"
    if owner is not None and owner != "car":           # a character: skin, hair and eyes first
        for pat, kind in BY_MATERIAL[:6]:
            if re.search(pat, m):
                return kind
    if owner == "Animal":
        if re.search(r"eye|pupil|iris", m):
            return "eye"
        if re.search(r"horn|hoof|antler|nose", m):
            return "plastic"
        return "fur"
    if owner == "car":
        lum = _luminance(bsdf)
        if re.search(r"window|glass", m):
            return "glass"
        if lum < 0.03:
            return "rubber"
        if re.search(r"grey|gray|silver|chrome|rim|wheel", m) or "metal" in m:
            return "chrome"
        return "car_paint"
    if owner in ("Person", "ToyFigure", "Human") or owner and owner.endswith("Character"):
        part = o + " " + m
        for pat, kind in CHARACTER_PARTS:
            if re.search(pat, o):
                return kind
        for pat, kind in CLOTHES:
            if re.search(pat, part):
                if kind == "denim" and not _bluish(bsdf):
                    kind = "corduroy" if _luminance(bsdf) < 0.08 else "linen"
                if kind == "leather" and _luminance(bsdf) > 0.5:
                    kind = "fabric"                   # white trainers
                return kind
        return "cotton"
    # dreamreel's own materials are named after their colour ("plastic wood", "matte #a9a196"):
    # for those, what the object is decides first; a pack's material names its substance
    generic = re.match(r"^(plastic|matte) ", m) is not None
    for rules, text in (((BY_OBJECT, o), (BY_MATERIAL, m)) if generic else ((BY_MATERIAL, m), (BY_OBJECT, o))):
        for pat, kind in rules:
            if re.search(pat, text):
                return kind
    return "plastic"


def _base_color(bsdf):
    c = bsdf.inputs["Base Color"].default_value
    return (c[0], c[1], c[2])


def _luminance(bsdf):
    r, g, b = _base_color(bsdf)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _bluish(bsdf):
    r, g, b = _base_color(bsdf)
    return b > r * 1.15 and b > 0.02


# ---------------------------------------------------------------------- textures
def _get(url, dest):
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    os.replace(tmp, dest)


def _json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


MAPS = ("color", "roughness", "displacement", "ao", "metalness", "opacity")


def fetch(src, download=True):
    """A texture set on disk: {"maps": {map: path}, "size": metres across}, or None (offline)."""
    lib, ident = src
    folder = os.path.join(CACHE, f"{ident}_{RES}")
    meta_path = os.path.join(folder, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return json.load(f)
    if not download:
        return None
    os.makedirs(folder, exist_ok=True)
    maps, size = {}, 1.0
    try:
        if lib == "acg":
            info = _json(f"https://ambientcg.com/api/v2/full_json?id={ident}&include=dimensionsData")
            a = info["foundAssets"][0]
            size = max(a.get("dimensionX") or 100, a.get("dimensionY") or 100) / 100.0
            z = os.path.join(folder, "maps.zip")
            _get(f"https://ambientcg.com/get?file={ident}_{RES}-JPG.zip", z)
            names = {"_color": "color", "_roughness": "roughness", "_displacement": "displacement",
                     "_ambientocclusion": "ao", "_metalness": "metalness", "_opacity": "opacity"}
            with zipfile.ZipFile(z) as zf:
                for n in zf.namelist():
                    low = os.path.splitext(n)[0].lower()
                    for suffix, role in names.items():
                        if low.endswith(suffix):
                            zf.extract(n, folder)
                            maps[role] = os.path.join(folder, n)
            os.remove(z)
        else:
            info = _json(f"https://api.polyhaven.com/info/{ident}")
            dims = info.get("dimensions") or [1000, 1000]
            size = max(dims) / 1000.0
            files = _json(f"https://api.polyhaven.com/files/{ident}")
            res = RES.lower()
            for key, role in (("Diffuse", "color"), ("Rough", "roughness"), ("Displacement", "displacement"),
                              ("AO", "ao")):
                entry = files.get(key, {}).get(res) or files.get(key, {}).get("1k")
                if not entry:
                    continue
                url = (entry.get("jpg") or entry.get("png") or {}).get("url")
                if not url:
                    continue
                path = os.path.join(folder, f"{role}{os.path.splitext(url)[1]}")
                _get(url, path)
                maps[role] = path
    except (OSError, ValueError, KeyError, IndexError, zipfile.BadZipFile) as e:
        print(f"[dreamreel] couldn't fetch the {ident} texture ({e}); using a procedural surface")
        return None
    if not maps:
        return None
    meta = {"maps": maps, "size": size, "mean": _mean_color(maps["color"]) if "color" in maps else [0.5] * 3}
    with open(meta_path, "w") as f:
        json.dump(meta, f)
    return meta


def _mean_color(path):
    """The texture's average colour (linear), so tinting can keep its light and dark but take on
    a new colour."""
    img = bpy.data.images.load(path, check_existing=False)
    try:
        img.scale(32, 32)
        px = list(img.pixels)
    finally:
        bpy.data.images.remove(img)
    n = len(px) // 4
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    return [max(1e-3, sum(lin(px[i * 4 + k]) for i in range(n)) / n) for k in range(3)]


def download_all(progress=print):
    """Fetch every material's textures (about 250 MB at 1K)."""
    seen = set()
    for kind, spec in KINDS.items():
        src = spec.get("src")
        if src and src not in seen:
            seen.add(src)
            progress(f"  {kind}: {src[1]}")
            fetch(src)
    for hdri in set(HDRIS.values()):
        progress(f"  sky: {hdri}")
        fetch_hdri(hdri)


# ---------------------------------------------------------------------- building materials
class _Nodes:
    """Small helpers for building a node tree."""

    def __init__(self, nt):
        self.nt = nt

    def new(self, kind, **inputs):
        n = self.nt.nodes.new(kind)
        for k, v in inputs.items():
            if k in n.inputs and not isinstance(v, bpy.types.NodeSocket):
                n.inputs[k].default_value = v
            elif isinstance(v, bpy.types.NodeSocket):
                self.nt.links.new(v, n.inputs[k])
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def math(self, op, a, b=None, vector=False):
        n = self.nt.nodes.new("ShaderNodeVectorMath" if vector else "ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                self.link(v, n.inputs[i])
            else:
                n.inputs[i].default_value = v
        return n.outputs[0]

    def mix(self, a, b, fac, blend="MIX"):
        n = self.nt.nodes.new("ShaderNodeMix")
        n.data_type = "RGBA"
        n.blend_type = blend
        for sock, v in ((n.inputs["Factor"], fac), (n.inputs[6], a), (n.inputs[7], b)):
            if isinstance(v, bpy.types.NodeSocket):
                self.link(v, sock)
            else:
                sock.default_value = v if not isinstance(v, tuple) or len(v) == 4 else (*v, 1.0)
        return n.outputs[2]


def _rest_coords(obj):
    """Pin patterns to the object: a 'dr_rest' attribute with each vertex's rest position in
    metres (deforming characters don't make textures slide)."""
    me = obj.data
    if "dr_rest" in me.attributes:
        return
    s = obj.matrix_world.to_scale()
    k = (abs(s.x) + abs(s.y) + abs(s.z)) / 3 or 1.0
    attr = me.attributes.new("dr_rest", "FLOAT_VECTOR", "POINT")
    co = [0.0] * (len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    attr.data.foreach_set("vector", [c * k for c in co])


_images = {}


def _image(path, data):
    key = (path, data)
    img = _images.get(key)
    try:
        alive = img is not None and img.name in bpy.data.images
    except ReferenceError:              # Blender was reset (a new scene)
        alive = False
    if not alive:
        img = bpy.data.images.load(path, check_existing=True)
        if data:
            img.colorspace_settings.name = "Non-Color"
        _images[key] = img
    return img


def _tex(N, path, coords, data):
    t = N.new("ShaderNodeTexImage")
    t.image = _image(path, data)
    t.projection = "BOX"
    t.projection_blend = 0.3
    t.interpolation = "Cubic" if data else "Linear"
    N.link(coords, t.inputs["Vector"])
    return t


def _coords(N, size):
    """Coordinates in tiles: from the rest positions, shifted at random per object."""
    attr = N.new("ShaderNodeAttribute")
    attr.attribute_name = "dr_rest"
    info = N.new("ShaderNodeObjectInfo")
    shift = N.math("MULTIPLY", info.outputs["Random"], 97.0)
    scaled = N.math("MULTIPLY", attr.outputs["Vector"], (1.0 / size,) * 3, vector=True)
    return N.math("ADD", scaled, shift, vector=True)


def _design_color(N, bsdf):
    """The colour the film gave the surface: its texture or vertex colours if linked, else the
    plain colour."""
    sock = bsdf.inputs["Base Color"]
    if sock.is_linked:
        return sock.links[0].from_socket
    rgb = N.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = tuple(sock.default_value)
    return rgb.outputs[0]


def realise(mat, kind, download=True):
    """Turn `mat` into the real material `kind` (in place). Returns True if it changed."""
    spec = KINDS.get(kind)
    if spec is None or not mat.use_nodes:
        return False
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return False
    N = _Nodes(nt)
    design = _design_color(N, bsdf)
    if spec["src"] is None:
        PROCEDURAL[kind](N, bsdf, design, mat)
    else:
        tex = fetch(spec["src"], download)
        if tex is None:
            _plastic(N, bsdf, design, mat)
        else:
            _textured(N, bsdf, design, spec, tex)
    mat["dr_kind"] = kind
    mat["dr_real"] = True
    return True


def _textured(N, bsdf, design, spec, tex):
    size = spec.get("size") or tex["size"]
    co = _coords(N, size)
    maps = tex["maps"]
    if spec.get("detail_only") or "color" not in maps:   # imperfections only: the film's colour, varied shine
        base = design
    else:
        col = _tex(N, maps["color"], co, False).outputs["Color"]
        mean = tex["mean"]
        how = spec.get("color", "natural")
        if how == "paint":                # paint over it: the film's colour, the grain only faintly
            norm = N.math("MULTIPLY", col, tuple(1.0 / m for m in mean), vector=True)
            faint = N.mix((1.0, 1.0, 1.0, 1.0), norm, 0.12)
            base = N.mix(design, faint, 1.0, "MULTIPLY")
        elif how == "keep":
            base = col
        else:
            # the texture's light and dark, around the film's colour: tex * design / mean(tex)
            norm = N.math("MULTIPLY", col, tuple(1.0 / m for m in mean), vector=True)
            tinted = N.mix(design, norm, 1.0, "MULTIPLY")
            base = tinted if how == "tint" else N.mix(col, tinted, 0.35)
        if "ao" in maps and how != "paint":
            ao = _tex(N, maps["ao"], co, True).outputs["Color"]
            base = N.mix(base, ao, 0.6, "MULTIPLY")
    N.link(base, bsdf.inputs["Base Color"])
    lo, hi = spec.get("rough", (None, None))
    if "roughness" in maps:
        r = _tex(N, maps["roughness"], co, True).outputs["Color"]
        if lo is not None:
            mr = N.new("ShaderNodeMapRange", **{"From Min": 0.0, "From Max": 1.0, "To Min": lo, "To Max": hi})
            N.link(r, mr.inputs["Value"])
            r = mr.outputs["Result"]
        N.link(r, bsdf.inputs["Roughness"])
    elif lo is not None:
        bsdf.inputs["Roughness"].default_value = (lo + hi) / 2
    if spec.get("metal"):
        if "metalness" in maps:
            N.link(_tex(N, maps["metalness"], co, True).outputs["Color"], bsdf.inputs["Metallic"])
        else:
            bsdf.inputs["Metallic"].default_value = spec["metal"]
    else:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "displacement" in maps and spec.get("bump", 0) > 0:
        h = _tex(N, maps["displacement"], co, True).outputs["Color"]
        bump = N.new("ShaderNodeBump", Strength=min(1.0, spec["bump"]), Distance=0.004 * size, Height=h)
        N.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
    for name, v in (("Coat Weight", 0.0), ("Specular IOR Level", 0.5)):
        if bsdf.inputs.get(name) is not None:
            bsdf.inputs[name].default_value = v
    if spec.get("foliage"):               # light through leaves
        _set(bsdf, "Subsurface Weight", 0.35)
        _set(bsdf, "Subsurface Radius", (0.3, 1.0, 0.2))
        _set(bsdf, "Subsurface Scale", 0.02)
        _set(bsdf, "Sheen Weight", 0.2)
    if spec.get("fur"):                   # soft fibres catching light at the edges
        _set(bsdf, "Sheen Weight", 0.8)
        _set(bsdf, "Sheen Roughness", 0.4)
        _set(bsdf, "Specular IOR Level", 0.2)


def _set(bsdf, name, value):
    sock = bsdf.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def _noise_bump(N, bsdf, scale, strength, stretch=(1, 1, 1), detail=8.0):
    attr = N.new("ShaderNodeAttribute")
    attr.attribute_name = "dr_rest"
    co = N.math("MULTIPLY", attr.outputs["Vector"], stretch, vector=True)
    noise = N.new("ShaderNodeTexNoise", Scale=scale, Detail=detail, Roughness=0.6)
    N.link(co, noise.inputs["Vector"])
    bump = N.new("ShaderNodeBump", Strength=strength, Distance=0.002)
    N.link(noise.outputs["Fac"], bump.inputs["Height"])
    N.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return noise


def _imperfections(N, bsdf, lo, hi):
    """Real surfaces aren't evenly shiny: smudges and wear vary the roughness."""
    tex = fetch(KINDS["painted_metal"]["src"])
    if tex is None:
        bsdf.inputs["Roughness"].default_value = (lo + hi) / 2
        return
    co = _coords(N, 1.0)
    r = _tex(N, tex["maps"]["roughness"] if "roughness" in tex["maps"] else tex["maps"]["color"], co, True)
    mr = N.new("ShaderNodeMapRange", **{"To Min": lo, "To Max": hi})
    N.link(r.outputs["Color"], mr.inputs["Value"])
    N.link(mr.outputs["Result"], bsdf.inputs["Roughness"])


def _plastic(N, bsdf, design, mat):
    """Moulded plastic and anything unknown: the film's colour, varied shine, a fine grain."""
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Coat Weight", 0.0)
    _set(bsdf, "Specular IOR Level", 0.5)
    _imperfections(N, bsdf, 0.3, 0.55)
    _noise_bump(N, bsdf, 400.0, 0.04)


def _skin(N, bsdf, design, mat):
    """Skin: light scattering under the surface (redder deeper down), pores, a soft sheen of oil."""
    noise = N.new("ShaderNodeTexNoise", Scale=12.0, Detail=4.0)
    attr = N.new("ShaderNodeAttribute")
    attr.attribute_name = "dr_rest"
    N.link(attr.outputs["Vector"], noise.inputs["Vector"])
    blotch = N.mix(design, N.math("MULTIPLY", design, (1.06, 0.95, 0.93), vector=True), noise.outputs["Fac"])
    N.link(blotch, bsdf.inputs["Base Color"])
    _set(bsdf, "Subsurface Weight", 1.0)
    _set(bsdf, "Subsurface Radius", (1.0, 0.35, 0.18))
    _set(bsdf, "Subsurface Scale", 0.006)
    _set(bsdf, "Roughness", 0.45)
    _set(bsdf, "Specular IOR Level", 0.45)
    _set(bsdf, "Coat Weight", 0.06)
    _set(bsdf, "Coat Roughness", 0.35)
    _set(bsdf, "Sheen Weight", 0.08)
    vor = N.new("ShaderNodeTexVoronoi", Scale=900.0)
    N.link(attr.outputs["Vector"], vor.inputs["Vector"])
    bump = N.new("ShaderNodeBump", Strength=0.08, Distance=0.0005)
    N.link(vor.outputs["Distance"], bump.inputs["Height"])
    N.link(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _hair(N, bsdf, design, mat):
    """Hair: strands running down the head, a sheen that slides along them."""
    N.link(design, bsdf.inputs["Base Color"])
    noise = _noise_bump(N, bsdf, 6.0, 0.35, stretch=(60.0, 60.0, 4.0), detail=10.0)
    streak = N.mix(design, N.math("MULTIPLY", design, (0.6, 0.6, 0.6), vector=True), noise.outputs["Fac"])
    N.link(streak, bsdf.inputs["Base Color"])
    _set(bsdf, "Roughness", 0.35)
    _set(bsdf, "Specular IOR Level", 0.3)
    _set(bsdf, "Coat Weight", 0.0)
    _set(bsdf, "Anisotropic", 0.8)
    _set(bsdf, "Sheen Weight", 0.3)


def _eye(N, bsdf, design, mat):
    """Eyes: wet and glossy."""
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Roughness", 0.05)
    _set(bsdf, "Coat Weight", 1.0)
    _set(bsdf, "Coat Roughness", 0.02)
    _set(bsdf, "Specular IOR Level", 0.6)


def _glass(N, bsdf, design, mat):
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Roughness", 0.02)
    _set(bsdf, "Transmission Weight", 1.0)
    _set(bsdf, "IOR", 1.5)
    _set(bsdf, "Metallic", 0.0)
    _set(bsdf, "Coat Weight", 0.0)
    a = bsdf.inputs.get("Alpha")
    if a is not None and a.default_value > 0.6:
        a.default_value = 0.6


def _car_paint(N, bsdf, design, mat):
    """Car paint: a deep colour under a glossy clear coat, with fine metallic flakes."""
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Metallic", 0.5)
    _set(bsdf, "Roughness", 0.35)
    _set(bsdf, "Coat Weight", 1.0)
    _set(bsdf, "Coat Roughness", 0.03)
    _noise_bump(N, bsdf, 3000.0, 0.03, detail=2.0)


def _rubber(N, bsdf, design, mat):
    N.link(N.mix(design, (0.02, 0.02, 0.02, 1.0), 0.5), bsdf.inputs["Base Color"])
    _set(bsdf, "Roughness", 0.8)
    _set(bsdf, "Specular IOR Level", 0.3)
    _set(bsdf, "Coat Weight", 0.0)
    _noise_bump(N, bsdf, 300.0, 0.15)


def _baked(N, bsdf, design, mat):
    """Biscuits, bread and cake: a golden crust, darker where it browned, crumbly relief."""
    noise = _noise_bump(N, bsdf, 60.0, 0.5, detail=12.0)
    dark = N.math("MULTIPLY", design, (0.55, 0.42, 0.3), vector=True)
    N.link(N.mix(design, dark, noise.outputs["Fac"]), bsdf.inputs["Base Color"])
    _set(bsdf, "Roughness", 0.75)
    _set(bsdf, "Subsurface Weight", 0.2)
    _set(bsdf, "Subsurface Scale", 0.005)
    _set(bsdf, "Coat Weight", 0.0)


def _wax(N, bsdf, design, mat):
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Subsurface Weight", 0.8)
    _set(bsdf, "Subsurface Scale", 0.02)
    _set(bsdf, "Roughness", 0.4)
    _set(bsdf, "Coat Weight", 0.0)


def _petals(N, bsdf, design, mat):
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Subsurface Weight", 0.5)
    _set(bsdf, "Subsurface Scale", 0.01)
    _set(bsdf, "Roughness", 0.5)
    _set(bsdf, "Sheen Weight", 0.3)
    _set(bsdf, "Coat Weight", 0.0)
    _noise_bump(N, bsdf, 80.0, 0.15, stretch=(1, 1, 6))


def _frosting(N, bsdf, design, mat):
    N.link(design, bsdf.inputs["Base Color"])
    _set(bsdf, "Subsurface Weight", 0.4)
    _set(bsdf, "Subsurface Scale", 0.01)
    _set(bsdf, "Roughness", 0.3)
    _set(bsdf, "Coat Weight", 0.0)
    _noise_bump(N, bsdf, 20.0, 0.2)


PROCEDURAL = {"skin": _skin, "hair": _hair, "eye": _eye, "glass": _glass, "car_paint": _car_paint,
              "rubber": _rubber, "baked": _baked, "wax": _wax, "petals": _petals, "frosting": _frosting,
              "plastic": _plastic}


# ---------------------------------------------------------------------- a whole scene
def _owners(scene):
    """{object: owner} for everything that belongs to a character (its class name) or a car."""
    owners = {}
    for c in getattr(scene, "actors", {}).values():
        root = getattr(c, "root", None)
        if root is None:
            continue
        tag = type(c).__name__
        for o in [root] + list(root.children_recursive) + list(getattr(c, "meshes", []) or []):
            owners[o] = tag
    for o in bpy.data.objects:
        if o not in owners and re.match(r"^car\d*(\.|$)", o.name):
            for k in [o] + list(o.children_recursive):
                owners.setdefault(k, "car")
    return owners


def realise_scene(scene, download=True):
    """Give every surface in the scene its real material. Each (material, kind) pair becomes one
    new material, so a material shared by things made of different stuff (a pack's "White" on a
    door and on a window frame) comes out right on each; the originals are left as they were."""
    owners = _owners(scene)
    made = {}                        # (original material, kind) -> real material
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or obj.get("dr_fx") or not obj.material_slots:
            continue
        owner, p = owners.get(obj), obj.parent
        while owner is None and p is not None:
            owner, p = owners.get(p), p.parent
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or mat.get("dr_real") or mat.name.startswith(("outline", "fog")):
                continue
            kind = classify(obj, mat, owner)
            if kind is None:
                continue
            _rest_coords(obj)
            key = (mat.name, kind)
            if key not in made:
                real = mat.copy()
                real.name = f"{mat.name} ({kind})"
                made[key] = real if realise(real, kind, download) else mat
            slot.material = made[key]
    return len(made)


def soften(scene):
    """Low-poly people, animals and rocks (Quaternius's are flat-shaded, made of separate faces)
    get smooth surfaces: the faces are joined up, shaded smooth and subdivided once, so light
    rolls over a cheek or a dog's back instead of breaking on facets."""
    import bmesh
    owners = _owners(scene)
    done = set()
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or obj.data in done or obj.get("dr_fx"):
            continue
        owner = owners.get(obj)
        p = obj.parent
        while owner is None and p is not None:
            owner, p = owners.get(p), p.parent
        rock = re.match(r"^(rock|stone|boulder)", obj.name.lower()) is not None
        if owner not in ("Person", "Animal") and not rock:
            continue
        if obj.name.endswith(("lips", "mouthkeys", "lidkeys")):
            continue
        me = obj.data
        done.add(me)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4 * max(obj.dimensions or (1,)))
        bm.to_mesh(me)
        bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        if not any(m.type == "SUBSURF" for m in obj.modifiers):
            mod = obj.modifiers.new("soft", "SUBSURF")
            mod.levels, mod.render_levels = 0, 1
            mod.uv_smooth = "PRESERVE_CORNERS"


# ---------------------------------------------------------------------- real skies
# Poly Haven's sky photographs (HDRIs, CC0), by time of day
HDRIS = {
    "dawn": "kloofendal_misty_morning_puresky", "morning": "kloofendal_48d_partly_cloudy_puresky",
    "day": "kloofendal_48d_partly_cloudy_puresky", "golden_hour": "kloofendal_43d_clear_puresky",
    "sunset": "belfast_sunset_puresky", "dusk": "qwantani_dusk_2_puresky", "night": "qwantani_night_puresky",
    "indoor": "brown_photostudio_02",
}


def fetch_hdri(ident, download=True):
    path = os.path.join(CACHE, "skies", f"{ident}_1k.hdr")
    if os.path.exists(path):
        return path
    if not download:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        files = _json(f"https://api.polyhaven.com/files/{ident}")
        _get(files["hdri"]["1k"]["hdr"]["url"], path)
    except (OSError, ValueError, KeyError) as e:
        print(f"[dreamreel] couldn't fetch the {ident} sky ({e}); keeping the painted sky")
        return None
    return path


def real_sky(scene, download=True):
    """A photographed sky for the scene's time of day: what you see outdoors and what lights and
    reflects in everything (indoors, only in reflections). Turned so its sun is where the
    scene's sun is."""
    env = getattr(scene, "environment", None)
    world = scene.bscene.world
    if env is None or world is None or not world.use_nodes:
        return False
    tod = getattr(env, "time_of_day", "day") if env.outdoor else "indoor"
    path = fetch_hdri(HDRIS.get(tod, HDRIS["day"]), download)
    if path is None:
        return False
    nt = world.node_tree
    bg = next((n for n in nt.nodes if n.type == "BACKGROUND"), None)
    out = next((n for n in nt.nodes if n.type == "OUTPUT_WORLD"), None)
    if bg is None or out is None:
        return False
    N = _Nodes(nt)
    env_tex = N.new("ShaderNodeTexEnvironment")
    env_tex.image = bpy.data.images.load(path, check_existing=True)
    co = N.new("ShaderNodeTexCoord")
    mapping = N.new("ShaderNodeMapping")
    N.link(co.outputs["Generated"], mapping.inputs["Vector"])
    N.link(mapping.outputs["Vector"], env_tex.inputs["Vector"])
    az, photo_lum = _sun_azimuth(env_tex.image)
    sun = next((o for o in scene.bscene.objects if o.type == "LIGHT" and o.data.type == "SUN"), None)
    if sun is not None and az is not None:
        d = sun.matrix_world.to_3x3() @ Vector((0, 0, 1))          # towards the sun
        # the mapping turns each view direction before the photo is looked up, so the photo's sun
        # (at azimuth az) shows at az - rotation
        mapping.inputs["Rotation"].default_value[2] = az - math.atan2(d.y, d.x)
    strength = bg.inputs["Strength"].default_value
    if env.outdoor:
        # as bright overall as the sky dreamreel painted for this light (the sun lamp gives the
        # sunlight; the photo's own sun would double it)
        L = env.light
        painted = [(a + b) / 2 for a, b in zip(look.rgb(L.horizon), look.rgb(L.zenith))]
        want = (0.2126 * painted[0] + 0.7152 * painted[1] + 0.0722 * painted[2]) * strength
        N.link(env_tex.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = max(0.02, want / max(1e-3, photo_lum)) if photo_lum else strength * 0.3
    else:
        # indoors the room's own light stays; the photo only shows in reflections
        lp = N.new("ShaderNodeLightPath")
        refl = N.new("ShaderNodeBackground", Strength=0.6)
        N.link(env_tex.outputs["Color"], refl.inputs["Color"])
        mix = N.new("ShaderNodeMixShader")
        N.link(lp.outputs["Is Glossy Ray"], mix.inputs["Fac"])
        N.link(bg.outputs[0], mix.inputs[1])
        N.link(refl.outputs[0], mix.inputs[2])
        N.link(mix.outputs[0], out.inputs["Surface"])
    return True


def _sun_azimuth(img):
    """Where the sun is in a sky photograph (the azimuth, from +x towards +y, of its brightest
    spot), and the photo's typical brightness (the median, so the sun doesn't count)."""
    try:
        w, h = img.size
        if not w or not h:
            return None, None
        small = img.copy()
        small.scale(64, 32)
        px = list(small.pixels)
        bpy.data.images.remove(small)
    except (RuntimeError, ValueError):
        return None, None
    best, bi = -1.0, 0
    lums = []
    for i in range(64 * 32):
        lum = px[i * 4] + px[i * 4 + 1] + px[i * 4 + 2]
        if i >= 64 * 16:                 # the upper half (rows run bottom-up): the sky, not the ground
            lums.append(lum / 3)
        if lum > best:
            best, bi = lum, i
    u = (bi % 64 + 0.5) / 64
    # Blender's equirectangular lookup: u = atan2(dir.y, -dir.x) / 2pi + 0.5
    theta = (u - 0.5) * 2 * math.pi
    lums.sort()
    return math.atan2(math.sin(theta), -math.cos(theta)), lums[len(lums) // 2] if lums else None


def describe():
    """What dreamreel can make surfaces out of, for docs and tools."""
    return {k: (v["src"][1] if v.get("src") else "procedural") for k, v in KINDS.items()}


def fetched():
    return os.path.isdir(CACHE) and any(n.endswith(f"_{RES}") for n in os.listdir(CACHE))

