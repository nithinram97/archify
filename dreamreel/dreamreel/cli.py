"""The `dreamreel` command.

    dreamreel new my-film            start a project (add --example for a finished short to learn from)
    dreamreel check                  build every scene and print its timeline (fast, no rendering)
    dreamreel cast                   picture of every cast member
    dreamreel plan kitchen           top-down map of a set with all its marks
    dreamreel still 010 2.5 6        render frames of scene 010 at 2.5 s and 6 s
    dreamreel contact 010            6 frames of a scene on one sheet
    dreamreel previz                 fast flat-shaded video of the whole film
    dreamreel render                 the final film (only changed scenes are re-rendered)
    dreamreel studio                 the same, in a friendly app in your browser
    dreamreel plugins                every feature you can use (built-in and from extensions/)
    dreamreel extend prop cake       start a new feature as a class in extensions/
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
    for sub in ("audio/music", "audio/sfx", "renders", "extensions"):
        os.makedirs(os.path.join(a.dir, sub), exist_ok=True)
    print(f"Created {a.dir}. Next:\n  cd {a.dir}\n  dreamreel check\n  dreamreel contact 010\n"
          f"Or open the folder in an AI coding agent (Claude Code, Codex, ...) and describe your film: "
          f"AGENTS.md tells it how to direct.")


def cmd_check(a):
    from . import film
    p = _project()
    paths = [p.scene_path(a.scene)] if a.scene else p.scenes()
    if a.json:
        import json
        out = []
        for path in paths:
            try:
                s = film.build(p, path)
                out.append({"scene": s.name, **s.timeline()})
            except BaseException as e:  # report the error for this scene and carry on
                import traceback
                from .scene import BeatError
                if isinstance(e, BeatError):
                    out.append({"scene": os.path.splitext(os.path.basename(path))[0], "beat": e.beat,
                                "error": str(e)})
                    continue
                line = getattr(e, "lineno", None) if isinstance(e, SyntaxError) else None
                for fr in traceback.extract_tb(e.__traceback__):
                    if os.path.abspath(fr.filename) == os.path.abspath(path):
                        line = fr.lineno
                msg = str(e) if not isinstance(e, SystemExit) else str(e.code)
                out.append({"scene": os.path.splitext(os.path.basename(path))[0], "line": line,
                            "error": f"{type(e).__name__}: {msg}"})
        print("@@JSON " + json.dumps(out))
        return
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
    r.filepath = a.out or p.renders("stills", "cast.png" if not a.names else f"cast_{'_'.join(a.names)}.png")
    bpy.ops.render.render(write_still=True)
    print(r.filepath)


def cmd_plan(a):
    import bpy
    from . import _compat, look, scene as scene_mod, shapes
    p = _project()
    s = scene_mod.Scene(a.set)
    st = s.set
    if a.view:  # how the set looks through the camera, empty
        s.cut.wide(at=0)
        s.finish()
        r = s.bscene.render
        r.resolution_percentage = a.percent
        _compat.set_image_output(r)
        r.filepath = p.renders("stills", f"view_{a.set}.png")
        bpy.ops.render.render(write_still=True)
        print(r.filepath)
        return
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


def cmd_studio(a):
    from .studio import server
    server.serve(a.dir, a.port, open_browser=not a.no_browser)


def cmd_info(a):
    """Everything a tool needs to offer valid choices: every plugin with its settings, the colours,
    and each set's marks and seats."""
    import json
    from . import look, plugins, scene as scene_mod, sets, voices
    from .sets import ZONES
    p = _project()
    info = {
        "plugins": plugins.describe_all(),
        "catalog": {
            "places": [z for z in ZONES if z != "centre"], "colors": look.COLORS,
            "voices": list(voices.SUGGESTED), "voice_engine": voices.pick_engine() is not None,
        },
        "sets": {},
    }
    for name in p.set_names():
        try:
            scene_mod._reset_blender()
            st = sets.Set.create(p.set_spec(name), name=name)
            info["sets"][name] = {"kind": st.kind, "marks": sorted(st.marks), "seats": sorted(st.seats),
                                  "props": sorted(st.props)}
        except Exception as e:
            info["sets"][name] = {"error": f"{type(e).__name__}: {e}", "marks": [], "seats": []}
    print("@@JSON " + json.dumps(info))


def cmd_plugins(a):
    """List every feature (built-in and from extensions) with its settings."""
    from . import plugins
    _project_optional()
    for kind in [a.kind] if a.kind else plugins.kinds():
        print(f"\n{kind}")
        for cls in plugins.registry(kind).values():
            d = cls.describe()
            src = "" if d["source"] == "built-in" else f"   [{d['source']}]"
            print(f"  {d['name']:<16} {d['description']}{src}")
            if a.verbose:
                for prm in d["params"]:
                    extra = f" one of {prm['choices']}" if prm.get("choices") else ""
                    dflt = f" = {prm['default']!r}" if "default" in prm else ""
                    print(f"      {prm['name']} ({prm['type']}){dflt}{extra}")


EXTEND_TEMPLATES = {
    "character": ('''class {cls}(dr.Character):
    """{desc}"""
    description = "{desc}"
    params = dr.Character.params + [Param("accent", "color", default="gold")]

    # Override any build step: build_rig, build_legs, build_body, build_arms, build_head, build_face,
    # build_hair, build_extras. Keep the attributes later steps and animation use (see character.py).
    def build_extras(self):
        super().build_extras()
        shapes.sphere(f"{{self.name}}.badge", 0.03 * self.H, self.color("accent"), self.body,
                      at=(0.08 * self.H, -self.body_r * 0.9, self.neck_z - 0.15 * self.H))
''', 'type = "{name}" in a cast file'),
    "body": ('''class {cls}(dr.BodyPlan):
    """{desc}"""
    description = "{desc}"
    capabilities = {{"walk", "tail"}}

    def skeleton(self, c):
        # joints (name, (x, y, z), radius, parent) become a smooth skinned body; facing -Y, feet at z = 0
        S = c.size
        k = dr.Skeleton()
        k.joint("pelvis", (0, 0.2 * S, 0.45 * S), 0.15 * S)
        k.joint("chest", (0, -0.2 * S, 0.5 * S), 0.16 * S, "pelvis")
        k.joint("neck", (0, -0.35 * S, 0.75 * S), 0.07 * S, "chest")
        k.head, k.head_r = "neck", 0.14 * S               # the head (with its face) sits on this joint
        for name, y, parent in (("LF", -0.2, "chest"), ("RF", -0.2, "chest"), ("LH", 0.2, "pelvis"), ("RH", 0.2, "pelvis")):
            x = (0.1 if name[0] == "L" else -0.1) * S
            k.joint(f"hip.{{name}}", (x, y * S, 0.4 * S), 0.07 * S, parent)
            k.joint(f"knee.{{name}}", (x, y * S, 0.22 * S), 0.05 * S, f"hip.{{name}}")
            k.joint(f"foot.{{name}}", (x, y * S, 0.05 * S), 0.05 * S, f"knee.{{name}}")
            k.leg(f"leg.{{name}}", f"hip.{{name}}", f"knee.{{name}}", f"foot.{{name}}")
        return k
''', 'type = "creature", body = "{name}" in a cast file'),
    "extra": ('''class {cls}(dr.Extra):
    """{desc}"""
    description = "{desc}"

    def build(self, c):
        # c.neck: parent for things on the head; c.body: on the torso; c.hc / c.hr: head centre / radius
        shapes.cylinder(f"{{c.name}}.{name}", c.hr * 0.6, c.hr * 0.4, "gold", c.neck, at=c.head_top())
''', 'extras = ["{name}"] in a cast file'),
    "hair": ('''class {cls}(dr.Hair):
    """{desc}"""
    description = "{desc}"

    def build(self, c, color):
        self.cap(c, color)                      # the basic cap, then add shapes on c.neck
        shapes.sphere(f"{{c.name}}.hair", c.hr * 0.5, color, c.neck, at=c.head_top())
''', 'hair = "{name}" in a cast file'),
    "mood": ('''class {cls}(dr.Mood):
    """{desc}"""
    description = "{desc}"
    brow_tilt = 12      # degrees; + raises the inner ends, - lowers them
    brow_lift = 0.01
    smile = 0.0
    frown = 0.2
    eyes = 1.0
    mouth_open = 0.0
    head_tilt = 8
''', 'mood = "{name}" on a say or feel beat'),
    "gesture": ('''class {cls}(dr.Gesture):
    """{desc}"""
    description = "{desc}"

    def perform(self, c, t, target=None):
        # pose helpers: c.arm_to(side, t, rot), c.arms_rest(t), c.arms_up_at(t), c.nod_at(t), c.tilt_head_at(t),
        # c.hop_at(t, height, t_up, t_down), c.jump_at(t), c.lean_at(t, side_deg, forward_deg)
        c.arms_up_at(t + 0.3)
        c.hop_at(t, 0.05, 0.3, 0.7)
        c.arms_rest(t + 1.2)
        return t + 1.2                          # when it ends
''', 'do = "gesture", gesture = "{name}" in a beat'),
    "action": ('''class {cls}(dr.Action):
    """{desc}"""
    label = "{label}"
    description = "{desc}"
    sentence = "{{who}} {label} {{whom}}"
    params = [Param("whom", "character", required=True, label="Who")]

    def run(self, s, who, whom):
        who.walk_to(whom)
        who.do("wave", target=whom)
''', 'do = "{name}" in a beat'),
    "prop": ('''class {cls}(dr.Prop):
    """{desc}"""
    description = "{desc}"
    default_place = "center"
    params = dr.Prop.params + [Param("color", "color", default="red")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.5, 0.5, self.default_place)
        shapes.box(name, 0.5, 0.5, 0.6, p.get("color", "red"), at=(pos.x, pos.y, 0))
        s.block(pos, 0.5, 0.5)                              # characters walk round it
        s.add_mark(name, (pos.x, pos.y - 0.6), facing="back")  # a spot in front of it
''', '[[props]] type = "{name}" in a set file'),
    "set": ('''class {cls}(dr.Set):
    """{desc}"""
    description = "{desc}"
    size = (6.0, 4.0)
    params = [Param("floor_color", "color", default="#c9ccd1")]

    def build_environment(self):
        W, D = self.width, self.depth
        shapes.box("floor", W + 0.4, D + 0.4, 0.1, self.spec["floor_color"], at=(0, 0, -0.1), bevel=0)
''', 'kind = "{name}" in a set file'),
    "shot": ('''class {cls}(dr.ShotType):
    """{desc}"""
    description = "{desc}"
    subjects = 1

    def frame(self, d, t, of=None, other=None):
        c = d.character(of)
        head = c.head_point(t)
        f = c.forward(t)
        pos = (head.x + f.x * 1.6, head.y + f.y * 1.6, 0.25)   # low, in front, looking up
        return d.add(self.name, t, [c], pos, head, lens=24, fstop=4.0, label=f"{name}({{c.name}})")
''', 'do = "shot", shot = "{name}" in a beat'),
    "voice": ('''class {cls}(dr.VoiceEngine):
    """{desc}"""
    description = "{desc}"

    @classmethod
    def available(cls):
        return True

    def speak(self, text, voice, wav_path):
        raise NotImplementedError("write a 16-bit WAV file of `text` to wav_path")
''', 'voice_engine = "{name}" in film.toml'),
}


def cmd_extend(a):
    """Write a starting point for a new class in the film's extensions/ folder."""
    import re as _re
    p = _project()
    name = _re.sub(r"[^a-z0-9_-]", "", a.name.lower().replace(" ", "_"))
    if not name:
        raise SystemExit("give the new thing a name, e.g. dreamreel extend prop cake")
    body, usage = EXTEND_TEMPLATES[a.kind]
    cls = "".join(w.capitalize() for w in _re.split(r"[_-]", name))
    desc = a.description or f"A new {a.kind}: {name.replace('_', ' ')}"
    path = os.path.join(p.root, "extensions", f"{name}.py")
    if os.path.exists(path):
        raise SystemExit(f"{os.path.relpath(path, p.root)} already exists")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    head = (f'"""{desc}\n\nUse it with: {usage.format(name=name)}\n"""\n'
            "import math\n\nfrom mathutils import Vector\n\nimport dreamreel as dr\n"
            "from dreamreel import look, shapes\nfrom dreamreel.plugins import Param\n\n\n")
    code = body.format(cls=cls, name=name, desc=desc, label=name.replace("_", " "))
    first, rest = code.split("\n", 1)
    with open(path, "w") as f:
        f.write(head + first + f'\n    name = "{name}"\n' + rest)
    print(f"{os.path.relpath(path, p.root)}: a {a.kind} called {name!r}. Use it with: {usage.format(name=name)}")


def _project_optional():
    from . import project
    pr = project.find(os.getcwd())
    if pr is not None:
        project.activate(pr)
    return pr


def cmd_voices(a):
    from . import voices
    if a.say:
        v = a.voice or voices.DEFAULT_VOICE
        p = _project()
        out = p.renders("voices", f"{v}.wav")
        if not voices._piper_available():
            raise SystemExit("voices need Piper: pip install piper-tts")
        voices._piper(a.say, v, out)
        print(out)
        return
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
    c.add_argument("--json", action="store_true", help="machine-readable output (for tools and the studio)")
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
    ca.add_argument("--out")
    ca.set_defaults(fn=cmd_cast)

    pl = sub.add_parser("plan", help="top-down map of a set and its marks")
    pl.add_argument("set")
    pl.add_argument("--view", action="store_true", help="render the empty set through the camera instead")
    pl.add_argument("--percent", type=int, default=35)
    pl.set_defaults(fn=cmd_plan)

    for name, fn, help_ in (("previz", cmd_previz, "fast flat-shaded film"), ("render", cmd_render, "final film")):
        r = sub.add_parser(name, help=help_)
        r.add_argument("scene", nargs="?")
        r.add_argument("--percent", type=int)
        r.add_argument("--force", action="store_true", help="re-render even unchanged scenes")
        r.set_defaults(fn=fn)

    v = sub.add_parser("voices", help="how to give characters voices")
    v.add_argument("--say", help="speak this text with --voice into renders/voices/ (to audition a voice)")
    v.add_argument("--voice")
    v.set_defaults(fn=cmd_voices)

    i = sub.add_parser("info", help="every feature and set mark as JSON (for tools)")
    i.set_defaults(fn=cmd_info)

    pg = sub.add_parser("plugins", help="list every feature: characters, props, gestures, actions, shots...")
    pg.add_argument("kind", nargs="?")
    pg.add_argument("-v", "--verbose", action="store_true", help="show each one's settings")
    pg.set_defaults(fn=cmd_plugins)

    ex = sub.add_parser("extend", help="start a new class in extensions/ (a new prop, gesture, character...)")
    ex.add_argument("kind", choices=sorted(EXTEND_TEMPLATES))
    ex.add_argument("name")
    ex.add_argument("--description", "-d")
    ex.set_defaults(fn=cmd_extend)

    sd = sub.add_parser("studio", help="open dreamreel studio in your browser")
    sd.add_argument("dir", nargs="?", default=".", help="film folder (or a folder to create films in)")
    sd.add_argument("--port", type=int, default=8765)
    sd.add_argument("--no-browser", action="store_true")
    sd.set_defaults(fn=cmd_studio)

    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main(sys.argv[1:])
