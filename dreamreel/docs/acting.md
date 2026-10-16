# How dreamreel acts

dreamreel's movement is built on published animation research rather than ad-hoc tweaks. This page
explains what each idea is, where it comes from, and where it lives in the code, so contributors
(and AI agents) can extend it consistently.

## The principles of animation

Disney's animators worked out the principles of animation in the 1930s; John Lasseter restated
them for 3D computer animation in *Principles of Traditional Animation Applied to 3D Computer
Animation* (SIGGRAPH 1987). How dreamreel applies them:

| Principle | In dreamreel |
|---|---|
| Squash and stretch | jumps and hops squash on take-off and landing and stretch in the air (`Character.squash_at`) |
| Anticipation | every gesture starts with a small counter-move; jumps crouch first (`acting.shape`) |
| Staging | the camera grammar and automatic director (camera.py) |
| Follow-through, overlapping action | gestures overshoot and settle; dangly parts are springs that lag and settle (`acting.follow_through`); the body carries on a little when a walk stops |
| Slow in and slow out | eased keys everywhere (keys.py) |
| Arcs | limbs rotate about joints, so hands travel on arcs |
| Secondary action | blinks and breathing (`Character._alive`) |
| Timing | set by effort: sudden movements are quicker, sustained ones slower |
| Exaggeration | `exaggeration` in film.toml, defaulting per style (toon pushes it, realistic holds back) |

## Effort: how a movement is done

The EMOTE model (Chi, Costa, Zhao and Badler, *The EMOTE Model for Effort and Shape*, SIGGRAPH 2000)
made procedural movement expressive by layering the Effort qualities of Laban Movement Analysis on
top of any movement. dreamreel uses the same four qualities, each from -1 to +1:

| Quality | -1 | +1 | Changes |
|---|---|---|---|
| weight | light | strong | amplitude, walk bounce and arm swing |
| time | sustained | sudden | tempo, anticipation, walk speed |
| space | indirect | direct | (reserved for paths and gaze) |
| flow | free | bound | overshoot and settle |

Moods carry an effort (`acting.MOOD_EFFORT`), and a beat can override it with a manner
(`how = "nervously"`). Manners are plugins (`dr.Manner`).

How it is applied: while a gesture plays, every animation curve it keys is recorded
(`keys.recording`); afterwards `acting.shape` retimes and rescales those keys around the gesture's
start and adds anticipation and overshoot. So every gesture, including ones a film adds as an
extension, is shaped the same way without knowing about effort.

## Follow-through as springs

Parts registered with `Character.dangle(obj, root, stiffness, damping, gain)` hang from a pivot. When
the scene is finished, the body's accelerations (travel, turns, nods, jumps), smoothed over about a
fifth of a second, drive a damped spring per part, which is baked to keys
(`acting.follow_through`). This is the mass-spring-damper approach games use for secondary motion,
baked onto keyframes because dreamreel renders offline.

## Editing

The automatic director cuts *on action*: a moment into a walk or a big gesture rather than before it,
so the movement carries the eye across the cut (`camera.CUT_ON_ACTION`). Dialogue cuts come just
before a line. Camera choices follow film idioms in the spirit of *The Virtual Cinematographer*
(He, Cohen and Salesin, SIGGRAPH 1996).

## Where this is going

- Motion library: offline *motion matching* (Clavet and Büttner, Ubisoft, GDC 2016; *Learned Motion
  Matching*, Holden et al. 2020) over clips you import, retargeted to any dreamreel body. dreamreel
  can't ship third-party motion capture (Mixamo forbids redistribution; CMU's and AMASS's terms are
  research-oriented), so the library imports what you download.
- Lip sync with separate jaw and lip axes, after JALI (Edwards, Landreth, Fiume and Singh,
  SIGGRAPH 2016), using the phonemes the voice engine already knows.
- Text-to-motion models (such as MDM, ICLR 2023) as an optional add-on.

## References

- J. Lasseter. Principles of Traditional Animation Applied to 3D Computer Animation. SIGGRAPH 1987.
- D. Chi, M. Costa, L. Zhao, N. Badler. The EMOTE Model for Effort and Shape. SIGGRAPH 2000.
- L. He, M. Cohen, D. Salesin. The Virtual Cinematographer. SIGGRAPH 1996.
- S. Clavet. Motion Matching and The Road to Next-Gen Animation. GDC 2016.
- D. Holden, O. Kanoun, M. Perepichka, T. Popa. Learned Motion Matching. SIGGRAPH 2020.
- P. Edwards, C. Landreth, E. Fiume, K. Singh. JALI: an animator-centric viseme model for expressive
  lip synchronization. SIGGRAPH 2016.
- G. Tevet et al. Human Motion Diffusion Model. ICLR 2023 (arXiv 2022).
