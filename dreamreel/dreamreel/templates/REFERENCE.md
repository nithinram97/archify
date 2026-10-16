# Reference

## Cast: `cast/<name>.toml`

| Field | Values | Default |
|---|---|---|
| `name` | what the character is called on screen | file name |
| `height` | 1.0 is an adult; 0.8 short, 1.15 tall | 1.0 |
| `body` | `bean`, `round`, `tall`, `kid` | `bean` |
| `skin` | `skin1` (lightest) ... `skin6` (deepest), or a hex colour | `skin2` |
| `hair` | `none`, `short`, `bob`, `long`, `spiky`, `bun`, `curly`, `ponytail`, `mohawk` | `short` |
| `hair_color` | a colour | `brown` |
| `top`, `bottom`, `shoes` | colours | `blue`, `navy`, `charcoal` |
| `outfit` | `shirt` or `dress` (uses the `top` colour) | `shirt` |
| `eyes` | `small`, `normal`, `big` | `normal` |
| `extras` | any of `glasses`, `hat`, `cap`, `scarf`, `tie`, `bow`, `beard`, `moustache`, `headphones` | none |
| `blush`, `nose` | `true` / `false` | `true` |
| `voice` | a Piper voice name, e.g. `en_US-amy-medium` | `en_US-lessac-medium` |

**Colours**: a hex code (`"#e4572e"`) or a name: `red orange yellow green teal blue navy purple pink
cream beige wood darkwood charcoal denim mint sky brick leaf grass white black grey brown chestnut
blonde ginger`.

## Sets: `sets/<name>.toml`

```toml
kind = "room"        # "room" (no front wall) or "outdoor"
size = "medium"      # small, medium, large
walls = "mint"       # room only
floor = "wood"       # wood, tiles, carpet, concrete, stone, grass, sand, or a colour

[[props]]
type = "table"
place = "center"
chairs = 2
items = ["plate", "cup"]

[marks]              # extra named spots
by_the_plant = "left"
```

**Places** (a 3 x 3 grid, seen from the camera):

```
back-left    back     back-right       <- back wall
left         center   right
front-left   front    front-right      <- camera side
```

Each place is also a mark. Things on the back row go against the back wall.

**Props** and the marks and seats they create:

| type | options | marks / seats |
|---|---|---|
| `door` | `color` | mark `door` (just inside) |
| `window` | `view` (colour outside) | mark `window` |
| `table` | `width`, `depth`, `color`, `chairs` (0-2), `chair_color`, `items` | marks `table` (in front), `table-left`, `table-right`; seats `chair`, `chair-2` |
| `chair` | `color`, `facing` (`camera`, `left`, `right`, `back` or a mark) | seat and mark `chair` |
| `sofa` | `width`, `color`, `facing` | seats `sofa`, `sofa-2`; mark `sofa` |
| `bench` | `color`, `facing` | seats `bench`, `bench-2`; mark `bench` |
| `counter` | `width`, `color`, `top`, `items` | mark `counter` |
| `fridge`, `bookshelf`, `plant`, `lamp`, `rug` | `color` | mark (fridge) |
| `tree`, `streetlamp`, `house` | outdoor props | marks `tree`, `house` |

Table and counter `items`: `cookie-jar`, `cookie`, `plate`, `cup`, `vase`, `laptop`, `book`.

A second prop of the same type gets `-2`, `-3`... (`chair-2`), or give it a `name`.
Outdoor sets also take `ground`, `path` (true/false), `trees` (count) and `hills` (count).

## Scenes: `scenes/<NNN_name>.py`

```python
import dreamreel as dr
s = dr.Scene("kitchen")                 # set name; time_of_day="night" for evening light
mia, tom = s.cast("mia", "tom")
```

### Time

Each action starts when the previous one ends.

| | |
|---|---|
| `with s.together():` | everything inside starts at the same moment |
| `s.wait(1.5)` | a pause |
| `s.at(12.0)` | jump the clock to 12 s |
| `at=` on any action | start that action at an exact time |
| `wait=False` on any action | don't hold up the next action |

### Actions (on a character)

Where to: a **mark** (`"door"`, `"table"`, `"front-left"`), a **seat**, or **another character**
(walking to a character stops in front of them).

| Action | What it does |
|---|---|
| `place(where, facing=None)` | stand there from the start |
| `enter(where, facing=None)` | appear there now (hidden until then) |
| `leave()` | disappear now |
| `walk_to(where, speed="normal", facing=None)` | walk there, round furniture. speed: `slow`, `normal`, `fast`, `run` |
| `run_to(where)` | run there |
| `turn_to(target)` | turn the whole body: a character, a mark, `"camera"`, `"left"`, `"right"`, `"back"` |
| `look_at(target)` | turn just the head |
| `look_forward()` | head back to straight |
| `sit(seat)` | walk to the seat and sit; `already=True` = sitting when the scene starts |
| `stand()` | get up |
| `say(line, mood=None, to=None)` | speak (voice, mouth, subtitle); `to` = who they're talking to |
| `feel(mood)` | change expression |
| `do(gesture, target=None)` | play a gesture |

**Moods**: `neutral`, `happy`, `excited`, `sad`, `angry`, `surprised`, `worried`, `scared`, `smug`, `sleepy`.

**Gestures**: `wave`, `nod`, `shake_head`, `shrug`, `point` (at `target`), `jump`, `cheer`, `facepalm`,
`clap`, `think`, `bow`, `stomp`.

Characters blink and breathe on their own.

### Camera

Without any camera lines, dreamreel directs the scene itself (`auto`). To choose shots, write them
where they should start:

| | |
|---|---|
| `s.cut.wide()` | the action area of the set |
| `s.cut.medium(who)` | waist up |
| `s.cut.close_up(who)` | face |
| `s.cut.two_shot(a, b)` | both characters |
| `s.cut.over_shoulder(past, on=who)` | past one character's shoulder onto the other's face |
| `s.cut.from_point(mark, look_at)` | camera at a mark, aimed at a character or mark |

### Text

| | |
|---|---|
| `s.caption("Meanwhile...", duration=3)` | text over the picture |
| `s.title_card("Chapter 1", duration=2.5)` | full-screen card before the scene |

Dialogue becomes subtitles automatically.

## Commands

| | |
|---|---|
| `dreamreel new DIR [--example]` | new project |
| `dreamreel check [scene]` | build scenes and print timelines and warnings (no rendering) |
| `dreamreel cast [names]` | picture of the cast |
| `dreamreel plan SET` | top-down map of a set with marks and seats |
| `dreamreel still SCENE T [T ...] [--percent N] [--previz]` | frames at those seconds |
| `dreamreel contact SCENE [--count N]` | evenly spaced frames on one sheet |
| `dreamreel previz [scene]` | fast flat-shaded film |
| `dreamreel render [scene] [--percent N] [--force]` | final film |
| `dreamreel voices` | how to set up voices |

Scenes are named by number or name: `010`, `empty_jar`, `010_empty_jar`.
