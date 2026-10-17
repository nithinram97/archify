# Modeling: what makes a 3D model look good

dreamreel builds every model from code: characters, animals, props and buildings. Code can make a
cylinder in one line, and that is the trap: models made of primitives look like toys. This page
collects the sculpting and modeling principles the generators follow, so new plugins (written by
people or AI) can follow them too.

## 1. Big, medium, small (primary, secondary, tertiary forms)

Sculptors work in three passes, and never skip one:

1. **Primary forms**: the few big masses and the silhouette. For a person, the cranium, the
   ribcage, the pelvis and the limbs; for a car, the body and the wheels; for a house, the walls
   and the roof. Proportions are decided here and can't be rescued later.
2. **Secondary forms**: the forms that explain how the thing is built. On a face: eye sockets, brow
   ridge, cheekbones, cheek fat, nose wings, lips, chin. On a machine: panels, housings, joints,
   handles. On a building: window recesses, sills, trims, doors.
3. **Tertiary detail**: wrinkles, freckles, screws, seams, cracks, wear. Small, last, and never a
   fix for weak big forms.

A generator that stops after pass 1 makes a toy. Pass 2 is where things start to look made.

## 2. Silhouette first

A model is read by its outline first, so it should be recognisable as a solid black shape, from
the front and from the side. Check the blockout from several angles before adding detail: a
design that works from the front can be too thin or unbalanced from the side. A clear silhouette
beats a busy surface ("the squint test": squint and the main shape should still read).

## 3. Shape language, and straights against curves

Shapes carry character: circles read as friendly and soft, squares as solid and dependable,
triangles as dynamic or dangerous (Mr. Incredible's blocky build, Elastigirl's long one).
Appeal also comes from contrast: **set straights against curves**. A straight line leads the eye
quickly; a curve slows it down. An arm has a straight underside and a curved top; a leg has a
straight shin and a curved calf. Limbs taper; nothing in nature is a tube of one width. Even a
straight limb gets a slight curve that follows the pose.

## 4. The human head

Construction (Loomis): a ball for the cranium, sliced at the sides, with the face hung below it.
The planes of the head (Asaro): the forehead turns into the temples, the eye sockets are set in
(the "orbital inset"), the cheekbones form a ridge from the eye corner towards the ear, the
muzzle (mouth area) is a rounded cylinder in front of the teeth, the chin is a small box.

Landmarks, for an adult:
- The eyes are **halfway** down the head (top of the skull to chin), not higher.
- The face divides into thirds: hairline to brow, brow to the bottom of the nose, nose to chin.
- The head is about **five eyes** wide; there is one eye's width between the eyes.
- The ears run from the brow line (or the eyes) down to the bottom of the nose, set behind the
  middle of the head.
- The mouth's corners line up below the pupils; the lower lip sits halfway between nose and chin.

For a child the cranium is the same size while the face is smaller: the **brows** are on the
halfway line, the eyes below it, and the features look bigger because they are closer together,
not because they are larger. The nose, mouth and jaw grow down and forward with age.

Stylized film faces push this: bigger crania, larger eyes set in real sockets, a small nose, full
cheeks and a soft jaw on children; more planes and a stronger jaw on adults.

Eyes are balls in sockets with lids that slide over them (skin, with a lash line at the edge);
blinks and expressions move the lids, not the eyeballs. Mouths are lips: closed, they make a line
between two soft shapes; the dark inside only shows when they open.

## 5. The human body

Block the body as three masses: the **cranium**, the **ribcage** (an egg, wide at the top) and the
**pelvis** (a box/bowl, narrower), joined by the flexible neck and waist. Fix the bony landmarks
first (collarbones, the iliac crest at the hip, knees, ankles, wrists, elbows): they don't move
when muscle volume is added. Then add the muscle groups that shape the outline (shoulders,
chest, buttocks, thighs, calves, forearms), not every muscle.

Stylized proportions in heads: about 3-4 heads tall for a child character, 5-6 for a teen, 6-7.5
for an adult (real adults are about 7.5). Shoulders are about two head-widths on a man, less on a
woman and a child; the hips are about as wide as the shoulders on a woman.

Hands: a palm (a slightly cupped box), four fingers in three segments that taper, and a thumb
that comes from the side of the palm, not its end. Feet (or shoes): a wedge, heel to toe, with the
ankle bones (inner higher than outer).

## 6. Animals

All legs have the same joints (hip, knee, ankle, toes); what changes is the proportions:
- **Plantigrade** (people, bears, mice, raccoons): the whole foot on the ground.
- **Digitigrade** (dogs, cats, birds): on the toes, heel raised. The "backwards knee" is the
  **ankle**; the long bone above the toes is the foot. Make the shin shorter and the foot longer.
- **Unguligrade** (horses, deer, cows): on hooves (big toenails), the foot even longer.

Birds hide the thigh inside the body. Animals are blocked like people: skull, ribcage, pelvis, and
a spine that runs through them (the line of action), with the neck and tail continuing it.

## 7. Equipment and props (hard surface)

Hard-surface models follow the same three passes: the primary shape that makes it recognisable
(a microscope's arm and base, a scalpel's handle and blade), then the structure that explains how
it works (panels, supports, openings, handles, joints), then screws, vents, seams and labels. Test
each detail: does it improve the silhouette, explain a function, separate materials, or guide the
eye? If not, leave it out.

Real objects have **no perfectly sharp edges**: bevel every edge a little so it catches light.
Use few materials, each clearly different (metal, glass, plastic, rubber).

## 8. Buildings and sets

Build from a **kit**: walls, corners, roofs, trims, windows, doors and arches that snap together on
a grid, so many buildings come from a few pieces. Keep proportions right at blockout (doors about
2 m, storeys about 3 m) and add depth: windows set into walls, sills and frames that stick out,
roofs that overhang. Break repetition with variation (window placement, colour, wear). Stylized
buildings exaggerate proportions and lean slightly ("wonky" verticals, bold shapes), but stay
readable as one silhouette.

## How dreamreel applies this

dreamreel's models come from Quaternius's free (CC0) packs, made by an artist who applies these
principles: people and animals (rigged and animated), and, step by step, furniture, nature,
buildings and vehicles. The principles above are the checklist for anything dreamreel still makes
in code, and for judging new packs.

## Sources

- [Loomis method](https://finearttutorials.com/guide/loomis-method/); [CG Cookie: intro to sculpting the human head](https://cgcookie.com/lessons/intro-to-sculpting-the-human-head)
- [Head proportions (Fiveable study guide)](https://fiveable.me/drawing-foundations/unit-10/proportions-human-body/study-guide/bVYcw96jRRpCUZJk); [Drawing the head (Cut Out + Keep)](https://www.cutoutandkeep.net/projects/drawing-the-head/print); [Children's proportions (Drawing Faces, O'Reilly)](https://oreilly.com/library/view/drawing-faces/9781560100027/xhtml/ch04.html)
- [Anatomy for artists: masses of the skull, ribcage and pelvis (KTH handout)](https://www.csc.kth.se/utbildning/kth/kurser/DH2640/grip07/pdf/anatomy.pdf); [Anatomy for 3D artists: landmarks, silhouette](https://www.hitem3d.ai/blog/en-Anatomy-for-3D-Artists-Essential-Knowledge-for-Sculpting-Realistic-Characters)
- [Character shape language](https://blog.cg-wire.com/character-shape-language/); [Straights and curves (Creature Art Teacher)](https://creatureartteacher.com/lesson/11-straights-curves/); [How to simplify figures for animation (Creative Bloq)](https://www.creativebloq.com/how-to/simplfy-figures-for-animation)
- [Pixar: Eyes Without a Face (detached facial features)](https://graphics.pixar.com/library/DFF)
- [Quadruped anatomy for animators (School of Motion)](https://schoolofmotion.com/blog/how-to-rig-quadrupeds-animation); [Animal leg anatomy cheat sheet](https://line-of-action.com/nl/article/animal-leg-anatomy-cheat-sheet)
- [Hard surface modeling in Blender: primary forms, structure, detail (GarageFarm)](https://garagefarm.net/blog/hard-surface-modeling-in-blender)
- [Creating modules for stylised environments (80.lv)](https://80.lv/articles/creating-modules-for-stylised-environments/)
- [Quaternius: free CC0 3D packs](https://quaternius.com)
