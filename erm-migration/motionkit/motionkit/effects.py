"""Finishing effects, applied when the movie is built: glow (bloom), vignette, motion blur.

    movie.effects.glow(strength=1.0)      # bright, glowing materials bloom (glow > 1)
    movie.effects.vignette(0.35)          # darker corners
    movie.effects.motion_blur(0.5)        # smears fast motion (shutter, in frames)

Glow and vignette run in the compositor, which EEVEE in Blender 5 evaluates on the GPU.
"""
from . import _compat


class Effects:
    def __init__(self, scene):
        self.scene = scene
        self._glow = None
        self._vignette = None

    def glow(self, strength=1.0, threshold=0.85, size=0.7, kind="BLOOM"):
        """Bloom around bright materials. Only parts brighter than `threshold` glow."""
        self._glow = dict(strength=strength, threshold=threshold, size=size, kind=kind)
        return self

    def vignette(self, amount=0.35):
        """Darken the corners (0 = off, 0.5 = strong)."""
        self._vignette = amount
        return self

    def motion_blur(self, shutter=0.5):
        """Motion blur; `shutter` 0.5 is cinematic, 1.0 smears more (whip pans)."""
        r = self.scene.render
        if hasattr(r, "use_motion_blur"):
            r.use_motion_blur = True
            r.motion_blur_shutter = shutter
        ee = self.scene.eevee
        if hasattr(ee, "use_motion_blur"):  # EEVEE before 4.2
            ee.use_motion_blur = True
            ee.motion_blur_shutter = shutter
        if hasattr(ee, "motion_blur_steps"):
            ee.motion_blur_steps = 1
        return self

    def build(self):
        """Create the compositor nodes (called by Movie.finish)."""
        if self._glow is None and self._vignette is None:
            return
        scene = self.scene
        if hasattr(scene.render, "compositor_device"):
            try:
                scene.render.compositor_device = "GPU"
            except TypeError:
                pass
        try:
            tree, out = _compat.compositor_tree(scene)
            rl = tree.nodes.new("CompositorNodeRLayers")
            last = rl.outputs["Image"]
            if self._glow:
                g = tree.nodes.new("CompositorNodeGlare")
                _compat.configure_glare(g, **self._glow)
                tree.links.new(last, g.inputs[0])
                last = g.outputs[0]
            if self._vignette:
                ell = tree.nodes.new("CompositorNodeEllipseMask")
                for attr, val in (("width", 1.15), ("height", 1.0)):
                    if hasattr(ell, attr):
                        setattr(ell, attr, val)
                for name, val in (("Size", (1.15, 1.0)),):
                    s = ell.inputs.get(name) if hasattr(ell.inputs, "get") else None
                    if s is not None:
                        try:
                            s.default_value = val
                        except Exception:
                            pass
                blur = tree.nodes.new("CompositorNodeBlur")
                for attr, val in (("size_x", 400), ("size_y", 400)):
                    if hasattr(blur, attr):
                        setattr(blur, attr, val)
                s = blur.inputs.get("Size") if hasattr(blur.inputs, "get") else None
                if s is not None:
                    try:
                        s.default_value = (400, 400)
                    except Exception:
                        pass
                tree.links.new(ell.outputs[0], blur.inputs[0])
                last = _compat.multiply_node(tree, last, blur.outputs[0], self._vignette)
            tree.links.new(last, out.inputs[0])
        except Exception as exc:  # effects are optional: never fail a render because of them
            print("[motionkit] effects skipped:", exc)
