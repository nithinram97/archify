# Troubleshooting

| Symptom | Fix |
|---|---|
| `blender` is not recognised | Use the full path, `& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b -P ...`, or add that folder to PATH |
| `ModuleNotFoundError: motionkit` | Keep the two `sys.path` lines at the top of the script, and keep the script inside `examples/` (or adjust the path) |
| An image shows as a flat colour | The path is wrong. The console prints `image not found: ...`. Use paths relative to the script: `os.path.join(HERE, "assets", "x.png")` |
| A font looks like Blender's default | The `.ttf` path is wrong (the console says so); Windows fonts live in `C:\Windows\Fonts` |
| Everything is black | The camera is looking at empty space. Render `--still` at a few times, or open with `blender -P script.py` and press Numpad 0 |
| Something appears too early | Fade it or pop it in: items are only hidden before a `fade_in`, `pop_in`, `slide_in`, `show` or `visible` |
| No glow | Add `movie.effects.glow()` and give the item `glow=2` or more |
| Text is cut off by the frame | Reduce `size`, or move the camera back (`place((0, -14, 0))`) |
| Render is slow | `--preview` for checks, `--percent 25` for quick tests, and fewer `Starfield` stars. A GPU helps EEVEE most |
| No sound in the MP4 | `add_music` needs a WAV/MP3 that exists; the console says if it doesn't |
| A transition lands in the wrong place | Outside a `with movie.shot(...)` block, use `shot.point(x, y, z)` for positions inside that shot |

## Blender versions

motionkit targets **Blender 5.0+** (tested on 5.0.1). It is written to also run on 4.2-4.5 (untested). Every API difference
(layered actions, keyframe interpolation, EEVEE engine names, the 5.x compositor node group, glare
inputs, sequencer `strips`, video output) is handled in `motionkit/_compat.py`. If a future Blender
release breaks something, that's the only file to change. Run `tests/smoke_test.py` to see what fails.

Notes from the ERM trailer that this kit encodes:

* Keys inserted from Python ignore the "default interpolation" preference in Blender 4.4+, so the kit
  writes the interpolation on each key. That's why hard cuts stay hard.
* EEVEE has no bloom setting since 4.2, so glow comes from the compositor Glare node.
* Very bright emission clips saturated colours to white under the Standard view; glow values are
  compressed above 1.
