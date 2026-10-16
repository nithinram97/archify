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
from .acting import HOW
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
              Param("facing", "target", label="Then faces"), HOW]

    def run(self, s, who, where, speed="normal", facing=None, how=None):
        who.walk_to(where, speed=speed, facing=facing, how=how)


class RunTo(Action):
    label = "runs to"
    sentence = "{who} runs to {where}"
    params = [Param("where", "target", required=True, label="To"), HOW]

    def run(self, s, who, where, how=None):
        who.run_to(where, how=how)


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
    params = [Param("where", "target", required=True, label="At"), Param("facing", "target", label="Facing"),
              Param("on", "surface", label="On top of")]

    def run(self, s, who, where, facing=None, on=None):
        who.place(where, facing=facing, on=on)


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
    params = [Param("gesture", "gesture", required=True, default="wave"), Param("target", "target", label="At"), HOW]

    def run(self, s, who, gesture, target=None, how=None):
        who.do(gesture, target=target, how=how)


class Perform(Action):
    label = "performs"
    description = "Play a motion-capture clip from the film's motion library (motions/)"
    sentence = "{who} performs {motion}"
    needs = ("arms",)
    params = [Param("motion", "motion", required=True, label="Motion"),
              Param("speed", "number", default=1.0, min=0.2, max=3, step=0.1),
              Param("mirror", "bool", default=False, label="Mirror (left is right)"),
              Param("in_place", "bool", default=False, label="On the spot"),
              Param("start", "number", label="From (s)"), Param("end", "number", label="To (s)"), HOW]

    def run(self, s, who, motion, speed=1.0, mirror=False, in_place=False, start=None, end=None, how=None):
        who.perform(motion, speed=speed, mirror=mirror, in_place=in_place, start=start, end=end, how=how)


class Hold(Action):
    label = "is holding"
    description = "Holding something from this moment (a thing in the set, or a new item such as a scalpel)"
    sentence = "{who} is holding {thing}"
    needs = ("arms",)
    params = [Param("thing", "thing", required=True, label="What"),
              Param("hand", "choice", default=None, choices=("right", "left"))]

    def run(self, s, who, thing, hand=None):
        who.hold(thing, hand=hand, at=s._start(who, None))


class PickUp(Action):
    label = "picks up"
    description = "Walk over, reach and pick something up"
    sentence = "{who} picks up {thing}"
    needs = ("arms",)
    params = [Param("thing", "thing", required=True, label="What"),
              Param("hand", "choice", default=None, choices=("right", "left"))]

    def run(self, s, who, thing, hand=None):
        who.pick_up(thing, hand=hand)


class Grab(Action):
    label = "grabs"
    description = "Grab a small character (a frog, a cat...) and hold it"
    sentence = "{who} grabs {thing}"
    needs = ("arms",)
    params = [Param("thing", "character", required=True, label="Who"),
              Param("hand", "choice", default=None, choices=("right", "left"))]

    def run(self, s, who, thing, hand=None):
        who.grab(thing, hand=hand)


class PutDown(Action):
    label = "puts down"
    description = "Put what they're holding down: on a table, bench or tray, or on the floor"
    sentence = "{who} puts down {thing}"
    needs = ("arms",)
    params = [Param("thing", "thing", label="What (what they hold)"), Param("on", "surface", label="On")]

    def run(self, s, who, thing=None, on=None):
        who.put_down(thing, on=on)


class Give(Action):
    label = "gives"
    description = "Hand what they're holding to someone"
    sentence = "{who} gives {thing} to {to}"
    needs = ("arms",)
    params = [Param("to", "character", required=True, label="To"), Param("thing", "thing", label="What")]

    def run(self, s, who, to, thing=None):
        who.give(to, thing=thing)


class Drop(Action):
    label = "drops"
    description = "Let go: it falls to the floor"
    sentence = "{who} drops {thing}"
    needs = ("arms",)
    params = [Param("thing", "thing", label="What")]

    def run(self, s, who, thing=None):
        who.drop(thing)


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


class SlowMotion(Action):
    scope = "scene"
    label = "slow motion"
    description = "The next moments play slowly (put the action after it)"
    sentence = "slow motion {seconds} s at {speed}x"
    params = [Param("seconds", "number", default=2.0, min=0.2, max=20, step=0.1, label="For (story seconds)"),
              Param("speed", "number", default=0.3, min=0.05, max=4, step=0.05, label="Speed (1 = normal)"),
              Param("ramp", "number", default=0.3, min=0, max=3, step=0.1, label="Ease in/out (s)"),
              Param("after", "number", default=0.0, min=0, max=30, step=0.1, label="Starting after (s)")]

    def run(self, s, who, seconds=2.0, speed=0.3, ramp=0.3, after=0.0):
        s.slow_motion(float(seconds), float(speed), float(ramp), float(after))


class FreezeFrame(Action):
    scope = "scene"
    label = "freeze frame"
    description = "Everything stops for a moment, then carries on"
    sentence = "freeze {seconds} s"
    params = [Param("seconds", "number", default=1.5, min=0.2, max=20, step=0.1),
              Param("after", "number", default=0.0, min=0, max=30, step=0.1, label="Starting after (s)")]

    def run(self, s, who, seconds=1.5, after=0.0):
        s.freeze(float(seconds), float(after))


class JumpCut(Action):
    scope = "scene"
    label = "jump cut"
    description = "Cut a stretch of story out: the picture jumps ahead"
    sentence = "jump cut {seconds} s"
    params = [Param("seconds", "number", default=2.0, min=0.2, max=60, step=0.1, label="Cut out (s)"),
              Param("after", "number", default=0.5, min=0, max=30, step=0.1, label="Starting after (s)")]

    def run(self, s, who, seconds=2.0, after=0.5):
        s.jump_cut(float(seconds), float(after))


class Screen(Action):
    scope = "scene"
    label = "screen effect"
    description = "Fade out, fade in, flash, dip or black out the picture"
    sentence = "screen: {effect}"
    params = [Param("effect", "screen", required=True, default="fade_out"),
              Param("duration", "number", min=0.1, max=10, step=0.1, label="Seconds"),
              Param("color", "color", label="Colour"),
              Param("after", "number", default=0.0, min=0, max=30, step=0.1, label="Starting after (s)")]

    def run(self, s, who, effect="fade_out", duration=None, color=None, after=0.0):
        s.screen(effect, duration, color, float(after))


class Shot(Action):
    scope = "scene"
    label = "camera shot"
    description = "Choose the camera from here on: framing, angle, side, tilt, lens and move"
    sentence = "camera: {shot}"
    params = [Param("shot", "shot", required=True, default="wide", label="Framing"),
              Param("of", "target", label="Of"),
              Param("other", "target", label="And / onto"),
              Param("angle", "choice", default=None, choices=("eye_level", "high", "low", "birds_eye", "worms_eye")),
              Param("side", "choice", default=None, choices=("auto", "front", "three_quarter", "profile", "back")),
              Param("move", "move", label="Camera move"),
              Param("amount", "number", label="Move amount"),
              Param("to", "target", label="Move / focus to"),
              Param("handheld", "bool", default=False, label="Handheld"),
              Param("dutch", "number", min=-45, max=45, step=1, label="Dutch tilt (°)"),
              Param("lens", "number", min=10, max=200, step=1, label="Lens (mm)"),
              Param("duration", "number", min=0.5, max=60, step=0.5, label="Then back to automatic after (s)")]

    def run(self, s, who, shot="wide", of=None, other=None, angle=None, side=None, move=None, amount=None,
            to=None, handheld=False, dutch=None, lens=None, duration=None):
        s.cut.shot(shot, of=of, other=other, angle=angle, side=side, move=move, amount=amount, to=to,
                   handheld=handheld, dutch=dutch, lens=lens, duration=duration)
