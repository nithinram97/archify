"""Keys for AI services, kept for you on this computer, never in a film's folder.

The studio's Toolbox has a place to paste them; `dreamreel keys set FISH_API_KEY` does the same. They
are saved in ~/.config/dreamreel/keys.json (readable only by you) and act as if they were set in the
environment. A key that is really set in the environment wins.
"""
import json
import os

KEYS = {
    # name: (what it's for, where to get it)
    "HF_TOKEN": ("Indian AI voices (Indic Parler-TTS, IndicF5) and other open models",
                 "huggingface.co, Settings, Access tokens (a free 'read' token); then accept the terms on "
                 "huggingface.co/ai4bharat/indic-parler-tts and huggingface.co/ai4bharat/IndicF5"),
    "FISH_API_KEY": ("Fish Audio voices (Drama 3)", "fish.audio, then API keys (paid)"),
    "ANTHROPIC_API_KEY": ("Claude, for the AI modeller and agents", "console.anthropic.com"),
    "OPENAI_API_KEY": ("OpenAI models", "platform.openai.com"),
    "GEMINI_API_KEY": ("Gemini models", "aistudio.google.com"),
    "OPENROUTER_API_KEY": ("Any model through OpenRouter", "openrouter.ai"),
    "DREAMREEL_AI_KEY": ("A custom OpenAI-compatible endpoint", "your provider"),
    "DREAMREEL_BOOST_URL": ("A booster: AI models on a graphics card (dreamreel boost)",
                            "the address a booster prints when it starts"),
    "DREAMREEL_BOOST_TOKEN": ("The booster's pass key", "printed by the booster with its address"),
}


def path():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "dreamreel", "keys.json")


def saved():
    try:
        with open(path()) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if isinstance(v, str) and v}
    except (OSError, ValueError):
        return {}


_from_file = set()


def load():
    """Put saved keys into the environment (keys already set there win)."""
    for k, v in saved().items():
        if not os.environ.get(k) or k in _from_file:
            os.environ[k] = v
            _from_file.add(k)


def set_key(name, value):
    if name not in KEYS:
        raise ValueError(f"unknown key {name!r}; one of: {', '.join(KEYS)}")
    data = saved()
    value = (value or "").strip()
    if value:
        data[name] = value
    else:
        data.pop(name, None)
        if name in _from_file:
            os.environ.pop(name, None)
            _from_file.discard(name)
    p = path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".part"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, p)
    load()


def status():
    """Which keys are set (never their values): {name: {"set", "from", "for", "get"}}."""
    file_keys = saved()
    out = {}
    for k, (what, where) in KEYS.items():
        src = "saved" if k in file_keys and (k in _from_file or not os.environ.get(k)) else (
            "environment" if os.environ.get(k) else None)
        out[k] = {"set": src is not None, "from": src, "for": what, "get": where}
    return out
