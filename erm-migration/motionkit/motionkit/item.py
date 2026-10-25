"""`Item`: anything on screen, with chainable motion.

Every asset (`Text3D`, `Ring`, `Screen`, `Globe`, ...) returns an Item, so they all move the same way:

    title = mk.Text3D("Hello")
    title.pop_in(at=0.5).float(start=1.5, end=6).fade_out(at=5.5)

Rules of thumb
  * Times are seconds from the start of the movie (`at=`), durations in seconds.
  * Call motions in time order for the same property (each one starts where the previous one ended).
  * An item that is faded or popped in is invisible before that moment; no extra calls needed.
"""
import math

from mathutils import Euler, Vector

from .color import rgba
from .keys import key, socket_key, value_at

_DIRS = {"left": (-1, 0, 0), "right": (1, 0, 0), "up": (0, 0, 1), "down": (0, 0, -1),
         "front": (0, -1, 0), "back": (0, 1, 0)}


def _vec(v):
    return Vector(v) if hasattr(v, "__len__") else Vector((v, v, v))


class Item:
    """Wraps a Blender object (and the materials that make it visible).

    Attributes:
        obj: the bpy object (use it for anything the kit doesn't cover).
        materials: GlowMaterials faded by fade_in/fade_out.
        parts: child Items, for composite assets (a chart's bars, a wall's screens, ...).
    """

    def __init__(self, obj, materials=(), parts=()):
        self.obj = obj
        self.materials = list(materials)
        self.parts = list(parts)
        self._loc = obj.location.copy()
        self._scale = obj.scale.copy()
        self._rot = obj.rotation_euler.copy()
        self._alpha = [m.alpha.default_value for m in self.materials]

    # ------------------------------------------------------------------ placement (no animation)
    def at(self, x=0.0, y=0.0, z=0.0):
        """Place the item (no animation). Returns self."""
        self.obj.location = (x, y, z)
        self._loc = self.obj.location.copy()
        return self

    def size(self, s):
        """Uniform or (x, y, z) scale (no animation)."""
        self.obj.scale = _vec(s)
        self._scale = self.obj.scale.copy()
        return self

    def turn(self, x=0.0, y=0.0, z=0.0):
        """Rotation in degrees (no animation)."""
        self.obj.rotation_euler = Euler([math.radians(a) for a in (x, y, z)])
        self._rot = self.obj.rotation_euler.copy()
        return self

    def face_camera(self):
        """Always turn to face the camera (labels, sprites). Works while the camera moves."""
        import bpy
        c = self.obj.constraints.new("TRACK_TO")
        c.target = bpy.context.scene.camera
        c.track_axis = "TRACK_Z"
        c.up_axis = "UP_Y"
        return self

    def parent_to(self, other):
        """Attach to another Item so it moves with it."""
        self.obj.parent = other.obj
        return self

    # ------------------------------------------------------------------ visibility
    def show(self, at):
        """Appear instantly at `at` (hidden before)."""
        key(self.obj, "hide_render", 0, True, "snap")
        key(self.obj, "hide_viewport", 0, True, "snap")
        key(self.obj, "hide_render", at, False, "snap")
        key(self.obj, "hide_viewport", at, False, "snap")
        return self

    def hide(self, at):
        """Disappear instantly at `at`."""
        key(self.obj, "hide_render", at, True, "snap")
        key(self.obj, "hide_viewport", at, True, "snap")
        return self

    def visible(self, start, end=None):
        """Only visible between `start` and `end` (hard cuts)."""
        self.show(start)
        if end is not None:
            self.hide(end)
        for p in self.parts:
            p.visible(start, end)
        return self

    def fade_in(self, at, duration=0.5, ease="smooth"):
        """Fade from invisible to its opacity."""
        for m, a in zip(self.materials, self._alpha):
            socket_key(m.alpha, at, 0.0, ease)
            socket_key(m.alpha, at + duration, a or 1.0, ease)
        for p in self.parts:
            p.fade_in(at, duration, ease)
        return self

    def fade_out(self, at, duration=0.5, ease="smooth"):
        """Fade to invisible, finishing at `at + duration`."""
        for m, a in zip(self.materials, self._alpha):
            socket_key(m.alpha, at, a or 1.0, ease)
            socket_key(m.alpha, at + duration, 0.0, ease)
        for p in self.parts:
            p.fade_out(at, duration, ease)
        return self

    def fade_to(self, opacity, at, duration=0.5, ease="smooth"):
        """Animate to a partial opacity (e.g. dim to 0.3)."""
        for i, m in enumerate(self.materials):
            socket_key(m.alpha, at, self._alpha[i] or 1.0, ease)
            socket_key(m.alpha, at + duration, opacity, ease)
            self._alpha[i] = opacity
        for p in self.parts:
            p.fade_to(opacity, at, duration, ease)
        return self

    # ------------------------------------------------------------------ entrances and exits
    def pop_in(self, at, duration=0.5, overshoot=1.12):
        """Grow from nothing with a small overshoot."""
        s = self._scale
        key(self.obj, "scale", at, s * 0.001, "ease_out")
        key(self.obj, "scale", at + duration * 0.7, s * overshoot, "smooth")
        key(self.obj, "scale", at + duration, s, "smooth")
        return self

    def pop_out(self, at, duration=0.4):
        """Shrink to nothing, finishing at `at + duration`."""
        s = self._scale
        key(self.obj, "scale", at, s, "ease_in")
        key(self.obj, "scale", at + duration, s * 0.001, "snap")
        return self

    def slide_in(self, at, duration=0.8, direction="left", distance=3.0, fade=True, ease="ease_out"):
        """Arrive from `direction` ("left", "right", "up", "down", "front", "back" or a vector)."""
        d = Vector(_DIRS.get(direction, direction)) * distance if isinstance(direction, str) else Vector(direction)
        key(self.obj, "location", at, self._loc + d, ease)
        key(self.obj, "location", at + duration, self._loc, "smooth")
        if fade:
            self.fade_in(at, duration * 0.8)
        return self

    def slide_out(self, at, duration=0.8, direction="right", distance=3.0, fade=True, ease="ease_in"):
        d = Vector(_DIRS.get(direction, direction)) * distance if isinstance(direction, str) else Vector(direction)
        key(self.obj, "location", at, self._loc, ease)
        key(self.obj, "location", at + duration, self._loc + d, "smooth")
        if fade:
            self.fade_out(at + duration * 0.2, duration * 0.8)
        return self

    def rise_in(self, at, duration=0.8, distance=0.6):
        """Drift up into place while fading in (good for titles)."""
        return self.slide_in(at, duration, "down", distance)

    # ------------------------------------------------------------------ motion
    def move_to(self, x, y, z, at, duration=1.0, ease="smooth"):
        """Travel to (x, y, z)."""
        key(self.obj, "location", at, value_at(self.obj, "location", at), ease)
        self._loc = Vector((x, y, z))
        key(self.obj, "location", at + duration, self._loc, ease)
        return self

    def move_by(self, dx=0.0, dy=0.0, dz=0.0, at=0.0, duration=1.0, ease="smooth"):
        p = self._loc + Vector((dx, dy, dz))
        return self.move_to(p.x, p.y, p.z, at, duration, ease)

    def scale_to(self, s, at, duration=0.6, ease="smooth"):
        key(self.obj, "scale", at, value_at(self.obj, "scale", at), ease)
        self._scale = _vec(s)
        key(self.obj, "scale", at + duration, self._scale, ease)
        return self

    def rotate_to(self, x, y, z, at, duration=1.0, ease="smooth"):
        """Rotate to (x, y, z) degrees."""
        key(self.obj, "rotation_euler", at, value_at(self.obj, "rotation_euler", at), ease)
        self._rot = Euler([math.radians(a) for a in (x, y, z)])
        key(self.obj, "rotation_euler", at + duration, self._rot, ease)
        return self

    def spin(self, turns=1.0, start=0.0, end=4.0, axis="Z", ease="linear"):
        """Rotate `turns` full turns around `axis` between `start` and `end`."""
        i = "XYZ".index(axis.upper())
        r0 = value_at(self.obj, "rotation_euler", start)
        r1 = r0.copy()
        r1[i] += 2 * math.pi * turns
        key(self.obj, "rotation_euler", start, r0, ease)
        key(self.obj, "rotation_euler", end, r1, ease)
        self._rot = r1
        return self

    def float(self, start=0.0, end=4.0, height=0.12, period=2.0):
        """Gentle up-and-down bob (idle motion)."""
        t, i = start, 0
        while t <= end + 1e-6:
            z = self._loc.z + (height if i % 2 else 0.0)
            key(self.obj, "location", t, (self._loc.x, self._loc.y, z), "smooth")
            t += period / 2
            i += 1
        return self

    def orbit(self, around=(0, 0, 0), radius=3.0, turns=1.0, start=0.0, end=8.0, tilt=0.0, phase=0.0,
              clockwise=False, path=False, path_color="muted", ease="linear"):
        """Circle around a point or another Item, on the ground plane (flat, like planets round a sun).

        Args:
            around: a position (x, y, z) or an Item to circle (a moon around a planet follows the planet).
            radius: distance from the centre.
            turns: how many full circles between `start` and `end` (0.5 = half a circle).
            tilt: tilts the orbit's plane, in degrees (0 = perfectly flat).
            phase: where on the circle it starts, in degrees (0 = right of the centre, 90 = behind it).
            clockwise: direction seen from above.
            path: also draw the orbit as a thin flat ring (`path_color`).
        The item keeps its own `.spin()` for turning on its axis.
        """
        import bpy
        from .stage import STAGE
        tilt_e = STAGE.link(bpy.data.objects.new(f"{self.obj.name} orbit", None))
        if isinstance(around, Item):
            c = tilt_e.constraints.new("COPY_LOCATION")  # follow the centre's position, not its spin
            c.target = around.obj
        else:
            tilt_e.location = around
        tilt_e.rotation_euler = (math.radians(tilt), 0, 0)
        spin_e = bpy.data.objects.new(f"{self.obj.name} orbit spin", None)
        STAGE.link(spin_e)
        spin_e.parent = tilt_e
        self.obj.parent = spin_e
        self.obj.location = (radius, 0, 0)
        self._loc = self.obj.location.copy()
        sign = -1 if clockwise else 1
        a0 = math.radians(phase)
        key(spin_e, "rotation_euler", start, (0, 0, a0), ease)
        key(spin_e, "rotation_euler", end, (0, 0, a0 + sign * 2 * math.pi * turns), ease)
        self.orbit_pivot = Item(spin_e)
        if path:
            from .assets import Ring
            ring = Ring(radius, 0.008, path_color, glow=1.2, facing="up", opacity=0.5)
            ring.obj.parent = tilt_e
            ring.obj.location = (0, 0, 0)
            self.orbit_path = ring
        return self

    def pulse(self, at, times=1, amount=1.15, period=0.5):
        """Briefly grow and settle back, `times` times (draws the eye)."""
        s = self._scale
        for k in range(times):
            t = at + k * period
            key(self.obj, "scale", t, s, "smooth")
            key(self.obj, "scale", t + period * 0.4, s * amount, "smooth")
            key(self.obj, "scale", t + period, s, "smooth")
        return self

    # ------------------------------------------------------------------ look
    def glow_to(self, strength, at, duration=0.5, ease="smooth"):
        """Animate the glow (emission strength). Pair with movie.effects.glow()."""
        from .materials import compress_glow
        for m in self.materials:
            socket_key(m.strength, at, m.strength.default_value, ease)
            socket_key(m.strength, at + duration, compress_glow(strength), ease)
        for p in self.parts:
            p.glow_to(strength, at, duration, ease)
        return self

    def color_to(self, color, at, duration=0.5, ease="smooth"):
        """Animate to another colour (solid-colour materials only)."""
        for m in self.materials:
            if m.image is None:
                socket_key(m.color, at, tuple(m.color.default_value), ease)
                socket_key(m.color, at + duration, rgba(color), ease)
        for p in self.parts:
            p.color_to(color, at, duration, ease)
        return self

    def __repr__(self):
        return f"<Item {self.obj.name}>"


class Group(Item):
    """Several items that move together: `Group(a, b, c).at(0, 0, 2).spin(...)`."""

    def __init__(self, *items, name="group"):
        import bpy
        from .stage import STAGE
        root = STAGE.link(bpy.data.objects.new(name, None))
        for it in items:
            it.obj.parent = root
        super().__init__(root, parts=items)
