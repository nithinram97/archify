"""dreamreel: make animated films by describing what happens. No animation skills needed.

Everything is a class you can extend (see plugins.py):

    import dreamreel as dr

    class Robot(dr.Character): ...       # a new kind of character
    class Crown(dr.Extra): ...           # something to wear
    class Dance(dr.Gesture): ...         # body language
    class Hug(dr.Action): ...            # a new verb for scenes
    class Cake(dr.Prop): ...             # furniture and things
    class Spaceship(dr.Set): ...         # a new kind of place
    class LowAngle(dr.ShotType): ...     # a camera shot
    class MyTTS(dr.VoiceEngine): ...     # voices

Put such classes in a film's extensions/ folder and they appear in the studio's menus.
Run `dreamreel --help` for the commands.
"""
__version__ = "0.2.0"

import bpy  # noqa: F401,E402  (loads mathutils and bmesh)

from . import keys, look, shapes  # noqa: F401,E402
from .plugins import Param, Plugin, describe_all, get, names, registry  # noqa: F401,E402
from .character import BODIES, SPEEDS, Character, ToyFigure  # noqa: F401,E402
from .parts import Extra, Hair, Mood  # noqa: F401,E402
from .gestures import Gesture  # noqa: F401,E402
from .sets import FLOORS, SIZES, ZONES, Outdoor, Room, Set  # noqa: F401,E402
from .props import Item, Prop  # noqa: F401,E402
from .camera import ShotType  # noqa: F401,E402
from .actions import Action  # noqa: F401,E402
from .voices import VoiceEngine  # noqa: F401,E402
from .scene import BeatError, Scene  # noqa: F401,E402
from .look import COLORS  # noqa: F401,E402
from . import actions, gestures, parts, props  # noqa: F401,E402
