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
