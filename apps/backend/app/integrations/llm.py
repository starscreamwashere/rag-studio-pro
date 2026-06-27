"""Multi-provider LLM generation.

The TRD requires multi-provider inference. ``settings.llm_provider`` selects the
active provider; each provider is a thin httpx call exposing the same
{'text', 'usage'} shape. Gemini and Groq are wired here; Anthropic/Ollama slot
in the same way.
"""

import httpx

from app.core.config import settings

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMNotConfigured(Exception):
    """Raised when the selected provider has no API key configured."""


class LLMError(Exception):
    """Raised when the LLM provider call fails (HTTP error, timeout, etc.)."""


async def _post(url: str, *, params=None, headers=None, json=None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, params=params, headers=headers, json=json)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        hint = " (rate limit / quota exceeded)" if code == 429 else ""
        raise LLMError(f"{settings.llm_provider} returned HTTP {code}{hint}.") from exc
    except httpx.HTTPError as exc:
        raise LLMError(f"{settings.llm_provider} request failed: {exc}") from exc


async def _gemini(prompt: str, system: str | None) -> dict:
    if not settings.gemini_api_key:
        raise LLMNotConfigured("GEMINI_API_KEY is not set.")
    body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = await _post(
        GEMINI_URL.format(model=settings.gemini_model),
        params={"key": settings.gemini_api_key},
        json=body,
    )
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return {
        "text": "".join(p.get("text", "") for p in parts).strip(),
        "usage": data.get("usageMetadata", {}),
    }


async def _groq(prompt: str, system: str | None) -> dict:
    if not settings.groq_api_key:
        raise LLMNotConfigured("GROQ_API_KEY is not set.")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = await _post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
        json={"model": settings.groq_model, "messages": messages},
    )
    return {
        "text": data["choices"][0]["message"]["content"].strip(),
        "usage": data.get("usage", {}),
    }


_PROVIDERS = {"gemini": _gemini, "groq": _groq}
_MODELS = {"gemini": "gemini_model", "groq": "groq_model"}
_KEYS = {"gemini": "gemini_api_key", "groq": "groq_api_key"}


def active_model() -> str:
    """Model name for the currently selected provider."""
    attr = _MODELS.get(settings.llm_provider)
    return getattr(settings, attr) if attr else settings.llm_provider


def is_configured() -> bool:
    """Whether the currently selected provider has an API key set."""
    attr = _KEYS.get(settings.llm_provider)
    return bool(getattr(settings, attr)) if attr else False


async def generate(prompt: str, system: str | None = None) -> dict:
    """Generate with the configured provider. Returns {'text', 'usage'}."""
    provider = _PROVIDERS.get(settings.llm_provider)
    if provider is None:
        raise LLMNotConfigured(f"Unknown LLM provider: {settings.llm_provider}")
    return await provider(prompt, system)
