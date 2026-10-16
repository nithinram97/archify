"""The `dreamreel` command.

    dreamreel new my-film            start a project (add --example for a finished short to learn from)
    dreamreel check                  build every scene and print its timeline (fast, no rendering)
    dreamreel cast                   picture of every cast member
    dreamreel plan kitchen           top-down map of a set with all its marks
    dreamreel still 010 2.5 6        render frames of scene 010 at 2.5 s and 6 s
    dreamreel contact 010            6 frames of a scene on one sheet
    dreamreel previz                 fast flat-shaded video of the whole film
    dreamreel render                 the final film (only changed scenes are re-rendered)
"""
import argparse
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _project():
    from . import project
    p = project.find(os.getcwd())
    if p is None:
        raise SystemExit("not inside a dreamreel project (no film.toml here or above). Run `dreamreel new my-film`.")
    project.activate(p)
    return p


def cmd_new(a):
    src = os.path.join(HERE, "templates", "example" if a.example else "blank")
    if os.path.exists(a.dir) and os.listdir(a.dir):
        raise SystemExit(f"{a.dir} already exists and isn't empty")
    shutil.copytree(src, a.dir, dirs_exist_ok=True)
    for f in ("AGENTS.md", "REFERENCE.md"):  # so any AI coding agent opened here knows how to direct
        shutil.copy(os.path.join(HERE, "templates", f), os.path.join(a.dir, f))
    with open(os.path.join(a.dir, "CLAUDE.md"), "w") as fh:
        fh.write("@AGENTS.md\n")
    with open(os.path.join(a.dir, ".gitignore"), "w") as fh:
        fh.write("renders/\naudio/voices/\n")
    for sub in ("audio/music", "audio/sfx", "renders"):
        os.makedirs(os.path.join(a.dir, sub), exist_ok=True)
    print(f"Created {a.dir}. Next:\n  cd {a.dir}\n  dreamreel check\n  dreamreel contact 010\n"
          f"Or open the folder in an AI coding agent (Claude Code, Codex, ...) and describe your film: "
          f"AGENTS.md tells it how to direct.")


def cmd_check(a):
    from . import film
    p = _project()
    paths = [p.scene_path(a.scene)] if a.scene else p.scenes()
    total = 0.0
    for path in paths:
        s = film.build(p, path)
        print(s.summary())
        total += s.length + sum(c[1] for c in s.cards)
        print()
    print(f"{p.title}: {len(paths)} scene(s), {total:.1f} s")
    for extra in p.unlisted() if not a.scene else []:
        print(f"note: {os.path.basename(extra)} is not in film.toml's scenes list, so it isn't in the film")


def cmd_still(a):
    from . import film
    p = _project()
    _, paths = film.still(p, p.scene_path(a.scene), [float(t) for t in a.times], a.percent,
                          "previz" if a.previz else "final")
    for x in paths:
        print(x)


def cmd_contact(a):
    from . import film
    p = _project()
    s, dest, times = film.contact_sheet(p, p.scene_path(a.scene), a.count, a.percent, "previz" if a.previz else "final")
    print(f"{dest}\nframes at: {', '.join(f'{t:g}s' for t in times)}")


def cmd_cast(a):
    import bpy
    from . import _compat, scene as scene_mod
    p = _project()
    names = a.names or p.cast_names()
    s = scene_mod.Scene({"kind": "room", "size": "small", "walls": "#e9e4dc", "floor": "carpet"})
    actors = s.cast(*names)
    actors = actors if isinstance(actors, list) else [actors]
    n = len(actors)
    for i, c in enumerate(actors):
        c.place((-(n - 1) * 0.55 + i * 1.1, -0.6), facing="camera")
    lens = 40
    width = n * 1.1 + 0.6
    d = s.cut._dist_for_width(width, lens)
    s.cut._add("cast", 0.0, actors, (0, -0.6 - d, 0.75), (0, -0.6, 0.5), lens, 8.0, "cast")
    s.cut.manual = True
    s.finish()
    r = s.bscene.render
    r.resolution_percentage = a.percent
    _compat.set_image_output(r)
    s.bscene.frame_set(1)
    r.filepath = p.renders("stills", "cast.png")
    bpy.ops.render.render(write_still=True)
    print(r.filepath)


def cmd_plan(a):
    import bpy
    from . import _compat, look, scene as scene_mod, shapes
    p = _project()
    s = scene_mod.Scene(a.set)
    st = s.set
    for name, m in st.marks.items():
        shapes.cylinder("mark", 0.09, 0.02, look.plastic("red", emission=0.5), at=(m.at.x, m.at.y, 2.5), bevel=0)
        if m.facing is not None:
            shapes.box("mark.dir", 0.03, 0.18, 0.02, "red", at=(m.at.x + math.sin(m.facing) * 0.12,
                       m.at.y - math.cos(m.facing) * 0.12, 2.5), rot=(0, 0, m.facing), bevel=0)
        txt = bpy.data.curves.new("label", "FONT")
        txt.body = name
        txt.size = 0.16
        txt.align_x = "CENTER"
        ob = bpy.data.objects.new("label", txt)
        s.bscene.collection.objects.link(ob)
        ob.location = (m.at.x, m.at.y - 0.25, 2.52)
        ob.data.materials.append(look.plastic("black"))
    for w in getattr(st, "walls", []):
        w.hide_render = True
    cam = s.cut.cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(st.width, st.depth * 16 / 9) + 1.0
    cam.data.dof.use_dof = False
    cam.constraints.clear()
    cam.location = (0, 0, 12)
    cam.rotation_euler = (0, 0, 0)
    s.cut.manual = True
    s.cut.shots = []
    s.cut.build = lambda: None
    s.finish()
    s.previz_settings()
    s.bscene.display.shading.show_shadows = False
    r = s.bscene.render
    r.resolution_percentage = 50
    _compat.set_image_output(r)
    r.filepath = p.renders("stills", f"plan_{a.set}.png")
    bpy.ops.render.render(write_still=True)
    print(r.filepath)
    print("marks:", ", ".join(sorted(st.marks)))
    if st.seats:
        print("seats:", ", ".join(sorted(st.seats)))


def _render_all(a, quality):
    from . import film
    p = _project()
    paths = [p.scene_path(a.scene)] if a.scene else p.scenes()
    metas = [film.render_scene(p, path, quality, a.percent, a.force) for path in paths]
    out = film.assemble(p, metas, quality)
    print(f"[dreamreel] film: {out}")


def cmd_previz(a):
    _render_all(a, "previz")


def cmd_render(a):
    _render_all(a, "final")


def cmd_voices(a):
    from . import voices
    print("Voices come from Piper (free, offline). Install it with:  pip install piper-tts")
    print("Browse voices at https://rhasspy.github.io/piper-samples/ and put the name in a cast file:")
    print('  voice = "en_US-amy-medium"')
    print(f"Default voice: {voices.DEFAULT_VOICE}. Engine available now: {voices._piper_available()}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dreamreel", description="Make animated films by writing what happens.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="start a new film project")
    n.add_argument("dir")
    n.add_argument("--example", action="store_true", help="start from the example short film")
    n.set_defaults(fn=cmd_new)

    c = sub.add_parser("check", help="build scenes and print their timelines")
    c.add_argument("scene", nargs="?")
    c.set_defaults(fn=cmd_check)

    st = sub.add_parser("still", help="render frames of a scene")
    st.add_argument("scene")
    st.add_argument("times", nargs="+")
    st.add_argument("--percent", type=int, default=50)
    st.add_argument("--previz", action="store_true")
    st.set_defaults(fn=cmd_still)

    cs = sub.add_parser("contact", help="a sheet of frames from one scene")
    cs.add_argument("scene")
    cs.add_argument("--count", type=int, default=6)
    cs.add_argument("--percent", type=int, default=25)
    cs.add_argument("--previz", action="store_true")
    cs.set_defaults(fn=cmd_contact)

    ca = sub.add_parser("cast", help="picture of the cast")
    ca.add_argument("names", nargs="*")
    ca.add_argument("--percent", type=int, default=50)
    ca.set_defaults(fn=cmd_cast)

    pl = sub.add_parser("plan", help="top-down map of a set and its marks")
    pl.add_argument("set")
    pl.set_defaults(fn=cmd_plan)

    for name, fn, help_ in (("previz", cmd_previz, "fast flat-shaded film"), ("render", cmd_render, "final film")):
        r = sub.add_parser(name, help=help_)
        r.add_argument("scene", nargs="?")
        r.add_argument("--percent", type=int)
        r.add_argument("--force", action="store_true", help="re-render even unchanged scenes")
        r.set_defaults(fn=fn)

    v = sub.add_parser("voices", help="how to give characters voices")
    v.set_defaults(fn=cmd_voices)

    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main(sys.argv[1:])
