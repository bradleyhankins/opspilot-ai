from __future__ import annotations

import hashlib
import os

import streamlit as st

DEFAULT_MODEL = "gpt-4.1-mini"
TOKEN_NAME = "OPENAI_TOKEN"
MAX_PROMPT_CHARS = 12000

AI_GUARDRAIL_PREFIX = """
You are an embedded AI enhancement layer inside a deterministic business workflow app.
The rules-based app output is the source of truth.
Your job is to improve clarity, structure, tone, and usefulness without changing the underlying facts.
Do not invent facts, numbers, prices, discounts, deadlines, rankings, guarantees, legal requirements, hiring decisions, or business results.
Do not override calculations, scores, statuses, recommendations, or rule-based outputs provided by the app.
If information is missing, say it is missing or keep the fallback framing.
Keep the output practical, professional, and aligned with the user's provided context.
""".strip()


def read_token() -> str | None:
    try:
        token = st.secrets.get(TOKEN_NAME, None)
    except Exception:
        token = None
    return token or os.getenv(TOKEN_NAME)


def stable_cache_key(prefix: str, value: object) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"


def prepare_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS] + "\n\n[Input was trimmed for length before AI enhancement.]"
    return f"{AI_GUARDRAIL_PREFIX}\n\n---\n\n{prompt}"


def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        return None

    token = read_token()
    if not token:
        return None

    return OpenAI(api_key=token)


def generate_ai_text(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    client = get_openai_client()
    if client is None:
        return None

    try:
        response = client.responses.create(model=model, input=prepare_prompt(prompt))
        return response.output_text
    except Exception:
        return None


def enhance_text(prompt: str, fallback: str, cache_key: str) -> str:
    if cache_key not in st.session_state:
        generated = generate_ai_text(prompt)
        st.session_state[cache_key] = generated.strip() if generated else fallback
    return st.session_state[cache_key]
