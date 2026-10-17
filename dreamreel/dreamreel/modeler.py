"""dreamreel's modelling agent: describe a character or a thing (or show a picture), and an AI model
builds it in dreamreel's modelling kit, looks at renders of what it built from four sides, and
corrects it, a few rounds over, the way a modeller works.

    dreamreel generate frog --prompt "a chubby green cartoon frog with big eyes and a red scarf"
    dreamreel generate lamp --prompt "a brass desk lamp" --prop
    dreamreel generate girl --image refs/girl.png --height 1.2 --rounds 4
    dreamreel generate frog --spec models/frog.json          # rebuild after editing the recipe

The AI never runs code on your computer: it writes a recipe (JSON) of parts in the kit below, and
dreamreel builds that. The recipe is kept next to the model (models/NAME.json), so you, or the AI
again, can change it later. Which AI does the work is up to you (see ai.py): any frontier model
with your key, or a free one on your own machine.
"""
import json
import math
import os
import re

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

SHAPES = ("sphere", "box", "cylinder", "capsule", "tube", "lathe", "extrude", "torus", "blob")

KIT = """\
# dreamreel modelling kit

You build 3D models by writing a recipe: JSON describing parts. Units are metres; z is up; the
model's front faces -y (towards the camera); x is its left-right. It stands on the ground (z = 0),
centred on x = 0, y = 0.

{"name": "frog", "kind": "character", "materials": {...}, "parts": [...]}

materials: {"skin": {"color": "#5fb04a", "rough": 0.5, "metal": 0, "glow": 0, "glass": false}, ...}
  rough 0..1 (0 = shiny), metal 0..1, glow = emission strength (eyes of a robot, a lamp's bulb),
  glass = see-through.

Every part: {"name": "...", "shape": "...", "material": "skin", ...shape fields...,
             "rotate": [x, y, z] (degrees, optional), "mirror": true (optional: a copy at -x),
             "smooth": true (optional: rounded, subdivided surface)}

shapes:
- "sphere": "at": [x, y, z] centre, "size": [rx, ry, rz] radii (an ellipsoid; equal radii = a ball)
- "box": "at" = centre of its bottom face, "size": [width, depth, height], "round": edge radius
- "cylinder": "at" = centre of its bottom, "radius", "radius_top" (cone/taper), "height", "sides"
- "capsule": "from": [x, y, z], "to": [x, y, z], "radius", "radius_to" (a limb, a finger, a bone)
- "tube": "points": [[x, y, z], ...] a path, "radius": r or [r per point] (tails, handles, hair, wires)
- "lathe": "at" = base centre, "profile": [[r, z], ...] radius at each height, bottom to top
  (vases, bottles, heads, bodies, lamp shades: anything round about a vertical axis)
- "extrude": "at", "outline": [[x, z], ...] a flat outline seen from the front, "depth" (thickness
  along y): signs, leaves, ears, fins, blades, flat shapes
- "torus": "at", "radius" (ring), "thickness" (tube), lying flat (rotate it to stand up)
- "blob": like clay: "at" + "size" (an ellipsoid), or "from"/"to" + "radius" (a capsule); all blobs
  with the same "group" melt together into one smooth surface. Use blobs for organic bodies
  (creatures, characters, soft toys) so torso, neck and limbs join with no seams.

Modelling well:
- Work big to small: first the main masses and the silhouette, then the forms that explain how it's
  built (eye sockets, cheeks, panels, handles, joints), then a few details. Few parts that read
  well beat many tiny ones.
- Keep real proportions for the kind of thing (a door ~2 m, a chair seat ~0.45 m, a mug ~0.1 m);
  stylized characters may have big heads and eyes, but keep them consistent.
- Eyes: a white sphere set into the head, a coloured iris and a dark pupil in front of it, a small
  glint; lids are blobs or spheres over them.
- Use 3-8 materials with clearly different colours; nothing pure black or pure white.
- Characters ("kind": "character") stand in an A pose: legs apart and straight, feet on the ground,
  arms held down and out at about 45 degrees, clear of the body, hands open, facing -y. dreamreel
  rigs and animates them, so keep the limbs separate and well defined, and give their skeleton:
  "joints": {"hips": [x, y, z], "chest": [...], "neck": [...], "head": [top of the head],
             "shoulder": [...], "elbow": [...], "wrist": [...], "hand": [fingertips],
             "hip": [...], "knee": [...], "ankle": [...], "toe": [tip of the foot]}
  hips, chest, neck and head on the middle line (x = 0); the rest for the left side (+x; dreamreel
  mirrors them). Put each joint inside the body where it bends: the shoulder where the arm meets
  the torso, the hip where the leg meets the pelvis.

Reply with your thinking in a sentence or two, then the complete recipe in one ```json block.
"""

LOOK = """Here is what your recipe builds, rendered from four sides: top left FRONT (from -y), top right
RIGHT SIDE (from +x), bottom left BACK, bottom right THREE-QUARTER view.{ref}

Look hard at the picture. Compare it with what was asked: proportions, silhouette from each side,
parts floating or sunk inside others, missing parts, colours, symmetry, faces and eyes.
List the biggest problems, then reply with the complete corrected recipe in one ```json block.
If it is already right, reply with just: DONE"""


class RecipeError(ValueError):
    pass


# ---------------------------------------------------------------------- reading recipes
def parse(text):
    """The recipe in an AI reply (a ```json block, or the first {...}); None if it says DONE."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            raw = text[start:end + 1]
    if raw is None:
        if re.search(r"\bDONE\b", text):
            return None
        raise RecipeError("there's no recipe in your reply: give it in one ```json block")
    try:
        recipe = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RecipeError(f"the recipe isn't valid JSON ({e.msg} at line {e.lineno}, column {e.colno})")
    check(recipe)
    return recipe


def _vec(part, key, n=3, required=True):
    v = part.get(key)
    if v is None:
        if required:
            raise RecipeError(f"part {part.get('name', '?')!r} needs \"{key}\"")
        return None
    if isinstance(v, (int, float)) and n == 3 and key == "size":
        v = [v, v, v]
    if not (isinstance(v, list) and len(v) == n and all(isinstance(x, (int, float)) for x in v)):
        raise RecipeError(f"part {part.get('name', '?')!r}: \"{key}\" must be {n} numbers")
    return Vector(v) if n == 3 else v


JOINTS = ("hips", "chest", "neck", "head", "shoulder", "elbow", "wrist", "hand", "hip", "knee", "ankle", "toe")
ROLE = {"hips": "hips", "chest": "chest", "neck": "neck", "head": "head", "shoulder": "arm", "elbow": "elbow",
        "wrist": "wrist", "hand": "hand", "hip": "hip", "knee": "knee", "ankle": "ankle", "toe": "toe"}


def skeleton(recipe, lift=0.0):
    """A character recipe's joints as dreamreel's auto-rigger names them (both sides), or None."""
    j = recipe.get("joints")
    if not j:
        return None
    out = {}
    for name in JOINTS:
        x, y, z = j[name]
        if name in ("hips", "chest", "neck", "head"):
            out[name] = Vector((0.0, y, z + lift))
        else:
            out[f"l_{ROLE[name]}"] = Vector((abs(x), y, z + lift))
            out[f"r_{ROLE[name]}"] = Vector((-abs(x), y, z + lift))
    return out


def check(recipe):
    """Raise RecipeError, worded for the AI to fix, if the recipe can't be built."""
    if not isinstance(recipe, dict) or not isinstance(recipe.get("parts"), list) or not recipe["parts"]:
        raise RecipeError("the recipe needs \"parts\": a list of parts")
    if len(recipe["parts"]) > 400:
        raise RecipeError("too many parts (400 at most): fewer, bigger forms read better")
    mats = recipe.get("materials") or {}
    if not isinstance(mats, dict):
        raise RecipeError("\"materials\" must be an object of name: {color, ...}")
    for name, m in mats.items():
        if not isinstance(m, dict) or not _color_ok(m.get("color", "#cccccc")):
            raise RecipeError(f"material {name!r} needs \"color\": a hex colour like \"#5fb04a\"")
    joints = recipe.get("joints")
    if recipe.get("kind") == "character" or joints:
        if not isinstance(joints, dict):
            raise RecipeError("a character needs \"joints\" (its skeleton): " + ", ".join(JOINTS))
        missing = [n for n in JOINTS if n not in joints]
        if missing:
            raise RecipeError(f"the joints are missing: {', '.join(missing)}")
        for n in JOINTS:
            v = joints[n]
            if not (isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v)):
                raise RecipeError(f"joint {n!r} must be [x, y, z]")
        if not joints["hips"][2] < joints["chest"][2] < joints["neck"][2] < joints["head"][2]:
            raise RecipeError("the joints must go up the body: hips below chest below neck below head")
        if not joints["shoulder"][0] > 0 or not joints["hip"][0] > 0:
            raise RecipeError("give the left side's joints (shoulder, hip...: x > 0); dreamreel mirrors them")
    for i, part in enumerate(recipe["parts"]):
        if not isinstance(part, dict):
            raise RecipeError(f"part {i} isn't an object")
        shape = part.get("shape")
        if shape not in SHAPES:
            raise RecipeError(f"part {part.get('name', i)!r}: unknown shape {shape!r}; use one of {', '.join(SHAPES)}")
        if part.get("material") and part["material"] not in mats:
            raise RecipeError(f"part {part.get('name', i)!r} uses material {part['material']!r}, which isn't in materials")
        if "rotate" in part:
            _vec(part, "rotate")
        if shape in ("sphere", "box"):
            _vec(part, "at"), _vec(part, "size")
        elif shape in ("cylinder", "lathe", "extrude", "torus"):
            _vec(part, "at")
        if shape in ("capsule",) or (shape == "blob" and "from" in part):
            _vec(part, "from"), _vec(part, "to")
            _num(part, "radius")
        elif shape == "blob":
            _vec(part, "at"), _vec(part, "size")
        if shape == "cylinder":
            _num(part, "radius"), _num(part, "height")
        if shape == "torus":
            _num(part, "radius"), _num(part, "thickness")
        if shape == "tube":
            pts = part.get("points")
            if not (isinstance(pts, list) and len(pts) >= 2 and all(isinstance(p, list) and len(p) == 3 for p in pts)):
                raise RecipeError(f"part {part.get('name', i)!r}: \"points\" must be a list of at least 2 [x, y, z]")
        if shape in ("lathe", "extrude"):
            key = "profile" if shape == "lathe" else "outline"
            pts = part.get(key)
            if not (isinstance(pts, list) and len(pts) >= 3 and all(isinstance(p, list) and len(p) == 2 for p in pts)):
                raise RecipeError(f"part {part.get('name', i)!r}: \"{key}\" must be a list of at least 3 [a, b] pairs")
    return recipe


def _num(part, key, default=None):
    v = part.get(key, default)
    if not isinstance(v, (int, float)) or v <= 0:
        raise RecipeError(f"part {part.get('name', '?')!r} needs \"{key}\": a positive number")
    return float(v)


def _color_ok(c):
    return isinstance(c, str) and re.fullmatch(r"#?[0-9a-fA-F]{6}", c) is not None


# ---------------------------------------------------------------------- building
def _material(name, m):
    from . import look
    c = m.get("color", "#cccccc")
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    rgb = look.rgb(c if c.startswith("#") else "#" + c)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = float(m.get("rough", 0.5))
    bsdf.inputs["Metallic"].default_value = float(m.get("metal", 0.0))
    if m.get("glow"):
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = float(m["glow"])
    if m.get("glass"):
        bsdf.inputs["Alpha"].default_value = 0.3
        bsdf.inputs["Roughness"].default_value = 0.05
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
    mat.diffuse_color = (*rgb, 1)
    return mat


def _mesh_object(name, bm, mat):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if mat is not None:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _between(a, b):
    """Rotation taking +z to the direction a -> b, and the distance."""
    d = b - a
    return Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4(), d.length


def _ring_mesh(rings, cap=True):
    """A closed surface through rings of vertices (each ring a list of Vectors, same count)."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vs, vs[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap:
        for ring, flip in ((vs[0], True), (vs[-1], False)):
            if len({tuple(round(c, 6) for c in v.co) for v in ring}) > 2:
                f = bm.faces.new(ring[::-1] if flip else ring)
                f.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def _part(part, mat):
    shape, name = part["shape"], part.get("name", part["shape"])
    if shape == "sphere":
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
        bmesh.ops.scale(bm, vec=_vec(part, "size"), verts=bm.verts)
        obj = _mesh_object(name, bm, mat)
        obj.location = _vec(part, "at")
        _smooth(obj)
    elif shape == "box":
        w, d, h = _vec(part, "size")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
        obj = _mesh_object(name, bm, mat)
        obj.location = _vec(part, "at")
        r = float(part.get("round", 0.0) or 0.0)
        if r > 0:
            mod = obj.modifiers.new("round", "BEVEL")
            mod.width = min(r, w / 2.1, d / 2.1, h / 2.1)
            mod.segments = 3
    elif shape == "cylinder":
        r, h = _num(part, "radius"), _num(part, "height")
        r2 = float(part.get("radius_top", r))
        sides = max(3, min(64, int(part.get("sides", 24))))
        rings = [[Vector((rr * math.cos(2 * math.pi * k / sides), rr * math.sin(2 * math.pi * k / sides), z))
                  for k in range(sides)] for rr, z in ((r, 0.0), (max(r2, 1e-4), h))]
        obj = _mesh_object(name, _ring_mesh(rings), mat)
        obj.location = _vec(part, "at")
    elif shape == "capsule":
        a, b = _vec(part, "from"), _vec(part, "to")
        r1 = _num(part, "radius")
        r2 = float(part.get("radius_to", r1))
        obj = _tube(name, [a, b], [r1, r2], mat, caps=True)
    elif shape == "tube":
        pts = [Vector(p) for p in part["points"]]
        rad = part.get("radius", 0.05)
        rads = rad if isinstance(rad, list) else [rad] * len(pts)
        if len(rads) != len(pts):
            raise RecipeError(f"part {name!r}: \"radius\" needs one number per point")
        obj = _tube(name, pts, [float(x) for x in rads], mat, caps=True)
    elif shape == "lathe":
        prof = part["profile"]
        sides = 32
        rings = [[Vector((max(r, 1e-4) * math.cos(2 * math.pi * k / sides), max(r, 1e-4) * math.sin(2 * math.pi * k / sides), z))
                  for k in range(sides)] for r, z in prof]
        obj = _mesh_object(name, _ring_mesh(rings), mat)
        obj.location = _vec(part, "at")
        _smooth(obj)
    elif shape == "extrude":
        outline = part["outline"]
        depth = float(part.get("depth", 0.02))
        bm = bmesh.new()
        front = [bm.verts.new((x, -depth / 2, z)) for x, z in outline]
        back = [bm.verts.new((x, depth / 2, z)) for x, z in outline]
        try:
            bm.faces.new(front)
            bm.faces.new(back[::-1])
        except ValueError:
            raise RecipeError(f"part {name!r}: the outline crosses itself")
        n = len(outline)
        for k in range(n):
            bm.faces.new((front[k], back[k], back[(k + 1) % n], front[(k + 1) % n]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        obj = _mesh_object(name, bm, mat)
        obj.location = _vec(part, "at")
    elif shape == "torus":
        R, r = _num(part, "radius"), _num(part, "thickness")
        rings = []
        for i in range(32):
            a = 2 * math.pi * i / 32
            c, s = math.cos(a), math.sin(a)
            rings.append([Vector(((R + r * math.cos(2 * math.pi * k / 12)) * c, (R + r * math.cos(2 * math.pi * k / 12)) * s,
                                  r * math.sin(2 * math.pi * k / 12))) for k in range(12)])
        rings.append(rings[0])
        bm = _ring_mesh(rings, cap=False)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        obj = _mesh_object(name, bm, mat)
        obj.location = _vec(part, "at")
        _smooth(obj)
    else:
        raise RecipeError(f"unknown shape {shape!r}")
    if "rotate" in part:
        obj.rotation_euler = Euler([math.radians(x) for x in _vec(part, "rotate")])
    if part.get("smooth"):
        mod = obj.modifiers.new("smooth", "SUBSURF")
        mod.levels = mod.render_levels = 2
        _smooth(obj)
    return obj


def _tube(name, pts, rads, mat, caps=True, sides=16):
    """A tube through points, its radius changing along it, with rounded ends."""
    rings, u = [], None
    for i, p in enumerate(pts):
        d = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        d = d.normalized() if d.length > 1e-9 else Vector((0, 0, 1))
        if u is None:
            u = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
        else:                       # carry the frame along so the tube doesn't twist
            u = (u - d * u.dot(d)).normalized()
        v = d.cross(u)
        rings.append([p + (u * math.cos(2 * math.pi * k / sides) + v * math.sin(2 * math.pi * k / sides)) * rads[i]
                      for k in range(sides)])
    if caps:
        ends = []
        for end, nxt in ((0, 1), (len(pts) - 1, len(pts) - 2)):
            out = (pts[end] - pts[nxt]).normalized()
            ring = rings[end]
            dome = []
            for j in (1, 2, 3):
                t = j / 3.5 * math.pi / 2
                dome.append([pts[end] + (q - pts[end]) * math.cos(t) + out * rads[end] * math.sin(t) for q in ring])
            ends.append(dome)
        rings = ends[0][::-1] + rings + ends[1]
    obj = _mesh_object(name, _ring_mesh(rings, cap=True), mat)
    _smooth(obj)
    return obj


def _smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


BLOB = 1.46     # a metaball's surface sits inside its radius: this makes blobs the size asked
                # (measured: stiffness 4, threshold 0.6)


def _blobs(group, parts, mats):
    """Blobs of one group as one smooth mesh (metaballs melted together)."""
    mb = bpy.data.metaballs.new(f"blob.{group}")
    sizes = []
    for part in parts:
        el = mb.elements.new()
        if "from" in part:
            a, b = _vec(part, "from"), _vec(part, "to")
            r = _num(part, "radius")
            el.type = "CAPSULE"
            el.co = (a + b) / 2
            el.radius = r * BLOB
            el.size_x = max(1e-3, (b - a).length / 2)
            d = (b - a).normalized() if (b - a).length > 1e-6 else Vector((1, 0, 0))
            el.rotation = Vector((1, 0, 0)).rotation_difference(d)
            sizes.append(r)
        else:
            s = _vec(part, "size")
            el.type = "ELLIPSOID"
            el.co = _vec(part, "at")
            el.radius = max(s) * BLOB
            el.size_x, el.size_y, el.size_z = s.x / max(s), s.y / max(s), s.z / max(s)
            if "rotate" in part:
                el.rotation = Euler([math.radians(x) for x in _vec(part, "rotate")]).to_quaternion()
            sizes.append(min(s))
        el.stiffness = 4.0
    mb.resolution = mb.render_resolution = max(0.004, min(sizes) / 3)
    mb.threshold = 0.6
    obj = bpy.data.objects.new(f"blob.{group}", mb)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    bpy.data.objects.remove(obj)
    bpy.data.metaballs.remove(mb)
    mat_name = parts[0].get("material")
    mesh.materials.clear()
    if mat_name:
        mesh.materials.append(mats[mat_name])
    out = bpy.data.objects.new(group, mesh)
    bpy.context.scene.collection.objects.link(out)
    _smooth(out)
    return out


def build(recipe):
    """Build a recipe in a fresh scene; returns the model as one object, on the ground at the origin."""
    check(recipe)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = {name: _material(name, m) for name, m in (recipe.get("materials") or {}).items()}
    objs = []
    groups = {}
    for part in recipe["parts"]:
        copies = [part]
        if part.get("mirror"):
            copies.append(_mirrored(part))
        for p in copies:
            if p["shape"] == "blob":
                groups.setdefault(p.get("group", "body"), []).append(p)
            else:
                objs.append(_part(p, mats.get(p.get("material"))))
    for group, parts in groups.items():
        objs.append(_blobs(group, parts, mats))
    bpy.context.view_layer.update()
    for o in objs:          # apply rounding and smoothing, then join
        bpy.context.view_layer.objects.active = o
        for mod in list(o.modifiers):
            with bpy.context.temp_override(object=o, active_object=o):
                bpy.ops.object.modifier_apply(modifier=mod.name)
    for o in bpy.context.view_layer.objects:
        o.select_set(o in objs)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    model = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    model.name = model.data.name = recipe.get("name", "model")
    lo = min((model.matrix_world @ Vector(c)).z for c in model.bound_box)
    model.data.transform(Matrix.Translation((0, 0, -lo)))
    model["dr_lift"] = -lo          # how far it was moved to stand on the ground (joints move too)
    return model


def _mirrored(part):
    """A part's mirror image across x = 0 (its name gets _l/_r swapped)."""
    p = json.loads(json.dumps(part))
    p.pop("mirror", None)
    name = p.get("name", "")
    p["name"] = (name[:-2] + "_r" if name.endswith("_l") else name[:-2] + "_l" if name.endswith("_r") else name + ".mirror")
    for key in ("at", "from", "to"):
        if key in p:
            p[key] = [-p[key][0], p[key][1], p[key][2]]
    if "points" in p:
        p["points"] = [[-x, y, z] for x, y, z in p["points"]]
    if "outline" in p:
        p["outline"] = [[-x, z] for x, z in p["outline"]][::-1]
    if "rotate" in p:
        rx, ry, rz = p["rotate"]
        p["rotate"] = [rx, -ry, -rz]
    return p


# ---------------------------------------------------------------------- looking at it
def turnaround(model, path, size=384):
    """Render the model from the front, right, back and three-quarter view into one 2x2 sheet."""
    import numpy as np
    scene = bpy.context.scene
    lo = Vector([min((model.matrix_world @ Vector(c))[i] for c in model.bound_box) for i in range(3)])
    hi = Vector([max((model.matrix_world @ Vector(c))[i] for c in model.bound_box) for i in range(3)])
    mid, span = (lo + hi) / 2, max(hi - lo)
    cam = bpy.data.objects.new("look", bpy.data.cameras.new("look"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = span * 1.25
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_cavity = True
    scene.display.shading.show_shadows = False
    scene.world = scene.world or bpy.data.worlds.new("w")
    scene.world.color = (0.62, 0.66, 0.72)
    r = scene.render
    r.resolution_x = r.resolution_y = size
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    tiles = []
    for yaw in (0, 90, 180, 35):
        a = math.radians(yaw)
        d = Vector((math.sin(a), -math.cos(a), 0.12 if yaw == 35 else 0.0)).normalized()
        cam.location = mid + d * span * 3
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        tmp = path + f".{yaw}.png"
        r.filepath = tmp
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(tmp)
        tiles.append(np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4))
        bpy.data.images.remove(img)
        os.remove(tmp)
    top = np.concatenate([tiles[2], tiles[3]], axis=1)           # image rows start at the bottom
    bottom_row = np.concatenate([tiles[0], tiles[1]], axis=1)
    sheet = np.concatenate([top, bottom_row], axis=0)
    out = bpy.data.images.new("turnaround", 2 * size, 2 * size, alpha=True)
    out.pixels[:] = sheet.ravel()
    out.filepath_raw, out.file_format = path, "PNG"
    out.save()
    bpy.data.images.remove(out)
    bpy.data.objects.remove(cam)
    return path


# ---------------------------------------------------------------------- the agent
def generate(ai, description=None, image=None, kind="character", rounds=3, workdir=".", progress=print):
    """Have an AI model build a model, look at it and correct it; returns the final recipe."""
    system = KIT
    ask = f"Make a {kind}: {description}" if description else f"Make this {kind}, as in the picture."
    if image and description:
        ask += " The picture shows what it should look like."
    first = [{"text": ask + f'\nUse "kind": "{kind}".'}]
    if image:
        first.insert(0, {"image": image})
    messages = [{"role": "user", "content": first}]
    recipe, built = None, None
    attempts = 0
    while attempts < rounds + 3:
        attempts += 1
        progress(f"  asking {ai} ...")
        reply = ai.ask(system, messages)
        messages.append({"role": "assistant", "content": [{"text": reply}]})
        try:
            new = parse(reply)
            if new is None:
                if recipe is None:
                    raise RecipeError("there's nothing built yet: give the recipe in a ```json block")
                progress("  the AI is happy with it")
                break
            model = build(new)
        except RecipeError as e:
            progress(f"  recipe problem: {e}")
            messages.append({"role": "user", "content": [{"text": f"That recipe can't be built: {e}. Fix it and "
                                                                  "reply with the complete recipe."}]})
            continue
        recipe = new
        built = (built or 0) + 1
        progress(f"  built round {built}: {len(new['parts'])} parts, {len(model.data.polygons)} faces")
        if built > rounds:
            break
        sheet = turnaround(model, os.path.join(workdir, f"look_{built}.png"))
        ref = " The first picture I sent shows what it should look like." if image else ""
        messages.append({"role": "user", "content": [{"image": sheet}, {"text": LOOK.format(ref=ref)}]})
    if recipe is None:
        raise RecipeError("the AI didn't produce a recipe that builds; try again or another model")
    return recipe


def save(recipe, glb):
    """Build a recipe and save it as a .glb, with the recipe beside it (.json)."""
    model = build(recipe)
    os.makedirs(os.path.dirname(os.path.abspath(glb)), exist_ok=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(o is model)
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True)
    with open(os.path.splitext(glb)[0] + ".json", "w") as f:
        json.dump(dict(recipe, lift=model["dr_lift"]), f, indent=1)
    return model
