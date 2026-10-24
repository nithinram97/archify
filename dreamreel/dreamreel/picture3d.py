"""3D models from a picture, and rigging any model, with AI models on a booster.

    dreamreel generate robot --image refs/robot.png --from-picture            # a character from a drawing
    dreamreel generate lamp --image refs/lamp.jpg --from-picture --prop
    dreamreel generate dragon --image refs/dragon.png --from-picture --rig     # rigged by AI, not by shape
    dreamreel rig models/hero.glb                                              # rig a model you have

The shape comes from VAST's TripoSG (MIT), which makes a model's geometry from one picture; dreamreel
then paints it by projecting the picture onto it from the front (the back gets a mirror of the front),
which is quick and keeps the picture's colours. Characters are rigged when cast, by dreamreel (from
the silhouette); `--rig` uses VAST's UniRig (MIT) instead, which also rigs creatures with tails, wings
or many legs. Both need a booster (boost.py, docs/boosters.md).

Without a booster, `dreamreel generate` still makes models with the recipe modeller (modeler.py), with
any AI model, on any computer.
"""
import os
import shutil

MESH_SKILL = "mesh.triposg"
RIG_SKILL = "rig.unirig"


class PictureError(RuntimeError):
    pass


def _skill(env, default):
    return os.environ.get(env) or default


def _booster(skill):
    from . import boost
    b = boost.configured()
    if b is None:
        raise PictureError("models from a picture need a booster with a graphics card: see `dreamreel boost` "
                           "(free on Google Colab)")
    if not b.has(skill):
        raise PictureError(f"the connected booster can't do {skill}; update its notebook and run it again")
    return b


def make(root, name, image, paint=True, rig=False, faces=40000, seed=42, progress=print):
    """models/<name>.glb from a picture (shape on the booster, paint here); returns its path."""
    from . import boost
    if not os.path.exists(image):
        raise PictureError(f"no picture at {image}")
    b = _booster(_skill("DREAMREEL_MESH_SKILL", MESH_SKILL))
    models = os.path.join(root, "models")
    os.makedirs(models, exist_ok=True)
    work = os.path.join(models, f".{name}-making")
    os.makedirs(work, exist_ok=True)
    try:
        progress(f"making {name}'s shape from {os.path.basename(image)} on the booster (a minute or two) ...")
        out = b.run(_skill("DREAMREEL_MESH_SKILL", MESH_SKILL), {"seed": int(seed), "faces": int(faces)},
                    {"image": image}, out_dir=work, timeout=3600, log=lambda line: None)
        glb = os.path.join(models, f"{name}.glb")
        shutil.copyfile(out["model"], glb)
        if paint:
            progress("painting it from the picture")
            paint_from_picture(glb, out.get("cutout") or image)
        if rig:
            rig_model(glb, progress=progress)
        return glb
    except boost.BoostError as e:
        raise PictureError(str(e))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def rig_model(path, progress=print):
    """Rig a model with UniRig on the booster; the rigged model replaces it (the original is kept as
    <name>.unrigged.<ext>)."""
    from . import boost
    b = _booster(_skill("DREAMREEL_RIG_SKILL", RIG_SKILL))
    work = path + ".rigging"
    os.makedirs(work, exist_ok=True)
    try:
        progress(f"rigging {os.path.basename(path)} on the booster (a few minutes) ...")
        out = b.run(_skill("DREAMREEL_RIG_SKILL", RIG_SKILL), {}, {"model": path}, out_dir=work, timeout=3600,
                    log=lambda line: None)
        stem, ext = os.path.splitext(path)
        keep = f"{stem}.unrigged{ext}"
        if not os.path.exists(keep):
            shutil.copyfile(path, keep)
        dest = stem + os.path.splitext(out["model"])[1]
        shutil.copyfile(out["model"], dest)
        return dest
    except boost.BoostError as e:
        raise PictureError(str(e))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def paint_from_picture(glb, image):
    """Colour a model by projecting a picture of it (cut to the subject) onto it from the front (-Y),
    through to the back."""
    import bpy
    from . import models
    objs = models.import_file(glb)
    meshes = [o for o in objs if o.type == "MESH"]
    if not meshes:
        raise PictureError(f"{glb} has no mesh to paint")
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    w, h = max(1e-6, hi[0] - lo[0]), max(1e-6, hi[2] - lo[2])
    img = bpy.data.images.load(os.path.abspath(image))
    img.pack()
    mat = bpy.data.materials.new("picture")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "EXTEND"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.65
    for o in meshes:
        me = o.data
        uv = me.uv_layers.new(name="picture")
        mw = o.matrix_world
        for poly in me.polygons:
            for li in poly.loop_indices:
                p = mw @ me.vertices[me.loops[li].vertex_index].co
                # the picture (cut to the subject) spans the model's width and height, seen from the front
                uv.data[li].uv = ((p.x - lo[0]) / w, (p.z - lo[2]) / h)
        me.uv_layers.active = uv
        me.materials.clear()
        me.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format="GLB")
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.materials.remove(mat)
    bpy.data.images.remove(img)
