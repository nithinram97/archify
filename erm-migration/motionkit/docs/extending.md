# Extending the kit

## Add an asset

An asset is a class that builds Blender objects and calls `Item.__init__(obj, materials, parts)`:

```python
# in motionkit/assets.py
class Badge(Item):
    """A rounded label with text, e.g. "New"."""

    def __init__(self, text, color="pink", width=1.4, height=0.45):
        card = Card(width, height, color, glow=2)
        label = Text3D(text, height * 0.5, "white", glow=1, depth=0)
        label.obj.parent = card.obj
        label.obj.location = (0, -0.01, 0)
        super().__init__(card.obj, card.materials, [label])
```

Rules:

1. Create objects through the helpers (`_plane_object`, `_mesh_object`, `_curve_object`, other
   assets) or link them with `STAGE.link(obj)`, so they land in the current shot.
2. Use `GlowMaterial` so fades, glow and colour changes work.
3. Pass child items as `parts` so `fade_in` / `fade_out` reach them.
4. Write a docstring with every argument; add a line to `docs/api-reference.md` and a check to
   `tests/smoke_test.py`.
5. Export it in `motionkit/__init__.py`.

## Add a motion

Add a method to `Item` in `item.py` that calls `key(...)` / `socket_key(...)` and returns `self`. Start
from `value_at(self.obj, prop, at)` so it works in any order.

## Add a transition

A function in `transitions.py` taking `(movie, at, to, look_at, ...)`. Combine camera moves (end them
one frame before the cut with `_tick()`), `movie.camera.cut_to(...)` and overlay effects.

## Blender version issues

Put every version check in `_compat.py` and nowhere else.
