"""Building a scene from its script, rendering it, and cutting scenes together into the film."""
import glob
import hashlib
import json
import os
import runpy

import bpy

from . import __version__, _compat, keys, project, restyle, scene as scene_mod


def build(proj, path):
    """Run a scene script and return the finished Scene."""
    name = os.path.splitext(os.path.basename(path))[0]
    project.activate(proj, name)
    scene_mod.CURRENT = None
    if path.endswith(".toml"):
        s = scene_mod.Scene.from_file(path, name=name)
    else:
        runpy.run_path(path, run_name="__dreamreel__")
        s = scene_mod.CURRENT
    if s is None:
        raise SystemExit(f"{path}: the script never created a dr.Scene(...)")
    s.name = name
    s.finish()
    return s


def scene_hash(proj, path, quality):
    """Changes when anything the scene depends on changes, so unchanged scenes aren't re-rendered."""
    h = hashlib.sha256()
    h.update(f"{__version__}|{quality}".encode())
    files = [os.path.join(proj.root, "film.toml"), path]
    files += [os.path.join(proj.root, "cast", n + ".toml") for n in proj.cast_names()]
    files += [os.path.join(proj.root, "sets", n + ".toml") for n in proj.set_names()]
    ext = os.path.join(proj.root, "extensions")
    files += sorted(os.path.join(ext, n) for n in os.listdir(ext) if n.endswith(".py")) if os.path.isdir(ext) else []
    for f in files:
        with open(f, "rb") as fh:
            h.update(fh.read())
    sfx = os.path.join(proj.root, "audio", "sfx")            # the film's own sounds replace built-in ones
    if os.path.isdir(sfx):
        for n in sorted(os.listdir(sfx)):
            h.update(f"{n}|{os.path.getmtime(os.path.join(sfx, n))}".encode())
    h.update(_library_hash().encode())
    return h.hexdigest()[:16]


_LIB = None


def _library_hash():
    """dreamreel's own code: a new version (or a local edit) re-renders scenes."""
    global _LIB
    if _LIB is None:
        h = hashlib.sha256()
        pkg = os.path.dirname(os.path.abspath(__file__))
        for f in sorted(glob.glob(os.path.join(pkg, "*.py"))):
            with open(f, "rb") as fh:
                h.update(fh.read())
        _LIB = h.hexdigest()
    return _LIB


def _apply_quality(s, quality, percent):
    r = s.bscene.render
    if quality == "previz":
        s.previz_settings()
    r.resolution_percentage = percent or (50 if quality == "previz" else 100)


def still(proj, path, times, percent=50, quality="final", out_dir=None):
    s = build(proj, path)
    _apply_quality(s, quality, percent)
    r = s.bscene.render
    _compat.set_image_output(r)
    for o in s.bscene.objects:      # cloth needs every frame before the one shown: in a single frame it
        for m in o.modifiers:       # hangs as it's skinned (the film itself plays it frame by frame)
            if m.type == "CLOTH":
                m.show_render = m.show_viewport = False
    out = []
    for t in times:
        s.bscene.frame_set(keys.CLOCK.frame(t))
        p = os.path.join(out_dir or proj.renders("stills"), f"{s.name}_{t:05.2f}s.png")
        r.filepath = p
        bpy.ops.render.render(write_still=True)
        out.append(p)
    return s, out


def contact_sheet(proj, path, count=6, percent=25, quality="final"):
    """Render `count` evenly spaced frames and tile them into one image: a quick review of a scene."""
    s = build(proj, path)
    times = [round(s.length * (i + 0.5) / count, 2) for i in range(count)]
    _, paths = still(proj, path, times, percent, quality, out_dir=proj.renders("stills", "contact"))
    import numpy as np
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        w, h = im.size
        px = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        imgs.append(px.reshape(h, w, 4))
    cols = 3 if count > 4 else 2
    rows = -(-count // cols)
    h, w = imgs[0].shape[:2]
    pad = 6
    sheet = np.ones(((h + pad) * rows + pad, (w + pad) * cols + pad, 4), dtype=np.float32) * 0.08
    sheet[..., 3] = 1
    for i, im in enumerate(imgs):
        r_, c_ = divmod(i, cols)
        y0 = pad + (rows - 1 - r_) * (h + pad)  # Blender images start at the bottom
        x0 = pad + c_ * (w + pad)
        sheet[y0:y0 + h, x0:x0 + w] = im
    out = bpy.data.images.new("contact", sheet.shape[1], sheet.shape[0], alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    dest = proj.renders("stills", f"{s.name}_contact.png")
    out.filepath_raw = dest
    out.file_format = "PNG"
    out.save()
    return s, dest, times


def render_scene(proj, path, quality="final", percent=None, force=False):
    """Render one scene to renders/<quality>/<scene>.mp4 (skipped if nothing changed)."""
    name = os.path.splitext(os.path.basename(path))[0]
    out = proj.renders(quality, f"{name}.mp4")
    meta_path = proj.renders(quality, f"{name}.json")
    digest = scene_hash(proj, path, f"{quality}{percent}")
    if not force and os.path.exists(out) and os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        if meta.get("hash") == digest:
            print(f"[dreamreel] {name}: unchanged, keeping {os.path.relpath(out, proj.root)}")
            meta = restyle.apply(proj, meta, path, quality)      # (the style may have changed)
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=1)
            return meta
    s = build(proj, path)
    _apply_quality(s, quality, percent)
    r = s.bscene.render
    print(f"[dreamreel] rendering {name}: {s.bscene.frame_end} frames", flush=True)
    if quality == "final":
        _render_frames(proj, s, name, digest, out)
    else:
        _compat.set_video_output(r)
        r.ffmpeg.constant_rate_factor = "HIGH"
        r.filepath = out
        bpy.ops.render.render(animation=True)
    meta = s.metadata()
    meta["size"] = [int(r.resolution_x * r.resolution_percentage / 100), int(r.resolution_y * r.resolution_percentage / 100)]
    meta["hash"] = digest
    meta["video"] = out
    meta = restyle.apply(proj, meta, path, quality)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=1)
    print(f"[dreamreel] {name}: rendered {os.path.relpath(out, proj.root)}")
    return meta


def _render_frames(proj, s, name, digest, out):
    """A final render goes frame by frame into renders/final/<scene>.frames/ and is then made into the
    video, so if it's stopped (a closed laptop, a lost connection) it carries on from where it was:
    frames already there for this version of the scene aren't rendered again."""
    import shutil
    import subprocess
    sc, r = s.bscene, s.bscene.render
    root = proj.renders("final", f"{name}.frames")
    os.makedirs(root, exist_ok=True)               # (a name with a dot isn't taken for a folder)
    frames = os.path.join(root, digest[:12])
    for old in os.listdir(root):                 # frames of an older version of the scene go
        if old != digest[:12]:
            shutil.rmtree(os.path.join(root, old), ignore_errors=True)
    os.makedirs(frames, exist_ok=True)
    done = sorted(f for f in os.listdir(frames) if f.endswith(".png"))
    if done:                                     # the last one may have been cut off mid-write
        os.remove(os.path.join(frames, done[-1]))
        done = done[:-1]
    first = sc.frame_start + len(done)
    if done:
        print(f"[dreamreel] {name}: {len(done)} frames already rendered, carrying on from frame {first}", flush=True)
        if any(m.type == "CLOTH" for o in sc.objects for m in o.modifiers):
            for f in range(sc.frame_start, first):  # cloth has to live through every frame before
                sc.frame_set(f)
    _compat.set_image_output(r)
    r.use_overwrite, r.use_placeholder = False, False
    r.filepath = os.path.join(frames, "####")
    bpy.ops.render.render(animation=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(s.fps), "-start_number",
                    str(sc.frame_start), "-i", os.path.join(frames, "%04d.png"), "-c:v", "libx264", "-crf", "16",
                    "-pix_fmt", "yuv420p", out], check=True)


def duck(strip, spans, amount, fade=6):
    """Lower a sound strip to `amount` of its volume while anyone speaks (spans of frames)."""
    if not spans or amount >= 1:
        return
    v = strip.volume
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1] + 2 * fade:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    strip.keyframe_insert("volume", frame=1)
    for a, b in merged:
        for f, val in ((a - fade, v), (a, v * amount), (b, v * amount), (b + fade, v)):
            strip.volume = val
            strip.keyframe_insert("volume", frame=max(1, f))
    strip.volume = v


def assemble(proj, metas, quality="final", subtitles=True, edit=None):
    """Cut the film together: clips from the rendered scenes in edit-list order, title cards, transitions,
    screen effects, subtitles, captions, voices and music."""
    from . import plugins
    from .editing import Clip, Editor
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    film = proj.film
    fps = int(film.get("fps", 24))
    sc.render.fps = fps
    # the canvas is exactly the size the scenes were rendered at, so clips are never rescaled
    size = next((m["size"] for m in metas if m.get("size")), None)
    if size:
        sc.render.resolution_x, sc.render.resolution_y = size
        sc.render.resolution_percentage = 100
    else:
        sc.render.resolution_x, sc.render.resolution_y = film.get("resolution", (1920, 1080))
        sc.render.resolution_percentage = 100 if quality == "final" else 50
    ed = Editor(sc, fps)
    by_name = {m["name"]: m for m in metas}
    if edit is None:
        edit = proj.edit_list()
        if len(metas) == 1 and [e.get("scene") for e in edit] != [metas[0]["name"]]:   # one scene on its own
            edit = [{"scene": metas[0]["name"]}]
    clips = []
    cursor = 1
    channel = 2
    sounds = 0
    speech = []        # (first, last frame) of every line spoken, to duck the music under

    def place_movie(meta, start, from_s, to_s, chan):
        mv = ed.strips.new_movie(name=meta["name"], filepath=meta["video"], channel=chan, frame_start=int(start),
                                 fit_method="ORIGINAL")
        f_from, f_to = int(round(from_s * fps)), int(round(to_s * fps))
        mv.frame_offset_start = f_from
        mv.frame_offset_end = max(0, mv.frame_duration - f_to)
        mv.frame_start = int(start) - f_from
        mv.blend_type = "ALPHA_OVER"
        return mv

    def overlays(meta, start, from_s, to_s, audio_from=None, audio_to=None):
        nonlocal sounds
        off = start - from_s * fps
        a_from = from_s if audio_from is None else audio_from
        a_to = to_s if audio_to is None else audio_to
        if subtitles:
            for t0, t1, who, line in meta.get("subtitles", []):
                if from_s <= t0 < to_s:
                    ed.text(line, off + t0 * fps, off + min(t1, to_s) * fps, ed.top + 2)
        for t0, t1, content in meta.get("captions", []):
            if from_s <= t0 < to_s:
                ed.text(content, off + t0 * fps, off + min(t1, to_s) * fps, ed.top + 3, y=0.86, size=0.05)
        for t0, wav in meta.get("audio", []):
            if a_from <= t0 < a_to:
                v = ed.strips.new_sound(name="voice", filepath=wav, channel=ed.top + 5 + sounds % 4,
                                        frame_start=int(off + t0 * fps))
                speech.append((v.frame_final_start, v.frame_final_end))
                sounds += 1
        for t0, wav, vol in meta.get("sounds", []):           # sound effects (sounds.py)
            if a_from <= t0 < a_to and os.path.exists(wav):
                fx = ed.strips.new_sound(name="sfx", filepath=wav, channel=ed.top + 11, frame_start=int(off + t0 * fps))
                fx.volume = vol
        bed = meta.get("ambience")
        if bed and os.path.exists(bed[0]):                    # the scene's ambience, for as long as it's on screen
            amb = ed.strips.new_sound(name="ambience", filepath=bed[0], channel=ed.top + 20,
                                      frame_start=int(off + a_from * fps))
            amb.volume = bed[1]
            amb.frame_final_end = min(amb.frame_final_end, max(amb.frame_final_start + 1, int(off + a_to * fps)))
        for t, fx, dur, color in meta.get("screen", []):
            if from_s <= t < to_s:
                plugins.get("screen", fx)().apply(ed, int(off + t * fps), ed.frames(dur), color)

    for i, entry in enumerate(edit):
        # how this clip comes in: the edit entry, else the scene's own setting, else a cut
        first_meta = by_name.get(entry.get("scene")) or by_name.get((entry.get("split") or [None])[0])
        if first_meta is None:
            continue
        trans = dict((first_meta.get("transition") or {}) if entry.get("from", 0) in (0, None) else {})
        for k in ("transition", "duration", "color", "direction"):
            if entry.get(k) is not None:
                trans["name" if k == "transition" else k] = entry[k]
        # title cards come first, as their own clips
        if entry.get("from", 0) in (0, None) and "scene" in entry:
            for content, dur, color in first_meta.get("cards", []):
                n = ed.frames(dur)
                col = ed.color(cursor, cursor + n, color, channel=channel)
                ed.text(content, cursor, cursor + n, channel + 1, y=0.5, size=0.07, box=False)
                card = Clip("card", cursor, n, [col], channel=channel)
                if clips:
                    plugins.get("transition", "cut")().apply(ed, clips[-1], card, cursor, 0)
                clips.append(card)
                cursor += n
        tr_cls = plugins.get("transition", trans.get("name") or "cut")
        dur = trans.get("duration")
        n = ed.frames(tr_cls.default_duration if dur is None else float(dur)) if tr_cls.name != "cut" else 0
        prev = clips[-1] if clips else None
        overlap = n if (tr_cls.overlap and prev is not None) else 0
        if prev is not None:
            n = min(n, prev.length - 1) if overlap else n
            overlap = min(overlap, n)
        start = cursor - overlap
        chan = (prev.channel + 1 if overlap else 2) if prev is not None else 2
        if chan >= ed.top - 3:
            chan = 2
        audio = (entry.get("audio") or "").lower()
        lead = float(entry.get("audio_seconds", 0.8)) if audio in ("j", "l") else 0.0
        if prev is not None and audio == "l" and prev.kind == "scene":
            # the previous clip's picture ends early; its sound carries on under this one
            cut = min(ed.frames(lead), prev.length - 1)
            for s in prev.strips:
                s.frame_final_end = max(s.frame_final_start + 1, s.frame_final_end - cut)
            prev.length -= cut
            start -= cut
        if "split" in entry:
            metas_ = [by_name[s] for s in entry["split"] if s in by_name]
            length_s = min(float(entry.get("to") or m["length"]) for m in metas_)
            from_s = float(entry.get("from") or 0.0)
            strips_ = []
            for k, m in enumerate(metas_):
                mv = place_movie(m, start, from_s, length_s, chan + k)
                if entry.get("layout", "side_by_side") == "top_bottom":
                    mv.crop.min_y = mv.crop.max_y = int(ed.H / 4)
                    mv.transform.offset_y = ed.H / 4 * (1 if k == 0 else -1)
                else:
                    mv.crop.min_x = mv.crop.max_x = int(ed.W / 4)
                    mv.transform.offset_x = ed.W / 4 * (-1 if k == 0 else 1)
                strips_.append(mv)
                overlays(m, start, from_s, length_s)
            clip = Clip("split", start, int((length_s - from_s) * fps), strips_, metas_[0], from_s, chan + len(metas_) - 1)
        else:
            meta = by_name[entry["scene"]]
            from_s = float(entry.get("from") or 0.0)
            to_s = float(entry.get("to") or meta["length"])
            pic_from = from_s + (lead if audio == "j" else 0.0)
            mv = place_movie(meta, start, pic_from, to_s, chan)
            if audio == "j":   # this clip's sound starts before its picture
                overlays(meta, start - lead * fps, from_s, to_s, audio_from=from_s)
            else:
                overlays(meta, start - (pic_from - from_s) * fps, pic_from, to_s)
            clip = Clip("scene", start, int(round((to_s - pic_from) * fps)), [mv], meta, pic_from, chan)
        if prev is not None:
            tr_cls().apply(ed, prev, clip, start, n, color=trans.get("color"), direction=trans.get("direction"))
        clips.append(clip)
        cursor = clip.end
        label = entry.get("scene") or " | ".join(entry.get("split", []))
        print(f"[dreamreel] edit {len(clips):3d}: {(start - 1) / fps:7.2f}s  {label:<24} "
              f"{tr_cls.name if prev is not None else 'start'}{f' ({n / fps:.1f}s)' if n and prev is not None else ''}",
              flush=True)
    music = film.get("music")
    if music:
        m = ed.strips.new_sound(name="music", filepath=os.path.join(proj.root, music["file"]), channel=ed.top + 10,
                                frame_start=1)
        m.volume = music.get("volume", 0.35)
        if m.frame_final_end > cursor:
            m.frame_final_end = cursor
        duck(m, speech, music.get("duck", 0.4))
    sc.frame_start, sc.frame_end = 1, max(2, cursor - 1)
    r = sc.render
    _compat.set_video_output(r)
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 192
    r.ffmpeg.constant_rate_factor = "HIGH"
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in proj.title.lower()).strip("-")
    out = proj.renders(f"{safe}{'' if quality == 'final' else '-' + quality}.mp4")
    r.filepath = out
    r.use_sequencer = True
    print(f"[dreamreel] rendering film: {sc.frame_end} frames", flush=True)
    bpy.ops.render.render(animation=True)
    return out
