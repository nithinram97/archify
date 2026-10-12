# motionkit knowledge (for the motionkit Director gem)
motionkit is a Python library for making motion-graphics videos in Blender 5 with EEVEE. Scripts run with `blender -b -P script.py -- --render`. This file has the concepts, the complete API, the Shot Script format, recipes and full example scripts. Only use the API documented here.


<!-- docs/concepts.md -->

# Concepts

Six ideas explain the whole kit.

## 1. Time is in seconds

Every `at=`, `start=`, `end=`, `until=` and `duration=` is in **seconds from the start of the movie**.
The kit converts to frames using the movie's fps. You never type a frame number.

## 2. Everything on screen is an Item

All assets return an `Item`. Items share one set of motions, and each motion returns the item, so you
can chain them:

```python
mk.Text3D("Hello").at(0, 0, 1).pop_in(at=0.5).float(start=1, end=5).fade_out(at=5)
```

* **Placement** (`at`, `size`, `turn`) sets things without animation.
* **Motions** (`move_to`, `fade_in`, `spin`, ...) create keyframes.
* An item that fades or pops in is **invisible before that moment**, with nothing else to set.
* **Order doesn't matter**: every motion starts from wherever the item (or camera) stands at that
  moment, which is its last keyframe at or before `at`.
* `item.obj` is the underlying Blender object, for anything the kit doesn't cover.

## 3. The world and the camera

* Blender units, **Z is up**. The camera usually stands at negative Y looking towards +Y.
* `(0, 0, 0)` is the centre of the stage. A sensible default camera is `place((0, -12, 1), look_at=(0, 0, 0))`.
* The camera always **looks at a target point**. You direct it like a cinematographer: *stand here,
  look there, move there.* It never needs rotation angles.
* Text, screens and logos are created upright and facing the camera.

Rough sizes with the default 35 mm lens and the camera 12 units away: the frame is about 12 units wide
and 7 tall, and a `Text3D` of `size=1` is a large title.

## 3b. Axes and planes (read this before 3D work)

```
            Z (up)
            |
            |    Y (away from the camera, into the screen)
            |   /
            |  /
            | /
            +---------- X (right)
   camera at (0, -12, 1), looking towards +Y
```

| Plane | Contains | Use it for |
|---|---|---|
| **Screen plane** (X and Z) | things that face the camera | text, screens, logos, `Ring()` (default), halos |
| **Ground plane** (X and Y) | things lying flat | floors (`GridFloor`), orbits (`item.orbit`), `Ring(facing="up")`, maps, bar-chart bases |

* Anything that **circles** something else: use `item.orbit(around=..., radius=..., turns=...)`. It moves
  on the ground plane (tilt it with `tilt=`). Never build orbits from rotations by hand.
* Anything that **turns on its own axis** (a planet's day, a spinning logo seen from the front): `.spin(axis="Z")`.
  A ring facing the camera turns with `axis="Y"`.
* Looking **from above**: put the camera high on Z (`move(to=(0, -6, 12), look_at=(0, 0, 0))`).

## 4. Shots

For longer movies, build each section on its own stage:

```python
with movie.shot("intro", 0, 5) as s1:
    mk.Text3D("Act one")                         # positions here are relative to this shot
    movie.camera.place((0, -10, 0))              # ...and so are camera positions
with movie.shot("data", 5, 10) as s2:
    mk.BarChart([3, 5, 2])
mk.transitions.flash_cut(movie, at=5, to=s2.point(0, -9, 0), look_at=s2.point(0, 0, 0))
```

* Stages sit 500 units apart, so a camera cut between shots is clean.
* **Inside** a `with movie.shot(...)` block, positions (objects *and* camera) are relative to that shot.
* **Outside** it, use `shot.point(x, y, z)` to refer to a place inside a shot (transitions need this).
* Short movies don't need shots at all.

## 5. The overlay (screen space)

`movie.overlay` is a layer glued to the camera for captions, titles, logos and fades. Nothing in
the 3D scene can cover it.

* `x` runs from -0.5 (left edge) to 0.5 (right edge); `y` from -0.5 (bottom) to 0.5 (top).
* Sizes are fractions of the frame height: `size=0.05` is 5% of the height.
* `at=` fades in, `until=` fades out.

## 6. Look: glowing or lit

There are two looks, and you choose per object:

| | **Glowing** (default) | **Lit** (`lit=True`) |
|---|---|---|
| What it is | Self-lit flat colour; ignores lights | A real surface shaded by lights: bright side, dark side, highlights |
| Use for | Text, UI, screens, logos, rings, lines, suns, neon | Planets, products, blocks, anything that should look solid |
| Needs | `movie.effects.glow()` for bloom when `glow` > 1 | At least one `mk.Light(...)` |

* A glowing object never blocks or shadows light, so a glowing sun can hold the `Light` that lights the planets.
* Lit objects take `roughness` (0 glossy, 1 matte) and `metallic` (0 plastic/rock, 1 metal).
* A typical lit setup: `mk.Light("area", 1500).at(4, -6, 6).point_at(0, 0, 0)` (key) plus
  `mk.Light("sun", 0.3).point_at(0, 0, 0)` (soft fill).

## 6b. Colours and glow

* Colours: palette names (`"pink"`, `"indigo"`, `"cyan"`, `"white"`, `"muted"`, `"night"`, `"gold"`,
  `"green"`, `"red"`) or any hex string (`"#22c55e"`). Choose the palette with `Movie(palette="neon")` or
  `"corporate"`, or make your own `mk.Palette`.
* Glowing items are **self-lit**: no lights needed, and colours come out exactly as specified. Lit items
  (`lit=True`) are shaded by the `Light`s you add.
* `glow=1` is a flat colour; `glow=2`-`4` glows once `movie.effects.glow()` is on.
* Opacity, glow and colour are animatable on every item (`fade_to`, `glow_to`, `color_to`).

## Easing

Every motion takes `ease=`: `"smooth"` (default), `"linear"`, `"ease_in"`, `"ease_out"`,
`"ease_in_out"`, `"back"` (overshoot), `"bounce"`, `"elastic"`, `"snap"` (hard switch).

## Why EEVEE

motionkit's look is self-lit objects plus bloom, so there's no light transport to simulate. EEVEE renders
it in real time and looks the same as Cycles here, many times faster. The kit turns off what this style
doesn't use (shadows, ray tracing, volumes), uses 64 samples for finals and 16 for previews, and does
the glow in the GPU compositor.


<!-- docs/api-reference.md -->

# API reference

`import motionkit as mk`. Times are seconds, positions `(x, y, z)` in Blender units (Z up), colours
are palette names or hex strings. Every method that animates returns its object, so calls chain.

---

## Movie

```python
movie = mk.Movie(name="movie", length=10.0, fps=24, size=(1920, 1080), background="night",
                 palette="neon", quality="final", lens=35.0, out=None)
```

| Argument | Meaning |
|---|---|
| `name` | Output file name (`render/<name>.mp4` next to the script) |
| `length` | Duration in seconds |
| `fps` | 24 (cinematic) or 30 |
| `size` | `(width, height)`: `(1920, 1080)`, `(1080, 1920)` vertical, `(1080, 1080)` square |
| `background` | Colour behind everything |
| `palette` | `"neon"`, `"corporate"` or a `mk.Palette` |
| `quality` | `"final"` (64 samples) or `"preview"` (half size, 16 samples) |
| `lens` | Camera focal length in mm |
| `out` | Video path override |

Creating a Movie **clears the current Blender scene**, then sets up the camera, the overlay and EEVEE.

| Member | Does |
|---|---|
| `movie.camera` | The [Camera](#camera) |
| `movie.overlay` | The [Overlay](#overlay-screen-space) |
| `movie.effects` | The [Effects](#effects) |
| `with movie.shot(name, start, end, origin=None) as shot:` | Build a section on its own stage ([concepts](concepts.md#4-shots)) |
| `shot.point(x, y, z)` | A position inside the shot, as a world position (for transitions) |
| `movie.add_music(path, volume=1.0, at=0.0)` | Soundtrack (WAV/MP3) |
| `movie.run()` | Finish, then act on command-line options (below) |
| `movie.render(out=None, preview=None)` | Render the MP4 now |
| `movie.still(at, out=None)` | Render one PNG at `at` seconds |
| `movie.save(path)` | Save a `.blend` to open by hand |

**Command line** (after `--`): `--preview`, `--render`, `--still 3.5` (repeatable), `--out file.mp4`,
`--save file.blend`, `--percent 25` (tiny test renders).

---

## Item (motions shared by every asset)

### Placement (no animation)
| Method | Does |
|---|---|
| `.at(x, y, z)` | Place |
| `.size(s)` | Scale: a number or `(x, y, z)` |
| `.turn(x, y, z)` | Rotation in degrees |
| `.face_camera()` | Always face the camera (labels) |
| `.parent_to(item)` | Move together with another item |

### Visibility
| Method | Does |
|---|---|
| `.show(at)` / `.hide(at)` | Instant on/off |
| `.visible(start, end=None)` | Only visible between start and end |
| `.fade_in(at, duration=0.5, ease)` | Fade up from invisible |
| `.fade_out(at, duration=0.5, ease)` | Fade to invisible |
| `.fade_to(opacity, at, duration=0.5, ease)` | Dim to a partial opacity |

### Entrances and exits
| Method | Does |
|---|---|
| `.pop_in(at, duration=0.5, overshoot=1.12)` | Grow from nothing with a bounce |
| `.pop_out(at, duration=0.4)` | Shrink away |
| `.slide_in(at, duration=0.8, direction="left", distance=3.0, fade=True, ease="ease_out")` | Arrive from `"left"`, `"right"`, `"up"`, `"down"`, `"front"`, `"back"` or a vector |
| `.slide_out(at, duration=0.8, direction="right", distance=3.0, fade=True, ease="ease_in")` | Leave |
| `.rise_in(at, duration=0.8, distance=0.6)` | Drift up while fading in (titles) |

### Motion
| Method | Does |
|---|---|
| `.move_to(x, y, z, at, duration=1.0, ease)` | Travel to a point |
| `.move_by(dx, dy, dz, at, duration=1.0, ease)` | Travel by an offset |
| `.scale_to(s, at, duration=0.6, ease)` | Grow or shrink |
| `.rotate_to(x, y, z, at, duration=1.0, ease)` | Rotate to angles (degrees) |
| `.spin(turns=1.0, start=0.0, end=4.0, axis="Z", ease="linear")` | Full turns |
| `.float(start=0.0, end=4.0, height=0.12, period=2.0)` | Idle bobbing |
| `.pulse(at, times=1, amount=1.15, period=0.5)` | Grow and settle (draws the eye) |
| `.orbit(around=(0,0,0), radius=3.0, turns=1.0, start=0.0, end=8.0, tilt=0.0, phase=0.0, clockwise=False, path=False, path_color="muted", ease="linear")` | Circle a point or an Item on the ground plane. `around=item` follows that item (moons). `phase` = start angle in degrees, `path=True` draws the orbit ring. Combine with `.spin()` for the item's own rotation |

### Look
| Method | Does |
|---|---|
| `.glow_to(strength, at, duration=0.5, ease)` | Animate the glow |
| `.color_to(color, at, duration=0.5, ease)` | Animate the colour (solid colours) |

`item.obj` is the Blender object; `item.materials` holds its GlowMaterials; `item.parts` holds its child items.

---

## Assets

| Constructor | Notes |
|---|---|
| `mk.Text3D(text, size=1.0, color="white", glow=1.5, depth=0.05, font=None, align="center", spacing=1.0, opacity=1.0, lit=False)` | `font` = path to .ttf/.otf. Extra: `.type_on(at, duration=1.0, cursor=False)` |
| `mk.Counter(end, start=0, at=0.0, duration=1.5, size=1.0, color="white", glow=1.5, prefix="", suffix="", steps=30, decimals=0, font=None)` | Counts from start to end |
| `mk.Card(width=2.0, height=1.2, color="white", glow=1.0, image=None, opacity=1.0, lit=False)` | Flat rectangle facing the camera |
| `mk.Screen(image, width=3.2, frame_color="pink", frame_glow=2.5, frame=0.04, opacity=1.0)` | Screenshot with a glowing frame; `.height` |
| `mk.Logo(image, height=1.0, opacity=1.0)` | PNG with transparency |
| `mk.Sphere(radius=1.0, color="indigo", glow=None, opacity=1.0, blend=False, lit=False, roughness=0.6, metallic=0.0)` | Glowing ball (sun, marker) or, with `lit=True`, a shaded planet/object |
| `mk.Box(width=1.0, depth=1.0, height=1.0, color="white", bevel=0.05, lit=True, glow=None, roughness=0.4, metallic=0.0, opacity=1.0)` | Block with rounded edges (lit) |
| `mk.Light(kind="point", power=1000.0, color="white", size=0.5, shadows=True)` | `kind`: `"point"`, `"sun"`, `"spot"`, `"area"`. Power in watts (point/spot/area, 500-3000 typical) or strength (sun, 0.2-6). `.point_at(x, y, z)`, `.power_to(power, at, duration)` |
| `mk.Ring(radius=2.0, thickness=0.04, color="pink", glow=3.0, start=0.0, end=360.0, opacity=1.0, facing="camera")` | `facing="camera"` stands up; `facing="up"` lies flat (orbits, floor targets). Extra: `.draw_on(at, duration=1.0, ease, from_middle=False)`, `.erase(at, duration)` |
| `mk.Arc(radius=2.0, start=0.0, end=120.0, **ring_args)` | Partial ring (degrees, 0 = right, 90 = top) |
| `mk.Line(points, thickness=0.03, color="cyan", glow=2.5, opacity=1.0)` | Smooth path; `.draw_on`, `.erase` |
| `mk.Starfield(count=1500, spread=(40, 30, 25), color="muted", size=0.03, glow=1.5, seed=7, center=(0, 20, 0))` | Background stars |
| `mk.GridFloor(size=40.0, spacing=1.0, color="indigo", glow=1.2, height=-2.0, thickness=0.012, opacity=0.6)` | Glowing ground grid |
| `mk.Globe(radius=3.0, land_color="cyan", ocean_color="#0b1530", dot_size=0.022, glow=1.4)` | `.focus(lat, lon, at, duration=1.5)`, `.marker(lat, lon, color="pink", size=0.09, label=None, label_size=0.25)` returns an Item (label = `.parts[0]`) |
| `mk.BarChart(values, labels=None, width=6.0, height=3.0, color="indigo", highlight_color="pink", show_values=True, text_color="white")` | Bottom at the item's position. `.grow(at, duration=1.0, stagger=0.12)`, `.highlight(index, at, duration=0.8)`, `.bars` |
| `mk.ScreenWall(images, columns=3, width=3.0, gap=0.35, curve=8.0, frame_color="pink")` | `.cascade_in(at, stagger=0.15, duration=0.6)`, `.screens` |
| `mk.Portal(radius=2.2, color="pink", color2="indigo", glow=4.0)` | `.open(at, duration=0.8)`; fly through with `transitions.through_portal` |
| `mk.Group(*items, name="group")` | Move several items as one |

---

## Camera

`movie.camera`. Positions inside a shot are relative to the shot. Every move starts from where the camera
stands at `at`.

| Method | Does |
|---|---|
| `place(position, look_at=(0, 0, 0), at=0.0)` | Put the camera somewhere |
| `move(to, look_at=None, at=0.0, duration=2.0, ease="smooth")` | Travel (and turn to look elsewhere) |
| `cut_to(position, look_at=(0, 0, 0), at=0.0)` | Hard cut |
| `push_in(to, at=0.0, duration=3.0, ease="ease_in_out")` | Move closer, same subject |
| `pull_out(to, at=0.0, duration=3.0, ease="ease_in_out")` | Move away (reveal) |
| `orbit(center=(0,0,0), radius=10.0, start=-30.0, end=30.0, height=0.0, at=0.0, duration=4.0, ease="smooth")` | Circle around; angles in degrees, 0 = in front, 90 = right side |
| `crane(rise=3.0, at=0.0, duration=3.0, ease="smooth")` | Rise (or sink with a negative value) |
| `follow_path(points, look_at=None, at=0.0, duration=4.0, ease="smooth")` | Fly through points |
| `shake(at=0.0, duration=0.6, strength=0.15, frequency=12.0, seed=1)` | Impact / handheld shake |
| `zoom(lens, at=0.0, duration=1.0, ease="smooth")` | Change focal length (mm) |
| `dolly_zoom(distance, at=0.0, duration=2.0)` | Vertigo effect |
| `focus(distance=None, f_stop=2.8, item=None)` | Depth of field on an item or a distance |

`movie.camera.obj` is the camera object; `movie.camera.target` is the empty it looks at.

---

## Overlay (screen space)

`movie.overlay`. `x` from -0.5 to 0.5, `y` from -0.5 to 0.5, sizes as fractions of the frame height.
`at` fades in, `until` fades out.

| Method | Does |
|---|---|
| `text(text, x=0, y=0, size=0.05, color="white", glow=1.0, at=None, until=None, fade=0.4, font=None, align="center", spacing=1.0, rise=True)` | Any text |
| `caption(text, eyebrow=None, at=None, until=None, color="white", accent="pink")` | Subtitle line near the bottom, with a small label above |
| `title(text, subtitle=None, at=None, until=None, color="white", accent="pink", size=0.14)` | Big centred title |
| `lower_third(name, role=None, at=None, until=None, accent="pink")` | Name and role, bottom left |
| `image(path, x=0, y=0, height=0.2, at=None, until=None, fade=0.4)` | Picture or logo on screen |
| `box(x, y, w, h, color="black", opacity=1.0, at=None, until=None, fade=0.4)` | Filled rectangle (backing panel) |
| `letterbox(amount=0.1, color="black")` | Cinema bars |
| `fade_from_black(at=0.0, duration=1.0)` / `fade_to_black(at, duration=1.0)` | Fades |
| `dip(at, color="black", duration=0.8)` | Fade to a colour and back, peaking at `at` |
| `flash(at, color="white", strength=0.9, duration=0.4)` | Flash peaking at `at` |

---

## Transitions

`from motionkit import transitions as tr`. `to` / `look_at` are where the camera lands (use
`shot.point(...)`). `at` is the moment of the cut.

| Function | Feel |
|---|---|
| `tr.cut(movie, at, to, look_at)` | Plain cut |
| `tr.fade_through_black(movie, at, to=None, look_at=None, duration=1.0)` | Calm, chapter change |
| `tr.dip_to_color(movie, at, color="white", to=None, look_at=None, duration=0.8)` | Soft reveal |
| `tr.flash_cut(movie, at, to=None, look_at=None, color="white")` | Energetic |
| `tr.whip_pan(movie, at, to, look_at, duration=0.4, side=8.0)` | Fast sideways smear |
| `tr.push_through(movie, at, to, look_at, duration=0.8)` | Rush forward into the next shot |
| `tr.through_portal(movie, portal, at, to, look_at, duration=1.6)` | Fly through a `Portal` |

---

## Effects

`movie.effects` (chainable).

| Method | Does |
|---|---|
| `glow(strength=1.0, threshold=0.85, size=0.7, kind="BLOOM")` | Bloom on bright materials (`kind`: `"BLOOM"`, `"FOG_GLOW"`, `"STREAKS"`) |
| `vignette(amount=0.35)` | Darker corners |
| `motion_blur(shutter=0.5)` | Motion blur |

---

## Low level

| API | Does |
|---|---|
| `mk.key(target, prop, at, value, ease="smooth")` | One keyframe on any Blender property |
| `mk.animate(target, prop, {t: value, ...}, ease="smooth" or [eases])` | Several keyframes |
| `mk.GlowMaterial(color="white", glow=None, alpha=1.0, image=None, blend=True, name=..., lit=False, roughness=0.6, metallic=0.0)` | `.alpha`, `.strength`, `.color` sockets, `.mat`; `lit=True` = shaded surface |
| `mk.Palette(name, {"pink": "#...", ...})` | Your own colour names |
| `mk.EASINGS` | The ease names |

Anything else: use `bpy` directly on `item.obj`. The kit never hides Blender from you.


<!-- docs/shot-script.md -->

# Shot Script

A plain-language format for describing a motionkit video. Write it yourself, or let the Gemini gem
draft it from a loose idea. The gem turns a Shot Script into a runnable Python script, one line at a time.

## Example

```
MOVIE "hello_dms" 8s 1920x1080 24fps palette neon

SHOT intro 0s-8s
  ADD stars
  ADD grid floor at 0,0,-1.6
  ADD ring "halo" radius 2.6 indigo glow 3 at 0,1.5,0.3
  ADD text "title" "Hello DMS" size 1.1 pink glow 3 at 0,0,0.3
  halo: draw-on @0.3 for 1.2s | spin 0.25 turns axis Y 1.5s-8s
  title: pop-in @0.8 for 0.7s | float 1.5s-8s
  CAMERA place 0,-14,1.5 look 0,0,0.3
  CAMERA orbit around 0,0,0.3 radius 11 from -25° to 12° height 1 @0 for 8s
  CAPTION "Built with motionkit" eyebrow "Demo" @3 until 6.6

START fade-from-black for 1s
END fade-to-black @7.2 for 0.8s
EFFECTS glow | vignette 0.3
```

## Grammar

| Write | Means |
|---|---|
| `@2.5` | at 2.5 seconds |
| `for 1.2s` | lasting 1.2 seconds |
| `1.5s-8s` | from 1.5 to 8 seconds |
| `at x,y,z` | position (Z is up; the camera usually sits at negative Y) |
| `"name"` right after `ADD <thing>` | gives the item a name so later lines can animate it |
| `name: motion | motion` | chain motions on a named item |
| colours | palette names (`pink`, `indigo`, `cyan`, `white`, `muted`, `gold`, `green`, `red`) or `#hex` |
| `#` | a comment |

Indent the lines that belong to a shot. Short videos can use a single `SHOT`.

## Vocabulary

### Movie
| Shot Script | motionkit |
|---|---|
| `MOVIE "name" 10s 1920x1080 24fps palette neon background night` | `mk.Movie("name", length=10, size=(1920, 1080), fps=24, palette="neon", background="night")` |
| `MUSIC "file.wav" volume 0.8` | `movie.add_music("file.wav", volume=0.8)` |
| `SHOT name 4s-10s` | `with movie.shot("name", 4, 10) as name:` |
| `EFFECTS glow | vignette 0.3 | motion blur` | `movie.effects.glow().vignette(0.3).motion_blur()` |
| `START fade-from-black for 1s` / `END fade-to-black @9 for 1s` | overlay fades |

### ADD
| Shot Script | motionkit |
|---|---|
| `ADD text "id" "Words" size 1 pink glow 2 font "x.ttf"` | `mk.Text3D("Words", size=1, color="pink", glow=2, font="x.ttf")` |
| `ADD counter "id" to 892 suffix " users" @1 for 1.5s` | `mk.Counter(892, at=1, duration=1.5, suffix=" users")` |
| `ADD card "id" 2x1.2 indigo` / `ADD card "id" image "x.png"` | `mk.Card(...)` |
| `ADD screen "id" "shot.png" width 4 frame cyan` | `mk.Screen("shot.png", width=4, frame_color="cyan")` |
| `ADD logo "id" "logo.png" height 1` | `mk.Logo("logo.png", height=1)` |
| `ADD sphere`, `ADD ring`, `ADD arc from 0° to 120°`, `ADD line through x,y,z; x,y,z` | `mk.Sphere`, `mk.Ring`, `mk.Arc`, `mk.Line` |
| `ADD sphere "earth" 0.4 #3b82f6 lit` | `mk.Sphere(0.4, color="#3b82f6", lit=True)` (shaded; needs a light) |
| `ADD box "phone" 2x1.2x0.3 #1f2937 bevel 0.08 metallic 0.6` | `mk.Box(2, 1.2, 0.3, color="#1f2937", bevel=0.08, metallic=0.6)` |
| `ADD light point 2500 at 0,0,0` / `ADD light area 1500 at 4,-6,6 aim 0,0,0` / `ADD light sun 0.3 aim 0,0,0` | `mk.Light("point", 2500).at(0, 0, 0)` / `mk.Light("area", 1500).at(4, -6, 6).point_at(0, 0, 0)` |
| `ADD ring "path" radius 5 flat` | `mk.Ring(5, facing="up")` (lies on the ground) |
| `ADD stars`, `ADD grid floor` | `mk.Starfield()`, `mk.GridFloor()` |
| `ADD globe "id"` | `mk.Globe()` |
| `ADD chart "id" 345,120,95 labels B,O,P` | `mk.BarChart([345, 120, 95], labels=["B", "O", "P"])` |
| `ADD wall "id" "a.png","b.png" columns 2` | `mk.ScreenWall([...], columns=2)` |
| `ADD portal "id"` | `mk.Portal()` |

### Motions (`name: ...`)
`fade-in @t for d` · `fade-out @t for d` · `dim to 0.3 @t` · `pop-in @t` · `pop-out @t` ·
`slide-in from left @t` · `slide-out to right @t` · `rise-in @t` · `move to x,y,z @t for d` ·
`scale to 1.5 @t` · `rotate to 0,0,90 @t` · `spin 2 turns axis Z t1-t2` · `float t1-t2` · `pulse @t x2` ·
`glow to 4 @t` · `color to cyan @t` · `show @t` · `hide @t` · `visible t1-t2` · `draw-on @t for d` ·
`type-on @t for d` · `face camera`
`orbit around sun radius 5 2 turns 0s-10s tilt 5 phase 30 path` (circle a point or an item, flat) ·
Globe: `focus lat,lon @t` · `marker lat,lon "Label" pop-in @t`.
Chart: `grow @t` · `highlight 0 @t`. Wall: `cascade-in @t`. Portal: `open @t`.

### CAMERA
`CAMERA place x,y,z look x,y,z` · `CAMERA move to x,y,z look x,y,z @t for d` · `CAMERA push-in to x,y,z @t for d` ·
`CAMERA pull-out to x,y,z @t for d` · `CAMERA orbit around x,y,z radius r from a° to b° height h @t for d` ·
`CAMERA crane up 3 @t for d` · `CAMERA path x,y,z; x,y,z @t for d` · `CAMERA shake @t` · `CAMERA zoom 50mm @t` ·
`CAMERA vertigo 3 @t for d` · `CAMERA cut to x,y,z look x,y,z @t` · `CAMERA focus on id f/2.8`

### On screen
`CAPTION "text" eyebrow "label" @t until t2` · `TITLE "text" subtitle "sub" @t` ·
`LOWER-THIRD "name" "role" @t until t2` · `OVERLAY TEXT "x" at -0.4,0.4 size 0.04 @t` ·
`OVERLAY IMAGE "logo.png" at 0.4,0.4 height 0.1 @t` · `LETTERBOX` · `FLASH @t` · `DIP white @t`

### TRANSITION (between shots)
`TRANSITION cut @t -> shot` · `TRANSITION fade-through-black @t -> shot` · `TRANSITION dip white @t -> shot` ·
`TRANSITION flash-cut @t -> shot` · `TRANSITION whip-pan @t -> shot` · `TRANSITION push-through @t -> shot` ·
`TRANSITION portal "id" @t -> shot`
(Optionally `-> shot at x,y,z look x,y,z`; the default lands 9 units in front of the shot's centre.)

## Free text works too

You can also just describe the video: *"a 10-second intro: our logo appears among stars, then three
screenshots slide in, end on 'ERM 2.0, coming soon'"*. The gem writes a Shot Script draft, checks it
with you, then writes the code.


<!-- docs/cookbook.md -->

# Cookbook

Copy-paste recipes. Each one assumes the usual header:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motionkit as mk
from motionkit import transitions as tr
movie = mk.Movie("recipe", length=8)
```

…and ends with `movie.run()`.

## Logo sting (5 s)

```python
mk.Starfield()
logo = mk.Logo("assets/logo.png", height=1.4).at(0, 0, 0.2)
logo.pop_in(at=0.6, duration=0.8)
mk.Ring(2.2, color="pink").at(0, 0.3, 0.2).draw_on(at=0.3, duration=1.0).spin(0.5, 1.3, 5, axis="Y")
movie.camera.place((0, -9, 0.3), look_at=(0, 0, 0.2)).push_in(to=(0, -7.5, 0.25), at=0, duration=5)
movie.overlay.flash(at=0.6)
movie.effects.glow(1.2)
```

## Title with typing

```python
t = mk.Text3D("DMS India", size=0.9, color="white", glow=2, font="fonts/Montserrat-SemiBold.ttf")
t.type_on(at=0.5, duration=1.2, cursor=True)
movie.overlay.caption("Brought to you by", at=0.2, until=3)
```

## Screens fly in, then one comes forward

```python
wall = mk.ScreenWall(["a.png", "b.png", "c.png", "d.png", "e.png", "f.png"], columns=3).at(0, 3, 0)
wall.cascade_in(at=0.3, stagger=0.12)
hero = wall.screens[4]
for s in wall.screens:
    if s is not hero:
        s.fade_to(0.15, at=2.5)
hero.move_to(0, -2, 0, at=2.5, duration=1.2).scale_to(1.5, at=2.5, duration=1.2)
```

## Data moment: bars plus a counter

```python
chart = mk.BarChart([345, 120, 95, 60, 55], labels=list("BOPAL")).at(-2, 2, -1.4)
chart.grow(at=0.5).highlight(0, at=2.0)
mk.Counter(892, at=0.8, duration=1.6, size=1, color="pink", glow=3, suffix=" users").at(3.5, 1.5, 0.5)
```

## Globe tour

```python
globe = mk.Globe(3)
for i, (name, lat, lon) in enumerate([("Toulouse", 43.6, 1.4), ("Hamburg", 53.5, 10.0)]):
    t = 0.5 + i * 2
    globe.focus(lat, lon, at=t)
    globe.marker(lat, lon, label=name).pop_in(at=t + 1)
```

## Solar system (lit planets, orbits, a moon)

```python
sun = mk.Sphere(1.2, color="#ffb547", glow=6).pop_in(at=0.3)
mk.Light("point", power=2500, color="#fff3d6", size=1.0)          # inside the sun: lights the planets
mk.Light("sun", power=0.15, color="#9fb4ff").point_at(0, 0, 0)     # faint fill for the night sides
earth = mk.Sphere(0.4, color="#3b82f6", lit=True)
earth.orbit(around=sun, radius=5, turns=1, start=0, end=10, path=True).spin(turns=3, start=0, end=10)
mk.Sphere(0.1, color="#d4d4d8", lit=True).orbit(around=earth, radius=0.75, turns=4, start=0, end=10)
movie.camera.place((0, -11, 1.2), look_at=(0, 0, 0))
movie.camera.move(to=(0, -9, 12), look_at=(0, 0, 0), at=1, duration=8)   # crane up to look from above
movie.effects.glow(threshold=1.0)
```

## Product on a turntable (lit)

```python
mk.Light("area", 1500).at(4, -6, 6).point_at(0, 0, 0.5)   # key light
mk.Light("sun", 0.4).point_at(0, 0, 0)                     # fill
mk.Box(2, 1.2, 0.3, color="#1f2937", bevel=0.08, metallic=0.6, roughness=0.3).at(0, 0, 0.15).spin(1, 0, 8)
mk.Ring(2.2, color="pink", facing="up").at(0, 0, 0.01).draw_on(at=0.5)   # glowing ring on the floor
movie.camera.place((0, -7, 2.5), look_at=(0, 0, 0.3))
```

## Two shots with a flash cut

```python
with movie.shot("one", 0, 4) as a:
    mk.Text3D("Before").pop_in(0.3)
    movie.camera.place((0, -8, 0))
with movie.shot("two", 4, 8) as b:
    mk.Text3D("After", color="cyan").pop_in(4.2)
tr.flash_cut(movie, at=4, to=b.point(0, -8, 0), look_at=b.point(0, 0, 0))
```

## Portal between worlds

```python
with movie.shot("old", 0, 5) as a:
    gate = mk.Portal().at(0, -1, 0)
    gate.open(at=1)
    movie.camera.place((0, -10, 0), look_at=(0, 0, 0))
with movie.shot("new", 5, 10) as b:
    mk.Screen("new_app.png", width=5).at(0, 2, 0)
tr.through_portal(movie, gate, at=5, to=b.point(0, -7, 0.5), look_at=b.point(0, 2, 0))
```

## Lower third for a speaker or a feature

```python
movie.overlay.lower_third("Custom one-pager layout", "New in ERM 2.0", at=1, until=4)
```

## Vertical video for phones

```python
movie = mk.Movie("reel", length=10, size=(1080, 1920), lens=28)
```

## Music

```python
movie.add_music("audio/theme.wav", volume=0.8)
```

## Anything the kit doesn't cover

```python
import bpy
cube = mk.Card(1, 1, "gold")
cube.obj.modifiers.new("bevel", "BEVEL")                   # raw Blender on item.obj
mk.key(cube.obj, "rotation_euler", 2.0, (0, 0, 3.14), "bounce")  # keyframe any property
```


# Example scripts (complete, tested)

## examples/01_hello_title.py

```python
"""Demo 1: a glowing title, 8 seconds. The smallest useful motionkit movie.

Run it (PowerShell, from the motionkit folder):
    blender -b -P examples/01_hello_title.py -- --preview --render     # quick check, half size
    blender -b -P examples/01_hello_title.py -- --render               # final 1080p MP4 in examples/render/
    blender -P examples/01_hello_title.py                              # open in Blender to scrub and tweak
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motionkit as mk

movie = mk.Movie("hello_title", length=8)

# 1. Set the stage: stars far away, a glowing grid below.
mk.Starfield()
mk.GridFloor(height=-1.6)

# 2. A ring draws itself behind the title, then keeps turning slowly.
ring = mk.Ring(radius=2.6, color="indigo", glow=3).at(0, 1.5, 0.3)
ring.draw_on(at=0.3, duration=1.2).spin(turns=0.25, start=1.5, end=8, axis="Y")

# 3. The title pops in and floats.
title = mk.Text3D("Hello DMS", size=1.1, color="pink", glow=3, depth=0.12).at(0, 0, 0.3)
title.pop_in(at=0.8, duration=0.7).float(start=1.5, end=8, height=0.08)

# 4. The camera drifts around the title while moving closer.
movie.camera.place((0, -14, 1.5), look_at=(0, 0, 0.3))
movie.camera.orbit(center=(0, 0, 0.3), radius=11, start=-25, end=12, height=1.0, at=0, duration=8)

# 5. Words on screen, fades, and the glow.
movie.overlay.caption("Built with motionkit in 25 lines", eyebrow="Demo", at=3, until=6.6)
movie.overlay.fade_from_black(at=0, duration=1)
movie.overlay.fade_to_black(at=7.2, duration=0.8)
movie.effects.glow().vignette(0.3)

movie.run()
```

## examples/02_product_reveal.py

```python
"""Demo 2: a product story in three shots, about 16 seconds.

  Shot 1  "Today": a wall of old screens cascades in; a portal opens.
  Shot 2  "Tomorrow": the camera flies through the portal and lands on the new app.
  Shot 3  "Impact": bars grow and a number counts up, then the end title.

Shows shots, transitions, screens, a bar chart, a counter, captions and music.
    blender -b -P examples/02_product_reveal.py -- --preview --render
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import motionkit as mk
from motionkit import transitions as tr

A = lambda name: os.path.join(HERE, "assets", name)
movie = mk.Movie("product_reveal", length=16, palette="neon")
mk.Starfield(count=2500, spread=(1600, 60, 40), center=(800, 30, 0))  # one sky behind every shot

# ---------------------------------------------------------------- shot 1: today (0-6 s)
with movie.shot("today", 0, 6) as s1:
    wall = mk.ScreenWall([A("slate_heat.png"), A("slate_table.png"), A("slate_report.png"), A("slate_tracker.png")],
                         columns=2, width=3.2, frame_color="red").at(0, 2, 0)
    wall.cascade_in(at=0.3, stagger=0.25)
    wall.fade_to(0.35, at=3.0, duration=0.8)
    gate = mk.Portal(radius=2.0).at(0, -1, 0)
    gate.open(at=3.2)
    movie.camera.place((0, -13, 0.5), look_at=(0, 2, 0))      # inside a shot, positions are relative to it
    movie.camera.push_in(to=(0, -10, 0.3), at=0, duration=3.5)
    movie.overlay.caption("Today: slow, fragile, undocumented", eyebrow="The problem", at=0.8, until=3.4)

# ---------------------------------------------------------------- shot 2: tomorrow (6-11 s)
with movie.shot("tomorrow", 6, 11) as s2:
    app = mk.Screen(A("react_heat.png"), width=5.5, frame_color="cyan").at(0, 2, 0.2)
    app.fade_in(at=6.0, duration=0.3).float(start=6.5, end=11, height=0.05)
    mk.Ring(radius=4.2, color="cyan", glow=2.5).at(0, 2.5, 0.2).draw_on(at=6.3, duration=1.2)
    movie.overlay.caption("Tomorrow: fast, stable, documented", eyebrow="The solution", at=6.6, until=10.4)
    movie.camera.orbit(center=(0, 2, 0.2), radius=9, start=-12, end=12, height=0.6, at=7.0, duration=4)

# fly through the portal from shot 1 into shot 2 (outside a shot, use shot.point() for positions)
tr.through_portal(movie, gate, at=6.0, to=s2.point(0, -7, 0.5), look_at=s2.point(0, 2, 0.2))

# ---------------------------------------------------------------- shot 3: impact (11-16 s)
with movie.shot("impact", 11, 16) as s3:
    chart = mk.BarChart([345, 120, 95, 60, 55], labels=["B", "O", "P", "A", "L"], width=6, height=3).at(-2.2, 2, -1.4)
    chart.grow(at=11.3, duration=0.8).highlight(0, at=12.6)
    users = mk.Counter(892, at=11.6, duration=1.8, size=1.1, color="pink", glow=3, suffix=" users").at(3.6, 1.5, 0.6)
    users.fade_in(at=11.6, duration=0.3).fade_out(at=13.4, duration=0.5)
    chart.fade_out(at=13.4, duration=0.5)
tr.flash_cut(movie, at=11.0, to=s3.point(0.6, -11, 0.8), look_at=s3.point(0.6, 2, 0.3))
movie.camera.push_in(to=s3.point(0.6, -9.5, 0.6), at=11.0, duration=5)
movie.overlay.title("ERM 2.0", subtitle="Coming soon", at=14.0)
movie.overlay.fade_to_black(at=15.3, duration=0.7)

movie.overlay.fade_from_black(at=0, duration=0.8)
movie.effects.glow().vignette(0.3).motion_blur(0.5)
music = os.path.join(HERE, "..", "..", "trailer", "audio", "erm2_trailer_mix.wav")
if os.path.exists(music):
    movie.add_music(music, volume=0.8)
movie.run()
```

## examples/03_globe_tour.py

```python
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
```

## examples/04_solar_system.py

```python
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
```
