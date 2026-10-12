"""Materials.

The kit's look is emission based (self-lit, no lights to set up) with an alpha you can animate, so
any object can fade in and out. Two flavours:

    GlowMaterial("pink", glow=2.0)            solid colour; glow > 1 triggers the bloom effect
    GlowMaterial(image="screen.png")          an image (screenshots, logos), keeps the image's own transparency

Each has three animatable handles: `.alpha`, `.strength` (glow) and `.color` (node sockets).
"""
import os

import bpy

from . import _compat
from .color import rgba


def compress_glow(strength):
    """Glow above 1 is compressed so saturated colours bloom without clipping to white."""
    return strength if strength <= 1.0 else 1.0 + (strength - 1.0) * 0.3


def load_image(path):
    """Load an image file once (reused if already loaded). Returns None, with a warning, if missing."""
    if path and os.path.exists(path):
        return bpy.data.images.load(os.path.abspath(path), check_existing=True)
    print(f"[motionkit] image not found: {path}; using a flat colour instead")
    return None


class GlowMaterial:
    """Material with animatable alpha, glow strength and colour. Two looks:

    * **glowing** (default, `lit=False`): self-lit, flat colour that ignores lights. For text, UI,
      screens, rings, lines: the motion-graphics look.
    * **lit** (`lit=True`): a real surface that is shaded by lights (`mk.Light`), with highlights and a
      dark side. For solid 3D objects: planets, products, blocks. Add at least one `mk.Light`.

    Args:
        color: any colour spec (hex, palette name, tuple).
        glow: glowing look: 1 = flat colour, 2-4 = glowing (with the bloom effect on).
              lit look: 0 = no glow (default); above 1 adds a self-glow on top of the shading.
        alpha: starting opacity 0-1.
        image: path to an image, or a loaded bpy image; the image drives the colour.
        blend: True for smooth fades; False keeps depth sorting (opaque solids such as globes).
        lit: True for the shaded look (see above).
        roughness: lit look only: 0 = mirror-glossy, 1 = matte.
        metallic: lit look only: 0 = plastic/rock, 1 = metal.
        name: material name shown in Blender.
    """

    def __init__(self, color="white", glow=None, alpha=1.0, image=None, blend=True, name="motionkit",
                 lit=False, roughness=0.6, metallic=0.0):
        self.lit = lit
        glow = (0.0 if lit else 1.0) if glow is None else glow
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        nt = self.mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tr.outputs[0], mix.inputs[1])
        if lit:
            em = nt.nodes.new("ShaderNodeBsdfPrincipled")
            em.inputs["Base Color"].default_value = rgba(color)
            em.inputs["Roughness"].default_value = roughness
            em.inputs["Metallic"].default_value = metallic
            em.inputs["Emission Color"].default_value = rgba(color)
            em.inputs["Emission Strength"].default_value = max(0.0, compress_glow(glow) - 1.0) if glow > 1 else 0.0
            color_in, strength_in = em.inputs["Base Color"], em.inputs["Emission Strength"]
        else:
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = rgba(color)
            em.inputs["Strength"].default_value = compress_glow(glow)
            color_in, strength_in = em.inputs["Color"], em.inputs["Strength"]
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        self.alpha = mix.inputs[0]
        if isinstance(image, str):
            image = load_image(image)
        if image is not None:
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = image
            tex.interpolation = "Cubic"
            tex.extension = "CLIP"
            nt.links.new(tex.outputs["Color"], color_in)
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            nt.links.new(tex.outputs["Alpha"], mul.inputs[0])
            nt.links.new(mul.outputs[0], mix.inputs[0])
            self.alpha = mul.inputs[1]
        self.image = image
        self.alpha.default_value = alpha
        self.strength = strength_in
        self.color = color_in
        if blend:
            _compat.make_blended(self.mat)

    @property
    def aspect(self):
        """Width / height of the image (1.0 without an image)."""
        if self.image is None or not self.image.size[1]:
            return 1.0
        return self.image.size[0] / self.image.size[1]
