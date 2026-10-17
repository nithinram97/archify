"""Props: furniture and things in a set. Each kind is a class, so new ones are easy to add:

    class Cake(dr.Prop):
        description = "A birthday cake on a stand"
        default_place = "center"
        params = dr.Prop.params + [dr.Param("color", "color", default="pink")]

        def build(self, s, name, p):
            pos = s.spot_for(p, 0.4, 0.4, self.default_place)     # where it goes, as (x, y)
            dr.shapes.cylinder(name, 0.2, 0.15, p.get("color", "pink"), at=(pos.x, pos.y, 0))
            s.block(pos, 0.4, 0.4)                                  # characters walk round it
            s.add_mark(name, (pos.x, pos.y - 0.5), facing="back")   # a spot to stand at, facing it

`build` gets the set `s`, the prop's unique name and its settings `p` (from the set file). Helpers on
the set: spot_for, block, add_mark, add_seat, place_item, seat_facing, tree, add_prop, lights.
Table and counter `items` are classes too (`dr.Item`).
"""
import math
import random

import bpy

from mathutils import Vector

from . import look, plugins, shapes
from .plugins import Param, Plugin
from .sets import Mark, Seat, ZONES


class Prop(Plugin):
    kind = "prop"
    abstract = True
    default_place = "center"
    params = [Param("place", "place", label="Where"), Param("name", "text", label="Name (optional)")]

    @classmethod
    def describe_extra(cls):
        return {"default_place": cls.default_place}

    def build(self, s, name, p):
        raise NotImplementedError


class Item(Plugin):
    """A small thing on a table or counter. `build(s, x, y, z, rng)` puts it at (x, y) on a surface at height z.
    How it falls and bounces (physics.py): mass (kg), bounce (0..1), friction, shape (hull, sphere, box)."""
    kind = "item"
    abstract = True
    mass, bounce, friction, shape = 0.3, 0.2, 0.6, "hull"

    def build(self, s, x, y, z, rng):
        raise NotImplementedError


class CookieJar(Item):
    mass, bounce = 0.6, 0.15
    name = "cookie-jar"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("cookie-jar", 0.09, 0.16, look.glass(), at=(x, y, z))
        shapes.cylinder("cookie-jar.lid", 0.095, 0.03, "red", at=(x, y, z + 0.16))
        for i in range(3):
            shapes.cylinder("cookie", 0.05, 0.015, "#c98b4f", at=(x, y, z + 0.01 + i * 0.02))


class Cookie(Item):
    mass, bounce = 0.02, 0.1
    def build(self, s, x, y, z, rng):
        shapes.cylinder("cookie", 0.05, 0.015, "#c98b4f", at=(x, y - 0.1, z))


class Plate(Item):
    mass, bounce = 0.4, 0.2
    def build(self, s, x, y, z, rng):
        shapes.cylinder("plate", 0.12, 0.015, "white", at=(x, y, z))


class Cup(Item):
    mass, bounce = 0.25, 0.2
    def build(self, s, x, y, z, rng):
        shapes.cylinder("cup", 0.045, 0.09, rng.choice(["red", "teal", "yellow"]), at=(x, y, z))


class Vase(Item):
    mass, bounce = 0.6, 0.1
    description = "A vase of flowers"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("vase", 0.06, 0.2, "teal", at=(x, y, z), r2=0.04)
        for i in range(3):
            shapes.sphere("flower", 0.045, rng.choice(["pink", "yellow", "red"]),
                          at=(x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05), z + 0.26 + 0.04 * i))


class Laptop(Item):
    mass, bounce, shape = 1.5, 0.05, "box"
    def build(self, s, x, y, z, rng):
        shapes.box("laptop", 0.32, 0.22, 0.015, "#c9ccd1", at=(x, y, z))
        shapes.box("laptop", 0.32, 0.015, 0.2, "#c9ccd1", at=(x, y + 0.11, z), rot=(math.radians(-15), 0, 0))


class Book(Item):
    mass, bounce, friction, shape = 0.5, 0.05, 0.8, "box"
    def build(self, s, x, y, z, rng):
        shapes.box("book", 0.2, 0.14, 0.04, rng.choice(["red", "blue", "green"]), at=(x, y, z), bevel=0.005)


class Ball(Item):
    description = "A bouncy ball (put it on the floor: props = [{type = \"ball\", place = \"front\"}])"
    mass, bounce, friction, shape = 0.4, 0.72, 0.5, "sphere"

    def build(self, s, x, y, z, rng):
        r = 0.11
        c1, c2 = rng.choice([("red", "white"), ("blue", "yellow"), ("teal", "white"), ("orange", "navy")])
        shapes.sphere("ball", r, c1, at=(x, y, z + r))
        shapes.cylinder("ball.band", r * 1.01, r * 0.5, c2, at=(x, y, z + r * 0.75), segments=24)


class Table(Prop):
    name = "table"
    description = "A table; with chairs it makes the seats chair and chair-2"
    default_place = "center"
    params = Prop.params + [Param("width", "number", default=1.4, min=0.6, max=3, step=0.1), Param("depth", "number", default=0.8, min=0.5, max=2, step=0.1), Param("color", "color", default="wood"), Param("chairs", "choice", default=0, choices=(0, 1, 2)), Param("chair_color", "color", label="Chair colour"), Param("items", "items", label="On top")]

    def build(self, s, name, p):
        w, d, h = p.get("width", 1.4), p.get("depth", 0.8), s.sized(0.48, 0.76)
        pos = s.spot_for(p, w, d, "center")
        c = p.get("color", "wood")
        top = s.model("Table_RoundLarge", name, (w, d, h), (pos.x, pos.y, 0))
        if top is None:
            top = shapes.box(name, w, d, 0.05, c, at=(pos.x, pos.y, h - 0.05), bevel=0.02)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    shapes.box(name + ".leg", 0.06, 0.06, h - 0.05, c, at=(pos.x + sx * (w / 2 - 0.08), pos.y + sy * (d / 2 - 0.08), 0), bevel=0.01)
        s.block(pos, w, d)
        s.add_surface(name, pos, h, (w, d))
        s.marks[name] = Mark(name, (pos.x, pos.y - d / 2 - 0.35), facing=math.pi)
        for side, label in ((-1, "left"), (1, "right")):
            s.marks[f"{name}-{label}"] = Mark(f"{name}-{label}", (pos.x + side * (w / 2 + 0.35), pos.y),
                                                 facing=math.pi / 2 * (1 if side < 0 else -1))
        for i in range(p.get("chairs", 0)):
            side = (-1, 1)[i % 2]
            s.add_prop({"type": "chair", "at": (pos.x + side * (w / 2 + s.sized(0.3, 0.35)), pos.y), "face": (-side, 0), "tucked": True,
                           "color": p.get("chair_color", c)})
        for item in p.get("items", []):
            s.place_item(item, pos, h, w, on=name, depth=d)
        return top


class Chair(Prop):
    name = "chair"
    description = "A chair to sit on"
    default_place = "center"
    params = Prop.params + [Param("color", "color", default="wood"), Param("facing", "facing", default="camera")]

    def build(self, s, name, p):
        pos = Vector(p["at"]) if "at" in p else s.spot_for(p, 0.45, 0.45, "center")
        f = s.seat_facing(p, pos)
        c = p.get("color", "wood")
        seat_h = s.sized(0.3, 0.46)
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        if s.seat_model("Chair_2", name + ".model", (0.42, 0.4, seat_h / 0.47), (0, 0), seat_h, parent=root) is None:
            shapes.box(name + ".seat", 0.42, 0.4, 0.04, c, root, at=(0, 0, seat_h - 0.04))
            shapes.box(name + ".back", 0.42, 0.04, 0.45, c, root, at=(0, 0.2, seat_h - 0.02))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    shapes.box(name + ".leg", 0.04, 0.04, seat_h - 0.04, c, root, at=(sx * 0.17, sy * 0.16, 0), bevel=0.008)
        fwd = Vector((math.sin(f), -math.cos(f)))
        front = pos + fwd * 0.6
        if p.get("tucked"):  # pushed under a table: get in from the side nearest the camera
            perp = Vector((-fwd.y, fwd.x))
            front = pos + (perp if perp.y < 0 else -perp) * 0.6
        s.seats[name] = Seat(name, pos, f, seat_h, front)
        s.marks.setdefault(name, Mark(name, front, facing=f))
        s.block(pos, 0.4, 0.4)
        return root


class Sofa(Prop):
    name = "sofa"
    description = "A sofa with two seats"
    default_place = "back"
    params = Prop.params + [Param("width", "number", default=1.8, min=1, max=3, step=0.1), Param("color", "color", default="teal"), Param("facing", "facing", default="camera")]

    def build(self, s, name, p):
        w = p.get("width", 1.8)
        pos = s.spot_for(p, w, 0.8, "back")
        f = s.seat_facing(p, pos)
        c = p.get("color", "teal")
        seat_h = s.sized(0.32, 0.45)
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        if s.seat_model("Couch_Medium1", name + ".model", (w, 0.8, seat_h * 2), (w * 0.22, 0), seat_h,
                        parent=root) is None:
            shapes.box(name, w, 0.8, seat_h - 0.04, c, root, bevel=0.06)
            shapes.box(name, w, 0.22, 0.7, c, root, at=(0, 0.3, 0), bevel=0.08)
            for sd in (-1, 1):
                shapes.box(name, 0.2, 0.8, 0.45, c, root, at=(sd * (w / 2 - 0.1), 0, 0), bevel=0.08)
                shapes.box(name + ".cushion", w / 2 - 0.22, 0.6, 0.08, c, root, at=(sd * (w / 4 - 0.05), -0.05, seat_h - 0.08), bevel=0.04)
        fwd = Vector((math.sin(f), -math.cos(f)))
        side = Vector((math.cos(f), math.sin(f)))
        for i, sd in enumerate((-1, 1)):
            sname = name if i == 0 else f"{name}-2"
            at = pos + side * sd * w * 0.22
            s.seats[sname] = Seat(sname, at, f, seat_h, at + fwd * 0.65)
        s.marks.setdefault(name, Mark(name, pos + fwd * 0.75, facing=f))
        s.block(pos, w, 0.8)
        return root


class Door(Prop):
    name = "door"
    description = "A door in the back wall; characters enter through it"
    default_place = "back-left"
    params = Prop.params + [Param("color", "color", default="#8a5a3c")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 1.0, 0.1, "back-left")
        c = p.get("color", "#8a5a3c")
        if not s.outdoor:
            pos.y = s.depth / 2
        if s.model("Door_1", name, (None, None, s.sized(1.75, 2.1)), (pos.x, pos.y - 0.06, 0)) is None:
            shapes.box(name + ".frame", 1.0, 0.1, 1.75, look.matte("white", 0.5), at=(pos.x, pos.y - 0.02, 0), bevel=0.01)
            shapes.box(name, 0.86, 0.1, 1.68, c, at=(pos.x, pos.y - 0.05, 0), bevel=0.015)
            shapes.sphere(name + ".knob", 0.035, "#e2b53e", at=(pos.x + 0.32, pos.y - 0.12, 0.85))
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.6), facing=0.0)
        return None


class Window(Prop):
    name = "window"
    description = "A window in the back wall"
    default_place = "back-right"
    wall = True
    params = Prop.params + [Param("view", "color", default="sky", label="Outside")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 1.2, 0.1, "back-right")
        if not s.outdoor:
            pos.y = s.depth / 2
        if "view" in p:
            sky = look.plastic(p["view"], 0.9, 0.0, emission=1.2)
        else:   # shows the sky of the scene's time of day and weather
            sky = look.plastic("sky", 0.9, 0.0, emission=1.2).copy()
            s.glows.append((sky, "sky", 1.2))
            s.windows.append((pos.x, pos.y, 1.25))
        shapes.box(name + ".view", 1.2, 0.05, 0.9, sky, at=(pos.x, pos.y - 0.02, 0.8), bevel=0)
        if s.model("Window_Large1", name, (1.3, 0.1, 1.0), (pos.x, pos.y - 0.06, 0.75)) is not None:
            s.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
            return None
        frame = look.matte("white", 0.5)
        for dz in (0.8, 1.25, 1.7):
            shapes.box(name + ".frame", 1.3, 0.08, 0.06, frame, at=(pos.x, pos.y - 0.04, dz - 0.03), bevel=0.01)
        for dx in (-0.62, 0, 0.62):
            shapes.box(name + ".frame", 0.06, 0.08, 0.96, frame, at=(pos.x + dx, pos.y - 0.04, 0.77), bevel=0.01)
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None


class Counter(Prop):
    name = "counter"
    description = "A kitchen counter with cupboards"
    default_place = "back-right"
    params = Prop.params + [Param("width", "number", default=2.2, min=0.8, max=4, step=0.1), Param("color", "color", default="white"), Param("top", "color", default="charcoal", label="Worktop"), Param("items", "items", label="On top")]

    def build(self, s, name, p):
        w = p.get("width", 2.2)
        pos = s.spot_for(p, w, 0.6, "back-right")
        c = p.get("color", "white")
        h = s.sized(0.6, 0.9)
        n = max(1, round(w / (h * 0.62)))      # kitchen units side by side
        units = [s.model(("Kitchen_3Drawers", "Kitchen_Cabinet1", "Kitchen_2Drawers")[i % 3], f"{name}.unit",
                         (w / n, 0.6, h), (pos.x - w / 2 + (i + 0.5) * w / n, pos.y, 0)) for i in range(n)]
        if None in units:
            for u in units:
                if u is not None:
                    bpy.data.objects.remove(u)
            shapes.box(name, w, 0.6, h - 0.05, c, at=(pos.x, pos.y, 0), bevel=0.02)
            shapes.box(name + ".top", w + 0.05, 0.65, 0.05, p.get("top", "charcoal"), at=(pos.x, pos.y, h - 0.05), bevel=0.01)
            for i in range(int(w / 0.55)):
                shapes.sphere(name + ".knob", 0.02, "#e2b53e", at=(pos.x - w / 2 + 0.28 + i * 0.55, pos.y - 0.31, h * 0.7))
        for item in p.get("items", []):
            s.place_item(item, pos, h, w, on=name, depth=0.6)
        s.block(pos, w, 0.6)
        s.add_surface(name, pos, h, (w, 0.6))
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None


class Fridge(Prop):
    name = "fridge"
    description = "A fridge"
    default_place = "back-right"
    params = Prop.params + [Param("color", "color", default="#d8eef0")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.7, 0.65, "back-right")
        c = p.get("color", "#d8eef0")
        if s.model("Kitchen_Fridge", name, (0.7, 0.65, s.sized(1.55, 1.8)), (pos.x, pos.y, 0)) is None:
            shapes.box(name, 0.7, 0.65, 1.55, c, at=(pos.x, pos.y, 0), bevel=0.06)
            shapes.box(name + ".line", 0.7, 0.01, 0.015, "#9fb7ba", at=(pos.x, pos.y - 0.33, 1.0), bevel=0)
            for z in (0.6, 1.2):
                shapes.box(name + ".handle", 0.03, 0.04, 0.22, "#9fb7ba", at=(pos.x + 0.25, pos.y - 0.35, z), bevel=0.01)
        s.block(pos, 0.7, 0.65)
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.75), facing=math.pi)
        return None


class Bookshelf(Prop):
    name = "bookshelf"
    description = "A bookshelf full of books"
    default_place = "back"
    params = Prop.params + [Param("width", "number", default=1.2, min=0.6, max=3, step=0.1), Param("color", "color", default="darkwood")]

    def build(self, s, name, p):
        w = p.get("width", 1.2)
        pos = s.spot_for(p, w, 0.35, "back")
        c = p.get("color", "darkwood")
        shapes.box(name + ".back", w, 0.03, 1.6, c, at=(pos.x, pos.y + 0.16, 0), bevel=0.005)
        for sx in (-1, 1):
            shapes.box(name, 0.04, 0.35, 1.6, c, at=(pos.x + sx * (w / 2 - 0.02), pos.y, 0), bevel=0.005)
        rng = random.Random(name)
        for shelf in range(5):
            shapes.box(name + ".shelf", w, 0.35, 0.03, c, at=(pos.x, pos.y, shelf * 0.38 + (0 if shelf else 0.04)),
                       bevel=0.004)
        shapes.box(name + ".top", w, 0.35, 0.04, c, at=(pos.x, pos.y, 1.56), bevel=0.004)
        for shelf in range(4):
            z = 0.07 + shelf * 0.38
            x = pos.x - w / 2 + 0.06
            while x < pos.x + w / 2 - 0.12:
                bw = rng.uniform(0.04, 0.08)
                bh = rng.uniform(0.22, 0.3)
                shapes.box(name + ".book", bw, 0.24, bh, rng.choice(["red", "blue", "green", "yellow", "cream", "teal"]),
                           at=(x + bw / 2, pos.y - 0.02, z), bevel=0.004)
                x += bw + 0.008
                if rng.random() < 0.06:
                    x += 0.12
        s.block(pos, w, 0.35)
        return None


class Plant(Prop):
    name = "plant"
    description = "A potted plant"
    default_place = "back-right"
    params = Prop.params + [Param("color", "color", default="brick", label="Pot")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.4, 0.4, "back-right")
        if s.model("Houseplant_1", name, (None, None, s.sized(0.75, 1.0)), (pos.x, pos.y, 0)) is not None:
            s.block(pos, 0.4, 0.4)
            return None
        shapes.cylinder(name + ".pot", 0.16, 0.28, p.get("color", "brick"), at=(pos.x, pos.y, 0), r2=0.2)
        rng = random.Random(name)
        for i in range(7):
            a = 2 * math.pi * i / 7
            shapes.ellipsoid(name + ".leaf", 0.07, 0.07, 0.28, look.plastic("leaf", 0.6, 0.1),
                             at=(pos.x + 0.08 * math.cos(a), pos.y + 0.08 * math.sin(a), 0.45 + rng.uniform(0, 0.15)),
                             rot=(0.5 * math.sin(a), -0.5 * math.cos(a), 0))
        s.block(pos, 0.4, 0.4)
        return None


class Lamp(Prop):
    name = "lamp"
    description = "A floor lamp that gives warm light"
    default_place = "back-left"
    params = Prop.params

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.4, 0.4, "back-left")
        h = s.sized(1.6, 1.7)
        if s.model("Light_Floor1", name, (None, None, h), (pos.x, pos.y, 0)) is None:
            h = 1.6
            shapes.cylinder(name, 0.15, 0.03, "charcoal", at=(pos.x, pos.y, 0))
            shapes.cylinder(name, 0.02, 1.35, "charcoal", at=(pos.x, pos.y, 0.03), bevel=0)
            shapes.cylinder(name + ".shade", 0.24, 0.3, look.plastic("cream", 0.7, 0.0, emission=0.6), at=(pos.x, pos.y, 1.3), r2=0.14)
        s.lights.append(((pos.x, pos.y, h - 0.25), "#ffd9a0", 60))
        s.block(pos, 0.3, 0.3)
        return None


class Rug(Prop):
    name = "rug"
    description = "A round rug"
    default_place = "center"
    params = Prop.params + [Param("color", "color", default="#d9775b"), Param("width", "number", default=1.3, min=0.5, max=3, step=0.1)]

    def build(self, s, name, p):
        pos = s.spot_for(p, 2, 1.4, "center")
        w = p.get("width", 1.3)
        if s.model("Carpet_Round", name, (2 * w, 1.2 * w, 0.02), (pos.x, pos.y, 0.008)) is not None:
            return None
        shapes.cylinder(name, p.get("width", 1.3), 0.012, look.matte(p.get("color", "#d9775b"), 0.9),
                        at=(pos.x, pos.y, 0.0), bevel=0.004, segments=48).scale.y = 0.6
        return None


class Bench(Prop):
    name = "bench"
    description = "A park bench with two seats"
    default_place = "center"
    params = Prop.params + [Param("color", "color", default="wood"), Param("facing", "facing", default="camera")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 1.6, 0.5, "center")
        f = s.seat_facing(p, pos)
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        c = p.get("color", "wood")
        for i in range(3):
            shapes.box(name, 1.6, 0.12, 0.04, c, root, at=(0, -0.14 + i * 0.14, 0.3), bevel=0.01)
        shapes.box(name, 1.6, 0.04, 0.3, c, root, at=(0, 0.2, 0.36), bevel=0.01)
        for sd in (-1, 1):
            shapes.box(name, 0.06, 0.45, 0.3, "charcoal", root, at=(sd * 0.7, 0, 0), bevel=0.01)
        fwd = Vector((math.sin(f), -math.cos(f)))
        side = Vector((math.cos(f), math.sin(f)))
        for i, sd in enumerate((-1, 1)):
            sname = name if i == 0 else f"{name}-2"
            at = pos + side * sd * 0.4
            s.seats[sname] = Seat(sname, at, f, 0.32, at + fwd * 0.55)
        s.marks.setdefault(name, Mark(name, pos + fwd * 0.7, facing=f))
        s.block(pos, 1.6, 0.5)
        return root


class Tree(Prop):
    name = "tree"
    description = "A tree (or any scenery: pine, palm, cactus, rock...)"
    default_place = "back-left"
    params = Prop.params + [Param("scale", "number", default=1.0, min=0.5, max=2.5, step=0.1, label="Size"),
                            Param("variety", "scenery", default="tree", label="Kind")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 1, 1, "back-left")
        s.tree(name, pos, p.get("scale", 1.0), random.Random(name), kind=p.get("variety", "tree"), block=False)
        s.block(pos, 0.5, 0.5)
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.7), facing=math.pi)
        return None


class StreetLamp(Prop):
    name = "streetlamp"
    description = "A street lamp that glows"
    default_place = "back-right"
    params = Prop.params

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.3, 0.3, "back-right")
        shapes.cylinder(name, 0.05, 2.2, "charcoal", at=(pos.x, pos.y, 0), bevel=0)
        shapes.sphere(name + ".bulb", 0.14, look.plastic("#fff1c4", 0.5, 0.0, emission=4), at=(pos.x, pos.y, 2.3))
        s.lights.append(((pos.x, pos.y, 2.2), "#ffd9a0", 120))
        s.block(pos, 0.2, 0.2)
        return None


class House(Prop):
    name = "house"
    description = "A small house with a door"
    default_place = "back"
    params = Prop.params + [Param("color", "color", default="cream"), Param("roof", "color", default="brick")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 3, 3, "back")
        c = p.get("color", "cream")
        shapes.box(name, 3.0, 2.6, 2.2, c, at=(pos.x, pos.y + 1.2, 0), bevel=0.04)
        roof = shapes.cylinder(name + ".roof", 2.2, 3.4, p.get("roof", "brick"), at=(pos.x - 1.7, pos.y + 1.2, 2.2),
                               rot=(0, math.radians(90), 0), segments=3, bevel=0.02)
        roof.scale = (0.75, 1.05, 1)
        roof.rotation_euler = (math.radians(90), 0, math.radians(90))
        roof.location = (pos.x - 1.7, pos.y + 1.2, 2.55)
        shapes.box(name + ".door", 0.7, 0.05, 1.5, "#8a5a3c", at=(pos.x, pos.y - 0.1, 0), bevel=0.01)
        for sd in (-1, 1):
            shapes.box(name + ".window", 0.6, 0.05, 0.55, look.plastic("sky", 0.2, 0.3, emission=0.6),
                       at=(pos.x + sd * 0.95, pos.y - 0.1, 1.0), bevel=0.01)
        s.block(Vector((pos.x, pos.y + 1.2)), 3.0, 2.6)
        s.marks[name] = Mark(name, (pos.x, pos.y - 0.6), facing=0.0)
        return None


# ---------------------------------------------------------------------- more furniture
def _wall_y(s, p, depth):
    """For things against the back wall: the y of their front."""
    pos = s.spot_for(p, 1, depth, "back")
    if not s.outdoor:
        pos.y = s.depth / 2 - depth / 2 - 0.05
    return pos


class Bed(Prop):
    name = "bed"
    description = "A bed with a pillow and blanket; you can sit on its edge"
    default_place = "back"
    params = Prop.params + [Param("color", "color", default="#7aa6d9", label="Blanket"),
                            Param("frame", "color", default="wood"), Param("width", "number", default=1.4, min=0.9,
                                                                            max=2.0, step=0.1)]

    def build(self, s, name, p):
        w, d = p.get("width", 1.4), 2.0
        pos = _wall_y(s, dict(p, place=p.get("place", "back")), d)
        fr = p.get("frame", "wood")
        top = s.sized(0.42, 0.5)
        if s.seat_model("Bed_Single", name, (w + 0.1, d + 0.1, 1.0), (0, -d / 2 + 0.25), top,
                        depth=False, at=(pos.x, pos.y, 0)) is None:
            base = top - 0.17
            shapes.box(name, w + 0.1, d + 0.1, base, fr, at=(pos.x, pos.y, 0), bevel=0.03)
            shapes.box(name + ".head", w + 0.1, 0.08, base + 0.6, fr, at=(pos.x, pos.y + d / 2 + 0.02, 0), bevel=0.03)
            shapes.box(name + ".mattress", w, d - 0.05, 0.18, look.matte("#f4f1ea", 0.7), at=(pos.x, pos.y, base),
                       bevel=0.06)
            shapes.box(name + ".pillow", w * 0.7, 0.35, 0.12, look.matte("white", 0.7),
                       at=(pos.x, pos.y + d / 2 - 0.3, top), bevel=0.05)
            shapes.box(name + ".blanket", w + 0.04, d * 0.62, 0.05, look.matte(p.get("color", "#7aa6d9"), 0.85),
                       at=(pos.x, pos.y - d * 0.19, top - 0.01), bevel=0.02)
        s.block(pos, w + 0.1, d + 0.1)
        edge = Vector((pos.x, pos.y - d / 2 + 0.25))
        s.add_seat(name, edge, 0.0, top, (edge.x, edge.y - 0.6))
        return None


class Desk(Prop):
    name = "desk"
    description = "A desk, with a chair (seat '<name>-chair') and things on it"
    default_place = "left"
    params = Prop.params + [Param("color", "color", default="wood"), Param("chair", "bool", default=True),
                            Param("facing", "choice", default="back", choices=("back", "camera"), label="Sits facing"),
                            Param("items", "items", label="On top")]

    def build(self, s, name, p):
        w, d, h = 1.2, 0.6, s.sized(0.5, 0.76)
        pos = s.spot_for(p, w, d, "left")
        c = p.get("color", "wood")
        shapes.box(name, w, d, 0.04, c, at=(pos.x, pos.y, h - 0.04), bevel=0.01)
        for sx in (-1, 1):
            shapes.box(name + ".side", 0.04, d, h - 0.04, c, at=(pos.x + sx * (w / 2 - 0.02), pos.y, 0), bevel=0.005)
        shapes.box(name + ".drawers", 0.4, d - 0.05, h * 0.55, c, at=(pos.x + w / 2 - 0.24, pos.y, h * 0.4), bevel=0.01)
        s.block(pos, w, d)
        s.add_surface(name, pos, h, (w, d))
        for item in p.get("items", []):
            s.place_item(item, pos, h, w, on=name, depth=d)
        toward = 1 if p.get("facing", "back") == "back" else -1     # the sitter faces the back wall or the camera
        if p.get("chair", True):
            s.add_prop({"type": "chair", "name": f"{name}-chair", "at": (pos.x, pos.y - toward * (d / 2 + 0.3)),
                        "face": (0, toward), "tucked": True, "color": p.get("chair_color", "charcoal")})
        s.marks.setdefault(name, Mark(name, (pos.x + w / 2 + 0.4, pos.y - 0.2), facing=-math.pi / 2))
        return None


class Wardrobe(Prop):
    name = "wardrobe"
    description = "A tall wardrobe"
    default_place = "back-left"
    params = Prop.params + [Param("color", "color", default="#c9a27a")]

    def build(self, s, name, p):
        w, d = 1.1, 0.6
        pos = _wall_y(s, dict(p, place=p.get("place", "back-left")), d)
        c = p.get("color", "#c9a27a")
        shapes.box(name, w, d, 1.95, c, at=(pos.x, pos.y, 0), bevel=0.02)
        shapes.box(name + ".split", 0.012, 0.01, 1.8, look.matte("#5a4030"), at=(pos.x, pos.y - d / 2, 0.08), bevel=0)
        for sx in (-1, 1):
            shapes.box(name + ".handle", 0.025, 0.04, 0.2, "#e2b53e", at=(pos.x + sx * 0.06, pos.y - d / 2 - 0.02, 0.95),
                       bevel=0.005)
        s.block(pos, w, d)
        s.marks[name] = Mark(name, (pos.x, pos.y - d / 2 - 0.6), facing=math.pi)
        return None


class Television(Prop):
    name = "tv"
    description = "A television on a stand"
    default_place = "left"
    params = Prop.params + [Param("facing", "facing", default="right"), Param("on", "bool", default=True)]

    def build(self, s, name, p):
        pos = s.spot_for(p, 1.0, 0.45, "left")
        f = s.seat_facing(p, pos)
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f
        shapes.box(name + ".stand", 1.1, 0.42, 0.42, "charcoal", root, bevel=0.02)
        shapes.box(name, 1.0, 0.06, 0.6, look.plastic("#1c1a1a", 0.3, 0.4), root, at=(0, 0.05, 0.47), bevel=0.015)
        screen = look.plastic("#6fa8dc" if p.get("on", True) else "#202024", 0.2, 0.3,
                              emission=1.5 if p.get("on", True) else 0.0)
        shapes.box(name + ".screen", 0.92, 0.01, 0.52, screen, root, at=(0, 0.015, 0.51), bevel=0)
        if p.get("on", True):
            fwd = Vector((math.sin(f), -math.cos(f)))
            s.lights.append(((pos.x + fwd.x * 0.6, pos.y + fwd.y * 0.6, 0.8), "#9cc9ec", 25))
        s.block(pos, 1.1, 0.45)
        return root


class Painting(Prop):
    name = "painting"
    description = "A framed picture on the back wall"
    default_place = "back"
    wall = True
    params = Prop.params + [Param("color", "color", default="#e8b33c", label="Main colour"),
                            Param("height", "number", default=1.5, min=0.8, max=2.2, step=0.05)]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.9, 0.05, "back")
        y = s.depth / 2 - 0.02 if not s.outdoor else pos.y
        z = p.get("height", 1.5)
        shapes.box(name + ".frame", 0.9, 0.04, 0.68, look.matte("#6e4a2f", 0.5), at=(pos.x, y, z - 0.34), bevel=0.01)
        shapes.box(name, 0.78, 0.045, 0.56, look.matte("#f3e6cc"), at=(pos.x, y - 0.002, z - 0.28), bevel=0)
        rng = random.Random(name)
        for k in range(3):
            shapes.box(name + ".paint", rng.uniform(0.15, 0.35), 0.05, rng.uniform(0.12, 0.3),
                       look.matte(rng.choice([p.get("color", "#e8b33c"), "teal", "red", "navy", "pink"])),
                       at=(pos.x + rng.uniform(-0.2, 0.2), y - 0.004, z - 0.25 + rng.uniform(0, 0.2)), bevel=0)
        s.focus.setdefault(name, Vector((pos.x, y, z)))
        return None


class WallClock(Prop):
    name = "clock"
    description = "A round clock on the back wall"
    default_place = "back-right"
    wall = True
    params = Prop.params + [Param("time", "text", default="10:10", label="Shows")]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.4, 0.05, "back-right")
        y = s.depth / 2 - 0.03 if not s.outdoor else pos.y
        z = 1.85
        face = shapes.cylinder(name, 0.2, 0.04, look.matte("white", 0.5), at=(pos.x, y, z), bevel=0.01, segments=32)
        face.rotation_euler.x = math.pi / 2
        rim = shapes.torus(name + ".rim", 0.2, 0.02, "charcoal", at=(pos.x, y - 0.02, z))
        rim.rotation_euler.x = math.pi / 2
        try:
            hh, mm = [int(v) for v in str(p.get("time", "10:10")).split(":")]
        except ValueError:
            hh, mm = 10, 10
        for length, ang in ((0.1, (hh % 12 + mm / 60) / 12), (0.16, mm / 60)):
            hand = shapes.box(name + ".hand", 0.015, 0.01, length, "charcoal", at=(pos.x, y - 0.045, z), bevel=0)
            hand.rotation_euler.y = ang * 2 * math.pi
        s.focus.setdefault(name, Vector((pos.x, y, z)))
        return None


class Blackboard(Prop):
    name = "blackboard"
    description = "A blackboard on the back wall (a classroom)"
    default_place = "back"
    wall = True
    params = Prop.params + [Param("width", "number", default=2.4, min=1, max=4, step=0.1)]

    def build(self, s, name, p):
        w = p.get("width", 2.4)
        pos = s.spot_for(p, w, 0.05, "back")
        y = s.depth / 2 - 0.03 if not s.outdoor else pos.y
        shapes.box(name + ".frame", w + 0.1, 0.04, 1.1, look.matte("wood"), at=(pos.x, y, 0.85), bevel=0.01)
        shapes.box(name, w, 0.045, 1.0, look.matte("#2f4a3a", 0.9), at=(pos.x, y - 0.003, 0.9), bevel=0)
        shapes.box(name + ".tray", w, 0.08, 0.03, look.matte("wood"), at=(pos.x, y - 0.05, 0.84), bevel=0.005)
        for k in range(4):
            shapes.box(name + ".chalk", 0.5 - 0.1 * k, 0.046, 0.025, look.matte("#e8ece6"),
                       at=(pos.x - w / 4 + 0.05 * k, y - 0.005, 1.6 - 0.15 * k), bevel=0)
        s.focus.setdefault(name, Vector((pos.x, y, 1.4)))
        s.marks[name] = Mark(name, (pos.x - w / 2 + 0.3, y - 0.7), facing=math.pi)
        return None


class ModelProp(Prop):
    name = "model"
    description = "Your own 3D model as a prop (glTF, FBX, OBJ in models/; `dreamreel generate --prop` makes one)"
    default_place = "center"
    params = Prop.params + [Param("file", "model", required=True, label="Model file (in models/)"),
                            Param("height", "number", default=1.0, min=0.02, max=30, step=0.05, label="Height (m)"),
                            Param("facing", "choice", default="camera", choices=("camera", "left", "right", "back")),
                            Param("solid", "bool", default=True, label="Characters walk round it")]

    def build(self, s, name, p):
        import os
        from . import quaternius
        from .models import find
        if not p.get("file"):
            raise ValueError(f"prop {name}: a model prop needs file = \"models/...\"")
        path = find(p["file"])
        if not os.path.exists(path):
            raise ValueError(f"prop {name}: no model file {p['file']!r}")
        pos = Vector(p["at"][:2]) if "at" in p else s.spot_for(p, 0.6, 0.6, "center")
        f = {"left": -math.pi / 2, "right": math.pi / 2, "camera": 0.0, "back": math.pi}[p.get("facing", "camera")]
        obj = quaternius.place_mesh(quaternius.load(path, f"model.{name}"), name, (None, None, float(p.get("height", 1.0))),
                                    (pos.x, pos.y, 0), f)
        w, d = obj.dimensions.x, obj.dimensions.y
        if p.get("solid", True):
            s.block(pos, w if abs(math.sin(f)) < 0.5 else d, d if abs(math.sin(f)) < 0.5 else w)
        s.marks.setdefault(name, Mark(name, (pos.x, pos.y - max(w, d) / 2 - 0.45), facing=math.pi))
        return obj


CARS = {"car": "NormalCar1", "small": "NormalCar2", "suv": "SUV", "sports": "SportsCar", "taxi": "Taxi",
        "police": "Cop"}
CAR_LENGTH = {"small": 0.8, "sports": 0.95, "police": 0.9}


class Car(Prop):
    name = "car"
    description = "A car (Quaternius's: car, small, suv, sports, taxi, police)"
    default_place = "front-left"
    params = Prop.params + [Param("color", "color", default="red"),
                            Param("model", "choice", default="car", choices=tuple(CARS)),
                            Param("facing", "choice", default="left", choices=("left", "right", "camera", "back"))]

    def build(self, s, name, p):
        if "at" in p:
            pos = Vector(p["at"])
        else:
            pos = s.spot_for(p, 1.9, 0.9, "front-left")
        f = {"left": -math.pi / 2, "right": math.pi / 2, "camera": 0.0, "back": math.pi}[p.get("facing", "left")]
        kind = p.get("model", "car")
        length = s.sized(2.0, 4.2) * CAR_LENGTH.get(kind, 1.0)
        car = s.model(CARS.get(kind, CARS["car"]), name, (None, length, None), (pos.x, pos.y, 0), f, pack="cars")
        if car is not None:
            if kind not in ("taxi", "police"):      # repaint the body (the biggest surface)
                area = {}
                for poly in car.data.polygons:
                    area[poly.material_index] = area.get(poly.material_index, 0.0) + poly.area
                slot = car.material_slots[max(area, key=area.get)]
                slot.link = "OBJECT"
                slot.material = look.plastic(p.get("color", "red"), 0.3, 0.6)
            wide = car.dimensions.x
            along = abs(math.sin(f)) > 0.5
            s.block(pos, length if along else wide, wide if along else length)
            s.marks.setdefault(name, Mark(name, (pos.x, pos.y - wide / 2 - 0.45 if along else pos.y - length / 2 - 0.45),
                                          facing=math.pi))
            return car
        root = shapes.empty(name, at=(pos.x, pos.y, 0))
        root.rotation_euler.z = f + math.pi / 2       # the car is built pointing along +x
        c = look.plastic(p.get("color", "red"), 0.3, 0.6)
        shapes.box(name, 2.0, 0.9, 0.42, c, root, at=(0, 0, 0.16), bevel=0.12)
        shapes.box(name + ".cabin", 1.05, 0.8, 0.36, c, root, at=(-0.12, 0, 0.55), bevel=0.12)
        glass = look.plastic("#2a3a4a", 0.1, 0.8)
        shapes.box(name + ".glass", 1.0, 0.82, 0.24, glass, root, at=(-0.12, 0, 0.6), bevel=0.08)
        for sx in (-1, 1):
            for sy in (-1, 1):
                wheel = shapes.cylinder(name + ".wheel", 0.17, 0.12, "charcoal", root,
                                        at=(sx * 0.62, sy * 0.4, 0.17), bevel=0.02, segments=20)
                wheel.rotation_euler.x = math.pi / 2
                wheel.location.y += sy * 0.06
            shapes.sphere(name + ".light", 0.06, look.plastic("#fff6d8", 0.2, 0.2, emission=0.8), root,
                          at=(1.0, sx * 0.3, 0.42), segments=12)
        s.block(pos, 2.0 if abs(math.sin(f)) > 0.5 else 0.9, 0.9 if abs(math.sin(f)) > 0.5 else 2.0)
        s.marks.setdefault(name, Mark(name, (pos.x, pos.y - 0.9), facing=math.pi))
        return root


# ---------------------------------------------------------------------- a science lab
def _metal(color="#c9ced3"):
    return look.metal(color, 0.28)


class Tray(Item):
    mass, bounce, shape = 0.8, 0.15, "box"
    description = "A metal dissection tray"

    def build(self, s, x, y, z, rng):
        m = _metal()
        shapes.box("tray", 0.46, 0.32, 0.012, m, at=(x, y, z), bevel=0.004)
        for sx in (-1, 1):
            shapes.box("tray.rim", 0.012, 0.32, 0.035, m, at=(x + sx * 0.224, y, z), bevel=0.003)
        for sy in (-1, 1):
            shapes.box("tray.rim", 0.46, 0.012, 0.035, m, at=(x, y + sy * 0.154, z), bevel=0.003)
        shapes.box("tray.wax", 0.43, 0.29, 0.008, look.matte("#2f3436", 0.35), at=(x, y, z + 0.012), bevel=0)
        s.focus.setdefault("tray", Vector((x, y, z + 0.03)))
        s.add_mark("tray", (x, y - 0.55), facing="back")
        s.add_surface("tray", (x, y), z + 0.02, (0.4, 0.26))


class Scalpel(Item):
    mass, bounce = 0.04, 0.3
    description = "A scalpel"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("scalpel", 0.008, 0.12, _metal("#d9dde0"), at=(x, y, z + 0.008), rot=(0, math.pi / 2, 0),
                        bevel=0, segments=8)
        blade = shapes.box("scalpel.blade", 0.035, 0.002, 0.012, _metal("#eef1f3"), at=(x + 0.135, y, z + 0.002),
                           bevel=0)
        blade.rotation_euler.y = 0.15


class ToolCup(Item):
    mass, bounce = 0.3, 0.15
    name = "tool-cup"
    description = "A cup of scalpels, probes and tweezers"

    def build(self, s, x, y, z, rng):
        x += 0.3
        shapes.cylinder("tool-cup", 0.045, 0.11, look.plastic("#3a3d40", 0.5, 0.2), at=(x, y, z))
        m = _metal("#d9dde0")
        for k in range(4):
            tool = shapes.cylinder("tool", 0.005, 0.2, m, at=(x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.02, 0.02),
                                                                 z + 0.02), bevel=0, segments=6)
            tool.rotation_euler = (rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), 0)


class Jar(Item):
    mass, bounce = 0.7, 0.1
    description = "A specimen jar with something floating in it"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("jar", 0.07, 0.2, look.glass("#dff2e6"), at=(x, y, z))
        shapes.cylinder("jar.lid", 0.074, 0.03, "charcoal", at=(x, y, z + 0.2))
        shapes.cylinder("jar.liquid", 0.064, 0.15, look.glass("#d9e8a0"), at=(x, y, z + 0.01))
        thing = shapes.ellipsoid("jar.thing", 0.03, 0.025, 0.04, look.plastic(rng.choice(["#8a9a5b", "#c9a27a", "#5f7f9f"]),
                                                                               0.5, 0.2), at=(x, y, z + 0.09))
        thing.rotation_euler.y = rng.uniform(-0.6, 0.6)


class Beaker(Item):
    mass, bounce = 0.2, 0.15
    description = "A glass beaker"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("beaker", 0.05, 0.13, look.glass(), at=(x, y, z))
        shapes.cylinder("beaker.liquid", 0.046, 0.06, look.glass(rng.choice(["#7fc8e8", "#e88a8a", "#9de87f"])),
                        at=(x, y, z + 0.005))


class Bottle(Item):
    mass, bounce = 0.5, 0.1
    description = "A brown chemical bottle with a label"

    def build(self, s, x, y, z, rng):
        shapes.cylinder("bottle", 0.055, 0.2, look.plastic("#6b3f1f", 0.15, 0.6), at=(x, y, z))
        shapes.cylinder("bottle.neck", 0.022, 0.06, look.plastic("#6b3f1f", 0.15, 0.6), at=(x, y, z + 0.2))
        shapes.cylinder("bottle.cap", 0.026, 0.03, "charcoal", at=(x, y, z + 0.26))
        shapes.box("bottle.label", 0.08, 0.01, 0.09, look.matte("#f4f1ea"), at=(x, y - 0.05, z + 0.05), bevel=0)


class Scale(Item):
    mass, bounce, shape = 1.2, 0.05, "box"
    description = "A weighing scale"

    def build(self, s, x, y, z, rng):
        shapes.box("scale", 0.2, 0.22, 0.07, look.plastic("#e8862e", 0.4, 0.3), at=(x, y, z), bevel=0.02)
        shapes.box("scale.dial", 0.1, 0.01, 0.05, look.matte("#f4f1ea"), at=(x, y - 0.11, z + 0.01), bevel=0)
        shapes.cylinder("scale.pan", 0.1, 0.012, _metal(), at=(x, y, z + 0.075))


class LabBench(Prop):
    name = "lab_bench"
    description = "A lab bench with a black top and cupboards"
    default_place = "center"
    params = Prop.params + [Param("width", "number", default=1.8, min=0.8, max=3.5, step=0.1),
                            Param("color", "color", default="#c9b49a", label="Cupboards"),
                            Param("items", "items", label="On top")]

    def build(self, s, name, p):
        w, d, h = p.get("width", 1.8), 0.75, 0.55
        pos = s.spot_for(p, w, d, "center")
        c = p.get("color", "#c9b49a")
        shapes.box(name, w - 0.06, d - 0.08, h - 0.05, c, at=(pos.x, pos.y, 0), bevel=0.01)
        shapes.box(name + ".top", w, d, 0.05, look.plastic("#1f2224", 0.35, 0.3), at=(pos.x, pos.y, h - 0.05),
                   bevel=0.01)
        n = max(1, int(w / 0.45))
        for i in range(n):
            x = pos.x - w / 2 + (i + 0.5) * w / n
            shapes.box(name + ".door", w / n - 0.04, 0.01, h - 0.15, c, at=(x, pos.y - d / 2 + 0.035, 0.05), bevel=0.004)
            shapes.box(name + ".handle", 0.06, 0.02, 0.012, _metal(), at=(x, pos.y - d / 2 + 0.025, h - 0.16), bevel=0.003)
        for item in p.get("items", []):
            s.place_item(item, pos, h, w, on=name, depth=d)
        s.block(pos, w, d)
        s.add_surface(name, pos, h, (w, d))
        s.marks[name] = Mark(name, (pos.x, pos.y - d / 2 - 0.35), facing=math.pi)
        for side, label in ((-1, "left"), (1, "right")):
            s.marks[f"{name}-{label}"] = Mark(f"{name}-{label}", (pos.x + side * (w / 2 + 0.35), pos.y),
                                                 facing=math.pi / 2 * (1 if side < 0 else -1))
        return None


class Shelves(Prop):
    name = "shelves"
    description = "Open shelves of jars, beakers and bottles (a lab or a pantry)"
    default_place = "back-right"
    params = Prop.params + [Param("width", "number", default=1.2, min=0.6, max=3, step=0.1),
                            Param("color", "color", default="#c9b49a")]

    def build(self, s, name, p):
        w = p.get("width", 1.2)
        pos = _wall_y(s, dict(p, place=p.get("place", "back-right")), 0.3)
        c = p.get("color", "#c9b49a")
        for k in range(4):
            shapes.box(name + ".shelf", w, 0.3, 0.025, c, at=(pos.x, pos.y, 0.05 + k * 0.42), bevel=0.004)
        for sx in (-1, 1):
            shapes.box(name, 0.03, 0.3, 1.35, c, at=(pos.x + sx * (w / 2 - 0.015), pos.y, 0), bevel=0.004)
        rng = random.Random(name)
        kinds = ["jar", "beaker", "bottle", "jar"]
        for k in range(1, 4):
            x = pos.x - w / 2 + 0.12
            while x < pos.x + w / 2 - 0.12:
                plugins.get("item", rng.choice(kinds))().build(s, x, pos.y, 0.075 + k * 0.42, rng)
                x += rng.uniform(0.16, 0.24)
        s.block(pos, w, 0.3)
        return None


class Poster(Prop):
    name = "poster"
    description = "A poster on the back wall: a table of elements, a safety notice or a chart"
    default_place = "back-left"
    wall = True
    params = Prop.params + [Param("design", "choice", default="elements", choices=("elements", "safety", "chart")),
                            Param("height", "number", default=1.5, min=0.8, max=2.2, step=0.05)]

    def build(self, s, name, p):
        pos = s.spot_for(p, 0.8, 0.05, "back-left")
        y = s.depth / 2 - 0.02 if not s.outdoor else pos.y
        z = p.get("height", 1.5)
        design = p.get("design", "elements")
        rng = random.Random(name)
        if design == "elements":
            w, h = 0.95, 0.6
            shapes.box(name, w, 0.01, h, look.matte("#f4f1ea"), at=(pos.x, y, z - h / 2), bevel=0)
            cols = ["#e88a8a", "#f2c46d", "#9de87f", "#7fc8e8", "#c6a4e8", "#f4f1ea"]
            for r in range(7):
                for c in range(18):
                    if r == 0 and 0 < c < 17 or r in (1, 2) and 1 < c < 12:
                        continue
                    shapes.box(name + ".cell", 0.042, 0.012, 0.05, look.matte(cols[min(5, (c // 3 + r) % 6)]),
                               at=(pos.x - w / 2 + 0.06 + c * 0.047, y - 0.003, z - 0.08 - r * 0.062), bevel=0)
        elif design == "safety":
            w, h = 0.5, 0.7
            shapes.box(name, w, 0.01, h, look.matte("#f2d13a"), at=(pos.x, y, z - h / 2), bevel=0)
            shapes.box(name + ".band", w - 0.08, 0.012, 0.12, look.matte("#1c1a1a"), at=(pos.x, y - 0.003, z - 0.18),
                       bevel=0)
            mark = shapes.cylinder(name + ".sign", 0.12, 0.012, look.matte("#1c1a1a"), at=(pos.x, y - 0.004, z - 0.45),
                                   segments=3, bevel=0)
            mark.rotation_euler.x = math.pi / 2
        else:
            w, h = 0.7, 0.5
            shapes.box(name, w, 0.01, h, look.matte("#f4f1ea"), at=(pos.x, y, z - h / 2), bevel=0)
            for k in range(6):
                bh = rng.uniform(0.08, 0.36)
                shapes.box(name + ".bar", 0.07, 0.012, bh, look.matte(rng.choice(["teal", "red", "navy"])),
                           at=(pos.x - 0.25 + k * 0.1, y - 0.003, z - h + 0.05), bevel=0)
        s.focus.setdefault(name, Vector((pos.x, y, z - 0.3)))
        return None
