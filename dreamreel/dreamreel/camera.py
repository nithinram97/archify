"""The camera, directed in film language.

    s.cut.wide()                      # the whole set
    s.cut.medium(mia)                 # waist up
    s.cut.close_up(mia)               # face
    s.cut.two_shot(mia, tom)          # both of them
    s.cut.over_shoulder(tom, on=mia)  # past Tom's shoulder onto Mia
    s.cut.auto()                      # let the director choose the coverage (the default)

Each cut starts at the scene's current time and holds until the next one. Framing is computed from
where the characters are at that moment. Two-person shots always stay on the same side of the line
between the characters (the 180-degree rule), so nobody seems to swap places across a cut.
"""
import math

import bpy
from mathutils import Vector

from . import keys
from .keys import key

SENSOR = 36.0


class Shot:
    def __init__(self, kind, at, subjects, pos, aim, lens, fstop, label):
        self.kind, self.at, self.subjects, self.pos, self.aim = kind, at, subjects, pos, aim
        self.lens, self.fstop, self.label = lens, fstop, label


class Director:
    def __init__(self, scene):
        self.scene = scene
        cam_data = bpy.data.cameras.new("camera")
        cam_data.sensor_width = SENSOR
        cam_data.clip_start = 0.05
        cam_data.clip_end = 200
        self.cam = bpy.data.objects.new("camera", cam_data)
        bpy.context.scene.collection.objects.link(self.cam)
        bpy.context.scene.camera = self.cam
        self.aim = bpy.data.objects.new("camera.aim", None)
        bpy.context.scene.collection.objects.link(self.aim)
        c = self.cam.constraints.new("TRACK_TO")
        c.target = self.aim
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        cam_data.dof.use_dof = True
        cam_data.dof.focus_object = None
        self.shots = []
        self.manual = False

    # ------------------------------------------------------------------ helpers
    def _fov(self, lens):
        h = 2 * math.atan(SENSOR / 2 / lens)
        aspect = self.scene.size[1] / self.scene.size[0]
        v = 2 * math.atan(math.tan(h / 2) * aspect)
        return h, v

    def _dist_for_height(self, height, lens):
        _, v = self._fov(lens)
        return height / 2 / math.tan(v / 2)

    def _dist_for_width(self, width, lens):
        h, _ = self._fov(lens)
        return width / 2 / math.tan(h / 2)

    def _char(self, c):
        return self.scene.character(c)

    def _side(self, a, b, t):
        """Unit vector perpendicular to the line a-b, on the camera's side of the line for this pair."""
        pa, pb = a.position(t), b.position(t)
        d = pb - pa
        if d.length < 1e-3:
            return Vector((0, -1))
        n = Vector((-d.y, d.x)).normalized()
        pair = tuple(sorted((a.name, b.name)))
        chosen = self.scene._line_sides.get(pair)
        if chosen is None:
            chosen = n if n.y < 0 or (abs(n.y) < 1e-3 and n.x > 0) else -n
            self.scene._line_sides[pair] = chosen.copy() if a.name < b.name else -chosen
            return chosen
        stored = chosen if a.name < b.name else -chosen
        return n if n.dot(stored) >= 0 else -n

    def _keep_inside(self, pos, aim):
        """Keep the camera on the open side of a room and out of the walls."""
        st = self.scene.set
        if st is None or st.kind != "room":
            return pos
        W, D = st.width / 2 - 0.15, st.depth / 2 - 0.15
        p = Vector(pos)
        p.x = max(-W, min(W, p.x))
        p.y = min(D, p.y)
        return p

    def _add(self, kind, at, subjects, pos, aim, lens, fstop, label):
        at = self.scene._now() if at is None else at
        pos = self._keep_inside(pos, aim)
        self.shots.append(Shot(kind, at, subjects, Vector(pos), Vector(aim), lens, fstop, label))
        return self

    # ------------------------------------------------------------------ shot types
    def wide(self, at=None, height=None):
        """The whole set (or, outdoors, everyone in the scene)."""
        self.manual = True
        return self._wide(at, height)

    def _wide(self, at=None, height=None):
        t = self.scene._now() if at is None else at
        st = self.scene.set
        lens = 30
        chars = [c for c in self.scene.actors.values() if c.visible(t)]
        # frame where the action is: everyone visible now, plus wherever movers are heading
        pts = [c.position(t) for c in chars]
        for e in self.scene.events:
            if e["kind"] == "move" and e["t0"] <= t + 0.5 and e["t1"] >= t:
                pts.append(e["who"].position(e["t1"]))
        if not pts:
            pts = [Vector((0, 0))]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        width = max(4.2, max(xs) - min(xs) + 3.0)
        if st is not None and st.kind == "room":
            width = min(width, st.width * 0.95)
            cx = max(-st.width / 2 + width / 2, min(st.width / 2 - width / 2, cx))
        d = self._dist_for_width(width, lens) + (max(ys) - min(ys)) / 2
        pos = (cx, cy - d, height or (0.85 + 0.2 * d))
        aim = (cx, cy + 0.2, 0.45)
        return self._add("wide", t, chars, pos, aim, lens, 8.0, "wide")

    def medium(self, who, at=None, angle=20):
        """Waist up, slightly to one side of the face."""
        self.manual = True
        return self._single(who, at, "medium", 0.62, 45, angle)

    def close_up(self, who, at=None, angle=25):
        """The face fills the frame."""
        self.manual = True
        return self._single(who, at, "close_up", 0.42, 60, angle)

    def _single(self, who, at, kind, frame_h, lens, angle, toward=None):
        c = self._char(who)
        t = self.scene._now() if at is None else at
        head = c.head_point(t)
        fwd = c.forward(t)
        if toward is not None:
            # 3/4 view from the line side, looking at the character as they face their partner
            o = self._char(toward)
            to_o = (o.position(t) - c.position(t))
            to_o = to_o.normalized() if to_o.length > 1e-3 else fwd
            side = self._side(c, o, t)
            d2 = (to_o * 0.75 + side * 0.65).normalized()
        else:
            a = math.radians(angle)
            d2 = Vector((fwd.x * math.cos(a) - fwd.y * math.sin(a), fwd.x * math.sin(a) + fwd.y * math.cos(a)))
            if d2.y > 0.35:  # facing away from the open side: shoot from the front side anyway
                d2.y = -abs(d2.y)
                d2.normalize()
        H = c.H
        dist = self._dist_for_height(frame_h * H * 1.25, lens)
        aim = head + Vector((0, 0, -0.03 * H if kind == "close_up" else -0.12 * H))
        pos = aim + Vector((d2.x * dist, d2.y * dist, 0.04 * H))
        return self._add(kind, t, [c], pos, aim, lens, 2.8 if kind == "close_up" else 4.0, f"{kind}({c.name})")

    def two_shot(self, a, b, at=None):
        """Both characters, from their side of the line."""
        self.manual = True
        return self._two_shot(a, b, at)

    def _two_shot(self, a, b, at=None):
        a, b = self._char(a), self._char(b)
        t = self.scene._now() if at is None else at
        ha, hb = a.head_point(t), b.head_point(t)
        mid = (ha + hb) / 2
        side = self._side(a, b, t)
        lens = 35
        width = (ha - hb).length + 1.0 * max(a.H, b.H)
        dist = max(self._dist_for_width(width, lens), self._dist_for_height(1.2 * max(a.H, b.H), lens))
        aim = mid + Vector((0, 0, -0.2 * max(a.H, b.H)))
        pos = aim + Vector((side.x * dist, side.y * dist, 0.12))
        return self._add("two_shot", t, [a, b], pos, aim, lens, 4.0, f"two_shot({a.name}, {b.name})")

    def over_shoulder(self, past, on, at=None):
        """Over `past`'s shoulder, looking at `on`'s face."""
        self.manual = True
        return self._over_shoulder(past, on, at)

    def _over_shoulder(self, past, on, at=None):
        p, o = self._char(past), self._char(on)
        t = self.scene._now() if at is None else at
        hp, ho = p.head_point(t), o.head_point(t)
        d = Vector((hp.x - ho.x, hp.y - ho.y))
        if d.length < 1e-3:
            return self._single(o, t, "close_up", 0.42, 60, 25)
        u = d.normalized()
        side = self._side(p, o, t)
        # behind and to the side of the near character, at a height between the two faces, so the
        # near head fills about a third of the frame and the far face is clear
        back = 1.25 * p.H
        off = 0.55 * p.H
        z = max(hp.z, ho.z) * 0.6 + min(hp.z, ho.z) * 0.4 + 0.08 * p.H
        pos = Vector((hp.x + u.x * back + side.x * off, hp.y + u.y * back + side.y * off, z))
        aim = ho + Vector((0, 0, -0.06 * o.H)) + Vector((-side.x, -side.y, 0)) * 0.1 * o.H
        return self._add("over_shoulder", t, [o, p], pos, aim, 40, 4.0, f"over_shoulder({p.name} -> {o.name})")

    def from_point(self, where, look_at, at=None, lens=35, height=1.2):
        """Escape hatch: put the camera at a mark and aim it at a character or mark."""
        self.manual = True
        t = self.scene._now() if at is None else at
        p = self.scene._resolve(where, t)
        target = self.scene.character(look_at)
        aim = target.head_point(t) if target else Vector((*self.scene._resolve(look_at, t), 0.6))
        return self._add("custom", t, [], (p.x, p.y, height), aim, lens, 5.6, f"from {where}")

    # ------------------------------------------------------------------ automatic coverage
    def auto(self):
        """Choose shots from what happens: establish wide, cover dialogue with over-the-shoulders and
        close-ups on the speaker, go wide when people move about."""
        self.shots = []
        sc = self.scene
        events = sorted(sc.events, key=lambda e: e["t0"])
        self._wide(0.0)
        count = {}
        last_kind = "wide"
        for e in events:
            t0 = e["t0"]
            if e["kind"] == "move" and t0 > 0.5:
                if last_kind != "wide":
                    self._wide(max(0.0, t0 - 0.1))
                    last_kind = "wide"
                continue
            if e["kind"] != "say":
                continue
            who, other = e["who"], e.get("listener")
            if any(m["kind"] == "move" and m["t0"] < e["t1"] and m["t1"] > t0 for m in events):
                continue  # someone is moving: stay wide
            n = count.get(who.name, 0)
            count[who.name] = n + 1
            tc = max(0.0, t0 - 0.2)
            if t0 < 1.8 and not self.shots[1:]:
                tc = max(tc, 1.8)
                if tc > e["t1"] - 0.6:
                    continue
            if other is None:
                (self._single(who, tc, "medium", 0.62, 45, 20) if n % 2 == 0 else
                 self._single(who, tc, "close_up", 0.42, 60, 25))
            elif n == 0 and len(count) == 1:
                self._two_shot(who, other, tc)
            elif n % 3 == 2:
                self._single(who, tc, "close_up", 0.42, 60, 25, toward=other)
            else:
                self._over_shoulder(other, who, tc)
            last_kind = self.shots[-1].kind
        # drop shots that would last less than a second
        cleaned = []
        for i, s in enumerate(self.shots):
            nxt = self.shots[i + 1].at if i + 1 < len(self.shots) else sc.length
            if nxt - s.at < 1.0 and i + 1 < len(self.shots):
                continue
            if cleaned and cleaned[-1].label == s.label:
                continue
            cleaned.append(s)
        self.shots = cleaned

    # ------------------------------------------------------------------ keys
    def build(self):
        if not self.manual and not self.shots:
            self.auto()
        if not self.shots:
            self._wide(0.0)
        self.shots.sort(key=lambda s: s.at)
        if self.shots[0].at > 0:
            first = self.shots[0]
            self.shots.insert(0, Shot(first.kind, 0.0, first.subjects, first.pos, first.aim, first.lens,
                                      first.fstop, first.label))
        cd = self.cam.data
        for s in self.shots:
            key(self.cam, "location", s.at, tuple(s.pos), "cut")
            key(self.aim, "location", s.at, tuple(s.aim), "cut")
            key(cd, "lens", s.at, s.lens, "cut")
            key(cd.dof, "aperture_fstop", s.at, s.fstop, "cut")
            key(cd.dof, "focus_distance", s.at, (s.pos - s.aim).length, "cut")

    def describe(self):
        return [(s.at, s.label) for s in self.shots]
