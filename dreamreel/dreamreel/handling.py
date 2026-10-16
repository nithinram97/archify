"""Handling things: holding, picking up, putting down, giving, dropping, and grabbing small characters.

Small items on tables, counters, desks and benches (`items = [...]` in a set file) are *things*: each
is one movable unit with a name (`cup`, `cup-2`, `scalpel`). A character reaches for a thing with a
real arm aim, the thing follows the hand while held (a Child Of constraint switched on at the moment
of the grab), and is let go exactly where it is put.

    [[beats]]
    who = "mia"
    do = "pick_up"
    thing = "cup"                 # walks over first if it's out of reach

    [[beats]]
    who = "mia"
    do = "give"
    to = "tom"

    [[beats]]
    who = "gran"
    do = "grab"
    thing = "frog"                # small characters can be grabbed too

Characters without arms can't handle things (they have no hands to do it with).
"""
import math

import bpy
from mathutils import Matrix, Vector

from . import keys, plugins


class Thing:
    """Something that can be held: an item, or a (small) character."""

    def __init__(self, name, root, approach=None, character=None, grip=0.0):
        self.name, self.root, self.approach, self.character = name, root, approach, character
        self.grip = grip           # height above its base where a hand holds it
        self.holder = None         # (character, side) while held


def _frame(t):
    return keys.CLOCK.frame(t)


def evaluate(scene, t):
    """Make every object's matrix_world show the animation at time t."""
    scene.bscene.frame_set(_frame(t))
    bpy.context.view_layer.update()


def _key_const(obj, prop, t, value, index=-1):
    """A key that switches instantly (for attaching and letting go)."""
    keys.key(obj, prop, t, value, "cut", index)


def _con(thing_obj, hand):
    name = f"held:{hand.name}"
    con = thing_obj.constraints.get(name)
    if con is None:
        con = thing_obj.constraints.new("CHILD_OF")
        con.name = name
        con.target = hand
        con.inverse_matrix = Matrix.Identity(4)
        con.influence = 0.0
        con.keyframe_insert("influence", frame=1)
    return con


def _influence(con, t, value):
    con.influence = value
    con.keyframe_insert("influence", frame=_frame(t))
    from ._compat import fcurves
    for fc in fcurves(con.id_data):
        if fc.data_path.endswith(f'["{con.name}"].influence'):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def _followers(thing):
    """Objects that move with a thing: its root, and a creature's foot targets."""
    objs = [thing.root]
    c = thing.character
    if c is not None and getattr(c, "feet", None):
        objs += list(c.feet.values())
    return objs


def attach(scene, thing, hand, t, snap=True):
    """From time t, `thing` moves with `hand`. With snap, it is held at its grip point (the hand closes
    on it); otherwise it keeps where it is relative to the hand right then."""
    evaluate(scene, t)
    H = hand.matrix_world
    root_w = thing.root.matrix_world.copy()
    root_local = H.inverted() @ root_w
    if snap:
        rot = root_local.to_quaternion()
        root_local = Matrix.Translation(-(rot.to_matrix() @ Vector((0, 0, thing.grip)))) @ rot.to_matrix().to_4x4()
    for obj in _followers(thing):
        # everything that moves with the thing keeps its place relative to the thing's root
        local = root_local @ root_w.inverted() @ obj.matrix_world
        for other in obj.constraints:       # let go of whoever held it before
            if other.name.startswith("held:") and other.influence > 0:
                _influence(other, t, 0.0)
        con = _con(obj, hand)
        loc, rot, _ = local.decompose()
        _key_const(obj, "location", t - 1 / keys.CLOCK.fps, tuple(obj.location))
        _key_const(obj, "location", t, tuple(loc))
        if obj.rotation_mode != "QUATERNION":
            _key_const(obj, "rotation_euler", t, tuple(rot.to_euler(obj.rotation_mode)))
        _influence(con, t - 1 / keys.CLOCK.fps, 0.0)
        _influence(con, t, 1.0)


def release(scene, thing, t, at=None, heading=None):
    """From time t the thing stays in the world: where it is then, or at `at` (x, y, z) if given."""
    evaluate(scene, t)
    for obj in _followers(thing):
        W = obj.matrix_world.copy()
        loc, rot, _ = W.decompose()
        if at is not None and obj is thing.root:
            loc = Vector(at)
            rot = Matrix.Rotation(heading or 0.0, 4, "Z").to_quaternion()
        elif at is not None:      # a creature's feet go down with it
            c = thing.character
            leg = next(k for k, v in c.feet.items() if v is obj)
            loc = c.home_at(leg, Vector(at[:2]), heading or 0.0, at[2])
        for con in obj.constraints:
            if con.name.startswith("held:") and con.influence > 0:
                _influence(con, t, 0.0)
        _key_const(obj, "location", t, tuple(loc))
        if obj.rotation_mode != "QUATERNION":
            _key_const(obj, "rotation_euler", t, tuple(rot.to_euler(obj.rotation_mode)))
    thing.holder = None


def fall(scene, thing, t, floor=0.0):
    """Let go and drop to the floor (or `floor` height), with a little bounce."""
    evaluate(scene, t)
    start = thing.root.matrix_world.translation.copy()
    release(scene, thing, t)
    h = max(0.0, start.z - floor)
    if h < 0.01:
        return t
    tf = math.sqrt(2 * h / 9.8)
    x, y = start.x, start.y
    keys.key(thing.root, "location", t + tf, (x, y, floor), "ease_in")
    keys.key(thing.root, "location", t + tf * 1.25, (x, y, floor + h * 0.06), "ease_out")
    keys.key(thing.root, "location", t + tf * 1.5, (x, y, floor), "ease_in")
    return t + tf * 1.5


# ---------------------------------------------------------------------- arms and hands
def arm_rest(c):
    """Each arm's rest direction (shoulder to hand) in its pivot's frame, and its reach."""
    if getattr(c, "_arm_rest", None) is None:
        bpy.context.view_layer.update()
        c._arm_rest = {}
        for side, piv in c.arms.items():
            hand = c.hands[side]
            r0 = piv.matrix_world.inverted() @ hand.matrix_world.translation
            c._arm_rest[side] = (r0.normalized(), r0.length)
    return c._arm_rest


def aim(c, side, t, target):
    """The rotation of an arm's pivot that points its hand at a world point (at time t)."""
    rest, _ = arm_rest(c)[side]
    evaluate(c.scene, t)
    piv = c.arms[side]
    P = piv.parent.matrix_world
    shoulder = piv.matrix_world.translation
    d = P.to_3x3().inverted() @ (Vector(target) - shoulder)
    if d.length < 1e-6:
        return (0.0, 0.0, 0.0)
    q = rest.rotation_difference(d.normalized())
    return tuple(q.to_euler("XYZ"))


def reach(c, side, t0, t1, target):
    """Move an arm so the hand reaches a world point by t1, leaning in if it's out of reach."""
    target = Vector(target)
    _, L = arm_rest(c)[side]
    step_in(c, side, t0, min(t1, t0 + 0.3), target, L)
    evaluate(c.scene, min(t1, t0 + 0.3))
    shoulder = c.arms[side].matrix_world.translation
    gap = (target - shoulder).length - L * 0.95
    if gap > 0.02 and c.body is not None:
        lean = min(math.radians(40), math.atan2(gap, max(0.15, shoulder.z - target.z + 0.25)) * 1.3)
        keys.hold(c.body, "rotation_euler", t0)
        cur = keys.value_at(c.body, "rotation_euler", t0)
        keys.key(c.body, "rotation_euler", t1, (cur[0] - lean, cur[1], cur[2]))
        c._leaning = True
    keys.hold(c.arms[side], "rotation_euler", t0)
    keys.key(c.arms[side], "rotation_euler", t1, aim(c, side, t1, target))


def step_in(c, side, t0, t1, target, L, most=0.35):
    """Take a small step towards something out of arm's reach (but not into furniture)."""
    evaluate(c.scene, t0)
    shoulder = c.arms[side].matrix_world.translation
    flat = Vector((target.x - shoulder.x, target.y - shoulder.y))
    need = flat.length - L * 0.8
    if need <= 0.02:
        return
    loc = Vector(keys.value_at(c.root, "location", t0))
    step = flat.normalized() * min(most, need)
    end = Vector((loc.x + step.x, loc.y + step.y))
    st = c.scene.set
    if st is not None:
        for _ in range(8):           # stop short of anything solid (tables are edges, not walls)
            inside = any(abs(end.x - cx) < hw + 0.12 and abs(end.y - cy) < hd + 0.12
                         for cx, cy, hw, hd in st.obstacles)
            if not inside:
                break
            end = Vector((loc.x, loc.y)) + (end - Vector((loc.x, loc.y))) * 0.6
    keys.hold(c.root, "location", t0)
    keys.key(c.root, "location", t1, (end.x, end.y, loc.z))


def straighten(c, t0, t1):
    """Stand up straight again after leaning in to reach."""
    if getattr(c, "_leaning", False):
        keys.hold(c.body, "rotation_euler", t0)
        keys.key(c.body, "rotation_euler", t1, (0, 0, 0))
        c._leaning = False


def carry_point(c, side, t):
    """Where a held thing sits: in front of the chest, a little to the hand's side."""
    _, L = arm_rest(c)[side]
    evaluate(c.scene, t)
    shoulder = c.arms[side].matrix_world.translation
    h = keys.value_at(c.root, "rotation_euler", t)[2]
    fwd = Vector((math.sin(h), -math.cos(h), 0))
    return shoulder + fwd * 0.7 * L + Vector((0, 0, -0.55 * L))


def thing_point(scene, thing, t):
    evaluate(scene, t)
    return thing.root.matrix_world.translation.copy()
