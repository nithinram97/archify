"""The camera, directed in film language.

A shot is a combination, not a fixed list:

    framing  establishing, wide, full, medium_wide, medium, medium_close, close_up, extreme_close_up,
             two_shot, over_shoulder, pov, insert (a thing), group
    angle    eye_level, high, low, birds_eye, worms_eye          (how high the camera is)
    side     auto, front, three_quarter, profile, back           (where round the subject it stands)
    dutch    degrees of tilt (unease)
    lens     millimetres (24 wide ... 85 long); chosen from the framing if not given
    move     static, push_in, pull_out, pan_left/right, tilt_up/down, truck_left/right, crane_up/down,
             orbit_left/right, follow, zoom_in/out, dolly_zoom, rack_focus; plus handheld = true

From a beat:

    [[beats]]
    do = "shot"
    shot = "close_up"
    of = "mia"
    angle = "low"
    move = "push_in"

or from Python: `s.cut.shot("close_up", of="mia", angle="low", move="push_in")`.

A shot lasts until the next shot (or for `duration` seconds, after which the automatic director takes
over again). Without any shots, the automatic director covers the scene: it establishes the place,
follows people who travel, cuts between speakers keeping to the 180-degree rule, and adds camera
moves and angles from the mood of the moment.

Framings (`ShotType`) and moves (`CameraMove`) are classes, so new ones are easy to add:

    class Vertigo(dr.CameraMove):
        def track(self, d, shot, t0, t1, amount=None, to=None):
            ...   # return [(time, CameraState), ...]
"""
import math
import random

import bpy
from mathutils import Euler, Matrix, Vector

from . import keys, plugins
from .keys import key, value_at
from .plugins import Param, Plugin

SENSOR = 36.0
UP = Vector((0, 0, 1))

# framing: (what fills the frame height, as a function of the subject, aim height, default lens, f-stop)
SIZE_ORDER = ("extreme_close_up", "close_up", "medium_close", "medium", "medium_wide", "full", "wide", "establishing")
ANGLES = {"eye_level": 4.0, "high": 28.0, "low": -14.0, "birds_eye": 80.0, "worms_eye": -32.0}
SIDES = {"front": 0.0, "three_quarter": 32.0, "profile": 90.0, "back": 180.0}


class CameraState:
    """Where the camera is at one moment: position, the point it looks at, lens, roll and focus point."""

    def __init__(self, pos, aim, lens=35.0, roll=0.0, focus=None, fstop=4.0):
        self.pos, self.aim, self.lens, self.roll = Vector(pos), Vector(aim), lens, roll
        self.focus = Vector(focus) if focus is not None else Vector(aim)
        self.fstop = fstop

    def copy(self, **kw):
        s = CameraState(self.pos, self.aim, self.lens, self.roll, self.focus, self.fstop)
        for k, v in kw.items():
            setattr(s, k, Vector(v) if k in ("pos", "aim", "focus") else v)
        return s

    def right(self):
        """Screen right, as a world direction."""
        v = (self.aim - self.pos)
        r = v.cross(UP)
        return r.normalized() if r.length > 1e-6 else Vector((1, 0, 0))


class Shot:
    def __init__(self, kind, at, subjects, pos, aim, lens, fstop, label, roll=0.0, focus=None):
        self.kind, self.at, self.subjects, self.label = kind, at, subjects, label
        self.state = CameraState(pos, aim, lens, roll, focus, fstop)
        self.moves = []          # [(CameraMove instance, {params})]
        self.duration = None     # seconds, or None: until the next shot
        self.manual = False

    # older names
    @property
    def pos(self):
        return self.state.pos

    @property
    def aim(self):
        return self.state.aim

    @property
    def lens(self):
        return self.state.lens

    def clone(self, at):
        s = Shot(self.kind, at, self.subjects, self.state.pos, self.state.aim, self.state.lens, self.state.fstop,
                 self.label, self.state.roll, self.state.focus)
        s.moves = list(self.moves)
        return s


class Director:
    def __init__(self, scene):
        self.scene = scene
        cam_data = bpy.data.cameras.new("camera")
        cam_data.sensor_width = SENSOR
        cam_data.clip_start = 0.05
        cam_data.clip_end = 300
        cam_data.dof.use_dof = True
        coll = bpy.context.scene.collection
        # rig (position, looks at the aim) -> camera (roll)
        self.rig = bpy.data.objects.new("camera.rig", None)
        coll.objects.link(self.rig)
        self.aim = bpy.data.objects.new("camera.aim", None)
        coll.objects.link(self.aim)
        c = self.rig.constraints.new("TRACK_TO")
        c.target = self.aim
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        self.cam = bpy.data.objects.new("camera", cam_data)
        coll.objects.link(self.cam)
        self.cam.parent = self.rig
        bpy.context.scene.camera = self.cam
        self.shots = []          # shots asked for (by beats or Python)
        self.final = []          # what gets keyed (after automatic coverage is merged in)
        self.manual = False      # True: no automatic coverage at all (stills, cast photos)
        self.impulses = []       # (time, strength) of blows the camera feels (see impact)

    # ------------------------------------------------------------------ geometry helpers
    def _fov(self, lens):
        h = 2 * math.atan(SENSOR / 2 / lens)
        aspect = self.scene.size[1] / self.scene.size[0]
        v = 2 * math.atan(math.tan(h / 2) * aspect)
        return h, v

    @property
    def aspect(self):
        return self.scene.size[0] / self.scene.size[1]

    def _dist_for_height(self, height, lens):
        _, v = self._fov(lens)
        return height / 2 / math.tan(v / 2)

    def _dist_for_width(self, width, lens):
        h, _ = self._fov(lens)
        return width / 2 / math.tan(h / 2)

    distance_for_height = _dist_for_height
    distance_for_width = _dist_for_width

    def _char(self, c):
        return self.scene.character(c)

    def character(self, who):
        c = self._char(who)
        if c is None:
            raise ValueError(f"no character called {who!r} in this scene")
        return c

    def point(self, what, t, z=None):
        """A character's face, a prop's middle, or a mark (at `z`, default 0.6 m) as a 3D point."""
        c = self._char(what) if isinstance(what, str) or not isinstance(what, (tuple, list, Vector)) else None
        if c is not None:
            return c.head_point(t)
        st = self.scene.set
        if st is not None and isinstance(what, str) and what in getattr(st, "focus", {}):
            return st.focus[what].copy()
        p = self.scene._resolve(what, t)
        return Vector((p.x, p.y, 0.6 if z is None else z))

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

    line_side = _side

    def _keep_inside(self, pos):
        """Keep the camera above ground and, in rooms, on the open side and out of the walls."""
        p = Vector(pos)
        p.z = max(0.06, p.z)
        st = self.scene.set
        if st is None or st.outdoor:
            return p
        W, D = st.width / 2 - 0.15, st.depth / 2 - 0.15
        p.x = max(-W, min(W, p.x))
        p.y = min(D, p.y)
        if getattr(st, "ceiling_h", None):
            p.z = min(p.z, st.ceiling_h - 0.12)
        return p

    # ------------------------------------------------------------------ seeing past things
    def _actor_roots(self):
        return {c.root for c in self.scene.actors.values()}

    @staticmethod
    def _top(obj):
        while obj.parent is not None:
            obj = obj.parent
        return obj

    def clear_view(self, a, b, subjects=None):
        """True if nothing is between points a and b but characters (furniture and walls block). With
        `subjects`, only those characters can be seen past: anyone else standing in the way blocks too."""
        d = Vector(b) - Vector(a)
        L = d.length
        if L < 0.15:
            return True
        dirn = d / L
        roots = self._actor_roots() if subjects is None else {self.character(c).root for c in subjects}
        dg = bpy.context.evaluated_depsgraph_get()
        origin, remaining = Vector(a) + dirn * 0.05, L - 0.1
        for _ in range(12):
            hit, loc, _n, _i, obj, _m = self.scene.bscene.ray_cast(dg, origin, dirn, distance=remaining)
            if not hit:
                return True
            if self._top(obj) not in roots and not obj.name.startswith(("camera", "floor", "ground")) \
                    and not obj.get("dr_fx"):
                return False
            step = (loc - origin).length + 0.01
            origin, remaining = loc + dirn * 0.01, remaining - step
            if remaining <= 0:
                return True
        return True

    def unblock(self, pos, aim, kind="", subjects=None):
        """If something hides the subject from `pos`, find a nearby position that sees it: higher first,
        then a little round to either side (less for two-person shots, to keep the 180-degree rule).
        With `subjects`, other people in the way (a crowd round a fight) count as being in the way."""
        pos, aim = Vector(pos), Vector(aim)
        if self.clear_view(aim, pos, subjects):
            return pos
        off = pos - aim
        dist = off.length
        flat = Vector((off.x, off.y, 0))
        el = math.atan2(off.z, flat.length) if flat.length > 1e-6 else math.pi / 2
        yaws = (0, 25, -25) if kind in ("two_shot", "over_shoulder", "group") else (0, 25, -25, 50, -50, 80, -80)
        # an angle asked for (a worm's-eye shot, say) is kept: look round the side or come in closer instead
        rises = (0,) if getattr(self, "_angle_locked", False) else (0, 12, 25, 40)
        for yaw in yaws:
            for rise in rises:
                if yaw == 0 and rise == 0:
                    continue
                e = min(math.radians(85), el + math.radians(rise))
                f = Matrix.Rotation(math.radians(yaw), 3, UP) @ (flat.normalized() if flat.length > 1e-6 else Vector((0, -1, 0)))
                cand = aim + Vector((f.x * math.cos(e), f.y * math.cos(e), math.sin(e))) * dist
                cand = self._keep_inside(cand)
                if self.clear_view(aim, cand, subjects):
                    return cand
        if subjects is not None:          # no clear view past the people: come in closer, then settle for the walls
            for k in (0.8, 0.65, 0.5):
                cand = self._keep_inside(aim + (pos - aim) * k)
                if self.clear_view(aim, cand, subjects):
                    return cand
            return self.unblock(pos, aim, kind)
        # nothing clear nearby: come in front of whatever is in the way
        dg = bpy.context.evaluated_depsgraph_get()
        dirn = (pos - aim).normalized()
        origin, left = aim + dirn * 0.05, dist
        for _ in range(12):
            hit, loc, _n, _i, obj, _m = self.scene.bscene.ray_cast(dg, origin, dirn, distance=left)
            if not hit:
                return pos
            if not obj.get("dr_fx"):
                break
            left -= (loc - origin).length + 0.01
            origin = loc + dirn * 0.01
        else:
            return pos
        if (loc - aim).length < 0.3:   # the aim point itself is inside something: leave it
            return pos
        return loc - dirn * 0.12

    # ------------------------------------------------------------------ people in the way, over a whole shot
    EXEMPT = ("over_shoulder", "group", "wide", "establishing", "custom", "pov", "cast", "insert")

    def _people_in_way(self, pos, aim, subjects, t):
        """Whether someone other than the subjects stands between the camera and its aim at time t, or
        the camera is inside them. People are taken as upright cylinders (it's fast: no scene update)."""
        for c in self.scene.actors.values():
            if c in subjects or not c.visible(t):
                continue
            p = c.position(t)
            H, r = c.height(), 0.13 * c.height() + 0.03      # shoulder-wide
            z0 = value_at(c.root, "location", t)[2]
            d = Vector(aim) - Vector(pos)
            flat = Vector((d.x, d.y))
            q = Vector((pos.x - p.x, pos.y - p.y))
            if q.length < r + 0.15 and z0 - 0.1 < pos.z < z0 + H + 0.1:
                return True                                        # inside them
            if flat.length < 1e-6:
                continue
            u = max(0.0, min(1.0, -q.dot(flat) / flat.length_squared))
            if (q + flat * u).length < r and z0 < pos.z + d.z * u < z0 + H and u < 0.97:
                return True                                        # between the camera and the subject
        return False

    CLOSE = ("extreme_close_up", "close_up", "medium_close")
    HEADROOM = 0.84           # the top of a head stays below this much of the half-height above centre (8% margin)
    FACE_ANGLE = 70.0         # degrees: in close shots the camera stays this near where the face points

    def _face_dir(self, c, t):
        """Where the face points at `t` (the body's heading turned by the neck), as a flat vector."""
        h = c.heading(t)
        if getattr(c, "neck", None) is not None:
            h += value_at(c.neck, "rotation_euler", t)[2]
        return Vector((math.sin(h), -math.cos(h)))

    def _keep_framed(self, s, t0, t1):
        """Over the whole of shot s (not only its first moment): close shots stay round the side the face
        turns to, and nobody's head goes out of the top of the frame (tilt up a little, else pull back)."""
        if s.kind in self.EXEMPT or not s.subjects or s.manual:
            return
        subjects = [c for c in (self.character(k) for k in s.subjects) if c is not None]
        if not subjects:
            return
        times = [t0 + (t1 - t0) * k / 5 for k in range(6)] if t1 > t0 else [t0]
        st = s.state
        if s.kind in self.CLOSE and len(subjects) == 1:
            c = subjects[0]
            later = [tt for tt in times if tt >= t0 + 0.35 * (t1 - t0)] or times      # after any head turn
            face = sum((self._face_dir(c, tt) for tt in later), Vector((0, 0)))
            head = c.head_point(later[len(later) // 2])
            to_cam = Vector((st.pos.x - head.x, st.pos.y - head.y))
            if face.length > 1e-3 and to_cam.length > 1e-3:
                face.normalize()
                ang = math.degrees(face.angle_signed(to_cam.normalized()))
                if abs(ang) > self.FACE_ANGLE:
                    turn = math.radians(-math.copysign(abs(ang) - self.FACE_ANGLE + 10, ang))
                    off = st.pos - st.aim
                    rot = Matrix.Rotation(turn, 3, UP)
                    s.state = st = st.copy(pos=st.aim + rot @ off)
        _, v = self._fov(st.lens)
        top = math.tan(v / 2) * self.HEADROOM

        def worst(pos, aim):
            fwd = (aim - pos).normalized()
            right = fwd.cross(UP).normalized()
            up = right.cross(fwd)
            out = -1e9
            for tt in times:
                for c in subjects:
                    p = c.head_point(tt) + Vector((0, 0, 1.6 * c.head_r)) - pos
                    depth = p.dot(fwd)
                    if depth > 0.1:
                        out = max(out, p.dot(up) / depth)
            return out
        if worst(st.pos, st.aim) <= top:
            return
        dist = (st.pos - st.aim).length
        for lift, back in ((0.04, 1.0), (0.08, 1.0), (0.08, 1.12), (0.1, 1.25), (0.12, 1.4), (0.12, 1.6)):
            aim = st.aim + Vector((0, 0, lift * dist))
            pos = aim + (st.pos - st.aim) * back
            if worst(pos, aim) <= top:
                s.state = st.copy(pos=self._keep_inside(pos), aim=aim)
                return

    def _keep_clear_of_people(self, s, t0, t1):
        """Over the whole of shot s, nobody but its subjects should block it; if someone does (a crowd round
        a fight, people walking through), move the camera round, up or in until nobody does."""
        if s.kind in self.EXEMPT or not s.subjects or len(self.scene.actors) <= len(s.subjects):
            return
        subjects = [self.character(c) for c in s.subjects]
        times = [t0 + (t1 - t0) * k / 5 for k in range(6)] if t1 > t0 else [t0]
        st = s.state
        if (st.pos - st.aim).length < 1.2:          # close shots: someone that close is in the shot, not in the way
            return

        def clear(pos):
            return not any(self._people_in_way(pos, st.aim, subjects, tt) for tt in times)
        if clear(st.pos):
            return
        off = st.pos - st.aim
        dist, flat = off.length, Vector((off.x, off.y, 0))
        el = math.atan2(off.z, flat.length) if flat.length > 1e-6 else math.pi / 2
        f0 = flat.normalized() if flat.length > 1e-6 else Vector((0, -1, 0))
        for k in (1.0, 0.8, 0.65, 0.5):
            if dist * k < 1.0:
                break
            for yaw in (0, 20, -20, 40, -40, 65, -65, 90, -90):
                for rise in (0, 15, 30, 45):
                    if k == 1.0 and yaw == 0 and rise == 0:
                        continue
                    e = min(math.radians(80), el + math.radians(rise))
                    f = Matrix.Rotation(math.radians(yaw), 3, UP) @ f0
                    cand = self._keep_inside(st.aim + Vector((f.x * math.cos(e), f.y * math.cos(e), math.sin(e))) * dist * k)
                    if clear(cand) and self.clear_view(st.aim, cand):
                        s.state = st.copy(pos=cand)
                        return

    def in_front(self, pos, aim, margin=0.3):
        """`pos`, or if a wall (not a character) is between it and `aim`, just in front of the wall."""
        pos, aim = Vector(pos), Vector(aim)
        if self.clear_view(aim, pos):
            return pos
        roots = self._actor_roots()
        dg = bpy.context.evaluated_depsgraph_get()
        dirn = (pos - aim).normalized()
        origin, left = aim + dirn * 0.05, (pos - aim).length
        for _ in range(12):
            hit, loc, _n, _i, obj, _m = self.scene.bscene.ray_cast(dg, origin, dirn, distance=left)
            if not hit:
                return pos
            if self._top(obj) not in roots and not obj.name.startswith(("camera", "floor", "ground")) \
                    and not obj.get("dr_fx"):
                return aim + dirn * max(0.4, (loc - aim).length - margin)
            left -= (loc - origin).length + 0.01
            origin = loc + dirn * 0.01
        return pos

    def _add(self, kind, at, subjects, pos, aim, lens, fstop, label, roll=0.0, focus=None):
        at = self.scene._now() if at is None else at
        pos = self._keep_inside(pos)
        if kind not in ("custom", "pov", "cast"):
            # a shot of somebody shouldn't be of the back of somebody else (over-the-shoulder shots mean to be)
            own = subjects if kind not in ("over_shoulder", "group", "wide", "establishing") and subjects else None
            if own and len(self.scene.actors) > len(own):
                self.scene.bscene.frame_set(keys.CLOCK.frame(at))     # where everyone is at that moment
            pos = self.unblock(pos, aim, kind, own)
        s = Shot(kind, at, subjects, self._keep_inside(pos), Vector(aim), lens, fstop, label, roll, focus)
        self.shots.append(s)
        return s

    def add(self, kind, t, subjects, pos, aim, lens=35, fstop=4.0, label=None, roll=0.0, focus=None):
        """Record a shot starting at t: camera at `pos` looking at `aim`. Returns the Shot."""
        return self._add(kind, t, subjects, Vector(pos), Vector(aim), lens, fstop, label or kind, roll, focus)

    # ------------------------------------------------------------------ the shot grammar
    def shot(self, name, of=None, other=None, at=None, angle=None, side=None, dutch=None, lens=None,
             move=None, amount=None, to=None, handheld=False, duration=None):
        """Cut to a shot: a framing (see dr.registry("shot")) with optional angle, side, dutch tilt, lens and move."""
        st = plugins.get("shot", name)
        t = self.scene._now() if at is None else at
        if st.subjects >= 1 and of is None:
            raise ValueError(f"the {st.label} shot needs a subject (of = ...)")
        if st.subjects >= 2 and other is None:
            raise ValueError(f"the {st.label} shot needs a second subject (other = ...)")
        before = len(self.shots)
        self._angle_locked = angle not in (None, "eye_level")
        try:
            st().frame(self, t, of=of, other=other, angle=angle or "eye_level", side=side or "auto",
                       lens=lens, dutch=float(dutch or 0))
        finally:
            self._angle_locked = False
        if len(self.shots) == before:
            raise ValueError(f"the {st.label} shot didn't produce a camera position")
        shot = self.shots[-1]
        shot.manual = True
        shot.duration = float(duration) if duration else None
        if dutch:
            shot.state.roll = float(dutch)
            shot.label += f" dutch {float(dutch):g}°"
        if move and move != "static":
            shot.moves.append((plugins.get("move", move)(), {"amount": amount, "to": to}))
            shot.label += f" · {move.replace('_', ' ')}"
        if handheld:
            shot.moves.append((plugins.get("move", "handheld")(), {"amount": amount if move in (None, "static") else None}))
            shot.label += " · handheld"
        return self

    # Python shortcuts
    def wide(self, at=None, **kw):
        return self.shot("wide", at=at, **kw)

    def establishing(self, at=None, **kw):
        return self.shot("establishing", at=at, **kw)

    def full(self, who, at=None, **kw):
        return self.shot("full", of=who, at=at, **kw)

    def medium(self, who, at=None, **kw):
        return self.shot("medium", of=who, at=at, **kw)

    def close_up(self, who, at=None, **kw):
        return self.shot("close_up", of=who, at=at, **kw)

    def two_shot(self, a, b, at=None, **kw):
        return self.shot("two_shot", of=a, other=b, at=at, **kw)

    def over_shoulder(self, past, on, at=None, **kw):
        return self.shot("over_shoulder", of=past, other=on, at=at, **kw)

    def pov(self, who, looking_at=None, at=None, **kw):
        return self.shot("pov", of=who, other=looking_at, at=at, **kw)

    def from_point(self, where, look_at, at=None, lens=35, height=1.2):
        """Escape hatch: put the camera at a mark and aim it at a character or mark."""
        self.manual = True
        t = self.scene._now() if at is None else at
        p = self.scene._resolve(where, t)
        aim = self.point(look_at, t)
        s = self._add("custom", t, [], (p.x, p.y, height), aim, lens, 5.6, f"from {where}")
        s.manual = True
        return self

    # ------------------------------------------------------------------ framing maths (used by ShotTypes)
    def frame_single(self, c, t, size, angle="eye_level", side="auto", lens=None, toward=None, dutch=0.0, label=None):
        """Frame one character at a shot size, from an angle and side; adds lead room. Returns the Shot."""
        c = self.character(c)
        head = c.head_point(t)
        loc, _, hz = c.where_at(t)
        feet_z = loc.z + hz - getattr(c, "hip_z", 0.0)     # off the ground only as far as the hips are raised
        H, hr, L = c.height(), c.head_r, c.length()
        table = {
            "extreme_close_up": (1.5 * hr, head.z + 0.12 * hr, 85, 2.0),
            "close_up": (3.2 * hr, head.z - 0.2 * hr, 60, 2.8),
            "medium_close": (max(5.5 * hr, 0.45 * H), head.z + hr - 0.42 * max(5.5 * hr, 0.45 * H), 50, 2.8),
            "medium": (max(7.5 * hr, 0.62 * H), head.z + hr - 0.42 * max(7.5 * hr, 0.62 * H), 40, 4.0),
            "medium_wide": (0.9 * H, feet_z + H - 0.45 * 0.9 * H, 35, 4.0),
            "full": (1.25 * H, feet_z + 0.5 * H, 32, 5.6),
            "wide": (2.8 * H, feet_z + 0.5 * H, 28, 8.0),
        }
        if size not in table:
            raise ValueError(f"unknown size {size!r}")
        fh, aim_z, auto_lens, fstop = table[size]
        if size in ("full", "wide", "medium_wide"):
            fh = max(fh, (L * (1.35 if size != "wide" else 2.6)) / self.aspect)   # long bodies fit across
        lens = float(lens) if lens else auto_lens
        # direction from the subject to the camera (horizontal)
        fwd = c.forward(t)
        if toward is not None:   # three-quarter on the line side, as they face their partner
            o = self.character(toward)
            to_o = o.position(t) - c.position(t)
            to_o = to_o.normalized() if to_o.length > 1e-3 else fwd
            line = self._side(c, o, t)
            base = to_o
            sign = 1 if (Vector((-base.y, base.x))).dot(line) >= 0 else -1
        else:
            base, sign = fwd, (1 if Vector((-fwd.y, fwd.x)).y <= 0 else -1)
        yaw = SIDES.get(side, SIDES["three_quarter"] if side == "auto" else 0.0) * sign
        a = math.radians(yaw)
        dh = Vector((base.x * math.cos(a) - base.y * math.sin(a), base.x * math.sin(a) + base.y * math.cos(a)))
        if side == "auto" and toward is None and dh.y > 0.35 and self.scene.set is not None and \
                not self.scene.set.outdoor and size in ("full", "wide", "medium_wide"):
            dh.y = -abs(dh.y)   # in a room, wide shots stay on the open side (close ones need little room
            dh.normalize()      # in front of a face, and showing the back of a head is no close-up)
        el = math.radians(ANGLES.get(angle, 4.0))
        dist = self._dist_for_height(fh, lens)
        aim = Vector((head.x, head.y, aim_z)) if size in ("extreme_close_up", "close_up", "medium_close", "medium") \
            else Vector((loc.x, loc.y, aim_z))
        if angle in ("low", "worms_eye") and size in ("extreme_close_up", "close_up"):
            aim.z = head.z
        dirv = Vector((dh.x * math.cos(el), dh.y * math.cos(el), math.sin(el)))
        pos = aim + dirv * dist
        if pos.z < 0.06:   # a low camera can't go under the floor: slide it up and look up more
            pos.z = 0.06
        # lead room: the subject sits off-centre, with space in the direction they face
        st = CameraState(pos, aim)
        gaze = Vector((fwd.x, fwd.y, 0))
        s = gaze.dot(st.right())
        aim = aim + st.right() * s * fh * self.aspect * 0.12
        name = label or f"{size}({c.name})" + ("" if angle == "eye_level" else f" {angle.replace('_', ' ')}")
        return self._add(size, t, [c], pos, aim, lens, fstop, name, focus=head)

    def frame_group(self, people, t, kind="two_shot", angle="eye_level", lens=None, label=None, size="medium"):
        """Frame several characters from the side of the line (the first two set the line)."""
        people = [self.character(p) for p in people]
        heads = [p.head_point(t) for p in people]
        H = max(p.height() for p in people)
        xs = [h.x for h in heads]
        ys = [h.y for h in heads]
        mid = Vector((sum(xs) / len(xs), sum(ys) / len(ys), 0))
        if len(people) >= 2:
            side = self._side(people[0], people[1], t)
        else:
            side = Vector((0, -1))
        span = max((a - b).length for a in heads for b in heads) if len(heads) > 1 else 0
        lens = float(lens) if lens else (35 if size != "full" else 30)
        fh = {"full": 1.3 * H, "medium_wide": 0.95 * H}.get(size, max(0.7 * H, 6 * max(p.head_r for p in people)))
        width = span + 1.2 * max(H, max(p.head_r for p in people) * 4)
        dist = max(self._dist_for_width(width, lens), self._dist_for_height(fh, lens))
        top = max(h.z + p.head_r for h, p in zip(heads, people))
        aim = Vector((mid.x, mid.y, top - 0.42 * fh if size != "full" else top - 0.5 * fh))
        el = math.radians(ANGLES.get(angle, 4.0))
        pos = aim + Vector((side.x * math.cos(el), side.y * math.cos(el), math.sin(el))) * dist
        names = ", ".join(p.name for p in people)
        return self._add(kind, t, people, pos, aim, lens, 4.0, label or f"{kind}({names})", focus=aim)

    def frame_over_shoulder(self, past, on, t, angle="eye_level", lens=None):
        p, o = self.character(past), self.character(on)
        hp, ho = p.head_point(t), o.head_point(t)
        d = Vector((hp.x - ho.x, hp.y - ho.y))
        if d.length < 1e-3:
            return self.frame_single(o, t, "close_up", angle)
        u = d.normalized()
        side = self._side(p, o, t)
        S = p.head_r / 0.19
        back = 1.25 * S
        drop = max(0.0, hp.z - ho.z)
        off = 0.55 * S + 1.3 * drop
        z = max(hp.z, ho.z) * 0.6 + min(hp.z, ho.z) * 0.4 + 0.08 * S + 0.6 * drop + {"high": 0.3, "low": -0.15}.get(angle, 0) * S
        pos = Vector((hp.x + u.x * back + side.x * off, hp.y + u.y * back + side.y * off, z))
        aim = ho + Vector((0, 0, -0.06 * o.head_r / 0.19)) + Vector((-side.x, -side.y, 0)) * 0.1 * o.head_r / 0.19
        return self._add("over_shoulder", t, [o, p], pos, aim, float(lens) if lens else 40, 4.0,
                         f"over_shoulder({p.name} -> {o.name})", focus=ho)

    def frame_pov(self, who, t, looking_at=None, lens=None):
        """Through a character's eyes."""
        c = self.character(who)
        head = c.head_point(t)
        fwd = c.forward(t)
        pos = head + Vector((fwd.x, fwd.y, 0)) * c.head_r * 1.3
        if looking_at is not None:
            aim = self.point(looking_at, t)
        else:
            aim = pos + Vector((fwd.x, fwd.y, -0.08)) * 3
        return self._add("pov", t, [c], pos, aim, float(lens) if lens else 30, 5.6, f"pov({c.name})", focus=aim)

    def frame_insert(self, what, t, angle="high", lens=None):
        """A detail: a prop, a thing on a table, or a spot."""
        p = self.point(what, t, z=0.55)
        el = math.radians(ANGLES.get(angle, 28) if angle != "eye_level" else 20)
        lens = float(lens) if lens else 60
        dist = self._dist_for_height(0.45, lens)
        dh = Vector((0.35, -1, 0)).normalized()
        pos = p + Vector((dh.x * math.cos(el), dh.y * math.cos(el), math.sin(el))) * dist
        return self._add("insert", t, [], pos, p, lens, 2.8, f"insert({what})", focus=p)

    def frame_wide(self, t, angle="eye_level", lens=None, establishing=False):
        st = self.scene.set
        lens = float(lens) if lens else (24 if establishing else 30)
        chars = [c for c in self.scene.actors.values() if c.visible(t)]
        pts = [c.position(t) for c in chars]
        for e in self.scene.events:
            if e["kind"] == "move" and e["t0"] <= t + 0.5 and e["t1"] >= t:
                pts.append(e["who"].position(e["t1"]))
        if establishing and st is not None:
            pts += [Vector((-st.width / 2 * 0.8, 0)), Vector((st.width / 2 * 0.8, 0))]
        if not pts:
            pts = [Vector((0, 0))]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        tall = max([c.height() for c in chars] + [1.0])
        width = max(4.2 * tall, max(xs) - min(xs) + 3.0 * tall)
        if st is not None and not st.outdoor:
            width = min(width, st.width * (1.0 if establishing else 0.95))
            cx = max(-st.width / 2 + width / 2, min(st.width / 2 - width / 2, cx))
        d = self._dist_for_width(width, lens) + (max(ys) - min(ys)) / 2
        el = math.radians(ANGLES.get(angle, 4.0)) if angle != "eye_level" else (0.22 if establishing else 0.12)
        aim = Vector((cx, cy + 0.2, 0.45 * tall))
        pos = aim + Vector((0, -math.cos(el), math.sin(el))) * d
        if not establishing and angle == "eye_level":
            pos.z = 0.85 * tall + 0.2 * d * tall / max(tall, 1)
        kind = "establishing" if establishing else "wide"
        return self._add(kind, t, chars, pos, aim, lens, 8.0, kind + ("" if angle == "eye_level" else f" {angle}"))

    # keep older internal names working
    def _wide(self, at=None, height=None):
        return self.frame_wide(self.scene._now() if at is None else at)

    def _single(self, who, at, kind, frame_h=None, lens=None, angle=None, toward=None):
        return self.frame_single(who, at, kind, toward=toward)

    def _two_shot(self, a, b, at=None):
        return self.frame_group([a, b], at)

    def _over_shoulder(self, past, on, at=None):
        return self.frame_over_shoulder(past, on, at)

    # ------------------------------------------------------------------ automatic coverage
    def auto(self):
        """Cover the scene like a TV director: establish the place, follow people who travel, cut between
        speakers on one side of the line, and let the mood choose angles and camera moves."""
        sc = self.scene
        saved, self.shots = self.shots, []
        events = sorted(sc.events, key=lambda e: e["t0"])
        first_move = next((e for e in events if e["kind"] == "move" and e["t0"] < 1.0), None)
        est = self.frame_wide(0.0, establishing=sc.set is not None and first_move is None)
        est.moves.append((plugins.get("move", "push_in")(), {"amount": 0.12}))
        count = {}
        last = "wide"
        for e in events:
            t0 = e["t0"]
            if e["kind"] == "move" and t0 > 0.5:
                dur = e["t1"] - t0
                movers = [m for m in events if m["kind"] == "move" and m["t0"] < e["t1"] and m["t1"] > t0]
                # cut on action: a moment into the movement, so the motion carries across the cut
                tc = t0 + min(CUT_ON_ACTION, 0.3 * dur)
                if dur > 2.5 and len({m["who"].name for m in movers}) == 1:
                    s = self.frame_single(e["who"], tc, "medium_wide", side="auto")
                    s.moves.append((plugins.get("move", "follow")(), {}))
                    s.label += " · follow"
                    last = "follow"
                elif last != "wide":
                    self.frame_wide(tc)
                    last = "wide"
                continue
            if e["kind"] == "gesture" and e.get("gesture") in BIG_GESTURES and t0 > 0.5:
                talking = any(x["kind"] == "say" and x["t0"] < e["t1"] and x["t1"] > t0 for x in events)
                if not talking:
                    self.frame_single(e["who"], t0 + min(CUT_ON_ACTION, 0.25 * (e["t1"] - t0)), "full")
                    last = "full"
                continue
            if e["kind"] != "say":
                continue
            who, other = e["who"], e.get("listener")
            if any(m["kind"] == "move" and m["t0"] < e["t1"] and m["t1"] > t0 for m in events):
                continue  # someone is moving: the follow or wide shot holds
            n = count.get(who.name, 0)
            count[who.name] = n + 1
            tc = max(0.0, t0 - 0.2)
            if t0 < 1.8 and len(self.shots) < 2:
                tc = max(tc, 1.8)
                if tc > e["t1"] - 0.6:
                    continue
            mood = e.get("mood") or getattr(who, "mood", "neutral")
            angle = MOOD_ANGLE.get(mood, "eye_level")
            if other is None:
                s = self.frame_single(who, tc, "medium" if n % 2 == 0 else "close_up", angle=angle)
            elif n == 0 and len(count) == 1:
                s = self.frame_group([who, other], tc)
            elif n % 3 == 2 or mood in STRONG_MOODS:
                s = self.frame_single(who, tc, "close_up", angle=angle, toward=other)
            else:
                s = self.frame_over_shoulder(other, who, tc)
            if mood in STRONG_MOODS or (e["t1"] - t0) > 3.5:
                s.moves.append((plugins.get("move", "push_in")(), {"amount": 0.18 if mood in STRONG_MOODS else 0.1}))
                s.label += " · push in"
            last = s.kind
        auto, self.shots = self.shots, saved
        cleaned = []
        for i, s in enumerate(auto):
            nxt = auto[i + 1].at if i + 1 < len(auto) else sc.length
            if nxt - s.at < 1.0 and i + 1 < len(auto):
                continue
            if cleaned and cleaned[-1].label == s.label:
                continue
            cleaned.append(s)
        return cleaned

    def _merge(self, auto):
        """Asked-for shots win from their start until the next asked-for shot (or their duration ends);
        automatic coverage fills the rest."""
        manual = sorted([s for s in self.shots], key=lambda s: s.at)
        if not manual:
            return auto
        spans = []
        for i, m in enumerate(manual):
            nxt = manual[i + 1].at if i + 1 < len(manual) else float("inf")
            end = min(nxt, m.at + m.duration) if m.duration else nxt
            spans.append((m.at, end))
        inside = lambda t: any(a <= t < b for a, b in spans)  # noqa: E731
        out = [s for s in auto if not inside(s.at)] + manual
        for (a, b), m in zip(spans, manual):
            if b != float("inf") and not any(x.at == b for x in manual):
                active = [s for s in auto if s.at <= b]
                if active:
                    out.append(active[-1].clone(b))
        if not any(s.at <= 0.0 for s in out) and auto:
            pass
        return sorted(out, key=lambda s: s.at)

    # ------------------------------------------------------------------ keys
    def build(self):
        L = self.scene.length
        if self.manual:
            shots = sorted(self.shots, key=lambda s: s.at)
        else:
            shots = self._merge(self.auto())
        if not shots:
            shots = [self.frame_wide(0.0)]
            self.shots.pop()
        if shots[0].at > 0:
            shots.insert(0, shots[0].clone(0.0))
        self.final = shots
        cd = self.cam.data
        spf = 1.0 / self.scene.fps
        for i, s in enumerate(shots):
            t0 = s.at
            t1 = (shots[i + 1].at if i + 1 < len(shots) else L) - spf
            self._keep_framed(s, t0, t1)
            self._keep_clear_of_people(s, t0, t1)
            track = [(t0, s.state)]
            ease = "smooth"
            for mv, params in s.moves:
                base = track
                track = mv.track(self, s, t0, max(t1, t0 + spf), base, **{k: v for k, v in params.items() if v is not None})
                ease = mv.ease
            for j, (t, st) in enumerate(track):
                e = "cut" if j == len(track) - 1 else ease
                pos = self._keep_inside(st.pos)
                if s.kind not in ("custom", "pov", "cast"):
                    pos = self.in_front(pos, st.aim)      # never inside a wall, wherever a move takes it
                key(self.rig, "location", t, tuple(pos), e)
                key(self.aim, "location", t, tuple(st.aim), e)
                key(cd, "lens", t, st.lens, e)
                # near enough that rain and dust right at the lens don't show, never so near it cuts into
                # a small subject in a tight close-up
                key(cd, "clip_start", t, max(0.02, min(0.35, 0.5 * (st.focus - pos).length)), e)
                key(self.cam, "rotation_euler", t, (0, 0, math.radians(st.roll)), e)
                key(cd.dof, "aperture_fstop", t, st.fstop, e)
                key(cd.dof, "focus_distance", t, max(0.1, (st.focus - pos).length), e)
        self._shake()

    def snap_to_frames(self):
        """Put the camera's keys back on whole frames (time effects can move them between frames), so a
        cut is always between two frames and the shutter never spans one."""
        from . import _compat
        for owner in (self.rig, self.aim, self.cam, self.cam.data):
            for fc in _compat.fcurves(owner):
                for kp in fc.keyframe_points:
                    x = round(kp.co.x)
                    if abs(x - kp.co.x) > 1e-4:
                        d = x - kp.co.x
                        kp.co.x = x
                        kp.handle_left.x += d
                        kp.handle_right.x += d
                fc.update()

    def impact(self, t, strength=0.5):
        """The camera feels a blow at `t` (strength 0-1): a jolt that dies away in a few frames."""
        self.impulses.append((float(t), max(0.0, min(1.5, float(strength)))))

    def _shake(self):
        if not self.impulses:
            return
        shaker = bpy.data.objects.new("camera.shaker", None)
        self.scene.bscene.collection.objects.link(shaker)
        self.aim.parent = shaker
        fps, decay, hz = self.scene.fps, 0.28, 13.0
        rng = random.Random(7)
        kicks = [(t0, s, Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.6, 1))).normalized(),
                  rng.uniform(0, 6.28)) for t0, s in sorted(self.impulses)]

        def offset(t):
            v = Vector()
            for t0, s, d, ph in kicks:
                if 0 <= t - t0 < decay:
                    u = t - t0
                    v += d * (0.06 * s * math.exp(-u * 11) * math.cos(2 * math.pi * hz * u + ph))
            return v
        frames = set()
        for t0, *_ in kicks:
            f0 = keys.CLOCK.frame(t0)
            frames.update(range(f0 - 1, f0 + int(decay * fps) + 2))
        for f in sorted(frames):
            shaker.location = offset(keys.CLOCK.seconds(f))
            shaker.keyframe_insert("location", frame=f)

    def describe(self):
        shots = self.final or sorted(self.shots, key=lambda s: s.at)
        return [(s.at, s.label) for s in shots]

    def top_down(self, height, ortho_scale):
        """Look straight down from above (for maps of a set)."""
        for o in bpy.data.objects:          # see into rooms with ceilings
            if o.get("dr_ceiling"):
                o.hide_render = True
        self.rig.constraints.clear()
        self.rig.location = (0, 0, height)
        self.rig.rotation_euler = (0, 0, 0)
        self.cam.data.type = "ORTHO"
        self.cam.data.ortho_scale = ortho_scale
        self.cam.data.dof.use_dof = False


CUT_ON_ACTION = 0.3   # seconds into a movement that the automatic director cuts (editing: cut on action)
BIG_GESTURES = {"cheer", "jump", "dance", "rear_up", "flap", "spin", "bow", "stomp", "roar", "wave"}
STRONG_MOODS = {"angry", "surprised", "scared", "excited"}
MOOD_ANGLE = {"angry": "low", "smug": "low", "scared": "high", "sad": "high", "worried": "high"}


# ---------------------------------------------------------------------- framings
class ShotType(Plugin):
    """A framing. `frame(d, t, of, other, angle, side, lens, dutch)` records a Shot with the director's
    frame_* helpers or `d.add(...)`."""
    kind = "shot"
    abstract = True
    subjects = 0   # how many subjects the framing needs (0, 1 or 2)

    @classmethod
    def describe_extra(cls):
        return {"subjects": cls.subjects}

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        raise NotImplementedError


class Establishing(ShotType):
    description = "The whole place, from a little above"

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_wide(t, angle=angle, lens=lens, establishing=True)


class Wide(ShotType):
    description = "Everyone and where they're going"

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_wide(t, angle=angle, lens=lens)


class _Single(ShotType):
    abstract = True
    subjects = 1
    size = "medium"

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_single(of, t, self.size, angle=angle, side=side, lens=lens,
                              toward=other if side == "auto" and other else None)


class Full(_Single):
    description = "Head to toe"
    size = "full"


class MediumWide(_Single):
    label = "Medium wide"
    description = "From the knees up"
    size = "medium_wide"


class Medium(_Single):
    description = "From the waist up"
    size = "medium"


class MediumClose(_Single):
    label = "Medium close-up"
    description = "Head and shoulders"
    size = "medium_close"


class CloseUp(_Single):
    label = "Close-up"
    description = "The face fills the frame"
    size = "close_up"


class ExtremeCloseUp(_Single):
    label = "Extreme close-up"
    description = "Just the eyes"
    size = "extreme_close_up"


class TwoShot(ShotType):
    label = "Two-shot"
    description = "Two characters together, from their side of the line"
    subjects = 2

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_group([of, other], t, angle=angle, lens=lens)


class FullTwoShot(ShotType):
    label = "Two-shot (full)"
    description = "Two characters head to toe, from their side of the line (fights, dances)"
    subjects = 2

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_group([of, other], t, kind="two_shot", angle=angle, lens=lens, size="full",
                             label=f"two_shot_full({d.character(of).name}, {d.character(other).name})")


class Group(ShotType):
    description = "Everyone in the scene who's visible"

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        people = [c for c in d.scene.actors.values() if c.visible(t)]
        if not people:
            return d.frame_wide(t, angle=angle, lens=lens)
        return d.frame_group(people, t, kind="group", angle=angle, lens=lens, size="full", label="group")


class OverShoulder(ShotType):
    label = "Over the shoulder"
    description = "Past one character's shoulder (of) onto the other's face (other)"
    subjects = 2

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_over_shoulder(of, other, t, angle=angle, lens=lens)


class Pov(ShotType):
    label = "Point of view"
    description = "Through a character's eyes (of), looking at someone or something (other)"
    subjects = 1

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_pov(of, t, looking_at=other, lens=lens)


class Insert(ShotType):
    description = "A detail: a thing, a prop or a spot (of)"
    subjects = 1

    def frame(self, d, t, of=None, other=None, angle="eye_level", side="auto", lens=None, dutch=0.0):
        return d.frame_insert(of, t, angle="high" if angle == "eye_level" else angle, lens=lens)


# ---------------------------------------------------------------------- camera moves
class CameraMove(Plugin):
    """How the camera moves during a shot. `track(d, shot, t0, t1, base)` gets the track so far
    (a list of (time, CameraState); usually just the start) and returns the new one."""
    kind = "move"
    abstract = True
    ease = "smooth"           # interpolation between the returned samples
    params = [Param("amount", "number", label="How much")]
    default_amount = 1.0

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        raise NotImplementedError


def _two(base, t1, fn):
    """A move from the start state to fn(start) at t1."""
    t0, s0 = base[0]
    return [(t0, s0), (t1, fn(s0))]


def _rot_about(p, centre, axis, ang):
    return centre + (Matrix.Rotation(ang, 3, axis) @ (p - centre))


class Static(CameraMove):
    description = "The camera doesn't move"

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        return base


class PushIn(CameraMove):
    label = "Push in"
    description = "Move slowly towards the subject (tension, realisation)"
    default_amount = 0.25

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = self.default_amount if amount is None else float(amount)
        return _two(base, t1, lambda s: s.copy(pos=s.pos.lerp(s.aim, a)))


class PullOut(CameraMove):
    label = "Pull out"
    description = "Move away from the subject (reveal, loneliness)"
    default_amount = 0.4

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = self.default_amount if amount is None else float(amount)
        return _two(base, t1, lambda s: s.copy(pos=s.aim + (s.pos - s.aim) * (1 + a)))


class _Pan(CameraMove):
    abstract = True
    direction = 1
    default_amount = 30.0   # degrees

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = math.radians((self.default_amount if amount is None else float(amount)) * self.direction)
        if to is not None:
            target = d.point(to, t1)
            return _two(base, t1, lambda s: s.copy(aim=target))
        return _two(base, t1, lambda s: s.copy(aim=_rot_about(s.aim, s.pos, UP, -a)))


class PanLeft(_Pan):
    label = "Pan left"
    description = "Turn the camera left (or to `to`)"
    direction = -1


class PanRight(_Pan):
    label = "Pan right"
    description = "Turn the camera right (or to `to`)"
    direction = 1


class _Tilt(CameraMove):
    abstract = True
    direction = 1
    default_amount = 15.0

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = math.radians((self.default_amount if amount is None else float(amount)) * self.direction)
        return _two(base, t1, lambda s: s.copy(aim=_rot_about(s.aim, s.pos, s.right(), a)))


class TiltUp(_Tilt):
    label = "Tilt up"
    description = "Tip the camera up (look up at something big)"


class TiltDown(_Tilt):
    label = "Tilt down"
    direction = -1


class _Truck(CameraMove):
    abstract = True
    direction = 1
    default_amount = 1.0   # metres

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = (self.default_amount if amount is None else float(amount)) * self.direction
        return _two(base, t1, lambda s: s.copy(pos=s.pos + s.right() * a, aim=s.aim + s.right() * a))


class TruckLeft(_Truck):
    label = "Truck left"
    description = "Slide sideways to the left"
    direction = -1


class TruckRight(_Truck):
    label = "Truck right"
    description = "Slide sideways to the right"


class _Crane(CameraMove):
    abstract = True
    direction = 1
    default_amount = 1.2

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = (self.default_amount if amount is None else float(amount)) * self.direction
        return _two(base, t1, lambda s: s.copy(pos=s.pos + UP * a, aim=s.aim + UP * a * 0.25))


class CraneUp(_Crane):
    label = "Crane up"
    description = "Rise up and look down (an ending, a reveal)"


class CraneDown(_Crane):
    label = "Crane down"
    direction = -1


class _Orbit(CameraMove):
    abstract = True
    direction = 1
    default_amount = 40.0
    ease = "linear"

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = math.radians((self.default_amount if amount is None else float(amount)) * self.direction)
        t_, s0 = base[0]
        n = max(2, int(abs(math.degrees(a)) / 8))
        out = []
        for i in range(n + 1):
            u = i / n
            u = u * u * (3 - 2 * u)
            out.append((t0 + (t1 - t0) * i / n, s0.copy(pos=_rot_about(s0.pos, s0.aim, UP, a * u))))
        return out


class OrbitLeft(_Orbit):
    label = "Orbit left"
    description = "Circle round the subject"
    direction = -1


class OrbitRight(_Orbit):
    label = "Orbit right"
    description = "Circle round the subject"


class Follow(CameraMove):
    description = "Keep the subject framed as they move"
    ease = "linear"

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        if not shot.subjects:
            return base
        c = shot.subjects[0]
        p0, _, h0 = c.where_at(t0)
        out = []
        t = t0
        step = 4.0 / d.scene.fps
        while True:
            p, _, h = c.where_at(t)
            off = p - p0 + Vector((0, 0, h - h0))
            # keep the start state's offset from the subject (base may already have moves in it)
            s = base[0][1]
            out.append((t, s.copy(pos=s.pos + off, aim=s.aim + off, focus=s.focus + off)))
            if t >= t1:
                break
            t = min(t1, t + step)
        return out


class _Zoom(CameraMove):
    abstract = True
    direction = 1
    default_amount = 1.6   # lens factor

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        f = self.default_amount if amount is None else float(amount)
        f = f if self.direction > 0 else 1 / f
        return _two(base, t1, lambda s: s.copy(lens=max(10.0, min(300.0, s.lens * f))))


class ZoomIn(_Zoom):
    label = "Zoom in"
    description = "Change the lens to get closer (flatter than a push in)"


class ZoomOut(_Zoom):
    label = "Zoom out"
    direction = -1


class DollyZoom(CameraMove):
    label = "Dolly zoom"
    description = "Move in while zooming out: the subject stays, the world stretches (shock)"
    default_amount = 0.5

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = self.default_amount if amount is None else float(amount)

        def end(s):
            d0 = (s.pos - s.aim).length
            p = s.pos.lerp(s.aim, a)
            d1 = max(0.2, (p - s.aim).length)
            return s.copy(pos=p, lens=max(10.0, s.lens * d1 / d0))
        return _two(base, t1, end)


class RackFocus(CameraMove):
    label = "Rack focus"
    description = "Shift focus from the subject to someone or something else (to)"
    params = [Param("to", "target", label="Focus on")]

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        if to is None:
            return base
        target = d.point(to, t0)
        mid = t0 + (t1 - t0) * 0.45
        t_, s0 = base[0]
        return [(t0, s0.copy(fstop=min(s0.fstop, 2.0))), (mid, s0.copy(fstop=min(s0.fstop, 2.0))),
                (mid + 0.6, s0.copy(focus=target, fstop=min(s0.fstop, 2.0))), (t1, s0.copy(focus=target, fstop=min(s0.fstop, 2.0)))]


class Handheld(CameraMove):
    description = "A gentle, human wobble (documentary, tension); add it to any move"
    ease = "smooth"

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        a = 1.0 if amount is None else float(amount)
        rng = random.Random(int(t0 * 1000))
        out = []
        step = 0.25

        def at(t):   # the base track's state at time t (piecewise linear)
            prev = base[0]
            for b in base:
                if b[0] > t:
                    u = (t - prev[0]) / max(1e-6, b[0] - prev[0])
                    s0, s1 = prev[1], b[1]
                    return s0.copy(pos=s0.pos.lerp(s1.pos, u), aim=s0.aim.lerp(s1.aim, u),
                                   lens=s0.lens + (s1.lens - s0.lens) * u, focus=s0.focus.lerp(s1.focus, u))
                prev = b
            return prev[1]
        t = t0
        while True:
            s = at(t)
            j = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.012 * a
            k = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.02 * a
            out.append((t, s.copy(pos=s.pos + j, aim=s.aim + k, roll=s.roll + rng.uniform(-0.6, 0.6) * a)))
            if t >= t1:
                break
            t = min(t1, t + step)
        return out
