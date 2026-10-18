"""Sound effects and ambience: the film sounds like what happens in it.

Sounds are plugins like everything else (see plugins.py). A `Sound` is played by name ("punch",
"footstep_wood", "door_open", "whoosh"...) and its file is found, in this order:

1. the film's own `audio/sfx/` folder: `audio/sfx/punch.wav` (or punch_1.ogg, punch_2.ogg... for
   variations) replaces the built-in sound, and any file there can be played by its name;
2. the sound's recording in Kenney's packs (impacts, footsteps, doors, cloth, books, knives, clicks,
   sci-fi): CC0, free for any use, downloaded the first time and kept in ~/.cache/dreamreel/sounds
   (`dreamreel assets --pack sounds` fetches them all at once);
3. the sound made here from noise and tones by the class's `synth` (a recorded sound inherits the
   `synth` of the made-here sound it is a kind of), so a film always has its sounds, offline too.

New sounds are new classes:

    class Squeak(dr.Sound):                   # made from code
        def synth(self, rng):
            return dr.sounds.tone(0.15, lambda t: 2400 - 6000 * t, decay=0.04)

    class Moo(dr.Sound):                      # a recording in audio/sfx/moo.wav, with a stand-in
        stand_in = "boing"

An `Ambience` is a quiet bed under a whole scene, made for its length: room tone, a street's hum and
passing cars, wind and birds, crickets, rain, the sea. Each set says which it wants (`Set.ambience`,
and an outdoor set asks its biome), rain and snow change it, and `ambience = "sea"` in a scene file (or
"none", or a file in audio/sfx/) chooses.

Characters make their own sounds: footsteps on what they walk on (`Character.footstep_sound`), the
whoosh of a punch and the smack where it lands, claps, stomps and landings. Add one anywhere with a
beat: `do = "sound"`, `sound = "door_close"`. Sounds move with slow motion like everything else.
"""
import hashlib
import math
import os
import re
import urllib.request
import wave
import zipfile

import numpy as np

from . import plugins
from .plugins import Plugin

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dreamreel", "sounds")
RATE = 44100
UA = {"User-Agent": "dreamreel sound fetcher"}

# Kenney's packs (CC0): the asset page names the current zip
PACKS = {"impact": "impact-sounds", "rpg": "rpg-audio", "interface": "interface-sounds", "scifi": "sci-fi-sounds"}


def _seed(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------- the packs
def _pack_dir(pack):
    return os.path.join(CACHE, PACKS[pack])


def pack_installed(pack):
    d = _pack_dir(pack)
    return os.path.isdir(d) and any(f.endswith(".ogg") for f in os.listdir(d))


def fetch_pack(pack):
    """Download one of Kenney's packs (only its .ogg sounds are kept). The folder, or None offline."""
    d = _pack_dir(pack)
    if pack_installed(pack):
        return d
    page = f"https://kenney.nl/assets/{PACKS[pack]}"
    try:
        with urllib.request.urlopen(urllib.request.Request(page, headers=UA), timeout=30) as r:
            html = r.read().decode("utf-8", "ignore")
        m = re.search(r"https://kenney\.nl/media/[^\"']+\.zip", html)
        if not m:
            return None
        os.makedirs(CACHE, exist_ok=True)
        tmp = os.path.join(CACHE, PACKS[pack] + ".zip.part")
        with urllib.request.urlopen(urllib.request.Request(m.group(0), headers=UA), timeout=120) as r, \
                open(tmp, "wb") as f:
            f.write(r.read())
        os.makedirs(d, exist_ok=True)
        with zipfile.ZipFile(tmp) as z:
            for info in z.infolist():
                base = os.path.basename(info.filename)
                if base.endswith(".ogg") and re.fullmatch(r"[\w.-]+", base):     # flat, plain names only
                    with z.open(info) as src, open(os.path.join(d, base), "wb") as out:
                        out.write(src.read())
        os.remove(tmp)
        return d if pack_installed(pack) else None
    except Exception as e:
        print(f"[dreamreel] sounds: couldn't fetch {PACKS[pack]} ({e}); using sounds made here")
        return None


def download_all():
    return {p: fetch_pack(p) is not None for p in PACKS}


def _variants(folder, prefix):
    pat = re.compile(re.escape(prefix) + r"(_?\d+)?\.(wav|ogg|mp3|flac)$", re.I)
    try:
        return sorted(os.path.join(folder, f) for f in os.listdir(folder) if pat.fullmatch(f))
    except OSError:
        return []


# ---------------------------------------------------------------------- building blocks for synth()
def _write(p, x):
    x = np.clip(x, -1, 1)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".part"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    os.replace(tmp, p)
    return p


def times(seconds):
    """Sample times (seconds) for a sound this long."""
    return np.arange(int(seconds * RATE)) / RATE


def band(n, rng, lo, hi, tilt=0.0):
    """n samples of noise with its energy between lo and hi Hz (tilt > 0: darker)."""
    spec = rng.normal(size=n // 2 + 1) + 1j * rng.normal(size=n // 2 + 1)
    f = np.fft.rfftfreq(n, 1 / RATE)
    mask = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    x = np.fft.irfft(spec * mask / np.maximum(f, 20) ** tilt, n)
    return x / (np.abs(x).max() + 1e-9)


def env(n, attack, decay):
    """A strike: up in `attack` seconds, dying away with time constant `decay`."""
    t = np.arange(n) / RATE
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def swell(n, power=2):
    """Up and down again over n samples."""
    return np.sin(np.pi * np.linspace(0, 1, n)) ** power


def norm(x, peak):
    return x * (peak / (np.abs(x).max() + 1e-9))


def tone(seconds, freq, decay=None, square=False):
    """A tone whose frequency (Hz) is a number or a function of time, dying away with `decay`."""
    t = times(seconds)
    f = freq(t) if callable(freq) else np.full(len(t), float(freq))
    x = np.sin(2 * np.pi * np.cumsum(f) / RATE)
    x = np.sign(x) if square else x
    return x * env(len(t), 0.001, decay) if decay else x


def scatter(n, rng, per_second, make_one):
    """Sounds made by `make_one()` dropped at random over n samples, `per_second` on average."""
    x = np.zeros(n)
    for _ in range(rng.poisson(per_second * n / RATE)):
        e = make_one()
        s = rng.integers(0, max(1, n - len(e)))
        x[s:s + len(e)] += e[:n - s]
    return x


def chirp(rng, lo, hi, seconds):
    """A bird's or an insect's call: a warbling sweep between lo and hi Hz."""
    t = times(seconds)
    f0, f1, wob = rng.uniform(lo, hi), rng.uniform(lo, hi), rng.uniform(15, 40)
    return tone(seconds, lambda t: f0 + (f1 - f0) * t / seconds + 300 * np.sin(2 * np.pi * wob * t)) * \
        np.sin(np.pi * t / seconds) ** 2


# ---------------------------------------------------------------------- sounds
class Sound(Plugin):
    """A sound effect, played by name. Subclasses give it a recording (`pack` and `prefix` in
    Kenney's packs, or a file in the film's audio/sfx/) and/or make it in code (`synth`)."""
    kind = "sound"
    abstract = True
    pack = None           # one of PACKS
    prefix = None         # the recording's file name in the pack, without its number
    stand_in = None       # the name of a sound whose synth() stands in when there's no recording
    variants = 4          # how many different takes synth() makes (each seed picks one)

    def synth(self, rng):
        """The sound made in code: samples at RATE, -1..1 (default: the stand-in's)."""
        if self.stand_in is None:
            raise NotImplementedError(f"{self.name}: no recording and no synth()")
        return plugins.get("sound", self.stand_in)().synth(rng)

    def recordings(self, project_dir=None, download=True):
        """Files of this sound: the film's own, else the pack's."""
        if project_dir:
            own = _variants(os.path.join(project_dir, "audio", "sfx"), self.name)
            if own:
                return own
        if self.pack:
            folder = fetch_pack(self.pack) if download else (_pack_dir(self.pack) if pack_installed(self.pack) else None)
            if folder:
                return _variants(folder, self.prefix or self.name)
        return []

    def file(self, seed=0, project_dir=None, download=True):
        """A file to play (a different take for each seed)."""
        got = self.recordings(project_dir, download)
        if got:
            return got[seed % len(got)]
        v = seed % self.variants
        p = os.path.join(CACHE, "made", f"{self.name}_{v}.wav")
        if not os.path.exists(p):
            _write(p, self.synth(np.random.default_rng(_seed(self.name, v))))
        return p


# made here (and the stand-ins for recordings)
class Whoosh(Sound):
    """Air moving fast: a punch, a kick, something thrown."""
    category = "movement"
    seconds = 0.32

    def synth(self, rng):
        n = int(self.seconds * RATE)
        e = swell(n)
        return norm(band(n, rng, 300, 1400) * e + 0.5 * band(n, rng, 1500, 5000) * e ** 3, 0.7)


class Swish(Whoosh):
    """A quick, light whoosh."""
    seconds = 0.18


class Smack(Sound):
    """A hit on a body."""
    category = "fight"

    def synth(self, rng):
        n = int(0.25 * RATE)
        x = 0.9 * band(n, rng, 120, 2500) * env(n, 0.001, 0.035) + tone(0.25, 85, decay=0.06)
        return norm(x, 0.95)


class Thump(Sound):
    """Something heavy and soft landing."""
    category = "impact"

    def synth(self, rng):
        x = tone(0.4, lambda t: 70 - 30 * t, decay=0.09)
        x += 0.4 * band(len(x), rng, 60, 600) * env(len(x), 0.001, 0.03)
        return norm(x, 0.9)


class Step(Sound):
    """A footstep."""
    category = "footsteps"

    def synth(self, rng):
        n = int(0.18 * RATE)
        x = band(n, rng, 80, 1800) * env(n, 0.003, 0.025) + 0.3 * band(n, rng, 2000, 6000) * env(n, 0.01, 0.04)
        return norm(x, 0.7)


class Clap(Sound):
    """Hands clapping."""
    category = "people"

    def synth(self, rng):
        n = int(0.3 * RATE)
        x = np.zeros(n)
        for k, a in enumerate((1.0, 0.7, 0.5)):
            s = int(k * 0.008 * RATE)
            x[s:] += a * band(n - s, rng, 900, 3500) * env(n - s, 0.0005, 0.02)
        return norm(x, 0.9)


class Knock(Sound):
    """A knock on wood."""
    category = "impact"
    pitch = (180, 260)
    ring = 0.05

    def synth(self, rng):
        base = rng.uniform(*self.pitch)
        x = sum(tone(0.6, base * r) * a for r, a in ((1, 1), (2.76, 0.5), (5.4, 0.25))) * env(int(0.6 * RATE), 0.001, self.ring)
        x += 0.3 * band(len(x), rng, 500, 6000) * env(len(x), 0.0005, 0.01)
        return norm(x, 0.8)


class Clink(Knock):
    """Glass or metal tapped: it rings."""
    pitch = (1800, 2600)
    ring = 0.18


class Creak(Sound):
    """A creaking hinge or floorboard."""
    category = "household"

    def synth(self, rng):
        t = times(0.7)
        drift = 30 * rng.normal(size=len(t)).cumsum() / RATE
        x = tone(0.7, lambda t: 140 + 60 * np.sin(2 * np.pi * 1.3 * t) + drift, square=True) * 0.3 * swell(len(t), 1)
        return norm(x * band(len(t), rng, 100, 3000) ** 2, 0.5)


class Rustle(Sound):
    """Cloth or paper moving."""
    category = "household"

    def synth(self, rng):
        n = int(0.45 * RATE)
        return norm(band(n, rng, 1500, 8000) * np.abs(band(n, rng, 2, 25)) * swell(n, 1), 0.5)


class Tick(Sound):
    """A small click."""
    category = "interface"

    def synth(self, rng):
        return norm(tone(0.05, 2200, decay=0.012), 0.6)


class Pop(Sound):
    """A cartoon pop."""
    category = "cartoon"

    def synth(self, rng):
        return norm(tone(0.12, lambda t: 600 + 7500 * t, decay=0.03), 0.6)


class Boing(Sound):
    """A cartoon spring."""
    category = "cartoon"

    def synth(self, rng):
        return norm(tone(0.6, lambda t: 180 + 120 * np.exp(-t * 4) * np.sin(2 * np.pi * 9 * t), decay=0.25), 0.7)


class Splash(Sound):
    """Something falling into water."""
    category = "nature"

    def synth(self, rng):
        n = int(0.8 * RATE)
        return norm(band(n, rng, 300, 7000) * env(n, 0.005, 0.18), 0.7)


class Zap(Sound):
    """An electric or laser zap."""
    category = "sci-fi"

    def synth(self, rng):
        return norm(tone(0.3, lambda t: 1800 * np.exp(-t * 9) + 200, decay=0.09, square=True), 0.5)


class Boom(Sound):
    """An explosion."""
    category = "impact"

    def synth(self, rng):
        n = int(1.8 * RATE)
        return norm(band(n, rng, 20, 400, tilt=0.5) * env(n, 0.005, 0.5) + 0.6 * band(n, rng, 400, 4000) * env(n, 0.001, 0.08), 0.95)


class Hum(Sound):
    """A machine's hum."""
    category = "sci-fi"

    def synth(self, rng):
        t = times(1.5)
        x = sum(tone(1.5, 55 * h) / h for h in (1, 2, 3, 4)) * (1 + 0.2 * np.sin(2 * np.pi * 3 * t))
        return norm(x * np.minimum(1, np.minimum(t, t[-1] - t) / 0.15), 0.4)


# recordings from the packs: each is a kind of a made-here sound, whose synth() stands in offline
RECORDINGS = {   # name: (made-here sound it is a kind of, pack, file prefix, category)
    "punch": (Smack, "impact", "impactPunch_medium", "fight"),
    "punch_heavy": (Smack, "impact", "impactPunch_heavy", "fight"),
    "block": (Thump, "impact", "impactSoft_medium", "fight"),
    "thud": (Thump, "impact", "impactSoft_heavy", "impact"),
    "footstep_wood": (Step, "impact", "footstep_wood", "footsteps"),
    "footstep_carpet": (Step, "impact", "footstep_carpet", "footsteps"),
    "footstep_concrete": (Step, "impact", "footstep_concrete", "footsteps"),
    "footstep_grass": (Step, "impact", "footstep_grass", "footsteps"),
    "footstep_snow": (Step, "impact", "footstep_snow", "footsteps"),
    "knock": (Knock, "impact", "impactWood_medium", "impact"),
    "wood": (Knock, "impact", "impactWood_heavy", "impact"),
    "plank": (Knock, "impact", "impactPlank_medium", "impact"),
    "dig": (Knock, "impact", "impactMining", "impact"),
    "glass": (Clink, "impact", "impactGlass_medium", "impact"),
    "glass_heavy": (Clink, "impact", "impactGlass_heavy", "impact"),
    "metal": (Clink, "impact", "impactMetal_medium", "impact"),
    "metal_heavy": (Clink, "impact", "impactMetal_heavy", "impact"),
    "plate": (Clink, "impact", "impactPlate_medium", "household"),
    "tin": (Clink, "impact", "impactTin_medium", "household"),
    "bell": (Clink, "impact", "impactBell_heavy", "impact"),
    "door_open": (Creak, "rpg", "doorOpen", "household"),
    "door_close": (Thump, "rpg", "doorClose", "household"),
    "creak": (Creak, "rpg", "creak", "household"),
    "cloth": (Rustle, "rpg", "cloth", "movement"),
    "book_open": (Rustle, "rpg", "bookOpen", "household"),
    "book_close": (Thump, "rpg", "bookClose", "household"),
    "page": (Rustle, "rpg", "bookFlip", "household"),
    "coins": (Clink, "rpg", "handleCoins", "household"),
    "draw_knife": (Swish, "rpg", "drawKnife", "fight"),
    "slice": (Swish, "rpg", "knifeSlice", "fight"),
    "chop": (Knock, "rpg", "chop", "household"),
    "pot": (Clink, "rpg", "metalPot", "household"),
    "latch": (Tick, "rpg", "metalLatch", "household"),
    "click": (Tick, "interface", "click", "interface"),
    "select": (Tick, "interface", "select", "interface"),
    "switch": (Tick, "interface", "switch", "interface"),
    "confirm": (Pop, "interface", "confirmation", "interface"),
    "error": (Pop, "interface", "error", "interface"),
    "drop": (Pop, "interface", "drop", "interface"),
    "laser": (Zap, "scifi", "laserSmall", "sci-fi"),
    "laser_big": (Zap, "scifi", "laserLarge", "sci-fi"),
    "explosion": (Boom, "scifi", "explosionCrunch", "impact"),
    "rumble": (Boom, "scifi", "lowFrequency_explosion", "impact"),
    "engine": (Hum, "scifi", "spaceEngine", "sci-fi"),
    "force_field": (Hum, "scifi", "forceField", "sci-fi"),
    "glitch": (Zap, "scifi", "glitch", "sci-fi"),
}
for _name, (_base, _pack, _prefix, _cat) in RECORDINGS.items():
    type(_name.title().replace("_", ""), (_base,), {
        "name": _name, "pack": _pack, "prefix": _prefix, "category": _cat, "__module__": __name__,
        "description": f"{_name.replace('_', ' ').capitalize()} (recorded; CC0, Kenney)"})


def names():
    return plugins.names("sound")


def path(name, seed=0, project_dir=None, download=True):
    """The file to play for `name`: a Sound's, or a file in the film's audio/sfx/. None if neither."""
    if name in plugins.names("sound"):
        return plugins.get("sound", name)().file(seed, project_dir, download)
    if project_dir:
        own = _variants(os.path.join(project_dir, "audio", "sfx"), name)
        if own:
            return own[seed % len(own)]
    return None


# ---------------------------------------------------------------------- ambience
class Ambience(Plugin):
    """A bed of sound under a whole scene. `synth(n, rng)` makes n samples of it, quietly (peaks
    around 0.1-0.3); the bed is made once for the scene's length and kept."""
    kind = "ambience"
    abstract = True

    def synth(self, n, rng):
        raise NotImplementedError

    def file(self, seconds, seed=0):
        seconds = max(1, math.ceil(seconds + 1.0))
        p = os.path.join(CACHE, "made", f"ambience_{self.name}_{seconds}_{seed}.wav")
        if not os.path.exists(p):
            n = int(seconds * RATE)
            x = self.synth(n, np.random.default_rng(_seed(self.name, seed)))
            fade = min(n // 2, int(0.5 * RATE))
            x[:fade] *= np.linspace(0, 1, fade)
            x[-fade:] *= np.linspace(1, 0, fade)
            _write(p, np.clip(x, -0.5, 0.5))
        return p


def _drift(n, rng, lo, hi):
    """A slow wander around 1 (for wind gusts and the like)."""
    return 0.6 + 0.4 * band(n, rng, lo, hi)


class Room(Ambience):
    """Room tone: the quiet hum of indoors."""

    def synth(self, n, rng):
        return 0.02 * band(n, rng, 40, 400, tilt=0.5) + 0.004 * tone(n / RATE, 50)


class City(Ambience):
    """A street: the hum of the city and cars going by."""
    cars = 0.25           # per second
    insects = 0.0

    def synth(self, n, rng):
        car_n = int(4 * RATE)
        x = 0.06 * band(n, rng, 30, 500, tilt=0.5)
        x += (0.08 if self.cars > 0.1 else 0.04) * scatter(n, rng, self.cars, lambda: band(car_n, rng, 150, 1600) * swell(car_n, 4))
        if self.insects:
            x += 0.01 * scatter(n, rng, self.insects, lambda: chirp(rng, 4200, 4800, 0.06))
        return x


class CityNight(City):
    """A street at night: fewer cars, a few crickets."""
    cars = 0.08
    insects = 2.0


class Country(Ambience):
    """Open country: a breeze and birds."""
    birds = 0.6           # calls per second

    def synth(self, n, rng):
        x = 0.04 * band(n, rng, 150, 900) * _drift(n, rng, 0.05, 0.4)
        if self.birds:
            x += 0.025 * scatter(n, rng, self.birds, lambda: chirp(rng, 2200, 5200, rng.uniform(0.08, 0.3)))
        return x


class Forest(Country):
    """A wood: wind in the trees and many birds."""
    birds = 1.2


class Wind(Country):
    """Wind and nothing else (deserts, snow, mountains)."""
    birds = 0.0


class Night(Ambience):
    """Night outdoors: crickets and a light wind."""

    def synth(self, n, rng):
        return 0.015 * scatter(n, rng, 3.0, lambda: chirp(rng, 4300, 4700, 0.05)) + \
            0.02 * band(n, rng, 100, 600) * _drift(n, rng, 0.05, 0.3)


class Rain(Ambience):
    """Rain falling, drops close by."""

    def synth(self, n, rng):
        drops = scatter(n, rng, 40, lambda: band(400, rng, 2000, 9000) * np.hanning(400))
        return 0.05 * band(n, rng, 800, 9000) + 0.02 * drops


class Sea(Ambience):
    """Waves rolling in."""

    def synth(self, n, rng):
        waves = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / RATE / 7.0 + rng.uniform(0, 6)) ** 2
        return 0.07 * band(n, rng, 100, 3000) * waves


class Space(Ambience):
    """A low drone (space, a spaceship, the moon)."""

    def synth(self, n, rng):
        return 0.02 * band(n, rng, 30, 200, tilt=0.5) + 0.008 * tone(n / RATE, 41) * _drift(n, rng, 0.02, 0.1)


def ambiences():
    return plugins.names("ambience")


def ambience(name, seconds, seed=0):
    """A bed of the ambience `name`, at least `seconds` long."""
    return plugins.get("ambience", name)().file(seconds, seed)


WEATHER = {"rain": "rain", "storm": "rain"}            # weather that drowns out the place
OUTDOOR_WEATHER = {"snow": "wind", "fog": "wind"}      # and weather that changes an outdoor one


def ambience_for(set_obj, time_of_day=None, weather=None):
    """The ambience a scene calls for: the weather's, else the set's own (Set.ambience)."""
    if weather in WEATHER:
        return WEATHER[weather]
    outdoor = set_obj is None or getattr(set_obj, "outdoor", False)
    if outdoor and weather in OUTDOOR_WEATHER:
        return OUTDOOR_WEATHER[weather]
    return set_obj.ambience(time_of_day) if set_obj is not None else "country"
