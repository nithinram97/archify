"""dreamreel studio: a local web app for making films without touching code.

    dreamreel studio            # in a film folder, or in a folder to create films in
    -> http://127.0.0.1:8765

The server only uses the Python standard library. Everything that needs Blender (checking, rendering,
reading set marks) runs as a `dreamreel ...` command in a separate process, exactly as on the command
line, so the studio and the CLI always agree. It listens on 127.0.0.1 only.
"""
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import tomllib
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .. import userkeys

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,40}$")
SCENE_FILE = re.compile(r"^[0-9]{2,4}_[a-z0-9_]{1,40}\.(toml|py)$")


# ---------------------------------------------------------------------- toml writing
def _toml_value(v):
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k} = {_toml_value(x)}" for k, x in v.items() if x is not None) + "}"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    raise ValueError(f"can't write {v!r} to toml")


def to_toml(data, header=""):
    """Write a dict as toml: plain keys first, then [tables], then [[arrays of tables]]."""
    lines = [header.rstrip()] if header else []
    tables, arrays = [], []
    for k, v in data.items():
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, dict):
            tables.append((k, v))
        elif isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            arrays.append((k, v))
        else:
            lines.append(f"{k} = {_toml_value(v)}")
    for k, v in tables:
        lines += ["", f"[{k}]"] + [f"{json.dumps(kk) if not re.match(r'^[A-Za-z0-9_-]+$', kk) else kk} = {_toml_value(vv)}"
                                   for kk, vv in v.items() if vv not in (None, "")]
    for k, items in arrays:
        for item in items:
            lines += ["", f"[[{k}]]"] + [f"{kk} = {_toml_value(vv)}" for kk, vv in item.items()
                                         if vv not in (None, "", [])]
    return "\n".join(lines).lstrip("\n") + "\n"


# ---------------------------------------------------------------------- jobs
class Job:
    _next = 1
    _lock = threading.Lock()

    def __init__(self, kind, args, root, label):
        with Job._lock:
            self.id = Job._next
            Job._next += 1
        self.kind, self.args, self.root, self.label = kind, args, root, label
        self.status = "queued"
        self.lines = []
        self.progress = None
        self.total = None
        self.outputs = []
        self.result = None
        self.started = self.finished = None
        self.proc = None
        self.cancelled = False

    def run(self):
        self.status = "running"
        self.started = time.time()
        cmd = [sys.executable, "-u", "-m", "dreamreel", *self.args]
        env = dict(os.environ, PYTHONUNBUFFERED="1")
        try:
            self.proc = subprocess.Popen(cmd, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, bufsize=1, env=env)
        except OSError as e:
            self.lines.append(str(e))
            self.status = "failed"
            return
        frame_re = re.compile(r"(?:Append frame|Fra:)\s*(\d+)")
        for raw in self.proc.stdout:
            line = raw.rstrip("\n")
            if line.startswith("@@JSON "):
                try:
                    self.result = json.loads(line[7:])
                except ValueError:
                    pass
                continue
            m = re.search(r"\[dreamreel\] rendering .*?: (\d+) frames", line)
            if m:
                self.total = int(m.group(1))
                self.progress = 0
            m = frame_re.search(line)
            if m and self.total:
                self.progress = min(self.total, int(m.group(1)))
            if "EGL" in line or line.startswith("Fra:") or "| render " in line:
                continue  # Blender's per-frame chatter
            self.lines.append(line)
            p = line.strip()
            for cand in (p, p.split("Saved: ")[-1].strip("'") if "Saved:" in p else None,
                         p.split("film: ")[-1] if "film: " in p else None):
                if cand and os.path.isabs(cand) and os.path.isfile(cand) and cand.startswith(self.root):
                    rel = os.path.relpath(cand, self.root)
                    if rel not in self.outputs:
                        self.outputs.append(rel)
            m = re.search(r"rendered (\S+\.mp4)", line)
            if m:
                rel = m.group(1)
                if rel not in self.outputs:
                    self.outputs.append(rel)
        self.proc.wait()
        self.finished = time.time()
        if self.cancelled:
            self.status = "cancelled"
        else:
            self.status = "done" if self.proc.returncode == 0 else "failed"

    def cancel(self):
        self.cancelled = True
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        if self.status == "queued":
            self.status = "cancelled"

    def as_dict(self, since=0):
        return {"id": self.id, "kind": self.kind, "label": self.label, "status": self.status,
                "progress": self.progress, "total": self.total, "outputs": self.outputs, "result": self.result,
                "log": self.lines[since:], "log_len": len(self.lines),
                "elapsed": round((self.finished or time.time()) - self.started, 1) if self.started else 0}


class Jobs:
    """Quick jobs (check, info) run at once; renders wait their turn, one at a time."""

    def __init__(self):
        self.all = {}
        self.queue = []
        self.cv = threading.Condition()
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, kind, args, root, label, quick=False):
        job = Job(kind, args, root, label)
        self.all[job.id] = job
        if quick:
            threading.Thread(target=job.run, daemon=True).start()
        else:
            with self.cv:
                self.queue.append(job)
                self.cv.notify()
        return job

    def _worker(self):
        while True:
            with self.cv:
                while not self.queue:
                    self.cv.wait()
                job = self.queue.pop(0)
            if job.status == "queued":
                job.run()

    def recent(self):
        return [j.as_dict(len(j.lines)) for j in sorted(self.all.values(), key=lambda j: -j.id)[:30]]


JOBS = Jobs()


# ---------------------------------------------------------------------- the studio
class Studio:
    def __init__(self, start):
        self.start = os.path.abspath(start)
        self.root = None
        self.info_cache = None
        self.info_key = None
        self.info_lock = threading.Lock()
        self.open(self.start)

    def open(self, path):
        d = os.path.abspath(path)
        while True:
            if os.path.exists(os.path.join(d, "film.toml")):
                self.root = d
                self.info_cache = None
                return True
            parent = os.path.dirname(d)
            if parent == d:
                return False
            d = parent

    # ------------------------------------------------------------ reading
    def film(self):
        with open(os.path.join(self.root, "film.toml"), "rb") as f:
            return tomllib.load(f)

    def _tomls(self, folder):
        out = {}
        d = os.path.join(self.root, folder)
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if fn.endswith(".toml"):
                key = fn[:-5]
                try:
                    with open(os.path.join(d, fn), "rb") as f:
                        out[key] = tomllib.load(f)
                except tomllib.TOMLDecodeError as e:
                    out[key] = {"_error": str(e)}
        return out

    def scenes(self):
        """Scene files in film order. Beat scenes (.toml) are edited in the studio; script scenes (.py)
        are written by developers or AI agents and are only checked and rendered here."""
        film = self.film()
        d = os.path.join(self.root, "scenes")
        files = sorted(f for f in os.listdir(d) if f.endswith((".toml", ".py"))) if os.path.isdir(d) else []
        stems = {os.path.splitext(f)[0]: f for f in files}
        order = film.get("scenes")
        if film.get("edit"):   # an edit list (cross-cutting, split screens): its scenes, in first-use order
            order = list(dict.fromkeys(n for e in film["edit"] if isinstance(e, dict)
                                       for n in ([e["scene"]] if "scene" in e else e.get("split", []))))
        listed = [stems.get(os.path.splitext(s)[0], s if s.endswith((".toml", ".py")) else s + ".toml")
                  for s in order] if order else files
        out = [{"file": f, "in_film": True, "exists": f in files} for f in listed]
        out += [{"file": f, "in_film": False, "exists": True} for f in files if f not in listed]
        for s in out:
            s["kind"] = "script" if s["file"].endswith(".py") else "beats"
            s["set"] = None
            if not s["exists"]:
                continue
            path = os.path.join(d, s["file"])
            if s["kind"] == "beats":
                try:
                    with open(path, "rb") as fh:
                        spec = tomllib.load(fh)
                    s["set"] = spec.get("set")
                    s["beats"] = len(spec.get("beats", []))
                except tomllib.TOMLDecodeError as e:
                    s["error"] = str(e)
            else:
                with open(path, encoding="utf-8") as fh:
                    m = re.search(r"dr\.Scene\(\s*[\"']([^\"']+)[\"']", fh.read())
                s["set"] = m.group(1) if m else None
        return out

    def renders(self):
        out = []
        base = os.path.join(self.root, "renders")
        for dirpath, _, files in os.walk(base):
            for fn in files:
                if fn.endswith((".mp4", ".png", ".wav")):
                    full = os.path.join(dirpath, fn)
                    out.append({"path": os.path.relpath(full, self.root), "mtime": os.path.getmtime(full),
                                "size": os.path.getsize(full)})
        return sorted(out, key=lambda r: -r["mtime"])

    def music(self):
        d = os.path.join(self.root, "audio", "music")
        return sorted(os.path.join("audio", "music", f) for f in os.listdir(d)
                      if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a"))) if os.path.isdir(d) else []

    def samples(self):
        """Recordings of voices to copy (audio/samples)."""
        d = os.path.join(self.root, "audio", "samples")
        return sorted(os.path.join("audio", "samples", f) for f in os.listdir(d)
                      if f.lower().endswith(AUDIO)) if os.path.isdir(d) else []

    def info(self):
        """Plugins, catalogue and set marks, from `dreamreel info` (cached until a set or extension changes)."""
        pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        key = (max(os.path.getmtime(os.path.join(pkg, f)) for f in os.listdir(pkg) if f.endswith(".py")),
               os.path.getmtime(userkeys.path()) if os.path.exists(userkeys.path()) else 0)
        for sub in ("sets", "extensions"):  # new set files or extension classes change what's offered
            d = os.path.join(self.root, sub)
            if os.path.isdir(d):
                key += tuple((sub, f, os.path.getmtime(os.path.join(d, f))) for f in sorted(os.listdir(d)))
        with self.info_lock:
            if self.info_cache is not None and self.info_key == key:
                return self.info_cache
            r = subprocess.run([sys.executable, "-m", "dreamreel", "info"], cwd=self.root, capture_output=True,
                               text=True)
            for line in r.stdout.splitlines():
                if line.startswith("@@JSON "):
                    self.info_cache = json.loads(line[7:])
                    self.info_key = key
                    return self.info_cache
            raise RuntimeError("dreamreel info failed:\n" + (r.stdout + r.stderr)[-2000:])

    def state(self):
        if self.root is None:
            return {"project": None, "folder": self.start, "films": self._films_near()}
        return {
            "project": {"root": self.root, "film": self.film()},
            "cast": self._tomls("cast"), "sets": self._tomls("sets"), "scenes": self.scenes(),
            "renders": self.renders(), "music": self.music(), "samples": self.samples(), "info": self.info(),
            "keys": userkeys.status(),
        }

    def _films_near(self):
        out = []
        for fn in sorted(os.listdir(self.start)) if os.path.isdir(self.start) else []:
            if os.path.exists(os.path.join(self.start, fn, "film.toml")):
                out.append(os.path.join(self.start, fn))
        return out

    # ------------------------------------------------------------ writing
    def path(self, *parts):
        full = os.path.abspath(os.path.join(self.root, *parts))
        if not full.startswith(self.root + os.sep):
            raise PermissionError("outside the project")
        return full

    def write(self, rel, text):
        full = self.path(rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        tmp = full + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, full)


AUDIO = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
UPLOAD_LIMIT = 40 * 1024 * 1024


# ---------------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    studio = None
    server_version = "dreamreel-studio"

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    # ------------------------------------------------------------ helpers
    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, msg, status=400):
        self._json({"error": msg}, status)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw or b"{}")

    def _file(self, full, cache=False):
        if not os.path.isfile(full):
            return self._error("not found", 404)
        size = os.path.getsize(full)
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            if a:
                start = int(a)
                end = int(b) if b else size - 1
            else:
                start = max(0, size - int(b))
            end = min(end, size - 1)
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-cache")
        self.end_headers()
        with open(full, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def _route(self, method):
        url = urlparse(self.path)
        parts = [unquote(p) for p in url.path.strip("/").split("/") if p]
        query = parse_qs(url.query)
        st = self.studio
        try:
            if method == "GET" and (not parts or parts[0] in ("index.html",)):
                return self._file(os.path.join(STATIC, "index.html"))
            if method == "GET" and parts[0] == "static" and len(parts) == 2:
                return self._file(os.path.join(STATIC, os.path.basename(parts[1])))
            if method == "GET" and parts[0] == "thumbs" and len(parts) == 2:     # pictures of people and animals
                from .. import quaternius
                name = os.path.basename(parts[1])
                if not re.match(r"^[a-z0-9_]+\.png$", name):
                    return self._error("not found", 404)
                return self._file(os.path.join(quaternius.THUMBS, name), cache=True)
            if method == "GET" and parts[0] == "files":
                if st.root is None:
                    return self._error("no film open", 404)
                rel = "/".join(parts[1:])
                if not (rel.startswith("renders/") or rel.startswith("audio/")):
                    return self._error("not allowed", 403)
                return self._file(st.path(rel))
            if parts[0] != "api":
                return self._error("not found", 404)
            return self._api(method, parts[1:], query)
        except PermissionError as e:
            return self._error(str(e), 403)
        except (ValueError, KeyError, tomllib.TOMLDecodeError) as e:
            return self._error(f"{type(e).__name__}: {e}")
        except Exception as e:  # pragma: no cover - shown in the UI
            return self._error(f"{type(e).__name__}: {e}", 500)

    def _api(self, method, parts, query):
        st = self.studio
        what = parts[0] if parts else ""
        if what == "state" and method == "GET":
            return self._json(st.state())
        if what == "projects" and method == "POST":
            b = self._body()
            name = b.get("name", "").strip()
            if not NAME.match(name):
                return self._error("Use lower-case letters, numbers and dashes for the folder name, e.g. my-film")
            dest = os.path.join(st.start if st.root is None else os.path.dirname(st.root), name)
            args = ["new", dest] + (["--example"] if b.get("example") else [])
            r = subprocess.run([sys.executable, "-m", "dreamreel", *args], capture_output=True, text=True)
            if r.returncode:
                return self._error((r.stdout + r.stderr)[-800:])
            if b.get("title"):
                p = os.path.join(dest, "film.toml")
                with open(p, "rb") as f:
                    film = tomllib.load(f)
                film["title"] = b["title"]
                with open(p, "w") as f:
                    f.write(to_toml(film))
            st.open(dest)
            return self._json({"ok": True, "root": dest})
        if what == "open" and method == "POST":
            if not st.open(self._body().get("path", "")):
                return self._error("no film.toml in that folder")
            return self._json({"ok": True})
        if what == "keys":
            # keys never leave this computer, and are never sent back: only whether each one is set
            if method == "PUT":
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    return self._error("bad request")
                b = self._body()
                userkeys.set_key(str(b.get("name", "")), str(b.get("value", "")))
                st.info_cache = None
            return self._json(userkeys.status())
        if st.root is None:
            return self._error("no film open", 409)
        if what == "upload" and method == "POST":
            # a voice recording to copy: browsers must send this header, which other sites can't
            if self.headers.get("X-Dreamreel") != "1":
                return self._error("bad request")
            name = os.path.basename((query.get("name") or [""])[0]).lower()
            stem, ext = os.path.splitext(name)
            stem = re.sub(r"[^a-z0-9_-]+", "-", stem).strip("-")[:40]
            if not stem or ext not in AUDIO:
                return self._error(f"a sound file please ({', '.join(AUDIO)})")
            n = int(self.headers.get("Content-Length") or 0)
            if not 0 < n <= UPLOAD_LIMIT:
                return self._error("that file is too big (40 MB at most)")
            data = self.rfile.read(n)
            rel = os.path.join("audio", "samples", stem + ext)
            full = st.path(rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full + ".part", "wb") as f:
                f.write(data)
            os.replace(full + ".part", full)
            return self._json({"ok": True, "path": rel})

        if what == "film" and method == "PUT":
            b = self._body()
            film = st.film()
            if "scenes" in b and film.get("edit"):
                return self._error("This film's scene order comes from the [[edit]] list in film.toml "
                                   "(cross-cutting, split screens). Change the order there, or ask your AI agent.", 409)
            for k in ("title", "fps", "resolution", "scenes", "music", "voices", "lipsync", "style"):
                if k in b:
                    if b[k] in (None, "", []) and k in film:
                        del film[k]
                    elif b[k] not in (None, "", []):
                        film[k] = b[k]
            st.write("film.toml", to_toml(film, "# The film: written by dreamreel studio."))
            return self._json({"ok": True})

        if what in ("cast", "sets") and len(parts) == 2:
            key = parts[1]
            if not NAME.match(key):
                return self._error("Names use lower-case letters, numbers, - and _ (e.g. mia, old-tom)")
            rel = os.path.join(what, key + ".toml")
            if method == "PUT":
                spec = self._body().get("spec", {})
                header = "# A character: written by dreamreel studio." if what == "cast" else \
                    "# A set: written by dreamreel studio."
                st.write(rel, to_toml(spec, header))
                return self._json({"ok": True})
            if method == "DELETE":
                os.remove(st.path(rel))
                return self._json({"ok": True})

        if what == "scenes":
            if method == "POST" and len(parts) == 1:
                b = self._body()
                name = re.sub(r"[^a-z0-9_]+", "_", b.get("name", "").strip().lower()).strip("_") or "scene"
                existing = [s["file"] for s in st.scenes() if s["exists"]]
                nums = [int(f.split("_", 1)[0]) for f in existing if f.split("_", 1)[0].isdigit()]
                num = (max(nums) // 10 + 1) * 10 if nums else 10
                fn = f"{num:03d}_{name}.toml"
                cast = [c for c in b.get("cast", []) if NAME.match(c)]
                spec = {"set": b.get("set") or "", "cast": cast, "beats": []}
                st.write(os.path.join("scenes", fn), to_toml(spec, f"# Scene: {b.get('name', '')}. Written by dreamreel studio."))
                film = st.film()
                if film.get("edit"):
                    film["edit"] = film["edit"] + [{"scene": os.path.splitext(fn)[0]}]
                    st.write("film.toml", to_toml(film, "# The film: written by dreamreel studio."))
                elif film.get("scenes"):
                    film["scenes"] = film["scenes"] + [os.path.splitext(fn)[0]]
                    st.write("film.toml", to_toml(film, "# The film: written by dreamreel studio."))
                return self._json({"ok": True, "file": fn})
            if len(parts) == 2:
                fn = parts[1]
                if not SCENE_FILE.match(fn):
                    return self._error("scene files are named like 010_kitchen.py")
                rel = os.path.join("scenes", fn)
                if method == "GET":
                    if fn.endswith(".py"):
                        return self._json({"file": fn, "script": True})
                    with open(st.path(rel), "rb") as f:
                        return self._json({"file": fn, "spec": tomllib.load(f)})
                if method == "PUT":
                    if fn.endswith(".py"):
                        return self._error("script scenes are edited outside the studio", 403)
                    spec = self._body().get("spec", {})
                    empty = lambda v: v is None or v is False or v == "" or v == []  # noqa: E731
                    spec["beats"] = [{k: v for k, v in b.items() if not empty(v)} for b in spec.get("beats", [])]
                    st.write(rel, to_toml(spec, "# Scene written by dreamreel studio. Beats play in order;\n"
                                                "# with_previous = true starts a beat together with the one before."))
                    return self._json({"ok": True})
                if method == "DELETE":
                    os.remove(st.path(rel))
                    film = st.film()
                    stem = os.path.splitext(fn)[0]
                    if film.get("edit"):
                        film["edit"] = [e for e in film["edit"] if e.get("scene") != stem and stem not in e.get("split", [])]
                        st.write("film.toml", to_toml(film, "# The film: written by dreamreel studio."))
                    elif film.get("scenes"):
                        film["scenes"] = [s for s in film["scenes"] if os.path.splitext(s)[0] != stem]
                        st.write("film.toml", to_toml(film, "# The film: written by dreamreel studio."))
                    return self._json({"ok": True})

        if what == "jobs":
            if method == "GET" and len(parts) == 1:
                return self._json({"jobs": JOBS.recent()})
            if method == "GET" and len(parts) == 2:
                job = JOBS.all.get(int(parts[1]))
                if not job:
                    return self._error("no such job", 404)
                return self._json(job.as_dict(int(query.get("since", ["0"])[0])))
            if method == "POST" and len(parts) == 3 and parts[2] == "cancel":
                job = JOBS.all.get(int(parts[1]))
                if job:
                    job.cancel()
                return self._json({"ok": True})
            if method == "POST" and len(parts) == 1:
                return self._submit(self._body())

        if what == "info" and method == "GET":
            st.info_cache = None
            return self._json(st.info())
        return self._error("not found", 404)

    def _submit(self, b):
        """Start a dreamreel command. Only these shapes are allowed, so the page can't run anything else."""
        st = self.studio
        kind = b.get("kind")
        scene = b.get("scene")
        if scene is not None and not SCENE_FILE.match(scene):
            return self._error("bad scene")
        sc = os.path.splitext(scene)[0] if scene else None
        pct = str(int(b.get("percent", 0))) if b.get("percent") else None
        if kind == "check":
            args, label, quick = ["check", "--json"] + ([sc] if sc else []), f"Check {sc or 'film'}", True
        elif kind == "still":
            times = [str(float(t)) for t in b.get("times", [])][:6] or ["1"]
            args = ["still", sc, *times, "--percent", pct or "50"] + (["--previz"] if b.get("previz") else [])
            label, quick = f"Frame of {sc} at {', '.join(times)} s", False
        elif kind == "contact":
            args = ["contact", sc, "--count", str(int(b.get("count", 6))), "--percent", pct or "25"]
            args += ["--previz"] if b.get("previz") else []
            label, quick = f"Contact sheet of {sc}", False
        elif kind in ("previz", "render"):
            args = [kind] + ([sc] if sc else []) + (["--percent", pct] if pct else []) + \
                   (["--force"] if b.get("force") else [])
            label, quick = f"{'Previz' if kind == 'previz' else 'Final render'} of {sc or 'the film'}", False
        elif kind == "cast":
            names = [n for n in b.get("names", []) if NAME.match(n)]
            args = ["cast", *names, "--percent", pct or "40"]
            label, quick = f"Portrait of {', '.join(names) or 'the cast'}", False
        elif kind in ("plan", "view"):
            name = b.get("set", "")
            if not NAME.match(name):
                return self._error("bad set")
            args = ["plan", name] + (["--view"] if kind == "view" else [])
            label, quick = f"{'Map' if kind == 'plan' else 'View'} of {name}", False
        elif kind == "assets":
            pack = b.get("pack")
            from .. import quaternius
            if pack is not None and pack not in quaternius.PACKS:
                return self._error("unknown pack")
            args = ["assets", "--download"] + (["--pack", pack] if pack else [])
            label, quick = f"Download {pack or 'all the 3D packs'}", False
        elif kind == "thumbs":
            args, label, quick = ["assets", "--thumbs"], "Pictures of people and animals", False
        elif kind == "voice":
            voice = b.get("voice") or {}
            spec = voice if isinstance(voice, dict) else {"name": str(voice)}
            if spec.get("name") and not re.match(r"^[A-Za-z0-9_.-]{3,80}$", str(spec["name"])):
                return self._error("bad voice name")
            args = ["voices", "--say", str(b.get("text") or "Hello! This is my voice.")[:300]]
            for k, flag in (("name", "--voice"), ("language", "--language"), ("describe", "--describe"),
                            ("engine", "--engine"), ("sample", "--sample"), ("sample_text", "--sample-text"),
                            ("fish", "--fish"), ("speed", "--speed")):
                if spec.get(k) not in (None, ""):
                    args += [flag, str(spec[k])[:500]]
            if b.get("mood"):
                args += ["--mood", str(b["mood"])[:40]]
            label, quick = f"Voice of {str(b.get('who') or spec.get('name') or 'a character')[:40]}", True
        else:
            return self._error(f"unknown job {kind!r}")
        job = JOBS.submit(kind, args, st.root, label, quick)
        return self._json({"id": job.id})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_DELETE(self):
        self._route("DELETE")


def serve(folder=".", port=8765, open_browser=True):
    userkeys.load()
    Handler.studio = Studio(folder)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    where = Handler.studio.root or Handler.studio.start
    print(f"dreamreel studio: {url}  ({where})\nPress Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve(sys.argv[1] if len(sys.argv) > 1 else ".")
