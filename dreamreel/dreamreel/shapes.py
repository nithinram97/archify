"""Procedural meshes: the building blocks for characters, props and sets.

Each function makes one object, names it, gives it a material and optionally parents it. Sizes are
in metres; positions are relative to the parent.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import look


def _collection():
    return bpy.context.scene.collection


def empty(name, parent=None, at=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = 0.1
    _collection().objects.link(obj)
    obj.parent = parent
    obj.location = at
    return obj


def _object(name, bm, material, parent, at, rot, smooth=True):
    mesh = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    _collection().objects.link(obj)
    if material is not None:
        mesh.materials.append(material if isinstance(material, bpy.types.Material) else look.plastic(material))
    obj.parent = parent
    obj.location = at
    obj.rotation_euler = rot
    return obj


def ellipsoid(name, rx, ry, rz, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0), segments=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=segments // 2, radius=1.0)
    bmesh.ops.scale(bm, vec=(rx, ry, rz), verts=bm.verts)
    return _object(name, bm, material, parent, at, rot)


def sphere(name, r, material, parent=None, at=(0, 0, 0), segments=32):
    return ellipsoid(name, r, r, r, material, parent, at, segments=segments)


def capsule(name, radius, length, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0), hang=False,
            squash=(1.0, 1.0)):
    """A pill: `length` is the straight part between the two round ends (total = length + 2*radius).

    With hang=True the capsule hangs down from its origin (for arms and legs); otherwise it's centred.
    `squash` scales x and y (a bean body is a squashed capsule).
    """
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=radius)
    for v in bm.verts:
        v.co.z += length / 2 if v.co.z > 1e-6 else (-length / 2 if v.co.z < -1e-6 else 0)
        v.co.x *= squash[0]
        v.co.y *= squash[1]
        if hang:
            v.co.z -= length / 2 + radius
    return _object(name, bm, material, parent, at, rot)


def box(name, w, d, h, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0), bevel=0.02, base=True):
    """A rounded box. With base=True its origin is the middle of the bottom face (it sits on things)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    if base:
        bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    obj = _object(name, bm, material, parent, at, rot, smooth=False)
    if bevel:
        mod = obj.modifiers.new("round", "BEVEL")
        mod.width = min(bevel, w / 2.2, d / 2.2, h / 2.2)
        mod.segments = 3
        mod.limit_method = "NONE"
        mod.harden_normals = True
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def cylinder(name, r, h, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0), r2=None, bevel=0.01, segments=32):
    """A cylinder (or cone with r2) standing on its base."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    obj = _object(name, bm, material, parent, at, rot, smooth=False)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        mod = obj.modifiers.new("round", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.harden_normals = True
    return obj


def torus(name, major, minor, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0), arc=360):
    bm = bmesh.new()
    seg_major, seg_minor = 40, 12
    rings = []
    steps = seg_major if arc >= 360 else seg_major + 1
    for i in range(steps):
        a = math.radians(arc) * i / seg_major
        ring = []
        for j in range(seg_minor):
            b = 2 * math.pi * j / seg_minor
            r = major + minor * math.cos(b)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b))))
        rings.append(ring)
    n = len(rings) if arc >= 360 else len(rings) - 1
    for i in range(n):
        r1, r2 = rings[i], rings[(i + 1) % len(rings)]
        for j in range(seg_minor):
            bm.faces.new((r1[j], r1[(j + 1) % seg_minor], r2[(j + 1) % seg_minor], r2[j]))
    return _object(name, bm, material, parent, at, rot)


def plane(name, w, d, material, parent=None, at=(0, 0, 0), rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(bm, vec=(w, d, 1), verts=bm.verts)
    return _object(name, bm, material, parent, at, rot, smooth=False)


def cut_below(obj, point, normal):
    """Remove the part of a mesh on the back side of a plane (in the object's own space)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=point, plane_no=normal, clear_inner=True)
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def solidify(obj, thickness):
    mod = obj.modifiers.new("thick", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = 0
    return obj
