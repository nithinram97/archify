"""Exercises dreamreel studio's HTTP API on a copy of the example film (no browser, no rendering).

    python tests/test_studio.py
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import tomllib
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import cli  # noqa: E402
from dreamreel.studio import server  # noqa: E402


def call(base, method, path, body=None):
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def wait_job(base, jid, timeout=180):
    end = time.time() + timeout
    while time.time() < end:
        _, j = call(base, "GET", f"/api/jobs/{jid}")
        if j["status"] in ("done", "failed", "cancelled"):
            return j
        time.sleep(0.5)
    raise TimeoutError(jid)


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-studio-")
    try:
        film = os.path.join(tmp, "cookie")
        cli.main(["new", film, "--example"])
        server.Handler.studio = server.Studio(film)
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{httpd.server_address[1]}"

        code, st = call(base, "GET", "/api/state")
        assert code == 200 and st["project"]["film"]["title"] == "The Last Cookie", st
        assert set(st["cast"]) == {"mia", "tom", "gran"} and "kitchen" in st["info"]["sets"]
        assert "chair-2" in st["info"]["sets"]["kitchen"]["seats"]

        # a new character round-trips through toml
        spec = {"name": "Zara", "body": "kid", "hair": "curly", "extras": ["headphones"], "height": 1.1}
        assert call(base, "PUT", "/api/cast/zara", {"spec": spec})[0] == 200
        with open(os.path.join(film, "cast", "zara.toml"), "rb") as f:
            assert tomllib.load(f) == spec
        assert call(base, "PUT", "/api/cast/../evil", {"spec": {}})[0] in (400, 404)

        # a set with props and marks round-trips too
        s_spec = {"kind": "room", "size": "small", "walls": "#aabbcc", "props": [{"type": "sofa", "place": "back"}],
                  "marks": {"by_door": "left"}}
        assert call(base, "PUT", "/api/sets/den", {"spec": s_spec})[0] == 200
        with open(os.path.join(film, "sets", "den.toml"), "rb") as f:
            assert tomllib.load(f) == s_spec

        # new scene, edit, check
        code, r = call(base, "POST", "/api/scenes", {"name": "Den talk", "set": "den", "cast": ["zara", "mia"]})
        assert code == 200 and r["file"] == "030_den_talk.py", r
        _, text = call(base, "GET", f"/api/scenes/{r['file']}")
        body = text["text"] + 'zara.sit("sofa", already=True)\nmia.enter("by_door")\n' \
                              'mia.say("Hi!", mood="happy", to=zara)\n'
        assert call(base, "PUT", f"/api/scenes/{r['file']}", {"text": body})[0] == 200
        _, j = call(base, "POST", "/api/jobs", {"kind": "check", "scene": r["file"]})
        j = wait_job(base, j["id"])
        res = j["result"][0]
        assert "error" not in res, res
        assert any(e["kind"] == "say" and e["line"] == "Hi!" for e in res["events"]), res

        # a broken scene reports the line
        assert call(base, "PUT", f"/api/scenes/{r['file']}", {"text": body + 'mia.walk_to("nowhere")\n'})[0] == 200
        _, j = call(base, "POST", "/api/jobs", {"kind": "check", "scene": r["file"]})
        res = wait_job(base, j["id"])["result"][0]
        assert res["line"] == body.count("\n") + 1 and "nowhere" in res["error"], res

        # the film order picked up the new scene; files outside renders/ are refused
        with open(os.path.join(film, "film.toml"), "rb") as f:
            assert tomllib.load(f)["scenes"][-1] == "030_den_talk"
        assert call(base, "GET", "/files/film.toml")[0] == 403
        assert call(base, "POST", "/api/jobs", {"kind": "shell", "cmd": "rm -rf /"})[0] == 400
        httpd.shutdown()
        print("OK")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
