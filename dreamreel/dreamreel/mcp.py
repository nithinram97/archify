"""dreamreel as an MCP server: any AI model that speaks the Model Context Protocol (Claude, ChatGPT,
local models in an MCP client) can direct a film through tools: read and write the cast, sets and
scenes, check scenes, look at frames, and render.

    dreamreel mcp path/to/film            # serves MCP over stdin/stdout

    # Claude Code:
    claude mcp add dreamreel -- dreamreel mcp /path/to/film
    # Claude Desktop and other clients (their MCP settings file):
    {"mcpServers": {"dreamreel": {"command": "dreamreel", "args": ["mcp", "/path/to/film"]}}}

The tools work at the level of the film (who, where, what happens), which AI models get right far more
often than Blender operations. Heavy work (building scenes, rendering) runs in a separate dreamreel
process, so a failure never takes the server down.
"""
import base64
import json
import os
import re
import subprocess
import sys
import tomllib

PROTOCOL = "2025-06-18"
WRITABLE = ("film.toml", "cast/", "sets/", "scenes/", "extensions/")
READABLE = WRITABLE + ("AGENTS.md", "REFERENCE.md", "motions/", "models/")

TOOLS = [
    {"name": "film", "description": "The film: title, scenes in order, cast, sets, and what has been rendered. "
                                    "Start here.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "guide", "description": "How to write dreamreel films: the project guide (AGENTS.md) and the full "
                                     "reference of cast, set and scene files (REFERENCE.md). Read before writing.",
     "inputSchema": {"type": "object", "properties": {"part": {"type": "string", "enum": ["agents", "reference", "both"],
                                                                "default": "both"}}}},
    {"name": "features", "description": "Every feature available to this film, with its settings: kinds of "
                                        "character, props, gestures, actions, moods, shots, camera moves, looks, "
                                        "voices... (including ones the film's extensions add).",
     "inputSchema": {"type": "object", "properties": {"kind": {"type": "string", "description":
                     "one kind, e.g. action, gesture, prop, character, shot, mood (omit for a list of kinds)"}}}},
    {"name": "read", "description": "Read a file of the film: film.toml, cast/<name>.toml, sets/<name>.toml, "
                                    "scenes/<NNN_name>.toml, extensions/<file>.py, AGENTS.md, REFERENCE.md.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write", "description": "Write a file of the film (film.toml, cast/, sets/, scenes/, extensions/). "
                                     "TOML is checked before it's saved. Run `check` after changing a scene.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                     "required": ["path", "content"]}},
    {"name": "check", "description": "Build scenes without rendering: each scene's timeline (who does what when, "
                                     "lines, shots) or the error and the beat that caused it.",
     "inputSchema": {"type": "object", "properties": {"scene": {"type": "string", "description":
                     "a scene number or name, e.g. 010 (omit for all)"}}}},
    {"name": "look", "description": "Render a contact sheet of frames from a scene and return it as a picture, "
                                    "to see staging, framing and acting.",
     "inputSchema": {"type": "object", "properties": {
         "scene": {"type": "string"}, "count": {"type": "integer", "default": 6, "minimum": 1, "maximum": 12},
         "previz": {"type": "boolean", "default": True, "description": "quick flat look (false: the final look, slower)"}},
         "required": ["scene"]}},
    {"name": "render", "description": "Render the film (or one scene) to video. Previz is quick and rough; final "
                                      "takes much longer. Returns the video's path.",
     "inputSchema": {"type": "object", "properties": {
         "scene": {"type": "string"}, "previz": {"type": "boolean", "default": True},
         "percent": {"type": "integer", "minimum": 10, "maximum": 100}}}},
    {"name": "voices", "description": "Voice engines and languages ready on this computer (and on a connected "
                                      "booster), and how characters' voices are set.",
     "inputSchema": {"type": "object", "properties": {}}},
]


class Film:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        if not os.path.exists(os.path.join(self.root, "film.toml")):
            raise SystemExit(f"{self.root}: no film.toml here (make one with `dreamreel new`)")

    # ------------------------------------------------------------------ helpers
    def path(self, rel, allowed):
        rel = rel.replace("\\", "/").lstrip("/")
        full = os.path.abspath(os.path.join(self.root, rel))
        if not full.startswith(self.root + os.sep) or not any(rel == a or (a.endswith("/") and rel.startswith(a))
                                                               for a in allowed):
            raise ValueError(f"{rel}: not a file this tool can use (one of: {', '.join(allowed)})")
        return full

    def dreamreel(self, *args, timeout=3600):
        """Run a dreamreel command in the film's folder; (exit code, its output without Blender's chatter)."""
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = dict(os.environ, PYTHONPATH=here + os.pathsep + os.environ.get("PYTHONPATH", ""), PYTHONUNBUFFERED="1")
        r = subprocess.run([sys.executable, "-m", "dreamreel", *args], cwd=self.root, capture_output=True, text=True,
                           timeout=timeout, env=env)
        lines = [ln for ln in (r.stdout + r.stderr).splitlines()
                 if not re.search(r"EGL|^Fra:|\| render |^Warning|Blender create|glTF import|INFO:", ln)]
        return r.returncode, lines

    def _json(self, lines):
        for ln in lines:
            if ln.startswith("@@JSON "):
                return json.loads(ln[7:])
        return None

    # ------------------------------------------------------------------ tools
    def film(self):
        with open(os.path.join(self.root, "film.toml"), "rb") as f:
            film = tomllib.load(f)

        def names(sub, ext=".toml"):
            d = os.path.join(self.root, sub)
            return sorted(os.path.splitext(f)[0] for f in os.listdir(d) if f.endswith(ext)) if os.path.isdir(d) else []
        renders = []
        for d, _, fs in os.walk(os.path.join(self.root, "renders")):
            renders += [os.path.relpath(os.path.join(d, f), self.root) for f in fs if f.endswith((".mp4", ".png"))]
        return {"folder": self.root, "film": film, "cast": names("cast"), "sets": names("sets"),
                "scenes": names("scenes") + names("scenes", ".py"), "renders": sorted(renders)[-40:]}

    def guide(self, part="both"):
        out = []
        for name in (("AGENTS.md",) if part == "agents" else ("REFERENCE.md",) if part == "reference"
                     else ("AGENTS.md", "REFERENCE.md")):
            p = os.path.join(self.root, name)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    out.append(f.read())
        return "\n\n".join(out) or "no guide files in this film"

    def features(self, kind=None):
        code, lines = self.dreamreel("info", timeout=600)
        info = self._json(lines)
        if info is None:
            raise RuntimeError("\n".join(lines[-20:]))
        plugins = info["plugins"]
        if not kind:
            return {"kinds": {k: len(v) for k, v in plugins.items()}, "catalog": info.get("catalog", {}).get("places")}
        if kind not in plugins:
            raise ValueError(f"no kind {kind!r}; kinds: {', '.join(plugins)}")
        return [{k: p[k] for k in ("name", "description", "params") if k in p} for p in plugins[kind]]

    def read(self, path):
        with open(self.path(path, READABLE), encoding="utf-8") as f:
            return f.read()

    def write(self, path, content):
        full = self.path(path, WRITABLE)
        if full.endswith(".toml"):
            tomllib.loads(content)          # a broken file is refused, not saved
        elif not full.endswith((".py", ".md", ".txt")):
            raise ValueError("write .toml (cast, sets, scenes, film) or .py (extensions) files")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        tmp = full + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, full)
        return f"saved {os.path.relpath(full, self.root)}"

    def check(self, scene=None):
        code, lines = self.dreamreel("check", *([scene] if scene else []), "--json", timeout=1800)
        out = self._json(lines)
        if out is None:
            raise RuntimeError("\n".join(lines[-30:]))
        return out

    def look(self, scene, count=6, previz=True):
        args = ["contact", str(scene), "--count", str(max(1, min(12, int(count)))), "--percent", "30"]
        code, lines = self.dreamreel(*args, *(["--previz"] if previz else []), timeout=3600)
        sheet = next((ln.strip() for ln in lines if ln.strip().endswith(".png") and os.path.isfile(ln.strip())), None)
        if code or not sheet:
            raise RuntimeError("\n".join(lines[-30:]))
        times = next((ln for ln in lines if ln.startswith("frames at:")), "")
        return sheet, times

    def render(self, scene=None, previz=True, percent=None):
        args = ["previz" if previz else "render"] + ([scene] if scene else []) + (["--percent", str(percent)] if percent else [])
        code, lines = self.dreamreel(*args, timeout=6 * 3600)
        if code:
            raise RuntimeError("\n".join(lines[-30:]))
        films = [ln.split("film: ")[-1] for ln in lines if "film: " in ln]
        return "\n".join([ln for ln in lines if ln.startswith("[dreamreel]")][-15:] + (films[-1:] if films else []))

    def voices(self):
        code, lines = self.dreamreel("voices", timeout=120)
        return "\n".join(lines)

    # ------------------------------------------------------------------ MCP
    def call(self, name, args):
        """A tool's result as MCP content."""
        if name == "look":
            sheet, times = self.look(**args)
            with open(sheet, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return [{"type": "image", "data": data, "mimeType": "image/png"},
                    {"type": "text", "text": f"{os.path.relpath(sheet, self.root)} ({times})"}]
        fn = {"film": self.film, "guide": self.guide, "features": self.features, "read": self.read,
              "write": self.write, "check": self.check, "render": self.render, "voices": self.voices}.get(name)
        if fn is None:
            raise ValueError(f"no tool {name!r}")
        out = fn(**args)
        return [{"type": "text", "text": out if isinstance(out, str) else json.dumps(out, indent=1, ensure_ascii=False)}]


def handle(film, msg):
    """One JSON-RPC message in, its reply out (None for notifications)."""
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if mid is None:
        return None                                    # notifications (initialized, cancelled ...)
    try:
        if method == "initialize":
            from . import __version__
            result = {"protocolVersion": params.get("protocolVersion") or PROTOCOL,
                      "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "dreamreel", "version": __version__},
                      "instructions": "You direct an animated film. Call `film` and `guide` first; write cast, "
                                      "sets and scenes as TOML with `write`; `check` after each change and `look` "
                                      "at the frames before rendering."}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                result = {"content": film.call(params.get("name"), dict(params.get("arguments") or {}))}
            except Exception as e:                    # a tool's failure is the model's to read, not a protocol error
                result = {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True}
        else:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    except Exception as e:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": f"{type(e).__name__}: {e}"}}


def serve(root, stdin=None, stdout=None):
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    film = Film(root)
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "not JSON"}}
        else:
            reply = handle(film, msg)
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()
