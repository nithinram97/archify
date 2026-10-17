"""A film project on disk.

    my-film/
      film.toml            title, frame rate, resolution, scene order, music
      cast/<name>.toml     one file per character (how they look and sound)
      sets/<name>.toml     one file per place (room or outdoor, furniture, marks)
      scenes/<NNN_name>.toml one file per scene: set, cast and beats (who does what, in order);
                           a scene can also be a Python script (.py) for anything beats can't say
      extensions/*.py      your own classes: new characters, props, gestures, actions, shots...
      audio/music/ ...     your music and sound effects; audio/voices/ is generated
      renders/             everything dreamreel renders (safe to delete)

Everything is plain text, so a film can be versioned with git, diffed and edited by any AI model.
"""
import glob
import os
import tomllib

CURRENT_SCENE_NAME = None
_current = None


class Project:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        with open(os.path.join(self.root, "film.toml"), "rb") as f:
            self.film = tomllib.load(f)

    @property
    def title(self):
        return self.film.get("title", os.path.basename(self.root))

    def _toml(self, folder, name):
        path = os.path.join(self.root, folder, f"{name}.toml")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return tomllib.load(f)

    def cast_spec(self, name):
        return self._toml("cast", name)

    def set_spec(self, name):
        return self._toml("sets", name)

    def cast_names(self):
        return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(self.root, "cast", "*.toml")))

    def set_names(self):
        return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(self.root, "sets", "*.toml")))

    def edit_list(self):
        """The film's edit: a list of entries {scene, from, to, transition, ...} or {split: [a, b], ...}.
        From film.toml `edit` if there is one, else `scenes` (names or tables), else every scene file."""
        raw = self.film.get("edit") or self.film.get("scenes")
        if not raw:
            return [{"scene": os.path.splitext(os.path.basename(f))[0]} for f in self._all_scene_files()]
        out = []
        for e in raw:
            e = {"scene": e} if isinstance(e, str) else dict(e)
            if "scene" in e:
                e["scene"] = os.path.splitext(e["scene"])[0]
            out.append(e)
        return out

    def scenes(self):
        """Scene file paths used by the film, in order of first appearance."""
        seen, out = set(), []
        for e in self.edit_list():
            for stem in ([e["scene"]] if "scene" in e else e.get("split", [])):
                path = self._scene_file(stem)
                if path not in seen:
                    seen.add(path)
                    out.append(path)
        return out

    def _all_scene_files(self):
        d = os.path.join(self.root, "scenes")
        return sorted(glob.glob(os.path.join(d, "*.toml")) + glob.glob(os.path.join(d, "*.py")))

    def _scene_file(self, stem):
        if stem.endswith((".py", ".toml")):
            return os.path.join(self.root, "scenes", stem)
        for ext in (".toml", ".py"):
            p = os.path.join(self.root, "scenes", stem + ext)
            if os.path.exists(p):
                return p
        return os.path.join(self.root, "scenes", stem + ".toml")

    def scene_path(self, name):
        if os.path.exists(name):
            return os.path.abspath(name)
        every = self.scenes() + self._all_scene_files()
        for p in every:
            base = os.path.splitext(os.path.basename(p))[0]
            if name in (base, base.split("_", 1)[0], base.split("_", 1)[-1]):
                return p
        raise SystemExit(f"no scene matching {name!r}; scenes: {[os.path.basename(p) for p in every]}")

    def unlisted(self):
        """Scene files that film.toml's `scenes` list leaves out (they won't be in the film)."""
        listed = set(self.scenes())
        return [p for p in self._all_scene_files() if p not in listed]

    def renders(self, *parts):
        path = os.path.join(self.root, "renders", *parts)
        os.makedirs(os.path.dirname(path) if os.path.splitext(path)[1] else path, exist_ok=True)
        return path


def find(start="."):
    d = os.path.abspath(start)
    if os.path.isfile(d):
        d = os.path.dirname(d)
    while True:
        if os.path.exists(os.path.join(d, "film.toml")):
            return Project(d)
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def current():
    return _current


def activate(project, scene_name=None):
    """Make `project` the current film and load its extensions."""
    global _current, CURRENT_SCENE_NAME
    _current = project
    CURRENT_SCENE_NAME = scene_name
    if project is not None:
        from . import plugins
        plugins.load_extensions(project.root)
