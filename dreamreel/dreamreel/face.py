"""Faces that can do more than smile and frown.

The toy face has a handful of controls, after the action units of Ekman and Friesen's Facial Action
Coding System (FACS) that matter most at toy scale:

| Control | Range | What it does | FACS |
|---|---|---|---|
| `brow_tilt`, `brow_lift` | degrees, height | inner ends up (sad) or down (angry); raised | AU1, AU2, AU4 |
| `brow_squeeze` | 0-1 | brows pulled together (concentration, anger) | AU4 |
| `eyes` | 0.4-1.5 | eye size: narrowed ... wide open | AU5, AU7 |
| `pupils` | 0.3-1 | iris and pupil shrink in the whites (crazed, terrified) | |
| `lids` | 0-1 | upper lids come down (sleepy, bored, suspicious) | AU43 |
| `squint` | 0-1 | lower lids come up: cheeks raised in a real smile, or a glare | AU6, AU7 |
| `lid_slant` | -1-1 | the lid line slopes: -1 angry (low by the nose), 1 sad | |
| `smile`, `frown` | 0-1 | mouth corners up, down | AU12, AU15 |
| `wide` | 0-1 | lips stretched wide (fear, gritted teeth, a big grin) | AU20 |
| `o` | 0-1 | lips rounded (surprise, "ooh") | AU18, AU22 |
| `smirk` | -1-1 | one corner up (smirk), or a sneer on the other side | AU12 (one side), AU10 |
| `mouth_open` | 0-1 | jaw drop | AU26, AU27 |
| `teeth` | 0-1 | teeth showing: upper only up to 0.5, both (clenched) above | AU25 |
| `blush`, `tears`, `sweat` | 0-1 | cheeks colour up, tears run, a drop of nervous sweat | |
| `head_tilt` | degrees | forward (+) or back (-) | |

Moods (parts.py) are sets of these; `feel(mood, how_much=1.5)` pushes one further.
"""
import math

from mathutils import Vector

from . import look, shapes
from .keys import hold, key, value_at

LID_KEYS = ("upper", "lower", "angry", "sad")
MOUTH_KEYS = ("smile", "frown", "wide", "o", "smirk")
CONTROLS = ("brow_tilt", "brow_lift", "brow_squeeze", "smile", "frown", "eyes", "pupils", "lids", "squint",
            "lid_slant", "wide", "o", "smirk", "mouth_open", "teeth", "blush", "tears", "sweat", "head_tilt")
NEUTRAL = {"eyes": 1.0, "pupils": 1.0}


def _deg(d):
    return math.radians(d)


def lid_keys(obj, rx, rz, side, pad=0.0):
    """Upper and lower lids, as shape keys that flatten the eye along a lid line (eye space); `pad`
    moves the line out (for an outline round the eye)."""
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis")
    inner = -side             # +x of this eye towards the nose is -side

    def clamp(name, fn):
        sk = obj.shape_key_add(name=name, from_mix=False)
        sk.value = 0.0                      # new keys start fully on; the face starts neutral
        for v in sk.data:
            v.co.z = fn(v.co.x, v.co.z)
    clamp("upper", lambda x, z: min(z, pad))
    clamp("lower", lambda x, z: max(z, -0.2 * rz - pad))
    clamp("angry", lambda x, z: min(z, 0.25 * rz + pad - 0.5 * rz * (inner * x / rx)))
    clamp("sad", lambda x, z: min(z, 0.25 * rz + pad + 0.5 * rz * (inner * x / rx)))


def mouth_keys(obj, rx, rz, H):
    """smile, frown, wide, o (round) and smirk (one corner up) on a mouth (or teeth) mesh."""
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis")
    have = set(obj.data.shape_keys.key_blocks.keys())

    def shape(name, fn):
        if name in have:
            return
        sk = obj.shape_key_add(name=name, from_mix=False)
        sk.value = 0.0
        for v in sk.data:
            v.co = fn(v.co.copy())
    for name, sign in (("smile", 1), ("frown", -1)):
        shape(name, lambda c, s=sign: Vector((c.x, c.y, c.z + s * 0.022 * H * (c.x / (0.042 * H)) ** 2
                                              - s * 0.004 * H)))
    shape("wide", lambda c: Vector((c.x * 1.5, c.y, c.z * 0.85)))
    shape("o", lambda c: Vector((c.x * 0.62, c.y, c.z * 1.35)))
    shape("smirk", lambda c: Vector((c.x, c.y, c.z + 0.026 * H * max(0.0, c.x / rx) ** 2
                                     - 0.006 * H * max(0.0, -c.x / rx) ** 2)))
    for kb in obj.data.shape_keys.key_blocks[1:]:     # room to push past 1 (how_much), and a sneer
        kb.slider_max = 1.5
        if kb.name == "smirk":
            kb.slider_min = -1.0


def build(c):
    """Add the richer parts to a toy face built by Character.build_face: eye whites, lids, teeth,
    braces. Sets c.irises, c.scleras, c.glints, c.teeth, c.blushes, c.mouth_parts."""
    H, n = getattr(c, "face_H", c.H), c.name
    es = {"small": 0.8, "normal": 1.0, "big": 1.3}.get(c.get("eyes"), 1.0)
    rx, rz = 0.03 * H * es, 0.043 * H * es
    c.irises, c.scleras, c.glints = [], [], []
    gazes = getattr(c, "gazes", [])
    for side, piv in zip((1, -1), c.eyes):
        kids = piv.children_recursive
        ball = next((o for o in piv.children if o.name.startswith(f"{n}.eye")), None)
        if ball is None:
            continue
        if gazes:           # white eyes: lids close over the eyeball, the iris and the pupil
            dark = [o for o in kids if o.name.startswith((f"{n}.iris", f"{n}.pupil"))]
            white = ball
            # a dark rim round the eye: it draws the lid line when the lids come down
            rim = shapes.ellipsoid(f"{n}.eyeline", rx * 1.1, 0.019 * H, rz * 1.07, look.plastic("#3b2922", 0.4, 0.2),
                                   piv, at=(0, 0.0012 * H, 0), segments=32)
            lid_keys(rim, rx * 1.1, rz, side, pad=0.07 * rz)
            c.scleras.append(rim)
        else:               # bead eyes: a white behind the bead shows when the "pupil" shrinks
            dark = [ball]
            white = shapes.ellipsoid(f"{n}.white", rx * 0.99, 0.019 * H, rz * 0.99,
                                     look.plastic("#f7f4ee", 0.3, 0.3), piv, at=(0, 0.0015 * H, 0))
        for o in dark + [white]:
            lid_keys(o, rx, rz, side)
        c.irises += dark
        c.scleras.append(white)
        c.glints += [g for g in kids if ".glint" in g.name]
    mouth_parts(c, 0.042 * H, 0.012 * H, front=0.016 * H)
    c.blushes = [o for o in c.neck.children if o.name.startswith(f"{n}.blush")]


def mouth_parts(c, mrx, mrz, front, extra=(), teeth_z=0.42):
    """Mouth shapes on c.mouth_mesh (and `extra` meshes like lips), upper and lower teeth, braces."""
    H, n = getattr(c, "face_H", c.H), c.name
    m = c.mouth_mesh
    for o in [m] + list(extra):
        mouth_keys(o, mrx, mrz, H)
    c.teeth = {}
    tooth = look.plastic("#fbf8f0", 0.35, 0.3)
    for where, z in (("upper", 1), ("lower", -1)):
        t = shapes.ellipsoid(f"{n}.teeth.{where}", mrx * 0.82, 0.006 * H, mrz * 0.5, tooth, c.mouth,
                             at=(0, -front, z * mrz * teeth_z), segments=24)
        mouth_keys(t, mrx * 0.82, mrz * 0.5, H)
        t.scale = (1, 1, 0.0)
        c.teeth[where] = t
    if c.get("braces"):
        shapes.box(f"{n}.braces", mrx * 1.4, 0.004 * H, mrz * 0.18, look.metal("#c9ced3"), c.teeth["upper"],
                   at=(0, -0.004 * H, -mrz * 0.12), bevel=0)
    c.mouth_parts = [m] + list(extra) + list(c.teeth.values())


def lid_angles(v, side):
    """Rotations (about the eye's x axis) of an upper and a lower lid of skin that slide over an
    eyeball, and the tilt of the lid line, from the face controls. Lid edges are given as heights on
    the eyeball (-1 bottom ... 1 top); a lid edge at height h is a rotation of -asin(h)."""
    up = 0.62 + max(0.0, v["eyes"] - 1) * 0.9 - max(0.0, 1 - v["eyes"]) * 1.3   # resting: a little over the iris
    up = min(0.98, up)
    up += (-0.05 - up) * min(1.0, v["lids"])                                       # lids 1: half closed
    low = -0.78 + 0.62 * min(1.0, v["squint"])
    low = max(low, -0.98)
    up = max(up, low + 0.05)
    tilt = math.radians(26) * v["lid_slant"] * side
    return -math.asin(max(-1, min(1, up))), -math.asin(max(-1, min(1, low))), tilt


def values(mood, amount=1.0):
    """A mood's controls, pushed towards (amount < 1) or past (> 1) its extremes from neutral."""
    out = {}
    for k in CONTROLS:
        v = float(getattr(mood, k, NEUTRAL.get(k, 0.0)))
        base = NEUTRAL.get(k, 0.0)
        out[k] = base + (v - base) * amount
    for k in ("smile", "frown", "wide", "o", "teeth", "lids", "squint", "brow_squeeze", "blush", "tears",
              "sweat", "mouth_open"):
        out[k] = max(0.0, min(1.3, out[k]))
    out["pupils"] = max(0.25, min(1.0, out["pupils"]))
    out["eyes"] = max(0.3, out["eyes"])
    return out


def apply(c, v, t, t1):
    """Key the face to the control values `v` by t1 (holding what it was at t)."""
    H = getattr(c, "face_H", c.H)
    for side, brow in c.brows.items():
        hold(brow, "rotation_euler", t)
        hold(brow, "location", t)
        key(brow, "rotation_euler", t1, (0, _deg(v["brow_tilt"]) * side, 0))
        base = brow.get("z0", brow.location.z)
        brow["z0"] = base
        bx = brow.get("x0", brow.location.x)
        brow["x0"] = bx
        loc = value_at(brow, "location", t)
        key(brow, "location", t1, (bx - side * 0.014 * H * v["brow_squeeze"], loc[1],
                                   base + v["brow_lift"] * H - 0.006 * H * v["brow_squeeze"]))
    k = getattr(c, "eye_scale", 1.0)          # how much "eyes" grows the eyeball (people: a little)
    for e in c.eyes:
        size = 1 + (v["eyes"] - 1) * k
        hold(e, "scale", t)
        key(e, "scale", t1, (size, 1, size))
        e["open"] = size
    slant = v["lid_slant"]
    for side, (up, low) in getattr(c, "lid_pivots", {}).items():
        a_up, a_low, tilt = lid_angles(v, side)
        for o, rot in ((up, (a_up, tilt, 0)), (low, (a_low, -0.4 * tilt, 0))):
            hold(o, "rotation_euler", t)
            key(o, "rotation_euler", t1, rot)
        up["open"] = a_up
    lids = {"upper": v["lids"], "lower": v["squint"], "angry": max(0.0, -slant), "sad": max(0.0, slant)}
    for o in getattr(c, "irises", []) + getattr(c, "scleras", []):
        kb = o.data.shape_keys.key_blocks
        for name, val in lids.items():
            hold(kb[name], "value", t)
            key(kb[name], "value", t1, min(1.0, val))
    p = v["pupils"]
    gazes = getattr(c, "gazes", None)
    if gazes:      # the iris shrinks a little, the pupil more: a pinprick in a coloured ring
        g = math.sqrt(p)
        for o in gazes:
            hold(o, "scale", t)
            key(o, "scale", t1, (g, 1, g))
            for pu in [k for k in o.children if ".pupil" in k.name]:
                hold(pu, "scale", t)
                key(pu, "scale", t1, (g, 1, g))
    else:          # bead eyes: the bead shrinks, showing the whites
        for o in getattr(c, "irises", []):
            hold(o, "scale", t)
            key(o, "scale", t1, (p, 1, p))
    for g in getattr(c, "glints", []):
        hold(g, "scale", t)
        gone = max(0.0, min(1.0, 1.4 * max(v["lids"], 0.6 * max(0.0, -slant))))
        key(g, "scale", t1, (1 - gone,) * 3)
    for o in getattr(c, "mouth_parts", [c.mouth_mesh]):
        kb = o.data.shape_keys.key_blocks
        for name, val in (("smile", v["smile"]), ("frown", v["frown"]), ("wide", v["wide"]), ("o", v["o"]),
                          ("smirk", v["smirk"])):
            if name in kb:
                hold(kb[name], "value", t)
                key(kb[name], "value", t1, val)
    mopen = max(v["mouth_open"], v["teeth"] * getattr(c, "teeth_open", 0.0))   # people part their lips to show teeth
    hold(c.mouth, "scale", t)
    key(c.mouth, "scale", t1, (1 - 0.3 * mopen, 1, 1 + 2.2 * mopen))
    c.mouth["rest"] = mopen
    teeth = getattr(c, "teeth", {})
    if teeth:
        up = min(1.0, v["teeth"] * 2)
        low = max(0.0, min(1.0, v["teeth"] * 2 - 1))
        squash = 1 / (1 + 2.2 * mopen)            # the mouth pivot stretches with the jaw; teeth don't
        for name, amt in (("upper", up), ("lower", low)):
            hold(teeth[name], "scale", t)
            key(teeth[name], "scale", t1, (1, 1, amt * squash))
    for b in getattr(c, "blushes", []):
        hold(b, "scale", t)
        k = 1 + 0.7 * v["blush"]
        key(b, "scale", t1, (k, 1 + 2 * v["blush"], k))
    hold(c.neck, "rotation_euler", t)
    cur = value_at(c.neck, "rotation_euler", t)
    key(c.neck, "rotation_euler", t1, (_deg(v["head_tilt"]), cur[1], cur[2]))


def drops(c, length):
    """Tears and sweat for the stretches of the scene in moods that have them (added at the end)."""
    from . import plugins
    moods = getattr(c, "_moods", [])
    if not moods or not getattr(c, "eyes", None):
        return
    spans = []
    for i, (t, name, amount) in enumerate(moods):
        end = moods[i + 1][0] if i + 1 < len(moods) else length
        v = values(plugins.get("mood", name), amount)
        if v["tears"] > 0.05 or v["sweat"] > 0.05:
            spans.append((t + 0.3, end, v["tears"], v["sweat"]))
    if not spans:
        return
    H, n = getattr(c, "face_H", c.H), c.name
    water = look.glass("#bfe6ff") if hasattr(look, "glass") else "#bfe6ff"
    for t0, t1, tears, sweat in spans:
        if tears > 0.05:
            for side, piv in zip((1, -1), c.eyes):
                start = piv.location + Vector((-side * 0.01 * H, -0.004 * H, -0.03 * H))
                tt = t0 + (0.0 if side > 0 else 0.35)
                while tt < t1 - 0.2:
                    d = shapes.sphere(f"{n}.tear", 0.012 * H * (0.7 + 0.3 * tears), water, c.neck, at=start,
                                      segments=12)
                    d.scale = (0.8, 0.8, 1.3)
                    fall = 0.075 * H
                    key(d, "scale", tt - 0.01, (0, 0, 0), "cut")
                    key(d, "scale", tt, (0.8, 0.8, 1.3), "cut")
                    key(d, "location", tt, tuple(start), "ease_in")
                    key(d, "location", tt + 0.9, tuple(start + Vector((0, 0.004 * H, -fall))), "linear")
                    key(d, "scale", tt + 0.9, (0.8, 0.8, 1.3), "cut")
                    key(d, "scale", tt + 0.91, (0, 0, 0), "cut")
                    tt += 1.1 - 0.4 * tears
        if sweat > 0.05:
            at = c.face_point(0.13 * H, 0.075 * H, 0.012)
            d = shapes.sphere(f"{n}.sweat", 0.014 * H, water, c.neck, at=at, segments=12)
            d.scale = (0.75, 0.75, 1.25)
            key(d, "scale", 0.0, (0, 0, 0), "cut")
            key(d, "scale", t0, (0.75, 0.75, 1.25), "cut")
            key(d, "location", t0, tuple(at), "ease_in")
            key(d, "location", min(t1, t0 + 1.6), tuple(at + Vector((0, 0, -0.03 * H))), "ease_in")
            key(d, "scale", t1, (0, 0, 0), "cut")
