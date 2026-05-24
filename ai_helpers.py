from __future__ import annotations

import os

import streamlit as st

DEFAULT_MODEL = "gpt-4.1-mini"
TOKEN_NAME = "OPENAI_TOKEN"


def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        return None

    token = os.getenv(TOKEN_NAME)
    if not token:
        return None

    return OpenAI(api_key=token)


def generate_ai_text(prompt: str, model: str = DEFAULT_MODEL):
    client = get_openai_client()
    if client is None:
        return None

    try:
        response = client.responses.create(model=model, input=prompt)
        return response.output_text
    except Exception:
        return None


def enhance_text(prompt: str, fallback: str, cache_key: str) -> str:
    if cache_key not in st.session_state:
        generated = generate_ai_text(prompt)
        st.session_state[cache_key] = generated if generated else fallback
    return st.session_state[cache_key]
