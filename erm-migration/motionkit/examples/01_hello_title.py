"""Demo 1: a glowing title, 8 seconds. The smallest useful motionkit movie.

Run it (PowerShell, from the motionkit folder):
    blender -b -P examples/01_hello_title.py -- --preview --render     # quick check, half size
    blender -b -P examples/01_hello_title.py -- --render               # final 1080p MP4 in examples/render/
    blender -P examples/01_hello_title.py                              # open in Blender to scrub and tweak
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motionkit as mk

movie = mk.Movie("hello_title", length=8)

# 1. Set the stage: stars far away, a glowing grid below.
mk.Starfield()
mk.GridFloor(height=-1.6)

# 2. A ring draws itself behind the title, then keeps turning slowly.
ring = mk.Ring(radius=2.6, color="indigo", glow=3).at(0, 1.5, 0.3)
ring.draw_on(at=0.3, duration=1.2).spin(turns=0.25, start=1.5, end=8, axis="Y")

# 3. The title pops in and floats.
title = mk.Text3D("Hello DMS", size=1.1, color="pink", glow=3, depth=0.12).at(0, 0, 0.3)
title.pop_in(at=0.8, duration=0.7).float(start=1.5, end=8, height=0.08)

# 4. The camera drifts around the title while moving closer.
movie.camera.place((0, -14, 1.5), look_at=(0, 0, 0.3))
movie.camera.orbit(center=(0, 0, 0.3), radius=11, start=-25, end=12, height=1.0, at=0, duration=8)

# 5. Words on screen, fades, and the glow.
movie.overlay.caption("Built with motionkit in 25 lines", eyebrow="Demo", at=3, until=6.6)
movie.overlay.fade_from_black(at=0, duration=1)
movie.overlay.fade_to_black(at=7.2, duration=0.8)
movie.effects.glow().vignette(0.3)

movie.run()
