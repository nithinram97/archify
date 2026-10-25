"""dreamreel's MCP server, driven like an AI client would: start it, list the tools, read the guide,
write a scene, check it, look at its frames (a picture comes back), and get errors as tool results.

    python tests/test_mcp.py
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import cli  # noqa: E402

SCENE = '''set = "kitchen"
cast = ["mia", "tom"]

[[beats]]
who = "mia"
do = "enter"
where = "door"

[[beats]]
who = "mia"
do = "say"
line = "Has anyone seen my cookie?"
to = "tom"
'''


class Client:
    def __init__(self, film):
        env = dict(os.environ, PYTHONPATH=ROOT)
        self.p = subprocess.Popen([sys.executable, "-m", "dreamreel", "mcp", film], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env)
        self.n = 0

    def rpc(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})}
        if not notify:
            self.n += 1
            msg["id"] = self.n
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        if notify:
            return None
        reply = json.loads(self.p.stdout.readline())
        assert reply["id"] == self.n, reply
        return reply

    def tool(self, name, **args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})["result"]
        return r

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=30)


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-mcp-")
    try:
        film = os.path.join(tmp, "cookie")
        cli.main(["new", film, "--example"])
        c = Client(film)
        init = c.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                    "clientInfo": {"name": "test", "version": "1"}})["result"]
        assert init["serverInfo"]["name"] == "dreamreel" and "tools" in init["capabilities"], init
        c.rpc("notifications/initialized", notify=True)
        tools = {t["name"] for t in c.rpc("tools/list")["result"]["tools"]}
        assert {"film", "guide", "features", "read", "write", "check", "look", "render", "voices"} <= tools, tools

        info = json.loads(c.tool("film")["content"][0]["text"])
        assert info["film"]["title"] == "The Last Cookie" and "mia" in info["cast"], info
        assert "## " in c.tool("guide", part="reference")["content"][0]["text"]
        gestures = json.loads(c.tool("features", kind="gesture")["content"][0]["text"])
        assert any(g["name"] == "shrug" for g in gestures), gestures[:3]
        assert "mia" in c.tool("read", path="cast/mia.toml")["content"][0]["text"].lower()

        # only the film's own files, and only valid TOML
        bad = c.tool("read", path="../../etc/passwd")
        assert bad.get("isError") and "not a file" in bad["content"][0]["text"], bad
        bad = c.tool("write", path="scenes/050_x.toml", content="this is = = not toml")
        assert bad.get("isError"), bad
        assert not os.path.exists(os.path.join(film, "scenes", "050_x.toml"))

        assert "saved" in c.tool("write", path="scenes/050_mcp.toml", content=SCENE)["content"][0]["text"]
        chk = json.loads(c.tool("check", scene="050")["content"][0]["text"])
        assert chk[0]["scene"] == "050_mcp" and "error" not in chk[0], chk
        broken = SCENE.replace('do = "enter"', 'do = "teleport"')
        c.tool("write", path="scenes/050_mcp.toml", content=broken)
        chk = json.loads(c.tool("check", scene="050")["content"][0]["text"])
        assert "error" in chk[0] and "teleport" in chk[0]["error"], chk
        c.tool("write", path="scenes/050_mcp.toml", content=SCENE)

        seen = c.tool("look", scene="050", count=2, previz=True)
        assert not seen.get("isError"), seen
        img = seen["content"][0]
        assert img["type"] == "image" and base64.b64decode(img["data"])[:8] == b"\x89PNG\r\n\x1a\n"
        assert c.rpc("nope")["error"]["code"] == -32601
        c.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("mcp: ok")


if __name__ == "__main__":
    main()
