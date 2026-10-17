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
import urllib.parse
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
    os.environ["XDG_CONFIG_HOME"] = os.path.join(tmp, "config")     # keys saved by this test stay here
    try:
        film = os.path.join(tmp, "cookie")
        cli.main(["new", film, "--example"])
        server.Handler.studio = server.Studio(film)
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{httpd.server_address[1]}"

        code, st = call(base, "GET", "/api/state")
        assert code == 200 and st["project"]["film"]["title"] == "The Last Cookie", st
        assert set(st["cast"]) == {"mia", "tom", "gran", "bolt", "biscuit"} and "kitchen" in st["info"]["sets"]
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

        # new scene as beats, edit, check (no code anywhere)
        code, r = call(base, "POST", "/api/scenes", {"name": "Den talk", "set": "den", "cast": ["zara", "mia"]})
        assert code == 200 and r["file"] == "040_den_talk.toml", r
        _, got = call(base, "GET", f"/api/scenes/{r['file']}")
        spec = got["spec"]
        spec["beats"] = [{"who": "zara", "do": "sit", "seat": "sofa", "already": True},
                         {"who": "mia", "do": "enter", "where": "by_door"},
                         {"who": "mia", "do": "say", "line": "Hi!", "mood": "happy", "to": "zara"},
                         {"who": "zara", "do": "gesture", "gesture": "wave", "with_previous": True}]
        assert call(base, "PUT", f"/api/scenes/{r['file']}", {"spec": spec})[0] == 200
        _, j = call(base, "POST", "/api/jobs", {"kind": "check", "scene": r["file"]})
        res = wait_job(base, j["id"])["result"][0]
        assert "error" not in res, res
        assert any(e["kind"] == "say" and e["line"] == "Hi!" and e["beat"] == 2 for e in res["events"]), res

        # a broken beat is reported by number
        spec["beats"].append({"who": "mia", "do": "walk_to", "where": "nowhere"})
        assert call(base, "PUT", f"/api/scenes/{r['file']}", {"spec": spec})[0] == 200
        _, j = call(base, "POST", "/api/jobs", {"kind": "check", "scene": r["file"]})
        res = wait_job(base, j["id"])["result"][0]
        assert res["beat"] == 4 and "nowhere" in res["error"], res

        # the film's own extensions are offered as features
        _, info = call(base, "GET", "/api/info")
        assert any(p["name"] == "robot" and p["source"] != "built-in" for p in info["plugins"]["character"])
        assert any(p["name"] == "dance" for p in info["plugins"]["gesture"])

        # the film order picked up the new scene; files outside renders/ are refused
        with open(os.path.join(film, "film.toml"), "rb") as f:
            assert tomllib.load(f)["scenes"][-1] == "040_den_talk"
        assert call(base, "GET", "/files/film.toml")[0] == 403
        assert call(base, "POST", "/api/jobs", {"kind": "shell", "cmd": "rm -rf /"})[0] == 400

        # the 3D packs: what's installed, the people's outfits and animals, pictures of them for the pickers
        packs = info["assets"]["packs"]
        assert {"men", "women", "animals", "interior", "nature", "city", "cars"} <= set(packs)
        person = next(p for p in info["plugins"]["character"] if p["name"] == "person")
        assert {q["name"]: q["type"] for q in person["params"]}["outfit"] == "outfit"
        if packs["women"]["installed"]:
            assert "casual" in info["assets"]["outfits"]["woman"]
        for key in info["assets"]["thumbs"][:1]:
            req = urllib.request.urlopen(base + f"/thumbs/{key}.png")
            assert req.read(4) == b"\x89PNG"
        for bad in ("../film.toml", "x.txt"):
            try:
                urllib.request.urlopen(base + "/thumbs/" + urllib.parse.quote(bad, safe=""))
                raise AssertionError(bad)
            except urllib.error.HTTPError as e:
                assert e.code == 404
        assert call(base, "POST", "/api/jobs", {"kind": "assets", "pack": "../../etc"})[0] == 400

        # voices: languages and engines are offered; keys are saved but never sent back
        info = st["info"]["catalog"]
        assert info["languages"]["ta"]["native"] == "தமிழ்" and "piper" in info["voice_engines"], info.keys()
        code, keys = call(base, "PUT", "/api/keys", {"name": "FISH_API_KEY", "value": "secret-fish"})
        assert code == 200 and keys["FISH_API_KEY"]["set"] and "secret-fish" not in json.dumps(keys)
        _, st = call(base, "GET", "/api/state")
        assert st["keys"]["FISH_API_KEY"]["set"] and st["info"]["catalog"]["voice_engines"]["fish"]["available"]
        assert "secret-fish" not in json.dumps(st)
        assert not any("secret-fish" in open(os.path.join(d, f), errors="ignore").read()
                       for d, _, fs in os.walk(film) for f in fs if f.endswith(".toml")), "keys stay out of films"
        call(base, "PUT", "/api/keys", {"name": "FISH_API_KEY", "value": ""})
        assert call(base, "PUT", "/api/keys", {"name": "PATH", "value": "x"})[0] == 400
        # a voice recording: only from the studio page (its header), only sound files, into audio/samples
        wav = b"RIFF" + b"\0" * 60

        def upload(name, data, header=True):
            req = urllib.request.Request(base + "/api/upload?name=" + urllib.parse.quote(name), method="POST", data=data,
                                         headers={"Content-Type": "audio/wav", **({"X-Dreamreel": "1"} if header else {})})
            try:
                with urllib.request.urlopen(req) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read() or b"{}")
        assert upload("Ammamma Voice.wav", wav, header=False)[0] == 400
        assert upload("evil.sh", wav)[0] == 400
        code, r = upload("../Ammamma Voice.wav", wav)
        assert code == 200 and r["path"] == os.path.join("audio", "samples", "ammamma-voice.wav"), r
        assert os.path.exists(os.path.join(film, r["path"]))
        _, st = call(base, "GET", "/api/state")
        assert st["samples"] == [r["path"]]
        # a voice saved as a table round-trips, and the audition job takes it
        voice = {"language": "ta", "describe": "A warm, gentle grandmother", "speed": 0.9}
        assert call(base, "PUT", "/api/cast/zara", {"spec": {"name": "Zara", "voice": voice}})[0] == 200
        with open(os.path.join(film, "cast", "zara.toml"), "rb") as f:
            assert tomllib.load(f)["voice"] == voice
        code, r = call(base, "POST", "/api/jobs", {"kind": "voice", "who": "Zara", "voice": voice,
                                                    "text": "வணக்கம்"})
        assert code == 200
        j = wait_job(base, r["id"])
        assert j["status"] in ("done", "failed") and any("Tamil" in line or "audio/voices" in line
                                                        for line in j["log"]), j["log"][-5:]
        assert call(base, "POST", "/api/jobs", {"kind": "voice", "voice": {"name": "../../x"}})[0] == 400

        # a film with an [[edit]] list: the studio follows it and keeps it up to date
        with open(os.path.join(film, "film.toml"), "rb") as f:
            ft = tomllib.load(f)
        ft.pop("scenes", None)
        ft["edit"] = [{"scene": "020_gran", "to": 3.0}, {"scene": "010_empty_jar", "transition": "whip"},
                      {"scene": "020_gran", "from": 3.0}, {"split": ["010_empty_jar", "040_den_talk"]}]
        with open(os.path.join(film, "film.toml"), "w") as f:
            f.write(server.to_toml(ft))
        _, st = call(base, "GET", "/api/state")
        assert [x["file"] for x in st["scenes"] if x["in_film"]][:3] == ["020_gran.toml", "010_empty_jar.toml",
                                                                         "040_den_talk.toml"], st["scenes"]
        assert call(base, "PUT", "/api/film", {"scenes": ["010_empty_jar"]})[0] == 409
        _, r = call(base, "POST", "/api/scenes", {"name": "Coda", "set": "den", "cast": []})
        assert call(base, "DELETE", "/api/scenes/040_den_talk.toml")[0] == 200
        with open(os.path.join(film, "film.toml"), "rb") as f:
            edit = tomllib.load(f)["edit"]
        assert edit[-1] == {"scene": os.path.splitext(r["file"])[0]} and len(edit) == 4, edit
        assert edit[2]["from"] == 3.0 and edit[1]["transition"] == "whip"
        httpd.shutdown()
        print("OK")
    finally:
        os.environ.pop("XDG_CONFIG_HOME", None)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
