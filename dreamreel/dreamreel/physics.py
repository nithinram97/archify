"""Physics: things that fall, bounce, roll, tumble and get knocked over.

When a character lets go of something (`drop`, `throw` without a catcher, `knock_over`, `kick`), the
moment is simulated with real rigid-body physics (Bullet, through Blender) and the result is baked
into ordinary keys. The thing keeps the hand's speed, hits the table edge, the floor, the walls and
other things, and comes to rest; things it hits move too. Because it's baked straight away, later
beats know where it ended up (`pick_up` walks over to it).

    [[beats]]
    who = "mia"
    do = "knock_over"
    thing = "vase"

    [[beats]]
    who = "tom"
    do = "throw"
    thing = "ball"
    to = "mia"          # she catches it; to a place, it lands, bounces and rolls

Items say how they behave: `mass` (kg), `bounce` (0 dead ... 1 superball), `friction`, and `shape`
("hull", "sphere", "box"). A new item can set them as class attributes.
"""
import bmesh
import bpy
from mathutils import Matrix, Vector

from . import keys

G = Vector((0, 0, -9.81))
LEAD = 3            # frames of kinematic motion before the simulation takes over (carries the speed)


def _props(thing):
    from . import plugins
    item = getattr(thing, "item", None)
    cls = plugins.get("item", item) if item else None
    return {k: getattr(cls, k, d) for k, d in
            (("mass", 0.3), ("bounce", 0.2), ("friction", 0.6), ("shape", "hull"))}


def _descendants(obj):
    out = []
    for c in obj.children:
        out.append(c)
        out += _descendants(c)
    return out


def _owned(scene):
    """Objects that belong to characters or things (not the set's solid scenery)."""
    owned = set()
    for c in scene.actors.values():
        owned.add(c.root.name)
        owned.update(o.name for o in _descendants(c.root))
        for extra in list(getattr(c, "feet", {}).values()) + [getattr(c, "holder", None)]:
            if extra is not None:
                owned.add(extra.name)
                owned.update(o.name for o in _descendants(extra))
    if scene.set is not None:
        for th in scene.set.things.values():
            owned.add(th.root.name)
            owned.update(o.name for o in _descendants(th.root))
    return owned


def _hull(thing, dg):
    """A convex mesh round the thing as it is now (world space), centred on its middle."""
    pts = []
    for o in _descendants(thing.root):
        if o.type != "MESH" or o.hide_render:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        pts += [ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    if len(pts) < 4:
        return None, None
    bm = bmesh.new()
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    # the centre of mass (Bullet's pivot is the object's origin): the hull's volume centroid
    bm.verts.ensure_lookup_table()
    o = bm.verts[0].co.copy()
    vol, acc = 0.0, Vector()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for a, b in zip(vs[1:-1], vs[2:]):
            dv = (vs[0] - o).dot((a - o).cross(b - o)) / 6
            vol += dv
            acc += dv * (o + vs[0] + a + b) / 4
    mid = acc / vol if abs(vol) > 1e-12 else sum(pts, Vector()) / len(pts)
    for v in bm.verts:
        v.co -= mid
    me = bpy.data.meshes.new(f"phys.{thing.name}")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(f"phys.{thing.name}", me)
    obj.location = mid
    return obj, mid


def _rigid(objs, kind):
    if not objs:
        return
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.rigidbody.objects_add(type=kind)


def simulate(scene, t, pushes, most=4.0, reach=2.5, sweep=None):
    """Simulate from time t: `pushes` is {thing: (velocity, spin)} (m/s, rad/s vectors) for the things
    set moving (or None for things that start still); other loose things nearby join in (and move if
    they're hit). `sweep` = (start, velocity, seconds) moves an invisible hand through the scene that
    pushes whatever it meets. Bakes keys; returns the time everything has settled."""
    from . import handling
    fps = keys.CLOCK.fps
    f0 = keys.CLOCK.frame(t)
    handling.evaluate(scene, t)
    dg = bpy.context.evaluated_depsgraph_get()
    sc = scene.bscene
    coll = bpy.data.collections.new("physics")
    sc.collection.children.link(coll)
    made = []
    # what moves: the pushed things, and any loose thing near them
    centres = [handling.thing_point(scene, th, t) for th in pushes]
    loose = [th for th in (scene.set.things.values() if scene.set else [])
             if th not in pushes and th.holder is None and th.character is None
             and any((th.root.matrix_world.translation - c).length < reach for c in centres)]
    bodies = {}
    for th in list(pushes) + loose:
        obj, mid = _hull(th, dg)
        if obj is None:
            continue
        coll.objects.link(obj)
        obj.hide_render = True
        made.append(obj)
        bpy.context.view_layer.update()
        bodies[th] = (obj, obj.matrix_world.inverted() @ th.root.matrix_world)
    # what they hit: the set's solid things near them (shared meshes, so the set itself is untouched)
    owned = _owned(scene)
    fast = max([Vector(pv[0]).length for pv in pushes.values() if pv is not None] + [0.0])
    if sweep is not None:
        fast = max(fast, Vector(sweep[1]).length)
    far = min(15.0, reach + 1 + fast * most * 0.6)     # as far as anything could get
    lo = Vector((min(c.x for c in centres) - far, min(c.y for c in centres) - far))
    hi = Vector((max(c.x for c in centres) + far, max(c.y for c in centres) + far))
    solid = []
    for o in list(sc.objects):
        if (o.type != "MESH" or o.name in owned or o.hide_render or o.get("dr_fx") or o.get("dr_final_only")
                or o.name.startswith("phys.")):
            continue
        bb = [o.matrix_world @ Vector(b) for b in o.bound_box]
        if (max(p.x for p in bb) < lo.x or min(p.x for p in bb) > hi.x or max(p.y for p in bb) < lo.y
                or min(p.y for p in bb) > hi.y):
            continue
        if max(p.z for p in bb) - min(p.z for p in bb) > 30:      # skies and domes
            continue
        p = bpy.data.objects.new(f"phys.solid.{o.name}", o.data)
        p.matrix_world = o.matrix_world.copy()
        p.hide_render = True
        coll.objects.link(p)
        made.append(p)
        solid.append(p)
    # a floor under everything, in case the set has none
    floor_me = bpy.data.meshes.new("phys.floor")
    floor_me.from_pydata([(-50, -50, 0), (50, -50, 0), (50, 50, 0), (-50, 50, 0)], [], [(0, 1, 2, 3)])
    floor = bpy.data.objects.new("phys.floor", floor_me)
    floor.hide_render = True
    coll.objects.link(floor)
    made.append(floor)
    if not getattr(scene.set, "outdoor", False):
        solid.append(floor)
    bpy.context.view_layer.update()
    had_world = sc.rigidbody_world is not None
    if not had_world:
        bpy.ops.rigidbody.world_add()
    rw = sc.rigidbody_world
    rw.enabled = True
    rw.substeps_per_frame = 20 if fast < 6 else 40
    rw.solver_iterations = 20
    end = f0 + int(most * fps)
    rw.point_cache.frame_start = f0 - LEAD
    rw.point_cache.frame_end = end
    _rigid(solid, "PASSIVE")
    for p in solid:
        rb = p.rigid_body
        rb.collision_shape = "MESH"
        rb.mesh_source = "FINAL"
        rb.friction, rb.restitution = 0.7, 0.3
        rb.use_margin, rb.collision_margin = True, 0.0
    hand = None
    if sweep is not None:
        hme = bpy.data.meshes.new("phys.hand")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.035)
        bm.to_mesh(hme)
        bm.free()
        hand = bpy.data.objects.new("phys.hand", hme)
        hand.hide_render = True
        coll.objects.link(hand)
        made.append(hand)
    _rigid([b[0] for b in bodies.values()], "ACTIVE")
    if hand is not None:
        _rigid([hand], "ACTIVE")
        rb = hand.rigid_body
        rb.kinematic, rb.collision_shape, rb.mass = True, "SPHERE", 2.0
        start, hv, dur = Vector(sweep[0]), Vector(sweep[1]), sweep[2]
        for k in range(-LEAD, int(dur * fps) + 2):
            hand.location = start + hv * (k / fps)
            hand.keyframe_insert("location", frame=f0 + k)
        hand.location = start + hv * dur + Vector((0, 0, 3))      # then out of the way
        hand.keyframe_insert("location", frame=f0 + int(dur * fps) + 3)
    for th, (obj, _) in bodies.items():
        pr = _props(th)
        rb = obj.rigid_body
        rb.collision_shape = {"sphere": "SPHERE", "box": "BOX"}.get(pr["shape"], "CONVEX_HULL")
        rb.mass, rb.friction, rb.restitution = pr["mass"], pr["friction"], pr["bounce"]
        rb.use_margin, rb.collision_margin = True, 0.002
        # round things roll on and on in Bullet (no rolling resistance): damp their spin more
        rb.linear_damping, rb.angular_damping = (0.3, 0.6) if pr["shape"] == "sphere" else (0.05, 0.15)
        if pushes.get(th) is not None:
            v, spin = pushes[th]
            v, spin = Vector(v), Vector(spin or (0, 0, 0))
            base = obj.matrix_world.copy()
            for k in range(LEAD + 1):           # moving at v (and turning at spin) up to the release
                dt = (k - LEAD) / fps
                ang = spin.length * dt
                R = Matrix.Rotation(ang, 4, spin.normalized()) if spin.length > 1e-6 else Matrix.Identity(4)
                m = Matrix.Translation(base.translation + v * dt) @ R @ base.to_3x3().to_4x4()
                obj.matrix_world = m
                obj.keyframe_insert("location", frame=f0 - LEAD + k)
                obj.keyframe_insert("rotation_euler", frame=f0 - LEAD + k)
            rb.kinematic = True
            rb.keyframe_insert("kinematic", frame=f0)
            rb.kinematic = False
            rb.keyframe_insert("kinematic", frame=f0 + 1)
        elif th not in pushes:
            rb.use_deactivation = True
            rb.use_start_deactivated = True
    # run it, frame by frame, until everything is still
    track = {th: [] for th in bodies}
    still = 0
    f = f0 - LEAD
    for f in range(f0 - LEAD, end + 1):
        sc.frame_set(f)
        moving = False
        for th, (obj, off) in bodies.items():
            m = obj.matrix_world.copy()
            if f >= f0 and track[th] and (m.translation - track[th][-1][1].translation).length > 0.0015:
                moving = True
            if f >= f0:
                track[th].append((f, m @ off))
        still = 0 if moving or f < f0 + 6 else still + 1
        if still >= 10:
            break
    stop = f
    # tidy up: the simulation is gone, its result stays as keys
    rw.point_cache.frame_start, rw.point_cache.frame_end = 1, 250
    if not had_world:
        bpy.ops.rigidbody.world_remove()
    for o in made:
        data = o.data if o.name.startswith("phys.") and o.data and o.data.users == 1 else None
        bpy.data.objects.remove(o)
        if data is not None:
            bpy.data.meshes.remove(data)
    bpy.data.collections.remove(coll)
    for th, frames in track.items():
        if not frames:
            continue
        moved = max((m.translation - frames[0][1].translation).length for _, m in frames)
        if th not in pushes and moved < 0.01:
            continue
        _bake(th.root, frames)
    sc.frame_set(f0)
    return keys.CLOCK.seconds(stop)


def _bake(root, frames):
    """Keys every frame (linear between), with Euler angles kept continuous."""
    prev = root.rotation_euler.copy()
    for f, m in frames:
        loc, rot, _ = m.decompose()
        eul = rot.to_euler(root.rotation_mode, prev)
        prev = eul
        root.location = loc
        root.rotation_euler = eul
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    lo, hi = frames[0][0], frames[-1][0]
    from ._compat import fcurves
    for fc in fcurves(root):
        if fc.data_path in ("location", "rotation_euler"):
            for kp in fc.keyframe_points:
                if lo <= kp.co[0] <= hi:
                    kp.interpolation = "LINEAR"
        # anything keyed later (picked up again...) still applies after the settle
    # the frame after the last one holds the rest pose
    f, m = frames[-1]
    loc, rot, _ = m.decompose()
    keys.key(root, "location", keys.CLOCK.seconds(f + 1), tuple(loc), "cut")
    keys.key(root, "rotation_euler", keys.CLOCK.seconds(f + 1), tuple(prev), "cut")


def velocity(scene, obj, t, dt=None):
    """How fast an object is moving at time t (world, m/s), from its animation."""
    from . import handling
    dt = dt or 2 / keys.CLOCK.fps
    handling.evaluate(scene, t - dt)
    a = obj.matrix_world.translation.copy()
    handling.evaluate(scene, t)
    return (obj.matrix_world.translation - a) / dt


def ballistic(p, q, T):
    """The launch velocity that carries a thing from p to q in T seconds."""
    return (Vector(q) - Vector(p) - 0.5 * G * T * T) / T


def flight_time(p, q):
    """A natural throw: longer throws take longer, short tosses still arc."""
    d = (Vector(q) - Vector(p)).length
    return max(0.35, 0.28 + 0.13 * d)


def fly(thing, p, v, t0, T, spin=6.0):
    """Key a thrown thing along its arc (for catches: no simulation, it has to arrive)."""
    fps = keys.CLOCK.fps
    n = max(2, int(T * fps))
    root = thing.root
    base = root.rotation_euler.copy()
    for k in range(n + 1):
        tt = T * k / n
        pos = Vector(p) + Vector(v) * tt + 0.5 * G * tt * tt
        f = keys.CLOCK.frame(t0 + tt)
        root.location = pos
        root.rotation_euler = (base.x + spin * tt, base.y, base.z + 0.3 * spin * tt)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    from ._compat import fcurves
    lo, hi = keys.CLOCK.frame(t0), keys.CLOCK.frame(t0 + T)
    for fc in fcurves(root):
        if fc.data_path in ("location", "rotation_euler"):
            for kp in fc.keyframe_points:
                if lo <= kp.co[0] <= hi:
                    kp.interpolation = "LINEAR"


def spin_for(v, amount=1.0):
    """A tumble that goes with a push: turning about the horizontal axis across the motion."""
    flat = Vector((v.x, v.y, 0))
    if flat.length < 1e-6:
        return Vector((amount * 2, 0, 0))
    return Vector((0, 0, 1)).cross(flat.normalized()) * amount * 6
