from __future__ import annotations

import os

DEFAULT_MODEL = "gpt-4.1-mini"


def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        return None

    token = os.getenv("OPENAI_TOKEN")
    if not token:
        return None

    return OpenAI(api_key=token)


def generate_ai_text(prompt: str, model: str = DEFAULT_MODEL) -> str:
    client = get_openai_client()
    if client is None:
        return "AI mode is not configured in this environment."

    try:
        response = client.responses.create(model=model, input=prompt)
        return response.output_text
    except Exception as exc:
        return f"AI generation failed safely: {exc}"
