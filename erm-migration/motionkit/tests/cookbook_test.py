"""Runs every recipe in docs/cookbook.md (build only, no rendering) so the docs stay correct.

    blender -b -P tests/cookbook_test.py
Image and font paths in the recipes are swapped for the example assets.
"""
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import bpy  # noqa: E402,F401
import motionkit as mk  # noqa: E402,F401
from motionkit import transitions as tr  # noqa: E402,F401

IMG = os.path.join(ROOT, "examples", "assets", "react_heat.png")
text = open(os.path.join(ROOT, "docs", "cookbook.md"), encoding="utf-8").read()
recipes = re.findall(r"## (.+?)\n.*?```python\n(.*?)```", text, re.S)
failed = []
for title, code in recipes:
    code = re.sub(r'"[^"]*\.png"', repr(IMG), code).replace('"audio/theme.wav"', '"missing.wav"')
    movie = mk.Movie("cookbook", length=10, size=(320, 180))
    try:
        exec(code, {"mk": mk, "tr": tr, "movie": movie, "bpy": bpy})
        movie.finish()
        print(f"  ok    {title}")
    except Exception:
        failed.append(title)
        print(f"  FAIL  {title}")
        traceback.print_exc()
print("ALL PASSED" if not failed else f"FAILED: {failed}")
sys.exit(1 if failed else 0)
