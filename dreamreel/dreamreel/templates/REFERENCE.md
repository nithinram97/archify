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
| `body` | biped, quadruped, bird, fish, serpent, bug, spider, blob |
| `size` | overall scale (1 = dog-sized quadruped, child-sized biped) |
| `length`, `legs_length`, `neck`, `tail`, `girth` | proportions (1 = normal) |
| `leg_pairs` | for bugs (3 = insect) |
| `color`, `belly` | main and underside colours |
| `pattern`, `pattern_color` | none, spots, stripes |
| `head` | round, snout, beak, fish, bug, none (each body has a sensible default) |
| `ears` | none, pointy, round, floppy, long |
| `horns` | none, small, ram, unicorn |
| `wings` | true for wings (and flying) |
| `float` | true makes a blob float (a ghost) |
| `eyes`, `hair` (a mane), `hair_color`, `extras` | as for toys |

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

All bodies: say, feel (moods), look_at, turn_to, nod, shake_head, jump, bow, roar, sniff, spin.

**Colours**: hex (`"#e4572e"`) or a name: red orange yellow green teal blue navy purple pink cream
beige wood darkwood charcoal denim mint sky brick leaf grass white black grey brown chestnut blonde
ginger.

## Sets: `sets/<name>.toml`

`kind = "room"`: `size` (small, medium, large), `walls`, `floor` (wood, tiles, carpet, concrete,
grass, sand, stone), `trim`, `wallpaper`.
`kind = "outdoor"`: `ground`, `trees`, `hills`, `path` (true/false), `seed`.

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
| tree, streetlamp, house | outdoors | `tree`, `house` |

Items on tables and counters: cookie-jar, cookie, plate, cup, vase, laptop, book.
A second thing of the same type gets `-2` (`chair-2`), or give it a `name`.

## Scenes: `scenes/NNN_name.toml`

```toml
set = "kitchen"
cast = ["mia", "tom"]
time_of_day = "day"          # or "night"

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
| shot (no who) | shot, of, other, angle, side, move, amount, to, handheld, dutch, lens, duration (see Camera) |

**Where / target / facing**: a spot or seat name, a character, or `camera`, `left`, `right`, `back`.

**Moods**: neutral, happy, excited, sad, angry, surprised, worried, scared, smug, sleepy.

**Gestures**: wave, nod, shake_head, shrug, point, jump, cheer, facepalm, clap, think, bow, stomp
(toys); roar, sniff, spin, tail_wag, flap, rear_up (any body that has what it needs).

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
| `angle` | eye_level, high, low, birds_eye, worms_eye |
| `side` | auto, front, three_quarter, profile, back |
| `move` | static, push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down, truck_left, truck_right, crane_up, crane_down, orbit_left, orbit_right, follow, zoom_in, zoom_out, dolly_zoom, rack_focus |
| `amount` | how much the move does (degrees for pans, tilts and orbits; metres for trucks and cranes; a share of the distance for push and pull; a lens factor for zooms) |
| `to` | pan to someone or something; rack focus onto them |
| `handheld` | true adds a human wobble to any shot or move |
| `dutch` | tilt the frame by degrees (unease) |
| `lens` | millimetres (24 wide ... 85 long); chosen from the framing otherwise |
| `duration` | seconds before the automatic camera takes over again |

Faces get headroom and lead room (space on the side they're looking towards) automatically.

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
