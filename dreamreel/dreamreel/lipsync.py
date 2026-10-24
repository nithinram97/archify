"""Lip sync from the sounds of a line, not just its loudness.

dreamreel listens to each voiced line with Rhubarb Lip Sync (https://github.com/DanielSWolf/rhubarb-lip-sync,
MIT, by Daniel Wolf), which hears the sounds and gives the mouth shape for each moment: lips pressed
together for M, B and P, wide open for "aa", rounded for "oo", teeth on the lip for F and V. Rhubarb is
downloaded the first time it's needed (about 90 MB) into ~/.cache/dreamreel/tools, and it runs on any
computer, without a graphics card or internet.

English lines are matched against their words for accuracy; any other language uses Rhubarb's
language-independent recogniser, which hears the sounds without knowing the words.

    # film.toml
    lipsync = "sounds"      # the default: mouth shapes from the sounds (falls back to loudness)
    lipsync = "loudness"    # the mouth opens with how loud the voice is (no download)
    lipsync = "ai"          # the mouth from LAM Audio2Expression on a booster (see face_cues below),
                            # else from the sounds

Results are cached next to each voice file, so a line is only listened to once.
"""
import json
import os
import platform
import shutil
import stat
import subprocess
import tempfile
import urllib.request
import zipfile

VERSION = "1.14.0"
TOOLS = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "tools")
URL = "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v{v}/Rhubarb-Lip-Sync-{v}-{os}.zip"

# Rhubarb's mouth shapes (after the Hanna-Barbera set animators use) as dreamreel's mouth controls:
# open (jaw), round (lips pushed forward), wide (lips stretched)
SHAPES = {
    "X": (0.0, 0.0, 0.0),     # rest
    "A": (0.0, 0.0, 0.1),     # M, B, P: lips pressed together
    "B": (0.18, 0.0, 0.35),   # K, S, T, EE: teeth nearly closed, lips apart
    "C": (0.5, 0.0, 0.2),     # EH, AE: open
    "D": (0.95, 0.0, 0.1),    # AA: wide open
    "E": (0.45, 0.45, 0.0),   # AO, ER: slightly rounded
    "F": (0.15, 1.0, 0.0),    # UW, OW, W: puckered
    "G": (0.1, 0.0, 0.25),    # F, V: upper teeth on the lower lip
    "H": (0.35, 0.0, 0.1),    # L: tongue up behind the teeth
}

_warned = set()


def _warn(msg):
    if msg not in _warned:
        _warned.add(msg)
        print(f"[dreamreel] {msg}")


def _os_name():
    s = platform.system()
    return {"Darwin": "macOS", "Windows": "Windows"}.get(s, "Linux")


def _exe():
    return "rhubarb.exe" if platform.system() == "Windows" else "rhubarb"


def installed():
    """Rhubarb's program, if it's on this computer (DREAMREEL_RHUBARB, the PATH or dreamreel's cache)."""
    env = os.environ.get("DREAMREEL_RHUBARB")
    if env and os.path.isfile(env):
        return env
    found = shutil.which("rhubarb")
    if found:
        return found
    path = os.path.join(TOOLS, f"Rhubarb-Lip-Sync-{VERSION}-{_os_name()}", _exe())
    return path if os.path.isfile(path) else None


def install():
    """Download Rhubarb into dreamreel's cache; returns the program's path."""
    have = installed()
    if have:
        return have
    os.makedirs(TOOLS, exist_ok=True)
    url = URL.format(v=VERSION, os=_os_name())
    _warn(f"downloading Rhubarb Lip Sync {VERSION} (MIT) for lip sync, about 90 MB, once ...")
    zpath = os.path.join(TOOLS, f"rhubarb-{VERSION}.zip.part")
    req = urllib.request.Request(url, headers={"User-Agent": "dreamreel"})
    with urllib.request.urlopen(req, timeout=600) as r, open(zpath, "wb") as f:
        shutil.copyfileobj(r, f)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(TOOLS)
    os.remove(zpath)
    path = os.path.join(TOOLS, f"Rhubarb-Lip-Sync-{VERSION}-{_os_name()}", _exe())
    if not os.path.isfile(path):
        raise RuntimeError(f"Rhubarb's download didn't contain {_exe()}")
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def available(download=True):
    """Whether sound-based lip sync can run (downloading Rhubarb if allowed)."""
    if installed():
        return True
    if not download:
        return False
    try:
        return bool(install())
    except Exception as e:
        _warn(f"couldn't get Rhubarb Lip Sync ({e}); mouths follow the loudness of the voice instead")
        return False


def cues(wav, text=None, english=True, download=True):
    """[(start seconds, (open, round, wide))] for a voice file, or None if it can't be listened to."""
    raw = letters(wav, text, english, download)
    return None if raw is None else [(t, SHAPES.get(v, SHAPES["X"])) for t, v in raw]


def letters(wav, text=None, english=True, download=True):
    """[(start seconds, Rhubarb's mouth shape letter A-H or X)] for a voice file, or None."""
    cache = wav + ".cues.json"
    if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(wav):
        with open(cache) as f:
            raw = json.load(f)
    else:
        if not available(download):
            return None
        cmd = [installed(), "-q", "-f", "json", "--extendedShapes", "GHX"]
        dialog = None
        if english and text:
            fd, dialog = tempfile.mkstemp(suffix=".txt")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            cmd += ["-d", dialog]
        else:
            cmd += ["-r", "phonetic"]
        try:
            out = subprocess.run(cmd + [wav], check=True, capture_output=True, text=True, timeout=300).stdout
            raw = json.loads(out)["mouthCues"]
        except Exception as e:
            _warn(f"lip sync couldn't listen to a line ({e}); that line uses loudness")
            return None
        finally:
            if dialog:
                os.remove(dialog)
        tmp = f"{cache}.{os.getpid()}.part"
        with open(tmp, "w") as f:
            json.dump(raw, f)
        os.replace(tmp, cache)
    return [(float(c["start"]), c["value"]) for c in raw]


# ---------------------------------------------------------------------- the face from the voice, by AI
FACE_SKILL = "face.lam_a2e"


def _w(frame, idx, *names):
    vals = [frame[idx[n]] for n in names if n in idx]
    return sum(vals) / len(vals) if vals else 0.0


def face_frames(wav, download=True):
    """[(time, {ARKit shape name: weight})] from LAM Audio2Expression on a booster, or None: the
    whole face (brows, eyes, cheeks, lips) as the voice suggests it, for faces that have all 52."""
    data = _face_data(wav, download)
    if data is None:
        return None
    names = data.get("names") or data.get("metadata", {}).get("blendshape_names") or []
    fps = float(data.get("metadata", {}).get("fps", 30.0))
    out = []
    for i, fr in enumerate(data.get("frames", [])):
        w = fr.get("weights", [])
        if len(w) >= len(names):
            out.append((float(fr.get("time", i / fps)), dict(zip(names, w))))
    return out or None


def _face_data(wav, download=True):
    cache = wav + ".face.json"
    if not (os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(wav)):
        from . import boost
        skill = os.environ.get("DREAMREEL_FACE_SKILL") or FACE_SKILL
        b = boost.configured()
        if not download or b is None or not b.has(skill):
            _warn("lip sync from AI (lipsync = \"ai\") needs a booster (see `dreamreel boost`); "
                  "mouths follow the sounds instead")
            return None
        try:
            out = b.run(skill, {}, {"speech": wav}, out_dir=os.path.dirname(wav) or ".", timeout=900)
        except boost.BoostError as e:
            _warn(f"the booster couldn't read the face from the voice ({e}); mouths follow the sounds instead")
            return None
        os.replace(out["face"], cache)
    with open(cache) as f:
        return json.load(f)


def face_cues(wav, download=True):
    """[(start, (open, round, wide))] from LAM Audio2Expression's 52 ARKit face shapes for the line,
    made on a booster (cached next to the voice file); None without one. The jaw opens with jawOpen,
    the lips round with mouthFunnel and mouthPucker, and stretch with mouthStretch (and a little with
    mouthSmile)."""
    data = _face_data(wav, download)
    if data is None:
        return None
    names = data.get("names") or data.get("metadata", {}).get("blendshape_names") or []
    idx = {n: i for i, n in enumerate(names)}
    fps = float(data.get("metadata", {}).get("fps", 30.0))
    out = []
    for i, fr in enumerate(data.get("frames", [])):
        w = fr.get("weights", [])
        if len(w) < len(names):
            continue
        t = float(fr.get("time", i / fps))
        jaw = _w(w, idx, "jawOpen")
        rnd = max(_w(w, idx, "mouthFunnel"), _w(w, idx, "mouthPucker"))
        wide = max(_w(w, idx, "mouthStretchLeft", "mouthStretchRight"),
                   0.5 * _w(w, idx, "mouthSmileLeft", "mouthSmileRight"))
        out.append((t, (min(1.0, jaw * 1.4), min(1.0, rnd * 1.2), min(1.0, wide))))
    return out or None
