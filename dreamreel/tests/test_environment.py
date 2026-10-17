"""Environments: every time of day, weather, biome, scenery, street and furnished room builds; the
acting area stays flat and clear; weather moves; the camera sees through rain.

    python tests/test_environment.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import keys, sets  # noqa: E402


def scene(spec, **kw):
    s = dr.Scene(spec, **kw)
    mia = s.cast(mia={})
    mia.place("center", facing="camera")
    s.wait(2)
    s.finish()
    return s, mia


def main():
    # every time of day and weather, outdoors and in a room
    for tod in dr.names("time"):
        for spec in ({"kind": "outdoor", "density": 0.2}, {"kind": "room", "props": [{"type": "window"}]}):
            s, _ = scene(spec, time_of_day=tod)
            assert s.environment.light.sun_energy > 0, tod
    for w in dr.names("weather"):
        s, _ = scene({"kind": "outdoor", "density": 0.2}, weather=w)
        names = {o.name.split(".")[0] + "." + o.name.split(".")[1] if o.name.startswith("fx.") else "" for o in
                 bpy.data.objects}
        if w in ("rain", "storm"):
            assert "fx.rain" in names, w
        if w == "snow":
            assert "fx.snow" in names
        if w == "fog":
            fog = bpy.data.objects["fx.fog"]
            assert fog.get("dr_final_only")
            s.previz_settings()
            assert fog.hide_render, "fog is left out of the fast previz"
        scene({"kind": "room"}, weather=w)        # indoors: just the light changes
    # night is dark and lamps matter; a window shows the sky's colour
    s, _ = scene({"kind": "room", "props": [{"type": "window"}, {"type": "lamp"}]}, time_of_day="night")
    assert s.environment.light.dark
    mat, kind, _ = s.set.glows[0]
    assert kind == "sky"
    sky = mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
    assert sky[2] > sky[0], "the night sky in the window is blue"

    # rain falls, loops and the camera looks straight through it
    s, mia = scene({"kind": "outdoor", "density": 0.3}, weather="storm")
    rain = bpy.data.objects["fx.rain"]
    zs = []
    for t in (0.0, 0.25, 0.5):
        s.bscene.frame_set(keys.CLOCK.frame(t))
        zs.append(rain.location.z)
    assert zs[0] > zs[1] > zs[2], zs
    energies = set()
    for f in range(1, keys.CLOCK.frame(s.length)):
        s.bscene.frame_set(f)
        energies.add(round(s.environment.sun.data.energy, 2))
    assert max(energies) > 5 * min(energies), "lightning flashes"
    assert s.cut.clear_view(Vector((0, -6, 1.2)), mia.head_point(1.0)), "rain doesn't block the camera"
    assert len(s.set.sway) > 5, "trees move in the wind"

    # every biome: flat, clear acting area, scenery round it
    for b in dr.names("biome"):
        s, mia = scene({"kind": "outdoor", "biome": b})
        for place in sets.ZONES:
            p = s.set.zone(place)
            assert abs(s.set.ground_height(p.x, p.y)) < 1e-6, (b, place)
        W, D = s.set.width, s.set.depth
        for cx, cy, hw, hd in s.set.obstacles:
            assert not (abs(cx) < W / 2 - 0.5 and abs(cy) < D / 2 - 0.5), (b, "scenery in the acting area")
        assert len(bpy.data.objects) > 60, b
        mia.walk_to("left")      # people can still get about
    # every scenery kind, as a prop
    for k in dr.names("scenery"):
        scene({"kind": "outdoor", "density": 0, "props": [{"type": "tree", "variety": k, "place": "back-left"}]})

    # a street, in each style, with its marks
    for style in ("town", "city", "old_town"):
        s, mia = scene({"kind": "street", "style": style}, time_of_day="night")
        for m in ("door", "crossing", "kerb", "lamp", "across"):
            assert m in s.set.marks, (style, m)
        lit = [g for g in s.set.glows if g[1] == "lit"]
        assert lit and any(g[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value > 0
                           for g in lit), "some windows are lit at night"
        mia.walk_to("door")

    # furnished rooms: every type builds, your own props win, places aren't doubled up
    for kind in sets.FURNISH:
        for size in ("small", "large"):
            s, mia = scene({"kind": "room", "furnish": kind, "size": size})
            assert len(s.set.props) >= 4, (kind, s.set.props)
    props = sets.furnish("kitchen", [{"type": "sofa", "place": "center"}, {"type": "door", "place": "back-right"}])
    assert sum(p["type"] == "door" for p in props) == 1
    assert not any(p["type"] == "table" for p in props), "the table's place was taken by your sofa"
    floor = [p["place"] for p in props if not getattr(dr.get("prop", p["type"]), "wall", False)]
    assert len(floor) == len(set(floor)), floor
    # a lab, with a tiled ceiling and strip lights; the camera stays under the ceiling
    s, mia = scene({"kind": "room", "furnish": "lab", "size": "large"})
    assert s.set.ceiling_h and s.set.panels
    assert any(o.name.startswith("strip light") for o in bpy.data.objects)
    assert {"lab_bench", "shelves", "blackboard"} <= {p.split("-")[0] for p in s.set.props}
    assert "tray" in s.set.marks and "tray" in s.set.surfaces
    frog = s.cast(frog=dict(type="creature", body="frog", size=0.4))
    frog.place("tray", on="tray")
    assert abs(frog.root.location.z - s.set.surfaces["tray"][2]) < 1e-6
    assert all(abs(t.location.z - s.set.surfaces["tray"][2]) < 0.05 for t in frog.feet.values()), "feet on the tray"
    s.cut.shot("establishing", at=0.0, angle="high")
    s.cut.build()
    for sh in s.cut.final:
        assert sh.state.pos.z < s.set.ceiling_h, sh.label
    s, mia = scene({"kind": "room", "furnish": "bedroom"})
    assert "bed" in s.set.seats and "desk-chair" in s.set.seats
    mia.sit("bed")
    print("environment: ok")


if __name__ == "__main__":
    main()
