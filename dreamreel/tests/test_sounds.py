"""Sound effects and ambience (sounds.py): sounds are plugins that find a recording or make
themselves; places pick their own ambience; characters make footsteps, fights and claps sound; the
sounds keep time through moods and slow motion; music ducks under dialogue.

    python tests/test_sounds.py
"""
import os
import shutil
import sys
import tempfile
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import film, sounds  # noqa: E402


def seconds_of(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def library():
    names = sounds.names()
    assert {"punch", "footstep_wood", "door_open", "whoosh", "clap"} <= set(names), names
    # a recording is a kind of the made-here sound that stands in for it
    assert issubclass(dr.get("sound", "punch"), dr.get("sound", "smack"))
    assert issubclass(dr.get("sound", "footstep_grass"), dr.get("sound", "step"))
    assert {"room", "city", "forest", "rain", "sea"} <= set(sounds.ambiences())
    saved = sounds.CACHE
    sounds.CACHE = tempfile.mkdtemp(prefix="dreamreel-sounds-")
    try:                                    # offline: every sound is still there, made here
        for n in names:
            p = sounds.path(n, seed=1, download=False)
            assert p.endswith(".wav") and 0.03 < seconds_of(p) < 3, (n, p)
        assert sounds.path("punch", 0, download=False) != sounds.path("punch", 1, download=False), "takes vary"
        bed = sounds.ambience("city", 6.0)
        assert seconds_of(bed) >= 6.0
    finally:
        shutil.rmtree(sounds.CACHE, ignore_errors=True)
        sounds.CACHE = saved

    class Squeak(dr.Sound):                 # a new sound is a new class
        def synth(self, rng):
            return sounds.tone(0.15, lambda t: 2400 - 6000 * t, decay=0.04)
    assert "squeak" in sounds.names() and seconds_of(sounds.path("squeak")) > 0.1

    film_dir = tempfile.mkdtemp(prefix="dreamreel-film-")
    try:                                    # the film's own files replace or add sounds
        os.makedirs(os.path.join(film_dir, "audio", "sfx"))
        for f in ("punch.wav", "moo_1.wav", "moo_2.wav"):
            shutil.copy(sounds.path("pop"), os.path.join(film_dir, "audio", "sfx", f))
        assert sounds.path("punch", project_dir=film_dir).endswith("punch.wav")
        assert sounds.path("moo", 1, project_dir=film_dir).endswith("moo_2.wav")
        assert sounds.path("nothing_like_it", project_dir=film_dir) is None
    finally:
        shutil.rmtree(film_dir, ignore_errors=True)
    print(f"  library: ok ({len(names)} sounds, {len(sounds.ambiences())} ambiences)")


def places():
    cases = [({"kind": "room"}, None, None, "room"),
             ({"kind": "street"}, "night", None, "city_night"),
             ({"kind": "street"}, "day", "rain", "rain"),
             ({"kind": "outdoor", "biome": "forest"}, "day", None, "forest"),
             ({"kind": "outdoor", "biome": "beach"}, "night", None, "sea"),
             ({"kind": "outdoor", "biome": "meadow"}, "night", None, "night"),
             ({"kind": "outdoor", "biome": "meadow"}, "day", "snow", "wind")]
    for spec, tod, weather, want in cases:
        s = dr.Scene(spec, time_of_day=tod, weather=weather)
        got = sounds.ambience_for(s.set, tod, weather)
        assert got == want, (spec, tod, weather, got)
        assert os.path.basename(s.ambience_bed()[0]).startswith(f"ambience_{want}_")
    s = dr.Scene({"kind": "room"})
    s.ambience = "none"
    assert s.ambience_bed() is None
    s.ambience = "sea"
    assert "ambience_sea" in s.ambience_bed()[0]
    print("  places: ok (each place picks its own ambience)")


def characters():
    s = dr.Scene({"kind": "room", "floor": "wood"})
    mia = s.cast(mia={})
    mia.place("left", facing="right")
    mia.walk_to("right")
    steps = [n for _, _, _, n in s.sound_fx]
    assert len(steps) >= 4 and set(steps) == {"footstep_wood"}, steps
    mia.feel("sad")                          # a slow, sad clap keeps time with its slower hands
    t = s.clock
    mia.do("clap")
    claps = sorted(ts for ts, _, _, n in s.sound_fx if n == "clap")
    assert len(claps) == 4 and claps[-1] - t > 1.0, claps

    class Ghost(dr.ToyFigure):              # a body can change its footsteps
        def footstep_sound(self, footing):
            return None
    s = dr.Scene({"kind": "outdoor", "biome": "meadow"})
    g = s.cast(boo=dict(type="ghost"))
    tom = s.cast(tom={})
    g.place("left", facing="right")
    tom.place("center", facing="left")
    g.walk_to("right")
    assert not s.sound_fx, "ghosts walk silently"
    tom.walk_to("left")
    assert {n for *_, n in s.sound_fx} == {"footstep_grass"}

    s = dr.Scene({"kind": "street"})
    a, b = s.cast(a={}), s.cast(b={})
    a.place((-0.4, 0), facing="right")
    b.place((0.4, 0), facing="left")
    s.slow_motion(1.0, 0.5)
    t = s.clock
    a.do("punch", target="b")
    b.do("flinch")
    hit = next(ts for ts, _, _, n in s.sound_fx if n == "punch_heavy")
    s.finish()
    hit_after = next(ts for ts, _, _, n in s.sound_fx if n == "punch_heavy")
    assert hit_after > hit + 0.1, ("the blow lands later in slow motion", hit, hit_after)
    names = {n for *_, n in s.sound_fx}
    assert {"whoosh", "punch_heavy"} <= names, names
    meta = s.metadata()
    assert meta["sounds"] and all(os.path.exists(f) for _, f, _ in meta["sounds"]) and meta["ambience"]
    print(f"  characters: ok (footsteps, claps, a punch landing at {hit_after:.2f}s in slow motion)")


def ducking():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.sequence_editor_create()
    ed = sc.sequence_editor
    strips = ed.strips if hasattr(ed, "strips") else ed.sequences
    m = strips.new_sound(name="music", filepath=sounds.ambience("country", 10), channel=1, frame_start=1)
    m.volume = 0.5
    film.duck(m, [(48, 96), (100, 120)], 0.4)
    fc = next(f for f in (sc.animation_data.action.fcurves if hasattr(sc.animation_data.action, "fcurves")
                          else [c for layer in sc.animation_data.action.layers for st in layer.strips
                                for bag in st.channelbags for c in bag.fcurves])
              if f.data_path.endswith("volume"))
    assert abs(fc.evaluate(72) - 0.2) < 1e-3 and abs(fc.evaluate(20) - 0.5) < 1e-3 and abs(fc.evaluate(140) - 0.5) < 1e-3
    assert abs(fc.evaluate(98) - 0.2) < 1e-3, "lines close together stay ducked"
    print("  ducking: ok (the music dips under dialogue)")


def main():
    library()
    places()
    characters()
    ducking()
    print("sounds: all ok")


if __name__ == "__main__":
    main()
