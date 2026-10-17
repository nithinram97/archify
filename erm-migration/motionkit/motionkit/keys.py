"""Keyframes, the one primitive every animation in the kit is built on.

    key(obj, "location", at=2.0, value=(0, 0, 1), ease="smooth")
    animate(obj, "scale", {0: 0.0, 0.6: 1.1, 1.0: 1.0}, ease="back")

`ease` describes the motion *from this key to the next one*.
"""
from . import _compat
from .timing import easing


def _frame(at):
    from . import timing
    return timing.CLOCK.frame(at)


def key(target, prop, at, value, ease="smooth"):
    """Set `target.prop = value` and keyframe it at `at` seconds.

    The interpolation is written on the key itself: Blender 4.4+ ignores the user preference for
    keys inserted from Python, which used to turn hard cuts into slow ramps.
    """
    interp, mode = easing(ease)
    frame = _frame(at)
    if isinstance(value, (int, float)) and hasattr(getattr(target, prop), "__len__"):
        value = (value,) * len(getattr(target, prop))
    setattr(target, prop, value)
    target.keyframe_insert(prop, frame=frame)
    try:
        full = target.path_from_id(prop)
    except Exception:
        full = prop
    for fc in _compat.fcurves(target.id_data):
        if fc.data_path == full:
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - frame) < 0.5:
                    kp.interpolation = interp
                    if interp not in ("BEZIER", "CONSTANT", "LINEAR"):
                        kp.easing = mode


def animate(target, prop, keys, ease="smooth"):
    """Keyframe several values at once: `keys` maps seconds -> value.

    `ease` may be one name for every segment or a list with one name per key.
    """
    items = sorted(keys.items())
    eases = ease if isinstance(ease, (list, tuple)) else [ease] * len(items)
    for (t, v), e in zip(items, eases):
        key(target, prop, t, v, e)


def socket_key(socket, at, value, ease="smooth"):
    """Keyframe a node socket's value (material alpha, glow strength, ...)."""
    key(socket, "default_value", at, value, ease)


def value_at(target, prop, at):
    """Where `target.prop` stands at `at` seconds: the value of its last key at or before that moment
    (or its current value if it has no keys yet).

    Every move starts from here, so motions can be written in any order: a move that starts at 6 s
    picks up from wherever the previous move ended, even if later shots were scripted first.
    """
    from . import timing
    frame = timing.CLOCK.frame(at) + 0.5
    cur = getattr(target, prop)
    try:
        full = target.path_from_id(prop)
    except Exception:
        full = prop
    curves = {fc.array_index: fc for fc in _compat.fcurves(target.id_data) if fc.data_path == full}

    def held(fc, default):
        best = None
        for kp in fc.keyframe_points:
            if kp.co[0] <= frame and (best is None or kp.co[0] > best.co[0]):
                best = kp
        return best.co[1] if best is not None else default

    if not hasattr(cur, "__len__"):
        return held(curves[0], cur) if 0 in curves else cur
    vec = cur.copy() if hasattr(cur, "copy") else list(cur)
    for i, fc in curves.items():
        vec[i] = held(fc, vec[i])
    return vec
