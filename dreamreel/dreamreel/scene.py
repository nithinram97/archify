"""A scene: one set, some cast members, and what they do, in order.

Scenes are usually data (scenes/<NNN_name>.toml): a set, a cast and a list of beats, each naming an
action (see actions.py). That's what the studio edits. The same scene in Python:

    import dreamreel as dr

    s = dr.Scene("kitchen")                 # the set from sets/kitchen.toml
    mia, tom = s.cast("mia", "tom")         # characters from cast/mia.toml and cast/tom.toml
    tom.place("table-left", facing="mia")
    mia.enter("door").walk_to("table")
    mia.say("Who ate the last cookie?", mood="angry", to=tom)
    tom.say("What cookie?", mood="worried")

Time runs forward by itself: each action starts when the previous one ends. To make things happen
at the same time, use `with s.together():`; to pause, `s.wait(1)`. Every action also takes `at=`
(seconds) if you need an exact moment.
"""
import math
import os
from contextlib import contextmanager

import bpy
from mathutils import Vector

from . import _compat, keys, look, plugins, project
from .camera import Director
from .character import Character
from .sets import Set
from .voices import Voices

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None


class BeatError(Exception):
    """A beat in a scene file couldn't be played; `beat` is its index (0-based)."""

    def __init__(self, beat, message):
        super().__init__(message)
        self.beat = beat

CURRENT = None  # the Scene being built (the CLI renders it after the script runs)


def _reset_blender():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    look.reset()


class Scene:
    def __init__(self, set=None, name=None, length=None, lighting=None, time_of_day=None, weather=None,
                 weather_strength=None, style=None):
        global CURRENT
        _reset_blender()
        self.project = project.current()
        self.film = self.project.film if self.project else {}
        self.fps = int(self.film.get("fps", 24))
        self.size = tuple(self.film.get("resolution", (1920, 1080)))
        keys.CLOCK = keys.Clock(self.fps)
        self.name = name or (project.CURRENT_SCENE_NAME or "scene")
        self.bscene = bpy.context.scene
        self.actors = {}
        self.events = []
        self.subtitles = []
        self.captions = []
        self.cards = []
        self._line_sides = {}
        self.clock = 0.0
        self.end_time = 0.0
        self._group = None
        self._beat = None        # index of the beat being played (scene files), for the studio
        self.warps = []          # time effects (slow motion, freezes, jump cuts), applied when finishing
        self.screen_fx = []      # (time, effect, duration, colour) done to the picture in the edit
        self.time_fx = []        # (story start, story end, label) of the time effects, for the timeline
        self.transition = None   # how this scene comes in after the previous one (see editing.py)
        self.fixed_length = length
        self.time_of_day = time_of_day
        self.weather = weather
        self.weather_strength = weather_strength
        self.style = plugins.get("style", style or self.film.get("style") or "toy")()
        self.voices = Voices(self.project.root if self.project else None,
                             engine=self.film.get("voice_engine", "auto"), enabled=self.film.get("voices", True))
        if isinstance(set, dict):
            self.set = Set.create(set, name="set")
        elif set:
            spec = self.project.set_spec(set) if self.project else None
            if spec is None:
                raise ValueError(f"no set called {set!r}: create sets/{set}.toml")
            self.set = Set.create(spec, name=set)
        else:
            self.set = None
        self.cut = Director(self)
        self.camera = self.cut
        self._light(lighting)
        self._render_settings()
        CURRENT = self

    # ------------------------------------------------------------------ cast
    def cast(self, *names, **specs):
        """Bring characters into the scene: by name from cast/<name>.toml, or described inline with
        keyword arguments (s.cast(kid={"hair": "spiky", "top": "yellow"}))."""
        out = []
        for n in names:
            spec = self.project.cast_spec(n) if self.project else None
            if spec is None:
                raise ValueError(f"no cast member called {n!r}: create cast/{n}.toml")
            out.append(self._add_actor(n, spec))
        for n, spec in specs.items():
            out.append(self._add_actor(n, spec))
        for i, c in enumerate(out):  # start somewhere sensible until placed
            if not keys._compat.fcurves(c.root):
                c.root.location = (-1.0 + 2.0 * i / max(1, len(out) - 1), -0.5, 0) if len(out) > 1 else (0, -0.5, 0)
        return out[0] if len(out) == 1 else out

    def _add_actor(self, key_name, spec):
        spec = dict(spec)
        display = spec.pop("name", key_name.capitalize())
        cls = plugins.get("character", spec.pop("type", "toy"))
        c = cls(display, scene=self, **spec)
        c.key = key_name
        self.actors[key_name] = c
        return c

    def character(self, who):
        if isinstance(who, Character):
            return who
        if who in self.actors:
            return self.actors[who]
        for c in self.actors.values():
            if c.name.lower() == str(who).lower():
                return c
        return None

    # ------------------------------------------------------------------ time
    def _now(self):
        return self.clock

    def _start(self, who, at):
        if at is not None:
            return float(at)
        if self._group is not None:
            return max(self._group["t0"], who.busy if who is not None else 0.0)
        return self.clock

    def _end(self, who, end, wait=True):
        if who is not None:
            who.busy = max(who.busy, end)
        self.end_time = max(self.end_time, end)
        if self._group is not None:
            self._group["end"] = max(self._group["end"], end)
        elif wait:
            self.clock = max(self.clock, end)

    @contextmanager
    def together(self):
        """Everything inside starts at the same moment; afterwards time continues from the latest end."""
        if self._group is not None:
            yield
            return
        self._group = {"t0": self.clock, "end": self.clock}
        try:
            yield
        finally:
            g, self._group = self._group, None
            self.clock = max(self.clock, g["end"])

    def wait(self, seconds):
        """A pause: nothing new starts for this long (characters keep breathing and blinking)."""
        self.clock += seconds
        self.end_time = max(self.end_time, self.clock)
        return self

    def at(self, seconds):
        """Jump the scene clock to an exact time."""
        self.clock = float(seconds)
        return self

    @property
    def length(self):
        return self.fixed_length or round(max(self.end_time, self.clock) + 1.2, 2)

    # ------------------------------------------------------------------ scenes as data
    @classmethod
    def from_spec(cls, spec, name=None):
        """Build a scene from a scene file's contents: set, cast, time_of_day and beats."""
        s = cls(spec.get("set"), name=name, time_of_day=spec.get("time_of_day"), weather=spec.get("weather"),
                weather_strength=spec.get("weather_strength"), style=spec.get("style"), length=spec.get("length"))
        cast = spec.get("cast", [])
        if cast:
            s.cast(*cast)
        if spec.get("transition"):
            s.transition = {"name": spec["transition"], "duration": spec.get("transition_duration"),
                            "color": spec.get("transition_color"), "direction": spec.get("transition_direction")}
        s.run_beats(spec.get("beats", []))
        return s

    @classmethod
    def from_file(cls, path, name=None):
        with open(path, "rb") as f:
            spec = tomllib.load(f)
        return cls.from_spec(spec, name=name or os.path.splitext(os.path.basename(path))[0])

    def run_beats(self, beats):
        """Play beats in order. A beat with `with_previous = true` starts together with the one before."""
        groups = []
        for i, b in enumerate(beats):
            if b.get("with_previous") and groups:
                groups[-1].append((i, b))
            else:
                groups.append([(i, b)])
        for g in groups:
            if len(g) == 1:
                self.run_beat(*g[0])
            else:
                with self.together():
                    for i, b in g:
                        self.run_beat(i, b)

    def run_beat(self, i, beat):
        b = dict(beat)
        do = b.pop("do", None)
        who = b.pop("who", None)
        at = b.pop("at", None)
        for k in ("with_previous", "note"):
            b.pop(k, None)
        label = f"Beat {i + 1}"
        try:
            if not do:
                raise ValueError("it doesn't say what happens (do = ...)")
            act = plugins.get("action", do)
            label = f"Beat {i + 1} ({(who + ' ') if who else ''}{act.label})"
            actor = None
            if act.scope == "character":
                if not who:
                    raise ValueError("it doesn't say who does it (who = ...)")
                actor = self.character(who)
                if actor is None:
                    raise ValueError(f"{who!r} isn't in this scene's cast {list(self.actors)}")
            params = {k: v for k, v in b.items() if v not in ("", None)}
            known = {p.name for p in act.params}
            extra = set(params) - known
            if extra:
                raise ValueError(f"{act.label} doesn't take {sorted(extra)}; it takes {sorted(known)}")
            missing = [p.name for p in act.params if p.required and p.name not in params and p.default is None]
            if missing:
                raise ValueError(f"{act.label} needs {missing}")
            if at is not None:
                self.at(float(at))
            self._beat = i
            act.check(actor)
            act().run(self, actor, **params)
            self._beat = None
        except BeatError:
            raise
        except Exception as e:
            raise BeatError(i, f"{label}: {e}") from e

    # ------------------------------------------------------------------ text
    def caption(self, text, at=None, duration=3.0):
        """On-screen text over the picture (not dialogue): 'Meanwhile, next door...'."""
        t = self.clock if at is None else at
        self.captions.append((t, t + duration, text))
        self.end_time = max(self.end_time, t + duration)
        return self

    # ------------------------------------------------------------------ time and picture effects
    def slow_motion(self, seconds=2.0, speed=0.3, ramp=0.3, after=0.0):
        """The next `seconds` of story play at `speed` (0.3 = slow motion, 2 = fast), easing in and out
        over `ramp` seconds. Doesn't move the scene clock: put the action to slow down after it."""
        from . import timewarp
        t = self.clock + after
        self.warps += timewarp.slow_motion(t, seconds, speed, ramp)
        self.time_fx.append((t, t + seconds, f"[{'SLOW MOTION' if speed < 1 else 'FAST'} x{speed:g}]"))
        return self

    def freeze(self, seconds=1.5, after=0.0):
        """Everything stops for `seconds` (a freeze frame), then carries on."""
        from . import timewarp
        self.warps.append(timewarp.Freeze(self.clock + after, seconds))
        self.time_fx.append((self.clock + after, None, f"[FREEZE {seconds:g}s]"))
        return self

    def jump_cut(self, seconds=2.0, after=0.0):
        """Cut `seconds` of story out, `after` seconds from now: the picture jumps ahead."""
        from . import timewarp
        self.warps.append(timewarp.Jump(self.clock + after, seconds))
        self.time_fx.append((self.clock + after, None, f"[JUMP CUT -{seconds:g}s]"))
        return self

    def screen(self, effect="fade_out", duration=None, color=None, after=0.0):
        """Do something to the whole picture: fade_out, fade_in, flash, dip, blackout."""
        from . import plugins as _p
        fx = _p.get("screen", effect)
        t = self.clock + after
        dur = fx.default_duration if duration is None else float(duration)
        self.screen_fx.append((t, effect, dur, color or fx.default_color))
        self.end_time = max(self.end_time, t + dur)
        return self

    def title_card(self, text, duration=2.5, color="black"):
        """A full-screen card shown before this scene: 'Chapter 1', 'Three days later'."""
        self.cards.append((text, duration, color))
        return self

    # ------------------------------------------------------------------ bookkeeping
    def _event(self, kind, who, t0, t1, **kw):
        e = {"kind": kind, "who": who, "t0": t0, "t1": t1, "beat": self._beat, **kw}
        self.events.append(e)
        if kind == "say":
            self.subtitles.append((t0, t1 + 0.2, who.name, kw.get("line", "")))

    def _nearest(self, me, t):
        best = None
        for c in self.actors.values():
            if c is me or not c.visible(t):
                continue
            d = (c.position(t) - me.position(t)).length
            if best is None or d < best[0]:
                best = (d, c)
        return best[1] if best else None

    def _resolve(self, where, t, me=None, approach=False):
        """A character, mark, prop, place name or (x, y) -> a point on the floor."""
        if isinstance(where, Character) or (isinstance(where, str) and self.character(where) is not None
                                            and not (self.set and where in self.set.marks)):
            other = self.character(where)
            p = other.position(t)
            if approach and me is not None:
                d = me.position(t) - p
                d = d.normalized() if d.length > 1e-3 else Vector((0, -1))
                return p + d * 0.75 * max(other.H, me.H)
            return p
        if isinstance(where, (tuple, list)):
            return Vector(where[:2])
        if isinstance(where, Vector):
            return Vector((where.x, where.y))
        if self.set is not None:
            if where in self.set.marks:
                return self.set.marks[where].at.copy()
            if where in self.set.seats:
                return self.set.seats[where].front.copy()
            raise ValueError(f"no mark called {where!r} in set {self.set.name!r}. Marks: "
                             f"{sorted(self.set.marks)}; characters: {sorted(self.actors)}")
        raise ValueError(f"can't find {where!r}")

    # ------------------------------------------------------------------ look
    def _light(self, lighting):
        """The sky, sun, weather and lights: see environment.py."""
        from .environment import Environment
        sp = self.set.spec if self.set is not None else {}
        self.time_of_day = self.time_of_day or sp.get("time_of_day") or "day"
        self.weather = self.weather or sp.get("weather") or "clear"
        k = self.weather_strength if self.weather_strength is not None else sp.get("weather_strength", 1.0)
        self.environment = Environment(self, self.time_of_day, self.weather, k)
        if self.set is not None:
            self.set.adjust_light(self.environment.light)
        self.style.adjust_light(self.environment.light)
        self.environment.build()

    def _render_settings(self):
        sc, r = self.bscene, self.bscene.render
        r.engine = _compat.eevee_engine()
        r.resolution_x, r.resolution_y = self.size
        r.resolution_percentage = 100
        r.fps = self.fps
        ee = sc.eevee
        for attr, val in (("use_shadows", True), ("use_raytracing", True), ("ray_tracing_method", "SCREEN"),
                          ("use_fast_gi", True), ("taa_render_samples", 48), ("use_gtao", True)):
            if hasattr(ee, attr):
                try:
                    setattr(ee, attr, val)
                except (TypeError, ValueError):
                    pass
        try:
            sc.view_settings.view_transform = "AgX"
            sc.view_settings.look = "AgX - Punchy"
        except TypeError:
            pass

    def previz_settings(self):
        """Fast flat-shaded look for checking timing and staging."""
        sc = self.bscene
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_shadows = True
        sh.show_cavity = False
        self.style.previz(sc)
        for o in bpy.data.objects:      # fog volumes and the like only show in the final render
            if o.get("dr_final_only"):
                o.hide_render = True
        try:
            sc.view_settings.view_transform = "Standard"
        except TypeError:
            pass

    # ------------------------------------------------------------------ finish
    def finish(self):
        """Add life (blinks, breathing) and the camera. The CLI calls this; you don't need to."""
        if getattr(self, "_finished", False):
            return
        self._finished = True
        L = self.length
        for c in self.actors.values():
            c.prepare(L)
            c._alive(L)
        self.environment.animate(L)
        if self.set is not None:
            self.set.animate(L)
        self.cut.build()
        if self.warps:
            self._apply_warps()
        self.bscene.frame_start = 1
        self.bscene.frame_end = keys.CLOCK.frame(self.length) - 1   # time effects may have changed it
        self.style.finish(self)
        self.bscene.frame_set(1)

    def _apply_warps(self):
        from . import timewarp
        m = timewarp.apply(self.warps)
        for e in self.events:
            e["t0"], e["t1"] = m(e["t0"]), m(e["t1"])
        self.subtitles = [(m(a), m(b), who, line) for a, b, who, line in self.subtitles]
        self.captions = [(m(a), m(b), text) for a, b, text in self.captions]
        self.screen_fx = [(m(t), fx, d, c) for t, fx, d, c in self.screen_fx]
        self.time_fx = [(m(a), m(b) if b is not None else None, label) for a, b, label in self.time_fx]
        for shot in self.cut.final:
            shot.at = m(shot.at)
        story_end = max(self.end_time, self.clock)
        self.end_time = self.clock = m(story_end)
        if self.fixed_length:
            self.fixed_length = m(self.fixed_length)
        self.warps_applied = [type(w).__name__.lower() for w in self.warps]
        self.warps = []

    def summary(self):
        """A text timeline of the scene: what a director (human or AI) checks before rendering."""
        self.finish()
        air = self.time_of_day.replace("_", " ") + ("" if self.weather == "clear" else f", {self.weather}".replace("_", " "))
        lines = [f"scene {self.name}: {self.length:.1f} s, set {self.set.name if self.set else '-'} ({air}), "
                 f"cast {', '.join(c.name for c in self.actors.values())}"]
        rows = []
        for e in self.events:
            who = e["who"].name
            if e["kind"] == "say":
                to = f" (to {e['listener'].name})" if e.get("listener") else ""
                rows.append((e["t0"], f"{who} says{to}: \"{e['line']}\""))
            elif e["kind"] == "move":
                rows.append((e["t0"], f"{who} moves until {e['t1']:.1f}s"))
            elif e["kind"] == "gesture":
                rows.append((e["t0"], f"{who} {e['gesture']}"))
        for t, label in self.cut.describe():
            rows.append((t, f"[CUT] {label}"))
        for t0, t1, text in self.captions:
            rows.append((t0, f"[CAPTION] {text}"))
        for t0, t1, label in self.time_fx:
            rows.append((t0, label + (f" until {t1:.1f}s" if t1 is not None else "")))
        for t, fx, d, c in self.screen_fx:
            rows.append((t, f"[SCREEN] {fx} ({d:g}s)"))
        for t, text in sorted(rows, key=lambda r: r[0]):
            lines.append(f"  {t:6.2f}s  {text}")
        warnings = self.check()
        lines += [f"  WARNING: {w}" for w in warnings]
        return "\n".join(lines)

    def timeline(self):
        """The scene as data: length, events, camera cuts and warnings (for `check --json`)."""
        self.finish()
        rows = []
        for e in self.events:
            row = {"t": round(e["t0"], 2), "end": round(e["t1"], 2), "kind": e["kind"], "who": e["who"].name,
                   "beat": e.get("beat")}
            if e["kind"] == "say":
                row["line"] = e["line"]
                row["to"] = e["listener"].name if e.get("listener") else None
            elif e["kind"] == "gesture":
                row["gesture"] = e["gesture"]
            rows.append(row)
        for t, label in self.cut.describe():
            rows.append({"t": round(t, 2), "kind": "cut", "shot": label})
        for t0, t1, text in self.captions:
            rows.append({"t": round(t0, 2), "end": round(t1, 2), "kind": "caption", "text": text})
        for t0, t1, label in self.time_fx:
            rows.append({"t": round(t0, 2), "end": round(t1, 2) if t1 is not None else None, "kind": "time",
                         "text": label})
        for t, fx, d, c in self.screen_fx:
            rows.append({"t": round(t, 2), "end": round(t + d, 2), "kind": "screen", "effect": fx})
        rows.sort(key=lambda r: (r["t"], r["kind"] != "cut"))
        return {"length": self.length, "set": self.set.name if self.set else None,
                "cast": [c.name for c in self.actors.values()], "events": rows, "warnings": self.check(),
                "cards": [c[0] for c in self.cards], "time_of_day": self.time_of_day, "weather": self.weather}

    def check(self):
        """Things that will probably look wrong."""
        out = []
        names = list(self.actors.values())
        for t in [i * 0.5 for i in range(int(self.length * 2))]:
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    if a.visible(t) and b.visible(t) and (a.position(t) - b.position(t)).length < 0.35 * max(a.H, b.H):
                        out.append(f"{a.name} and {b.name} overlap at {t:.1f}s")
                        break
        seen = set()
        return [w for w in out if not (w.split(" at ")[0] in seen or seen.add(w.split(" at ")[0]))]

    def metadata(self):
        return {
            "name": self.name, "length": self.length, "fps": self.fps,
            "subtitles": [list(s) for s in self.subtitles],
            "captions": [list(c) for c in self.captions],
            "cards": [list(c) for c in self.cards],
            "audio": [[e["t0"], e["audio"].path] for e in self.events if e["kind"] == "say" and e.get("audio")],
            "shots": self.cut.describe(),
            "screen": [list(x) for x in self.screen_fx],
            "transition": self.transition,
            "time_of_day": self.time_of_day, "weather": self.weather, "style": self.style.name,
        }
