"""Actions: the verbs of a scene. A scene file is a list of beats, and each beat names an action:

    [[beats]]
    who = "mia"
    do = "say"
    line = "Who ate the last cookie?"
    mood = "angry"
    to = "tom"

Every action is a class with `params` (what the studio asks for) and `run(scene, who, **params)`.
Add a new verb by subclassing:

    class Hug(dr.Action):
        label = "hugs"
        description = "Walk up to someone and hug them"
        params = [dr.Param("whom", "character", required=True, label="Who")]

        def run(self, s, who, whom):
            who.walk_to(whom)
            with s.together():
                who.arms_up_at(s.clock)              # use the pose helpers, or dr.keys.key(...)
                s.character(whom).do("cheer")

Scene-level actions (pauses, captions, camera shots) set `scope = "scene"` and get who=None.
"""
from .plugins import Param, Plugin


class Action(Plugin):
    kind = "action"
    abstract = True
    scope = "character"      # "character": a cast member does it; "scene": the scene itself (camera, pause...)
    needs = ()               # body capabilities it needs ("fly", "arms"...); see Character.capabilities
    sentence = None          # how the studio reads a beat back, e.g. "{who} says “{line}”"

    @classmethod
    def describe_extra(cls):
        return {"scope": cls.scope, "sentence": cls.sentence, "needs": list(cls.needs)}

    def run(self, s, who, **params):
        raise NotImplementedError

    @classmethod
    def check(cls, who):
        """Raise a helpful error if `who` can't do this action."""
        if who is None or not cls.needs:
            return
        missing = set(cls.needs) - who.capabilities
        if missing:
            raise ValueError(f"{who.name} can't {cls.label} (needs {', '.join(sorted(missing))})")


# ---------------------------------------------------------------------- characters
class Say(Action):
    label = "says"
    description = "Speak a line: voice, moving mouth and subtitle"
    sentence = "{who} says “{line}”"
    params = [Param("line", "text", required=True, label="Line"), Param("mood", "mood"),
              Param("to", "character", label="To")]

    def run(self, s, who, line, mood=None, to=None):
        who.say(line, mood=mood, to=to)


class WalkTo(Action):
    label = "goes to"
    description = "Walk, swim, slither or hop somewhere, going round furniture"
    sentence = "{who} goes to {where}"
    params = [Param("where", "target", required=True, label="To"),
              Param("speed", "choice", default="normal", choices=("slow", "normal", "fast", "run")),
              Param("facing", "target", label="Then faces")]

    def run(self, s, who, where, speed="normal", facing=None):
        who.walk_to(where, speed=speed, facing=facing)


class RunTo(Action):
    label = "runs to"
    sentence = "{who} runs to {where}"
    params = [Param("where", "target", required=True, label="To")]

    def run(self, s, who, where):
        who.run_to(where)


class FlyTo(Action):
    needs = ("fly",)
    label = "flies to"
    description = "Take off, fly somewhere and land (needs wings)"
    sentence = "{who} flies to {where}"
    params = [Param("where", "target", required=True, label="To"),
              Param("height", "number", default=1.5, min=0.3, max=10, step=0.1, label="Height (m)"),
              Param("land", "bool", default=True, label="Land there")]

    def run(self, s, who, where, height=1.5, land=True):
        if not hasattr(who, "fly_to"):
            raise ValueError(f"{who.name} can't fly")
        who.fly_to(where, height=float(height), land=land)


class LieDown(Action):
    label = "lies down"
    description = "Lie down where they are (animals and other bodies)"
    sentence = "{who} lies down"

    def run(self, s, who):
        if hasattr(who, "lie_down"):
            who.lie_down()
        else:
            raise ValueError(f"{who.name} can't lie down; try sits on")


class Enter(Action):
    label = "comes in at"
    description = "Appear at a spot (usually a door); hidden until then"
    sentence = "{who} comes in at {where}"
    params = [Param("where", "mark", required=True, label="At")]

    def run(self, s, who, where):
        who.enter(where)


class Place(Action):
    label = "is standing at"
    description = "Already standing somewhere when the scene starts"
    sentence = "{who} is standing at {where}"
    params = [Param("where", "target", required=True, label="At"), Param("facing", "target", label="Facing")]

    def run(self, s, who, where, facing=None):
        who.place(where, facing=facing)


class Sit(Action):
    label = "sits on"
    sentence = "{who} sits on {seat}"
    params = [Param("seat", "seat", required=True, label="Seat"),
              Param("already", "bool", default=False, label="Already sitting when the scene starts")]

    def run(self, s, who, seat, already=False):
        who.sit(seat, already=already)


class Stand(Action):
    label = "stands up"
    sentence = "{who} stands up"

    def run(self, s, who):
        who.stand()


class TurnTo(Action):
    label = "turns to"
    sentence = "{who} turns to {target}"
    params = [Param("target", "target", required=True, label="Towards")]

    def run(self, s, who, target):
        who.turn_to(target)


class LookAt(Action):
    label = "looks at"
    description = "Turn the head (not the body)"
    sentence = "{who} looks at {target}"
    params = [Param("target", "target", required=True, label="At")]

    def run(self, s, who, target):
        who.look_at(target)


class Feel(Action):
    label = "feels"
    description = "Change expression"
    sentence = "{who} feels {mood}"
    params = [Param("mood", "mood", required=True, default="happy")]

    def run(self, s, who, mood):
        who.feel(mood)


class DoGesture(Action):
    name = "gesture"
    label = "does"
    description = "Body language: wave, shrug, cheer..."
    sentence = "{who} does {gesture}"
    params = [Param("gesture", "gesture", required=True, default="wave"), Param("target", "target", label="At")]

    def run(self, s, who, gesture, target=None):
        who.do(gesture, target=target)


class Leave(Action):
    label = "leaves"
    description = "Disappear (for example after walking to the door)"
    sentence = "{who} leaves"

    def run(self, s, who):
        who.leave()


# ---------------------------------------------------------------------- the scene
class Wait(Action):
    scope = "scene"
    label = "pause"
    sentence = "pause {seconds} s"
    params = [Param("seconds", "number", default=1.0, min=0.1, max=30, step=0.1, required=True)]

    def run(self, s, who, seconds=1.0):
        s.wait(float(seconds))


class Caption(Action):
    scope = "scene"
    label = "caption on screen"
    sentence = "caption “{text}”"
    params = [Param("text", "text", required=True), Param("duration", "number", default=3.0, min=0.5, max=20, step=0.5)]

    def run(self, s, who, text, duration=3.0):
        s.caption(text, duration=float(duration))


class TitleCard(Action):
    scope = "scene"
    label = "title card before the scene"
    sentence = "title card “{text}”"
    params = [Param("text", "text", required=True), Param("duration", "number", default=2.5, min=0.5, max=10, step=0.5)]

    def run(self, s, who, text, duration=2.5):
        s.title_card(text, duration=float(duration))


class Shot(Action):
    scope = "scene"
    label = "camera shot"
    description = "Choose the camera shot from here on (otherwise dreamreel picks shots itself)"
    sentence = "camera: {shot}"
    params = [Param("shot", "shot", required=True, default="wide"), Param("of", "character", label="Of"),
              Param("other", "character", label="And / onto")]

    def run(self, s, who, shot="wide", of=None, other=None):
        s.cut.shot(shot, of=of, other=other)
