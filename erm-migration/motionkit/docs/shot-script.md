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
