# Working with an AI model

dreamreel is built so a frontier AI model can direct a film for someone who can't animate, cheaply
and reliably:

- **The model only writes text.** Scenes are short Python files of plain verbs (`walk_to`, `say`,
  `feel`), characters and sets are small toml files. A one-minute film is a few hundred lines.
- **No 3D maths.** Models are weak at spatial reasoning, so nothing in the API takes coordinates.
  Characters move between named marks; furniture goes in named places; the camera is directed in
  film terms (close-up, over-the-shoulder) and keeps to the 180-degree rule by itself.
- **Fast feedback without rendering.** `dreamreel check` builds every scene in about a second and
  prints its timeline (who says what when, every camera cut) plus warnings such as characters
  overlapping.
- **Cheap visual feedback.** `dreamreel contact <scene>` renders a sheet of frames that a multimodal
  model can look at in one image; `dreamreel cast` and `dreamreel plan <set>` show the characters and
  a labelled map of each set.
- **Small edits stay small.** A note like "make Tom angrier in scene 2" is a one-word change, and
  only that scene re-renders.

## Setup

Every project made with `dreamreel new` contains `AGENTS.md` (instructions for the agent), `CLAUDE.md`
(points Claude Code at it) and `REFERENCE.md` (everything dreamreel can do). Open the project folder
in an agent that can run commands and read images (Claude Code, Codex, Cursor and others) and start
talking about your film.

## A session looks like this

> **You:** A 40-second film. Two kids in a park find a lost puppy, argue about who keeps it, then
> see a girl crying on a bench and give it back.
>
> **Agent:** proposes three scenes with timings → writes `cast/`, `sets/park.toml` → shows you
> `dreamreel cast` and the set plan → writes the scenes → runs `dreamreel check`, fixes an overlap →
> renders contact sheets, notices the girl faces away in the close-up and turns her → renders the previz.
>
> **You:** The argument is too short and the boy should stomp off first.
>
> **Agent:** adds two lines and a `stomp` gesture to scene 2, checks, shows the new frames.

## Tips

- Ask for the story and scene list first, before any files.
- Give notes the way you would to a person: "slower", "she should look worried", "end on a wide shot".
- Keep the previz for timing and the final render for the end.
