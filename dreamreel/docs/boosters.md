# Boosters: AI on a graphics card, for free

dreamreel runs on an ordinary laptop. A few of its AI helpers need a graphics card (NVIDIA, CUDA) to
be quick: Indian AI voices, acting from a sentence, 3D models from a picture, rigging any model,
faces driven by the voice, and restyling a scene. A **booster** runs them somewhere that has one,
while dreamreel and your film stay on your computer:

- **Free:** a Google Colab (or Kaggle) notebook with a T4 graphics card.
- **Your own computer** with an NVIDIA graphics card: `dreamreel boost serve`.
- **A rented cloud GPU**, the same way.

Everything that can use a booster also works without one: voices fall back to ready-made ones,
models to the recipe modeller, rigging to dreamreel's own rigger, faces to lip sync from the sounds.

## Start one on Colab

1. In dreamreel studio, open **Toolbox → Booster** and click **Open the free booster notebook**
   (or open `notebooks/dreamreel-booster.ipynb` in Colab yourself).
2. **Runtime → Change runtime type → T4 GPU**, then **Runtime → Run all**.
3. The last cells print an **address** (`https://....trycloudflare.com`) and a **pass key**. Paste them
   into the Booster card, or run `dreamreel boost connect <address> <pass key>`.
4. Keep the tab open while you work. Free notebooks stop after some hours or when idle: run it again
   and reconnect (the address changes each time).

Only someone with the pass key can use your booster. The address and key are saved on your computer
(`~/.config/dreamreel/keys.json`), never in a film's folder.

## On a computer with a graphics card

```bash
dreamreel boost serve                 # prints its pass key; listens on port 8780
dreamreel boost connect http://that-computer:8780 <pass key>      # on the computer you work on
```

The booster is one folder (`dreamreel/booster/`) that needs only Python 3.10+: it doesn't need
Blender or the rest of dreamreel, and installs each model the first time it's asked for it.

## What a booster can do

`dreamreel boost` lists the skills of the connected booster and whether each is installed.

| Skill | What for | Model (licence) | Status |
|---|---|---|---|
| `voice.indic_parler` | Voices described in words, 21 Indian languages | AI4Bharat Indic Parler-TTS (Apache-2.0; accept its terms, needs a Hugging Face token) | Built; not yet run on a real GPU |
| `voice.indic_f5` | Copying a recorded voice, 11 Indian languages | AI4Bharat IndicF5 (MIT; accept its terms, needs a Hugging Face token) | Built; not yet run on a real GPU |

More skills (acting, models, rigging, faces, restyling) are being added; see the roadmap. "Not yet
run on a real GPU" means dreamreel's side is tested against a stand-in booster, and the model code
follows each model's own documentation, but nobody has run it end to end yet. Please report what
happens when you do.

## How it works

dreamreel sends a job (a skill name, settings and files) over HTTPS; the booster runs jobs one at a
time on its graphics card and sends back the results (a voice line, a motion, a model). Files are
sent once and kept by their contents. If a model needs your Hugging Face token, dreamreel passes the
one you saved with the job. The HTTP API is described at the top of `dreamreel/booster/server.py`;
new skills are classes in `dreamreel/booster/skills.py`.
