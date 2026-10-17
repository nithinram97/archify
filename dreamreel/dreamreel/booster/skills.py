"""What a booster can do. A skill installs its model the first time it's used, then runs jobs:

    class MySkill(Skill):
        name = "kind.model"
        about = "one sentence"
        license = "MIT"
        def installed(self): ...                         # quick check: packages and weights present
        def install(self, log): ...                      # pip installs, git clones, weight downloads
        def run(self, inputs, files, out_dir, log, progress):
            return {"name": "path/of/a/file/in/out_dir", "other": "a plain value"}

Skills run on the booster (a graphics card, often a fresh notebook), never on the film maker's
computer, and get their inputs from dreamreel (boost.py) as plain values and files.
"""
import importlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("DREAMREEL_BOOST_WORK") or os.path.join(os.path.expanduser("~"), ".cache", "dreamreel-booster")
REPOS = os.path.join(WORK, "repos")


def gpu():
    """The graphics card's name and memory, or None."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return out.splitlines()[0] if out else None
    except (OSError, subprocess.SubprocessError):
        return None


def has(*modules):
    return all(importlib.util.find_spec(m) is not None for m in modules)


def sh(cmd, log, cwd=None, env=None):
    """Run a command, passing its output to the job's log; raise if it fails."""
    log("$ " + (cmd if isinstance(cmd, str) else " ".join(cmd))[:300])
    p = subprocess.Popen(cmd, shell=isinstance(cmd, str), cwd=cwd, env=dict(os.environ, **(env or {})),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    tail = []
    for line in p.stdout:
        line = line.rstrip()
        if line:
            tail = (tail + [line])[-30:]
            log(line)
    if p.wait():
        raise RuntimeError(f"command failed ({p.returncode}): " + " | ".join(tail[-5:]))


def pip(log, *pkgs):
    sh([sys.executable, "-m", "pip", "install", "-q", *pkgs], log)
    importlib.invalidate_caches()


def clone(url, name, log, ref=None):
    """A model's code, cloned once into the booster's work folder."""
    dest = os.path.join(REPOS, name)
    if not os.path.isdir(os.path.join(dest, ".git")):
        os.makedirs(REPOS, exist_ok=True)
        sh(["git", "clone", "--depth", "1"] + (["--branch", ref] if ref else []) + [url, dest], log)
    return dest


def hf_download(repo, log, **kw):
    """A model's weights from Hugging Face (HF_TOKEN for gated ones)."""
    if not has("huggingface_hub"):
        pip(log, "huggingface_hub")
    from huggingface_hub import snapshot_download
    log(f"downloading {repo} ...")
    return snapshot_download(repo, token=os.environ.get("HF_TOKEN") or None, **kw)


class Skill:
    name = ""
    about = ""
    license = ""
    needs_gpu = True
    test_only = False

    def installed(self):
        return False

    def install(self, log):
        pass

    def run(self, inputs, files, out_dir, log, progress):
        raise NotImplementedError


# ---------------------------------------------------------------------- voices (speakers.py)
def _speakers():
    sys.path.insert(0, os.path.dirname(HERE))
    return importlib.import_module("speakers")


class IndicParler(Skill):
    name = "voice.indic_parler"
    about = "Indic Parler-TTS: a voice described in words, 21 Indian languages and English (AI4Bharat)"
    license = "Apache-2.0 (accept the terms at huggingface.co/ai4bharat/indic-parler-tts; needs HF_TOKEN)"
    engine = "indic_parler"
    packages = ("torch", "transformers", "parler_tts")

    def installed(self):
        return has(*self.packages)

    def install(self, log):
        pip(log, "git+https://github.com/huggingface/parler-tts.git")

    def run(self, inputs, files, out_dir, log, progress):
        job = dict(inputs)
        job["out"] = os.path.join(out_dir, "speech.wav")
        if "sample" in files:
            job["sample"] = files["sample"]
        log(f"speaking: {inputs.get('text', '')[:80]}")
        _speakers().SPEAK[self.engine](job)
        return {"speech": job["out"]}


class IndicF5(IndicParler):
    name = "voice.indic_f5"
    about = "IndicF5: copies a voice from a short recording, 11 Indian languages (AI4Bharat)"
    license = "MIT (accept the terms at huggingface.co/ai4bharat/IndicF5; needs HF_TOKEN)"
    engine = "indic_f5"
    packages = ("torch", "transformers", "f5_tts")

    def install(self, log):
        pip(log, "f5-tts", "transformers", "soundfile")


class Echo(Skill):
    """For tests: echoes its inputs, copies its file, and can fail on request."""
    name = "test.echo"
    about = "a test skill"
    license = "MIT"
    needs_gpu = False
    test_only = True

    def installed(self):
        return os.path.exists(os.path.join(WORK, "echo-installed"))

    def install(self, log):
        log("installing echo")
        os.makedirs(WORK, exist_ok=True)
        open(os.path.join(WORK, "echo-installed"), "w").close()

    def run(self, inputs, files, out_dir, log, progress):
        if inputs.get("fail"):
            raise RuntimeError("asked to fail")
        progress(0.5)
        out = {"echo": inputs}
        if "file" in files:
            dest = os.path.join(out_dir, "copy" + os.path.splitext(files["file"])[1])
            shutil.copyfile(files["file"], dest)
            out["copy"] = dest
        return out


class Tone(IndicParler):
    """For tests: the stand-in voice model of speakers.py."""
    name = "voice.tone"
    about = "a test voice"
    engine = "tone"
    needs_gpu = False
    test_only = True

    def installed(self):
        return True


SKILLS = [IndicParler(), IndicF5(), Echo(), Tone()]


def register(skill):
    SKILLS.append(skill)
    return skill


def available():
    test = bool(os.environ.get("DREAMREEL_BOOST_TEST"))
    return {s.name: s for s in SKILLS if test or not s.test_only}


if __name__ == "__main__":
    print(json.dumps({"gpu": gpu(), "skills": {n: s.installed() for n, s in available().items()}}, indent=1))
