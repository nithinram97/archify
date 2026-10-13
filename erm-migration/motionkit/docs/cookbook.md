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

## Your own geometry with kit motions

```python
import bpy, bmesh
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.8, radius2=0.0, depth=1.5)
me = bpy.data.meshes.new("cone"); bm.to_mesh(me); bm.free()
obj = bpy.data.objects.new("cone", me)
mat = mk.GlowMaterial("gold", lit=True, metallic=0.8)
obj.data.materials.append(mat.mat)
mk.stage.STAGE.link(obj)
mk.Item(obj, [mat]).pop_in(at=0.2).orbit(radius=2, turns=1, start=0, end=4)
mk.Light("area", 800).at(2, -3, 3).point_at(0, 0, 0)
```

## Anything the kit doesn't cover

```python
import bpy
cube = mk.Card(1, 1, "gold")
cube.obj.modifiers.new("bevel", "BEVEL")                   # raw Blender on item.obj
mk.key(cube.obj, "rotation_euler", 2.0, (0, 0, 3.14), "bounce")  # keyframe any property
```
