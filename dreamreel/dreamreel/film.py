"""Building a scene from its script, rendering it, and cutting scenes together into the film."""
import hashlib
import json
import os
import runpy

import bpy

from . import __version__, _compat, keys, project, scene as scene_mod


def build(proj, path):
    """Run a scene script and return the finished Scene."""
    name = os.path.splitext(os.path.basename(path))[0]
    project.activate(proj, name)
    scene_mod.CURRENT = None
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
    for f in files:
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


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
            return meta
    s = build(proj, path)
    _apply_quality(s, quality, percent)
    r = s.bscene.render
    _compat.set_video_output(r)
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.filepath = out
    bpy.ops.render.render(animation=True)
    meta = s.metadata()
    meta["hash"] = digest
    meta["video"] = out
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=1)
    print(f"[dreamreel] {name}: rendered {os.path.relpath(out, proj.root)}")
    return meta


def assemble(proj, metas, quality="final", subtitles=True):
    """Cut the rendered scenes together with title cards, subtitles, captions, voices and music."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    film = proj.film
    fps = int(film.get("fps", 24))
    sc.render.fps = fps
    sc.render.resolution_x, sc.render.resolution_y = film.get("resolution", (1920, 1080))
    sc.render.resolution_percentage = 100 if quality == "final" else 50
    strips = _compat.sequence_strips(sc)
    frame = 1
    W = sc.render.resolution_x

    def text(content, f0, f1, channel, y=0.08, size=0.045, box=True):
        st = strips.new_effect(name="text", type="TEXT", channel=channel, frame_start=f0, length=max(1, f1 - f0))
        st.text = content
        st.font_size = int(size * sc.render.resolution_y)
        st.location = (0.5, y)
        st.anchor_x, st.anchor_y = "CENTER", "BOTTOM" if y < 0.5 else "CENTER"
        st.color = (1, 1, 1, 1)
        if hasattr(st, "use_shadow"):
            st.use_shadow = True
        if box and hasattr(st, "use_box"):
            st.use_box = True
            st.box_color = (0, 0, 0, 0.55)
            if hasattr(st, "box_margin"):
                st.box_margin = 0.012
        return st

    for meta in metas:
        for content, dur, color in meta.get("cards", []):
            n = int(dur * fps)
            col = strips.new_effect(name="card", type="COLOR", channel=1, frame_start=frame, length=n)
            from .look import rgb
            col.color = rgb(color)
            text(content, frame, frame + n, 2, y=0.5, size=0.07, box=False)
            frame += n
        mv = strips.new_movie(name=meta["name"], filepath=meta["video"], channel=1, frame_start=frame)
        length = mv.frame_final_duration
        if subtitles:
            for t0, t1, who, line in meta["subtitles"]:
                text(line, frame + int(t0 * fps), frame + int(t1 * fps), 3)
        for t0, t1, content in meta.get("captions", []):
            text(content, frame + int(t0 * fps), frame + int(t1 * fps), 4, y=0.86, size=0.05)
        for i, (t0, wav) in enumerate(meta.get("audio", [])):
            strips.new_sound(name="voice", filepath=wav, channel=5 + i % 2, frame_start=frame + int(t0 * fps))
        frame += length
    music = film.get("music")
    if music:
        m = strips.new_sound(name="music", filepath=os.path.join(proj.root, music["file"]), channel=8, frame_start=1)
        m.volume = music.get("volume", 0.35)
        if m.frame_final_end > frame:
            m.frame_final_end = frame
    sc.frame_start, sc.frame_end = 1, frame - 1
    r = sc.render
    _compat.set_video_output(r)
    r.ffmpeg.audio_codec = "AAC"
    r.ffmpeg.audio_bitrate = 192
    r.ffmpeg.constant_rate_factor = "HIGH"
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in proj.title.lower()).strip("-")
    out = proj.renders(f"{safe}{'' if quality == 'final' else '-' + quality}.mp4")
    r.filepath = out
    r.use_sequencer = True
    bpy.ops.render.render(animation=True)
    return out
