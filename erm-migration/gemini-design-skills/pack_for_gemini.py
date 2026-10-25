"""Pack the claudedesignskills repo into single text files a Gemini gem can use as knowledge.

    python pack_for_gemini.py /path/to/claudedesignskills

Writes:
  design-skills-for-gemini.md          everything in one file (index first, then every skill)
  parts/design-skills-part-N.md        the same content split by category, for gems that need smaller files

Rules:
  * Takes plugins/individual (the 22 skills: SKILL.md, references, agents, commands, scripts, assets)
    plus the bundle integration agents and the top-level README, MARKETPLACE and CLAUDE.md guides.
  * Skips duplicates (plugins/bundles copies, .claude/, .factory/), Claude/Factory plumbing
    (plugin.json manifests, marketplace scripts, skill-creator, droids) and binaries (.zip, .pyc, images).
  * Replaces Claude with Gemini everywhere (Claude/claude/CLAUDE), except inside URLs, so links keep working,
    and in the original MIT licence notice, which is appended unchanged.
"""
import os
import re
import sys

SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "../../../claudedesignskills")
HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".txt", ".glsl", ".yml", ".yaml", ".sh")
SKIP_PARTS = (".claude-plugin", "__pycache__", "node_modules")

CATEGORIES = [  # parts for the split version
    ("3D engines", ["threejs-webgl", "react-three-fiber", "babylonjs-engine", "playcanvas-engine", "aframe-webxr"]),
    ("Animation", ["gsap-scrolltrigger", "motion-framer", "react-spring-physics", "animejs", "lottie-animations"]),
    ("Scroll and page transitions", ["locomotive-scroll", "barba-js", "scroll-reveal-libraries", "lightweight-3d-effects"]),
    ("2D, components and design", ["pixijs-2d", "animated-component-libraries", "modern-web-design"]),
    ("Authoring tools and integration", ["blender-web-pipeline", "spline-interactive", "rive-interactive",
                                         "substance-3d-texturing", "web3d-integration-patterns"]),
]

URL = re.compile(r"https?://\S+|git@\S+")


def to_gemini(text):
    out, last = [], 0
    for m in URL.finditer(text):
        out.append(_swap(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_swap(text[last:]))
    return "".join(out)


def _swap(s):
    return s.replace("CLAUDE", "GEMINI").replace("Claude", "Gemini").replace("claude", "gemini")


def files_of(root):
    found = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_PARTS)
        for f in sorted(fs):
            if f.endswith(TEXT) and f != "plugin.json":
                found.append(os.path.join(d, f))
    # SKILL.md first, then references, agents, commands, scripts, assets
    order = lambda p: (0 if p.endswith("SKILL.md") else 1 if "/references/" in p else 2 if "/agents/" in p
                       else 3 if "/commands/" in p else 4 if "/scripts/" in p else 5, p)
    return sorted(found, key=order)


def block(path):
    rel = to_gemini(os.path.relpath(path, SRC))
    with open(path, encoding="utf-8", errors="replace") as f:
        body = to_gemini(f.read())
    lang = os.path.splitext(path)[1].lstrip(".")
    fence = "````" if "```" in body else "```"
    return f"\n\n===== FILE: {rel} =====\n\n" + (body if lang == "md" else f"{fence}{lang}\n{body}\n{fence}") + "\n"


def description(skill_dir):
    p = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(p):
        return ""
    head = open(p, encoding="utf-8").read().split("---")
    m = re.search(r"description:\s*(.+)", head[1] if len(head) > 2 else "")
    return to_gemini(m.group(1).strip()) if m else ""


ind = os.path.join(SRC, "plugins", "individual")
skills = sorted(os.listdir(ind))
assert sum(len(c) for _, c in CATEGORIES) == len(skills), "a skill is missing from CATEGORIES"

HEADER = """# Design Skills for Gemini

This file is a library of **22 design and animation skills** (3D/WebGL, animation, scroll, 2D, design
systems and authoring tools). Each skill has a SKILL.md (when to use it, core patterns, pitfalls),
references (API notes, guides), agents (expert roles), commands (task recipes), scripts and asset templates.

**How to use this file**
1. Find the skill that matches the task in the index below (match on technology or on what the user wants to build).
2. Read that skill's `SKILL.md` first and follow its patterns, then its `references/` for API details.
3. A file under `commands/` is a ready-made recipe: when the user asks for that task (or types `/command-name`),
   follow its steps. A file under `agents/` describes an expert role you can adopt.
4. Several skills can combine (e.g. Three.js + GSAP scroll); `web3d-integration-patterns` covers how.
5. Write complete, runnable code. Prefer the versions and APIs shown in the skill; say so when you go beyond them.

Every file starts with a line `===== FILE: <path> =====`.

"""


def index(selection):
    rows = ["| Skill | Use it for |", "|---|---|"]
    for s in selection:
        rows.append(f"| `{to_gemini(s)}` | {description(os.path.join(ind, s, 'skills', s)) or '(see SKILL.md)'} |")
    return "\n".join(rows) + "\n"


def skill_text(s):
    return f"\n\n# Skill: {to_gemini(s)}\n" + "".join(block(p) for p in files_of(os.path.join(ind, s)))


extras = [os.path.join(SRC, f) for f in ("README.md", "MARKETPLACE.md", "CLAUDE.md")]
bundle_agents = sorted(os.path.join(d, f) for d, _, fs in os.walk(os.path.join(SRC, "plugins", "bundles"))
                       for f in fs if "/agents/" in os.path.join(d, f) + "/" and f.endswith("-integration.md"))
guides = "\n\n# Guides and integration agents\n" + "".join(block(p) for p in extras + bundle_agents if os.path.exists(p))

lic_path = os.path.join(SRC, "LICENSE")
LICENSE = ("\n\n# Licence (original notice, kept unchanged as the MIT licence requires)\n\n```\n"
           + open(lic_path, encoding="utf-8").read() + "\n```\n") if os.path.exists(lic_path) else ""
guides += LICENSE
full = HEADER + "## Index\n\n" + index(skills) + "".join(skill_text(s) for s in skills) + guides
with open(os.path.join(HERE, "design-skills-for-gemini.md"), "w", encoding="utf-8") as f:
    f.write(full)

os.makedirs(os.path.join(HERE, "parts"), exist_ok=True)
for i, (name, group) in enumerate(CATEGORIES, 1):
    text = HEADER.replace("# Design Skills for Gemini", f"# Design Skills for Gemini, part {i} of {len(CATEGORIES) + 1}: {name}")
    text += "## Skills in this part\n\n" + index(group) + "".join(skill_text(s) for s in group)
    with open(os.path.join(HERE, "parts", f"design-skills-part-{i}.md"), "w", encoding="utf-8") as f:
        f.write(text)
with open(os.path.join(HERE, "parts", f"design-skills-part-{len(CATEGORIES) + 1}.md"), "w", encoding="utf-8") as f:
    f.write(HEADER.replace("# Design Skills for Gemini", f"# Design Skills for Gemini, part {len(CATEGORIES) + 1}: index, guides and integration")
            + "## Index of all skills (they are in parts 1-5)\n\n" + index(skills) + guides)

left = len(re.findall(r"claude", URL.sub("", full.replace(LICENSE, "")), re.I))
print(f"wrote design-skills-for-gemini.md: {len(full) // 1024} KB, ~{len(full) // 4 // 1000}k tokens; "
      f"{len(skills)} skills; Claude mentions left outside URLs: {left}")
for f in sorted(os.listdir(os.path.join(HERE, "parts"))):
    print(f"  parts/{f}: {os.path.getsize(os.path.join(HERE, 'parts', f)) // 1024} KB")
