"""Time of day, sky and weather: the light and the air of a scene.

A scene file chooses them (a set file can give defaults for its scenes):

    time_of_day = "golden_hour"   # dawn, morning, day, golden_hour, sunset, dusk, night
    weather = "rain"              # clear, cloudy, overcast, fog, rain, snow, storm, windy
    weather_strength = 1.0        # 0.3 a little ... 2 a lot

Both are classes, so a film can add its own: an eclipse, a sandstorm, the sky of another planet.

    class AlienDusk(dr.TimeOfDay):
        description = "Two suns setting in a green sky"
        sun_elevation, sun_azimuth = 6, 30
        sun_color, sun_energy = "#c8ffb0", 1.6
        zenith, horizon = "#1d4d3a", "#a8e070"

    class Sandstorm(dr.Weather):
        description = "Blowing sand: hazy, orange, windy"
        wind = 2.0
        def adjust(self, light, k):
            light.tint_sky("#d9a066", 0.7 * k)
            light.sun_energy *= 0.4
            light.fog = 0.05 * k
            light.fog_color = "#d9a066"

How it works: the TimeOfDay makes a `Light` (sun, sky colours, how bright rooms and lamps are), the
Weather changes it (`adjust`) and adds things (`build`: clouds, rain; `animate`: lightning), then
dreamreel builds the sun, the sky, stars and moon, fog and the room lights from it.
"""
import math
import random

import bpy
from mathutils import Vector

from . import keys, look, shapes
from .plugins import Param, Plugin


def mix(a, b, t):
    """Mix two colours (names, hex or linear rgb) in linear light: t=0 is a, t=1 is b."""
    a, b = look.rgb(a), look.rgb(b)
    t = max(0.0, min(1.0, t))
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def fx_object(obj, final_only=False):
    """Mark an object as atmosphere: the camera sees through it when looking for a clear view, and
    with final_only it is left out of the fast previz render (fog volumes)."""
    obj["dr_fx"] = True
    if final_only:
        obj["dr_final_only"] = True
    return obj


class Light:
    """What the light is like: made by a TimeOfDay, changed by Weather, then built into the scene."""

    def __init__(self, **kw):
        self.sun_elevation = 50.0     # degrees above the horizon
        self.sun_azimuth = 215.0      # 0 = behind the set (in shot), 90 = right, 180 = behind the camera
        self.sun_color = "#fff1dc"
        self.sun_energy = 3.2
        self.sun_softness = 8.0       # degrees: bigger is softer shadows
        self.zenith = "#6fa8dc"
        self.horizon = "#a9d2f0"
        self.sky_strength = 0.9
        self.room = 1.0               # how bright a room's own lights are
        self.room_color = "#fff0dc"
        self.practicals = 1.0         # lamps and street lights
        self.lit_windows = 0.0        # share of a town's windows lit from inside
        self.stars = 0.0
        self.sun_disc = False
        self.moon = False
        self.fog = 0.0                # fog density outdoors
        self.fog_color = "#dfe3e8"
        self.wind = 0.3               # how much trees sway
        self.key = 1.0                # the main light (a style like noir makes it harder...)
        self.fill = 1.0               # ...and the light filling the shadows weaker
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def dark(self):
        return self.sun_energy < 1.0 and self.practicals >= 2.0

    def tint_sky(self, color, t):
        """Move the sky towards a colour (grey for overcast, orange for a sandstorm)."""
        self.zenith = mix(self.zenith, color, t)
        self.horizon = mix(self.horizon, color, t)

    def direction(self):
        """Unit vector towards the sun."""
        el, az = math.radians(self.sun_elevation), math.radians(self.sun_azimuth)
        return Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))


# ---------------------------------------------------------------------- time of day
class TimeOfDay(Plugin):
    """The time of day: where the sun is, its colour, the sky, and how much lamps matter."""
    kind = "time"
    abstract = True
    sun_elevation, sun_azimuth = 50.0, 215.0
    sun_color, sun_energy = "#fff1dc", 3.2
    zenith, horizon, sky_strength = "#6fa8dc", "#a9d2f0", 0.9
    room, room_color, practicals = 1.0, "#fff0dc", 1.0
    lit_windows, stars, sun_disc, moon = 0.0, 0.0, False, False

    @classmethod
    def describe_extra(cls):
        return {"dark": cls.practicals >= 2.0}

    def light(self):
        names = ("sun_elevation", "sun_azimuth", "sun_color", "sun_energy", "zenith", "horizon", "sky_strength",
                 "room", "room_color", "practicals", "lit_windows", "stars", "sun_disc", "moon")
        return Light(**{n: getattr(self, n) for n in names})


class Dawn(TimeOfDay):
    description = "First light: pink sky, long soft shadows, lamps still on"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 4, 110, "#ffb08a", 1.3
    zenith, horizon, sky_strength = "#4a5f9a", "#f4b49a", 0.55
    room, room_color, practicals, lit_windows, stars, sun_disc = 0.55, "#ffd9c4", 1.6, 0.3, 0.2, True


class Morning(TimeOfDay):
    description = "Fresh morning light"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 25, 200, "#fff0d8", 2.7
    zenith, horizon, sky_strength = "#7fb3e6", "#dbe9f2", 0.8
    room, room_color = 0.9, "#fff4e6"


class Day(TimeOfDay):
    description = "Bright daylight (the default)"


class GoldenHour(TimeOfDay):
    description = "Low warm sun before sunset: the most flattering light"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 11, 235, "#ffc27a", 2.7
    zenith, horizon, sky_strength = "#8fb0d8", "#ffd9a0", 0.75
    room, room_color, practicals = 0.85, "#ffd8a8", 1.2


class Sunset(TimeOfDay):
    description = "The sun going down behind the scene: orange sky, silhouettes"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 3, 25, "#ff8a4c", 1.9
    zenith, horizon, sky_strength = "#5a6aa8", "#ff9a6a", 1.0
    room, room_color, practicals, lit_windows, sun_disc = 0.6, "#ffb88a", 1.8, 0.4, True


class Dusk(TimeOfDay):
    description = "After sunset: blue hour, lights coming on"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 8, 20, "#9aa8ff", 0.5
    zenith, horizon, sky_strength = "#2a3570", "#c88aa0", 0.6
    room, room_color, practicals, lit_windows, stars = 0.45, "#c8c8ff", 2.2, 0.6, 0.35


class Night(TimeOfDay):
    description = "Moonlight, stars and lamps"
    sun_elevation, sun_azimuth, sun_color, sun_energy = 35, 200, "#aab8ff", 0.6
    zenith, horizon, sky_strength = "#0d1530", "#22305a", 0.25
    room, room_color, practicals, lit_windows, stars, moon = 0.35, "#aab8ff", 2.5, 0.7, 1.0, True


# ---------------------------------------------------------------------- weather
class Weather(Plugin):
    """Weather: changes the light (`adjust`), adds things to the scene (`build`) and moves them
    (`animate`, once the scene's length is known). `k` is the weather's strength (1 = normal)."""
    kind = "weather"
    abstract = True
    wind = 0.3

    def adjust(self, light, k):
        pass

    def build(self, env, k):
        pass

    def animate(self, env, k, length):
        pass


class Clear(Weather):
    description = "Clear sky (the default)"


class Cloudy(Weather):
    description = "Clouds drifting across the sky"
    wind = 0.5

    def adjust(self, light, k):
        light.sun_energy *= 1 - 0.25 * min(k, 2)
        light.tint_sky("#c4cad2", 0.25 * k)

    def build(self, env, k):
        env.clouds(int(10 * k), "#ffffff")


class Overcast(Weather):
    description = "A grey sky and soft, shadowless light"

    def adjust(self, light, k):
        light.sun_energy *= 0.35
        light.sun_softness = 35
        light.tint_sky("#aab1b9", min(1.0, 0.7 * k))
        light.sun_disc = light.moon = False
        light.stars = 0.0


class Fog(Weather):
    description = "Fog: the distance disappears"

    def adjust(self, light, k):
        light.sun_energy *= 0.55
        light.sun_softness = 25
        light.tint_sky("#d5d9de", min(1.0, 0.6 * k))
        light.fog = 0.035 * k
        light.fog_color = mix(light.horizon, "#ffffff", 0.3)
        light.stars = 0.0


class Rain(Weather):
    description = "Rain falling (outdoors), a grey sky"
    density, wind = 1.0, 0.6

    def adjust(self, light, k):
        light.sun_energy *= 0.4
        light.sun_softness = 30
        light.tint_sky("#8e969f", min(1.0, 0.6 * k))
        light.sun_disc = light.moon = False
        light.stars = 0.0

    def build(self, env, k):
        env.precipitation("rain", int(4000 * self.density * k))


class Snow(Weather):
    description = "Snow falling gently"
    wind = 0.4

    def adjust(self, light, k):
        light.sun_energy *= 0.6
        light.sun_softness = 25
        light.tint_sky("#dfe4ea", min(1.0, 0.5 * k))
        light.sun_disc = False
        light.stars *= 0.3

    def build(self, env, k):
        env.precipitation("snow", int(2500 * k))


class Storm(Rain):
    description = "Dark sky, heavy rain, wind and lightning"
    density, wind = 1.6, 1.6

    def adjust(self, light, k):
        super().adjust(light, k)
        light.sun_energy *= 0.5
        light.tint_sky("#4a5058", 0.6)
        light.practicals = max(light.practicals, 1.6)
        light.lit_windows = max(light.lit_windows, 0.4)

    def build(self, env, k):
        super().build(env, k)
        env.clouds(int(12 * k), "#6b727b")

    def animate(self, env, k, length):
        env.lightning(length, every=6.0 / max(0.3, k))


class Windy(Weather):
    description = "A strong wind: trees bend, clouds race"
    wind = 1.4

    def adjust(self, light, k):
        light.tint_sky("#c4cad2", 0.15)

    def build(self, env, k):
        env.clouds(int(8 * k), "#ffffff", drift=3.0)


# ---------------------------------------------------------------------- building it
class Environment:
    """The sky, sun, atmosphere and weather of one scene."""

    def __init__(self, scene, time_of_day="day", weather="clear", strength=1.0):
        from . import plugins
        self.scene = scene
        self.set = scene.set
        self.outdoor = self.set is not None and self.set.outdoor
        self.time = plugins.get("time", time_of_day or "day")()
        self.weather = plugins.get("weather", weather or "clear")()
        self.k = float(strength if strength is not None else 1.0)
        self.light = self.time.light()
        self.light.wind = self.weather.wind * (self.k if self.weather.wind > 0.3 else 1.0)
        self.weather.adjust(self.light, self.k)
        self.sun = None
        self.drifting = []    # (object, metres per second) for clouds
        self.falling = []     # (object, height, metres per second, sideways sway) for rain and snow
        self.rng = random.Random(f"{time_of_day}/{weather}")

    # -------------------------------------------------------------- build
    def build(self):
        L = self.light
        self._sky()
        custom = self.set is not None and self.set.lighting(self.scene, L.dark)
        if not custom:
            if self.outdoor:
                self._sun()
            else:
                self._room_lights()
        self._practicals()
        if self.set is not None:
            self.set.apply_light(L)
        if self.outdoor:
            if L.stars > 0:
                self._stars()
            if L.sun_disc or L.moon:
                self._disc()
            if L.fog > 0:
                self._fog()
        self.weather.build(self, self.k)

    def _sky(self):
        L = self.light
        world = bpy.data.worlds.new("world")
        self.scene.bscene.world = world
        world.use_nodes = True
        nt = world.node_tree
        bg = nt.nodes.get("Background")
        if self.outdoor:
            coords = nt.nodes.new("ShaderNodeTexCoord")
            sep = nt.nodes.new("ShaderNodeSeparateXYZ")
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.inputs["From Min"].default_value = -1.0
            mr.inputs["From Max"].default_value = 1.0
            nt.links.new(coords.outputs["Generated"], sep.inputs[0])
            nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
            nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
            cr = ramp.color_ramp
            cr.interpolation = "EASE"
            cr.elements[0].position, cr.elements[0].color = 0.0, (*mix(L.horizon, "#3a3a3a", 0.5), 1)
            cr.elements[1].position, cr.elements[1].color = 1.0, (*look.rgb(L.zenith), 1)
            e = cr.elements.new(0.5)
            e.color = (*look.rgb(L.horizon), 1)
            e = cr.elements.new(0.62)
            e.color = (*mix(L.horizon, L.zenith, 0.55), 1)
            bg.inputs["Strength"].default_value = L.sky_strength
            world.color = mix(L.horizon, L.zenith, 0.4)      # the fast previz shows this
        else:
            wall = mix("#f1e6d6", L.room_color, 0.4)
            bg.inputs["Color"].default_value = (*wall, 1)
            bg.inputs["Strength"].default_value = 0.55 * max(0.3, L.room) * L.fill
            world.color = wall
        self.background = bg

    def _sun(self):
        L = self.light
        data = bpy.data.lights.new("sun", "SUN")
        data.energy = L.sun_energy
        data.color = look.rgb(L.sun_color)
        data.angle = math.radians(L.sun_softness)
        sun = bpy.data.objects.new("sun", data)
        self.scene.bscene.collection.objects.link(sun)
        d = L.direction()
        if d.z < 0.05:                       # keep light coming from above the ground
            d.z = 0.05
            d.normalize()
        sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        self.sun = sun
        # a soft fill from the camera side, stronger when the sun is weak (night, rain), so faces read
        weak = max(0.12, 1.0 - L.sun_energy / 3.2)
        self._area("fill", (1.5, -9.0, 5.0), 900 * weak * L.fill, mix(L.zenith, "#ffffff", 0.55), 9.0,
                   target=(0, 0, 0.7))

    def _area(self, name, loc, energy, color, size, target=(0, 0, 0.6)):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = look.rgb(color)
        data.size = size
        obj = bpy.data.objects.new(name, data)
        self.scene.bscene.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return obj

    def _room_lights(self):
        L = self.light
        k = L.room
        ceil = getattr(self.set, "ceiling_h", None) if self.set is not None else None
        key_at = getattr(L, "key_position", (-3.0, -4.5, 4.2))
        if ceil:      # under the ceiling, coming in from the open side
            key_at = (key_at[0], min(key_at[1], -4.5), min(key_at[2], ceil - 0.25))
        self._area("key", key_at, 900 * k * L.key, mix("#fff0dc", L.room_color, 0.6), 4.0 if L.key <= 1 else 2.0)
        self._area("fill", (4.0, -3.5, min(2.5, (ceil or 9) - 0.3)), 350 * k * L.fill,
                   mix("#dce8ff", L.room_color, 0.3), 5.0)
        panels = getattr(self.set, "panels", [])
        if panels:    # strip lights in the ceiling (one light per row, to keep renders quick)
            rows = sorted({round(y, 3) for _, y in panels})
            xs = [x for x, _ in panels]
            span = max(xs) - min(xs) + 0.6
            each = 620 * L.fill ** 0.5 / len(rows) ** 0.5
            for y in rows:
                lt = self._area("strip light", ((max(xs) + min(xs)) / 2, y, ceil - 0.06), each, "#eef6ff", 1.0,
                                target=((max(xs) + min(xs)) / 2, y, 0))
                lt.data.shape = "RECTANGLE"
                lt.data.size, lt.data.size_y = span, 1.15
        elif ceil:
            self._area("top", (0, 0, ceil - 0.05), 250 * k * L.fill, mix("#fff6ea", L.room_color, 0.5), 3.0)
        else:
            self._area("top", (0, 0, 3.5), 250 * k * L.fill, mix("#fff6ea", L.room_color, 0.5), 6.0)
        # daylight through the windows, in the colour of the sun
        for x, y, z in (self.set.windows if self.set is not None else []):
            glow = L.sun_energy / 3.2
            if glow > 0.15:
                self._area("window light", (x, y + 0.6, z + 0.4), 260 * glow, L.sun_color, 1.3,
                           target=(x * 0.6, y - 2.5, 0.2))
        self.sun = None

    def _practicals(self):
        if self.set is None:
            return
        for loc, color, power in self.set.lights:
            data = bpy.data.lights.new("practical", "POINT")
            data.energy = power * self.light.practicals
            data.color = look.rgb(color)
            data.shadow_soft_size = 0.2
            obj = bpy.data.objects.new("practical", data)
            self.scene.bscene.collection.objects.link(obj)
            obj.location = loc

    def _emissive(self, name, color, strength):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (*look.rgb(color), 1)
        bsdf.inputs["Emission Color"].default_value = (*look.rgb(color), 1)
        bsdf.inputs["Emission Strength"].default_value = strength
        mat.diffuse_color = (*look.rgb(color), 1)
        return mat

    def _stars(self):
        import bmesh
        bm = bmesh.new()
        rng = random.Random(7)
        R = 260.0
        for _ in range(900):
            z = rng.uniform(0.12, 1.0)
            a = rng.uniform(0, 2 * math.pi)
            c = Vector((math.cos(a) * math.sqrt(1 - z * z), math.sin(a) * math.sqrt(1 - z * z), z)) * R
            s = rng.uniform(0.25, 0.6)
            t1 = c.orthogonal().normalized() * s
            t2 = c.normalized().cross(t1).normalized() * s
            vs = [bm.verts.new(c + t1), bm.verts.new(c + t2 - t1 * 0.5), bm.verts.new(c - t2 - t1 * 0.5)]
            bm.faces.new(vs)
        obj = shapes._object("fx.stars", bm, self._emissive("stars", "#ffffff", 4.0 * self.light.stars), None,
                             (0, 0, 0), (0, 0, 0), smooth=False)
        fx_object(obj)

    def _disc(self):
        L = self.light
        d = L.direction()
        if L.moon:
            pos = Vector((0.35, 0.94, 0.3)).normalized() * 240
            fx_object(shapes.sphere("fx.moon", 7, self._emissive("moon", "#eef1ff", 2.5), at=pos, segments=24))
        else:
            if d.z < 0.01:
                d.z = 0.01
            pos = d.normalized() * 240
            fx_object(shapes.sphere("fx.sun", 11, self._emissive("sun disc", mix(L.sun_color, "#fff6e0", 0.5), 8.0),
                                    at=pos, segments=24))

    def _fog(self):
        L = self.light
        obj = shapes.box("fx.fog", 160, 160, 40, None, at=(0, 10, -1), bevel=0)
        mat = bpy.data.materials.new("fog")
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            if n.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(n)
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = (*look.rgb(L.fog_color), 1)
        vol.inputs["Density"].default_value = L.fog
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
        obj.data.materials.append(mat)
        fx_object(obj, final_only=True)
        sc = self.scene.bscene
        if hasattr(sc.eevee, "volumetric_end"):
            sc.eevee.volumetric_end = 150

    # -------------------------------------------------------------- weather helpers
    def clouds(self, n, color, drift=0.6):
        """Puffy clouds high in the sky, behind and around the set."""
        if not self.outdoor or n <= 0:
            return
        mat = look.plastic(mix(color, self.light.horizon, 0.25), 0.95, 0.0, emission=0.35)
        rng = self.rng
        for i in range(n):
            a = rng.uniform(-1.3, 1.3)
            dist = rng.uniform(90, 200)
            c = Vector((math.sin(a) * dist, math.cos(a) * dist, rng.uniform(25, 55)))
            root = shapes.empty(f"fx.cloud{i}", at=c)
            fx_object(root)
            size = rng.uniform(8, 18)
            for j in range(rng.randint(4, 7)):
                fx_object(shapes.ellipsoid(f"fx.cloud{i}", size * rng.uniform(0.5, 0.9), size * rng.uniform(0.4, 0.6),
                                           size * rng.uniform(0.25, 0.4), mat, root,
                                           at=(rng.uniform(-1, 1) * size, rng.uniform(-0.3, 0.3) * size,
                                               rng.uniform(-0.1, 0.25) * size), segments=16))
            self.drifting.append((root, drift * rng.uniform(0.7, 1.3)))

    def precipitation(self, kind, n):
        """Rain or snow: a block of drops round the set that falls, loops seamlessly and drifts."""
        if not self.outdoor or n <= 0:
            return
        import bmesh
        H = 9.0
        bm = bmesh.new()
        rng = random.Random(kind)
        W, D = 30.0, 32.0
        for _ in range(n):
            x, y, z = rng.uniform(-W / 2, W / 2), rng.uniform(-D / 2 + 1, D / 2 + 1), rng.uniform(0, H)
            for dz in (0.0, H):                 # the same drops again above: the block loops seamlessly
                if kind == "rain":
                    ln, w = rng.uniform(0.25, 0.4), 0.007
                    for ax in ((w, 0), (0, w)):
                        vs = [bm.verts.new((x - ax[0], y - ax[1], z + dz)), bm.verts.new((x + ax[0], y + ax[1], z + dz)),
                              bm.verts.new((x + ax[0], y + ax[1], z + dz + ln)), bm.verts.new((x - ax[0], y - ax[1], z + dz + ln))]
                        bm.faces.new(vs)
                else:
                    r = rng.uniform(0.015, 0.03)
                    p = [Vector((x, y, z + dz)) + Vector(o) * r for o in
                         ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
                    v = [bm.verts.new(q) for q in p]
                    for a, b, c in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
                        bm.faces.new((v[a], v[b], v[c]))
        if kind == "rain":
            mat = look.plastic(mix("#c9d6e3", self.light.horizon, 0.3), 0.2, 0.0, emission=0.4)
            speed, sway = 8.0, 0.0
        else:
            mat = look.plastic("#ffffff", 0.9, 0.0, emission=0.5)
            speed, sway = 1.1, 0.4
        obj = shapes._object(f"fx.{kind}", bm, mat, None, (0, 0, 0), (0, 0, 0), smooth=False)
        fx_object(obj)
        if kind == "rain" and self.light.wind > 1:
            obj.rotation_euler.x = math.radians(8)
        self.falling.append((obj, H, speed, sway))

    def lightning(self, length, every=6.0):
        """Flashes of lightning: the sun and the sky jump in brightness for a moment."""
        rng = random.Random(11)
        targets = []
        if self.sun is not None:
            targets.append((self.sun.data, "energy", self.sun.data.energy, 25.0))
        targets.append((self.background.inputs["Strength"], "default_value",
                        self.background.inputs["Strength"].default_value, 3.0))
        t = rng.uniform(0.8, min(every, 2.6))      # the first flash comes soon
        flashes = []
        while t < length - 0.3:
            flashes.append(t)
            t += rng.uniform(every * 0.6, every * 1.4)
        for target, prop, base, peak in targets:
            setattr(target, prop, base)
            target.keyframe_insert(prop, frame=1)
            for t0 in flashes:
                f = keys.CLOCK.frame(t0)
                for df, v in ((-1, base), (0, peak), (2, base * 2), (3, peak * 0.7), (6, base)):
                    setattr(target, prop, v)
                    target.keyframe_insert(prop, frame=f + df)

    # -------------------------------------------------------------- animation
    def animate(self, length):
        """Move the weather for the whole scene (called when the scene's length is known)."""
        fps = keys.CLOCK.fps
        last = keys.CLOCK.frame(length) + 1
        for obj, H, speed, sway in self.falling:
            period = max(2, int(round(H / speed * fps)))
            f = 1
            while f <= last:
                obj.location.z = 0.0
                obj.keyframe_insert("location", index=2, frame=f)
                obj.location.z = -H * (period - 1) / period
                obj.keyframe_insert("location", index=2, frame=f + period - 1)
                f += period
            _interp(obj, "location", "LINEAR", index=2, constant_every=2)
            if sway:
                for f in range(1, last + 1, 12):
                    t = keys.CLOCK.seconds(f)
                    obj.location.x = sway * math.sin(t * 0.7) + 0.3 * sway * math.sin(t * 1.9)
                    obj.keyframe_insert("location", index=0, frame=f)
        for root, speed in self.drifting:
            x0 = root.location.x
            root.keyframe_insert("location", index=0, frame=1)
            root.location.x = x0 + speed * length
            root.keyframe_insert("location", index=0, frame=last)
            root.location.x = x0
            _interp(root, "location", "LINEAR", index=0)
        if self.set is not None and self.set.sway:
            self._sway(length, last)
        self.weather.animate(self, self.k, length)

    def _sway(self, length, last):
        """Trees and plants move in the wind (a little even on a still day)."""
        w = self.light.wind
        for i, (obj, k) in enumerate(self.set.sway):
            rng = random.Random(i)
            ph1, ph2 = rng.uniform(0, 6.3), rng.uniform(0, 6.3)
            amp = math.radians(2.2) * w * k
            lean = math.radians(5.0) * max(0.0, w - 0.8) * k
            for f in range(1, last + 1, 4):
                t = keys.CLOCK.seconds(f)
                g = 0.6 + 0.4 * math.sin(t * 0.37 + ph2)      # gusts
                obj.rotation_euler.x = lean * g + amp * g * math.sin(t * 1.7 + ph1)
                obj.rotation_euler.y = amp * 0.6 * g * math.sin(t * 1.3 + ph2)
                obj.keyframe_insert("rotation_euler", index=0, frame=f)
                obj.keyframe_insert("rotation_euler", index=1, frame=f)


def _interp(obj, path, kind, index=None, constant_every=0):
    from ._compat import fcurves
    for fc in fcurves(obj):
        if fc.data_path != path or (index is not None and fc.array_index != index):
            continue
        for i, kp in enumerate(fc.keyframe_points):
            kp.interpolation = kind
            if constant_every and i % constant_every == constant_every - 1:
                kp.interpolation = "CONSTANT"


WEATHER_PARAMS = [Param("time_of_day", "time", default="day", label="Time of day"),
                  Param("weather", "weather", default="clear", label="Weather"),
                  Param("weather_strength", "number", default=1.0, min=0.2, max=2.5, step=0.1, label="How much")]
