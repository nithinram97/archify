"""AI models dreamreel's agents talk to: any frontier model, or one running free on your own machine.

    # film.toml (or flags: dreamreel generate ... --provider ollama --model qwen2.5vl)
    [ai]
    provider = "anthropic"          # anthropic, openai, gemini, openrouter, ollama, lmstudio, custom
    model = "claude-opus-5-5"       # the provider's model name
    url = ""                        # only for custom: an OpenAI-compatible endpoint

Keys come from the environment, never from project files: ANTHROPIC_API_KEY (or an `ant auth login`
profile), OPENAI_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, or DREAMREEL_AI_KEY for a custom
endpoint. Ollama and LM Studio run models on your own computer and need no key: that's the free
way (pick a model that can see pictures, e.g. a "vision" or "VL" model, for agents that look at
their own renders).

Claude goes through Anthropic's SDK (`pip install anthropic`); every other provider speaks the
OpenAI-compatible chat API, which needs nothing extra.
"""
import base64
import json
import os
import urllib.error
import urllib.request

PROVIDERS = {
    # name: (OpenAI-compatible base URL, key variable, default model or None)
    "anthropic": (None, "ANTHROPIC_API_KEY", "claude-opus-5-5"),
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY", None),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY", None),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", None),
    "ollama": ("http://localhost:11434/v1", None, None),
    "lmstudio": ("http://localhost:1234/v1", None, None),
    "custom": (None, "DREAMREEL_AI_KEY", None),
}
LOCAL = ("ollama", "lmstudio")
# Claude models that can retry a declined request on another model server-side
FALLBACKS = ("claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5")


class AIError(RuntimeError):
    pass


class Model:
    """One configured model. `ask(system, messages)` returns its reply as text.

    messages: [{"role": "user" | "assistant", "content": [part, ...]}] where a part is
    {"text": "..."} or {"image": "path/to/picture.png"}.
    """

    def __init__(self, provider, model=None, url=None):
        if provider not in PROVIDERS:
            raise AIError(f"unknown AI provider {provider!r}; use one of: {', '.join(PROVIDERS)}")
        base, key_var, default = PROVIDERS[provider]
        self.provider = provider
        self.model = model or default
        if not self.model:
            raise AIError(f"say which {provider} model to use (--model, or model = \"...\" under [ai] in film.toml)")
        self.url = (url or base or "").rstrip("/")
        if provider == "custom" and not self.url:
            raise AIError("a custom provider needs url = \"http://.../v1\" (an OpenAI-compatible endpoint)")
        self.key = os.environ.get(key_var, "").strip() if key_var else ""
        if provider not in LOCAL + ("anthropic", "custom") and not self.key:
            raise AIError(f"set {key_var} to use {provider} (or run a model locally for free: --provider ollama)")

    def __str__(self):
        return f"{self.provider}:{self.model}"

    def ask(self, system, messages, max_tokens=64000):
        if self.provider == "anthropic":
            return self._claude(system, messages, max_tokens)
        return self._openai(system, messages, max_tokens)

    # ------------------------------------------------------------------ Claude (Anthropic SDK)
    def _claude(self, system, messages, max_tokens):
        try:
            import anthropic
        except ImportError:
            raise AIError("Claude needs Anthropic's SDK: pip install anthropic (into the Python that runs dreamreel)")
        client = anthropic.Anthropic(base_url=self.url) if self.url else anthropic.Anthropic()
        msgs = []
        for m in messages:
            content = []
            for part in m["content"]:
                if "image" in part:
                    content.append({"type": "image", "source": {"type": "base64", "media_type": _mime(part["image"]),
                                                                "data": _b64(part["image"])}})
                else:
                    content.append({"type": "text", "text": part["text"]})
            msgs.append({"role": m["role"], "content": content})
        kwargs = dict(model=self.model, max_tokens=max_tokens, system=system, messages=msgs,
                      thinking={"type": "adaptive"}, output_config={"effort": "high"})
        try:
            if self.model in FALLBACKS:     # a declined request is retried on another Claude model
                with client.beta.messages.stream(betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                                                 **kwargs) as stream:
                    reply = stream.get_final_message()
            else:
                with client.messages.stream(**kwargs) as stream:
                    reply = stream.get_final_message()
        except anthropic.AuthenticationError:
            raise AIError("Claude: the API key was refused (set ANTHROPIC_API_KEY, or run `ant auth login`)")
        except anthropic.RateLimitError:
            raise AIError("Claude: rate limited; wait a little and try again")
        except anthropic.APIStatusError as e:
            raise AIError(f"Claude: {e.status_code} {e.message}")
        except anthropic.APIConnectionError:
            raise AIError("Claude: couldn't reach the API (network?)")
        if reply.stop_reason == "refusal":
            raise AIError("Claude declined this request; try describing it differently")
        text = "".join(b.text for b in reply.content if b.type == "text")
        if reply.stop_reason == "max_tokens":
            raise AIError("Claude's reply was cut off (too long)")
        return text

    # ------------------------------------------------------------------ OpenAI-compatible chat
    def _openai(self, system, messages, max_tokens):
        msgs = [{"role": "system", "content": system}]
        for m in messages:
            parts = []
            for part in m["content"]:
                if "image" in part:
                    url = f"data:{_mime(part['image'])};base64,{_b64(part['image'])}"
                    parts.append({"type": "image_url", "image_url": {"url": url}})
                else:
                    parts.append({"type": "text", "text": part["text"]})
            msgs.append({"role": m["role"], "content": parts})
        body = {"model": self.model, "messages": msgs, "max_tokens": min(max_tokens, 32000)}
        headers = {"Content-Type": "application/json", "User-Agent": "dreamreel"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request(self.url + "/chat/completions", data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                out = json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            raise AIError(f"{self}: HTTP {e.code} {detail}")
        except urllib.error.URLError as e:
            hint = " (is it running? e.g. `ollama serve`)" if self.provider in LOCAL else ""
            raise AIError(f"{self}: couldn't connect to {self.url}{hint}: {e.reason}")
        try:
            choice = out["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise AIError(f"{self}: unexpected reply: {str(out)[:300]}")
        if isinstance(text, list):          # some servers return content parts
            text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
        if choice.get("finish_reason") == "length":
            raise AIError(f"{self}: the reply was cut off (too long)")
        return text or ""


def configured(provider=None, model=None, url=None):
    """The model to use: flags first, then film.toml's [ai], then whatever key is set."""
    from . import project
    p = project.current()
    cfg = dict((p.film.get("ai") or {}) if p else {})
    provider = provider or cfg.get("provider") or os.environ.get("DREAMREEL_AI_PROVIDER")
    model = model or cfg.get("model") or os.environ.get("DREAMREEL_AI_MODEL")
    url = url or cfg.get("url") or os.environ.get("DREAMREEL_AI_URL")
    if not provider:
        if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            provider = "anthropic"
        else:
            for name, (_, var, _) in PROVIDERS.items():
                if var and name not in ("anthropic", "custom") and os.environ.get(var):
                    provider = name
                    break
    if not provider:
        raise AIError("no AI model set up. Use any provider with your key (e.g. ANTHROPIC_API_KEY, OPENAI_API_KEY "
                      "with --provider openai --model ...), or a free local one: install Ollama, `ollama pull` a "
                      "vision model, then --provider ollama --model <name>")
    return Model(provider, model, url)


def _b64(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()


def _mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
            ".gif": "image/gif"}.get(ext, "image/png")
