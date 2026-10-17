"""The camera, and every camera move you will need.

The camera always looks at a *target* point, so you describe shots like a director:
"stand here, look there". Positions are (x, y, z); inside a shot they are relative to that shot.

    cam = movie.camera
    cam.place((0, -12, 1), look_at=(0, 0, 0))                       # starting position
    cam.push_in(to=(0, -7, 0.5), at=0, duration=4)                   # slow push towards the subject
    cam.orbit(center=(0, 0, 0), radius=9, start=-30, end=30, at=4, duration=3)
    cam.cut_to((20, -10, 2), look_at=(20, 0, 0), at=7)               # hard cut to another place

Moves (all take `at` and `duration` in seconds and an `ease`):
    place / move / cut_to / push_in / pull_out / orbit / crane / dolly_zoom / follow_path /
    shake / zoom (lens) / focus (depth of field)
"""
import math
import random

import bpy
from mathutils import Vector

from .keys import key, value_at
from .stage import STAGE


class Camera:
    def __init__(self, lens=35.0, name="Camera"):
        data = bpy.data.cameras.new(name)
        data.lens = lens
        data.sensor_fit = "HORIZONTAL"
        data.sensor_width = 36
        data.clip_start = 0.05
        data.clip_end = 1000
        self.obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.scene.camera = self.obj
        self.target = bpy.data.objects.new(name + " target", None)
        bpy.context.scene.collection.objects.link(self.target)
        c = self.obj.constraints.new("TRACK_TO")
        c.target = self.target
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        self._pos = Vector((0, -12, 0))
        self._look = Vector((0, 0, 0))
        self.obj.location, self.target.location = self._pos, self._look

    # ------------------------------------------------------------------ basics
    def _now(self, at):
        """Where the camera is and what it looks at, at `at` seconds (from the keys set so far)."""
        return Vector(value_at(self.obj, "location", at)), Vector(value_at(self.target, "location", at))

    def _key(self, at, pos, look, ease):
        key(self.obj, "location", at, pos, ease)
        key(self.target, "location", at, look, ease)
        self._pos, self._look = Vector(pos), Vector(look)

    def place(self, position, look_at=(0, 0, 0), at=0.0):
        """Put the camera somewhere (no movement) from time `at`."""
        self._key(at, STAGE.world(position), STAGE.world(look_at), "smooth")
        return self

    def move(self, to, look_at=None, at=0.0, duration=2.0, ease="smooth"):
        """Travel to `to` while turning to `look_at` (keeps looking at the same point if None)."""
        p0, l0 = self._now(at)
        look = STAGE.world(look_at) if look_at is not None else l0
        self._key(at, p0, l0, ease)
        self._key(at + duration, STAGE.world(to), look, ease)
        return self

    def cut_to(self, position, look_at=(0, 0, 0), at=0.0):
        """Hard cut: the camera jumps at `at` with no in-between frames."""
        from . import timing
        before = at - 1 / timing.CLOCK.fps
        p0, l0 = self._now(before)
        self._key(before, p0, l0, "snap")
        self._key(at, STAGE.world(position), STAGE.world(look_at), "smooth")
        return self

    # ------------------------------------------------------------------ classic moves
    def push_in(self, to, at=0.0, duration=3.0, ease="ease_in_out"):
        """Move closer to the subject, still looking at it."""
        return self.move(to, None, at, duration, ease)

    def pull_out(self, to, at=0.0, duration=3.0, ease="ease_in_out"):
        """Move away from the subject (reveal)."""
        return self.move(to, None, at, duration, ease)

    def orbit(self, center=(0, 0, 0), radius=10.0, start=-30.0, end=30.0, height=0.0, at=0.0, duration=4.0,
              ease="smooth", step=0.25):
        """Circle around `center` from angle `start` to `end` (degrees; 0 = in front, 90 = right side)."""
        c = STAGE.world(center)
        n = max(2, int(duration / step))
        from .timing import smoothstep
        shape = {"linear": lambda u: u}.get(ease, lambda u: smoothstep(0, 1, u))
        for i in range(n + 1):
            u = shape(i / n)
            a = math.radians(start + (end - start) * u)
            pos = c + Vector((radius * math.sin(a), -radius * math.cos(a), height))
            self._key(at + duration * i / n, pos, c, "linear" if 0 < i < n else "smooth")
        return self

    def crane(self, rise=3.0, at=0.0, duration=3.0, ease="smooth"):
        """Rise (or sink with a negative value) while looking at the same point."""
        p0, l0 = self._now(at)
        self._key(at, p0, l0, ease)
        self._key(at + duration, p0 + Vector((0, 0, rise)), l0, ease)
        return self

    def follow_path(self, points, look_at=None, at=0.0, duration=4.0, ease="smooth"):
        """Fly through `points` [(x, y, z), ...] spread evenly over `duration`."""
        p0, l0 = self._now(at)
        look = STAGE.world(look_at) if look_at is not None else l0
        self._key(at, p0, l0, ease)
        for i, p in enumerate(points, 1):
            self._key(at + duration * i / len(points), STAGE.world(p), look, "smooth")
        return self

    def shake(self, at=0.0, duration=0.6, strength=0.15, frequency=12.0, seed=1):
        """Handheld / impact shake around the current position, settling at the end."""
        rnd = random.Random(seed)
        base_p, base_l = self._now(at)
        n = max(2, int(duration * frequency))
        for i in range(n + 1):
            fall = 1 - i / n
            j = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * strength * fall
            key(self.obj, "location", at + duration * i / n, base_p + j, "smooth")
        self._pos, self._look = base_p, base_l
        key(self.obj, "location", at + duration, base_p, "smooth")
        return self

    # ------------------------------------------------------------------ lens
    def zoom(self, lens, at=0.0, duration=1.0, ease="smooth"):
        """Change the focal length in mm (bigger = tighter). Animates from the current value."""
        key(self.obj.data, "lens", at, value_at(self.obj.data, "lens", at), ease)
        key(self.obj.data, "lens", at + duration, lens, ease)
        return self

    def dolly_zoom(self, distance, at=0.0, duration=2.0):
        """'Vertigo' effect: move by `distance` towards the target while zooming to keep its size."""
        p0, l0 = self._now(at)
        d0 = (l0 - p0).length
        d1 = max(0.5, d0 - distance)
        lens0 = value_at(self.obj.data, "lens", at)
        direction = (l0 - p0).normalized()
        self._key(at, p0, l0, "smooth")
        key(self.obj.data, "lens", at, lens0, "smooth")
        self._key(at + duration, l0 - direction * d1, l0, "smooth")
        key(self.obj.data, "lens", at + duration, lens0 * d1 / d0, "smooth")
        return self

    def focus(self, distance=None, f_stop=2.8, item=None):
        """Depth of field: focus on an Item (or a distance in units). Lower f_stop = blurrier background."""
        dof = self.obj.data.dof
        dof.use_dof = True
        dof.aperture_fstop = f_stop
        if item is not None:
            dof.focus_object = item.obj
        elif distance is not None:
            dof.focus_distance = distance
        return self
