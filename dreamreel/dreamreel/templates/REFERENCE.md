# dreamreel reference

Everything here is built in. `dreamreel plugins -v` lists the same, plus whatever this film's
`extensions/` add, with every setting.

## Cast: `cast/<name>.toml`

Every character has `name`, `voice` (a Piper voice such as `en_US-amy-medium`) and a `type`.

### `type = "toy"` (the default): a jointed vinyl figure

| Field | Values |
|---|---|
| `height` | 1.0 is an adult (0.7-1.3) |
| `body` | bean, round, tall, kid |
| `skin` | skin1 (lightest) ... skin6 (deepest), or a colour |
| `hair` | none, short, bob, long, ponytail, bun, spiky, curly, mohawk |
| `hair_color`, `top`, `bottom`, `shoes` | colours |
| `outfit` | shirt, dress |
| `eyes` | small, normal, big |
| `extras` | any of glasses, hat, cap, scarf, tie, bow, beard, moustache, headphones |

### `type = "creature"`: any body

| Field | Values |
|---|---|
| `body` | biped, quadruped, bird, fish, serpent, bug, spider, blob, frog |
| `size` | overall scale (1 = dog-sized quadruped, child-sized biped) |
| `length`, `legs_length`, `neck`, `tail`, `girth` | proportions (1 = normal) |
| `leg_pairs` | for bugs (3 = insect) |
| `color`, `belly` | main and underside colours |
| `pattern`, `pattern_color` | none, spots, stripes |
| `head` | round, snout, beak, fish, bug, frog, none (each body has a sensible default) |
| `ears` | none, pointy, round, floppy, long |
| `horns` | none, small, ram, unicorn |
| `wings` | true for wings (and flying) |
| `float` | true makes a blob float (a ghost) |
| `eyes`, `hair` (a mane), `hair_color`, `extras` | as for toys |
| `iris` | an eye colour (with a pupil), e.g. `"#8a5fd1"` |

What each body can do:

| Body | Moves by | Can also |
|---|---|---|
| biped | walking | arm gestures |
| quadruped | walk, trot (fast), gallop (run) | tail_wag, rear_up; with wings: fly_to, flap |
| bird | walking | fly_to, flap, tail |
| fish | swimming | tail_wag |
| serpent | slithering | tail_wag |
| bug, spider | scuttling (tripod gait) | |
| blob | hopping | |
| frog | hopping (big jumps, feet and all) | arm gestures (wave, cheer, point...), croak, tongue, swim |

All bodies: say, feel (moods), look_at, turn_to, nod, shake_head, jump, bow, roar, sniff, spin.

**Colours**: hex (`"#e4572e"`) or a name: red orange yellow green teal blue navy purple pink cream
beige wood darkwood charcoal denim mint sky brick leaf grass white black grey brown chestnut blonde
ginger.

## Sets: `sets/<name>.toml`

`kind = "room"`: `size` (small, medium, large), `walls`, `floor` (wood, tiles, carpet, concrete,
grass, sand, stone), `trim`, `wallpaper`, and `furnish` to have it furnished for you: living_room,
kitchen, bedroom, office, classroom, cafe, lab. Your own `[[props]]` come first; the furniture fills
the places that are still free. `ceiling` (none, plain, tiles) puts a ceiling on the room so low
angles look up at something; tiles come with strip lights that light the room.

`kind = "outdoor"`: `biome` (meadow, forest, autumn, beach, desert, snow, mountains, moon),
`terrain` (flat, rolling, hills, mountains, dunes, craters; the biome chooses otherwise), `density`
(how much scenery, 0-3), `ground` (a colour), `path` (true/false), `seed` (a different arrangement).
The acting area always stays flat and clear; scenery is laid out round it by the biome's rules.

`kind = "street"`: a town street made by rules. `style` (town, city, old_town), `shops` (0-1),
`cars`, `lamps`, `trees`, `seed`. The pavement in front of the buildings is the acting area, the
road runs towards the camera, the other side of the street is there for reverse shots. Marks:
`door`, `shop`, `crossing`, `kerb`, `lamp`, `across`, and `car`, `car-2`... for parked cars.

A set file can also give its scenes a default `time_of_day` and `weather`.

Things go in **places** (a 3 x 3 grid seen from the camera; the back row is against the back wall):

```
back-left    back     back-right
left         center   right
front-left   front    front-right      <- camera side
```

```toml
[[props]]
type = "table"
place = "center"
chairs = 2
items = ["plate", "cup"]

[marks]            # your own named spots
by_the_plant = "left"
```

| Prop | Settings | Spots and seats it makes |
|---|---|---|
| door | color | `door` |
| window | view | `window` |
| table | width, depth, color, chairs (0-2), chair_color, items | `table`, `table-left`, `table-right`; seats `chair`, `chair-2` |
| chair | color, facing | seat `chair` |
| sofa, bench | width, color, facing | seats `sofa`, `sofa-2` / `bench`, `bench-2` |
| counter | width, color, top, items | `counter` |
| fridge, bookshelf, plant, lamp, rug | color (lamp and streetlamp give light) | `fridge` |
| tree | scale, variety (any scenery: tree, pine, palm, cactus, rock, bush, snowman...) | `tree` |
| streetlamp, house | (the street lamp gives light) | `house` |
| bed | color, frame, width | seat `bed` (sitting on its edge) |
| desk | color, chair, facing (back, camera), items | `desk`; seat `desk-chair` |
| wardrobe, tv | color / facing, on | `wardrobe` |
| painting, clock, blackboard | on the back wall (they don't take a floor place) | `blackboard` |
| car | color, facing (left, right, camera, back) | `car` |
| lab_bench | width, color, items | `lab_bench`, `lab_bench-left`, `lab_bench-right` |
| shelves | width, color (full of jars, beakers and bottles) | |
| poster | design (elements, safety, chart), height; on the back wall | |

Items on tables, counters and benches: cookie-jar, cookie, plate, cup, vase, laptop, book, tray (a
dissection tray; makes the mark `tray`), tool-cup, jar, beaker, bottle, scale.
A second thing of the same type gets `-2` (`chair-2`), or give it a `name`.

## Scenes: `scenes/NNN_name.toml`

```toml
set = "kitchen"
cast = ["mia", "tom"]
time_of_day = "golden_hour"  # dawn, morning, day, golden_hour, sunset, dusk, night
weather = "rain"             # clear, cloudy, overcast, fog, rain, snow, storm, windy
weather_strength = 1.0       # 0.3 a little ... 2 a lot

[[beats]]
who = "mia"
do = "walk_to"
where = "table"
```

Beats play in order. `with_previous = true` starts a beat together with the one before;
`at = 12.5` starts it at an exact second.

| `do` | Settings |
|---|---|
| say | line, mood, to |
| walk_to | where, speed (slow, normal, fast, run), facing |
| run_to | where |
| fly_to | where, height, land (needs wings) |
| enter | where (appears there; hidden before) |
| place | where, facing (standing there from the start) |
| sit | seat, already (true: sitting from the start). Bodies without arms lie down there |
| lie_down, stand, leave | |
| turn_to, look_at | target |
| feel | mood |
| gesture | gesture, target |
| wait (no who) | seconds |
| caption, title_card (no who) | text, duration |
| slow_motion (no who) | seconds, speed (0.3 slow ... 2 fast), ramp, after: the next story-seconds play at that speed |
| freeze_frame (no who) | seconds, after: everything stops, then carries on |
| jump_cut (no who) | seconds, after: that much story is cut out and the picture jumps ahead |
| screen (no who) | effect (fade_out, fade_in, flash, dip, blackout), duration, color, after |
| shot (no who) | shot, of, other, angle, side, move, amount, to, handheld, dutch, lens, duration (see Camera) |

Time of day sets the sun, the sky and how much lamps matter (rooms get their light through the
windows). Weather changes the light everywhere; outdoors it also brings clouds, rain, snow, fog,
lightning and wind in the trees. Slow motion slows the rain too.

**Where / target / facing**: a spot or seat name, a character, or `camera`, `left`, `right`, `back`.

**Moods**: neutral, happy, excited, sad, angry, surprised, worried, scared, smug, sleepy.

**Gestures**: wave, nod, shake_head, shrug, point, jump, cheer, facepalm, clap, think, bow, stomp
(toys); roar, sniff, spin, tail_wag, flap, rear_up, croak, tongue (any body that has what it needs).

## Camera

Without shot beats, dreamreel directs the scene itself. It establishes the place, follows people
who travel, cuts between speakers on one side of the line (the 180° rule), and lets the mood choose
angles and moves (low angle for anger, high for fear, a push in on surprise).

A `shot` beat takes over from that moment until the next shot, or for `duration` seconds:

```toml
[[beats]]
do = "shot"
shot = "close_up"      # the framing
of = "mia"
angle = "low"
move = "push_in"
handheld = true
```

| Setting | Values |
|---|---|
| `shot` (framing) | establishing, wide, group, full, medium_wide, medium, medium_close, close_up, extreme_close_up, two_shot (of, other), over_shoulder (of = past whom, other = onto whom), pov (through of's eyes, looking at other), insert (of = a prop or thing on a table, e.g. `cookie-jar`) |
| `angle` | eye_level, high, low, birds_eye, worms_eye (kept even when furniture is in the way) |
| `side` | auto, front, three_quarter, profile, back |
| `move` | static, push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down, truck_left, truck_right, crane_up, crane_down, orbit_left, orbit_right, follow, zoom_in, zoom_out, dolly_zoom, rack_focus |
| `amount` | how much the move does (degrees for pans, tilts and orbits; metres for trucks and cranes; a share of the distance for push and pull; a lens factor for zooms) |
| `to` | pan to someone or something; rack focus onto them |
| `handheld` | true adds a human wobble to any shot or move |
| `dutch` | tilt the frame by degrees (unease) |
| `lens` | millimetres (24 wide ... 85 long); chosen from the framing otherwise |
| `duration` | seconds before the automatic camera takes over again |

Faces get headroom and lead room (space on the side they're looking towards) automatically.

## Looks: `style`

`style = "toon"` in `film.toml` sets the look of the whole film; `style = "noir"` at the top of a
scene file gives that scene its own (flashbacks, dreams, a film within the film).

| Style | Look |
|---|---|
| toy | soft vinyl toys under warm light (the default) |
| toon | flat colours, two tones, bold outlines |
| anime | crisp cel shading, cool violet shadows, fine lines, vivid colour |
| clay | matte clay with thumbprints, animated on twos like stop-motion |
| paper | flat card cut-outs with white edges, animated on threes |
| storybook | soft pastel tones, gentle brown lines, a warm painted feel |
| noir | black and white, a low hard side light, deep shadows |
| realistic | less plastic, more texture, richer contrast |

## Editing: transitions, time and the edit list

How a scene comes in after the one before it goes at the top of its scene file:

```toml
transition = "dissolve"
transition_duration = 1.0      # seconds (each transition has its own default)
transition_color = "black"     # fade, flash
transition_direction = "left"  # wipe, push, whip: left, right, up, down; iris: out (opens) or in
```

| Transition | Use it for |
|---|---|
| cut | the default; also smash cuts and match cuts (the content makes the difference) |
| fade | out to a colour and in again: the end of a chapter, a long time passing |
| dissolve | one scene melting into the next: time passing, memories, montage |
| wipe | the next scene sweeps across: adventure serials, comedy |
| iris | a circle opening (or closing, `in`) on the picture: cartoons, old films |
| clock | a clock-hand sweep: time passing |
| push | the next scene shoves the old one off the screen |
| whip | a fast whip pan between places: energy, "meanwhile" |
| zoom | zooming through into the next scene |
| flash | a flash of white (or any colour) at the cut: shocks, memories, action |

Time effects (`slow_motion`, `freeze_frame`, `jump_cut`) change the scene's own animation, so slow
motion is truly smooth; put them just before the action they affect. Voices, subtitles, captions
and camera cuts move with them. Screen effects (`screen`) are done in the edit, like transitions.

`film.toml` lists the scenes in order (`scenes = [...]`). For more control, use an edit list
instead: each `[[edit]]` entry is one clip, and the same scene can appear more than once.

```toml
[[edit]]
scene = "010_kitchen"
to = 8.0                       # only up to 8 s in: cut away (cross-cutting)

[[edit]]
scene = "020_street"
transition = "whip"            # overrides the scene file's own transition (also duration,
direction = "right"            # color, direction)

[[edit]]
scene = "010_kitchen"
from = 8.0                     # back to the kitchen where we left it
audio = "l"                    # L-cut: the previous clip's sound runs on under this picture
audio_seconds = 0.8            # (j: this clip's sound starts before its picture)

[[edit]]
split = ["030_her", "040_him"] # split screen: a phone call, two places at once
layout = "side_by_side"        # or "top_bottom"
```

`dreamreel check` prints the edit list and the film's length. Transitions never re-render scenes,
so trying a different one is quick.

## Commands

| | |
|---|---|
| `dreamreel new DIR [--example]` | new project |
| `dreamreel studio [DIR]` | the app, in your browser |
| `dreamreel check [scene]` | timelines, warnings and errors, without rendering |
| `dreamreel cast [names]` | picture of the cast |
| `dreamreel plan SET [--view]` | map of a set with its spots (or a picture of it) |
| `dreamreel still SCENE T [T ...]` | frames at those seconds (`--percent`, `--previz`) |
| `dreamreel contact SCENE` | frames from across a scene on one sheet |
| `dreamreel previz [scene]` / `render [scene]` | fast film / final film (`--percent`, `--force`) |
| `dreamreel plugins [kind] [-v]` | every feature and its settings |
| `dreamreel extend KIND NAME` | start a new feature as a class in `extensions/` |
| `dreamreel voices` | how to set up voices |
