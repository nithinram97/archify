"""Watching a render the way an animation supervisor does, and rewriting the scene from the notes.

    dreamreel review 010                # notes on the rendered scene: renders/<quality>/010.review.json
    dreamreel review 010 --fix          # ... and a revised scene, scenes/.proposed/010_x.toml (it must build)
    dreamreel review 010 --fix --apply  # ... and use it (the old one is kept in scenes/.history/)

Any AI model that can see pictures will do (film.toml [ai], or --provider/--model): Claude, Gemini,
GPT, or a free local one with Ollama. The render is cut into sheets of frames, a few per second, each
stamped with its time, and sent with the scene's timeline (who does what when, the cuts, the lines), so
the notes can say what's wrong and exactly when: twinning, sliding or floating feet, stiff or robotic
timing, poses that read badly, staging and framing, light. The fixes are changes to the scene file
(beats, timing, moods, shots), never to dreamreel itself, and a proposed scene only counts if it builds.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile

SUPERVISOR = """You are the animation supervisor on a film made with dreamreel (scenes are written as beats:
who does what, when, with which mood; dreamreel animates and films them). You are shown the rendered
scene as sheets of frames, each stamped with its time in seconds, and the scene's timeline.

Look hard, frame by frame, for what an audience would notice:
- twinning: both arms or both legs moving as perfect mirror images; two characters moving in unison
- feet that slide, float above the floor or sink into it; hands passing through bodies or props
- robotic timing: moves that start and stop dead, holds that are too long or too short, no anticipation
- poses that don't read (silhouette, line of action), stiff listeners, dead faces
- staging and camera: characters blocked by others, cut off by the frame, crossing the line, shots too long
- light: faces in shadow, subjects lost against the background

Reply with JSON only:
{"summary": "one or two sentences", "issues": [{"start": seconds, "end": seconds, "who": "name or null",
 "defect": "what is wrong, concretely", "fix": "what to change in the scene to fix it", "severity": 1-3}]}
Only report what you can actually see; an empty list is a fine answer."""

REWRITER = """You edit dreamreel scene files. You get the scene file, the supervisor's notes on its render,
and dreamreel's reference for scene files. Change the scene so every note you can address is addressed:
timing (at, wait, seconds), beats added or removed, moods, gestures, shots and camera moves. Keep the
story, the dialogue and the characters' names. Use only beats, gestures, moods and shots the reference
lists. Reply with the complete revised file in one ```{lang} block, then one line per note: what you
changed for it, or why it can't be fixed in the scene."""


class ReviewError(RuntimeError):
    pass


# ---------------------------------------------------------------------- looking
def sheets(video, out_dir, fps=4.0, columns=4, rows=3, width=360, start=0.0, end=None):
    """Cut a video into sheets of frames (`fps` per second), each stamped with its time; returns
    [(path, first second, last second)]."""
    os.makedirs(out_dir, exist_ok=True)
    length = duration(video)
    end = min(end or length, length)
    per = columns * rows
    span = per / fps
    out, t = [], start
    while t < end - 1e-3:
        path = os.path.join(out_dir, f"sheet_{len(out) + 1:03d}.png")
        stamp = f"drawtext=text='%{{pts\\:flt\\:{t:.3f}}}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6"
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-t", f"{min(span, end - t):.3f}", "-i", video,
               "-vf", f"fps={fps},scale={width}:-2,{stamp},tile={columns}x{rows}", "-frames:v", "1", path]
        subprocess.run(cmd, check=True)
        out.append((path, round(t, 2), round(min(t + span, end), 2)))
        t += span
    return out


def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def parse_json(text):
    """The JSON object in a reply (bare, or in a ``` block)."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("{"):text.rfind("}") + 1]
    try:
        return json.loads(raw)
    except ValueError:
        raise ReviewError(f"the reviewer's notes weren't JSON: {text[:300]!r}")


def review(ai, video, timeline, fps=4.0, workdir=None, progress=print):
    """Notes on a rendered scene from an AI model that can see: {summary, issues: [...]}."""
    workdir = workdir or tempfile.mkdtemp(prefix="dreamreel-review-")
    pics = sheets(video, workdir, fps=fps)
    progress(f"  {len(pics)} sheets of frames at {fps:g} per second")
    content = [{"text": "The scene's timeline (times in seconds):\n" + json.dumps(timeline, default=str)}]
    for path, t0, t1 in pics:
        content.append({"text": f"Frames from {t0:g}s to {t1:g}s:"})
        content.append({"image": path})
    content.append({"text": "Your notes, as JSON."})
    progress(f"  asking {ai} ...")
    notes = parse_json(ai.ask(SUPERVISOR, [{"role": "user", "content": content}]))
    notes.setdefault("issues", [])
    notes["issues"] = sorted(notes["issues"], key=lambda i: (-int(i.get("severity", 1)), float(i.get("start", 0))))
    return notes


# ---------------------------------------------------------------------- fixing
def _code(text, lang):
    m = re.search(rf"```(?:{lang})?\s*\n(.*?)```", text, re.S)
    if not m:
        raise ReviewError("the reply had no file in a ``` block")
    return m.group(1)


def propose(ai, scene_text, notes, reference, lang="toml", check=None, tries=3, progress=print):
    """A revised scene file for the notes. `check(text)` builds it and raises if it doesn't; a failure is
    sent back to the model to correct, up to `tries` times. Returns (text, the model's account)."""
    messages = [{"role": "user", "content": [{"text": (
        f"dreamreel's reference:\n{reference}\n\nThe scene file:\n```{lang}\n{scene_text}\n```\n\n"
        f"The supervisor's notes on its render:\n{json.dumps(notes, indent=1)}")}]}]
    system = REWRITER.format(lang=lang)
    for attempt in range(1, tries + 1):
        progress(f"  asking {ai} for a revised scene{'' if attempt == 1 else f' (try {attempt})'} ...")
        reply = ai.ask(system, messages)
        try:
            text = _code(reply, lang)
            if check is not None:
                check(text)
            return text, reply[reply.rfind("```") + 3:].strip()
        except Exception as e:      # noqa: BLE001 (any way the scene fails to build goes back to the model)
            progress(f"  that one doesn't build: {e}")
            messages += [{"role": "assistant", "content": [{"text": reply}]},
                         {"role": "user", "content": [{"text": f"That scene doesn't build: {type(e).__name__}: {e}\n"
                                                               "Fix it and reply with the complete file again."}]}]
    raise ReviewError(f"no revised scene that builds after {tries} tries")


def apply(scene_path, proposed_path):
    """Use the proposed scene; the old one goes to scenes/.history/. Returns where it went."""
    hist = os.path.join(os.path.dirname(scene_path), ".history")
    os.makedirs(hist, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base, ext = os.path.splitext(os.path.basename(scene_path))
    kept = os.path.join(hist, f"{base}.{stamp}{ext}")
    shutil.copy2(scene_path, kept)
    shutil.move(proposed_path, scene_path)
    return kept


def proposed_path(scene_path):
    """Where a proposed scene waits (scenes/.proposed/: not part of the film until it's applied)."""
    d = os.path.join(os.path.dirname(scene_path), ".proposed")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, os.path.basename(scene_path))
