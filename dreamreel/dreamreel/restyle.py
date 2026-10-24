"""Restyling (experimental): an AI video model repaints a rendered scene in a style you describe,
keeping its staging and motion.

    # a scene file (or film.toml's [restyle], for every scene)
    restyle = "a watercolour painting, soft paper texture, gentle light"
    restyle_strength = 0.5       # 0.1 barely changes it ... 0.9 repaints it freely

Wan 2.1 (1.3B, Apache-2.0) does the painting, on a booster (boost.py, docs/boosters.md), a few seconds of
film at a time. Only final renders are restyled (not previz); the restyled scene is kept beside the
plain one (renders/final/<scene>.restyled.mp4) and made again only if the scene or the style changes.
It's experimental: expect some flicker between frames, and several minutes of booster time for every
few seconds of film. Set restyle = "" in a scene to keep that one as rendered.
"""
import hashlib
import os
import tomllib

SKILL = "restyle.wan"
_warned = set()


def _say(msg):
    if msg not in _warned:
        _warned.add(msg)
        print(f"[dreamreel] {msg}")


def wanted(proj, path):
    """(style, strength) asked for by the scene, else by film.toml's [restyle]; (None, 0) for none."""
    film = dict(proj.film.get("restyle") or {})
    style, strength = film.get("prompt") or film.get("restyle"), film.get("strength", 0.5)
    if path.endswith(".toml"):
        with open(path, "rb") as f:
            spec = tomllib.load(f)
        if "restyle" in spec:
            style = spec["restyle"]
        strength = spec.get("restyle_strength", strength)
    if not style:
        return None, 0.0
    return str(style), max(0.1, min(0.9, float(strength)))


def _digest(video, style, strength):
    h = hashlib.sha1(f"{style}|{strength:.2f}|".encode())
    with open(video, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def apply(proj, meta, path, quality):
    """Point the scene's metadata at its restyled video (making it on a booster if needed)."""
    from . import boost
    plain = meta.get("video_plain") or meta.get("video")
    meta["video"] = plain
    meta["video_plain"] = plain
    style, strength = wanted(proj, path)
    if not style or quality != "final" or not plain or not os.path.exists(plain):
        return meta
    out = os.path.splitext(plain)[0] + ".restyled.mp4"
    digest = _digest(plain, style, strength)
    if os.path.exists(out) and meta.get("restyle", {}).get("hash") == digest:
        meta["video"] = out
        return meta
    skill = os.environ.get("DREAMREEL_RESTYLE_SKILL") or SKILL
    b = boost.configured()
    if b is None or not b.has(skill):
        _say("restyling needs a booster with a graphics card (see `dreamreel boost`); scenes stay as rendered")
        return meta
    print(f"[dreamreel] {meta.get('name')}: restyling on the booster as {style!r} (this takes a while) ...", flush=True)
    try:
        got = b.run(skill, {"prompt": style, "strength": strength}, {"video": plain},
                    out_dir=os.path.dirname(out), timeout=6 * 3600, log=lambda line: print(f"  booster: {line}"))
    except boost.BoostError as e:
        _say(f"restyling failed ({e}); the scene stays as rendered")
        return meta
    os.replace(got["video"], out)
    meta["video"] = out
    meta["restyle"] = {"style": style, "strength": strength, "hash": digest}
    return meta
