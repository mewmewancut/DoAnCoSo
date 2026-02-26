"""
LLM client factory.

Returns a LangChain chat model based on the ``LLM_PROVIDER`` setting.
All API keys are read from ``django.conf.settings`` (which in turn
reads them from ``.env`` via python-decouple).
"""
from __future__ import annotations

import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)


def get_llm():
    """
    Build and return the configured LangChain chat model.

    Supported providers (``settings.LLM_PROVIDER``):
        - ``openai``  → ChatOpenAI  (gpt-3.5-turbo)
        - ``gemini``  → ChatGoogleGenerativeAI (gemini-2.0-flash)
        - ``groq``    → ChatGroq  (llama-3.3-70b-versatile)

    Raises:
        ValueError: If the provider is unknown or the key is missing.
    """
    provider = getattr(settings, "LLM_PROVIDER", "gemini").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is empty — set it in .env")
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key,
            timeout=30,
            max_retries=2,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is empty — set it in .env")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key,
            convert_system_message_to_human=True,
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is empty — set it in .env")
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=api_key,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def test_connection() -> bool:
    """Quick smoke-test for the configured LLM."""
    try:
        llm = get_llm()
        response = llm.invoke("Say 'OK' if you can hear me.")
        logger.info("LLM connection OK — %s", response.content[:80])
        return True
    except Exception as exc:
        logger.error("LLM connection FAILED — %s", exc)
        return False
