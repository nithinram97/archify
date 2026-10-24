"""Growing new features: an AI model writes a new class, dreamreel tries it out, and keeps it only if it works.

    dreamreel evolve gesture moonwalk "glides backwards while the feet look like they walk forwards"
    dreamreel evolve prop campfire "a ring of stones round crackling logs" --look
    dreamreel evolve gesture wave "a bigger, happier wave" --from wave --replace

Every feature in dreamreel is a class (see plugins.py), so a missing one is a new child class and a
weak one is a better child of the same class. The model gets the parent class's source, a couple of
similar classes as examples and the starting point `dreamreel extend` would write, and writes
extensions/<name>.py. The draft is tried in a separate Python process: it has to register under its
name and work in a small scene made for its kind (a gesture is performed, a prop is placed in a room,
a style finishes a scene...). With --look, a still of that scene is shown to the model, which judges
it against what was asked. Errors and judgements go back to the model for another round. Only a draft
that passes reaches extensions/, where the film loads it like any other extension.

The separate process keeps a crash or a hang from taking dreamreel down with it; it is not a security
sandbox. The code is written by the model you chose and runs on your computer: read it, as you would
anything an AI coding agent writes (the path is printed).
"""
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from . import plugins

WRITER = """You write extensions for dreamreel, a Python tool that makes animated films in Blender. Every
feature is a class; defining a child class registers it (plugins.py). You get the parent class's source,
similar classes as examples, and a starting point. Write one complete Python file defining the new class:
- it must set `name = "{name}"` and subclass the parent given (or one of its children)
- import what you use (`import dreamreel as dr`, `from dreamreel import shapes, look, keys`, `bpy`, `mathutils`)
- use only methods and attributes you can see in the sources given; keep it self-contained
- no files, network or subprocesses: it builds and animates things in the Blender scene, nothing else
Reply with the file in one ```python block, then a line or two on how it works."""

JUDGE = """You check new dreamreel features. The picture is a still from a small test scene using the new
{kind} "{name}". What was asked for: {intent}
Does the picture show it working as asked (allow for a quick, flat-shaded preview)? Reply with JSON only:
{{"pass": true or false, "notes": "what's wrong and what to change, if anything"}}"""

TRIAL_TIMEOUT = 600


class EvolveError(RuntimeError):
    pass


def clean_name(name):
    n = re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_"))
    if not n or n[0].isdigit():
        raise EvolveError(f"{name!r} won't do as a name: letters, digits and _ (e.g. moonwalk)")
    return n


# ---------------------------------------------------------------------- what to start from
def base_class(kind, base=None):
    """The class a new `kind` grows from: `base` (a registered name), else the kind's own base class."""
    if base:
        return plugins.get(kind, base)
    family = plugins.registry(kind)
    if not family:
        raise EvolveError(f"no kind of feature called {kind!r}; kinds: {', '.join(plugins.kinds())}")
    for b in reversed(next(iter(family.values())).__mro__):
        if b is not plugins.Plugin and issubclass(b, plugins.Plugin) and getattr(b, "kind", None) == kind:
            return b
    return plugins.Plugin


def similar(kind, intent, parent, n=2):
    """The registered classes of this kind whose names and descriptions share most words with `intent`."""
    words = set(re.findall(r"[a-z]{3,}", intent.lower()))
    scored = []
    for name, cls in plugins.registry(kind).items():
        if cls is parent or not issubclass(cls, parent):
            continue
        text = f"{name} {getattr(cls, 'description', '') or ''} {getattr(cls, 'label', '') or ''}".lower()
        scored.append((len(words & set(re.findall(r"[a-z]{3,}", text))), name, cls))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [cls for _, _, cls in scored[:n]]


def _source(cls):
    try:
        return inspect.getsource(cls)
    except (OSError, TypeError):
        return f"class {cls.__name__}: ...  (source not available)"


def brief(kind, name, intent, parent):
    """The first message to the model: what to make and what to make it from."""
    from .cli import EXTEND_TEMPLATES
    parts = [f"Make a new {kind} called {name!r}: {intent}",
             f"The parent class, {parent.__module__}.{parent.__name__}:\n```python\n{_source(parent)}\n```"]
    for cls in similar(kind, intent, parent):
        parts.append(f"An existing {kind} for comparison, {cls.__name__}:\n```python\n{_source(cls)}\n```")
    if kind in EXTEND_TEMPLATES:
        body, usage = EXTEND_TEMPLATES[kind]
        cls_name = "".join(w.capitalize() for w in name.split("_"))
        start = body.format(cls=cls_name, name=name, desc=intent, label=name.replace("_", " "))
        parts.append(f"A starting point (how `dreamreel extend` begins one):\n```python\n{start}```\n"
                     f"It will be used as: {usage.format(name=name)}")
    return "\n\n".join(parts)


def _code(text):
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    if not m:
        raise EvolveError("the reply had no ```python block")
    return m.group(1)


# ---------------------------------------------------------------------- trying it out
def trial(root, path, kind, name, picture=None, timeout=TRIAL_TIMEOUT):
    """Load the draft in a separate process and use it in a small scene for its kind. Returns
    (ok, message); with `picture`, a still of the scene is saved there."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([here, os.environ.get("PYTHONPATH", "")]))
    cmd = [sys.executable, "-c", "from dreamreel import evolve; evolve._trial_main()", root or "", path, kind, name,
           picture or ""]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=root or None)
    except subprocess.TimeoutExpired:
        return False, f"the test scene didn't finish in {timeout} s (an endless loop?)"
    for line in r.stdout.splitlines()[::-1]:
        if line.startswith("@@TRIAL "):
            res = json.loads(line[8:])
            return res["ok"], res["message"]
    tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-12:])
    return False, f"the test process died (exit {r.returncode}):\n{tail}"


def _trial_main():
    """Runs in the trial process: argv = root, draft path, kind, name, picture path."""
    import traceback
    root, path, kind, name, picture = sys.argv[1:6]
    try:
        import dreamreel as dr
        from . import project
        if root:
            pr = project.find(root)
            if pr is not None:
                project.activate(pr)
        plugins._import_file(path, f"extensions/{os.path.basename(path)}")
        cls = plugins.registry(kind).get(name)
        if cls is None:
            raise EvolveError(f"the file doesn't register a {kind} called {name!r} (set name = \"{name}\")")
        if plugins._SOURCE.get((kind, name)) != f"extensions/{os.path.basename(path)}":
            raise EvolveError(f"{name!r} is still the old {kind}: the new class must set name = \"{name}\"")
        cls.describe()
        s = SMOKE.get(kind, _registered)(dr, cls, name)
        msg = f"the {kind} {name!r} works in a test scene"
        if s is not None:
            s.finish()
            warn = s.check()
            if warn:
                msg += " (the scene's checks say: " + "; ".join(warn[:3]) + ")"
            if picture:
                _still(s, picture)
        print("@@TRIAL " + json.dumps({"ok": True, "message": msg}))
    except BaseException as e:      # noqa: BLE001 (every way it can fail is a note for the model)
        tb = traceback.format_exc().strip().splitlines()
        print("@@TRIAL " + json.dumps({"ok": False, "message": f"{type(e).__name__}: {e}\n" + "\n".join(tb[-8:])}))


def _still(s, path):
    import bpy
    from . import _compat
    s.previz_settings()
    r = s.bscene.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = 640, 360, 100
    _compat.set_image_output(r)
    s.bscene.frame_set(max(1, int(s.length * s.fps * 0.6)))
    r.filepath = path
    bpy.ops.render.render(write_still=True)


# a small scene for each kind of feature (anything else: registered and describable is enough)
def _two(dr, style=None, **kw):
    s = dr.Scene({"kind": "room"}, style=style, **kw)
    a, b = s.cast(a={}), s.cast(b={})
    a.place((-0.6, 0), facing="right")
    b.place((0.6, 0), facing="left")
    return s, a, b


def _gesture(dr, cls, name):
    s, a, b = _two(dr)
    a.do(name, target="b")
    s.end_time = s.clock + 0.5
    return s


def _mood(dr, cls, name):
    s, a, b = _two(dr)
    a.feel(name)
    a.say("Well, look at that.", mood=name, to="b")
    return s


def _prop(dr, cls, name):
    s = dr.Scene({"kind": "room", "props": [{"type": name, "name": "it"}]})
    s.cast(a={}).place((1.2, -0.8), facing="left")
    s.end_time = 1.0
    return s


def _character(dr, cls, name):
    s = dr.Scene({"kind": "room"})
    c = s.cast(it={"type": name})
    c.place((-1, 0), facing="right")
    c.walk_to((1, 0))
    if "arms" in c.capabilities:
        c.do("wave")
    return s


def _style(dr, cls, name):
    s, a, b = _two(dr, style=name)
    a.say("Hello.", to="b")
    return s


def _shot(dr, cls, name):
    s, a, b = _two(dr)
    s.cut.shot(name, of="a", other="b", at=0)
    a.say("Hello.", to="b")
    return s


def _move(dr, cls, name):
    s, a, b = _two(dr)
    s.cut.shot("medium", of="a", at=0, move=name)
    a.say("Hello.", to="b")
    return s


def _lint(dr, cls, name):
    s, a, b = _two(dr)
    a.say("Hello.", to="b")
    s.finish()
    out = cls(s).check(s)
    if not isinstance(out, list) or not all(isinstance(w, str) for w in out):
        raise EvolveError(f"check() must return a list of sentences, not {out!r}")
    return s


def _time(dr, cls, name):
    s = dr.Scene({"kind": "outdoor", "biome": "meadow"}, time_of_day=name)
    s.cast(a={}).place((0, 0), facing="camera")
    s.end_time = 1.0
    return s


def _weather(dr, cls, name):
    s = dr.Scene({"kind": "outdoor", "biome": "meadow"}, weather=name)
    s.cast(a={}).place((0, 0), facing="camera")
    s.end_time = 1.0
    return s


def _wearing(key):
    def make(dr, cls, name):
        s = dr.Scene({"kind": "room"})
        s.cast(a={key: [name] if key == "extras" else name}).place((0, 0), facing="camera")
        s.end_time = 1.0
        return s
    return make


def _sound(dr, cls, name):
    from . import sounds
    if sounds.path(name, download=False) is None:
        raise EvolveError(f"the sound {name!r} made no file")
    return None


def _registered(dr, cls, name):
    return None


SMOKE = {"gesture": _gesture, "mood": _mood, "prop": _prop, "character": _character, "style": _style,
         "shot": _shot, "move": _move, "lint": _lint, "time": _time, "weather": _weather,
         "extra": _wearing("extras"), "hair": _wearing("hair"), "sound": _sound}


# ---------------------------------------------------------------------- the loop
def evolve(ai, root, kind, name, intent, base=None, rounds=3, look=False, replace=False, progress=print):
    """Have `ai` write a new `kind` called `name` that does `intent`, try it, and keep it in
    extensions/<name>.py if it works. Returns the path."""
    name = clean_name(name)
    dest = os.path.join(root, "extensions", f"{name}.py")
    if os.path.exists(dest) and not replace:
        raise EvolveError(f"extensions/{name}.py already exists (--replace to grow a better one)")
    parent = base_class(kind, base)
    drafts = os.path.join(root, "extensions", ".drafts")
    os.makedirs(drafts, exist_ok=True)
    draft = os.path.join(drafts, f"{name}.py")
    system = WRITER.format(name=name)
    messages = [{"role": "user", "content": [{"text": brief(kind, name, intent, parent)}]}]
    work = tempfile.mkdtemp(prefix="dreamreel-evolve-")
    try:
        for attempt in range(1, rounds + 1):
            progress(f"  asking {ai} to write it{'' if attempt == 1 else f' (round {attempt})'} ...")
            reply = ai.ask(system, messages)
            messages.append({"role": "assistant", "content": [{"text": reply}]})
            try:
                code = _code(reply)
                compile(code, draft, "exec")
            except (EvolveError, SyntaxError) as e:
                note = f"That isn't a Python file that compiles: {e}. Reply with the complete file."
                progress(f"  {note}")
                messages.append({"role": "user", "content": [{"text": note}]})
                continue
            with open(draft, "w") as f:
                f.write(code)
            picture = os.path.join(work, f"look_{attempt}.png") if look else None
            progress("  trying it in a test scene ...")
            ok, msg = trial(root, draft, kind, name, picture)
            if not ok:
                progress(f"  it doesn't work yet: {msg.splitlines()[0]}")
                messages.append({"role": "user", "content": [{"text": f"Trying it failed:\n{msg}\n"
                                                                      "Fix it and reply with the complete file."}]})
                continue
            progress(f"  {msg}")
            if look and picture and os.path.exists(picture):
                progress(f"  asking {ai} whether it looks right ...")
                verdict = _verdict(ai.ask(JUDGE.format(kind=kind, name=name, intent=intent),
                                          [{"role": "user", "content": [{"image": picture},
                                                                        {"text": "Your verdict, as JSON."}]}]))
                if not verdict.get("pass"):
                    notes = verdict.get("notes") or "it doesn't look as asked"
                    progress(f"  not as asked: {notes}")
                    messages.append({"role": "user", "content": [
                        {"image": picture},
                        {"text": f"It runs, but a still of it doesn't look as asked: {notes}\n"
                                 "Improve it and reply with the complete file."}]})
                    continue
            if os.path.exists(dest):
                hist = os.path.join(root, "extensions", ".history")
                os.makedirs(hist, exist_ok=True)
                shutil.move(dest, os.path.join(hist, f"{name}.{len(os.listdir(hist)) + 1}.py"))
            shutil.move(draft, dest)
            return dest
        raise EvolveError(f"no working {kind} after {rounds} rounds; the last draft is in "
                          f"extensions/.drafts/{name}.py")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _verdict(text):
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group(0)) if m else {"pass": False, "notes": text[:300]}
    except ValueError:
        return {"pass": False, "notes": text[:300]}
