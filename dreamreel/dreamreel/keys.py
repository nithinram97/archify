"""Time and keyframes.

Everything in dreamreel thinks in **seconds**; this module converts to frames and writes keys.

    key(obj, "location", at=2.0, value=(0, 0, 1), ease="smooth")
    value_at(obj, "location", at=2.0)   # where obj stands at 2 s, from its keys

`ease` describes the motion from this key to the next one.
"""
from . import _compat

EASINGS = {
    "smooth": ("BEZIER", "AUTO"),
    "linear": ("LINEAR", "AUTO"),
    "ease_in": ("CUBIC", "EASE_IN"),
    "ease_out": ("CUBIC", "EASE_OUT"),
    "ease_in_out": ("SINE", "EASE_IN_OUT"),
    "back": ("BACK", "EASE_OUT"),
    "bounce": ("BOUNCE", "EASE_OUT"),
    "cut": ("CONSTANT", "AUTO"),
}


class Clock:
    """Seconds <-> frames for the scene being built. Frame 1 is t = 0."""

    def __init__(self, fps=24):
        self.fps = fps

    def frame(self, seconds):
        return int(round(seconds * self.fps)) + 1

    def seconds(self, frame):
        return (frame - 1) / self.fps


CLOCK = Clock()


def _path(target, prop):
    try:
        return target.path_from_id(prop)
    except Exception:
        return prop


RECORDING = []    # stacks of key records while a gesture is being performed (see acting.py)


class recording:
    """Collect every curve keyed inside the block: `with keys.recording() as rec: ...`."""

    def __enter__(self):
        self.curves = set()
        RECORDING.append(self.curves)
        return self.curves

    def __exit__(self, *exc):
        RECORDING.remove(self.curves)


def key(target, prop, at, value, ease="smooth", index=-1):
    """Set `target.prop` (or one component of it, with `index`) and keyframe it at `at` seconds."""
    interp, mode = EASINGS[ease]
    frame = CLOCK.frame(at)
    if index >= 0:
        vec = getattr(target, prop)
        vec[index] = value
        target.keyframe_insert(prop, index=index, frame=frame)
    else:
        if isinstance(value, (int, float)) and hasattr(getattr(target, prop), "__len__"):
            value = (value,) * len(getattr(target, prop))
        setattr(target, prop, value)
        target.keyframe_insert(prop, frame=frame)
    full = _path(target, prop)
    for fc in _compat.fcurves(target.id_data):
        if fc.data_path == full and (index < 0 or fc.array_index == index):
            for rec in RECORDING:
                rec.add(fc)
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - frame) < 0.5:
                    kp.interpolation = interp
                    if interp not in ("BEZIER", "CONSTANT", "LINEAR"):
                        kp.easing = mode


def value_at(target, prop, at):
    """The value of `target.prop` at `at` seconds: its last key at or before that moment, or its
    current value if it has no keys. Actions start from here, so they can be written in any order."""
    frame = CLOCK.frame(at) + 0.25
    cur = getattr(target, prop)
    full = _path(target, prop)
    curves = {fc.array_index: fc for fc in _compat.fcurves(target.id_data) if fc.data_path == full}

    def held(fc, default):
        best = None
        for kp in fc.keyframe_points:
            if kp.co[0] <= frame and (best is None or kp.co[0] > best.co[0]):
                best = kp
        return best.co[1] if best is not None else default

    if not hasattr(cur, "__len__"):
        return held(curves[0], cur) if 0 in curves else cur
    vec = list(cur)
    for i, fc in curves.items():
        vec[i] = held(fc, vec[i])
    return vec


def hold(target, prop, at, index=-1, ease="smooth"):
    """Key the current value at `at` so a following move starts from here, not from an earlier key."""
    v = value_at(target, prop, at)
    if index >= 0:
        key(target, prop, at, v[index], ease, index)
    else:
        key(target, prop, at, v, ease)
    return v


def sample(target, prop, at):
    """The animated value of `target.prop` at `at` seconds, interpolated between keys (unlike value_at,
    which gives the last key). Used to follow moving things smoothly."""
    frame = CLOCK.frame(at)
    cur = getattr(target, prop)
    full = _path(target, prop)
    curves = {fc.array_index: fc for fc in _compat.fcurves(target.id_data) if fc.data_path == full}
    if not hasattr(cur, "__len__"):
        return curves[0].evaluate(frame) if 0 in curves else cur
    vec = list(cur)
    for i, fc in curves.items():
        vec[i] = fc.evaluate(frame)
    return vec


def bake(target, prop, frames, rows):
    """Replace `target.prop`'s animation with one key per frame: rows[i] is the value at frames[i].
    Fast, for simulated motion (springs)."""
    n = len(rows[0]) if hasattr(rows[0], "__len__") else 1
    target.keyframe_insert(prop, frame=frames[0])
    full = _path(target, prop)
    for fc in _compat.fcurves(target.id_data):
        if fc.data_path != full:
            continue
        i = fc.array_index
        pts = fc.keyframe_points
        pts.clear()
        pts.add(len(frames))
        co = []
        for f, r in zip(frames, rows):
            co += [f, r[i] if n > 1 else r]
        pts.foreach_set("co", co)
        for kp in pts:
            kp.interpolation = "LINEAR"
        fc.update()
