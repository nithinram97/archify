"""Growing features (evolve.py, `dreamreel evolve`): a model writes a new class from its parent's source;
the draft is tried in a separate process in a scene made for its kind; what doesn't compile, register or
work goes back to the model with the error, a still is judged with --look, and only a working class
reaches extensions/ (a replaced one is kept). A stand-in model plays the AI.

    python tests/test_evolve.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dreamreel as dr  # noqa: E402,F401
from dreamreel import ai, cli, evolve, gestures, plugins  # noqa: E402

SYNTAX = "```python\nclass Broken(:\n```"
WRONG = '''```python
import dreamreel as dr


class Bounce(dr.Gesture):
    name = "bounce"
    description = "A bouncy jump"

    def perform(self, c, t, target=None):
        c.hop_at(t, 0.1, 0.25, 0.5)
        return c.no_such_thing(t)
```'''
GOOD = WRONG.replace("return c.no_such_thing(t)", "c.arms_up_at(t + 0.2)\n        c.arms_rest(t + 0.9)\n"
                     "        return t + 0.9")


class Stand_in:
    def __init__(self, replies):
        self.replies, self.asked = list(replies), []

    def __str__(self):
        return "stand-in"

    def ask(self, system, messages, max_tokens=64000):
        self.asked.append((system, list(messages)))        # as it was then: the conversation grows
        return self.replies.pop(0)


def main():
    assert evolve.base_class("gesture") is gestures.Gesture
    assert evolve.base_class("gesture", "wave") is plugins.get("gesture", "wave")
    assert "Wave" in evolve.brief("gesture", "farewell", "a slow sad goodbye wave", gestures.Gesture), \
        "a similar gesture comes along as an example"
    tmp = tempfile.mkdtemp(prefix="dreamreel-evolve-")
    saved = ai.configured
    try:
        dest = os.path.join(tmp, "film")
        cli.main(["new", dest])
        os.chdir(dest)
        model = Stand_in([SYNTAX, WRONG, GOOD])
        ai.configured = lambda *a, **k: model
        cli.main(["evolve", "gesture", "bounce", "a happy bounce on the spot"])
        notes = [m[1][-1]["content"][-1]["text"] for m in model.asked[1:]]
        assert "compiles" in notes[0], notes[0]
        assert "no_such_thing" in notes[1] and "Trying it failed" in notes[1], notes[1]
        path = os.path.join(dest, "extensions", "bounce.py")
        assert os.path.exists(path) and "arms_up_at" in open(path).read()
        assert not os.path.exists(os.path.join(dest, "extensions", ".drafts", "bounce.py"))
        print("  write, try, correct: ok (a syntax error and a broken move went back; the working one was kept)")

        better = GOOD.replace("0.1, 0.25", "0.2, 0.3")
        judge_no = '{"pass": false, "notes": "the arms never go up"}'
        judge_yes = '{"pass": true, "notes": ""}'
        model = Stand_in([GOOD, judge_no, better, judge_yes])
        ai.configured = lambda *a, **k: model
        cli.main(["evolve", "gesture", "bounce", "a bigger bounce", "--look", "--replace"])
        assert "image" in model.asked[1][1][0]["content"][0], "the judge saw a still"
        assert "the arms never go up" in model.asked[2][1][-1]["content"][-1]["text"], "the judgement went back"
        assert "0.2, 0.3" in open(path).read()
        kept = os.listdir(os.path.join(dest, "extensions", ".history"))
        assert kept == ["bounce.1.py"], kept
        print("  looking and replacing: ok (a still was judged; the old version kept in extensions/.history)")

        model = Stand_in([GOOD.replace('name = "bounce"', 'name = "wave"')])
        ai.configured = lambda *a, **k: model
        try:
            cli.main(["evolve", "gesture", "hop", "a little hop", "--rounds", "1"])
            raise AssertionError("a class under the wrong name isn't kept")
        except SystemExit as e:
            assert "no working gesture" in str(e), e
        assert not os.path.exists(os.path.join(dest, "extensions", "hop.py"))
        print("  nothing that fails reaches extensions/: ok")
        print("evolve: all ok")
    finally:
        ai.configured = saved
        os.chdir(ROOT)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
