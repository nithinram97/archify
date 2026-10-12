"""Builds every motionkit component and transition in Blender, checks the result, renders 2 tiny frames.

    blender -b -P tests/smoke_test.py            # with Blender
    python tests/smoke_test.py                   # with the bpy module (pip install bpy)
Exits with status 1 on the first failure.
"""
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import bpy  # noqa: E402
import motionkit as mk  # noqa: E402
from motionkit import transitions as tr  # noqa: E402

ASSETS = os.path.join(HERE, "..", "examples", "assets")
failures = []


def check(name, fn):
    try:
        fn()
        print(f"  ok    {name}")
    except Exception:
        failures.append(name)
        print(f"  FAIL  {name}")
        traceback.print_exc()


movie = mk.Movie("smoke", length=12, size=(320, 180))
print(f"Blender {bpy.app.version_string}, engine {bpy.context.scene.render.engine}")

with movie.shot("one", 0, 6) as s1:
    check("Text3D + motions", lambda: mk.Text3D("Hi", color="pink").pop_in(0.2).float(1, 3).spin(1, 3, 5).fade_out(5))
    check("Text3D.type_on", lambda: mk.Text3D("Typing", size=0.5).at(0, 0, -1).type_on(0.5, 1.0))
    check("Counter", lambda: mk.Counter(892, at=1, duration=1, suffix=" users").at(3, 0, 0))
    check("Card + image", lambda: mk.Card(2, 1, image=os.path.join(ASSETS, "react_heat.png")).slide_in(0.5))
    check("Screen", lambda: mk.Screen(os.path.join(ASSETS, "slate_heat.png")).rise_in(1))
    check("Logo (missing file falls back)", lambda: mk.Logo("does-not-exist.png", 0.5).fade_in(1))
    check("Sphere", lambda: mk.Sphere(0.5, "cyan").at(-3, 0, 0).pulse(2, times=2))
    check("Ring + Arc draw_on", lambda: (mk.Ring(2).draw_on(0, 1), mk.Arc(1.5, 0, 90).draw_on(0, 1, from_middle=True)))
    check("Line", lambda: mk.Line([(0, 0, 0), (1, 0, 1), (2, 0, 0)]).draw_on(1, 1).erase(3, 1))
    check("Starfield + GridFloor", lambda: (mk.Starfield(200), mk.GridFloor(10, 1)))
    check("Group", lambda: mk.Group(mk.Sphere(0.2), mk.Sphere(0.2).at(1, 0, 0)).move_to(0, 0, 2, at=1).rotate_to(0, 0, 90, 2))
    check("colour animation", lambda: mk.Card(1, 1, "indigo").color_to("pink", 1).glow_to(3, 2).fade_to(0.3, 3))
    portal = mk.Portal().at(0, 4, 0)
    check("Portal.open", lambda: portal.open(2))
    check("camera moves", lambda: (movie.camera.place((0, -10, 1)), movie.camera.push_in((0, -7, 1), 0, 2),
                                   movie.camera.orbit(radius=8, at=2, duration=2), movie.camera.crane(1, 4, 1),
                                   movie.camera.shake(5, 0.5), movie.camera.zoom(50, 5, 0.5)))

with movie.shot("two", 6, 12) as s2:
    check("Globe focus + marker", lambda: mk.Globe(2).focus(45, 2, 6.5).marker(45, 2, label="Here").pop_in(7))
    check("BarChart grow + highlight", lambda: mk.BarChart([3, 1, 2], ["a", "b", "c"]).at(0, 0, -2).grow(7).highlight(0, 8))
    check("ScreenWall cascade", lambda: mk.ScreenWall([os.path.join(ASSETS, "slate_table.png")] * 4, 2).at(6, 3, 0).cascade_in(7))

check("through_portal", lambda: tr.through_portal(movie, portal, 6, s2.point(0, -8, 0.5), s2.point(0, 0, 0)))
check("flash_cut / fade_through_black / dip / whip / push", lambda: (
    tr.flash_cut(movie, 8, s2.point(0, -9, 0), s2.point(0, 0, 0)),
    tr.fade_through_black(movie, 9, s2.point(1, -9, 0), s2.point(0, 0, 0)),
    tr.dip_to_color(movie, 9.6, "white"),
    tr.whip_pan(movie, 10.4, s2.point(2, -9, 0), s2.point(2, 0, 0)),
    tr.push_through(movie, 11.2, s2.point(0, -6, 0), s2.point(0, 0, 0))))
check("overlay", lambda: (movie.overlay.caption("Caption", eyebrow="Eyebrow", at=1, until=3),
                          movie.overlay.title("Title", "Subtitle", at=4, until=5.5),
                          movie.overlay.lower_third("Name", "Role", at=2, until=4),
                          movie.overlay.image(os.path.join(ASSETS, "react_summary.png"), 0.3, 0.3, 0.2, at=1),
                          movie.overlay.letterbox(), movie.overlay.fade_from_black(0, 0.5),
                          movie.overlay.fade_to_black(11.5, 0.5), movie.overlay.flash(3)))
check("effects", lambda: movie.effects.glow().vignette().motion_blur())
check("key / animate", lambda: mk.animate(mk.Sphere(0.1).obj, "location", {0: (0, 0, 0), 1: (0, 0, 1), 2: (0, 0, 0)},
                                          ease=["ease_out", "bounce", "linear"]))

# the camera must actually be where the transitions put it
def camera_lands():
    s = bpy.context.scene
    s.frame_set(int(round(6.0 * 24)) + 3)
    assert s.camera.location.x > 900, f"camera did not land in shot two: {tuple(s.camera.location)}"
check("camera lands in shot two after the portal", camera_lands)

out = tempfile.mkdtemp()
check("render stills (EEVEE)", lambda: (movie.still(1.5, os.path.join(out, "a.png")), movie.still(7.5, os.path.join(out, "b.png"))))
check("stills exist", lambda: [os.path.getsize(os.path.join(out, f)) for f in ("a.png", "b.png")])

print(f"\n{'ALL PASSED' if not failures else 'FAILED: ' + ', '.join(failures)}")
sys.exit(1 if failures else 0)
