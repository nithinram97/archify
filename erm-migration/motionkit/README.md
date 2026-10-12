# motionkit

Reusable building blocks for motion-graphics videos in **Blender 5 (EEVEE)**: trailers, product
reveals, title sequences, data stories.

You describe *what* happens ("the title pops in at 0.5 s, the camera orbits, a flash cuts to the next
shot") and motionkit does the Blender work: materials, keyframes, easing, camera rigs,
compositor glow, render settings and version quirks.

```python
import motionkit as mk

movie = mk.Movie("hello", length=6)
mk.Starfield()
mk.Text3D("Hello DMS", size=1.2, color="pink", glow=3).pop_in(at=0.5).float(start=1.2, end=6)
movie.camera.place((0, -12, 0.5)).push_in(to=(0, -8, 0.3), at=0, duration=6)
movie.overlay.caption("Built with motionkit", at=2.5, until=5.5)
movie.effects.glow().vignette()
movie.run()
```

```powershell
blender -b -P hello.py -- --preview --render     # quick half-size MP4
blender -b -P hello.py -- --render               # final 1080p MP4
blender -b -P hello.py -- --still 3              # one PNG at 3 s
blender -P hello.py                              # open Blender with the scene built
```

## What's inside

| Layer | You get |
|---|---|
| **Movie** | Clean scene, EEVEE tuned for motion graphics, shots, music, command-line rendering |
| **Assets** | `Text3D`, `Counter`, `Card`, `Screen`, `Logo`, `Sphere`, `Box`, `Ring` (upright or flat), `Arc`, `Line`, `Starfield`, `GridFloor`, `Globe`, `BarChart`, `ScreenWall`, `Portal`, `Group`, `Light` |
| **Looks** | Glowing (self-lit motion graphics) or lit (`lit=True`: shaded solids such as planets and products, with `Light`s) |
| **Motion** (on every asset) | `fade_in/out`, `pop_in/out`, `slide_in/out`, `rise_in`, `move_to`, `scale_to`, `rotate_to`, `spin`, `orbit`, `float`, `pulse`, `glow_to`, `color_to`, `show/hide`, `draw_on`, `type_on` ... |
| **Camera** | `place`, `move`, `cut_to`, `push_in`, `pull_out`, `orbit`, `crane`, `follow_path`, `shake`, `zoom`, `dolly_zoom`, `focus` |
| **Overlay** (screen space) | `caption`, `title`, `lower_third`, `text`, `image`, `box`, `letterbox`, `fade_from_black`, `fade_to_black`, `dip`, `flash` |
| **Transitions** | `cut`, `fade_through_black`, `dip_to_color`, `flash_cut`, `whip_pan`, `push_through`, `through_portal` |
| **Effects** | `glow` (bloom), `vignette`, `motion_blur` |

## Folder layout

```
motionkit/
  motionkit/            the package (import motionkit as mk)
    movie.py            Movie, shots, rendering, command line
    assets.py           ready-made 3D assets
    item.py             Item: the motions every asset shares
    camera.py           camera moves
    overlay.py          captions, titles, fades (screen space)
    transitions.py      shot-to-shot transitions
    effects.py          glow, vignette, motion blur
    materials.py        GlowMaterial (self-lit, animatable alpha/glow/colour)
    keys.py, timing.py  keyframes and easing (seconds, named eases)
    color.py            colours and palettes
    _compat.py          every Blender-version difference, in one place
    data/               world map dots for Globe
  examples/             01 hello title (the demo), 02 product reveal, 03 globe tour, 04 solar system
  docs/                 guide, concepts, API reference, cookbook, Shot Script, troubleshooting
  gemini-gem/           everything to set up the Gemini gem that writes motionkit code
  presentation/         developer deck (PowerPoint / Google Slides) and the demo video
  tests/                smoke_test.py (every component, 2 renders), cookbook_test.py (every recipe)
```

## Documentation

1. [Getting started](docs/getting-started.md): install, run the demo, make your first change.
2. [Concepts](docs/concepts.md): seconds, items, shots, the camera target, overlay coordinates.
3. [API reference](docs/api-reference.md): every class, method and argument.
4. [Cookbook](docs/cookbook.md): copy-paste recipes.
5. [Shot Script](docs/shot-script.md): the plain-language format for asking Gemini for a video.
6. [Troubleshooting](docs/troubleshooting.md) and [Extending the kit](docs/extending.md).
7. [Gemini gem setup](gemini-gem/GEM.md): name, description, instructions and the knowledge file to upload.

## Requirements

Blender 5.0 or later (tested on 5.0.1; the compatibility layer also covers 4.2-4.5, untested). Nothing to install: the examples add the
kit to Python's path themselves. To use it from your own folder, copy the inner `motionkit/` package
next to your script or add its parent folder to `sys.path`.

Check your install at any time:

```powershell
blender -b -P tests/smoke_test.py       # builds every component, renders two frames
blender -b -P tests/cookbook_test.py    # runs every recipe in docs/cookbook.md
```
