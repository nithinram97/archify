"""Captured fight moves: real people punching, kicking, blocking, ducking and getting up off the floor.

The moves come from the CMU Graphics Lab Motion Capture Database (free for any use; mocap.cs.cmu.edu),
downloaded the first time a fight needs them and kept in ~/.cache/dreamreel/motions/cmu (`dreamreel
assets --pack fights` fetches them all at once). Each recording is cut into single moves, and each
move knows when its blow lands (measured from the motion: the fist or foot at full extension, the
hands up at the face, the head at the bottom of a duck), so a captured punch can be played to land
exactly when the choreography says. Punches are told apart by how the fist travels into the blow:
straight (a jab with the lead hand, a cross with the rear), round (a hook) or up (an uppercut).

Bodies with a skeleton (realistic people, rigged models) play them bone by bone
(ModelCharacter.perform_clip); others keep dreamreel's hand-made moves.
"""
import json
import os
import random
import urllib.request

from mathutils import Matrix, Vector

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "motions", "cmu")
BASE = "http://mocap.cs.cmu.edu/subjects"
VERSION = 5

# which recordings, and what to look for in each
SOURCES = {
    "13_17": ("punches", "stance"), "13_18": ("punches", "stance"), "14_01": ("punches", "stance"),
    "14_02": ("punches", "ducks", "stance"), "14_03": ("punches", "ducks"),
    "143_23": ("punches", "stance"), "144_13": ("punches",), "144_20": ("punches",), "144_21": ("punches",),
    "141_14": ("punches", "kicks"),
    "144_05": ("kicks",), "144_09": ("kicks",), "143_24": ("kicks",), "135_04": ("kicks",),
    "144_07": ("blocks",), "144_26": ("blocks",),
    "139_09": ("ducks",),
    "88_06": ("spin_kick",), "87_01": ("spin_kick",),
    "90_05": ("flying_kick",), "90_06": ("flying_kick",),
    "139_18": ("get_up",), "140_08": ("get_up",), "140_01": ("get_up_face_down",),
}
WINDOW = {"punch": (0.55, 0.55), "kick": (0.7, 0.6), "block": (0.5, 0.5), "duck": (0.6, 0.7),
          "spin_kick": (0.9, 0.7), "flying_kick": (1.0, 0.8)}


def _subject(trial):
    return trial.split("_")[0]


def _paths(trial):
    s = _subject(trial)
    return os.path.join(CACHE, f"{s}.asf"), os.path.join(CACHE, f"{trial}.amc")


def fetch(trials=None, progress=print):
    """Download the recordings (each skeleton once); returns how many are here."""
    os.makedirs(CACHE, exist_ok=True)
    got = 0
    for trial in trials or SOURCES:
        s = _subject(trial)
        for url, dest in ((f"{BASE}/{int(s):02d}/{s}.asf", _paths(trial)[0]),
                          (f"{BASE}/{int(s):02d}/{trial}.amc", _paths(trial)[1])):
            if os.path.exists(dest):
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "dreamreel"})
                with urllib.request.urlopen(req, timeout=120) as r, open(dest + ".part", "wb") as f:
                    f.write(r.read())
                os.replace(dest + ".part", dest)
            except Exception as e:
                progress(f"[dreamreel] fights: couldn't fetch {url} ({e})")
                break
        got += all(os.path.exists(p) for p in _paths(trial))
    return got


def installed():
    return any(all(os.path.exists(p) for p in _paths(t)) for t in SOURCES)


_CLIPS = {}


def clip(trial):
    if trial not in _CLIPS:
        from . import motion
        _CLIPS[trial] = motion.load(_paths(trial)[1])
    return _CLIPS[trial]


# ---------------------------------------------------------------------- finding the moves in a recording
def _local(c):
    """Each frame's joints relative to the hips, turned to face forward (-y)."""
    out = []
    for i in range(c.n):
        p = {r: v[i] for r, v in c.roles.items()}
        R = Matrix.Rotation(-c.heading(p), 3, "Z")
        f = {r: R @ (v - p["hips"]) for r, v in p.items()}
        f["_hips"] = p["hips"]
        out.append(f)
    return out


def _peaks(vals, fps, thresh, sep):
    found, w = [], max(1, int(0.08 * fps))
    for i in range(w, len(vals) - w):
        if vals[i] >= thresh and vals[i] == max(vals[i - w:i + w + 1]):
            if not found or (i - found[-1]) / fps > sep:
                found.append(i)
            elif vals[i] > vals[found[-1]]:
                found[-1] = i
    return found


def segment(trial, what):
    """The moves in one recording: [{kind, side, at (s), start, end}]."""
    c = clip(trial)
    F = _local(c)
    fps = c.fps
    arm = (c.roles["l_arm"][0] - c.roles["l_elbow"][0]).length + (c.roles["l_elbow"][0] - c.roles["l_wrist"][0]).length
    L = c.leg_length
    moves = []

    def add(kind, side, i, **kw):
        before, after = WINDOW.get(kind, (0.6, 0.6))
        at = i / fps
        moves.append(dict(trial=trial, kind=kind, side=side, at=at, start=max(0.0, at - before),
                          end=min(c.length, at + after), **kw))
    if "punches" in what or "blocks" in what:
        for s, side in (("l", 1), ("r", -1)):
            ext = [-(f[f"{s}_wrist"] - f["chest"]).y / arm for f in F]
            for i in _peaks(ext, fps, 0.78, 0.35):
                if "blocks" in what:
                    add("block", side, i)
                    continue
                j = max(0, i - int(0.12 * fps))
                v = F[i][f"{s}_wrist"] - F[j][f"{s}_wrist"]
                fwd, across, up = -v.y, v.x * side, v.z      # across: towards the other side of the body
                style = "uppercut" if up > 0.8 * max(fwd, 1e-6) else "hook" if -across > 0.7 * max(fwd, 1e-6) else "straight"
                add("punch", side, i, style=style)
    if "kicks" in what:
        for s, side in (("l", 1), ("r", -1)):
            lift = [(f[f"{s}_ankle"].z - min(f["l_ankle"].z, f["r_ankle"].z)) / L for f in F]
            for i in _peaks(lift, fps, 0.55, 0.6):
                add("kick", side, i)
    for special in ("spin_kick", "flying_kick"):
        if special in what:
            lift = [max(f["l_ankle"].z, f["r_ankle"].z) - min(f["l_ankle"].z, f["r_ankle"].z) for f in F]
            i = max(range(len(lift)), key=lambda k: lift[k])
            side = 1 if F[i]["l_ankle"].z > F[i]["r_ankle"].z else -1
            add(special, side, i)
    if "ducks" in what:
        head = [f["head"].z + f["_hips"].z for f in F]
        stand = sorted(head)[int(0.8 * len(head))]
        for i in _peaks([stand - h for h in head], fps, 0.18 * stand, 0.8):
            add("duck", 0, i)
    if "get_up" in what or "get_up_face_down" in what:
        # from just before the head comes up off the floor to just after they're standing
        head = [f["head"].z + f["_hips"].z - c.floor for f in F]
        stand = sorted(head)[int(0.95 * len(head))]
        up = next((i for i, h in enumerate(head) if h > 0.85 * stand), len(head) - 1)
        low = max((i for i in range(up) if head[i] < 0.3 * stand), default=0)
        moves.append(dict(trial=trial, kind="get_up_face_down" if "get_up_face_down" in what else "get_up", side=0,
                          at=max(0.0, low / fps - 0.3), start=max(0.0, low / fps - 0.3),
                          end=min(c.length, up / fps + 0.3)))
    if "stance" in what:
        # stretches with the guard up and no blow thrown: a fighter's stance, bouncing and circling
        busy = set()
        for m in moves:
            busy.update(range(int((m["at"] - 0.6) * fps), int((m["at"] + 0.6) * fps)))
        run = 0
        for i, f in enumerate(F):
            guard = min(f["l_wrist"].z, f["r_wrist"].z) > f["chest"].z - 0.05 and i not in busy
            run = run + 1 if guard else 0
            if run == int(1.6 * fps):
                moves.append(dict(trial=trial, kind="stance", side=0, at=(i - run) / fps,
                                  start=(i - run) / fps, end=i / fps))
                run = 0
    return moves


_INDEX = None


def index():
    """Every move in the library (found once, then kept with the recordings)."""
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    path = os.path.join(CACHE, "moves.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
            if data.get("version") == VERSION:
                _INDEX = data["moves"]
                return _INDEX
        except (OSError, ValueError):
            pass
    moves = []
    for trial, what in SOURCES.items():
        if all(os.path.exists(p) for p in _paths(trial)):
            moves += segment(trial, what)
    if moves:
        with open(path, "w") as f:
            json.dump({"version": VERSION, "moves": moves}, f)
    _INDEX = moves
    return moves


# dreamreel's moves, and what to look for among the captured ones
WANTS = {
    "jab": dict(kind="punch", style="straight", side=1), "punch": dict(kind="punch", style="straight", side=-1),
    "hook": dict(kind="punch", style="hook"), "uppercut": dict(kind="punch", style="uppercut"),
    "kick": dict(kind="kick"), "spin_kick": dict(kind="spin_kick"), "flying_kick": dict(kind="flying_kick"),
    "block": dict(kind="block"), "dodge": dict(kind="duck"), "get_up": dict(kind="get_up"),
    "get_up_face_down": dict(kind="get_up_face_down"), "stance": dict(kind="stance"),
}


def pick(move, rng=None, side=None):
    """A captured version of one of dreamreel's moves (jab, hook, kick, block, dodge, get_up...), or None.
    Returns (move, mirror): mirror when it was captured on the other side."""
    want = WANTS.get(move)
    if want is None or not installed():
        return None
    rng = rng or random
    cands = [m for m in index() if m["kind"] == want["kind"] and m.get("style", want.get("style")) == want.get("style", m.get("style"))]
    if not cands and want.get("style"):                 # no uppercut captured: any punch from that side
        cands = [m for m in index() if m["kind"] == want["kind"]]
    if not cands:
        return None
    side = side if side is not None else want.get("side")
    same = [m for m in cands if side is None or m["side"] in (side, 0)]
    m = rng.choice(same or cands)
    return m, bool(side is not None and m["side"] not in (side, 0))


def play(c, move, hit, mirror=False, drift=None, lead=None, in_place=False):
    """Play a captured move on `c` so its blow lands at `hit` (seconds), starting at most `lead` before
    it. `drift`: (x, y) metres to travel by the blow (stepping in to reach). Returns the end time."""
    cl = clip(move["trial"])
    start = move["start"] if lead is None else max(move["start"], move["at"] - lead)
    t0 = hit - (move["at"] - start)
    return c.perform_clip(cl, t0, mirror=mirror, in_place=in_place, start=start, end=move["end"], drift=drift,
                          drift_until=max(0.05, move["at"] - start))
