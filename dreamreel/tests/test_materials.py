"""Real materials (materials.py): surfaces are recognised for what they're made of, made real in the
realistic look (pinned to their objects, keeping the film's colours), and the look still works
offline with procedural surfaces.

    python tests/test_materials.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import look, materials  # noqa: E402


def thing(obj_name, mat_name, color="#808080"):
    me = bpy.data.meshes.new(obj_name)
    me.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    o = bpy.data.objects.new(obj_name, me)
    bpy.context.scene.collection.objects.link(o)
    m = bpy.data.materials.new(mat_name)
    m.use_nodes = True
    next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = \
        (*look.rgb(color), 1)
    me.materials.append(m)
    return o, m


def classify():
    cases = [
        (("floor", "plastic wood"), None, "wood_floor"),
        (("wall.back", "plastic mint"), None, "plaster"),
        (("tree.003", "Bark_NormalTree.002"), None, "bark"),
        (("tree.003", "Leaves_NormalTree"), None, "leaves"),
        (("building1.2", "MI_RedBrick_Pale"), None, "brick_pale"),
        (("ground.road", "plastic #47474c"), None, "asphalt"),
        (("cup", "plastic teal"), None, "porcelain"),
        (("counter.unit", "KitchenTop.001"), None, "granite"),
        (("streetlamp.bulb", "plastic #fff1c4"), None, None),
        (("car2", "Yellow"), "car", "car_paint"),
        (("car2", "Windows"), "car", "glass"),
        (("Casual_Legs", "LightBlue", "#6fa8dc"), "Person", "denim"),
        (("Casual_Body", "Purple", "#7b5ea7"), "Person", "cotton"),
        (("Casual_Head", "Hair_Brown"), "Person", "hair"),
        (("Casual_Head", "Skin"), "Person", "skin"),
        (("Casual_Head", "Brown", "#5a3825"), "Person", "cotton"),
        (("ShibaInu", "Main", "#c98b4f"), "Animal", "fur"),
        (("ShibaInu", "Eyes_Black"), "Animal", "eye"),
        (("Mia.white", "plastic #f7f4ee"), "ToyFigure", "eye"),
        (("Mia.glint", "plastic white"), "ToyFigure", None),
    ]
    for args, owner, want in cases:
        o, m = thing(*args)
        got = materials.classify(o, m, owner)
        assert got == want, (args, owner, got, want)
    o, m = thing("crate", "Mystery")
    m["dr_material"] = "wicker"
    assert materials.classify(o, m) == "wicker", "a film can say what something is made of"
    print("  classify: ok")


def scene():
    s = dr.Scene({"kind": "room", "props": [{"type": "table", "place": "back", "items": ["cup", "plate"]}]})
    mia = s.cast(mia={})
    mia.place("center", facing="camera")
    s.wait(1)
    cup = next(o for o in bpy.data.objects if o.name.startswith("cup"))
    teal = tuple(cup.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)[:3]
    made = materials.realise_scene(s)
    assert made >= 5, made
    real = {sl.material.get("dr_kind") for o in bpy.data.objects if o.type == "MESH"
            for sl in o.material_slots if sl.material and sl.material.get("dr_real")}
    assert {"wood_floor", "plaster", "porcelain", "skin"} <= real, real
    assert "dr_rest" in cup.data.attributes, "patterns are pinned to the object"
    m = cup.material_slots[0].material
    rgb = next((n for n in m.node_tree.nodes if n.type == "RGB"), None)
    assert rgb is not None and tuple(rgb.outputs[0].default_value)[:3] == teal, "the film's colour is kept"
    # a second pass changes nothing (materials are made real once)
    assert materials.realise_scene(s) == 0
    print(f"  scene: ok ({made} materials made real: {sorted(real)})")


def offline():
    saved = materials.CACHE
    materials.CACHE = os.path.join(saved, "__nowhere__")
    try:
        o, m = thing("table.top", "Wood")
        assert materials.realise(m, "wood", download=False), "offline, a procedural surface stands in"
        assert m.get("dr_kind") == "wood"
        assert materials.fetch(("acg", "Wood049"), download=False) is None
    finally:
        materials.CACHE = saved
    print("  offline: ok")


def look_realistic():
    s = dr.Scene({"kind": "room"}, style="realistic")
    s.cast(mia={}).place("center", facing="camera")
    s.wait(1)
    s.finish()
    n = sum(1 for m in bpy.data.materials if m.get("dr_real") and m.users)
    assert n >= 3, n
    print(f"  realistic look: ok ({n} real materials in use)")


def main():
    classify()
    offline()
    scene()
    look_realistic()
    print("materials: all ok")


if __name__ == "__main__":
    main()
