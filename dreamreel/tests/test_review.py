"""The review loop (review.py, `dreamreel review`): a render cut into timestamped sheets of frames and
shown with the timeline to a model that can see; its notes saved; a revised scene that has to build
(a broken one goes back to be fixed); applied with the old scene kept. A stand-in model plays the AI.

    python tests/test_review.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import ai, cli, project, review  # noqa: E402

NOTES = {"summary": "Mia's entrance reads, but Tom is frozen at the window.",
         "issues": [{"start": 1.0, "end": 3.0, "who": "Tom", "defect": "doesn't move while Mia enters",
                     "fix": "have him look round at her", "severity": 1},
                    {"start": 3.5, "end": 4.5, "who": "Mia", "defect": "both arms rise as mirror images",
                     "fix": "start the surprise with one hand", "severity": 2}]}


class Stand_in:
    """Answers in turn: the notes, a scene that doesn't build, then one that does."""

    def __init__(self, scene_text):
        fixed = scene_text + '\n[[beats]]\nwho = "tom"\ndo = "look_at"\ntarget = "mia"\n'
        broken = scene_text + '\n[[beats]]\nwho = "tom"\ndo = "gesture"\ngesture = "moonwalk"\n'
        self.replies = [json.dumps(NOTES), f"```toml\n{broken}```\nTom moonwalks.",
                        f"```toml\n{fixed}```\nTom looks round at Mia as she comes in."]
        self.asked = []

    def __str__(self):
        return "stand-in"

    def ask(self, system, messages, max_tokens=64000):
        self.asked.append((system, messages))
        return self.replies.pop(0)


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-review-")
    saved_cfg = ai.configured
    try:
        dest = os.path.join(tmp, "cookie")
        cli.main(["new", dest, "--example"])
        os.chdir(dest)
        p = project.find(dest)
        scene = p.scene_path("010")
        name = os.path.splitext(os.path.basename(scene))[0]
        video = p.renders("previz", f"{name}.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=320x180:rate=24",
                        "-t", "6", "-pix_fmt", "yuv420p", video], check=True)
        sheets = review.sheets(video, os.path.join(tmp, "sheets"), fps=4)
        assert [(t0, t1) for _, t0, t1 in sheets] == [(0.0, 3.0), (3.0, 6.0)], sheets
        assert all(os.path.getsize(f) > 1000 for f, _, _ in sheets)
        print(f"  sheets: ok ({len(sheets)} sheets of 12 frames, each with its time)")

        with open(scene) as f:
            original = f.read()
        model = Stand_in(original)
        ai.configured = lambda *a, **k: model
        cli.main(["review", "010", "--apply"])
        system, messages = model.asked[0]
        parts = messages[0]["content"]
        assert "supervisor" in system and sum("image" in x for x in parts) == 2, "it saw the frames"
        assert '"events"' in parts[0]["text"] and "Mia" in parts[0]["text"], "and the timeline"
        notes = json.load(open(p.renders("previz", f"{name}.review.json")))
        assert [i["severity"] for i in notes["issues"]] == [2, 1], "worst first"
        retry = model.asked[2][1][-1]["content"][0]["text"]
        assert "doesn't build" in retry and "moonwalk" in retry, "a broken scene goes back with its error"
        with open(scene) as f:
            now = f.read()
        assert now.endswith('target = "mia"\n') and "moonwalk" not in now, "the revision that builds is applied"
        kept = os.listdir(os.path.join(dest, "scenes", ".history"))
        assert len(kept) == 1 and open(os.path.join(dest, "scenes", ".history", kept[0])).read() == original
        assert len(p.scenes()) == 3, "proposals and history aren't scenes of the film"
        print("  review, revise, apply: ok (notes worst first; the broken revision was sent back; the old scene kept)")
        print("review: all ok")
    finally:
        ai.configured = saved_cfg
        os.chdir(ROOT)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
