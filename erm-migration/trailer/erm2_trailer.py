"""
ERM 2.0 trailer for ERM users (about 1:48, 16 shots), built entirely in Blender.

Follows erm-migration/docs/trailer-storyboard: ERM today -> Your ERM -> Until now -> The turn ->
The reveal -> Nothing lost -> 11 new -> seven feature shots on a card carousel -> In their words -> End card.

Requirements
  Blender 4.2 or newer (EEVEE). Tested API paths cover 4.2 to 5.x; older versions may need small changes.
  The textures/ folder next to this script (mock app screens). Real screenshots take priority when present:
    slate_<name>.png  for the wall in shots 2 and 3 (heat, table, onepager, tracker)
    react_<name>.png  for the feature cards (search, share, slide, filters, onepager_pick, report, locked, toast)
    logo_skywise.png, logo_clairvoyant.png  team logos on the end card (transparent PNG; names show until added)
                      logo_skywise.png is in place, rendered from logos/skywise.svg (Blender can't load SVG as a texture)
  See textures/SCREENSHOTS.md for what to capture. Use sample or test data only.

Run
  Build the scene and open it:          blender -P erm2_trailer.py
  Build and render the MP4 (headless):  blender -b -P erm2_trailer.py -- --render
  Quick low-res preview render:         blender -b -P erm2_trailer.py -- --render --preview
  Options after "--":
    --assets DIR    folder with the textures (default: textures/ next to this script)
    --music FILE    licensed music track, added to the timeline (cuts are timed for ~120 BPM)
    --font FILE     .ttf/.otf for all titles (default: Blender's built-in font)
    --out PATH      output file (default: render/erm2_trailer.mp4 next to this script)
    --save FILE     also save the built scene as a .blend

Everything is on the timeline: open the .blend to retime shots, change captions or swap textures.
"""

import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector

# ----------------------------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------------------------
FPS = 24
RES = (1920, 1080)

# Shot timing in seconds, from the storyboard.
SHOTS = {
    1: (0, 7), 2: (7, 14), 3: (14, 21), 4: (21, 25), 5: (25, 31), 6: (31, 38), 7: (38, 43),
    8: (43, 50), 9: (50, 57), 10: (57, 64), 11: (64, 71), 12: (71, 77), 13: (77, 83), 14: (83, 89),
    15: (89, 99), 16: (99, 108),
}

# Team logos on the end card: textures/logo_skywise.png and textures/logo_clairvoyant.png.
LOGO_H = 0.2         # logo height on screen (HUD units; the frame is about 2.9 tall)
LOGO_PLATE = None    # e.g. '#f8fafc' to put a light card behind dark logos

PINK = '#ec4f8f'
INDIGO = '#6366f1'
CYAN = '#7dd3fc'
GREEN = '#22c55e'
WHITE = '#f8fafc'
MUTED = '#94a3b8'
NAVY = '#070b16'

CAPTIONS = {
    2: ('Every quarter, your risk reporting runs through ERM.', 'YOUR ERM'),
    3: ('Waiting for tabs to load. Hunting for the right dashboard.', 'UNTIL NOW'),
    6: ('Every feature you rely on, carried over and checked one by one.', 'NOTHING LOST'),
}
# Carousel cards: (texture, start s, end s, caption, eyebrow)
CARDS = [
    ('search', 43, 50, 'Find any dashboard in seconds.', 'NEW · DASHBOARD SWITCHER'),
    ('share', 50, 53.5, 'Share a link to any tab.', 'NEW · LINK TO ANY TAB'),
    ('slide', 53.5, 57, 'Present in slideshow mode.', 'NEW · SLIDESHOW MODE'),
    ('filters', 57, 64, 'Filter the way you think. Columns remember your width.', 'NEW · FILTERS AND COLUMNS'),
    ('onepager_pick', 64, 71, 'A new one-pager layout. Pick risks in one click.', 'NEW · ONE-PAGER'),
    ('report', 71, 77, 'Reports with classification and an optional cover page.', 'NEW · REPORTS'),
    ('locked', 77, 83, 'Released dashboard? Update permissions without unlocking it.', 'NEW · LOCKED VERSIONS'),
    ('toast', 83, 89, 'Every save confirmed. Every list up to date.', 'BETTER EVERY DAY'),
]
NEW_FEATURES = ['Dashboard switcher', 'Link to any tab', 'Slideshow mode', 'Criticality-differs filter',
                'Category filters', 'Columns that remember', 'New one-pager layout', 'Selection shortcuts',
                'Risks by ID or title', 'Report classification and cover', 'Permissions on locked versions']
SITES = [('Blagnac', -1.2, -0.4, 271), ('Hamburg', 1.4, 2.6, 205), ('Saint-Martin', -1.9, 0.5, 43),
         ('Broughton', -3.0, 3.0, 32), ('Filton', -3.6, 2.1, 26), ('Getafe', -3.6, -1.9, 25),
         ('Mirabel', -8.3, 1.6, 12), ('Bangalore', 8.6, -3.0, 7)]

# ----------------------------------------------------------------------------------------------
# Arguments
# ----------------------------------------------------------------------------------------------
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = bpy.path.abspath('//') or os.getcwd()
if not os.path.isdir(HERE):  # run from Blender's text editor
    HERE = bpy.path.abspath('//') or os.getcwd()
ASSETS = arg('--assets', os.path.join(HERE, 'textures'))
MUSIC = arg('--music')
FONT_PATH = arg('--font')
OUT = arg('--out', os.path.join(HERE, 'render', 'erm2_trailer.mp4'))
DO_RENDER = '--render' in argv
PREVIEW = '--preview' in argv
SAVE = arg('--save')

random.seed(11)


def F(sec):
    """Seconds to frame number (frame 1 = 0 s)."""
    return int(round(sec * FPS)) + 1


def S0(n):
    return F(SHOTS[n][0])


def S1(n):
    return F(SHOTS[n][1])


END = S1(16)

# ----------------------------------------------------------------------------------------------
# Scene reset and keyframe helpers
# ----------------------------------------------------------------------------------------------
scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(block):
        if item.users == 0:
            block.remove(item)
for coll in list(scene.collection.children):
    scene.collection.children.unlink(coll)

PREF = bpy.context.preferences.edit
_old_interp = PREF.keyframe_new_interpolation_type


def kf(target, path, frame, value, interp='BEZIER'):
    """Set a property and insert a keyframe whose segment to the next key uses `interp`."""
    PREF.keyframe_new_interpolation_type = interp
    setattr(target, path, value)
    target.keyframe_insert(path, frame=frame)


def hex_rgb(h):
    h = h.lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


def link(ob, coll):
    coll.objects.link(ob)
    return ob


# ----------------------------------------------------------------------------------------------
# Materials (emission based, with an animatable alpha)
# ----------------------------------------------------------------------------------------------
def _blended(mat):
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'BLENDED'
    if hasattr(mat, 'blend_method'):
        try:
            mat.blend_method = 'BLEND'
        except TypeError:
            pass
    if hasattr(mat, 'use_backface_culling'):
        mat.use_backface_culling = False


class Mat:
    """Emission material. `.alpha` and `.strength` are sockets you can keyframe; `.color` too."""

    def __init__(self, name, color=WHITE, strength=1.0, alpha=1.0, image=None, blend=True):
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        nt = self.mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
        em.inputs['Color'].default_value = (*hex_rgb(color), 1)
        if image is not None:
            tex = nt.nodes.new('ShaderNodeTexImage')
            tex.image = image
            tex.interpolation = 'Cubic'
            nt.links.new(tex.outputs['Color'], em.inputs['Color'])
        em.inputs['Strength'].default_value = strength
        mix.inputs[0].default_value = alpha
        if blend:
            _blended(self.mat)
        self.alpha = mix.inputs[0]
        self.strength = em.inputs['Strength']
        self.color = em.inputs['Color']


def fade(sock, f_in, f_out, ramp=10, peak=1.0):
    """Animate an alpha/strength socket: 0 -> peak over `ramp` frames, hold, peak -> 0 at f_out."""
    kf(sock, 'default_value', f_in, 0.0)
    kf(sock, 'default_value', f_in + ramp, peak)
    if f_out is not None:
        kf(sock, 'default_value', f_out - ramp, peak)
        kf(sock, 'default_value', f_out, 0.0)


def load_image(*names):
    """First image found among `names` (.png or .jpg in ASSETS), e.g. a real screenshot before the mock-up."""
    for name in names:
        for ext in ('.png', '.jpg', '.jpeg'):
            path = os.path.join(ASSETS, name + ext)
            if os.path.exists(path):
                return bpy.data.images.load(path, check_existing=True)
    print(f'[erm2] no texture for {names}, using a flat card')
    return None


# ----------------------------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------------------------
def mesh_object(name, bm, coll, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat.mat)
    return link(ob, coll)


def plane(name, w, h, coll, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = co
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat.mat)
    return link(ob, coll)


def sphere(name, r, coll, mat, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    ob = mesh_object(name, bm, coll, mat)
    ob.location = loc
    return ob


def cube(name, size, coll, mat, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = mesh_object(name, bm, coll, mat)
    ob.location = loc
    return ob


def torus(name, R, r, coll, mat, seg=128, ring=12):
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(ring):
            b = 2 * math.pi * j / ring
            row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        verts.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % ring], verts[i][(j + 1) % ring]))
    return mesh_object(name, bm, coll, mat)


def dust(name, count, spread, coll, mat, radius=0.03, center=(0, 0, 0)):
    """Many tiny spheres merged into one mesh (stars, user dots, particles)."""
    bm = bmesh.new()
    for _ in range(count):
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius * random.uniform(0.6, 1.4))
        off = Vector((random.uniform(-1, 1) * spread[0], random.uniform(-1, 1) * spread[1], random.uniform(-1, 1) * spread[2]))
        bmesh.ops.translate(bm, vec=off, verts=res['verts'])
    ob = mesh_object(name, bm, coll, mat)
    ob.location = center  # origin at the cloud's centre, so scaling and drifting stay in place
    return ob


def curve_path(name, points, coll, mat, bevel=0.02, cyclic=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
    if hasattr(cu, 'bevel_factor_mapping_end'):
        cu.bevel_factor_mapping_end = 'SPLINE'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(points) - 1)
    for bp, co in zip(sp.bezier_points, points):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(mat.mat)
    return link(ob, coll)


FONT = bpy.data.fonts.load(FONT_PATH) if FONT_PATH and os.path.exists(FONT_PATH) else None


def text(body, size, mat, coll, loc=(0, 0, 0), align='CENTER', extrude=0.0, parent=None, upright=True, spacing=1.0):
    """Text object. upright=True stands it up facing -Y (towards the cameras); HUD text passes False."""
    cu = bpy.data.curves.new('txt', 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.space_character = spacing
    if FONT:
        cu.font = FONT
    ob = bpy.data.objects.new('txt_' + body[:16], cu)
    ob.data.materials.append(mat.mat)
    link(ob, coll)
    if parent:
        ob.parent = parent
    if upright:
        ob.rotation_euler = (math.radians(90), 0, 0)
    ob.location = loc
    return ob


def pop(ob, f, base=1.0, dur=10, overshoot=1.12, out=None, out_dur=8):
    """Scale-in with a small overshoot; optional scale-out at `out`."""
    kf(ob, 'scale', f, Vector((0.001,) * 3))
    kf(ob, 'scale', f + int(dur * 0.7), Vector((base * overshoot,) * 3))
    kf(ob, 'scale', f + dur, Vector((base,) * 3))
    if out:
        kf(ob, 'scale', out - out_dur, Vector((base,) * 3))
        kf(ob, 'scale', out, Vector((0.001,) * 3))


def window(ob, f_in, f_out, base=1.0):
    """Hard on/off visibility via constant-interpolated scale (for counters)."""
    kf(ob, 'scale', 1, Vector((0.001,) * 3), 'CONSTANT')
    kf(ob, 'scale', max(f_in, 2), Vector((base,) * 3), 'CONSTANT')
    kf(ob, 'scale', f_out, Vector((0.001,) * 3), 'CONSTANT')


# ----------------------------------------------------------------------------------------------
# World, camera, HUD (captions, letterbox, fades)
# ----------------------------------------------------------------------------------------------
world = scene.world or bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background') or world.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (*hex_rgb(NAVY), 1)
bg.inputs['Strength'].default_value = 1.0

C_CAM = collection('Camera and titles')
cam_data = bpy.data.cameras.new('Camera')
cam_data.lens = 35
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.sensor_width = 36
cam = link(bpy.data.objects.new('Camera', cam_data), C_CAM)
scene.camera = cam

cam_data.clip_start = 0.02
# Titles, letterbox, fades and flashes live on a small rig 0.6 units in front of the lens (laid out in a
# 5-unit space scaled by 0.12), so scene objects never cover them, even when the camera flies close.
hud_root = link(bpy.data.objects.new('HUD', None), C_CAM)
hud_root.parent = cam
hud_root.scale = (0.12, 0.12, 0.12)
HUD_D = 5.0
HUD_W = HUD_D * 36 / 35
HUD_H = HUD_W * RES[1] / RES[0]


def hud(body, size, y, color=WHITE, f_in=None, f_out=None, x=0.0, spacing=1.0, ramp=10, z=0.0):
    m = Mat('hud', color, 1.0, 0.0)
    ob = text(body, size, m, C_CAM, loc=(x, y, -HUD_D + z), parent=hud_root, upright=False, spacing=spacing)
    if f_in is not None:
        fade(m.alpha, f_in, f_out, ramp)
        kf(ob, 'location', f_in, Vector((x, y - 0.04, -HUD_D + z)))
        kf(ob, 'location', f_in + ramp + 6, Vector((x, y, -HUD_D + z)))
    return ob, m


def hud_logo(names, fallback, h, x, y, f_in, f_out, plate=None):
    """A team logo on the HUD: the first image found among `names`, `h` tall, aspect from the file.
    Transparent PNG/SVG-export is best. `plate` puts a rounded-off card behind it (for dark logos).
    Without a file it falls back to the team name as a wordmark, so the credit still reads."""
    img = load_image(*names)
    if img is None:
        ob, m = hud(fallback, h * 0.42, y - h * 0.15, WHITE, f_in, f_out, x=x, spacing=1.5)
        return ob
    w = h * img.size[0] / max(1, img.size[1])
    m = Mat('logo ' + fallback, WHITE, 1.0, 0.0, image=img)
    nt = m.mat.node_tree
    tex = next(n for n in nt.nodes if n.type == 'TEX_IMAGE')
    mix = next(n for n in nt.nodes if n.type == 'MIX_SHADER')
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 0.0
    nt.links.new(tex.outputs['Alpha'], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    m.alpha = mul.inputs[1]  # fade the logo while keeping its own transparency
    ob = plane('logo ' + fallback, w, h, C_CAM, m)
    ob.parent = hud_root
    ob.location = (x, y, -HUD_D + 0.005)
    fade(m.alpha, f_in, f_out, 12)
    if plate:
        pm = Mat('logo plate', plate, 1.0, 0.0)
        pl = plane('logo plate ' + fallback, w + h * 0.5, h * 1.5, C_CAM, pm)
        pl.parent = hud_root
        pl.location = (x, y, -HUD_D + 0.004)
        fade(pm.alpha, f_in, f_out, 12)
    kf(ob, 'location', f_in, Vector((x, y - 0.04, -HUD_D + 0.005)))
    kf(ob, 'location', f_in + 18, Vector((x, y, -HUD_D + 0.005)))
    return ob


def caption(main, eyebrow, f_in, f_out):
    hud(main, 0.135, -HUD_H / 2 + 0.42, WHITE, f_in, f_out)
    if eyebrow:
        hud(eyebrow, 0.06, -HUD_H / 2 + 0.25, '#f9a8d4', f_in + 6, f_out, spacing=1.4)


# Letterbox bars and full-frame fade/flash cards, all parented to the camera.
bar_h = HUD_H * 60 / 900 * 1.02
for sign in (1, -1):
    b = plane('letterbox', HUD_W * 1.2, bar_h, C_CAM, Mat('bar', '#000000', 1.0, 1.0))
    b.parent = hud_root
    b.location = (0, sign * (HUD_H / 2 - bar_h / 2 + 0.001), -HUD_D + 0.02)
black = Mat('fade to black', '#000000', 1.0, 0.0)
fader = plane('fader', HUD_W * 1.2, HUD_H * 1.2, C_CAM, black)
fader.parent = hud_root
fader.location = (0, 0, -HUD_D + 0.01)


def dip(f_mid, half=6):
    kf(black.alpha, 'default_value', f_mid - half, 0.0)
    kf(black.alpha, 'default_value', f_mid, 1.0)
    kf(black.alpha, 'default_value', f_mid + half, 0.0)


def flash(f_mid, color=WHITE, peak=0.9, half=6):
    m = Mat('flash', color, 2.0, 0.0)
    p = plane('flash', HUD_W * 1.2, HUD_H * 1.2, C_CAM, m)
    p.parent = hud_root
    p.location = (0, 0, -HUD_D + 0.015)
    kf(m.alpha, 'default_value', f_mid - half, 0.0)
    kf(m.alpha, 'default_value', f_mid, peak)
    kf(m.alpha, 'default_value', f_mid + half * 2, 0.0)


def aim(loc, target):
    d = Vector(target) - Vector(loc)
    return d.to_track_quat('-Z', 'Y').to_euler()


def cam_key(frame, loc, target, interp='BEZIER'):
    kf(cam, 'location', frame, Vector(loc), interp)
    kf(cam, 'rotation_euler', frame, aim(loc, target), interp)


def cam_shot(n, keys):
    """keys: list of (fraction 0..1, location, target) relative to the shot; the shot ends on a cut."""
    a, b = S0(n), S1(n) - 1
    for i, (t, loc, tgt) in enumerate(keys):
        frame = round(a + (b - a) * t)
        last = i == len(keys) - 1
        cam_key(frame, loc, tgt, 'CONSTANT' if last else 'BEZIER')


def O(n):
    """Each shot is built at its own spot along X, so a camera jump is a cut."""
    return Vector((n * 400.0, 0, 0))


# ----------------------------------------------------------------------------------------------
# Shot 1 · ERM today: sites, people, connections
# ----------------------------------------------------------------------------------------------
def shot_1():
    c, o, a = collection('01 ERM today'), O(1), S0(1)
    site_mat = Mat('site', PINK, 6.0)
    arc_mat = Mat('arc', '#f9a8d4', 3.0)
    dot_mat = Mat('people', CYAN, 3.0)
    for k, (_, x, z, _) in enumerate(SITES[:3]):
        d = dust(f'people {k}', 320 if k < 2 else 120, (2.2, 0.6, 1.6), c, dot_mat, 0.03, o + Vector((x, 0.3, z)))
        pop(d, a + 18 + k * 6, dur=20, overshoot=1.03)
    bx, bz = SITES[0][1], SITES[0][2]
    for k, (name, x, z, users) in enumerate(SITES):
        s = sphere('site ' + name, 0.12 + math.sqrt(users) * 0.035, c, site_mat, o + Vector((x, 0, z)))
        pop(s, a + 6 + k * 4)
        lm = Mat('label', WHITE, 1.0, 0.0)
        text(f'{name} · {users}', 0.22, lm, c, o + Vector((x, -0.3, z + 0.6)))
        fade(lm.alpha, a + 40 + k * 4, S1(1) - 20)
        if name != 'Blagnac':
            mid = o + Vector(((bx + x) / 2, -1.0, (bz + z) / 2 + 1.5))
            arc = curve_path('arc ' + name, [o + Vector((bx, 0, bz)), mid, o + Vector((x, 0, z))], c, arc_mat, 0.018)
            kf(arc.data, 'bevel_factor_end', a + 20 + k * 5, 0.0)
            kf(arc.data, 'bevel_factor_end', a + 60 + k * 5, 1.0)
    # Headline numbers count up (stepped text swaps)
    counter([0, 120, 260, 410, 560, 700, 830, 892], a + 12, a + 60, '{} colleagues', -1.85, S1(1) - 18, size=0.15)
    counter([0, 300, 700, 1100, 1400, 1600], a + 30, a + 72, '{:,}+ dashboards', 0.0, S1(1) - 18, size=0.15)
    counter([1, 2, 3, 4, 5, 6], a + 48, a + 84, '{} countries', 1.85, S1(1) - 18, size=0.15)
    hud('ERM TODAY', 0.06, -HUD_H / 2 + 0.25, '#f9a8d4', a + 20, S1(1) - 12, spacing=1.4)
    # Camera: slow push, then a fast dive into Blagnac (match cut to the wall of dashboards)
    cam_shot(1, [(0.0, o + Vector((0, -22, 0.5)), o + Vector((0, 0, 0.4))),
                 (0.78, o + Vector((0, -16, 0.4)), o + Vector((0, 0, 0.3))),
                 (1.0, o + Vector((bx, -1.2, bz)), o + Vector((bx, 0, bz)))])
    flash(S1(1) - 2, WHITE, 0.95, 5)


def counter(values, f_start, f_end, fmt, x, f_out, size=0.15, y=None, color=WHITE):
    """A number that counts up: one text per value, each shown for its own slice of time."""
    y = HUD_H / 2 - 0.42 if y is None else y
    step = (f_end - f_start) / max(1, len(values) - 1)
    for i, v in enumerate(values):
        ob, m = hud(fmt.format(v), size, y, color, x=x)
        m.alpha.default_value = 1.0
        f_in = round(f_start + i * step)
        f_off = round(f_start + (i + 1) * step) if i < len(values) - 1 else f_out
        window(ob, f_in, f_off)
    return values[-1]


# ----------------------------------------------------------------------------------------------
# Shots 2 and 3 · the wall of dashboards, then the wait
# ----------------------------------------------------------------------------------------------
WALL_TEX = ['heat', 'table', 'onepager', 'tracker']


def wall(n, dim):
    c, o, a = collection(f'{n:02d} wall'), O(n), S0(n)
    centre = o + Vector((0, -9, 0))
    for r in range(3):
        for k in range(5):
            name = WALL_TEX[(r * 5 + k) % 4]
            img = load_image('slate_' + name, name)  # the app users know today, if you add Slate screenshots
            m = Mat('screen', '#9aa4b2', 0.28 if dim else 1.0, 1.0, image=img, blend=False)
            ang = (k - 2) * 0.32
            pos = centre + Vector((11 * math.sin(ang), 11 * math.cos(ang), (1 - r) * 2.4))
            p = plane('screen', 3.2, 2.0, c, m)
            p.location = pos
            p.rotation_euler = (math.radians(90), 0, -ang)
            glow = plane('frame', 3.32, 2.12, c, Mat('frame', '#334155' if dim else PINK, 1.5, 0.55))
            glow.location = pos + (pos - centre).normalized() * 0.02
            glow.rotation_euler = p.rotation_euler
            if not dim:
                pop(p, a + 2 + (r * 5 + k) * 2, dur=12, overshoot=1.02)
                pop(glow, a + 2 + (r * 5 + k) * 2, dur=12, overshoot=1.02)
    return centre, c


def shot_2():
    centre, _ = wall(2, False)
    cam_shot(2, [(0.0, centre + Vector((0, -1.0, 0.3)), centre + Vector((0, 11, 0))),
                 (1.0, centre + Vector((0, 1.8, 0.2)), centre + Vector((0, 11, 0)))])
    caption(*CAPTIONS[2], S0(2) + 18, S1(2) - 6)


def shot_3():
    centre, c = wall(3, True)
    a = S0(3)
    pivot = link(bpy.data.objects.new('spinner pivot', None), c)
    pivot.location = centre + Vector((0, 7.0, 0))
    pivot.rotation_euler = (math.radians(90), 0, 0)
    ring_pts = [(math.cos(t) * 1.1, math.sin(t) * 1.1, 0) for t in [i * math.pi / 2 for i in range(4)]]
    spin = curve_path('spinner', ring_pts, c, Mat('spinner', MUTED, 1.5), 0.07, cyclic=True)
    spin.data.bevel_factor_end = 0.7
    spin.parent = pivot
    kf(spin, 'rotation_euler', a, Vector((0, 0, 0)), 'LINEAR')
    kf(spin, 'rotation_euler', S1(3), Vector((0, 0, -math.radians(360 * 3.5))), 'LINEAR')
    cam_shot(3, [(0.0, centre + Vector((0, 1.0, 0.2)), centre + Vector((0, 11, 0))),
                 (1.0, centre + Vector((0, 1.3, 0.2)), centre + Vector((0, 11, 0)))])
    caption(*CAPTIONS[3], a + 12, S1(3) - 2)


# ----------------------------------------------------------------------------------------------
# Shot 4 · the turn (black, two lines)
# ----------------------------------------------------------------------------------------------
def shot_4():
    o, a = O(4), S0(4)
    cam_shot(4, [(0.0, o + Vector((0, -10, 0)), o), (1.0, o + Vector((0, -10, 0)), o)])
    hud('So we rebuilt it.', 0.3, 0.2, WHITE, a + 8, S1(4) - 2, ramp=8)
    hud('From the ground up.', 0.3, -0.25, PINK, a + 34, S1(4) - 2, ramp=8)


# ----------------------------------------------------------------------------------------------
# Rings, stars and the logo (shots 5 and 16)
# ----------------------------------------------------------------------------------------------
def rings_and_logo(n, coll, tagline=None):
    o, a = O(n), S0(n)
    r1 = torus('ring pink', 4.6, 0.06, coll, Mat('ring', PINK, 6.0))
    r2 = torus('ring indigo', 5.4, 0.03, coll, Mat('ring', INDIGO, 6.0))
    for r, rot, sc in ((r1, (1.35, 0.15, 0), 1.25), (r2, (1.45, -0.2, 0.25), 1.2)):
        r.location = o
        r.rotation_euler = (math.pi / 2 - rot[0], rot[1], rot[2])  # nearly edge-on, seen as a wide ellipse
        pop(r, a + 4, base=sc, dur=18, overshoot=1.08)
        kf(r, 'rotation_euler', a, Vector(r.rotation_euler), 'LINEAR')
        kf(r, 'rotation_euler', S1(n), Vector(r.rotation_euler) + Vector((math.radians(6), math.radians(18), 0)), 'LINEAR')
    stars = dust('stars', 900, (20, 14, 11), coll, Mat('stars', '#cbd5e1', 2.0), 0.03, o + Vector((0, 14, 0)))
    base = stars.location.copy()
    kf(stars, 'location', a, base, 'LINEAR')
    kf(stars, 'location', S1(n), base + Vector((0, -6, 0)), 'LINEAR')  # drift towards the camera
    logo_w = Mat('logo', WHITE, 3.0, 0.0)
    logo_p = Mat('logo 2.0', PINK, 4.0, 0.0)
    erm = text('ERM', 1.9, logo_w, coll, o + Vector((-1.35, -1.0, 0.1)), extrude=0.06)
    two = text('2.0', 1.9, logo_p, coll, o + Vector((2.15, -1.0, 0.1)), extrude=0.06)
    f_logo = a + 20
    fade(logo_w.alpha, f_logo, None, 12)
    fade(logo_p.alpha, f_logo + 6, None, 12)
    pop(erm, f_logo, dur=16, overshoot=1.06)
    pop(two, f_logo + 6, dur=16, overshoot=1.1)
    if tagline:
        hud(tagline[0], 0.13, -0.95, '#e2e8f0', a + 48, END - 6)
        hud(tagline[1], 0.07, -1.18, '#f9a8d4', a + 66, END - 6, spacing=1.6)
    cam_shot(n, [(0.0, o + Vector((0, -16, 0)), o), (1.0, o + Vector((0, -13.5, 0)), o)])
    return f_logo


def shot_5():
    c, a = collection('05 reveal'), S0(5)
    hud('INTRODUCING', 0.08, 0.95, '#cbd5e1', a + 6, S1(5) - 4, spacing=1.8)
    f_logo = rings_and_logo(5, c)
    flash(f_logo, WHITE, 0.7, 4)


# ----------------------------------------------------------------------------------------------
# Shot 6 · nothing lost: 105 tiles turn green
# ----------------------------------------------------------------------------------------------
def shot_6():
    c, o, a = collection('06 nothing lost'), O(6), S0(6)
    grid = link(bpy.data.objects.new('grid', None), c)
    grid.location = o
    wave0, wave1 = a + 12, S1(6) - 40
    for r in range(7):
        for k in range(15):
            m = Mat('tile', '#1e293b', 1.0, blend=False)
            t = cube('tile', (0.62, 0.12, 0.62), c, m, ((k - 7) * 0.78, 0, (3 - r) * 0.78))
            t.parent = grid
            f = round(wave0 + (wave1 - wave0) * (k / 14) + r * 1.5)
            kf(m.color, 'default_value', f, (*hex_rgb('#1e293b'), 1))
            kf(m.color, 'default_value', f + 6, (*hex_rgb(GREEN), 1))
            kf(m.strength, 'default_value', f, 1.0)
            kf(m.strength, 'default_value', f + 4, 3.0)
            kf(m.strength, 'default_value', f + 12, 1.4)
    sweep = cube('sweep', (0.06, 0.3, 6.5), c, Mat('sweep', WHITE, 8.0), o + Vector((-6.6, -0.2, 0.4)))
    kf(sweep, 'location', wave0, o + Vector((-6.6, -0.2, 0.4)), 'LINEAR')
    kf(sweep, 'location', wave1 + 6, o + Vector((6.6, -0.2, 0.4)), 'LINEAR')
    counter([0, 15, 30, 45, 60, 75, 90, 105], wave0, wave1 + 6, '{} / 105', 0.0, S1(6) - 12, size=0.24, color='#86efac')
    # Transition: every tile rushes to the centre and folds into the "11" of the next shot.
    kf(grid, 'scale', S1(6) - 14, Vector((1, 1, 1)))
    kf(grid, 'scale', S1(6) - 1, Vector((0.02, 0.02, 0.02)))
    cam_shot(6, [(0.0, o + Vector((-2.4, -12.5, 0.9)), o + Vector((0, 0, 0.7))),
                 (1.0, o + Vector((1.2, -11.0, 0.6)), o + Vector((0, 0, 0.5)))])
    caption(*CAPTIONS[6], a + 16, S1(6) - 14)


# ----------------------------------------------------------------------------------------------
# Shot 7 · 11 new features
# ----------------------------------------------------------------------------------------------
def shot_7():
    c, o, a = collection('07 eleven'), O(7), S0(7)
    num_m = Mat('eleven', WHITE, 4.0)
    eleven = text('11', 2.6, num_m, c, o + Vector((0, -0.5, 0.35)), extrude=0.12)
    pop(eleven, a + 2, dur=12, overshoot=1.25)
    sub_m = Mat('new features', '#f9a8d4', 2.0, 0.0)
    text('NEW FEATURES', 0.42, sub_m, c, o + Vector((0, -0.5, -1.25)), spacing=1.5)
    fade(sub_m.alpha, a + 12, None, 10)
    orbit = link(bpy.data.objects.new('orbit', None), c)
    orbit.location = o
    ring = torus('feature ring', 6.2, 0.03, c, Mat('ring', PINK, 5.0))
    ring.parent = orbit
    ring.scale = (1, 0.5, 1)
    ring.rotation_euler = (math.radians(90), 0, 0)
    for i, name in enumerate(NEW_FEATURES):
        ang = i / len(NEW_FEATURES) * 2 * math.pi
        lm = Mat('feature', WHITE, 1.5, 0.0)
        t = text(name, 0.26, lm, c, (math.cos(ang) * 6.2, math.sin(ang) * 1.5, math.sin(ang) * 3.1))
        t.parent = orbit
        fade(lm.alpha, a + 14 + i * 3, None, 8)
    kf(orbit, 'rotation_euler', a, Vector((0, 0, 0)), 'LINEAR')
    kf(orbit, 'rotation_euler', S1(7), Vector((0, math.radians(-25), 0)), 'LINEAR')
    stars = dust('stars', 500, (20, 6, 11), c, Mat('stars', '#475569', 2.0), 0.03, o + Vector((0, 10, 0)))
    # Camera: impact shake as the number lands, then a dive forward into the feature names.
    base = o + Vector((0, -15, 0))
    cam_key(a, base, o)
    for i, d in enumerate([(0.12, 0, 0.08), (-0.1, 0, -0.06), (0.06, 0, 0.04), (-0.03, 0, -0.02), (0, 0, 0)]):
        cam_key(a + 9 + i * 2, base + Vector(d), o)
    cam_key(S1(7) - 16, base + Vector((0, 1.5, 0)), o)
    cam_key(S1(7) - 1, o + Vector((0, -4.0, -1.0)), o + Vector((0, 6, -1.4)), 'CONSTANT')
    flash(S1(7) - 2, WHITE, 0.8, 4)


# ----------------------------------------------------------------------------------------------
# Shots 8 to 14 · feature cards on a carousel that swings on the beat
# ----------------------------------------------------------------------------------------------
def shot_carousel():
    c, o = collection('08-14 feature carousel'), O(8)
    hub = link(bpy.data.objects.new('carousel', None), c)
    hub.location = o
    R, n = 9.0, len(CARDS)
    step = 2 * math.pi / n
    for k, (tex, t0, t1, cap, eyebrow) in enumerate(CARDS):
        phi = -math.pi / 2 - k * step
        img = load_image('react_' + tex, tex)  # a real React screenshot wins over the mock-up
        m = Mat('card ' + tex, '#cfd5df', 1.0, 1.0, image=img, blend=False)
        card = plane('card ' + tex, 6.4, 4.0, c, m)
        card.parent = hub
        card.location = (R * math.cos(phi), R * math.sin(phi), 0.55)
        card.rotation_euler = (math.radians(90), 0, phi + math.pi / 2)
        frame = plane('card frame', 6.56, 4.16, c, Mat('frame', INDIGO if tex == 'slide' else PINK, 2.0, 0.6))
        frame.parent = card
        frame.location = (0, 0, -0.02)
        f0, f1 = F(t0), F(t1)
        # The card breathes forward slightly while it is in front.
        kf(card, 'scale', f0, Vector((1, 1, 1)))
        kf(card, 'scale', f1 - 12, Vector((1.04, 1.04, 1.04)))
        kf(card, 'scale', f1, Vector((1, 1, 1)))
        # Swing: hold, then rotate the hub 1/n turn over 12 frames as the next card arrives.
        kf(hub, 'rotation_euler', f1 - 12 if k < n - 1 else f1, Vector((0, 0, k * step)))
        if k < n - 1:
            kf(hub, 'rotation_euler', f1, Vector((0, 0, (k + 1) * step)))
        caption(cap, eyebrow, f0 + 8, f1 - 2)
    kf(hub, 'rotation_euler', F(CARDS[0][1]), Vector((0, 0, 0)))
    view = o + Vector((0, -R - 10.0, 0.55))
    target = o + Vector((0, -R, 0.55))
    cam_key(S0(8), view + Vector((0, 1.2, 0)), target)  # lands from the dive
    cam_key(S0(8) + 16, view, target)
    cam_key(S1(14) - 12, view + Vector((0, 0.6, 0)), target)
    cam_key(S1(14) - 1, view + Vector((0, 2.4, 0)), target, 'CONSTANT')  # push into the green toast
    flash(S1(14) - 3, GREEN, 0.85, 6)


# ----------------------------------------------------------------------------------------------
# Shot 15 · in their words
# ----------------------------------------------------------------------------------------------
def shot_15():
    c, o, a = collection('15 quotes'), O(15), S0(15)
    stars = dust('stars', 700, (20, 8, 11), c, Mat('stars', '#64748b', 2.0), 0.03, o + Vector((0, 10, 0)))
    base = stars.location.copy()
    kf(stars, 'location', a, base, 'LINEAR')
    kf(stars, 'location', S1(15), base + Vector((0, -4, 0.6)), 'LINEAR')
    cam_shot(15, [(0.0, o + Vector((0, -14, 0)), o), (1.0, o + Vector((0, -13.4, 0)), o)])
    hud('“User interface and performance have significantly improved.”', 0.13, 0.62, WHITE, a + 6, S1(15) - 4)
    hud('ERM CENTRE OF COMPETENCE', 0.06, 0.38, MUTED, a + 24, S1(15) - 4, spacing=1.4)
    hud('“Great new features that make navigation easier', 0.13, -0.12, WHITE, a + 84, S1(15) - 4)
    hud('and give us a much clearer view of our R&O data.”', 0.13, -0.34, WHITE, a + 90, S1(15) - 4)
    hud('RISK AND OPPORTUNITY MANAGER', 0.06, -0.6, MUTED, a + 104, S1(15) - 4, spacing=1.4)


# ----------------------------------------------------------------------------------------------
# Shot 16 · end card
# ----------------------------------------------------------------------------------------------
def shot_16():
    c = collection('16 end card')
    rings_and_logo(16, c, ('Everything you rely on. Faster and easier.', 'COMING SOON'))
    # Team credit above the logo: Skywise and the Clairvoyant team, side by side.
    a = S0(16)
    hud('BROUGHT TO YOU BY', 0.05, 1.1, MUTED, a + 84, END - 6, spacing=1.8)
    hud_logo(('logo_skywise',), 'SKYWISE', LOGO_H, -0.85, 0.86, a + 92, END - 6, LOGO_PLATE)
    hud('×', 0.08, 0.83, MUTED, a + 98, END - 6)
    hud_logo(('logo_clairvoyant',), 'CLAIRVOYANT TEAM', LOGO_H, 0.85, 0.86, a + 104, END - 6, LOGO_PLATE)


# ----------------------------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------------------------
shot_1(); shot_2(); shot_3(); shot_4(); shot_5(); shot_6(); shot_7(); shot_carousel(); shot_15(); shot_16()

# Fades: in from black, a dip between the wall shots, out to black at the end.
kf(black.alpha, 'default_value', 1, 1.0)
kf(black.alpha, 'default_value', 18, 0.0)
dip(S0(3), 3)                     # colour drains as the wall greys out
kf(black.alpha, 'default_value', S0(5) - 1, 0.0)
kf(black.alpha, 'default_value', S0(5), 1.0)  # out of the black statement
kf(black.alpha, 'default_value', S0(5) + 10, 0.0)
kf(black.alpha, 'default_value', END - 30, 0.0)
kf(black.alpha, 'default_value', END, 1.0)

# ----------------------------------------------------------------------------------------------
# Render settings, compositor, sound
# ----------------------------------------------------------------------------------------------
r = scene.render
r.resolution_x, r.resolution_y = RES
r.resolution_percentage = 50 if PREVIEW else 100
r.fps = FPS
scene.frame_start, scene.frame_end = 1, END
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
r.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
ee = scene.eevee
if hasattr(ee, 'taa_render_samples'):
    ee.taa_render_samples = 8 if PREVIEW else 48
for owner, attr in ((r, 'use_motion_blur'), (ee, 'use_motion_blur')):
    if hasattr(owner, attr):
        setattr(owner, attr, True)
if hasattr(ee, 'use_bloom'):  # EEVEE before 4.2
    ee.use_bloom = True
    ee.bloom_intensity = 0.06
scene.view_settings.view_transform = 'Standard'


def setup_compositor():
    """Glow on bright emission, plus a soft vignette. Skipped with a warning if the API differs."""
    try:
        if hasattr(scene, 'compositing_node_group'):  # Blender 5.x
            tree = bpy.data.node_groups.new('ERM trailer compositor', 'CompositorNodeTree')
            tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
            scene.compositing_node_group = tree
            out = tree.nodes.new('NodeGroupOutput')
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            tree.nodes.clear()
            out = tree.nodes.new('CompositorNodeComposite')
        rl = tree.nodes.new('CompositorNodeRLayers')
        glare = tree.nodes.new('CompositorNodeGlare')
        for attr, val in (('glare_type', 'FOG_GLOW'), ('quality', 'HIGH'), ('size', 8), ('threshold', 0.9), ('mix', -0.55)):
            if hasattr(glare, attr):
                setattr(glare, attr, val)
        for name, val in (('Threshold', 0.9), ('Strength', 0.5), ('Size', 0.6)):
            if name in glare.inputs and hasattr(glare.inputs[name], 'default_value'):
                try:
                    glare.inputs[name].default_value = val
                except TypeError:
                    pass
        tree.links.new(rl.outputs['Image'], glare.inputs[0])
        last = glare.outputs[0]
        try:
            ell = tree.nodes.new('CompositorNodeEllipseMask')
            for attr, val in (('width', 1.15), ('height', 1.0)):
                if hasattr(ell, attr):
                    setattr(ell, attr, val)
            blur = tree.nodes.new('CompositorNodeBlur')
            for attr, val in (('size_x', 400), ('size_y', 400)):
                if hasattr(blur, attr):
                    setattr(blur, attr, val)
            tree.links.new(ell.outputs[0], blur.inputs[0])
            mix = tree.nodes.new('CompositorNodeMixRGB')
            mix.blend_type = 'MULTIPLY'
            tree.links.new(last, mix.inputs[1])
            tree.links.new(blur.outputs[0], mix.inputs[2])
            mix.inputs[0].default_value = 0.35
            last = mix.outputs[0]
        except Exception as exc:  # vignette is optional
            print('[erm2] vignette skipped:', exc)
        tree.links.new(last, out.inputs[0])
    except Exception as exc:
        print('[erm2] compositor skipped (glow off):', exc)


setup_compositor()

# Video output
try:
    r.image_settings.media_type = 'VIDEO'  # Blender 5.x
except (AttributeError, TypeError):
    pass
r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'
r.ffmpeg.codec = 'H264'
r.ffmpeg.constant_rate_factor = 'MEDIUM' if PREVIEW else 'HIGH'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
r.filepath = OUT

if MUSIC and os.path.exists(MUSIC):
    se = scene.sequence_editor_create()
    strips = getattr(se, 'strips', None) or se.sequences
    strips.new_sound('music', MUSIC, channel=1, frame_start=1)
    r.ffmpeg.audio_codec = 'AAC'
    print('[erm2] music added:', MUSIC)

PREF.keyframe_new_interpolation_type = _old_interp
scene.frame_set(1)
print(f'[erm2] built {END} frames ({END / FPS:.0f} s) at {FPS} fps; textures from {ASSETS}')

if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(SAVE))
if DO_RENDER:
    bpy.ops.render.render(animation=True)
    print('[erm2] rendered to', OUT)
