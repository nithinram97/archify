# dreamreel

**Your dream animated film, made easy.** Write what happens; dreamreel builds the characters, the
sets, the acting and the camera work in Blender, and renders the film. No animation skills, no
Blender knowledge, no keyframes.

![Frames from the example film, "The Last Cookie"](docs/media/contact-sheet.jpg)

```python
import dreamreel as dr

s = dr.Scene("kitchen")
mia, tom = s.cast("mia", "tom")

tom.sit("chair-2", already=True)
mia.enter("door").walk_to("counter")
mia.feel("surprised")
mia.turn_to(tom)
mia.say("Tom. The cookie jar is empty.", mood="worried", to=tom)
tom.say("Is it? How strange.", mood="worried", to=mia)
tom.do("shrug")
```

That's a scene. Mia walks in through the door and round the table, her face changes, she talks
with her mouth in sync with her voice, Tom answers, and the camera covers it like a TV director
would: a wide shot while people move, then over-the-shoulder shots and close-ups for the dialogue,
always on the same side of the conversation.

## Why not AI video generation?

| AI video generators | dreamreel |
|---|---|
| Characters change from shot to shot | The same character file in every shot, forever |
| Every change means generating again (and paying again) | Change one line, re-render that scene, for free |
| A few seconds per clip, wobbly motion | Any length; real camera; physically consistent |
| You get pixels | You get a plain-text project: edit it, version it, re-render it in 4K |
| Tokens are spent on pixels | An AI model only writes text (the script); rendering runs on your machine |

dreamreel is designed to be driven by a frontier AI model: you describe the film, the model writes
the project files, `dreamreel check` tells it what happens when (without rendering), and
`dreamreel contact` renders a sheet of frames it can look at. See [docs/ai-director.md](docs/ai-director.md).

## Install

```bash
pip install dreamreel            # includes Blender itself (as the bpy module); no separate install
pip install "dreamreel[voices]"  # optional: free offline voices (Piper)
```

Needs Python 3.13 (what Blender 5.2's `bpy` is built for). A GPU makes final renders much faster
but isn't required.

## Make a film

```bash
dreamreel new my-film --example   # a finished 50-second short to learn from
cd my-film
dreamreel cast                    # picture of the cast
dreamreel plan kitchen            # map of the set with its marks
dreamreel check                   # every scene's timeline, in a second
dreamreel contact 010             # 6-9 frames of scene 010 on one sheet
dreamreel previz                  # fast flat-shaded film with voices and subtitles
dreamreel render                  # the final film (only changed scenes re-render)
```

A project is a folder of plain text:

```
my-film/
  film.toml              title, frame rate, resolution, scene order, music
  cast/mia.toml          how each character looks and sounds
  sets/kitchen.toml      each place: room or outdoor, furniture, marks
  scenes/010_jar.py      each scene: who does what, in order
  audio/                 your music; generated voices are cached here
  renders/               everything dreamreel renders
```

## The look

![Four characters, each described in a few lines of text](docs/media/cast.jpg)

dreamreel's first style is **toy figures**: jointed vinyl characters with big heads and stubby limbs,
in miniature sets with soft light and shallow depth of field. It's a style where procedural animation
looks intentional instead of stiff. More styles (claymation, paper cut-out) are on the
[roadmap](ROADMAP.md).

## Docs

- [Getting started](docs/getting-started.md)
- [Reference](dreamreel/templates/REFERENCE.md): cast, sets, actions, moods, gestures, camera
- [Working with an AI model](docs/ai-director.md)
- [Roadmap](ROADMAP.md)

## Licence

MIT. Blender (bpy) is GPL; Piper voices have their own licences (see each voice's model card).
