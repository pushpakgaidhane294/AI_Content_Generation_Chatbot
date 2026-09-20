"""
AI Provider abstraction layer.
Swap providers without touching routes or frontend.
Supported: ollama (local), openai (future), groq (future).
"""

import os

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").lower()


def get_ai_service():
    """
    Factory: returns the configured AI service instance.
    Add new providers here in the future without changing routes or frontend.
    """
    if AI_PROVIDER == "ollama":
        from app.services.ollama_service import ollama_service
        return ollama_service

    # Future providers — add here when needed:
    # elif AI_PROVIDER == "openai":
    #     from app.services.openai_service import openai_service
    #     return openai_service
    # elif AI_PROVIDER == "groq":
    #     from app.services.groq_service import groq_service
    #     return groq_service

    else:
        raise ValueError(
            f"Unknown AI_PROVIDER: '{AI_PROVIDER}'. "
            "Supported values: 'ollama'. "
            "Set the AI_PROVIDER environment variable to a supported provider."
        )
