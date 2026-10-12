"""Ready-made 3D assets. Each returns an `Item` (see item.py) so it can be placed and animated.

Coordinates: Blender units, Z is up, the default camera looks along +Y (towards the back).
Text, screens and logos stand upright facing the camera.

    Text3D     extruded, glowing title text; .type_on() reveals it letter by letter
    Counter    a number that counts up
    Card       flat rectangle (solid colour or image)
    Screen     an image (screenshot) with a glowing frame
    Logo       an image with transparency, sized by height
    Sphere     ball
    Ring       circle outline; .draw_on() draws it; Arc is a partial ring
    Line       a path through points; .draw_on()
    Starfield  a cloud of tiny stars (background depth)
    GridFloor  glowing grid on the ground (tech look)
    Globe      dotted world map on a sphere; .focus(lat, lon) turns a place to the camera; .marker()
    BarChart   3D bars that grow; .highlight(i)
    ScreenWall a grid of screens; .cascade_in()
    Portal     a glowing gate (rings + swirl) to fly the camera through
"""
import json
import math
import os
import random

import bmesh
import bpy
from mathutils import Euler, Vector

from .item import Item
from .keys import key, socket_key, value_at
from .materials import GlowMaterial, load_image
from .stage import STAGE

_FONT_CACHE = {}
_DATA = os.path.join(os.path.dirname(__file__), "data")


def _font(path):
    if not path:
        return None
    if path not in _FONT_CACHE:
        _FONT_CACHE[path] = bpy.data.fonts.load(path, check_existing=True) if os.path.exists(path) else None
        if _FONT_CACHE[path] is None:
            print(f"[motionkit] font not found: {path}; using Blender's default font")
    return _FONT_CACHE[path]


def _mesh_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat.mat)
    return STAGE.link(ob)


def _plane_object(name, w, h, mat):
    me = bpy.data.meshes.new(name)
    # XZ plane facing -Y (the camera), UVs 0-1
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = co
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat.mat)
    return STAGE.link(ob)


def _curve_object(name, mat, thickness):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thickness
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.bevel_factor_mapping_start = "SPLINE"
    cu.bevel_factor_mapping_end = "SPLINE"
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(mat.mat)
    return STAGE.link(ob), cu


class _Drawable(Item):
    """Curve-based items that can draw themselves on."""

    def draw_on(self, at, duration=1.0, ease="smooth", from_middle=False):
        """Draw the line/ring progressively from start to end (or outwards from the middle)."""
        cu = self.obj.data
        if from_middle:
            key(cu, "bevel_factor_start", at, 0.5, ease)
            key(cu, "bevel_factor_start", at + duration, 0.0, ease)
            key(cu, "bevel_factor_end", at, 0.5, ease)
        else:
            key(cu, "bevel_factor_end", at, 0.0, ease)
        key(cu, "bevel_factor_end", at + duration, 1.0, ease)
        return self

    def erase(self, at, duration=1.0, ease="smooth"):
        cu = self.obj.data
        key(cu, "bevel_factor_start", at, 0.0, ease)
        key(cu, "bevel_factor_start", at + duration, 1.0, ease)
        return self


# ---------------------------------------------------------------------------------------------- text
class Text3D(Item):
    """Extruded, glowing text standing up and facing the camera.

    Args:
        text: the words. Use "\\n" for a new line.
        size: letter height in Blender units.
        color, glow: see GlowMaterial.
        depth: extrusion (0 = flat).
        font: path to a .ttf/.otf file (default: Blender's built-in font).
        align: "left", "center" or "right".
        spacing: letter spacing multiplier (1.0 = normal, 1.3 = airy).
    """

    def __init__(self, text, size=1.0, color="white", glow=1.5, depth=0.05, font=None, align="center",
                 spacing=1.0, opacity=1.0):
        mat = GlowMaterial(color, glow, opacity, name=f"text {text[:12]}")
        self._args = dict(size=size, depth=depth, font=font, align=align, spacing=spacing)
        ob = self._make(text, mat)
        self.text = text
        super().__init__(ob, [mat])

    def _make(self, body, mat):
        a = self._args
        cu = bpy.data.curves.new("text", "FONT")
        cu.body = body
        cu.size = a["size"]
        cu.align_x = a["align"].upper()
        cu.align_y = "CENTER"
        cu.extrude = a["depth"]
        cu.space_character = a["spacing"]
        f = _font(a["font"])
        if f:
            cu.font = f
        ob = bpy.data.objects.new("text " + body[:16], cu)
        ob.data.materials.append(mat.mat)
        ob.rotation_euler = (math.radians(90), 0, 0)
        return STAGE.link(ob)

    def type_on(self, at, duration=1.0, cursor=False):
        """Reveal the text letter by letter, like typing."""
        n = len(self.text)
        step = duration / n
        for i in range(1, n):
            ghost = self._make(self.text[:i] + ("|" if cursor else ""), self.materials[0])
            ghost.parent, ghost.location, ghost.rotation_euler = self.obj.parent, self.obj.location, self.obj.rotation_euler
            ghost.scale = self.obj.scale
            Item(ghost).visible(at + (i - 1) * step, at + i * step)
            if self.text[i - 1] == " ":
                Item(ghost).hide(at)  # nothing new to show on a space
        self.show(at + (n - 1) * step)
        return self


class Counter(Item):
    """A number that counts from `start` to `end` between `at` and `at + duration`.

    `prefix`/`suffix` wrap the number ("$", "%", "+"); `steps` = how many distinct values are shown.
    """

    def __init__(self, end, start=0, at=0.0, duration=1.5, size=1.0, color="white", glow=1.5, prefix="",
                 suffix="", steps=30, decimals=0, font=None):
        mat = GlowMaterial(color, glow, name="counter")
        fmt = lambda v: f"{prefix}{v:,.{decimals}f}{suffix}"
        objs = []
        for k in range(steps + 1):
            e = 1 - (1 - k / steps) ** 3  # ease out: fast, then settles
            t = Text3D.__new__(Text3D)
            t._args = dict(size=size, depth=0.04, font=font, align="center", spacing=1.0)
            objs.append(t._make(fmt(start + (end - start) * e), mat))
        root = STAGE.link(bpy.data.objects.new("counter", None))
        dt = duration / steps
        for k, ob in enumerate(objs):
            ob.parent = root
            ob.location = (0, 0, 0)
            Item(ob).visible(at + k * dt if k else 0.0, at + (k + 1) * dt if k < steps else None)
        super().__init__(root, [mat])


# ---------------------------------------------------------------------------------------------- flat things
class Card(Item):
    """A flat rectangle facing the camera: solid colour, or an image when `image=` is given."""

    def __init__(self, width=2.0, height=1.2, color="white", glow=1.0, image=None, opacity=1.0):
        mat = GlowMaterial(color, glow, opacity, image=image, name="card")
        super().__init__(_plane_object("card", width, height, mat), [mat])


class Screen(Item):
    """A screenshot with a glowing frame. Height follows the image's aspect ratio."""

    def __init__(self, image, width=3.2, frame_color="pink", frame_glow=2.5, frame=0.04, opacity=1.0):
        mat = GlowMaterial("white", 1.0, opacity, image=image, name="screen")
        h = width / mat.aspect
        ob = _plane_object("screen", width, h, mat)
        fmat = GlowMaterial(frame_color, frame_glow, opacity, name="screen frame")
        fr = _plane_object("screen frame", width + frame * 2, h + frame * 2, fmat)
        fr.parent = ob
        fr.location = (0, 0.005, 0)
        super().__init__(ob, [mat, fmat])
        self.height = h


class Logo(Item):
    """An image with transparency (PNG logo), sized by `height`."""

    def __init__(self, image, height=1.0, opacity=1.0):
        mat = GlowMaterial("white", 1.0, opacity, image=image, name="logo")
        super().__init__(_plane_object("logo", height * mat.aspect, height, mat), [mat])


# ---------------------------------------------------------------------------------------------- solids and lines
class Sphere(Item):
    def __init__(self, radius=1.0, color="indigo", glow=1.0, opacity=1.0, blend=False):
        mat = GlowMaterial(color, glow, opacity, blend=blend, name="sphere")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)
        super().__init__(_mesh_object("sphere", bm, mat), [mat])


class Ring(_Drawable):
    """A circle outline in the XZ plane (facing the camera). `.draw_on()` draws it, `.spin()` turns it."""

    def __init__(self, radius=2.0, thickness=0.04, color="pink", glow=3.0, start=0.0, end=360.0, opacity=1.0):
        mat = GlowMaterial(color, glow, opacity, name="ring")
        ob, cu = _curve_object("ring", mat, thickness)
        sp = cu.splines.new("POLY")
        n = max(8, int(abs(end - start) / 3))
        sp.points.add(n)
        for i, p in enumerate(sp.points):
            a = math.radians(start + (end - start) * i / n)
            p.co = (radius * math.cos(a), 0, radius * math.sin(a), 1)
        super().__init__(ob, [mat])


def Arc(radius=2.0, start=0.0, end=120.0, **kw):
    """A partial ring from `start` to `end` degrees (0 = right, 90 = top)."""
    return Ring(radius, start=start, end=end, **kw)


class Line(_Drawable):
    """A smooth path through `points` [(x, y, z), ...]."""

    def __init__(self, points, thickness=0.03, color="cyan", glow=2.5, opacity=1.0):
        mat = GlowMaterial(color, glow, opacity, name="line")
        ob, cu = _curve_object("line", mat, thickness)
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(points) - 1)
        for bp, co in zip(sp.bezier_points, points):
            bp.co = co
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        super().__init__(ob, [mat])


def _dots_object(name, points, radius, mat):
    bm = bmesh.new()
    for p in points:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius)
        bmesh.ops.translate(bm, vec=Vector(p), verts=res["verts"])
    return _mesh_object(name, bm, mat)


class Starfield(Item):
    """Background stars: `count` dots spread in a box of `spread` (x, y, z) around `center`."""

    def __init__(self, count=1500, spread=(40, 30, 25), color="muted", size=0.03, glow=1.5, seed=7, center=(0, 20, 0)):
        rnd = random.Random(seed)
        pts = [tuple(rnd.uniform(-1, 1) * s for s in spread) for _ in range(count)]
        mat = GlowMaterial(color, glow, name="stars")
        ob = _dots_object("stars", pts, size, mat)
        ob.location = center
        super().__init__(ob, [mat])


class GridFloor(Item):
    """A glowing grid on the ground (z = `height`), `size` units wide, a line every `spacing`."""

    def __init__(self, size=40.0, spacing=1.0, color="indigo", glow=1.2, height=-2.0, thickness=0.012, opacity=0.6):
        mat = GlowMaterial(color, glow, opacity, name="grid")
        bm = bmesh.new()
        n = int(size / spacing)
        for i in range(n + 1):
            c = -size / 2 + i * spacing
            for (x0, y0, x1, y1) in ((c, -size / 2, c, size / 2), (-size / 2, c, size / 2, c)):
                horiz = y0 == y1
                dx, dy = (0, thickness) if horiz else (thickness, 0)
                vs = [bm.verts.new(v) for v in ((x0 - dx, y0 - dy, 0), (x1 - dx, y1 - dy, 0), (x1 + dx, y1 + dy, 0), (x0 + dx, y0 + dy, 0))]
                bm.faces.new(vs)
        ob = _mesh_object("grid", bm, mat)
        ob.location = (0, 0, height)
        super().__init__(ob, [mat])


# ---------------------------------------------------------------------------------------------- globe
def _lat_lon(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    # lon 0 / lat 0 faces the camera (-Y); east is to the right (+X); north is up (+Z)
    return Vector((r * math.cos(la) * math.sin(lo), -r * math.cos(la) * math.cos(lo), r * math.sin(la)))


class Globe(Item):
    """A dotted world map on a dark sphere.

    Args:
        radius: globe radius.
        land_color / ocean_color: colours of the land dots and the sphere.
        dot_size: radius of each land dot.

    Methods:
        focus(lat, lon, at, duration): rotate so that place faces the camera.
        marker(lat, lon, color, label=None): a glowing pin (returns an Item to animate, e.g. .pop_in()).
    """

    def __init__(self, radius=3.0, land_color="cyan", ocean_color="#0b1530", dot_size=0.022, glow=1.4):
        dots = json.load(open(os.path.join(_DATA, "world-land-dots.json")))
        ocean = GlowMaterial(ocean_color, 1.0, blend=False, name="ocean")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=radius * 0.995)
        body = _mesh_object("globe", bm, ocean)
        land = GlowMaterial(land_color, glow, blend=False, name="land")
        pts = [_lat_lon(la, lo, radius) for la, lo in dots]
        dob = _dots_object("land", pts, dot_size, land)
        dob.parent = body
        self.radius = radius
        body.rotation_mode = "ZXY"
        super().__init__(body, [ocean, land])

    def focus(self, lat, lon, at, duration=1.5, ease="smooth"):
        """Turn the globe so (lat, lon) faces the camera."""
        target = Euler((math.radians(lat), 0, math.radians(-lon)), "ZXY")  # spin the place to the front, then tilt it level
        key(self.obj, "rotation_euler", at, value_at(self.obj, "rotation_euler", at), ease)
        self._rot = target
        key(self.obj, "rotation_euler", at + duration, target, ease)
        return self

    def marker(self, lat, lon, color="pink", size=0.09, label=None, label_size=0.25):
        """A glowing pin on the surface (moves with the globe). Returns an Item; label is a child Text3D."""
        m = Sphere(size, color, glow=4.0, blend=True)
        m.obj.parent = self.obj
        m.obj.location = _lat_lon(lat, lon, self.radius * 1.01)
        m._loc = m.obj.location.copy()
        if label:
            t = Text3D(label, label_size, "white", glow=1.2, depth=0, align="left")
            t.obj.parent = m.obj
            t.obj.location = (size * 2.0, 0, size * 1.5)
            t.face_camera()
            m.parts.append(t)
        return m


# ---------------------------------------------------------------------------------------------- data
class BarChart(Item):
    """3D bars that grow from the floor.

    Args:
        values: numbers; bar heights are scaled so the largest is `height`.
        labels: optional names under the bars.
        color / highlight_color: normal and highlighted bar colours.
        show_values: print each value above its bar.
    Methods:
        grow(at, duration, stagger): bars rise one after another.
        highlight(index, at, duration): one bar glows in highlight_color and pulses.
    """

    def __init__(self, values, labels=None, width=6.0, height=3.0, color="indigo", highlight_color="pink",
                 show_values=True, text_color="white"):
        root = STAGE.link(bpy.data.objects.new("chart", None))
        n, top = len(values), max(values)
        slot = width / n
        self.bars, self.values = [], values
        self.highlight_color = highlight_color
        for i, v in enumerate(values):
            x = -width / 2 + slot * (i + 0.5)
            mat = GlowMaterial(color, 1.6, name=f"bar {i}")
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.translate(bm, vec=Vector((0, 0, 0.5)), verts=bm.verts)  # pivot at the floor
            ob = _mesh_object(f"bar {i}", bm, mat)
            ob.parent = root
            ob.location = (x, 0, 0)
            ob.scale = (slot * 0.62, slot * 0.62, height * v / top)
            bar = Item(ob, [mat])
            if show_values:
                t = Text3D(f"{v:g}", slot * 0.32, text_color, glow=1.2, depth=0)
                t.obj.parent = root
                t.obj.location = (x, 0, height * v / top + slot * 0.3)
                t._loc = t.obj.location.copy()
                bar.parts.append(t)
            if labels:
                lab = Text3D(str(labels[i]), slot * 0.3, "muted", glow=1.0, depth=0)
                lab.obj.parent = root
                lab.obj.location = (x, 0, -slot * 0.35)
                bar.parts.append(lab)
            self.bars.append(bar)
        super().__init__(root, [], self.bars)

    def grow(self, at, duration=1.0, stagger=0.12):
        """Bars rise from the floor one after another; their labels fade in."""
        for i, b in enumerate(self.bars):
            t = at + i * stagger
            s = b._scale
            key(b.obj, "scale", t, (s.x, s.y, 0.001), "ease_out")
            key(b.obj, "scale", t + duration, s, "smooth")
            for p in b.parts:
                p.fade_in(t + duration * 0.6, 0.4)
        return self

    def highlight(self, index, at, duration=0.8):
        """Make bar `index` glow in the highlight colour and pulse, then return to normal."""
        b = self.bars[index]
        b.color_to(self.highlight_color, at, 0.2).glow_to(3.5, at, 0.2)
        if len(b.parts):
            b.parts[0].pulse(at, 1, 1.5, duration)
        b.glow_to(1.6, at + duration, 0.3)
        return self


class ScreenWall(Item):
    """A grid of screenshots (e.g. today's app), `columns` wide, slightly curved around the camera."""

    def __init__(self, images, columns=3, width=3.0, gap=0.35, curve=8.0, frame_color="pink"):
        root = STAGE.link(bpy.data.objects.new("screen wall", None))
        screens = []
        rows = math.ceil(len(images) / columns)
        for i, img in enumerate(images):
            c, r = i % columns, i // columns
            s = Screen(img, width, frame_color=frame_color)
            x = (c - (columns - 1) / 2) * (width + gap)
            z = ((rows - 1) / 2 - r) * (s.height + gap)
            s.obj.parent = root
            s.at(x, abs(x) * curve / 100, z).turn(0, 0, -x * curve * 0.6)
            screens.append(s)
        super().__init__(root, [], screens)
        self.screens = screens

    def cascade_in(self, at, stagger=0.15, duration=0.6):
        """Screens pop in one after another."""
        for i, s in enumerate(self.screens):
            s.fade_in(at + i * stagger, duration).pop_in(at + i * stagger, duration)
        return self


class Portal(Item):
    """A glowing gate: two rings and a swirling core, in the XZ plane facing the camera.

    Fly the camera through it with `transitions.through_portal(movie, portal, at)`.
    """

    def __init__(self, radius=2.2, color="pink", color2="indigo", glow=4.0):
        root = STAGE.link(bpy.data.objects.new("portal", None))
        outer = Ring(radius, 0.06, color, glow)
        inner = Ring(radius * 0.86, 0.03, color2, glow)
        core = GlowMaterial(color2, 2.0, 0.55, name="portal core")
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=radius * 0.84)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler((math.radians(90), 0, 0)).to_matrix())
        disc = Item(_mesh_object("portal core", bm, core), [core])
        swirl = [Arc(radius * f, start=a, end=a + 110, thickness=0.02, color=color, glow=3.0)
                 for f, a in ((0.3, 0), (0.45, 120), (0.6, 240), (0.72, 60))]
        for it in [outer, inner, disc] + swirl:
            it.obj.parent = root
        super().__init__(root, [], [outer, inner, disc] + swirl)
        self.swirl = swirl

    def open(self, at, duration=0.8):
        """The gate grows open and its swirl starts turning."""
        self.pop_in(at, duration, 1.06)
        for i, s in enumerate(self.swirl):
            s.spin(turns=(-1) ** i * 2, start=at, end=at + 12, axis="Y")
        return self
