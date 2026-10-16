"""dreamreel: make animated films by writing what happens. No animation skills needed.

    import dreamreel as dr

    s = dr.Scene("kitchen")
    mia, tom = s.cast("mia", "tom")
    mia.enter("door").walk_to("table").say("Who ate the last cookie?", mood="angry", to=tom)

Run it with the `dreamreel` command (see `dreamreel --help`).
"""
__version__ = "0.1.0"

import bpy  # noqa: F401,E402  (loads mathutils and bmesh)

from .character import EXTRAS, GESTURES, HAIR, MOODS, Character  # noqa: F401
from .look import COLORS  # noqa: F401
from .scene import Scene  # noqa: F401
from .sets import PROP_TYPES, ZONES, Set  # noqa: F401
