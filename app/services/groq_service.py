"""
Groq API Service.
Communicates with the Groq REST API.
Handles API key presence, model availability, generation requests, and user-friendly error wrapping.
"""

import os
from typing import Dict, Any, Optional
from groq import AsyncGroq, APIError, AuthenticationError
from dotenv import load_dotenv

load_dotenv(override=True)

class GroqServiceError(Exception):
    """Custom application-level exception for Groq errors with user-friendly messages."""
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class GroqService:
    """
    Service wrapper for interacting with the Groq API.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None

    async def check_status(self) -> Dict[str, Any]:
        """
        Verifies if the Groq client is configured.
        Returns diagnostic dictionary.
        """
        if not self.api_key:
            return {
                "provider": "Groq",
                "configured": False,
                "model": self.model,
                "message": "Groq API is not configured. Please check your GROQ_API_KEY."
            }
        
        return {
            "provider": "Groq",
            "configured": True,
            "model": self.model,
            "message": "Connected and model ready."
        }

    async def generate(self, prompt: str, system_override: Optional[str] = None, history: Optional[list] = None) -> str:
        """
        Sends an engineered prompt to Groq and returns the generated content.
        Raises GroqServiceError with helpful user-facing messages upon failure.
        """
        if not self.api_key or not self.client:
            raise GroqServiceError("Groq API is not configured. Please check your GROQ_API_KEY.", status_code=500)

        messages = []
        if system_override:
            messages.append({"role": "system", "content": system_override})
        
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                top_p=0.9,
            )
            
            generated_text = chat_completion.choices[0].message.content
            
            if not generated_text:
                raise GroqServiceError("Groq returned an empty response. Please try modifying your prompt.", status_code=500)
                
            return generated_text.strip()
            
        except AuthenticationError:
            raise GroqServiceError("Groq API authentication failed. Please check your GROQ_API_KEY.", status_code=401)
        except APIError as e:
            err_msg = str(e)
            if "model_decommissioned" in err_msg or "does not exist" in err_msg or "is not supported" in err_msg:
                raise GroqServiceError(f"The configured Groq model is unavailable. Please check GROQ_MODEL. Details: {err_msg}", status_code=400)
            raise GroqServiceError(f"Groq API returned an error: {err_msg}", status_code=500)
        except Exception as exc:
            raise GroqServiceError(f"An unexpected error occurred during content generation: {str(exc)}", status_code=500)

groq_service = GroqService()
