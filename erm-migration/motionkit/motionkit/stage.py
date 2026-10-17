"""Where new objects go.

Every object the kit creates is linked into the *current stage*: the movie's collection, or a shot's
stage while you are inside `with movie.shot(...)`. A shot stage sits at its own spot in the world,
so jumping the camera from one shot to the next is a clean cut, and positions inside a shot are
always relative to that shot.
"""
import bpy
from mathutils import Vector


class _Stage:
    def __init__(self):
        self.collection = None
        self.root = None            # empty every new object is parented to (a shot's origin)
        self.origin = Vector((0, 0, 0))

    def link(self, obj):
        coll = self.collection or bpy.context.scene.collection
        coll.objects.link(obj)
        if self.root is not None and obj.parent is None:
            obj.parent = self.root
        return obj

    def world(self, pos):
        """Shot-relative position -> world position (used by the camera)."""
        return self.origin + Vector(pos)


STAGE = _Stage()


def new_collection(name, parent=None):
    coll = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(coll)
    return coll
