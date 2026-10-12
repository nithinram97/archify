"""motionkit: reusable building blocks for motion-graphics videos in Blender 5 (EEVEE).

Write *what* you want (a title pops in, the camera orbits, a flash cuts to the next shot); the kit
handles the Blender details (materials, keyframes, constraints, compositor, render settings).

Quick start:

    import motionkit as mk
    movie = mk.Movie("hello", length=6)
    mk.Starfield()
    mk.Text3D("Hello DMS", size=1.2, color="pink", glow=3).pop_in(at=0.5).float(start=1.2, end=6)
    movie.camera.place((0, -12, 0.5)).push_in(to=(0, -8, 0.3), at=0, duration=6)
    movie.overlay.caption("Built with motionkit", at=2.5, until=5.5)
    movie.effects.glow().vignette()
    movie.run()

See docs/ for the guide and the API reference.
"""
__version__ = "1.0.0"

import bpy  # noqa: F401  (loads mathutils when running as the bpy Python module)

from . import transitions
from .assets import (Arc, BarChart, Box, Card, Counter, Globe, GridFloor, Light, Line, Logo, Portal, Ring, Screen,
                     ScreenWall, Sphere, Starfield, Text3D)
from .color import CORPORATE, NEON, Palette, PALETTES
from .item import Group, Item
from .keys import animate, key
from .materials import GlowMaterial
from .movie import Movie, Shot
from .timing import EASINGS

__all__ = [
    "Movie", "Shot", "Item", "Group", "GlowMaterial", "transitions", "key", "animate", "EASINGS",
    "Text3D", "Counter", "Card", "Screen", "Logo", "Sphere", "Box", "Light", "Ring", "Arc", "Line", "Starfield", "GridFloor",
    "Globe", "BarChart", "ScreenWall", "Portal", "Palette", "PALETTES", "NEON", "CORPORATE",
]
