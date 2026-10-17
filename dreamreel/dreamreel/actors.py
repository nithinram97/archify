"""People and animals from Quaternius's free (CC0) packs, acting with their own animation.

    # cast/mia.toml
    type = "person"
    body = "woman"            # woman or man
    outfit = "casual"         # see `dreamreel assets` (casual, formal, suit, worker, punk, witch, ...)
    height = 1.65             # metres

    # cast/rex.toml
    type = "animal"
    species = "husky"         # alpaca, bull, cow, deer, donkey, fox, horse, horse_white, husky,
                              # shiba_inu, stag, wolf
    size = 1.0

Quaternius's characters and animals come rigged with their own clips (idle, walk, run, wave,
interact, punch, kick, eat, attack, death...). A clip actor is moved round the set by dreamreel
(paths round furniture, turns, marks) while its clips play in time with it, blended into each
other: walking or running at the speed it travels, idling when still. Gestures that have a clip
play it (`do = "wave"`, "punch", "eat"); the head turns to look at people and nods; hands hold
things. The models come from `dreamreel assets --download` (see quaternius.py).
"""
import math

import bpy
from mathutils import Matrix, Vector

from . import keys, plugins, quaternius, shapes
from .character import Character
from .gestures import Gesture
from .keys import hold, key, value_at
from .plugins import Param

# dreamreel's clip names -> names used in the files (first that exists; ".001" suffixes ignored)
CLIPS = {
    "idle": ("Idle", "Idle_Loop", "Idle_Neutral"), "idle_2": ("Idle_2", "Idle_Neutral"),
    "walk": ("Walk", "Walk_Loop"), "run": ("Run", "Gallop", "Jog_Fwd_Loop", "Sprint_Loop"),
    "wave": ("Wave",), "interact": ("Interact", "PickUp_Table"), "pick_up": ("PickUp_Table", "Interact"),
    "punch": ("Punch_Right", "Punch_Cross", "Punch_Jab"), "kick": ("Kick_Right", "Kick_Left"),
    "die": ("Death", "Death01"), "flinch": ("HitRecieve", "Hit_Chest", "Idle_HitReact1", "HitReact"),
    "roll": ("Roll",), "dance": ("Dance_Loop",), "talk": ("Idle_Talking_Loop",), "push": ("Push_Loop",),
    "jump": ("Jump", "Gallop_Jump", "Jump_ToIdle"), "eat": ("Eating",), "attack": ("Attack", "Sword_Slash"),
    "look_down": ("Idle_2_HeadLow",), "sit": ("Sitting_Idle_Loop",),
}
GAITS = ("walk", "run")


def _base(name):
    return name.split("|")[-1].split(".")[0]


def _cycle(arm, act, feet):
    """How far one cycle of an on-the-spot walk or run carries the actor and how long it takes."""
    fps = keys.CLOCK.fps
    f0, f1 = act.frame_range
    dur = max(1e-3, (f1 - f0) / fps)
    if not feet:
        return {"stride": 0.6, "duration": dur, "speed": 0.6 / dur}
    ad = arm.animation_data or arm.animation_data_create()
    old = ad.action
    ad.action = act
    scene = bpy.context.scene
    ranges = []
    for n in feet:
        b = arm.pose.bones[n]
        ys = []
        for f in range(int(f0), int(f1) + 1):
            scene.frame_set(f)
            ys.append((arm.matrix_world @ b.tail).y)
        ranges.append(max(ys) - min(ys))
    ad.action = old
    scene.frame_set(1)
    # a foot is on the ground about 60% of a cycle, sliding back all the while
    stride = max(0.05, sum(ranges) / len(ranges) / 0.6)
    return {"stride": stride, "duration": dur, "speed": stride / dur}


class ClipGesture(Gesture):
    """A gesture played from an actor's own clip."""
    abstract = True
    clip = None

    def perform(self, c, t, target=None):
        return c.play(self.clip, t)


for _name in ("punch", "kick", "dance", "roll", "interact", "eat", "attack", "die", "flinch", "look_down", "talk"):
    type(_name.title().replace("_", ""), (ClipGesture,), {
        "name": _name, "label": _name.replace("_", " ").capitalize(), "clip": _name, "needs": (_name,),
        "description": f"{_name.replace('_', ' ').capitalize()} (people and animals with that animation)"})


class ClipActor(Character):
    """A rigged model that acts with its own clips (see the module docs)."""
    abstract = True
    drawing = None
    foot_names = ("FF.L", "FFB.L", "foot_l", "Foot.L", "ball_l")
    hand_names = {1: ("hand_l", "Wrist.L", "Hand.L"), -1: ("hand_r", "Wrist.R", "Hand.R")}
    head_names = ("Head", "head")

    def model_file(self):
        raise NotImplementedError

    @property
    def capabilities(self):
        caps = {"walk", "head"} | set(getattr(self, "clip_names", {}))
        if getattr(self, "hands", None):
            caps.add("hands")
        return caps

    # ------------------------------------------------------------------ build
    def build(self):
        from .models import import_file, keep_character, world_points
        n = self.name
        before = set(bpy.data.actions)
        objs = import_file(self.model_file(), keep_actions=True)
        arm, meshes = keep_character(objs)
        if arm is None or not meshes:
            raise ValueError(f"{self.name}: the model has no rig")
        for o in objs:                                   # stray helpers (Quaternius files carry an icosphere)
            if o.type == "MESH" and o not in meshes:
                bpy.data.objects.remove(o, do_unlink=True)
        clips = [a for a in bpy.data.actions if a not in before]
        for a in clips:
            a.use_fake_user = True
        self.clip_names = {}
        for ours, theirs in CLIPS.items():
            for nm in theirs:
                match = next((a for a in clips if _base(a.name) == nm), None)
                if match is not None:
                    self.clip_names[ours] = match
                    break
        self.root = shapes.empty(n)
        self.root.empty_display_size = 0.3
        holder = shapes.empty(f"{n}.model", self.root)
        bpy.context.view_layer.update()
        for o in [arm] + meshes:
            if o.parent is None or o.parent not in meshes + [arm]:
                mw = o.matrix_world.copy()
                o.parent = holder
                o.matrix_world = mw
        pts = world_points(meshes)
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        k = self.H / max(1e-6, hi.z - lo.z)
        holder.matrix_world = Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))
        bpy.context.view_layer.update()
        self.rig, self.meshes, self.holder = arm, meshes, holder
        self.body_length = (hi.y - lo.y) * k
        # dreamreel's pivots: the neck pivot turns the head (looks, nods); the clips do the rest
        self.hip_z = 0.0
        self.hips = shapes.empty(f"{n}.hips", self.root)
        self.body = shapes.empty(f"{n}.body", self.hips)
        head = next((arm.data.bones[h] for h in self.head_names if h in arm.data.bones), None)
        hp = arm.matrix_world @ head.head_local if head else Vector((0, 0, self.H * 0.9))
        self.neck = shapes.empty(f"{n}.neck", self.body, hp)
        self.head_offset = Vector(hp)
        self.top_z = self.neck_z = hp.z
        self.hr = self.head_r = max(0.05, (self.H - hp.z) * 0.6) if self.H - hp.z > 0.05 else self.H * 0.08
        self.hc = self.head_center = Vector((0, 0, self.hr * 0.6))
        if head:
            c = arm.pose.bones[head.name].constraints.new("COPY_ROTATION")
            c.target, c.mix_mode, c.owner_space, c.target_space = self.neck, "ADD", "LOCAL", "LOCAL"
        self.mouth = shapes.empty(f"{n}.mouth", self.neck)       # talking keys it; nothing to show
        self.arms, self.legs, self.eyes, self.brows, self.holding = {}, {}, [], {}, {}
        self.hands = {}
        for side, names in self.hand_names.items():
            b = next((nm for nm in names if nm in arm.data.bones), None)
            if b:
                h = shapes.empty(f"{n}.hand.{'L' if side > 0 else 'R'}")
                h.parent, h.parent_type, h.parent_bone = arm, "BONE", b
                h.location = (0, 0, 0)
                self.hands[side] = h
        arm.animation_data_create()
        arm.animation_data.action = None
        self.segments = []
        feet = [f for f in self.foot_names if f in arm.data.bones][:2]
        self.gait = {g: _cycle(arm, self.clip_names[g], feet) for g in GAITS if g in self.clip_names}

    def build_rig(self):
        pass

    # ------------------------------------------------------------------ clips on the timeline
    def play(self, clip, t, rate=1.0, until=None, hold_end=False, blend=0.2):
        """Play one of its clips from t (once, or looped until `until`); returns when it ends."""
        act = clip if isinstance(clip, bpy.types.Action) else self.clip_names.get(clip)
        if act is None:
            raise ValueError(f"{self.name} has no {clip!r} animation (it has: {', '.join(sorted(self.clip_names))})")
        f0, f1 = act.frame_range
        dur = (f1 - f0) / keys.CLOCK.fps / rate
        end = until if until is not None else t + dur
        self.segments.append((t, end, act, rate, hold_end or clip == "die", blend))
        return end

    def do(self, gesture, target=None, at=None, wait=True, how=None):
        if gesture in self.clip_names:
            t = self._start(at)
            end = self.play(gesture, t)
            self.scene._event("gesture", self, t, end, gesture=gesture, how=how)
            return self._end(end, wait)
        return super().do(gesture, target=target, at=at, wait=wait, how=how)

    def animate_steps(self, path, n_steps, step_t, run):
        gait = "run" if run and "run" in self.clip_names else "walk"
        cycle = self.gait.get(gait)
        speed = path.total / max(1e-6, path.end - path.start)
        rate = speed / cycle["speed"] if cycle else 1.0
        self.play(gait, path.start, rate=max(0.3, min(3.0, rate)), until=path.end)

    def gait_timing(self, speed, run):
        """A stride of its own walk (or run), at its natural pace."""
        cycle = self.gait.get("run" if run and "run" in self.gait else "walk")
        if not cycle:
            return 0.5 * self.H, 0.4
        return cycle["stride"] / 2, cycle["duration"] / 2 / max(0.4, min(2.0, speed))

    def prepare(self, length):
        """Lay the clips out on the timeline (blended NLA strips), idling in between."""
        super().prepare(length)
        fps = keys.CLOCK.fps
        segs = sorted(((t0, min(t1, max(length, t0 + 1 / fps)), *rest) for t0, t1, *rest in self.segments),
                      key=lambda s: s[0])
        for i in range(len(segs) - 1):              # when clips overlap, the later one takes over
            t0, t1, act, rate, hold_end, bl = segs[i]
            if t1 > segs[i + 1][0]:
                segs[i] = (t0, max(t0 + 1 / fps, segs[i + 1][0]), act, rate, False, bl)
        idle = self.clip_names.get("idle")
        filled, t, dead = [], 0.0, False
        for s in segs:
            if s[0] > t + 0.05 and idle is not None and not dead:
                filled.append((t, s[0], idle, 1.0, False, 0.2))
            filled.append(s)
            t = max(t, s[1])
            dead = dead or s[4]
        if t < length and idle is not None and not dead:
            filled.append((t, length, idle, 1.0, False, 0.2))
        ad = self.rig.animation_data
        for i, (t0, t1, act, rate, hold_end, blend) in enumerate(filled):
            blend *= fps
            f0, f1 = act.frame_range
            track = ad.nla_tracks.new()                 # one track each: later ones blend in over earlier
            strip = track.strips.new(f"{_base(act.name)}.{i}", int(keys.CLOCK.frame(t0)), act)
            strip.action_frame_start, strip.action_frame_end = f0, f1
            strip.scale = 1.0 / rate
            span = max(1.0, (t1 - t0) * fps)
            strip.repeat = 1.0 if hold_end else max(0.05, span / max(1e-6, (f1 - f0) / rate))
            strip.blend_in = min(blend, span * 0.4) if i else 0.0
            last = hold_end or i == len(filled) - 1
            strip.extrapolation = "HOLD_FORWARD" if last else "NOTHING"
            strip.use_auto_blend = False

    # ------------------------------------------------------------------ sitting
    def _sit_clip(self, height):
        """A seated pose for a seat `height` high, made on the rig (the packs have no sitting clip):
        the idle pose, the body lowered onto the seat, thighs forward, shins down to the floor."""
        name = f"{self.name}.sit.{height:.2f}"
        if name in bpy.data.actions:
            return bpy.data.actions[name]
        arm = self.rig
        bones = arm.data.bones
        legs = {sd: (f"UpperLeg.{sd}", f"LowerLeg.{sd}", f"Foot.{sd}") for sd in "LR"}
        if "Body" not in bones or not all(b in bones for chain in legs.values() for b in chain):
            return None
        ad = arm.animation_data
        ad.action = self.clip_names.get("idle")
        scene = bpy.context.scene
        scene.frame_set(int(ad.action.frame_range[0]) if ad.action else 1)
        bpy.context.view_layer.update()
        # actor space (the root's): metres, z up, facing -y
        to_arm = (self.root.matrix_world.inverted() @ arm.matrix_world).inverted()
        from_arm = to_arm.inverted()
        pb = arm.pose.bones

        def head(b):
            return from_arm @ pb[b].head

        def tail(b):
            return from_arm @ pb[b].tail

        def aim(b, new_head, direction):
            rest = pb[b].matrix.copy()
            cur = (tail(b) - head(b)).normalized()
            q = cur.rotation_difference(direction.normalized())
            rot = (to_arm.to_quaternion() @ q @ from_arm.to_quaternion()).to_matrix().to_4x4()
            m = rot @ Matrix.Translation(-rest.translation) @ rest
            m.translation = to_arm @ new_head
            pb[b].matrix = m
            bpy.context.view_layer.update()

        hip = head(legs["L"][0])
        drop = Vector((0, 0.04 * self.H, height + 0.03 * self.H - hip.z))
        body = pb["Body"].matrix.copy()
        body.translation = to_arm @ (head("Body") + drop)
        pb["Body"].matrix = body
        bpy.context.view_layer.update()
        floor = min(head(chain[2]).z for chain in legs.values())
        for sd, (up, low, foot) in legs.items():
            thigh = (tail(up) - head(up)).length
            shin = (tail(low) - head(low)).length
            aim(up, head(up), Vector((0, -1, -0.08)))
            knee = tail(up)
            fall = knee.z - floor
            reach = math.sqrt(max(0.0, shin * shin - fall * fall)) if shin > fall else 0.0
            ankle = Vector((knee.x, knee.y - reach * 0.35, max(floor, knee.z - shin)))
            aim(low, knee, ankle - knee)
            fm = pb[foot].matrix.copy()
            fm.translation = to_arm @ tail(low)
            pb[foot].matrix = fm
            bpy.context.view_layer.update()
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        ad.action = act
        for b in pb:
            for f in (1, 25):
                b.keyframe_insert("location", frame=f)
                b.keyframe_insert("rotation_quaternion", frame=f)
        ad.action = None
        for b in pb:
            b.matrix_basis = Matrix()
        return act

    def sit(self, on, at=None, wait=True, already=False):
        """Walk to a seat, turn round and sit down (a seated pose made for the seat's height)."""
        super().sit(on, at=at, wait=wait, already=already)
        seat = self.sitting
        act = self._sit_clip(seat.height)
        if act is not None:
            t = (0.0 if at is None else at) if already else self.busy - 0.45
            self.play(act, t, until=math.inf, blend=0.0 if already else 0.4)
            self._seated = len(self.segments) - 1
        return self

    def stand(self, at=None, wait=True):
        if not self.sitting:
            return self
        i = getattr(self, "_seated", None)
        super().stand(at=at, wait=wait)
        if i is not None:
            t0, _, act, rate, hold_end, blend = self.segments[i]
            t = self.busy - 0.45
            self.segments[i] = (t0, t, act, rate, hold_end, blend)
            self.play("idle", t, until=t + 0.5, blend=0.35)
            self._seated = None
        return self

    # ------------------------------------------------------------------ handling things
    def _hand(self, hand=None, holding=None):
        if not self.hands:
            raise ValueError(f"{self.name} has no hands to hold things with")
        if holding is not None:
            side = next((s for s, n in self.holding.items() if n == holding), None)
            if side is None:
                raise ValueError(f"{self.name} isn't holding {holding!r}")
            return side
        if hand in ("left", 1, "right", -1):
            return 1 if hand in ("left", 1) else -1
        free = [s for s in (-1, 1) if s in self.hands and s not in self.holding]
        if not free:
            raise ValueError(f"{self.name}'s hands are full: put something down first")
        return free[0]

    def _take(self, thing, side, t):
        from . import handling
        th = self.scene.thing(thing) if isinstance(thing, str) else thing
        handling.attach(self.scene, th, self.hands[side], t)
        self.holding[side] = th.name
        th.holder = (self, side)
        return th

    def pick_up(self, thing, hand=None, at=None, wait=True):
        """Walk over, reach (its interact or pick-up clip) and take it."""
        from . import handling
        th = self.scene.thing(thing)
        side = self._hand(hand)
        t = self._start(at)
        p = handling.thing_point(self.scene, th, t)
        if (self.position(t) - p.to_2d()).length > 0.55 * self.H:
            self.walk_to(th.approach or (p.x, p.y), at=t, wait=True)
            t = max(self.busy, t)
        self.turn_to((p.x, p.y), at=t, wait=True)
        t = max(self.busy, t)
        clip = "pick_up" if "pick_up" in self.clip_names else "interact"
        end = self.play(clip, t) if clip in self.clip_names else t + 0.6
        self._take(th, side, t + (end - t) * 0.45)
        self.scene._event("handle", self, t, end, action="picks up", thing=th.name)
        return self._end(end, wait)

    def hold(self, thing, hand=None, at=None):
        from . import handling
        t = 0.0 if at is None else at
        side = self._hand(hand)
        th = self.scene.thing(thing, create=True)
        handling.evaluate(self.scene, t)
        if th.character is None:
            keys.key(th.root, "location", t, tuple(self.hands[side].matrix_world.translation), "cut")
        self._take(th, side, t)
        return self

    def put_down(self, thing=None, on=None, at=None, wait=True):
        """Put what's held down: on a surface (walking there) or the floor in front."""
        from . import handling
        name = self._held(thing)
        side = self._hand(holding=name)
        th = self.scene.thing(name)
        t = self._start(at)
        if on is not None:
            cx, cy, h = self.scene.set.surfaces[on]
            if on in self.scene.set.marks:
                self.walk_to(on, at=t, wait=True)
                t = max(self.busy, t)
            here = self.position(t)
            d = Vector((cx, cy)) - here
            spot = here + d.normalized() * min(d.length, 0.45 * self.H) if d.length > 1e-3 else here
            point = (spot.x, spot.y, h)
        else:
            h = self.heading(t) or 0.0
            spot = self.position(t) + Vector((math.sin(h), -math.cos(h))) * 0.35 * self.H
            point = (spot.x, spot.y, 0.0)
        end = self.play("interact", t) if "interact" in self.clip_names else t + 0.6
        handling.release(self.scene, th, t + (end - t) * 0.5, at=point, heading=self.heading(t))
        del self.holding[side]
        self.scene._event("handle", self, t, end, action="puts down", thing=name)
        return self._end(end, wait)

    def give(self, to, thing=None, at=None, wait=True):
        name = self._held(thing)
        side = self._hand(holding=name)
        other = self.scene.character(to) if isinstance(to, str) else to
        t = self._start(at)
        self._approach = "close"
        try:
            self.walk_to(other.name, at=t, wait=True)
        finally:
            self._approach = True
        t = max(self.busy, other.busy, t)
        other.turn_to(self.name, at=t, wait=False)
        end = self.play("interact", t) if "interact" in self.clip_names else t + 0.6
        oside = other._hand()
        th = self.scene.thing(name)
        from . import handling
        handling.attach(self.scene, th, other.hands[oside], t + (end - t) * 0.5)
        del self.holding[side]
        other.holding[oside] = name
        th.holder = (other, oside)
        self.scene._event("handle", self, t, end, action=f"gives {name} to {other.name}", thing=name)
        return self._end(end, wait)

    # ------------------------------------------------------------------ the rest of Character
    def head_point(self, t):
        loc = Vector(value_at(self.root, "location", t))
        h = value_at(self.root, "rotation_euler", t)[2]
        return loc + Matrix.Rotation(h, 3, "Z") @ (self.head_offset + Vector((0, 0, self.hr * 0.4)))

    def height(self):
        return self.H

    def length(self):
        return self.body_length

    def feel(self, mood, at=None, wait=False, how_much=1.0):
        """Moods show in how they move: the head goes down when sad, up when proud or happy."""
        m = plugins.get("mood", mood)
        t = self._start(at)
        self._moods = sorted(getattr(self, "_moods", []) + [(t, mood, float(how_much or 1.0))], key=lambda x: x[0])
        hold(self.neck, "rotation_euler", t)
        cur = value_at(self.neck, "rotation_euler", t)
        key(self.neck, "rotation_euler", t + 0.3, (math.radians(getattr(m, "head_tilt", 0.0)) * 0.8, cur[1], cur[2]))
        self.mood = mood
        return self._end(t + 0.3, wait)

    def build_face(self):
        pass

    def _alive(self, length):
        pass


class Person(ClipActor):
    """A person from Quaternius's character packs."""
    name = "person"
    label = "Person"
    description = "A person (Quaternius characters): women and men in many outfits, with their own animation"
    params = [
        Param("name", "text", label="Name"),
        Param("body", "choice", default="woman", choices=("woman", "man")),
        Param("outfit", "outfit", default="casual", label="Outfit"),
        Param("height", "number", default=None, min=0.5, max=2.2, step=0.01, label="Height (m)"),
        Param("voice", "voice"),
    ]

    def validate(self):
        body, outfit = self.get("body", "woman"), str(self.get("outfit", "casual")).lower()
        have = outfits(body)
        if not have:
            raise ValueError(f"{self.name}: people need Quaternius's characters: `dreamreel assets --download`")
        if outfit not in have:
            raise ValueError(f"{self.name}: no {body} outfit {outfit!r}; there are: {', '.join(sorted(have))}")

    def proportions(self):
        body = self.get("body", "woman")
        self.H = float(self.get("height") or (1.68 if body == "woman" else 1.8))

    def model_file(self):
        return outfits(self.get("body", "woman"))[str(self.get("outfit", "casual")).lower()]


def outfits(body):
    """{outfit name: model file} for women or men."""
    pack = "women" if body == "woman" else "men"
    out = {}
    for name, path in quaternius.files(pack).items():
        out[name.lower().replace("casual_2", "casual").replace("casual_hoodie", "hoodie")] = path
    return out


ANIMAL_HEIGHTS = {"alpaca": 1.75, "bull": 1.65, "cow": 1.55, "deer": 1.35, "donkey": 1.35, "fox": 0.45,
                  "horse": 2.1, "horse_white": 2.1, "husky": 0.75, "shiba_inu": 0.5, "stag": 1.7, "wolf": 0.85}


def species():
    """{species: model file} for every animal installed."""
    out = {}
    for name, path in quaternius.files("animals").items():
        key_ = "".join("_" + ch.lower() if ch.isupper() and i and name[i - 1].islower() else ch.lower()
                       for i, ch in enumerate(name)).replace("-", "_")
        out[key_] = path
    return out


class Animal(ClipActor):
    """An animal from Quaternius's animal packs."""
    name = "animal"
    label = "Animal"
    description = "An animal (Quaternius): dog, wolf, fox, horse, deer, cow... with its own walks and actions"
    params = [
        Param("name", "text", label="Name"),
        Param("species", "species", required=True, label="Species"),
        Param("size", "number", default=1.0, min=0.2, max=3.0, step=0.05),
        Param("voice", "voice"),
    ]

    def validate(self):
        sp = str(self.spec.get("species") or "").lower()
        have = species()
        if sp not in have:
            raise ValueError(f"{self.name}: no animal {sp!r}. "
                             + (f"Installed: {', '.join(sorted(have))}" if have else
                                "Run `dreamreel assets --download` (free CC0 animals by Quaternius)"))

    def proportions(self):
        self.species = str(self.spec["species"]).lower()
        self.H = ANIMAL_HEIGHTS.get(self.species, 1.0) * float(self.get("size", 1.0) or 1.0)

    def model_file(self):
        return species()[self.species]

