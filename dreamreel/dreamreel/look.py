"""Colours and materials for the toy look: soft vinyl plastic, warm light, shallow depth of field.

Anywhere dreamreel asks for a colour you can pass a hex string ("#e4572e") or one of the names in
`COLORS` ("red", "teal", "skin3", ...).
"""
import bpy

COLORS = {
    # skin tones, light to deep
    "skin1": "#f6dcc8", "skin2": "#eec1a0", "skin3": "#d9a07a", "skin4": "#b97a55",
    "skin5": "#8d5a3b", "skin6": "#5e3a26",
    # hair
    "black": "#1c1a1a", "brown": "#5a3825", "chestnut": "#8a4b2a", "blonde": "#e8c170",
    "ginger": "#c8562b", "grey": "#9a9a9e", "white": "#f4f1ea",
    # clothes and props
    "red": "#e4572e", "orange": "#f29e4c", "yellow": "#f1c453", "green": "#62b06f", "teal": "#2a9d8f",
    "blue": "#3d7dd8", "navy": "#26375f", "purple": "#7b5ea7", "pink": "#ef7aa1", "cream": "#f3e6cc",
    "beige": "#d9c4a0", "wood": "#b07d4f", "darkwood": "#6e4a2f", "charcoal": "#3a3a40", "denim": "#4a6fa5",
    "mint": "#a8dcc4", "sky": "#9cc9ec", "brick": "#b4553b", "leaf": "#4f9a4a", "grass": "#7cb85a",
}


def hex_to_linear(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def rgb(color):
    """Any colour spec -> linear RGB tuple."""
    if isinstance(color, (tuple, list)):
        return tuple(color[:3])
    name = str(color).lower()
    if name in COLORS:
        return hex_to_linear(COLORS[name])
    if name.lstrip("#") and all(c in "0123456789abcdef" for c in name.lstrip("#")) and len(name.lstrip("#")) == 6:
        return hex_to_linear(name)
    raise ValueError(f"Unknown colour {color!r}: use a hex code like '#e4572e' or one of {sorted(COLORS)}")


def rgba(color, alpha=1.0):
    return (*rgb(color), alpha)


_cache = {}


def _set(bsdf, name, value):
    sock = bsdf.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def plastic(color, rough=0.38, coat=0.35, emission=0.0):
    """Soft vinyl toy plastic. Materials are shared by colour, so a scene stays light."""
    k = ("plastic", rgb(color), rough, coat, emission)
    if k in _cache and _cache[k].name in bpy.data.materials:
        return _cache[k]
    mat = bpy.data.materials.new(f"plastic {color}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    _set(bsdf, "Base Color", rgba(color))
    _set(bsdf, "Roughness", rough)
    _set(bsdf, "Coat Weight", coat)
    _set(bsdf, "Coat Roughness", 0.25)
    _set(bsdf, "Specular IOR Level", 0.45)
    if emission:
        _set(bsdf, "Emission Color", rgba(color))
        _set(bsdf, "Emission Strength", emission)
    mat.diffuse_color = rgba(color)  # what the fast previz renderer shows
    mat.roughness = rough
    _cache[k] = mat
    return mat


def skin(color, rough=0.5):
    """Skin: soft, a little light under the surface (subsurface scattering)."""
    k = ("skin", rgb(color), rough)
    if k in _cache and _cache[k].name in bpy.data.materials:
        return _cache[k]
    mat = plastic(color, rough=rough, coat=0.0).copy()
    mat.name = f"skin {color}"
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    _set(bsdf, "Subsurface Weight", 0.25)
    _set(bsdf, "Subsurface Radius", (1.0, 0.35, 0.2))
    _set(bsdf, "Subsurface Scale", 0.02)
    _set(bsdf, "Specular IOR Level", 0.35)
    _cache[k] = mat
    return mat


def hair(color):
    """Hair: soft sheen, no plastic shine (big overhead lights would turn dark hair grey)."""
    k = ("hair", rgb(color))
    if k in _cache and _cache[k].name in bpy.data.materials:
        return _cache[k]
    mat = plastic(color, rough=0.55, coat=0.0).copy()
    mat.name = f"hair {color}"
    _set(mat.node_tree.nodes.get("Principled BSDF"), "Specular IOR Level", 0.12)
    _cache[k] = mat
    return mat


def matte(color, rough=0.8):
    """Painted walls, floors and fabric."""
    return plastic(color, rough=rough, coat=0.0)


def metal(color="#c9ced3", rough=0.3):
    """Steel, aluminium, chrome (rough=0.1), brass (a gold colour)."""
    k = ("metal", rgb(color), rough)
    if k in _cache and _cache[k].name in bpy.data.materials:
        return _cache[k]
    mat = plastic(color, rough=rough, coat=0.0).copy()
    mat.name = f"metal {color}"
    _set(mat.node_tree.nodes.get("Principled BSDF"), "Metallic", 1.0)
    mat.metallic = 1.0
    _cache[k] = mat
    return mat


def glass(color="white"):
    k = ("glass", rgb(color))
    if k in _cache and _cache[k].name in bpy.data.materials:
        return _cache[k]
    mat = bpy.data.materials.new("glass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    _set(bsdf, "Base Color", rgba(color))
    _set(bsdf, "Roughness", 0.05)
    _set(bsdf, "Transmission Weight", 1.0)
    _set(bsdf, "Alpha", 0.35)
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    mat.diffuse_color = (*rgb(color), 0.3)
    _cache[k] = mat
    return mat


def reset():
    _cache.clear()
