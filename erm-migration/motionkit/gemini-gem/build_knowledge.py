"""Build gemini-gem/knowledge/motionkit-knowledge.md: one file with everything the gem needs.

    python gemini-gem/build_knowledge.py
Run it after changing the kit or its docs, then re-upload the file to the gem.
"""
import glob
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PARTS = ["docs/concepts.md", "docs/api-reference.md", "docs/shot-script.md", "docs/cookbook.md"]

out = ["# motionkit knowledge (for the motionkit Director gem)\n",
       "motionkit is a Python library for making motion-graphics videos in Blender 5 with EEVEE. "
       "Scripts run with `blender -b -P script.py -- --render`. This file has the concepts, the complete API, "
       "the Shot Script format, recipes and full example scripts. Only use the API documented here.\n"]
for part in PARTS:
    with open(os.path.join(ROOT, part), encoding="utf-8") as f:
        out.append(f"\n\n<!-- {part} -->\n\n" + f.read())
out.append("\n\n# Example scripts (complete, tested)\n")
for path in sorted(glob.glob(os.path.join(ROOT, "examples", "*.py"))):
    with open(path, encoding="utf-8") as f:
        out.append(f"\n## examples/{os.path.basename(path)}\n\n```python\n{f.read()}```\n")
dest = os.path.join(ROOT, "gemini-gem", "knowledge", "motionkit-knowledge.md")
with open(dest, "w", encoding="utf-8") as f:
    f.write("".join(out))
print("wrote", os.path.relpath(dest, ROOT), f"({os.path.getsize(dest) // 1024} KB)")
