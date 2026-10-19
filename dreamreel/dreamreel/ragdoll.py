"""Ragdolls: bodies that fall the way bodies fall.

When a blow knocks someone down, the moment is simulated: the body becomes a ragdoll (a capsule for the
pelvis, chest, head, upper and lower arms and legs, jointed with the limits of real joints), moving
as it was when the blow landed plus the blow's push. It flies, hits the ground (and the set, and the
other bodies falling with it), tumbles, slides and comes to rest, all with Bullet's physics through
Blender. The result is baked onto the skeleton, and a captured get-up (off the back, or face down)
takes over from wherever and however the body came to rest.

    ragdoll.knock_down(scene, [(smith, push)], t)        # push: the blow's velocity (m/s)

Several bodies knocked down at once fall together and collide with each other (the pile-on bursting).
Bodies without a skeleton can't be ragdolls (fighting.knock_down animates them instead).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import keys

LEAD = 3
# the body's parts: (name, from joint, to joint, radius as a share of height, mass share, bones it moves)
PARTS = [
    ("pelvis", "hips", "_waist", 0.075, 0.15, ("hips",)),
    ("chest", "_waist", "neck", 0.085, 0.25, ("_spine",)),
    ("head", "neck", "_top", 0.06, 0.08, ("neck", "head")),
    ("l_upper", "l_arm", "l_elbow", 0.03, 0.03, ("l_arm",)),
    ("l_fore", "l_elbow", "_l_hand", 0.026, 0.025, ("l_elbow", "l_wrist")),
    ("r_upper", "r_arm", "r_elbow", 0.03, 0.03, ("r_arm",)),
    ("r_fore", "r_elbow", "_r_hand", 0.026, 0.025, ("r_elbow", "r_wrist")),
    ("l_thigh", "l_hip", "l_knee", 0.045, 0.1, ("l_hip",)),
    ("l_shin", "l_knee", "_l_toe", 0.034, 0.06, ("l_knee", "l_ankle")),
    ("r_thigh", "r_hip", "r_knee", 0.045, 0.1, ("r_hip",)),
    ("r_shin", "r_knee", "_r_toe", 0.034, 0.06, ("r_knee", "r_ankle")),
]
# joints: (part, part, where, angle limit in degrees)
JOINTS = [("pelvis", "chest", "_waist", 25), ("chest", "head", "neck", 40),
          ("chest", "l_upper", "l_arm", 85), ("l_upper", "l_fore", "l_elbow", 70),
          ("chest", "r_upper", "r_arm", 85), ("r_upper", "r_fore", "r_elbow", 70),
          ("pelvis", "l_thigh", "l_hip", 70), ("l_thigh", "l_shin", "l_knee", 65),
          ("pelvis", "r_thigh", "r_hip", 70), ("r_thigh", "r_shin", "r_knee", 65)]
# how much of a blow each part takes (a punch moves the head and chest more than the feet)
TAKES = {"head": 1.2, "chest": 1.1, "pelvis": 0.8, "l_upper": 1.0, "r_upper": 1.0, "l_fore": 0.9, "r_fore": 0.9,
         "l_thigh": 0.55, "r_thigh": 0.55, "l_shin": 0.35, "r_shin": 0.35}


def can_fall(c):
    return bool(getattr(c, "rig", None)) and hasattr(c, "perform_clip") and all(
        r in getattr(c, "roles", {}) for r in ("hips", "neck", "l_arm", "l_elbow", "l_wrist", "l_hip", "l_knee", "l_ankle",
                                               "r_arm", "r_elbow", "r_wrist", "r_hip", "r_knee", "r_ankle"))


def _joints(c):
    """World positions of the joints (and a few points between them) as the body is now."""
    rig, R = c.rig, c.roles
    pb = rig.pose.bones
    M = rig.matrix_world
    J = {r: M @ pb[b].head for r, b in R.items() if b in pb}
    J["_waist"] = J["hips"].lerp(J["neck"], 0.45)
    head = pb[R.get("head", R["neck"])]
    J["_top"] = M @ head.tail if (M @ head.tail - J["neck"]).length > 0.08 * c.H else J["neck"] + (J["neck"] - J["hips"]).normalized() * 0.22 * c.H
    for s in "lr":
        fore = J[f"{s}_wrist"] - J[f"{s}_elbow"]
        J[f"_{s}_hand"] = J[f"{s}_wrist"] + fore.normalized() * 0.06 * c.H
        shin = J[f"{s}_ankle"] - J[f"{s}_knee"]
        J[f"_{s}_toe"] = J[f"{s}_ankle"] + shin.normalized() * 0.03 * c.H
    return J


def _capsule(name, a, b, r, coll):
    """A body part: a box the size of the capsule (Bullet makes the capsule from its bounds), long axis z."""
    L = max(0.02, (b - a).length)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(2 * r, 2 * r, L + 2 * r), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    o.hide_render = True
    o.display_type = "WIRE"
    d = (b - a).normalized() if (b - a).length > 1e-6 else Vector((0, 0, 1))
    o.matrix_world = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    return o


def _rigid(objs, kind):
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.rigidbody.objects_add(type=kind)


def knock_down(scene, falls, t, most=3.0, settle=None):
    """Simulate bodies knocked down at time t: `falls` is [(character, push velocity Vector)]. Bakes each
    fall onto its skeleton and returns {character: {rest: time, on_back, heading, where}}. `settle(c, axis,
    on_back, pelvis)` may choose where the character's root goes (where, heading) for what comes next."""
    from . import handling, physics
    fps = keys.CLOCK.fps
    f0 = keys.CLOCK.frame(t)
    sc = scene.bscene
    coll = bpy.data.collections.new("ragdolls")
    sc.collection.children.link(coll)
    made, bodies = [], {}
    # each body as it is a moment before and at the blow (its own motion carries on)
    handling.evaluate(scene, keys.CLOCK.seconds(f0 - 1))
    before = {c: _joints(c) for c, _ in falls}
    handling.evaluate(scene, t)
    now = {c: _joints(c) for c, _ in falls}
    bones_at = {c: {pb.name: c.rig.matrix_world @ pb.matrix for pb in c.rig.pose.bones} for c, _ in falls}
    for c, push in falls:
        J, J1 = now[c], before[c]
        parts = {}
        for name, a, b, r, mass, _ in PARTS:
            o = _capsule(f"rag.{c.name}.{name}", J[a], J[b], r * c.H, coll)
            made.append(o)
            v = ((J[a] + J[b]) - (J1[a] + J1[b])) / 2 * fps + Vector(push) * TAKES.get(name, 1.0)
            parts[name] = (o, mass * 75.0 * (c.H / 1.75) ** 3, v)
        bodies[c] = parts
    # what they land on and hit: the set near them, and a floor
    centres = [now[c]["hips"] for c, _ in falls]
    far = 3.0 + max(Vector(p).length for _, p in falls) * most * 0.5
    solid = []
    owned = physics._owned(scene)
    roots = {ch.root for ch in scene.actors.values()}
    for o in list(sc.objects):
        if o.type != "MESH" or o.hide_render or o.name.startswith(("rag.", "phys.")) or o.name in owned or o.get("dr_fx"):
            continue
        top = o
        while top.parent is not None:
            top = top.parent
        if top in roots:
            continue
        bb = [o.matrix_world @ Vector(b) for b in o.bound_box]
        if max(p.z for p in bb) - min(p.z for p in bb) > 30 or not any(
                min(p.x for p in bb) - far < q.x < max(p.x for p in bb) + far and
                min(p.y for p in bb) - far < q.y < max(p.y for p in bb) + far for q in centres):
            continue
        s = bpy.data.objects.new(f"rag.solid.{o.name}", o.data)
        s.matrix_world = o.matrix_world.copy()
        s.hide_render = True
        coll.objects.link(s)
        made.append(s)
        solid.append(s)
    ground = scene.set.ground_height(centres[0].x, centres[0].y) if scene.set and hasattr(scene.set, "ground_height") else 0.0
    fme = bpy.data.meshes.new("rag.floor")
    fme.from_pydata([(-60, -60, ground), (60, -60, ground), (60, 60, ground), (-60, 60, ground)], [], [(0, 1, 2, 3)])
    floor = bpy.data.objects.new("rag.floor", fme)
    floor.hide_render = True
    coll.objects.link(floor)
    made.append(floor)
    solid.append(floor)
    bpy.context.view_layer.update()
    had_world = sc.rigidbody_world is not None
    if not had_world:
        bpy.ops.rigidbody.world_add()
    rw = sc.rigidbody_world
    rw.enabled = True
    rw.substeps_per_frame, rw.solver_iterations = 30, 30
    end = f0 + int(most * fps)
    rw.point_cache.frame_start, rw.point_cache.frame_end = f0 - LEAD, end
    _rigid(solid, "PASSIVE")
    for s in solid:
        s.rigid_body.collision_shape = "MESH"
        s.rigid_body.friction, s.rigid_body.restitution = 0.8, 0.1
    every = [o for parts in bodies.values() for o, _, _ in parts.values()]
    _rigid(every, "ACTIVE")
    for parts in bodies.values():
        for o, mass, v in parts.values():
            rb = o.rigid_body
            rb.collision_shape = "CAPSULE"
            rb.mass, rb.friction, rb.restitution = mass, 0.7, 0.05
            rb.linear_damping, rb.angular_damping = 0.05, 0.35
            base = o.matrix_world.copy()
            for k in range(LEAD + 1):               # moving as it was, plus the blow, up to the moment of the blow
                o.matrix_world = Matrix.Translation(base.translation + v * ((k - LEAD) / fps)) @ base.to_3x3().to_4x4()
                o.keyframe_insert("location", frame=f0 - LEAD + k)
                o.keyframe_insert("rotation_euler", frame=f0 - LEAD + k)
            rb.kinematic = True
            rb.keyframe_insert("kinematic", frame=f0)
            rb.kinematic = False
            rb.keyframe_insert("kinematic", frame=f0 + 1)
    # the joints
    for c, parts in bodies.items():
        J = now[c]
        for a, b, where, lim in JOINTS:
            e = bpy.data.objects.new(f"rag.{c.name}.joint.{a}.{b}", None)
            coll.objects.link(e)
            e.matrix_world = Matrix.Translation(J[where]) @ parts[a][0].matrix_world.to_3x3().to_4x4()
            made.append(e)
            vl = bpy.context.view_layer
            for o in vl.objects:
                o.select_set(False)
            e.select_set(True)
            vl.objects.active = e
            bpy.ops.rigidbody.constraint_add(type="GENERIC")
            rc = e.rigid_body_constraint
            rc.object1, rc.object2 = parts[a][0], parts[b][0]
            rc.disable_collisions = True
            for ax in "xyz":
                setattr(rc, f"use_limit_lin_{ax}", True)
                setattr(rc, f"limit_lin_{ax}_lower", 0.0)
                setattr(rc, f"limit_lin_{ax}_upper", 0.0)
                setattr(rc, f"use_limit_ang_{ax}", True)
                twist = 0.4 if ax == "z" else 1.0          # little twist along the limb
                setattr(rc, f"limit_ang_{ax}_lower", -math.radians(lim * twist))
                setattr(rc, f"limit_ang_{ax}_upper", math.radians(lim * twist))
    # run it until everyone is still (cloth sits it out: it's simulated when the film plays)
    cloth = [m for o in bpy.data.objects for m in o.modifiers if m.type == "CLOTH" and m.show_viewport]
    for m in cloth:
        m.show_viewport = False
    track = {c: {name: [] for name in parts} for c, parts in bodies.items()}
    rest_at = {c: None for c in bodies}
    still = {c: 0 for c in bodies}
    last = {}
    for f in range(f0 - LEAD, end + 1):
        sc.frame_set(f)
        for c, parts in bodies.items():
            moved = 0.0
            for name, (o, _, _) in parts.items():
                m = o.matrix_world.copy()
                if f >= f0:
                    track[c][name].append((f, m))
                key_ = (c, name)
                if key_ in last:
                    moved = max(moved, (m.translation - last[key_]).length)
                last[key_] = m.translation.copy()
            if f > f0 + 8 and rest_at[c] is None:
                still[c] = still[c] + 1 if moved < 0.003 else 0
                if still[c] >= 8:
                    rest_at[c] = f
        if all(r is not None for r in rest_at.values()):
            break
    for m in cloth:
        m.show_viewport = True
    # tidy up: the simulation goes, its result stays on the skeletons
    # (the joints go before the parts they join, and the world last: a joint let go of after its part is
    # gone crashes Blender)
    rw.point_cache.frame_start, rw.point_cache.frame_end = 1, 250
    for o in reversed(made):
        data = o.data if o.type == "MESH" and o.data and o.data.users == 1 and o.name.startswith("rag.") else None
        bpy.data.objects.remove(o)
        if data is not None:
            bpy.data.meshes.remove(data)
    bpy.data.collections.remove(coll)
    if not had_world:
        bpy.ops.rigidbody.world_remove()
    out = {}
    for c, parts in bodies.items():
        out[c] = _bake(c, track[c], now[c], bones_at[c], f0, settle)
    sc.frame_set(f0)
    return out


def _bake(c, track, J0, bones0, f0, settle=None):
    """Key the fall onto the skeleton (and move the root to where the body ends up). Returns how it lies."""
    from .keys import CLOCK, hold, key
    from . import _compat
    from .models import _RigPose
    R = c.roles
    solver = _RigPose(c)
    # which part moves which bone, and each bone's place on its part at the blow
    owner = {}
    for name, a, b, r, mass, moves in PARTS:
        for role in moves:
            if role == "_spine":
                for bn in solver.spine:
                    owner[bn] = name
            elif role in R:
                owner[R[role]] = name
    first = {name: frames[0][1] for name, frames in track.items()}
    offset = {bn: first[part].inverted() @ bones0[bn] for bn, part in owner.items() if bn in bones0}
    frames = [f for f, _ in track["pelvis"]]
    last = {name: fr[-1][1] for name, fr in track.items()}
    # where it ends up: the root goes under the pelvis, turned along the body
    pel, ch = last["pelvis"].translation, last["chest"].translation
    axis = Vector((ch.x - pel.x, ch.y - pel.y))
    # lying on its back or its front: which way the front of the hips faces
    lh = last["l_thigh"].translation
    rh = last["r_thigh"].translation
    front = (lh - rh).cross(ch - pel)
    on_back = front.z > 0
    root_h = math.atan2(axis.x, -axis.y) if axis.length > 1e-3 else 0.0
    root_loc = Vector((pel.x, pel.y, 0.0))
    if settle is not None:
        root_loc, root_h = settle(c, axis, on_back, root_loc)
    rig_world = (Matrix.Translation(root_loc) @ Matrix.Rotation(root_h, 4, "Z")) @ c._rig_in_root
    t0 = CLOCK.seconds(f0)
    # the skeleton takes over from dreamreel's controls at the blow
    cut = f0 - 0.5
    for fc in _compat.fcurves(c.rig):
        if fc.data_path.startswith("pose.bones[") and not any(f in fc.data_path for f in ("Thumb", "Index", "Middle", "Ring", "Pinky")):
            for kp in [kp for kp in fc.keyframe_points if kp.co.x > cut][::-1]:
                fc.keyframe_points.remove(kp)
    for pb in c.rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        for con in pb.constraints:
            hold(con, "influence", CLOCK.seconds(f0 - 1))
            key(con, "influence", t0, 0.0, "cut")
    hold(c.root, "location", CLOCK.seconds(f0 - 1))
    hold(c.root, "rotation_euler", CLOCK.seconds(f0 - 1))
    key(c.root, "location", t0, tuple(root_loc), "cut")
    key(c.root, "rotation_euler", t0, (0, 0, root_h), "cut")
    hold(c.hips, "location", CLOCK.seconds(f0 - 1))
    key(c.hips, "location", t0, (0, 0, c.hip_z), "cut")
    pbs = c.rig.pose.bones
    for i, f in enumerate(frames):
        world = {bn: track[part][i][1] @ offset[bn] for bn, part in owner.items() if bn in offset}
        turns = solver.turns_from(world, rig_world)
        hips_head = (rig_world.inverted() @ world[R["hips"]]).translation
        for bn, (q, loc) in solver.bases(turns, hips_head).items():
            pbs[bn].rotation_quaternion = q
            pbs[bn].location = loc
            pbs[bn].keyframe_insert("rotation_quaternion", frame=f)
            pbs[bn].keyframe_insert("location", frame=f)
    return {"rest": CLOCK.seconds(frames[-1]), "on_back": on_back, "heading": root_h, "where": root_loc}
