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
