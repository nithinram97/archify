"""Blender version shims.

Everything that differs between Blender versions lives here, so the rest of dreamreel never needs
version checks. If a future Blender breaks something, this is the one file to fix.
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
