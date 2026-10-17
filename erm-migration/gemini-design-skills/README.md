# Design Skills for Gemini

Your `claudedesignskills` repo (22 skills: Three.js, React Three Fiber, Babylon.js, PlayCanvas, A-Frame,
GSAP, Motion, React Spring, Anime.js, Lottie, Locomotive, Barba, AOS, Zdog/Vanta, PixiJS, Magic UI,
modern web design, Blender pipeline, Spline, Rive, Substance 3D, integration patterns) packed as plain
text for a Gemini gem, with "Claude" replaced by "Gemini".

| File | What it is |
|---|---|
| `design-skills-for-gemini.md` | Everything in one file (~2.5 MB, ~650k tokens): an index, then every skill's SKILL.md, references, agents, commands, scripts and templates |
| `parts/design-skills-part-1.md` … `part-6.md` | The same content split by category (3D engines · animation · scroll · 2D and design · authoring tools · index and guides), for when one big file is refused or too slow |
| `pack_for_gemini.py` | Rebuilds both from the repo: `python pack_for_gemini.py /path/to/claudedesignskills` |

What's left out: duplicate copies (`plugins/bundles`, `.claude/`, `.factory/`), Claude- and
Factory-specific plumbing (plugin manifests, marketplace scripts, skill-creator, droids) and binaries
(`.zip`). Links (URLs) keep their original spelling so they still work, and the MIT licence notice is
kept unchanged at the end.

## Add it to a gem

**Option A: give the motionkit Director gem web/design skills too.** Edit the gem › Knowledge › add
`design-skills-for-gemini.md` (or parts 1-6) next to `motionkit-knowledge.md` › Save. The updated
instructions in `motionkit/gemini-gem/GEM.md` already tell it to use these skills for web and design work.

**Option B: a separate "Design Studio" gem.** New Gem › name `Design Studio` › paste the instructions
below › upload the file(s) › Save.

```
You are Design Studio, a senior creative developer for 3D/WebGL, animation and modern web design.
Your knowledge file is a library of 22 skills; its index says which skill fits which task.
For every request: pick the matching skill(s) from the index, read their SKILL.md first, then the
references; follow their patterns, versions and pitfalls. Combine skills when needed (see
web3d-integration-patterns). Files under commands/ are ready-made recipes: when the user asks for one of
those tasks or types /<command-name>, follow its steps. Files under agents/ are expert roles you can adopt.
Write complete, runnable code (all files, with how to run it), explain choices briefly, and say clearly
when you go beyond what the skills cover.
```

Use the **Thinking** model (or Pro) for code. If Gemini refuses the single file or answers slowly, use the
six parts instead (a gem takes up to about ten knowledge files).
