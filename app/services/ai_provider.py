"""
AI Provider abstraction layer.
Swap providers without touching routes or frontend.
Supported: groq (cloud).
"""

import os

AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()

def get_ai_service():
    """
    Factory: returns the configured AI service instance.
    Add new providers here in the future without changing routes or frontend.
    """
    if AI_PROVIDER == "groq":
        from app.services.groq_service import groq_service
        return groq_service
    else:
        raise ValueError(
            f"Unknown AI_PROVIDER: '{AI_PROVIDER}'. "
            "Supported values: 'groq'. "
            "Set the AI_PROVIDER environment variable to a supported provider."
        )
