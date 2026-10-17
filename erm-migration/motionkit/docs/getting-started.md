# Getting started

## 1. Install Blender 5

Download Blender 5.0+ from blender.org and install it. To run it from PowerShell, either use the full
path or add Blender's folder to your PATH:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --version
# or, once Blender's folder is on PATH:
blender --version
```

## 2. Run the demo

From the `motionkit` folder:

```powershell
blender -b -P examples/01_hello_title.py -- --still 3.5            # one picture, a few seconds
blender -b -P examples/01_hello_title.py -- --preview --render     # half-size MP4, about a minute
blender -b -P examples/01_hello_title.py -- --render               # final 1080p MP4
```

* `-b` runs Blender without its window, `-P` runs the script, and everything after `--` is for motionkit.
* Output goes to `examples/render/` (`hello_title.mp4`, `hello_title_03.50s.png`).

To see and scrub the scene in Blender's window instead:

```powershell
blender -P examples/01_hello_title.py
```

Press **Space** to play, drag the timeline to scrub, and press **Numpad 0** to look through the camera.

## 3. Read the demo

```python
movie = mk.Movie("hello_title", length=8)            # an 8-second, 1080p, 24 fps movie

mk.Starfield()                                         # background stars
mk.GridFloor(height=-1.6)                              # glowing floor grid

ring = mk.Ring(radius=2.6, color="indigo", glow=3).at(0, 1.5, 0.3)
ring.draw_on(at=0.3, duration=1.2).spin(turns=0.25, start=1.5, end=8, axis="Y")

title = mk.Text3D("Hello DMS", size=1.1, color="pink", glow=3, depth=0.12).at(0, 0, 0.3)
title.pop_in(at=0.8, duration=0.7).float(start=1.5, end=8, height=0.08)

movie.camera.place((0, -14, 1.5), look_at=(0, 0, 0.3))
movie.camera.orbit(center=(0, 0, 0.3), radius=11, start=-25, end=12, height=1.0, at=0, duration=8)

movie.overlay.caption("Built with motionkit in 25 lines", eyebrow="Demo", at=3, until=6.6)
movie.overlay.fade_from_black(at=0, duration=1)
movie.overlay.fade_to_black(at=7.2, duration=0.8)
movie.effects.glow().vignette(0.3)

movie.run()
```

Every line is one idea: *create* something, *place* it (`.at`), *animate* it (`.pop_in`, `.spin`, ...),
move the *camera*, add *words on screen*, add *effects*, *run*.

## 4. Make your first change

* Change the words: `mk.Text3D("Your team name", ...)`.
* Change the colour: `color="cyan"` (palette names) or `color="#22c55e"` (any hex).
* Make it slower: `title.pop_in(at=0.8, duration=1.5)`.
* Swap the camera move: replace the `orbit` line with
  `movie.camera.push_in(to=(0, -7, 0.4), at=0, duration=8)`.
* Add a logo: `mk.Logo("my_logo.png", height=1).at(0, 0, -1.4).fade_in(at=2)`.

Run with `--still 3` after each change: a single frame renders in seconds.

## 5. Make your own movie

1. Copy `examples/01_hello_title.py` to a new file next to it, and keep the two `sys.path` lines at the top.
2. Plan on paper first: *0-2 s title, 2-5 s screens, 5-6 s flash, 6-10 s chart...*
3. Build one shot at a time and check it with `--still`.
4. When it looks right, render `--preview --render`, watch it, then do the final `--render`.

Or describe it to the **motionkit gem** in Gemini using the [Shot Script](shot-script.md) format and
paste the code it writes.

## Render times

EEVEE renders a 1080p frame of a typical motionkit scene in about 1-3 s on a laptop GPU, so a
10-second movie takes a few minutes. `--preview` (half size, fewer samples) is about 4x faster.
