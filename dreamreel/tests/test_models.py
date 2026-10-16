"""Your own models: a figure built here is saved as OBJ (unrigged) and GLB (with shape keys, rigged with
Mixamo-style bone names, rigged with meaningless names), then cast, and has to wave, walk, carry a cup
and smile like any other character.

    python tests/test_models.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling, models  # noqa: E402

MIXAMO = {"hips": "mixamorig:Hips", "chest": "mixamorig:Spine", "neck": "mixamorig:Neck"}
for _s, _side in (("l", "Left"), ("r", "Right")):
    MIXAMO.update({f"{_s}_arm": f"mixamorig:{_side}Arm", f"{_s}_elbow": f"mixamorig:{_side}ForeArm",
                   f"{_s}_wrist": f"mixamorig:{_side}Hand", f"{_s}_hip": f"mixamorig:{_side}UpLeg",
                   f"{_s}_knee": f"mixamorig:{_side}Leg", f"{_s}_ankle": f"mixamorig:{_side}Foot"})


def _cyl(a, b, r):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=16, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o


def figure():
    """A 1.8-unit person in an A pose, facing -Y, as one mesh."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    parts = [_cyl((s * 0.1, 0, 0), (s * 0.1, 0, 0.85), 0.07) for s in (1, -1)]
    parts.append(_cyl((0, 0, 0.8), (0, 0, 1.45), 0.17))
    parts += [_cyl((s * 0.2, 0, 1.4), (s * 0.6, 0, 0.95), 0.05) for s in (1, -1)]
    parts.append(_cyl((0, 0, 1.44), (0, 0, 1.56), 0.06))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0, 0, 1.66))
    parts.append(bpy.context.object)
    for o in bpy.context.view_layer.objects:
        o.select_set(o in parts)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "person"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    body.shape_key_add(name="Basis")
    for name, dz in (("eyeBlink", -0.01), ("mouthSmile", 0.01)):
        kb = body.shape_key_add(name=name)
        for v in kb.data:
            if v.co.z > 1.6:
                v.co.z += dz
    return body


def save(folder):
    paths = {}
    body = figure()
    paths["obj"] = os.path.join(folder, "plain.obj")
    bpy.ops.wm.obj_export(filepath=paths["obj"], export_materials=False)
    paths["faces"] = os.path.join(folder, "faces.glb")
    bpy.ops.export_scene.gltf(filepath=paths["faces"], export_format="GLB")
    arm = models.auto_rig([body], 1.8)
    bpy.context.view_layer.objects.active = arm
    for b in arm.data.bones:
        b.name = MIXAMO[b.name] if b.name in MIXAMO else f"mixamorig:{b.name}"
    paths["mixamo"] = os.path.join(folder, "mixamo.glb")
    bpy.ops.export_scene.gltf(filepath=paths["mixamo"], export_format="GLB")
    for i, b in enumerate(arm.data.bones):
        b.name = f"bone{i:02d}"
    paths["nameless"] = os.path.join(folder, "nameless.glb")
    bpy.ops.export_scene.gltf(filepath=paths["nameless"], export_format="GLB")
    return paths


def at(s, obj, t):
    handling.evaluate(s, t)
    return obj.matrix_world.translation.copy()


def skin_near(s, c, point, t):
    """How far the model's (deformed) skin is from a point at time t."""
    from mathutils.bvhtree import BVHTree
    handling.evaluate(s, t)
    dg = bpy.context.evaluated_depsgraph_get()
    best = 9.0
    for m in c.meshes:
        tree = BVHTree.FromObject(m, dg)
        mw = m.matrix_world
        hit = tree.find_nearest(mw.inverted() @ point)
        if hit[0] is not None:
            best = min(best, (mw @ hit[0] - point).length)
    return best


def act(path, kind):
    s = dr.Scene({"kind": "room", "props": [{"type": "table", "place": "back", "items": ["cup"]}]})
    hero, mia = s.cast(hero=dict(type="model", file=path, height=1.0), mia={})
    hero.place("center", facing="camera")
    mia.place("right", facing="hero")
    roles = hero.roles
    for r in ("hips", "chest", "neck", "l_arm", "l_elbow", "l_wrist", "r_arm", "r_wrist", "l_hip", "l_knee",
              "l_ankle", "r_hip", "r_ankle"):
        assert r in roles, (kind, "role", r)
    assert roles["l_wrist"] != roles["r_wrist"] and roles["l_ankle"] != roles["r_ankle"], (kind, roles)
    # feet on the floor, the height asked for, standing at its place
    handling.evaluate(s, 0.0)
    dg = bpy.context.evaluated_depsgraph_get()
    zs = [(m.evaluated_get(dg).matrix_world @ v.co).z for m in hero.meshes for v in m.evaluated_get(dg).data.vertices]
    assert abs(min(zs)) < 0.04 and abs(max(zs) - 1.0) < 0.06, (kind, "height", min(zs), max(zs))
    assert 0.78 < hero.head_point(0.0).z < 1.0, (kind, "the face is where the head is", hero.head_point(0.0))
    t0 = s.clock
    hero.do("wave")
    t_wave = t0 + 0.6
    start = at(s, hero.root, s.clock)
    hero.pick_up("cup")
    t_held = s.clock + 0.2
    t_go = s.clock
    hero.walk_to("left")
    t_walk = s.clock - 0.3
    hero.feel("sad")
    t_sad = s.clock + 0.5
    s.wait(0.6)
    hero.feel("happy")
    t_happy = s.clock + 0.5
    s.wait(1)
    s.finish()
    hand = hero.hands[1]
    shoulder = at(s, hero.arms[1], t_wave)
    assert at(s, hand, t_wave).z > shoulder.z - 0.05, (kind, "the waving hand is up", at(s, hand, t_wave), shoulder)
    assert at(s, hand, 0.0).z < shoulder.z - 0.2, (kind, "and down at rest")
    assert skin_near(s, hero, at(s, hand, t_wave), t_wave) < 0.08, (kind, "the skin follows the hand")
    cup = s.set.things["cup"].root
    holding = hero.hands[-1] if (at(s, cup, t_held) - at(s, hero.hands[-1], t_held)).length < 0.1 else hand
    for t in (t_held, t_walk):
        assert (at(s, cup, t) - at(s, holding, t)).length < 0.1, (kind, "the cup is in hand", t)
    assert (at(s, hero.root, t_walk) - start).length > 0.5, (kind, "it walked")
    ankle = hero.rig.pose.bones[roles["l_ankle"]]
    lows = []
    for k in range(24):
        handling.evaluate(s, t_go + (t_walk - t_go) * k / 23)
        lows.append((hero.rig.matrix_world @ ankle.head).z)
    assert min(lows) < 0.12 and max(lows) - min(lows) > 0.03, (kind, "feet step", lows)
    if kind == "faces":
        assert {"blink", "smile"} <= set(hero.face_keys), hero.face_keys
        smile = hero.face_keys["smile"][0]
        handling.evaluate(s, t_sad)
        before = smile.value
        handling.evaluate(s, t_happy)
        assert smile.value > before + 0.3, ("smiles when happy, not when sad", before, smile.value)
        for kb in hero.face_keys["blink"] + hero.face_keys["smile"]:
            fc = kb.id_data.animation_data.drivers.find(f'key_blocks["{kb.name}"].value')
            assert fc.driver.is_simple_expression, fc.driver.expression
    print(f"  {kind}: ok ({len(roles)} roles)")


def main():
    with tempfile.TemporaryDirectory() as folder:
        paths = save(folder)
        for kind in ("obj", "faces", "mixamo", "nameless"):
            act(paths[kind], kind)
        s = dr.Scene({"kind": "room"})
        try:
            s.cast(bad=dict(type="model"))
        except ValueError as e:
            assert "file" in str(e)
        else:
            raise AssertionError("a model needs a file")
    print("models: all ok")


if __name__ == "__main__":
    main()
