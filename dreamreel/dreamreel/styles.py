"""Visual styles: the look of the whole film (or of one scene, for a flashback or a dream).

    # film.toml
    style = "toon"      # toy (the default), toon, anime, clay, paper, storybook, noir, realistic

    # scenes/040_flashback.toml
    style = "noir"      # this scene only

A style changes the materials (cel shading, clay, paper), adds outlines, adjusts the light (noir's
hard key and deep shadows), sets the colour grading and can animate "on twos" like stop-motion.
It never changes the story, the staging or the camera, so trying a different look is one line.

Styles are classes, so a film can add its own:

    class Comic(dr.Style):
        description = "Comic book: bold inks, three flat tones"
        outline, outline_color = 0.016, "#000000"
        bands = [(0.0, 0.45), (0.2, 0.75), (0.5, 1.0)]     # (where, brightness) of the tones
        saturation = 1.3
"""
import bpy

from . import look, timewarp
from .plugins import Plugin


def _bsdf(mat):
    if not mat or not mat.use_nodes or not mat.node_tree:
        return None, None
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None) or \
        next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    return bsdf, out


def _glows(bsdf):
    s = bsdf.inputs.get("Emission Strength")
    return s is not None and s.default_value > 0.001


def _glass(bsdf):
    t = bsdf.inputs.get("Transmission Weight")
    return t is not None and t.default_value > 0.5


def _saturate(rgba, k):
    r, g, b = rgba[:3]
    grey = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return tuple(max(0.0, grey + (c - grey) * k) for c in (r, g, b)) + (rgba[3] if len(rgba) > 3 else 1.0,)


def _base_source(nt, bsdf, saturation=1.0, tint=None):
    """The material's colour as a socket (a texture or attribute if it has one, else an RGB node),
    with saturation and a tint applied."""
    sock = bsdf.inputs["Base Color"]
    if sock.is_linked:
        src = sock.links[0].from_socket
        if saturation != 1.0:
            hs = nt.nodes.new("ShaderNodeHueSaturation")
            hs.inputs["Saturation"].default_value = saturation
            nt.links.new(src, hs.inputs["Color"])
            src = hs.outputs["Color"]
    else:
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = _saturate(tuple(sock.default_value), saturation)
        src = rgb.outputs[0]
    if tint is not None:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(src, mix.inputs[6])
        mix.inputs[7].default_value = (*look.rgb(tint), 1)
        src = mix.outputs[2]
    return src


class Style(Plugin):
    """A look for the film. Override `material` to change each material, `adjust_light` to change
    the light, or the class settings below."""
    kind = "style"
    abstract = True
    view = ("AgX", "AgX - Punchy")      # colour management: view transform and look
    exposure = 0.0
    outline = 0.0                       # outline thickness (metres, for a 60 cm object); 0 for none
    outline_color = "#1c1a1a"
    steps = 1                           # 2: animate on twos (stop-motion), 3: on threes
    bands = None                        # cel shading: [(where, brightness or (r, g, b)), ...]
    saturation = 1.0
    tint = None                         # a colour every material is multiplied by
    edge = 0.08                         # how soft the edge between two tones is
    samples = 48
    exaggeration = 1.0                  # how far acting is pushed (1 = natural; toon styles push it)
    # the camera and the grade
    ambient = 1.0                       # how much bounce light fills indoor shadows (lower: more contrast)
    rim = 0.7                           # a light behind whoever is in each shot, tracing their outline (0: none)
    grade = None                        # (lift, gamma, gain) colours: e.g. teal shadows and warm highlights
    bloom = 0.0                         # a glow round the brightest highlights (0: none; 0.3 subtle)
    lens = 0.0                          # lens distortion and colour fringing at the edges (0.005: subtle)
    motion_blur = 0.0                   # the shutter (0: off; 0.5 a film camera's)
    vignette = 0.0                      # how much the edges of the frame fall off (0: none; 0.3 a lens's)
    separation = 0.0                    # how much less the key light lights the set than the people (0-1)

    @classmethod
    def describe_extra(cls):
        return {"outline": cls.outline > 0, "steps": cls.steps, "cel": bool(cls.bands)}

    # -------------------------------------------------------------- hooks
    def adjust_light(self, light):
        """Change the light before the scene's lights are built."""

    def material(self, mat, scene):
        """Change one material (the default: cel shading if `bands` is set, else only colour)."""
        bsdf, out = _bsdf(mat)
        if bsdf is None or out is None or _glows(bsdf) or _glass(bsdf):
            return
        if self.bands:
            self.cel(mat, bsdf, out, scene)
        elif self.saturation != 1.0 or self.tint:
            src = _base_source(mat.node_tree, bsdf, self.saturation, self.tint)
            mat.node_tree.links.new(src, bsdf.inputs["Base Color"])

    # -------------------------------------------------------------- building blocks
    def cel(self, mat, bsdf, out, scene):
        """Flat tones instead of smooth shading: the light is measured, then snapped to `bands`.
        Night stays dark: the tones are scaled by how bright the scene's light is."""
        nt = mat.node_tree
        bright = _brightness(scene)
        diffuse = nt.nodes.new("ShaderNodeBsdfDiffuse")
        diffuse.inputs["Color"].default_value = (1, 1, 1, 1)
        to_rgb = nt.nodes.new("ShaderNodeShaderToRGB")
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        scale = nt.nodes.new("ShaderNodeMath")
        scale.operation = "MULTIPLY"
        scale.inputs[1].default_value = 1.0 / (2.4 * bright)     # lit surfaces come out near 1
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        cr = ramp.color_ramp
        cr.interpolation = "LINEAR"
        stops = []                       # each tone edge gets a narrow soft step, so it doesn't sparkle
        for i, (pos, val) in enumerate(self.bands):
            color = (val, val, val) if isinstance(val, (int, float)) else look.rgb(val)
            if i:
                stops.append((max(stops[-1][0] + 0.001, pos - self.edge), stops[-1][1]))
            stops.append((pos, color))
        for i, (pos, color) in enumerate(stops):
            e = cr.elements[i] if i < len(cr.elements) else cr.elements.new(pos)
            e.position = pos
            e.color = (*color, 1)
        while len(cr.elements) > len(stops):
            cr.elements.remove(cr.elements[-1])
        nt.links.new(diffuse.outputs[0], to_rgb.inputs[0])
        nt.links.new(to_rgb.outputs["Color"], bw.inputs[0])
        nt.links.new(bw.outputs[0], scale.inputs[0])
        nt.links.new(scale.outputs[0], ramp.inputs["Fac"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(_base_source(nt, bsdf, self.saturation, self.tint), mix.inputs[6])
        nt.links.new(ramp.outputs["Color"], mix.inputs[7])
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Strength"].default_value = min(1.0, max(0.18, bright ** 0.7))
        nt.links.new(mix.outputs[2], emit.inputs["Color"])
        nt.links.new(emit.outputs[0], out.inputs["Surface"])

    def outlines(self, scene):
        """Ink lines round characters, props and scenery (an 'inverted hull': a slightly bigger
        copy of each surface, seen only from inside, in the outline colour)."""
        ink = bpy.data.materials.new("outline")
        ink.use_nodes = True
        nt = ink.node_tree
        bsdf, out = _bsdf(ink)
        nt.nodes.remove(bsdf)
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = (*look.rgb(self.outline_color), 1)
        nt.links.new(emit.outputs[0], out.inputs["Surface"])
        ink.use_backface_culling = True
        if hasattr(ink, "use_backface_culling_shadow"):
            ink.use_backface_culling_shadow = True
        ink.diffuse_color = (*look.rgb(self.outline_color), 1)
        done = set()
        for obj in list(bpy.data.objects):
            if obj.type != "MESH" or obj.get("dr_fx") or obj.name.startswith(("ground", "floor", "fx.", "wall")):
                continue
            size = max(obj.dimensions) if max(obj.dimensions) > 0 else 1.0
            if size > 30 or size < 0.07:      # the ground and the sky; pupils and highlights
                continue
            mesh = obj.data
            if mesh.name not in done:
                if not mesh.materials:
                    mesh.materials.append(look.plastic("grey"))
                mesh.materials.append(ink)
                done.add(mesh.name)
            mod = obj.modifiers.new("outline", "SOLIDIFY")
            mod.thickness = self.outline * min(1.8, max(0.55, size / 0.6))
            mod.offset = 1.0
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.material_offset = len(mesh.materials) - 1
            mod.use_quality_normals = True

    # -------------------------------------------------------------- applying it
    def finish(self, scene):
        for mat in list(bpy.data.materials):
            if mat.name.startswith(("outline", "fog")):
                continue
            self.material(mat, scene)
        if self.outline > 0:
            self.outlines(scene)
        if self.steps > 1:
            for fc in timewarp.all_fcurves():
                if not any(m.type == "STEPPED" for m in fc.modifiers):
                    m = fc.modifiers.new("STEPPED")
                    m.frame_step = self.steps
        if self.separation > 0:
            self.separate(scene)
        self.render_settings(scene.bscene)
        film = getattr(scene, "film", {}) or {}
        if film.get("samples") and hasattr(scene.bscene.eevee, "taa_render_samples"):
            scene.bscene.eevee.taa_render_samples = int(film["samples"])     # fewer: faster, noisier

    def separate(self, scene):
        """Light the people more than the set, the way a film crew flags the key off the walls: the key
        lights only the cast, and a weaker copy of it lights everything else (Blender's light linking)."""
        key = next((o for o in scene.bscene.objects if o.type == "LIGHT" and o.name.split(".")[0] == "key"), None)
        roots = {c.root for c in scene.actors.values()}
        if key is None or not roots:
            return

        def top(o):
            while o.parent is not None:
                o = o.parent
            return o
        people = bpy.data.collections.new("dr people")
        for o in scene.bscene.objects:
            if o.type == "MESH" and top(o) in roots:
                people.objects.link(o)
        if not people.objects:
            bpy.data.collections.remove(people)
            return
        room_key = key.copy()
        room_key.data = key.data.copy()
        room_key.name = "key for the set"
        room_key.data.energy = key.data.energy * (1.0 - self.separation)
        scene.bscene.collection.objects.link(room_key)
        rest = bpy.data.collections.new("dr not people")
        for o in scene.bscene.objects:
            if o.type == "MESH" and top(o) not in roots:
                rest.objects.link(o)
        key.light_linking.receiver_collection = people
        room_key.light_linking.receiver_collection = rest

    def render_settings(self, sc):
        try:
            sc.view_settings.view_transform = self.view[0]
            sc.view_settings.look = self.view[1]
        except TypeError:
            pass
        sc.view_settings.exposure = self.exposure
        if hasattr(sc.eevee, "taa_render_samples"):
            sc.eevee.taa_render_samples = self.samples
        sc.render.use_motion_blur = self.motion_blur > 0
        if self.motion_blur > 0:
            sc.render.motion_blur_shutter = self.motion_blur
        self.compositor(sc)

    def compositor(self, sc):
        """The film's grade after rendering: bloom, the lens, and the colour grade (Blender's compositor)."""
        if not (self.bloom or self.lens or self.grade or self.vignette) or not hasattr(sc, "compositing_node_group"):
            return
        ng = bpy.data.node_groups.new("dreamreel grade", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        src = ng.nodes.new("CompositorNodeRLayers").outputs["Image"]
        if self.bloom:
            g = ng.nodes.new("CompositorNodeGlare")
            g.inputs["Type"].default_value = "Fog Glow"
            g.inputs["Quality"].default_value = "High"
            g.inputs["Highlights Threshold"].default_value = 1.6      # lamps and glints, not a pale wall
            g.inputs["Strength"].default_value = self.bloom
            ng.links.new(src, g.inputs["Image"])
            src = g.outputs["Image"]
        if self.lens:
            d = ng.nodes.new("CompositorNodeLensdist")
            d.inputs["Distortion"].default_value = self.lens
            d.inputs["Dispersion"].default_value = 2 * self.lens
            d.inputs["Fit"].default_value = True
            ng.links.new(src, d.inputs["Image"])
            src = d.outputs["Image"]
        if self.grade:
            cb = ng.nodes.new("CompositorNodeColorBalance")
            cb.inputs["Type"].default_value = "Lift/Gamma/Gain"
            for part, color in zip(("Lift", "Gamma", "Gain"), self.grade):
                cb.inputs[f"Color {part}"].default_value = (*color, 1)
            ng.links.new(src, cb.inputs["Image"])
            src = cb.outputs["Image"]
        if self.vignette:              # a soft ellipse: 1 in the middle, falling to 1 - vignette at the corners
            frame = ng.nodes.new("ShaderNodeMath")     # zeros the size of the picture: masks with no image
            frame.operation = "MULTIPLY"               # input come out as a single value
            frame.inputs[1].default_value = 0.0
            ng.links.new(src, frame.inputs[0])
            mask = ng.nodes.new("CompositorNodeEllipseMask")
            mask.inputs["Size"].default_value = (0.95, 0.95)
            ng.links.new(frame.outputs[0], mask.inputs["Mask"])
            blur = ng.nodes.new("CompositorNodeBlur")
            blur.inputs["Size"].default_value = (sc.render.resolution_x * 0.12, sc.render.resolution_x * 0.12)
            ng.links.new(mask.outputs["Mask"], blur.inputs["Image"])
            fall = ng.nodes.new("ShaderNodeMath")
            fall.operation = "MULTIPLY_ADD"
            fall.inputs[1].default_value = self.vignette
            fall.inputs[2].default_value = 1.0 - self.vignette
            ng.links.new(blur.outputs["Image"], fall.inputs[0])
            mul = ng.nodes.new("ShaderNodeMix")
            mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
            ins = {i.identifier: i for i in mul.inputs}       # several sockets share a name: go by identifier
            ins["Factor_Float"].default_value = 1.0
            ng.links.new(src, ins["A_Color"])
            ng.links.new(fall.outputs[0], ins["B_Color"])
            src = next(o for o in mul.outputs if o.identifier == "Result_Color")
        ng.links.new(src, ng.nodes.new("NodeGroupOutput").inputs[0])
        sc.compositing_node_group = ng
        sc.render.use_compositing = True

    def previz(self, sc):
        """The fast previz shows outlines too."""
        if self.outline > 0:
            sc.display.shading.show_backface_culling = True


def _brightness(scene):
    """Roughly how bright the scene's light is (1 = daylight), for cel shading."""
    env = getattr(scene, "environment", None)
    if env is None:
        return 1.0
    L = env.light
    if env.outdoor:
        b = (L.sun_energy / 3.2 + 0.35 * L.sky_strength * L.fill) / 1.3
    else:
        b = 0.15 + 0.85 * L.room * (0.5 + 0.5 * L.key)
    return max(0.12, min(1.5, b))


# ---------------------------------------------------------------------- the styles
class Toy(Style):
    description = "Soft vinyl toys under warm light (the default)"


class Toon(Style):
    description = "Cartoon: flat colours, two tones and bold outlines"
    exaggeration = 1.35
    samples = 64
    view = ("Standard", "None")
    outline = 0.012
    bands = [(0.0, (0.52, 0.5, 0.6)), (0.5, 1.0)]
    saturation = 1.15


class Anime(Style):
    description = "Anime: crisp cel shading, cool violet shadows, fine lines, vivid colour"
    exaggeration = 1.2
    samples = 64
    view = ("Standard", "None")
    outline, outline_color = 0.007, "#2a2238"
    bands = [(0.0, (0.62, 0.58, 0.8)), (0.45, 1.0), (1.7, (1.1, 1.08, 1.04))]
    saturation = 1.25

    def adjust_light(self, light):
        from .environment import mix
        light.zenith = mix(light.zenith, "#3d8fe0", 0.4)


class Clay(Style):
    description = "Claymation: soft matte clay with thumbprints, animated on twos"
    exaggeration = 1.15
    view = ("AgX", "AgX - Punchy")
    steps = 2
    saturation = 1.2

    def material(self, mat, scene):
        bsdf, out = _bsdf(mat)
        if bsdf is None or _glows(bsdf) or _glass(bsdf):
            return
        nt = mat.node_tree
        for name, v in (("Roughness", 0.78), ("Coat Weight", 0.0), ("Subsurface Weight", 0.08),
                        ("Specular IOR Level", 0.3)):
            if bsdf.inputs.get(name) is not None:
                bsdf.inputs[name].default_value = v
        coord = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 14.0
        noise.inputs["Detail"].default_value = 3.0
        prints = nt.nodes.new("ShaderNodeTexVoronoi")
        prints.inputs["Scale"].default_value = 7.0
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.6
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
        nt.links.new(coord.outputs["Object"], prints.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], add.inputs[0])
        nt.links.new(prints.outputs["Distance"], add.inputs[1])
        nt.links.new(add.outputs[0], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        if self.saturation != 1.0:
            nt.links.new(_base_source(nt, bsdf, self.saturation), bsdf.inputs["Base Color"])

    def adjust_light(self, light):
        light.sun_softness = max(light.sun_softness, 14)


class Paper(Style):
    description = "Paper cut-out: flat card shapes with white edges, animated on threes"
    exaggeration = 1.25
    samples = 64
    view = ("Standard", "None")
    outline, outline_color = 0.01, "#f7f3ea"
    bands = [(0.0, 0.76), (0.42, 1.0)]
    steps = 3
    saturation = 0.95

    def cel(self, mat, bsdf, out, scene):
        super().cel(mat, bsdf, out, scene)
        nt = mat.node_tree
        emit = next(n for n in nt.nodes if n.type == "EMISSION")
        src = emit.inputs["Color"].links[0].from_socket
        grain = nt.nodes.new("ShaderNodeTexNoise")
        grain.inputs["Scale"].default_value = 90.0
        grain.inputs["Detail"].default_value = 6.0
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 0.12
        nt.links.new(src, mix.inputs[6])
        nt.links.new(grain.outputs["Color"], mix.inputs[7])
        nt.links.new(mix.outputs[2], emit.inputs["Color"])


class Storybook(Style):
    description = "Storybook: soft pastel tones, gentle brown lines, a warm painted feel"
    exaggeration = 1.1
    samples = 64
    view = ("Standard", "None")
    outline, outline_color = 0.005, "#6b4a35"
    bands = [(0.0, (0.66, 0.6, 0.66)), (0.3, (0.86, 0.82, 0.8)), (0.75, (1.0, 0.98, 0.93))]
    saturation = 0.78
    tint = "#fff6e6"


class Noir(Style):
    description = "Film noir: black and white, a low hard side light, deep shadows"
    exaggeration = 0.9
    view = ("AgX", "AgX - Greyscale")
    exposure = 0.5
    samples = 96
    ambient = 0.35
    rim = 1.2                     # noir lives on rim light
    bloom = 0.25                  # and on highlights that bleed

    def adjust_light(self, light):
        light.key = 1.6
        light.fill = 0.14
        light.key_position = (-3.6, -3.4, 2.0)        # low, hard and from the side
        light.sky_strength *= 0.3
        light.sun_softness = 1.5
        light.sun_elevation = min(light.sun_elevation, 22)
        light.sun_azimuth = 255
        light.sun_energy *= 1.3
        light.practicals *= 1.5

    def separate(self, scene):
        """Light the people more than the set, the way a film crew flags the key off the walls: the key
        lights only the cast, and a weaker copy of it lights everything else (Blender's light linking)."""
        key = next((o for o in scene.bscene.objects if o.type == "LIGHT" and o.name.split(".")[0] == "key"), None)
        roots = {c.root for c in scene.actors.values()}
        if key is None or not roots:
            return

        def top(o):
            while o.parent is not None:
                o = o.parent
            return o
        people = bpy.data.collections.new("dr people")
        for o in scene.bscene.objects:
            if o.type == "MESH" and top(o) in roots:
                people.objects.link(o)
        if not people.objects:
            bpy.data.collections.remove(people)
            return
        room_key = key.copy()
        room_key.data = key.data.copy()
        room_key.name = "key for the set"
        room_key.data.energy = key.data.energy * (1.0 - self.separation)
        scene.bscene.collection.objects.link(room_key)
        rest = bpy.data.collections.new("dr not people")
        for o in scene.bscene.objects:
            if o.type == "MESH" and top(o) not in roots:
                rest.objects.link(o)
        key.light_linking.receiver_collection = people
        room_key.light_linking.receiver_collection = rest

    def render_settings(self, sc):
        super().render_settings(sc)
        try:
            sc.view_settings.look = "AgX - Greyscale"
        except TypeError:
            pass


class Realistic(Style):
    description = "Real materials and light: photo-scanned surfaces on everything, real skies (see materials.py)"
    exaggeration = 0.8
    view = ("AgX", "AgX - Medium High Contrast")
    samples = 96
    ambient = 0.75
    rim = 1.0
    grade = ((0.92, 0.96, 1.0), (1.0, 1.0, 1.0), (1.05, 1.02, 0.95))   # teal shadows, warm highlights
    bloom = 0.3
    lens = 0.004
    motion_blur = 0.5
    vignette = 0.3
    separation = 0.45

    def adjust_light(self, light):
        light.fill = 0.7              # shadows that stay shadows: the key shapes faces

    def finish(self, scene):
        from . import materials
        materials.soften(scene)
        materials.realise_scene(scene)
        materials.real_sky(scene)
        super().finish(scene)

    def material(self, mat, scene):
        """Anything materials.py didn't make real: less plastic, a fine grain."""
        bsdf, out = _bsdf(mat)
        if bsdf is None or _glows(bsdf) or _glass(bsdf) or mat.get("dr_real"):
            return
        nt = mat.node_tree
        r = bsdf.inputs["Roughness"].default_value
        for name, v in (("Roughness", min(0.85, r + 0.15)), ("Coat Weight", 0.0), ("Specular IOR Level", 0.5)):
            if bsdf.inputs.get(name) is not None:
                bsdf.inputs[name].default_value = v
        coord = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 60.0
        noise.inputs["Detail"].default_value = 8.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.005
        nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
