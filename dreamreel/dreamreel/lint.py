"""Checks that read a finished scene the way a director would, before anything is rendered.

Each check is a class (kind "lint"); `dreamreel check` runs them all and prints what they find, and
`check --json` hands the same warnings to tools and AI agents. A film can add its own:

    class NoFaceInWide(dr.Lint):
        label = "Faces in wide shots"
        def check(self, scene):
            return [...]                    # sentences; each says what's wrong and where

or switch some off in film.toml:

    [check]
    ignore = ["static_camera"]
    static_camera_seconds = 14          # a check's settings: <name>_<setting>
"""
from .plugins import Plugin


class Lint(Plugin):
    """One thing to look for in a scene. `check(scene)` returns warnings (sentences)."""
    kind = "lint"
    abstract = True
    label = ""
    description = ""
    settings = {}            # name: default, overridable in film.toml [check] as <rule>_<name>

    def __init__(self, scene):
        cfg = (getattr(scene, "film", None) or {}).get("check") or {}
        self.opts = {k: cfg.get(f"{self.name}_{k}", v) for k, v in self.settings.items()}

    def check(self, scene):
        raise NotImplementedError


def run(scene):
    """Every check that's switched on, in order; their warnings, each reported once."""
    from . import plugins
    cfg = (getattr(scene, "film", None) or {}).get("check") or {}
    off = set(cfg.get("ignore", []))
    out = []
    for name, cls in plugins.registry("lint").items():
        if name not in off:
            out += [w for w in cls(scene).check(scene) if w not in out]
    return out


# ---------------------------------------------------------------------- helpers
def shots(scene):
    """[(shot, start, end)] as the film will cut them."""
    final = scene.cut.final or sorted(scene.cut.shots, key=lambda s: s.at)
    return [(s, s.at, final[i + 1].at if i + 1 < len(final) else scene.length) for i, s in enumerate(final)]


def busy(scene, c, t0, t1, slack=0.4):
    """Whether `c` does anything between t0 and t1: a gesture, a move, a line, a look, a turn, a feeling."""
    for e in scene.events:
        if e["who"] is c and e["t0"] < t1 + slack and e["t1"] > t0 - slack:
            return True
    return any(t0 - slack <= t <= t1 + slack for t, _ in getattr(c, "acts", []))


def _fmt(t):
    return f"{t:.1f}s"


# ---------------------------------------------------------------------- the checks
class Overlap(Lint):
    label = "Overlapping characters"
    description = "Two characters standing inside each other (not counting blows, falls and pile-ons, where "\
                  "bodies are meant to meet)."

    def check(self, scene):
        out, seen = [], set()
        names = list(scene.actors.values())
        for t in [i * 0.5 for i in range(int(scene.length * 2))]:
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    if (a.name, b.name) in seen or a.touching(t) or b.touching(t):
                        continue
                    if a.visible(t) and b.visible(t) and (a.position(t) - b.position(t)).length < 0.35 * max(a.H, b.H):
                        seen.add((a.name, b.name))
                        out.append(f"{a.name} and {b.name} overlap at {_fmt(t)}")
        return out


class StaticCamera(Lint):
    label = "Static camera"
    description = "A long shot where the camera never moves and nothing cuts away."
    settings = {"seconds": 10.0}

    def check(self, scene):
        out = []
        for s, t0, t1 in shots(scene):
            moving = [mv for mv, _ in s.moves if mv.name != "static"]
            if t1 - t0 > self.opts["seconds"] and not moving:
                out.append(f"static camera: the {s.label} shot at {_fmt(t0)} holds {t1 - t0:.1f}s without a move "
                           f"or a cut (add a cut, a reaction shot or a camera move)")
        return out


class RadioPlay(Lint):
    label = "Radio play"
    description = "Line after line of dialogue with nobody doing anything: it plays like radio."
    settings = {"lines": 3}

    def check(self, scene):
        out, run, since = [], [], 0.0
        for e in sorted((e for e in scene.events if e["kind"] == "say"), key=lambda e: e["t0"]):
            if self._acted(scene, min(since, e["t0"] - self.LEAD_IN), e["t1"]):
                run = []
            else:
                run.append(e)
                if len(run) == self.opts["lines"]:
                    out.append(f"radio play: {len(run)} lines in a row from {_fmt(run[0]['t0'])} to {_fmt(e['t1'])} "
                               f"with nobody doing anything: no gesture, move, look or change of feeling (give "
                               f"someone something to do)")
            since = e["t1"]
        return out

    LEAD_IN = 0.75           # a turn or a look just before a line goes with it

    @staticmethod
    def _acted(scene, t0, t1):
        """Anyone doing anything (not just talking) between t0 and t1."""
        if any(e["kind"] != "say" and e["t0"] < t1 and e["t1"] > t0 for e in scene.events):
            return True
        return any(t0 <= t <= t1 for c in scene.actors.values() for t, _ in getattr(c, "acts", []))


class DeadReaction(Lint):
    label = "Dead reactions"
    description = "Someone in a shot who isn't speaking and never reacts: a listener made of wood."
    settings = {"seconds": 4.0}

    def check(self, scene):
        out = []
        for s, t0, t1 in shots(scene):
            if t1 - t0 <= self.opts["seconds"]:
                continue
            for key in s.subjects or ():
                c = scene.character(key)
                if c is None or not c.visible((t0 + t1) / 2) or busy(scene, c, t0, t1, slack=0.0):
                    continue
                out.append(f"dead reaction: {c.name} is in the {s.label} shot from {_fmt(t0)} to {_fmt(t1)} and "
                           f"never reacts (a look, a nod, a change of feeling)")
        return out


class FootSlide(Lint):
    label = "Sliding feet"
    description = "A foot that should be planted on the ground slides along it (skating)."
    settings = {"speed": 0.15, "drift": 0.02}        # m/s while planted; metres in one contact before it counts

    def check(self, scene):
        from . import handling
        bodies = [c for c in scene.actors.values() if c.foot_points()]
        if not bodies:
            return []
        step = 2 / scene.fps
        times = [i * step for i in range(int(scene.length / step) + 1)]
        tracks = {c: [] for c in bodies}
        for t in times:
            handling.evaluate(scene, t)
            for c in bodies:
                tracks[c].append(c.foot_points())
        out = []
        for c, track in tracks.items():
            skip = [tuple(getattr(c, "_down", ()) or ())] + getattr(c, "contacts", [])
            for i in range(len(track[0])):
                zs = sorted(p[i].z for p in track)
                planted = zs[len(zs) // 10] * 1.15 + 0.01        # an ankle at rest, give or take
                run, drift = [], 0.0
                for k in range(1, len(times) + 1):
                    ok = k < len(times) and track[k][i].z <= planted and track[k - 1][i].z <= planted and \
                        not any(len(w) == 2 and w[0] <= times[k] <= w[1] for w in skip)
                    if ok:
                        a, b = track[k - 1][i], track[k][i]
                        d = ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5
                        ok = d / step > self.opts["speed"]
                    if ok:
                        run.append(times[k])
                        drift += d
                        continue
                    if run and drift > self.opts["drift"]:
                        foot = ("left", "right")[i] if len(track[0]) == 2 else f"number {i + 1}"
                        out.append(f"foot slide: {c.name}'s {foot} foot slides "
                                   f"{drift * 100:.0f} cm while planted from {_fmt(run[0] - step)} to {_fmt(run[-1])}")
                    run, drift = [], 0.0
        return out
