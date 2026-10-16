"""The plugin system: every feature in dreamreel is a class, and a child class is all it takes to add one.

    import dreamreel as dr

    class Cake(dr.Prop):                      # a new kind of furniture
        label = "Birthday cake"
        params = [dr.Param("color", "color", default="pink"), dr.Param("candles", "number", default=5)]

        def build(self, s, name, place, color="pink", candles=5):
            ...                               # make meshes with dr.shapes, add marks with s.add_mark(...)

Defining the class registers it. It can then be used in set files (`type = "cake"`), and the studio
shows it in its menus with a form built from `params`. The same works for every kind of feature:

    kind        base class          used as
    character   dr.Character        cast/<name>.toml  type = "robot"
    hair        dr.Hair             cast file         hair = "afro"
    extra       dr.Extra            cast file         extras = ["crown"]
    mood        dr.Mood             feel / say        mood = "confused"
    gesture     dr.Gesture          beats             do = "gesture", gesture = "dance"
    action      dr.Action           beats             do = "hug"
    prop        dr.Prop             set files         [[props]] type = "cake"
    set         dr.Set              set files         kind = "spaceship"
    shot        dr.ShotType         beats             do = "shot", shot = "dutch_angle"
    voice       dr.VoiceEngine      film.toml         voice_engine = "my-tts"

A class registers under its `name` (default: the class name in snake_case). Giving a child class the
same name as a built-in replaces the built-in, e.g. `class Say(dr.actions.Say)` to change how all
characters talk.

Where extensions live:
  * `extensions/*.py` inside a film project: loaded automatically for that film;
  * any installed Python package that declares an entry point in the group `dreamreel.plugins`.
"""
import importlib.util
import os
import re
import sys

_REGISTRY = {}       # kind -> {name: class}
_SOURCE = {}         # (kind, name) -> "built-in", "extensions/x.py", "package:name"
_loading = ["built-in"]
_loaded_dirs = set()
_entry_points_loaded = False


def _snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Param:
    """One setting of a plugin, described so the studio (and an AI) can offer valid values.

    type: "text", "number", "bool", "color", "choice" (fixed `choices`), "choices" (several of `choices`),
          or a reference resolved from the film: "mark", "seat", "character", "target" (character, mark or
          the camera), "mood", "gesture", "shot", "hair", "extra", "place", "voice", "prop", "surface",
          "thing", "motion" (a clip in motions/), "model" (a file in models/).
    """

    def __init__(self, name, type="text", default=None, label=None, choices=None, required=False,
                 min=None, max=None, step=None, help=None, optional=None):
        self.name, self.type, self.default = name, type, default
        self.label = label or name.replace("_", " ").capitalize()
        self.choices, self.required, self.help = choices, required, help
        self.min, self.max, self.step = min, max, step
        self.optional = (not required) if optional is None else optional

    def describe(self):
        d = {"name": self.name, "type": self.type, "label": self.label, "required": self.required,
             "optional": self.optional}
        for k in ("default", "choices", "min", "max", "step", "help"):
            v = getattr(self, k)
            if v is not None:
                d[k] = list(v) if isinstance(v, (tuple, set)) else v
        return d


class Plugin:
    """Base of every extensible feature. Subclasses set `kind` once; their children register themselves."""

    kind = None          # set by each family base class ("prop", "action", ...)
    name = None          # registry name; default: the class name in snake_case
    label = None         # what people see; default: the name in words
    description = ""     # one sentence for menus and for AI models
    category = ""        # optional grouping in menus
    params = []          # list of Param
    abstract = True      # family base classes and helpers set this; concrete plugins don't

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if cls.__dict__.get("abstract", False):
            return
        cls.abstract = False
        if "name" not in cls.__dict__ or not cls.__dict__["name"]:
            cls.name = _snake(cls.__name__)
        if "label" not in cls.__dict__ or not cls.__dict__["label"]:
            cls.label = cls.name.replace("_", " ").capitalize()
        if cls.kind is None:
            raise TypeError(f"{cls.__name__}: subclass one of dreamreel's base classes (Prop, Action, ...)")
        register(cls)

    @classmethod
    def describe(cls):
        d = {"name": cls.name, "label": cls.label, "description": (cls.description or cls.__doc__ or "").strip()
             .split("\n")[0], "category": cls.category, "params": [p.describe() for p in cls.params],
             "source": _SOURCE.get((cls.kind, cls.name), "built-in")}
        d.update(cls.describe_extra())
        return d

    @classmethod
    def describe_extra(cls):
        """Extra facts a family adds for tools (e.g. a prop's default place)."""
        return {}

    @classmethod
    def defaults(cls):
        return {p.name: p.default for p in cls.params if p.default is not None}


def register(cls):
    _REGISTRY.setdefault(cls.kind, {})[cls.name] = cls
    _SOURCE[(cls.kind, cls.name)] = _loading[-1]
    return cls


def registry(kind):
    """All plugins of a kind, by name (built-ins first, then extensions in load order)."""
    return dict(_REGISTRY.get(kind, {}))


def names(kind):
    return list(_REGISTRY.get(kind, {}))


def get(kind, name):
    try:
        return _REGISTRY[kind][name]
    except KeyError:
        known = ", ".join(names(kind)) or "none"
        raise ValueError(f"no {kind} called {name!r}. Available: {known}. "
                         f"New ones can be added as classes in the film's extensions/ folder.") from None


def kinds():
    return sorted(_REGISTRY)


def describe_all():
    return {k: [cls.describe() for cls in _REGISTRY[k].values()] for k in kinds()}


# ---------------------------------------------------------------------- loading extensions
def _import_file(path, label):
    mod_name = "dreamreel_ext_" + re.sub(r"\W", "_", os.path.relpath(path).replace(os.sep, "_"))[:-3]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    _loading.append(label)
    try:
        spec.loader.exec_module(mod)
    finally:
        _loading.pop()
    return mod


def load_entry_points():
    global _entry_points_loaded
    if _entry_points_loaded:
        return
    _entry_points_loaded = True
    try:
        from importlib.metadata import entry_points
        eps = entry_points(group="dreamreel.plugins")
    except Exception:
        return
    for ep in eps:
        _loading.append(f"package:{ep.name}")
        try:
            ep.load()
        except Exception as e:
            print(f"[dreamreel] couldn't load plugin package {ep.name}: {e}")
        finally:
            _loading.pop()


def load_extensions(root):
    """Import every extensions/*.py of a film (once per process), so their classes register."""
    load_entry_points()
    d = os.path.join(root, "extensions")
    if d in _loaded_dirs or not os.path.isdir(d):
        return []
    _loaded_dirs.add(d)
    if root not in sys.path:
        sys.path.insert(0, root)  # extensions can import each other: `from extensions import common`
    loaded = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".py") and not fn.startswith("_"):
            _import_file(os.path.join(d, fn), f"extensions/{fn}")
            loaded.append(fn)
    return loaded
