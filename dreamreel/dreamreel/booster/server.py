"""dreamreel booster: AI models on a graphics card, for a dreamreel running on another computer.

dreamreel runs on any laptop. Some of its AI helpers (Indian voices, acting from a sentence, models from
a picture, auto-rigging, faces driven by the voice, restyling) need a graphics card (NVIDIA, CUDA). A
booster is this small server, started wherever there is one:

  * free: a Google Colab or Kaggle notebook (notebooks/dreamreel-booster.ipynb starts it and makes a
    public address with a Cloudflare quick tunnel);
  * your own computer with a graphics card:  python dreamreel/booster/server.py
  * a rented cloud GPU, the same way.

It prints an address and a pass key; give them to dreamreel (the studio's Toolbox, or
`dreamreel boost connect <address> <key>`) and dreamreel sends it work. Models install and download on
first use, then stay loaded. Nothing here needs Blender or dreamreel itself: only Python 3.10+.

    python server.py [--port 8780] [--host 0.0.0.0] [--token KEY] [--prepare voice.indic_parler,...]

HTTP API (every request needs `Authorization: Bearer <key>`):
    GET  /status                   the graphics card and each skill: ready, installing, or not yet
    POST /files                    upload a file (raw body)          -> {"id": sha1}
    GET  /files/<id>               download a file
    POST /jobs                     {"skill", "inputs": {...}, "files": {"name": id}}  -> {"id"}
    GET  /jobs/<id>                {"status", "progress", "log", "outputs", "error"}
    POST /prepare                  {"skills": [...]}: install them now, in the background
"""
import argparse
import hashlib
import hmac
import json
import os
import queue
import re
import secrets
import shutil
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                      # skills.py
sys.path.insert(0, os.path.dirname(HERE))     # speakers.py (dreamreel's voice models), also needs no Blender

import skills  # noqa: E402

VERSION = 1
PASS_ON = ("HF_TOKEN",)
MAX_UPLOAD = 2 * 1024 ** 3


class Job:
    def __init__(self, skill, inputs, files):
        self.id = secrets.token_hex(8)
        self.skill, self.inputs, self.files = skill, inputs, files
        self.status, self.progress, self.error = "queued", 0.0, None
        self.log, self.outputs = [], {}
        self.created = time.time()

    def say(self, line):
        self.log = (self.log + [str(line)[:500]])[-60:]

    def as_dict(self):
        return {"id": self.id, "skill": self.skill, "status": self.status, "progress": round(self.progress, 3),
                "log": self.log[-20:], "outputs": self.outputs, "error": self.error}


class Booster:
    def __init__(self, work, token):
        self.work, self.token = work, token
        self.files = os.path.join(work, "files")
        os.makedirs(self.files, exist_ok=True)
        self.jobs = {}
        self.todo = queue.Queue()              # one graphics card: one job at a time, in order
        self.installing = {}                   # skill -> "installing" | "failed: ..."
        self.lock = threading.Lock()
        threading.Thread(target=self._worker, daemon=True).start()

    # ------------------------------------------------------------------ skills
    def status(self):
        out = {}
        for name, sk in skills.available().items():
            state = self.installing.get(name)
            if state is None:
                state = "ready" if sk.installed() else "not installed"
            out[name] = {"state": state, "ready": state == "ready", "about": sk.about, "license": sk.license,
                         "needs_gpu": sk.needs_gpu}
        return {"booster": VERSION, "gpu": skills.gpu(), "skills": out,
                "busy": sum(1 for j in self.jobs.values() if j.status in ("queued", "running"))}

    def prepare(self, name, log=print):
        sk = skills.available()[name]
        with self.lock:
            if sk.installed() or self.installing.get(name) == "installing":
                return
            self.installing[name] = "installing"
        try:
            sk.install(log)
            self.installing.pop(name, None)
        except Exception as e:
            self.installing[name] = f"failed: {e}"
            raise

    def _worker(self):
        while True:
            job = self.todo.get()
            job.status = "running"
            out_dir = tempfile.mkdtemp(prefix=f"job-{job.id}-", dir=self.work)
            try:
                sk = skills.available()[job.skill]
                if not sk.installed():
                    job.say(f"installing {job.skill} (first use: this takes a few minutes)")
                    self.prepare(job.skill, job.say)
                paths = {k: os.path.join(self.files, v) for k, v in job.files.items()}

                def progress(x):
                    job.progress = max(0.0, min(1.0, float(x)))
                outputs = sk.run(job.inputs, paths, out_dir, job.say, progress)
                for k, v in outputs.items():
                    job.outputs[k] = {"file": self.store(v)} if isinstance(v, str) and os.path.isfile(v) else v
                job.progress, job.status = 1.0, "done"
            except Exception as e:
                job.error = f"{type(e).__name__}: {e}"
                job.say(traceback.format_exc()[-1500:])
                job.status = "failed"
            finally:
                shutil.rmtree(out_dir, ignore_errors=True)

    # ------------------------------------------------------------------ files
    def store(self, path):
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        fid = h.hexdigest() + os.path.splitext(path)[1].lower()[:8]
        dest = os.path.join(self.files, fid)
        if not os.path.exists(dest):
            shutil.copyfile(path, dest + ".part")
            os.replace(dest + ".part", dest)
        return fid

    def submit(self, skill, inputs, files):
        if skill not in skills.available():
            raise KeyError(f"this booster has no skill {skill!r}")
        for v in files.values():
            if not FILE_ID.match(v) or not os.path.exists(os.path.join(self.files, v)):
                raise KeyError(f"unknown file {v!r}: upload it first")
        job = Job(skill, inputs, files)
        self.jobs[job.id] = job
        self.todo.put(job)
        return job


FILE_ID = re.compile(r"^[0-9a-f]{40}(\.[a-z0-9]{1,7})?$")


class Handler(BaseHTTPRequestHandler):
    booster = None
    server_version = "dreamreel-booster"

    def log_message(self, fmt, *args):
        pass

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorised(self):
        got = self.headers.get("Authorization", "")
        return hmac.compare_digest(got.encode(), f"Bearer {self.booster.token}".encode())

    def _route(self, method):
        if not self._authorised():
            return self._json({"error": "wrong or missing pass key"}, 401)
        parts = [p for p in self.path.split("?")[0].strip("/").split("/") if p]
        b = self.booster
        try:
            if method == "GET" and parts == ["status"]:
                return self._json(b.status())
            if method == "POST" and parts == ["files"]:
                n = int(self.headers.get("Content-Length") or 0)
                if not 0 < n <= MAX_UPLOAD:
                    return self._json({"error": "empty or too big"}, 400)
                ext = re.sub(r"[^a-z0-9.]", "", (self.headers.get("X-Extension") or "").lower())[:8]
                fd, tmp = tempfile.mkstemp(dir=b.files, suffix=".up")
                h = hashlib.sha1()
                with os.fdopen(fd, "wb") as f:
                    left = n
                    while left > 0:
                        chunk = self.rfile.read(min(1 << 20, left))
                        if not chunk:
                            break
                        h.update(chunk)
                        f.write(chunk)
                        left -= len(chunk)
                fid = h.hexdigest() + (ext if ext.startswith(".") else "")
                os.replace(tmp, os.path.join(b.files, fid))
                return self._json({"id": fid})
            if method in ("GET", "HEAD") and len(parts) == 2 and parts[0] == "files":
                if not FILE_ID.match(parts[1]):
                    return self._json({"error": "not found"}, 404)
                full = os.path.join(b.files, parts[1])
                if not os.path.isfile(full):
                    return self._json({"error": "not found"}, 404)
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(os.path.getsize(full)))
                self.end_headers()
                if method == "GET":
                    with open(full, "rb") as f:
                        shutil.copyfileobj(f, self.wfile)
                return
            if method == "POST" and parts == ["jobs"]:
                body = self._body()
                for k, v in dict(body.get("env") or {}).items():    # e.g. HF_TOKEN, for models that need one
                    if k in PASS_ON and isinstance(v, str) and v and not os.environ.get(k):
                        os.environ[k] = v
                job = b.submit(str(body.get("skill", "")), dict(body.get("inputs") or {}), dict(body.get("files") or {}))
                return self._json({"id": job.id})
            if method == "GET" and len(parts) == 2 and parts[0] == "jobs":
                job = b.jobs.get(parts[1])
                return self._json(job.as_dict()) if job else self._json({"error": "no such job"}, 404)
            if method == "POST" and parts == ["prepare"]:
                names = [n for n in self._body().get("skills", []) if n in skills.available()]
                for n in names:
                    threading.Thread(target=self._prepare, args=(n,), daemon=True).start()
                return self._json({"preparing": names})
            return self._json({"error": "not found"}, 404)
        except KeyError as e:
            return self._json({"error": str(e).strip("'\"")}, 400)
        except Exception as e:
            return self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def _prepare(self, name):
        try:
            self.booster.prepare(name)
        except Exception:
            pass

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        self._route("GET")

    def do_HEAD(self):
        self._route("HEAD")

    def do_POST(self):
        self._route("POST")


def serve(port=8780, host="0.0.0.0", token=None, work=None, prepare=(), ready=None):
    """Start a booster; returns the HTTP server (serving on a thread when `ready` is given)."""
    token = token or os.environ.get("DREAMREEL_BOOST_TOKEN") or secrets.token_urlsafe(18)
    work = work or os.path.join(os.path.expanduser("~"), ".cache", "dreamreel-booster")
    Handler.booster = Booster(work, token)
    httpd = ThreadingHTTPServer((host, port), Handler)
    for name in prepare:
        threading.Thread(target=Handler.booster.prepare, args=(name,), daemon=True).start()
    if ready is not None:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        ready(httpd, token)
        return httpd
    print(f"dreamreel booster on port {httpd.server_address[1]}  (graphics card: {skills.gpu() or 'none found'})")
    print(f"pass key: {token}")
    print("Give dreamreel this computer's address and the pass key: dreamreel boost connect <address> <key>")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return httpd


def main(argv=None):
    ap = argparse.ArgumentParser(description="dreamreel booster: AI models on a graphics card")
    ap.add_argument("--port", type=int, default=8780)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--token", help="the pass key (default: a new random one)")
    ap.add_argument("--work", help="where models and files are kept")
    ap.add_argument("--prepare", default="", help="skills to install right away, comma-separated (or 'all')")
    a = ap.parse_args(argv)
    names = list(skills.available()) if a.prepare == "all" else [n for n in a.prepare.split(",") if n]
    serve(a.port, a.host, a.token, a.work, names)


if __name__ == "__main__":
    main()
