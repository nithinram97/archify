"""Demo 3: a globe that turns to each site in turn, with pins and labels (10 seconds).

    blender -b -P examples/03_globe_tour.py -- --preview --render
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motionkit as mk

movie = mk.Movie("globe_tour", length=10)
mk.Starfield()
globe = mk.Globe(radius=3, land_color="cyan")
globe.fade_in(at=0, duration=1).focus(20, 0, at=0, duration=0.01)

sites = [("Toulouse", 43.6, 1.4), ("Hamburg", 53.5, 10.0), ("Bristol", 51.5, -2.6), ("Madrid", 40.4, -3.7),
         ("Montreal", 45.5, -73.6)]
t = 1.0
for name, lat, lon in sites:
    globe.focus(lat, lon, at=t, duration=1.0)
    pin = globe.marker(lat, lon, color="pink", label=name).pop_in(at=t + 0.9, duration=0.4)
    pin.parts[0].fade_out(at=t + 1.4, duration=0.3)  # the label leaves when the globe moves on; the pin stays
    t += 1.5

movie.camera.place((0, -11, 1.5), look_at=(0, 0, 0.6))
movie.camera.push_in(to=(0, -9, 1.0), at=0, duration=8.5)
movie.overlay.caption("Used across five countries", eyebrow="Our users", at=1.2, until=8.6)
movie.overlay.fade_to_black(at=9.2, duration=0.8)
movie.effects.glow()
movie.run()
