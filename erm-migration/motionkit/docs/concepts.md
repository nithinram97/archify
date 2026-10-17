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
