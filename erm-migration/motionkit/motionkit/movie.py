"""`Movie`: the one object every script starts with.

    import motionkit as mk

    movie = mk.Movie("hello", length=6)            # 6 seconds, 1920x1080, 24 fps, EEVEE
    title = mk.Text3D("Hello DMS", color="pink").pop_in(at=0.5)
    movie.camera.place((0, -10, 0)).push_in(to=(0, -7, 0), at=0, duration=6)
    movie.effects.glow()
    movie.run()                                    # build; render if asked on the command line

Run from a terminal (PowerShell):
    blender -b -P hello.py -- --preview --render   # fast, half-size check
    blender -b -P hello.py -- --render             # final MP4
    blender -b -P hello.py -- --still 3.0          # one PNG at 3 seconds
    blender -P hello.py                            # open Blender with the scene built (scrub & tweak)
"""
import os
import sys
from contextlib import contextmanager

import bpy
from mathutils import Vector

from . import _compat, timing
from .camera import Camera
from .color import rgba, use_palette
from .effects import Effects
from .overlay import Overlay
from .stage import STAGE, new_collection


def _reset_scene():
    scene = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights,
                  bpy.data.images, bpy.data.node_groups):
        for item in list(block):
            if item.users == 0:
                block.remove(item)
    for coll in list(scene.collection.children):
        scene.collection.children.unlink(coll)
    if scene.sequence_editor:
        for s in list(_compat.sequence_strips(scene)):
            _compat.sequence_strips(scene).remove(s)
    return scene


class Shot:
    """A section of the movie with its own stage. Use as `with movie.shot("name", start, end) as shot:`.

    Attributes:
        start, end: seconds.
        origin: where this shot's stage sits in the world.
    """

    def __init__(self, movie, name, start, end, origin):
        self.movie, self.name, self.start, self.end = movie, name, start, end
        self.origin = Vector(origin)
        self.collection = new_collection(name, movie.collection)
        self.root = bpy.data.objects.new(f"{name} stage", None)
        self.collection.objects.link(self.root)
        self.root.location = self.origin

    def point(self, x, y, z):
        """A position inside this shot as a world position (for transitions and cuts)."""
        return tuple(self.origin + Vector((x, y, z)))


class Movie:
    """Sets up a clean scene for a video.

    Args:
        name: used for the output file name.
        length: seconds.
        fps: frames per second (24 = cinematic, 30 = screen recordings).
        size: (width, height) in pixels.
        background: colour behind everything.
        palette: "neon", "corporate" or a Palette; colour names resolve against it.
        quality: "final" or "preview" (preview is also chosen by --preview on the command line).
        lens: camera focal length in mm (35 = natural, 24 = wide, 50+ = tight).
        out: output path for the video (default: render/<name>.mp4 next to the script).
    """

    def __init__(self, name="movie", length=10.0, fps=24, size=(1920, 1080), background="night",
                 palette="neon", quality="final", lens=35.0, out=None):
        use_palette(palette)
        timing.CLOCK = timing.Clock(fps)
        self.name, self.length, self.fps, self.size = name, length, fps, size
        self.scene = _reset_scene()
        self.collection = new_collection(name)
        STAGE.collection, STAGE.root, STAGE.origin = self.collection, None, Vector((0, 0, 0))
        self.camera = Camera(lens)
        self.overlay = Overlay(self.camera, size)
        self.effects = Effects(self.scene)
        self.quality = quality
        script = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0].endswith(".py") else os.getcwd()
        self.out = out or os.path.join(os.path.dirname(script) if script.endswith(".py") else script, "render", f"{name}.mp4")
        self._shots = 0
        self._set_world(background)
        self._render_settings()

    # ------------------------------------------------------------------ structure
    @contextmanager
    def shot(self, name, start, end, origin=None):
        """Build a section of the movie on its own stage (positions inside are relative to it).

        Stages are spread 500 units apart along X, so a camera cut between shots never shows the
        neighbouring stage.
        """
        self._shots += 1
        sh = Shot(self, name, start, end, origin if origin is not None else (500.0 * self._shots, 0, 0))
        saved = (STAGE.collection, STAGE.root, STAGE.origin)
        STAGE.collection, STAGE.root, STAGE.origin = sh.collection, sh.root, sh.origin
        try:
            yield sh
        finally:
            STAGE.collection, STAGE.root, STAGE.origin = saved

    def add_music(self, path, volume=1.0, at=0.0):
        """Add a soundtrack (WAV/MP3) starting at `at` seconds."""
        if not os.path.exists(path):
            print(f"[motionkit] music not found: {path}")
            return
        strip = _compat.sequence_strips(self.scene).new_sound("music", path, channel=1, frame_start=timing.CLOCK.frame(at))
        strip.volume = volume
        self.scene.render.ffmpeg.audio_codec = "AAC"

    # ------------------------------------------------------------------ settings
    def _set_world(self, background):
        world = self.scene.world or bpy.data.worlds.new("World")
        self.scene.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes.get("Background") or world.node_tree.nodes.new("ShaderNodeBackground")
        bg.inputs["Color"].default_value = rgba(background)
        bg.inputs["Strength"].default_value = 1.0

    def _render_settings(self):
        """EEVEE tuned for self-lit motion graphics: no lights, shadows or ray tracing to pay for."""
        s, r = self.scene, self.scene.render
        r.engine = _compat.eevee_engine()
        r.resolution_x, r.resolution_y = self.size
        r.fps = self.fps
        s.frame_start, s.frame_end = 1, timing.CLOCK.frame(self.length) - 1
        ee = s.eevee
        for attr, val in (("use_shadows", False), ("use_raytracing", False), ("use_volumetric_shadows", False),
                          ("use_gtao", False), ("use_ssr", False), ("use_soft_shadows", False),
                          ("use_fast_gi", False), ("taa_samples", 8)):
            if hasattr(ee, attr):
                setattr(ee, attr, val)
        r.film_transparent = False
        if hasattr(r, "filter_size"):
            r.filter_size = 1.5
        s.view_settings.view_transform = "Standard"  # brand colours come out exactly as specified
        s.view_settings.look = "None"
        self._apply_quality()

    def _apply_quality(self):
        preview = self.quality == "preview"
        self.scene.render.resolution_percentage = 50 if preview else 100
        ee = self.scene.eevee
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = 16 if preview else 64

    # ------------------------------------------------------------------ output
    def finish(self):
        """Build effects and restore the playhead. Called by run(), render() and still()."""
        self.effects.build()
        self.scene.frame_set(1)

    def render(self, out=None, preview=None):
        """Render the whole movie to an MP4 (with sound if music was added)."""
        if preview is not None:
            self.quality = "preview" if preview else "final"
            self._apply_quality()
        self.finish()
        r = self.scene.render
        _compat.set_video_output(r)
        r.ffmpeg.constant_rate_factor = "MEDIUM" if self.quality == "preview" else "HIGH"
        path = os.path.abspath(out or self.out)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r.filepath = path
        bpy.ops.render.render(animation=True)
        print(f"[motionkit] rendered {path}")
        return path

    def still(self, at, out=None):
        """Render one frame at `at` seconds to a PNG (quick look without rendering the video)."""
        self.finish()
        r = self.scene.render
        _compat.set_image_output(r)
        self.scene.frame_set(timing.CLOCK.frame(at))
        path = os.path.abspath(out or os.path.join(os.path.dirname(self.out), f"{self.name}_{at:05.2f}s.png"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r.filepath = path
        bpy.ops.render.render(write_still=True)
        print(f"[motionkit] still {path}")
        return path

    def save(self, path):
        """Save the built scene as a .blend file to open and tweak by hand."""
        self.finish()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(path))

    def run(self):
        """Finish the scene and act on the command-line options after `--`:

            --preview          half resolution, fewer samples
            --render           render the MP4
            --still 3.5        render one PNG at 3.5 s (repeatable: --still 1 --still 4)
            --out path.mp4     where to write the video
            --save file.blend  save the scene
            --percent 25       render at 25% size (very fast test renders)
        """
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
        opt = lambda name: argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None
        if "--preview" in argv:
            self.quality = "preview"
            self._apply_quality()
        if opt("--percent"):
            self.scene.render.resolution_percentage = int(opt("--percent"))
        self.finish()
        print(f"[motionkit] built '{self.name}': {self.length:g} s at {self.fps} fps, {self.size[0]}x{self.size[1]}")
        if opt("--save"):
            self.save(opt("--save"))
        stills = [float(argv[i + 1]) for i, a in enumerate(argv) if a == "--still" and i + 1 < len(argv)]
        for t in stills:
            self.still(t)
        if "--render" in argv:
            self.render(opt("--out"))
