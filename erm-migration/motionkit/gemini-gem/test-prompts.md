# Test prompts for the motionkit Director gem

These prompts are **not** in the gem's knowledge file: none of them matches an example, a cookbook
recipe or an earlier test. They check whether the gem *understands* the kit (axes, pivots, timing,
easing, lit vs glowing) rather than copying a recipe. Don't upload this file to the gem.

Paste one prompt at a time into a fresh chat. Score each with the rubric at the bottom, and paste
anything that looks wrong back to Claude to run in Blender 5.

---

## 1. Analogue clock (pivots and rotation axis)
```
/idea 8 seconds: an analogue clock face seen from the front. The minute hand sweeps a full circle and the hour hand moves one hour, both turning clockwise around the centre of the dial. Twelve small tick marks around the edge.
```
**Look for:** hands built as `mk.Line` from the centre outwards so they pivot at the centre; rotation
with `.spin(..., axis="Y")` (the clock faces the camera); **negative** turns for clockwise as seen by
the viewer; minute hand 1 turn, hour hand 1/12 turn; tick marks placed with sin/cos on the X-Z plane.
**Red flags:** spinning around Z (the hands would swing towards the camera); hands rotating around their own middle.

## 2. Bouncing ball (believable physics)
```
/idea 6 seconds: a lit orange ball drops onto a floor and bounces three times, each bounce lower than the last, then rests. Squash it slightly each time it hits the floor.
```
**Look for:** falling with `ease="ease_in"` and rising with `ease="ease_out"`; bounce heights that shrink
(e.g. 3 → 1.5 → 0.7); bounces that get **shorter in time** too; a brief `scale_to` squash (wider, flatter)
exactly at each impact; `lit=True` plus a `Light`; the floor at the ball's lowest point (no sinking).
**Red flags:** `ease="bounce"` on one long fall (looks fake); equal timing for every bounce; no light.

## 3. Roadmap staircase (lit blocks and a tracking camera)
```
/idea 12 seconds: five rounded blocks rise one after another like a staircase, left to right, labelled 2022 to 2026 on their fronts. The camera glides sideways along the stairs, ending on 2026, which glows pink.
```
**Look for:** `mk.Box(..., lit=True)` with increasing heights; labels as `Text3D` just in front of each
block (more negative Y); staggered `pop_in` or `slide_in(direction="down")`; `camera.move` along X with
`look_at` moving too; a key and fill `Light`; the 2026 block using `glow_to`/`color_to` or a glowing label.
**Red flags:** labels inside the blocks; the camera turning away from the stairs.

## 4. Network with data pulses (lines and travelling objects)
```
/idea 10 seconds: six glowing nodes form a network; connection lines draw on one by one; then small bright pulses travel along three of the connections from one node to another.
```
**Look for:** `Sphere` nodes; `mk.Line([a, b])` between node positions with staggered `.draw_on`;
pulses as tiny glowing spheres that `.move_to` from node A to node B (several moves for multi-hop
paths), appearing with `show`/`fade_in` and leaving with `fade_out`.
**Red flags:** pulses that don't start and end exactly on node positions.

## 5. Bar race, horizontal (scaling from one end)
```
/idea 8 seconds: a horizontal bar race with four teams. Bars grow from a common left edge towards the right to different lengths, the leader turns gold at the end, team names on the left.
```
**Look for:** the gem noticing that `BarChart` is vertical, so it uses `mk.Box` or `mk.Card`; and that a
box scales **around its centre**, so it either moves the bar right by half the added length while scaling
(`move_to` + `scale_to` at the same time) or explains the trick. Names right-aligned at the shared left edge.
**Red flags:** bars that grow in both directions from the middle.

## 6. Coin flip reveal (two-sided card)
```
/idea 5 seconds: a gold coin-like disc shows "Q3" on the front, flips around its vertical axis, and shows "+76%" on the back.
```
**Look for:** front and back built as two items back to back (the back one turned 180°) inside a
`Group`; the group rotated around **Z** (vertical) with `rotate_to(0, 0, 180, ...)`; text on the back not
mirrored after the flip; ideally a little `pop`/`pulse` when the back lands.
**Red flags:** rotating around X or Y; one card whose back shows the front text mirrored.

## 7. Day to night (a gap in the kit)
```
/idea 10 seconds: a small lit house-shaped block on a floor; the light goes from warm daylight to cool moonlight and the sky colour fades from light blue to dark navy.
```
**Look for:** `Light.power_to` (and a second light fading in) for the light change. **The sky colour can't
be animated with motionkit**: a good answer says so and uses a short `# raw Blender:` block keyframing the
world background colour (`bpy.context.scene.world.node_tree.nodes["Background"].inputs[0]`).
**Red flags:** an invented `movie.background_to(...)` or `mk.Sky`.

## 8. Terminal typing (choosing the right layer)
```
/idea 7 seconds: a dark terminal window; three lines of green code type themselves one after another, then a line "Build passed ✓" appears in bright green.
```
**Look for:** typing done with `Text3D.type_on` (only 3D text can type; `overlay.text` can't), left-aligned
lines stacked on Z with staggered start times; a dark `Card` behind as the window; a mono font path or a
note that the default font isn't monospaced; ✓ possibly flagged as a font risk.
**Red flags:** `overlay.text(..., type_on=...)` (doesn't exist).

## 9. Before / after split screen
```
/idea 8 seconds: two app screenshots side by side, "Before" on the left and "After" on the right; a glowing vertical divider sweeps from left to right revealing the After screen.
```
**Look for:** two `Screen`s or `Card(image=...)`; a thin glowing `Card` as the divider moving with
`move_to`; a plausible reveal (After fading or sliding in as the divider passes); labels via `overlay.text`
or `Text3D`. A good answer admits that a true pixel wipe (masking) isn't in the kit and approximates it.
**Red flags:** claiming a real masked wipe with invented calls.

## 10. Outside the kit (honesty)
```
Import our product model from assets/drone.fbx, make it hover and rotate slowly, and render it with Cycles for realistic reflections.
```
**Look for:** FBX import done with raw Blender (`bpy.ops.import_scene.fbx`) marked `# raw Blender:` and
wrapped as `mk.Item(obj)` so the kit's motions work; an explanation that the kit is tuned for EEVEE and
that switching to Cycles is outside it (offered as a clearly marked raw line, or declined with the reason).
**Red flags:** `mk.Model("drone.fbx")`, `Movie(engine="cycles")`, or silently ignoring the Cycles request.

## 11. Impossible timing (checks before writing)
```
/script
MOVIE "short" 6s
SHOT a 0s-6s
  ADD text "t" "Late title"
  t: pop-in @7.5
```
**Look for:** the gem pointing out that 7.5 s is after the 6 s end and asking (or proposing to extend the
movie / move the title) **before** writing code.
**Red flags:** writing the code as is.

## 12. Vague request (does it ask?)
```
Make something cool for our team.
```
**Look for:** two or three short questions (length, purpose, team name, colours, format) or a clearly
labelled draft with stated assumptions and "Shall I write the code?".
**Red flags:** a long script built on silent guesses.

---

## Scoring rubric (per prompt, 0-2 each)

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| **Runs** | errors | runs after a small fix | runs as given |
| **Real API only** | invents API | one dubious call | everything exists (or raw Blender clearly marked) |
| **Spatially correct** | wrong axes, pivots or planes | minor slips | right axes, pivots, planes, in frame |
| **Motion quality** | robotic or wrong timing | acceptable | believable easing and timing |
| **Honest about limits** | pretends | half-explains | says what the kit can't do and offers a real alternative |

**10/10 per prompt** = production-ready. Below 6 on a prompt points at a gap: in the kit (add a
helper), in the docs (explain it better) or in the gem's rules. Paste failing scripts back to Claude
to diagnose in Blender 5.
