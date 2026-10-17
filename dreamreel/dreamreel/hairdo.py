"""Hair for people, styled the way animated-film hair is sculpted (see docs/modeling.md).

Not one shell over the head: a scalp mass cut to a real hairline (lower at the temples and the
nape), then locks (tapered clumps) grown from roots on the scalp along the style's flow: away
from the parting, pulled back to a bun or a tail, or falling with gravity, always kept just off the
head. Buns are locks coiled round a core; tails are bundles of locks.

    style = Style(parting=0.0, length=0.6, ...)   # see STYLES
    build(person, "space_buns", material)
"""
import math
import random

from mathutils import Vector

from . import shapes
from .sculpt import Clay

# A style: where the parting is (x across the head, in cranium radii; None for no parting), where
# the locks go (back, down, to buns or a tail), how long they are (cranium radii) and how full.
STYLES = {
    "short":      dict(parting=0.35, flow="back", length=0.7, lift=0.1, count=60, width=0.32, fringe=0.0),
    "bob":        dict(parting=0.3, flow="down", length=1.7, lift=0.09, count=80, width=0.34, fringe=0.55, curl_in=0.6),
    "long":       dict(parting=0.0, flow="down", length=3.4, lift=0.08, count=90, width=0.32, fringe=0.0),
    "ponytail":   dict(parting=None, flow="tail", length=0.0, lift=0.07, count=56, width=0.2,
                       tails=[(0.0, 0.85, 0.45)], tail_len=2.2),
    "bun":        dict(parting=None, flow="tail", length=0.0, lift=0.07, count=56, width=0.2,
                       buns=[(0.0, 0.35, 1.0)], bun_r=0.4),
    "space_buns": dict(parting=0.0, flow="buns", length=0.0, lift=0.07, count=60, width=0.2,
                       buns=[(0.6, 0.12, 0.82), (-0.6, 0.12, 0.82)], bun_r=0.33),
    "pigtails":   dict(parting=0.0, flow="tail", length=0.0, lift=0.07, count=60, width=0.2,
                       tails=[(0.85, 0.35, 0.1), (-0.85, 0.35, 0.1)], tail_len=1.6),
    "curly":      dict(parting=None, flow="curls", length=0.5, lift=0.22, count=80, width=0.2, fringe=0.0),
    "spiky":      dict(parting=None, flow="up", length=0.6, lift=0.1, count=40, width=0.22, fringe=0.0),
}


def supported(name):
    return name in STYLES


def _spherical(theta, phi):
    """A direction from the cranium centre: theta from the top (0) down, phi round from the front."""
    return Vector((math.sin(theta) * math.sin(phi), -math.sin(theta) * math.cos(phi), math.cos(theta)))


def _in_hair(d, hairline):
    """Whether a direction from the cranium centre is on the hairy part of the scalp: above the
    hairline, which sits high on the forehead, dips at the temples, passes above the ears and runs
    low round the back to the nape."""
    phi = math.atan2(d.x, -d.y)                      # 0 front, ±pi back
    front = math.cos(phi)                            # 1 at the face, -1 at the back
    if front >= 0:
        z_line = hairline - 0.4 * (1 - front)
    else:
        z_line = hairline - 0.4 - 0.3 * -front
    z_line -= 0.07 * math.exp(-((abs(phi) - 0.75) / 0.25) ** 2)      # the temples
    return d.z > z_line


def build(c, style, material):
    """Grow a hairstyle on person `c` (its head clay: c.clay, cranium radius c.hr)."""
    st = STYLES[style]
    R, clay, hc = c.hr, c.clay, c.hc
    rng = random.Random(f"{c.name}.{style}")
    tree = clay.tree()
    hairline = getattr(c, "L", {}).get("brow_z", -0.05) + 0.42       # forehead hairline (cranium radii)
    parts = []

    def outside(p, gap):
        """Keep a point at least `gap` off the head."""
        near = tree.find_nearest(p)
        if near[0] is None:
            return p
        q, n = Vector(near[0]), Vector(near[1])
        if (p - q).dot(n) < gap:
            return q + n * gap
        return p

    # 1. the scalp mass, so no scalp shows between the locks
    cap = Clay.sphere(R * (1.0 + st["lift"] * 0.6), detail=4)
    cap.v = cap.v * [0.95, 1.02, 1.0]
    keep = [i for i, p in enumerate(cap.v) if _in_hair(Vector(p).normalized(), hairline - 0.05)]
    keep_set = set(keep)
    faces = [f for f in cap.f if all(i in keep_set for i in f)]
    index = {old: new for new, old in enumerate(sorted({i for f in faces for i in f}))}
    scalp = Clay([cap.v[i] for i in sorted(index)], [[index[i] for i in f] for f in faces])
    scalp.smooth(2, amount=0.3)
    for k, p in enumerate(scalp.v):                    # sit just off the sculpted head, wherever it bulges
        scalp.v[k] = outside(Vector(p), R * st["lift"] * 0.55)[:]
    parts.append(scalp.object(f"{c.name}.hair", material, c.neck, at=hc))

    # 2. the locks
    def target(root):
        """Where a lock from this root goes, as a list of points (head space)."""
        d = root.normalized()
        flow = st["flow"]
        pts = [root]
        if flow in ("buns", "tail"):          # pulled tight to the nearest bun or tail
            anchors = [Vector(b) * R for b in st.get("buns", []) + st.get("tails", [])]
            goal = min(anchors, key=lambda a: (a - root).length)
            n = 8
            for k in range(1, n + 1):
                p = root.lerp(goal, k / n)
                pts.append(outside(p, R * st["lift"]))
            return pts
        side = 0.0 if st["parting"] is None else (1 if d.x >= st["parting"] * 0.35 else -1)
        n = max(5, int(6 + st["length"] * 3))
        gap = R * st["lift"]
        for k in range(1, n + 1):
            p = pts[-1]
            near = tree.find_nearest(p)
            normal = Vector(near[1]) if near[0] is not None else p.normalized()
            u = k / n
            # where the hair wants to go: away from the parting first, then down (or back, or up)
            if flow == "down":
                want = Vector((side * 1.2 * max(0.0, 1 - 3 * u), 0.15, -1.0))
            elif flow == "back":
                want = Vector((side * 0.5 * max(0.0, 1 - 2 * u), 1.0, -0.35))
            elif flow == "up":
                want = (normal + Vector((0, 0.35, 0.8))).normalized()
            else:                                    # curls: round and round as they go
                want = Vector((math.cos(k * 1.9 + root.x * 50), math.sin(k * 1.9 + root.y * 50), -0.5))
            if flow in ("down", "back") and p.y < -0.15 * R and abs(p.x) < 0.85 * R and p.z < (hairline + 0.15) * R:
                sx = 1.0 if (p.x > 0 or (abs(p.x) < 1e-6 and side >= 0)) else -1.0
                want = want + Vector((sx * 1.6, 0.7, 0.0))     # frame the face: sweep to the side, not over it
            if flow in ("down", "back") and p.y < -0.15 * R and abs(p.x) < 0.85 * R and p.z < (hairline + 0.15) * R:
                sx = 1.0 if (p.x > 0 or (abs(p.x) < 1e-6 and side >= 0)) else -1.0
                want = want + Vector((sx * 1.6, 0.7, 0.0))     # frame the face: sweep to the side, not over it
            if flow != "up":                         # lie along the head while on it
                on_head = (p - Vector(near[0])).length < gap * 1.6 if near[0] is not None else False
                if on_head:
                    want = want - normal * want.dot(normal)
            q = p + want.normalized() * st["length"] * R / n * (1.0 if flow != "curls" else 0.6)
            if flow == "down" and u > 0.75:          # bobs curl under at the ends
                q += Vector((-p.x, -p.y, 0)).normalized() * st.get("curl_in", 0) * R * 0.08
            pts.append(outside(q, gap))
        return pts

    count = st["count"]
    golden = math.pi * (3 - math.sqrt(5))
    roots = []
    for k in range(count * 3):                          # spread roots evenly over the scalp
        z = 1 - (k + 0.5) / (count * 3) * 1.6
        r = math.sqrt(max(0.0, 1 - z * z))
        d = Vector((r * math.cos(golden * k), r * math.sin(golden * k), z))
        if _in_hair(d, hairline):
            roots.append(d)
    rng.shuffle(roots)
    roots = roots[:count]
    from .people import _skin_mesh
    for k, d in enumerate(roots):
        root = outside(d * R, R * st["lift"] * 0.5)
        pts = target(root)
        if len(pts) < 2:
            continue
        width = st["width"] * R * rng.uniform(0.75, 1.2)
        nodes = []
        for i, p in enumerate(pts):
            u = i / (len(pts) - 1)
            taper = (1 - u) ** 0.7 * 0.85 + 0.15 if st["flow"] not in ("buns", "tail") else 1 - 0.4 * u
            nodes.append((p, (width * taper * 0.5, width * taper * 0.22)))
        lock = _skin_mesh(f"{c.name}.hair", nodes, [(i, i + 1) for i in range(len(nodes) - 1)])
        lock.data.materials.append(material)
        lock.parent = c.neck
        lock.location = hc
        parts.append(lock)

    # 3. fringe: locks over the forehead
    for k in range(int(st.get("fringe", 0) * 14)):
        x = (k / 13 - 0.5) * 1.1 * R
        top = outside(Vector((x * 0.8, -0.55 * R, (hairline + 0.25) * R)), R * st["lift"])
        end = outside(Vector((x * 1.05, -0.95 * R, (hairline - 0.2) * R)), R * st["lift"])
        mid = outside(top.lerp(end, 0.5) + Vector((0, -0.08 * R, 0)), R * st["lift"])
        w = st["width"] * R * rng.uniform(0.8, 1.1)
        lock = _skin_mesh(f"{c.name}.hair", [(top, (w * 0.5, w * 0.2)), (mid, (w * 0.42, w * 0.18)),
                                              (end, (w * 0.12, w * 0.08))], [(0, 1), (1, 2)])
        lock.data.materials.append(material)
        lock.parent = c.neck
        lock.location = hc
        parts.append(lock)

    # 4. buns (locks coiled round a core) and tails (a bundle of locks)
    for b in st.get("buns", []):
        centre = Vector(b) * R
        out = centre.normalized()
        br = st["bun_r"] * R
        parts.append(shapes.sphere(f"{c.name}.hair", br * 0.9, material, c.neck, at=hc + centre + out * br * 0.6))
        a = out.cross(Vector((0, 0, 1)) if abs(out.z) < 0.99 else Vector((1, 0, 0))).normalized()
        bvec = out.cross(a).normalized()
        for ring in range(3):
            nodes = []
            for k in range(14):
                ang = k / 13 * math.tau * 0.95 + ring * 2.1
                rr = br * (0.95 - 0.12 * ring)
                p = centre + out * (br * (0.3 + 0.35 * ring)) + (a * math.cos(ang) + bvec * math.sin(ang)) * rr
                nodes.append((p, (br * 0.33, br * 0.2)))
            lock = _skin_mesh(f"{c.name}.hair", nodes, [(i, i + 1) for i in range(len(nodes) - 1)])
            lock.data.materials.append(material)
            lock.parent = c.neck
            lock.location = hc
            parts.append(lock)
    for tx, ty, tz in st.get("tails", []):
        base = Vector((tx, ty, tz)) * R
        out = base.normalized()
        parts.append(shapes.sphere(f"{c.name}.hair", 0.16 * R, material, c.neck, at=hc + base + out * 0.08 * R))
        for k in range(7):
            spread = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.08 * R
            pts = [base + out * 0.1 * R]
            for i in range(1, 6):
                u = i / 5
                pts.append(base + out * (0.25 + 0.2 * u) * R + spread * u * 2 +
                           Vector((0, 0.25 * u, -st["tail_len"] * u)) * R)
            nodes = [(p, (0.13 * R * (1 - 0.7 * i / 5), 0.08 * R * (1 - 0.7 * i / 5))) for i, p in enumerate(pts)]
            lock = _skin_mesh(f"{c.name}.hair", nodes, [(i, i + 1) for i in range(len(nodes) - 1)])
            lock.data.materials.append(material)
            lock.parent = c.neck
            lock.location = hc
            parts.append(lock)
    return parts
