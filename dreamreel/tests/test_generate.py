"""dreamreel's modelling agent, against a stand-in AI (no key, network or GPU needed): the AI writes a
recipe, sees renders of it from four sides and corrects it; dreamreel builds, saves and casts the
result. Both ways of talking to models are covered: Anthropic's API (through its SDK, streamed)
and the OpenAI-compatible chat API (OpenAI, Gemini, OpenRouter, Ollama, LM Studio). Also: heavy
models are lightened, and models stand in sets as props.

    python tests/test_generate.py
"""
import base64
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
from dreamreel import ai, cli, handling, modeler, models, project  # noqa: E402

MATS = {"skin": {"color": "#5fb04a", "rough": 0.45}, "belly": {"color": "#d9e8a0"},
        "eye": {"color": "#f4f1ea", "rough": 0.2}, "pupil": {"color": "#1d1d24"}}


def frog(arms=True):
    """A small A-pose frog recipe, as an AI would write it (arms=False: something to correct)."""
    parts = [
        {"name": "body", "shape": "blob", "group": "body", "at": [0, 0, 0.42], "size": [0.2, 0.17, 0.24], "material": "skin"},
        {"name": "head", "shape": "blob", "group": "body", "at": [0, -0.01, 0.72], "size": [0.21, 0.18, 0.15],
         "material": "skin"},
        {"name": "thigh_l", "shape": "blob", "group": "body", "from": [0.09, 0, 0.3], "to": [0.11, 0, 0.12],
         "radius": 0.06, "material": "skin", "mirror": True},
        {"name": "shin_l", "shape": "blob", "group": "body", "from": [0.11, 0, 0.13], "to": [0.12, 0, 0.02],
         "radius": 0.05, "material": "skin", "mirror": True},
        {"name": "belly", "shape": "sphere", "at": [0, -0.11, 0.42], "size": [0.15, 0.07, 0.18], "material": "belly"},
        {"name": "eye_l", "shape": "sphere", "at": [0.1, -0.08, 0.85], "size": [0.065, 0.065, 0.065], "material": "eye",
         "mirror": True},
        {"name": "pupil_l", "shape": "sphere", "at": [0.1, -0.14, 0.85], "size": [0.025, 0.012, 0.025],
         "material": "pupil", "mirror": True},
    ]
    if arms:
        parts.append({"name": "arm_l", "shape": "capsule", "from": [0.17, 0, 0.55], "to": [0.32, 0, 0.38],
                      "radius": 0.04, "radius_to": 0.035, "material": "skin", "mirror": True})
    joints = {"hips": [0, 0, 0.3], "chest": [0, 0, 0.5], "neck": [0, 0, 0.62], "head": [0, 0, 0.88],
              "shoulder": [0.16, 0, 0.56], "elbow": [0.25, 0, 0.46], "wrist": [0.32, 0, 0.39], "hand": [0.37, 0, 0.34],
              "hip": [0.1, 0, 0.3], "knee": [0.11, 0, 0.14], "ankle": [0.12, 0, 0.04], "toe": [0.13, -0.12, 0.01]}
    return {"name": "frog", "kind": "character", "materials": MATS, "parts": parts, "joints": joints}


def modeller(turn, saw_image):
    """What the stand-in AI says on each turn of a conversation."""
    if turn == 0:
        return "Here goes: ```json\n{\"parts\": [ {\"shape\": \"sphere\" ]}\n```"          # broken JSON
    if turn == 1:
        return "A frog in an A pose.\n```json\n" + json.dumps(frog(arms=False)) + "\n```"
    if turn == 2:
        assert saw_image, "the AI is shown its model"
        return "It has no arms. Adding them.\n```json\n" + json.dumps(frog()) + "\n```"
    return "DONE"


class FakeAI(http.server.BaseHTTPRequestHandler):
    """Both APIs: POST /v1/chat/completions (OpenAI-compatible) and POST /v1/messages (Anthropic)."""
    log = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.log.append((self.path, dict(self.headers), body))
        if self.path.startswith("/v1/chat/completions"):
            if self.headers.get("Authorization") != "Bearer sk-test":
                return self._json(401, {"error": {"message": "bad key"}})
            msgs = body["messages"]
            assert msgs[0]["role"] == "system" and "modelling kit" in msgs[0]["content"]
            turn = sum(1 for m in msgs if m["role"] == "assistant")
            saw = any(p.get("type") == "image_url" and p["image_url"]["url"].startswith("data:image/png;base64,")
                      for p in msgs[-1]["content"])
            return self._json(200, {"choices": [{"message": {"role": "assistant", "content": modeller(turn, saw)},
                                                 "finish_reason": "stop"}]})
        if self.path.startswith("/v1/messages"):
            msgs = body["messages"]
            turn = sum(1 for m in msgs if m["role"] == "assistant")
            saw = any(p["type"] == "image" and base64.b64decode(p["source"]["data"])[:4] == b"\x89PNG"
                      for p in msgs[-1]["content"])
            text = "nope" if "REFUSE" in json.dumps(msgs[0]) else modeller(turn, saw)
            return self._sse(text, "refusal" if text == "nope" else "end_turn")
        self._json(404, {})

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _sse(self, text, stop):
        events = [
            ("message_start", {"type": "message_start", "message": {
                "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5", "content": [],
                "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 1}}}),
            ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
            ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}}),
            ("content_block_stop", {"type": "content_block_stop", "index": 0}),
            ("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None},
                               "usage": {"output_tokens": 5}}),
            ("message_stop", {"type": "message_stop"}),
        ]
        data = "".join(f"event: {e}\ndata: {json.dumps(d)}\n\n" for e, d in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def heavy_model(path):
    """A figure with far too many faces, as scanned or AI-made models come."""
    from test_models import figure
    body = figure()
    sub = body.modifiers.new("dense", "SUBSURF")
    sub.levels = 4
    body.shape_key_clear()
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="dense")
    faces = len(body.data.polygons)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    return faces


def kit():
    """Every shape builds; bad recipes are explained in words an AI can act on."""
    every = {"name": "all", "materials": {"m": {"color": "#c98b2a"}, "g": {"color": "#88ccee", "glass": True}}, "parts": [
        {"shape": "sphere", "at": [0, 0, 1], "size": [0.1, 0.1, 0.1], "material": "m"},
        {"shape": "box", "at": [0.5, 0, 0], "size": [0.2, 0.2, 0.2], "round": 0.02, "material": "m"},
        {"shape": "cylinder", "at": [1, 0, 0], "radius": 0.1, "radius_top": 0.05, "height": 0.3, "material": "g"},
        {"shape": "capsule", "from": [1.5, 0, 0.1], "to": [1.5, 0, 0.5], "radius": 0.05, "material": "m"},
        {"shape": "tube", "points": [[2, 0, 0.1], [2.1, 0, 0.3], [2, 0.1, 0.5]], "radius": [0.03, 0.02, 0.01]},
        {"shape": "lathe", "at": [2.5, 0, 0], "profile": [[0.05, 0], [0.1, 0.1], [0.04, 0.3]], "material": "g"},
        {"shape": "extrude", "at": [3, 0, 0], "outline": [[0, 0], [0.2, 0], [0.1, 0.3]], "depth": 0.02},
        {"shape": "torus", "at": [3.5, 0, 0.3], "radius": 0.1, "thickness": 0.02, "rotate": [90, 0, 0]},
        {"shape": "blob", "at": [4, 0, 0.3], "size": [0.2, 0.15, 0.1], "material": "m", "mirror": True, "smooth": True},
    ]}
    m = modeler.build(every)
    assert len(m.data.polygons) > 500 and min((m.matrix_world @ v.co).z for v in m.data.vertices) > -1e-4
    sheet = modeler.turnaround(m, os.path.join(tempfile.gettempdir(), "dr_turn.png"))
    img = bpy.data.images.load(sheet)
    assert tuple(img.size) == (768, 768), img.size
    blob = modeler.build({"name": "b", "parts": [{"shape": "blob", "at": [0, 0, 0.5], "size": [0.3, 0.2, 0.1]}]})
    assert abs(blob.dimensions.x - 0.6) < 0.05 and abs(blob.dimensions.z - 0.2) < 0.03, ("blobs are the size asked",
                                                                                          blob.dimensions)
    for bad, says in (({"parts": []}, "parts"), ({"parts": [{"shape": "cube"}]}, "unknown shape"),
                      ({"parts": [{"shape": "sphere", "at": [0, 0]}]}, "3 numbers"),
                      ({"parts": [{"shape": "sphere", "at": [0, 0, 0], "size": 1, "material": "x"}]}, "isn't in materials"),
                      (dict(frog(), joints=None), "needs \"joints\""),
                      (dict(frog(), joints=dict(frog()["joints"], shoulder=[-0.16, 0, 0.56])), "left side")):
        try:
            modeler.check(bad)
        except modeler.RecipeError as e:
            assert says in str(e), (bad, e)
        else:
            raise AssertionError(f"{bad} should be refused")
    assert modeler.parse("All good. DONE") is None
    try:
        modeler.parse("{not json}")
    except modeler.RecipeError as e:
        assert "JSON" in str(e)
    print("  kit: ok")


def providers(url):
    """Choosing a model: flags, film.toml, keys; clear errors when something's missing."""
    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY",
                "DREAMREEL_AI_PROVIDER", "DREAMREEL_AI_MODEL", "DREAMREEL_AI_URL"):
        os.environ.pop(var, None)
    for args, says in ((("nope",), "unknown AI provider"), (("openai", "some-model"), "OPENAI_API_KEY"),
                       (("ollama",), "which ollama model"), (("custom", "m"), "url")):
        try:
            ai.Model(*args)
        except ai.AIError as e:
            assert says in str(e), (args, e)
        else:
            raise AssertionError(f"{args} should be refused")
    try:
        ai.configured()
    except ai.AIError as e:
        assert "ollama" in str(e)
    os.environ["OPENAI_API_KEY"] = "sk-test"
    try:
        ai.configured()
    except ai.AIError as e:
        assert "which openai model" in str(e), e
    m = ai.configured(model="gpt-test", url=url + "/v1")
    assert m.provider == "openai" and m.model == "gpt-test"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
    assert ai.configured().provider == "anthropic" and ai.configured().model == "claude-opus-5-5"
    local = ai.Model("ollama", "qwen2.5vl", url=url + "/nowhere")
    try:
        local.ask("hi", [{"role": "user", "content": [{"text": "hi"}]}])
    except ai.AIError as e:
        assert "HTTP 404" in str(e) or "connect" in str(e), e
    print("  providers: ok")


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeAI)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    kit()
    providers(url)
    with tempfile.TemporaryDirectory() as tmp:
        film = os.path.join(tmp, "film")
        cli.main(["new", film])
        os.chdir(film)
        # a character, made by a model behind the OpenAI-compatible API
        try:                    # no key for the endpoint: its refusal is passed on
            cli.main(["generate", "frog", "--prompt", "a chubby green frog",
                      "--provider", "custom", "--model", "test-vl", "--url", url + "/v1"])
        except SystemExit as e:
            assert "HTTP 401" in str(e) and "bad key" in str(e), e
        else:
            raise AssertionError("a refused key is reported")
        os.environ["DREAMREEL_AI_KEY"] = "sk-test"
        FakeAI.log.clear()
        cli.main(["generate", "frog", "--prompt", "a chubby green frog", "--height", "1.1", "--force",
                  "--provider", "custom", "--model", "test-vl", "--url", url + "/v1"])
        assert len(FakeAI.log) == 4, [p for p, _, _ in FakeAI.log]          # broken, recipe, corrected, DONE
        recipe = json.load(open(os.path.join(film, "models", "frog.json")))
        assert any(p["name"] == "arm_l" for p in recipe["parts"]), "the correction after looking is kept"
        assert os.path.getsize(os.path.join(film, "models", "frog.glb")) > 10000
        cast = open(os.path.join(film, "cast", "frog.toml")).read()
        assert 'type = "model"' in cast and "height = 1.1" in cast, cast
        # the same through Claude (Anthropic's SDK, streamed), as a prop
        try:
            import anthropic  # noqa: F401
        except ImportError:
            anthropic = None
            print("  Claude: skipped (pip install anthropic to test it)")
            cli.main(["generate", "lamp", "--spec", "models/frog.json", "--prop"])
        if anthropic is not None:
            FakeAI.log.clear()
            os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
            os.environ["ANTHROPIC_BASE_URL"] = url
            cli.main(["generate", "lamp", "--prompt", "a lamp", "--prop", "--provider", "anthropic", "--rounds", "2"])
            path, headers, body = FakeAI.log[0]
            assert body["model"] == "claude-opus-5-5" and body["thinking"] == {"type": "adaptive"}, body
            assert body.get("fallbacks") == "default" and "server-side-fallback-2026-07-01" in headers.get("anthropic-beta", "")
            assert body["output_config"]["effort"] == "high" and body["stream"] is True
            assert os.path.exists(os.path.join(film, "models", "lamp.glb"))
            assert not os.path.exists(os.path.join(film, "cast", "lamp.toml"))
            try:
                ai.Model("anthropic").ask("system", [{"role": "user", "content": [{"text": "REFUSE"}]}])
            except ai.AIError as e:
                assert "declined" in str(e), e
            else:
                raise AssertionError("a refusal is reported")
        # rebuild from an edited recipe, no AI
        recipe["materials"]["skin"]["color"] = "#3f7fd0"
        with open(os.path.join(film, "models", "frog.json"), "w") as f:
            json.dump(recipe, f)
        cli.main(["generate", "frog", "--spec", "models/frog.json"])
        # the made character acts; a heavy model is lightened; models stand in sets
        heavy = os.path.join(film, "models", "heavy.glb")
        assert heavy_model(heavy) > models.FACES
        project.activate(project.find(film))
        s = dr.Scene({"kind": "room", "props": [{"type": "model", "file": "models/lamp.glb", "height": 0.8,
                                                  "place": "back-left"}]})
        hero, big = s.cast("frog", big=dict(type="model", file="models/heavy.glb"))
        hero.place("center", facing="camera")
        big.place("right")
        assert sum(len(m.data.polygons) for m in big.meshes) <= models.FACES * 1.05, "lightened"
        start = hero.root.matrix_world.translation.copy()
        hero.do("wave")
        hero.walk_to("left")
        s.finish()
        handling.evaluate(s, 0.0)
        assert abs(hero.head_point(0.0).z - 1.1) < 0.35, hero.head_point(0.0)
        bones = {b.name: hero.rig.matrix_world @ b.head_local for b in hero.rig.data.bones}
        assert abs(bones["l_arm"].z / 1.1 - 0.56 / 0.94) < 0.05, ("the AI's skeleton is used", bones["l_arm"])
        handling.evaluate(s, s.length)
        assert (hero.root.matrix_world.translation - start).length > 0.5, "the made frog walks"
        lamp = s.bscene.objects["model"]
        assert abs(lamp.dimensions.z - 0.8) < 0.01 and "model" in s.set.marks
        os.chdir(ROOT)
    os.environ.pop("ANTHROPIC_BASE_URL", None)
    server.shutdown()
    print("generate: all ok")


if __name__ == "__main__":
    main()
