"""Transitions between shots. Each one combines a camera move with an overlay effect.

    from motionkit import transitions as tr
    tr.fade_through_black(movie, at=5, to=(30, -10, 1), look_at=(30, 0, 0))
    tr.flash_cut(movie, at=9, to=..., look_at=...)
    tr.whip_pan(movie, at=12, to=..., look_at=...)
    tr.through_portal(movie, portal, at=15, to=..., look_at=...)

`to` / `look_at` are where the camera lands for the next shot (in world units; use `shot.point(x, y, z)`
to convert a position inside a shot). Leave them out to stay in the same place.
"""
from mathutils import Vector


def _tick():
    """One frame, in seconds: moves into a cut end one frame early so the cut picks up from there."""
    from . import timing
    return 1 / timing.CLOCK.fps


def cut(movie, at, to, look_at):
    """A plain hard cut."""
    movie.camera.cut_to(to, look_at, at)


def fade_through_black(movie, at, to=None, look_at=None, duration=1.0):
    """Fade to black, cut while black, fade back up. `at` is the darkest moment."""
    movie.overlay.dip(at, "black", duration)
    if to is not None:
        movie.camera.cut_to(to, look_at, at)


def dip_to_color(movie, at, color="white", to=None, look_at=None, duration=0.8):
    """Like fade_through_black with any colour (white feels like a memory or a reveal)."""
    movie.overlay.dip(at, color, duration)
    if to is not None:
        movie.camera.cut_to(to, look_at, at)


def flash_cut(movie, at, to=None, look_at=None, color="white"):
    """A bright flash with the cut hidden at its peak; energetic."""
    movie.overlay.flash(at, color)
    if to is not None:
        movie.camera.cut_to(to, look_at, at)


def whip_pan(movie, at, to, look_at, duration=0.4, side=8.0):
    """The camera whips sideways (motion blur smears it) and lands on the next shot."""
    cam = movie.camera
    half = duration / 2
    p0, l0 = cam._now(at - half)
    cam.move(p0 + Vector((side, 0, 0)), l0 + Vector((side * 2, 0, 0)), at - half, half - _tick(), "ease_in")
    cam.cut_to(Vector(to) - Vector((side, 0, 0)), Vector(look_at) - Vector((side * 2, 0, 0)), at)
    cam.move(to, look_at, at, half, "ease_out")
    movie.effects.motion_blur(1.0)


def push_through(movie, at, to, look_at, duration=0.8):
    """Rush forward into the subject, then arrive in the next shot moving forward (fast, seamless)."""
    cam = movie.camera
    p0, l0 = cam._now(at - duration * 0.6)
    cam.move(l0 - (l0 - p0).normalized() * 0.3, None, at - duration * 0.6, duration * 0.6 - _tick(), "ease_in")
    movie.overlay.flash(at, "white", 0.6, 0.3)
    v = (Vector(look_at) - Vector(to)).normalized()
    cam.cut_to(Vector(to) - v * 4, look_at, at)
    cam.move(to, look_at, at, duration * 0.8, "ease_out")


def through_portal(movie, portal, at, to, look_at, duration=1.6):
    """Fly the camera into the centre of a Portal; flash; arrive in the next shot.

    `at` is the moment the camera crosses the gate.
    """
    import bpy
    cam = movie.camera
    bpy.context.view_layer.update()  # make sure the portal's world position is up to date
    centre = portal.obj.matrix_world.translation.copy()
    cam.move(centre + Vector((0, -2.5, 0)), centre, at - duration, duration * 0.75, "ease_in")
    cam.move(centre + Vector((0, 0.5, 0)), centre + Vector((0, 5, 0)), at - duration * 0.25, duration * 0.25 - _tick(), "ease_in")
    movie.overlay.flash(at, "white", 1.0, 0.5)
    v = (Vector(look_at) - Vector(to)).normalized()
    cam.cut_to(Vector(to) - v * 3, look_at, at)
    cam.move(to, look_at, at, 1.0, "ease_out")
