"""Boosters: dreamreel's AI helpers that need a graphics card, run on one somewhere else.

A booster (booster/server.py) runs on a free Google Colab or Kaggle notebook, on your own computer
with a graphics card, or on a rented one. Connect it once:

    dreamreel boost connect https://something.trycloudflare.com <pass key>
    dreamreel boost                       # what it can do: voices, acting, models, rigging, faces ...

(or paste the address and key in the studio's Toolbox). The address and key are saved on this
computer (userkeys.py), never in a film's folder. A film can also name one in film.toml:

    [boost]
    url = "http://192.168.1.20:8780"      # e.g. a desktop with a graphics card at home

Whatever uses a booster also works without one, more slowly on this computer or in a simpler way.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

PASS_ON = ("HF_TOKEN",)
# the free notebook that starts a booster, opened straight in Google Colab
NOTEBOOK = ("https://colab.research.google.com/github/nithinram97/archify/blob/"
            "claude/slate-code-json-upload-n9rp3l/dreamreel/notebooks/dreamreel-booster.ipynb")     # keys a booster may need for the models it downloads (sent with jobs)


class BoostError(RuntimeError):
    pass


class Booster:
    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.token = token or ""
        self._status, self._when = None, 0.0

    def __str__(self):
        return self.url

    def _req(self, method, path, body=None, data=None, headers=None, timeout=60):
        h = {"Authorization": f"Bearer {self.token}", "User-Agent": "dreamreel"}
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        req = urllib.request.Request(self.url + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                return json.loads(raw) if r.headers.get("Content-Type", "").startswith("application/json") else raw
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read()).get("error")
            except Exception:
                msg = e.reason
            if e.code == 401:
                raise BoostError("the booster refused the pass key (connect again with the key it printed)")
            raise BoostError(f"booster: {e.code} {msg}")
        except (urllib.error.URLError, OSError) as e:
            raise BoostError(f"couldn't reach the booster at {self.url} ({getattr(e, 'reason', e)}); "
                             f"is the notebook still running?")

    def status(self, fresh=False):
        """{"gpu", "skills": {name: {"ready", "state", "about", ...}}}, checked at most every 30 s (an
        unreachable booster too, so a film doesn't wait on it line after line)."""
        if fresh or time.time() - self._when > 30:
            self._when = time.time()
            try:
                self._status = self._req("GET", "/status", timeout=15)
            except BoostError as e:
                self._status = e
        if isinstance(self._status, BoostError):
            raise self._status
        return self._status

    def has(self, skill):
        try:
            return skill in self.status().get("skills", {})
        except BoostError:
            return False

    def prepare(self, names):
        return self._req("POST", "/prepare", {"skills": list(names)})

    def upload(self, path):
        """Send a file once (the booster keeps files by their contents)."""
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        ext = os.path.splitext(path)[1].lower()[:8]
        fid = h.hexdigest() + ext
        try:
            self._req("HEAD", f"/files/{fid}", timeout=30)
            return fid
        except BoostError:
            pass
        with open(path, "rb") as f:
            data = f.read()
        return self._req("POST", "/files", data=data, headers={"X-Extension": ext,
                                                                "Content-Type": "application/octet-stream"},
                         timeout=600)["id"]

    def download(self, fid, dest):
        data = self._req("GET", f"/files/{fid}", timeout=600)
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        tmp = f"{dest}.{os.getpid()}.part"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, dest)
        return dest

    def run(self, skill, inputs, files=None, out_dir=".", timeout=3600, on_progress=None, log=None):
        """Run a skill and wait: returns its outputs, with files downloaded into out_dir."""
        ids = {k: self.upload(p) for k, p in (files or {}).items()}
        env = {k: os.environ[k] for k in PASS_ON if os.environ.get(k)}
        jid = self._req("POST", "/jobs", {"skill": skill, "inputs": inputs, "files": ids, "env": env})["id"]
        end, seen, delay = time.time() + timeout, 0, 0.5
        while True:
            j = self._req("GET", f"/jobs/{jid}", timeout=60)
            if log:
                for line in j.get("log", [])[seen:]:
                    log(line)
                seen = len(j.get("log", []))
            if on_progress:
                on_progress(j.get("progress", 0.0))
            if j["status"] == "done":
                break
            if j["status"] == "failed":
                raise BoostError(f"the booster's {skill} failed: {j.get('error')}")
            if time.time() > end:
                raise BoostError(f"the booster's {skill} took longer than {timeout} s")
            time.sleep(delay)
            delay = min(5.0, delay * 1.5)
        out = {}
        for k, v in j.get("outputs", {}).items():
            if isinstance(v, dict) and "file" in v:
                out[k] = self.download(v["file"], os.path.join(out_dir, k + os.path.splitext(v["file"])[1]))
            else:
                out[k] = v
        return out


_cache = {}


def configured():
    """The booster to use, or None: film.toml's [boost], else the saved address and key."""
    from . import project
    p = project.current()
    cfg = dict((p.film.get("boost") or {}) if p else {})
    url = cfg.get("url") or os.environ.get("DREAMREEL_BOOST_URL")
    token = os.environ.get("DREAMREEL_BOOST_TOKEN") or cfg.get("token")
    if not url:
        return None
    key = (url, token)
    if key not in _cache:
        _cache[key] = Booster(url, token)
    return _cache[key]


def can(skill):
    """Whether a connected booster offers this skill (installed or installable)."""
    b = configured()
    return bool(b and b.has(skill))


def summary():
    """For the studio: connected or not, the graphics card, and each skill's state."""
    b = configured()
    if b is None:
        return {"connected": False, "notebook": NOTEBOOK}
    try:
        st = b.status(fresh=True)
    except BoostError as e:
        return {"connected": True, "ok": False, "url": b.url, "error": str(e), "notebook": NOTEBOOK}
    return {"connected": True, "ok": True, "url": b.url, "gpu": st.get("gpu"), "busy": st.get("busy", 0),
            "skills": st.get("skills", {}), "notebook": NOTEBOOK}
