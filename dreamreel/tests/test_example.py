"""Builds the example film without rendering: every scene must build, cut and check cleanly.

    python tests/test_example.py           # build + timeline checks (seconds)
    python tests/test_example.py --render  # also render a cast picture and one final still
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dreamreel import cli, film, project  # noqa: E402


def main():
    tmp = tempfile.mkdtemp(prefix="dreamreel-test-")
    try:
        dest = os.path.join(tmp, "cookie")
        cli.main(["new", dest, "--example"])
        for f in ("AGENTS.md", "CLAUDE.md", "REFERENCE.md", "film.toml"):
            assert os.path.exists(os.path.join(dest, f)), f
        os.chdir(dest)
        p = project.find(dest)
        project.activate(p)
        for path in p.scenes():
            s = film.build(p, path)
            says = [e for e in s.events if e["kind"] == "say"]
            assert says, f"{path}: no dialogue"
            assert len(s.cut.shots) >= 3, f"{path}: only {len(s.cut.shots)} shots"
            assert not s.check(), f"{path}: {s.check()}"
            assert 5 < s.length < 120, s.length
            print(s.summary().splitlines()[0])
        # blank template too
        blank = os.path.join(tmp, "blank")
        cli.main(["new", blank])
        os.chdir(blank)
        cli.main(["check"])
        if "--render" in sys.argv:
            os.chdir(dest)
            cli.main(["cast", "--percent", "25"])
            cli.main(["still", "010", "4", "--percent", "25"])
            print("renders in", os.path.join(dest, "renders"))
            return
        print("OK")
    finally:
        if "--render" not in sys.argv:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
