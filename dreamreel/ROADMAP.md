# Roadmap

The goal and the quality bar every feature is measured against are in [docs/vision.md](docs/vision.md):
Hollywood quality, for anyone with a story, with little or no budget.

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
- (Done: the realistic look puts photo-scanned CC0 materials on everything and lights outdoor scenes
  with real skies.) Next: fur strands on animals in close-ups, grass blades, wet and weathered
  surfaces after rain, and textures from the AI for made models.
- Styles that change over a scene (fading into a memory); hatching and watercolour styles.
- (Experimental: AI restyling of final renders with Wan 2.1 on a booster.) Next: steadier frames
  (overlapping windows, guiding with depth and outlines), and the larger Wan models on bigger cards.

## Acting
- Open doors, sit on and climb things.
- Ragdolls beyond fights (tripping, falling down stairs), cloth for more clothes (skirts, capes, flags), and
  things that break. (Done: ragdoll knockdowns, captured fight moves, a cloth coat.)
- Walk cycles that follow curves and stairs; crowds walking in the background.
- More gestures (hug, high-five, dance, fall over, sneak) and gesture layering while talking.
- (Done: lip sync from the sounds of speech, with Rhubarb Lip Sync; visemes and the whole face from the voice
  for realistic people.) Next: NVIDIA Audio2Face-3D (open since 2025) as a booster skill.
- Eye direction (eyes follow before the head turns).

## Characters
- (Done: realistic people from MakeHuman's CC0 assets, with ARKit's 52 face shapes and visemes, and
  bending elbows and knees.) Next: more outfits and hair (MakeHuman's community packs), fingers that
  grip, eyes that look where the head is about to turn, and ARKit faces transferred onto Quaternius
  people and AI-made heads.
- Quaternius everywhere: buses and trains, street props and a modular-kit builder for varied buildings (people, animals, furniture, nature, city buildings and cars are done); the base characters with the Universal Animation Library (talking, dancing).
- The AI modeller, further: rigs for four legs, wings and tails; an animation preset library any
  rigged model can play; facial shape keys on made heads so they talk and emote; style filters
  (voxel, brick, clay); splitting models into parts; exporting to other formats. (The modelling
  agent with any AI, part-aware rigging and lightening heavy models are done.)
- A character designer: describe a person in a sentence and get a cast file with a turnaround image.
- (Done: models from a picture with TripoSG and rigging any model with UniRig, on a booster.) Next:
  textures from the AI (not only a projected picture), and SkinTokens, UniRig's successor.
- CC0 asset packs as props and sets (Kenney, Quaternius, Poly Haven); fingers on imported models.

## Places
- More set kinds: space station, castle, underwater; rivers and lakes in biomes.
- Time of day changing during a scene (a sunset as it happens, lights coming on).
- Sets that span several rooms, with cuts between them.

## Film-making
- (Done: fight choreography: strikes and reactions that meet, knockdowns, get-ups, stances, fight faces, camera shake,
  bullet time, and surround / brawl / burst staging of one against many; identical clones with `name*N`.)
- Fights with things: staffs, poles and chairs as weapons; bodies hitting walls, cars and each other.
- Knockdowns driven by physics (ragdolls) for falls nobody has to choreograph.
- Shot variety learnt from scene content (reaction shots, cutaways to props).
- (Done: sound effects, footsteps, ambience and music ducking, see REFERENCE.md "Sound".)
- Sounds placed in space (louder near the camera, panned left and right); pitch following slow motion.
- Cloud voice engines as plugins; multi-language voices and subtitles.

## Tooling
- (Done: an MCP server, `dreamreel mcp`, so any AI assistant can direct a film.)
- dreamreel studio (done in 0.1): next, an "Ask the AI director" panel that takes notes in plain
  words, drag-and-drop blocking on the floor plan, and a one-click installer with no terminal.
- Render farm / GPU cloud render command.
