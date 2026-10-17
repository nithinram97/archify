"""Acting: how a movement is done, not just what it is.

Every gesture and walk is shaped by the character's *effort*, the four qualities of Laban Movement
Analysis as used for animation by the EMOTE model (Chi, Costa, Zhao and Badler, SIGGRAPH 2000):

    weight  -1 light ... +1 strong      (how big and forceful)
    time    -1 sustained ... +1 sudden  (how quick)
    space   -1 indirect ... +1 direct   (how straight to the point)
    flow    -1 free ... +1 bound        (how loose: free flow overshoots and settles)

Moods carry an effort (angry is strong, sudden, direct, bound; sad is light, sustained, indirect),
and a beat can say *how* something is done (`how = "nervously"`), which overrides the mood. On top,
the classic principles of animation (Lasseter, SIGGRAPH 1987) are applied to every gesture:
anticipation (a small counter-move first), and follow-through (an overshoot and a settle at the
end), scaled by the film's `exaggeration` (film.toml; each style has its own default).

Manners are classes, so new ones are one line:

    dr.Manner.define("drunkenly", weight=-0.4, time=-0.5, space=-1.0, flow=-1.0)
"""
from . import keys
from .plugins import Param, Plugin


class Effort:
    def __init__(self, weight=0.0, time=0.0, space=0.0, flow=0.0):
        self.weight, self.time, self.space, self.flow = (max(-1.0, min(1.0, float(v)))
                                                          for v in (weight, time, space, flow))

    def __repr__(self):
        return f"Effort(weight={self.weight:+.1f}, time={self.time:+.1f}, space={self.space:+.1f}, flow={self.flow:+.1f})"

    # how the four qualities change a movement
    def tempo(self):
        """Duration multiplier: sudden is quicker, sustained slower."""
        return 1.0 - 0.28 * self.time

    def amplitude(self):
        return 1.0 + 0.25 * self.weight - 0.08 * max(0.0, self.flow)

    def anticipation(self):
        return 0.08 + 0.1 * max(0.0, self.time) + 0.06 * max(0.0, self.weight)

    def overshoot(self):
        return 0.04 + 0.12 * max(0.0, -self.flow) + 0.04 * max(0.0, self.time)

    def walk_speed(self):
        return 1.0 + 0.22 * self.time + 0.06 * self.weight

    def bounce(self):
        return 1.0 - 0.45 * self.weight + 0.2 * max(0.0, -self.flow)

    def swing(self):
        return 1.0 + 0.3 * self.weight + 0.15 * max(0.0, -self.flow)


# moods carry an effort (weight, time, space, flow)
MOOD_EFFORT = {
    "neutral": (0, 0, 0, 0), "happy": (-0.2, 0.3, 0.0, -0.5), "excited": (-0.3, 0.8, -0.2, -0.8),
    "sad": (-0.7, -0.8, -0.5, 0.2), "angry": (0.9, 0.7, 0.8, 0.6), "surprised": (0.2, 0.9, 0.3, 0.4),
    "worried": (-0.4, 0.3, -0.6, 0.7), "scared": (-0.3, 0.9, -0.5, 0.9), "smug": (0.3, -0.4, 0.6, -0.3),
    "sleepy": (-0.8, -0.9, -0.6, -0.4),
    "gleeful": (-0.1, 0.6, 0.0, -0.7), "crazed": (0.6, 0.8, 0.4, -0.9), "furious": (1.0, 0.9, 0.9, 0.8),
    "determined": (0.7, 0.2, 0.9, 0.7), "terrified": (-0.5, 1.0, -0.8, 1.0), "screaming": (0.4, 1.0, -0.3, 0.6),
    "shocked": (0.1, 1.0, 0.2, 0.9), "disgusted": (0.2, 0.3, 0.4, 0.6), "suspicious": (0.1, -0.5, 0.8, 0.5),
    "crying": (-0.8, -0.4, -0.7, 0.3), "embarrassed": (-0.6, 0.2, -0.7, 0.6), "nervous": (-0.4, 0.5, -0.7, 0.8),
    "bored": (-0.7, -0.8, -0.3, -0.6), "loving": (-0.6, -0.4, 0.0, -0.8),
}


class Manner(Plugin):
    """How something is done: "angrily", "nervously", "proudly"... (an effort, see above)."""
    kind = "manner"
    abstract = True
    weight = time = space = flow = 0.0

    @classmethod
    def describe_extra(cls):
        return {"effort": [cls.weight, cls.time, cls.space, cls.flow]}

    @classmethod
    def define(cls, name, **values):
        return type(name.title().replace("_", ""), (cls,), {"name": name, **values})

    def effort(self):
        return Effort(self.weight, self.time, self.space, self.flow)


for _n, _e in {
    "angrily": (0.9, 0.7, 0.8, 0.6), "happily": (-0.2, 0.3, 0.0, -0.6), "sadly": (-0.7, -0.8, -0.5, 0.2),
    "nervously": (-0.4, 0.6, -0.8, 0.9), "proudly": (0.5, -0.2, 0.8, -0.2), "lazily": (-0.6, -0.9, -0.4, -0.6),
    "excitedly": (-0.2, 0.9, -0.3, -0.9), "carefully": (-0.5, -0.6, 0.6, 0.8), "sneakily": (-0.8, -0.3, -0.2, 0.8),
    "wildly": (0.7, 0.9, -0.9, -1.0), "gently": (-0.8, -0.5, 0.2, -0.4), "firmly": (0.8, 0.0, 0.9, 0.5),
}.items():
    Manner.define(_n, weight=_e[0], time=_e[1], space=_e[2], flow=_e[3])


HOW = Param("how", "manner", label="How")


def effort_of(c, t, how=None):
    """The effort a character moves with at time t: the manner asked for, else their mood's."""
    from . import plugins
    if how:
        return plugins.get("manner", how)().effort()
    mood = "neutral"
    for tm, m, *_ in getattr(c, "_moods", []):
        if tm <= t + 1e-6:
            mood = m
    m = plugins.get("mood", mood)
    e = getattr(m, "effort", None) or MOOD_EFFORT.get(mood, (0, 0, 0, 0))
    return Effort(*e)


def shape(curves, t0, t1, effort, exaggeration=1.0):
    """Reshape the keys a gesture made between t0 and t1 (seconds) by effort: retime, rescale, add
    anticipation and follow-through. Returns the new end time."""
    f0, f1 = keys.CLOCK.frame(t0), keys.CLOCK.frame(t1)
    if f1 <= f0:
        return t1
    tempo = effort.tempo()
    amp = 1.0 + (effort.amplitude() - 1.0) * exaggeration
    amp *= 1.0 + 0.25 * (exaggeration - 1.0)
    antic = effort.anticipation() * exaggeration
    over = effort.overshoot() * exaggeration
    settle_frames = max(2, int(round(0.28 * keys.CLOCK.fps * tempo)))
    end_frame = f0 + (f1 - f0) * tempo
    for fc in curves:
        pts = [kp for kp in fc.keyframe_points if f0 - 0.01 <= kp.co.x <= f1 + 0.01]
        if len(pts) < 2:
            continue
        pts.sort(key=lambda kp: kp.co.x)
        base = fc.evaluate(f0)
        later = [kp for kp in fc.keyframe_points if kp.co.x > f1 + 0.01]
        moves = [kp for kp in pts[1:] if abs(kp.co.y - base) > 1e-4]
        if not moves:
            continue
        rot = "rotation" in fc.data_path
        for kp in pts[1:]:
            x = f0 + (kp.co.x - f0) * tempo
            d = kp.co.y - base
            extra = d * (amp - 1.0)
            if rot:      # big rotations grow by at most 15 degrees, and poses past 120 degrees not at all
                extra = max(-0.26, min(0.26, extra))
                if abs(base + d) > 2.09 and abs(base + d + extra) > abs(base + d):
                    extra = 0.0
            y = base + d + extra
            dx, dy = x - kp.co.x, y - kp.co.y
            kp.co = (x, y)
            kp.handle_left = (kp.handle_left.x + dx, kp.handle_left.y + dy)
            kp.handle_right = (kp.handle_right.x + dx, kp.handle_right.y + dy)
        first = moves[0]
        if antic > 0.01 and first.co.x - f0 >= 3:
            xa = f0 + (first.co.x - f0) * 0.45
            fc.keyframe_points.insert(xa, base - (first.co.y - base) * antic, options={"FAST"})
        last, prev = pts[-1], pts[-2]
        if over > 0.01 and abs(last.co.y - prev.co.y) > 1e-4 and not later:
            xo = last.co.x + settle_frames * 0.4
            fc.keyframe_points.insert(xo, last.co.y + (last.co.y - prev.co.y) * over, options={"FAST"})
            fc.keyframe_points.insert(last.co.x + settle_frames, last.co.y, options={"FAST"})
            end_frame = max(end_frame, last.co.x + settle_frames)
        fc.update()
    return keys.CLOCK.seconds(end_frame)


def follow_through(c, length, exaggeration=1.0):
    """Bake a damped spring onto each of a character's dangly parts: they lag behind the body when
    it starts, stops, turns, nods or jumps, and then settle (follow-through, overlapping action)."""
    import math
    if not c.danglers:
        return
    fps = keys.CLOCK.fps
    n = keys.CLOCK.frame(length) + 2
    frames = list(range(1, n + 1))

    def at(f):
        t = keys.CLOCK.seconds(f)
        loc = keys.sample(c.root, "location", t)
        hz = keys.sample(c.hips, "location", t)[2]
        rz = keys.sample(c.root, "rotation_euler", t)[2]
        nod = keys.sample(c.neck, "rotation_euler", t)[0] if c.neck is not None else 0.0
        return loc[0], loc[1], loc[2] + hz, rz, nod

    samples = [at(f) for f in range(0, n + 2)]
    dt = 1.0 / fps
    acc = []
    for i in range(1, n + 1):
        p0, p1, p2 = samples[i - 1], samples[i], samples[i + 1]
        ax, ay, az = ((p2[j] - 2 * p1[j] + p0[j]) / dt ** 2 for j in range(3))
        h = p1[3]
        # into the character's own frame (it faces -y): sideways and forward/back
        lx = ax * math.cos(-h) - ay * math.sin(-h)
        ly = ax * math.sin(-h) + ay * math.cos(-h)
        turn = (p2[3] - 2 * p1[3] + p0[3]) / dt ** 2
        nod = (p2[4] - 2 * p1[4] + p0[4]) / dt ** 2
        acc.append((lx, ly, az, turn, nod))
    # smooth over ~0.2 s: real bodies don't change speed in a single frame
    w = max(1, int(round(0.1 * fps)))
    acc = [tuple(sum(acc[j][m] for j in range(max(0, i - w), min(len(acc), i + w + 1))) /
                 (min(len(acc), i + w + 1) - max(0, i - w)) for m in range(5)) for i in range(len(acc))]
    for piv, stiff, damp, gain in c.danglers:
        k = 260.0 * stiff
        cdamp = 2 * 0.22 * math.sqrt(k) * damp
        g = 8.0 * gain * exaggeration
        th = [0.0, 0.0, 0.0]
        vel = [0.0, 0.0, 0.0]
        rows = []
        lim = math.radians(40)
        for lx, ly, az, turn, nod in acc:
            drive = (-g * ly - 0.18 * g * az - 0.35 * nod * gain,     # about x: forward/back (and bounce)
                     g * lx,                                             # about y: sideways
                     -0.5 * turn * gain)                                 # about z: lag behind a turn
            for _ in range(4):
                for j in range(3):
                    a = -k * th[j] - cdamp * vel[j] + drive[j]
                    vel[j] += a * dt / 4
                    th[j] = max(-lim, min(lim, th[j] + vel[j] * dt / 4))
            rows.append(tuple(th))
        keys.bake(piv, "rotation_euler", frames, rows)
