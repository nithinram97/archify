"""
ERM 2.0 trailer for ERM users (1:34, 11 shots), built entirely in Blender.

Follows storyboard v3 (erm-migration/docs/trailer-storyboard, motion preview: prototypes/trailer-animatic.html):
  1 ERM around the world   globe of dots, stops on each country, pins, arcs, user counts
  2 Across every function the globe's dots fly into one cloud per siglum around an ERM hub, dive into the hub
  3 Your ERM               curved wall of today's dashboards
  4 Until now              the wall drains, a spinner turns, dip to black
  5 The turn               "So we rebuilt it. From the ground up." A line of light collapses to a point
  6 Nothing left behind    the point opens into a gate; today's screens pass through and come out as ERM 2.0
  7 Every tab you use      Maps, Table, Action Tracker, Summary, Report, Full Search (whip pans, tab bar)
  8 New: custom one-pager  layout picker, pulsing frame on Layout 4 (Custom)
  9 New: slideshow mode    the slide goes full screen, fade to black
 10 Brought to you by      Skywise logo, Clairvoyant mark, CLAIRVOYANT typed in Michroma; glides into the end card
 11 ERM 2.0                rings, logo, tagline, Coming soon

Requirements
  Blender 4.2 or newer (EEVEE). Tested API paths cover 4.2 to 5.x; older versions may need small changes.
  Next to this script: textures/ (screens and logos), data/globe-dots.json, fonts/Michroma-Regular.ttf.
    react_<name>.png   ERM 2.0 screens with sample data (heat, table, tracker, summary, report, fullsearch,
                       onepager_pick, slide)
    <name>.png         mock-ups of today's screens; slate_<name>.png wins if you add real Slate screenshots
    logo_skywise.png, logo_clairvoyant_mark.png   team logos (sources in logos/)
  See textures/SCREENSHOTS.md. Use sample or test data only.

Run
  Build the scene and open it:          blender -P erm2_trailer.py
  Build and render the MP4 (headless):  blender -b -P erm2_trailer.py -- --render
  Quick low-res preview render:         blender -b -P erm2_trailer.py -- --render --preview
  Options after "--":
    --assets DIR    textures folder (default: textures/ next to this script)
    --music FILE    soundtrack (default: audio/erm2_trailer_mix.wav, the original score; --no-music for none)
    --font FILE     .ttf/.otf for titles and captions (default: Blender's built-in font)
    --out PATH      output file (default: render/erm2_trailer.mp4 next to this script)
    --save FILE     also save the built scene as a .blend

Everything is on the timeline: open the .blend to retime shots, change captions or swap textures.
"""

import bpy
import bmesh
import json
import math
import os
import random
import sys
from mathutils import Euler, Vector

# ----------------------------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------------------------
FPS = 24
RES = (1920, 1080)

# Shot timing in seconds (storyboard v3).
SHOTS = {1: (0, 10), 2: (10, 17), 3: (17, 23), 4: (23, 29), 5: (29, 33), 6: (33, 41),
         7: (41, 65), 8: (65, 71), 9: (71, 77), 10: (77, 84), 11: (84, 94)}

PINK = '#ec4f8f'
INDIGO = '#6366f1'
CYAN = '#7dd3fc'
WHITE = '#f8fafc'
MUTED = '#94a3b8'
NAVY = '#070b16'
SLATE_DOT = '#5d6f8f'

K = 1.26  # camera distances from the animatic (40° vertical FOV) scaled for the 35 mm lens used here

# [country, users, site, lat, lon, arrival time s]
COUNTRIES = [
    ('France', 314, 'Blagnac · Toulouse', 43.63, 1.36, 1.4), ('Germany', 205, 'Hamburg', 53.55, 9.99, 3.0),
    ('United Kingdom', 58, 'Broughton', 53.17, -2.99, 4.4), ('Spain', 25, 'Getafe', 40.31, -3.73, 5.6),
    ('Canada', 12, 'Mirabel', 45.68, -74.04, 7.0), ('India', 7, 'Bangalore', 12.97, 77.59, 8.4),
]
# Globe orientation keys [t, lat, lon]: stop on each country, fast spins between (westward to India).
GLOBE_KEYS = [(0, 25, -35), (1.4, 46, 2), (2.4, 46, 2), (3.0, 51, 10), (3.8, 51, 10), (4.4, 54, -2), (5.0, 54, -2),
              (5.6, 40, -4), (6.2, 40, -4), (7.0, 46, -74), (7.6, 46, -74), (8.4, 15, -282.4), (8.9, 15, -282.4),
              (10.0, None, None), (10.4, 32, -345)]
GLOBE_DIST = [(0, 13), (1.4, 10.5), (6.2, 10.5), (6.6, 11.9), (7.0, 10.5), (7.6, 10.5), (8.0, 12.3), (8.4, 10.5),
              (8.9, 10.5), (10, 14)]
SIGLUMS = [('B', 345), ('O', 120), ('P', 95), ('A', 60), ('L', 55), ('S', 55), ('K', 50)]
GATE = [('table', 'table'), ('tracker', 'tracker'), ('summary', 'onepager'), ('report', 'report'),
        ('fullsearch', 'search'), ('heat', 'heat')]  # (ERM 2.0 screen, today's mock-up); Maps comes out last
TABS = [('heat', 'Maps', 'Your risks and opportunities on one heat map.', (0.72, 0.3)),
        ('table', 'Table', 'Every risk, sorted and filtered your way.', (0.45, 0.28)),
        ('tracker', 'Action Tracker', 'Every action followed through to the finish.', (0.5, 0.32)),
        ('summary', 'Summary', 'The story of the quarter, in one place.', (0.25, 0.2)),
        ('report', 'Report', 'Ready-to-share reports, straight to PDF.', (0.62, 0.42)),
        ('fullsearch', 'Full Search', 'Find any risk, across every dashboard.', (0.6, 0.16))]
# Michroma advance widths (em) for the typed name; the cursor follows them.
MICH_ADV = {'A': 1.0625, 'C': 1.0474, 'I': 0.2812, 'L': 0.8125, 'N': 1.1333, 'O': 1.0474, 'R': 1.019, 'T': 0.9355,
            'V': 1.0, 'Y': 1.0625}
MICH_SPACING = 1.07  # 7% tracking (brand kit)

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
DATA = os.path.join(HERE, 'data')
MUSIC = arg('--music', os.path.join(HERE, 'audio', 'erm2_trailer_mix.wav'))
if '--no-music' in argv:
    MUSIC = None
FONT_PATH = arg('--font')
MICHROMA_PATH = os.path.join(HERE, 'fonts', 'Michroma-Regular.ttf')
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


END = S1(11)


def ss(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


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


def rgba(h):
    return (*hex_rgb(h), 1)


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


def link(ob, coll):
    coll.objects.link(ob)
    return ob


def empty(name, coll, loc=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None), coll)
    e.location = loc
    return e


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
    """Emission material. `.alpha`, `.strength` and `.color` are sockets you can keyframe.
    With an image, the image drives the colour and its own transparency is kept (alpha = image alpha x .alpha).
    blend=False keeps depth (dithered), which globes and occluders need."""

    def __init__(self, name, color=WHITE, strength=1.0, alpha=1.0, image=None, blend=True):
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        nt = self.nt = self.mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = self.em = nt.nodes.new('ShaderNodeEmission')
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
        em.inputs['Color'].default_value = rgba(color)
        em.inputs['Strength'].default_value = strength
        self.alpha = mix.inputs[0]
        if image is not None:
            tex = self.tex = nt.nodes.new('ShaderNodeTexImage')
            tex.image = image
            tex.interpolation = 'Cubic'
            nt.links.new(tex.outputs['Color'], em.inputs['Color'])
            mul = nt.nodes.new('ShaderNodeMath')
            mul.operation = 'MULTIPLY'
            nt.links.new(tex.outputs['Alpha'], mul.inputs[0])
            nt.links.new(mul.outputs[0], mix.inputs[0])
            self.alpha = mul.inputs[1]
        self.alpha.default_value = alpha
        if blend:
            _blended(self.mat)
        self.strength = em.inputs['Strength']
        self.color = em.inputs['Color']


def fade(sock, f_in, f_out, ramp=10, peak=1.0):
    """Animate an alpha/strength socket: 0 -> peak over `ramp` frames, hold, peak -> 0 at f_out."""
    kf(sock, 'default_value', f_in, 0.0)
    kf(sock, 'default_value', f_in + ramp, peak)
    if f_out is not None:
        kf(sock, 'default_value', f_out - ramp, peak)
        kf(sock, 'default_value', f_out, 0.0)


def fade_out(sock, f0, f1, start=1.0):
    kf(sock, 'default_value', f0, start)
    kf(sock, 'default_value', f1, 0.0)


def load_image(*names):
    """First image found among `names` (.png or .jpg in ASSETS), e.g. a real screenshot before the mock-up."""
    for name in names:
        for ext in ('.png', '.jpg', '.jpeg'):
            path = os.path.join(ASSETS, name + ext)
            if os.path.exists(path):
                return bpy.data.images.load(path, check_existing=True)
    print(f'[erm2] no texture for {names}, using a flat card')
    return None


def socket(sockets, identifier):
    return next(s for s in sockets if s.identifier == identifier)


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


def dots(name, points, radius, coll, mat):
    """One mesh of tiny spheres at `points`. Returns the object and, per dot, the indices of its vertices."""
    bm = bmesh.new()
    groups = []
    for p in points:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius)
        bmesh.ops.translate(bm, vec=Vector(p), verts=res['verts'])
        groups.append(res['verts'])
    bm.verts.index_update()
    idx = [[v.index for v in g] for g in groups]
    return mesh_object(name, bm, coll, mat), idx


def dust(name, count, spread, coll, mat, radius=0.03, center=(0, 0, 0)):
    """Random cloud of tiny spheres (stars)."""
    pts = [(random.uniform(-1, 1) * spread[0], random.uniform(-1, 1) * spread[1], random.uniform(-1, 1) * spread[2])
           for _ in range(count)]
    ob, _ = dots(name, pts, radius, coll, mat)
    ob.location = center
    return ob


def curve_path(name, points, coll, mat, bevel=0.02, cyclic=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 4
    if hasattr(cu, 'bevel_factor_mapping_end'):
        cu.bevel_factor_mapping_start = 'SPLINE'
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


def grow(curve_ob, f0, f1, from_middle=False):
    if from_middle:
        kf(curve_ob.data, 'bevel_factor_start', f0, 0.5)
        kf(curve_ob.data, 'bevel_factor_start', f1, 0.0)
        kf(curve_ob.data, 'bevel_factor_end', f0, 0.5)
    else:
        kf(curve_ob.data, 'bevel_factor_end', f0, 0.0)
    kf(curve_ob.data, 'bevel_factor_end', f1, 1.0)


FONT = bpy.data.fonts.load(FONT_PATH) if FONT_PATH and os.path.exists(FONT_PATH) else None
MICHROMA = bpy.data.fonts.load(MICHROMA_PATH) if os.path.exists(MICHROMA_PATH) else None
if not MICHROMA:
    print('[erm2] fonts/Michroma-Regular.ttf not found; the Clairvoyant name uses the default font')


def text(body, size, mat, coll, loc=(0, 0, 0), align='CENTER', extrude=0.0, parent=None, upright=True, spacing=1.0, font=None):
    """Text object. upright=True stands it up facing -Y (towards the cameras); HUD text passes False."""
    cu = bpy.data.curves.new('txt', 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.space_character = spacing
    if font or FONT:
        cu.font = font or FONT
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
    b = Vector(base) if hasattr(base, '__len__') else Vector((base,) * 3)
    kf(ob, 'scale', f, b * 0.001)
    kf(ob, 'scale', f + int(dur * 0.7), b * overshoot)
    kf(ob, 'scale', f + dur, b)
    if out:
        kf(ob, 'scale', out - out_dur, b)
        kf(ob, 'scale', out, b * 0.001)


def window(ob, f_in, f_out, base=1.0):
    """Hard on/off visibility via constant-interpolated scale."""
    b = Vector(base) if hasattr(base, '__len__') else Vector((base,) * 3)
    kf(ob, 'scale', 1, b * 0.001, 'CONSTANT')
    kf(ob, 'scale', max(f_in, 2), b, 'CONSTANT')
    if f_out is not None:
        kf(ob, 'scale', f_out, b * 0.001, 'CONSTANT')


# ----------------------------------------------------------------------------------------------
# World, camera, HUD (captions, letterbox, fades)
# ----------------------------------------------------------------------------------------------
world = scene.world or bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background') or world.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = rgba(NAVY)
bg.inputs['Strength'].default_value = 1.0

C_CAM = collection('Camera and titles')
cam_data = bpy.data.cameras.new('Camera')
cam_data.lens = 35
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.sensor_width = 36
cam_data.clip_start = 0.02
cam = link(bpy.data.objects.new('Camera', cam_data), C_CAM)
scene.camera = cam

# Titles, logos, letterbox, fades and flashes live on a rig in front of the lens (laid out in a 5-unit space
# scaled by 0.12), so scene objects never cover them.
hud_root = link(bpy.data.objects.new('HUD', None), C_CAM)
hud_root.parent = cam
hud_root.scale = (0.12, 0.12, 0.12)
HUD_D = 5.0
HUD_W = HUD_D * 36 / 35
HUD_H = HUD_W * RES[1] / RES[0]


# The animatic is laid out in 1280 x 720 px; these map its pixels to HUD units.
def hx(px):
    return (px - 640) / 1280 * HUD_W


def hy(py):
    return (360 - py) / 720 * HUD_H


def hs(px):
    return px / 720 * HUD_H


def hud(body, size, y, color=WHITE, f_in=None, f_out=None, x=0.0, spacing=1.0, ramp=10, z=0.0, align='CENTER', font=None, rise=True):
    m = Mat('hud', color, 1.0, 0.0)
    ob = text(body, size, m, C_CAM, loc=(x, y, -HUD_D + z), parent=hud_root, upright=False, spacing=spacing, align=align, font=font)
    if f_in is not None:
        fade(m.alpha, f_in, f_out, ramp)
        if rise:
            kf(ob, 'location', f_in, Vector((x, y - 0.04, -HUD_D + z)))
            kf(ob, 'location', f_in + ramp + 6, Vector((x, y, -HUD_D + z)))
    return ob, m


def hud_plane(name, w, h, x, y, mat, z=-0.003):
    p = plane(name, w, h, C_CAM, mat)
    p.parent = hud_root
    p.location = (x, y, -HUD_D + z)
    return p


def caption(main, eyebrow, f_in, f_out):
    hud(main, 0.135, -HUD_H / 2 + 0.42, WHITE, f_in, f_out)
    if eyebrow:
        hud(eyebrow.upper(), 0.06, -HUD_H / 2 + 0.25, '#f9a8d4', f_in + 4, f_out, spacing=1.4)


bar_h = HUD_H * 60 / 900 * 1.02
for sign in (1, -1):
    hud_plane('letterbox', HUD_W * 1.2, bar_h, 0, sign * (HUD_H / 2 - bar_h / 2 + 0.001), Mat('bar', '#000000', 1.0, 1.0), 0.02)
black = Mat('fade to black', '#000000', 1.0, 0.0)
hud_plane('fader', HUD_W * 1.2, HUD_H * 1.2, 0, 0, black, 0.01)


def to_black(f0, f1):
    kf(black.alpha, 'default_value', f0, 0.0)
    kf(black.alpha, 'default_value', f1, 1.0)


def from_black(f0, f1):
    kf(black.alpha, 'default_value', f0, 1.0)
    kf(black.alpha, 'default_value', f1, 0.0)


def flash(f_mid, color=WHITE, peak=0.9, half=6):
    m = Mat('flash', color, 2.0, 0.0)
    hud_plane('flash', HUD_W * 1.2, HUD_H * 1.2, 0, 0, m, 0.015)
    kf(m.alpha, 'default_value', f_mid - half, 0.0)
    kf(m.alpha, 'default_value', f_mid, peak)
    kf(m.alpha, 'default_value', f_mid + half * 2, 0.0)


def aim(loc, target):
    d = Vector(target) - Vector(loc)
    return d.to_track_quat('-Z', 'Y').to_euler()


def cam_key(frame, loc, target, interp='BEZIER'):
    kf(cam, 'location', frame, Vector(loc), interp)
    kf(cam, 'rotation_euler', frame, aim(loc, target), interp)


def cam_path(t0, t1, fn, step=0.5, cut=True):
    """Sample a camera function fn(t) -> (location, target) every `step` seconds; the last key holds (cut)."""
    n = max(1, round((t1 - t0) / step))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        loc, tgt = fn(t)
        last = i == n
        cam_key(F(t) - (1 if last and cut else 0), loc, tgt, 'CONSTANT' if last and cut else 'BEZIER')


def O(n):
    """Shot groups are built at their own spot along X, so a camera jump is a cut."""
    return Vector((n * 400.0, 0, 0))


def anim(x, y, z):
    """Animatic coordinates (Y up, camera on +Z) to Blender (Z up, camera on -Y)."""
    return Vector((x, -z, y))


# ----------------------------------------------------------------------------------------------
# Shots 1-2 · globe, then the siglum constellation (same place, one continuous camera)
# ----------------------------------------------------------------------------------------------
R = 3.0
G = O(1)


def ll(lat, lon, r=R):
    a, o = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(a) * math.sin(o), -r * math.cos(a) * math.cos(o), r * math.sin(a)))


def globe_rot(lat, lon):
    return Euler((math.radians(lat), 0.0, math.radians(-lon)), 'ZYX')  # bring (lat, lon) to face the camera


def globe_pose(t):
    keys = [k for k in GLOBE_KEYS if k[1] is not None]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            e = ss(a[0], b[0], t)
            return lerp(a[1], b[1], e), lerp(a[2], b[2], e)
    return keys[-1][1], keys[-1][2]


def keyed(keys, t):
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            return lerp(a[1], b[1], ss(a[0], b[0], t))
    return keys[-1][1]


DOT_DATA = json.load(open(os.path.join(DATA, 'globe-dots.json')))
GLOBE_MATS = []


def halo_mat():
    """Soft rim behind the globe: only back faces, fading out towards the outer edge."""
    m = Mat('globe halo', INDIGO, 2.0, 1.0)
    nt = m.nt
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    inv = nt.nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs['Facing'], inv.inputs[1])
    back = nt.nodes.new('ShaderNodeMath')
    back.operation = 'MULTIPLY'
    nt.links.new(inv.outputs[0], back.inputs[0])
    nt.links.new(geo.outputs['Backfacing'], back.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    nt.links.new(back.outputs[0], mul.inputs[0])
    mix = next(n for n in nt.nodes if n.type == 'MIX_SHADER')
    nt.links.new(mul.outputs[0], mix.inputs[0])
    m.alpha = mul.inputs[1]
    m.alpha.default_value = 0.45
    return m


def shot_globe():
    c = collection('01 globe')
    globe = empty('globe', c, G)
    globe.rotation_mode = 'ZYX'
    for t, lat, lon in GLOBE_KEYS:
        if lat is None:
            lat, lon = globe_pose(t)  # pinned so the hand-off to shot 2 lands exactly
        kf(globe, 'rotation_euler', F(t), Vector(globe_rot(lat, lon)))
    core_m = Mat('globe core', '#0b1222', 1.0, 1.0, blend=False)
    core = sphere('globe core', R * 0.992, c, core_m)
    core.parent = globe
    halo_m = halo_mat()
    halo = sphere('globe halo', R * 1.12, c, halo_m)
    halo.parent = globe
    base_m = Mat('globe dots', SLATE_DOT, 1.6, 1.0, blend=False)
    base_ob, _ = dots('globe dots', [ll(la, lo) for la, lo, cc in DOT_DATA if not cc], 0.028, c, base_m)
    base_ob.parent = globe
    GLOBE_MATS.extend([(core_m, 1.0), (halo_m, 0.45), (base_m, 1.0)])
    blagnac = ll(43.63, 1.36)
    for k, (name, users, site, lat, lon, t_arr) in enumerate(COUNTRIES):
        t0 = t_arr - 0.25
        nxt = COUNTRIES[k + 1][5] - 0.25 if k + 1 < len(COUNTRIES) else 8.9
        m = Mat('country ' + name, SLATE_DOT, 1.6, 1.0, blend=False)
        ob, _ = dots('country ' + name, [ll(la, lo) for la, lo, cc in DOT_DATA if cc == k + 1], 0.03, c, m)
        ob.parent = globe
        GLOBE_MATS.append((m, 1.0))
        for f, col, st in ((F(t0), SLATE_DOT, 1.6), (F(t0) + 6, '#ff4f9a', 5.0), (F(nxt), '#ff4f9a', 5.0),
                           (F(nxt) + 8, '#c46b9b', 2.2), (F(8.9), '#c46b9b', 2.2), (F(9.2), '#ff4f9a', 4.0)):
            kf(m.color, 'default_value', f, rgba(col))
            kf(m.strength, 'default_value', f, st)
        # Pin, head and the arc back to Toulouse (all ride on the globe)
        pin_m = Mat('pin', '#f9a8d4', 3.0)
        pin = curve_path('pin ' + name, [ll(lat, lon), ll(lat, lon, R * 1.14)], c, pin_m, 0.012)
        pin.parent = globe
        grow(pin, F(t0), F(t0 + 0.45))
        head = sphere('pin head ' + name, 0.045, c, Mat('pin head', '#ff7ab6', 6.0), ll(lat, lon, R * 1.14))
        head.parent = globe
        pop(head, F(t0), dur=10)
        GLOBE_MATS.append((pin_m, 1.0))
        if k:
            b = ll(lat, lon)
            mid = (blagnac + b) / 2
            mid = mid.normalized() * R * (1.12 + (blagnac - b).length * 0.06)
            arc_m = Mat('arc', '#f472b6', 4.0)
            arc = curve_path('arc ' + name, [blagnac, mid, b], c, arc_m, 0.01)
            arc.parent = globe
            grow(arc, F(t0), F(t0 + 0.8))
            GLOBE_MATS.append((arc_m, 1.0))
        # Country tag: the country is centred, so the tag sits just right of centre
        hud(name, 0.12, 0.2, WHITE, F(t0), F(min(nxt, 8.9)), x=0.4, align='LEFT', ramp=6)
        hud(f'{users} users  ·  {site}', 0.06, 0.04, '#f9a8d4', F(t0) + 3, F(min(nxt, 8.9)), x=0.4, align='LEFT', ramp=6)
    hud('892 users  ·  6 countries  ·  1,600+ dashboards', 0.15, HUD_H / 2 - 0.42, WHITE, F(9.0), F(10.4))
    caption('Every day, users around the world manage risk in ERM.', 'ERM today', F(1.0), F(8.7))
    cam_path(0, 10, lambda t: (G + Vector((0, -keyed(GLOBE_DIST, t) * K, 0.2)), G), step=0.2, cut=False)
    return globe


def shot_siglums(globe):
    c, t_a = collection('02 siglums'), 10.0
    # The globe's other dots fade and drift outwards
    kf(globe, 'scale', F(10), Vector((1, 1, 1)))
    kf(globe, 'scale', F(10.9), Vector((1.35, 1.35, 1.35)))
    for m, a0 in GLOBE_MATS:
        fade_out(m.alpha, F(10), F(10.8), a0)
    # Nodes (animatic layout, mapped to Blender axes)
    nodes = []
    for i, (n, users) in enumerate(SIGLUMS):
        ang = math.radians(180 - i * 360 / 7)
        nodes.append(dict(name=n, users=users, r=0.1 + math.sqrt(users) * 0.026, named=True, i=i,
                          pos=G + anim(math.cos(ang) * 4.7, math.sin(ang) * 2.45, -math.sin(ang) * 0.6)))
    for j in range(12):
        ang = math.radians(180 - (j + 0.5) * 30 + 8)
        nodes.append(dict(name='', users=10 if j < 4 else 9, r=0.08, named=False, i=j,
                          pos=G + anim(math.cos(ang) * 6.9, math.sin(ang) * 3.35, -1.2)))
    hub = G + anim(0, 0, 0.4)
    rnd = random.Random(21)
    dst, swirl = [], []
    for nd in nodes:
        for _ in range(nd['users']):
            d = Vector((rnd.random() - 0.5, rnd.random() - 0.5, rnd.random() - 0.5)).normalized()
            dst.append(nd['pos'] + d * (nd['r'] * 1.2 + 0.12 + rnd.random() ** 0.7 * (0.3 + nd['r'] * 1.4)))
            swirl.append(rnd.random() - 0.5)
    # One dot per user: the front-facing globe dots at 10 s become the people
    rot = globe_rot(*globe_pose(10.0)).to_matrix()
    front = [p for p in (G + rot @ ll(la, lo) for la, lo, _ in DOT_DATA) if p.y - G.y < -0.3]
    src = [front[int(i * len(front) / len(dst))] for i in range(len(dst))]
    people_m = Mat('people', SLATE_DOT, 2.2, 1.0)
    people, idx = dots('people', src, 0.034, c, people_m)
    people.shape_key_add(name='Basis', from_mix=False)
    cloud = people.shape_key_add(name='cloud', from_mix=False)
    whirl = people.shape_key_add(name='swirl', from_mix=False)
    for i, vids in enumerate(idx):
        dv, sv = dst[i] - src[i], Vector((0, -1.4, swirl[i] * 1.2))
        for v in vids:
            cloud.data[v].co = people.data.vertices[v].co + dv
            whirl.data[v].co = people.data.vertices[v].co + sv
    window(people, F(10), None)
    kf(cloud, 'value', F(10), 0.0)
    kf(cloud, 'value', F(11.6), 1.0)
    kf(whirl, 'value', F(10), 0.0)
    kf(whirl, 'value', F(10.8), 1.0)
    kf(whirl, 'value', F(11.6), 0.0)
    kf(people_m.color, 'default_value', F(10), rgba(SLATE_DOT))
    kf(people_m.color, 'default_value', F(11.4), rgba(CYAN))
    # Hub, nodes, links, pulses, tags
    hub_ob = sphere('ERM hub', 0.3, c, Mat('hub', '#ff4f9a', 4.0), hub)
    pop(hub_ob, F(10.9), dur=12, overshoot=1.2)
    kf(hub_ob, 'scale', F(16.2), Vector((1, 1, 1)))
    kf(hub_ob, 'scale', F(17), Vector((3.5, 3.5, 3.5)))
    hub_m = Mat('hub label', WHITE, 2.0, 0.0)
    text('ERM', 0.28, hub_m, c, hub + Vector((0, -0.35, 0)))
    fade(hub_m.alpha, F(11.1), F(16.4), 8)
    for nd in nodes:
        t0 = 11.3 + nd['i'] * 0.22 if nd['named'] else 12.6 + nd['i'] * 0.05
        s = sphere('siglum ' + nd['name'], nd['r'], c, Mat('node', '#d63a7c' if nd['named'] else '#6d74e8', 3.0), nd['pos'])
        pop(s, F(t0), dur=11, overshoot=1.2)
        ctrl = (nd['pos'] + hub) / 2 + Vector((0, -1.3, 0))
        link_m = Mat('link', '#f9a8d4' if nd['named'] else INDIGO, 2.0, 0.7)
        ln = curve_path('link ' + nd['name'], [nd['pos'], ctrl, hub], c, link_m, 0.012 if nd['named'] else 0.006)
        grow(ln, F(t0), F(t0 + 0.6))
        if not nd['named']:
            continue
        for q in range(2):  # light pulses travel from the node into ERM
            p = sphere('pulse', 0.05, c, Mat('pulse', WHITE, 6.0), nd['pos'])
            window(p, F(t0 + 0.6), F(16.4))
            t = t0 + 0.6
            while t < 16.4:
                f = (t * 0.45 + nd['i'] * 0.17 + q * 0.5) % 1.0
                b = (1 - f) ** 2 * nd['pos'] + 2 * (1 - f) * f * ctrl + f ** 2 * hub
                kf(p, 'location', F(t), b, 'CONSTANT' if f > 0.9 else 'LINEAR')
                t += 0.2
        tag_m = Mat('tag', WHITE, 1.5, 0.0)
        text(f'{nd["name"]}   {nd["users"]}', 0.2, tag_m, c, nd['pos'] + Vector((0, -0.2, nd['r'] + 0.38)))
        fade(tag_m.alpha, F(t0 + 0.15), F(16.3), 8)
    more_m = Mat('more', '#cbd5e1', 1.2, 0.0)
    text('+ 12 more', 0.2, more_m, c, G + anim(4.2, -3.5, -1.2))
    fade(more_m.alpha, F(13.0), F(16.3), 8)
    caption('Every function reports its risks in ERM.', 'Across every function', F(11.6), F(16.15))

    def cam_fn(t):
        u = t - t_a
        ang = lerp(-0.14, 0.14, min(1.0, u / 6.2))
        dist = lerp(lerp(14, 12.5, ss(0, 1.6, u)), 0.55, ss(6.15, 7.0, u) ** 1.6)
        height = lerp(0.2, 0.8 * dist / 12.5, ss(0, 1.6, u))
        rel = anim(math.sin(ang) * dist, height, math.cos(ang) * dist)
        return hub + rel * K, hub

    cam_path(10, 17, cam_fn, step=0.25)
    flash(F(16.85), WHITE, 0.95, 4)


# ----------------------------------------------------------------------------------------------
# Shots 3-4 · the wall of today's dashboards, then the wait (one wall, the colour drains)
# ----------------------------------------------------------------------------------------------
WALL_TEX = ['heat', 'table', 'onepager', 'tracker']


def shot_wall():
    c, o = collection('03-04 wall'), O(3)
    centre = o + Vector((0, -9, 0))
    screens, frames = [], []
    for r in range(3):
        for k in range(5):
            name = WALL_TEX[(r * 5 + k) % 4]
            img = load_image('slate_' + name, name)  # the app users know today, if you add Slate screenshots
            m = Mat('wall screen', '#9aa4b2', 0.82, 1.0, image=img, blend=False)
            ang = (k - 2) * 0.32
            pos = centre + Vector((11 * math.sin(ang), 11 * math.cos(ang), (1 - r) * 2.4))
            p = plane('wall screen', 3.2, 2.0, c, m)
            p.location = pos
            p.rotation_euler = (math.radians(90), 0, -ang)
            fm = Mat('wall frame', PINK, 1.5, 0.55)
            glow = plane('wall frame', 3.32, 2.12, c, fm)
            glow.location = pos + (pos - centre).normalized() * 0.02
            glow.rotation_euler = p.rotation_euler
            pop(p, S0(3) + 2 + (r * 5 + k) * 2, dur=12, overshoot=1.02)
            pop(glow, S0(3) + 2 + (r * 5 + k) * 2, dur=12, overshoot=1.02)
            screens.append(m)
            frames.append(fm)
    # Shot 4: the colour drains
    for m in screens:
        kf(m.strength, 'default_value', S0(4), 0.82)
        kf(m.strength, 'default_value', F(24.6), 0.26)
    for fm in frames:
        kf(fm.color, 'default_value', S0(4), rgba(PINK))
        kf(fm.color, 'default_value', F(24.6), rgba('#334155'))
        kf(fm.alpha, 'default_value', S0(4), 0.55)
        kf(fm.alpha, 'default_value', F(24.6), 0.15)
    pivot = empty('spinner pivot', c, centre + Vector((0, 6.2, 0)))
    pivot.rotation_euler = (math.radians(90), 0, 0)
    ring_pts = [(math.cos(t) * 0.9, math.sin(t) * 0.9, 0) for t in [i * math.pi / 2 for i in range(4)]]
    spin_m = Mat('spinner', '#cbd5e1', 1.5, 0.0)
    spin = curve_path('spinner', ring_pts, c, spin_m, 0.07, cyclic=True)
    spin.data.bevel_factor_end = 0.7
    spin.parent = pivot
    fade(spin_m.alpha, F(23.6), None, 12)
    kf(spin, 'rotation_euler', S0(4), Vector((0, 0, 0)), 'LINEAR')
    kf(spin, 'rotation_euler', S1(4), Vector((0, 0, -math.radians(360 * 4.5))), 'LINEAR')
    look = centre + Vector((0, 11, 0))

    def cam_fn(t):
        if t < 23:
            u = t - 17
            return centre + Vector((math.sin(u * 0.2) * 0.4, lerp(-1.0, 1.6, ss(0, 6, u)), 0.3)), look
        u = t - 23
        wander = math.sin(u * 0.9)
        return (centre + Vector((wander * 0.6, lerp(1.6, 2.0, ss(0, 6, u)), 0.3)),
                look + Vector((wander * 0.3, 0, 0)))

    cam_path(17, 29, cam_fn, step=0.5)
    caption('Every quarter, your risk reporting runs through ERM.', 'Your ERM', F(17.5), F(22.7))
    caption('Waiting for tabs to load. Hunting for the right dashboard.', 'Until now', F(23.6), F(28.4))


# ----------------------------------------------------------------------------------------------
# Shot 5 · the turn
# ----------------------------------------------------------------------------------------------
def shot_turn():
    c, o = collection('05 turn'), O(5)
    cam_path(29, 33, lambda t: (o + Vector((0, -10, 0)), o), step=4)
    hud('So we rebuilt it.', 0.3, 0.22, WHITE, F(29.3), F(32.4), ramp=10)
    hud('From the ground up.', 0.3, -0.24, PINK, F(30.3), F(32.4), ramp=10)
    line = plane('light line', 1.0, 0.03, c, Mat('light line', '#ffe4f1', 8.0))
    line.location = o
    line.rotation_euler = (math.radians(90), 0, 0)
    kf(line, 'scale', F(32.0), Vector((0.001, 1, 1)))
    kf(line, 'scale', F(32.6), Vector((9.0, 1, 1)))
    kf(line, 'scale', F(32.65), Vector((9.0, 1, 1)))
    kf(line, 'scale', F(33.0) - 1, Vector((0.08, 1, 1)))


# ----------------------------------------------------------------------------------------------
# Shot 6 · through the gate, today's screens come out as ERM 2.0
# ----------------------------------------------------------------------------------------------
SW, SH, SRY, SPEED, X_STOP = 3.4, 2.125, -0.6, 4.2, 2.4


def gate_mat(name, mock_img, real_img, gate_x):
    """Today's screen (dimmed) on the near side of the gate, ERM 2.0 beyond it (world X > gate_x)."""
    m = Mat(name, WHITE, 0.82, 1.0)
    nt = m.nt
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    side = nt.nodes.new('ShaderNodeMath')
    side.operation = 'GREATER_THAN'
    side.inputs[1].default_value = gate_x
    nt.links.new(sep.outputs['X'], side.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(side.outputs[0], socket(mix.inputs, 'Factor_Float'))
    for img, ident in ((mock_img, 'A_Color'), (real_img, 'B_Color')):
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = img
        tex.interpolation = 'Cubic'
        nt.links.new(tex.outputs['Color'], socket(mix.inputs, ident))
    nt.links.new(socket(mix.outputs, 'Result_Color'), m.em.inputs['Color'])
    st = nt.nodes.new('ShaderNodeMath')
    st.operation = 'MULTIPLY_ADD'  # strength 0.45 before the gate, 0.82 after
    st.inputs[1].default_value = 0.37
    st.inputs[2].default_value = 0.45
    nt.links.new(side.outputs[0], st.inputs[0])
    nt.links.new(st.outputs[0], m.em.inputs['Strength'])
    return m


def frame_mat(gate_x):
    m = Mat('gate frame', PINK, 1.5, 0.55)
    nt = m.nt
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    side = nt.nodes.new('ShaderNodeMath')
    side.operation = 'GREATER_THAN'
    side.inputs[1].default_value = gate_x
    nt.links.new(sep.outputs['X'], side.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(side.outputs[0], socket(mix.inputs, 'Factor_Float'))
    socket(mix.inputs, 'A_Color').default_value = rgba('#475569')
    socket(mix.inputs, 'B_Color').default_value = rgba(PINK)
    nt.links.new(socket(mix.outputs, 'Result_Color'), m.em.inputs['Color'])
    return m


BOOST = 1.7  # screens speed up once they are through the gate


def gate_x(k, u):
    x = -9.5 + (u - 0.9 - k * 0.75) * SPEED
    if x > 0:
        x *= BOOST
    return min(x, X_STOP) if k == 5 else x


def shot_gate():
    c, o, t_a = collection('06 gate'), O(6), 33.0
    dust('stars', 400, (20, 14, 11), c, Mat('stars', '#334155', 2.0), 0.03, o + Vector((0, 12, 0)))
    for k, (real, mock) in enumerate(GATE):
        m = gate_mat('gate screen ' + real, load_image('slate_' + mock, mock), load_image('react_' + real, real), o.x)
        p = plane('gate screen ' + real, SW, SH, c, m)
        p.rotation_euler = (math.radians(90), 0, SRY)
        fr = plane('gate frame', SW + 0.12, SH + 0.12, c, frame_mat(o.x))
        fr.parent = p
        fr.location = (0, 0, -0.01)
        y, z = math.sin(k * 1.7) * 0.3, math.cos(k * 2.3) * 0.35
        u_cross = 0.9 + k * 0.75 + 9.5 / SPEED
        keys = [0.0, u_cross, 8.0] if k < 5 else [0.0, u_cross, u_cross + X_STOP / (SPEED * BOOST), 8.0]
        for u in keys:
            kf(p, 'location', F(t_a + u), o + anim(gate_x(k, u), y, z), 'LINEAR')
        if k < 5:
            fade_out(m.alpha, F(40.0), F(40.6))
    # The gate: a line of light that opens into an upright oval ring
    line_m = Mat('gate line', WHITE, 6.0)
    line = curve_path('gate line', [o + Vector((0, 0, -2.7)), o + Vector((0, 0, 2.7))], c, line_m, 0.02)
    grow(line, F(t_a), F(t_a + 0.55), from_middle=True)
    for k in range(6):  # flare as each screen crosses
        tc = t_a + 0.9 + k * 0.75 + 9.5 / SPEED
        kf(line_m.strength, 'default_value', F(tc - 0.3), 6.0)
        kf(line_m.strength, 'default_value', F(tc), 16.0)
        kf(line_m.strength, 'default_value', F(tc + 0.3), 6.0)
    ring_m = Mat('gate ring', '#ff7ab6', 5.0)
    ring = torus('gate ring', 2.75, 0.045, c, ring_m)
    ring.location = o
    ring.rotation_euler = (0, math.radians(90), 0)
    kf(ring, 'scale', F(t_a + 0.15), Vector((0.001, 0.001, 1)))
    kf(ring, 'scale', F(t_a + 1.1), Vector((1, 0.62, 1)))
    for m in (line_m, ring_m):
        fade_out(m.alpha, F(40.0), F(40.7))
    caption('Everything you rely on, carried over. And faster.', 'Nothing left behind', F(34.4), F(39.7))
    # Camera: three-quarter view of the gate, then lands square on the Maps screen (it becomes shot 7)
    n = anim(math.sin(SRY), 0, math.cos(SRY))
    tgt0 = o + anim(0.6, 0, 0)

    def cam_fn(t):
        u = t - t_a
        ph = o + anim(gate_x(5, u), math.sin(5 * 1.7) * 0.3, math.cos(5 * 2.3) * 0.35)
        base = tgt0 + (anim(-6.2 + u * 0.12, 0.9, 7.6) + o - tgt0) * K
        land = ph + n * 4.66 * K
        e = ss(7.0, 8.0, u)
        return base.lerp(land, e), tgt0.lerp(ph, e)

    cam_path(33, 41, cam_fn, step=0.25)


# ----------------------------------------------------------------------------------------------
# Shots 7-9 · inside the app: every tab, then the two new features
# ----------------------------------------------------------------------------------------------
AW, AH = 5.4, 3.375
A = O(7)


def load_bar(c, p, t0):
    """A pink bar on the screen's top edge that fills almost instantly as the screen arrives."""
    bm = Mat('load bar', '#ff4fa0', 3.0, 1.0)
    bar = plane('load bar', AW, 0.05, c, bm)
    bar.parent = p
    kf(bar, 'location', F(t0 - 0.15), Vector((-AW / 2, AH / 2 + 0.03, 0.02)))
    kf(bar, 'scale', F(t0 - 0.15), Vector((0.001, 1, 1)))
    kf(bar, 'location', F(t0 + 0.12), Vector((0, AH / 2 + 0.03, 0.02)))
    kf(bar, 'scale', F(t0 + 0.12), Vector((1, 1, 1)))
    fade_out(bm.alpha, F(t0 + 0.25), F(t0 + 0.7))


def app_screen(c, key, name):
    m = Mat('app ' + key, WHITE, 0.82, 1.0, image=load_image('react_' + key, key))
    p = plane(name, AW, AH, c, m)
    fm = Mat('app frame', PINK, 1.5, 0.55)
    fr = plane(name + ' frame', AW + 0.12, AH + 0.12, c, fm)
    fr.parent = p
    fr.location = (0, 0, -0.01)
    return p, m, fm


def place(p, f, x=0.0, z=0.0, yaw=0.0, scale=1.0, interp='BEZIER'):
    kf(p, 'location', f, A + Vector((x, 0, z)), interp)
    kf(p, 'rotation_euler', f, Vector((math.radians(90), 0, yaw)), interp)
    kf(p, 'scale', f, Vector((scale,) * 3), interp)


PUSH, SLIDE = 0.45, 6.4  # screens change with a push: the next slides in while the current slides out


def hide(p, f):
    kf(p, 'scale', f, Vector((0.001,) * 3), 'CONSTANT')


def push_screen(p, t0, t1, focus=(0.5, 0.5), zoom=0.1, kb=0.5, yaw=0.0, push_in=True, push_out=True):
    """Push in from the right (overlapping the previous screen), ease towards `focus` (Ken Burns), push out left."""
    fx, fz = (focus[0] - 0.5) * AW, (0.5 - focus[1]) * AH
    sc = 1 + zoom
    hide(p, 1)
    if push_in:
        place(p, F(t0 - PUSH), SLIDE, 0, yaw - 0.25)
        streaks(t0 - PUSH)
    place(p, F(t0), 0, 0, yaw)
    if push_out:
        place(p, F(t1 - PUSH), -fx * sc * kb, -fz * sc * kb, yaw, sc)
        place(p, F(t1), -fx * sc * kb - SLIDE, -fz * sc * kb, yaw + 0.25, sc)
        hide(p, F(t1) + 1)


C_APP = None


def streaks(t):
    """A few faint motion streaks during a push."""
    rnd = random.Random(int(t * 10))
    for _ in range(4):
        m = Mat('streak', WHITE, 2.0, 0.0)
        s = plane('streak', rnd.uniform(2, 5), 0.01, C_APP, m)
        s.location = A + Vector((rnd.uniform(-3, 3), -0.6, rnd.uniform(-1.8, 1.8)))
        s.rotation_euler = (math.radians(90), 0, 0)
        kf(m.alpha, 'default_value', F(t), 0.0)
        kf(m.alpha, 'default_value', F(t + PUSH / 2), 0.35)
        kf(m.alpha, 'default_value', F(t + PUSH), 0.0)


def badge(parent, label, x, z, f_in, f_out=None, color=PINK, w=0.62):
    """Small pill (plane + text) on a screen's top edge, popping in."""
    holder = empty('badge ' + label, C_APP)
    holder.parent = parent
    holder.location = (x, z, 0.03)
    bp = plane('badge', w, 0.24, C_APP, Mat('badge', color, 2.2))
    bp.parent = holder
    t = text(label, 0.13, Mat('badge text', WHITE, 1.5), C_APP, (0, 0, 0.005), parent=holder, upright=False, spacing=1.2)
    t.location = (0, 0, 0.005)
    pop(holder, f_in, dur=10, overshoot=1.25, out=f_out)
    return holder


def tab_bar():
    """Floating tab bar (HUD): six pills; the pink highlight slides to the next tab on each whip."""
    pill_w, pill_h, y = hs(126), hs(30), hy(77)
    xs = [hx(305 + 134 * i) for i in range(6)]
    f_on, f_off = F(41.1), F(64.7)
    for i, (_, name, _, _) in enumerate(TABS):
        pm = Mat('tab pill', '#0f172a', 1.0, 0.0)
        hud_plane('tab pill', pill_w, pill_h, xs[i], y, pm, -0.006)
        fade(pm.alpha, f_on, f_off, 10, 0.75)
        hud(name, hs(14), y, '#e2e8f0', f_on, f_off, x=xs[i], rise=False)
    im = Mat('tab highlight', PINK, 2.2, 0.0)
    ind = hud_plane('tab highlight', pill_w, pill_h, xs[0], y, im, -0.004)
    fade(im.alpha, f_on, f_off, 10)
    for k in range(6):
        t1 = 41 + 4 * k + 4
        kf(ind, 'location', F(t1 - PUSH), Vector((xs[k], y, -HUD_D - 0.004)))
        if k < 5:
            kf(ind, 'location', F(t1), Vector((xs[k + 1], y, -HUD_D - 0.004)))


def shot_app():
    global C_APP
    c = C_APP = collection('07-09 app')
    dust('stars', 500, (20, 14, 11), c, Mat('stars', '#334155', 2.0), 0.03, A + Vector((0, 12, 0)))
    for k, (key, name, line, focus) in enumerate(TABS):
        t0 = 41 + 4 * k
        p, _, _ = app_screen(c, key, 'tab ' + name)
        push_screen(p, t0, t0 + 4, focus, push_in=k > 0)
        if k == 0:
            place(p, F(41), 0, 0, 0, 0.96)  # lands from the gate shot and settles
            place(p, F(41.35), 0, 0, 0, 1.0)
        load_bar(c, p, t0)
        caption(line, name, F(t0 + 0.4), F(t0 + 3.6))
    tab_bar()
    # The one performance note, on the first tab
    tag_m = Mat('speed tag', '#0f172a', 1.0, 0.0)
    hud_plane('speed tag', hs(150), hs(28), hx(940), hy(114), tag_m, -0.004)
    fade(tag_m.alpha, F(41.5), F(44.4), 8, 0.9)
    hud('LOADS IN A BLINK', hs(12), hy(114), '#f9a8d4', F(41.5), F(44.4), x=hx(940), spacing=1.3, ramp=8)
    # Shot 8 · custom one-pager layout
    p, _, _ = app_screen(c, 'onepager_pick', 'one-pager layout')
    push_screen(p, 65, 71, (0.79, 0.46), zoom=0.38, kb=0.65, yaw=-0.06)
    u0, u1, v0, v1 = 0.701, 0.886, 0.338, 0.585  # Layout 4 (Custom) on the screenshot
    x0, x1, z0, z1 = (u0 - 0.5) * AW, (u1 - 0.5) * AW, (0.5 - v0) * AH, (0.5 - v1) * AH
    hm = Mat('layout highlight', '#ff4fa0', 3.0, 0.0)
    for cx, cz, w, h in (((x0 + x1) / 2, z0, x1 - x0, 0.035), ((x0 + x1) / 2, z1, x1 - x0, 0.035),
                         (x0, (z0 + z1) / 2, 0.035, z0 - z1), (x1, (z0 + z1) / 2, 0.035, z0 - z1)):
        b = plane('highlight', w, h, c, hm)
        b.parent = p
        b.location = (cx, cz, 0.02)
    t = 66.0
    while t < 70.6:  # pulse
        kf(hm.alpha, 'default_value', F(t), 0.35)
        kf(hm.alpha, 'default_value', F(t + 0.25), 1.0)
        t += 0.5
    kf(hm.alpha, 'default_value', F(70.8), 0.0)
    badge(p, 'NEW', -AW / 2 + 0.45, AH / 2 + 0.24, F(65.5))
    caption('Build your own one-pager layout.', 'New', F(65.6), F(70.6))
    # Shot 9 · slideshow mode: the slide turns flat and grows to fill the frame
    p, _, fm = app_screen(c, 'slide', 'slideshow')
    hide(p, 1)
    place(p, F(71 - PUSH), SLIDE, 0.1, -0.47, 0.95)
    place(p, F(71), 0, 0.1, -0.22, 0.95)
    place(p, F(72.3), 0, 0.1, -0.22, 0.95)
    place(p, F(73.5), 0, 0, 0, 1.3)
    fade_out(fm.alpha, F(72.3), F(73.5), 0.55)  # the frame fades as the slide fills the screen
    badge(p, 'NEW', -AW / 2 + 0.45, AH / 2 + 0.24, F(71.5), F(72.7))
    badge(p, 'SLIDESHOW', -AW / 2 + 1.45, AH / 2 + 0.24, F(71.6), F(72.7), '#0f172a', 1.2)
    caption('Present straight from ERM, in slideshow mode.', 'New', F(73.6), F(76.4))
    # Camera: one gentle drift through shots 7-9
    cam_path(41, 77, lambda t: (A + anim(math.sin(t * 0.3) * 0.5, 0.15, 7.4) * K, A), step=1.0)


# ----------------------------------------------------------------------------------------------
# Shots 10-11 · brought to you by, then the end card (same place, one camera)
# ----------------------------------------------------------------------------------------------
E0 = 82.8  # rings start (s)
MARK_A = 896 / 1110  # Clairvoyant mark aspect (cropped file)
SKY_A = 772 / 193.2


def mich_width(s):
    return sum(MICH_ADV[ch] for ch in s) * MICH_SPACING


def cv_width(mh):
    """Clairvoyant lockup width for mark height mh (brand kit: wordmark 52/272 of the mark, gap 64/272)."""
    return mh * MARK_A + mh * 64 / 272 + mich_width('CLAIRVOYANT') * mh * 52 / 272


def credit_layouts():
    sh, mh, gap, xw = 66, 118, 64, 26
    sw, cw = sh * SKY_A, cv_width(mh)
    x0 = 640 - (sw + gap + xw + gap + cw) / 2
    a = dict(hy=236, hs=16, sh=sh, sx=x0 + sw / 2, sy=352, xx=x0 + sw + gap + xw / 2, xy=350, xs=30, mh=mh,
             cl=x0 + sw + gap + xw + gap, cy=352)
    b = dict(hy=84, hs=12, sh=50, sx=428, sy=146, xx=640, xy=143, xs=24, mh=70, cl=852 - cv_width(70) / 2, cy=146)
    return a, b


def img_plane(name, img, h, x, y):
    m = Mat(name, WHITE, 1.0, 0.0, image=img)
    w = h * img.size[0] / max(1, img.size[1]) if img else h
    return hud_plane(name, w, h, x, y, m, 0.0), m


def glide(ob, f0, f1, loc_a, loc_b, sc_b):
    kf(ob, 'location', f0, Vector(loc_a))
    kf(ob, 'scale', f0, Vector((1, 1, 1)))
    kf(ob, 'location', f1, Vector(loc_b))
    kf(ob, 'scale', f1, Vector((sc_b,) * 3))


def shot_credits():
    c, o = collection('10-11 credits and end card'), O(10)
    a, b = credit_layouts()
    g0, g1 = F(82.4), F(83.6)  # glide into the end-card layout
    z = -HUD_D
    # Brought to you by
    head, hm = hud('BROUGHT TO YOU BY', hs(a['hs']), hy(a['hy']), MUTED, x=0, spacing=1.6, rise=False)
    fade(hm.alpha, F(77.4), None, 14)
    glide(head, g0, g1, (0, hy(a['hy']), z), (0, hy(b['hy']), z), b['hs'] / a['hs'])
    # Skywise
    sky_img = load_image('logo_skywise')
    sky, sm = img_plane('Skywise logo', sky_img, hs(a['sh']), hx(a['sx']), hy(a['sy']))
    fade(sm.alpha, F(77.9), None, 14)
    kf(sky, 'scale', F(77.9), Vector((0.92, 0.92, 0.92)))
    kf(sky, 'scale', F(78.5), Vector((1, 1, 1)))
    glide(sky, g0, g1, (hx(a['sx']), hy(a['sy']), z), (hx(b['sx']), hy(b['sy']), z), b['sh'] / a['sh'])
    # ×
    times, tm = hud('×', hs(a['xs']), hy(a['xy']), MUTED, x=hx(a['xx']), rise=False)
    fade(tm.alpha, F(78.4), None, 10)
    glide(times, g0, g1, (hx(a['xx']), hy(a['xy']), z), (hx(b['xx']), hy(b['xy']), z), b['xs'] / a['xs'])
    # Clairvoyant mark (no wordmark), then the name typed in Michroma
    mark_img = load_image('logo_clairvoyant_mark')
    mh_a, mh_b = hs(a['mh']), hs(b['mh'])
    mx_a, mx_b = hx(a['cl']) + mh_a * MARK_A / 2, hx(b['cl']) + mh_b * MARK_A / 2
    mark, mm = img_plane('Clairvoyant mark', mark_img, mh_a, mx_a, hy(a['cy']))
    fade(mm.alpha, F(78.6), None, 10)
    pop(mark, F(78.6), dur=12, overshoot=1.08)
    glide(mark, g0, g1, (mx_a, hy(a['cy']), z), (mx_b, hy(b['cy']), z), b['mh'] / a['mh'])
    fs_a = mh_a * 52 / 272
    tx_a, tx_b = hx(a['cl']) + mh_a * (MARK_A + 64 / 272), hx(b['cl']) + mh_b * (MARK_A + 64 / 272)
    word = 'CLAIRVOYANT'
    step = (80.4 - 79.2) / len(word)
    caret_m = Mat('cursor', WHITE, 1.5, 1.0)
    caret = hud_plane('cursor', hs(2.2), fs_a * 0.95, tx_a, hy(a['cy']), caret_m, 0.0)
    kf(caret, 'scale', 1, Vector((0.001,) * 3), 'CONSTANT')
    for i in range(1, len(word) + 1):
        f_in = F(79.2 + (i - 1) * step)
        last = i == len(word)
        t_ob, t_m = hud(word[:i], fs_a, hy(a['cy']), WHITE, x=tx_a, align='LEFT', font=MICHROMA, spacing=MICH_SPACING, rise=False)
        t_m.alpha.default_value = 1.0
        window(t_ob, f_in, None if last else F(79.2 + i * step))
        kf(caret, 'location', f_in, Vector((tx_a + mich_width(word[:i]) * fs_a + hs(3), hy(a['cy']), z)), 'CONSTANT')
        kf(caret, 'scale', f_in, Vector((1, 1, 1)), 'CONSTANT')
        if last:
            glide(t_ob, g0, g1, (tx_a, hy(a['cy']), z), (tx_b, hy(b['cy']), z), b['mh'] / a['mh'])
    t = 80.4
    while t < 81.2:  # blink, then gone
        kf(caret, 'scale', F(t), Vector((0.001,) * 3), 'CONSTANT')
        kf(caret, 'scale', F(t + 0.25), Vector((1, 1, 1)), 'CONSTANT')
        t += 0.5
    kf(caret, 'scale', F(81.2), Vector((0.001,) * 3), 'CONSTANT')
    # Stars, rings and the logo
    stars = dust('stars', 1100, (20, 14, 11), c, Mat('stars', '#cbd5e1', 2.0), 0.03, o + Vector((0, 14, 0)))
    kf(stars, 'location', S0(10), stars.location.copy(), 'LINEAR')
    kf(stars, 'location', END, stars.location + Vector((0, -6, 0)), 'LINEAR')
    r1 = torus('ring pink', 4.6, 0.06, c, Mat('ring', PINK, 6.0))
    r2 = torus('ring indigo', 5.4, 0.03, c, Mat('ring', INDIGO, 6.0))
    for i, (r, rot, sc) in enumerate(((r1, (1.35, 0.15, 0), 1.25), (r2, (1.45, -0.2, 0.25), 1.2))):
        r.location = o
        final = Vector((math.pi / 2 - rot[0], rot[1], rot[2]))  # nearly edge-on, a wide ellipse
        f0 = F(E0 + i * 0.12)
        pop(r, f0, base=sc, dur=24, overshoot=1.08)
        kf(r, 'rotation_euler', f0, final + Vector((-0.6, 0, 0)))  # swings down into place
        kf(r, 'rotation_euler', f0 + 24, final)
        kf(r, 'rotation_euler', END, final + Vector((math.radians(4), math.radians(14), 0)), 'LINEAR')
    logo_w = Mat('logo', WHITE, 3.0, 0.0)
    logo_p = Mat('logo 2.0', PINK, 4.0, 0.0)
    erm = text('ERM', 1.9, logo_w, c, o + Vector((-1.35, -1.0, 0.1)), extrude=0.06)
    two = text('2.0', 1.9, logo_p, c, o + Vector((2.15, -1.0, 0.1)), extrude=0.06)
    fade(logo_w.alpha, F(E0 + 0.5), None, 12)
    fade(logo_p.alpha, F(E0 + 0.65), None, 12)
    pop(erm, F(E0 + 0.5), dur=16, overshoot=1.06)
    pop(two, F(E0 + 0.65), dur=16, overshoot=1.1)
    flash(F(E0 + 0.7), WHITE, 0.45, 5)
    hud('Everything you rely on. Faster and easier.', 0.13, -0.95, '#e2e8f0', F(E0 + 1.8), END - 6)
    hud('COMING SOON', 0.07, -1.18, '#f9a8d4', F(E0 + 2.6), END - 6, spacing=1.6)
    cam_path(77, 94, lambda t: (o + Vector((0, lerp(-15.2, -14.0, ss(77, 84, t)) + 0.6 * ss(84, 94, t), 0)), o), step=1.0, cut=False)


# ----------------------------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------------------------
g = shot_globe()
shot_siglums(g)
shot_wall()
shot_turn()
shot_gate()
shot_app()
shot_credits()

# Fades and the black background of the turn
from_black(1, F(0.8))
to_black(F(28.5), F(29.0))
from_black(F(29.0), F(29.15))  # the world turns black for the turn, the text needs the fader gone
kf(bg.inputs['Color'], 'default_value', F(29.0), rgba('#000000'), 'CONSTANT')
kf(bg.inputs['Color'], 'default_value', F(33.0), rgba(NAVY), 'CONSTANT')
kf(bg.inputs['Color'], 'default_value', 1, rgba(NAVY), 'CONSTANT')
to_black(F(76.45), F(77.0))
from_black(F(77.0), F(77.4))
to_black(F(93.0), END)

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
