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
- Places: eight outdoor biomes with generated terrain and rule-based scenery, a generated town
  street, rooms that furnish themselves, seven times of day and eight kinds of weather.
- Looks: eight visual styles (toy, toon, anime, clay, paper, storybook, noir, realistic) for a
  whole film or a single scene.
- Acting: effort (Laban) shapes every gesture and walk; anticipation, follow-through springs,
  squash and stretch; cutting on action.
- Handling things: pick up, carry, give, put down, drop, grab small characters.
- Motion library: BVH/FBX clips retargeted to any two-armed, two-legged body; library walk cycles.

Next, roughly in order:

## Looks
- Styles that change over a scene (fading into a memory); hatching and watercolour styles.

## Acting
- Open doors, sit on and climb things.
- Physics for bodies (a character tripping and falling as a ragdoll), cloth and things that break.
- Walk cycles that follow curves and stairs; crowds walking in the background.
- More gestures (hug, high-five, dance, fall over, sneak) and gesture layering while talking.
- Better lip sync from phonemes (Rhubarb Lip Sync) instead of loudness.
- Eye direction (eyes follow before the head turns).

## Characters
- Quaternius everywhere: buildings, streets and vehicles from its packs (people, animals, furniture and nature are done); the base characters with the Universal Animation Library (talking, dancing).
- A character designer: describe a person in a sentence and get a cast file with a turnaround image.
- CC0 asset packs as props and sets (Kenney, Quaternius, Poly Haven); fingers on imported models.

## Places
- More set kinds: space station, castle, underwater; rivers and lakes in biomes.
- Time of day changing during a scene (a sunset as it happens, lights coming on).
- Sets that span several rooms, with cuts between them.

## Film-making
- Shot variety learnt from scene content (reaction shots, cutaways to props).
- Sound effects library and footsteps; music ducking under dialogue.
- Cloud voice engines as plugins; multi-language voices and subtitles.

## Tooling
- An MCP server so any AI model can drive dreamreel as tools.
- dreamreel studio (done in 0.1): next, an "Ask the AI director" panel that takes notes in plain
  words, drag-and-drop blocking on the floor plan, and a one-click installer with no terminal.
- Render farm / GPU cloud render command.
