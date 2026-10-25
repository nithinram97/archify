# dreamreel reference

Everything here is built in. `dreamreel plugins -v` lists the same, plus whatever this film's
`extensions/` add, with every setting.

## Cast: `cast/<name>.toml`

Every character has `name`, `voice` and a `type`.

### Voices: any language

`voice = "en_US-amy-medium"` names a ready-made Piper voice (English, and Hindi `hi_IN-priyamvada-medium`,
`hi_IN-rohan-medium`, Telugu `te_IN-maya-medium`, Malayalam `ml_IN-meera-medium`, Marathi
`mr_IN-google-medium`, Bengali `bn_BD-google-medium`, Urdu `ur_PK-fasih-medium` ...). For anything
else, `voice` is a table:

```toml
[voice]
language = "ta"          # en hi ta te bn mr kn ml gu pa or as ur ne
describe = "A warm, gentle grandmother who speaks slowly"     # a described voice (Indic Parler-TTS)
sample = "audio/samples/ammamma.wav"                          # or copy a recorded voice (IndicF5) ...
sample_text = "what the recording says, word for word"
fish = "<Fish Audio voice id>"                                # or a Fish Audio voice (paid)
speed = 0.9
```

Lines are spoken in the language of their script: write Tamil lines in Tamil script. `dreamreel voices`
shows which engines are set up; a voice that isn't available yet is spoken by a ready-made voice of
the language when there is one, otherwise the line is a subtitle only. Subtitles in every Indian
script are drawn properly shaped.

### `type = "toy"` (the default): a jointed vinyl figure

| Field | Values |
|---|---|
| `height` | 1.0 is an adult (0.7-1.3) |
| `body` | bean, round, tall, kid |
| `skin` | skin1 (lightest) ... skin6 (deepest), or a colour |
| `hair` | none, short, bob, long, ponytail, bun, space_buns, spiky, curly, mohawk |
| `hair_color`, `top`, `bottom`, `shoes` | colours |
| `outfit` | shirt, dress |
| `eyes` | small, normal, big |
| `eye_style`, `eye_color` | whites (white eyes with a coloured iris, the default) or beads (glossy toy beads); iris colour |
| `braces` | true for braces on the teeth (seen in grins) |
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

### `type = "person"`: a person (Quaternius)

```toml
type = "person"
body = "woman"         # woman or man
outfit = "casual"      # women: adventurer, casual, formal, medieval, punk, scifi, soldier, suit, witch,
                       # worker; men: adventurer, beach, casual, hoodie, farmer, king, punk, spacesuit,
                       # suit, swat, worker
height = 1.68          # metres
```

### `type = "animal"`: an animal (Quaternius)

```toml
type = "animal"
species = "husky"      # alpaca, bull, cow, deer, donkey, fox, horse, horse_white, husky, shiba_inu, stag, wolf
size = 1.0
```

People and animals come from Quaternius's free (CC0) packs, rigged and animated: they walk and
run with their own animation while dreamreel moves them round the set, idle when still, turn their
heads to look and nod, carry things, and play their gestures: people `wave`, `interact`, `punch`,
`kick`, `roll`, `die`, `flinch`; animals `eat`, `attack`, `jump`, `die`, `flinch`, `look_down`.
People sit on chairs, sofas and beds (in a set with `scale = "people"`, so the furniture fits them).
Get the packs once with `dreamreel assets --download`.

### `type = "human"`: a realistic person (MakeHuman)

```toml
type = "human"
gender = "female"           # female or male
age = 28                    # years (5-90)
build = "average"           # slim, average, athletic, heavy, stocky
heritage = "south_asian"    # african, east_asian, european, south_asian, latin, middle_eastern, mixed
skin_tone = "#8d5a3b"       # optional; else one that suits the heritage
hair = "long01"             # afro01, bob01, bob02, braid01, long01, ponytail01, short01-04, none
hair_color = "black"
eyes = "brown"              # brown, brownlight, blue, bluegreen, deepblue, green, grey, ice, lightblue
outfit = "female_elegantsuit01"   # female_elegantsuit01, female_sportsuit01, male_casualsuit01-06,
                                  # male_elegantsuit01, male_worksuit01 (any fits anyone)
outfit_tint = "teal"        # optional: the outfit in another colour
shoes = "shoes02"           # shoes01-06
face = 0.5                  # how distinctive the face is (0-1); the same name always gives the same face
seed = "twins"              # optional: the same seed gives the same person whatever the name
height = 1.62               # metres
extras = ["sunglasses", "long_coat"]   # things dreamreel makes for them (coat_color = "#101010")
```

Realistic people walk, sit (knees bent, feet on the floor), gesture with bending elbows, perform
motion capture and carry things. Their faces have ARKit's 52 shapes and 15 visemes: every mood
becomes an expression, they blink, and their mouths make the sounds of speech (`lipsync = "ai"`
with a booster moves the whole face with the voice). Get the assets once with
`dreamreel assets --pack humans`; until then a toy figure stands in.

### `type = "model"`: your own 3D model

```toml
type = "model"
file = "models/hero.glb"     # glTF/GLB, FBX or OBJ, in the film's models/ folder
height = 1.0                 # metres; toy figures are about 1 m
turn = 0                     # degrees, if it doesn't face the front after import
faces = 50000                # heavier models (AI-made, scanned) are lightened to about this
```

A rigged model (Mixamo, Ready Player Me, VRoid, Quaternius...) keeps its skeleton; an unrigged
one standing in a T or A pose is rigged automatically. Either way it walks, gestures, performs
motion capture and handles things like a toy figure. If the model has facial shape keys (blink,
smile, jawOpen; ARKit and VRM names work), moods, blinks and talking drive them; without them its
face doesn't change. Check the licence of any model you use.

`dreamreel generate NAME --prompt "..."` (or `--image picture.png`) has dreamreel's modelling agent
make a model: an AI model writes a recipe in dreamreel's modelling kit, sees renders of it from
four sides and corrects it (`--rounds`, default 3). It saves `models/NAME.glb`, the recipe
`models/NAME.json` (edit it and rebuild with `--spec models/NAME.json`) and `cast/NAME.toml`, rigged
on the skeleton in the recipe; add `--prop` for a thing instead of a character. The AI is the
film's `[ai]` in film.toml (`provider` = anthropic, openai, gemini, openrouter, ollama, lmstudio
or custom with `url`; `model`), or `--provider`/`--model`; keys come from the environment
(ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, DREAMREEL_AI_KEY). Ollama and
LM Studio run free on the film maker's own computer.
Your own models go in sets too: `[[props]] type = "model"`, `file = "models/lamp.glb"`, `height`,
`facing`, `place`.

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

Every kind of set takes `scale`: `toy` (the default: furniture for toy figures about 1 m tall) or
`people` (life-size furniture for `person` characters: 0.76 m tables, 0.46 m chair seats). The
furniture is Quaternius's models (`dreamreel assets --download --pack interior`) fitted to the same
sizes, and outdoors the trees, pines, bushes, rocks, flowers, grass and mushrooms are too (`--pack
nature`), city and old town streets are its brick buildings (`--pack city`), and cars are its
cars (`--pack cars`; a car prop's `model`: car, small, suv, sports, taxi, police);
`furniture = "simple"` uses dreamreel's own shapes instead, as it does when the packs
aren't downloaded.

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
A second thing of the same type gets `-2` (`chair-2`), or give it a `name`. Items on surfaces are
*things* that characters can pick up, carry, give and put down, named after the item (`cup`,
`cup-2`); a scalpel is an item too. An item on its own in `props` stands on the floor:
`{type = "ball", place = "front-left"}`. Dropped, thrown, knocked and kicked things move with real
physics: they fall, bounce, roll, tip over and knock into each other, then stay where they end up.

## Scenes: `scenes/NNN_name.toml`

```toml
set = "kitchen"
cast = ["mia", "tom"]        # "agent*8" brings eight identical copies of cast/agent.toml: agent_1 ... agent_8
time_of_day = "golden_hour"  # dawn, morning, day, golden_hour, sunset, dusk, night
weather = "rain"             # clear, cloudy, overcast, fog, rain, snow, storm, windy
weather_strength = 1.0       # 0.3 a little ... 2 a lot
ambience = "sea"             # the sound of the place; default: from the set, time and weather; "none"
restyle = "a watercolour painting"   # experimental, needs a booster: AI repaints the final render
restyle_strength = 0.5               # 0.1 barely ... 0.9 freely (film.toml [restyle] sets it for all)

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
| walk_to | where, speed (slow, normal, fast, run), facing, how |
| run_to | where, how |
| fly_to | where, height, land (needs wings) |
| enter | where (appears there; hidden before) |
| place | where, facing, on (standing there from the start; `on` = a table, bench, desk, counter or tray top) |
| sit | seat, already (true: sitting from the start). Bodies without arms lie down there |
| lie_down, stand, leave | |
| turn_to, look_at | target |
| feel | mood, how_much |
| gesture | gesture, target, how |
| pick_up | thing (walks over if needed), hand (right, left) |
| put_down | thing (what they hold), on (a table, counter, bench, desk or tray; else the floor) |
| give | to, thing |
| drop | thing (it falls, bounces and comes to rest) |
| throw | thing (picked up first if not held), to: a character catches it; a place, it lands and rolls |
| knock_over | thing: a sweep of the arm tips it over, or off the table |
| kick | thing (a ball on the floor), to: a character, mark or place |
| hold | thing, hand: holding it from this moment; a thing in the set, or a new item (`scalpel`) |
| grab | thing = a small character (a frog, a cat): carried like a thing, put down the same way |
| perform | motion, speed, mirror, in_place, start, end, how: play a motion-capture clip (see Motion library) |
| act | what (a sentence: "slowly gets up from the bench and stretches"), seconds (1-12), take (another version), in_place, how: motion made by AI (HY-Motion on a booster, see `dreamreel boost`), kept in motions/ai/. Without a booster: the closest gesture |
| wait (no who) | seconds |
| caption, title_card (no who) | text, duration |
| slow_motion (no who) | seconds, speed (0.3 slow ... 2 fast), ramp, after: the next story-seconds play at that speed |
| freeze_frame (no who) | seconds, after: everything stops, then carries on |
| sound (no who) | sound, volume, after: a sound effect (`dreamreel plugins sound`, or a file in `audio/sfx/`) |
| jump_cut (no who) | seconds, after: that much story is cut out and the picture jumps ahead |
| screen (no who) | effect (fade_out, fade_in, flash, dip, blackout), duration, color, after |
| shot (no who) | shot, of, other, angle, side, move, amount, to, handheld, dutch, lens, duration (see Camera) |

Time of day sets the sun, the sky and how much lamps matter (rooms get their light through the
windows). Weather changes the light everywhere; outdoors it also brings clouds, rain, snow, fog,
lightning and wind in the trees. Slow motion slows the rain too.

**How** (`how = "angrily"`): angrily, happily, sadly, nervously, proudly, lazily, excitedly,
carefully, sneakily, wildly, gently, firmly. Without it, the character's current mood decides how
they move: an angry wave is quick, big and sharp; a sad walk is slow, with small steps. Every gesture
anticipates (a small counter-move first) and follows through (overshoots and settles); long hair,
ponytails, floppy ears and antennae swing and settle; jumps squash and stretch. Within a move the
forearm trails the upper arm and the hand trails the forearm (overlapping action), and two-handed moves
are never mirror images: one side (always the same one for a character) comes a touch later and a
touch smaller. Between moves nobody is ever quite still: the trunk shifts its weight and the head
drifts (`[acting] alive = 0.5` in film.toml for less, `0` for none). `exaggeration` in film.toml (0.5
subtle ... 1 natural ... 2 very cartoony) pushes all of it; each style has its own default (the overlap,
the asymmetry and the drift grow with its square: tight on realistic people, loose on toons). In a fight,
everyone stays in it: guards stay up between exchanges, and fighters waiting their turn stand in a
stance watching.

**Where / target / facing**: a spot or seat name, a character, or `camera`, `left`, `right`, `back`.

**Moods**: neutral, happy, excited, sad, angry, surprised, worried, scared, smug, sleepy, and the
big ones: gleeful, crazed, furious, determined (gritted teeth), terrified, screaming, shocked,
disgusted, suspicious, crying (with tears), embarrassed (blushing), nervous (sweating), bored,
loving. `how_much` on `feel` (0.5 a hint ... 1 ... 1.5 pushed further) sets how strongly. A new mood
sets any of the face controls: brow_tilt, brow_lift, brow_squeeze, eyes, pupils, lids, squint,
lid_slant, smile, frown, wide, o, smirk, mouth_open, teeth, blush, tears, sweat, head_tilt
(`dr.Mood.define("smitten", smile=0.7, blush=1, lids=0.3)`).

**Gestures**: wave, nod, shake_head, shrug, point, jump, cheer, facepalm, clap, think, bow, stomp
(toys); roar, sniff, spin, tail_wag, flap, rear_up, croak, tongue (any body that has what it needs).


## Fights

**Strikes** (give a `target`; they step in until they land): jab, punch, hook, uppercut, kick, spin_kick,
flying_kick, sweep. **Reactions** (start them with the blow, `with_previous = true`, and they meet it
whenever it lands): block, dodge, flinch, knocked_down (thrown through the air on to their back, lying a
moment, getting up), get_up. **stance**: guard up, bouncing on the toes. Faces flash with effort
(`fierce`) and `pain`; the moods `focused` and `cold` suit the moments before. Blows sound where they
land and the camera feels them. A mood shapes a move but never changes when its blow lands.

Realistic people and rigged models fight with **captured moves**: real people punching, kicking,
blocking, ducking and getting up off the floor, from the CMU Motion Capture Database (free for any
use), played bone by bone and timed so the captured blow lands exactly on the beat. They're downloaded
the first time a fight needs them (`dreamreel assets --pack fights` fetches them all). When they're
**knocked down** they fall as ragdolls (real physics: they crumple, hit the ground and anything in the
way, and lie however they landed), then get up with a captured get-up that starts from how they lie.
Their feet stay where they're put: turning on the spot is stepping round (a step for every 60°, the
planted foot fixed to the ground, the other lifting), someone too far away to reach walks in before
the blow, and the feet step into the stance a captured move starts from and out of the one it ends in.
Give a body time to turn: a beat that needs it facing the other way at once can't step, and the
foot-slide check (below) says where.
A `long_coat` is cloth: its tails swing and flare in a spin kick and hang again after
(`coat_cloth = false` keeps it stiff, which renders faster when scrubbing).

Whole fights, one against many, are staged with three beats, the way stunt teams do it (attackers wait
in a ring in their stances and come in one or two at a time; every attack is answered with a block or
a dodge and a counter; whoever is beaten is thrown out of the fight, gets up and comes again; the
camera cuts on the blows):

```toml
[[beats]]
do = "surround"          # they walk to a ring round the hero
hero = "neo"
attackers = "smith_*"    # names, or a pattern
radius = 2.0
enter_from = 7.0         # they start from a ring this far out (0: from where they are)

[[beats]]
do = "brawl"
hero = "neo"
attackers = "smith_*"
exchanges = 8
doubles = 0.3            # how often two come at once
pressure = 0.35          # how hard they keep coming
seed = 1                 # another seed, another fight

[[beats]]
do = "burst"             # they all pile on; the hero bursts out, throwing them every way
hero = "neo"
attackers = "smith_*"

[[beats]]
do = "bullet_time"       # time all but stops while the camera circles (put the action after it)
of = "neo"
seconds = 0.8
speed = 0.25
```

## Sound

Scenes sound like what happens in them, with nothing to set up:

- **Footsteps** on what the floor or ground is made of (wood, carpet, concrete, grass, snow).
- **Fights**: punches and kicks whoosh; a blow smacks where it lands (on whoever flinches or blocks).
- **Claps, stomps, landings**, and any sound you add with a `sound` beat:
  `do = "sound"`, `sound = "door_close"`. `dreamreel plugins sound` shows them all: doors, glass,
  metal, wood, books, coins, knives, clicks, lasers, explosions, cartoon pops and boings...
- **Ambience** under every scene, from the place: room tone, a street's hum and cars, birds in the
  country and the woods, crickets at night, the sea, rain. `ambience = "..."` in a scene chooses.

Recorded sounds come from Kenney's CC0 packs, downloaded when first needed (`dreamreel assets --pack
sounds`); offline, dreamreel makes every sound itself. Put your own files in `audio/sfx/`:
`punch.wav` replaces the built-in punch (`punch_1.wav`, `punch_2.wav`... for variations), and any
other name becomes a new sound. Sounds follow slow motion. The music ducks under dialogue.

```toml
# film.toml
[music]
file = "audio/music/theme.mp3"
volume = 0.35
duck = 0.4                 # music volume while someone speaks (1 = no ducking)

[sound]
effects = true             # false: no sound effects
footsteps = true
ambience = true            # false: none; or the name of one for the whole film
volume = 1.0               # all sound effects
ambience_volume = 1.0
```

New sounds and ambiences are classes (`dr.Sound` with a `synth`, or a file; `dr.Ambience`), and a body
can change its footsteps by overriding `footstep_sound` (a robot clanks, a ghost is silent).

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
| `side` | auto, front, three_quarter, profile, back (with `other` too: measured from the line between them) |
| `move` | static, push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down, truck_left, truck_right, crane_up, crane_down, orbit_left, orbit_right, follow, zoom_in, zoom_out, dolly_zoom, rack_focus |
| `amount` | how much the move does (degrees for pans, tilts and orbits; metres for trucks and cranes; a share of the distance for push and pull; a lens factor for zooms) |
| `to` | pan to someone or something; rack focus onto them |
| `handheld` | true adds a human wobble to any shot or move |
| `dutch` | tilt the frame by degrees (unease) |
| `lens` | millimetres (24 wide ... 85 long); chosen from the framing otherwise |
| `duration` | seconds before the automatic camera takes over again |

Faces get headroom and lead room (space on the side they're looking towards) automatically.
Every shot of a pair stays on one side of the line between them. A fight's `two_shot` (full) is the
exception that makes the rule work: `of` is the hero, and each exchange is shot from the side their body
faces (a passing head turn doesn't count), turned a little toward the foe so their face is seen
three-quarters on; the rest of the exchange keeps that side. Someone standing between the camera and
the subject moves the camera round, up or in; they're checked as their body is posed at each moment of
the shot (an arm thrown out blocks, someone lying on the floor under the view doesn't).

## Motion library: `motions/`

Put motion-capture clips in `motions/` (`.bvh`; `.fbx`, `.glb` too), or `dreamreel motions --add
FILE --name NAME --tags walk`. `dreamreel motions` lists them. Any toy figure (or creature with two
arms and two legs) can `perform` a clip: it is retargeted to their body (arm and leg directions,
lean, head, hip height and travel, scaled to their size), whatever the source calls its joints
(CMU, Mixamo, SMPL...). `mirror = true` swaps left and right; `in_place = true` keeps them on the spot.

Clips tagged `walk` or `run` (by file name, or in `motions/library.toml`) are used for walking: the
one closest to the speed needed is looped along the path.

```toml
# motions/library.toml (optional)
[cartwheel]
file = "49_07.bvh"
start = 1.0          # seconds into the file
end = 4.5
tags = ["acrobatics"]
```

dreamreel doesn't include third-party motion capture. Free sources include the CMU Graphics Lab
Motion Capture Database (BVH) and Mixamo (FBX); check each one's licence for your film.

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
| realistic | real materials on everything (photo-scanned wood, plaster, brick, fabric, fur, skin...), real skies |

Every style also sets the camera and grade: a rim light behind whoever is in each shot and a soft face
light from beside the camera (both moved at every cut and lighting only the cast, so faces read at night
and in dim rooms without lighting up the street behind them), and for `realistic` and `noir` a film grade (teal shadows,
warm highlights), bloom on bright highlights, a little lens distortion, a vignette, motion blur, and
more light on the cast than on the walls behind them. A style of your own sets any of them:

```python
class Dusk(dr.styles.Realistic):
    rim = 1.5                     # 0: no rim light
    face_fill = 0.8               # the face light (0: none, for silhouettes)
    grade = ((0.9, 0.95, 1.05), (1, 1, 1), (1.1, 1.0, 0.9))   # lift, gamma, gain colours
    bloom, lens, vignette, motion_blur = 0.4, 0.0, 0.4, 0.5
    ambient, separation = 0.6, 0.5   # bounce light indoors; how much less the key lights the set
```

In the realistic look each surface is given the real material it is made of, worked out from what
it is (a floor, a wall, a pack's "Bark", a person's trousers, a dog). To say what something is made
of yourself, give its material a `dr_material` property (in Blender, or `mat["dr_material"] = "leather"`
in an extension): wood_floor, wood, painted_wood, plaster, brick, brick_pale, concrete, asphalt,
paving, roof, tiles, granite, metal, chrome, painted_metal, fabric, cotton, denim, linen, corduroy,
leather, carpet, grass, ground, gravel, sand, rock, bark, leaves, porcelain, paper, cardboard,
wicker, fur, skin, hair, eye, glass, car_paint, rubber, baked, wax, petals, frosting, plastic.
Textures come from ambientCG and Poly Haven (CC0); `dreamreel assets --pack materials` fetches them
all at once, otherwise each is fetched the first time it's needed.

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

## Checks: directing before rendering

`dreamreel check` builds every scene and reads it the way a director would, before anything is
rendered. Besides errors and characters standing inside each other, it warns about:

- **static camera**: a shot that holds over 10 s with no camera move and no cut
- **radio play**: three lines in a row with nobody doing anything (no gesture, move, look or change of feeling)
- **dead reaction**: someone in a shot over 4 s who isn't speaking and never reacts
- **foot slide**: a foot that should be planted skating along the ground (faster than 0.15 m/s, over 2 cm),
  measured from the animation itself, with times

Each check is a class (`class X(dr.Lint)` with `check(self, scene)` returning sentences), so a film can
add its own in `extensions/`. Tune or silence them in film.toml:

```toml
[check]
ignore = ["radio_play"]
static_camera_seconds = 14      # <check>_<setting>
dead_reaction_seconds = 6
```

## AI notes and new features

With an AI model set up (`[ai]` in film.toml, or `--provider`/`--model`; any that can see pictures,
including free local ones):

- `dreamreel review 010` cuts the rendered scene into sheets of frames stamped with their times and
  shows them, with the timeline, to the model as an animation supervisor: twinning, robotic timing,
  poses, staging, light. It also sees both sides of every cut, and the fighting at 8 frames a second. The notes go in `renders/<quality>/<scene>.review.json`.
  `--fix` asks for a revised scene that addresses them; it must build (a broken one goes back to the
  model with the error) and waits in `scenes/.proposed/`. `--apply` uses it and keeps the old scene in
  `scenes/.history/`.
- `dreamreel evolve gesture moonwalk "glides backwards while the feet walk forwards"` has the model write
  a new class from its parent's source (`--from wave` to grow it from an existing one). The draft is
  tried in a test scene for its kind in a separate process; what fails goes back to the model, and
  `--look` also has it judged on a picture made for its kind (a turnaround of a prop or character, five
  frames across a gesture, a set's view and plan, a still of a style), against a rubric for that kind. Only a class that works reaches `extensions/` (`--replace` keeps
  the old one in `extensions/.history/`). The code is the model's and runs on your computer: read it.

## Commands

| | |
|---|---|
| `dreamreel new DIR [--example]` | new project |
| `dreamreel studio [DIR]` | the app, in your browser |
| `dreamreel check [scene]` | timelines, warnings and errors, without rendering (see "Checks") |
| `dreamreel cast [names]` | picture of the cast |
| `dreamreel plan SET [--view]` | map of a set with its spots (or a picture of it) |
| `dreamreel still SCENE T [T ...]` | frames at those seconds (`--percent`, `--previz`) |
| `dreamreel contact SCENE` | frames from across a scene on one sheet |
| `dreamreel previz [scene]` / `render [scene]` | fast film / final film (`--percent`, `--force`) |
| `dreamreel plugins [kind] [-v]` | every feature and its settings |
| `dreamreel extend KIND NAME` | start a new feature as a class in `extensions/` |
| `dreamreel generate NAME --prompt/--image` | make a character (or `--prop`) with the AI modeller |
| `dreamreel review SCENE [--fix [--apply]]` | an AI model watches the render and gives notes; `--fix` rewrites the scene |
| `dreamreel evolve KIND NAME "what it does"` | an AI model writes a new feature, tried in a test scene, kept if it works |
| `dreamreel kit` | the modelling kit model recipes are written in |
| `dreamreel assets [--download] [--pack P]` | free asset packs: Quaternius 3D (people, animals, furniture...), humans, materials, sounds, fights |
| `dreamreel voices` | how to set up voices |
