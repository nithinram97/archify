"""Blender version shims.

Everything that changed between Blender 4.2 and 5.x lives here, so the rest of the kit (and your
scripts) never needs version checks. If a future Blender breaks something, this is the one file
to fix.
"""
import bpy

VERSION = bpy.app.version  # e.g. (4, 2, 0)


def fcurves(id_data):
    """All F-curves of an ID's action: legacy actions and the layered actions of Blender 4.4+ / 5.x."""
    ad = getattr(id_data, "animation_data", None)
    act = ad.action if ad else None
    if act is None:
        return []
    if getattr(act, "layers", None):
        try:
            from bpy_extras import anim_utils
            bag = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
            if bag:
                return list(bag.fcurves)
        except Exception:
            pass
        found = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in getattr(strip, "channelbags", []):
                    found.extend(bag.fcurves)
        return found
    return list(getattr(act, "fcurves", []))


def eevee_engine():
    """The EEVEE engine id: BLENDER_EEVEE_NEXT in 4.2-4.x, BLENDER_EEVEE before and in 5.x."""
    items = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    return "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in items else "BLENDER_EEVEE"


def make_blended(mat):
    """Let a material fade (alpha blending) in both the old and the new EEVEE."""
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    if hasattr(mat, "blend_method"):
        try:
            mat.blend_method = "BLEND"
        except TypeError:
            pass
    if hasattr(mat, "use_backface_culling"):
        mat.use_backface_culling = False


def sequence_strips(scene):
    """The video sequencer strip collection: `strips` in Blender 5.x, `sequences` before."""
    se = scene.sequence_editor_create()
    return se.strips if hasattr(se, "strips") else se.sequences


def compositor_tree(scene, name="motionkit compositor"):
    """Return (tree, output_node) for the scene compositor, in the 5.x node-group style or the classic one."""
    if hasattr(scene, "compositing_node_group"):  # Blender 5.x
        tree = bpy.data.node_groups.new(name, "CompositorNodeTree")
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        scene.compositing_node_group = tree
        return tree, tree.nodes.new("NodeGroupOutput")
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    return tree, tree.nodes.new("CompositorNodeComposite")


def configure_glare(node, kind="BLOOM", threshold=0.85, size=0.7, strength=1.0):
    """Set up a Glare node whether its settings are node properties (<= 4.3) or inputs (4.4+ / 5.x)."""
    for attr, val in (("glare_type", kind), ("glare_type", "FOG_GLOW"), ("quality", "HIGH"),
                      ("size", 8), ("threshold", threshold), ("mix", 0.0)):
        if hasattr(node, attr):
            try:
                setattr(node, attr, val)
                if attr == "glare_type":
                    break
            except (TypeError, ValueError):
                continue
    for attr, val in (("quality", "HIGH"), ("size", 8), ("threshold", threshold), ("mix", 0.0)):
        if hasattr(node, attr):
            try:
                setattr(node, attr, val)
            except (TypeError, ValueError):
                pass
    nice = {"BLOOM": ("Bloom", "BLOOM", "Fog Glow", "FOG_GLOW"), "FOG_GLOW": ("Fog Glow", "FOG_GLOW"),
            "STREAKS": ("Streaks", "STREAKS")}.get(kind, (kind,))
    for name, vals in (("Type", nice), ("Quality", ("High", "HIGH")), ("Threshold", (threshold,)),
                       ("Highlights Threshold", (threshold,)), ("Strength", (strength,)), ("Size", (size,))):
        sock = node.inputs.get(name) if hasattr(node.inputs, "get") else None
        if sock is None:
            continue
        for v in vals:
            try:
                sock.default_value = v
                break
            except Exception:
                continue


def multiply_node(tree, a, b, factor):
    """Multiply two colour outputs in a compositor tree; returns the output socket."""
    try:
        mix = tree.nodes.new("CompositorNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        tree.links.new(a, mix.inputs[1])
        tree.links.new(b, mix.inputs[2])
        mix.inputs[0].default_value = factor
        return mix.outputs[0]
    except Exception:  # Blender 5.x: the generic Mix node
        mix = tree.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        sock = lambda socks, ident: next(s for s in socks if s.identifier == ident)
        sock(mix.inputs, "Factor_Float").default_value = factor
        tree.links.new(a, sock(mix.inputs, "A_Color"))
        tree.links.new(b, sock(mix.inputs, "B_Color"))
        return sock(mix.outputs, "Result_Color")


def set_video_output(render):
    """Switch the render output to an H.264 MP4 file (5.x needs media_type first)."""
    try:
        render.image_settings.media_type = "VIDEO"
    except (AttributeError, TypeError):
        pass
    render.image_settings.file_format = "FFMPEG"
    render.ffmpeg.format = "MPEG4"
    render.ffmpeg.codec = "H264"


def set_image_output(render):
    try:
        render.image_settings.media_type = "IMAGE"
    except (AttributeError, TypeError):
        pass
    render.image_settings.file_format = "PNG"
