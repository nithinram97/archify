"""Acting from a sentence: a character does what you describe, as motion made by an AI model.

    [[beats]]
    who = "gran"
    do = "act"
    what = "slowly gets up from the bench, stretches her back and sighs"
    seconds = 5

The motion comes from Tencent's HY-Motion 1.0 (text to 3D human motion) running on a booster (see
boost.py and docs/boosters.md): it needs a graphics card. Each motion is made once and kept in the film's
motions/ai/ folder, so it never changes unless you change the words (or `take`, to ask for another
version), and it plays like any motion-capture clip: on toy figures and on people from the 3D packs.

Without a booster, the character does the closest gesture they know (a wave for "waves", a shrug for
"shrugs" ...) and dreamreel says what it would need for the real thing.

HY-Motion's licence (Tencent HY-Motion 1.0 Community License) doesn't cover the EU, the UK or South
Korea, and its output may not be used to train other AI models; a film maker there can't use this beat.
"""
import hashlib
import os
import re

SKILL = "motion.hy_motion"
# words in the description -> a gesture to do instead, when there's no booster
FALLBACK = (("wave", "wave"), ("cheer", "cheer"), ("celebrat", "cheer"), ("shrug", "shrug"), ("point", "point"),
            ("clap", "clap"), ("bow", "bow"), ("think", "think"), ("ponder", "think"), ("facepalm", "facepalm"),
            ("despair", "facepalm"), ("punch", "punch"), ("kick", "kick"), ("pick", "pick_up"), ("roll", "roll"),
            ("nod", "nod"), ("shake", "shake_head"), ("jump", "jump"), ("dance", "dance"))
_warned = set()


def _say(msg):
    if msg not in _warned:
        _warned.add(msg)
        print(f"[dreamreel] {msg}")


def path_for(root, what, seconds, take=1):
    """Where the motion for these words is kept: motions/ai/<words>-<hash> (.fbx, or .bvh)."""
    key = f"{' '.join(what.lower().split())}|{float(seconds):.2f}|{int(take)}"
    slug = re.sub(r"[^a-z0-9]+", "-", what.lower()).strip("-")[:40] or "motion"
    return os.path.join(root, "motions", "ai", f"{slug}-{hashlib.sha1(key.encode()).hexdigest()[:8]}")


def clip_for(scene, what, seconds=4.0, take=1):
    """The motion for this description: kept from before, or made now on a booster; None if neither."""
    from . import boost
    root = scene.project.root if scene.project else None
    if root is None:
        return None
    base = path_for(root, what, seconds, take)
    for ext in (".fbx", ".bvh"):
        if os.path.exists(base + ext):
            return base + ext
    b = boost.configured()
    skill = os.environ.get("DREAMREEL_MOTION_SKILL") or SKILL
    if b is None or not b.has(skill):
        _say("acting from a sentence (do = \"act\") needs a booster with a graphics card (see `dreamreel "
             "boost`); doing the closest gesture instead")
        return None
    seconds = max(0.7, min(12.0, float(seconds)))
    print(f"[dreamreel] making a motion on the booster: {what!r} ({seconds:g} s) ...")
    try:
        out = b.run(skill, {"text": what, "seconds": seconds, "seed": int(take)}, out_dir=os.path.dirname(base),
                    timeout=3600)
    except boost.BoostError as e:
        _say(f"the booster couldn't make the motion ({e}); doing the closest gesture instead")
        return None
    path = base + os.path.splitext(out["motion"])[1].lower()
    os.replace(out["motion"], path)
    if out.get("npz") and os.path.exists(out["npz"]):
        os.replace(out["npz"], base + ".npz")            # the raw SMPL-H data, kept beside it
    return path


def fallback_gesture(what, can):
    """The closest gesture this character can do, for when there's no motion."""
    low = what.lower()
    for word, gesture in FALLBACK:
        if word in low and can(gesture):
            return gesture
    return None
