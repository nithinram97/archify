"""Sculpting in code: a ball of clay and the brushes a sculptor would use on it.

Primitives make toys (see docs/modeling.md). Organic forms are made the way sculptors make them:
start from a simple mass and push, pull, inflate and smooth it at landmarks, big forms first.

    clay = Clay.sphere(radius=0.1)
    clay.stretch(lambda x, y, z: ...)              # block out the big form
    clay.inflate(clay.surface(0.03, -0.01), 0.03, -0.01)   # an eye socket
    clay.smooth(2)
    obj = clay.object("head", material)

Brushes work on the surface around a centre point with a smooth falloff; `radius` can be a number
or (rx, ry, rz) for an elongated brush. All positions are in the clay's own space.
"""
import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import shapes


def _falloff(d):
    """1 at the centre, 0 at the edge, smooth both ends."""
    d = np.clip(d, 0.0, 1.0)
    return 1 - d * d * (3 - 2 * d)


class Clay:
    def __init__(self, verts, faces):
        self.v = np.asarray(verts, dtype=float)
        self.f = [tuple(f) for f in faces]
        self._tri = np.array([(f[0], f[i], f[i + 1]) for f in self.f for i in range(1, len(f) - 1)])
        self._nbrs = None

    @classmethod
    def sphere(cls, radius=1.0, detail=5):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=radius)
        verts = [v.co[:] for v in bm.verts]
        faces = [[v.index for v in f.verts] for f in bm.faces]
        bm.free()
        return cls(verts, faces)

    # ------------------------------------------------------------------ queries
    def normals(self):
        v, t = self.v, self._tri
        fn = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
        n = np.zeros_like(v)
        for k in range(3):
            np.add.at(n, t[:, k], fn)
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        return n / np.maximum(ln, 1e-12)

    def tree(self):
        return BVHTree.FromPolygons([Vector(p) for p in self.v], self.f)

    def surface(self, x, z, side=-1):
        """The surface point seen looking at (x, z) from the front (side -1, -Y) or back (+1)."""
        hit = self.tree().ray_cast(Vector((x, side * 50.0, z)), Vector((0, -side, 0)))
        if hit[0] is None:
            return Vector((x, 0, z))
        return Vector(hit[0])

    def side_point(self, y, z, side=1):
        """The surface point seen looking at (y, z) from the side (+X for side 1)."""
        hit = self.tree().ray_cast(Vector((side * 50.0, y, z)), Vector((-side, 0, 0)))
        return Vector(hit[0]) if hit[0] is not None else Vector((0, y, z))

    def _weights(self, centre, radius):
        r = np.array(radius if isinstance(radius, (tuple, list)) else (radius,) * 3, dtype=float)
        d = np.linalg.norm((self.v - np.asarray(centre, dtype=float)) / r, axis=1)
        return _falloff(d)

    # ------------------------------------------------------------------ brushes
    def stretch(self, fn):
        """Reshape every point: fn(x, y, z) -> (x, y, z) (the block-out pass)."""
        self.v = np.array([fn(*p) for p in self.v], dtype=float)
        return self

    def inflate(self, centre, radius, amount):
        """Push the surface out along its normals (in, with a negative amount)."""
        w = self._weights(centre, radius)
        self.v = self.v + self.normals() * (w * amount)[:, None]
        return self

    def grab(self, centre, radius, offset):
        """Move the surface near a point (the grab / move brush)."""
        w = self._weights(centre, radius)
        self.v = self.v + np.outer(w, np.asarray(offset, dtype=float))
        return self

    def flatten(self, centre, radius, normal, amount=1.0):
        """Pull the surface towards a plane through the centre (planes of the head)."""
        n = np.asarray(normal, dtype=float)
        n = n / np.linalg.norm(n)
        w = self._weights(centre, radius) * amount
        dist = (self.v - np.asarray(centre, dtype=float)) @ n
        self.v = self.v - np.outer(w * dist, n)
        return self

    def smooth(self, times=1, centre=None, radius=None, amount=0.5):
        """Relax the surface (everywhere, or near a point)."""
        if self._nbrs is None:
            nb = [set() for _ in range(len(self.v))]
            for a, b, c in self._tri:
                nb[a] |= {b, c}
                nb[b] |= {a, c}
                nb[c] |= {a, b}
            self._nbrs = [list(s) for s in nb]
        w = np.full(len(self.v), amount) if centre is None else self._weights(centre, radius) * amount
        for _ in range(times):
            avg = np.array([self.v[n].mean(axis=0) for n in self._nbrs])
            self.v = self.v + (avg - self.v) * w[:, None]
        return self

    # ------------------------------------------------------------------ out
    def object(self, name, material=None, parent=None, at=(0, 0, 0)):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(p) for p in self.v], [], self.f)
        for p in me.polygons:
            p.use_smooth = True
        if material is not None:
            me.materials.append(material)
        obj = bpy.data.objects.new(name, me)
        shapes._collection().objects.link(obj)
        obj.parent = parent
        obj.location = at
        return obj
