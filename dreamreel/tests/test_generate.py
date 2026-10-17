"""AI-made models: `dreamreel generate` against a stand-in for Tripo's API (no key or network
needed), then the heavy model it returns is lightened, rigged, cast and put in a set as a prop.

    python tests/test_generate.py
"""
import http.server
import json
import os
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import bpy  # noqa: E402

import dreamreel as dr  # noqa: E402
from dreamreel import handling, models, project, tripo  # noqa: E402
from test_models import figure  # noqa: E402

KEY = "tsk_test"


class FakeTripo(http.server.BaseHTTPRequestHandler):
    """Just enough of Tripo's v3 API: upload, text/image to model, task status, the model file."""
    tasks, seen, model = {}, [], b""

    def log_message(self, *a):
        pass

    def _send(self, code, obj=None, raw=None):
        body = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorised(self):
        if self.headers.get("Authorization") != f"Bearer {KEY}":
            self._send(401, {"code": 1002, "message": "invalid api key", "suggestion": "check your key"})
            return False
        return True

    def do_POST(self):
        if not self._authorised():
            return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if self.path == "/v3/files":
            assert b'name="file"' in data and self.headers["Content-Type"].startswith("multipart/form-data")
            self.seen.append(("upload", len(data)))
            return self._send(200, {"code": 0, "data": {"file_token": "file_abc"}})
        body = json.loads(data)
        self.seen.append((self.path, body))
        tid = f"task{len(self.tasks)}"
        self.tasks[tid] = 0
        if "fail" in body.get("prompt", ""):
            self.tasks[tid] = -1
        return self._send(200, {"code": 0, "data": {"task_id": tid}})

    def do_GET(self):
        if self.path == "/files/model.glb":           # signed result links carry no key
            assert "Authorization" not in self.headers
            return self._send(200, raw=self.model)
        if not self._authorised():
            return
        tid = self.path.rsplit("/", 1)[-1]
        n = self.tasks[tid]
        if n < 0:
            return self._send(200, {"code": 0, "data": {"task_id": tid, "status": "failed", "error_msg": "no luck"}})
        self.tasks[tid] = n + 1
        if n < 1:
            return self._send(200, {"code": 0, "data": {"task_id": tid, "status": "running", "progress": 50}})
        url = f"http://127.0.0.1:{self.server.server_port}/files/model.glb"
        return self._send(200, {"code": 0, "data": {"task_id": tid, "status": "success",
                                                    "output": {"model_url": url}}})


def heavy_model(path):
    """A figure with far too many faces, as AI-made models come."""
    body = figure()
    sub = body.modifiers.new("dense", "SUBSURF")
    sub.levels = 4
    body.shape_key_clear()
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="dense")
    faces = len(body.data.polygons)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    return faces


def main():
    tripo.time.sleep = lambda s: None          # don't wait between polls
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeTripo)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    tripo.API = f"http://127.0.0.1:{server.server_port}"
    with tempfile.TemporaryDirectory() as tmp:
        glb = os.path.join(tmp, "heavy.glb")
        faces = heavy_model(glb)
        assert faces > models.FACES, faces
        with open(glb, "rb") as f:
            FakeTripo.model = f.read()

        # keys are checked before anything is sent
        for bad in ("", "sk-123"):
            os.environ["TRIPO_API_KEY"] = bad
            try:
                tripo.start(prompt="a frog")
            except tripo.TripoError as e:
                assert "TRIPO_API_KEY" in str(e) or "tsk_" in str(e), e
            else:
                raise AssertionError("a missing or wrong key is an error")
        os.environ["TRIPO_API_KEY"] = "tsk_wrong"
        try:
            tripo.start(prompt="a frog")
        except tripo.TripoError as e:
            assert "invalid api key" in str(e) and "check your key" in str(e), e
        else:
            raise AssertionError("the API's errors are reported")
        os.environ["TRIPO_API_KEY"] = KEY

        # a character from a description: asked for in an A pose, saved, cast
        film = os.path.join(tmp, "film")
        from dreamreel import cli
        cli.main(["new", film])
        os.chdir(film)
        cli.main(["generate", "frog", "--prompt", "a chubby cartoon frog", "--height", "1.1"])
        path, body = FakeTripo.seen[-1]
        assert path == "/v3/generation/text-to-model", path
        assert body["prompt"].startswith("a chubby cartoon frog") and "A pose" in body["prompt"], body
        assert body["model"] == tripo.MODEL and body["texture"] and body["face_limit"] == 20000, body
        assert os.path.getsize(os.path.join(film, "models", "frog.glb")) == len(FakeTripo.model)
        cast = open(os.path.join(film, "cast", "frog.toml")).read()
        assert 'type = "model"' in cast and 'file = "models/frog.glb"' in cast and "height = 1.1" in cast, cast
        try:
            cli.main(["generate", "frog", "--prompt", "again"])
        except SystemExit as e:
            assert "already exists" in str(e), e
        else:
            raise AssertionError("an existing model isn't replaced without --force")

        # a prop from a picture: uploaded first, no pose added, no cast file
        pic = os.path.join(tmp, "lamp.png")
        img = bpy.data.images.new("lamp", 8, 8)
        img.filepath_raw, img.file_format = pic, "PNG"
        img.save()
        cli.main(["generate", "lamp", "--image", pic, "--prop"])
        assert FakeTripo.seen[-2][0] == "upload", FakeTripo.seen[-2]
        path, body = FakeTripo.seen[-1]
        assert path == "/v3/generation/image-to-model" and body["input"] == "file_abc" and "prompt" not in body
        assert not os.path.exists(os.path.join(film, "cast", "lamp.toml"))
        try:
            cli.main(["generate", "toad", "--prompt", "fail please"])
        except SystemExit as e:
            assert "failed" in str(e) and "no luck" in str(e), e
        else:
            raise AssertionError("a failed task is reported")

        # the heavy model is lightened, rigged and acts; the prop stands in the set
        project.activate(project.find(film))
        s = dr.Scene({"kind": "room", "props": [{"type": "model", "file": "models/lamp.glb", "height": 0.8,
                                                  "place": "back-left"}]})
        frog = s.cast("frog")
        n = sum(len(m.data.polygons) for m in frog.meshes)
        assert n <= models.FACES * 1.05, ("lightened", n)
        handling.evaluate(s, 0.0)
        assert abs(frog.head_point(0.0).z - 1.1) < 0.3, frog.head_point(0.0)
        start = frog.root.matrix_world.translation.copy()
        frog.walk_to("right")
        s.finish()
        handling.evaluate(s, s.length)
        assert (frog.root.matrix_world.translation - start).length > 0.5, "it walks"
        lamp = s.bscene.objects["model"]
        assert abs(lamp.dimensions.z - 0.8) < 0.01 and len(lamp.data.polygons) <= models.FACES * 1.05
        assert "model" in s.set.marks and s.set.obstacles
        os.chdir(ROOT)
    server.shutdown()
    print("generate: all ok")


if __name__ == "__main__":
    main()
