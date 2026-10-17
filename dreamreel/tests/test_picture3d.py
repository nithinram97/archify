"""Models from a picture: the booster makes the shape (here a stand-in hands back a test model; TripoSG
needs a graphics card), dreamreel paints it from the picture (red on top, blue below lands that way
round), casts it, and `--rig` keeps the original beside the rigged one.

    python tests/test_picture3d.py
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

from dreamreel import boost, cli, models, picture3d  # noqa: E402


def make_model(path):
    """A two-ball figure, as a model file."""
    before = set(bpy.data.objects)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0.3))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, 0.75))
    new = [o for o in bpy.data.objects if o not in before]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in new:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, export_format="GLB")
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)


def make_picture(path):
    """Red above, blue below."""
    img = bpy.data.images.new("pic", 32, 64)
    px = []
    for y in range(64):
        for x in range(32):
            px += [1, 0, 0, 1] if y >= 32 else [0, 0, 1, 1]    # rows go bottom up
    img.pixels = px
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def start_booster(work):
    spec = importlib.util.spec_from_file_location("dreamreel_booster_server3",
                                                  os.path.join(ROOT, "dreamreel", "booster", "server.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    got = {}
    httpd = mod.serve(port=0, host="127.0.0.1", token="k", work=work, ready=lambda h, t: got.update(port=h.server_address[1]))
    return httpd, f"http://127.0.0.1:{got['port']}"


def colour_at_top(glb):
    """The painted colour where the model is highest."""
    objs = models.import_file(glb)
    try:
        bpy.context.view_layer.update()
        meshes = [o for o in objs if o.type == "MESH"]
        best = None
        for o in meshes:
            me = o.data
            mat = me.materials[0]
            tex = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
            uv = me.uv_layers.active
            for poly in me.polygons:
                for li in poly.loop_indices:
                    z = (o.matrix_world @ me.vertices[me.loops[li].vertex_index].co).z
                    if best is None or z > best[0]:
                        best = (z, tuple(uv.data[li].uv), tex.image)
        z, (u, v), img = best
        w, h = img.size
        i = (min(h - 1, int(v * h)) * w + min(w - 1, int(u * w))) * 4
        return tuple(round(c, 2) for c in img.pixels[i:i + 3])
    finally:
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-pic3d-")
    names = ("DREAMREEL_BOOST_TEST", "DREAMREEL_BOOST_URL", "DREAMREEL_BOOST_TOKEN", "DREAMREEL_BOOST_WORK",
             "DREAMREEL_MESH_SKILL", "DREAMREEL_RIG_SKILL", "DREAMREEL_TEST_MODEL", "XDG_CONFIG_HOME")
    keep = {k: os.environ.get(k) for k in names}
    httpd = None
    cwd = os.getcwd()
    try:
        os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")
        os.environ.pop("DREAMREEL_BOOST_URL", None)
        film = os.path.join(tmp, "film")
        with redirect_stdout(io.StringIO()):
            cli.main(["new", film])
        os.chdir(film)
        shape = os.path.join(tmp, "shape.glb")
        make_model(shape)
        os.makedirs(os.path.join(film, "models", "refs"))
        pic = os.path.join(film, "models", "refs", "robot.png")
        make_picture(pic)

        # no booster: a clear message
        try:
            picture3d.make(film, "robot", pic)
            raise AssertionError("expected a message about boosters")
        except picture3d.PictureError as e:
            assert "booster" in str(e)

        os.environ.update(DREAMREEL_BOOST_TEST="1", DREAMREEL_BOOST_WORK=os.path.join(tmp, "work"),
                          DREAMREEL_MESH_SKILL="test.model", DREAMREEL_RIG_SKILL="test.model", DREAMREEL_TEST_MODEL=shape)
        httpd, url = start_booster(os.path.join(tmp, "work"))
        os.environ.update(DREAMREEL_BOOST_URL=url, DREAMREEL_BOOST_TOKEN="k")
        boost._cache.clear()
        with redirect_stdout(io.StringIO()) as out:
            cli.main(["generate", "robot", "--image", "models/refs/robot.png", "--from-picture", "--height", "1.2"])
        glb = os.path.join(film, "models", "robot.glb")
        assert os.path.exists(glb) and os.path.exists(os.path.join(film, "cast", "robot.toml")), out.getvalue()
        assert colour_at_top(glb) == (1.0, 0.0, 0.0), ("the top of the picture paints the top", colour_at_top(glb))
        assert not any(f.startswith(".robot") for f in os.listdir(os.path.join(film, "models"))), "no leftovers"

        # rigged by AI: the original is kept beside it
        with redirect_stdout(io.StringIO()):
            cli.main(["rig", "models/robot.glb"])
        assert os.path.exists(os.path.join(film, "models", "robot.unrigged.glb"))
        assert os.path.exists(glb)
        # a prop from a picture: no cast file
        with redirect_stdout(io.StringIO()) as out:
            cli.main(["generate", "lamp", "--image", "models/refs/robot.png", "--from-picture", "--prop"])
        assert os.path.exists(os.path.join(film, "models", "lamp.glb"))
        assert not os.path.exists(os.path.join(film, "cast", "lamp.toml")) and 'type = \\"model\\"' not in out.getvalue()
    finally:
        os.chdir(cwd)
        if httpd:
            httpd.shutdown()
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("picture3d: ok")


if __name__ == "__main__":
    main()
