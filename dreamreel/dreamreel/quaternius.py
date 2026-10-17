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
    "nature": {"itch": "https://quaternius.itch.io/stylized-nature-megakit",
               "about": "trees, bushes, rocks, flowers, grass"},
    "city": {"itch": "https://quaternius.itch.io/downtown-city-megakit",
             "about": "city buildings, streets, props"},
}


def folder(pack):
    return os.path.join(CACHE, pack)


def installed():
    return {p for p in PACKS if os.path.isdir(folder(p)) and os.listdir(folder(p))}


def files(pack, exts=(".gltf", ".glb", ".fbx")):
    """Model files of an installed pack: {name: path} (name = file name without extension)."""
    out = {}
    base = folder(pack)
    for d, _, names in os.walk(base):
        for n in sorted(names):
            if os.path.splitext(n)[1].lower() in exts:
                out.setdefault(os.path.splitext(n)[0], os.path.join(d, n))
    return out


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
    names = re.findall(r'class="name" title="([^"]+)"', dl)
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
