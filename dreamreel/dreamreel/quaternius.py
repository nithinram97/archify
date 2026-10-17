"""Quaternius's free (CC0) 3D asset packs: the look of dreamreel's people, animals, furniture,
nature, buildings and vehicles.

Quaternius (quaternius.com) makes stylized low-poly game assets and releases them as CC0: free for
any use. dreamreel doesn't bundle them: `dreamreel assets --download` fetches the packs it uses
into a cache folder (about 1 GB in all; `--pack NAME` for one), and everything that needs a model
finds it there by name.

Packs are published two ways, both handled here: public Google Drive folders (older packs, one
file per model) and free itch.io downloads (the newer MegaKits, one zip each).
"""
import http.cookiejar
import json
import os
import re
import urllib.parse
import urllib.request
import zipfile

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "quaternius")
UA = [("User-Agent", "Mozilla/5.0 (dreamreel asset fetcher)")]

# name -> where it comes from. "drive": a public Google Drive folder (we take its glTF/FBX files);
# "itch": an itch.io page with a free download (a zip).
PACKS = {
    "men": {"drive": "1qpSIycVWTwhKMgyA_bEFHPh1CfBBBa09",
            "about": "dressed men: adventurer, beach, casual, hoodie, farmer, king, punk, spacesuit, suit, swat, worker"},
    "women": {"drive": "1_FIjjIVE0SkQIrwgWJ3Q8NQku25ll5a2",
              "about": "dressed women: adventurer, casual, formal, medieval, punk, scifi, soldier, suit, witch, worker"},
    "animals": {"drive": "1yJXdB1iSrI8Db7hG77zxZ66vKsqIt0ry",
                "about": "alpaca, bull, cow, deer, donkey, fox, horse, husky, shiba inu, stag, wolf"},
    "interior": {"drive": "1SNK9PwPi8xqqxmpU5xEZeiQjB26C1oX6",
                 "about": "furniture: tables, chairs, sofas, beds, shelves, kitchens, doors, windows, lamps, plants"},
    "nature": {"itch": "https://quaternius.itch.io/stylized-nature-megakit",
               "about": "trees, bushes, rocks, flowers, grass"},
    "city": {"itch": "https://quaternius.itch.io/downtown-city-megakit", "vertex_colors": False,
             "about": "city buildings, streets, props"},
}


def folder(pack):
    return os.path.join(CACHE, pack)


def installed():
    return {p for p in PACKS if os.path.isdir(folder(p)) and os.listdir(folder(p))}


def files(pack, exts=(".gltf", ".glb", ".fbx")):
    """Model files of an installed pack: {name: path} (name = file name without extension; when a
    pack has a model in several formats, the first of `exts` wins)."""
    found = {}
    for d, _, names in os.walk(folder(pack)):
        for n in sorted(names):
            stem, ext = os.path.splitext(n)
            if ext.lower() in exts:
                found.setdefault(stem, []).append((exts.index(ext.lower()), os.path.join(d, n)))
    return {stem: min(paths)[1] for stem, paths in found.items()}


# ---------------------------------------------------------------------- models in sets
_LIBRARY = {}     # (pack, name) -> mesh: each model is imported once and shared by every copy


def mesh(pack, name):
    """A pack's model as one mesh, its origin in the middle of its base and its front facing -Y
    (the camera); None if the pack isn't installed."""
    import bpy
    from mathutils import Matrix, Vector
    from .models import import_file
    got = _LIBRARY.get((pack, name))
    try:
        if got is not None and got.name:
            return got
    except ReferenceError:          # a new Blender scene was started
        pass
    path = files(pack).get(name)
    if path is None:
        return None
    objs = import_file(path)
    meshes = [o for o in objs if o.type == "MESH"]
    cols = meshes[0].data.color_attributes if meshes else None
    render_color = cols[cols.render_color_index].name if cols and cols.render_color_index >= 0 else None
    bpy.context.view_layer.update()
    parts = []
    for o in meshes:
        m = o.data.copy()
        m.transform(o.matrix_world)
        parts.append(m)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    import bmesh
    bm = bmesh.new()
    mats = []
    for m in parts:
        offset = len(mats)
        mats += list(m.materials)
        bm2 = bmesh.new()
        bm2.from_mesh(m)
        for f in bm2.faces:
            f.material_index += offset
        tmp = bpy.data.meshes.new("tmp")
        bm2.to_mesh(tmp)
        bm2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
        bpy.data.meshes.remove(m)
    out = bpy.data.meshes.new(f"{pack}.{name}")
    bm.to_mesh(out)
    bm.free()
    names = [c.name for c in out.color_attributes]
    if render_color in names:       # materials read "the" vertex colour: keep the file's choice
        out.color_attributes.active_color_index = names.index(render_color)
        out.color_attributes.render_color_index = names.index(render_color)
    if not PACKS.get(pack, {}).get("vertex_colors", True):     # masks for game engines, not colours
        for mat in mats:
            for node in list(mat.node_tree.nodes if mat and mat.node_tree else ()):
                if node.type == "VERTEX_COLOR":
                    mat.node_tree.nodes.remove(node)
    for mat in mats:
        out.materials.append(mat)
        bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat and mat.node_tree else None
        if bsdf is not None and bsdf.inputs["Alpha"].is_linked:     # cut-out leaves and petals:
            mat.use_transparent_shadow = False                          # 15x faster, much the same
        elif bsdf is not None:          # FBX files come in with alpha 0
            glass = "glass" in mat.name.lower()
            bsdf.inputs["Alpha"].default_value = 0.2 if glass else 1.0
            if glass and hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "BLENDED"
            bsdf.inputs["Roughness"].default_value = 0.1 if glass else max(0.5, bsdf.inputs["Roughness"].default_value)
    lo = Vector(tuple(min(v.co[i] for v in out.vertices) for i in range(3)))
    hi = Vector(tuple(max(v.co[i] for v in out.vertices) for i in range(3)))
    out.transform(Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    out.use_fake_user = True
    _LIBRARY[(pack, name)] = out
    return out


def place(pack, name, label, size, at=(0, 0, 0), facing=0.0, parent=None):
    """A copy of a pack's model, fitted to size (width, depth, height; None for an axis that follows
    the others), standing at `at` facing `facing` (radians; 0 faces the camera). None if the pack isn't
    installed (the caller builds its own)."""
    import bpy
    from . import shapes
    m = mesh(pack, name)
    if m is None:
        return None
    dims = [max(1e-6, max(v.co[i] for v in m.vertices) - min(v.co[i] for v in m.vertices)) for i in range(3)]
    ks = [None if s is None else s / d for s, d in zip(size, dims)]
    given = [k for k in ks if k is not None]
    mean = sum(given) / len(given) if given else 1.0
    obj = bpy.data.objects.new(label, m)
    shapes._collection().objects.link(obj)
    obj.parent = parent
    obj.location = at
    obj.rotation_euler = (0, 0, facing)
    obj.scale = [mean if k is None else k for k in ks]
    return obj


def rest_on(obj, at, height, depth=True):
    """Scale a placed model's height (and its depth with it, unless depth=False) so that its surface above
    `at` (x, y in metres from its middle, before it is turned) is `height` above its base: a seat, a
    mattress, a worktop at the height a character expects. Returns where that surface was found."""
    import bpy
    if obj is None:
        return None
    bpy.context.view_layer.update()
    sx, sy, sz = obj.scale
    top = max(v.co.z for v in obj.data.vertices) + 1.0
    hit, loc, *_ = obj.ray_cast((at[0] / sx, at[1] / sy, top), (0, 0, -1))
    if not hit or loc.z <= 1e-6:
        return None
    k = height / (loc.z * sz)
    obj.scale = (sx, sy * k if depth else sy, sz * k)
    return loc.z * sz


# ---------------------------------------------------------------------- fetching
def _opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = UA
    return op


def _itch(url, dest, progress):
    """Download every file of a free itch.io page (the zips are unpacked)."""
    op = _opener()
    page = op.open(url).read().decode()
    tok = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    r = json.loads(op.open(url + "/download_url", urllib.parse.urlencode({"csrf_token": tok}).encode()).read())
    dl = op.open(r["url"]).read().decode()
    tok2 = re.search(r'name="csrf_token" value="([^"]+)"', dl).group(1)
    uploads = re.findall(r'data-upload_id="(\d+)"', dl)
    names = [a or b for a, b in re.findall(r'<strong[^>]*?(?:title="([^"]+)"[^>]*class="name"|class="name"[^>]*title="([^"]+)")', dl)]
    if not uploads or len(names) != len(uploads):
        raise RuntimeError(f"{url}: couldn't find the files to download (has the page changed?)")
    for up, name in zip(uploads, names):
        q = urllib.parse.urlencode({"source": "game_download", "after_download_lightbox": "1", "as_props": "1"})
        res = json.loads(op.open(f"{url}/file/{up}?{q}", urllib.parse.urlencode({"csrf_token": tok2}).encode()).read())
        if not res.get("url"):
            raise RuntimeError(f"{url}: no download for {name}: {res.get('errors')}")
        target = os.path.join(dest, name)
        progress(f"  {name}")
        with op.open(res["url"]) as src, open(target, "wb") as fh:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        if target.lower().endswith(".zip"):
            with zipfile.ZipFile(target) as z:
                z.extractall(dest)
            os.remove(target)


def _drive(folder_id, dest, progress, exts=(".gltf", ".glb", ".fbx", ".png", ".bin")):
    """Download the model files of a public Google Drive folder (and its subfolders)."""
    op = _opener()
    html = op.open(f"https://drive.google.com/embeddedfolderview?id={folder_id}").read().decode()
    entries = re.findall(r'href="https://drive\.google\.com/(file/d|drive/folders)/([A-Za-z0-9_-]+)[^"]*".*?'
                         r'flip-entry-title">([^<]+)', html, re.S)
    for kind, fid, name in entries:
        if kind == "drive/folders":
            sub = os.path.join(dest, name)
            os.makedirs(sub, exist_ok=True)
            _drive(fid, sub, progress, exts)
        elif os.path.splitext(name)[1].lower() in exts:
            target = os.path.join(dest, name)
            if os.path.exists(target):
                continue
            progress(f"  {name}")
            url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
            with op.open(url) as src, open(target, "wb") as fh:
                fh.write(src.read())


def download(packs=None, progress=print):
    """Fetch packs (all of PACKS by default) into the cache."""
    for name in packs or list(PACKS):
        spec = PACKS[name]
        dest = folder(name)
        os.makedirs(dest, exist_ok=True)
        progress(f"{name}: {spec['about']}")
        if "itch" in spec:
            _itch(spec["itch"], dest, progress)
        else:
            _drive(spec["drive"], dest, progress)
    progress(f"Quaternius packs (CC0, quaternius.com) in {CACHE}")
