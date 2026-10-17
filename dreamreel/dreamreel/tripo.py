"""AI-made models from Tripo (tripo3d.ai): describe a character or a prop, or give a picture of
one, and get a textured 3D model in the film's models/ folder, ready to cast or put in a set.

    dreamreel generate frog --prompt "a chubby green cartoon frog with big eyes"
    dreamreel generate lamp --prompt "a brass desk lamp" --prop
    dreamreel generate girl --image refs/girl.png --height 1.2

Tripo is a paid online service by VAST: you need your own API key (platform.tripo3d.ai), in the
environment as TRIPO_API_KEY. Your prompt or picture is sent to Tripo, and what it makes is yours
under Tripo's terms (not CC0), so keep it out of public repositories unless those terms allow it.

Characters come back as a still model; dreamreel rigs it when it's cast (`type = "model"`), so
character prompts ask for a figure standing in an A pose, which rigs best. Heavy meshes are
lightened when they're loaded (see models.lighten).
"""
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
import uuid

API = "https://openapi.tripo3d.ai"
MODEL = "v3.1-20260211"
POSE = ", full body, standing straight in an A pose with the arms held away from the body, facing forward"


class TripoError(RuntimeError):
    pass


def api_key():
    key = os.environ.get("TRIPO_API_KEY", "").strip()
    if not key:
        raise TripoError("set TRIPO_API_KEY to your Tripo API key (from platform.tripo3d.ai)")
    if not key.startswith("tsk_"):
        raise TripoError("TRIPO_API_KEY doesn't look like a Tripo key (they start with tsk_)")
    return key


def _call(method, path, body=None, data=None, content_type=None):
    """One request to the API; returns the response's data (unwrapped from its envelope)."""
    headers = {"Authorization": f"Bearer {api_key()}", "Accept": "application/json",
               "User-Agent": "dreamreel", "X-Tripo-Trace-ID": str(uuid.uuid4())}
    if body is not None:
        data = json.dumps(body).encode()
        content_type = "application/json"
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            out = json.loads(e.read() or b"{}")
        except ValueError:
            raise TripoError(f"Tripo: HTTP {e.code} for {path}") from None
    if out.get("code") not in (None, 0) or out.get("status") == "error":
        msg = out.get("message") or out.get("error") or "request failed"
        hint = f" ({out['suggestion']})" if out.get("suggestion") else ""
        raise TripoError(f"Tripo: {msg}{hint}")
    return out.get("data", out)


def upload(path):
    """Send a picture to Tripo; returns its file token."""
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    kind = mimetypes.guess_type(name)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
                f"Content-Type: {kind}\r\n\r\n").encode() + f.read() + f"\r\n--{boundary}--\r\n".encode()
    out = _call("POST", "/v3/files", data=body, content_type=f"multipart/form-data; boundary={boundary}")
    if not out.get("file_token"):
        raise TripoError("Tripo: the upload gave no file token")
    return out["file_token"]


def start(prompt=None, image=None, character=True, faces=20000):
    """Start making a model from a description or a picture; returns the task id."""
    common = {"model": MODEL, "face_limit": int(faces), "texture": True, "pbr": True}
    if image:
        body = dict(common, input=upload(image) if os.path.exists(image) else image)
        out = _call("POST", "/v3/generation/image-to-model", body)
    elif prompt:
        body = dict(common, prompt=prompt + (POSE if character else ""))
        out = _call("POST", "/v3/generation/text-to-model", body)
    else:
        raise TripoError("give a prompt or an image")
    if not out.get("task_id"):
        raise TripoError("Tripo: no task id in the reply")
    return out["task_id"]


def wait(task_id, progress=print, timeout=900):
    """Wait for a task to finish; returns the URL of the model it made."""
    delay, t0, last = 2.0, time.time(), None
    while True:
        task = _call("GET", f"/v3/tasks/{task_id}")
        status = task.get("status")
        if status != last or status == "running":
            progress(f"  {status} {task.get('progress', '')}".rstrip())
            last = status
        if status == "success":
            out = task.get("output") or {}
            url = out.get("model_url") or out.get("pbr_model") or out.get("model")
            if not url:
                raise TripoError("Tripo: the task finished without a model")
            return url
        if status in ("failed", "cancelled", "banned", "expired"):
            raise TripoError(f"Tripo: the task {status}: {task.get('error_msg') or task.get('error_code') or ''}".strip())
        if time.time() - t0 > timeout:
            raise TripoError(f"Tripo: still not done after {timeout} s (task {task_id})")
        time.sleep(delay)
        delay = min(30.0, delay * 2)


def download(url, path):
    """Save a finished model (result links are signed: no API key is sent with them)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "dreamreel"}), timeout=300) as r, \
            open(path, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    return path


def generate(path, prompt=None, image=None, character=True, faces=20000, progress=print):
    """Make a model and save it at `path` (a .glb)."""
    progress("Tripo: making " + ("a model from " + os.path.basename(image) if image else repr(prompt)))
    url = wait(start(prompt, image, character, faces), progress)
    return download(url, path)
