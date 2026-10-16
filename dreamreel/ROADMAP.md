# Roadmap

dreamreel 0.1 can make a short dialogue film with toy-figure characters in rooms and simple outdoor
places, with voices, subtitles and automatic camera coverage. Next, roughly in order:

## Acting
- Hold and hand over props (`pick_up`, `give`, `put_down`), open doors.
- Walk cycles that follow curves and stairs; crowds walking in the background.
- More gestures (hug, high-five, dance, fall over, sneak) and gesture layering while talking.
- Better lip sync from phonemes (Rhubarb Lip Sync) instead of loudness.
- Eye direction (eyes follow before the head turns).

## Characters
- More body types (animals, robots, monsters), more hair and outfits.
- A character designer: describe a person in a sentence and get a cast file with a turnaround image.
- Import your own models (glTF) and CC0 asset packs (Kenney, Quaternius, Poly Haven).

## Places
- More set kinds: street, office, classroom, forest, beach, space station.
- Weather (rain, snow, wind) and time of day animation (sunset, lights coming on).
- Sets that span several rooms, with cuts between them.

## Film-making
- Camera moves: push in, follow a walker, crane up, handheld.
- Shot variety learnt from scene content (reaction shots, cutaways to props).
- Sound effects library and footsteps; music ducking under dialogue.
- More looks: claymation (12 fps, fingerprint texture), paper cut-out, low-poly storybook.
- Cloud voice engines as plugins; multi-language voices and subtitles.

## Tooling
- An MCP server so any AI model can drive dreamreel as tools.
- A simple desktop app: story -> scenes -> previz with notes, for people who don't use a terminal.
- Render farm / GPU cloud render command.
