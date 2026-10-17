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


def venv(name, python, log):
    """A separate Python for one model (models pin different, often older, packages than the
    notebook's own): made with uv, which fetches the Python version it needs."""
    root = os.path.join(WORK, "venvs", name)
    py = os.path.join(root, "bin", "python")
    if not os.path.exists(py):
        if not shutil.which("uv") and not has("uv"):
            pip(log, "uv")
        uv = shutil.which("uv") or os.path.join(os.path.dirname(sys.executable), "uv")
        sh([uv, "venv", "-p", python, root], log)
    return py


def venv_pip(py, log, *args):
    uv = shutil.which("uv") or os.path.join(os.path.dirname(sys.executable), "uv")
    sh([uv, "pip", "install", "--python", py, *args], log)


def gpu_memory_gb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.split()
        return float(out[0]) / 1024 if out else 0.0
    except (OSError, subprocess.SubprocessError, ValueError):
        return 0.0


def run_script(py, script, job, log, cwd=None):
    """Run a model's script (a string) with its own Python, the job as JSON; returns its JSON answer."""
    os.makedirs(job["out_dir"], exist_ok=True)
    path = os.path.join(job["out_dir"], "_run.py")
    with open(path, "w") as f:
        f.write(script)
    with open(os.path.join(job["out_dir"], "_job.json"), "w") as f:
        json.dump(job, f)
    sh([py, path, os.path.join(job["out_dir"], "_job.json")], log, cwd=cwd)
    with open(os.path.join(job["out_dir"], "_answer.json")) as f:
        return json.load(f)


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


# ---------------------------------------------------------------------- acting: HY-Motion 1.0
HY_RUN = r"""
import json, os, sys
job = json.load(open(sys.argv[1]))
os.chdir(job["repo"]); sys.path.insert(0, job["repo"])
os.environ["USE_HF_MODELS"] = "0"
import torch
if job.get("small_gpu"):
    # a 16 GB card: the 8B text encoder is loaded already quantised to 4 bits, straight onto the card,
    # computing in float16 (T4s have no bfloat16)
    import transformers
    from transformers import BitsAndBytesConfig
    _orig = transformers.AutoModelForCausalLM.from_pretrained.__func__
    def _load(cls, path, *a, **kw):
        if "Qwen3" in str(path):
            kw.pop("torch_dtype", None); kw.pop("low_cpu_mem_usage", None)
            kw["device_map"] = {"": 0}
            kw["torch_dtype"] = torch.float16
            kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
                                                           bnb_4bit_quant_type="nf4")
        return _orig(cls, path, *a, **kw)
    transformers.AutoModelForCausalLM.from_pretrained = classmethod(_load)
    _to = torch.nn.Module.to
    def _safe_to(self, *a, **kw):
        if getattr(self, "is_loaded_in_4bit", False) or getattr(self, "is_quantized", False):
            return self
        return _to(self, *a, **kw)
    torch.nn.Module.to = _safe_to
from hymotion.utils.t2m_runtime import T2MRuntime
lite = job["model"]
rt = T2MRuntime(config_path=f"ckpts/tencent/{lite}/config.yml", ckpt_name=f"ckpts/tencent/{lite}/latest.ckpt",
                disable_prompt_engineering=True)
rt.generate_motion(text=job["text"], seeds_csv=str(job.get("seed", 1)), duration=float(job["seconds"]),
                   cfg_scale=5.0, output_format="fbx", output_dir=job["out_dir"], output_filename="motion")
files = sorted(os.listdir(job["out_dir"]))
fbx = next((f for f in files if f.startswith("motion") and f.endswith(".fbx")), None)
npz = next((f for f in files if f.startswith("motion") and f.endswith(".npz")), None)
if fbx is None:
    raise SystemExit("HY-Motion made no FBX (is fbxsdkpy installed?); files: " + ", ".join(files))
json.dump({"motion": os.path.join(job["out_dir"], fbx), "npz": os.path.join(job["out_dir"], npz) if npz else None},
          open(os.path.join(job["out_dir"], "_answer.json"), "w"))
"""


class HYMotion(Skill):
    name = "motion.hy_motion"
    about = "HY-Motion 1.0 (Tencent): 3D human motion from a sentence, up to 12 s"
    license = ("Tencent HY-Motion 1.0 Community License: not for the EU, UK or South Korea; outputs may not "
               "train other AI models")

    def repo(self):
        return os.path.join(REPOS, "HY-Motion-1.0")

    def installed(self):
        r = self.repo()
        return (os.path.exists(os.path.join(WORK, "venvs", "hymotion", "bin", "python"))
                and os.path.exists(os.path.join(r, "ckpts", "tencent", "HY-Motion-1.0-Lite", "latest.ckpt"))
                and os.path.isdir(os.path.join(r, "ckpts", "Qwen3-8B")))

    def install(self, log):
        r = clone("https://github.com/Tencent-Hunyuan/HY-Motion-1.0.git", "HY-Motion-1.0", log)
        sh("git lfs install && git lfs pull", log, cwd=r)       # the wooden rig the FBX export uses
        py = venv("hymotion", "3.11", log)
        venv_pip(py, log, "-r", os.path.join(r, "requirements.txt"),
                 "--extra-index-url", "https://download.pytorch.org/whl/cu124", "--index-strategy", "unsafe-best-match")
        from huggingface_hub import snapshot_download  # noqa: F401  (installed by hf_download)
        hf_download("tencent/HY-Motion-1.0", log, allow_patterns=["HY-Motion-1.0-Lite/*"],
                    local_dir=os.path.join(r, "ckpts", "tencent"))
        hf_download("openai/clip-vit-large-patch14", log, local_dir=os.path.join(r, "ckpts", "clip-vit-large-patch14"))
        # the text encoder: full precision on a big card, a 4-bit copy (about 6 GB) on a 16 GB one
        qwen = "Qwen/Qwen3-8B" if gpu_memory_gb() >= 30 else "unsloth/Qwen3-8B-bnb-4bit"
        hf_download(qwen, log, local_dir=os.path.join(r, "ckpts", "Qwen3-8B"))

    def run(self, inputs, files, out_dir, log, progress):
        text = str(inputs.get("text", "")).strip()
        if not text:
            raise ValueError("say what the character does")
        job = {"repo": self.repo(), "text": text, "seconds": max(0.7, min(12.0, float(inputs.get("seconds", 4)))),
               "seed": int(inputs.get("seed", 1)), "model": "HY-Motion-1.0-Lite", "out_dir": out_dir,
               "small_gpu": gpu_memory_gb() < 30}
        log(f"making motion: {text[:80]} ({job['seconds']:g} s)")
        return run_script(os.path.join(WORK, "venvs", "hymotion", "bin", "python"), HY_RUN, job, log, cwd=self.repo())


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


class FakeMotion(Skill):
    """For tests: a 'made' motion is the BVH file the test hands in."""
    name = "test.motion"
    about = "a test motion"
    needs_gpu = False
    test_only = True

    def installed(self):
        return True

    def run(self, inputs, files, out_dir, log, progress):
        dest = os.path.join(out_dir, "motion.bvh")
        shutil.copyfile(os.environ["DREAMREEL_TEST_MOTION"], dest)
        return {"motion": dest}


SKILLS = [IndicParler(), IndicF5(), HYMotion(), Echo(), Tone(), FakeMotion()]


def register(skill):
    SKILLS.append(skill)
    return skill


def available():
    test = bool(os.environ.get("DREAMREEL_BOOST_TEST"))
    return {s.name: s for s in SKILLS if test or not s.test_only}


if __name__ == "__main__":
    print(json.dumps({"gpu": gpu(), "skills": {n: s.installed() for n, s in available().items()}}, indent=1))
