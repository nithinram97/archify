# Getting started

## 1. Install

```bash
python3.13 -m venv ~/dreamreel-env
source ~/dreamreel-env/bin/activate        # Windows: ~\dreamreel-env\Scripts\activate
pip install "dreamreel[voices]"
```

That installs Blender too (as a Python module); you never open the Blender app. On Linux servers
without a screen, also install the EGL libraries: `sudo apt install libegl1 libgl1-mesa-dri libgbm1`.

## 2. Look at the example film

```bash
dreamreel new cookie --example
cd cookie
dreamreel check          # what happens when, in each scene
dreamreel contact 010    # frames from scene 010 -> renders/stills/
dreamreel previz         # the whole film, fast -> renders/the-last-cookie-previz.mp4
```

Open `scenes/010_empty_jar.py` next to the video: every line in the file is something you see.

## 3. Make your own

The friendliest way: run `dreamreel studio` and use the app in your browser (see [studio.md](studio.md)).

Or open your project folder in an AI coding agent (Claude Code, Codex or similar) and describe
your film. Every project includes `AGENTS.md`, which tells the agent how to direct with
dreamreel, check its work and show you frames. See [ai-director.md](ai-director.md).

By hand:

```bash
dreamreel new my-film
cd my-film
```

1. Describe your characters in `cast/` (copy `hero.toml`). Run `dreamreel cast` to see them.
2. Describe your places in `sets/`. Run `dreamreel plan room` to see the marks you can use.
3. Write scenes in `scenes/`, one file each, numbered in story order (`010_...`, `020_...`).
4. `dreamreel check`, then `dreamreel contact 010` to see it. Change, repeat.
5. `dreamreel render` when you're happy. Changing one scene later re-renders only that scene.

## Voices

With `dreamreel[voices]` installed, each line is spoken by the character's `voice` (a Piper voice
name; listen to them at https://rhasspy.github.io/piper-samples/). Voices download on first use and
are cached. Without voices, mouths still move from the words and lines show as subtitles.

Mouths follow the sounds of each line: lips press together for M, B and P, round for "oo", open
wide for "aa". dreamreel listens with Rhubarb Lip Sync (free, MIT, downloaded once, about 90 MB; it
runs on any computer). To skip the download, set `lipsync = "loudness"` in `film.toml` and the mouth
opens with how loud the voice is.

## Music

Put a file in `audio/music/` and add to `film.toml`:

```toml
[music]
file = "audio/music/theme.mp3"
volume = 0.35
```

## Render times

Final renders use Blender's EEVEE engine: a few seconds per frame on a laptop GPU, much slower on
CPU only. `previz` is 10-20x faster. Use `--percent 50` for half-size test renders.
