"""Visual styles: every style builds; cel styles shade flat, outlined styles get outlines, clay and
paper animate on twos and threes; a film's style and a scene's own style both apply.

    python tests/test_styles.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import cli, project, timewarp  # noqa: E402


def build(style, set_spec=None, **kw):
    s = dr.Scene(set_spec or {"kind": "room", "props": [{"type": "table"}, {"type": "window"}]}, style=style, **kw)
    mia = s.cast(mia={})
    dog = s.cast(dog={"type": "creature", "body": "quadruped"})
    mia.place("left")
    dog.place("right")
    mia.walk_to("center")
    s.wait(1)
    s.finish()
    return s


def main():
    assert set(dr.names("style")) >= {"toy", "toon", "anime", "clay", "paper", "storybook", "noir", "realistic"}
    for name, cls in dr.registry("style").items():
        s = build(name)
        assert s.style.name == name
        outlined = [o for o in bpy.data.objects if any(m.name == "outline" for m in o.modifiers)]
        if cls.outline > 0:
            assert len(outlined) > 10, (name, len(outlined))
            assert not any(o.name.startswith(("ground", "floor", "fx.")) for o in outlined)
        else:
            assert not outlined, name
        cel = [m for m in bpy.data.materials if m.node_tree and any(n.bl_idname == "ShaderNodeShaderToRGB" for n in m.node_tree.nodes)]
        assert bool(cel) == bool(cls.bands), name
        stepped = [fc for fc in timewarp.all_fcurves() if any(m.type == "STEPPED" for m in fc.modifiers)]
        if cls.steps > 1:
            assert stepped and all(m.frame_step == cls.steps for fc in stepped for m in fc.modifiers
                                   if m.type == "STEPPED"), name
        else:
            assert not stepped, name
        if name == "noir":
            assert s.bscene.view_settings.look == "AgX - Greyscale"
            assert s.environment.light.fill < 0.5
    # lamps and windows keep glowing in a cel style; night stays darker than day
    build("toon", time_of_day="day")
    glow = [m for m in bpy.data.materials if m.node_tree and any(n.bl_idname == "ShaderNodeShaderToRGB" for n in m.node_tree.nodes)]
    strength_day = next(n for n in glow[0].node_tree.nodes if n.type == "EMISSION").inputs["Strength"].default_value
    night = build("toon", time_of_day="night")
    glow = [m for m in bpy.data.materials if m.node_tree and any(n.bl_idname == "ShaderNodeShaderToRGB" for n in m.node_tree.nodes)]
    strength_night = next(n for n in glow[0].node_tree.nodes if n.type == "EMISSION").inputs["Strength"].default_value
    assert strength_night < strength_day, (strength_night, strength_day)
    sky = [m for m, kind, _ in night.set.glows if kind == "sky"][0]
    assert not any(n.bl_idname == "ShaderNodeShaderToRGB" for n in sky.node_tree.nodes), "windows still glow"
    # outdoors and in a street too
    build("anime", {"kind": "outdoor", "biome": "forest", "density": 0.3}, weather="rain")
    build("storybook", {"kind": "street"})
    # the previz shows outlines
    s = build("toon")
    s.previz_settings()
    assert s.bscene.display.shading.show_backface_culling

    # a film's style, and a scene of its own
    tmp = tempfile.mkdtemp(prefix="dreamreel-style-")
    try:
        film = os.path.join(tmp, "film")
        cli.main(["new", film])
        with open(os.path.join(film, "film.toml"), "a") as f:
            f.write('\nstyle = "clay"\n')
        from dreamreel import film as film_mod
        p = project.Project(film)
        scene_file = p.scenes()[0]
        s = film_mod.build(p, scene_file)
        assert s.style.name == "clay", s.style.name
        with open(scene_file) as f:
            text = f.read()
        with open(scene_file, "w") as f:
            f.write('style = "noir"\n' + text)
        s = film_mod.build(p, scene_file)
        assert s.style.name == "noir" and s.metadata()["style"] == "noir"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("styles: ok")


if __name__ == "__main__":
    main()
