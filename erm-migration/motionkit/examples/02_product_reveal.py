"""Demo 2: a product story in three shots, about 16 seconds.

  Shot 1  "Today": a wall of old screens cascades in; a portal opens.
  Shot 2  "Tomorrow": the camera flies through the portal and lands on the new app.
  Shot 3  "Impact": bars grow and a number counts up, then the end title.

Shows shots, transitions, screens, a bar chart, a counter, captions and music.
    blender -b -P examples/02_product_reveal.py -- --preview --render
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import motionkit as mk
from motionkit import transitions as tr

A = lambda name: os.path.join(HERE, "assets", name)
movie = mk.Movie("product_reveal", length=16, palette="neon")
mk.Starfield(count=2500, spread=(1600, 60, 40), center=(800, 30, 0))  # one sky behind every shot

# ---------------------------------------------------------------- shot 1: today (0-6 s)
with movie.shot("today", 0, 6) as s1:
    wall = mk.ScreenWall([A("slate_heat.png"), A("slate_table.png"), A("slate_report.png"), A("slate_tracker.png")],
                         columns=2, width=3.2, frame_color="red").at(0, 2, 0)
    wall.cascade_in(at=0.3, stagger=0.25)
    wall.fade_to(0.35, at=3.0, duration=0.8)
    gate = mk.Portal(radius=2.0).at(0, -1, 0)
    gate.open(at=3.2)
    movie.camera.place((0, -13, 0.5), look_at=(0, 2, 0))      # inside a shot, positions are relative to it
    movie.camera.push_in(to=(0, -10, 0.3), at=0, duration=3.5)
    movie.overlay.caption("Today: slow, fragile, undocumented", eyebrow="The problem", at=0.8, until=3.4)

# ---------------------------------------------------------------- shot 2: tomorrow (6-11 s)
with movie.shot("tomorrow", 6, 11) as s2:
    app = mk.Screen(A("react_heat.png"), width=5.5, frame_color="cyan").at(0, 2, 0.2)
    app.fade_in(at=6.0, duration=0.3).float(start=6.5, end=11, height=0.05)
    mk.Ring(radius=4.2, color="cyan", glow=2.5).at(0, 2.5, 0.2).draw_on(at=6.3, duration=1.2)
    movie.overlay.caption("Tomorrow: fast, stable, documented", eyebrow="The solution", at=6.6, until=10.4)
    movie.camera.orbit(center=(0, 2, 0.2), radius=9, start=-12, end=12, height=0.6, at=7.0, duration=4)

# fly through the portal from shot 1 into shot 2 (outside a shot, use shot.point() for positions)
tr.through_portal(movie, gate, at=6.0, to=s2.point(0, -7, 0.5), look_at=s2.point(0, 2, 0.2))

# ---------------------------------------------------------------- shot 3: impact (11-16 s)
with movie.shot("impact", 11, 16) as s3:
    chart = mk.BarChart([345, 120, 95, 60, 55], labels=["B", "O", "P", "A", "L"], width=6, height=3).at(-2.2, 2, -1.4)
    chart.grow(at=11.3, duration=0.8).highlight(0, at=12.6)
    users = mk.Counter(892, at=11.6, duration=1.8, size=1.1, color="pink", glow=3, suffix=" users").at(3.6, 1.5, 0.6)
    users.fade_in(at=11.6, duration=0.3).fade_out(at=13.4, duration=0.5)
    chart.fade_out(at=13.4, duration=0.5)
tr.flash_cut(movie, at=11.0, to=s3.point(0.6, -11, 0.8), look_at=s3.point(0.6, 2, 0.3))
movie.camera.push_in(to=s3.point(0.6, -9.5, 0.6), at=11.0, duration=5)
movie.overlay.title("ERM 2.0", subtitle="Coming soon", at=14.0)
movie.overlay.fade_to_black(at=15.3, duration=0.7)

movie.overlay.fade_from_black(at=0, duration=0.8)
movie.effects.glow().vignette(0.3).motion_blur(0.5)
music = os.path.join(HERE, "..", "..", "trailer", "audio", "erm2_trailer_mix.wav")
if os.path.exists(music):
    movie.add_music(music, volume=0.8)
movie.run()
