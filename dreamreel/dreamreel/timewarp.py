"""Time effects inside a scene: slow motion (with speed ramps), freeze frames and jump cuts.

They work on the scene's animation itself, after everything else is built: every keyframe (characters,
camera, faces, lights) is moved in time. So slow motion is genuinely smooth (Blender renders the
in-between frames), a freeze holds everything still, and a jump cut skips story time.

    [[beats]]
    do = "slow_motion"        # the next 2 story-seconds play at 30% speed
    seconds = 2.0
    speed = 0.3
    ramp = 0.4                # ease into and out of it

The scene's subtitles, captions, voices and camera cuts move with the picture.
"""
import bpy

from . import keys


def fcurves_of(act):
    """An action's animation curves (legacy and layered actions)."""
    out = []
    if act is None:
        return out
    if getattr(act, "layers", None):
        for layer in act.layers:
            for strip in layer.strips:
                for bag in getattr(strip, "channelbags", []):
                    out.extend(bag.fcurves)
    else:
        out.extend(getattr(act, "fcurves", []))
    return out


def all_fcurves():
    """Every animation curve in the file."""
    return [fc for act in bpy.data.actions for fc in fcurves_of(act)]


class Warp:
    """One time effect: `map_time` moves a story moment (seconds) to its time on screen and `unmap` is
    the way back (which story moment is on screen at a time)."""

    def __init__(self, at, seconds):
        self.at, self.seconds = at, seconds

    def map_time(self, t):
        return t

    def unmap(self, u):
        return u


class Slow(Warp):
    """Story time [at, at+seconds] plays at `speed` (0.3 = slow motion; 2 = fast forward)."""

    def __init__(self, at, seconds, speed):
        super().__init__(at, seconds)
        self.speed = max(0.02, speed)

    def map_time(self, t):
        a, b = self.at, self.at + self.seconds
        if t <= a:
            return t
        if t <= b:
            return a + (t - a) / self.speed
        return t + self.seconds * (1 / self.speed - 1)

    def unmap(self, u):
        a, b = self.at, self.at + self.seconds / self.speed
        if u <= a:
            return u
        if u <= b:
            return a + (u - a) * self.speed
        return u - self.seconds * (1 / self.speed - 1)


class Freeze(Warp):
    """Everything holds still for `seconds` at `at`."""

    def map_time(self, t):
        return t if t <= self.at else t + self.seconds

    def unmap(self, u):
        if u <= self.at:
            return u
        return self.at if u <= self.at + self.seconds else u - self.seconds


class Jump(Warp):
    """A jump cut: story time [at, at+seconds] is cut out."""

    def map_time(self, t):
        return t if t <= self.at else max(self.at, t - self.seconds)

    def unmap(self, u):
        return u if u <= self.at else u + self.seconds


def slow_motion(at, seconds, speed, ramp=0.0):
    """Slow motion, with optional ease in and out (a speed ramp)."""
    ramp = max(0.0, min(ramp, seconds / 3))
    if ramp <= 0:
        return [Slow(at, seconds, speed)]
    mid = (1 + speed) / 2
    return [Slow(at, ramp, mid), Slow(at + ramp, seconds - 2 * ramp, speed), Slow(at + seconds - ramp, ramp, mid)]


def _retime(fc, to_screen, to_story, first):
    """Re-key one curve on screen time. Step curves (visibility, camera cuts) keep their keys, moved;
    smooth curves are sampled every frame from the original, so their shape is kept exactly."""
    pts = fc.keyframe_points
    if len(pts) == 0 or pts[-1].co.x <= first:
        return
    clock = keys.CLOCK

    def fmap(f):
        return to_screen(clock.seconds(f)) * clock.fps + 1
    values = {round(kp.co.y, 6) for kp in pts}
    if len(pts) == 1 or len(values) == 1 or all(kp.interpolation == "CONSTANT" for kp in pts[:-1]):
        moved = {}
        for kp in pts:
            moved[round(fmap(kp.co.x), 3)] = (kp.co.y, kp.interpolation)
        pts.clear()
        for x, (y, interp) in sorted(moved.items()):
            kp = pts.insert(x, y, options={"FAST"})
            kp.interpolation = interp
        fc.update()
        return
    lo, hi = pts[0].co.x, pts[-1].co.x
    g0, g1 = int(fmap(lo)), int(fmap(hi)) + 1
    samples = []
    for g in range(g0, g1 + 1):
        f = min(hi, max(lo, to_story(clock.seconds(g)) * clock.fps + 1))
        samples.append((g, fc.evaluate(f)))
    pts.clear()
    pts.add(len(samples))
    flat = [c for xy in samples for c in xy]
    pts.foreach_set("co", flat)
    for kp in pts:
        kp.interpolation = "LINEAR"
    fc.update()


def apply(warps):
    """Apply time effects to every animation curve in the file.
    Returns a function that maps any story moment (seconds) to its time on screen."""
    order = sorted(warps, key=lambda w: w.at, reverse=True)

    def mapper(t):
        for w in order:
            t = w.map_time(t)
        return t

    def unmapper(u):
        for w in reversed(order):
            u = w.unmap(u)
        return u
    if order:
        first = keys.CLOCK.frame(min(w.at for w in order)) - 1
        for fc in all_fcurves():
            _retime(fc, mapper, unmapper, first)
    return mapper
