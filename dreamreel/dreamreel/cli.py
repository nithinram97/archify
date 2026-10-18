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
    dreamreel generate frog --prompt "a chubby cartoon frog"   make a model with dreamreel's AI modeller
"""
import argparse
import getpass
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
    for sub in ("audio/music", "audio/sfx", "renders", "extensions", "motions", "models"):
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
    built = {}
    for path in paths:
        s = film.build(p, path)
        print(s.summary())
        built[s.name] = (s.length, sum(c[1] for c in s.cards), s.transition)
        print()
    if a.scene:
        length, cards, _ = next(iter(built.values()))
        print(f"{p.title}: 1 scene, {length + cards:.1f} s")
    else:
        total, lines = _edit_plan(p.edit_list(), built)
        print(f"{p.title}: {len(paths)} scene(s), {len(lines)} clip(s) in the edit, about {total:.1f} s")
        for line in lines:
            print("  " + line)
    for extra in p.unlisted() if not a.scene else []:
        print(f"note: {os.path.basename(extra)} is not in film.toml's scenes list, so it isn't in the film")


def _edit_plan(edit, built):
    """Roughly how long the cut film is, and one line per clip (the edit decision list)."""
    from . import plugins
    total, lines = 0.0, []
    for e in edit:
        names = [e["scene"]] if "scene" in e else list(e.get("split", []))
        if not names or any(n not in built for n in names):
            continue
        length, cards, own = built[names[0]]
        start = float(e.get("from") or 0.0)
        end = min(float(e.get("to") or built[n][0]) for n in names)
        trans = dict(own or {}) if not start else {}
        if e.get("transition"):
            trans = {"name": e["transition"], "duration": e.get("duration")}
        elif e.get("duration") is not None:
            trans["duration"] = e["duration"]
        cls = plugins.get("transition", trans.get("name") or "cut")
        dur = trans.get("duration")
        dur = cls.default_duration if dur is None else float(dur)
        here = (cards if not start and "scene" in e else 0.0) + max(0.0, end - start)
        if lines and cls.overlap:
            here -= dur
        if lines and (e.get("audio") or "").lower() == "l":
            here -= float(e.get("audio_seconds", 0.8))
        how = "start" if not lines else cls.name + (f" {dur:g}s" if cls.name != "cut" else "")
        span = f"{start:g}-{end:g}s" if start or e.get("to") else f"{end:.1f}s"
        lines.append(f"{total:6.1f}s  {' | '.join(names):<24} {span:<10} {how}"
                     + (f", audio {e['audio']}" if e.get("audio") else ""))
        total += here
    return total, lines


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
    s.cut.top_down(12, max(st.width, st.depth * 16 / 9) + 1.0)
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


def _ai_ready():
    """The AI model the modeller would use now ("provider:model"), or None."""
    from . import ai
    try:
        return str(ai.configured())
    except ai.AIError:
        return None


def cmd_info(a):
    """Everything a tool needs to offer valid choices: every plugin with its settings, the colours,
    and each set's marks and seats."""
    import json
    from . import lipsync, look, plugins, scene as scene_mod, sets, voices
    from .sets import ZONES
    p = _project()
    info = {
        "plugins": plugins.describe_all(),
        "catalog": {
            "places": [z for z in ZONES if z != "centre"], "colors": look.COLORS,
            "voices": list(voices.SUGGESTED), "voice_engine": voices.pick_engine() is not None,
            "voice_engines": voices.status(), "lipsync_ready": lipsync.installed() is not None,
            "ai": _ai_ready(),
            "languages": {k: {"name": v[0], "native": v[1], "try": v[2], "piper": voices.PIPER_DEFAULT.get(k)}
                          for k, v in voices.LANGUAGES.items()},
        },
        "sets": {},
        "motions": [],
        "models": [],
    }
    from . import actors, quaternius
    from . import humans as humans_mod
    have = quaternius.installed()
    info["assets"] = {
        "packs": {n: {"installed": n in have, "about": spec["about"]} for n, spec in quaternius.PACKS.items()},
        "outfits": {b: sorted(actors.outfits(b)) for b in ("woman", "man")},
        "species": sorted(actors.species()),
        "thumbs": quaternius.thumb_names(),
        "humans": humans_mod.installed(),
    }
    from . import motion as _motion
    info["motions"] = _motion.Library(p.root).names()
    from . import models as _models
    info["models"] = _models.files(p.root)
    for name in p.set_names():
        try:
            scene_mod._reset_blender()
            st = sets.Set.create(p.set_spec(name), name=name)
            info["sets"][name] = {"kind": st.kind, "marks": sorted(st.marks), "seats": sorted(st.seats),
                                  "surfaces": sorted(st.surfaces), "props": sorted(st.props),
                                  "things": sorted(st.things)}
        except Exception as e:
            info["sets"][name] = {"error": f"{type(e).__name__}: {e}", "marks": [], "seats": []}
    print("@@JSON " + json.dumps(info))


def cmd_assets(a):
    """List Quaternius's free (CC0) packs dreamreel uses (people, animals...), or download them."""
    from . import humans, materials, quaternius as q
    extra = {"humans": humans, "materials": materials}
    if a.pack in extra:                     # MakeHuman's people, or the real-world materials
        print(f"fetching {a.pack}...")
        humans.download() if a.pack == "humans" else materials.download_all()
        return
    if a.download:
        q.download([a.pack] if a.pack else None)
    if a.download or a.thumbs:
        if {"women", "men", "animals"} & q.installed():
            print("pictures of the people and animals:")
            q.thumbnails(force=a.thumbs)
    have = q.installed()
    print(f"Quaternius packs (CC0, quaternius.com) in {q.CACHE}:")
    for name, spec in q.PACKS.items():
        mark = "installed" if name in have else "not installed"
        print(f"  {name:12s} {mark:14s} {spec['about']}")
    if not have:
        print("Download them with: dreamreel assets --download   (or --pack NAME)")
    print("\nAlso (all CC0):")
    print(f"  {'humans':12s} {'installed' if humans.installed() else 'not installed':14s} realistic people: MakeHuman's "
          "bodies, skins, hair, clothes and 52-shape faces (`--pack humans`, 700 MB)")
    print(f"  {'materials':12s} {'fetched' if materials.fetched() else 'on demand':14s} real-world surfaces for the "
          "realistic look, from ambientCG and Poly Haven (`--pack materials`, about 250 MB; else as needed)")


def cmd_generate(a):
    """Make a character or a thing with dreamreel's modelling agent (any AI model; see ai.py)."""
    import json
    import tempfile
    from . import ai, modeler, picture3d
    p = _project()
    glb = os.path.join(p.root, "models", f"{a.name}.glb")
    kind = "prop" if a.prop else "character"
    try:
        if a.from_picture:                # shape from a picture on a booster (picture3d.py)
            if not a.image:
                raise SystemExit("--from-picture needs --image picture.png")
            if os.path.exists(glb) and not a.force:
                raise SystemExit(f"models/{a.name}.glb already exists (--force to make it again)")
            image = a.image if os.path.isabs(a.image) else os.path.join(os.getcwd(), a.image)
            try:
                glb = picture3d.make(p.root, a.name, image, rig=a.rig)
            except picture3d.PictureError as e:
                raise SystemExit(str(e))
            print(f"saved models/{os.path.basename(glb)}")
            _cast_model(p, a, glb, kind)
            return
        if a.spec:                        # rebuild from a (hand-edited) recipe: no AI needed
            with open(os.path.join(p.root, a.spec) if not os.path.isabs(a.spec) else a.spec) as f:
                recipe = modeler.check(json.load(f))
        else:
            if not (a.prompt or a.image):
                raise SystemExit("say what to make: --prompt \"a chubby cartoon frog\" or --image picture.png "
                                 "(or --spec models/NAME.json to rebuild a recipe)")
            if os.path.exists(glb) and not a.force:
                raise SystemExit(f"models/{a.name}.glb already exists (--force to make it again)")
            model = ai.configured(a.provider, a.model, a.url)
            print(f"modelling {a.name} with {model} ({a.rounds} rounds of looking and correcting)")
            with tempfile.TemporaryDirectory() as tmp:
                recipe = modeler.generate(model, a.prompt, a.image, kind=kind, rounds=a.rounds, workdir=tmp)
        recipe["name"] = a.name
        modeler.save(recipe, glb)
    except (ai.AIError, modeler.RecipeError) as e:
        raise SystemExit(str(e))
    print(f"saved models/{a.name}.glb and its recipe models/{a.name}.json")
    if a.rig and kind == "character":
        try:
            picture3d.rig_model(glb)
        except picture3d.PictureError as e:
            print(f"not rigged by AI ({e}); dreamreel rigs it when it's cast")
    _cast_model(p, a, glb, kind)


def _cast_model(p, a, glb, kind):
    """A cast file for a new model character (or how to use a new prop)."""
    rel = os.path.relpath(glb, p.root).replace(os.sep, "/")
    if kind == "prop":
        print(f"put it in a set: [[props]] type = \"model\", file = \"{rel}\", height = ...")
        return
    cast = os.path.join(p.root, "cast", f"{a.name}.toml")
    if os.path.exists(cast) and not a.force:
        print(f"cast/{a.name}.toml exists; set its file = \"{rel}\" to use the new model")
        return
    os.makedirs(os.path.dirname(cast), exist_ok=True)
    with open(cast, "w") as f:
        f.write(f'name = "{a.name.capitalize()}"\ntype = "model"\nfile = "{rel}"\nheight = {a.height}\n')
    print(f"cast/{a.name}.toml is ready: rigged when cast, it walks, gestures and handles things. "
          "Check it with `dreamreel cast`.")


def cmd_kit(a):
    """Print the modelling kit recipes are written in (for people and AI agents writing them)."""
    from . import modeler
    print(modeler.KIT)


def cmd_motions(a):
    """List the film's motion library, or import a clip into it."""
    import shutil
    from . import motion
    p = _project()
    lib_dir = os.path.join(p.root, "motions")
    if a.add:
        os.makedirs(lib_dir, exist_ok=True)
        name = a.name or os.path.splitext(os.path.basename(a.add))[0]
        ext = os.path.splitext(a.add)[1].lower()
        dest = os.path.join(lib_dir, name + ext)
        clip = motion.load(a.add, name=name)          # check it can be read and retargeted first
        shutil.copyfile(a.add, dest)
        if a.tags:
            toml = os.path.join(lib_dir, "library.toml")
            with open(toml, "a") as fh:
                tags = ", ".join(f'"{t.strip()}"' for t in a.tags.split(",") if t.strip())
                fh.write(f'\n[{name}]\nfile = "{os.path.basename(dest)}"\ntags = [{tags}]\n')
        print(f"added {os.path.relpath(dest, p.root)}: {clip.length:.1f} s. Use it with do = \"perform\", motion = \"{name}\"")
        return
    lib = motion.Library(p.root)
    if not lib.names():
        print("No motions yet. Put .bvh or .fbx clips in motions/ (or: dreamreel motions --add FILE).")
        return
    for n in lib.names():
        try:
            c = lib.get(n)
            loop = f", loop {c.find_loop()[0] / c.fps:.2f}-{c.find_loop()[1] / c.fps:.2f} s" if c.tags & {"walk", "run", "jog"} else ""
            print(f"  {n:20} {c.length:6.1f} s  tags: {', '.join(sorted(c.tags)) or '-'}{loop}")
        except Exception as e:
            print(f"  {n:20} can't be used: {e}")


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
    "move": ('''class {cls}(dr.CameraMove):
    """{desc}"""
    description = "{desc}"
    default_amount = 1.0

    def track(self, d, shot, t0, t1, base, amount=None, to=None):
        # base: [(time, CameraState)] so far; return a new list. A CameraState has pos, aim, lens,
        # roll (degrees), focus and fstop; .copy(...) changes some of them; .right() is screen right.
        a = self.default_amount if amount is None else float(amount)
        t, s = base[0]
        return [(t0, s), (t1, s.copy(pos=s.pos + dr.camera.UP * a, roll=s.roll + 10 * a))]
''', 'do = "shot", move = "{name}" in a beat'),
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
    "scenery": ('''class {cls}(dr.Scenery):
    """{desc}"""
    description = "{desc}"
    radius = 0.5              # how much room it needs
    blocks = True             # people walk round it
    sway = 0.5                # how much it moves in the wind (0: not at all)

    def build(self, root, name, scale, rng):
        # Build round `root`, an empty at its base on the ground; sizes times `scale`.
        dr.shapes.cylinder(name, 0.12 * scale, 1.2 * scale, dr.look.matte("#7a5a3a"), root, bevel=0)
        dr.shapes.sphere(name, 0.5 * scale, dr.look.plastic(rng.choice(["#e07ab0", "#f2a9cf"])), root,
                         at=(0, 0, 1.4 * scale), segments=16)
''', 'variety = "{name}" on a tree prop, or in a biome\'s scatter list'),
    "biome": ('''class {cls}(dr.Biome):
    """{desc}"""
    description = "{desc}"
    ground, far = "#8fc06a", "#a0c880"         # ground colour near and far
    terrain = "hills"                          # flat, rolling, hills, mountains, dunes, craters
    scatter = [("tree", 1.0), ("bush", 0.5)]   # (scenery, weight) in the distance and at the sides
    near = [("flowers", 1.0)]                  # small things near the acting area
    density = 1.0

    def adjust_light(self, light):
        light.tint_sky("#ffd0e0", 0.2)         # a pinker sky; see dr.Light for everything

    def build_extra(self, s, rng):
        pass                                   # anything else: a lake, a castle on the hill...
''', 'kind = "outdoor", biome = "{name}" in a set file'),
    "time": ('''class {cls}(dr.TimeOfDay):
    """{desc}"""
    description = "{desc}"
    sun_elevation, sun_azimuth = 15, 220       # degrees; azimuth 0 = behind the set, 180 = behind the camera
    sun_color, sun_energy = "#ffcf9a", 2.4
    zenith, horizon, sky_strength = "#7a8fc8", "#ffd8b0", 0.8
    room, room_color, practicals = 0.8, "#ffe0c0", 1.4   # room lights, their colour, lamps
''', 'time_of_day = "{name}" in a scene file'),
    "weather": ('''class {cls}(dr.Weather):
    """{desc}"""
    description = "{desc}"
    wind = 1.0

    def adjust(self, light, k):
        light.sun_energy *= 0.6
        light.tint_sky("#d9a066", 0.5 * k)

    def build(self, env, k):
        env.clouds(int(6 * k), "#e8c8a0")       # also env.precipitation("rain" or "snow", count), env.light
''', 'weather = "{name}" in a scene file'),
    "style": ('''class {cls}(dr.Style):
    """{desc}"""
    description = "{desc}"
    view = ("Standard", "None")             # colour management (view transform, look)
    outline, outline_color = 0.012, "#1c1a1a"
    bands = [(0.0, 0.5), (0.25, 0.8), (0.6, 1.0)]  # cel shading tones: (where, brightness or colour)
    saturation = 1.2
    steps = 1                                # 2 or 3: animate on twos or threes

    def adjust_light(self, light):
        light.fill = 0.6                     # see dr.Light for everything that can change

    # def material(self, mat, scene): ...    # or change every material yourself
''', 'style = "{name}" in film.toml (the whole film) or in a scene file'),
    "transition": ('''class {cls}(dr.Transition):
    """{desc}"""
    description = "{desc}"
    overlap = True            # True: plays over the end of one scene and the start of the next
    default_duration = 0.8

    def apply(self, ed, a, b, start, frames, color=None, direction=None):
        # a, b: the outgoing and incoming clips (their .strips are video strips). start: b's first frame.
        # ed.fade(strip, f0, f1, a0, a1), ed.move(strip, f0, f1, offset, to, scale, scale_to),
        # ed.wipe(...), ed.color(f0, f1, colour, channel) are the building blocks.
        for s in b.strips:
            ed.fade(s, start, start + frames, 0.0, 1.0)
            ed.move(s, start, start + frames, (0, -ed.H * 0.1), (0, 0), scale=1.1, scale_to=1.0)
''', 'transition = "{name}" in a scene file, or in a film.toml [[edit]] entry'),
    "screen": ('''class {cls}(dr.ScreenEffect):
    """{desc}"""
    description = "{desc}"
    default_duration = 1.0
    default_color = "black"

    def apply(self, ed, f0, frames, color):
        # Something over the whole picture from frame f0 for `frames` frames; return the strip.
        c = ed.color(f0, f0 + frames, color, channel=ed.top - 2)
        for k in range(0, frames, 4):            # a flicker
            ed.key(c, "blend_alpha", f0 + k, 0.8 if k % 8 == 0 else 0.0)
        return c
''', 'do = "screen", effect = "{name}" in a beat'),
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
    from . import plugins, voices
    _project_optional()
    if a.say:
        p = _project()
        spec = {k: v for k, v in (("name", a.voice), ("language", a.language), ("describe", a.describe),
                                  ("engine", a.engine), ("sample", a.sample), ("sample_text", a.sample_text),
                                  ("fish", a.fish), ("speed", a.speed)) if v}

        class Who:
            name, voice = "audition", spec
        vs = voices.Voices(p.root, engine=a.engine or p.film.get("voice_engine", "auto"))
        speech = vs.speak(Who(), a.say, mood=a.mood)
        if speech is None:
            raise SystemExit("no voice engine here can speak that; run `dreamreel voices` to see what's set up")
        print(speech.path)
        return
    print("Voice engines (best first when several can speak a line):")
    for name, d in voices.status().items():
        langs = ", ".join(d["languages"]) or "any language"
        print(f"  {'ready' if d['available'] else 'off  '}  {name:13} {d['description']}  [{langs}]")
        if not d["available"] and d.get("setup"):
            print(f"         to use it: {d['setup']}")
    print("\nA cast file sets a voice by name (Piper), or as a table:")
    print('  voice = "hi_IN-priyamvada-medium"')
    print('  [voice]\n  language = "ta"\n  describe = "An old woman with a warm, slow voice"')
    print("Languages:", ", ".join(f"{k} ({v[0]})" for k, v in voices.LANGUAGES.items()))
    print("Lines written in an Indian script are spoken in that language automatically.")


def cmd_rig(a):
    from . import picture3d
    p = _project()
    path = a.file if os.path.isabs(a.file) else os.path.join(p.root, a.file)
    if not os.path.exists(path):
        raise SystemExit(f"no model at {a.file}")
    try:
        out = picture3d.rig_model(path)
    except picture3d.PictureError as e:
        raise SystemExit(str(e))
    print(f"rigged: {os.path.relpath(out, p.root)} (the original is kept as *.unrigged.*)")


def cmd_boost(a):
    from . import boost, userkeys
    _project_optional()
    if a.action == "connect":
        if not a.url:
            raise SystemExit("dreamreel boost connect <address> <pass key>  (both are printed by the booster)")
        url = a.url if "://" in a.url else "http://" + a.url
        b = boost.Booster(url, a.key or "")
        try:
            st = b.status(fresh=True)
        except boost.BoostError as e:
            raise SystemExit(str(e))
        userkeys.set_key("DREAMREEL_BOOST_URL", url)
        userkeys.set_key("DREAMREEL_BOOST_TOKEN", a.key or "")
        print(f"connected to the booster at {url} (graphics card: {st.get('gpu') or 'none'})")
        return
    if a.action == "disconnect":
        userkeys.set_key("DREAMREEL_BOOST_URL", "")
        userkeys.set_key("DREAMREEL_BOOST_TOKEN", "")
        print("booster forgotten")
        return
    if a.action == "serve":
        import runpy
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "booster", "server.py")
        sys.argv = [here] + (["--port", str(a.port)] if a.port else []) + (["--prepare", a.url] if a.url else [])
        runpy.run_path(here, run_name="__main__")
        return
    b = boost.configured()
    if b is None:
        print("No booster connected. A booster runs dreamreel's graphics-card AI (Indian voices, acting from a")
        print("sentence, models from a picture, rigging, faces, restyling) on a free Google Colab notebook or")
        print("any computer with a graphics card:")
        print("  1. open notebooks/dreamreel-booster.ipynb in Colab (Runtime: T4 GPU) and run it, or run")
        print("     `dreamreel boost serve` on a computer with a graphics card;")
        print("  2. dreamreel boost connect <address> <pass key>   (both are printed by the booster)")
        return
    try:
        st = b.status(fresh=True)
    except boost.BoostError as e:
        raise SystemExit(str(e))
    if a.action == "prepare":
        names = [n for n in (a.url or "").split(",") if n] or list(st["skills"])
        print("preparing:", ", ".join(b.prepare(names)["preparing"]))
        return
    print(f"booster: {b}  graphics card: {st.get('gpu') or 'none found'}  busy: {st.get('busy', 0)}")
    for name, d in st.get("skills", {}).items():
        print(f"  {d['state']:14} {name:22} {d['about']}")


def cmd_mcp(a):
    """MCP over stdio: the protocol keeps the real stdout; anything else printed (Blender, models) goes
    to stderr, so it can't corrupt a message."""
    from . import mcp
    proto = os.fdopen(os.dup(1), "w", encoding="utf-8", buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    mcp.serve(a.dir, sys.stdin, proto)


def cmd_keys(a):
    from . import userkeys
    if a.action == "set":
        if not a.name:
            raise SystemExit("which key? e.g. dreamreel keys set HF_TOKEN")
        value = a.value if a.value is not None else getpass.getpass(f"{a.name}: ")
        userkeys.set_key(a.name, value)
        print(f"{a.name} {'saved' if value.strip() else 'removed'} ({userkeys.path()})")
        return
    for k, d in userkeys.status().items():
        print(f"  {'set' if d['set'] else '   '}  {k:22} {d['for']}")
        if not d["set"]:
            print(f"        get one: {d['get']}")


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

    v = sub.add_parser("voices", help="voice engines, languages, and how to give characters voices")
    v.add_argument("--say", help="speak this text (to try a voice); prints the sound file")
    v.add_argument("--voice", help="a Piper voice name")
    v.add_argument("--language", help="en, hi, ta, te, bn, mr, kn, ml, gu, pa, or, as, ur, ne")
    v.add_argument("--describe", help="describe the voice in words (Indic Parler-TTS)")
    v.add_argument("--engine", help="piper, indic_parler, indic_f5, fish, ...")
    v.add_argument("--mood", help="a mood, for engines that act (happy, sad, angry, ...)")
    v.add_argument("--sample", help="a recording of the voice to copy (IndicF5)")
    v.add_argument("--sample-text", help="what the recording says, word for word")
    v.add_argument("--fish", help="a Fish Audio voice id")
    v.add_argument("--speed", type=float)
    v.set_defaults(fn=cmd_voices)

    bo = sub.add_parser("boost", help="a booster: AI models on a graphics card (a free Colab notebook, or a computer with one)")
    bo.add_argument("action", nargs="?", choices=("status", "connect", "disconnect", "prepare", "serve"), default="status")
    bo.add_argument("url", nargs="?", help="connect: the booster's address; prepare/serve: skills, comma-separated")
    bo.add_argument("key", nargs="?", help="connect: the pass key the booster printed")
    bo.add_argument("--port", type=int, help="serve: the port (default 8780)")
    bo.set_defaults(fn=cmd_boost)

    mc = sub.add_parser("mcp", help="serve this film to AI models over MCP (Claude, ChatGPT, local models)")
    mc.add_argument("dir", nargs="?", default=".", help="the film's folder")
    mc.set_defaults(fn=cmd_mcp)

    k = sub.add_parser("keys", help="keys for AI services, saved on this computer (not in the film)")
    k.add_argument("action", nargs="?", choices=("list", "set"), default="list")
    k.add_argument("name", nargs="?")
    k.add_argument("value", nargs="?", help="leave out to type it hidden; empty to remove")
    k.set_defaults(fn=cmd_keys)

    i = sub.add_parser("info", help="every feature and set mark as JSON (for tools)")
    i.set_defaults(fn=cmd_info)

    pg = sub.add_parser("plugins", help="list every feature: characters, props, gestures, actions, shots...")
    pg.add_argument("kind", nargs="?")
    pg.add_argument("-v", "--verbose", action="store_true", help="show each one's settings")
    pg.set_defaults(fn=cmd_plugins)

    mo = sub.add_parser("motions", help="the film's motion library (motion capture clips)")
    mo.add_argument("--add", metavar="FILE", help="import a .bvh/.fbx/.glb clip")
    mo.add_argument("--name")
    mo.add_argument("--tags", help="comma separated, e.g. walk or dance")
    mo.set_defaults(fn=cmd_motions)
    asp = sub.add_parser("assets", help="free 3D packs: people, animals, realistic humans, real-world materials")
    asp.add_argument("--download", action="store_true", help="fetch the packs (CC0) into the cache")
    asp.add_argument("--pack", help="just this pack (see the list; humans and materials too)")
    asp.add_argument("--thumbs", action="store_true", help="(re)make the pictures of people and animals for menus")
    asp.set_defaults(fn=cmd_assets)
    ge = sub.add_parser("generate", help="make a character or prop with dreamreel's modelling agent (any AI model)")
    ge.add_argument("name", help="what to call it (models/NAME.glb, cast/NAME.toml)")
    ge.add_argument("--prompt", help="describe it")
    ge.add_argument("--image", help="a picture of it (for AI models that can see)")
    ge.add_argument("--spec", help="rebuild from a recipe (models/NAME.json), no AI")
    ge.add_argument("--prop", action="store_true", help="a prop, not a character")
    ge.add_argument("--height", type=float, default=1.0, help="character height in metres")
    ge.add_argument("--rounds", type=int, default=3, help="times the AI looks at its model and corrects it")
    ge.add_argument("--provider", help="anthropic, openai, gemini, openrouter, ollama, lmstudio, custom")
    ge.add_argument("--model", help="the provider's model name")
    ge.add_argument("--url", help="endpoint for a custom (OpenAI-compatible) provider")
    ge.add_argument("--force", action="store_true", help="replace an existing model")
    ge.add_argument("--from-picture", action="store_true",
                    help="make the shape from --image with TripoSG on a booster, painted from the picture")
    ge.add_argument("--rig", action="store_true", help="rig it with UniRig on a booster (any creature)")
    ge.set_defaults(fn=cmd_generate)

    rg = sub.add_parser("rig", help="rig a model with UniRig on a booster (people, animals, creatures)")
    rg.add_argument("file", help="the model, e.g. models/dragon.glb")
    rg.set_defaults(fn=cmd_rig)
    sub.add_parser("kit", help="the modelling kit that model recipes are written in").set_defaults(fn=cmd_kit)
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
    from . import userkeys
    userkeys.load()
    a.fn(a)


if __name__ == "__main__":
    main(sys.argv[1:])
