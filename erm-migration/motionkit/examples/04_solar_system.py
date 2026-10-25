"""Demo 4: a small solar system, 12 seconds. Shows the *lit* look (shaded planets lit by the sun),
orbits on the ground plane, a moon following its planet, and a camera that cranes up to look from above.

    blender -b -P examples/04_solar_system.py -- --still 6
    blender -b -P examples/04_solar_system.py -- --preview --render
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motionkit as mk

movie = mk.Movie("solar_system", length=12)
mk.Starfield(count=2500, spread=(60, 60, 40), center=(0, 0, 0))

# The sun glows (self-lit) and holds the light that shades every planet.
sun = mk.Sphere(1.2, color="#ffb547", glow=6).pop_in(at=0.3, duration=1.0)
mk.Light("point", power=2500, color="#fff3d6", size=1.0)        # at the sun's centre
mk.Light("sun", power=0.15, color="#9fb4ff").point_at(0, 0, 0)   # faint fill so night sides aren't pure black

# Planets are lit=True: shaded by the sun, with a day side and a night side.
planets = [  # (radius, colour, distance, turns in 12 s, start angle)
    (0.22, "#c9b8a6", 2.6, 1.6, 30),
    (0.38, "#e6b86a", 3.8, 1.1, 200),
    (0.42, "#3b82f6", 5.2, 0.8, 120),
    (0.32, "#ef6b4a", 6.8, 0.55, 300),
]
for i, (r, color, dist, turns, phase) in enumerate(planets):
    p = mk.Sphere(r, color=color, lit=True, roughness=0.7)
    p.orbit(around=sun, radius=dist, turns=turns, start=0, end=12, phase=phase, path=True)
    p.spin(turns=3, start=0, end=12)                 # turning on its own axis
    p.pop_in(at=0.8 + i * 0.25, duration=0.6)
    if i == 2:  # the blue planet gets a moon that follows it around
        moon = mk.Sphere(0.1, color="#d4d4d8", lit=True)
        moon.orbit(around=p, radius=0.75, turns=4, start=0, end=12, phase=90).pop_in(at=1.8, duration=0.4)

# Camera: start low and close, crane up to see the whole system from above.
movie.camera.place((0, -11, 1.2), look_at=(0, 0, 0))
movie.camera.move(to=(0, -9, 12), look_at=(0, 0, 0), at=1.5, duration=9, ease="ease_in_out")

movie.overlay.caption("Lit planets, real orbits, one line each", eyebrow="motionkit", at=2, until=6)
movie.overlay.fade_from_black(at=0, duration=0.8)
movie.overlay.fade_to_black(at=11.2, duration=0.8)
movie.effects.glow(threshold=1.0)
movie.run()
