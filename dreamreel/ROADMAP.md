# Roadmap

dreamreel 0.1 can make a short dialogue film with toy-figure characters in rooms and simple outdoor
places, with voices, subtitles and automatic camera coverage.

Since then:
- Any body: body plans for bipeds, four-legged animals, birds, fish, snakes, insects, spiders and
  blobs (and dragons, by giving a quadruped wings), with gaits, flying and swimming.
- A real camera: thirteen framings × five angles × sides, Dutch tilt and lens, nineteen camera
  moves, the 180° rule, lead room, obstruction avoidance and a mood-aware automatic director.
- Editing: ten transitions, an edit list with cross-cutting, J and L cuts and split screens, slow
  motion with speed ramps, freeze frames, jump cuts and screen effects.

Next, roughly in order:

## Places and looks (next)
- Environments: terrain, sky and weather, more interiors, rule-based layout of furniture and nature.
- Visual styles: toon, clay, anime, noir, storybook, realistic.

## Acting
- Hold and hand over props (`pick_up`, `give`, `put_down`), open doors.
- Walk cycles that follow curves and stairs; crowds walking in the background.
- More gestures (hug, high-five, dance, fall over, sneak) and gesture layering while talking.
- Better lip sync from phonemes (Rhubarb Lip Sync) instead of loudness.
- Eye direction (eyes follow before the head turns).

## Characters
- More hair and outfits; robots and monsters as body plans.
- A character designer: describe a person in a sentence and get a cast file with a turnaround image.
- Import your own models (glTF) and CC0 asset packs (Kenney, Quaternius, Poly Haven).

## Places
- More set kinds: street, office, classroom, forest, beach, space station.
- Weather (rain, snow, wind) and time of day animation (sunset, lights coming on).
- Sets that span several rooms, with cuts between them.

## Film-making
- Shot variety learnt from scene content (reaction shots, cutaways to props).
- Sound effects library and footsteps; music ducking under dialogue.
- More looks: claymation (12 fps, fingerprint texture), paper cut-out, low-poly storybook.
- Cloud voice engines as plugins; multi-language voices and subtitles.

## Tooling
- An MCP server so any AI model can drive dreamreel as tools.
- dreamreel studio (done in 0.1): next, an "Ask the AI director" panel that takes notes in plain
  words, drag-and-drop blocking on the floor plan, and a one-click installer with no terminal.
- Render farm / GPU cloud render command.
